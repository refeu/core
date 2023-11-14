"""SmartIf entities state manager."""
from collections.abc import Callable
from typing import Any

from homeassistant.core import CALLBACK_TYPE, callback


class SmartIfState:
    """Defines the object that keeps the state for all SmartIf Entities."""

    def __init__(self) -> None:
        """Initialize the SmartIf State."""

        self.data: dict[str, Any] = {}
        self._listeners: dict[str, list[CALLBACK_TYPE]] = {}

    @callback
    def async_add_listener(
        self, entity_id: str, update_callback: CALLBACK_TYPE
    ) -> Callable[[], None]:
        """Listen for data updates."""

        @callback
        def remove_listener() -> None:
            """Remove update listener."""
            self._listeners[entity_id].remove(remove_listener)

            if not self._listeners[entity_id]:
                self._listeners.pop(entity_id)

        self._listeners.setdefault(entity_id, []).append(update_callback)
        return remove_listener

    @callback
    def async_set_updated_data(self, entity_id: str, data: Any) -> None:
        """Update the data and notify listeners."""

        self.data[entity_id] = data
        self.async_update_listeners(entity_id)

    @callback
    def async_update_listeners(self, entity_id: str) -> None:
        """Call all registered listeners."""

        for update_callback in list(self._listeners[entity_id]):
            update_callback()
