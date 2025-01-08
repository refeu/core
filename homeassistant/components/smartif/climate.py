"""Support for SmartIf climates."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    FAN_AUTO,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_WHOLE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HomeAssistantSmartIfData
from .const import DOMAIN, LOGGER
from .entity import SmartIfEntity
from .exceptions import SmartIfError
from .models import SmartIfClimateEntityInfo, SmartIfClimateState
from .smartif import SmartIf
from .smartif_climates import SmartIfClimates
from .smartif_state import SmartIfState


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up SmartIf Climate based on a config entry."""
    data: HomeAssistantSmartIfData = hass.data[DOMAIN][entry.entry_id]
    smart_if: SmartIf = data.client
    smart_if_climates: SmartIfClimates = SmartIfClimates(smart_if)
    async_add_entities(
        (
            SmartIfClimate(data.state, smart_if, smart_if_climates, climate_entity)
            for climate_entity in await smart_if_climates.all()
        ),
        True,
    )


class SmartIfClimate(
    SmartIfEntity[SmartIfClimateState],
    ClimateEntity,
):
    """Defines an SmartIf Climate."""

    def __init__(
        self,
        state: SmartIfState,
        client: SmartIf,
        climates: SmartIfClimates,
        climate_entity_info: SmartIfClimateEntityInfo,
    ) -> None:
        """Initialize SmartIf Climate."""
        super().__init__(SmartIfClimateState, client, climate_entity_info, state)
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_precision = PRECISION_WHOLE
        self._attr_target_temperature_step = PRECISION_WHOLE
        self._attr_max_temp = 32
        self._attr_min_temp = 16
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.COOL]
        self._attr_fan_modes = [FAN_AUTO, FAN_LOW, FAN_MEDIUM, FAN_HIGH]
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.TURN_OFF
        )

        if not climate_entity_info.supports_state:
            self._attr_assumed_state = True

        self._climates: SmartIfClimates = climates

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self.smart_if_state().target_temperature

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return hvac operation ie. heat, cool mode.

        Need to be one of HVAC_MODE_*.
        """
        hvac_mode_translations: dict[str, HVACMode] = {
            "HVAC_MODE_OFF": HVACMode.OFF,
            "HVAC_MODE_COOL": HVACMode.COOL,
            "HVAC_MODE_HEAT": HVACMode.HEAT,
        }

        return hvac_mode_translations.get(self.smart_if_state().hvac_mode, HVACMode.OFF)

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current running hvac operation if supported.

        Need to be one of CURRENT_HVAC_*.
        """
        hvac_action_translations: dict[str, HVACAction] = {
            "HVAC_MODE_OFF": HVACAction.OFF,
            "HVAC_MODE_COOL": HVACAction.COOLING,
            "HVAC_MODE_HEAT": HVACAction.HEATING,
        }

        return hvac_action_translations.get(
            self.smart_if_state().hvac_mode, HVACAction.IDLE
        )

    @property
    def fan_mode(self) -> str | None:
        """Return the fan setting.

        Requires ClimateEntityFeature.FAN_MODE.
        """
        fan_mode_translations: dict[str, str] = {
            "FAN_AUTO": FAN_AUTO,
            "FAN_LOW": FAN_LOW,
            "FAN_MEDIUM": FAN_MEDIUM,
            "FAN_HIGH": FAN_HIGH,
        }

        return fan_mode_translations.get(self.smart_if_state().fan_mode, FAN_AUTO)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        hvac_mode_translations: dict[HVACMode, str] = {
            HVACMode.OFF: "HVAC_MODE_OFF",
            HVACMode.COOL: "HVAC_MODE_COOL",
            HVACMode.HEAT: "HVAC_MODE_HEAT",
        }

        try:
            await self._climates.set_hvac_mode(
                self.smartif_entity_id,
                hvac_mode_translations.get(hvac_mode, "HVAC_MODE_OFF"),
            )
        except SmartIfError:
            LOGGER.error("An error occurred while updating the SmartIf Climate")

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        fan_mode_translations: dict[str, str] = {
            FAN_AUTO: "FAN_AUTO",
            FAN_LOW: "FAN_LOW",
            FAN_MEDIUM: "FAN_MEDIUM",
            FAN_HIGH: "FAN_HIGH",
        }

        try:
            await self._climates.set_fan_mode(
                self.smartif_entity_id, fan_mode_translations.get(fan_mode, "FAN_AUTO")
            )
        except SmartIfError:
            LOGGER.error("An error occurred while updating the SmartIf Climate")

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        try:
            await self._climates.set_temperature(
                self.smartif_entity_id, float(temperature)
            )
        except SmartIfError:
            LOGGER.error("An error occurred while updating the SmartIf Climate")

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        await self.async_set_hvac_mode(HVACMode.OFF)
