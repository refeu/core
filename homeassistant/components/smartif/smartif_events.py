"""SmartIf events manager."""

from collections.abc import Callable

from homeassistant.core import CALLBACK_TYPE, callback


class SmartIfEvents:
    """Defines the object that reacts to events from SmartIf and keeps listeners."""

    def __init__(self) -> None:
        """Initialize the SmartIf State."""
        self._listeners: dict[str, list[CALLBACK_TYPE]] = {}

    @callback
    def async_add_listener(
        self, event_name: str, on_event_callback: CALLBACK_TYPE
    ) -> Callable[[], None]:
        """Listen for events updates."""

        @callback
        def remove_listener() -> None:
            """Remove event listener."""
            self._listeners[event_name].remove(remove_listener)

            if not self._listeners[event_name]:
                self._listeners.pop(event_name)

        self._listeners.setdefault(event_name, []).append(on_event_callback)
        return remove_listener

    @callback
    def async_on_event(self, event_name: str) -> None:
        """Notify listeners."""
        self.async_update_listeners(event_name)

    @callback
    def async_update_listeners(self, event_name: str) -> None:
        """Call all registered listeners."""
        for on_event_callback in list(self._listeners.get(event_name, {})):
            on_event_callback()
