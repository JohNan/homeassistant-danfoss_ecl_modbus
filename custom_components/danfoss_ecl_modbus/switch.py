"""Switch platform for Danfoss ECL Modbus."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.exceptions import HomeAssistantError
from modbus_connection import ModbusError

from .const import REG_PUMP
from .entity import DanfossEclEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from . import DanfossEclConfigEntry
    from .coordinator import DanfossEclCoordinator
    from .hub import EclHub


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DanfossEclConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Danfoss ECL Modbus switch platform."""
    runtime_data = entry.runtime_data
    async_add_entities([EclPumpSwitch(runtime_data.coordinator, runtime_data.hub)])


class EclPumpSwitch(DanfossEclEntity, SwitchEntity):
    """Representation of a Danfoss ECL Modbus pump switch."""

    _attr_translation_key = "pump_switch"

    def __init__(
        self,
        coordinator: DanfossEclCoordinator,
        hub: EclHub,
    ) -> None:
        """Initialize the Danfoss ECL pump switch."""
        super().__init__(coordinator)
        self._hub = hub
        self._attr_unique_id = f"{self._entry_id}-pump-switch"

    @property
    def is_on(self) -> bool | None:
        """Return true if the pump switch is on."""
        val = self.coordinator.data.get("pump")
        return None if val is None else val == 1

    async def _async_set_pump(self, value: int) -> None:
        """Write the pump register and request a coordinator refresh."""
        try:
            await self._hub.write_register(REG_PUMP, value)
        except (ModbusError, OSError, TimeoutError) as err:
            raise HomeAssistantError(f"Failed to write pump register: {err}") from err
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the pump switch on."""
        await self._async_set_pump(1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the pump switch off."""
        await self._async_set_pump(0)
