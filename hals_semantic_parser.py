"""
HAL/S Semantic Parser
Based on NASA HAL/S Language Specification and Programming in HAL/S (1978)

HAL/S (High-order Assembly Language/Shuttle) is a real-time aerospace
programming language developed by Intermetrics for NASA. It powered
approximately 85% of the Space Shuttle flight software.

Reference: NASA Technical Reports - HAL/S Language Specification (1974-1978)
"""

import re
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class SymbolKind(Enum):
    """Symbol kinds for HAL/S"""
    PROGRAM = "program"
    PROCEDURE = "procedure"
    FUNCTION = "function"
    TASK = "task"
    COMPOOL = "compool"
    VARIABLE = "variable"
    CONSTANT = "constant"
    STRUCTURE = "structure"
    LABEL = "label"
    PARAMETER = "parameter"
    REPLACE = "replace"


@dataclass
class Symbol:
    """A symbol in the HAL/S program"""
    name: str
    kind: SymbolKind
    data_type: str
    line: int
    column: int
    end_line: int = 0
    end_column: int = 0
    scope: str = "global"
    documentation: str = ""
    parameters: List[str] = field(default_factory=list)
    dimensions: List[str] = field(default_factory=list)


@dataclass
class Reference:
    """A reference to a symbol"""
    name: str
    line: int
    column: int
    end_column: int = 0
    context: str = ""


@dataclass
class Diagnostic:
    """A diagnostic message"""
    line: int
    column: int
    end_column: int
    message: str
    severity: str = "error"


