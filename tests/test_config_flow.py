"""Tests for the Danfoss ECL Modbus config flow."""

from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SLAVE
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from modbus_connection.exceptions import ModbusTimeoutError
from modbus_connection.mock import MockModbusUnit

from custom_components.danfoss_ecl_modbus.const import (
    DEFAULT_SLAVE,
    DOMAIN,
    REG_ACTUAL_MODE,
)
from custom_components.danfoss_ecl_modbus.hub import EclHub


@pytest.mark.usefixtures("mock_modbus_connection")
async def test_user_flow_success(hass: HomeAssistant) -> None:
    """Test successful user config flow creation."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}

    user_input = {
        CONF_HOST: "  1.2.3.4  ",
        CONF_PORT: 502,
        CONF_SLAVE: DEFAULT_SLAVE,
    }
    expected_data = {
        CONF_HOST: "1.2.3.4",
        CONF_PORT: 502,
        CONF_SLAVE: DEFAULT_SLAVE,
    }
    with patch(
        "custom_components.danfoss_ecl_modbus.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "1.2.3.4"
    assert result["data"] == expected_data
    mock_setup_entry.assert_awaited_once()


async def test_user_flow_cannot_connect(
    hass: HomeAssistant,
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """Test user flow shows cannot_connect when probing fails."""
    mock_modbus_unit.fail_read(
        REG_ACTUAL_MODE,
        ModbusTimeoutError("timeout"),
        register_type="input",
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: "1.2.3.4",
            CONF_PORT: 502,
            CONF_SLAVE: DEFAULT_SLAVE,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


@pytest.mark.usefixtures("mock_modbus_connection")
async def test_user_flow_unknown_error(hass: HomeAssistant) -> None:
    """Test user flow shows unknown on unexpected errors."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    with patch.object(EclHub, "async_probe", side_effect=RuntimeError("boom")):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "1.2.3.4",
                CONF_PORT: 502,
                CONF_SLAVE: DEFAULT_SLAVE,
            },
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "unknown"}


@pytest.mark.usefixtures("mock_config_entry", "mock_modbus_connection")
async def test_user_flow_duplicate_abort(hass: HomeAssistant) -> None:
    """Test user flow aborts when the same device is already configured."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: "1.2.3.4",
            CONF_PORT: 502,
            CONF_SLAVE: DEFAULT_SLAVE,
        },
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
