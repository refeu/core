"""Support for SmartIf cameras."""
from __future__ import annotations

from pydantic import BaseModel

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HomeAssistantSmartIfData
from .const import DOMAIN, LOGGER
from .entity import SmartIfEntity
from .exceptions import SmartIfError
from .models import SmartIfEntityInfo
from .smartif import SmartIf
from .smartif_cameras import SmartIfCameras


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up SmartIf Camera based on a config entry."""
    data: HomeAssistantSmartIfData = hass.data[DOMAIN][entry.entry_id]
    smart_if: SmartIf = data.client
    smart_if_cameras: SmartIfCameras = SmartIfCameras(smart_if)
    async_add_entities(
        (
            SmartIfCamera(smart_if, smart_if_cameras, camera_entity)
            for camera_entity in await smart_if_cameras.all()
        ),
        True,
    )


class SmartIfCamera(SmartIfEntity[BaseModel], Camera):
    """Defines an SmartIf Camera."""

    def __init__(
        self,
        client: SmartIf,
        cameras: SmartIfCameras,
        camera_entity_info: SmartIfEntityInfo,
    ) -> None:
        """Initialize SmartIf Camera."""
        super().__init__(BaseModel, client, camera_entity_info)
        Camera.__init__(self)
        self._attr_is_recording = False
        self._attr_is_streaming = False
        self._attr_is_on = True
        self.cameras = cameras

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return bytes of camera image."""
        try:
            return await self.cameras.camera_image(self.entity_info.id)
        except SmartIfError:
            LOGGER.error("An error occurred while getting the SmartIf Camera Image")
            return None

    def enable_motion_detection(self) -> None:
        """Enable motion detection in the camera."""

    def disable_motion_detection(self) -> None:
        """Disable motion detection in camera."""
