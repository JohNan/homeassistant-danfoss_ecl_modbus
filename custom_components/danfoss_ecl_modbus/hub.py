"""Hub for Danfoss ECL Modbus communication."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from modbus_connection import (
    IllegalDataAddressError,
    ModbusError,
    ModbusExceptionError,
)
from modbus_connection.decode import decode_int16, decode_uint16
from modbus_connection.encode import encode_int

from .const import (
    REG_ACCUMULATED_OUTSIDE_TEMP,
    REG_ACTUAL_MODE,
    REG_ADDITION_TEMP,
    REG_CUTOUT_TEMP,
    REG_DESIRED_FLOW_TEMP,
    REG_DESIRED_ROOM_TEMP,
    REG_FLOW_TEMP_MAX,
    REG_FLOW_TEMP_MIN,
    REG_HVAC_MODE,
    REG_OUTSIDE_TEMP,
    REG_PARALLEL_DISPLACEMENT,
    REG_PUMP,
    REG_RETURN_TEMP,
    REG_RETURN_TEMP_LIMIT,
    REG_ROOM_TEMP,
    REG_SETBACK_TEMP,
    REG_SLOPE,
    REG_TARGET_TEMP,
    REG_VALVE_CLOSING,
    REG_VALVE_OPENING,
    SENSOR_DISCONNECTED_RAW,
)

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RegisterDef:
    """Definition of a Danfoss ECL Modbus register."""

    key: str
    address: int
    is_input: bool
    signed: bool = False
    disconnected_sentinel: int | None = None


REGISTERS: Final[tuple[RegisterDef, ...]] = (
    # Holding registers
    RegisterDef(key="pump", address=REG_PUMP, is_input=False),
    RegisterDef(key="valve_opening", address=REG_VALVE_OPENING, is_input=False),
    RegisterDef(key="valve_closing", address=REG_VALVE_CLOSING, is_input=False),
    RegisterDef(key="hvac_mode", address=REG_HVAC_MODE, is_input=False),
    RegisterDef(
        key="return_temp_limit",
        address=REG_RETURN_TEMP_LIMIT,
        is_input=False,
        signed=True,
    ),
    RegisterDef(key="heating_curve_slope", address=REG_SLOPE, is_input=False),
    RegisterDef(
        key="parallel_displacement",
        address=REG_PARALLEL_DISPLACEMENT,
        is_input=False,
        signed=True,
    ),
    RegisterDef(key="flow_temp_min", address=REG_FLOW_TEMP_MIN, is_input=False),
    RegisterDef(key="flow_temp_max", address=REG_FLOW_TEMP_MAX, is_input=False),
    RegisterDef(key="cutout_temp", address=REG_CUTOUT_TEMP, is_input=False),
    RegisterDef(
        key="target_temp",
        address=REG_TARGET_TEMP,
        is_input=False,
        signed=True,
    ),
    RegisterDef(
        key="setback_temp",
        address=REG_SETBACK_TEMP,
        is_input=False,
        signed=True,
    ),
    # Input registers
    RegisterDef(key="actual_mode", address=REG_ACTUAL_MODE, is_input=True),
    RegisterDef(
        key="accumulated_outside_temp",
        address=REG_ACCUMULATED_OUTSIDE_TEMP,
        is_input=True,
        signed=True,
    ),
    RegisterDef(
        key="outside_temp",
        address=REG_OUTSIDE_TEMP,
        is_input=True,
        signed=True,
        disconnected_sentinel=SENSOR_DISCONNECTED_RAW,
    ),
    RegisterDef(
        key="room_temp",
        address=REG_ROOM_TEMP,
        is_input=True,
        signed=True,
        disconnected_sentinel=SENSOR_DISCONNECTED_RAW,
    ),
    RegisterDef(
        key="addition_temp",
        address=REG_ADDITION_TEMP,
        is_input=True,
        signed=True,
        disconnected_sentinel=SENSOR_DISCONNECTED_RAW,
    ),
    RegisterDef(
        key="return_temp",
        address=REG_RETURN_TEMP,
        is_input=True,
        signed=True,
        disconnected_sentinel=SENSOR_DISCONNECTED_RAW,
    ),
    RegisterDef(
        key="desired_room_temp",
        address=REG_DESIRED_ROOM_TEMP,
        is_input=True,
        signed=True,
    ),
    RegisterDef(
        key="desired_flow_temp",
        address=REG_DESIRED_FLOW_TEMP,
        is_input=True,
        signed=True,
    ),
)


class EclHub:
    """Hub to manage Modbus reads and writes for a Danfoss ECL unit."""

    def __init__(self, unit: ModbusUnit) -> None:
        """Initialize the Danfoss ECL hub."""
        self._unit = unit
        self._unsupported_addresses: set[int] = set()

    async def async_probe(self) -> None:
        """Probe the device by reading the actual mode input register."""
        await self._unit.read_input_registers(REG_ACTUAL_MODE, 1)

    async def _async_read_register(
        self, reg: RegisterDef
    ) -> tuple[int | None, ModbusError | None]:
        """Read and decode a single register, handling Modbus exceptions."""
        try:
            words = await (
                self._unit.read_input_registers(reg.address, 1)
                if reg.is_input
                else self._unit.read_holding_registers(reg.address, 1)
            )
        except IllegalDataAddressError as err:
            _LOGGER.warning(
                "Register %s (%s) is unsupported by this device: %s",
                reg.address,
                reg.key,
                err,
            )
            self._unsupported_addresses.add(reg.address)
            return None, err
        except ModbusExceptionError as err:
            _LOGGER.warning(
                "Modbus exception reading register %s (%s): %s",
                reg.address,
                reg.key,
                err,
            )
            return None, err

        val = decode_int16(words) if reg.signed else decode_uint16(words)
        if reg.disconnected_sentinel is not None and val == reg.disconnected_sentinel:
            return None, None
        return val, None

    async def update(self) -> dict[str, int | None]:
        """Read all supported registers from the Danfoss ECL device."""
        data: dict[str, int | None] = {}
        last_exc: ModbusError | None = None

        for reg in REGISTERS:
            if reg.address in self._unsupported_addresses:
                continue
            val, err = await self._async_read_register(reg)
            if err is not None:
                last_exc = err
                continue
            data[reg.key] = val

        if not data:
            if last_exc is not None:
                raise last_exc
            raise ModbusError("No registers could be read from Danfoss ECL device")

        return data

    async def write_register(self, address: int, value: int) -> None:
        """Write a signed 16-bit integer value to a holding register."""
        word = encode_int(value, count=1)[0]
        await self._unit.write_register(address, word)
