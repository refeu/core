"""Asynchronous Python client for SmartIf Switches."""
from __future__ import annotations

from dataclasses import dataclass

from aiohttp.hdrs import METH_POST
from pydantic import parse_obj_as

from .models import SmartIfSwitchEntityInfo
from .smartif import SmartIf


@dataclass
class SmartIfSwitches:
    """Class for handling connections to SmartIf related with Switch entities."""

    smart_if: SmartIf

    async def all(self) -> list[SmartIfSwitchEntityInfo]:
        """Get all Switch entities."""
        return parse_obj_as(
            list[SmartIfSwitchEntityInfo], await self.smart_if.request("Switches")
        )

    async def turn_on(self, _id: str) -> None:
        """Turn the entity on."""
        await self.smart_if.request(f"Switches/{_id}/TurnOn", method=METH_POST)

    async def turn_off(self, _id: str) -> None:
        """Turn the entity off."""
        await self.smart_if.request(f"Switches/{_id}/TurnOff", method=METH_POST)
