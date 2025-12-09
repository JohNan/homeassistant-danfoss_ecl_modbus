"""Test the Danfoss ECL Modbus switch."""
from unittest.mock import AsyncMock, patch

from custom_components.danfoss_ecl_modbus.switch import EclPumpSwitch
from homeassistant.core import HomeAssistant


async def test_switch(hass: HomeAssistant) -> None:
    """Test the Danfoss ECL Modbus switch."""
    client = AsyncMock()
    slave = 5
    switch = EclPumpSwitch(client, slave)
    switch.hass = hass
    switch.entity_id = "switch.ecl_pump_switch"

    # Test turning the switch on
    with patch.object(
        client,
        "read_holding_registers",
        return_value=AsyncMock(registers=[1]),
    ):
        await switch.async_turn_on()
    assert switch.is_on is True

    # Test turning the switch off
    with patch.object(
        client,
        "read_holding_registers",
        return_value=AsyncMock(registers=[0]),
    ):
        await switch.async_turn_off()
    assert switch.is_on is False

    # Test updating the switch state
    with patch.object(
        client,
        "read_holding_registers",
        return_value=AsyncMock(registers=[1]),
    ):
        await switch.async_update()
    assert switch.is_on is True
