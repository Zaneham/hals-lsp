# HAL/S Language Support for Visual Studio Code

Language Server Protocol (LSP) implementation for **HAL/S** (High-order Assembly Language/Shuttle), the real-time aerospace programming language that powered NASA's Space Shuttle flight software.

## About HAL/S

HAL/S was developed by Intermetrics in the early 1970s under contract to NASA. It was specifically designed for programming onboard computers in real-time aerospace applications. The language powered approximately 85% of the Space Shuttle's Primary Avionics Software System (PASS).

HAL/S was used in:

- **Space Shuttle** Primary Avionics Software System (PASS)
- **Space Shuttle** Backup Flight Software (BFS)
- **Space Station Freedom** (precursor to ISS) software development
- **Various NASA spacecraft** guidance and control systems

The language is notable for its support of:
- Native vector and matrix operations
- Real-time scheduling primitives
- Multi-line mathematical notation format

## Features

- **Syntax highlighting** for HAL/S constructs
- **Code completion** for keywords, variables, procedures, functions
- **Hover information** with type details
- **Go to definition** for symbols
- **Find references** across the document
- **Document outline** showing programme structure
- **Support for all HAL/S constructs:**
  - Program units (PROGRAM, PROCEDURE, FUNCTION, TASK, COMPOOL)
  - Data types (INTEGER, SCALAR, VECTOR, MATRIX, BOOLEAN, CHARACTER, BIT, EVENT)
  - Real-time primitives (SCHEDULE, WAIT, SIGNAL, PRIORITY, TERMINATE)
  - Array and structure declarations
  - REPLACE macro definitions

## Installation

1. Install the extension from the VS Code Marketplace
2. Ensure Python 3.8+ is installed and available in PATH
3. Open any `.hal` or `.hals` file

## File Extensions

| Extension | Description |
|-----------|-------------|
| `.hal`    | HAL/S source file |
| `.hals`   | HAL/S source file (alternate) |

## Language Overview

HAL/S uses an ALGOL-like syntax with uppercase keywords:

```hals
C HAL/S NAVIGATION EXAMPLE
C FOR SPACE SHUTTLE FLIGHT SOFTWARE

SHUTTLE_NAV: PROGRAM;
    /* Declare constants */
    DECLARE PI CONSTANT(3.14159265);
    DECLARE G CONSTANT(9.80665);

    /* Declare variables */
    DECLARE ALTITUDE SCALAR;
    DECLARE VELOCITY VECTOR(3);
    DECLARE POSITION VECTOR(3);
    DECLARE ATTITUDE MATRIX(3,3);
    DECLARE ENGINE_ON BOOLEAN;
    DECLARE ABORT_FLAG EVENT;

    /* Arrays */
    DECLARE SENSOR_DATA ARRAY(10) SCALAR;

    /* Navigation loop */
NAV_LOOP:
    DO WHILE ENGINE_ON;
        /* Update position */
        POSITION = POSITION + VELOCITY * 0.1;

        /* Check altitude */
        IF ALTITUDE < 100.0 THEN
            SIGNAL ABORT_FLAG;

        GO TO NAV_LOOP;
    END;

CLOSE SHUTTLE_NAV;

/* Guidance function */
COMPUTE_THRUST: SCALAR FUNCTION(MASS, ACCEL);
    DECLARE MASS SCALAR;
    DECLARE ACCEL VECTOR(3);
    DECLARE THRUST SCALAR;

    THRUST = MASS * ABVAL(ACCEL);
    RETURN THRUST;
CLOSE COMPUTE_THRUST;

/* Real-time task */
NAV_TASK: TASK;
    DECLARE STATE VECTOR(6);

    DO WHILE TRUE;
        WAIT FOR 0.1 SECONDS;
        /* Update navigation state */
        STATE = STATE;
    END;
CLOSE NAV_TASK;
```

### Key Syntax Elements

- **Comments:** `C` in column 1, or `/* ... */`
- **Multi-line format:** E (exponent), S (subscript), M (main) line prefixes
- **Assignment:** `=`
- **Program units:** `label: PROGRAM;`, `label: PROCEDURE;`, etc.
- **Type specifiers:**
  - `INTEGER` - Integer values
  - `SCALAR` - Floating-point values
  - `VECTOR(n)` - n-element vectors
  - `MATRIX(r,c)` - r×c matrices
  - `BOOLEAN` - Logical values
  - `CHARACTER(n)` - Character strings
  - `BIT(n)` - Bit strings
  - `EVENT` - Synchronisation events
- **Real-time keywords:** `SCHEDULE`, `WAIT`, `SIGNAL`, `PRIORITY`, `TERMINATE`
- **Logical operators:** `NOT`, `AND`, `OR`

### Multi-line Format

HAL/S supports a unique multi-line format for mathematical notation:

```
E           2
M    X = Y
S     I
```

This represents X = Y² (Y subscript I squared), allowing source code to resemble mathematical equations.

## Documentation Sources

This extension was developed using official NASA documentation:

1. **HAL/S Language Specification** (NASA, 1976)
   - Primary language reference

2. **HAL/S Programmer's Guide** (Intermetrics, 1978)
   - Programming techniques and examples

3. **Programming in HAL/S** (NASA, 1978)
   - Tutorial and programming manual

## Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| `hals.pythonPath` | Path to Python interpreter | `python` |
| `hals.serverPath` | Path to LSP server script | (bundled) |
| `hals.trace.server` | Trace level for debugging | `off` |

## Requirements

- Visual Studio Code 1.75.0 or later
- Python 3.8 or later

## Known Limitations

- Multi-line E/S/M format parsing is simplified (subscript/exponent lines are currently skipped)
- The parser handles core HAL/S constructs but may not cover all implementation-specific extensions
- Some advanced COMPOOL patterns may not be fully supported

## Licence

Copyright 2025 Zane Hambly

Licensed under the Apache Licence, Version 2.0. See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please open an issue or pull request on GitHub.

## Acknowledgements

- NASA (National Aeronautics and Space Administration)
- Intermetrics, Inc. (original HAL/S compiler developers)
- Space Shuttle Program flight software engineers
