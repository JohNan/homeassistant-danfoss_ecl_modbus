"""Binary sensor platform for ECL Modbus."""
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
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
    """Set up the ECL Modbus binary sensor platform."""
    client = hass.data[DOMAIN][config_entry.entry_id]
    slave = config_entry.data[CONF_SLAVE]
    async_add_entities([EclPumpBinarySensor(client, slave)])


class EclPumpBinarySensor(BinarySensorEntity):
    """Representation of an ECL Modbus binary sensor."""

    def __init__(self, client, slave):
        """Initialize the binary sensor."""
        self._client = client
        self._slave = slave
        self._attr_name = "ECL Pump"
        self._attr_unique_id = "ecl-pump"
        self._attr_device_class = BinarySensorDeviceClass.RUNNING
        self._is_on = None

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._is_on

    async def async_update(self):
        """Fetch new state data for the binary sensor."""
        result = await self._client.read_input_registers(4001, 1, self._slave)
        if result.registers:
            self._is_on = result.registers[0] == 1
