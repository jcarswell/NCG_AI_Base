"""SecretServer integration module."""

import logging
from typing import Any, Dict, Optional

import requests

from ..exceptions import SecretServerError

logger = logging.getLogger(__name__)


class SecretServerClient:
    """Client for Delinea (formerly Thycotic) SecretServer API integration."""

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        timeout: int = 30,
    ):
        """Initialize SecretServer client.

        Args:
            url: SecretServer instance URL
            username: SecretServer API user
            password: SecretServer API password
            timeout: Request timeout in seconds
        """
        self.url = url.rstrip("/")
        self.username = username
        self.password = password
        self.timeout = timeout
        self.session = requests.Session()
        self._token: Optional[str] = None

    def _authenticate(self) -> None:
        """Authenticate with SecretServer API."""
        try:
            auth_url = f"{self.url}/api/v1/authentication/login"
            payload = {
                "username": self.username,
                "password": self.password,
                "grant_type": "password",
            }

            response = self.session.post(
                auth_url, json=payload, timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            self._token = data.get("access_token")

            if not self._token:
                raise SecretServerError("Failed to obtain authentication token")

            self.session.headers.update(
                {"Authorization": f"Bearer {self._token}"}
            )

            logger.info("Successfully authenticated with SecretServer")

        except requests.RequestException as e:
            logger.error(f"SecretServer authentication error: {str(e)}")
            raise SecretServerError(f"Failed to authenticate with SecretServer: {str(e)}")

    def get_secret(self, secret_id: int) -> Dict[str, Any]:
        """Retrieve a secret from SecretServer.

        Args:
            secret_id: ID of the secret to retrieve

        Returns:
            Secret dictionary

        Raises:
            SecretServerError: If secret retrieval fails
        """
        if not self._token:
            self._authenticate()

        try:
            url = f"{self.url}/api/v1/secrets/{secret_id}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"Failed to retrieve secret {secret_id}: {str(e)}")
            raise SecretServerError(f"Failed to retrieve secret: {str(e)}")

    def get_secret_field(self, secret_id: int, field_name: str) -> str:
        """Retrieve a specific field from a secret.

        Args:
            secret_id: ID of the secret
            field_name: Name of the field to retrieve

        Returns:
            Field value

        Raises:
            SecretServerError: If field retrieval fails
        """
        if not self._token:
            self._authenticate()

        try:
            url = f"{self.url}/api/v1/secrets/{secret_id}/fields/{field_name}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            return data.get("value", "")

        except requests.RequestException as e:
            logger.error(f"Failed to retrieve secret field: {str(e)}")
            raise SecretServerError(f"Failed to retrieve secret field: {str(e)}")

    def search_secrets(self, search_term: str) -> list:
        """Search for secrets by name.

        Args:
            search_term: Search term

        Returns:
            List of matching secrets

        Raises:
            SecretServerError: If search fails
        """
        if not self._token:
            self._authenticate()

        try:
            url = f"{self.url}/api/v1/secrets"
            params = {"searchText": search_term}

            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            return data.get("records", [])

        except requests.RequestException as e:
            logger.error(f"Failed to search secrets: {str(e)}")
            raise SecretServerError(f"Failed to search secrets: {str(e)}")
