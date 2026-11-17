"""Tests for the Danfoss ECL Modbus hub."""

import pytest
from modbus_connection.encode import encode_int
from modbus_connection.exceptions import (
    IllegalDataAddressError,
    ModbusConnectionError,
    ModbusError,
    ModbusExceptionError,
)
from modbus_connection.mock import MockModbusUnit

from custom_components.danfoss_ecl_modbus.const import (
    REG_DESIRED_ROOM_TEMP,
    REG_PARALLEL_DISPLACEMENT,
    REG_PUMP,
    REG_ROOM_TEMP,
    REG_TARGET_TEMP,
    SENSOR_DISCONNECTED_RAW,
)
from custom_components.danfoss_ecl_modbus.hub import EclHub
from tests.conftest import DEFAULT_HOLDING, DEFAULT_INPUT


def _event_touches_address(event: object, address: int) -> bool:
    """Return whether a mock read event covers the given register address."""
    ev_addr = getattr(event, "address", getattr(event, "start", None))
    if isinstance(ev_addr, int):
        count = getattr(event, "count", 1)
        if isinstance(count, int):
            return ev_addr <= address < ev_addr + count
        return ev_addr == address
    if isinstance(event, tuple):
        return address in event
    return False


async def test_hub_update_decodes_signed_and_unsigned(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """Test hub update decodes signed and unsigned registers."""
    hub = EclHub(mock_modbus_unit)
    data = await hub.update()

    assert data["pump"] == 1
    assert data["valve_opening"] == 0
    assert data["valve_closing"] == 0
    assert data["hvac_mode"] == 1
    assert data["actual_mode"] == 1
    assert data["return_temp_limit"] == 50
    assert data["heating_curve_slope"] == 18
    assert data["parallel_displacement"] == -4
    assert data["flow_temp_min"] == 20
    assert data["flow_temp_max"] == 70
    assert data["cutout_temp"] == 18
    assert data["target_temp"] == 21
    assert data["setback_temp"] == 17
    assert data["accumulated_outside_temp"] == -25
    assert data["outside_temp"] == -50
    assert data["room_temp"] == 215
    assert data["addition_temp"] == 455
    assert data["return_temp"] == 320
    assert data["desired_room_temp"] == 210
    assert data["desired_flow_temp"] == 460


async def test_hub_disconnected_sensor_sentinel(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """Test hub decodes disconnected sensor sentinel as None."""
    mock_modbus_unit.input[REG_ROOM_TEMP] = SENSOR_DISCONNECTED_RAW

    hub = EclHub(mock_modbus_unit)
    data = await hub.update()

    assert data["room_temp"] is None
    assert data["outside_temp"] == -50
    assert data["addition_temp"] == 455
    assert data["return_temp"] == 320


async def test_hub_caches_illegal_data_address(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """Test hub skips registers that return IllegalDataAddressError on later polls."""
    mock_modbus_unit.fail_read(
        REG_DESIRED_ROOM_TEMP,
        IllegalDataAddressError(2),
        register_type="input",
    )

    hub = EclHub(mock_modbus_unit)
    data1 = await hub.update()
    first_poll_count = len(mock_modbus_unit.read_events)
    data2 = await hub.update()

    assert "desired_room_temp" not in data1
    assert data1["desired_flow_temp"] == 460
    assert data1["outside_temp"] == -50

    assert "desired_room_temp" not in data2
    assert data2["desired_flow_temp"] == 460
    assert data2["outside_temp"] == -50

    first_events = mock_modbus_unit.read_events[:first_poll_count]
    second_events = mock_modbus_unit.read_events[first_poll_count:]
    assert (
        sum(
            1
            for event in first_events
            if _event_touches_address(event, REG_DESIRED_ROOM_TEMP)
        )
        == 1
    )
    assert (
        sum(
            1
            for event in second_events
            if _event_touches_address(event, REG_DESIRED_ROOM_TEMP)
        )
        == 0
    )


async def test_hub_all_registers_exception_raises(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """Test hub raises ModbusExceptionError when every register fails."""
    for address in DEFAULT_HOLDING:
        mock_modbus_unit.fail_read(
            address,
            ModbusExceptionError(4),
            register_type="holding",
        )
    for address in DEFAULT_INPUT:
        mock_modbus_unit.fail_read(
            address,
            ModbusExceptionError(4),
            register_type="input",
        )

    hub = EclHub(mock_modbus_unit)
    with pytest.raises(ModbusExceptionError):
        await hub.update()


async def test_hub_all_registers_cached_unsupported_raises(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """Test hub raises ModbusError when all registers are cached unsupported."""
    for address in DEFAULT_HOLDING:
        mock_modbus_unit.fail_read(
            address,
            IllegalDataAddressError(2),
            register_type="holding",
        )
    for address in DEFAULT_INPUT:
        mock_modbus_unit.fail_read(
            address,
            IllegalDataAddressError(2),
            register_type="input",
        )

    hub = EclHub(mock_modbus_unit)
    with pytest.raises(IllegalDataAddressError):
        await hub.update()
    with pytest.raises(ModbusError):
        await hub.update()


async def test_hub_transport_error_propagates(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """Test hub propagates transport errors immediately."""
    mock_modbus_unit.fail_read(
        REG_PUMP,
        ModbusConnectionError("reset"),
        register_type="holding",
    )

    hub = EclHub(mock_modbus_unit)
    with pytest.raises(ModbusConnectionError):
        await hub.update()


async def test_hub_write_register_signed_and_unsigned(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    """Test hub encodes both unsigned and negative signed register writes."""
    hub = EclHub(mock_modbus_unit)

    await hub.write_register(REG_TARGET_TEMP, 24)
    assert mock_modbus_unit.holding[REG_TARGET_TEMP] == 24

    await hub.write_register(REG_PARALLEL_DISPLACEMENT, -6)
    assert (
        mock_modbus_unit.holding[REG_PARALLEL_DISPLACEMENT]
        == encode_int(-6, count=1)[0]
    )
