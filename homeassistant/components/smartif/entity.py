"""Base entity for the SmartIf integration."""
from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .models import SmartIfEntityInfo
from .smartif import SmartIf
from .smartif_state import SmartIfState

TState = TypeVar("TState", bound=BaseModel)


class SmartIfEntity(Entity, Generic[TState]):
    """Defines a SmartIf entity."""

    _state: SmartIfState | None
    _attr_device_info: DeviceInfo | None
    _attr_name: str | None
    _attr_unique_id: str | None = None

    def __init__(
        self,
        state_type: type[TState],
        client: SmartIf,
        entity_info: SmartIfEntityInfo,
        state: SmartIfState | None,
    ) -> None:
        """Initialize a SmartIf entity."""
        self.state_type = state_type
        self.client = client
        self.entity_info = entity_info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entity_info.id)},
            manufacturer="Teldak",
            model="SmartIf",
            name=entity_info.name,
        )
        self._attr_name = entity_info.name
        self._attr_unique_id = entity_info.id
        self._state = state

    def smart_if_state(self) -> TState:
        """Get the entity state."""
        return (
            self.state_type.parse_obj(self._state.data[self.entity_info.id])
            if self._state
            else self.state_type()
        )

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""

        await super().async_added_to_hass()

        if self._state:
            self.async_on_remove(
                self._state.async_add_listener(
                    self.entity_info.id, self._handle_state_update
                )
            )

    @callback
    def _handle_state_update(self) -> None:
        """Handle updated data from the SmartIfState."""
        self.async_write_ha_state()

    @property
    def should_poll(self) -> bool:
        """No need to poll. SmartIfState notifies entity of updates."""
        return False
