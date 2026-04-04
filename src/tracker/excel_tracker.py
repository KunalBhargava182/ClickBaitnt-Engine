"""
Excel tracker — persists VideoRecord rows to an .xlsx spreadsheet.

Sheet layout
------------
  Row 1 : Bold header row (column names from config.yaml).
  Row 2+: One row per video, newest at the bottom.

All writes are atomic: the workbook is loaded → modified → saved in one
operation so a crash mid-write never leaves a half-written file.

Usage:
    tracker = ExcelTracker()
    tracker.append(record)             # add a new row
    tracker.update(record)             # overwrite row matched by video_id
    record = tracker.get("vid_001")    # fetch by ID (or None)
    all_records = tracker.load_all()   # list[VideoRecord]
"""

import shutil
import tempfile
from pathlib import Path
from typing import Optional

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from src.tracker.models import VideoRecord
from src.utils.config_loader import get_config, get_project_root
from src.utils.logger import log

# Header styling
_HEADER_FONT   = Font(bold=True, color="FFFFFF", size=11)
_HEADER_FILL   = PatternFill("solid", fgColor="1F4E79")   # dark blue
_HEADER_ALIGN  = Alignment(horizontal="center", vertical="center", wrap_text=False)

# Column widths (characters) — order matches config columns
_COL_WIDTHS = {
    "ID":           22,
    "Date":         12,
    "Topic":        40,
    "Script":       55,
    "Trend Source": 16,
    "Trend Score":  13,
    "Video File":   45,
    "YouTube URL":  40,
    "Status":       12,
    "Views (24h)":  13,
    "Notes":        40,
}


