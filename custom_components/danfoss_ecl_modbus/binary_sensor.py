"""Binary sensor platform for Danfoss ECL Modbus."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Danfoss ECL Modbus binary sensor platform."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = data["coordinator"]
    async_add_entities([EclPumpBinarySensor(coordinator)])


class EclPumpBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Danfoss ECL Modbus binary sensor."""

    def __init__(self, coordinator):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_name = "Pump"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-pump-binary"
        self._attr_has_entity_name = True
        self._attr_device_class = BinarySensorDeviceClass.RUNNING

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": "Danfoss ECL 110",
            "manufacturer": "Danfoss",
            "model": "ECL 110",
        }

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        val = self.coordinator.data.get("pump")
        if val is None:
            return None
        return val == 1
