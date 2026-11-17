"""Sensor platform for Danfoss ECL Modbus."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature

from .const import ACTUAL_MODE_MAP
from .entity import DanfossEclEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
    from homeassistant.helpers.typing import StateType

    from . import DanfossEclConfigEntry
    from .coordinator import DanfossEclCoordinator


@dataclass(frozen=True, kw_only=True)
class EclSensorEntityDescription(SensorEntityDescription):
    """Describe a Danfoss ECL sensor entity."""

    value_fn: Callable[[int], StateType]


def _map_actual_mode(value: int) -> StateType:
    """Map raw actual mode register value to an enum state."""
    return ACTUAL_MODE_MAP.get(value)


def _scale_tenth(value: int) -> float:
    """Scale a tenths-of-degree integer register value to Celsius."""
    return round(value * 0.1, 1)


def _temp_sensor(
    key: str,
    *,
    translation_key: str | None = None,
) -> EclSensorEntityDescription:
    """Build an entity description for a tenth-degree Celsius sensor."""
    return EclSensorEntityDescription(
        key=key,
        translation_key=translation_key or key,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=_scale_tenth,
    )


SENSOR_TYPES: Final[tuple[EclSensorEntityDescription, ...]] = (
    EclSensorEntityDescription(
        key="actual_mode",
        translation_key="actual_mode",
        device_class=SensorDeviceClass.ENUM,
        options=list(ACTUAL_MODE_MAP.values()),
        value_fn=_map_actual_mode,
    ),
    _temp_sensor("outside_temp"),
    _temp_sensor("accumulated_outside_temp"),
    _temp_sensor("addition_temp", translation_key="flow_temp"),
    _temp_sensor("desired_flow_temp"),
    _temp_sensor("return_temp"),
    _temp_sensor("room_temp"),
    _temp_sensor("desired_room_temp"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DanfossEclConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Danfoss ECL Modbus sensor platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        EclSensor(coordinator, description) for description in SENSOR_TYPES
    )


class EclSensor(DanfossEclEntity, SensorEntity):
    """Representation of a Danfoss ECL sensor."""

    entity_description: EclSensorEntityDescription

    def __init__(
        self,
        coordinator: DanfossEclCoordinator,
        description: EclSensorEntityDescription,
    ) -> None:
        """Initialize the Danfoss ECL sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self._entry_id}-{description.key}"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        raw = self.coordinator.data.get(self.entity_description.key)
        return None if raw is None else self.entity_description.value_fn(raw)
