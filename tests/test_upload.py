"""
Tests for Phase 8: YouTube Upload.

Covers:
- OAuthManager: token load/refresh/flow, credential persistence
- MetadataBuilder: title/description/tag construction, YouTube limits
- YouTubeUploader: insert request, progress loop, retry on server error

All Google API calls are mocked — tests run fully offline.

Run with: python -m pytest tests/test_upload.py -v
"""

import json
import os
import sys
import socket
from pathlib import Path
from unittest.mock import MagicMock, patch, call, PropertyMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


# ------------------------------------------------------------------ #
#  Helpers                                                            #
# ------------------------------------------------------------------ #

def _make_script(
    title="Ocean Waves Could Power the World",
    description="Scientists have discovered a way to harness wave energy.",
    tags=None,
    topic="ocean wave energy science",
    category="science",
) -> dict:
    return {
        "title":       title,
        "description": description,
        "tags":        tags or ["ocean", "energy", "science", "waves"],
        "topic":       topic,
        "category":    category,
    }


def _make_video_file(tmp_path: Path, name: str = "video.mp4", size: int = 1024 * 1024) -> Path:
    p = tmp_path / name
    p.write_bytes(b"\x00" * size)
    return p


def _fake_creds(valid=True, expired=False, has_refresh=True):
    """Build a mock Credentials object."""
    creds = MagicMock()
    creds.valid         = valid
    creds.expired       = expired
    creds.refresh_token = "rt_fake" if has_refresh else None
    creds.to_json.return_value = json.dumps({"token": "fake"})
    return creds


# ------------------------------------------------------------------ #
#  OAuthManager tests                                                 #
# ------------------------------------------------------------------ #

