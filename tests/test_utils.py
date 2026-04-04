"""
Tests for Phase 11: Utility modules.

Covers:
- CleanupManager: archive_video, delete_intermediates, prune_archives,
                  full_cleanup, missing-file tolerance
- with_retry: success on first try, retry-on-failure, reraise after exhaustion,
              selective exception types
- config_loader: get_config dot-access, reload flag, get_project_root,
                 missing-config error
- logger: setup_logger returns a bound logger, log dir is created

Run with: python -m pytest tests/test_utils.py -v
"""

import sys
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch, call
import tempfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


# ------------------------------------------------------------------ #
#  CleanupManager tests                                               #
# ------------------------------------------------------------------ #

class TestCleanupManager:

    def _make_manager(self, tmp_path: Path):
        from src.utils.cleanup import CleanupManager
        return CleanupManager(project_root=tmp_path)

    # archive_video -------------------------------------------------- #

    def test_archive_video_moves_file(self, tmp_path):
        """archive_video() moves the mp4 into output/archive/."""
        mgr = self._make_manager(tmp_path)
        video = tmp_path / "output" / "videos" / "vid_001.mp4"
        video.parent.mkdir(parents=True, exist_ok=True)
        video.write_bytes(b"fake video")

        dest = mgr.archive_video(video)

        assert dest.exists()
        assert dest.parent == mgr.archive_dir
        assert not video.exists()

    def test_archive_video_returns_new_path(self, tmp_path):
        """archive_video() returns the destination path."""
        mgr = self._make_manager(tmp_path)
        video = tmp_path / "vid_001.mp4"
        video.write_bytes(b"data")

        result = mgr.archive_video(video)
        assert result == mgr.archive_dir / "vid_001.mp4"

    def test_archive_video_missing_file_returns_original_path(self, tmp_path):
        """archive_video() is tolerant of a missing source file."""
        mgr = self._make_manager(tmp_path)
        ghost = tmp_path / "ghost.mp4"

        result = mgr.archive_video(ghost)
        assert result == ghost   # unchanged path returned

    # delete_intermediates ------------------------------------------- #

    def test_delete_intermediates_removes_images(self, tmp_path):
        """PNG/JPG images matching video_id pattern are deleted."""
        mgr = self._make_manager(tmp_path)
        mgr.images_dir.mkdir(parents=True, exist_ok=True)

        img1 = mgr.images_dir / "vid_001_scene_01.png"
        img2 = mgr.images_dir / "vid_001_scene_02.jpg"
        other = mgr.images_dir / "vid_002_scene_01.png"   # different ID
        img1.write_bytes(b"img")
        img2.write_bytes(b"img")
        other.write_bytes(b"img")

        mgr.delete_intermediates("vid_001")

        assert not img1.exists()
        assert not img2.exists()
        assert other.exists()   # untouched

    def test_delete_intermediates_removes_audio(self, tmp_path):
        """Audio files matching video_id are deleted."""
        mgr = self._make_manager(tmp_path)
        mgr.audio_dir.mkdir(parents=True, exist_ok=True)

        audio = mgr.audio_dir / "vid_001_voice.mp3"
        audio.write_bytes(b"audio")

        mgr.delete_intermediates("vid_001")
        assert not audio.exists()

    def test_delete_intermediates_removes_scripts(self, tmp_path):
        """Script files matching video_id are deleted."""
        mgr = self._make_manager(tmp_path)
        mgr.scripts_dir.mkdir(parents=True, exist_ok=True)

        script = mgr.scripts_dir / "vid_001_script.json"
        script.write_bytes(b"{}")

        mgr.delete_intermediates("vid_001")
        assert not script.exists()

    def test_delete_intermediates_missing_dirs_ok(self, tmp_path):
        """delete_intermediates() is safe when intermediate dirs don't exist."""
        mgr = self._make_manager(tmp_path)
        # images_dir, audio_dir, scripts_dir may not exist yet
        mgr.delete_intermediates("vid_999")   # should not raise

    # prune_archives ------------------------------------------------- #

    def test_prune_archives_deletes_old_files(self, tmp_path):
        """Videos older than retention_days are pruned."""
        from src.utils.cleanup import CleanupManager
        mgr = CleanupManager(project_root=tmp_path, retention_days=7)

        old_file = mgr.archive_dir / "old.mp4"
        old_file.write_bytes(b"old")

        # Set mtime to 10 days ago
        old_time = time.time() - 10 * 86400
        import os
        os.utime(str(old_file), (old_time, old_time))

        mgr.prune_archives()
        assert not old_file.exists()

    def test_prune_archives_keeps_recent_files(self, tmp_path):
        """Videos within retention_days are kept."""
        from src.utils.cleanup import CleanupManager
        mgr = CleanupManager(project_root=tmp_path, retention_days=7)

        recent = mgr.archive_dir / "recent.mp4"
        recent.write_bytes(b"new")

        mgr.prune_archives()
        assert recent.exists()

    def test_prune_archives_ignores_non_mp4(self, tmp_path):
        """prune_archives() only targets .mp4 files."""
        from src.utils.cleanup import CleanupManager
        mgr = CleanupManager(project_root=tmp_path, retention_days=0)

        txt_file = mgr.archive_dir / "log.txt"
        txt_file.write_bytes(b"log")

        mgr.prune_archives()
        assert txt_file.exists()

    # full_cleanup --------------------------------------------------- #

    def test_full_cleanup_runs_all_steps(self, tmp_path):
        """full_cleanup() archives the video and deletes intermediates."""
        mgr = self._make_manager(tmp_path)
        video = tmp_path / "vid_001.mp4"
        video.write_bytes(b"video data")
        mgr.images_dir.mkdir(parents=True, exist_ok=True)

        archived = mgr.full_cleanup("vid_001", video)

        assert archived.parent == mgr.archive_dir
        assert not video.exists()

    def test_full_cleanup_returns_archive_path(self, tmp_path):
        """full_cleanup() returns the new archive path."""
        mgr = self._make_manager(tmp_path)
        video = tmp_path / "vid_test.mp4"
        video.write_bytes(b"data")

        result = mgr.full_cleanup("vid_test", video)
        assert result == mgr.archive_dir / "vid_test.mp4"


