import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from mainTools.config_io import ConfigParser, read_config, write_config


SOURCE = """const config = {
    // User comments survive a save.
    BlogName: 'A blog',
    ProjectUrl: 'https://example.com/path', // keep this URL comment
    PostsPerPage: 5,
    InfoListUp: ['One', 'Two',],
    Links: [{name: 'Site', url: 'https://example.com',},],
    UtterancesConfig: {
        enabled: false,
        themeMapping: {'day': 'github-light', 'night': 'github-dark'},
    },
    CustomSetting: 'do not change',
};
export default config;
"""


class ConfigTests(unittest.TestCase):
    def test_round_trip_quotes_urls_lists_and_nested_booleans(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, 'config.js')
            path.write_text(SOURCE, encoding='utf-8')
            updates = {
                'BlogName': 'Writer\'s "notes" \\ drafts\n你好',
                'ProjectUrl': 'https://example.com/a,b?q=one/two',
                'InfoListUp': [],
                'Links': [{'name': "Writer's site", 'url': 'https://example.com/a]b'}],
                'UtterancesConfig': {'enabled': True, 'themeMapping': {'day': 'github-light'}},
            }
            write_config(path, updates)
            loaded = read_config(path)
            for key, value in updates.items():
                self.assertEqual(loaded[key], value)
            content = path.read_text(encoding='utf-8')
            self.assertIn('// User comments survive a save.', content)
            self.assertIn('// keep this URL comment', content)
            self.assertIn("CustomSetting: 'do not change'", content)
            self.assertIn('"enabled": true', content)
            self.assertNotIn('True', content)
            if shutil.which('node'):
                result = subprocess.run(['node', '--input-type=module', '--check'], input=content,
                                        capture_output=True, text=True, encoding='utf-8')
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_unsupported_or_missing_fields_leave_original_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, 'config.js')
            path.write_text(SOURCE, encoding='utf-8')
            with self.assertRaises(ValueError):
                write_config(path, {'Unknown': 1})
            self.assertEqual(path.read_text(encoding='utf-8'), SOURCE)
            with self.assertRaises(ValueError):
                write_config(path, {'PostsPerPage': float('nan')})
            self.assertEqual(path.read_text(encoding='utf-8'), SOURCE)

    def test_current_repository_config_is_readable(self):
        config = read_config(Path(__file__).resolve().parents[1] / 'src' / 'config.js')
        self.assertIsInstance(config['UtterancesConfig'], dict)
        self.assertIsInstance(config['Links'], list)
        self.assertIsInstance(config['enableTransitions'], bool)

    def test_parser_never_executes_expressions(self):
        with self.assertRaises(ValueError):
            ConfigParser('const config = {Name: process.exit(1)};').parse()


if __name__ == '__main__':
    unittest.main()