class TestOAuthManager:

    def test_get_service_uses_existing_valid_token(self, tmp_path):
        """If a valid token exists on disk, it is used without running OAuth."""
        from src.upload.oauth_manager import OAuthManager

        mgr = OAuthManager()
        mgr._token_path = tmp_path / "token.json"
        mgr._token_path.write_text(json.dumps({"token": "abc"}), encoding="utf-8")

        valid_creds = _fake_creds(valid=True, expired=False)

        with patch(
            "src.upload.oauth_manager.Credentials.from_authorized_user_file",
            return_value=valid_creds,
        ):
            with patch("src.upload.oauth_manager.build") as mock_build:
                mock_build.return_value = MagicMock()
                mgr.get_service()

        mock_build.assert_called_once_with("youtube", "v3", credentials=valid_creds)

    def test_get_service_refreshes_expired_token(self, tmp_path):
        """Expired token with refresh_token is refreshed without OAuth flow."""
        from src.upload.oauth_manager import OAuthManager

        mgr = OAuthManager()
        mgr._token_path = tmp_path / "token.json"
        mgr._token_path.write_text("{}", encoding="utf-8")

        expired_creds = _fake_creds(valid=False, expired=True, has_refresh=True)

        with patch(
            "src.upload.oauth_manager.Credentials.from_authorized_user_file",
            return_value=expired_creds,
        ):
            with patch("src.upload.oauth_manager.Request"):
                with patch("src.upload.oauth_manager.build", return_value=MagicMock()):
                    mgr.get_service()

        expired_creds.refresh.assert_called_once()

    def test_get_service_runs_oauth_flow_when_no_token(self, tmp_path):
        """No token on disk → OAuth flow is executed."""
        from src.upload.oauth_manager import OAuthManager

        mgr = OAuthManager()
        mgr._token_path   = tmp_path / "token.json"   # doesn't exist
        mgr._secrets_path = tmp_path / "secrets.json"  # doesn't exist

        new_creds = _fake_creds(valid=True)
        mock_flow = MagicMock()
        mock_flow.run_local_server.return_value = new_creds

        with patch.dict(os.environ, {
            "YOUTUBE_CLIENT_ID":     "fake_id",
            "YOUTUBE_CLIENT_SECRET": "fake_secret",
        }):
            with patch(
                "src.upload.oauth_manager.InstalledAppFlow.from_client_config",
                return_value=mock_flow,
            ):
                with patch("src.upload.oauth_manager.build", return_value=MagicMock()):
                    mgr.get_service()

        mock_flow.run_local_server.assert_called_once()

    def test_token_saved_after_oauth_flow(self, tmp_path):
        """After a successful OAuth flow, credentials are written to disk."""
        from src.upload.oauth_manager import OAuthManager

        mgr = OAuthManager()
        mgr._token_path   = tmp_path / "token.json"
        mgr._secrets_path = tmp_path / "secrets.json"

        new_creds = _fake_creds(valid=True)
        mock_flow = MagicMock()
        mock_flow.run_local_server.return_value = new_creds

        with patch.dict(os.environ, {
            "YOUTUBE_CLIENT_ID":     "cid",
            "YOUTUBE_CLIENT_SECRET": "csec",
        }):
            with patch(
                "src.upload.oauth_manager.InstalledAppFlow.from_client_config",
                return_value=mock_flow,
            ):
                with patch("src.upload.oauth_manager.build", return_value=MagicMock()):
                    mgr.get_service()

        assert mgr._token_path.exists()

    def test_build_flow_uses_secrets_file_when_present(self, tmp_path):
        """client_secrets.json is preferred over env vars when it exists."""
        from src.upload.oauth_manager import OAuthManager

        mgr = OAuthManager()
        mgr._secrets_path = tmp_path / "client_secrets.json"
        mgr._secrets_path.write_text("{}", encoding="utf-8")

        with patch(
            "src.upload.oauth_manager.InstalledAppFlow.from_client_secrets_file",
            return_value=MagicMock(),
        ) as mock_secrets:
            with patch(
                "src.upload.oauth_manager.InstalledAppFlow.from_client_config",
            ) as mock_config:
                mgr._build_flow()

        mock_secrets.assert_called_once()
        mock_config.assert_not_called()

    def test_build_flow_raises_when_no_credentials(self, tmp_path):
        """Raises ValueError if neither secrets file nor env vars are present."""
        from src.upload.oauth_manager import OAuthManager

        mgr = OAuthManager()
        mgr._secrets_path = tmp_path / "nonexistent.json"

        with patch.dict(os.environ, {
            "YOUTUBE_CLIENT_ID": "",
            "YOUTUBE_CLIENT_SECRET": "",
        }):
            with pytest.raises(ValueError, match="OAuth credentials not configured"):
                mgr._build_flow()

    def test_revoke_token_deletes_file(self, tmp_path):
        """revoke_token() removes the token file."""
        from src.upload.oauth_manager import OAuthManager

        mgr = OAuthManager()
        mgr._token_path = tmp_path / "token.json"
        mgr._token_path.write_text("{}", encoding="utf-8")

        mgr.revoke_token()
        assert not mgr._token_path.exists()

    def test_load_credentials_returns_none_when_no_file(self, tmp_path):
        """_load_credentials returns None if token file is missing."""
        from src.upload.oauth_manager import OAuthManager

        mgr = OAuthManager()
        mgr._token_path = tmp_path / "missing.json"

        assert mgr._load_credentials() is None

    def test_fallback_to_console_when_local_server_fails(self, tmp_path):
        """If run_local_server raises, falls back to run_console."""
        from src.upload.oauth_manager import OAuthManager

        mgr = OAuthManager()
        mgr._token_path   = tmp_path / "token.json"
        mgr._secrets_path = tmp_path / "secrets.json"

        console_creds = _fake_creds(valid=True)
        mock_flow = MagicMock()
        mock_flow.run_local_server.side_effect = OSError("browser unavailable")
        mock_flow.run_console.return_value = console_creds

        with patch.dict(os.environ, {
            "YOUTUBE_CLIENT_ID": "cid", "YOUTUBE_CLIENT_SECRET": "csec"
        }):
            with patch(
                "src.upload.oauth_manager.InstalledAppFlow.from_client_config",
                return_value=mock_flow,
            ):
                result = mgr._run_oauth_flow()

        assert result is console_creds
        mock_flow.run_console.assert_called_once()


