# Agent Directions for Danfoss ECL Modbus Home Assistant Integration

This document provides guidance for AI agents working on the `danfoss_ecl_modbus` custom integration for Home Assistant (`>= 2026.11.0`, Python `>= 3.14.2`). The project provides monitoring and control of Danfoss ECL 110 Modbus TCP controllers via Home Assistant's built-in `modbus` component.

## Architecture

The integration follows Home Assistant's modern typed coordinator architecture:

-   **Modbus Connection Sharing (`__init__.py`, `config_flow.py`):** Delegates TCP connection pooling and locking to Home Assistant's `modbus` integration (`homeassistant.components.modbus`) backed by `modbus-connection`:
    -   `async_setup_entry` acquires a persistent `ModbusUnit` via `async_get_unit(hass, entry, ModbusTcpParams(host=host, port=port), slave)`, converting `HomeAssistantError` into `ConfigEntryNotReady`.
    -   `DanfossEclModbusConfigFlow.async_step_user` validates connectivity with `async_get_temporary_unit(self.hass, ModbusTcpParams(host=host, port=port), slave)` and `await EclHub(unit).async_probe()`.
-   **Hub (`hub.py`):** `EclHub` wraps a `ModbusUnit` and declares all supported registers in `REGISTERS: tuple[RegisterDef, ...]`.
    -   `async_probe()` reads `REG_ACTUAL_MODE` (`4210`) during config flow validation.
    -   `update()` iterates `REGISTERS`, reads each register individually (`read_input_registers` or `read_holding_registers`), decodes `int16`/`uint16` via `modbus_connection.decode`, maps `SENSOR_DISCONNECTED_RAW` (`1920`, i.e., `192.0 °C`) to `None`, and caches addresses raising `IllegalDataAddressError` in `_unsupported_addresses` to skip them on subsequent polls. Raises `ModbusError` if no registers succeed.
    -   `write_register(address, value)` encodes signed 16-bit integers with `encode_int(value, count=1)[0]` and writes via `self._unit.write_register(...)`.
-   **Typed Config Entry & Runtime Data (`__init__.py`):** `DanfossEclRuntimeData(hub, coordinator)` is stored on `entry.runtime_data`, typed as `type DanfossEclConfigEntry = ConfigEntry[DanfossEclRuntimeData]`.
-   **Coordinator (`coordinator.py`):** `DanfossEclCoordinator(DataUpdateCoordinator[dict[str, int | None]])` polls `self.hub.update()` every `UPDATE_INTERVAL = timedelta(seconds=30)` and wraps `(ModbusError, OSError, TimeoutError)` in `UpdateFailed`.
-   **Base Entity (`entity.py`):** `DanfossEclEntity(CoordinatorEntity[DanfossEclCoordinator])` sets `_attr_has_entity_name = True` and shared `DeviceInfo(identifiers={(DOMAIN, entry_id)}, name="Danfoss ECL 110", manufacturer="Danfoss", model="ECL 110")`.
-   **Platforms (`binary_sensor.py`, `climate.py`, `number.py`, `sensor.py`, `switch.py`):** All platform entities inherit from `DanfossEclEntity`. `binary_sensor`, `number`, and `sensor` use frozen `EntityDescription` subclasses. Write methods convert `(ModbusError, OSError, TimeoutError)` into `HomeAssistantError` and call `await self.coordinator.async_request_refresh()`.

## Key Files

