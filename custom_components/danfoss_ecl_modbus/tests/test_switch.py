"""Test the Danfoss ECL Modbus switch platform."""

from unittest.mock import MagicMock

import pytest
from homeassistant.core import HomeAssistant

from custom_components.danfoss_ecl_modbus.const import DOMAIN, REG_PUMP
from custom_components.danfoss_ecl_modbus.switch import async_setup_entry


@pytest.mark.asyncio
async def test_switch_setup(hass: HomeAssistant, mock_coordinator, mock_hub):
    """Test switch setup."""
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry_id"
    hass.data[DOMAIN] = {
        "test_entry_id": {"coordinator": mock_coordinator, "hub": mock_hub}
    }

    async_add_entities = MagicMock()
    await async_setup_entry(hass, mock_entry, async_add_entities)

    entities = list(async_add_entities.call_args[0][0])
    assert len(entities) == 1
    switch = entities[0]

    assert switch.is_on is True

    await switch.async_turn_off()
    mock_hub.write_register.assert_called_with(REG_PUMP, 0)

    await switch.async_turn_on()
    mock_hub.write_register.assert_called_with(REG_PUMP, 1)
