"""Base entity for Danfoss ECL Modbus."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DanfossEclCoordinator


class DanfossEclEntity(CoordinatorEntity[DanfossEclCoordinator]):
    """Base entity shared by all Danfoss ECL Modbus platforms."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: DanfossEclCoordinator) -> None:
        """Initialize the Danfoss ECL entity."""
        super().__init__(coordinator)
        entry_id = coordinator.config_entry.entry_id
        self._entry_id = entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="Danfoss ECL 110",
            manufacturer="Danfoss",
            model="ECL 110",
        )
