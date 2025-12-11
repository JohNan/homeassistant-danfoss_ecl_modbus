"""Test the Danfoss ECL Modbus sensor platform."""

from unittest.mock import MagicMock

import pytest
from homeassistant.core import HomeAssistant

from custom_components.danfoss_ecl_modbus.const import DOMAIN
from custom_components.danfoss_ecl_modbus.sensor import async_setup_entry


@pytest.mark.asyncio
async def test_sensor_setup(hass: HomeAssistant, mock_coordinator):
    """Test sensor setup."""
    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry_id"

    hass.data[DOMAIN] = {"test_entry_id": {"coordinator": mock_coordinator}}

    async_add_entities = MagicMock()
    await async_setup_entry(hass, mock_entry, async_add_entities)

    assert async_add_entities.called
    sensors = list(async_add_entities.call_args[0][0])
    assert len(sensors) == 3

    # Check values
    for sensor in sensors:
        if sensor.entity_description.key == "actual_mode":
            assert sensor.native_value == 1
        elif sensor.entity_description.key == "outside_temp":
            assert sensor.native_value == 10.5
        elif sensor.entity_description.key == "addition_temp":
            assert sensor.native_value == 5.0
