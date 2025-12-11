"""Sensor platform for Danfoss ECL Modbus."""

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


@dataclass


class EclSensorEntityDescription(SensorEntityDescription):


    """Class describing Danfoss ECL sensor entities."""


    key_in_data: str = None


    scale: float = 1.0


    native_precision: int = None


SENSOR_TYPES: tuple[EclSensorEntityDescription, ...] = (
    EclSensorEntityDescription(
        key="actual_mode",
        name="Actual Mode",
        key_in_data="actual_mode",
        scale=1.0,
    ),
    EclSensorEntityDescription(
        key="outside_temp",
        name="Outside Temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        key_in_data="outside_temp",
        scale=0.1,
        native_precision=1,
    ),
    EclSensorEntityDescription(
        key="addition_temp",
        name="Addition Temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        key_in_data="addition_temp",
        scale=0.1,
        native_precision=1,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Danfoss ECL Modbus sensor platform."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = data["coordinator"]

    async_add_entities(
        EclSensor(coordinator, description) for description in SENSOR_TYPES
    )


class EclSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Danfoss ECL Modbus sensor."""

    entity_description: EclSensorEntityDescription

    def __init__(self, coordinator, description):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{description.key}"
        self._attr_has_entity_name = True
        if description.native_precision is not None:
            self._attr_native_precision = description.native_precision

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
    def native_value(self):
        """Return the state of the sensor."""
        value = self.coordinator.data.get(self.entity_description.key_in_data)
        if value is None:
            return None
        return value * self.entity_description.scale
