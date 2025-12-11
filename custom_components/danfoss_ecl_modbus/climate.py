"""Climate platform for Danfoss ECL Modbus."""

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, REG_HVAC_MODE, REG_TARGET_TEMP


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Danfoss ECL Modbus climate platform."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = data["coordinator"]
    hub = data["hub"]
    async_add_entities([EclVermeClimate(coordinator, hub)])


class EclVermeClimate(CoordinatorEntity, ClimateEntity):
    """Representation of a Danfoss ECL Modbus climate entity."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, coordinator, hub):
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._hub = hub
        self._attr_name = "Heating"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-climate"
        self._attr_has_entity_name = True
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_hvac_modes = [HVACMode.AUTO, HVACMode.OFF]
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        self._attr_min_temp = 15
        self._attr_max_temp = 30
        self._attr_target_temperature_step = 1

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
    def hvac_mode(self):
        """Return current hvac mode."""
        val = self.coordinator.data.get("hvac_mode")
        if val == 1:
            return HVACMode.AUTO
        if val == 4:
            return HVACMode.OFF
        return None

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self.coordinator.data.get("target_temp")

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.AUTO:
            await self._hub.write_register(REG_HVAC_MODE, 1)
        elif hvac_mode == HVACMode.OFF:
            await self._hub.write_register(REG_HVAC_MODE, 4)
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temp = kwargs.get("temperature")
        if temp:
            await self._hub.write_register(REG_TARGET_TEMP, int(temp))
            await self.coordinator.async_request_refresh()
