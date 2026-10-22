"""Read and patch the data-only config.js without executing JavaScript.

Supports objects, arrays, strings, numbers, booleans, null and comments.
Value spans let updates preserve unrelated settings and surrounding comments.
"""
import ast
import json
import os
import re
import tempfile
from pathlib import Path


class ConfigParser:
    def __init__(self, source):
        self.source = source
        match = re.search(r'\b(?:const|let|var)\s+config\s*=\s*', source)
        if not match:
            raise ValueError('Cannot find the config object in config.js')
        self.pos = match.end()
        self.spans = {}

    def skip(self):
        while self.pos < len(self.source):
            if self.source[self.pos].isspace():
                self.pos += 1
            elif self.source.startswith('//', self.pos):
                end = self.source.find('\n', self.pos)
                self.pos = len(self.source) if end < 0 else end + 1
            elif self.source.startswith('/*', self.pos):
                end = self.source.find('*/', self.pos + 2)
                if end < 0:
                    raise ValueError('Unclosed config comment')
                self.pos = end + 2
            else:
                break

    def take(self, char):
        self.skip()
        if not self.source.startswith(char, self.pos):
            raise ValueError(f'Expected {char!r} near character {self.pos}')
        self.pos += len(char)

    def string(self):
        start = self.pos
        quote = self.source[self.pos]
        self.pos += 1
        while self.pos < len(self.source):
            char = self.source[self.pos]
            self.pos += 1
            if char == '\\':
                self.pos += 1
            elif char == quote:
                literal = self.source[start:self.pos]
                # JSON strings are emitted by write_config; JS single quotes are
                # retained in existing files. Neither path evaluates code.
                if quote == '"':
                    return json.loads(literal)
                return ast.literal_eval(literal.replace(r'\/', '/'))
        raise ValueError('Unclosed config string')

    def value(self, root=False):
        self.skip()
        if self.pos >= len(self.source):
            raise ValueError('Unexpected end of config')
        char = self.source[self.pos]
        if char in "\"'":
            return self.string()
        if char in '{[':
            is_object = char == '{'
            close = '}' if is_object else ']'
            result = {} if is_object else []
            self.pos += 1
            self.skip()
            while not self.source.startswith(close, self.pos):
                if is_object:
                    self.skip()
                    if self.source[self.pos] in "\"'":
                        key = self.string()
                    else:
                        match = re.match(r'[A-Za-z_$][\w$]*', self.source[self.pos:])
                        if not match:
                            raise ValueError(f'Invalid config key near {self.pos}')
                        key = match.group()
                        self.pos += len(key)
                    self.take(':')
                    self.skip()
                    start = self.pos
                    result[key] = self.value()
                    if root:
                        self.spans[key] = (start, self.pos)
                else:
                    result.append(self.value())
                self.skip()
                if self.source.startswith(close, self.pos):
                    break
                self.take(',')
                self.skip()
            self.take(close)
            return result
        match = re.match(r'(?:true|false|null)\b|-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?',
                         self.source[self.pos:])
        if not match:
            raise ValueError(f'Unsupported config expression near character {self.pos}')
        token = match.group()
        self.pos += len(token)
        return {'true': True, 'false': False, 'null': None}[token] if token in ('true', 'false', 'null') else (
            float(token) if any(char in token for char in '.eE') else int(token))

    def parse(self):
        result = self.value(root=True)
        if not isinstance(result, dict):
            raise ValueError('config must be an object')
        return result


def read_config(path):
    return ConfigParser(Path(path).read_text(encoding='utf-8')).parse()


def write_config(path, updates):
    path = Path(path)
    source = path.read_text(encoding='utf-8')
    parser = ConfigParser(source)
    parser.parse()
    missing = set(updates) - parser.spans.keys()
    if missing:
        raise ValueError('Unknown config fields: ' + ', '.join(sorted(missing)))
    edits = [(parser.spans[key], json.dumps(value, ensure_ascii=False, allow_nan=False))
             for key, value in updates.items()]
    for (start, end), value in sorted(edits, reverse=True):
        source = source[:start] + value + source[end:]
    # Validate every replacement before touching the original.
    ConfigParser(source).parse()
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix='.config-', suffix='.tmp')
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(source)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
