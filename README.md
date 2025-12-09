# Danfoss ECL Modbus Integration for Home Assistant

This is a custom integration for Home Assistant to control Danfoss ECL Modbus devices.

## Installation

1.  Install via [HACS](https://hacs.xyz/).
2.  Restart Home Assistant.
3.  Add the "Danfoss ECL Modbus" integration in Home Assistant.

## Configuration

The integration is configured via the Home Assistant UI. You will need to provide the following information:

*   **Host:** The IP address of your Danfoss ECL Modbus device.
*   **Port:** The port number of your Danfoss ECL Modbus device (default is 502).
*   **Slave:** The slave ID of your Danfoss ECL Modbus device (default is 5).

## Supported Entities

This integration supports the following entities:

*   **Climate:** `ECL Värme`
*   **Sensor:** `ECL Actual Mode`, `ECL Outside Temp`, `ECL Addition Temp`
*   **Switch:** `ECL Pump Switch`
*   **Binary Sensor:** `ECL Pump`
