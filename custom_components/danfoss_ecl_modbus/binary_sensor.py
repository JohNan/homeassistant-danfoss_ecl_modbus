"""Binary sensor platform for Danfoss ECL Modbus."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory

from .entity import DanfossEclEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from . import DanfossEclConfigEntry
    from .coordinator import DanfossEclCoordinator


@dataclass(frozen=True, kw_only=True)
class EclBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describe a Danfoss ECL binary sensor entity."""

    unique_id_suffix: str


BINARY_SENSOR_TYPES: Final[tuple[EclBinarySensorEntityDescription, ...]] = (
    EclBinarySensorEntityDescription(
        key="pump",
        translation_key="pump",
        unique_id_suffix="pump-binary",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    EclBinarySensorEntityDescription(
        key="valve_opening",
        translation_key="valve_opening",
        unique_id_suffix="valve-opening",
        device_class=BinarySensorDeviceClass.OPENING,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    EclBinarySensorEntityDescription(
        key="valve_closing",
        translation_key="valve_closing",
        unique_id_suffix="valve-closing",
        device_class=BinarySensorDeviceClass.MOVING,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DanfossEclConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Danfoss ECL Modbus binary sensor platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        EclBinarySensor(coordinator, description) for description in BINARY_SENSOR_TYPES
    )


class EclBinarySensor(DanfossEclEntity, BinarySensorEntity):
    """Representation of a Danfoss ECL binary sensor."""

    entity_description: EclBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: DanfossEclCoordinator,
        description: EclBinarySensorEntityDescription,
    ) -> None:
        """Initialize the Danfoss ECL binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self._entry_id}-{description.unique_id_suffix}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        val = self.coordinator.data.get(self.entity_description.key)
        return None if val is None else val == 1
