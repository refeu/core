"""Support for SmartIf events."""

from typing import Final

from homeassistant.components.event import EventDeviceClass, EventEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HomeAssistantSmartIfData
from .const import DOMAIN, VIDEODOOR_CALL_EXTERNAL_EVENT
from .smartif_events import SmartIfEvents

VIDEODOOR_CALL_EVENT: Final = "VideoDoorCall"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up SmartIf Event based on a config entry."""
    data: HomeAssistantSmartIfData = hass.data[DOMAIN][entry.entry_id]
    smart_if_events: SmartIfEvents = data.events
    async_add_entities([SmartIfVideoDoorCallEvent(smart_if_events)], True)


class SmartIfVideoDoorCallEvent(EventEntity):
    """Defines an SmartIf Video Door Call Event."""

    def __init__(self, events: SmartIfEvents) -> None:
        """Initialize SmartIf Video Door Call Event."""
        self._events = events
        self._attr_device_class = EventDeviceClass.DOORBELL
        self._attr_event_types = [VIDEODOOR_CALL_EVENT]

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()

        self.async_on_remove(
            self._events.async_add_listener(
                VIDEODOOR_CALL_EXTERNAL_EVENT, self._async_handle_event
            )
        )

    @callback
    def _async_handle_event(self) -> None:
        """Handle the Video Door Call Event."""
        self._trigger_event(VIDEODOOR_CALL_EVENT, None)
        self.async_write_ha_state()
