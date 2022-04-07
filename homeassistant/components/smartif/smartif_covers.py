"""Asynchronous Python client for SmartIf Covers."""
from __future__ import annotations

from dataclasses import dataclass
import urllib.parse

from aiohttp.hdrs import METH_POST
from pydantic import parse_obj_as

from .models import SmartIfCoverEntityInfo
from .smartif import SmartIf


@dataclass
class SmartIfCovers:
    """Class for handling connections to SmartIf related with Cover entities."""

    smart_if: SmartIf

    async def all(self) -> list[SmartIfCoverEntityInfo]:
        """Get all Cover entities."""
        return parse_obj_as(
            list[SmartIfCoverEntityInfo], await self.smart_if.request("Covers")
        )

    async def open_cover(self, _id: str) -> None:
        """Open the cover."""
        await self.smart_if.request(
            f"Covers/{urllib.parse.quote(_id)}/OpenCover", method=METH_POST
        )

    async def close_cover(self, _id: str) -> None:
        """Close cover."""
        await self.smart_if.request(
            f"Covers/{urllib.parse.quote(_id)}/CloseCover", method=METH_POST
        )

    async def set_cover_position(self, _id: str, position: int) -> None:
        """Move the cover to a specific position."""
        await self.smart_if.request(
            f"Covers/{urllib.parse.quote(_id)}/SetCoverPosition?position={position}",
            method=METH_POST,
        )

    async def stop_cover(self, _id: str) -> None:
        """Stop the cover."""
        await self.smart_if.request(
            f"Covers/{urllib.parse.quote(_id)}/StopCover", method=METH_POST
        )
