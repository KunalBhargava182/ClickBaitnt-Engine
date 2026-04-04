"""
YouTube OAuth 2.0 manager.

Handles the full credentials lifecycle:
  1. Load existing token from data/youtube_token.json.
  2. Refresh if expired (uses refresh_token automatically).
  3. Run browser-based OAuth flow for first-time setup.
  4. Persist the token after every change.

Client credentials are resolved in priority order:
  a. data/client_secrets.json  (standard Google OAuth JSON download)
  b. YOUTUBE_CLIENT_ID + YOUTUBE_CLIENT_SECRET env vars

Usage:
    from src.upload.oauth_manager import OAuthManager
    service = OAuthManager().get_service()
    # service is a googleapiclient Resource for YouTube Data API v3
"""

import json
import os
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.utils.config_loader import get_project_root
from src.utils.logger import log

# The only scope we need: upload videos on behalf of the user
_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# YouTube Data API version
_API_SERVICE = "youtube"
_API_VERSION  = "v3"


class OAuthManager:
    """
    Manages YouTube OAuth 2.0 credentials and API service construction.

    Usage:
        mgr     = OAuthManager()
        service = mgr.get_service()
    """

    def __init__(self) -> None:
        root = get_project_root()
        self._token_path   = root / "data" / "youtube_token.json"
        self._secrets_path = root / "data" / "client_secrets.json"
        self._token_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def get_service(self):
        """
        Return an authenticated YouTube Data API v3 service resource.

        Runs OAuth flow on first use; subsequent calls load the saved token.

        Returns:
            googleapiclient.discovery.Resource for YouTube Data API v3.

        Raises:
            ValueError: OAuth credentials not configured.
            RuntimeError: OAuth flow failed.
        """
        creds = self._load_credentials()

        if creds and creds.valid:
            log.info("oauth_manager.using_existing_token")
        elif creds and creds.expired and creds.refresh_token:
            log.info("oauth_manager.refreshing_token")
            creds.refresh(Request())
            self._save_credentials(creds)
            log.info("oauth_manager.token_refreshed")
        else:
            log.info("oauth_manager.running_oauth_flow")
            creds = self._run_oauth_flow()
            self._save_credentials(creds)
            log.info("oauth_manager.token_saved", path=str(self._token_path))

        return build(_API_SERVICE, _API_VERSION, credentials=creds)

    def revoke_token(self) -> None:
        """Delete the stored token (forces re-auth on next get_service call)."""
        if self._token_path.exists():
            self._token_path.unlink()
            log.info("oauth_manager.token_revoked")

    # ------------------------------------------------------------------ #
    #  Credential helpers                                                  #
    # ------------------------------------------------------------------ #

    def _load_credentials(self) -> Optional[Credentials]:
        """Load credentials from the token file, or return None."""
        if not self._token_path.exists():
            return None
        try:
            creds = Credentials.from_authorized_user_file(
                str(self._token_path), _SCOPES
            )
            return creds
        except Exception as exc:
            log.warning(
                "oauth_manager.load_token_failed",
                error=str(exc),
            )
            return None

    def _save_credentials(self, creds: Credentials) -> None:
        """Persist credentials to the token file."""
        self._token_path.write_text(creds.to_json(), encoding="utf-8")

    def _run_oauth_flow(self) -> Credentials:
        """
        Execute the InstalledApp OAuth flow.

        Tries a local redirect server (opens browser tab) first.
        Falls back to console-based flow for headless environments.
        """
        flow = self._build_flow()

        try:
            creds = flow.run_local_server(port=0, open_browser=True)
            log.info("oauth_manager.flow_completed_local_server")
            return creds
        except Exception as exc:
            log.warning(
                "oauth_manager.local_server_failed_trying_console",
                error=str(exc)[:100],
            )

        try:
            creds = flow.run_console()
            log.info("oauth_manager.flow_completed_console")
            return creds
        except Exception as exc:
            raise RuntimeError(f"OAuth flow failed: {exc}") from exc

    def _build_flow(self) -> InstalledAppFlow:
        """
        Build an InstalledAppFlow from client_secrets.json or env vars.
        """
        if self._secrets_path.exists():
            log.info(
                "oauth_manager.using_client_secrets_file",
                path=str(self._secrets_path),
            )
            return InstalledAppFlow.from_client_secrets_file(
                str(self._secrets_path), _SCOPES
            )

        # Build from environment variables
        client_id     = os.environ.get("YOUTUBE_CLIENT_ID", "").strip()
        client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "").strip()

        if not client_id or not client_secret:
            raise ValueError(
                "YouTube OAuth credentials not configured.\n"
                "Options:\n"
                "  A) Download client_secrets.json from Google Cloud Console "
                "and place it in data/\n"
                "  B) Set YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET in .env"
            )

        log.info("oauth_manager.using_env_vars_for_credentials")

        client_config = {
            "installed": {
                "client_id":     client_id,
                "client_secret": client_secret,
                "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
                "token_uri":     "https://oauth2.googleapis.com/token",
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
            }
        }
        return InstalledAppFlow.from_client_config(client_config, _SCOPES)
