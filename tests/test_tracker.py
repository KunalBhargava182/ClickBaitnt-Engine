"""
Tests for Phase 9: Excel Tracker.

Covers:
- VideoRecord: construction, from_script, to_row/from_row roundtrip,
               update_status validation
- ExcelTracker: create workbook, append, update, get, load_all,
                update_views, duplicate-prevention, atomic save

Run with: python -m pytest tests/test_tracker.py -v
"""

import datetime
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


# ------------------------------------------------------------------ #
#  Helpers                                                            #
# ------------------------------------------------------------------ #

def _make_record(
    video_id="vid_001",
    topic="Ocean Waves",
    status="pending",
    trend_score=72.5,
    youtube_url="",
    views_24h=None,
) -> "VideoRecord":
    from src.tracker.models import VideoRecord
    return VideoRecord(
        video_id     = video_id,
        topic        = topic,
        script       = "Scientists discovered ocean waves...",
        trend_source = "google_trends",
        trend_score  = trend_score,
        status       = status,
        youtube_url  = youtube_url,
        views_24h    = views_24h,
    )


def _make_tracker(tmp_path: Path) -> "ExcelTracker":
    from src.tracker.excel_tracker import ExcelTracker
    tracker = ExcelTracker()
    tracker._path = tmp_path / "tracker.xlsx"
    return tracker


def _make_script_dict(**overrides) -> dict:
    base = {
        "title":       "Ocean Waves Power Source",
        "topic":       "ocean wave energy",
        "script_text": "Scientists discovered that ocean waves contain enormous energy. "
                       "This breakthrough could power entire cities.",
        "description": "A fascinating look at wave energy.",
        "tags":        ["ocean", "energy", "science"],
        "category":    "science",
    }
    base.update(overrides)
    return base


# ------------------------------------------------------------------ #
#  VideoRecord tests                                                  #
# ------------------------------------------------------------------ #

class TestVideoRecord:

    def test_default_date_is_today(self):
        """date field defaults to today's ISO date."""
        from src.tracker.models import VideoRecord
        r = VideoRecord(video_id="v1")
        assert r.date == datetime.date.today().isoformat()

    def test_default_status_is_pending(self):
        from src.tracker.models import VideoRecord
        r = VideoRecord(video_id="v1")
        assert r.status == "pending"

    def test_from_script_sets_status_scripted(self):
        """from_script() produces a record with status='scripted'."""
        from src.tracker.models import VideoRecord
        r = VideoRecord.from_script(_make_script_dict(), "vid_001")
        assert r.status == "scripted"

    def test_from_script_extracts_topic(self):
        from src.tracker.models import VideoRecord
        r = VideoRecord.from_script(_make_script_dict(), "vid_001")
        assert r.topic == "ocean wave energy"

    def test_from_script_excerpts_script_text(self):
        """script field is truncated to 120 chars with ellipsis."""
        from src.tracker.models import VideoRecord
        long_text = "A " * 200
        r = VideoRecord.from_script(_make_script_dict(script_text=long_text), "v1")
        assert len(r.script) <= 121   # 120 + 1 for ellipsis char
        assert r.script.endswith("…")

    def test_from_script_short_text_no_ellipsis(self):
        """Short narration is not truncated."""
        from src.tracker.models import VideoRecord
        short = "Brief narration."
        r = VideoRecord.from_script(_make_script_dict(script_text=short), "v1")
        assert r.script == short

    def test_from_script_trend_score_rounded(self):
        from src.tracker.models import VideoRecord
        r = VideoRecord.from_script(_make_script_dict(), "v1", trend_score=72.876)
        assert r.trend_score == 72.9

    def test_to_row_contains_all_columns(self):
        """to_row() dict has exactly the expected column headers."""
        from src.tracker.models import VideoRecord
        r   = _make_record()
        row = r.to_row()
        expected_keys = {
            "ID", "Date", "Topic", "Script", "Trend Source",
            "Trend Score", "Video File", "YouTube URL",
            "Status", "Views (24h)", "Notes",
        }
        assert expected_keys == set(row.keys())

    def test_to_row_values_match_fields(self):
        from src.tracker.models import VideoRecord
        r   = _make_record(video_id="abc", topic="Test Topic", status="uploaded")
        row = r.to_row()
        assert row["ID"]     == "abc"
        assert row["Topic"]  == "Test Topic"
        assert row["Status"] == "uploaded"

    def test_to_row_views_none_becomes_empty_string(self):
        from src.tracker.models import VideoRecord
        r = _make_record(views_24h=None)
        assert r.to_row()["Views (24h)"] == ""

    def test_to_row_views_int_preserved(self):
        from src.tracker.models import VideoRecord
        r = _make_record(views_24h=4200)
        assert r.to_row()["Views (24h)"] == 4200

    def test_from_row_roundtrip(self):
        """to_row → from_row produces an identical record."""
        from src.tracker.models import VideoRecord
        original = _make_record(
            video_id="round_v1", topic="Roundtrip", status="uploaded",
            views_24h=999,
        )
        row      = original.to_row()
        restored = VideoRecord.from_row(row)

        assert restored.video_id   == original.video_id
        assert restored.topic      == original.topic
        assert restored.status     == original.status
        assert restored.views_24h  == original.views_24h

    def test_from_row_handles_missing_views(self):
        """from_row with empty Views (24h) → views_24h=None."""
        from src.tracker.models import VideoRecord
        row = {"ID": "v1", "Views (24h)": ""}
        r   = VideoRecord.from_row(row)
        assert r.views_24h is None

    def test_update_status_valid_transition(self):
        from src.tracker.models import VideoRecord
        r = _make_record(status="scripted")
        r.update_status("rendered")
        assert r.status == "rendered"

    def test_update_status_sets_notes(self):
        from src.tracker.models import VideoRecord
        r = _make_record()
        r.update_status("failed", notes="FFmpeg not found")
        assert r.notes == "FFmpeg not found"

    def test_update_status_raises_on_invalid(self):
        from src.tracker.models import VideoRecord
        r = _make_record()
        with pytest.raises(ValueError, match="Unknown status"):
            r.update_status("unknown_stage")


