"""Asynchronous Python client for SmartIf."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
import socket
from typing import Any, cast

from aiohttp import ClientResponse
from aiohttp.client import ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_GET
import async_timeout
from yarl import URL

from .exceptions import SmartIfConnectionError


@dataclass
class SmartIf:
    """Main class for handling connections to SmartIf."""

    host: str
    port: int = 42443
    request_timeout: int = 8
    session: ClientSession | None = None

    _close_session: bool = False

    async def _do_request(
        self, uri: str, *, method: str = METH_GET, data: dict | None = None
    ) -> ClientResponse:
        url = URL.build(scheme="http", host=self.host, port=self.port, path="/").join(
            URL(uri)
        )

        headers = {
            "User-Agent": "PythonSmartIf",
            "Accept": "application/json, text/plain, */*",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        response: ClientResponse

        try:
            async with async_timeout.timeout(self.request_timeout):
                response = await self.session.request(
                    method, url, json=data, headers=headers
                )
                response.raise_for_status()
        except asyncio.TimeoutError as exception:
            raise SmartIfConnectionError(
                "Timeout occurred while connecting to SmartIf"
            ) from exception
        except (ClientError, ClientResponseError, socket.gaierror) as exception:
            raise SmartIfConnectionError(
                "Error occurred while communicating with SmartIf"
            ) from exception

        return response

    async def request(
        self, uri: str, *, method: str = METH_GET, data: dict | None = None
    ) -> dict[str, Any] | str:
        """Handle a request to a SmartIf.

        A generic method for sending/handling HTTP requests done against
        the SmartIf API.
        Args:
                uri: Request URI, for example, 'info'
                method: HTTP Method to use.
                data: Dictionary of data to send to the SmartIf.
        Returns:
                A Python dictionary (JSON decoded) with the response from
                the SmartIf API.
        Raises:
                SmartIfConnectionError: An error occurred while communicating with
                        the SmartIf.
                SmartIfError: Received an unexpected response from the SmartIf
                        API.
        """
        response: ClientResponse = await self._do_request(uri, method=method, data=data)
        content_type = response.headers.get("Content-Type", "")

        if "application/json" not in content_type:
            return await response.text()

        return await response.json()

    async def request_binary(
        self, uri: str, *, method: str = METH_GET, data: dict | None = None
    ) -> bytes:
        """Handle a request to a SmartIf.

        A generic method for sending/handling HTTP binary requests done against
        the SmartIf API.
        Args:
                uri: Request URI, for example, 'info'
                method: HTTP Method to use.
                data: Dictionary of data to send to the SmartIf.
        Returns:
                The bytes with the response from the SmartIf API.
        Raises:
                SmartIfConnectionError: An error occurred while communicating with
                        the SmartIf.
                SmartIfError: Received an unexpected response from the SmartIf
                        API.
        """
        response: ClientResponse = await self._do_request(uri, method=method, data=data)
        return await response.read()

    async def devices_state(self) -> dict[str, Any]:
        """Get the devices state."""
        return cast(dict[str, Any], await self.request("DevicesState"))

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> SmartIf:
        """Async enter.

        Returns:
            The SmartIf object.
        """
        return self

    async def __aexit__(self, *_exc_info) -> None:
        """Async exit.

        Args:
            _exc_info: Exec type.
        """
        await self.close()
