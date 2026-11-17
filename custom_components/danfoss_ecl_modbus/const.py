"""Constants for the Danfoss ECL Modbus integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "danfoss_ecl_modbus"

# Configuration defaults
DEFAULT_PORT: Final = 502
DEFAULT_SLAVE: Final = 5

# Sentinel value indicating a disconnected temperature sensor (192.0 C)
SENSOR_DISCONNECTED_RAW: Final = 1920

# Holding & input registers
REG_PUMP: Final = 4001
REG_VALVE_OPENING: Final = 4100
REG_VALVE_CLOSING: Final = 4101
REG_HVAC_MODE: Final = 4200
REG_ACTUAL_MODE: Final = 4210

REG_RETURN_TEMP_LIMIT: Final = 11029
REG_ACCUMULATED_OUTSIDE_TEMP: Final = 11099
REG_SLOPE: Final = 11174
REG_PARALLEL_DISPLACEMENT: Final = 11175
REG_FLOW_TEMP_MIN: Final = 11176
REG_FLOW_TEMP_MAX: Final = 11177
REG_CUTOUT_TEMP: Final = 11178
REG_TARGET_TEMP: Final = 11179
REG_SETBACK_TEMP: Final = 11180

REG_OUTSIDE_TEMP: Final = 11200
REG_ROOM_TEMP: Final = 11201
REG_ADDITION_TEMP: Final = 11202
REG_RETURN_TEMP: Final = 11203
REG_DESIRED_ROOM_TEMP: Final = 11228
REG_DESIRED_FLOW_TEMP: Final = 11229

# Controller operating modes
MODE_MANUAL: Final = 0
MODE_AUTO: Final = 1
MODE_COMFORT: Final = 2
MODE_SETBACK: Final = 3
MODE_STANDBY: Final = 4

# Climate preset modes
PRESET_AUTO: Final = "auto"
PRESET_COMFORT: Final = "comfort"
PRESET_SETBACK: Final = "setback"
PRESET_STANDBY: Final = "standby"

ACTUAL_MODE_MAP: Final[dict[int, str]] = {
    MODE_MANUAL: "manual",
    MODE_AUTO: PRESET_AUTO,
    MODE_COMFORT: PRESET_COMFORT,
    MODE_SETBACK: PRESET_SETBACK,
    MODE_STANDBY: PRESET_STANDBY,
}

PRESET_TO_MODE: Final[dict[str, int]] = {
    PRESET_AUTO: MODE_AUTO,
    PRESET_COMFORT: MODE_COMFORT,
    PRESET_SETBACK: MODE_SETBACK,
    PRESET_STANDBY: MODE_STANDBY,
}

MODE_TO_PRESET: Final[dict[int, str]] = {v: k for k, v in PRESET_TO_MODE.items()}
