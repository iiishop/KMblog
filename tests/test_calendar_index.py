import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'mainTools'))
from calendar_index import build_calendar_index


class CalendarIndexTests(unittest.TestCase):
    def test_extracts_only_gantt_blocks_and_preserves_source_dates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / '专题').mkdir()
            gantt = '```mermaid\ngantt\n task :2026-01-01, 1d\n```'
            (root / '专题' / '日程.md').write_text(
                '---\ntitle: Schedule\ndate: 2026-01-01\n---\nPrivate body text\n'
                + gantt + '\n```mermaid\nflowchart LR\n A-->B\n```\n' + gantt,
                encoding='utf-8')
            (root / 'ordinary.md').write_text('No calendar here', encoding='utf-8')
            entries = build_calendar_index(root)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]['path'], '/Posts/专题/日程.md')
            self.assertEqual(entries[0]['date'], '2026-01-01')
            self.assertEqual(entries[0]['content'], gantt + '\n\n' + gantt)
            self.assertNotIn('Private body text', str(entries))


if __name__ == '__main__':
    unittest.main()
