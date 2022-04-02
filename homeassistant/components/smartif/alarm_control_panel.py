"""Support for SmartIf lights."""
from __future__ import annotations

from homeassistant.components.alarm_control_panel import (
    FORMAT_NUMBER,
    AlarmControlPanelEntity,
)
from homeassistant.components.alarm_control_panel.const import (
    SUPPORT_ALARM_ARM_AWAY,
    SUPPORT_ALARM_ARM_HOME,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_ARMING,
    STATE_ALARM_DISARMED,
    STATE_ALARM_PENDING,
    STATE_ALARM_TRIGGERED,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from . import HomeAssistantSmartIfData
from .const import DOMAIN, LOGGER
from .entity import SmartIfEntity
from .exceptions import SmartIfError
from .models import SmartIfAlarmControlPanelState, SmartIfEntityInfo
from .smartif import SmartIf
from .smartif_alarmcontrolpanels import SmartIfAlarmControlPanels


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up SmartIf Alarm Control Panel based on a config entry."""
    data: HomeAssistantSmartIfData = hass.data[DOMAIN][entry.entry_id]
    smart_if: SmartIf = data.client
    smart_if_alarm_control_panels: SmartIfAlarmControlPanels = (
        SmartIfAlarmControlPanels(smart_if)
    )
    async_add_entities(
        (
            SmartIfAlarmControlPanel(
                data.coordinator,
                smart_if,
                smart_if_alarm_control_panels,
                alarm_control_panel_entity,
            )
            for alarm_control_panel_entity in await smart_if_alarm_control_panels.all()
        ),
        True,
    )


class SmartIfAlarmControlPanel(
    SmartIfEntity[SmartIfAlarmControlPanelState],
    CoordinatorEntity,
    AlarmControlPanelEntity,
):
    """Defines an SmartIf Alarm Control Panel."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        client: SmartIf,
        alarm_control_panels: SmartIfAlarmControlPanels,
        alarm_control_panel_entity_info: SmartIfEntityInfo,
    ) -> None:
        """Initialize SmartIf Alarm Control Panel."""
        super().__init__(
            SmartIfAlarmControlPanelState, client, alarm_control_panel_entity_info
        )
        CoordinatorEntity.__init__(self, coordinator)
        self._attr_code_format = FORMAT_NUMBER
        self._attr_code_arm_required = True
        self._attr_supported_features = SUPPORT_ALARM_ARM_AWAY | SUPPORT_ALARM_ARM_HOME
        self.alarm_control_panels = alarm_control_panels

    @property
    def state(self) -> StateType:
        """Return the state of the entity."""
        state_translations = {
            "disarmed": STATE_ALARM_DISARMED,
            "pending": STATE_ALARM_PENDING,
            "triggered": STATE_ALARM_TRIGGERED,
            "arming": STATE_ALARM_ARMING,
            "armed_home": STATE_ALARM_ARMED_HOME,
            "armed_away": STATE_ALARM_ARMED_AWAY,
        }
        return state_translations.get(self.smart_if_state().state, None)

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        try:
            await self.alarm_control_panels.alarm_disarm(self.entity_info.id, code)
        except SmartIfError:
            LOGGER.error("An error occurred while updating the SmartIf Alarm")

        await self.coordinator.async_refresh()

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Send arm home command."""
        try:
            await self.alarm_control_panels.alarm_arm_home(self.entity_info.id, code)
        except SmartIfError:
            LOGGER.error("An error occurred while updating the SmartIf Alarm")

        await self.coordinator.async_refresh()

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Send arm away command."""
        try:
            await self.alarm_control_panels.alarm_arm_away(self.entity_info.id, code)
        except SmartIfError:
            LOGGER.error("An error occurred while updating the SmartIf Alarm")

        await self.coordinator.async_refresh()
