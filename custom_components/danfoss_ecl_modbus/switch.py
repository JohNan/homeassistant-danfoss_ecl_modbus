"""Switch platform for Danfoss ECL Modbus."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, REG_PUMP


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Danfoss ECL Modbus switch platform."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = data["coordinator"]
    hub = data["hub"]
    async_add_entities([EclPumpSwitch(coordinator, hub)])


class EclPumpSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Danfoss ECL Modbus switch."""

    def __init__(self, coordinator, hub):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._hub = hub
        self._attr_name = "Pump Switch"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-pump-switch"
        self._attr_has_entity_name = True

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
        """Return true if the switch is on."""
        val = self.coordinator.data.get("pump")
        if val is None:
            return None
        return val == 1

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self._hub.write_register(REG_PUMP, 1)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self._hub.write_register(REG_PUMP, 0)
        await self.coordinator.async_request_refresh()
