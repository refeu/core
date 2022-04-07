"""Support for SmartIf."""

from typing import Any, NamedTuple

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER, SCAN_INTERVAL
from .smartif import SmartIf

PLATFORMS = [
    Platform.LIGHT,
    Platform.ALARM_CONTROL_PANEL,
    Platform.BINARY_SENSOR,
    Platform.CAMERA,
    Platform.CLIMATE,
    Platform.COVER,
    Platform.SIREN,
    Platform.SWITCH,
]


class HomeAssistantSmartIfData(NamedTuple):
    """SmartIf data stored in the Home Assistant data object."""

    coordinator: DataUpdateCoordinator[dict[str, Any]]
    client: SmartIf


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SmartIf from a config entry."""
    session = async_get_clientsession(hass)
    smartif = SmartIf(
        entry.data[CONF_HOST], port=entry.data[CONF_PORT], session=session
    )

    async def update() -> dict[str, Any]:
        return await smartif.devices_state()

    coordinator: DataUpdateCoordinator[dict[str, Any]] = DataUpdateCoordinator(
        hass,
        LOGGER,
        name=f"{DOMAIN}_{entry.data[CONF_HOST]}",
        update_interval=SCAN_INTERVAL,
        update_method=update,
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = HomeAssistantSmartIfData(
        coordinator=coordinator, client=smartif
    )
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload SmartIf config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Cleanup
        del hass.data[DOMAIN][entry.entry_id]

        if not hass.data[DOMAIN]:
            del hass.data[DOMAIN]

    return unload_ok
