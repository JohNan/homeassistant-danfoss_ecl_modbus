"""Climate platform for ECL Modbus."""
from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SLAVE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the ECL Modbus climate platform."""
    client = hass.data[DOMAIN][config_entry.entry_id]
    slave = config_entry.data[CONF_SLAVE]
    async_add_entities([EclVermeClimate(client, slave)])


class EclVermeClimate(ClimateEntity):
    """Representation of an ECL Modbus climate entity."""

    def __init__(self, client, slave):
        """Initialize the climate entity."""
        self._client = client
        self._slave = slave
        self._attr_name = "ECL Värme"
        self._attr_unique_id = "ecl-heating"
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_hvac_modes = [HVACMode.AUTO, HVACMode.OFF]
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        self._attr_min_temp = 15
        self._attr_max_temp = 30
        self._attr_target_temperature_step = 1
        self._hvac_mode = None
        self._current_temperature = None
        self._target_temperature = None

    @property
    def hvac_mode(self):
        """Return current hvac mode."""
        return self._hvac_mode

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temperature

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.AUTO:
            await self._client.write_register(4200, 1, self._slave)
        elif hvac_mode == HVACMode.OFF:
            await self._client.write_register(4200, 4, self._slave)
        self._hvac_mode = hvac_mode
        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get("temperature")
        if temperature is not None:
            await self._client.write_register(11179, int(temperature), self._slave)
            self._target_temperature = temperature
            self.async_write_ha_state()

    async def async_update(self):
        """Fetch new state data for the climate entity."""
        # Get current temperature
        result = await self._client.read_holding_registers(11179, 1, self._slave)
        if result.registers:
            self._current_temperature = result.registers[0]

        # Get target temperature
        result = await self._client.read_holding_registers(11179, 1, self._slave)
        if result.registers:
            self._target_temperature = result.registers[0]

        # Get HVAC mode
        result = await self._client.read_holding_registers(4200, 1, self._slave)
        if result.registers:
            mode = result.registers[0]
            if mode == 1:
                self._hvac_mode = HVACMode.AUTO
            elif mode == 4:
                self._hvac_mode = HVACMode.OFF
