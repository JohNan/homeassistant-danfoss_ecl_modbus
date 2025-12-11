"""Test the Danfoss ECL Modbus climate platform."""

from unittest.mock import MagicMock

import pytest
from homeassistant.components.climate import HVACMode
from homeassistant.core import HomeAssistant

from custom_components.danfoss_ecl_modbus.climate import async_setup_entry
from custom_components.danfoss_ecl_modbus.const import (
    DOMAIN,
    REG_HVAC_MODE,
    REG_TARGET_TEMP,
)


@pytest.mark.asyncio
async def test_climate_setup(hass: HomeAssistant, mock_coordinator, mock_hub):
    """Test climate setup."""
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry_id"

    hass.data[DOMAIN] = {
        "test_entry_id": {"coordinator": mock_coordinator, "hub": mock_hub}
    }

    async_add_entities = MagicMock()
    await async_setup_entry(hass, mock_entry, async_add_entities)

    assert async_add_entities.called
    climates = list(async_add_entities.call_args[0][0])
    assert len(climates) == 1
    climate = climates[0]

    # Check properties
    assert climate.hvac_mode == HVACMode.AUTO
    assert climate.target_temperature == 21

    # Test actions
    await climate.async_set_hvac_mode(HVACMode.OFF)
    mock_hub.write_register.assert_called_with(REG_HVAC_MODE, 4)

    await climate.async_set_temperature(temperature=25)
    mock_hub.write_register.assert_called_with(REG_TARGET_TEMP, 25)
