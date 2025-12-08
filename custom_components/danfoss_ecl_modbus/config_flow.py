"""Config flow for ECL Modbus."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SLAVE

from .const import DOMAIN


class EclModbusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """ECL Modbus config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        errors = {}
        if user_input is not None:
            # Here you would normally validate the user input, e.g., try to connect to the Modbus device.
            # For now, we'll just assume the input is valid.
            return self.async_create_entry(title=user_input[CONF_HOST], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=502): int,
                    vol.Required(CONF_SLAVE, default=5): int,
                }
            ),
            errors=errors,
        )
