"""Test the Danfoss ECL Modbus config flow."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries, setup
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.danfoss_ecl_modbus.const import DOMAIN


@pytest.mark.asyncio
async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    with (
        patch(
            "custom_components.danfoss_ecl_modbus.config_flow.EclHub"
        ) as mock_hub_class,
        patch(
            "custom_components.danfoss_ecl_modbus.async_setup_entry",
            return_value=True,
        ) as mock_setup_entry,
    ):
        mock_hub = mock_hub_class.return_value
        mock_hub.connect = AsyncMock(return_value=True)
        mock_hub.close = AsyncMock()

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "host": "1.2.3.4",
                "port": 502,
                "slave": 5,
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "1.2.3.4"
    assert result2["data"] == {
        "host": "1.2.3.4",
        "port": 502,
        "slave": 5,
    }
    assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.asyncio
async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.danfoss_ecl_modbus.config_flow.EclHub"
    ) as mock_hub_class:
        mock_hub = mock_hub_class.return_value
        mock_hub.connect = AsyncMock(return_value=False)
        mock_hub.close = AsyncMock()

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "host": "1.2.3.4",
                "port": 502,
                "slave": 5,
            },
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}
