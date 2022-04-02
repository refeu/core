"""Config flow to configure the SmartIf integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .exceptions import SmartIfError
from .smartif import SmartIf


class SmartIfFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a SmartIf config flow."""

    VERSION = 1

    host: str
    port: int

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user."""
        if user_input is None:
            return self._async_show_setup_form()

        self.host = user_input[CONF_HOST]
        self.port = user_input[CONF_PORT]

        try:
            session = async_get_clientsession(self.hass)
            smart_if = SmartIf(self.host, self.port, session=session)
            await smart_if.devices_state()

            await self.async_set_unique_id(
                self.host + str(self.port), raise_on_progress=False
            )
            self._abort_if_unique_id_configured(
                updates={CONF_HOST: self.host, CONF_PORT: self.port}
            )
        except SmartIfError:
            return self._async_show_setup_form({"base": "cannot_connect"})

        return self._async_create_entry()

    @callback
    def _async_show_setup_form(
        self, errors: dict[str, str] | None = None
    ) -> FlowResult:
        """Show the setup form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_PORT, default=9123): int,
                }
            ),
            errors=errors or {},
        )

    @callback
    def _async_create_entry(self) -> FlowResult:
        return self.async_create_entry(
            title="Teldak",
            data={CONF_HOST: self.host, CONF_PORT: self.port},
        )
