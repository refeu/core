"""Support for SmartIf."""

from dataclasses import dataclass, field
from typing import Any

from aiohttp import ClientSession
import unidecode

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER, SCAN_INTERVAL, UPDATE_EVENT
from .smartif import SmartIf
from .smartif_services import SmartIfServices
from .smartif_state import SmartIfState

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


@dataclass
class HomeAssistantSmartIfData:
    """SmartIf data stored in the Home Assistant data object."""

    state: SmartIfState
    client: SmartIf
    all_services: dict[str, str] = field(default_factory=dict)
    event_listener: CALLBACK_TYPE | None = None


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SmartIf from a config entry."""
    session: ClientSession = async_get_clientsession(hass)
    smartif = await hass.async_add_executor_job(
        SmartIf, entry.data[CONF_HOST], entry.data[CONF_PORT], session
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
    await coordinator.async_shutdown()
    await async_continue_setup(hass, entry, smartif, SmartIfState(coordinator.data))
    return True


async def async_continue_setup(
    hass: HomeAssistant,
    entry: ConfigEntry,
    smartif: SmartIf,
    smartIfState: SmartIfState,
) -> None:
    """Continue the setup after we have the devices state."""

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = HomeAssistantSmartIfData(
        smartIfState, smartif
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await setup_hass_events(hass, entry)
    smartif_services = SmartIfServices(smartif)
    service_names: list[str] = await smartif_services.all()
    await hass.async_add_executor_job(
        setup_hass_services, hass, entry, smartif_services, service_names
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload SmartIf config entry."""
    data: HomeAssistantSmartIfData = hass.data[DOMAIN][entry.entry_id]

    for service_name in data.all_services:
        hass.services.async_remove(DOMAIN, service_name)

    unload_ok: bool = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if data.event_listener:
        data.event_listener()

    hass.data[DOMAIN].pop(entry.entry_id)

    if len(hass.data[DOMAIN]) == 0:
        hass.data.pop(DOMAIN)

    return unload_ok


def setup_hass_services(
    hass: HomeAssistant,
    entry: ConfigEntry,
    smartif_services: SmartIfServices,
    service_names: list[str],
) -> None:
    """Home Assistant services."""
    data: HomeAssistantSmartIfData = hass.data[DOMAIN][entry.entry_id]

    async def handle_service(call: ServiceCall) -> None:
        name = call.service
        await smartif_services.call(data.all_services[name])

    for service_name in service_names:
        name_to_register: str = unidecode.unidecode(
            service_name.lower().replace(" ", "_")
        )
        data.all_services[name_to_register] = service_name
        hass.services.register(DOMAIN, name_to_register, handle_service)


async def setup_hass_events(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Home Assistant smartif callbacks."""
    data: HomeAssistantSmartIfData = hass.data[DOMAIN][entry.entry_id]

    async def update_event(event: Event) -> None:
        for smartif_entity_id, entity_data in event.data.items():
            data.state.async_set_updated_data(smartif_entity_id, entity_data)

    data.event_listener = hass.bus.async_listen(UPDATE_EVENT, update_event)
