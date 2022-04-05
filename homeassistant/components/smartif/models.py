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

    supports_state: str = Field(..., alias="supportsState")


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
