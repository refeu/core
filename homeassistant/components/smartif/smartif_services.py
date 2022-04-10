"""Asynchronous Python client for SmartIf Services."""
from __future__ import annotations

from dataclasses import dataclass

from aiohttp.hdrs import METH_POST
from pydantic import parse_obj_as

from .smartif import SmartIf


@dataclass
class SmartIfServices:
    """Class for handling connections to SmartIf related with Services."""

    smart_if: SmartIf

    async def all(self) -> list[str]:
        """Get all Services."""
        return parse_obj_as(list[str], await self.smart_if.request("Services"))

    async def call(self, name: str) -> None:
        """Call the Service."""
        await self.smart_if.request(f"Services/{name}/Call", method=METH_POST)
