"""Config flow for Danfoss ECL Modbus."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant.components.modbus import async_get_temporary_unit
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SLAVE
from homeassistant.exceptions import HomeAssistantError
from modbus_connection import ModbusError, ModbusTcpParams

from .const import DEFAULT_PORT, DEFAULT_SLAVE, DOMAIN
from .hub import EclHub

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigFlowResult

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=65535)
        ),
        vol.Required(CONF_SLAVE, default=DEFAULT_SLAVE): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=247)
        ),
    }
)


class DanfossEclModbusConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Danfoss ECL Modbus."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            slave = user_input.get(CONF_SLAVE, DEFAULT_SLAVE)
            cleaned_input = {
                CONF_HOST: host,
                CONF_PORT: port,
                CONF_SLAVE: slave,
            }

            self._async_abort_entries_match(cleaned_input)

            try:
                async with async_get_temporary_unit(
                    self.hass,
                    ModbusTcpParams(host=host, port=port),
                    slave,
                ) as unit:
                    await EclHub(unit).async_probe()
            except (ModbusError, HomeAssistantError, OSError, TimeoutError) as err:
                _LOGGER.debug(
                    "Failed to connect to Danfoss ECL at %s:%s (slave %s): %s",
                    host,
                    port,
                    slave,
                    err,
                )
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error connecting to Danfoss ECL device")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=host, data=cleaned_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
