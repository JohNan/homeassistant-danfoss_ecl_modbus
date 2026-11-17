"""Number platform for Danfoss ECL Modbus."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.exceptions import HomeAssistantError
from modbus_connection import ModbusError

from .const import (
    REG_CUTOUT_TEMP,
    REG_FLOW_TEMP_MAX,
    REG_FLOW_TEMP_MIN,
    REG_PARALLEL_DISPLACEMENT,
    REG_RETURN_TEMP_LIMIT,
    REG_SETBACK_TEMP,
    REG_SLOPE,
)
from .entity import DanfossEclEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from . import DanfossEclConfigEntry
    from .coordinator import DanfossEclCoordinator
    from .hub import EclHub


@dataclass(frozen=True, kw_only=True)
class EclNumberEntityDescription(NumberEntityDescription):
    """Describe a Danfoss ECL configurable number entity."""

    register: int
    scale: float = 1.0


def _temp_number(
    key: str,
    register: int,
    native_min_value: float,
    native_max_value: float,
) -> EclNumberEntityDescription:
    """Build an entity description for a Celsius temperature number entity."""
    return EclNumberEntityDescription(
        key=key,
        translation_key=key,
        register=register,
        native_min_value=native_min_value,
        native_max_value=native_max_value,
        native_step=1,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.CONFIG,
        mode=NumberMode.BOX,
    )


NUMBER_TYPES: Final[tuple[EclNumberEntityDescription, ...]] = (
    EclNumberEntityDescription(
        key="heating_curve_slope",
        translation_key="heating_curve_slope",
        register=REG_SLOPE,
        scale=0.1,
        native_min_value=0.1,
        native_max_value=4.0,
        native_step=0.1,
        entity_category=EntityCategory.CONFIG,
        mode=NumberMode.BOX,
    ),
    EclNumberEntityDescription(
        key="parallel_displacement",
        translation_key="parallel_displacement",
        register=REG_PARALLEL_DISPLACEMENT,
        native_min_value=-20,
        native_max_value=20,
        native_step=1,
        device_class=NumberDeviceClass.TEMPERATURE_DELTA,
        native_unit_of_measurement=UnitOfTemperature.KELVIN,
        entity_category=EntityCategory.CONFIG,
        mode=NumberMode.BOX,
    ),
    _temp_number("setback_temp", REG_SETBACK_TEMP, 5, 30),
    _temp_number("flow_temp_min", REG_FLOW_TEMP_MIN, 10, 90),
    _temp_number("flow_temp_max", REG_FLOW_TEMP_MAX, 10, 110),
    _temp_number("cutout_temp", REG_CUTOUT_TEMP, 1, 50),
    _temp_number("return_temp_limit", REG_RETURN_TEMP_LIMIT, 10, 110),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DanfossEclConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Danfoss ECL Modbus number platform."""
    runtime_data = entry.runtime_data
    async_add_entities(
        EclNumber(runtime_data.coordinator, runtime_data.hub, description)
        for description in NUMBER_TYPES
    )


class EclNumber(DanfossEclEntity, NumberEntity):
    """Representation of a Danfoss ECL configurable number entity."""

    entity_description: EclNumberEntityDescription

    def __init__(
        self,
        coordinator: DanfossEclCoordinator,
        hub: EclHub,
        description: EclNumberEntityDescription,
    ) -> None:
        """Initialize the Danfoss ECL number entity."""
        super().__init__(coordinator)
        self._hub = hub
        self.entity_description = description
        self._attr_unique_id = f"{self._entry_id}-{description.key}"

    @property
    def native_value(self) -> float | None:
        """Return the current numeric value."""
        raw = self.coordinator.data.get(self.entity_description.key)
        if raw is None:
            return None
        scale = self.entity_description.scale
        return round(raw * scale, 1) if scale != 1.0 else float(raw)

    async def async_set_native_value(self, value: float) -> None:
        """Write a new numeric value to the controller."""
        raw = round(value / self.entity_description.scale)
        try:
            await self._hub.write_register(self.entity_description.register, raw)
        except (ModbusError, OSError, TimeoutError) as err:
            raise HomeAssistantError(
                f"Failed to set {self.entity_description.key}: {err}"
            ) from err
        await self.coordinator.async_request_refresh()