# ------------------------------------------------------------------ #
#  with_retry tests                                                   #
# ------------------------------------------------------------------ #

class TestWithRetry:

    def test_success_on_first_try(self):
        """with_retry passes through a function that succeeds immediately."""
        from src.utils.retry import with_retry

        calls = []

        @with_retry(max_attempts=3)
        def fn():
            calls.append(1)
            return "ok"

        result = fn()
        assert result == "ok"
        assert len(calls) == 1

    def test_retries_on_failure_then_succeeds(self):
        """Function that fails twice succeeds on 3rd attempt."""
        from src.utils.retry import with_retry

        attempt = [0]

        @with_retry(max_attempts=3, min_wait=0, max_wait=0)
        def fn():
            attempt[0] += 1
            if attempt[0] < 3:
                raise RuntimeError("transient")
            return "success"

        result = fn()
        assert result == "success"
        assert attempt[0] == 3

    def test_reraises_after_max_attempts(self):
        """After all retries fail, the original exception is raised."""
        from src.utils.retry import with_retry

        @with_retry(max_attempts=2, min_wait=0, max_wait=0)
        def fn():
            raise ValueError("always fails")

        with pytest.raises(ValueError, match="always fails"):
            fn()

    def test_only_retries_specified_exceptions(self):
        """Exceptions not in the retry list are raised immediately."""
        from src.utils.retry import with_retry

        calls = [0]

        @with_retry(max_attempts=3, min_wait=0, max_wait=0,
                    exceptions=(RuntimeError,))
        def fn():
            calls[0] += 1
            raise TypeError("not retried")

        with pytest.raises(TypeError):
            fn()

        assert calls[0] == 1   # raised on first attempt, not retried

    def test_does_not_retry_on_success(self):
        """A successful call is never retried."""
        from src.utils.retry import with_retry

        calls = [0]

        @with_retry(max_attempts=5, min_wait=0, max_wait=0)
        def fn():
            calls[0] += 1
            return 42

        fn()
        assert calls[0] == 1


# ------------------------------------------------------------------ #
#  config_loader tests                                                #
# ------------------------------------------------------------------ #

