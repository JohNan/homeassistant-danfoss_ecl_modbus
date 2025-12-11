"""Config flow for Danfoss ECL Modbus."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SLAVE
from homeassistant.data_entry_flow import FlowResult

from .const import DEFAULT_PORT, DEFAULT_SLAVE, DOMAIN
from .hub import EclHub


class DanfossEclModbusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Danfoss ECL Modbus config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle a flow initiated by the user."""
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            slave = user_input[CONF_SLAVE]

            hub = EclHub(host, port, slave)
            try:
                if await hub.connect():
                    await hub.close()
                    return self.async_create_entry(title=host, data=user_input)
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-exception-caught
                errors["base"] = "cannot_connect"
            finally:
                await hub.close()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Required(CONF_SLAVE, default=DEFAULT_SLAVE): int,
                }
            ),
            errors=errors,
        )
