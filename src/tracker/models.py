"""
VideoRecord — the single data model for one produced YouTube Short.

One record is created when a video enters the pipeline and updated
at each milestone (script generated, uploaded, views collected).
The ExcelTracker serialises/deserialises these to and from the
tracking spreadsheet.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Optional


def _today() -> str:
    """Return today's date as an ISO-8601 string (YYYY-MM-DD)."""
    return datetime.date.today().isoformat()


@dataclass
class VideoRecord:
    """
    Tracks the full lifecycle of one YouTube Short.

    Fields mirror the columns defined in config.yaml → tracker → columns.
    Optional fields are filled in as the pipeline progresses.

    Attributes:
        video_id:     Internal unique identifier (e.g. "vid_20260319_001").
        date:         Date the video was produced (ISO-8601 date string).
        topic:        Trend topic the video covers.
        script:       First 120 chars of the script narration (for quick review).
        trend_source: Which discovery source found the topic (google_trends / newsapi).
        trend_score:  Composite score that ranked this topic (0–100).
        video_file:   Absolute path to the exported MP4.
        youtube_url:  Published URL (https://youtu.be/…) — empty until uploaded.
        status:       Pipeline stage: pending | scripted | rendered | uploaded | failed.
        views_24h:    View count 24 hours after upload (filled by a later job).
        notes:        Free-text field for errors or manual annotations.
    """

    video_id:     str
    date:         str                  = field(default_factory=_today)
    topic:        str                  = ""
    script:       str                  = ""
    trend_source: str                  = ""
    trend_score:  float                = 0.0
    video_file:   str                  = ""
    youtube_url:  str                  = ""
    status:       str                  = "pending"
    views_24h:    Optional[int]        = None
    notes:        str                  = ""

    # ------------------------------------------------------------------
    # Convenience constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_script(
        cls,
        script:       dict,
        video_id:     str,
        trend_source: str   = "",
        trend_score:  float = 0.0,
    ) -> "VideoRecord":
        """
        Build a record from a ScriptGenerator output dict.

        Args:
            script:       Dict returned by ScriptGenerator.generate().
            video_id:     Unique identifier for this video run.
            trend_source: Origin of the topic (e.g. "google_trends").
            trend_score:  Composite trend score (0–100).

        Returns:
            A VideoRecord with status="scripted".
        """
        narration = script.get("script_text", "")
        excerpt   = narration[:120].replace("\n", " ").strip()
        if len(narration) > 120:
            excerpt += "…"

        return cls(
            video_id     = video_id,
            topic        = script.get("topic", ""),
            script       = excerpt,
            trend_source = trend_source,
            trend_score  = round(float(trend_score), 1),
            status       = "scripted",
        )

    # ------------------------------------------------------------------
    # Dict serialisation (for Excel row writing)
    # ------------------------------------------------------------------

    def to_row(self) -> dict:
        """
        Return an ordered dict mapping column header → cell value.
        Matches the column order in config.yaml.
        """
        return {
            "ID":           self.video_id,
            "Date":         self.date,
            "Topic":        self.topic,
            "Script":       self.script,
            "Trend Source": self.trend_source,
            "Trend Score":  self.trend_score,
            "Video File":   self.video_file,
            "YouTube URL":  self.youtube_url,
            "Status":       self.status,
            "Views (24h)":  self.views_24h if self.views_24h is not None else "",
            "Notes":        self.notes,
        }

    @classmethod
    def from_row(cls, row: dict) -> "VideoRecord":
        """
        Reconstruct a VideoRecord from an Excel row dict.

        Args:
            row: Dict of {column_header: cell_value} from openpyxl.

        Returns:
            VideoRecord instance.
        """
        views_raw = row.get("Views (24h)", "")
        try:
            views = int(views_raw) if views_raw not in (None, "", "None") else None
        except (ValueError, TypeError):
            views = None

        return cls(
            video_id     = str(row.get("ID", "")),
            date         = str(row.get("Date", _today())),
            topic        = str(row.get("Topic", "")),
            script       = str(row.get("Script", "")),
            trend_source = str(row.get("Trend Source", "")),
            trend_score  = float(row.get("Trend Score", 0.0) or 0.0),
            video_file   = str(row.get("Video File", "")),
            youtube_url  = str(row.get("YouTube URL", "")),
            status       = str(row.get("Status", "pending")),
            views_24h    = views,
            notes        = str(row.get("Notes", "")),
        )

    # ------------------------------------------------------------------
    # Status helpers
    # ------------------------------------------------------------------

    VALID_STATUSES = frozenset(
        {"pending", "scripted", "rendered", "uploaded", "failed"}
    )

    def update_status(self, new_status: str, notes: str = "") -> None:
        """
        Transition to a new pipeline status.

        Args:
            new_status: One of the VALID_STATUSES values.
            notes:      Optional note to append (e.g. error message).

        Raises:
            ValueError: new_status is not a recognised status.
        """
        if new_status not in self.VALID_STATUSES:
            raise ValueError(
                f"Unknown status '{new_status}'. "
                f"Valid: {sorted(self.VALID_STATUSES)}"
            )
        self.status = new_status
        if notes:
            self.notes = notes


