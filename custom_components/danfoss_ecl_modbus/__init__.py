"""The Danfoss ECL Modbus integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from homeassistant.components.modbus import async_get_unit
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SLAVE, Platform
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from modbus_connection import ModbusTcpParams

from .const import DEFAULT_PORT, DEFAULT_SLAVE
from .coordinator import DanfossEclCoordinator
from .hub import EclHub

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


@dataclass(slots=True)
class DanfossEclRuntimeData:
    """Runtime data stored on the Danfoss ECL config entry."""

    hub: EclHub
    coordinator: DanfossEclCoordinator


type DanfossEclConfigEntry = ConfigEntry[DanfossEclRuntimeData]

PLATFORMS: Final[list[Platform]] = [
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DanfossEclConfigEntry,
) -> bool:
    """Set up Danfoss ECL Modbus from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    slave = entry.data.get(CONF_SLAVE, DEFAULT_SLAVE)

    try:
        unit = async_get_unit(
            hass,
            entry,
            ModbusTcpParams(host=host, port=port),
            slave,
        )
    except HomeAssistantError as err:
        raise ConfigEntryNotReady(str(err)) from err

    hub = EclHub(unit)
    coordinator = DanfossEclCoordinator(hass, entry, hub)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = DanfossEclRuntimeData(hub=hub, coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: DanfossEclConfigEntry,
) -> bool:
    """Unload a Danfoss ECL Modbus config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
