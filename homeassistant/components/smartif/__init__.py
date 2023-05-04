"""Support for SmartIf."""

from typing import Any, NamedTuple

import unidecode

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER, SCAN_INTERVAL
from .smartif import SmartIf
from .smartif_services import SmartIfServices

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
    all_services: dict[str, str]


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
    smartif_services: SmartIfServices = SmartIfServices(smartif)
    service_names: list[str] = await smartif_services.all()
    all_services: dict[str, str] = {}

    async def handle_service(call: ServiceCall) -> None:
        """Handle the service call."""
        name = call.service
        await smartif_services.call(all_services[name])

    for service_name in service_names:
        name_to_register: str = unidecode.unidecode(
            service_name.lower().replace(" ", "_")
        )
        hass.services.async_register(DOMAIN, name_to_register, handle_service)
        all_services[name_to_register] = service_name

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = HomeAssistantSmartIfData(
        coordinator=coordinator, client=smartif, all_services=all_services
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload SmartIf config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Cleanup
        data: HomeAssistantSmartIfData = hass.data[DOMAIN][entry.entry_id]

        for service_name in data.all_services.keys():
            hass.services.async_remove(DOMAIN, service_name)

        del hass.data[DOMAIN][entry.entry_id]

        if not hass.data[DOMAIN]:
            del hass.data[DOMAIN]

    return unload_ok
