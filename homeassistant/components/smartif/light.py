"""Support for SmartIf lights."""
from __future__ import annotations

from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    COLOR_MODE_BRIGHTNESS,
    COLOR_MODE_ONOFF,
    LightEntity,
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
from .models import SmartIfLightEntityInfo, SmartIfLightState
from .smartif import SmartIf
from .smartif_lights import SmartIfLights


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up SmartIf Light based on a config entry."""
    data: HomeAssistantSmartIfData = hass.data[DOMAIN][entry.entry_id]
    smart_if: SmartIf = data.client
    smart_if_lights: SmartIfLights = SmartIfLights(smart_if)
    async_add_entities(
        (
            SmartIfLight(data.coordinator, smart_if, smart_if_lights, light_entity)
            for light_entity in await smart_if_lights.all()
        ),
        True,
    )


class SmartIfLight(SmartIfEntity[SmartIfLightState], CoordinatorEntity, LightEntity):
    """Defines an SmartIf Light."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        client: SmartIf,
        lights: SmartIfLights,
        light_entity_info: SmartIfLightEntityInfo,
    ) -> None:
        """Initialize SmartIf Light."""
        super().__init__(SmartIfLightState, client, light_entity_info)
        CoordinatorEntity.__init__(self, coordinator)

        if light_entity_info.supports_brightness:
            self._attr_color_mode = COLOR_MODE_BRIGHTNESS
            self._attr_supported_color_modes = {COLOR_MODE_BRIGHTNESS}
        else:
            self._attr_color_mode = COLOR_MODE_ONOFF
            self._attr_supported_color_modes = {COLOR_MODE_ONOFF}

        self.lights = lights

    @property
    def is_on(self) -> bool:
        """Return the state of the light."""
        return self.smart_if_state().is_on

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        return self.smart_if_state().brightness

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        try:
            await self.lights.turn_off(self.entity_info.id)
        except SmartIfError:
            LOGGER.error("An error occurred while updating the SmartIf Light")

        await self.coordinator.async_refresh()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        try:
            brightness: int | None = (
                kwargs[ATTR_BRIGHTNESS]
                if self.supported_color_modes
                and COLOR_MODE_BRIGHTNESS in self.supported_color_modes
                and ATTR_BRIGHTNESS in kwargs
                else None
            )
            await self.lights.turn_on(self.entity_info.id, brightness)
        except SmartIfError:
            LOGGER.error("An error occurred while updating the SmartIf Light")

        await self.coordinator.async_refresh()
