"""Config flow to configure the SmartIf integration."""

from __future__ import annotations

from typing import Any

from aiohttp import ClientSession
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .exceptions import SmartIfError
from .smartif import SmartIf


class SmartIfFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a SmartIf config flow."""

    VERSION = 1

    _host: str
    _port: int

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""
        if user_input is None:
            return self._async_show_setup_form()

        self._host: str = user_input[CONF_HOST]
        self._port: int = user_input[CONF_PORT]

        try:
            session: ClientSession = async_get_clientsession(self.hass)
            smart_if = SmartIf(self._host, self._port, session=session)
            await smart_if.devices_state()

            await self.async_set_unique_id(
                self._host + str(self._port), raise_on_progress=False
            )
            self._abort_if_unique_id_configured(
                updates={CONF_HOST: self._host, CONF_PORT: self._port}
            )
        except SmartIfError:
            return self._async_show_setup_form({"base": "cannot_connect"})

        return self._async_create_entry()

    @callback
    def _async_show_setup_form(
        self, errors: dict[str, str] | None = None
    ) -> ConfigFlowResult:
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
    def _async_create_entry(self) -> ConfigFlowResult:
        return self.async_create_entry(
            title="Teldak",
            data={CONF_HOST: self._host, CONF_PORT: self._port},
        )
