# Agent Directions for Danfoss ECL Modbus Home Assistant Integration

This document provides guidance for AI agents working on the `danfoss_ecl_modbus` custom integration for Home Assistant. The project aims to provide control and monitoring of Danfoss ECL Modbus devices within a Home Assistant environment.

## Architecture

The integration follows a modern Home Assistant architectural pattern:

-   **Hub (`hub.py`):** Encapsulates the Modbus connection logic using `pymodbus`. It handles connection management (with locking) and provides methods to read batched data (`update()`) and write registers (`write_register()`).
-   **DataUpdateCoordinator (`__init__.py`):** Manages polling the device via the Hub. It fetches all data centrally every 30 seconds and distributes it to entities. This prevents "hammering" the device with multiple concurrent requests.
-   **CoordinatorEntity:** All entities (`sensor`, `climate`, `binary_sensor`, `switch`) inherit from `CoordinatorEntity`. They do not poll the device directly; they read from `coordinator.data`.
-   **Device Info:** All entities share the same `device_info`, grouping them under a single "Danfoss ECL 110" device in Home Assistant.

## Key Files

-   `__init__.py`: Entry point. Sets up the Hub and Coordinator.
-   `config_flow.py`: Manages setup via UI. Validates connection before creating an entry.
-   `const.py`: Centralized constants for register addresses, configuration keys, and defaults.
-   `hub.py`: Modbus communication layer.
-   `sensor.py`, `climate.py`, `binary_sensor.py`, `switch.py`: Entity implementations.

## Modbus Registers

Register mappings are defined in `const.py`. Key registers (based on current implementation):

-   `4200` (Holding): HVAC Mode (1=Auto, 4=Off).
-   `4210` (Input): Actual Mode.
-   `11179` (Holding): Target Temperature.
-   `11200` (Input): Outside Temperature (Scale 0.1).
-   `11202` (Input): Addition Temperature (Scale 0.1).
-   `4001` (Holding): Pump Status/Control (1=On, 0=Off).

## Development Guidelines

### Environment Setup

This project requires Python 3.13.2 or higher. It uses `uv` for dependency management and `ruff` for linting and formatting.

1.  **Install `uv`:**
    Follow the official installation instructions for `uv`.

2.  **Install dependencies:**
    ```bash
    uv sync --all-extras --dev
    ```

### Quality Assurance

Always run linters and tests before finalizing changes.

**1. Linting and Formatting:**
`ruff` is used for linting, formatting, and import sorting.

```bash
# Check for linting errors and formatting issues
uv run ruff check .

# Fix linting errors and format the code
uv run ruff format .
uv run ruff check . --fix

# Run static analysis with mypy
uv run mypy custom_components/danfoss_ecl_modbus
```

**2. Tests:**
Verify changes with the test suite.

```bash
# Run all tests
uv run pytest
```

### Testing Notes

-   **Framework:** `pytest`.
-   **Location:** `custom_components/danfoss_ecl_modbus/tests/`.
-   **Mocks:** Use `unittest.mock.AsyncMock` for async methods. Test fixtures for `hub` and `coordinator` are defined in `tests/conftest.py`.
-   **Integration Loading:** The `auto_enable_custom_integrations` fixture in `conftest.py` ensures the custom component is correctly loaded during tests.

## Best Practices Checklist

-   [x] **Use DataUpdateCoordinator:** Implemented.
-   [x] **Centralize Constants:** Implemented in `const.py`.
-   [x] **Device Registry:** Implemented via `device_info`.
-   [x] **Entity Descriptions:** Implemented for Sensors.
-   [x] **Robust Config Flow:** Implemented with connection validation.
-   [x] **Type Hinting:** Used in core methods.

When adding new features, ensure they follow the `CoordinatorEntity` pattern and define new registers in `const.py`.