"""Test the Danfoss ECL Modbus config flow."""
from unittest.mock import patch

from homeassistant import config_entries, setup
from custom_components.danfoss_ecl_modbus.const import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
import pytest

@pytest.mark.parametrize("enable_custom_integrations", [True])
async def test_form(hass: HomeAssistant, enable_custom_integrations: bool) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    with patch(
        "custom_components.danfoss_ecl_modbus.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "host": "1.1.1.1",
                "port": 502,
                "slave": 5,
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "1.1.1.1"
    assert result2["data"] == {
        "host": "1.1.1.1",
        "port": 502,
        "slave": 5,
    }
    assert len(mock_setup_entry.mock_calls) == 1
