"""Tests for the Danfoss ECL Modbus climate platform."""

import pytest
from homeassistant.components.climate import (
    ATTR_CURRENT_TEMPERATURE,
    ATTR_HVAC_MODE,
    ATTR_PRESET_MODE,
    DOMAIN as CLIMATE_DOMAIN,
    SERVICE_SET_HVAC_MODE,
    SERVICE_SET_PRESET_MODE,
    SERVICE_SET_TEMPERATURE,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_SUPPORTED_FEATURES,
    ATTR_TEMPERATURE,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from modbus_connection.exceptions import ModbusConnectionError
from modbus_connection.mock import MockModbusUnit
from pytest_homeassistant.common import MockConfigEntry

from custom_components.danfoss_ecl_modbus import DanfossEclRuntimeData
from custom_components.danfoss_ecl_modbus.climate import EclVermeClimate
from custom_components.danfoss_ecl_modbus.const import (
    DOMAIN,
    REG_HVAC_MODE,
    REG_ROOM_TEMP,
    REG_TARGET_TEMP,
    SENSOR_DISCONNECTED_RAW,
)
from tests.conftest import setup_integration


async def test_climate_entity(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """Test climate state, modes, presets, target temperature, and errors."""
    await setup_integration(hass, mock_config_entry)
    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id(
        CLIMATE_DOMAIN, DOMAIN, f"{mock_config_entry.entry_id}-climate"
    )
    assert entity_id is not None

    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == HVACMode.AUTO
    assert state.attributes[ATTR_PRESET_MODE] == "auto"
    assert state.attributes[ATTR_CURRENT_TEMPERATURE] == 21.5
    assert state.attributes[ATTR_TEMPERATURE] == 21

    expected_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    assert (
        state.attributes[ATTR_SUPPORTED_FEATURES] & expected_features
    ) == expected_features

    assert isinstance(mock_config_entry.runtime_data, DanfossEclRuntimeData)
    coordinator = mock_config_entry.runtime_data.coordinator

    for mode, expected_reg in (
        (HVACMode.HEAT, 2),
        (HVACMode.OFF, 4),
        (HVACMode.AUTO, 1),
    ):
        await hass.services.async_call(
            CLIMATE_DOMAIN,
            SERVICE_SET_HVAC_MODE,
            {ATTR_ENTITY_ID: entity_id, ATTR_HVAC_MODE: mode},
            blocking=True,
        )
        await coordinator.async_refresh()
        await hass.async_block_till_done()
        assert mock_modbus_unit.holding[REG_HVAC_MODE] == expected_reg
        state = hass.states.get(entity_id)
        assert state is not None
        assert state.state == mode

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert mock_modbus_unit.holding[REG_HVAC_MODE] == 4
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == HVACMode.OFF

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert mock_modbus_unit.holding[REG_HVAC_MODE] == 1
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == HVACMode.AUTO

    for preset, expected_reg in (
        ("comfort", 2),
        ("setback", 3),
        ("standby", 4),
        ("auto", 1),
    ):
        await hass.services.async_call(
            CLIMATE_DOMAIN,
            SERVICE_SET_PRESET_MODE,
            {ATTR_ENTITY_ID: entity_id, ATTR_PRESET_MODE: preset},
            blocking=True,
        )
        await coordinator.async_refresh()
        await hass.async_block_till_done()
        assert mock_modbus_unit.holding[REG_HVAC_MODE] == expected_reg
        state = hass.states.get(entity_id)
        assert state is not None
        assert state.attributes[ATTR_PRESET_MODE] == preset

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_TEMPERATURE,
        {ATTR_ENTITY_ID: entity_id, ATTR_TEMPERATURE: 24},
        blocking=True,
    )
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert mock_modbus_unit.holding[REG_TARGET_TEMP] == 24
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.attributes[ATTR_TEMPERATURE] == 24

    mock_modbus_unit.input[REG_ROOM_TEMP] = SENSOR_DISCONNECTED_RAW
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.attributes.get(ATTR_CURRENT_TEMPERATURE) is None

    mock_modbus_unit.fail_write(REG_TARGET_TEMP, ModbusConnectionError("err"))
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            CLIMATE_DOMAIN,
            SERVICE_SET_TEMPERATURE,
            {ATTR_ENTITY_ID: entity_id, ATTR_TEMPERATURE: 22},
            blocking=True,
        )

    climate_entity = EclVermeClimate(coordinator, mock_config_entry.runtime_data.hub)
    with pytest.raises(HomeAssistantError):
        await climate_entity.async_set_hvac_mode(HVACMode.COOL)
    with pytest.raises(HomeAssistantError):
        await climate_entity.async_set_preset_mode("invalid")
