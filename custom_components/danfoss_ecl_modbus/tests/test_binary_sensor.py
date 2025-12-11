"""Test the Danfoss ECL Modbus binary sensor platform."""

from unittest.mock import MagicMock

import pytest
from homeassistant.core import HomeAssistant

from custom_components.danfoss_ecl_modbus.binary_sensor import async_setup_entry
from custom_components.danfoss_ecl_modbus.const import DOMAIN


@pytest.mark.asyncio
async def test_binary_sensor_setup(hass: HomeAssistant, mock_coordinator):
    """Test binary sensor setup."""
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry_id"
    hass.data[DOMAIN] = {"test_entry_id": {"coordinator": mock_coordinator}}

    async_add_entities = MagicMock()
    await async_setup_entry(hass, mock_entry, async_add_entities)

    entities = list(async_add_entities.call_args[0][0])
    assert len(entities) == 1
    assert entities[0].is_on is True
