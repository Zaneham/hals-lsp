# HAL/S Language Support for Visual Studio Code

[![VS Code Marketplace](https://img.shields.io/visual-studio-marketplace/v/ZaneHambly.hals-lsp?label=VS%20Code%20Marketplace)](https://marketplace.visualstudio.com/items?itemName=ZaneHambly.hals-lsp)

Language Server Protocol (LSP) implementation for **HAL/S** (High-order Assembly Language/Shuttle), the programming language that flew the Space Shuttle for thirty years.

When astronauts needed to know where they were, how fast they were going, and whether they were going to make it home, HAL/S code gave them the answer. The language handled vectors and matrices natively because nobody should be debugging pointer arithmetic during re-entry.

## What is HAL/S?

HAL/S was developed by Intermetrics in the early 1970s under contract to NASA. The requirement was simple: a programming language for computers that absolutely could not crash, running software that absolutely had to work, in an environment where "have you tried turning it off and on again" was not an option.

The language powered approximately 85% of the Space Shuttle's Primary Avionics Software System (PASS). The other 15% was backup software, written by a completely separate team in a completely different way, so that a bug in the primary system wouldn't also be a bug in the backup. NASA took reliability seriously.

### What HAL/S Flew

| System | Role |
|--------|------|
| **Primary Avionics Software System (PASS)** | Main flight control, guidance, navigation for all 135 Shuttle missions |
| **Backup Flight Software (BFS)** | Independent backup system, never needed in flight |
| **Space Station Freedom** | Precursor to ISS, software development used HAL/S |
| **Various NASA spacecraft** | Guidance and control systems |

The Shuttle flew from 1981 to 2011. That's thirty years of launches, orbital operations, and re-entries. Every time you saw a Shuttle land, HAL/S code was calculating the glide slope. Every time astronauts docked with a space station, HAL/S code was managing the approach. Every time the Shuttle came home, HAL/S code was bringing it down safely.

## The Multi-Line Format

HAL/S has a feature you won't find in any other language: source code that looks like mathematical notation.

```
E           2
M    X = Y
S     I
```

The E line is exponents. The M line is the main expression. The S line is subscripts. This represents X = Y²ᵢ (Y subscript I, squared).

NASA's reasoning: astronauts and flight controllers were trained in mathematics, not programming. If the source code looked like the equations in the flight manuals, fewer mistakes would be made. Whether this was true is debatable. That it was attempted is remarkable.

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
4. Your orbital mechanics code now has syntax highlighting

## File Extensions

| Extension | Description |
|-----------|-------------|
| `.hal`    | HAL/S source file |
| `.hals`   | HAL/S source file (alternate) |

## Language Overview

HAL/S looks like ALGOL had a baby with linear algebra. Vectors and matrices are first-class types. You can multiply a matrix by a vector and it just works. This is what happens when rocket scientists design a programming language.

```hals
C HAL/S NAVIGATION EXAMPLE
C FOR SPACE SHUTTLE FLIGHT SOFTWARE

SHUTTLE_NAV:
PROGRAM;
   DECLARE PI CONSTANT(3.14159265);
   DECLARE G CONSTANT(9.80665);                    /* Gravity constant */
   DECLARE ALTITUDE SCALAR;
   DECLARE VELOCITY VECTOR(3);
   DECLARE POSITION VECTOR(3);
   DECLARE ATTITUDE MATRIX(3, 3);
   DECLARE ENGINE_ON BOOLEAN;
   DECLARE ABORT_FLAG EVENT;
   DECLARE SENSOR_DATA ARRAY(10) SCALAR;          /* IMU data */

C GUIDANCE FUNCTION - NESTED INSIDE PROGRAM
COMPUTE_THRUST:
FUNCTION(MASS, ACCEL) SCALAR;
   DECLARE MASS SCALAR;
   DECLARE ACCEL VECTOR(3);
   DECLARE THRUST SCALAR;
   THRUST = MASS ABVAL(ACCEL);                    /* Spaces for multiply */
   RETURN THRUST;
CLOSE COMPUTE_THRUST;

C REAL-TIME TASK FOR NAVIGATION UPDATES
NAV_TASK:
TASK;
   DECLARE STATE VECTOR(6);
   DO WHILE TRUE;
      WAIT 0.04;                                  /* 25 Hz update rate */
      STATE = STATE;
   END;
CLOSE NAV_TASK;

C NAVIGATION LOOP - RUNS DURING ASCENT
NAV_LOOP:
   DO WHILE ENGINE_ON;
      POSITION = POSITION + VELOCITY 0.04;        /* Vector math */
      IF ALTITUDE < 100.0 THEN
         SIGNAL ABORT_FLAG;
      REPEAT NAV_LOOP;
   END;
CLOSE SHUTTLE_NAV;
```

### Key Syntax Elements

- **Column 1:** Special - only M (main), C (comment), D (directive), E (exponent), S (subscript) allowed
- **Comments:** `C` in column 1 for full-line, or `/* ... */` inline
- **Multiplication:** Use spaces, not `*` (e.g., `A B` means A × B)
- **Multi-line format:** E (exponent), S (subscript), M (main) line prefixes
- **Assignment:** `=` (straightforward)
- **Program units:** `label:` on one line, `PROGRAM;` on next. One compilation unit per file, or nest inside PROGRAM.
- **WAIT:** `WAIT 0.1` not `WAIT FOR 0.1 SECONDS` (units are implementation-dependent)
- **Type specifiers:**
  - `INTEGER` for whole numbers
  - `SCALAR` for floating-point (they called it SCALAR, not FLOAT)
  - `VECTOR(n)` for n-element vectors
  - `MATRIX(r,c)` for r×c matrices
  - `BOOLEAN` for logical values
  - `CHARACTER(n)` for character strings
  - `BIT(n)` for bit strings
  - `EVENT` for synchronisation events
- **Real-time keywords:** `SCHEDULE`, `WAIT`, `SIGNAL`, `PRIORITY`, `TERMINATE`

The `COMPOOL` construct lets you define shared data across program units. On the Shuttle, this was how the guidance computer, the flight control computer, and the systems management computer all agreed on where the vehicle was and what it was doing.

## Documentation Sources

This extension was developed using official NASA documentation:

1. **HAL/S Language Specification** (NASA, 1976)
   - The primary reference, written by people who were actually going to fly this code

2. **HAL/S Programmer's Guide** (Intermetrics, 1978)
   - How to actually use the language, with examples

3. **Programming in HAL/S** (NASA, 1978)
   - Tutorial for new programmers joining the Shuttle software team

NASA's Shuttle software team was famous for their rigour. The HAL/S documentation reflects this. Every edge case is specified. Every ambiguity is resolved. When lives depend on your code, you don't leave things to interpretation.

## Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| `hals.pythonPath` | Path to Python interpreter | `python` |
| `hals.serverPath` | Path to LSP server script | (bundled) |
| `hals.trace.server` | Trace level for debugging | `off` |

## Requirements

- Visual Studio Code 1.75.0 or later
- Python 3.8 or later
- Optional: an understanding of orbital mechanics

## Known Limitations

- Multi-line E/S/M format parsing is simplified (exponent and subscript lines are currently handled as comments)
- The parser handles core HAL/S constructs but may not cover all implementation-specific extensions
- Some advanced COMPOOL patterns may not be fully supported
- Cannot actually calculate orbital trajectories (this is a syntax highlighter, not a flight computer)

## Why This Matters

The Space Shuttle is retired. The last one flew in 2011. But HAL/S matters for the same reason we study Latin: understanding where we came from helps us understand where we're going.

The Shuttle software team achieved something remarkable: millions of lines of code that flew 135 missions without a software-caused failure. They did this with 1970s tools, 1970s hardware, and 1970s management practices that would horrify modern agile consultants. They wrote specifications. They reviewed code. They tested exhaustively. They took responsibility.

Modern spacecraft don't use HAL/S. But the lessons of how the Shuttle software was built are still relevant. This LSP exists so that people who want to study that history can at least read the code.

## Licence

Copyright 2025 Zane Hambly

Licensed under the Apache Licence, Version 2.0. See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome. Particularly:
- Syntax patterns from real HAL/S code
- Corrections from people who actually worked on Shuttle software
- Better handling of the multi-line E/S/M format

If you worked on the Shuttle software, your knowledge would be invaluable. The code is archived. The experience of writing it is not.

## Related Projects

If you've found yourself oddly moved by a language that handles vectors natively because astronauts shouldn't debug pointer arithmetic during re-entry:

- **[JOVIAL J73 LSP](https://github.com/Zaneham/jovial-lsp)** - Same era, same contractors (Intermetrics built both), different altitude ceiling. JOVIAL keeps aircraft from crashing. HAL/S kept spacecraft from crashing. Similar problem, higher stakes.

- **[CMS-2 LSP](https://github.com/Zaneham/cms2-lsp)** - The US Navy's tactical language. For when you need real-time computing but prefer to stay attached to a planet. Aegis cruisers and submarines. No astronauts required.

- **[CORAL 66 LSP](https://github.com/Zaneham/coral66-lsp)** - The British equivalent. Developed at the Royal Radar Establishment, Malvern. Powers Tornado aircraft. Presumably runs perfectly well in drizzle.

- **[CHILL LSP](https://github.com/Zaneham/chill-lsp)** - For telephone switches. Also real-time, also critical, also forgotten. Different infrastructure, same era.

- **[Minuteman Guidance Computer Emulator](https://github.com/Zaneham/minuteman-emu)** - Another way of getting to space. Just the once. Rather more quickly. No heat tiles required. No return trip either.

## Contact

Questions? Found an issue? Worked on the actual Shuttle software and want to tell me everything I got wrong?

zanehambly@gmail.com

Ground control is standing by. All transmissions welcome. Response time faster than an orbital period.

## Acknowledgements

- NASA, for shooting people into space and bringing them back
- Intermetrics, for building a language that was up to the job
- The Shuttle software team, for thirty years of flawless operation
- Everyone who documented their work so thoroughly that we can still learn from it
- Ron Burkey and the [Virtual AGC Project](https://virtualagc.github.io/virtualagc/) for syntax corrections validated against an actual HAL/S compiler
