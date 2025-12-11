from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from custom_components.danfoss_ecl_modbus.hub import EclHub


@pytest.fixture
def mock_hub():
    hub = MagicMock(spec=EclHub)
    hub.update = AsyncMock(
        return_value={
            "hvac_mode": 1,
            "actual_mode": 1,
            "target_temp": 21,
            "outside_temp": 105,  # scaled 0.1 -> 10.5
            "addition_temp": 50,  # scaled 0.1 -> 5.0
            "pump": 1,
        }
    )
    hub.write_register = AsyncMock()
    return hub


@pytest.fixture
def mock_coordinator(hass, mock_hub):
    coordinator = MagicMock(spec=DataUpdateCoordinator)
    coordinator.hass = hass
    # Set data directly as dict, since CoordinatorEntity reads property
    coordinator.data = {
        "hvac_mode": 1,
        "actual_mode": 1,
        "target_temp": 21,
        "outside_temp": 105,
        "addition_temp": 50,
        "pump": 1,
    }
    coordinator.async_request_refresh = AsyncMock()

    mock_entry = MagicMock()
    mock_entry.entry_id = "test_entry_id"
    coordinator.config_entry = mock_entry

    return coordinator


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield
