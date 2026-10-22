"""Manager interaction regressions. All writes use fake commands or temp folders."""
import asyncio
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import flet as ft

from blog_manager import BlogManagerGUI


POSTS = """Post: first.md | Title: First idea | Created on: 2026-01-01 | Characters: 100
Collection: Notes | Created on: 2026-01-01 | Posts: 1
    Post: first.md | Title: Another idea | Created on: 2026-01-02 | Characters: 200
Collection: Empty | Created on: 2026-01-01 | Posts: 0
"""


def walk(control):
    yield control
    content = getattr(control, 'content', None)
    if isinstance(content, ft.Control):
        yield from walk(content)
    for child in getattr(control, 'controls', []):
        yield from walk(child)


class Page:
    def __init__(self):
        self.window = SimpleNamespace()
        self.width = 1180
        self.overlay = []
        self.controls = []
        self.dialogs = []
        self.tasks = []

    def add(self, control):
        self.controls.append(control)

    def update(self):
        pass

    def show_dialog(self, dialog):
        dialog.open = True
        self.dialogs.append(dialog)

    def run_task(self, task):
        self.tasks.append(task)


class ManagerTests(unittest.TestCase):
    def setUp(self):
        commands = {'ListAllPosts': lambda: SimpleNamespace(execute=lambda: POSTS)}
        with patch.object(BlogManagerGUI, 'check_updates_on_startup'), \
                patch.object(BlogManagerGUI, 'get_commands', return_value=commands):
            self.page = Page()
            self.app = BlogManagerGUI(self.page)

    def test_search_filters_title_and_keeps_input_and_shell(self):
        self.app.switch_view('posts')
        field = self.app.search_field
        shell = self.page.controls[0]
        field.value = 'another'
        asyncio.run(self.app.on_search(SimpleNamespace(control=field)))
        self.assertEqual(self.app.results_count.value, '1 / 2 篇文章')
        self.assertEqual(set(self.app.collection_widgets), {'Notes'})
        self.assertIs(self.app.search_field, field)
        self.assertIs(self.page.controls[0], shell)

    def test_empty_collections_and_in_place_expand(self):
        self.app.switch_view('posts')
        group = self.app.collection_widgets['Notes']
        body = group.content.controls[1]
        toggle = group.content.controls[0].content.controls[0]
        self.assertFalse(body.visible)
        toggle.on_click(None)
        self.assertTrue(body.visible)
        self.assertIn('Notes', self.app.expanded_collections)
        self.assertIs(self.app.collection_widgets['Notes'], group)
        toggle.on_click(None)
        self.assertFalse(body.visible)
        self.assertIn('Empty', self.app.collection_widgets)

    def test_search_results_can_be_collapsed(self):
        self.app.switch_view('posts')
        self.app.search_query = 'Notes'
        self.app.refresh_post_results()
        self.assertTrue(self.app.collection_widgets['Notes'].content.controls[1].visible)
        self.app.expand_all(False)
        self.assertFalse(self.app.collection_widgets['Notes'].content.controls[1].visible)

    def test_invalid_and_duplicate_names_are_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch('mainTools.path_utils.get_posts_path', return_value=directory):
            Path(directory, 'Markdowns').mkdir()
            Path(directory, 'Markdowns', 'exists.md').write_text('keep me')
            for name in ('', '../escape', 'bad/name', 'CON', 'bad.', 'exists'):
                self.assertIsNotNone(self.app.validate_post_name(name, ''), name)
            self.assertIsNotNone(self.app.validate_post_name('post', 'Images'))
            self.assertIsNone(self.app.validate_post_name('新文章', '新合集'))

    def test_add_dialog_renders_and_empty_submit_stays_open(self):
        self.app.show_add_dialog(None)
        dialog = self.page.dialogs[-1]
        fields = [c for c in walk(dialog) if isinstance(c, ft.TextField)]
        fields[0].on_submit(None)
        self.assertTrue(dialog.open)
        self.assertEqual(fields[0].error, self.app.t('please_input_post'))
        self.assertIn('error', fields[0].__dataclass_fields__)
        self.assertIsNotNone(fields[1].helper)

    def test_move_dialog_includes_uncollected_and_other_collections(self):
        self.app.show_move_dialog('first', 'Notes')
        target = next(c for c in walk(self.page.dialogs[-1]) if isinstance(c, ft.Dropdown))
        self.assertEqual({option.key for option in target.options}, {'Markdowns', 'Empty'})

    def test_operation_serializes_and_invalidates_cache(self):
        calls = []
        self.assertTrue(self.app.run_operation('first', lambda: calls.append('first')))
        self.assertFalse(self.app.run_operation('second', lambda: calls.append('second')))
        self.assertTrue(self.app.busy)
        asyncio.run(self.page.tasks.pop()())
        self.assertEqual(calls, ['first'])
        self.assertFalse(self.app.busy)
        self.assertFalse(self.app.task_progress.visible)
        self.assertFalse(self.app.operation_lock.locked())

    def test_failed_command_does_not_report_success(self):
        self.app.run_operation('delete', lambda: 'Error: Post is missing.')
        asyncio.run(self.page.tasks.pop()())
        self.assertIn('操作失败', self.app.status_text.value)
        self.assertFalse(self.app.operation_lock.locked())

    def test_config_draft_survives_navigation_and_link_removal(self):
        config = '{"BlogName":"Before","PostsPerPage":10,"BackgroundImgOpacity":0.5,"BackgroundImgBlur":0,"Links":[{"name":"A","url":"https://a.example"},{"name":"B","url":"https://b.example"}]}'
        with patch('mainTools.commands.GetConfig.execute', return_value=config), \
                patch('mainTools.commands.GetCryptoPassword.execute', return_value=''):
            self.app.switch_view('settings')
        view = self.app.settings_view
        fields = [c for c in walk(view) if isinstance(c, ft.TextField)]
        blog = next(c for c in fields if c.label == self.app.t('blog_name'))
        blog.value = 'After'
        blog.on_change(None)
        self.app.switch_view('dashboard')
        self.app.switch_view('settings')
        self.assertIs(view, self.app.content_host.content)
        self.assertEqual(blog.value, 'After')
        self.assertTrue(self.app.settings_dirty)
        links = [c for c in fields if c.label == self.app.t('link_name')]
        links[1].value = 'Edited B'
        delete = next(c for c in walk(view) if isinstance(c, ft.IconButton) and c.tooltip == self.app.t('remove_item'))
        delete.on_click(None)
        remaining = [c for c in walk(view) if isinstance(c, ft.TextField) and c.label == self.app.t('link_name')]
        self.assertEqual([c.value for c in remaining], ['Edited B'])

    def test_preview_uses_exact_collection(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch('mainTools.path_utils.get_posts_path', return_value=directory), \
                patch('mainTools.utility.parse_markdown_metadata', return_value={}):
            for collection, body in [('Markdowns', 'Wrong post'), ('Notes', 'Correct post')]:
                Path(directory, collection).mkdir()
                Path(directory, collection, 'same.md').write_text(body, encoding='utf-8')
            self.app.show_post_preview('same', 'Notes')
            text = [c.value for c in walk(self.page.dialogs[-1]) if isinstance(c, ft.Markdown)]
            self.assertEqual(text, ['Correct post'])

    def test_responsive_sidebar_does_not_rebuild_form(self):
        self.app.switch_view('posts')
        field = self.app.search_field
        self.page.width = 800
        self.app.on_resize(None)
        self.assertEqual(self.app.sidebar_host.content.width, 80)
        self.assertIs(self.app.search_field, field)

    def test_native_close_requires_choice_for_unsaved_settings(self):
        self.page.window.destroy = AsyncMock()
        self.app.settings_dirty = True
        asyncio.run(self.app.on_window_event(SimpleNamespace(type=ft.WindowEventType.CLOSE)))
        self.page.window.destroy.assert_not_awaited()
        self.assertTrue(self.page.dialogs[-1].modal)

    def test_clean_window_can_close(self):
        self.page.window.destroy = AsyncMock()
        asyncio.run(self.app.on_window_event(SimpleNamespace(type=ft.WindowEventType.CLOSE)))
        self.page.window.destroy.assert_awaited_once()


if __name__ == '__main__':
    unittest.main()
