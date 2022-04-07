"""Support for SmartIf sirens."""
from __future__ import annotations

from typing import Any

from homeassistant.components.siren import SirenEntity
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
from .models import SmartIfEntityInfo, SmartIfSirenState
from .smartif import SmartIf
from .smartif_sirens import SmartIfSirens


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up SmartIf Siren based on a config entry."""
    data: HomeAssistantSmartIfData = hass.data[DOMAIN][entry.entry_id]
    smart_if: SmartIf = data.client
    smart_if_sirens: SmartIfSirens = SmartIfSirens(smart_if)
    async_add_entities(
        (
            SmartIfSiren(data.coordinator, smart_if, smart_if_sirens, siren_entity)
            for siren_entity in await smart_if_sirens.all()
        ),
        True,
    )


class SmartIfSiren(SmartIfEntity[SmartIfSirenState], CoordinatorEntity, SirenEntity):
    """Defines an SmartIf Siren."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        client: SmartIf,
        sirens: SmartIfSirens,
        siren_entity_info: SmartIfEntityInfo,
    ) -> None:
        """Initialize SmartIf Siren."""
        super().__init__(SmartIfSirenState, client, siren_entity_info)
        CoordinatorEntity.__init__(self, coordinator)
        self.sirens = sirens

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        return self.smart_if_state().is_on

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        try:
            await self.sirens.turn_off(self.entity_info.id)
        except SmartIfError:
            LOGGER.error("An error occurred while updating the SmartIf Siren")

        await self.coordinator.async_refresh()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        try:
            await self.sirens.turn_on(self.entity_info.id)
        except SmartIfError:
            LOGGER.error("An error occurred while updating the SmartIf Siren")

        await self.coordinator.async_refresh()
