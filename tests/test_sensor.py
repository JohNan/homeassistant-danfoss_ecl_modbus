"""Tests for the Danfoss ECL Modbus sensor platform."""

from homeassistant.components.sensor import (
    ATTR_STATE_CLASS,
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import ATTR_DEVICE_CLASS, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from modbus_connection.mock import MockModbusUnit
from pytest_homeassistant.common import MockConfigEntry

from custom_components.danfoss_ecl_modbus import DanfossEclRuntimeData
from custom_components.danfoss_ecl_modbus.const import (
    DOMAIN,
    REG_ROOM_TEMP,
    SENSOR_DISCONNECTED_RAW,
)
from tests.conftest import setup_integration


async def test_sensors(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """Test all sensor states, attributes, unique IDs, and sentinel handling."""
    await setup_integration(hass, mock_config_entry)
    entity_registry = er.async_get(hass)
    entry_id = mock_config_entry.entry_id

    actual_mode_id = entity_registry.async_get_entity_id(
        SENSOR_DOMAIN, DOMAIN, f"{entry_id}-actual_mode"
    )
    assert actual_mode_id == "sensor.danfoss_ecl_110_actual_mode"
    actual_mode_state = hass.states.get("sensor.danfoss_ecl_110_actual_mode")
    assert actual_mode_state is not None
    assert actual_mode_state.state == "auto"
    assert actual_mode_state.attributes.get(ATTR_DEVICE_CLASS) == SensorDeviceClass.ENUM

    outside_temp_id = entity_registry.async_get_entity_id(
        SENSOR_DOMAIN, DOMAIN, f"{entry_id}-outside_temp"
    )
    assert outside_temp_id == "sensor.danfoss_ecl_110_outside_temperature"
    outside_temp_state = hass.states.get(outside_temp_id)
    assert outside_temp_state is not None
    assert outside_temp_state.state == "-5.0"
    assert (
        outside_temp_state.attributes.get(ATTR_STATE_CLASS)
        == SensorStateClass.MEASUREMENT
    )

    acc_outside_id = entity_registry.async_get_entity_id(
        SENSOR_DOMAIN, DOMAIN, f"{entry_id}-accumulated_outside_temp"
    )
    assert acc_outside_id == "sensor.danfoss_ecl_110_accumulated_outside_temperature"
    acc_outside_state = hass.states.get(acc_outside_id)
    assert acc_outside_state is not None
    assert acc_outside_state.state == "-2.5"

    addition_temp_id = entity_registry.async_get_entity_id(
        SENSOR_DOMAIN, DOMAIN, f"{entry_id}-addition_temp"
    )
    assert addition_temp_id is not None
    addition_temp_state = hass.states.get(addition_temp_id)
    assert addition_temp_state is not None
    assert addition_temp_state.state == "45.5"
    assert (
        addition_temp_state.attributes.get(ATTR_STATE_CLASS)
        == SensorStateClass.MEASUREMENT
    )

    expected_remaining = {
        "desired_flow_temp": "46.0",
        "return_temp": "32.0",
        "room_temp": "21.5",
        "desired_room_temp": "21.0",
    }
    for key, expected_state in expected_remaining.items():
        entity_id = entity_registry.async_get_entity_id(
            SENSOR_DOMAIN, DOMAIN, f"{entry_id}-{key}"
        )
        assert entity_id is not None
        state = hass.states.get(entity_id)
        assert state is not None
        assert state.state == expected_state

    room_entity_id = entity_registry.async_get_entity_id(
        SENSOR_DOMAIN, DOMAIN, f"{entry_id}-room_temp"
    )
    assert room_entity_id is not None

    mock_modbus_unit.input[REG_ROOM_TEMP] = SENSOR_DISCONNECTED_RAW
    assert isinstance(mock_config_entry.runtime_data, DanfossEclRuntimeData)
    await mock_config_entry.runtime_data.coordinator.async_refresh()
    await hass.async_block_till_done()

    disconnected_state = hass.states.get(room_entity_id)
    assert disconnected_state is not None
    assert disconnected_state.state == STATE_UNKNOWN
