"""Asynchronous Python client for SmartIf Sirens."""
from __future__ import annotations

from dataclasses import dataclass

from aiohttp.hdrs import METH_POST
from pydantic import parse_obj_as

from .models import SmartIfEntityInfo
from .smartif import SmartIf


@dataclass
class SmartIfSirens:
    """Class for handling connections to SmartIf related with Siren entities."""

    smart_if: SmartIf

    async def all(self) -> list[SmartIfEntityInfo]:
        """Get all Siren entities."""
        return parse_obj_as(
            list[SmartIfEntityInfo], await self.smart_if.request("Sirens")
        )

    async def turn_on(self, _id: str) -> None:
        """Turn the device on."""
        await self.smart_if.request(f"Sirens/{_id}/TurnOn", method=METH_POST)

    async def turn_off(self, _id: str) -> None:
        """Turn device off."""
        await self.smart_if.request(f"Sirens/{_id}/TurnOff", method=METH_POST)
