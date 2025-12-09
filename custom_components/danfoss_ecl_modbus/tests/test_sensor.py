"""Test the Danfoss ECL Modbus sensors."""
from unittest.mock import AsyncMock, patch

from pytest import approx
from custom_components.danfoss_ecl_modbus.sensor import (
    EclActualModeSensor,
    EclAdditionTempSensor,
    EclOutsideTempSensor,
)
from homeassistant.core import HomeAssistant


async def test_sensors(hass: HomeAssistant) -> None:
    """Test the Danfoss ECL Modbus sensors."""
    client = AsyncMock()
    slave = 5
    mode_sensor = EclActualModeSensor(client, slave)
    mode_sensor.hass = hass
    mode_sensor.entity_id = "sensor.ecl_actual_mode"

    outside_temp_sensor = EclOutsideTempSensor(client, slave)
    outside_temp_sensor.hass = hass
    outside_temp_sensor.entity_id = "sensor.ecl_outside_temp"

    addition_temp_sensor = EclAdditionTempSensor(client, slave)
    addition_temp_sensor.hass = hass
    addition_temp_sensor.entity_id = "sensor.ecl_addition_temp"

    # Test updating the mode sensor
    with patch.object(
        client,
        "read_input_registers",
        return_value=AsyncMock(registers=[3]),
    ):
        await mode_sensor.async_update()
    assert mode_sensor.native_value == 3

    # Test updating the outside temperature sensor
    with patch.object(
        client,
        "read_input_registers",
        return_value=AsyncMock(registers=[255]),
    ):
        await outside_temp_sensor.async_update()
    assert outside_temp_sensor.native_value == approx(25.5)

    # Test updating the addition temperature sensor
    with patch.object(
        client,
        "read_input_registers",
        return_value=AsyncMock(registers=[222]),
    ):
        await addition_temp_sensor.async_update()
    assert addition_temp_sensor.native_value == approx(22.2)
