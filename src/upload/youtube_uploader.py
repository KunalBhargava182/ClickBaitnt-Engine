"""
YouTube video uploader.

Uses the YouTube Data API v3 resumable upload protocol, which:
  - Supports files of any size (required > 5 MB).
  - Automatically resumes after transient network failures.
  - Reports progress in 10 MB chunks.

Retry policy:
  - Up to MAX_RETRIES attempts on server errors (5xx) or network errors.
  - Exponential backoff: 2^attempt seconds between retries.
  - Permanent client errors (4xx except 429) are raised immediately.

Usage:
    uploader = YouTubeUploader()
    url = uploader.upload(
        video_path = Path("output/videos/vid_001.mp4"),
        metadata   = metadata_builder.build(script, "vid_001"),
        video_id   = "vid_001",
    )
    # url: "https://youtu.be/{youtube_video_id}"
"""

import socket
import time
from pathlib import Path

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from src.upload.oauth_manager import OAuthManager
from src.utils.logger import log

# Resumable upload chunk size: 10 MB
_CHUNK_SIZE  = 10 * 1024 * 1024

# Retry settings
MAX_RETRIES        = 3
_RETRYABLE_STATUS  = {500, 502, 503, 504}   # server errors worth retrying

# YouTube video URL template
_YT_URL = "https://youtu.be/{video_id}"


class YouTubeUploader:
    """
    Uploads a video file to YouTube using the resumable upload API.

    The OAuthManager is called once on the first upload; the service
    resource is cached for the lifetime of this object.

    Usage:
        uploader = YouTubeUploader()
        url      = uploader.upload(video_path, metadata, video_id)
    """

    def __init__(self) -> None:
        self._oauth   = OAuthManager()
        self._service = None   # lazy-initialised

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def upload(
        self,
        video_path: Path,
        metadata:   dict,
        video_id:   str,
    ) -> str:
        """
        Upload a video to YouTube and return its public URL.

        Args:
            video_path: Path to the MP4 file to upload.
            metadata:   Dict built by MetadataBuilder.build().
            video_id:   Internal identifier (used only for logging).

        Returns:
            YouTube URL string: "https://youtu.be/{yt_video_id}"

        Raises:
            FileNotFoundError: video_path does not exist.
            RuntimeError:      Upload failed after all retries.
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        size_mb = video_path.stat().st_size / (1024 * 1024)
        log.info(
            "youtube_uploader.upload.start",
            video_id=video_id,
            file=video_path.name,
            size_mb=round(size_mb, 2),
        )

        service = self._get_service()
        request = self._build_insert_request(service, video_path, metadata)

        last_exc: Exception | None = None

        for attempt in range(MAX_RETRIES):
            try:
                yt_id = self._execute_upload(request)
                url   = _YT_URL.format(video_id=yt_id)

                log.info(
                    "youtube_uploader.upload.success",
                    video_id=video_id,
                    youtube_id=yt_id,
                    url=url,
                )
                return url

            except HttpError as exc:
                status = exc.resp.status if exc.resp else 0

                if status in _RETRYABLE_STATUS and attempt < MAX_RETRIES - 1:
                    wait = 2 ** attempt
                    log.warning(
                        "youtube_uploader.server_error_retry",
                        status=status,
                        attempt=attempt + 1,
                        wait_s=wait,
                    )
                    time.sleep(wait)
                    # Rebuild the request for the next attempt (fresh MediaUpload)
                    request = self._build_insert_request(service, video_path, metadata)
                    last_exc = exc
                    continue

                raise RuntimeError(
                    f"YouTube upload failed (HTTP {status}): {exc}"
                ) from exc

            except (socket.error, ConnectionError, TimeoutError) as exc:
                if attempt < MAX_RETRIES - 1:
                    wait = 2 ** attempt
                    log.warning(
                        "youtube_uploader.network_error_retry",
                        error=str(exc)[:100],
                        attempt=attempt + 1,
                        wait_s=wait,
                    )
                    time.sleep(wait)
                    last_exc = exc
                    continue

                raise RuntimeError(
                    f"YouTube upload failed (network error): {exc}"
                ) from exc

        raise RuntimeError(
            f"YouTube upload exhausted {MAX_RETRIES} attempts. "
            f"Last error: {last_exc}"
        )

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _get_service(self):
        """Return the cached YouTube API service (initialise on first call)."""
        if self._service is None:
            self._service = self._oauth.get_service()
        return self._service

    def _build_insert_request(self, service, video_path: Path, metadata: dict):
        """
        Construct a videos.insert() resumable upload request.

        The body uses the 'snippet' and 'status' parts; 'localizations'
        and other advanced parts are omitted for simplicity.
        """
        body = {
            "snippet": {
                "title":       metadata["title"],
                "description": metadata["description"],
                "tags":        metadata.get("tags", []),
                "categoryId":  metadata.get("categoryId", "22"),
            },
            "status": {
                "privacyStatus":           metadata.get("privacyStatus", "public"),
                "selfDeclaredMadeForKids": metadata.get("selfDeclaredMadeForKids", False),
            },
        }

        media = MediaFileUpload(
            str(video_path),
            mimetype="video/mp4",
            resumable=True,
            chunksize=_CHUNK_SIZE,
        )

        return service.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

    @staticmethod
    def _execute_upload(request) -> str:
        """
        Drive the resumable upload loop until completion.

        Returns:
            YouTube video ID string.
        """
        response = None
        last_progress = -1

        while response is None:
            status, response = request.next_chunk()

            if status:
                pct = int(status.progress() * 100)
                if pct != last_progress:
                    log.info("youtube_uploader.progress", percent=pct)
                    last_progress = pct

        yt_video_id: str = response.get("id", "")
        if not yt_video_id:
            raise RuntimeError(
                f"Upload completed but no video ID in response: {response}"
            )

        return yt_video_id
