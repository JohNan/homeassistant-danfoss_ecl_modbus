"""Climate platform for Danfoss ECL Modbus."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.exceptions import HomeAssistantError
from modbus_connection import ModbusError

from .const import (
    MODE_AUTO,
    MODE_COMFORT,
    MODE_SETBACK,
    MODE_STANDBY,
    MODE_TO_PRESET,
    PRESET_AUTO,
    PRESET_COMFORT,
    PRESET_SETBACK,
    PRESET_STANDBY,
    PRESET_TO_MODE,
    REG_HVAC_MODE,
    REG_TARGET_TEMP,
)
from .entity import DanfossEclEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from . import DanfossEclConfigEntry
    from .coordinator import DanfossEclCoordinator
    from .hub import EclHub

_HVAC_MODE_TO_VALUE: Final[dict[HVACMode, int]] = {
    HVACMode.AUTO: MODE_AUTO,
    HVACMode.HEAT: MODE_COMFORT,
    HVACMode.OFF: MODE_STANDBY,
}

_VALUE_TO_HVAC_MODE: Final[dict[int, HVACMode]] = {
    MODE_AUTO: HVACMode.AUTO,
    MODE_COMFORT: HVACMode.HEAT,
    MODE_SETBACK: HVACMode.HEAT,
    MODE_STANDBY: HVACMode.OFF,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DanfossEclConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Danfoss ECL Modbus climate platform."""
    runtime_data = entry.runtime_data
    async_add_entities([EclVermeClimate(runtime_data.coordinator, runtime_data.hub)])


class EclVermeClimate(DanfossEclEntity, ClimateEntity):
    """Representation of a Danfoss ECL Modbus climate entity."""

    _attr_translation_key = "heating"
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.AUTO, HVACMode.HEAT, HVACMode.OFF]  # noqa: RUF012
    _attr_preset_modes = [  # noqa: RUF012
        PRESET_AUTO,
        PRESET_COMFORT,
        PRESET_SETBACK,
        PRESET_STANDBY,
    ]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_min_temp = 10
    _attr_max_temp = 30
    _attr_target_temperature_step = 1

    def __init__(
        self,
        coordinator: DanfossEclCoordinator,
        hub: EclHub,
    ) -> None:
        """Initialize the Danfoss ECL climate entity."""
        super().__init__(coordinator)
        self._hub = hub
        self._attr_unique_id = f"{self._entry_id}-climate"

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return the current HVAC mode."""
        val = self.coordinator.data.get("hvac_mode")
        return None if val is None else _VALUE_TO_HVAC_MODE.get(val)

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        val = self.coordinator.data.get("hvac_mode")
        return None if val is None else MODE_TO_PRESET.get(val)

    @property
    def native_current_temperature(self) -> float | None:
        """Return the current room temperature."""
        raw = self.coordinator.data.get("room_temp")
        return None if raw is None else round(raw * 0.1, 1)

    @property
    def native_target_temperature(self) -> float | None:
        """Return the target room temperature."""
        val = self.coordinator.data.get("target_temp")
        return None if val is None else float(val)

    async def _async_write_register(self, address: int, value: int) -> None:
        """Write a holding register and request a coordinator refresh."""
        try:
            await self._hub.write_register(address, value)
        except (ModbusError, OSError, TimeoutError) as err:
            raise HomeAssistantError(
                f"Failed to write register {address}: {err}"
            ) from err
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set a new target HVAC mode."""
        mode = _HVAC_MODE_TO_VALUE.get(hvac_mode)
        if mode is None:
            raise HomeAssistantError(f"Unsupported HVAC mode: {hvac_mode}")
        await self._async_write_register(REG_HVAC_MODE, mode)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set a new preset mode."""
        mode = PRESET_TO_MODE.get(preset_mode)
        if mode is None:
            raise HomeAssistantError(f"Unsupported preset mode: {preset_mode}")
        await self._async_write_register(REG_HVAC_MODE, mode)

    async def async_turn_on(self) -> None:
        """Turn the climate entity on."""
        await self.async_set_hvac_mode(HVACMode.AUTO)

    async def async_turn_off(self) -> None:
        """Turn the climate entity off."""
        await self.async_set_hvac_mode(HVACMode.OFF)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set a new target temperature."""
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is not None:
            await self._async_write_register(REG_TARGET_TEMP, round(float(temp)))
