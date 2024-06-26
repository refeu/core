"""Support for SmartIf events."""

from homeassistant.components.event import EventDeviceClass, EventEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HomeAssistantSmartIfData
from .const import DOMAIN, VIDEODOOR_CALL_EXTERNAL_EVENT
from .smartif_events import SmartIfEvents


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up SmartIf Event based on a config entry."""
    data: HomeAssistantSmartIfData = hass.data[DOMAIN][entry.entry_id]
    smart_if_events: SmartIfEvents = data.events
    async_add_entities(
        [
            SmartIfEvent(
                smart_if_events,
                "Video Door",
                "VideoDoorCall",
                VIDEODOOR_CALL_EXTERNAL_EVENT,
                EventDeviceClass.DOORBELL,
            )
        ],
        True,
    )


class SmartIfEvent(EventEntity):
    """Defines an SmartIf Event."""

    def __init__(
        self,
        events: SmartIfEvents,
        name: str,
        event_name: str,
        external_event_name: str,
        device_class: EventDeviceClass | None,
    ) -> None:
        """Initialize SmartIf Event."""
        self._events = events
        self._event_name = event_name
        self._external_event_name = external_event_name
        self._attr_device_class = device_class
        self._attr_event_types = [event_name]

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, event_name)},
            manufacturer="Teldak",
            model="SmartIf",
            name=name,
        )
        self._attr_name = name
        self._attr_unique_id = event_name

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()

        self.async_on_remove(
            self._events.async_add_listener(
                self._external_event_name, self._async_handle_event
            )
        )

    @callback
    def _async_handle_event(self) -> None:
        """Handle the event."""
        self._trigger_event(self._event_name, None)
        self.async_write_ha_state()
