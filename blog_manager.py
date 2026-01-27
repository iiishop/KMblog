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
        self.expanded_collections = set()  # 记录展开的合集
        self.draggable_data_map = {}  # 映射 Draggable ID 到文章数据
        self.needs_generate = False  # 标记是否需要重新生成配置
        self.generate_timer = None  # 延迟生成的定时器

        # 数据缓存层
        self.posts_cache = {}  # 缓存文章数据
        self.is_cache_valid = False  # 缓存是否有效
        self.collection_widgets = {}  # 存储合集控件引用，用于增量更新

        # 延迟刷新定时器
        self.ui_refresh_timer = None  # UI刷新定时器
        self.pending_refresh = False  # 标记是否有待处理的UI刷新

        # 编辑器状态
        self.editor_running = False  # 编辑器是否正在运行
        self.editor_url = None  # 编辑器URL
        self.dev_server_process = None  # 开发服务器进程
        self.editor_server = None  # 后端服务器进程

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
                'crypto_tag': '加密标签',
                'crypto_password': '加密密码',
                'crypto_config': '加密配置',
                'migrate_hexo': '从Hexo迁移',
                'migrate_title': 'Hexo 文章迁移',
                'migrate_desc': '自动将 Hexo 格式的文章转换为 KMBlog 格式\n\n变化内容：\n• tags 和 categories 改为换行列表格式\n• 添加 pre（文章简介）和 img（文章封面）字段\n\n字段说明：\n• pre: 文章简介，会显示在文章列表中\n• img: 文章封面图片名称（放在 /public/Posts/Images 目录中）',
                'migrate_confirm': '确认迁移',
                'migrating': '正在迁移...',
                'migrate_success': '迁移成功',
                'migrate_failed': '迁移失败',
                'migrate_complete': '迁移完成',
                'migrate_start': '开始迁移',
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
                'crypto_tag': 'Crypto Tag',
                'crypto_password': 'Crypto Password',
                'crypto_config': 'Crypto Config',
                'migrate_hexo': 'Migrate from Hexo',
                'migrate_title': 'Migrate from Hexo',
                'migrate_desc': 'Automatically convert Hexo format posts to KMBlog format\n\nChanges:\n• tags and categories converted to line-separated list format\n• Added pre (post preview) and img (post cover) fields\n\nField descriptions:\n• pre: Post preview, displayed in post list\n• img: Post cover image name (place in /public/Posts/Images directory)',
                'migrate_confirm': 'Confirm Migration',
                'migrating': 'Migrating...',
                'migrate_success': 'Migration Success',
                'migrate_failed': 'Migration Failed',
                'migrate_complete': 'Migration Complete',
                'migrate_start': 'Start Migration',
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
        import time
        print(f"[性能-时间戳] 开始build_ui: {time.time():.3f}")

        self.page.controls.clear()
        layout = ft.Row([
            self.build_sidebar(),
            ft.VerticalDivider(width=1, color=ft.Colors.GREY_300),
            ft.Container(content=self.get_current_view(),
                         expand=True, padding=30),
        ], spacing=0, expand=True)
        self.page.add(layout)
        self.page.update()
        print(f"[性能-时间戳] UI更新完成: {time.time():.3f}")

    def build_sidebar(self):
        """侧边栏"""
        nav_items = [
            ('dashboard', ft.Icons.DASHBOARD, self.t('dashboard')),
            ('posts', ft.Icons.ARTICLE, self.t('posts')),
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

        # 构建快速操作区域 - 扁平化网格设计
        action_buttons = [
            self.action_btn(self.t('add_post'), ft.Icons.ADD_CIRCLE,
                            self.show_add_dialog, ft.Colors.GREEN_600, '新建文章'),
            self.action_btn(self.t('generate'), ft.Icons.BUILD_CIRCLE,
                            self.exec_generate, ft.Colors.BLUE_600, '生成配置'),
            self.action_btn(self.t('build_project'), ft.Icons.CONSTRUCTION,
                            self.exec_build, ft.Colors.ORANGE_600, '构建项目'),
            self.action_btn(self.t('deploy_github'), ft.Icons.CLOUD_UPLOAD,
                            self.show_github_dialog, ft.Colors.INDIGO_600, '部署到GitHub'),
            self.action_btn(self.t('migrate_hexo'), ft.Icons.TRANSFORM,
                            self.show_migrate_dialog, ft.Colors.TEAL_600, 'Hexo迁移'),
        ]

        # 编辑器按钮 - 根据状态显示不同的按钮
        if self.editor_running:
            action_buttons.append(
                self.action_btn('打开编辑器', ft.Icons.OPEN_IN_BROWSER,
                                self.open_editor_window, ft.Colors.PURPLE_600, '打开已运行的编辑器')
            )
            action_buttons.append(
                self.action_btn('关闭编辑器', ft.Icons.STOP_CIRCLE,
                                self.stop_editor, ft.Colors.RED_600, '停止编辑器服务')
            )
        else:
            action_buttons.append(
                self.action_btn('启动编辑器', ft.Icons.EDIT,
                                self.start_editor, ft.Colors.PURPLE_600, '本地Markdown编辑器')
            )

        if not self.is_blog_initialized():
            action_buttons.append(
                self.action_btn(self.t('init_blog'), ft.Icons.ROCKET_LAUNCH,
                                self.exec_init, ft.Colors.PURPLE_600, '初始化')
            )

        actions_content = ft.Column([
            ft.Text(self.t('quick_actions'), size=22,
                    weight=ft.FontWeight.BOLD),
            ft.Container(height=15),
            ft.Row(action_buttons, spacing=20, run_spacing=20, wrap=True),
        ])

        actions = ft.Container(
            content=actions_content,
            padding=30,
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

    def action_btn(self, text, icon, onclick, color, desc=""):
        """操作按钮 - 改进版"""
        def on_hover(e):
            if e.data == "true":
                e.control.shadow = ft.BoxShadow(
                    blur_radius=20, spread_radius=2,
                    color=ft.Colors.with_opacity(0.4, color))
                e.control.scale = 1.02
            else:
                e.control.shadow = ft.BoxShadow(
                    blur_radius=10, color=ft.Colors.with_opacity(0.2, color))
                e.control.scale = 1.0
            e.control.update()

        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=36, color=ft.Colors.WHITE),
                ft.Text(text, size=14, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
                ft.Text(desc, size=11, color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                        text_align=ft.TextAlign.CENTER) if desc else ft.Container(height=0),
            ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=160,
            height=120,
            padding=15,
            bgcolor=color,
            border_radius=12,
            shadow=ft.BoxShadow(
                blur_radius=10, color=ft.Colors.with_opacity(0.2, color)),
            on_hover=on_hover,
            on_click=onclick,
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
        """文章视图 - 合集包裹式"""
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
                    ft.Button(self.t('refresh'), icon=ft.Icons.REFRESH, on_click=lambda e: self.force_refresh(
                    ), bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE),
                ], spacing=12),
            ]),
            padding=25,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(
                blur_radius=15, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        )

        return ft.Column([header, ft.Container(height=20), self.build_collection_groups()], scroll=ft.ScrollMode.AUTO, expand=True)

    def update_draggable_map(self, control=None):
        """递归更新 Draggable 控件的 ID 映射"""
        if control is None:
            control = self.page

        # 检查控件类型
        if isinstance(control, ft.Draggable) and hasattr(control, 'data'):
            # 获取控件的真实 ID
            if hasattr(control, 'uid'):
                real_id = control.uid
            elif hasattr(control, '_Control__uid'):
                real_id = control._Control__uid
            else:
                real_id = id(control)

            # 如果有数据，存储映射
            if control.data:
                self.draggable_data_map[real_id] = control.data
                print(
                    f"[Drag] Mapped Draggable ID {real_id} -> {control.data}")

        # 递归处理子控件
        if hasattr(control, 'content'):
            if isinstance(control.content, list):
                for child in control.content:
                    self.update_draggable_map(child)
            elif control.content is not None:
                self.update_draggable_map(control.content)

        if hasattr(control, 'controls'):
            for child in control.controls:
                self.update_draggable_map(child)

    def build_collection_groups(self):
        """构建合集分组列表"""
        import time
        start_time = time.time()

        try:
            # 清空映射表和控件引用
            self.draggable_data_map.clear()
            self.collection_widgets.clear()

            # 获取所有文章数据（使用缓存）
            posts_data = self.get_posts_grouped_by_collection()

            collection_widgets = []

            # 首先显示 Markdowns (无合集) 的文章
            if 'Markdowns' in posts_data and posts_data['Markdowns']:
                collection_widgets.append(
                    self.build_collection_group(
                        '📄 无合集', 'Markdowns', posts_data['Markdowns'], is_default=True)
                )

            # 然后显示其他合集
            for coll_name in sorted(posts_data.keys()):
                if coll_name != 'Markdowns' and posts_data[coll_name]:
                    collection_widgets.append(
                        self.build_collection_group(
                            f'📁 {coll_name}', coll_name, posts_data[coll_name])
                    )

            if not collection_widgets:
                return ft.Container(
                    content=ft.Text(self.t('no_posts'), size=18,
                                    color=ft.Colors.GREY_500),
                    padding=25,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                )

            container = ft.Container(
                content=ft.Column(collection_widgets, spacing=15),
                padding=25,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                shadow=ft.BoxShadow(
                    blur_radius=15, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
            )

            elapsed = time.time() - start_time
            print(
                f"[性能] 构建合集列表耗时: {elapsed:.3f}秒 ({len(collection_widgets)}个合集)")
            print(f"[性能-时间戳] 构建完成时刻: {time.time():.3f}")
            return container
        except Exception as e:
            print(f"Error building collection groups: {e}")
            import traceback
            traceback.print_exc()
            return ft.Container(content=ft.Text(f"Error: {e}", color=ft.Colors.RED_500))

    def get_posts_grouped_by_collection(self, force_refresh=False):
        """获取按合集分组的文章数据（带缓存）"""
        import time

        print(f"[性能-时间戳] 开始获取posts数据: {time.time():.3f}")

        # 如果缓存有效且不强制刷新，直接返回缓存
        if not force_refresh and self.is_cache_valid:
            print("[Cache] Using cached posts data")
            return self.posts_cache

        start_time = time.time()
        result = self.commands['ListAllPosts']().execute()
        lines = result.split('\n')

        grouped_posts = {}
        current_collection = 'Markdowns'

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('Collection:'):
                # 解析合集名称
                parts = line.split('|')
                current_collection = parts[0].replace(
                    'Collection:', '').strip()
                grouped_posts[current_collection] = []
            elif line.startswith('Post:'):
                # 解析文章信息
                if current_collection not in grouped_posts:
                    grouped_posts[current_collection] = []
                grouped_posts[current_collection].append(line)

        # 缓存数据
        self.posts_cache = grouped_posts
        self.is_cache_valid = True

        elapsed = time.time() - start_time
        print(f"[性能] 获取文章数据耗时: {elapsed:.3f}秒")
        return grouped_posts

    def build_collection_group(self, display_name, collection_name, posts, is_default=False):
        """构建单个合集组"""
        is_expanded = collection_name in self.expanded_collections

        # 合集头部
        def toggle_expand(e):
            if is_expanded:
                self.expanded_collections.discard(collection_name)
            else:
                self.expanded_collections.add(collection_name)
            self.build_ui()

        # 删除合集按钮 (仅非默认合集)
        delete_button = None
        if not is_default:
            def on_delete_collection(e):
                self.confirm(
                    self.t('confirm_delete'),
                    self.t('confirm_delete_collection').format(
                        collection_name),
                    lambda: self.do_del_coll(collection_name)
                )
            delete_button = ft.IconButton(
                icon=ft.Icons.DELETE,
                icon_color=ft.Colors.RED_500,
                tooltip=self.t('delete_collection'),
                on_click=on_delete_collection,
            )

        # 拖放接收处理
        def on_drag_accept(e):
            print(f"[Drag] on_drag_accept triggered")
            print(f"[Drag] src_id: {e.src_id}")

            # 尝试直接从事件获取源控件
            src_control = None
            if hasattr(e, 'src') and e.src:
                src_control = e.src
                print(f"[Drag] Found src control: {type(src_control)}")

            # 如果找到源控件且有数据
            if src_control and hasattr(src_control, 'data') and src_control.data:
                data = src_control.data
                print(f"[Drag] Got data from src control: {data}")

                post_name = data.get('post_name')
                source_collection = data.get('source_collection')
                print(
                    f"[Drag] Moving {post_name} from {source_collection} to {collection_name}")

                try:
                    # 移动文章
                    self.move_post_to_collection(
                        post_name, source_collection, collection_name)
                except Exception as ex:
                    print(f"[Drag] Error in move_post_to_collection: {ex}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"[Drag] Warning: Could not get data from src control")

        # 拖放悬停效果
        def on_will_accept(e):
            import time
            print(f"[性能-时间戳] 拖拽开始(on_will_accept): {time.time():.3f}")
            print(f"[Drag] on_will_accept: entering {collection_name}")
            e.control.bgcolor = ft.Colors.BLUE_100
            e.control.border = ft.Border.all(2, ft.Colors.BLUE_500)
            e.control.update()

        def on_leave(e):
            print(f"[Drag] on_leave: leaving {collection_name}")
            e.control.bgcolor = ft.Colors.BLUE_GREY_50 if not is_default else ft.Colors.GREY_100
            e.control.border = None
            e.control.update()

        # 构建头部容器
        header_container = ft.Container(
            content=ft.Row([
                ft.Icon(
                    ft.Icons.EXPAND_MORE if is_expanded else ft.Icons.CHEVRON_RIGHT,
                    size=24,
                    color=ft.Colors.GREY_700
                ),
                ft.Text(
                    f"{display_name} ({len(posts)})",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_900,
                    expand=True
                ),
                delete_button if delete_button else ft.Container(),
            ], spacing=10),
            padding=ft.Padding(12, 8, 12, 8),
            bgcolor=ft.Colors.BLUE_GREY_50 if not is_default else ft.Colors.GREY_100,
            border_radius=8,
            on_click=toggle_expand,
            ink=True,
        )

        # 将头部包装在 DragTarget 中
        header = ft.DragTarget(
            group="posts",
            content=header_container,
            on_accept=on_drag_accept,
            on_will_accept=on_will_accept,
            on_leave=on_leave,
        )

        # 文章列表 (展开时显示)
        posts_list = None
        if is_expanded:
            post_widgets = []
            for post_line in posts:
                post_widgets.append(self.build_draggable_post(
                    post_line, collection_name))

            posts_list = ft.Container(
                content=ft.Column(post_widgets, spacing=8),
                padding=ft.Padding(35, 10, 10, 10),
            )

        return ft.Column([
            header,
            posts_list if posts_list else ft.Container(),
        ], spacing=5)

    def build_draggable_post(self, line, source_collection):
        """构建可拖拽的文章项"""
        # 从列表中提取文章名
        line_clean = line.replace('Post:', '').strip()
        parts = line_clean.split('|')
        post_info = parts[0].strip()

        # 处理文件名
        if '/' in post_info:
            post_name = post_info.split('/')[-1].strip()
        else:
            post_name = post_info

        # 移除 .md 扩展名
        if post_name.endswith('.md'):
            post_name = post_name[:-3]

        # 创建拖拽数据
        drag_data = {
            'post_name': post_name,
            'source_collection': source_collection
        }

        print(
            f"[Drag] Creating draggable: {post_name} from {source_collection}")

        def on_hover(e):
            if e.data == "true":
                e.control.bgcolor = ft.Colors.BLUE_100
                e.control.scale = 1.01
            else:
                e.control.bgcolor = ft.Colors.BLUE_50
                e.control.scale = 1.0
            e.control.update()

        def on_delete(e):
            e.stop_propagation()  # 阻止事件冒泡
            self.confirm(
                self.t('confirm_delete'),
                self.t('confirm_delete_post').format(post_name),
                lambda: self.do_del_post(
                    post_name, None if source_collection == 'Markdowns' else source_collection)
            )

        # 构建可拖拽的文章卡片
        post_card = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.DRAG_INDICATOR, size=20,
                        color=ft.Colors.GREY_400),
                ft.Icon(ft.Icons.ARTICLE, size=22, color=ft.Colors.BLUE_600),
                ft.Text(line.strip(), size=13, expand=True),
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_size=18,
                    icon_color=ft.Colors.RED_400,
                    tooltip=self.t('delete_post'),
                    on_click=on_delete,
                ),
            ], spacing=10),
            padding=12,
            border=ft.Border.all(1, ft.Colors.BLUE_200),
            border_radius=8,
            bgcolor=ft.Colors.BLUE_50,
            on_hover=on_hover,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            tooltip="拖动到合集以移动文章",
        )

        # 使用 Draggable 包装
        import json
        drag_json = json.dumps(drag_data)
        print(f"[Drag] Draggable data JSON: {drag_json}")

        draggable = ft.Draggable(
            group="posts",
            content=post_card,
            content_when_dragging=ft.Container(
                content=ft.Text("正在移动...", size=12, color=ft.Colors.GREY_400),
                padding=12,
                border=ft.Border.all(1, ft.Colors.GREY_300),
                border_radius=8,
                bgcolor=ft.Colors.GREY_50,
            ),
            content_feedback=ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.ARTICLE, size=22, color=ft.Colors.WHITE),
                    ft.Text(post_name, size=13, color=ft.Colors.WHITE),
                ], spacing=10),
                padding=12,
                bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.BLUE_700),
                border_radius=8,
                width=300,
                shadow=ft.BoxShadow(
                    blur_radius=10, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK)),
            ),
            data=drag_data,  # 直接附加数据
        )

        # 直接存储映射（使用Python对象id作为id）
        draggable_id = id(draggable)
        self.draggable_data_map[draggable_id] = drag_data

        return draggable

    def move_post_to_collection(self, post_name, source_collection, target_collection):
        """移动文章到目标合集"""
        import time
        start_time = time.time()

        try:
            from mainTools.move_post_command import MovePost
            move_cmd = MovePost()
            result = move_cmd.execute(
                post_name, source_collection, target_collection)

            if result['success']:
                print(f"[性能] 文件移动耗时: {time.time() - start_time:.3f}秒")

                # 标记需要重新生成配置（延迟执行）
                self.needs_generate = True
                self.schedule_generate()

                # 使缓存失效（下次刷新时会重新获取）
                self.is_cache_valid = False

                # 显示简短提示（不刷新UI）
                self.snack(f"✓ 已移动 {post_name} → 点击刷新按钮查看")
            else:
                self.snack(result['message'], True)
        except Exception as e:
            print(f"Move post error: {e}")
            import traceback
            traceback.print_exc()
            self.snack(f"移动失败: {e}", True)

    def force_refresh(self):
        """强制刷新（使缓存失效）"""
        print("[Cache] Force refresh - invalidating cache")
        self.is_cache_valid = False
        self.build_ui()

    def incremental_refresh_posts(self):
        """增量刷新posts视图（快速更新）"""
        import time
        start_time = time.time()
        print(f"[性能-时间戳] 开始增量刷新: {start_time:.3f}")

        if self.current_view != 'posts':
            return

        try:
            # 找到主布局中的内容容器
            layout = self.page.controls[0]
            content_container = layout.controls[2]

            # 重新构建posts视图（会使用新的缓存数据）
            new_content = self.build_posts_view()
            content_container.content = new_content

            # 只更新这个容器
            self.page.update()
            print(f"[性能-时间戳] 增量刷新UI更新完成: {time.time():.3f}")

            elapsed = time.time() - start_time
            print(f"[性能] 增量刷新UI耗时: {elapsed:.3f}秒")
        except Exception as e:
            print(f"Error in incremental refresh: {e}")
            import traceback
            traceback.print_exc()

    def schedule_ui_refresh(self):
        """延迟2秒后刷新UI（防抖，支持连续拖动）"""
        import threading

        # 取消之前的定时器
        if self.ui_refresh_timer:
            self.ui_refresh_timer.cancel()
            print("[UI刷新] 重置刷新定时器（检测到新的拖动操作）")

        # 标记有待处理的刷新
        self.pending_refresh = True

        # 设置新的定时器
        def do_refresh():
            if self.pending_refresh:
                print("[UI刷新] 执行延迟UI刷新...")
                try:
                    self.incremental_refresh_posts()
                    self.pending_refresh = False
                    print("[UI刷新] 完成")
                except Exception as e:
                    print(f"[UI刷新] 错误: {e}")

        self.ui_refresh_timer = threading.Timer(2.0, do_refresh)
        self.ui_refresh_timer.start()
        print("[UI刷新] 已调度刷新（2秒后执行）")

    def schedule_generate(self):
        """延迟2秒后执行Generate（防抖）"""
        import threading

        # 取消之前的定时器
        if self.generate_timer:
            self.generate_timer.cancel()

        # 设置新的定时器
        def do_generate():
            if self.needs_generate:
                print("[Generate] Executing delayed generate...")
                try:
                    self.commands['Generate']().execute()
                    self.needs_generate = False
                    print("[Generate] Done")
                except Exception as e:
                    print(f"[Generate] Error: {e}")

        self.generate_timer = threading.Timer(2.0, do_generate)
        self.generate_timer.start()

    def post_card(self, line):
        """文章卡片"""
        # 从列表中提取文章名，处理多种格式
        line_clean = line.replace('Post:', '').strip()
        parts = line_clean.split('|')
        post_info = parts[0].strip()

        # 如果包含路径分隔符，取最后一部分
        if '/' in post_info:
            post_name = post_info.split('/')[-1].strip()
            coll_name = post_info.split('/')[0].strip()
        else:
            post_name = post_info
            coll_name = None

        # 移除 .md 扩展名
        if post_name.endswith('.md'):
            post_name = post_name[:-3]

        print(
            f"DEBUG: post_name='{post_name}', coll_name='{coll_name}', line='{line}'")

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

        def on_delete(e):
            self.confirm(
                self.t('confirm_delete'),
                self.t('confirm_delete_post').format(post_name),
                lambda: self.do_del_post(post_name, coll_name)
            )

        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ARTICLE, size=26, color=ft.Colors.BLUE_600),
                ft.Text(line.strip(), size=14, expand=True),
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color=ft.Colors.RED_500,
                    tooltip=self.t('delete_post'),
                    on_click=on_delete,
                ),
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
                ft.Row([
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

        def on_delete(e):
            self.confirm(
                self.t('confirm_delete'),
                self.t('confirm_delete_collection').format(name),
                lambda: self.do_del_coll(name)
            )

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
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color=ft.Colors.RED_500,
                    tooltip=self.t('delete_collection'),
                    on_click=on_delete,
                ),
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
        print(f"DEBUG do_del_post: post='{post}', coll='{coll}'")
        inputs = [post, coll or '', 'y']
        idx = [0]

        def mock(p):
            v = inputs[idx[0]] if idx[0] < len(inputs) else ''
            print(f"DEBUG mock input: prompt='{p}', returning='{v}'")
            idx[0] += 1
            return v

        import builtins
        orig = builtins.input
        builtins.input = mock
        try:
            result = self.commands['DeletePost']().execute()
            print(f"DEBUG delete result: {result}")
            self.snack(self.t('operation_success'))
            self.build_ui()
        except Exception as e:
            print(f"DEBUG delete error: {e}")
            import traceback
            traceback.print_exc()
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
        print(f"DEBUG do_del_coll: coll='{coll}'")
        inputs = [coll, 'y']
        idx = [0]

        def mock(p):
            v = inputs[idx[0]] if idx[0] < len(inputs) else ''
            print(f"DEBUG mock input: prompt='{p}', returning='{v}'")
            idx[0] += 1
            return v

        import builtins
        orig_in = builtins.input
        orig_pr = builtins.print
        builtins.input = mock
        builtins.print = lambda *a, **k: None
        try:
            result = self.commands['DeleteCollection']().execute()
            print(f"DEBUG delete result: {result}")
            self.snack(self.t('operation_success'))
            self.build_ui()
        except Exception as e:
            print(f"DEBUG delete error: {e}")
            import traceback
            traceback.print_exc()
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
        # 创建进度对话框
        progress_bar = ft.ProgressBar(width=400, value=0)
        status_text = ft.Text("准备构建...", size=14)
        detail_text = ft.Text("", size=12, color=ft.Colors.GREY_600)

        progress_dlg = ft.AlertDialog(
            title=ft.Text("正在构建项目"),
            content=ft.Column([
                progress_bar,
                ft.Container(height=10),
                status_text,
                detail_text,
            ], tight=True, spacing=5),
            modal=True,
        )
        self.page.overlay.append(progress_dlg)
        progress_dlg.open = True
        self.page.update()

        def build_task():
            """在后台线程执行构建"""
            try:
                # 更新进度
                progress_bar.value = 0.2
                status_text.value = "正在安装依赖..."
                detail_text.value = "npm install"
                self.page.update()

                import time
                time.sleep(0.5)

                progress_bar.value = 0.5
                status_text.value = "正在构建项目..."
                detail_text.value = "npm run build"
                self.page.update()

                result = self.commands['Build']().execute()

                # 构建完成
                progress_bar.value = 1.0
                status_text.value = "构建完成！"
                detail_text.value = ""
                self.page.update()

                time.sleep(0.5)

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

        # 使用Flet的run_thread在后台执行
        import threading
        threading.Thread(target=lambda: self.page.run_thread(
            build_task), daemon=True).start()

    def start_editor(self, e):
        """启动编辑器 - 带进度条"""
        # 如果已经在运行，直接打开窗口
        if self.editor_running and self.editor_url:
            self.open_editor_window(e)
            return

        # 创建进度对话框
        progress_bar = ft.ProgressBar(width=400, value=0)
        status_text = ft.Text("准备启动编辑器...", size=14)
        detail_text = ft.Text("", size=12, color=ft.Colors.GREY_600)

        progress_dlg = ft.AlertDialog(
            title=ft.Text("启动编辑器"),
            content=ft.Column([
                progress_bar,
                ft.Container(height=10),
                status_text,
                detail_text,
            ], tight=True, spacing=5),
            modal=True,
        )
        self.page.overlay.append(progress_dlg)
        progress_dlg.open = True
        self.page.update()

        def editor_task():
            """在后台线程执行启动"""
            import subprocess
            import webbrowser
            import time
            import json
            import tempfile
            import re
            
            try:
                # 阶段1: 启动开发服务器
                progress_bar.value = 0.1
                status_text.value = "启动开发服务器..."
                detail_text.value = "npm run dev"
                self.page.update()
                
                base_path = os.path.dirname(os.path.abspath(__file__))
                
                # 启动开发服务器
                if os.name == 'nt':
                    self.dev_server_process = subprocess.Popen(
                        'npm run dev',
                        cwd=base_path,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True,
                        shell=True,
                        creationflags=subprocess.CREATE_NEW_CONSOLE,
                        encoding='utf-8',
                        errors='replace'
                    )
                else:
                    self.dev_server_process = subprocess.Popen(
                        ['npm', 'run', 'dev'],
                        cwd=base_path,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True,
                        encoding='utf-8',
                        errors='replace'
                    )
                
                print(f"[Editor] Dev server process started with PID: {self.dev_server_process.pid}")
                
                # 阶段2: 解析端口号
                progress_bar.value = 0.3
                status_text.value = "等待开发服务器就绪..."
                detail_text.value = "解析端口号"
                self.page.update()
                
                port_pattern = re.compile(r'Local:\s+https?://(?:localhost|127\.0\.0\.1):(\d+)')
                max_wait = 30
                start_time = time.time()
                frontend_port = None
                
                while time.time() - start_time < max_wait:
                    line = self.dev_server_process.stdout.readline()
                    if line:
                        line_stripped = line.rstrip()
                        if line_stripped:
                            print(f"[DEV SERVER] {line_stripped}")
                        
                        line_clean = re.sub(r'\x1b\[[0-9;]*m', '', line)
                        match = port_pattern.search(line_clean)
                        if match:
                            frontend_port = int(match.group(1))
                            print(f"[Editor] ✅ Port detected: {frontend_port}")
                            break
                    
                    if self.dev_server_process.poll() is not None:
                        raise Exception(f"开发服务器启动失败 (退出码: {self.dev_server_process.returncode})")
                    
                    time.sleep(0.1)
                
                if frontend_port is None:
                    raise Exception("无法从开发服务器输出中解析端口号")
                
                # 启动日志输出线程
                import threading
                def output_dev_server_logs():
                    try:
                        for line in iter(self.dev_server_process.stdout.readline, ''):
                            if line:
                                print(f"[DEV SERVER] {line.rstrip()}")
                    except Exception as e:
                        print(f"[Editor] Dev server log thread error: {e}")
                
                log_thread = threading.Thread(target=output_dev_server_logs, daemon=True)
                log_thread.start()
                
                # 阶段3: 启动后端服务器
                progress_bar.value = 0.5
                status_text.value = "启动后端API服务器..."
                detail_text.value = "FastAPI server"
                self.page.update()
                
                info_file = tempfile.NamedTemporaryFile(
                    mode='w', 
                    delete=False, 
                    suffix='.json'
                )
                info_path = info_file.name
                info_file.close()
                
                server_script = os.path.join(
                    os.path.dirname(__file__), 
                    'mainTools', 
                    'editor_server.py'
                )
                
                import sys
                python_exe = sys.executable
                
                self.editor_server = subprocess.Popen(
                    [python_exe, server_script, "--info-file", info_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                print(f"[Editor] Server process started with PID: {self.editor_server.pid}")
                
                # 启动服务器日志输出线程
                def output_server_logs():
                    try:
                        for line in iter(self.editor_server.stdout.readline, ''):
                            if line:
                                print(f"[SERVER] {line.rstrip()}")
                    except Exception as e:
                        print(f"[Editor] Log thread error: {e}")
                
                log_thread = threading.Thread(target=output_server_logs, daemon=True)
                log_thread.start()
                
                # 阶段4: 等待服务器就绪
                progress_bar.value = 0.7
                status_text.value = "等待后端服务器就绪..."
                detail_text.value = "读取服务器信息"
                self.page.update()
                
                max_wait = 20
                server_info = None
                
                for i in range(max_wait):
                    time.sleep(0.5)
                    
                    if self.editor_server.poll() is not None:
                        raise Exception(f"服务器进程意外退出 (退出码: {self.editor_server.returncode})")
                    
                    if os.path.exists(info_path) and os.path.getsize(info_path) > 0:
                        try:
                            with open(info_path, 'r') as f:
                                server_info = json.load(f)
                            print(f"[Editor] Server info loaded: port={server_info['port']}")
                            break
                        except json.JSONDecodeError:
                            if i < max_wait - 1:
                                continue
                            else:
                                raise Exception("服务器信息文件格式错误")
                
                if server_info is None:
                    raise Exception("等待服务器启动超时")
                
                self.editor_port = server_info['port']
                self.editor_token = server_info['token']
                
                # 阶段5: 打开浏览器
                progress_bar.value = 0.9
                status_text.value = "打开浏览器..."
                detail_text.value = ""
                self.page.update()
                
                self.editor_url = f"http://localhost:{frontend_port}/#/editor?token={self.editor_token}&api_port={self.editor_port}"
                print(f"[Editor] Opening browser: {self.editor_url}")
                webbrowser.open(self.editor_url)
                
                # 启动监控线程
                monitor_thread = threading.Thread(
                    target=self.monitor_editor_page,
                    daemon=True
                )
                monitor_thread.start()
                
                # 标记编辑器已启动
                self.editor_running = True
                
                # 完成
                progress_bar.value = 1.0
                status_text.value = "启动完成！"
                self.page.update()
                time.sleep(0.5)
                
                # 关闭进度对话框
                progress_dlg.open = False
                self.page.update()
                
                # 刷新UI以显示新按钮
                self.build_ui()
                
                self.snack("✅ 编辑器已启动！", False)
                
            except Exception as ex:
                # 关闭进度对话框
                progress_dlg.open = False
                self.page.update()
                
                self.snack(f"启动编辑器失败: {ex}", True)
                print(f"[Editor] Error: {ex}")
                import traceback
                traceback.print_exc()
                
                # 清理进程
                if hasattr(self, 'dev_server_process') and self.dev_server_process:
                    try:
                        self.dev_server_process.terminate()
                    except:
                        pass
                
                if hasattr(self, 'editor_server') and self.editor_server:
                    try:
                        self.editor_server.terminate()
                    except:
                        pass
                
                self.editor_running = False
                self.editor_url = None

        # 使用Flet的run_thread在后台执行
        import threading
        threading.Thread(target=lambda: self.page.run_thread(
            editor_task), daemon=True).start()

    def open_editor_window(self, e):
        """打开已运行的编辑器窗口"""
        if self.editor_url:
            import webbrowser
            webbrowser.open(self.editor_url)
            self.snack("✅ 已打开编辑器窗口", False)
        else:
            self.snack("编辑器未运行", True)

    def stop_editor(self, e):
        """停止编辑器服务"""
        def confirm_stop():
            try:
                # 停止开发服务器
                if hasattr(self, 'dev_server_process') and self.dev_server_process:
                    print("[Editor] Stopping dev server...")
                    try:
                        self.dev_server_process.terminate()
                        self.dev_server_process.wait(timeout=5)
                        print("[Editor] Dev server stopped")
                    except:
                        try:
                            self.dev_server_process.kill()
                        except:
                            pass
                
                # 停止后端服务器
                if hasattr(self, 'editor_server') and self.editor_server:
                    print("[Editor] Stopping backend server...")
                    try:
                        self.editor_server.terminate()
                        self.editor_server.wait(timeout=5)
                        print("[Editor] Backend server stopped")
                    except:
                        try:
                            self.editor_server.kill()
                        except:
                            pass
                
                # 重置状态
                self.editor_running = False
                self.editor_url = None
                self.dev_server_process = None
                self.editor_server = None
                
                # 刷新UI
                self.build_ui()
                
                self.snack("✅ 编辑器已关闭", False)
                
            except Exception as ex:
                self.snack(f"关闭失败: {ex}", True)
                import traceback
                traceback.print_exc()
        
        # 确认对话框
        self.confirm(
            "确认关闭",
            "确定要关闭编辑器服务吗？\n这将停止开发服务器和后端API服务器。",
            confirm_stop
        )

    def monitor_editor_page(self):
        """监控编辑器页面状态"""
        import time
        import requests
        
        consecutive_failures = 0
        max_failures = 5  # 连续失败5次后关闭服务器（增加容错）
        
        # 等待服务器启动（最多等待10秒）
        print("[Editor Monitor] Waiting for server to start...")
        print(f"[Editor Monitor] Target URL: http://127.0.0.1:{self.editor_port}/api/health")
        print(f"[Editor Monitor] Auth Token: {self.editor_token[:10]}...")
        
        startup_wait = 0
        while startup_wait < 10:
            # 检查编辑器是否已被关闭
            if not self.editor_running:
                print("[Editor Monitor] Editor stopped, exiting monitor")
                return
            
            try:
                print(f"[Editor Monitor] Startup attempt {startup_wait + 1}/10")
                response = requests.get(
                    f"http://127.0.0.1:{self.editor_port}/api/health",
                    headers={"X-Auth-Token": self.editor_token},
                    timeout=5
                )
                print(f"[Editor Monitor] Startup response: status={response.status_code}, body={response.text[:100]}")
                if response.status_code == 200:
                    print("[Editor Monitor] Server started successfully")
                    break
            except requests.exceptions.Timeout as e:
                print(f"[Editor Monitor] Startup timeout: {e}")
            except requests.exceptions.ConnectionError as e:
                print(f"[Editor Monitor] Startup connection error: {e}")
            except Exception as e:
                print(f"[Editor Monitor] Startup error: {type(e).__name__}: {e}")
            time.sleep(1)
            startup_wait += 1
        
        if startup_wait >= 10:
            print("[Editor Monitor] Server failed to start within 10 seconds")
            if self.editor_server:
                try:
                    self.editor_server.terminate()
                except:
                    pass
            return
        
        print("[Editor Monitor] Starting health check loop...")
        check_count = 0
        
        while True:
            # 检查编辑器是否已被关闭
            if not self.editor_running:
                print("[Editor Monitor] Editor stopped, exiting monitor")
                return
            
            check_count += 1
            try:
                print(f"[Editor Monitor] Health check #{check_count} at {time.strftime('%H:%M:%S')}")
                
                # 检查进程是否还活着（只在进程存在时检查）
                if self.editor_server:
                    poll_result = self.editor_server.poll()
                    if poll_result is not None:
                        print(f"[Editor Monitor] Server process died! Exit code: {poll_result}")
                        break
                    else:
                        print(f"[Editor Monitor] Server process is alive (PID: {self.editor_server.pid})")
                else:
                    print("[Editor Monitor] Server process is None, exiting monitor")
                    return
                
                # 发送健康检查请求
                print(f"[Editor Monitor] Sending GET request to http://127.0.0.1:{self.editor_port}/api/health")
                start_time = time.time()
                
                response = requests.get(
                    f"http://127.0.0.1:{self.editor_port}/api/health",
                    headers={"X-Auth-Token": self.editor_token},
                    timeout=10  # 增加到10秒超时
                )
                
                elapsed = time.time() - start_time
                print(f"[Editor Monitor] Response received in {elapsed:.2f}s: status={response.status_code}")
                
                if response.status_code == 200:
                    # 服务器正常响应，重置失败计数
                    print(f"[Editor Monitor] Health check OK (consecutive_failures reset from {consecutive_failures} to 0)")
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    print(f"[Editor Monitor] Health check failed with status {response.status_code} (consecutive_failures: {consecutive_failures}/{max_failures})")
                    print(f"[Editor Monitor] Response body: {response.text[:200]}")
                
                print(f"[Editor Monitor] Sleeping for 10 seconds...")
                time.sleep(10)  # 减少检查频率到每10秒
                
            except requests.exceptions.Timeout as e:
                consecutive_failures += 1
                print(f"[Editor Monitor] Health check timeout (consecutive_failures: {consecutive_failures}/{max_failures})")
                print(f"[Editor Monitor] Timeout details: {e}")
                time.sleep(10)
            except requests.exceptions.ConnectionError as e:
                consecutive_failures += 1
                print(f"[Editor Monitor] Health check connection error (consecutive_failures: {consecutive_failures}/{max_failures})")
                print(f"[Editor Monitor] Connection error details: {e}")
                time.sleep(10)
            except requests.exceptions.RequestException as e:
                consecutive_failures += 1
                print(f"[Editor Monitor] Health check request exception (consecutive_failures: {consecutive_failures}/{max_failures})")
                print(f"[Editor Monitor] Exception type: {type(e).__name__}")
                print(f"[Editor Monitor] Exception details: {e}")
                time.sleep(10)
            except Exception as e:
                print(f"[Editor Monitor] Unexpected error: {type(e).__name__}: {e}")
                consecutive_failures += 1
                import traceback
                traceback.print_exc()
                time.sleep(10)
            
            # 如果连续失败达到阈值，停止服务器
            if consecutive_failures >= max_failures:
                print(f"[Editor Monitor] Max failures reached ({consecutive_failures}/{max_failures}), stopping server...")
                if self.editor_server:
                    try:
                        print("[Editor Monitor] Terminating server process...")
                        self.editor_server.terminate()
                        self.editor_server.wait(timeout=5)
                        print("[Editor Monitor] Server stopped successfully")
                    except Exception as e:
                        print(f"[Editor Monitor] Error stopping server: {e}")
                        try:
                            print("[Editor Monitor] Killing server process...")
                            self.editor_server.kill()
                        except:
                            pass
                break

    def show_migrate_dialog(self, e):
        """显示迁移对话框"""
        content = ft.Column([
            ft.Text(self.t('migrate_title'), size=20,
                    weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            ft.Text(self.t('migrate_desc'), size=13, color=ft.Colors.GREY_700),
        ], tight=True)

        dlg = ft.AlertDialog(
            title=ft.Text(""),
            content=content,
            actions=[
                ft.TextButton(self.t('cancel'),
                              on_click=lambda e: self.close_dlg(dlg)),
                ft.Button(self.t('migrate_confirm'),
                          on_click=lambda e: self.confirm_migrate(dlg)),
            ],
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def confirm_migrate(self, dlg):
        """确认迁移，开始执行"""
        self.close_dlg(dlg)

        # 创建进度对话框
        progress_bar = ft.ProgressBar(width=400, value=0)
        status_text = ft.Text(self.t('migrating'), size=14)
        detail_text = ft.Text("", size=12, color=ft.Colors.GREY_600)

        progress_dlg = ft.AlertDialog(
            title=ft.Text(self.t('migrate_title')),
            content=ft.Column([
                progress_bar,
                ft.Container(height=10),
                status_text,
                detail_text,
            ], tight=True, spacing=5),
            modal=True,
        )
        self.page.overlay.append(progress_dlg)
        progress_dlg.open = True
        self.page.update()

        def migrate_task():
            try:
                status_text.value = self.t('migrating')
                progress_bar.value = 0.3
                detail_text.value = "扫描文章..."
                self.page.update()

                import time
                time.sleep(0.5)

                result = self.commands['MigrateFromHexo']().execute()

                # 迁移完成
                progress_bar.value = 1.0
                status_text.value = self.t('migrate_complete')
                detail_text.value = result
                self.page.update()

                time.sleep(1)

                # 关闭进度对话框
                progress_dlg.open = False
                self.page.update()

                # 显示成功消息
                self.snack(result)
                print(result)

            except Exception as ex:
                # 关闭进度对话框
                progress_dlg.open = False
                self.page.update()
                # 显示错误消息
                self.snack(f"{self.t('error')}: {ex}", True)

        # 使用Flet的run_thread在后台执行
        import threading
        threading.Thread(target=lambda: self.page.run_thread(
            migrate_task), daemon=True).start()

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

        # 加载加密密码
        crypto_password = ''
        try:
            from mainTools.commands import GetCryptoPassword
            get_crypto_pwd_cmd = GetCryptoPassword()
            crypto_password = get_crypto_pwd_cmd.execute()
        except:
            pass

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
            ('ChangeInfoAndTipPosition', self.t('change_info_tip_pos'), 'bool'),
        ]

        # 主题配置部分
        form_rows.append(ft.Divider())
        form_rows.append(ft.Text('主题配置', size=20, weight=ft.FontWeight.BOLD))

        theme_items = [
            ('LightTheme', '浅色主题', 'dropdown', ['day', 'bright']),
            ('DarkTheme', '深色主题', 'dropdown', ['dark', 'night']),
            ('defaultMode', '默认模式', 'dropdown', ['system', 'light', 'dark']),
            ('transitionDuration', '过渡时长(ms)', 'number'),
            ('enableTransitions', '启用过渡动画', 'bool'),
            ('enableSystemDetection', '启用系统主题检测', 'bool'),
        ]

        # 添加主题配置字段
        for item in theme_items:
            if len(item) == 4:
                key, label, field_type, options = item
            else:
                key, label, field_type = item
                options = None

            value = current_config.get(key, '')

            if field_type == 'dropdown':
                field = ft.Dropdown(
                    label=label,
                    value=str(value) if value else options[0],
                    options=[ft.dropdown.Option(opt) for opt in options],
                    width=300,
                )
            elif field_type == 'number':
                field = ft.TextField(
                    label=label,
                    value=str(value) if value else '300',
                    width=200,
                    keyboard_type=ft.KeyboardType.NUMBER,
                )
            elif field_type == 'bool':
                field = ft.Checkbox(
                    label=label,
                    value=bool(value) if value != '' else True,
                )

            config_fields[key] = field
            form_rows.append(ft.Container(content=field, padding=5))

        # 基本配置字段
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

        # 加密配置
        form_rows.append(ft.Divider())
        form_rows.append(ft.Text(self.t('crypto_config'),
                         size=20, weight=ft.FontWeight.BOLD))

        # CryptoTag 字段
        crypto_tag_field = ft.TextField(
            label=self.t('crypto_tag'),
            value=current_config.get('CryptoTag', ''),
            width=500,
            hint_text="例如: 暂未公开",
        )
        config_fields['CryptoTag'] = crypto_tag_field
        form_rows.append(ft.Container(content=crypto_tag_field, padding=5))

        # Password 字段（单独保存到 Crypto.json）
        password_field = ft.TextField(
            label=self.t('crypto_password'),
            value=crypto_password,
            width=500,
            password=True,
            can_reveal_password=True,
            hint_text="用于加密文章的密码",
        )
        form_rows.append(ft.Container(content=password_field, padding=5))

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
                    elif isinstance(field, ft.Dropdown):
                        config_updates[key] = field.value
                    else:
                        value = field.value
                        # 尝试转换为正确的类型
                        if key in ['BackgroundImgOpacity', 'BackgroundImgBlur']:
                            value = float(value) if value else 0.0
                        elif key in ['PostsPerPage', 'transitionDuration']:
                            value = int(value) if value else (10 if key == 'PostsPerPage' else 300)
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

                # 保存加密密码到 Crypto.json
                password = password_field.value.strip()
                try:
                    from mainTools.commands import UpdateCryptoPassword
                    update_pwd_cmd = UpdateCryptoPassword()
                    pwd_result = update_pwd_cmd.execute(password)
                    self.snack(f"{result}\n{pwd_result}", False)
                except Exception as pwd_ex:
                    self.snack(f"{result}\n密码保存失败: {pwd_ex}", True)

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
        """开始GitHub部署（使用run_thread）"""
        # 创建详细进度对话框
        progress_bar = ft.ProgressBar(width=400, value=0)
        status_text = ft.Text("准备部署...", size=14)
        detail_text = ft.Text("", size=12, color=ft.Colors.GREY_600)

        loading_dlg = ft.AlertDialog(
            title=ft.Text(self.t('deploying')),
            content=ft.Column([
                progress_bar,
                ft.Container(height=10),
                status_text,
                detail_text,
            ], tight=True, spacing=5),
            modal=True,
        )

        self.page.overlay.append(loading_dlg)
        loading_dlg.open = True
        self.page.update()

        def deploy_task():
            """在后台线程执行部署"""
            try:
                import time

                # 阶段1: 生成配置
                progress_bar.value = 0.1
                status_text.value = "生成配置文件..."
                detail_text.value = "Generate configuration"
                self.page.update()
                time.sleep(0.3)

                # 阶段2: 构建项目
                progress_bar.value = 0.3
                status_text.value = "构建项目..."
                detail_text.value = "Building project"
                self.page.update()
                time.sleep(0.3)

                # 阶段3: 验证仓库
                progress_bar.value = 0.5
                status_text.value = "验证GitHub仓库..."
                detail_text.value = "Verifying repository"
                self.page.update()

                # 执行部署
                from mainTools.github_commands import FullDeploy
                deploy_cmd = FullDeploy()

                # 阶段4: 上传文件
                progress_bar.value = 0.7
                status_text.value = "上传文件到GitHub..."
                detail_text.value = "Uploading files"
                self.page.update()

                result = deploy_cmd.execute(token, repo_name)

                # 阶段5: 完成
                progress_bar.value = 1.0
                status_text.value = "部署完成！"
                detail_text.value = ""
                self.page.update()
                time.sleep(0.5)

                # 关闭loading对话框
                loading_dlg.open = False
                self.page.update()

                if result and result['success']:
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
                    self.snack(result.get('message', '部署失败'), True)

            except Exception as e:
                # 关闭loading对话框
                loading_dlg.open = False
                self.page.update()
                # 显示错误
                self.snack(f"部署失败: {str(e)}", True)
                import traceback
                traceback.print_exc()

        # 使用Flet的run_thread在后台执行
        import threading
        threading.Thread(target=lambda: self.page.run_thread(
            deploy_task), daemon=True).start()


def main(page: ft.Page):
    BlogManagerGUI(page)


if __name__ == '__main__':
    ft.run(main)
