"""Support for SmartIf covers."""
from __future__ import annotations

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverDeviceClass,
    CoverEntity,
    SUPPORT_OPEN,
    SUPPORT_CLOSE,
    SUPPORT_SET_POSITION,
    SUPPORT_STOP,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from . import HomeAssistantSmartIfData
from .const import DOMAIN, LOGGER
from .entity import SmartIfEntity
from .exceptions import SmartIfError
from .models import SmartIfCoverEntityInfo, SmartIfCoverState
from .smartif import SmartIf
from .smartif_covers import SmartIfCovers


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up SmartIf Cover based on a config entry."""
    data: HomeAssistantSmartIfData = hass.data[DOMAIN][entry.entry_id]
    smart_if: SmartIf = data.client
    smart_if_covers: SmartIfCovers = SmartIfCovers(smart_if)
    async_add_entities(
        (
            SmartIfCover(data.coordinator, smart_if, smart_if_covers, cover_entity)
            for cover_entity in await smart_if_covers.all()
        ),
        True,
    )


class SmartIfCover(SmartIfEntity[SmartIfCoverState], CoordinatorEntity, CoverEntity):
    """Defines an SmartIf Cover."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        client: SmartIf,
        covers: SmartIfCovers,
        cover_entity_info: SmartIfCoverEntityInfo,
    ) -> None:
        """Initialize SmartIf Cover."""
        super().__init__(SmartIfCoverState, client, cover_entity_info)
        CoordinatorEntity.__init__(self, coordinator)

        device_class_translations = {
            "DEVICE_CLASS_BLIND": CoverDeviceClass.BLIND,
            "DEVICE_CLASS_CURTAIN": CoverDeviceClass.CURTAIN,
            "DEVICE_CLASS_DOOR": CoverDeviceClass.DOOR,
            "DEVICE_CLASS_GARAGE": CoverDeviceClass.GARAGE,
            "DEVICE_CLASS_GATE": CoverDeviceClass.GATE,
        }

        self._attr_device_class = device_class_translations.get(
            cover_entity_info.device_class, None
        )

        self._attr_supported_features = SUPPORT_OPEN

        if cover_entity_info.supports_close:
            self._attr_supported_features |= SUPPORT_CLOSE

        if cover_entity_info.supports_set_position:
            self._attr_supported_features |= SUPPORT_SET_POSITION

        if cover_entity_info.supports_stop:
            self._attr_supported_features |= SUPPORT_STOP

        self.covers = covers

    @property
    def current_cover_position(self) -> int | None:
        """Return current position of cover.

        None is unknown, 0 is closed, 100 is fully open.
        """
        return self.smart_if_state().current_cover_position

    @property
    def is_opening(self) -> bool | None:
        """Return if the cover is opening or not."""
        return self.smart_if_state().is_opening

    @property
    def is_closing(self) -> bool | None:
        """Return if the cover is closing or not."""
        return self.smart_if_state().is_closing

    @property
    def is_closed(self) -> bool | None:
        """Return if the cover is closed or not."""
        return self.smart_if_state().is_closed

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        try:
            await self.covers.open_cover(self.entity_info.id)
        except SmartIfError:
            LOGGER.error("An error occurred while updating the SmartIf Cover")

        await self.coordinator.async_refresh()

    async def async_close_cover(self, **kwargs):
        """Close cover."""
        try:
            await self.covers.close_cover(self.entity_info.id)
        except SmartIfError:
            LOGGER.error("An error occurred while updating the SmartIf Cover")

        await self.coordinator.async_refresh()

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        try:
            await self.covers.set_cover_position(
                self.entity_info.id, kwargs[ATTR_POSITION]
            )
        except SmartIfError:
            LOGGER.error("An error occurred while updating the SmartIf Cover")

        await self.coordinator.async_refresh()

    async def async_stop_cover(self, **kwargs):
        """Stop the cover."""
        try:
            await self.covers.stop_cover(self.entity_info.id)
        except SmartIfError:
            LOGGER.error("An error occurred while updating the SmartIf Cover")

        await self.coordinator.async_refresh()
