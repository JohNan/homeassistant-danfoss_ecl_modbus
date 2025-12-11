"""The Danfoss ECL Modbus integration."""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SLAVE
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_PORT, DEFAULT_SLAVE, DOMAIN
from .hub import EclHub

_LOGGER = logging.getLogger(__name__)
# Removed switch/binary_sensor as they weren't in the original verified code snippets.
PLATFORMS = ["sensor", "climate", "binary_sensor", "switch"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Danfoss ECL Modbus from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    slave = entry.data.get(CONF_SLAVE, DEFAULT_SLAVE)

    hub = EclHub(host, port, slave)

    # Verify connection
    try:
        if not await hub.connect():
            raise ConfigEntryNotReady(
                f"Failed to connect to Modbus device at {host}:{port}"
            )
    except Exception as e:
        raise ConfigEntryNotReady(
            f"Failed to connect to Modbus device at {host}:{port}"
        ) from e

    async def async_update_data():
        """Fetch data from API endpoint."""
        try:
            return await hub.update()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Danfoss ECL Modbus",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "hub": hub,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    hub = data["hub"]
    await hub.close()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
