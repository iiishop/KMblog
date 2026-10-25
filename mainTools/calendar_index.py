"""Publish only calendar source blocks, so visitors never scan every article."""
import re
from pathlib import Path

from utility import parse_markdown_metadata


def build_calendar_index(posts_path):
    root = Path(posts_path)
    entries = []
    for path in sorted(root.rglob('*.md')):
        content = path.read_text(encoding='utf-8-sig')
        # Match the existing CalendarPanel parser, including multiple Gantt blocks.
        blocks = re.findall(r'```mermaid\s*gantt[\s\S]*?```', content)
        if not blocks:
            continue
        metadata = parse_markdown_metadata(str(path)) or {}
        entries.append({
            'path': '/Posts/' + path.relative_to(root).as_posix(),
            'date': str(metadata.get('date') or ''),
            'content': '\n\n'.join(blocks),
        })
    return entries
