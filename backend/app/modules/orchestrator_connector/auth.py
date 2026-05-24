"""
OAuth authentication handler for UiPath Orchestrator.
Manages token acquisition, refresh, and expiration.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import httpx
import logging

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError, ExternalServiceError
from app.core.cache import cache_set, cache_get, make_cache_key
from app.modules.orchestrator_connector.dto import OAuthTokenDTO

logger = logging.getLogger(__name__)
settings = get_settings()


class OAuthClient:
    """Handles OAuth authentication with UiPath Orchestrator."""

    def __init__(self):
        """Initialize OAuth client."""
        self.token_url = f"{settings.ORCHESTRATOR_URL}/oauth/token"
        self.client_id = settings.ORCHESTRATOR_API_KEY
        self.tenant = settings.ORCHESTRATOR_TENANT
        self.current_token: Optional[OAuthTokenDTO] = None
        self.token_expiry: Optional[datetime] = None
        self.cache_key = make_cache_key("orchestrator", "oauth_token")

    async def get_token(self, force_refresh: bool = False) -> str:
        """
        Get valid OAuth token.

        Uses cached token if available and not expired.
        Automatically refreshes if expired.

        Args:
            force_refresh: Force token refresh

        Returns:
            Valid access token

        Raises:
            AuthenticationError: If token acquisition fails
        """
        # Check if we need a new token
        if not force_refresh and self._is_token_valid():
            return self.current_token.access_token

        # Try to refresh if we have a refresh token
        if not force_refresh and self.current_token and self.current_token.refresh_token:
            try:
                await self._refresh_token()
                return self.current_token.access_token
            except Exception as e:
                logger.warning(f"Token refresh failed: {str(e)}, acquiring new token")

        # Acquire new token
        await self._acquire_token()
        return self.current_token.access_token

    async def _acquire_token(self) -> None:
        """
        Acquire new OAuth token from Orchestrator.

        Raises:
            AuthenticationError: If token acquisition fails
        """
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_id,
                    "scope": "OR.Execution OR.Jobs OR.Queues",
                }

                if self.tenant:
                    payload["tenant"] = self.tenant

                response = await client.post(
                    self.token_url,
                    data=payload,
                    timeout=10.0,
                )
                response.raise_for_status()

                token_data = response.json()
                self.current_token = OAuthTokenDTO(**token_data)

                # Calculate expiry with 5-minute buffer
                self.token_expiry = datetime.now(timezone.utc) + timedelta(
                    seconds=self.current_token.expires_in - 300
                )

                # Cache token
                await cache_set(
                    self.cache_key,
                    self.current_token.model_dump_json(),
                    ttl=self.current_token.expires_in - 300,
                )

                logger.info("OAuth token acquired successfully")

        except httpx.HTTPStatusError as e:
            logger.error(f"OAuth token acquisition failed: {e.response.text}")
            raise AuthenticationError(
                "Failed to authenticate with UiPath Orchestrator"
            )
        except Exception as e:
            logger.error(f"OAuth token acquisition error: {str(e)}")
            raise ExternalServiceError(
                "UiPath Orchestrator",
                f"Token acquisition failed: {str(e)}",
            )

    async def _refresh_token(self) -> None:
        """
        Refresh OAuth token using refresh token.

        Raises:
            AuthenticationError: If refresh fails
        """
        if not self.current_token or not self.current_token.refresh_token:
            raise AuthenticationError("No refresh token available")

        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "grant_type": "refresh_token",
                    "refresh_token": self.current_token.refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_id,
                }

                response = await client.post(
                    self.token_url,
                    data=payload,
                    timeout=10.0,
                )
                response.raise_for_status()

                token_data = response.json()
                self.current_token = OAuthTokenDTO(**token_data)

                # Calculate expiry with 5-minute buffer
                self.token_expiry = datetime.now(timezone.utc) + timedelta(
                    seconds=self.current_token.expires_in - 300
                )

                # Cache token
                await cache_set(
                    self.cache_key,
                    self.current_token.model_dump_json(),
                    ttl=self.current_token.expires_in - 300,
                )

                logger.info("OAuth token refreshed successfully")

        except httpx.HTTPStatusError as e:
            logger.error(f"Token refresh failed: {e.response.text}")
            # Reset token and acquire new one
            self.current_token = None
            raise
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            raise

    def _is_token_valid(self) -> bool:
        """
        Check if current token is valid.

        Returns:
            True if token is valid and not expired
        """
        if not self.current_token or not self.token_expiry:
            return False

        # Check if token expires within next minute
        return datetime.now(timezone.utc) < (self.token_expiry - timedelta(seconds=60))

    def reset(self) -> None:
        """Reset token state."""
        self.current_token = None
        self.token_expiry = None


# Singleton instance
_oauth_client: Optional[OAuthClient] = None


def get_oauth_client() -> OAuthClient:
    """
    Get or create OAuth client singleton.

    Returns:
        OAuthClient instance
    """
    global _oauth_client
    if _oauth_client is None:
        _oauth_client = OAuthClient()
    return _oauth_client
