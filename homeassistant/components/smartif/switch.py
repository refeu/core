"""Support for SmartIf switches."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
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
from .models import SmartIfSwitchEntityInfo, SmartIfSwitchState
from .smartif import SmartIf
from .smartif_switches import SmartIfSwitches


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up SmartIf Switch based on a config entry."""
    data: HomeAssistantSmartIfData = hass.data[DOMAIN][entry.entry_id]
    smart_if: SmartIf = data.client
    smart_if_switches: SmartIfSwitches = SmartIfSwitches(smart_if)
    async_add_entities(
        (
            SmartIfSwitch(data.coordinator, smart_if, smart_if_switches, siren_switch)
            for siren_switch in await smart_if_switches.all()
        ),
        True,
    )


class SmartIfSwitch(SmartIfEntity[SmartIfSwitchState], CoordinatorEntity, SwitchEntity):
    """Defines an SmartIf Switch."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        client: SmartIf,
        switches: SmartIfSwitches,
        switch_entity_info: SmartIfSwitchEntityInfo,
    ) -> None:
        """Initialize SmartIf Switch."""
        super().__init__(SmartIfSwitchState, client, switch_entity_info)
        CoordinatorEntity.__init__(self, coordinator)

        self._attr_device_class = (
            SwitchDeviceClass.OUTLET
            if switch_entity_info.device_class == "outlet"
            else SwitchDeviceClass.SWITCH
        )

        self.switches = switches

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        return self.smart_if_state().is_on

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        try:
            await self.switches.turn_off(self.entity_info.id)
        except SmartIfError:
            LOGGER.error("An error occurred while updating the SmartIf Switch")

        await self.coordinator.async_refresh()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        try:
            await self.switches.turn_on(self.entity_info.id)
        except SmartIfError:
            LOGGER.error("An error occurred while updating the SmartIf Switch")

        await self.coordinator.async_refresh()