# ------------------------------------------------------------------ #
#  MetadataBuilder tests                                              #
# ------------------------------------------------------------------ #

class TestMetadataBuilder:

    def _builder(self):
        from src.upload.metadata_builder import MetadataBuilder
        return MetadataBuilder()

    def test_build_returns_required_keys(self):
        """build() dict contains all keys needed by YouTube API."""
        builder = self._builder()
        result  = builder.build(_make_script(), "vid_001")

        required = {
            "title", "description", "tags",
            "categoryId", "privacyStatus", "selfDeclaredMadeForKids",
        }
        assert required.issubset(result.keys())

    def test_title_includes_shorts_suffix(self):
        """Title has ' #Shorts' appended when it fits."""
        builder = self._builder()
        result  = builder.build(_make_script(title="Ocean Power"), "v1")
        assert "#Shorts" in result["title"]

    def test_title_truncated_to_100_chars(self):
        """Titles longer than 100 chars are truncated."""
        long_title = "A" * 200
        builder    = self._builder()
        result     = builder.build(_make_script(title=long_title), "v1")
        assert len(result["title"]) <= 100

    def test_title_falls_back_to_topic_when_no_title(self):
        """When script has no 'title' key, topic is used instead."""
        builder = self._builder()
        script  = _make_script()
        del script["title"]
        result = builder.build(script, "v1")
        assert "ocean" in result["title"].lower()

    def test_title_falls_back_to_video_id(self):
        """When neither title nor topic, video_id becomes the title."""
        builder = self._builder()
        script  = {"description": "desc", "tags": [], "category": "general"}
        result  = builder.build(script, "vid_fallback")
        assert "vid_fallback" in result["title"]

    def test_description_includes_hashtags(self):
        """Description contains the configured #Shorts hashtags."""
        builder = self._builder()
        result  = builder.build(_make_script(), "v1")
        assert "#Shorts" in result["description"]

    def test_description_includes_script_description(self):
        """Script description text appears in the video description."""
        builder = self._builder()
        desc    = "Scientists found that ocean waves can generate electricity."
        result  = builder.build(_make_script(description=desc), "v1")
        assert desc in result["description"]

    def test_description_truncated_to_5000_chars(self):
        """Very long descriptions are capped at 5 000 characters."""
        builder  = self._builder()
        long_desc = "X" * 10_000
        result   = builder.build(_make_script(description=long_desc), "v1")
        assert len(result["description"]) <= 5_000

    def test_tags_merged_with_defaults(self):
        """Script tags and config default_tags both appear in tags list."""
        builder = self._builder()
        result  = builder.build(_make_script(tags=["unique_script_tag"]), "v1")
        tag_str = " ".join(result["tags"])
        assert "unique_script_tag" in tag_str
        # Default tags (from config) — "shorts" and "facts" should be present
        assert any(t in ("shorts", "facts", "trending") for t in result["tags"])

    def test_tags_deduplicated(self):
        """Duplicate tags (from script + defaults) appear only once."""
        builder = self._builder()
        # "shorts" is in both script tags and default_tags
        result  = builder.build(_make_script(tags=["shorts", "facts"]), "v1")
        assert result["tags"].count("shorts") == 1

    def test_tags_capped_at_500_chars(self):
        """Total joined tag length never exceeds 500 characters."""
        builder    = self._builder()
        many_tags  = [f"longtag{i:04d}" for i in range(100)]  # 100 long tags
        result     = builder.build(_make_script(tags=many_tags), "v1")
        total_chars = sum(len(t) for t in result["tags"])
        assert total_chars <= 500

    def test_tags_capped_at_20_tags(self):
        """At most 20 tags are returned."""
        builder   = self._builder()
        many_tags = [f"tag{i}" for i in range(50)]
        result    = builder.build(_make_script(tags=many_tags), "v1")
        assert len(result["tags"]) <= 20

    def test_privacy_from_config(self):
        """privacyStatus matches the config value."""
        builder = self._builder()
        result  = builder.build(_make_script(), "v1")
        assert result["privacyStatus"] in ("public", "private", "unlisted")

    def test_category_id_is_string(self):
        """categoryId is always a string (YouTube API requires it)."""
        builder = self._builder()
        result  = builder.build(_make_script(), "v1")
        assert isinstance(result["categoryId"], str)

    def test_made_for_kids_is_bool(self):
        """selfDeclaredMadeForKids is a boolean."""
        builder = self._builder()
        result  = builder.build(_make_script(), "v1")
        assert isinstance(result["selfDeclaredMadeForKids"], bool)


