"""Sensor platform for Danfoss ECL Modbus."""
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
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
    """Set up the Danfoss ECL Modbus sensor platform."""
    client = hass.data[DOMAIN][config_entry.entry_id]
    slave = config_entry.data[CONF_SLAVE]
    async_add_entities(
        [
            EclActualModeSensor(client, slave),
            EclOutsideTempSensor(client, slave),
            EclAdditionTempSensor(client, slave),
        ]
    )


class EclActualModeSensor(SensorEntity):
    """Representation of a Danfoss ECL Modbus sensor."""

    def __init__(self, client, slave):
        """Initialize the sensor."""
        self._client = client
        self._slave = slave
        self._attr_name = "ECL Actual Mode"
        self._attr_unique_id = "ecl-actual-mode"
        self._attr_native_value = None

    async def async_update(self):
        """Fetch new state data for the sensor."""
        result = await self._client.read_input_registers(4210, 1, self._slave)
        if result.registers:
            self._attr_native_value = result.registers[0]


class EclOutsideTempSensor(SensorEntity):
    """Representation of a Danfoss ECL Modbus temperature sensor."""

    def __init__(self, client, slave):
        """Initialize the sensor."""
        self._client = client
        self._slave = slave
        self._attr_name = "ECL Outside Temp"
        self._attr_unique_id = "ecl-outside-temp"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_native_value = None
        self._attr_native_precision = 1

    async def async_update(self):
        """Fetch new state data for the sensor."""
        result = await self._client.read_input_registers(11200, 1, self._slave)
        if result.registers:
            self._attr_native_value = result.registers[0] * 0.1


class EclAdditionTempSensor(SensorEntity):
    """Representation of a Danfoss ECL Modbus temperature sensor."""

    def __init__(self, client, slave):
        """Initialize the sensor."""
        self._client = client
        self._slave = slave
        self._attr_name = "ECL Addition Temp"
        self._attr_unique_id = "ecl-addition-temp"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_native_value = None
        self._attr_native_precision = 1

    async def async_update(self):
        """Fetch new state data for the sensor."""
        result = await self._client.read_input_registers(11202, 1, self._slave)
        if result.registers:
            self._attr_native_value = result.registers[0] * 0.1
