"""Asynchronous Python client for SmartIf Alarms."""
from __future__ import annotations

from dataclasses import dataclass

from aiohttp.hdrs import METH_POST
from pydantic import parse_obj_as

from .models import SmartIfEntityInfo
from .smartif import SmartIf


@dataclass
class SmartIfAlarmControlPanels:
    """Class for handling connections to SmartIf related with Alarm entities."""

    smart_if: SmartIf

    async def all(self) -> list[SmartIfEntityInfo]:
        """Get all Alarm entities."""
        return parse_obj_as(
            list[SmartIfEntityInfo], await self.smart_if.request("AlarmControlPanels")
        )

    async def alarm_disarm(self, _id: str, code: str = None) -> None:
        """Send disarm command."""
        param: str = f"?code={code}" if code is not None else ""
        await self.smart_if.request(
            f"AlarmControlPanels/{_id}/AlarmDisarm{param}", method=METH_POST
        )

    async def alarm_arm_home(self, _id: str, code: str = None) -> None:
        """Send arm home command."""
        param: str = f"?code={code}" if code is not None else ""
        await self.smart_if.request(
            f"AlarmControlPanels/{_id}/AlarmArmHome{param}", method=METH_POST
        )

    async def alarm_arm_away(self, _id: str, code: str = None) -> None:
        """Send arm away command."""
        param: str = f"?code={code}" if code is not None else ""
        await self.smart_if.request(
            f"AlarmControlPanels/{_id}/AlarmArmAway{param}", method=METH_POST
        )
