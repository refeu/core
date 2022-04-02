"""Asynchronous Python client for SmartIf Lights."""
from __future__ import annotations

from dataclasses import dataclass

from aiohttp.hdrs import METH_POST
from pydantic import parse_obj_as

from .models import SmartIfLightEntityInfo
from .smartif import SmartIf


@dataclass
class SmartIfLights:
    """Class for handling connections to SmartIf related with Light entities."""

    smart_if: SmartIf

    async def all(self) -> list[SmartIfLightEntityInfo]:
        """Get all Light entities."""
        return parse_obj_as(
            list[SmartIfLightEntityInfo], await self.smart_if.request("Lights")
        )

    async def turn_on(self, _id: str, brightness: int | None = None) -> None:
        """Turn the device on."""
        param: str = f"?brightness={brightness}" if brightness is not None else ""
        await self.smart_if.request(f"Lights/{_id}/TurnOn{param}", method=METH_POST)

    async def turn_off(self, _id: str) -> None:
        """Turn device off."""
        await self.smart_if.request(f"Lights/{_id}/TurnOff", method=METH_POST)
