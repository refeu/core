"""Asynchronous Python client for SmartIf Binary Sensors."""
from __future__ import annotations

from dataclasses import dataclass

from pydantic import parse_obj_as

from .models import SmartIfBinarySensorEntityInfo
from .smartif import SmartIf


@dataclass
class SmartIfBinarySensors:
    """Class for handling connections to SmartIf related with Binary Sensor entities."""

    smart_if: SmartIf

    async def all(self) -> list[SmartIfBinarySensorEntityInfo]:
        """Get all Binary Sensor entities."""
        return parse_obj_as(
            list[SmartIfBinarySensorEntityInfo],
            await self.smart_if.request("BinarySensors"),
        )
