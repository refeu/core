"""Asynchronous Python client for SmartIf."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from pydantic.fields import Field


class SmartIfEntityInfo(BaseModel):
    """Object holding a SmartIf Entity information.

    This object holds information about a SmartIf Entity.

    Attributes:
        name: Name of the entity.
        id: A unique identifier for this entity.

    """

    name: str = Field(...)
    id: str = Field(...)


# Lights
class SmartIfLightEntityInfo(SmartIfEntityInfo):
    """Object holding a SmartIf Light information.

    This object holds information about a SmartIf Light.

    Attributes:
        supports_brightness: The light can be dimmed.

    """

    supports_brightness: bool = Field(..., alias="supportsBrightness")


class SmartIfLightState(BaseModel):
    """Object holding a SmartIf Light state.

    This object holds information about a SmartIf Light state.

    Attributes:
        is_on: True if the light entity is on.
        brightness: brightness of this light between 0..255.

    """

    is_on: bool = Field(..., alias="isOn")
    brightness: Any = Field(None)


# AlarmControlPanels
class SmartIfAlarmControlPanelState(BaseModel):
    """Object holding a SmartIf Alarm Control Panel state.

    This object holds information about a SmartIf Alarm Control Panel state.

    Attributes:
        state: SmartIf Alarm Control Panel state.

    """

    state: str = Field(...)


# BinarySensors
class SmartIfBinarySensorEntityInfo(SmartIfEntityInfo):
    """Object holding a SmartIf Binary Sensor information.

    This object holds information about a SmartIf Binary Sensor.

    Attributes:
        device_class: Type of binary sensor.

    """

    device_class: str = Field(..., alias="deviceClass")


class SmartIfBinarySensorState(BaseModel):
    """Object holding a SmartIf Binary Sensor state.

    This object holds information about a SmartIf Binary Sensor state.

    Attributes:
        is_on: True if the light entity is on.
        brightness: brightness of this light between 0..255.

    """

    is_on: bool = Field(..., alias="isOn")


# Climates
class SmartIfClimateEntityInfo(SmartIfEntityInfo):
    """Object holding a SmartIf Climate information.

    This object holds information about a SmartIf Climate.

    Attributes:
        supports_state: Supports state.

    """

    supports_state: bool = Field(..., alias="supportsState")


class SmartIfClimateState(BaseModel):
    """Object holding a SmartIf Climate state.

    This object holds information about a SmartIf Climate state.

    Attributes:
        target_temperature: The temperature currently set to be reached.
        hvac_mode: The current operation (e.g. heat, cool, idle).
        fan_mode: Returns the current fan mode.

    """

    target_temperature: float = Field(..., alias="targetTemperature")
    hvac_mode: str = Field(..., alias="hvacMode")
    fan_mode: str = Field(..., alias="fanMode")


# Covers
class SmartIfCoverEntityInfo(SmartIfEntityInfo):
    """Object holding a SmartIf Cover information.

    This object holds information about a SmartIf Cover.

    Attributes:
        device_class: Describes the type/class of the cover.
        supports_set_position: The cover supports moving to a specific position between opened and closed.
        supports_stop: The cover supports stopping the current action (open, close, set position).
        supports_close: The cover supports being closed.

    """

    device_class: str = Field(..., alias="deviceClass")
    supports_set_position: bool = Field(..., alias="supportsSetPosition")
    supports_stop: bool = Field(..., alias="supportsStop")
    supports_close: bool = Field(..., alias="supportsClose")


class SmartIfCoverState(BaseModel):
    """Object holding a SmartIf Cover state.

    This object holds information about a SmartIf Cover state.

    Attributes:
        current_cover_position: The current position of cover where 0 means closed and 100 is fully open.
        is_opening: If the cover is opening or not.
        is_closing: If the cover is closing or not.
        is_closed: If the cover is closed or not.

    """

    current_cover_position: Any = Field(None, alias="currentCoverPosition")
    is_opening: Any = Field(None, alias="isOpening")
    is_closing: Any = Field(None, alias="isClosing")
    is_closed: bool = Field(..., alias="isClosed")


# Sirens
class SmartIfSirenState(BaseModel):
    """Object holding a SmartIf Siren state.

    This object holds information about a SmartIf Siren state.

    Attributes:
        is_on: Whether the device is on or off.

    """

    is_on: bool = Field(..., alias="isOn")


# Switches
class SmartIfSwitchEntityInfo(SmartIfEntityInfo):
    """Object holding a SmartIf Switch information.

    This object holds information about a SmartIf Cover.

    Attributes:
        device_class: Return the class of this entity.

    """

    device_class: str = Field(..., alias="deviceClass")


class SmartIfSwitchState(BaseModel):
    """Object holding a SmartIf Switch state.

    This object holds information about a SmartIf Switch state.

    Attributes:
        is_on: Whether the device is on or off.

    """

    is_on: bool = Field(..., alias="isOn")
