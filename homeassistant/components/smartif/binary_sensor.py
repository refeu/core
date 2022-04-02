"""Support for SmartIf lights."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_DOOR,
    DEVICE_CLASS_GARAGE_DOOR,
    DEVICE_CLASS_GAS,
    DEVICE_CLASS_MOISTURE,
    DEVICE_CLASS_MOTION,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_SMOKE,
    DEVICE_CLASS_WINDOW,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from . import HomeAssistantSmartIfData
from .const import DOMAIN
from .entity import SmartIfEntity
from .models import SmartIfBinarySensorEntityInfo, SmartIfBinarySensorState
from .smartif import SmartIf
from .smartif_binarysensors import SmartIfBinarySensors


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up SmartIf Binary Sensor based on a config entry."""
    data: HomeAssistantSmartIfData = hass.data[DOMAIN][entry.entry_id]
    smart_if: SmartIf = data.client
    smart_if_binary_sensors: SmartIfBinarySensors = SmartIfBinarySensors(smart_if)
    async_add_entities(
        (
            SmartIfBinarySensor(
                data.coordinator,
                smart_if,
                smart_if_binary_sensors,
                binary_sensor_entity,
            )
            for binary_sensor_entity in await smart_if_binary_sensors.all()
        ),
        True,
    )


class SmartIfBinarySensor(
    SmartIfEntity[SmartIfBinarySensorState],
    CoordinatorEntity,
    BinarySensorEntity,
):
    """Defines an SmartIf Binary Sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        client: SmartIf,
        binary_sensors: SmartIfBinarySensors,
        binary_sensor_entity_info: SmartIfBinarySensorEntityInfo,
    ) -> None:
        """Initialize SmartIf Alarm."""
        super().__init__(SmartIfBinarySensorState, client, binary_sensor_entity_info)
        CoordinatorEntity.__init__(self, coordinator)

        device_class_translations = {
            "motion": DEVICE_CLASS_MOTION,
            "garage_door": DEVICE_CLASS_GARAGE_DOOR,
            "window": DEVICE_CLASS_WINDOW,
            "door": DEVICE_CLASS_DOOR,
            "moisture": DEVICE_CLASS_MOISTURE,
            "smoke": DEVICE_CLASS_SMOKE,
            "power": DEVICE_CLASS_POWER,
            "gas": DEVICE_CLASS_GAS,
        }

        self._attr_device_class = device_class_translations.get(
            binary_sensor_entity_info.device_class, None
        )
        self.binary_sensors = binary_sensors

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.smart_if_state().is_on
