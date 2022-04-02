"""Asynchronous Python client for SmartIf Cameras."""
from __future__ import annotations

from dataclasses import dataclass
import urllib.parse

from pydantic import parse_obj_as

from .models import SmartIfEntityInfo
from .smartif import SmartIf


@dataclass
class SmartIfCameras:
    """Class for handling connections to SmartIf related with Camera entities."""

    smart_if: SmartIf

    async def all(self) -> list[SmartIfEntityInfo]:
        """Get all Camera entities."""
        return parse_obj_as(
            list[SmartIfEntityInfo], await self.smart_if.request("Cameras")
        )

    async def camera_image(self, _id: str) -> bytes:
        """Return bytes of camera image."""
        return await self.smart_if.request_binary(
            f"Cameras/{urllib.parse.quote(_id)}/CameraImage"
        )
