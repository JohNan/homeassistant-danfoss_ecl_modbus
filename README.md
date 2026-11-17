# Danfoss ECL Modbus Integration for Home Assistant

This is a custom integration for Home Assistant (`>= 2026.11.0`) to monitor and control Danfoss ECL 110 controllers over Modbus TCP.

## Installation

1. Ensure you are running **Home Assistant 2026.11.0** or newer.
2. Install via [HACS](https://hacs.xyz/) (add this repository as a custom integration repository if needed, then install **Danfoss ECL Modbus**).
3. Restart Home Assistant.
4. Add the **Danfoss ECL Modbus** integration under **Settings → Devices & Services → Add Integration**.

## Configuration

The integration is configured via the Home Assistant UI. Provide the following parameters:

* **Host:** IP address or hostname of your Danfoss ECL Modbus TCP gateway.
* **Port:** Modbus TCP port number (default: `502`).
* **Slave / Unit ID:** Modbus slave / unit ID of your Danfoss ECL controller (default: `5`).

During setup, Home Assistant probes the controller (input register `4210`, Actual Mode) to verify connectivity before creating the config entry.

## Supported Entities

All entities are grouped under a single **Danfoss ECL 110** device and polled every 30 seconds via a central coordinator. Disconnected temperature sensors reporting the Danfoss sentinel value (`192.0 °C`) become unavailable/unknown (`None`), and optional registers unsupported by a specific controller model are automatically skipped after reporting an illegal data address.

### Climate

* **Heating** (`unique_id`: `<entry_id>-climate`)
  * **HVAC Modes:** `auto` (Auto), `heat` (Comfort / Setback), `off` (Standby)
  * **Preset Modes:** `auto`, `comfort`, `setback`, `standby`
  * **Target Temperature:** `10 °C` to `30 °C` (step `1 °C`, register `11179`)
  * **Current Temperature:** Room temperature (register `11201`)
  * **Controls:** Supports target temperature, preset mode selection, `turn_on` (sets `auto`), and `turn_off` (sets `off` / standby)

### Sensors

8 telemetry sensors:

| Entity | Description | Register | Unit / Values | Unique ID Suffix |
| --- | --- | --- | --- | --- |
| **Actual mode** | Controller operating state | `4210` (Input) | `manual`, `auto`, `comfort`, `setback`, `standby` | `actual_mode` |
| **Outside temperature** | Measured outside temperature | `11200` (Input) | `°C` | `outside_temp` |
| **Accumulated outside temperature** | Filtered/accumulated outside temperature | `11099` (Input) | `°C` | `accumulated_outside_temp` |
| **Flow temperature** | Heating flow temperature | `11202` (Input) | `°C` | `addition_temp` *(preserved for compatibility)* |
| **Desired flow temperature** | Calculated target flow temperature | `11229` (Input) | `°C` | `desired_flow_temp` |
| **Return temperature** | Heating return temperature | `11203` (Input) | `°C` | `return_temp` |
| **Room temperature** | Measured room temperature | `11201` (Input) | `°C` | `room_temp` |
| **Desired room temperature** | Effective target room temperature | `11228` (Input) | `°C` | `desired_room_temp` |

### Binary Sensors

3 status sensors:

| Entity | Description | Register | Device Class | Category | Unique ID Suffix |
| --- | --- | --- | --- | --- | --- |
| **Pump** | Circulation pump running state | `4001` (Holding) | `running` | Primary | `pump-binary` |
| **Valve opening** | Actuator valve opening state | `4100` (Holding) | `opening` | Diagnostic | `valve-opening` |
| **Valve closing** | Actuator valve closing state | `4101` (Holding) | `moving` | Diagnostic | `valve-closing` |

### Numbers

7 heating curve and temperature limit controls (Configuration category):

| Entity | Register | Range | Step | Unit | Unique ID Suffix |
| --- | --- | --- | --- | --- | --- |
| **Heating curve slope** | `11174` (Holding) | `0.1` – `4.0` | `0.1` | — | `heating_curve_slope` |
| **Parallel displacement** | `11175` (Holding) | `-20` – `20` | `1` | `K` | `parallel_displacement` |
| **Setback temperature** | `11180` (Holding) | `5` – `30` | `1` | `°C` | `setback_temp` |
| **Minimum flow temperature** | `11176` (Holding) | `10` – `90` | `1` | `°C` | `flow_temp_min` |
| **Maximum flow temperature** | `11177` (Holding) | `10` – `110` | `1` | `°C` | `flow_temp_max` |
| **Summer cut-out temperature** | `11178` (Holding) | `1` – `50` | `1` | `°C` | `cutout_temp` |
| **Return temperature limit** | `11029` (Holding) | `10` – `110` | `1` | `°C` | `return_temp_limit` |

### Switch

* **Pump switch** (`unique_id`: `<entry_id>-pump-switch`, register `4001` Holding) — Manually turns the circulation pump on (`1`) or off (`0`).