# ------------------------------------------------------------------ #
#  ExcelTracker tests                                                 #
# ------------------------------------------------------------------ #

class TestExcelTracker:

    def test_append_creates_file_when_missing(self, tmp_path):
        """First append creates the workbook."""
        tracker = _make_tracker(tmp_path)
        tracker.append(_make_record("v1"))
        assert tracker._path.exists()

    def test_append_creates_header_row(self, tmp_path):
        """The created workbook has a styled header in row 1."""
        import openpyxl
        tracker = _make_tracker(tmp_path)
        tracker.append(_make_record("v1"))

        wb = openpyxl.load_workbook(str(tracker._path))
        ws = wb[tracker._sheet]
        headers = [cell.value for cell in ws[1]]
        assert "ID" in headers
        assert "Topic" in headers
        assert "Status" in headers

    def test_append_adds_data_row(self, tmp_path):
        """append() writes one data row below the header."""
        import openpyxl
        tracker = _make_tracker(tmp_path)
        tracker.append(_make_record("v1", topic="Wave Power"))

        wb = openpyxl.load_workbook(str(tracker._path))
        ws = wb[tracker._sheet]
        assert ws.max_row == 2   # header + 1 data row

    def test_append_multiple_records(self, tmp_path):
        """Multiple appends produce sequential rows."""
        tracker = _make_tracker(tmp_path)
        for i in range(5):
            tracker.append(_make_record(f"vid_{i:03d}", topic=f"Topic {i}"))

        records = tracker.load_all()
        assert len(records) == 5

    def test_append_deduplicates_by_video_id(self, tmp_path):
        """Appending same video_id twice updates the existing row."""
        tracker = _make_tracker(tmp_path)
        tracker.append(_make_record("v1", status="pending"))
        tracker.append(_make_record("v1", status="uploaded"))

        records = tracker.load_all()
        assert len(records) == 1
        assert records[0].status == "uploaded"

    def test_get_returns_record_by_id(self, tmp_path):
        """get() finds a record by its video_id."""
        tracker = _make_tracker(tmp_path)
        tracker.append(_make_record("find_me", topic="Findable"))

        result = tracker.get("find_me")
        assert result is not None
        assert result.topic == "Findable"

    def test_get_returns_none_when_not_found(self, tmp_path):
        """get() returns None for an unknown video_id."""
        tracker = _make_tracker(tmp_path)
        tracker.append(_make_record("v1"))

        assert tracker.get("ghost_id") is None

    def test_get_returns_none_when_file_missing(self, tmp_path):
        """get() returns None gracefully if the xlsx doesn't exist yet."""
        tracker = _make_tracker(tmp_path)
        assert tracker.get("v1") is None

    def test_update_overwrites_row(self, tmp_path):
        """update() changes specific fields without creating a new row."""
        tracker = _make_tracker(tmp_path)
        tracker.append(_make_record("v1", status="scripted"))

        rec = tracker.get("v1")
        rec.update_status("uploaded")
        rec.youtube_url = "https://youtu.be/abc123"
        tracker.update(rec)

        updated = tracker.get("v1")
        assert updated.status      == "uploaded"
        assert updated.youtube_url == "https://youtu.be/abc123"

        # Still only one row
        assert len(tracker.load_all()) == 1

    def test_update_returns_true_when_found(self, tmp_path):
        tracker = _make_tracker(tmp_path)
        tracker.append(_make_record("v1"))
        rec = tracker.get("v1")
        assert tracker.update(rec) is True

    def test_update_returns_false_when_file_missing(self, tmp_path):
        tracker = _make_tracker(tmp_path)
        result  = tracker.update(_make_record("v1"))
        assert result is False

    def test_update_appends_when_id_not_found(self, tmp_path):
        """update() falls back to append if the ID isn't in the sheet."""
        tracker = _make_tracker(tmp_path)
        tracker.append(_make_record("v1"))
        tracker.update(_make_record("new_id"))

        records = tracker.load_all()
        ids = [r.video_id for r in records]
        assert "new_id" in ids

    def test_load_all_returns_empty_when_file_missing(self, tmp_path):
        tracker = _make_tracker(tmp_path)
        assert tracker.load_all() == []

    def test_load_all_preserves_order(self, tmp_path):
        """load_all() returns records in insertion order."""
        tracker = _make_tracker(tmp_path)
        ids = [f"vid_{i:03d}" for i in range(10)]
        for vid_id in ids:
            tracker.append(_make_record(vid_id))

        loaded_ids = [r.video_id for r in tracker.load_all()]
        assert loaded_ids == ids

    def test_load_all_skips_blank_rows(self, tmp_path):
        """Blank rows in the spreadsheet are ignored."""
        import openpyxl
        tracker = _make_tracker(tmp_path)
        tracker.append(_make_record("v1"))

        # Manually insert a blank row
        wb = openpyxl.load_workbook(str(tracker._path))
        ws = wb[tracker._sheet]
        ws.append([None] * 11)
        wb.save(str(tracker._path))

        records = tracker.load_all()
        assert len(records) == 1

    def test_update_views(self, tmp_path):
        """update_views() sets the views_24h field and persists it."""
        tracker = _make_tracker(tmp_path)
        tracker.append(_make_record("v1"))

        result = tracker.update_views("v1", 12_500)
        assert result is True

        rec = tracker.get("v1")
        assert rec.views_24h == 12_500

    def test_update_views_returns_false_for_unknown_id(self, tmp_path):
        tracker = _make_tracker(tmp_path)
        assert tracker.update_views("ghost", 100) is False

    def test_atomic_save_does_not_corrupt_on_error(self, tmp_path):
        """Original file is untouched if save fails mid-write."""
        tracker = _make_tracker(tmp_path)
        tracker.append(_make_record("v1"))

        original_content = tracker._path.read_bytes()

        # Force failure during wb.save by making the tmp dir read-only
        # (simulate by patching shutil.move to raise)
        import shutil
        original_move = shutil.move

        def failing_move(src, dst):
            raise OSError("Disk full")

        with patch("src.tracker.excel_tracker.shutil.move", side_effect=failing_move):
            with pytest.raises(OSError):
                tracker.append(_make_record("v2"))

        # Original should be intact
        assert tracker._path.read_bytes() == original_content

    def test_header_row_is_frozen(self, tmp_path):
        """Freeze pane is set so header stays visible when scrolling."""
        import openpyxl
        tracker = _make_tracker(tmp_path)
        tracker.append(_make_record("v1"))

        wb = openpyxl.load_workbook(str(tracker._path))
        ws = wb[tracker._sheet]
        assert ws.freeze_panes == "A2"

    def test_column_widths_set(self, tmp_path):
        """Column dimensions are set (not default) for better readability."""
        import openpyxl
        tracker = _make_tracker(tmp_path)
        tracker.append(_make_record("v1"))

        wb = openpyxl.load_workbook(str(tracker._path))
        ws = wb[tracker._sheet]
        # Column A (ID) should have a width set
        assert ws.column_dimensions["A"].width > 0

    def test_full_pipeline_record_lifecycle(self, tmp_path):
        """Simulate the full lifecycle: pending → scripted → rendered → uploaded."""
        from src.tracker.models import VideoRecord
        tracker = _make_tracker(tmp_path)

        # 1. Create from script
        rec = VideoRecord.from_script(
            _make_script_dict(), "lifecycle_vid",
            trend_source="newsapi", trend_score=88.0,
        )
        tracker.append(rec)

        # 2. Render stage
        rec.update_status("rendered")
        rec.video_file = "/output/videos/lifecycle_vid.mp4"
        tracker.update(rec)

        # 3. Upload stage
        rec.update_status("uploaded")
        rec.youtube_url = "https://youtu.be/xyz789"
        tracker.update(rec)

        # 4. Views update
        tracker.update_views("lifecycle_vid", 5_000)

        # Verify final state
        final = tracker.get("lifecycle_vid")
        assert final.status      == "uploaded"
        assert final.youtube_url == "https://youtu.be/xyz789"
        assert final.views_24h   == 5_000
        assert len(tracker.load_all()) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
