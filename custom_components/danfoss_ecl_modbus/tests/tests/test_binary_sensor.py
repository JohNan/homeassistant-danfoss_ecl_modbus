"""Test the Danfoss ECL Modbus binary sensor."""
from unittest.mock import AsyncMock, patch

from custom_components.danfoss_ecl_modbus.binary_sensor import EclPumpBinarySensor
from homeassistant.core import HomeAssistant


async def test_binary_sensor(hass: HomeAssistant) -> None:
    """Test the Danfoss ECL Modbus binary sensor."""
    client = AsyncMock()
    slave = 5
    binary_sensor = EclPumpBinarySensor(client, slave)

    # Test updating the binary sensor state
    with patch.object(
        client,
        "read_input_registers",
        return_value=AsyncMock(registers=[1]),
    ):
        await binary_sensor.async_update()
    assert binary_sensor.is_on is True