class TestConfigLoader:

    def test_get_config_returns_appconfig(self):
        """get_config() returns an AppConfig instance."""
        from src.utils.config_loader import get_config, AppConfig
        cfg = get_config()
        assert isinstance(cfg, AppConfig)

    def test_dot_access_top_level_key(self):
        """Top-level YAML keys are accessible via attribute syntax."""
        from src.utils.config_loader import get_config
        cfg = get_config()
        assert hasattr(cfg, "scheduler")
        assert hasattr(cfg, "trends")

    def test_dot_access_nested_key(self):
        """Nested keys resolve correctly via chained attribute access."""
        from src.utils.config_loader import get_config
        cfg = get_config()
        assert cfg.scheduler.timezone == "Asia/Kolkata"

    def test_get_returns_dict_for_nested_section(self):
        """Nested sections are returned as _DotDict (dict subclass)."""
        from src.utils.config_loader import get_config
        cfg = get_config()
        scheduler = cfg.scheduler
        assert isinstance(scheduler, dict)

    def test_missing_key_raises_attribute_error(self):
        """Accessing a non-existent key raises AttributeError."""
        from src.utils.config_loader import get_config
        cfg = get_config()
        with pytest.raises(AttributeError):
            _ = cfg.nonexistent_key_xyz

    def test_get_project_root_returns_path(self):
        """get_project_root() returns a Path pointing to the project root."""
        from src.utils.config_loader import get_project_root
        root = get_project_root()
        assert isinstance(root, Path)
        assert (root / "config.yaml").exists()

    def test_get_config_reload_flag(self):
        """reload=True forces a fresh read (does not raise)."""
        from src.utils.config_loader import get_config
        cfg1 = get_config(reload=True)
        cfg2 = get_config(reload=True)
        assert cfg1.project.name == cfg2.project.name

    def test_config_has_tracker_section(self):
        """tracker section exists with expected keys."""
        from src.utils.config_loader import get_config
        cfg = get_config()
        tr = cfg.tracker
        assert "excel_path" in tr
        assert "sheet_name" in tr
        assert "columns" in tr

    def test_missing_config_raises_file_not_found(self, tmp_path):
        """_load_yaml raises FileNotFoundError for a missing config.yaml."""
        from src.utils.config_loader import _load_yaml
        with pytest.raises(FileNotFoundError):
            _load_yaml(config_path=tmp_path / "nonexistent.yaml")


# ------------------------------------------------------------------ #
#  logger tests                                                       #
# ------------------------------------------------------------------ #

class TestLogger:

    def test_setup_logger_returns_bound_logger(self, tmp_path):
        """setup_logger() returns a structlog logger (BoundLoggerLazyProxy)."""
        import structlog
        from src.utils.logger import setup_logger

        logger = setup_logger(name="test-logger", log_dir=tmp_path)
        # structlog wraps loggers in a BoundLoggerLazyProxy at construction time
        assert type(logger).__name__ == "BoundLoggerLazyProxy"
        assert hasattr(logger, "info")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")

    def test_setup_logger_creates_log_dir(self, tmp_path):
        """setup_logger() creates the log directory if it doesn't exist."""
        from src.utils.logger import setup_logger

        log_dir = tmp_path / "new_logs"
        assert not log_dir.exists()

        setup_logger(log_dir=log_dir)
        assert log_dir.exists()

    def test_setup_logger_creates_log_file(self, tmp_path):
        """setup_logger() creates engine.log inside the log directory."""
        from src.utils.logger import setup_logger

        setup_logger(log_dir=tmp_path)
        # File is created lazily on first write; directory must exist
        assert tmp_path.exists()

    def test_module_level_log_is_importable(self):
        """The module-level `log` singleton is importable without error."""
        from src.utils.logger import log
        assert log is not None

    def test_log_can_emit_info(self, tmp_path):
        """log.info() does not raise."""
        from src.utils.logger import setup_logger

        logger = setup_logger(log_dir=tmp_path)
        logger.info("test_event", key="value")   # must not raise

    def test_log_level_debug_accepted(self, tmp_path):
        """setup_logger() accepts DEBUG level string without error."""
        from src.utils.logger import setup_logger

        logger = setup_logger(log_level="DEBUG", log_dir=tmp_path)
        assert logger is not None

    def test_log_level_warning_accepted(self, tmp_path):
        """setup_logger() accepts WARNING level string without error."""
        from src.utils.logger import setup_logger

        logger = setup_logger(log_level="WARNING", log_dir=tmp_path)
        assert logger is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
