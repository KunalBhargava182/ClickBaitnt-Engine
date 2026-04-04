"""
Temp file cleanup and archive management.
"""

import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from src.utils.logger import log


class CleanupManager:
    """
    Manages temporary file cleanup and video archiving.

    After a successful upload:
    - Moves the final video to output/archive/
    - Deletes intermediate assets (raw images, raw audio, temp frames)
    - Prunes archives older than retention_days
    """

    def __init__(self, project_root: Optional[Path] = None, retention_days: int = 7):
        """
        Args:
            project_root: Root of the project. Defaults to 3 levels above this file.
            retention_days: How many days of archived videos to keep.
        """
        if project_root is None:
            project_root = Path(__file__).resolve().parents[2]

        self.root = project_root
        self.retention_days = retention_days

        self.output_dir = self.root / "output"
        self.archive_dir = self.output_dir / "archive"
        self.images_dir = self.output_dir / "images"
        self.audio_dir = self.output_dir / "audio"
        self.scripts_dir = self.output_dir / "scripts"

        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def archive_video(self, video_path: Path) -> Path:
        """
        Move a final rendered video into output/archive/.

        Args:
            video_path: Path to the finished .mp4 file.

        Returns:
            New path inside the archive directory.
        """
        if not video_path.exists():
            log.warning("cleanup.archive_video.missing", path=str(video_path))
            return video_path

        dest = self.archive_dir / video_path.name
        shutil.move(str(video_path), str(dest))
        log.info("cleanup.archive_video.done", src=str(video_path), dest=str(dest))
        return dest

    def delete_intermediates(self, video_id: str) -> None:
        """
        Delete all intermediate files for a given video_id.
        Removes matching images, audio, and script files.

        Args:
            video_id: The unique ID used as filename prefix.
        """
        patterns = [
            (self.images_dir, f"{video_id}_*.png"),
            (self.images_dir, f"{video_id}_*.jpg"),
            (self.audio_dir, f"{video_id}*"),
            (self.scripts_dir, f"{video_id}*"),
        ]

        deleted = 0
        for directory, pattern in patterns:
            for f in directory.glob(pattern):
                try:
                    f.unlink()
                    deleted += 1
                except OSError as exc:
                    log.warning(
                        "cleanup.delete_intermediates.error",
                        file=str(f),
                        error=str(exc),
                    )

        log.info(
            "cleanup.delete_intermediates.done",
            video_id=video_id,
            files_deleted=deleted,
        )

    def prune_archives(self) -> None:
        """
        Delete archived videos older than self.retention_days.
        """
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        pruned = 0

        for f in self.archive_dir.glob("*.mp4"):
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime < cutoff:
                try:
                    f.unlink()
                    pruned += 1
                except OSError as exc:
                    log.warning(
                        "cleanup.prune_archives.error",
                        file=str(f),
                        error=str(exc),
                    )

        log.info(
            "cleanup.prune_archives.done",
            pruned=pruned,
            retention_days=self.retention_days,
        )

    def full_cleanup(self, video_id: str, video_path: Path) -> Path:
        """
        Run the complete post-upload cleanup sequence.

        Args:
            video_id: Unique video identifier.
            video_path: Path to the finished video file.

        Returns:
            Archive path of the moved video.
        """
        archived = self.archive_video(video_path)
        self.delete_intermediates(video_id)
        self.prune_archives()
        return archived
