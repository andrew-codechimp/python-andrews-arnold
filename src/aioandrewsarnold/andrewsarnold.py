"""Homeassistant Client."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Self

from aiohttp import ClientSession
from aiohttp.hdrs import METH_POST
from yarl import URL

from aioandrewsarnold.exceptions import (
    AndrewsArnoldConnectionError,
    AndrewsArnoldError,
    AndrewsArnoldAuthenticationError,
    AndrewsArnoldValidationError,
    AndrewsArnoldNotFoundError,
    AndrewsArnoldBadRequestError,
)
from aioandrewsarnold.models import InfoResponse


VERSION = metadata.version(__package__)

API_HOST = "https://chaos2.aa.net.uk"


@dataclass
class AndrewsArnoldClient:
    """Main class for handling connections with Andrews & Arnold."""

    control_login: str | None = None
    control_password: str | None = None
    session: ClientSession | None = None
    request_timeout: int = 10
    _close_session: bool = False

    async def _request(
        self,
        uri: str,
        *,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Handle a request to Andrews & Arnold."""
        url = URL(API_HOST).joinpath(uri)

        headers = {
            "User-Agent": f"AioAndrewsArnold/{VERSION}",
            "Content-Type": "application/json",
        }

        if not data:
            data = {}

        if self.control_login and self.control_password:
            data["control_login"] = self.control_login
            data["control_password"] = self.control_password

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        kwargs = {
            "headers": headers,
            "params": params,
            "json": data,
        }

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(METH_POST, url, **kwargs)
        except asyncio.TimeoutError as exception:
            msg = "Timeout occurred while connecting to Andrews & Arnold"
            raise AndrewsArnoldConnectionError(msg) from exception

        if response.status == 400:
            text = await response.text()
            msg = "Bad request to Andrews & Arnold"
            raise AndrewsArnoldBadRequestError(
                msg,
                {"response": text},
            )

        if response.status == 401:
            msg = "Unauthorized access to Andrews & Arnold"
            raise AndrewsArnoldAuthenticationError(msg)

        if response.status == 422:
            text = await response.text()
            msg = "Andrews & Arnold validation error"
            raise AndrewsArnoldValidationError(
                msg,
                {"response": text},
            )

        if response.status == 404:
            text = await response.text()
            msg = "Command not found in Andrews & Arnold"
            raise AndrewsArnoldNotFoundError(
                msg,
                {"response": text},
            )

        content_type = response.headers.get("Content-Type", "")

        if "application/json" not in content_type:
            text = await response.text()
            msg = "Unexpected response from Andrews & Arnold"
            raise AndrewsArnoldError(
                msg,
                {"Content-Type": content_type, "response": text},
            )

        return await response.text()

    async def get_info(
        self,
    ) -> InfoResponse:
        """Get quotas."""
        response = await self._request("broadband/info")

        quota_response = InfoResponse.from_json(response)
        if quota_response.error:
            if quota_response.error == "Control authorisation failed":
                raise AndrewsArnoldAuthenticationError
            raise AndrewsArnoldError(quota_response.error)
        return quota_response

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The AndrewsArnoldClient object.
        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.
        """
        await self.close()