class ExcelTracker:
    """
    Reads and writes VideoRecord rows in a persistent Excel workbook.

    The tracker is safe to use across multiple processes as long as
    they don't write simultaneously (no distributed lock is implemented).
    """

    def __init__(self) -> None:
        cfg          = get_config()
        tr           = cfg.tracker
        root         = get_project_root()

        rel_path: str        = tr.get("excel_path", "data/tracking_sheet.xlsx")
        self._path: Path     = root / rel_path
        self._sheet: str     = tr.get("sheet_name", "Shorts Tracker")
        self._columns: list  = list(tr.get("columns", list(_COL_WIDTHS.keys())))

        self._path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def append(self, record: VideoRecord) -> None:
        """
        Add a new row for record at the bottom of the sheet.

        If the workbook or sheet does not yet exist it is created first.
        If a row with the same video_id already exists, it is updated
        instead of duplicated.

        Args:
            record: VideoRecord to persist.
        """
        existing = self.get(record.video_id)
        if existing is not None:
            log.info(
                "excel_tracker.append.already_exists_updating",
                video_id=record.video_id,
            )
            self.update(record)
            return

        wb, ws = self._load_or_create()
        ws.append(self._record_to_row_values(record))
        self._save(wb)

        log.info(
            "excel_tracker.append",
            video_id=record.video_id,
            status=record.status,
            row=ws.max_row,
        )

    def update(self, record: VideoRecord) -> bool:
        """
        Overwrite the row matching record.video_id with fresh values.

        Args:
            record: Updated VideoRecord.

        Returns:
            True if a matching row was found and updated, False otherwise.
        """
        if not self._path.exists():
            log.warning(
                "excel_tracker.update.no_file",
                video_id=record.video_id,
            )
            return False

        wb, ws = self._open()
        headers = self._get_headers(ws)
        if not headers:
            return False

        id_col = headers.get("ID")
        if id_col is None:
            return False

        for row in ws.iter_rows(min_row=2):
            if str(row[id_col - 1].value) == record.video_id:
                values = self._record_to_row_values(record)
                for col_idx, val in enumerate(values, start=1):
                    row[col_idx - 1].value = val
                self._save(wb)
                log.info(
                    "excel_tracker.update",
                    video_id=record.video_id,
                    status=record.status,
                )
                return True

        # ID not found — append instead
        log.warning(
            "excel_tracker.update.id_not_found_appending",
            video_id=record.video_id,
        )
        ws.append(self._record_to_row_values(record))
        self._save(wb)
        return False

    def get(self, video_id: str) -> Optional[VideoRecord]:
        """
        Fetch the VideoRecord for video_id, or None if not found.

        Args:
            video_id: Internal video identifier.

        Returns:
            VideoRecord or None.
        """
        for record in self.load_all():
            if record.video_id == video_id:
                return record
        return None

    def load_all(self) -> list[VideoRecord]:
        """
        Return all VideoRecord rows from the spreadsheet.

        Returns:
            List of VideoRecord (empty list if file does not exist).
        """
        if not self._path.exists():
            return []

        try:
            wb, ws = self._open()
        except Exception as exc:
            log.error("excel_tracker.load_all.open_failed", error=str(exc))
            return []

        headers = self._get_headers(ws)
        if not headers:
            return []

        records: list[VideoRecord] = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if all(v is None for v in row):
                continue   # skip blank rows
            row_dict = {col: row[idx - 1] for col, idx in headers.items()}
            try:
                records.append(VideoRecord.from_row(row_dict))
            except Exception as exc:
                log.warning(
                    "excel_tracker.load_all.skip_bad_row",
                    error=str(exc),
                )

        return records

    def update_views(self, video_id: str, views: int) -> bool:
        """
        Convenience method: set views_24h for an uploaded video.

        Args:
            video_id: Internal video identifier.
            views:    View count to record.

        Returns:
            True if the row was found and updated.
        """
        record = self.get(video_id)
        if record is None:
            log.warning("excel_tracker.update_views.not_found", video_id=video_id)
            return False
        record.views_24h = views
        return self.update(record)

    # ------------------------------------------------------------------ #
    #  Workbook helpers                                                    #
    # ------------------------------------------------------------------ #

    def _load_or_create(self):
        """Open the workbook if it exists, otherwise create a new one."""
        if self._path.exists():
            return self._open()
        return self._create()

    def _open(self):
        wb = openpyxl.load_workbook(str(self._path))
        if self._sheet in wb.sheetnames:
            ws = wb[self._sheet]
        else:
            ws = wb.create_sheet(self._sheet)
            self._write_headers(ws)
        return wb, ws

    def _create(self):
        """Create a new workbook with styled headers."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = self._sheet
        self._write_headers(ws)
        self._save(wb)
        log.info("excel_tracker.created", path=str(self._path))
        return wb, ws

    def _write_headers(self, ws) -> None:
        """Write the bold styled header row."""
        ws.append(self._columns)
        header_row = ws[1]
        for cell in header_row:
            cell.font      = _HEADER_FONT
            cell.fill      = _HEADER_FILL
            cell.alignment = _HEADER_ALIGN

        # Set column widths
        for col_idx, col_name in enumerate(self._columns, start=1):
            width = _COL_WIDTHS.get(col_name, 18)
            ws.column_dimensions[get_column_letter(col_idx)].width = width

        # Freeze the header row
        ws.freeze_panes = "A2"

    def _save(self, wb) -> None:
        """
        Atomic save: write to a temp file then rename over the target.
        Prevents corrupt files if the process is killed mid-write.
        """
        tmp_fd, tmp_path = tempfile.mkstemp(
            suffix=".xlsx", dir=str(self._path.parent)
        )
        try:
            import os
            os.close(tmp_fd)
            wb.save(tmp_path)
            shutil.move(tmp_path, str(self._path))
        except Exception:
            try:
                import os
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    def _get_headers(self, ws) -> dict[str, int]:
        """
        Read the first row and return {column_name: 1-based column index}.
        Returns empty dict if the sheet has no rows.
        """
        first_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True), None)
        if not first_row:
            return {}
        return {
            str(cell): idx + 1
            for idx, cell in enumerate(first_row)
            if cell is not None
        }

    def _record_to_row_values(self, record: VideoRecord) -> list:
        """Return a list of cell values in column order."""
        row_dict = record.to_row()
        return [row_dict.get(col, "") for col in self._columns]
