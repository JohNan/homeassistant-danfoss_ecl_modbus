"""Hub for Danfoss ECL Modbus."""

import asyncio
import logging

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import (
    REG_ACTUAL_MODE,
    REG_ADDITION_TEMP,
    REG_HVAC_MODE,
    REG_OUTSIDE_TEMP,
    REG_PUMP,
    REG_TARGET_TEMP,
)

_LOGGER = logging.getLogger(__name__)


class EclHub:
    """Hub to manage Modbus connection and data retrieval."""

    def __init__(self, host, port, slave):
        """Initialize the Hub."""
        self._client = AsyncModbusTcpClient(host, port=port)
        self._slave = slave
        self._lock = asyncio.Lock()

    async def connect(self):
        """Connect to the Modbus device."""
        if not self._client.connected:
            await self._client.connect()
        return self._client.connected

    async def close(self):
        """Close the connection."""
        self._client.close()

    async def update(self):
        """Read all data from the device."""
        data = {}
        async with self._lock:
            if not await self.connect():
                raise ConnectionError("Failed to connect to Modbus device")

            try:
                # key, register, is_input
                registers = [
                    ("pump", REG_PUMP, False),
                    ("hvac_mode", REG_HVAC_MODE, False),
                    ("actual_mode", REG_ACTUAL_MODE, True),
                    ("target_temp", REG_TARGET_TEMP, False),
                    ("outside_temp", REG_OUTSIDE_TEMP, True),
                    ("addition_temp", REG_ADDITION_TEMP, True),
                ]

                for key, reg, is_input in registers:
                    if is_input:
                        rr = await self._client.read_input_registers(
                            reg, count=1, slave=self._slave
                        )
                    else:
                        rr = await self._client.read_holding_registers(
                            reg, count=1, slave=self._slave
                        )

                    if not rr.isError():
                        data[key] = rr.registers[0]
                    else:
                        _LOGGER.warning("Error reading %s: %s", key, rr)

            except ModbusException as e:
                _LOGGER.error("Modbus error: %s", e)
                raise e
            except Exception as e:
                _LOGGER.error("Error reading Modbus data: %s", e)
                raise e

        return data

    async def write_register(self, address, value):
        """Write a register."""
        async with self._lock:
            if not await self.connect():
                raise ConnectionError("Failed to connect to Modbus device")
            try:
                await self._client.write_register(address, value, slave=self._slave)
            except Exception as e:
                _LOGGER.error("Error writing register %s: %s", address, e)
                raise e