-   `custom_components/danfoss_ecl_modbus/__init__.py`: `DanfossEclRuntimeData`, `DanfossEclConfigEntry`, `PLATFORMS`, `async_setup_entry`, `async_unload_entry`.
-   `custom_components/danfoss_ecl_modbus/config_flow.py`: UI config flow (`DanfossEclModbusConfigFlow`) using `async_get_temporary_unit` and `EclHub.async_probe()`.
-   `custom_components/danfoss_ecl_modbus/const.py`: Register addresses, configuration defaults (`DEFAULT_PORT = 502`, `DEFAULT_SLAVE = 5`), `SENSOR_DISCONNECTED_RAW = 1920`, controller mode constants, and preset mappings.
-   `custom_components/danfoss_ecl_modbus/hub.py`: `RegisterDef`, `REGISTERS`, and `EclHub`.
-   `custom_components/danfoss_ecl_modbus/coordinator.py`: `DanfossEclCoordinator` (`UPDATE_INTERVAL = 30s`).
-   `custom_components/danfoss_ecl_modbus/entity.py`: `DanfossEclEntity` base class and shared `DeviceInfo`.
-   `custom_components/danfoss_ecl_modbus/binary_sensor.py`: `EclBinarySensor` (`pump`, `valve_opening`, `valve_closing`).
-   `custom_components/danfoss_ecl_modbus/climate.py`: `EclVermeClimate` (HVAC modes, presets, target temperature, `turn_on`/`turn_off`).
-   `custom_components/danfoss_ecl_modbus/number.py`: `EclNumber` (7 heating curve and limit configuration entities).
-   `custom_components/danfoss_ecl_modbus/sensor.py`: `EclSensor` (8 telemetry sensors).
-   `custom_components/danfoss_ecl_modbus/switch.py`: `EclPumpSwitch` (manual pump control).
-   `custom_components/danfoss_ecl_modbus/strings.json` & `translations/`: Config flow and entity translations.
-   `tests/`: Root pytest suite using `pytest-homeassistant` and `MockModbusConnection`.

## Modbus Registers

All 20 polled registers are defined in `const.py` and `REGISTERS` in `hub.py`.

### Holding Registers (`is_input=False`)

| Address | Constant | Key | Type | Scale / Values | Access | Platform(s) |
| --- | --- | --- | --- | --- | --- | --- |
| `4001` | `REG_PUMP` | `pump` | `uint16` | `0`=Off, `1`=On | R/W | `binary_sensor` (`pump-binary`), `switch` (`pump-switch`) |
| `4100` | `REG_VALVE_OPENING` | `valve_opening` | `uint16` | `0`=Off, `1`=On | R | `binary_sensor` (`valve-opening`, diagnostic) |
| `4101` | `REG_VALVE_CLOSING` | `valve_closing` | `uint16` | `0`=Off, `1`=On | R | `binary_sensor` (`valve-closing`, diagnostic) |
| `4200` | `REG_HVAC_MODE` | `hvac_mode` | `uint16` | `1`=Auto, `2`=Comfort, `3`=Setback, `4`=Standby | R/W | `climate` (`hvac_mode`, `preset_mode`) |
| `11029` | `REG_RETURN_TEMP_LIMIT` | `return_temp_limit` | `int16` | `1.0` °C (`10`–`110`, step `1`) | R/W | `number` (`return_temp_limit`) |
| `11174` | `REG_SLOPE` | `heating_curve_slope` | `uint16` | `0.1` (`0.1`–`4.0`, step `0.1`) | R/W | `number` (`heating_curve_slope`) |
| `11175` | `REG_PARALLEL_DISPLACEMENT` | `parallel_displacement` | `int16` | `1.0` K (`-20`–`20`, step `1`) | R/W | `number` (`parallel_displacement`) |
| `11176` | `REG_FLOW_TEMP_MIN` | `flow_temp_min` | `uint16` | `1.0` °C (`10`–`90`, step `1`) | R/W | `number` (`flow_temp_min`) |
| `11177` | `REG_FLOW_TEMP_MAX` | `flow_temp_max` | `uint16` | `1.0` °C (`10`–`110`, step `1`) | R/W | `number` (`flow_temp_max`) |
| `11178` | `REG_CUTOUT_TEMP` | `cutout_temp` | `uint16` | `1.0` °C (`1`–`50`, step `1`) | R/W | `number` (`cutout_temp`) |
| `11179` | `REG_TARGET_TEMP` | `target_temp` | `int16` | `1.0` °C (`10`–`30`, step `1`) | R/W | `climate` (`native_target_temperature`) |
| `11180` | `REG_SETBACK_TEMP` | `setback_temp` | `int16` | `1.0` °C (`5`–`30`, step `1`) | R/W | `number` (`setback_temp`) |

### Input Registers (`is_input=True`)

