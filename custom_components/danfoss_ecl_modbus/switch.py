"""Switch platform for ECL Modbus."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SLAVE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the ECL Modbus switch platform."""
    client = hass.data[DOMAIN][config_entry.entry_id]
    slave = config_entry.data[CONF_SLAVE]
    async_add_entities([EclPumpSwitch(client, slave)])


class EclPumpSwitch(SwitchEntity):
    """Representation of an ECL Modbus switch."""

    def __init__(self, client, slave):
        """Initialize the switch."""
        self._client = client
        self._slave = slave
        self._attr_name = "ECL Pump Switch"
        self._attr_unique_id = "ecl-pump-switch"
        self._is_on = None

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self._client.write_register(4001, 1, self._slave)
        # Verification
        result = await self._client.read_holding_registers(4001, 1, self._slave)
        if result.registers[0] == 1:
            self._is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self._client.write_register(4001, 0, self._slave)
        # Verification
        result = await self._client.read_holding_registers(4001, 1, self._slave)
        if result.registers[0] == 0:
            self._is_on = False
            self.async_write_ha_state()

    async def async_update(self):
        """Fetch new state data for the switch."""
        result = await self._client.read_holding_registers(4001, 1, self._slave)
        if result.registers:
            self._is_on = result.registers[0] == 1