class HALSParser:
    """
    Parser for HAL/S (High-order Assembly Language/Shuttle)

    Based on NASA HAL/S Language Specification
    """

    # HAL/S keywords
    KEYWORDS = {
        # Program units
        'PROGRAM', 'PROCEDURE', 'FUNCTION', 'TASK', 'COMPOOL', 'UPDATE',
        'CLOSE', 'RETURN',

        # Declarations
        'DECLARE', 'CONSTANT', 'INITIAL', 'STATIC', 'AUTOMATIC',
        'TEMPORARY', 'DENSE', 'ALIGNED', 'RIGID', 'REMOTE', 'ACCESS',
        'ASSIGN', 'NAME', 'LOCK', 'EXCLUSIVE', 'LATCHED', 'REPLACE',
        'STRUCTURE', 'ARRAY',

        # Data types
        'INTEGER', 'SCALAR', 'VECTOR', 'MATRIX', 'BOOLEAN', 'CHARACTER',
        'BIT', 'EVENT', 'SINGLE', 'DOUBLE',

        # Control flow
        'IF', 'THEN', 'ELSE', 'DO', 'END', 'FOR', 'TO', 'BY', 'WHILE',
        'UNTIL', 'REPEAT', 'EXIT', 'GO', 'GOTO', 'CASE',

        # Real-time
        'SCHEDULE', 'WAIT', 'SIGNAL', 'PRIORITY', 'TERMINATE', 'CANCEL',
        'SET', 'RESET', 'ON', 'OFF', 'ERROR', 'DEPENDENT', 'IGNORE',

        # I/O
        'READ', 'READALL', 'WRITE', 'FILE',

        # Operators as keywords
        'NOT', 'AND', 'OR', 'CAT', 'MOD', 'TRUE', 'FALSE',

        # Built-in functions
        'ABS', 'CEILING', 'FLOOR', 'TRUNCATE', 'ROUND', 'ODD', 'SIGN',
        'MAX', 'MIN', 'SUM', 'PROD', 'SHL', 'SHR', 'SIZE', 'LENGTH',
        'INDEX', 'MIDVAL', 'RANDOM', 'RANDOMG', 'DATE', 'RUNTIME',
        'CLOCKTIME', 'PRIO', 'NEXTIME',

        # Math functions
        'SIN', 'COS', 'TAN', 'ARCSIN', 'ARCCOS', 'ARCTAN', 'ARCTAN2',
        'SINH', 'COSH', 'TANH', 'EXP', 'LOG', 'SQRT',

        # Vector/Matrix operations
        'TRANSPOSE', 'TRACE', 'DET', 'INVERSE', 'IDENTITY',
        'UNIT', 'ABVAL', 'DOT', 'CROSS',
    }

    # Operators
    OPERATORS = {
        '**': 'exponentiation',
        '*': 'multiply',
        '/': 'divide',
        '+': 'add',
        '-': 'subtract',
        '=': 'equals',
        '¬=': 'not equal',
        '~=': 'not equal (alt)',
        '^=': 'not equal (alt)',
        '<': 'less than',
        '>': 'greater than',
        '<=': 'less or equal',
        '>=': 'greater or equal',
        '¬': 'not',
        '~': 'not (alt)',
        '^': 'not (alt)',
        '&': 'and',
        '|': 'or',
        '||': 'concatenate',
    }

    def __init__(self):
        self.symbols: Dict[str, Symbol] = {}
        self.references: List[Reference] = []
        self.diagnostics: List[Diagnostic] = []
        self.lines: List[str] = []
        self.current_scope: str = "global"
        self.scope_stack: List[str] = ["global"]

    def parse(self, text: str) -> None:
        """Parse HAL/S source code"""
        self.symbols = {}
        self.references = []
        self.diagnostics = []
        self.lines = text.split('\n')
        self.current_scope = "global"
        self.scope_stack = ["global"]

        # Preprocess multi-line format (E/S/M lines)
        processed_text = self._preprocess_multiline(text)

        # Remove comments
        cleaned_text = self._remove_comments(processed_text)

        # Parse declarations and structures
        self._parse_programs(cleaned_text)
        self._parse_procedures(cleaned_text)
        self._parse_functions(cleaned_text)
        self._parse_tasks(cleaned_text)
        self._parse_compools(cleaned_text)
        self._parse_declares(cleaned_text)
        self._parse_structures(cleaned_text)
        self._parse_replaces(cleaned_text)
        self._parse_labels(cleaned_text)

        # Parse references
        self._parse_references(cleaned_text)

    def _preprocess_multiline(self, text: str) -> str:
        """
        Preprocess HAL/S multi-line format.
        E = exponent line, S = subscript line, M = main line
        """
        lines = text.split('\n')
        result_lines = []

        for line in lines:
            if line and len(line) > 0:
                first_char = line[0].upper()
                if first_char in ('E', 'S'):
                    # Skip exponent/subscript lines for now (simplified parsing)
                    continue
                elif first_char == 'M':
                    # Main line - strip the M prefix
                    result_lines.append(line[1:] if len(line) > 1 else '')
                elif first_char == 'C':
                    # Comment line
                    result_lines.append('/*' + line[1:] + '*/')
                else:
                    result_lines.append(line)
            else:
                result_lines.append(line)

        return '\n'.join(result_lines)

    def _remove_comments(self, text: str) -> str:
        """Remove HAL/S comments: /* ... */ and C in column 1"""
        # Remove block comments
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        return text

    def _find_position(self, text: str, match_start: int) -> Tuple[int, int]:
        """Convert character offset to line and column"""
        line = text[:match_start].count('\n')
        last_newline = text.rfind('\n', 0, match_start)
        column = match_start - last_newline - 1 if last_newline >= 0 else match_start
        return (line, column)

    def _parse_programs(self, text: str) -> None:
        """Parse PROGRAM declarations: label: PROGRAM;"""
        pattern = r'\b([A-Z_][A-Z0-9_]*)\s*:\s*PROGRAM\s*;'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            name = match.group(1)
            line, col = self._find_position(text, match.start())

            self.symbols[name.upper()] = Symbol(
                name=name.upper(),
                kind=SymbolKind.PROGRAM,
                data_type="PROGRAM",
                line=line,
                column=col,
                documentation=f"HAL/S Program unit"
            )

    def _parse_procedures(self, text: str) -> None:
        """Parse PROCEDURE declarations"""
        pattern = r'\b([A-Z_][A-Z0-9_]*)\s*:\s*PROCEDURE\s*(?:\(([^)]*)\))?\s*;'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            name = match.group(1)
            params_text = match.group(2)
            line, col = self._find_position(text, match.start())

            params = []
            if params_text:
                params = [p.strip() for p in params_text.split(',')]

            self.symbols[name.upper()] = Symbol(
                name=name.upper(),
                kind=SymbolKind.PROCEDURE,
                data_type="PROCEDURE",
                line=line,
                column=col,
                parameters=params,
                documentation=f"Procedure with {len(params)} parameters" if params else "Procedure"
            )

    def _parse_functions(self, text: str) -> None:
        """Parse FUNCTION declarations with return type"""
        pattern = r'\b([A-Z_][A-Z0-9_]*)\s*:\s*(INTEGER|SCALAR|VECTOR|MATRIX|BOOLEAN|CHARACTER|BIT)?\s*FUNCTION\s*(?:\(([^)]*)\))?\s*;'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            name = match.group(1)
            return_type = match.group(2) or "SCALAR"
            params_text = match.group(3)
            line, col = self._find_position(text, match.start())

            params = []
            if params_text:
                params = [p.strip() for p in params_text.split(',')]

            self.symbols[name.upper()] = Symbol(
                name=name.upper(),
                kind=SymbolKind.FUNCTION,
                data_type=f"{return_type.upper()} FUNCTION",
                line=line,
                column=col,
                parameters=params,
                documentation=f"Function returning {return_type.upper()}"
            )

    def _parse_tasks(self, text: str) -> None:
        """Parse TASK declarations (real-time processes)"""
        pattern = r'\b([A-Z_][A-Z0-9_]*)\s*:\s*TASK\s*;'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            name = match.group(1)
            line, col = self._find_position(text, match.start())

            self.symbols[name.upper()] = Symbol(
                name=name.upper(),
                kind=SymbolKind.TASK,
                data_type="TASK",
                line=line,
                column=col,
                documentation="Real-time task (schedulable process)"
            )

    def _parse_compools(self, text: str) -> None:
        """Parse COMPOOL declarations (shared data pools)"""
        pattern = r'\b([A-Z_][A-Z0-9_]*)\s*:\s*COMPOOL\s*;'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            name = match.group(1)
            line, col = self._find_position(text, match.start())

            self.symbols[name.upper()] = Symbol(
                name=name.upper(),
                kind=SymbolKind.COMPOOL,
                data_type="COMPOOL",
                line=line,
                column=col,
                documentation="Communication pool (shared data)"
            )

    def _parse_declares(self, text: str) -> None:
        """
        Parse DECLARE statements:
        DECLARE name type;
        DECLARE name ARRAY(dims) type;
        DECLARE name CONSTANT(value);
        DECLARE name type INITIAL(value);
        """
        # Simple declarations
        pattern = r'\bDECLARE\s+([A-Z_][A-Z0-9_]*)\s+(INTEGER|SCALAR|VECTOR|MATRIX|BOOLEAN|CHARACTER|BIT|EVENT)\s*(?:INITIAL\s*\([^)]*\))?\s*;'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            name = match.group(1)
            data_type = match.group(2).upper()
            line, col = self._find_position(text, match.start())

            self.symbols[name.upper()] = Symbol(
                name=name.upper(),
                kind=SymbolKind.VARIABLE,
                data_type=data_type,
                line=line,
                column=col,
                documentation=f"{data_type} variable"
            )

        # Array declarations
        pattern = r'\bDECLARE\s+([A-Z_][A-Z0-9_]*)\s+ARRAY\s*\(([^)]+)\)\s+(INTEGER|SCALAR|VECTOR|MATRIX|BOOLEAN|CHARACTER|BIT)\s*;'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            name = match.group(1)
            dims = match.group(2)
            data_type = match.group(3).upper()
            line, col = self._find_position(text, match.start())

            self.symbols[name.upper()] = Symbol(
                name=name.upper(),
                kind=SymbolKind.VARIABLE,
                data_type=f"ARRAY({dims}) {data_type}",
                line=line,
                column=col,
                dimensions=[d.strip() for d in dims.split(',')],
                documentation=f"Array of {data_type} with dimensions ({dims})"
            )

        # Constants
        pattern = r'\bDECLARE\s+([A-Z_][A-Z0-9_]*)\s+CONSTANT\s*\(([^)]+)\)\s*;'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            name = match.group(1)
            value = match.group(2)
            line, col = self._find_position(text, match.start())

            self.symbols[name.upper()] = Symbol(
                name=name.upper(),
                kind=SymbolKind.CONSTANT,
                data_type="CONSTANT",
                line=line,
                column=col,
                documentation=f"Constant = {value}"
            )

        # Vector declarations with size
        pattern = r'\bDECLARE\s+([A-Z_][A-Z0-9_]*)\s+VECTOR\s*\((\d+)\)\s*;'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            name = match.group(1)
            size = match.group(2)
            line, col = self._find_position(text, match.start())

            self.symbols[name.upper()] = Symbol(
                name=name.upper(),
                kind=SymbolKind.VARIABLE,
                data_type=f"VECTOR({size})",
                line=line,
                column=col,
                dimensions=[size],
                documentation=f"Vector of {size} elements"
            )

        # Matrix declarations
        pattern = r'\bDECLARE\s+([A-Z_][A-Z0-9_]*)\s+MATRIX\s*\((\d+)\s*,\s*(\d+)\)\s*;'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            name = match.group(1)
            rows = match.group(2)
            cols = match.group(3)
            line, col = self._find_position(text, match.start())

            self.symbols[name.upper()] = Symbol(
                name=name.upper(),
                kind=SymbolKind.VARIABLE,
                data_type=f"MATRIX({rows},{cols})",
                line=line,
                column=col,
                dimensions=[rows, cols],
                documentation=f"Matrix of {rows}x{cols} elements"
            )

    def _parse_structures(self, text: str) -> None:
        """Parse STRUCTURE declarations"""
        pattern = r'\bDECLARE\s+([A-Z_][A-Z0-9_]*)\s+STRUCTURE\s*;'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            name = match.group(1)
            line, col = self._find_position(text, match.start())

            self.symbols[name.upper()] = Symbol(
                name=name.upper(),
                kind=SymbolKind.STRUCTURE,
                data_type="STRUCTURE",
                line=line,
                column=col,
                documentation="Structure type"
            )

    def _parse_replaces(self, text: str) -> None:
        """Parse REPLACE macro definitions"""
        pattern = r'\bREPLACE\s+([A-Z_][A-Z0-9_]*)\s+BY\s+"([^"]+)"\s*;'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            name = match.group(1)
            replacement = match.group(2)
            line, col = self._find_position(text, match.start())

            self.symbols[name.upper()] = Symbol(
                name=name.upper(),
                kind=SymbolKind.REPLACE,
                data_type="REPLACE",
                line=line,
                column=col,
                documentation=f"Macro expanding to: {replacement}"
            )

    def _parse_labels(self, text: str) -> None:
        """Parse statement labels (identifier followed by colon)"""
        pattern = r'\b([A-Z_][A-Z0-9_]*)\s*:'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            name = match.group(1)
            # Skip if it's a program unit keyword following the colon
            after = text[match.end():match.end()+20].strip().upper()
            if after.startswith(('PROGRAM', 'PROCEDURE', 'FUNCTION', 'TASK', 'COMPOOL')):
                continue

            # Skip if already defined as something else
            if name.upper() in self.symbols:
                continue

            line, col = self._find_position(text, match.start())
            self.symbols[name.upper()] = Symbol(
                name=name.upper(),
                kind=SymbolKind.LABEL,
                data_type="LABEL",
                line=line,
                column=col,
                documentation="Statement label (GO TO target)"
            )

    def _parse_references(self, text: str) -> None:
        """Parse all identifier references"""
        pattern = r'\b([A-Z_][A-Z0-9_]*)\b'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            name = match.group(1)
            if name.upper() in self.KEYWORDS:
                continue

            line, col = self._find_position(text, match.start())
            self.references.append(Reference(
                name=name.upper(),
                line=line,
                column=col,
                end_column=col + len(name)
            ))

    def get_symbols(self) -> Dict[str, Symbol]:
        """Get all parsed symbols"""
        return self.symbols

    def get_references(self) -> List[Reference]:
        """Get all references"""
        return self.references

    def get_diagnostics(self) -> List[Diagnostic]:
        """Get all diagnostics"""
        return self.diagnostics

    def get_completions(self, line: int, column: int) -> List[Dict]:
        """Get completion items at position"""
        completions = []

        # Add keywords
        for kw in sorted(self.KEYWORDS):
            completions.append({
                'label': kw,
                'kind': 'keyword',
                'detail': 'HAL/S keyword',
                'documentation': f"HAL/S keyword: {kw}"
            })

        # Add symbols
        for name, sym in self.symbols.items():
            completions.append({
                'label': sym.name,
                'kind': sym.kind.value,
                'detail': sym.data_type,
                'documentation': sym.documentation
            })

        return completions

    def get_hover(self, line: int, column: int) -> Optional[Dict]:
        """Get hover information at position"""
        if line >= len(self.lines):
            return None

        line_text = self.lines[line]

        # Find the word at this position
        for match in re.finditer(r'\b([A-Z_][A-Z0-9_]*)\b', line_text, re.IGNORECASE):
            if match.start() <= column <= match.end():
                word = match.group(1).upper()

                if word in self.KEYWORDS:
                    return {'contents': f"**{word}**\n\nHAL/S keyword"}

                if word in self.symbols:
                    sym = self.symbols[word]
                    return {'contents': f"**{sym.name}**: {sym.data_type}\n\n{sym.documentation}"}
                break

        return None

    def get_definition(self, line: int, column: int) -> Optional[Dict]:
        """Get definition location for symbol at position"""
        if line >= len(self.lines):
            return None

        line_text = self.lines[line]

        for match in re.finditer(r'\b([A-Z_][A-Z0-9_]*)\b', line_text, re.IGNORECASE):
            if match.start() <= column <= match.end():
                word = match.group(1).upper()
                if word in self.symbols:
                    sym = self.symbols[word]
                    return {
                        'line': sym.line,
                        'column': sym.column,
                        'name': sym.name
                    }
                break

        return None

    def get_references_at(self, line: int, column: int) -> List[Dict]:
        """Get all references to symbol at position"""
        if line >= len(self.lines):
            return []

        line_text = self.lines[line]
        target_word = None

        for match in re.finditer(r'\b([A-Z_][A-Z0-9_]*)\b', line_text, re.IGNORECASE):
            if match.start() <= column <= match.end():
                target_word = match.group(1).upper()
                break

        if not target_word:
            return []

        refs = []
        for ref in self.references:
            if ref.name == target_word:
                refs.append({
                    'line': ref.line,
                    'column': ref.column,
                    'end_column': ref.end_column
                })

        return refs

    def get_document_symbols(self) -> List[Dict]:
        """Get all document symbols for outline"""
        symbols = []
        for name, sym in self.symbols.items():
            symbols.append({
                'name': sym.name,
                'kind': sym.kind.value,
                'detail': sym.data_type,
                'line': sym.line,
                'column': sym.column
            })
        return sorted(symbols, key=lambda x: x['line'])


