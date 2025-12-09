"""Test the Danfoss ECL Modbus climate entity."""
from unittest.mock import AsyncMock, patch

from homeassistant.components.climate import HVACMode
from custom_components.danfoss_ecl_modbus.climate import EclVermeClimate
from homeassistant.core import HomeAssistant


async def test_climate(hass: HomeAssistant) -> None:
    """Test the Danfoss ECL Modbus climate entity."""
    client = AsyncMock()
    slave = 5
    climate = EclVermeClimate(client, slave)
    climate.hass = hass
    climate.entity_id = "climate.ecl_varme"

    # Test setting the HVAC mode
    await climate.async_set_hvac_mode(HVACMode.AUTO)
    client.write_register.assert_called_with(4200, 1, 5)
    assert climate.hvac_mode == HVACMode.AUTO

    # Test setting the temperature
    await climate.async_set_temperature(temperature=22)
    client.write_register.assert_called_with(11179, 22, 5)
    assert climate.target_temperature == 22

    # Test updating the climate state
    with patch.object(
        client,
        "read_holding_registers",
        side_effect=[
            AsyncMock(registers=[23]),  # Current temperature
            AsyncMock(registers=[21]),  # Target temperature
            AsyncMock(registers=[4]),   # HVAC mode
        ],
    ):
        await climate.async_update()
    assert climate.current_temperature == 23
    assert climate.target_temperature == 21
    assert climate.hvac_mode == HVACMode.OFF
