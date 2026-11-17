"""Tests for Danfoss ECL Modbus integration setup and unload."""

from unittest.mock import patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from modbus_connection.exceptions import ModbusConnectionError
from modbus_connection.mock import MockModbusUnit
from pytest_homeassistant.common import MockConfigEntry

from custom_components.danfoss_ecl_modbus import DanfossEclRuntimeData
from custom_components.danfoss_ecl_modbus.const import REG_PUMP
from custom_components.danfoss_ecl_modbus.hub import EclHub
from tests.conftest import setup_integration


@pytest.mark.usefixtures("mock_modbus_connection")
async def test_setup_and_unload(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test setting up and unloading a config entry."""
    await setup_integration(hass, mock_config_entry)

    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert isinstance(mock_config_entry.runtime_data, DanfossEclRuntimeData)
    assert isinstance(mock_config_entry.runtime_data.hub, EclHub)
    assert isinstance(mock_config_entry.runtime_data.coordinator, DataUpdateCoordinator)

    unload_ok = await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert unload_ok is True
    unloaded_entry = hass.config_entries.async_get_entry(mock_config_entry.entry_id)
    assert unloaded_entry is not None
    assert unloaded_entry.state is ConfigEntryState.NOT_LOADED


async def test_setup_first_refresh_failure(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """Test setup retries when the first coordinator refresh fails."""
    mock_modbus_unit.fail_read(
        REG_PUMP,
        ModbusConnectionError("offline"),
        register_type="holding",
    )

    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_setup_async_get_unit_error(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test setup retries when async_get_unit raises HomeAssistantError."""
    with patch(
        "custom_components.danfoss_ecl_modbus.async_get_unit",
        side_effect=HomeAssistantError("conflict"),
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY
