#!/usr/bin/env python3
"""
HAL/S Language Server Protocol (LSP) Implementation

Provides IDE features for HAL/S (High-order Assembly Language/Shuttle),
the real-time aerospace programming language used for NASA Space Shuttle
flight software.

Based on the NASA HAL/S Language Specification (1974-1978)
"""

import json
import sys
import re
from typing import Dict, List, Optional, Any

from hals_semantic_parser import HALSParser, SymbolKind


class HALSLanguageServer:
    """LSP server for HAL/S"""

    def __init__(self):
        self.parser = HALSParser()
        self.documents: Dict[str, str] = {}
        self.running = True

    def start(self):
        """Start the language server"""
        while self.running:
            try:
                message = self._read_message()
                if message:
                    response = self._handle_message(message)
                    if response:
                        self._send_message(response)
            except Exception as e:
                self._log(f"Error: {e}")

    def _read_message(self) -> Optional[Dict]:
        """Read a JSON-RPC message from stdin"""
        headers = {}
        while True:
            line = sys.stdin.readline()
            if not line:
                self.running = False
                return None
            line = line.strip()
            if not line:
                break
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()

        if 'Content-Length' not in headers:
            return None

        length = int(headers['Content-Length'])
        content = sys.stdin.read(length)
        return json.loads(content)

    def _send_message(self, message: Dict):
        """Send a JSON-RPC message to stdout"""
        content = json.dumps(message)
        header = f"Content-Length: {len(content)}\r\n\r\n"
        sys.stdout.write(header + content)
        sys.stdout.flush()

    def _send_notification(self, method: str, params: Dict):
        """Send a notification"""
        self._send_message({
            'jsonrpc': '2.0',
            'method': method,
            'params': params
        })

    def _log(self, message: str):
        """Log a message to the client"""
        self._send_notification('window/logMessage', {
            'type': 3,  # Info
            'message': f"[HAL/S] {message}"
        })

    def _handle_message(self, message: Dict) -> Optional[Dict]:
        """Handle incoming JSON-RPC message"""
        method = message.get('method', '')
        msg_id = message.get('id')
        params = message.get('params', {})

        handlers = {
            'initialize': self._handle_initialize,
            'initialized': self._handle_initialized,
            'shutdown': self._handle_shutdown,
            'exit': self._handle_exit,
            'textDocument/didOpen': self._handle_did_open,
            'textDocument/didChange': self._handle_did_change,
            'textDocument/didClose': self._handle_did_close,
            'textDocument/completion': self._handle_completion,
            'textDocument/hover': self._handle_hover,
            'textDocument/definition': self._handle_definition,
            'textDocument/references': self._handle_references,
            'textDocument/documentSymbol': self._handle_document_symbol,
        }

        handler = handlers.get(method)
        if handler:
            result = handler(params)
            if msg_id is not None:
                return {
                    'jsonrpc': '2.0',
                    'id': msg_id,
                    'result': result
                }
        elif msg_id is not None:
            return {
                'jsonrpc': '2.0',
                'id': msg_id,
                'error': {
                    'code': -32601,
                    'message': f"Method not found: {method}"
                }
            }
        return None

    def _handle_initialize(self, params: Dict) -> Dict:
        """Handle initialize request"""
        return {
            'capabilities': {
                'textDocumentSync': {
                    'openClose': True,
                    'change': 1,  # Full sync
                    'save': {'includeText': True}
                },
                'completionProvider': {
                    'triggerCharacters': ['.', ':', ' '],
                    'resolveProvider': False
                },
                'hoverProvider': True,
                'definitionProvider': True,
                'referencesProvider': True,
                'documentSymbolProvider': True,
            },
            'serverInfo': {
                'name': 'HAL/S Language Server',
                'version': '1.0.0'
            }
        }

    def _handle_initialized(self, params: Dict) -> None:
        """Handle initialized notification"""
        self._log("HAL/S Language Server ready - NASA Space Shuttle flight software language")
        return None

    def _handle_shutdown(self, params: Dict) -> None:
        """Handle shutdown request"""
        return None

    def _handle_exit(self, params: Dict) -> None:
        """Handle exit notification"""
        self.running = False
        return None

    def _handle_did_open(self, params: Dict) -> None:
        """Handle textDocument/didOpen"""
        doc = params.get('textDocument', {})
        uri = doc.get('uri', '')
        text = doc.get('text', '')
        self.documents[uri] = text
        self._parse_and_publish(uri, text)
        return None

    def _handle_did_change(self, params: Dict) -> None:
        """Handle textDocument/didChange"""
        doc = params.get('textDocument', {})
        uri = doc.get('uri', '')
        changes = params.get('contentChanges', [])
        if changes:
            text = changes[0].get('text', '')
            self.documents[uri] = text
            self._parse_and_publish(uri, text)
        return None

    def _handle_did_close(self, params: Dict) -> None:
        """Handle textDocument/didClose"""
        doc = params.get('textDocument', {})
        uri = doc.get('uri', '')
        if uri in self.documents:
            del self.documents[uri]
        return None

    def _parse_and_publish(self, uri: str, text: str):
        """Parse document and publish diagnostics"""
        self.parser.parse(text)
        diagnostics = []
        for diag in self.parser.get_diagnostics():
            diagnostics.append({
                'range': {
                    'start': {'line': diag.line, 'character': diag.column},
                    'end': {'line': diag.line, 'character': diag.end_column}
                },
                'message': diag.message,
                'severity': 1 if diag.severity == 'error' else 2
            })
        self._send_notification('textDocument/publishDiagnostics', {
            'uri': uri,
            'diagnostics': diagnostics
        })

    def _handle_completion(self, params: Dict) -> List[Dict]:
        """Handle textDocument/completion"""
        uri = params.get('textDocument', {}).get('uri', '')
        position = params.get('position', {})
        line = position.get('line', 0)
        char = position.get('character', 0)

        if uri in self.documents:
            self.parser.parse(self.documents[uri])

        completions = self.parser.get_completions(line, char)
        result = []

        kind_map = {
            'keyword': 14,      # Keyword
            'program': 2,       # Module
            'procedure': 3,     # Function
            'function': 3,      # Function
            'task': 2,          # Module
            'compool': 2,       # Module
            'variable': 6,      # Variable
            'constant': 21,     # Constant
            'structure': 22,    # Struct
            'label': 20,        # Reference
            'replace': 15,      # Snippet
            'parameter': 6,     # Variable
        }

        for c in completions:
            result.append({
                'label': c['label'],
                'kind': kind_map.get(c['kind'], 6),
                'detail': c['detail'],
                'documentation': c.get('documentation', '')
            })

        return result

    def _handle_hover(self, params: Dict) -> Optional[Dict]:
        """Handle textDocument/hover"""
        uri = params.get('textDocument', {}).get('uri', '')
        position = params.get('position', {})
        line = position.get('line', 0)
        char = position.get('character', 0)

        if uri in self.documents:
            self.parser.parse(self.documents[uri])

        hover = self.parser.get_hover(line, char)
        if hover:
            return {
                'contents': {
                    'kind': 'markdown',
                    'value': hover['contents']
                }
            }
        return None

    def _handle_definition(self, params: Dict) -> Optional[Dict]:
        """Handle textDocument/definition"""
        uri = params.get('textDocument', {}).get('uri', '')
        position = params.get('position', {})
        line = position.get('line', 0)
        char = position.get('character', 0)

        if uri in self.documents:
            self.parser.parse(self.documents[uri])

        definition = self.parser.get_definition(line, char)
        if definition:
            return {
                'uri': uri,
                'range': {
                    'start': {'line': definition['line'], 'character': definition['column']},
                    'end': {'line': definition['line'], 'character': definition['column'] + len(definition['name'])}
                }
            }
        return None

    def _handle_references(self, params: Dict) -> List[Dict]:
        """Handle textDocument/references"""
        uri = params.get('textDocument', {}).get('uri', '')
        position = params.get('position', {})
        line = position.get('line', 0)
        char = position.get('character', 0)

        if uri in self.documents:
            self.parser.parse(self.documents[uri])

        refs = self.parser.get_references_at(line, char)
        result = []
        for ref in refs:
            result.append({
                'uri': uri,
                'range': {
                    'start': {'line': ref['line'], 'character': ref['column']},
                    'end': {'line': ref['line'], 'character': ref['end_column']}
                }
            })
        return result

    def _handle_document_symbol(self, params: Dict) -> List[Dict]:
        """Handle textDocument/documentSymbol"""
        uri = params.get('textDocument', {}).get('uri', '')

        if uri in self.documents:
            self.parser.parse(self.documents[uri])

        symbols = self.parser.get_document_symbols()
        result = []

        kind_map = {
            'program': 2,       # Module
            'procedure': 12,    # Function
            'function': 12,     # Function
            'task': 2,          # Module
            'compool': 2,       # Module
            'variable': 13,     # Variable
            'constant': 14,     # Constant
            'structure': 23,    # Struct
            'label': 20,        # Key
            'replace': 15,      # Macro
            'parameter': 13,    # Variable
        }

        for sym in symbols:
            result.append({
                'name': sym['name'],
                'kind': kind_map.get(sym['kind'], 13),
                'range': {
                    'start': {'line': sym['line'], 'character': sym['column']},
                    'end': {'line': sym['line'], 'character': sym['column'] + len(sym['name'])}
                },
                'selectionRange': {
                    'start': {'line': sym['line'], 'character': sym['column']},
                    'end': {'line': sym['line'], 'character': sym['column'] + len(sym['name'])}
                },
                'detail': sym.get('detail', '')
            })

        return result


def main():
    """Start the HAL/S language server"""
    server = HALSLanguageServer()
    server.start()


if __name__ == '__main__':
    main()
