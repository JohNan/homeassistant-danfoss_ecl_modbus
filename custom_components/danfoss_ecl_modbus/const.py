"""Constants for the Danfoss ECL Modbus integration."""

DOMAIN = "danfoss_ecl_modbus"

# Registers
REG_PUMP = 4001
REG_HVAC_MODE = 4200
REG_ACTUAL_MODE = 4210
REG_TARGET_TEMP = 11179
REG_OUTSIDE_TEMP = 11200
REG_ADDITION_TEMP = 11202

# Configuration
CONF_SLAVE = "slave"
DEFAULT_SLAVE = 5
DEFAULT_PORT = 502
