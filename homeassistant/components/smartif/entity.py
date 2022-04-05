"""Base entity for the SmartIf integration."""
from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .models import SmartIfEntityInfo
from .smartif import SmartIf

TState = TypeVar("TState", bound=BaseModel)


class SmartIfEntity(Generic[TState]):
    """Defines a SmartIf entity."""

    coordinator: Any
    _attr_device_info: DeviceInfo | None
    _attr_name: str | None
    _attr_unique_id: str | None = None

    def __init__(
        self, state_type: type[TState], client: SmartIf, entity_info: SmartIfEntityInfo
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

    def smart_if_state(self) -> TState:
        """Get the entity state."""
        return self.state_type.parse_obj(self.coordinator.data[self.entity_info.id])
