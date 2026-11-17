"""Coordinator for Danfoss ECL Modbus data updates."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Final

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from modbus_connection import ModbusError

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .hub import EclHub

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL: Final = timedelta(seconds=30)


class DanfossEclCoordinator(DataUpdateCoordinator[dict[str, int | None]]):
    """Data update coordinator for Danfoss ECL Modbus."""

    config_entry: ConfigEntry[Any]

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry[Any],
        hub: EclHub,
    ) -> None:
        """Initialize the Danfoss ECL coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name="Danfoss ECL Modbus",
            update_interval=UPDATE_INTERVAL,
        )
        self.hub = hub

    async def _async_update_data(self) -> dict[str, int | None]:
        """Fetch the latest register values from the Danfoss ECL device."""
        try:
            return await self.hub.update()
        except (ModbusError, OSError, TimeoutError) as err:
            raise UpdateFailed(
                f"Error communicating with Modbus device: {err}"
            ) from err