def main():
    """Test the parser"""
    test_code = '''
C HAL/S TEST PROGRAM FOR SPACE SHUTTLE FLIGHT SOFTWARE
C DEMONSTRATES BASIC LANGUAGE FEATURES

SHUTTLE_NAV: PROGRAM;
    /* Declare constants */
    DECLARE PI CONSTANT(3.14159265);
    DECLARE G CONSTANT(9.80665);
    DECLARE EARTH_RADIUS CONSTANT(6371.0);

    /* Declare variables */
    DECLARE ALTITUDE SCALAR;
    DECLARE VELOCITY VECTOR(3);
    DECLARE POSITION VECTOR(3);
    DECLARE ATTITUDE MATRIX(3,3);
    DECLARE MISSION_TIME SCALAR;
    DECLARE ENGINE_ON BOOLEAN;
    DECLARE ABORT_FLAG EVENT;

    /* Arrays */
    DECLARE SENSOR_DATA ARRAY(10) SCALAR;
    DECLARE THRUSTER_STATUS ARRAY(6) BOOLEAN;

    /* Read initial state */
    READ(5) ALTITUDE, VELOCITY, POSITION;

    /* Navigation loop */
NAV_LOOP:
    DO WHILE ENGINE_ON;
        MISSION_TIME = MISSION_TIME + 0.1;

        /* Update position */
        POSITION = POSITION + VELOCITY * 0.1;

        /* Check altitude */
        IF ALTITUDE < 100.0 THEN
            SIGNAL ABORT_FLAG;

        /* Continue navigation */
        GO TO NAV_LOOP;
    END;

    WRITE(6) POSITION, VELOCITY, MISSION_TIME;

CLOSE SHUTTLE_NAV;

/* Guidance function */
COMPUTE_THRUST: SCALAR FUNCTION(MASS, ACCEL);
    DECLARE MASS SCALAR;
    DECLARE ACCEL VECTOR(3);
    DECLARE THRUST SCALAR;

    THRUST = MASS * ABVAL(ACCEL);
    RETURN THRUST;
CLOSE COMPUTE_THRUST;

/* Real-time navigation task */
NAV_TASK: TASK;
    DECLARE STATE VECTOR(6);

    DO WHILE TRUE;
        WAIT FOR 0.1 SECONDS;
        /* Update navigation state */
        STATE = STATE;
    END;
CLOSE NAV_TASK;
'''

    parser = HALSParser()
    parser.parse(test_code)

    print("=" * 60)
    print("HAL/S SEMANTIC PARSER TEST")
    print("NASA Space Shuttle Flight Software Language")
    print("=" * 60)
    print()

    print("SYMBOLS FOUND:")
    print("-" * 40)
    for name, sym in sorted(parser.symbols.items()):
        print(f"  {sym.name:20} {sym.kind.value:12} {sym.data_type}")
    print()

    print("COMPLETIONS (first 15):")
    print("-" * 40)
    completions = parser.get_completions(0, 0)
    for c in completions[:15]:
        print(f"  {c['label']:20} {c['kind']:12} {c['detail']}")
    print()

    print("DOCUMENT SYMBOLS:")
    print("-" * 40)
    for sym in parser.get_document_symbols():
        print(f"  Line {sym['line']:3}: {sym['name']:20} ({sym['kind']})")


if __name__ == '__main__':
    main()
