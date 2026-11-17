"""Tests for the Danfoss ECL Modbus binary sensor platform."""

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.const import STATE_OFF, STATE_ON, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from modbus_connection.mock import MockModbusUnit
from pytest_homeassistant.common import MockConfigEntry

from custom_components.danfoss_ecl_modbus import DanfossEclRuntimeData
from custom_components.danfoss_ecl_modbus.const import DOMAIN, REG_VALVE_OPENING
from tests.conftest import setup_integration


async def test_binary_sensors(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """Test binary sensor states, entity categories, and updates."""
    await setup_integration(hass, mock_config_entry)
    entity_registry = er.async_get(hass)
    entry_id = mock_config_entry.entry_id

    pump_entity_id = entity_registry.async_get_entity_id(
        BINARY_SENSOR_DOMAIN, DOMAIN, f"{entry_id}-pump-binary"
    )
    assert pump_entity_id is not None
    pump_state = hass.states.get(pump_entity_id)
    assert pump_state is not None
    assert pump_state.state == STATE_ON

    valve_opening_id = entity_registry.async_get_entity_id(
        BINARY_SENSOR_DOMAIN, DOMAIN, f"{entry_id}-valve-opening"
    )
    assert valve_opening_id is not None
    valve_opening_entry = entity_registry.async_get(valve_opening_id)
    assert valve_opening_entry is not None
    assert valve_opening_entry.entity_category is EntityCategory.DIAGNOSTIC
    valve_opening_state = hass.states.get(valve_opening_id)
    assert valve_opening_state is not None
    assert valve_opening_state.state == STATE_OFF

    valve_closing_id = entity_registry.async_get_entity_id(
        BINARY_SENSOR_DOMAIN, DOMAIN, f"{entry_id}-valve-closing"
    )
    assert valve_closing_id is not None
    valve_closing_entry = entity_registry.async_get(valve_closing_id)
    assert valve_closing_entry is not None
    assert valve_closing_entry.entity_category is EntityCategory.DIAGNOSTIC
    valve_closing_state = hass.states.get(valve_closing_id)
    assert valve_closing_state is not None
    assert valve_closing_state.state == STATE_OFF

    mock_modbus_unit.holding[REG_VALVE_OPENING] = 1
    assert isinstance(mock_config_entry.runtime_data, DanfossEclRuntimeData)
    await mock_config_entry.runtime_data.coordinator.async_refresh()
    await hass.async_block_till_done()

    updated_state = hass.states.get(valve_opening_id)
    assert updated_state is not None
    assert updated_state.state == STATE_ON
