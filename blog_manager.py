"""
KMBlog 管理工具 - 现代化 Flet GUI
具有可视化仪表板和直观的用户界面
"""



import flet as ft
import sys
import os
import importlib
import inspect
import json
import webbrowser

# 添加 mainTools 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mainTools'))
from mainTools.commands import Command

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
                'build_project': '构建项目',
                'blog_initialized': '博客已初始化',
                'settings': '配置管理',
                'blog_name': '博客名称',
                'short_desc': '简短描述',
                'author_name': '作者名称',
                'author_desc': '作者描述',
                'project_url': '项目URL',
                'background_img': '背景图片',
                'bg_opacity': '背景不透明度',
                'bg_blur': '背景模糊度',
                'head_img': '头像图片',
                'posts_per_page': '每页文章数',
                'theme': '主题',
                'change_info_tip_pos': '交换信息提示位置',
                'save_config': '保存配置',
                'lists_config': '列表配置',
                'social_links': '社交链接',
                'info_list_up': 'Info列表上',
                'info_list_down': 'Info列表下',
                'tip_list_up': 'Tip列表上',
                'tip_list_down': 'Tip列表下',
                'main_list_up': 'Main列表上',
                'main_list_down': 'Main列表下',
                'info_list_float': 'Info浮动列表',
                'tip_list_float': 'Tip浮动列表',
                'add_item': '添加项',
                'remove_item': '移除项',
                'link_name': '链接名称',
                'link_url': '链接URL',
                'add_link': '添加链接',
                'deploy_github': '部署到GitHub',
                'github_token': 'GitHub Token',
                'github_repo': '仓库名称',
                'verify_token': '验证Token',
                'get_token_guide': '获取Token指南',
                'token_valid': 'Token有效',
                'token_invalid': 'Token无效',
                'deploying': '正在部署...',
                'deploy_success': '部署成功',
                'deploy_failed': '部署失败',
                'token_permissions': 'Token权限要求',
                'token_perm_desc': '您需要一个具有以下权限的GitHub Personal Access Token:\n- repo (完整仓库访问权限)',
                'get_token_url': '获取Token地址: https://github.com/settings/tokens/new',
                'next_step': '下一步',
                'previous_step': '上一步',
                'start_deploy': '开始部署',
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
                'build_project': 'Build Project',
                'blog_initialized': 'Blog Initialized',
                'settings': 'Settings',
                'blog_name': 'Blog Name',
                'short_desc': 'Short Description',
                'author_name': 'Author Name',
                'author_desc': 'Author Description',
                'project_url': 'Project URL',
                'background_img': 'Background Image',
                'bg_opacity': 'BG Opacity',
                'bg_blur': 'BG Blur',
                'head_img': 'Avatar Image',
                'posts_per_page': 'Posts Per Page',
                'theme': 'Theme',
                'change_info_tip_pos': 'Swap Info/Tip Position',
                'save_config': 'Save Config',
                'lists_config': 'Lists Config',
                'social_links': 'Social Links',
                'info_list_up': 'Info List Up',
                'info_list_down': 'Info List Down',
                'tip_list_up': 'Tip List Up',
                'tip_list_down': 'Tip List Down',
                'main_list_up': 'Main List Up',
                'main_list_down': 'Main List Down',
                'info_list_float': 'Info List Float',
                'tip_list_float': 'Tip List Float',
                'add_item': 'Add Item',
                'remove_item': 'Remove',
                'link_name': 'Name',
                'link_url': 'URL',
                'add_link': 'Add Link',
                'deploy_github': 'Deploy to GitHub',
                'github_token': 'GitHub Token',
                'github_repo': 'Repository Name',
                'verify_token': 'Verify Token',
                'get_token_guide': 'Get Token Guide',
                'token_valid': 'Token Valid',
                'token_invalid': 'Token Invalid',
                'deploying': 'Deploying...',
                'deploy_success': 'Deploy Success',
                'deploy_failed': 'Deploy Failed',
                'token_permissions': 'Token Permissions',
                'token_perm_desc': 'You need a GitHub Personal Access Token with:\n- repo (Full repository access)',
                'get_token_url': 'Get Token: https://github.com/settings/tokens/new',
                'next_step': 'Next',
                'previous_step': 'Previous',
                'start_deploy': 'Start Deploy',
            }
        }
        return trans[self.current_lang].get(key, key)

    def switch_lang(self, e):
        self.current_lang = 'en' if self.current_lang == 'zh' else 'zh'
        self.build_ui()

    def switch_view(self, view):
        self.current_view = view
        self.build_ui()

    def is_blog_initialized(self):
        """检查博客是否已经初始化"""
        try:
            from mainTools.path_utils import get_assets_path
            assets_path = get_assets_path()

            # 检查必要的 JSON 文件是否存在
            required_files = [
                os.path.join(assets_path, 'PostDirectory.json'),
                os.path.join(assets_path, 'Categories.json'),
                os.path.join(assets_path, 'Tags.json'),
            ]

            return all(os.path.exists(f) for f in required_files)
        except:
            return False

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
            ('settings', ft.Icons.SETTINGS, self.t('settings')),
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
        elif self.current_view == 'settings':
            return self.build_settings_view()
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
                    # 只在博客未初始化时显示初始化按钮
                    self.action_btn(self.t(
                        'init_blog'), ft.Icons.ROCKET_LAUNCH, self.exec_init, ft.Colors.PURPLE_600) if not self.is_blog_initialized() else ft.Container(),
                    self.action_btn(self.t(
                        'build_project'), ft.Icons.CONSTRUCTION, self.exec_build, ft.Colors.ORANGE_600),
                    self.action_btn(self.t(
                        'deploy_github'), ft.Icons.CLOUD_UPLOAD, self.show_github_dialog, ft.Colors.INDIGO_600),
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
        # 从列表中提取文章名，处理多种格式
        line_clean = line.replace('Post:', '').strip()
        # 可能的格式: "name | collection | date" 或 "collection/name | date" 或只是 "name"
        parts = line_clean.split('|')
        post_info = parts[0].strip()

        # 如果包含路径分隔符，取最后一部分
        if '/' in post_info:
            post_name = post_info.split('/')[-1].strip()
        else:
            post_name = post_info

        def on_hover(e):
            e.control.bgcolor = ft.Colors.BLUE_100 if e.data == "true" else ft.Colors.BLUE_50
            e.control.update()

        def on_click(e):
            print(f"Clicking post: '{post_name}' from line: '{line}'")  # 调试信息
            self.show_post_preview(post_name)

        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.DESCRIPTION, size=22,
                        color=ft.Colors.BLUE_400),
                ft.Text(line.strip()[:80], size=13),
            ], spacing=12),
            padding=12,
            border=ft.Border.all(1, ft.Colors.BLUE_100),
            border_radius=8,
            bgcolor=ft.Colors.BLUE_50,
            on_hover=on_hover,
            on_click=on_click,
            animate=200,
            tooltip="点击查看详情",
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
        # 从列表中提取文章名，处理多种格式
        line_clean = line.replace('Post:', '').strip()
        parts = line_clean.split('|')
        post_info = parts[0].strip()

        # 如果包含路径分隔符，取最后一部分
        if '/' in post_info:
            post_name = post_info.split('/')[-1].strip()
        else:
            post_name = post_info

        def on_hover(e):
            if e.data == "true":
                e.control.bgcolor = ft.Colors.BLUE_100
                e.control.shadow = ft.BoxShadow(
                    blur_radius=20, color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK))
            else:
                e.control.bgcolor = ft.Colors.BLUE_50
                e.control.shadow = None
            e.control.update()

        def on_click(e):
            print(f"Clicking post: '{post_name}' from line: '{line}'")  # 调试信息
            self.show_post_preview(post_name)

        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ARTICLE, size=26, color=ft.Colors.BLUE_600),
                ft.Text(line.strip(), size=14, expand=True),
            ], spacing=15),
            padding=18,
            border=ft.Border.all(1, ft.Colors.BLUE_200),
            border_radius=10,
            bgcolor=ft.Colors.BLUE_50,
            on_hover=on_hover,
            on_click=on_click,
            animate=200,
            tooltip="点击查看详情",
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

        def on_hover(e):
            if e.data == "true":
                e.control.bgcolor = ft.Colors.ORANGE_100
                e.control.shadow = ft.BoxShadow(
                    blur_radius=20, color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK))
            else:
                e.control.bgcolor = ft.Colors.ORANGE_50
                e.control.shadow = None
            e.control.update()

        def on_click(e):
            self.show_collection_preview(name)

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
            border=ft.Border.all(1, ft.Colors.ORANGE_200),
            border_radius=12,
            bgcolor=ft.Colors.ORANGE_50,
            on_hover=on_hover,
            on_click=on_click,
            animate=200,
            tooltip="点击查看合集内容",
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

    def exec_build(self, e):
        """构建项目"""
        # 显示加载提示
        progress_dlg = ft.AlertDialog(
            title=ft.Text("正在构建项目..."),
            content=ft.Column([
                ft.ProgressRing(),
                ft.Container(height=10),
                ft.Text("请稍候，这可能需要几分钟时间", size=13, color=ft.Colors.GREY_700),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
            modal=True,
        )
        self.page.overlay.append(progress_dlg)
        progress_dlg.open = True
        self.page.update()

        # 在后台线程中执行构建
        import threading

        def build_thread():
            try:
                result = self.commands['Build']().execute()
                # 关闭进度对话框
                progress_dlg.open = False
                self.page.update()
                # 显示成功消息
                self.snack(self.t('operation_success'))
                print(result)  # 输出构建日志到控制台
            except Exception as ex:
                # 关闭进度对话框
                progress_dlg.open = False
                self.page.update()
                # 显示错误消息
                self.snack(f"{self.t('error')}: {ex}", True)

        threading.Thread(target=build_thread, daemon=True).start()

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

    def show_post_preview(self, post_name):
        """显示文章预览"""
        try:
            from mainTools.path_utils import get_posts_path
            import os

            # 确保 post_name 不包含 .md 后缀
            if post_name.endswith('.md'):
                post_name = post_name[:-3]

            print(f"Searching for post: '{post_name}'")  # 调试

            # 查找文章文件
            posts_path = get_posts_path()
            file_path = None

            # 在 Markdowns 目录中查找
            markdowns_path = os.path.join(
                posts_path, 'Markdowns', f'{post_name}.md')
            print(f"Checking: {markdowns_path}")  # 调试
            if os.path.exists(markdowns_path):
                file_path = markdowns_path
                print(f"Found in Markdowns")  # 调试
            else:
                # 在合集目录中查找
                print(f"Searching in collections...")  # 调试
                for item in os.listdir(posts_path):
                    item_path = os.path.join(posts_path, item)
                    if os.path.isdir(item_path) and item not in ['Markdowns', 'Images']:
                        post_path = os.path.join(item_path, f'{post_name}.md')
                        print(f"Checking: {post_path}")  # 调试
                        if os.path.exists(post_path):
                            file_path = post_path
                            print(f"Found in collection: {item}")  # 调试
                            break

            if not file_path:
                print(f"Post not found: '{post_name}'")  # 调试
                self.snack(f"未找到文章: {post_name}", True)
                return

            # 读取文章内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析元数据
            from mainTools.utility import parse_markdown_metadata
            metadata = parse_markdown_metadata(file_path)

            # 构建预览内容
            preview_items = [
                ft.Row([
                    ft.Icon(ft.Icons.TITLE, size=20, color=ft.Colors.BLUE_600),
                    ft.Text(metadata.get('title', post_name),
                            size=18, weight=ft.FontWeight.BOLD),
                ], spacing=10),
            ]

            if metadata.get('date'):
                preview_items.append(ft.Row([
                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=16,
                            color=ft.Colors.GREY_600),
                    ft.Text(f"日期: {metadata['date']}",
                            size=13, color=ft.Colors.GREY_700),
                ], spacing=8))

            if metadata.get('tags'):
                tags = metadata['tags'] if isinstance(
                    metadata['tags'], list) else [metadata['tags']]
                preview_items.append(ft.Row([
                    ft.Icon(ft.Icons.TAG, size=16, color=ft.Colors.GREY_600),
                    ft.Text(f"标签: {', '.join(tags)}", size=13,
                            color=ft.Colors.GREY_700),
                ], spacing=8))

            if metadata.get('categories'):
                cats = metadata['categories'] if isinstance(metadata['categories'], list) else [
                    metadata['categories']]
                preview_items.append(ft.Row([
                    ft.Icon(ft.Icons.CATEGORY, size=16,
                            color=ft.Colors.GREY_600),
                    ft.Text(f"分类: {', '.join(cats)}", size=13,
                            color=ft.Colors.GREY_700),
                ], spacing=8))

            if metadata.get('pre'):
                preview_items.append(ft.Container(height=10))
                preview_items.append(
                    ft.Text("简介:", size=14, weight=ft.FontWeight.BOLD))
                preview_items.append(ft.Container(
                    content=ft.Text(
                        metadata['pre'], size=13, color=ft.Colors.GREY_800),
                    padding=10,
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=8,
                ))

            # 显示内容预览（前500字符）
            body = content.split('---', 2)[-1].strip()[:500]
            if body:
                preview_items.append(ft.Container(height=10))
                preview_items.append(
                    ft.Text("内容预览:", size=14, weight=ft.FontWeight.BOLD))
                preview_items.append(ft.Container(
                    content=ft.Text(body + "...", size=12,
                                    color=ft.Colors.GREY_800),
                    padding=10,
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=8,
                    height=150,
                ))

            dlg = ft.AlertDialog(
                title=ft.Text(f"📄 {post_name}"),
                content=ft.Container(
                    content=ft.Column(preview_items, spacing=8,
                                      scroll=ft.ScrollMode.AUTO),
                    width=600,
                    height=400,
                ),
                actions=[
                    ft.TextButton(
                        "关闭", on_click=lambda e: self.close_dlg(dlg)),
                ],
            )
            self.page.overlay.append(dlg)
            dlg.open = True
            self.page.update()

        except Exception as e:
            self.snack(f"预览失败: {e}", True)

    def show_collection_preview(self, collection_name):
        """显示合集预览"""
        try:
            from mainTools.path_utils import get_posts_path
            import os

            posts_path = get_posts_path()
            collection_path = os.path.join(posts_path, collection_name)

            if not os.path.exists(collection_path):
                self.snack(f"未找到合集: {collection_name}", True)
                return

            # 获取合集中的文章
            posts = []
            for file in os.listdir(collection_path):
                if file.endswith('.md'):
                    post_name = file[:-3]
                    file_path = os.path.join(collection_path, file)

                    try:
                        from mainTools.utility import parse_markdown_metadata
                        metadata = parse_markdown_metadata(file_path)
                        posts.append({
                            'name': post_name,
                            'title': metadata.get('title', post_name),
                            'date': metadata.get('date', ''),
                            'pre': metadata.get('pre', '')[:100] + '...' if metadata.get('pre') else ''
                        })
                    except:
                        posts.append({
                            'name': post_name,
                            'title': post_name,
                            'date': '',
                            'pre': ''
                        })

            # 构建预览内容
            preview_items = [
                ft.Text(f"合集共有 {len(posts)} 篇文章", size=16,
                        color=ft.Colors.GREY_700),
                ft.Divider(),
            ]

            for post in posts:
                post_item = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.ARTICLE, size=20,
                                    color=ft.Colors.ORANGE_600),
                            ft.Text(post['title'], size=15,
                                    weight=ft.FontWeight.BOLD),
                        ], spacing=10),
                        ft.Text(
                            post['date'], size=12, color=ft.Colors.GREY_600) if post['date'] else ft.Container(),
                        ft.Text(
                            post['pre'], size=12, color=ft.Colors.GREY_700) if post['pre'] else ft.Container(),
                    ], spacing=4),
                    padding=12,
                    bgcolor=ft.Colors.ORANGE_50,
                    border_radius=8,
                    border=ft.Border.all(1, ft.Colors.ORANGE_200),
                    on_click=lambda e, name=post['name']: self.show_post_preview(
                        name),
                    tooltip="点击查看详情",
                )
                preview_items.append(post_item)

            dlg = ft.AlertDialog(
                title=ft.Text(f"📁 {collection_name}"),
                content=ft.Container(
                    content=ft.Column(preview_items, spacing=10,
                                      scroll=ft.ScrollMode.AUTO),
                    width=600,
                    height=400,
                ),
                actions=[
                    ft.TextButton(
                        "关闭", on_click=lambda e: self.close_dlg(dlg)),
                ],
            )
            self.page.overlay.append(dlg)
            dlg.open = True
            self.page.update()

        except Exception as e:
            self.snack(f"预览失败: {e}", True)

    def build_settings_view(self):
        """配置管理视图"""
        config_fields = {}
        list_fields = {}
        links_data = []

        # 加载当前配置
        try:
            from mainTools.commands import GetConfig
            get_config_cmd = GetConfig()
            config_result = get_config_cmd.execute()
            current_config = json.loads(config_result)
        except Exception as e:
            self.snack(f"加载配置失败: {e}", True)
            current_config = {}

        # 创建配置表单
        form_rows = []

        # 基本配置
        form_rows.append(ft.Text(self.t('settings'),
                         size=24, weight=ft.FontWeight.BOLD))

        config_items = [
            ('BlogName', self.t('blog_name'), 'text'),
            ('ShortDesc', self.t('short_desc'), 'text'),
            ('Name', self.t('author_name'), 'text'),
            ('Description', self.t('author_desc'), 'text'),
            ('ProjectUrl', self.t('project_url'), 'text'),
            ('BackgroundImg', self.t('background_img'), 'text'),
            ('BackgroundImgOpacity', self.t('bg_opacity'), 'number'),
            ('BackgroundImgBlur', self.t('bg_blur'), 'number'),
            ('HeadImg', self.t('head_img'), 'text'),
            ('PostsPerPage', self.t('posts_per_page'), 'number'),
            ('theme', self.t('theme'), 'text'),
            ('ChangeInfoAndTipPosition', self.t('change_info_tip_pos'), 'bool'),
        ]

        for key, label, field_type in config_items:
            value = current_config.get(key, '')

            if field_type == 'text':
                field = ft.TextField(
                    label=label,
                    value=str(value),
                    width=500,
                )
            elif field_type == 'number':
                field = ft.TextField(
                    label=label,
                    value=str(value),
                    width=200,
                    keyboard_type=ft.KeyboardType.NUMBER,
                )
            elif field_type == 'bool':
                field = ft.Checkbox(
                    label=label,
                    value=bool(value),
                )

            config_fields[key] = field
            form_rows.append(ft.Container(content=field, padding=5))

        # 列表配置
        form_rows.append(ft.Divider())
        form_rows.append(ft.Text(self.t('lists_config'),
                         size=20, weight=ft.FontWeight.BOLD))

        list_items = [
            ('InfoListUp', self.t('info_list_up')),
            ('InfoListDown', self.t('info_list_down')),
            ('TipListUp', self.t('tip_list_up')),
            ('TipListDown', self.t('tip_list_down')),
            ('MainListUp', self.t('main_list_up')),
            ('MainListDown', self.t('main_list_down')),
            ('InfoListFloat', self.t('info_list_float')),
            ('TipListFloat', self.t('tip_list_float')),
        ]

        for key, label in list_items:
            items = current_config.get(key, [])
            field = ft.TextField(
                label=label,
                value=', '.join(items) if items else '',
                width=500,
                hint_text="用逗号分隔多个项，例如: SelfIntroductionPanel, CollectionPanel",
                multiline=False,
            )
            list_fields[key] = field
            form_rows.append(ft.Container(content=field, padding=5))

        # 社交链接配置
        form_rows.append(ft.Divider())
        form_rows.append(ft.Text(self.t('social_links'),
                         size=20, weight=ft.FontWeight.BOLD))

        links = current_config.get('Links', [])
        links_container = ft.Column(spacing=10)

        def build_link_row(link_data, index):
            """构建单个链接编辑行"""
            name_field = ft.TextField(
                label=self.t('link_name'),
                value=link_data.get('name', ''),
                width=200,
            )
            url_field = ft.TextField(
                label=self.t('link_url'),
                value=link_data.get('url', ''),
                width=350,
            )

            def remove_link(e):
                links_data[index] = None
                update_links_ui()

            remove_btn = ft.IconButton(
                icon=ft.Icons.DELETE,
                icon_color=ft.Colors.RED_400,
                on_click=remove_link,
            )

            links_data.append({'name': name_field, 'url': url_field})

            return ft.Row([
                name_field,
                url_field,
                remove_btn,
            ], spacing=10)

        def update_links_ui():
            """更新链接界面"""
            links_container.controls.clear()
            for i, link in enumerate(links):
                if i < len(links_data) and links_data[i] is not None:
                    links_container.controls.append(build_link_row(link, i))
            self.page.update()

        # 初始化链接
        for i, link in enumerate(links):
            links_container.controls.append(build_link_row(link, i))

        def add_link(e):
            """添加新链接"""
            links.append({'name': '', 'url': ''})
            links_container.controls.append(build_link_row(
                {'name': '', 'url': ''}, len(links) - 1))
            self.page.update()

        add_link_btn = ft.ElevatedButton(
            self.t('add_link'),
            icon=ft.Icons.ADD,
            on_click=add_link,
        )

        form_rows.append(ft.Container(content=links_container, padding=10))
        form_rows.append(ft.Container(content=add_link_btn, padding=5))

        def save_config(e):
            """保存配置"""
            try:
                # 收集基本配置值
                config_updates = {}
                for key, field in config_fields.items():
                    if isinstance(field, ft.Checkbox):
                        config_updates[key] = field.value
                    else:
                        value = field.value
                        # 尝试转换为正确的类型
                        if key in ['BackgroundImgOpacity', 'BackgroundImgBlur']:
                            value = float(value) if value else 0.0
                        elif key in ['PostsPerPage']:
                            value = int(value) if value else 10
                        config_updates[key] = value

                # 收集列表配置
                for key, field in list_fields.items():
                    value = field.value.strip()
                    if value:
                        items = [item.strip()
                                 for item in value.split(',') if item.strip()]
                        config_updates[key] = items
                    else:
                        config_updates[key] = []

                # 收集链接配置
                valid_links = []
                for link_data in links_data:
                    if link_data is not None:
                        name = link_data['name'].value.strip()
                        url = link_data['url'].value.strip()
                        if name and url:
                            valid_links.append({'name': name, 'url': url})
                config_updates['Links'] = valid_links

                # 执行更新命令
                from mainTools.commands import UpdateConfig
                update_cmd = UpdateConfig()
                result = update_cmd.execute(**config_updates)
                self.snack(result, False)

            except Exception as ex:
                self.snack(f"保存失败: {ex}", True)
                import traceback
                traceback.print_exc()

        save_btn = ft.ElevatedButton(
            self.t('save_config'),
            icon=ft.Icons.SAVE,
            on_click=save_config,
        )

        form_rows.append(ft.Divider())
        form_rows.append(ft.Container(content=save_btn, padding=10))

        return ft.Container(
            content=ft.Column(
                form_rows,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
            padding=20,
        )

    def show_github_dialog(self, e):
        """显示GitHub部署配置对话框"""
        from mainTools.github_commands import LoadGitHubConfig

        # 加载已保存的配置
        load_cmd = LoadGitHubConfig()
        saved_config = load_cmd.execute()

        # 创建多步骤对话框
        current_step = [1]  # 当前步骤

        # Step 1: Token配置
        token_field = ft.TextField(
            label=self.t('github_token'),
            value=saved_config.get('token', ''),
            password=True,
            can_reveal_password=True,
            width=500
        )

        token_status = ft.Text("", size=12)
        verify_btn = ft.Button(
            self.t('verify_token'),
            icon=ft.Icons.VERIFIED_USER,
            on_click=lambda e: self.verify_github_token(
                token_field, token_status)
        )

        step1_content = ft.Column([
            ft.Text(self.t('token_permissions'),
                    size=16, weight=ft.FontWeight.BOLD),
            ft.Text(self.t('token_perm_desc'), size=12),
            ft.Container(height=10),
            ft.Button(
                "打开Token页面",
                icon=ft.Icons.TOKEN,
                on_click=lambda e: webbrowser.open(
                    'https://github.com/settings/tokens/new')
            ),
            ft.Container(height=20),
            token_field,
            ft.Row([verify_btn, token_status], spacing=10),
        ], tight=True, spacing=15)

        # Step 2: 仓库名称
        repo_field = ft.TextField(
            label=self.t('github_repo'),
            value=saved_config.get('repo_name', ''),
            hint_text='my-blog',
            width=500
        )

        step2_content = ft.Column([
            ft.Text(self.t('github_repo'), size=16, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            repo_field,
            ft.Text('如果仓库不存在，将自动创建', size=12, color=ft.Colors.GREY_600),
        ], tight=True, spacing=15)

        # 创建对话框容器
        dialog_content = ft.Container(
            content=step1_content, width=550, height=350)

        def update_dialog_content():
            """更新对话框内容"""
            if current_step[0] == 1:
                dialog_content.content = step1_content
                next_btn.text = self.t('next_step')
                prev_btn.visible = False
            else:
                dialog_content.content = step2_content
                next_btn.text = self.t('start_deploy')
                prev_btn.visible = True
            self.page.update()

        def next_step(e):
            """下一步或开始部署"""
            if current_step[0] == 1:
                # 验证 token
                token = token_field.value.strip()
                if not token:
                    self.snack('请输入 GitHub Token', True)
                    return

                # 验证 token 有效性
                from mainTools.github_commands import VerifyGitHubToken
                verify_cmd = VerifyGitHubToken()
                result = verify_cmd.execute(token)

                if not result['success']:
                    self.snack(result['message'], True)
                    return

                # 进入下一步
                current_step[0] = 2
                update_dialog_content()
            else:
                # 开始部署
                token = token_field.value.strip()
                repo = repo_field.value.strip()

                if not repo:
                    self.snack('请输入仓库名称', True)
                    return

                # 保存配置
                from mainTools.github_commands import SaveGitHubConfig
                save_cmd = SaveGitHubConfig()
                save_cmd.execute(token, repo)

                # 关闭配置对话框
                self.close_dlg(dlg)

                # 开始部署
                self.start_github_deploy(token, repo)

        def prev_step(e):
            """上一步"""
            current_step[0] = 1
            update_dialog_content()

        prev_btn = ft.TextButton(
            self.t('previous_step'), on_click=prev_step, visible=False)
        next_btn = ft.Button(self.t('next_step'), on_click=next_step)

        dlg = ft.AlertDialog(
            title=ft.Text(self.t('deploy_github')),
            content=dialog_content,
            actions=[
                ft.TextButton(self.t('cancel'),
                              on_click=lambda e: self.close_dlg(dlg)),
                prev_btn,
                next_btn,
            ],
        )

        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def verify_github_token(self, token_field, status_text):
        """验证GitHub Token"""
        token = token_field.value.strip()
        if not token:
            status_text.value = "❌ 请输入Token"
            status_text.color = ft.Colors.RED
            self.page.update()
            return

        from mainTools.github_commands import VerifyGitHubToken
        verify_cmd = VerifyGitHubToken()
        result = verify_cmd.execute(token)

        if result['success']:
            status_text.value = f"✅ {result['message']}"
            status_text.color = ft.Colors.GREEN
        else:
            status_text.value = f"❌ {result['message']}"
            status_text.color = ft.Colors.RED

        self.page.update()

    def start_github_deploy(self, token, repo_name):
        """开始GitHub部署"""
        # 创建进度对话框
        progress_text = ft.Text("正在准备部署...", size=14)
        progress_bar = ft.ProgressBar(value=0, width=500)
        progress_percent = ft.Text("0%", size=12, color=ft.Colors.GREY_600)

        progress_dlg = ft.AlertDialog(
            title=ft.Text(self.t('deploying')),
            content=ft.Column([
                progress_text,
                progress_bar,
                progress_percent,
                ft.Container(height=10),
                ft.Text("这可能需要几分钟，请耐心等待...", size=12,
                        color=ft.Colors.GREY_600),
            ], tight=True, spacing=10, width=500),
            modal=True,
        )

        self.page.overlay.append(progress_dlg)
        progress_dlg.open = True
        self.page.update()

        def update_progress(message, percent):
            """更新进度 - 线程安全的UI更新"""
            progress_text.value = message
            progress_bar.value = percent / 100
            progress_percent.value = f"{int(percent)}%"
            # 直接调用update()更新页面
            try:
                self.page.update()
            except Exception as e:
                print(f"进度更新异常: {e}")

        def deploy_thread():
            """部署线程"""
            try:
                from mainTools.github_commands import FullDeploy
                deploy_cmd = FullDeploy()
                result = deploy_cmd.execute(token, repo_name, update_progress)

                # 在主线程中关闭进度对话框
                import time
                time.sleep(0.1)  # 给UI线程一些时间
                progress_dlg.open = False
                self.page.update()

                if result['success']:
                    # 显示成功对话框
                    success_dlg = ft.AlertDialog(
                        title=ft.Text(self.t('deploy_success'),
                                      color=ft.Colors.GREEN),
                        content=ft.Column([
                            ft.Text(result['message']),
                            ft.Container(height=10),
                            ft.Row([
                                ft.Button(
                                    "查看仓库",
                                    icon=ft.Icons.OPEN_IN_NEW,
                                    on_click=lambda e: webbrowser.open(
                                        result.get('repo_url', ''))
                                ) if result.get('repo_url') else ft.Container(),
                                ft.Button(
                                    "查看Pages",
                                    icon=ft.Icons.LAUNCH,
                                    on_click=lambda e: webbrowser.open(
                                        result.get('pages_url', ''))
                                ) if result.get('pages_url') else ft.Container(),
                            ], spacing=10),
                        ], tight=True),
                        actions=[
                            ft.TextButton(
                                '确定', on_click=lambda e: self.close_dlg(success_dlg))
                        ],
                    )
                    self.page.overlay.append(success_dlg)
                    success_dlg.open = True
                    self.page.update()
                else:
                    self.snack(result['message'], True)

            except Exception as e:
                import time
                time.sleep(0.1)
                progress_dlg.open = False
                self.page.update()
                self.snack(f"部署失败: {str(e)}", True)
                import traceback
                traceback.print_exc()

        # 在后台线程执行部署
        import threading
        threading.Thread(target=deploy_thread, daemon=True).start()


def main(page: ft.Page):
    BlogManagerGUI(page)


if __name__ == '__main__':
    ft.run(main)
