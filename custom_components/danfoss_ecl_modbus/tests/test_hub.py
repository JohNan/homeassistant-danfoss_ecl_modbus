"""Test the Danfoss ECL Modbus Hub."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.danfoss_ecl_modbus.const import REG_HVAC_MODE
from custom_components.danfoss_ecl_modbus.hub import EclHub


@pytest.fixture
def mock_client():
    """Mock the AsyncModbusTcpClient."""
    with patch(
        "custom_components.danfoss_ecl_modbus.hub.AsyncModbusTcpClient"
    ) as mock_cls:
        client = mock_cls.return_value
        client.connect = AsyncMock(return_value=True)
        client.connected = True
        client.close = AsyncMock()
        client.write_register = AsyncMock()
        client.read_holding_registers = AsyncMock()
        client.read_input_registers = AsyncMock()
        yield client


@pytest.mark.asyncio
async def test_update_success(mock_client):
    """Test successful data update."""
    hub = EclHub("1.2.3.4", 502, 5)

    # Mock register responses
    success_response = MagicMock()
    success_response.isError.return_value = False
    success_response.registers = [10]

    mock_client.read_holding_registers.return_value = success_response
    mock_client.read_input_registers.return_value = success_response

    data = await hub.update()

    assert data["hvac_mode"] == 10
    assert data["actual_mode"] == 10
    assert data["pump"] == 10
    # Connect not called because we mocked it as already connected
    assert not mock_client.connect.called
    mock_client.read_holding_registers.assert_called()
    mock_client.read_input_registers.assert_called()


@pytest.mark.asyncio
async def test_write_register(mock_client):
    """Test writing a register."""
    hub = EclHub("1.2.3.4", 502, 5)
    await hub.write_register(REG_HVAC_MODE, 1)
    mock_client.write_register.assert_called_with(REG_HVAC_MODE, 1, device_id=5)


@pytest.mark.asyncio
async def test_connection_failure(mock_client):
    """Test connection failure."""
    hub = EclHub("1.2.3.4", 502, 5)
    mock_client.connected = False
    mock_client.connect.return_value = False

    with pytest.raises(ConnectionError):
        await hub.update()
