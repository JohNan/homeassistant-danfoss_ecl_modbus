"""Tests for the Danfoss ECL Modbus number platform."""

import pytest
from homeassistant.components.number import (
    ATTR_VALUE,
    DOMAIN as NUMBER_DOMAIN,
    SERVICE_SET_VALUE,
)
from homeassistant.const import ATTR_ENTITY_ID, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from modbus_connection.encode import encode_int
from modbus_connection.exceptions import (
    IllegalDataAddressError,
    ModbusConnectionError,
)
from modbus_connection.mock import MockModbusUnit
from pytest_homeassistant.common import MockConfigEntry

from custom_components.danfoss_ecl_modbus import DanfossEclRuntimeData
from custom_components.danfoss_ecl_modbus.const import (
    DOMAIN,
    REG_PARALLEL_DISPLACEMENT,
    REG_SLOPE,
)
from tests.conftest import setup_integration


async def test_numbers(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """Test number entities initial states, value writes, and error handling."""
    await setup_integration(hass, mock_config_entry)
    entity_registry = er.async_get(hass)
    entry_id = mock_config_entry.entry_id

    expected_initial: dict[str, float] = {
        "heating_curve_slope": 1.8,
        "parallel_displacement": -4.0,
        "setback_temp": 17.0,
        "flow_temp_min": 20.0,
        "flow_temp_max": 70.0,
        "cutout_temp": 18.0,
        "return_temp_limit": 50.0,
    }
    entity_ids: dict[str, str] = {}
    for key, expected_value in expected_initial.items():
        entity_id = entity_registry.async_get_entity_id(
            NUMBER_DOMAIN, DOMAIN, f"{entry_id}-{key}"
        )
        assert entity_id is not None
        entity_ids[key] = entity_id
        state = hass.states.get(entity_id)
        assert state is not None
        assert float(state.state) == expected_value

    slope_entity_id = entity_ids["heating_curve_slope"]
    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {ATTR_ENTITY_ID: slope_entity_id, ATTR_VALUE: 2.3},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert mock_modbus_unit.holding[REG_SLOPE] == 23
    slope_state = hass.states.get(slope_entity_id)
    assert slope_state is not None
    assert slope_state.state == "2.3"

    disp_entity_id = entity_ids["parallel_displacement"]
    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {ATTR_ENTITY_ID: disp_entity_id, ATTR_VALUE: -6},
        blocking=True,
    )
    assert isinstance(mock_config_entry.runtime_data, DanfossEclRuntimeData)
    await mock_config_entry.runtime_data.coordinator.async_refresh()
    await hass.async_block_till_done()
    assert (
        mock_modbus_unit.holding[REG_PARALLEL_DISPLACEMENT]
        == encode_int(-6, count=1)[0]
    )
    disp_state = hass.states.get(disp_entity_id)
    assert disp_state is not None
    assert float(disp_state.state) == -6.0
    assert disp_state.state in ("-6", "-6.0")

    mock_modbus_unit.fail_write(REG_SLOPE, ModbusConnectionError("err"))
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            NUMBER_DOMAIN,
            SERVICE_SET_VALUE,
            {ATTR_ENTITY_ID: slope_entity_id, ATTR_VALUE: 2.0},
            blocking=True,
        )


async def test_number_unsupported_register(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """Test number entity reports unknown when its register is unsupported."""
    mock_modbus_unit.fail_read(
        REG_SLOPE,
        IllegalDataAddressError(2),
        register_type="holding",
    )
    await setup_integration(hass, mock_config_entry)
    entity_registry = er.async_get(hass)
    slope_entity_id = entity_registry.async_get_entity_id(
        NUMBER_DOMAIN,
        DOMAIN,
        f"{mock_config_entry.entry_id}-heating_curve_slope",
    )
    assert slope_entity_id is not None
    state = hass.states.get(slope_entity_id)
    assert state is not None
    assert state.state == STATE_UNKNOWN
