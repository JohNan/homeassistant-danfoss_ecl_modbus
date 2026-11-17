"""Fixtures and helpers for Danfoss ECL Modbus tests."""

from collections.abc import Iterator
from unittest.mock import patch

import pytest
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SLAVE
from homeassistant.core import HomeAssistant
from modbus_connection.encode import encode_int
from modbus_connection.mock import MockModbusConnection, MockModbusUnit
from pytest_homeassistant.common import MockConfigEntry

from custom_components.danfoss_ecl_modbus.const import (
    DEFAULT_SLAVE,
    DOMAIN,
    REG_ACCUMULATED_OUTSIDE_TEMP,
    REG_ACTUAL_MODE,
    REG_ADDITION_TEMP,
    REG_CUTOUT_TEMP,
    REG_DESIRED_FLOW_TEMP,
    REG_DESIRED_ROOM_TEMP,
    REG_FLOW_TEMP_MAX,
    REG_FLOW_TEMP_MIN,
    REG_HVAC_MODE,
    REG_OUTSIDE_TEMP,
    REG_PARALLEL_DISPLACEMENT,
    REG_PUMP,
    REG_RETURN_TEMP,
    REG_RETURN_TEMP_LIMIT,
    REG_ROOM_TEMP,
    REG_SETBACK_TEMP,
    REG_SLOPE,
    REG_TARGET_TEMP,
    REG_VALVE_CLOSING,
    REG_VALVE_OPENING,
)

DEFAULT_HOLDING: dict[int, int] = {
    REG_PUMP: 1,
    REG_VALVE_OPENING: 0,
    REG_VALVE_CLOSING: 0,
    REG_HVAC_MODE: 1,
    REG_RETURN_TEMP_LIMIT: 50,
    REG_SLOPE: 18,
    REG_PARALLEL_DISPLACEMENT: encode_int(-4, count=1)[0],
    REG_FLOW_TEMP_MIN: 20,
    REG_FLOW_TEMP_MAX: 70,
    REG_CUTOUT_TEMP: 18,
    REG_TARGET_TEMP: 21,
    REG_SETBACK_TEMP: 17,
}

DEFAULT_INPUT: dict[int, int] = {
    REG_ACTUAL_MODE: 1,
    REG_ACCUMULATED_OUTSIDE_TEMP: encode_int(-25, count=1)[0],
    REG_OUTSIDE_TEMP: encode_int(-50, count=1)[0],
    REG_ROOM_TEMP: 215,
    REG_ADDITION_TEMP: 455,
    REG_RETURN_TEMP: 320,
    REG_DESIRED_ROOM_TEMP: 210,
    REG_DESIRED_FLOW_TEMP: 460,
}


@pytest.fixture
def mock_modbus_connection() -> Iterator[MockModbusConnection]:
    """Patch ModbusConnection to yield an in-memory MockModbusConnection."""
    conn = MockModbusConnection()
    unit = conn.for_unit(DEFAULT_SLAVE)
    for address, value in DEFAULT_HOLDING.items():
        unit.holding[address] = value
    for address, value in DEFAULT_INPUT.items():
        unit.input[address] = value

    def _create_connection(_params: object) -> MockModbusConnection:
        return conn

    with patch(
        "homeassistant.components.modbus.connection.ModbusConnection",
        side_effect=_create_connection,
    ):
        yield conn


@pytest.fixture
def mock_modbus_unit(mock_modbus_connection: MockModbusConnection) -> MockModbusUnit:
    """Return the mock Modbus unit for the default slave address."""
    return mock_modbus_connection.for_unit(DEFAULT_SLAVE)


@pytest.fixture
def mock_config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Create and register a mock config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="1.2.3.4",
        data={
            CONF_HOST: "1.2.3.4",
            CONF_PORT: 502,
            CONF_SLAVE: DEFAULT_SLAVE,
        },
        entry_id="test_entry_id",
    )
    entry.add_to_hass(hass)
    return entry


async def setup_integration(
    hass: HomeAssistant, entry: MockConfigEntry
) -> MockConfigEntry:
    """Set up the integration for a config entry and wait until ready."""
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry
