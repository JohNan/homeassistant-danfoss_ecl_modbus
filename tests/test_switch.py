"""Tests for the Danfoss ECL Modbus switch platform."""

import pytest
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from modbus_connection.exceptions import ModbusConnectionError
from modbus_connection.mock import MockModbusUnit
from pytest_homeassistant.common import MockConfigEntry

from custom_components.danfoss_ecl_modbus import DanfossEclRuntimeData
from custom_components.danfoss_ecl_modbus.const import DOMAIN, REG_PUMP
from tests.conftest import setup_integration


async def test_pump_switch(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """Test pump switch initial state, toggling, and write error handling."""
    await setup_integration(hass, mock_config_entry)
    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id(
        SWITCH_DOMAIN, DOMAIN, f"{mock_config_entry.entry_id}-pump-switch"
    )
    assert entity_id is not None

    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == STATE_ON

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert mock_modbus_unit.holding[REG_PUMP] == 0
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == STATE_OFF

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    assert isinstance(mock_config_entry.runtime_data, DanfossEclRuntimeData)
    await mock_config_entry.runtime_data.coordinator.async_refresh()
    await hass.async_block_till_done()
    assert mock_modbus_unit.holding[REG_PUMP] == 1
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == STATE_ON

    mock_modbus_unit.fail_write(REG_PUMP, ModbusConnectionError("err"))
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_OFF,
            {ATTR_ENTITY_ID: entity_id},
            blocking=True,
        )
