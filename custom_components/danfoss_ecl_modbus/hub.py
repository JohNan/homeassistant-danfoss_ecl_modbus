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
                # Read Pump (Holding)
                rr = await self._client.read_holding_registers(
                    REG_PUMP, count=1, slave=self._slave
                )
                if not rr.isError():
                    data["pump"] = rr.registers[0]
                else:
                    _LOGGER.warning("Error reading Pump: %s", rr)

                # Read HVAC Mode (Holding)
                rr = await self._client.read_holding_registers(
                    REG_HVAC_MODE, count=1, slave=self._slave
                )
                if not rr.isError():
                    data["hvac_mode"] = rr.registers[0]
                else:
                    _LOGGER.warning("Error reading HVAC Mode: %s", rr)

                # Read Actual Mode (Input)
                rr = await self._client.read_input_registers(
                    REG_ACTUAL_MODE, count=1, slave=self._slave
                )
                if not rr.isError():
                    data["actual_mode"] = rr.registers[0]
                else:
                    _LOGGER.warning("Error reading Actual Mode: %s", rr)

                # Read Target Temp (Holding)
                rr = await self._client.read_holding_registers(
                    REG_TARGET_TEMP, count=1, slave=self._slave
                )
                if not rr.isError():
                    data["target_temp"] = rr.registers[0]
                else:
                    _LOGGER.warning("Error reading Target Temp: %s", rr)

                # Read Outside Temp (Input)
                rr = await self._client.read_input_registers(
                    REG_OUTSIDE_TEMP, count=1, slave=self._slave
                )
                if not rr.isError():
                    data["outside_temp"] = rr.registers[0]
                else:
                    _LOGGER.warning("Error reading Outside Temp: %s", rr)

                # Read Addition Temp (Input)
                rr = await self._client.read_input_registers(
                    REG_ADDITION_TEMP, count=1, slave=self._slave
                )
                if not rr.isError():
                    data["addition_temp"] = rr.registers[0]
                else:
                    _LOGGER.warning("Error reading Addition Temp: %s", rr)

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
                await self._client.write_register(
                    address, value, slave=self._slave
                )
            except Exception as e:
                _LOGGER.error("Error writing register %s: %s", address, e)
                raise e