| Address | Constant | Key | Type | Scale / Values | Sentinel | Platform(s) |
| --- | --- | --- | --- | --- | --- | --- |
| `4210` | `REG_ACTUAL_MODE` | `actual_mode` | `uint16` | `0`=manual, `1`=auto, `2`=comfort, `3`=setback, `4`=standby | — | `sensor` (`actual_mode`), `EclHub.async_probe` |
| `11099` | `REG_ACCUMULATED_OUTSIDE_TEMP` | `accumulated_outside_temp` | `int16` | `0.1` °C | — | `sensor` (`accumulated_outside_temp`) |
| `11200` | `REG_OUTSIDE_TEMP` | `outside_temp` | `int16` | `0.1` °C | `1920` -> `None` | `sensor` (`outside_temp`) |
| `11201` | `REG_ROOM_TEMP` | `room_temp` | `int16` | `0.1` °C | `1920` -> `None` | `sensor` (`room_temp`), `climate` (`native_current_temperature`) |
| `11202` | `REG_ADDITION_TEMP` | `addition_temp` | `int16` | `0.1` °C | `1920` -> `None` | `sensor` (`flow_temp` translation, `addition_temp` unique_id) |
| `11203` | `REG_RETURN_TEMP` | `return_temp` | `int16` | `0.1` °C | `1920` -> `None` | `sensor` (`return_temp`) |
| `11228` | `REG_DESIRED_ROOM_TEMP` | `desired_room_temp` | `int16` | `0.1` °C | — | `sensor` (`desired_room_temp`) |
| `11229` | `REG_DESIRED_FLOW_TEMP` | `desired_flow_temp` | `int16` | `0.1` °C | — | `sensor` (`desired_flow_temp`) |

### Climate Mode & Preset Mappings

-   `HVACMode.AUTO` ↔ `1` (`MODE_AUTO` / `"auto"`)
-   `HVACMode.HEAT` → `2` (`MODE_COMFORT` / `"comfort"`), and reads `2` or `3` (`MODE_SETBACK` / `"setback"`) as `HVACMode.HEAT`
-   `HVACMode.OFF` ↔ `4` (`MODE_STANDBY` / `"standby"`)
-   Presets: `"auto"` (`1`), `"comfort"` (`2`), `"setback"` (`3`), `"standby"` (`4`)

## Development Guidelines

### Quality Assurance

Toolchain management and task execution use `mise` (`mise.toml`) and `uv` (`pyproject.toml`, Python `>= 3.14.2`). Always run the full check suite before finalizing changes:

```bash
# Bootstrap virtualenv and locked dev dependencies
mise run setup

# Lint & formatting checks
mise run lint
mise run format:check

# Auto-fix lint / format code
mise run lint:fix
mise run format

# Static type checking (strict mypy)
mise run typecheck

# Run pytest suite with coverage (enforces fail_under = 90)
mise run test

# Run all gates (lint, format:check, typecheck, test)
mise run check
```

### Testing Notes

-   **Framework & Runner:** `pytest` with `pytest-homeassistant` (`2026.11.2`), configured in `pyproject.toml` (`asyncio_mode = "auto"`, `testpaths = ["tests"]`, `pythonpath = ["."]`, `addopts = "-p no:respx --cov=custom_components.danfoss_ecl_modbus --cov-report=term-missing"`, `fail_under = 90`).
-   **Location:** Root `tests/` directory.
-   **Modbus Mocking:** Use `MockModbusConnection` from `modbus-connection` to simulate unit reads, writes, and Modbus exceptions without network I/O.

## Best Practices Checklist

-   [x] **Shared `modbus` Integration Connection:** `async_get_unit` and `async_get_temporary_unit` via `modbus-connection`.
-   [x] **Typed Config Entry Runtime Data:** `DanfossEclConfigEntry` with `entry.runtime_data`.
-   [x] **Centralized Polling Coordinator:** `DanfossEclCoordinator` in `coordinator.py`.
-   [x] **Centralized Constants & Register Table:** `const.py` and `REGISTERS` in `hub.py`.
-   [x] **Shared Base Entity & Device Registry:** `DanfossEclEntity` in `entity.py`.
-   [x] **Entity Descriptions:** Implemented for `sensor`, `binary_sensor`, and `number`.
-   [x] **Strict Typing & Linting:** Enforced via `ruff` and `mypy` (`disallow_untyped_defs = true`, Python 3.14).

When adding new features, follow the `DanfossEclEntity` / `CoordinatorEntity` pattern, declare register constants in `const.py`, add `RegisterDef` entries in `hub.py`, and keep unit test coverage at or above 90%.