# ------------------------------------------------------------------ #
#  YouTubeUploader tests                                              #
# ------------------------------------------------------------------ #

class TestYouTubeUploader:

    def _uploader_with_mock_service(self, mock_service=None):
        from src.upload.youtube_uploader import YouTubeUploader
        uploader = YouTubeUploader()
        uploader._service = mock_service or MagicMock()
        return uploader

    def _mock_insert_request(self, video_id="yt_abc123", chunks=1):
        """
        Build a mock insert request whose next_chunk() returns progress
        then a final response dict.
        """
        request = MagicMock()
        # Simulate: (status, None) for each chunk, then (None, response)
        side_effects = []
        for i in range(chunks):
            status = MagicMock()
            status.progress.return_value = (i + 1) / (chunks + 1)
            side_effects.append((status, None))
        # Final chunk: response
        side_effects.append((None, {"id": video_id}))
        request.next_chunk.side_effect = side_effects
        return request

    def test_upload_returns_youtube_url(self, tmp_path):
        """upload() returns the correct youtu.be URL."""
        from src.upload.youtube_uploader import YouTubeUploader

        video = _make_video_file(tmp_path)
        mock_request = self._mock_insert_request("vid123")

        uploader = self._uploader_with_mock_service()
        uploader._service.videos.return_value.insert.return_value = mock_request

        with patch("src.upload.youtube_uploader.MediaFileUpload"):
            result = uploader.upload(video, _make_script(), "internal_id")

        assert result == "https://youtu.be/vid123"

    def test_upload_calls_insert_with_title_and_description(self, tmp_path):
        """videos().insert() is called with the correct snippet body."""
        from src.upload.youtube_uploader import YouTubeUploader

        video    = _make_video_file(tmp_path)
        metadata = {
            "title":                   "Test Title #Shorts",
            "description":             "Test description",
            "tags":                    ["tag1", "tag2"],
            "categoryId":              "22",
            "privacyStatus":           "public",
            "selfDeclaredMadeForKids": False,
        }

        mock_request = self._mock_insert_request()
        uploader     = self._uploader_with_mock_service()
        mock_insert  = uploader._service.videos.return_value.insert
        mock_insert.return_value = mock_request

        with patch("src.upload.youtube_uploader.MediaFileUpload"):
            uploader.upload(video, metadata, "v1")

        call_kwargs = mock_insert.call_args[1]
        body = call_kwargs["body"]
        assert body["snippet"]["title"]       == "Test Title #Shorts"
        assert body["snippet"]["description"] == "Test description"
        assert body["status"]["privacyStatus"] == "public"

    def test_upload_raises_file_not_found(self, tmp_path):
        """FileNotFoundError when video_path doesn't exist."""
        from src.upload.youtube_uploader import YouTubeUploader

        uploader = self._uploader_with_mock_service()
        with pytest.raises(FileNotFoundError, match="Video file not found"):
            uploader.upload(tmp_path / "ghost.mp4", _make_script(), "v1")

    def test_upload_retries_on_500_error(self, tmp_path):
        """Server errors (500) trigger retries with backoff."""
        from src.upload.youtube_uploader import YouTubeUploader
        from googleapiclient.errors import HttpError

        video = _make_video_file(tmp_path)

        # First two calls raise 500; third succeeds
        server_err = HttpError(resp=MagicMock(status=500), content=b"Server Error")
        success_request = self._mock_insert_request("ok_vid")

        uploader   = self._uploader_with_mock_service()
        call_count = {"n": 0}

        def insert_side_effect(**kwargs):
            call_count["n"] += 1
            if call_count["n"] <= 2:
                req = MagicMock()
                req.next_chunk.side_effect = server_err
                return req
            return success_request

        uploader._service.videos.return_value.insert.side_effect = insert_side_effect

        with patch("src.upload.youtube_uploader.MediaFileUpload"):
            with patch("src.upload.youtube_uploader.time.sleep"):
                result = uploader.upload(video, _make_script(), "v1")

        assert result == "https://youtu.be/ok_vid"
        assert call_count["n"] == 3    # two failures + one success

    def test_upload_raises_after_max_retries(self, tmp_path):
        """RuntimeError after MAX_RETRIES consecutive server errors."""
        from src.upload.youtube_uploader import YouTubeUploader, MAX_RETRIES
        from googleapiclient.errors import HttpError

        video = _make_video_file(tmp_path)

        server_err = HttpError(resp=MagicMock(status=503), content=b"Unavailable")
        bad_request = MagicMock()
        bad_request.next_chunk.side_effect = server_err

        uploader = self._uploader_with_mock_service()
        uploader._service.videos.return_value.insert.return_value = bad_request

        with patch("src.upload.youtube_uploader.MediaFileUpload"):
            with patch("src.upload.youtube_uploader.time.sleep"):
                with pytest.raises(RuntimeError, match="YouTube upload"):
                    uploader.upload(video, _make_script(), "v1")

    def test_upload_raises_immediately_on_4xx_error(self, tmp_path):
        """Client errors (403) are raised immediately without retrying."""
        from src.upload.youtube_uploader import YouTubeUploader
        from googleapiclient.errors import HttpError

        video = _make_video_file(tmp_path)

        client_err  = HttpError(resp=MagicMock(status=403), content=b"Forbidden")
        bad_request = MagicMock()
        bad_request.next_chunk.side_effect = client_err

        uploader   = self._uploader_with_mock_service()
        call_count = {"n": 0}

        def insert_side_effect(**kwargs):
            call_count["n"] += 1
            return bad_request

        uploader._service.videos.return_value.insert.side_effect = insert_side_effect

        with patch("src.upload.youtube_uploader.MediaFileUpload"):
            with pytest.raises(RuntimeError, match="HTTP 403"):
                uploader.upload(video, _make_script(), "v1")

        # Should only call insert once (no retry for 4xx)
        assert call_count["n"] == 1

    def test_upload_progress_logged_for_multi_chunk(self, tmp_path):
        """Progress is logged for each chunk during upload."""
        from src.upload.youtube_uploader import YouTubeUploader

        video = _make_video_file(tmp_path, size=5 * 1024 * 1024)

        # 3 progress chunks before final response
        mock_request = self._mock_insert_request("progress_vid", chunks=3)

        uploader = self._uploader_with_mock_service()
        uploader._service.videos.return_value.insert.return_value = mock_request

        with patch("src.upload.youtube_uploader.MediaFileUpload"):
            result = uploader.upload(video, _make_script(), "v1")

        # next_chunk called 4 times (3 progress + 1 final)
        assert mock_request.next_chunk.call_count == 4
        assert result == "https://youtu.be/progress_vid"

    def test_execute_upload_raises_when_no_id_in_response(self):
        """RuntimeError if the API response contains no video id."""
        from src.upload.youtube_uploader import YouTubeUploader

        request = MagicMock()
        request.next_chunk.return_value = (None, {"kind": "youtube#video"})  # no "id"

        with pytest.raises(RuntimeError, match="no video ID"):
            YouTubeUploader._execute_upload(request)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
