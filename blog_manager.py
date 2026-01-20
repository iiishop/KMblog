"""
KMBlog 管理工具 - 现代化 Flet GUI
具有可视化仪表板和直观的用户界面
"""

from mainTools.commands import Command
import flet as ft
import sys
import os
import importlib
import inspect
import json

# 添加 mainTools 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mainTools'))


class BlogManagerGUI:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.commands = self.get_commands()
        self.current_lang = 'zh'
        self.current_view = 'dashboard'
        self.build_ui()

    def setup_page(self):
        """设置页面属性"""
        self.page.title = "KMBlog Manager"
        self.page.window.width = 1400
        self.page.window.height = 900
        self.page.padding = 0
        self.page.bgcolor = ft.Colors.GREY_50

    def get_commands(self):
        """动态获取所有命令类"""
        try:
            # 确保导入正确的模块 - 使用 mainTools.commands
            if 'mainTools.commands' in sys.modules:
                commands_module = sys.modules['mainTools.commands']
            else:
                commands_module = importlib.import_module('mainTools.commands')

            commands = {}
            for name, obj in inspect.getmembers(commands_module):
                if inspect.isclass(obj) and issubclass(obj, Command) and obj is not Command:
                    commands[name] = obj

            # 调试：打印加载的命令
            print(f"Loaded commands: {list(commands.keys())}")
            return commands
        except Exception as e:
            print(f"Error loading commands: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def t(self, key):
        """多语言翻译"""
        trans = {
            'zh': {
                'title': 'KMBlog 管理工具', 'dashboard': '仪表板', 'posts': '文章管理',
                'collections': '合集管理', 'post_name': '文章名称', 'collection_name': '合集名称',
                'add_post': '添加文章', 'delete_post': '删除文章', 'delete_collection': '删除合集',
                'generate': '生成配置', 'init_blog': '初始化博客', 'refresh': '刷新',
                'switch_lang': 'EN', 'total_posts': '总文章数', 'total_collections': '总合集数',
                'recent_posts': '最近文章', 'quick_actions': '快速操作', 'post_list': '文章列表',
                'collection_list': '合集列表', 'no_posts': '暂无文章', 'no_collections': '暂无合集',
                'success': '成功', 'error': '错误', 'confirm_delete': '确认删除',
                'confirm_delete_post': '确定要删除文章 "{}" 吗？',
                'confirm_delete_collection': '确定要删除合集 "{}" 及其所有文章吗？',
                'cancel': '取消', 'confirm': '确认', 'input_error': '输入错误',
                'please_input_post': '请输入文章名称！', 'please_input_collection': '请输入合集名称！',
                'operation_success': '操作成功！', 'articles': '篇文章',
            },
            'en': {
                'title': 'KMBlog Manager', 'dashboard': 'Dashboard', 'posts': 'Posts',
                'collections': 'Collections', 'post_name': 'Post Name', 'collection_name': 'Collection',
                'add_post': 'Add Post', 'delete_post': 'Delete Post', 'delete_collection': 'Delete Collection',
                'generate': 'Generate', 'init_blog': 'Init Blog', 'refresh': 'Refresh',
                'switch_lang': '中文', 'total_posts': 'Total Posts', 'total_collections': 'Total Collections',
                'recent_posts': 'Recent Posts', 'quick_actions': 'Quick Actions', 'post_list': 'Posts',
                'collection_list': 'Collections', 'no_posts': 'No posts', 'no_collections': 'No collections',
                'success': 'Success', 'error': 'Error', 'confirm_delete': 'Confirm',
                'confirm_delete_post': 'Delete "{}"?', 'confirm_delete_collection': 'Delete "{}" and all posts?',
                'cancel': 'Cancel', 'confirm': 'OK', 'input_error': 'Error',
                'please_input_post': 'Enter post name!', 'please_input_collection': 'Enter collection name!',
                'operation_success': 'Success!', 'articles': 'articles',
            }
        }
        return trans[self.current_lang].get(key, key)

    def switch_lang(self, e):
        self.current_lang = 'en' if self.current_lang == 'zh' else 'zh'
        self.build_ui()

    def switch_view(self, view):
        self.current_view = view
        self.build_ui()

    def build_ui(self):
        """构建主界面"""
        self.page.controls.clear()
        layout = ft.Row([
            self.build_sidebar(),
            ft.VerticalDivider(width=1, color=ft.Colors.GREY_300),
            ft.Container(content=self.get_current_view(),
                         expand=True, padding=30),
        ], spacing=0, expand=True)
        self.page.add(layout)
        self.page.update()

    def build_sidebar(self):
        """侧边栏"""
        nav_items = [
            ('dashboard', ft.Icons.DASHBOARD, self.t('dashboard')),
            ('posts', ft.Icons.ARTICLE, self.t('posts')),
            ('collections', ft.Icons.FOLDER, self.t('collections')),
        ]

        buttons = []
        for view, icon, label in nav_items:
            selected = self.current_view == view
            buttons.append(ft.Container(
                content=ft.Row([
                    ft.Icon(
                        icon, size=20, color=ft.Colors.WHITE if selected else ft.Colors.BLUE_GREY_400),
                    ft.Text(
                        label, color=ft.Colors.WHITE if selected else ft.Colors.BLUE_GREY_400),
                ], spacing=12),
                padding=ft.Padding(15, 12, 15, 12),
                bgcolor=ft.Colors.BLUE_700 if selected else None,
                border_radius=10,
                on_click=lambda e, v=view: self.switch_view(v),
                ink=True,
            ))

        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ARTICLE, size=36,
                                color=ft.Colors.BLUE_400),
                        ft.Text("KMBlog", size=26,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ], spacing=12),
                    padding=20,
                ),
                ft.Divider(height=1, color=ft.Colors.BLUE_GREY_700),
                ft.Container(content=ft.Column(
                    buttons, spacing=8), padding=15),
                ft.Container(expand=True),
                ft.Divider(height=1, color=ft.Colors.BLUE_GREY_700),
                ft.Container(
                    content=ft.Button(
                        self.t('switch_lang'), icon=ft.Icons.LANGUAGE,
                        on_click=self.switch_lang, width=210,
                    ),
                    padding=20,
                ),
            ], spacing=0),
            width=260,
            bgcolor=ft.Colors.BLUE_GREY_900,
        )

    def get_current_view(self):
        """获取当前视图"""
        if self.current_view == 'dashboard':
            return self.build_dashboard()
        elif self.current_view == 'posts':
            return self.build_posts_view()
        elif self.current_view == 'collections':
            return self.build_collections_view()
        return ft.Text("Unknown view")

    def build_dashboard(self):
        """仪表板"""
        stats = self.get_stats()

        stat_cards = ft.Row([
            self.stat_card(self.t('total_posts'), str(
                stats['posts']), ft.Icons.ARTICLE, ft.Colors.BLUE_500),
            self.stat_card(self.t('total_collections'), str(
                stats['collections']), ft.Icons.FOLDER, ft.Colors.ORANGE_500),
        ], spacing=20)

        actions = ft.Container(
            content=ft.Column([
                ft.Text(self.t('quick_actions'), size=22,
                        weight=ft.FontWeight.BOLD),
                ft.Container(height=15),
                ft.Row([
                    self.action_btn(self.t('add_post'), ft.Icons.ADD_CIRCLE,
                                    self.show_add_dialog, ft.Colors.GREEN_600),
                    self.action_btn(self.t(
                        'generate'), ft.Icons.BUILD_CIRCLE, self.exec_generate, ft.Colors.BLUE_600),
                    self.action_btn(self.t(
                        'init_blog'), ft.Icons.ROCKET_LAUNCH, self.exec_init, ft.Colors.PURPLE_600),
                ], spacing=15, wrap=True),
            ]),
            padding=25,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(
                blur_radius=15, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        )

        recent = self.build_recent_posts()

        return ft.Column([
            ft.Text(self.t('dashboard'), size=32, weight=ft.FontWeight.BOLD),
            ft.Container(height=25),
            stat_cards,
            ft.Container(height=25),
            actions,
            ft.Container(height=25),
            recent,
        ], scroll=ft.ScrollMode.AUTO, expand=True)

    def stat_card(self, title, value, icon, color):
        """统计卡片"""
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icon, size=42, color=ft.Colors.WHITE),
                    bgcolor=color, border_radius=12, padding=18,
                ),
                ft.Column([
                    ft.Text(title, size=14, color=ft.Colors.GREY_600),
                    ft.Text(value, size=36, weight=ft.FontWeight.BOLD),
                ], spacing=2),
            ], spacing=18),
            padding=25,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(
                blur_radius=15, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
            expand=True,
        )

    def action_btn(self, text, icon, onclick, color):
        """操作按钮"""
        return ft.Button(
            content=ft.Row(
                [ft.Icon(icon, size=22), ft.Text(text, size=15)], spacing=10),
            on_click=onclick,
            style=ft.ButtonStyle(padding=22, bgcolor=color,
                                 color=ft.Colors.WHITE),
        )

    def build_recent_posts(self):
        """最近文章"""
        try:
            result = self.commands['ListAllPosts']().execute()
            lines = [l for l in result.split('\n')[:6] if 'Post:' in l]
            items = [self.post_item(l) for l in lines] if lines else [
                ft.Text(self.t('no_posts'), color=ft.Colors.GREY_500)]

            return ft.Container(
                content=ft.Column([
                    ft.Text(self.t('recent_posts'), size=22,
                            weight=ft.FontWeight.BOLD),
                    ft.Container(height=15),
                    ft.Column(items, spacing=12),
                ]),
                padding=25,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                shadow=ft.BoxShadow(
                    blur_radius=15, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
            )
        except:
            return ft.Container()

    def post_item(self, line):
        """文章项"""
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.DESCRIPTION, size=22,
                        color=ft.Colors.BLUE_400),
                ft.Text(line.strip()[:80], size=13),
            ], spacing=12),
            padding=12,
            border=ft.border.all(1, ft.Colors.BLUE_100),
            border_radius=8,
            bgcolor=ft.Colors.BLUE_50,
        )

    def build_posts_view(self):
        """文章视图"""
        self.post_field = ft.TextField(label=self.t('post_name'), width=350)
        self.coll_field = ft.TextField(
            label=self.t('collection_name'), width=350)

        header = ft.Container(
            content=ft.Column([
                ft.Text(self.t('post_list'), size=28,
                        weight=ft.FontWeight.BOLD),
                ft.Container(height=15),
                ft.Row([self.post_field, self.coll_field], spacing=20),
                ft.Container(height=15),
                ft.Row([
                    ft.Button(self.t('add_post'), icon=ft.Icons.ADD, on_click=lambda e: self.exec_add_post(
                    ), bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
                    ft.Button(self.t('delete_post'), icon=ft.Icons.DELETE, on_click=lambda e: self.exec_del_post(
                    ), bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
                    ft.Button(self.t('refresh'), icon=ft.Icons.REFRESH, on_click=lambda e: self.build_ui(
                    ), bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE),
                ], spacing=12),
            ]),
            padding=25,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(
                blur_radius=15, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        )

        return ft.Column([header, ft.Container(height=20), self.build_posts_list()], scroll=ft.ScrollMode.AUTO, expand=True)

    def build_posts_list(self):
        """文章列表"""
        try:
            result = self.commands['ListAllPosts']().execute()
            lines = [l for l in result.split('\n') if 'Post:' in l]
            cards = [self.post_card(l) for l in lines] if lines else [ft.Text(
                self.t('no_posts'), size=18, color=ft.Colors.GREY_500)]

            return ft.Container(
                content=ft.Column(cards, spacing=12),
                padding=25,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                shadow=ft.BoxShadow(
                    blur_radius=15, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
            )
        except Exception as e:
            return ft.Container(content=ft.Text(f"Error: {e}", color=ft.Colors.RED_500))

    def post_card(self, line):
        """文章卡片"""
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ARTICLE, size=26, color=ft.Colors.BLUE_600),
                ft.Text(line.strip(), size=14, expand=True),
            ], spacing=15),
            padding=18,
            border=ft.border.all(1, ft.Colors.BLUE_200),
            border_radius=10,
            bgcolor=ft.Colors.BLUE_50,
        )

    def build_collections_view(self):
        """合集视图"""
        self.coll_name_field = ft.TextField(
            label=self.t('collection_name'), width=400)

        header = ft.Container(
            content=ft.Column([
                ft.Text(self.t('collection_list'), size=28,
                        weight=ft.FontWeight.BOLD),
                ft.Container(height=15),
                ft.Row([self.coll_name_field], spacing=20),
                ft.Container(height=15),
                ft.Row([
                    ft.Button(self.t('delete_collection'), icon=ft.Icons.DELETE, on_click=lambda e: self.exec_del_coll(
                    ), bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
                    ft.Button(self.t('refresh'), icon=ft.Icons.REFRESH, on_click=lambda e: self.build_ui(
                    ), bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE),
                ], spacing=12),
            ]),
            padding=25,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(
                blur_radius=15, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        )

        return ft.Column([header, ft.Container(height=20), self.build_coll_list()], scroll=ft.ScrollMode.AUTO, expand=True)

    def build_coll_list(self):
        """合集列表"""
        try:
            result = self.commands['ListCollections']().execute()
            if not result or not result.strip():
                return ft.Container(content=ft.Text(self.t('no_collections'), size=18, color=ft.Colors.GREY_500))

            lines = [l for l in result.split('\n') if 'Collection:' in l]
            cards = [self.coll_card(l) for l in lines] if lines else [
                ft.Text(self.t('no_collections'), color=ft.Colors.GREY_500)]

            return ft.Container(
                content=ft.Column(cards, spacing=18),
                padding=25,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                shadow=ft.BoxShadow(
                    blur_radius=15, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
            )
        except:
            return ft.Container(content=ft.Text(self.t('no_collections'), color=ft.Colors.GREY_500))

    def coll_card(self, line):
        """合集卡片"""
        parts = line.split('|')
        name = parts[0].replace('Collection:', '').strip()
        info = parts[1].strip() if len(parts) > 1 else ''
        date = parts[2].strip() if len(parts) > 2 else ''

        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.FOLDER, size=44,
                                    color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.ORANGE_600, border_radius=12, padding=20,
                ),
                ft.Column([
                    ft.Text(name, size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(info, size=13, color=ft.Colors.GREY_600),
                    ft.Text(date, size=12, color=ft.Colors.GREY_500),
                ], spacing=4, expand=True),
            ], spacing=18),
            padding=22,
            border=ft.border.all(1, ft.Colors.ORANGE_200),
            border_radius=12,
            bgcolor=ft.Colors.ORANGE_50,
        )

    def get_stats(self):
        """统计数据"""
        stats = {'posts': 0, 'collections': 0}
        try:
            if 'ListAllPosts' not in self.commands:
                print(
                    f"Warning: ListAllPosts not found. Available: {list(self.commands.keys())}")
                return stats

            result = self.commands['ListAllPosts']().execute()
            print(f"ListAllPosts result: {result[:200] if result else 'None'}")
            stats['posts'] = result.count('Post:') if result else 0

            if 'ListCollections' in self.commands:
                result = self.commands['ListCollections']().execute()
                print(
                    f"ListCollections result: {result[:200] if result else 'None'}")
                stats['collections'] = result.count(
                    'Collection:') if result else 0
        except Exception as e:
            print(f"Error in get_stats: {e}")
            import traceback
            traceback.print_exc()
        return stats

    def snack(self, msg, error=False):
        """消息提示"""
        snack_bar = ft.SnackBar(
            content=ft.Text(msg, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_600 if error else ft.Colors.GREEN_600,
            duration=3000,
        )
        snack_bar.open = True
        self.page.overlay.append(snack_bar)
        self.page.update()

    def show_add_dialog(self, e):
        """添加文章对话框"""
        post = ft.TextField(label=self.t('post_name'), width=350)
        coll = ft.TextField(label=self.t('collection_name'), width=350)

        def add(e):
            if not post.value or not post.value.strip():
                self.snack(self.t('please_input_post'), True)
                return
            self.close_dlg(dlg)
            self.do_add_post(post.value.strip(),
                             coll.value.strip() if coll.value else None)

        dlg = ft.AlertDialog(
            title=ft.Text(self.t('add_post')),
            content=ft.Column([post, coll], tight=True),
            actions=[
                ft.TextButton(self.t('cancel'),
                              on_click=lambda e: self.close_dlg(dlg)),
                ft.Button(self.t('confirm'), on_click=add),
            ],
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def exec_add_post(self):
        """执行添加文章"""
        post = self.post_field.value.strip() if self.post_field.value else ""
        coll = self.coll_field.value.strip() if self.coll_field.value else None
        if not post:
            self.snack(self.t('please_input_post'), True)
            return
        self.do_add_post(post, coll)

    def do_add_post(self, post, coll):
        """实际添加文章"""
        inputs = [post, coll or '', 'y']
        idx = [0]

        def mock(p):
            if idx[0] < len(inputs):
                v = inputs[idx[0]]
                idx[0] += 1
                return v
            return ''

        import builtins
        orig = builtins.input
        builtins.input = mock
        try:
            self.commands['AddPost']().execute()
            self.snack(self.t('operation_success'))
            self.build_ui()
        except Exception as e:
            self.snack(f"{self.t('error')}: {e}", True)
        finally:
            builtins.input = orig

    def exec_del_post(self):
        """执行删除文章"""
        post = self.post_field.value.strip() if self.post_field.value else ""
        coll = self.coll_field.value.strip() if self.coll_field.value else None
        if not post:
            self.snack(self.t('please_input_post'), True)
            return
        self.confirm(self.t('confirm_delete'), self.t('confirm_delete_post').format(
            post), lambda: self.do_del_post(post, coll))

    def do_del_post(self, post, coll):
        """实际删除文章"""
        inputs = [post, coll or '', 'y']
        idx = [0]

        def mock(p):
            if idx[0] < len(inputs):
                v = inputs[idx[0]]
                idx[0] += 1
                return v
            return ''

        import builtins
        orig = builtins.input
        builtins.input = mock
        try:
            self.commands['DeletePost']().execute()
            self.snack(self.t('operation_success'))
            self.build_ui()
        except Exception as e:
            self.snack(f"{self.t('error')}: {e}", True)
        finally:
            builtins.input = orig

    def exec_del_coll(self):
        """执行删除合集"""
        coll = self.coll_name_field.value.strip() if self.coll_name_field.value else ""
        if not coll:
            self.snack(self.t('please_input_collection'), True)
            return
        self.confirm(self.t('confirm_delete'), self.t(
            'confirm_delete_collection').format(coll), lambda: self.do_del_coll(coll))

    def do_del_coll(self, coll):
        """实际删除合集"""
        inputs = [coll, 'y']
        idx = [0]

        def mock(p):
            if idx[0] < len(inputs):
                v = inputs[idx[0]]
                idx[0] += 1
                return v
            return ''

        import builtins
        orig_in = builtins.input
        orig_pr = builtins.print
        builtins.input = mock
        builtins.print = lambda *a, **k: None
        try:
            self.commands['DeleteCollection']().execute()
            self.snack(self.t('operation_success'))
            self.build_ui()
        except Exception as e:
            self.snack(f"{self.t('error')}: {e}", True)
        finally:
            builtins.input = orig_in
            builtins.print = orig_pr

    def exec_generate(self, e):
        """生成配置"""
        try:
            self.commands['Generate']().execute()
            self.snack(self.t('operation_success'))
        except Exception as e:
            self.snack(f"{self.t('error')}: {e}", True)

    def exec_init(self, e):
        """初始化博客"""
        try:
            self.commands['InitBlog']().execute()
            self.snack(self.t('operation_success'))
            self.build_ui()
        except Exception as e:
            self.snack(f"{self.t('error')}: {e}", True)

    def confirm(self, title, msg, callback):
        """确认对话框"""
        def ok(e):
            self.close_dlg(dlg)
            callback()

        dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(msg),
            actions=[
                ft.TextButton(self.t('cancel'),
                              on_click=lambda e: self.close_dlg(dlg)),
                ft.Button(self.t('confirm'), on_click=ok,
                          bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
            ],
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def close_dlg(self, dlg):
        """关闭对话框"""
        dlg.open = False
        self.page.update()


def main(page: ft.Page):
    BlogManagerGUI(page)


if __name__ == '__main__':
    ft.run(main)
