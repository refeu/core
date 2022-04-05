"""Asynchronous Python client for SmartIf Climates."""
from __future__ import annotations

from dataclasses import dataclass

from aiohttp.hdrs import METH_POST
from pydantic import parse_obj_as

from .models import SmartIfClimateEntityInfo
from .smartif import SmartIf


@dataclass
class SmartIfClimates:
    """Class for handling connections to SmartIf related with Climate entities."""

    smart_if: SmartIf

    async def all(self) -> list[SmartIfClimateEntityInfo]:
        """Get all Climate entities."""
        return parse_obj_as(
            list[SmartIfClimateEntityInfo], await self.smart_if.request("Climates")
        )

    async def set_hvac_mode(self, _id: str, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        await self.smart_if.request(
            f"Climates/{_id}/SetHvacMode?hvacMode={hvac_mode}", method=METH_POST
        )

    async def set_fan_mode(self, _id: str, fan_mode: str) -> None:
        """Set new target fan mode."""
        await self.smart_if.request(
            f"Climates/{_id}/SetFanMode?fanMode={fan_mode}", method=METH_POST
        )

    async def set_temperature(self, _id: str, temperature: float) -> None:
        """Set new target temperature."""
        await self.smart_if.request(
            f"Climates/{_id}/SetTemperature?temperature={temperature}", method=METH_POST
        )
