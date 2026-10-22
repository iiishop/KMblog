"""
KMBlog 管理工具 - 现代化 Flet GUI
具有可视化仪表板和直观的用户界面
"""

import builtins
import asyncio
import flet as ft
import importlib
import inspect
import json
import os
import re
import sys
import threading
import time
import traceback
import webbrowser
from contextlib import contextmanager

# 添加 mainTools 目录到路径
if getattr(sys, 'frozen', False):
    # 打包后：mainTools 在临时目录
    sys.path.insert(0, os.path.join(sys._MEIPASS, 'mainTools'))
else:
    # 开发环境
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mainTools'))

from mainTools.commands import Command


@contextmanager
def mock_input(*responses):
    """Context manager: temporarily replace builtins.input with canned responses.

    Usage:
        with mock_input('post_name', 'collection', 'y'):
            SomeCommand().execute()
    """
    idx = [0]
    orig = builtins.input
    def _mock(prompt=''):
        if idx[0] < len(responses):
            v = responses[idx[0]]
            idx[0] += 1
            return v
        return ''
    builtins.input = _mock
    try:
        yield
    finally:
        builtins.input = orig


class BlogManagerGUI:
    # Quiet blue workspace with a consistent, accessible light surface.
    CLR_BG = "#f2f5fa"
    CLR_SIDEBAR = "#18283f"
    CLR_SIDEBAR_HOVER = "#223752"
    CLR_SIDEBAR_ACTIVE = "#304b6d"
    CLR_SURFACE = "#ffffff"
    CLR_BORDER = "#dbe3ee"
    CLR_BORDER_LIGHT = "#edf1f6"
    CLR_TEXT = "#203149"
    CLR_TEXT_SECONDARY = "#596b82"
    CLR_TEXT_MUTED = "#6c7b8e"
    CLR_ACCENT = "#315fbc"
    CLR_ACCENT_HOVER = "#244b98"
    CLR_ACCENT_SOFT = "#eaf0fc"
    CLR_GOOD = "#247557"
    CLR_BAD = "#b43c48"
    CLR_WARN = "#956216"

    def __init__(self, page: ft.Page):
        self.page = page

        # 初始化缩放因子（必须在 setup_page 之前）
        self.scale_factor = 1.0

        self.setup_page()
        self.commands = self.get_commands()
        self.current_lang = 'zh'
        self.current_view = 'dashboard'
        self.search_query = ''
        self.search_auto_expand = True
        self.post_sort = 'recent'
        self.settings_view = None
        self.settings_dirty = False
        self.operation_lock = threading.Lock()
        self.busy = False
        self._active_snack = None
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

        # 更新检查状态
        self.update_info = {
            'has_updates': False,
            'commits_behind': 0,
            'checking': False,
            'manager_has_update': False,  # 管理工具是否有更新
            'manager_version': None,  # 管理工具最新版本
        }

        self.build_ui()

        # 启动后台线程检查更新
        self.check_updates_on_startup()

    def setup_page(self):
        """Use logical pixels; window size is not the monitor resolution."""
        self.page.title = "KMBlog Manager"
        self.page.window.width = 1180
        self.page.window.height = 820
        self.page.window.min_width = 800
        self.page.window.min_height = 600
        self.page.window.prevent_close = True
        self.page.window.on_event = self.on_window_event
        self.page.padding = 0
        self.page.bgcolor = self.CLR_BG
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.theme = ft.Theme(
            color_scheme_seed=self.CLR_ACCENT,
            font_family="Microsoft YaHei",
            color_scheme=ft.ColorScheme(
                primary=self.CLR_ACCENT, on_primary="#ffffff",
                surface=self.CLR_SURFACE, on_surface=self.CLR_TEXT,
                outline=self.CLR_BORDER, error=self.CLR_BAD,
            ),
        )
        self.page.on_keyboard_event = self.on_keyboard
        self.page.on_resize = self.on_resize

    def copy(self, zh, en):
        return zh if self.current_lang == 'zh' else en

    async def on_window_event(self, e):
        if e.type != ft.WindowEventType.CLOSE:
            return
        if self.busy:
            self.snack(self.copy('操作进行中，请完成后再关闭窗口。',
                                 'A task is running. Close the window after it finishes.'), True)
            return
        if not self.settings_dirty:
            await self.page.window.destroy()
            return

        async def discard(e):
            self.close_dlg(dialog)
            await self.page.window.destroy()

        async def save_and_close(e):
            self.save_settings(None)
            if not self.settings_dirty:
                self.close_dlg(dialog)
                await self.page.window.destroy()

        dialog = ft.AlertDialog(
            modal=True, title=ft.Text(self.copy('保存修改后再离开？', 'Save changes before leaving?')),
            content=ft.Text(self.copy('配置中还有未保存的修改。', 'Your settings have unsaved changes.')),
            actions=[ft.TextButton(self.t('cancel'), on_click=lambda e: self.close_dlg(dialog)),
                     ft.TextButton(self.copy('不保存并关闭', 'Discard and close'), on_click=discard),
                     self.primary_button(self.copy('保存并关闭', 'Save and close'), ft.Icons.SAVE, save_and_close)],
        )
        self.open_dialog(dialog)

    async def on_keyboard(self, e):
        if any(getattr(control, 'open', False) for control in self.page.overlay):
            return
        if any(getattr(control, 'open', False) for control in getattr(self, '_dialogs', [])):
            return
        if e.ctrl or e.meta:
            if e.key.lower() == 'n':
                self.show_add_dialog(None)
            elif e.key.lower() == 'f':
                self.switch_view('posts')
                await self.search_field.focus()
            elif e.key.lower() == 's' and self.current_view == 'settings':
                self.save_settings(None)

    def on_resize(self, e):
        if not hasattr(self, 'sidebar_host'):
            return
        compact = (self.page.width or 1180) < 1000
        if compact != self.compact:
            self.compact = compact
            self.sidebar_host.content = self.build_sidebar()
            self.content_host.padding = 20 if compact else 32
            self.page.update()

    def primary_button(self, text, icon, handler):
        return ft.Button(text, icon=icon, on_click=handler, height=44,
                         bgcolor=self.CLR_ACCENT, color="#ffffff", elevation=0,
                         style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)))

    def open_dialog(self, dialog):
        self._dialogs = [item for item in getattr(self, '_dialogs', []) if item.open]
        self._dialogs.append(dialog)
        previous = dialog.on_dismiss
        def dismissed(e):
            self._modal_open = False
            if previous:
                previous(e)
        dialog.on_dismiss = dismissed
        self.page.show_dialog(dialog)

    def scale(self, value):
        """根据缩放因子调整数值

        Args:
            value: 原始数值（基于 2K 分辨率）

        Returns:
            调整后的数值
        """
        if isinstance(value, (int, float)):
            return int(value * self.scale_factor)
        return value

    def check_updates_on_startup(self):
        """启动时在后台检查更新"""
        def check_updates_thread():
            try:
                print("[更新检查] 开始检查框架更新...")
                self.update_info['checking'] = True

                # 1. 检查框架更新（Git commits）
                # 强制重新加载模块，避免缓存问题
                import sys
                if 'mainTools.update_framework' in sys.modules:
                    import importlib
                    importlib.reload(sys.modules['mainTools.update_framework'])

                # 导入更新模块
                from mainTools.update_framework import FrameworkUpdater

                # 检查更新
                updater = FrameworkUpdater()
                result = updater.check_for_updates()

                if result['success']:
                    self.update_info['has_updates'] = result['has_updates']
                    self.update_info['commits_behind'] = result.get(
                        'commits_behind', 0)

                    if result['has_updates']:
                        print(f"[更新检查] 发现框架更新 {result['commits_behind']} 个提交")
                        print(
                            f"[更新检查] 本地: {result.get('local_commit', 'unknown')}")
                        print(
                            f"[更新检查] 远程: {result.get('remote_commit', 'unknown')}")
                    else:
                        print("[更新检查] 框架已是最新版本")
                else:
                    print(f"[更新检查] 框架检查失败: {result.get('message', '未知错误')}")

                # 2. 检查管理工具更新（GitHub Releases）
                print("[更新检查] 开始检查管理工具更新...")
                try:
                    from mainTools.update_manager import ManagerUpdater
                    manager_updater = ManagerUpdater()
                    manager_result = manager_updater.check_for_updates()

                    if manager_result['success'] and manager_result['has_update']:
                        self.update_info['manager_has_update'] = True
                        self.update_info['manager_version'] = manager_result['latest_version']
                        print(
                            f"[更新检查] 发现管理工具更新: {manager_result['latest_version']}")
                    else:
                        print("[更新检查] 管理工具已是最新版本")
                except Exception as e:
                    print(f"[更新检查] 管理工具检查失败: {e}")

                self.update_info['checking'] = False

                # 如果有任何更新，刷新 UI 显示徽章
                has_any_update = self.update_info['has_updates'] or self.update_info['manager_has_update']
                if has_any_update:
                    try:
                        # 使用 run_task 在主线程中更新 UI
                        self.page.run_task(self.refresh_dashboard_ui)
                    except Exception as refresh_error:
                        print(f"[UI刷新] run_task 失败: {refresh_error}")

            except Exception as e:
                print(f"[更新检查] 异常: {e}")
                import traceback
                traceback.print_exc()
                self.update_info['checking'] = False

        # 在后台线程中执行检查
        import threading
        thread = threading.Thread(target=check_updates_thread, daemon=True)
        thread.start()

    async def refresh_dashboard_ui(self):
        """异步刷新 dashboard UI（用于显示更新徽章）"""
        try:
            print(f"[UI刷新] 开始刷新，当前视图: {self.current_view}")
            print(
                f"[UI刷新] 更新信息: has_updates={self.update_info['has_updates']}, manager_has_update={self.update_info['manager_has_update']}")

            # 重新构建 UI（无论当前在哪个视图，都更新侧边栏以显示徽章）
            if self.current_view == 'dashboard':
                self.build_ui()
        except Exception as e:
            print(f"[UI刷新] 刷新失败: {e}")
            import traceback
            traceback.print_exc()

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
                'confirm_delete_collection': '删除合集「{}」？文章会移入「无合集」，合集封面及其他文件将被删除。',
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
                'update_framework': '更新框架',
                'update_framework_title': '更新 KMBlog 框架',
                'update_framework_desc': '从 GitHub 同步最新框架代码\n\n更新内容：\n• 自动备份用户数据（文章、配置、图片）\n• 拉取最新框架代码\n• 恢复用户数据\n• 生成配置差异报告\n\n注意：\n• 需要 Git 环境\n• 更新前会自动备份\n• 配置文件变化需手动确认',
                'update_confirm': '开始更新',
                'updating': '正在更新...',
                'update_success': '更新成功',
                'update_failed': '更新失败',
                'checking_git': '检查 Git 状态...',
                'backing_up': '备份用户文件...',
                'pulling_code': '拉取最新代码...',
                'restoring_files': '恢复用户文件...',
                'generating_report': '生成更新报告...',
                'config_save_reminder': '修改配置后请点击 \'保存配置\' 按钮',
                'click_to_init': '点击开始初始化博客框架',
                'click_to_upload': '点击上传',
                'click_upload_cover': '点击上传封面',
                'current_image': '当前图片',
                'new_image': '新图片',
                'preparing_init': '准备初始化...',
                'init_blog_framework': '初始化博客框架',
                'preparing_build': '准备构建...',
                'building_project': '正在构建项目',
                'start_editor': '启动编辑器',
                'allow_lan_access': '是否允许局域网内其他设备访问编辑器？',
                'preparing_start_editor': '准备启动编辑器...',
                'localhost_address': '本机访问地址：',
                'lan_address': '局域网访问地址：',
                'editor_start_failed': '启动编辑器失败',
                'checking_update': '检查更新',
                'checking_updates': '正在检查更新...',
                'update_blog_framework': '更新博客框架',
                'update_manager_tool': '更新管理工具',
                'already_latest': '已是最新版本',
                'select_update_item': '选择更新项目',
                'hint': '提示',
                'found_new_version': '发现管理工具新版本',
                'update_notes': '更新说明:',
                'update_now_question': '是否立即更新管理工具？',
                'program_will_restart': '（程序将自动关闭并重启）',
                'update_later': '稍后更新',
                'update_now': '立即更新',
                'updating_manager': '更新管理工具',
                'downloading': '正在下载...',
                'brief': '简介:',
                'content_preview': '内容预览:',
                'theme_config': '主题配置',
                'image_config': '图片配置',
                'repo_auto_create': '如果仓库不存在，将自动创建',
                'preparing_deploy': '准备部署...',
                'close': '关闭',
                'close_editor': '关闭编辑器',
                'confirm_close': '确认关闭',
                'confirm_close_editor': '确定要关闭编辑器服务吗？\n这将停止开发服务器和后端API服务器。',
                'installing_deps': '正在安装依赖...',
                'building': '正在构建项目...',
                'build_complete': '构建完成！',
                'init_complete': '初始化完成！',
                'start_complete': '启动完成！',
                'editor_closed': '编辑器已关闭',
                'close_failed': '关闭失败',
                'configuring_firewall': '正在配置防火墙...',
                'firewall_success': '防火墙规则已添加成功',
                'firewall_failed_admin': '添加失败，请以管理员身份运行程序',
                'firewall_failed': '配置失败',
                'has_commits': '有 {} 个新提交',
                'latest_version': '最新版本: {}',
                'cancel_btn': '取消',
                'replace': '替换',
                'replace_cover_question': '替换 {} 的封面图片？',
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
                'confirm_delete_post': 'Delete "{}"?', 'confirm_delete_collection': 'Delete collection "{}"? Posts move to Uncollected. Its cover and other files are deleted.',
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
                'update_framework': 'Update Framework',
                'update_framework_title': 'Update KMBlog Framework',
                'update_framework_desc': 'Sync latest framework code from GitHub\n\nUpdate includes:\n• Auto backup user data (posts, config, images)\n• Pull latest framework code\n• Restore user data\n• Generate config diff report\n\nNote:\n• Requires Git environment\n• Auto backup before update\n• Config changes need manual confirmation',
                'update_confirm': 'Start Update',
                'updating': 'Updating...',
                'update_success': 'Update Success',
                'update_failed': 'Update Failed',
                'checking_git': 'Checking Git status...',
                'backing_up': 'Backing up user files...',
                'pulling_code': 'Pulling latest code...',
                'restoring_files': 'Restoring user files...',
                'generating_report': 'Generating update report...',
                'config_save_reminder': 'Please click the \'Save Config\' button after making changes',
                'click_to_init': 'Click to initialize blog framework',
                'click_to_upload': 'Click to upload',
                'click_upload_cover': 'Click to upload cover',
                'current_image': 'Current Image',
                'new_image': 'New Image',
                'preparing_init': 'Preparing initialization...',
                'init_blog_framework': 'Initialize Blog Framework',
                'preparing_build': 'Preparing build...',
                'building_project': 'Building Project',
                'start_editor': 'Start Editor',
                'allow_lan_access': 'Allow LAN access to editor?',
                'preparing_start_editor': 'Preparing to start editor...',
                'localhost_address': 'Localhost Address:',
                'lan_address': 'LAN Address:',
                'editor_start_failed': 'Editor Start Failed',
                'checking_update': 'Check Update',
                'checking_updates': 'Checking for updates...',
                'update_blog_framework': 'Update Blog Framework',
                'update_manager_tool': 'Update Manager Tool',
                'already_latest': 'Already Latest Version',
                'select_update_item': 'Select Update Item',
                'hint': 'Hint',
                'found_new_version': 'Found New Manager Version',
                'update_notes': 'Update Notes:',
                'update_now_question': 'Update manager tool now?',
                'program_will_restart': '(Program will close and restart)',
                'update_later': 'Later',
                'update_now': 'Update Now',
                'updating_manager': 'Updating Manager',
                'downloading': 'Downloading...',
                'brief': 'Brief:',
                'content_preview': 'Content Preview:',
                'theme_config': 'Theme Config',
                'image_config': 'Image Config',
                'repo_auto_create': 'Repository will be auto-created if not exists',
                'preparing_deploy': 'Preparing deployment...',
                'close': 'Close',
                'close_editor': 'Close Editor',
                'confirm_close': 'Confirm Close',
                'confirm_close_editor': 'Close editor service?\nThis will stop dev server and API server.',
                'installing_deps': 'Installing dependencies...',
                'building': 'Building project...',
                'build_complete': 'Build Complete!',
                'init_complete': 'Initialization Complete!',
                'start_complete': 'Start Complete!',
                'editor_closed': 'Editor Closed',
                'close_failed': 'Close Failed',
                'configuring_firewall': 'Configuring firewall...',
                'firewall_success': 'Firewall rule added successfully',
                'firewall_failed_admin': 'Failed, please run as administrator',
                'firewall_failed': 'Configuration failed',
                'has_commits': '{} new commits available',
                'latest_version': 'Latest version: {}',
                'cancel_btn': 'Cancel',
                'replace': 'Replace',
                'replace_cover_question': 'Replace cover image of {}?',
            }
        }
        return trans[self.current_lang].get(key, key)

    def switch_lang(self, e):
        if self.settings_dirty:
            self.snack(self.copy('请先保存配置，再切换语言。', 'Save your settings before switching language.'), True)
            return
        self.current_lang = 'en' if self.current_lang == 'zh' else 'zh'
        self.settings_view = None
        self.build_ui()

    def switch_view(self, view):
        if view == self.current_view:
            return
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
        """Keep the shell mounted so local interactions retain their state."""
        self.compact = (self.page.width or 1180) < 1000
        if not hasattr(self, 'content_host'):
            self.sidebar_host = ft.Container(content=self.build_sidebar())
            self.content_host = ft.Container(content=self.get_current_view(), expand=True,
                                             padding=20 if self.compact else 32)
            self.status_text = ft.Text(self.copy('准备就绪', 'Ready'), size=12,
                                       color=self.CLR_TEXT_SECONDARY, expand=True)
            self.task_progress = ft.ProgressBar(height=2, visible=False, color=self.CLR_ACCENT)
            self.page.add(ft.Row([
                self.sidebar_host,
                ft.Column([
                    self.content_host,
                    self.task_progress,
                    ft.Container(ft.Row([
                        ft.Icon(ft.Icons.CIRCLE, size=7, color=self.CLR_GOOD), self.status_text,
                        ft.Text('KMBlog', size=12, color=self.CLR_TEXT_MUTED),
                    ], spacing=8), padding=ft.Padding(24, 10, 24, 10),
                        bgcolor=self.CLR_SURFACE,
                        border=ft.Border(top=ft.BorderSide(1, self.CLR_BORDER))),
                ], spacing=0, expand=True),
            ], spacing=0, expand=True))
        else:
            self.sidebar_host.content = self.build_sidebar()
            self.content_host.content = self.get_current_view()
        self.page.update()

    @staticmethod
    def _pick_image_file(title="选择图片"):
        """Open tkinter file picker for images. Returns path or None."""
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        file_path = filedialog.askopenfilename(
            title=title,
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.webp *.gif"),
                ("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg"),
                ("WebP", "*.webp"), ("GIF", "*.gif"),
                ("所有文件", "*.*"),
            ],
        )
        root.destroy()
        return file_path if file_path else None

    @staticmethod
    def _card_hover(e, normal_bg, hover_bg):
        """Standard card hover: swap background on enter/leave."""
        e.control.bgcolor = hover_bg if str(e.data).lower() == "true" else normal_bg
        e.control.update()

    def build_sidebar(self):
        compact = getattr(self, 'compact', False)
        buttons = []
        for view, icon, label in [
            ('dashboard', ft.Icons.SPACE_DASHBOARD_OUTLINED, self.t('dashboard')),
            ('posts', ft.Icons.ARTICLE_OUTLINED, self.t('posts')),
            ('settings', ft.Icons.TUNE, self.t('settings')),
        ]:
            selected = self.current_view == view
            buttons.append(ft.TextButton(
                content=ft.Row([
                    ft.Icon(icon, size=21, semantics_label=label if compact else None),
                    *([] if compact else [ft.Text(label, size=14, expand=True)]),
                    *([ft.Icon(ft.Icons.CIRCLE, size=6)] if selected and not compact else []),
                ], spacing=12, alignment=ft.MainAxisAlignment.CENTER if compact else ft.MainAxisAlignment.START),
                tooltip=label, height=48, width=52 if compact else 188,
                on_click=lambda e, v=view: self.switch_view(v),
                style=ft.ButtonStyle(
                    color="#ffffff" if selected else "#b6c6db",
                    bgcolor=self.CLR_SIDEBAR_ACTIVE if selected else "transparent",
                    overlay_color=self.CLR_SIDEBAR_HOVER,
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=12,
                ),
            ))
        return ft.Container(
            width=80 if compact else 220, bgcolor=self.CLR_SIDEBAR,
            padding=ft.Padding(14, 28, 14, 18),
            content=ft.Column([
                ft.Container(ft.Row([
                    ft.Container(ft.Icon(ft.Icons.AUTO_STORIES, color="#ffffff", size=23),
                                 width=40, height=40, bgcolor=self.CLR_ACCENT,
                                 border_radius=12, alignment=ft.Alignment(0, 0)),
                    *([] if compact else [ft.Column([
                        ft.Text('KMBlog', size=19, weight=ft.FontWeight.W_700, color="#ffffff"),
                        ft.Text(self.copy('创作工作台', 'Your writing desk'), size=11, color="#b6c6db"),
                    ], spacing=2)]),
                ], spacing=12), padding=ft.Padding(0, 0, 0, 30)),
                *buttons,
                ft.Container(expand=True),
                *([] if compact else [ft.Container(ft.Column([
                    ft.Row([ft.Icon(ft.Icons.CIRCLE, size=8, color="#77d4ad" if self.editor_running else "#b6c6db"),
                            ft.Text(self.copy('编辑器运行中', 'Editor running') if self.editor_running else
                                    self.copy('编辑器未启动', 'Editor offline'), size=12, color="#c8d5e7")], spacing=8),
                    ft.Text('Ctrl+N  ' + self.t('add_post') + '\nCtrl+F  ' + self.copy('搜索文章', 'Find posts'),
                            size=11, color="#b6c6db"),
                ], spacing=12), padding=ft.Padding(8, 16, 8, 16))]),
                ft.IconButton(icon=ft.Icons.LANGUAGE,
                              tooltip=self.copy('切换语言', 'Switch language'), on_click=self.switch_lang,
                              icon_color="#c8d5e7") if compact else ft.TextButton(
                                  self.t('switch_lang'), icon=ft.Icons.LANGUAGE,
                                  tooltip=self.copy('切换语言', 'Switch language'), on_click=self.switch_lang,
                                  style=ft.ButtonStyle(color="#c8d5e7")),
            ], spacing=6),
        )

    def get_current_view(self):
        if self.current_view == 'posts':
            return self.build_posts_view()
        if self.current_view == 'settings':
            if self.settings_view is None:
                self.settings_view = self.build_settings_view()
            return self.settings_view
        return self.build_dashboard()

    def build_dashboard(self):
        stats = self.get_stats()
        initialized = self.is_blog_initialized()
        primary = self.primary_button(
            self.copy('继续写作', 'Open editor') if self.editor_running else self.t('start_editor'),
            ft.Icons.EDIT_OUTLINED, self.open_editor_window if self.editor_running else self.start_editor)
        hero = ft.Container(
            content=ft.ResponsiveRow([
                ft.Column([
                    ft.Text(self.copy('让想法，成为文章。', 'Make room for your next idea.'),
                            size=28, weight=ft.FontWeight.W_700, color=self.CLR_TEXT),
                    ft.Text(self.copy('写作、整理与发布，从这里开始。', 'Write, organize and publish from one place.'),
                            size=14, color=self.CLR_TEXT_SECONDARY),
                    ft.Container(height=8),
                    ft.Row([primary if initialized else self.primary_button(self.t('init_blog'), ft.Icons.ROCKET_LAUNCH, self.exec_init),
                            ft.TextButton(self.t('add_post'), icon=ft.Icons.ADD, on_click=self.show_add_dialog)], wrap=True),
                ], spacing=10, col={'xs': 12, 'md': 8}),
                ft.Column([
                    self.stat_card(self.t('total_posts'), str(stats['posts']), ft.Icons.ARTICLE_OUTLINED),
                    self.stat_card(self.t('total_collections'), str(stats['collections']), ft.Icons.FOLDER_OUTLINED),
                ], spacing=10, col={'xs': 12, 'md': 4}),
            ], spacing=24, run_spacing=24),
            padding=28, bgcolor=self.CLR_SURFACE, border_radius=16,
            border=ft.Border.all(1, self.CLR_BORDER),
        )
        actions = [
            self.action_btn(self.t('generate'), ft.Icons.SYNC, self.exec_generate,
                            self.copy('同步文章目录与索引', 'Refresh the content index')),
            self.action_btn(self.t('build_project'), ft.Icons.CONSTRUCTION, self.exec_build,
                            self.copy('生成可发布的站点', 'Prepare your site for publishing')),
            self.action_btn(self.t('deploy_github'), ft.Icons.CLOUD_UPLOAD_OUTLINED, self.show_github_dialog,
                            self.copy('发布到 GitHub Pages', 'Publish to GitHub Pages')),
            self.action_btn(self.t('migrate_hexo'), ft.Icons.DRIVE_FILE_MOVE_OUTLINED, self.show_migrate_dialog,
                            self.copy('导入已有 Hexo 文章', 'Bring your Hexo posts over')),
            self.action_btn(self.t('checking_update'), ft.Icons.SYSTEM_UPDATE_ALT, self.show_update_options_dialog,
                            self.copy('框架与管理工具更新', 'Framework and manager updates'),
                            badge=self.update_info['commits_behind'] + int(self.update_info['manager_has_update'])),
        ]
        if self.editor_running:
            actions.append(self.action_btn(self.t('close_editor'), ft.Icons.STOP_CIRCLE_OUTLINED, self.stop_editor,
                                            self.copy('停止本地编辑服务', 'Stop the local editor service')))
        return ft.Column([
            ft.Text(self.t('dashboard'), size=14, weight=ft.FontWeight.W_600, color=self.CLR_TEXT_SECONDARY),
            hero,
            ft.Container(ft.Text(self.t('quick_actions'), size=17, weight=ft.FontWeight.W_600,
                                 color=self.CLR_TEXT), padding=ft.Padding(0, 10, 0, 0)),
            ft.ResponsiveRow(actions, spacing=12, run_spacing=12) if initialized else ft.Text(self.t('click_to_init')),
            self.build_recent_posts(),
        ], spacing=18, scroll=ft.ScrollMode.AUTO, expand=True)

    def stat_card(self, title, value, icon):
        return ft.Container(ft.Row([
            ft.Icon(icon, size=22, color=self.CLR_ACCENT),
            ft.Text(title, size=12, color=self.CLR_TEXT_SECONDARY, expand=True),
            ft.Text(value, size=26, weight=ft.FontWeight.W_600, color=self.CLR_TEXT),
        ], spacing=12), padding=16, bgcolor=self.CLR_BG, border_radius=10)

    def action_btn(self, text, icon, onclick, desc="", badge=None):
        return ft.OutlinedButton(
            content=ft.Row([
                ft.Icon(icon, size=22, color=self.CLR_ACCENT),
                ft.Column([
                    ft.Text(text, size=14, weight=ft.FontWeight.W_600, color=self.CLR_TEXT),
                    ft.Text(desc, size=11, color=self.CLR_TEXT_SECONDARY, max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS),
                ], spacing=5, expand=True),
            ], spacing=12),
            badge=str(badge) if badge else None,
            col={'xs': 12, 'sm': 6, 'lg': 4}, height=84, on_click=onclick,
            style=ft.ButtonStyle(bgcolor=self.CLR_SURFACE, padding=16,
                                 side=ft.BorderSide(1, self.CLR_BORDER),
                                 shape=ft.RoundedRectangleBorder(radius=12)),
        )

    def build_recent_posts(self):
        try:
            records = [(line, coll) for coll, lines in self.get_posts_grouped_by_collection().items() for line in lines]
            records.sort(key=lambda item: self.post_modified(item[0], item[1]), reverse=True)
            items = [self.build_post_item(line, coll, compact=True) for line, coll in records[:5]]
            if not items:
                items = [self.empty_posts()]
            return ft.Container(ft.Column([
                ft.Row([ft.Text(self.copy('最近编辑', 'Recently edited'), size=17,
                                weight=ft.FontWeight.W_600, color=self.CLR_TEXT, expand=True),
                        ft.TextButton(self.copy('查看全部', 'View all'), on_click=lambda e: self.switch_view('posts'))]),
                *items,
            ], spacing=4), padding=20, bgcolor=self.CLR_SURFACE, border_radius=14,
                border=ft.Border.all(1, self.CLR_BORDER))
        except Exception as e:
            return ft.Text(self.copy('无法读取文章：', 'Could not load posts: ') + str(e), color=self.CLR_BAD)

    @staticmethod
    def parse_post(line):
        parts = line.strip().removeprefix('Post:').strip().split(' | ')
        name = parts[0].strip().replace('\\', '/').split('/')[-1].removesuffix('.md')
        metadata = {}
        for part in parts[1:]:
            key, _, value = part.partition(':')
            metadata[key.strip()] = value.strip()
        return {'name': name, 'title': metadata.get('Title') or name,
                'date': metadata.get('Created on', ''), 'characters': metadata.get('Characters', '')}

    def post_modified(self, line, collection):
        from mainTools.path_utils import get_posts_path
        try:
            return os.path.getmtime(os.path.join(get_posts_path(), collection, self.parse_post(line)['name'] + '.md'))
        except OSError:
            return 0

    def empty_posts(self):
        searching = bool(self.search_query.strip())
        return ft.Container(ft.Column([
            ft.Icon(ft.Icons.SEARCH_OFF if searching else ft.Icons.NOTE_ADD_OUTLINED,
                    size=36, color=self.CLR_ACCENT),
            ft.Text(self.copy('没有匹配的文章', 'No matching posts') if searching else self.t('no_posts'),
                    size=16, weight=ft.FontWeight.W_600, color=self.CLR_TEXT),
            ft.Text(self.copy('试试其他标题、文件名或合集名称。', 'Try another title, filename or collection.') if searching else
                    self.copy('创建第一篇文章，开始记录你的想法。', 'Create your first post to get started.'),
                    size=13, color=self.CLR_TEXT_SECONDARY),
            ft.TextButton(self.copy('清除搜索', 'Clear search') if searching else self.t('add_post'),
                          icon=ft.Icons.CLEAR if searching else ft.Icons.ADD,
                          on_click=self.clear_search if searching else self.show_add_dialog),
        ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=32, alignment=ft.Alignment(0, 0))

    def post_item(self, line):
        return self.build_post_item(line, 'Markdowns', compact=True)

    def build_posts_view(self):
        self.search_field = ft.TextField(
            value=self.search_query, hint_text=self.copy('搜索标题、文件名或合集…', 'Search titles, filenames or collections…'),
            prefix_icon=ft.Icons.SEARCH, on_change=self.on_search, expand=True,
            border_radius=10, border_color=self.CLR_BORDER, bgcolor=self.CLR_SURFACE,
            text_size=14, content_padding=14,
        )
        sort = ft.Dropdown(value=self.post_sort, width=160, text_size=13, dense=True,
                           border_color=self.CLR_BORDER, border_radius=10,
                           options=[ft.dropdown.Option('recent', self.copy('最近编辑', 'Last edited')),
                                    ft.dropdown.Option('name', self.copy('标题排序', 'Title A–Z'))],
                           on_select=self.on_sort)
        self.results_count = ft.Text(size=12, color=self.CLR_TEXT_SECONDARY, expand=True)
        self.posts_results = ft.Container(content=self.build_collection_groups())
        return ft.Column([
            ft.Row([ft.Column([
                ft.Text(self.t('posts'), size=26, weight=ft.FontWeight.W_700, color=self.CLR_TEXT),
                ft.Text(self.copy('整理你的文章，让每个想法各得其所。', 'A home for every idea.'),
                        size=13, color=self.CLR_TEXT_SECONDARY),
            ], spacing=6, expand=True), self.primary_button(self.t('add_post'), ft.Icons.ADD, self.show_add_dialog)]),
            ft.Row([self.search_field, ft.IconButton(icon=ft.Icons.CLEAR, tooltip=self.copy('清除搜索', 'Clear search'),
                                                   on_click=self.clear_search), sort], spacing=8),
            ft.Row([self.results_count,
                    ft.TextButton(self.copy('全部展开', 'Expand all'), on_click=lambda e: self.expand_all(True)),
                    ft.TextButton(self.copy('全部收起', 'Collapse all'), on_click=lambda e: self.expand_all(False)),
                    ft.IconButton(icon=ft.Icons.REFRESH, tooltip=self.t('refresh'), on_click=lambda e: self.force_refresh())],
                   spacing=4),
            ft.ListView([self.posts_results], expand=True, spacing=12),
        ], spacing=18, expand=True)

    async def on_search(self, e):
        self.search_query = e.control.value or ''
        self.search_auto_expand = True
        revision = getattr(self, '_search_revision', 0) + 1
        self._search_revision = revision
        await asyncio.sleep(0.16)
        if revision == self._search_revision and self.current_view == 'posts':
            self.refresh_post_results()

    def clear_search(self, e=None):
        self.search_query = ''
        self._search_revision = getattr(self, '_search_revision', 0) + 1
        if self.current_view == 'posts':
            self.search_field.value = ''
            self.refresh_post_results()

    def on_sort(self, e):
        self.post_sort = e.control.value
        self.refresh_post_results()

    def expand_all(self, expanded):
        self.search_auto_expand = expanded
        self.expanded_collections = set(self.get_posts_grouped_by_collection()) if expanded else set()
        self.refresh_post_results()

    def refresh_post_results(self):
        if self.current_view == 'posts':
            self.posts_results.content = self.build_collection_groups()
            self.page.update()

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
        try:
            data = self.get_posts_grouped_by_collection()
            query = self.search_query.strip().casefold()
            groups = []
            matched = 0
            total = sum(len(lines) for lines in data.values())
            self.collection_widgets.clear()
            for collection in sorted(data, key=lambda name: (name != 'Markdowns', name.casefold())):
                lines = [line for line in data[collection] if not query or query in collection.casefold()
                         or query in self.parse_post(line)['title'].casefold()
                         or query in self.parse_post(line)['name'].casefold()]
                if query and not lines:
                    continue
                matched += len(lines)
                if self.post_sort == 'name':
                    lines.sort(key=lambda line: self.parse_post(line)['title'].casefold())
                else:
                    lines.sort(key=lambda line: self.post_modified(line, collection), reverse=True)
                groups.append(self.build_collection_group(
                    self.copy('无合集', 'Uncollected') if collection == 'Markdowns' else collection,
                    collection, lines, is_default=collection == 'Markdowns'))
            if hasattr(self, 'results_count'):
                self.results_count.value = self.copy(f'{matched} / {total} 篇文章', f'{matched} of {total} posts')
            return ft.Column(groups, spacing=12) if groups else self.empty_posts()
        except Exception as e:
            return ft.Container(ft.Column([
                ft.Text(self.copy('文章加载失败', 'Unable to load posts'), color=self.CLR_BAD),
                ft.Text(str(e), selectable=True),
                ft.TextButton(self.t('refresh'), on_click=lambda e: self.force_refresh()),
            ]), padding=24)

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

                # 过滤掉 WaterfallGraph 文件夹
                if current_collection == 'WaterfallGraph':
                    current_collection = None  # 跳过这个合集
                    continue

                grouped_posts[current_collection] = []
            elif line.startswith('Post:'):
                # 解析文章信息
                if current_collection and current_collection not in grouped_posts:
                    grouped_posts[current_collection] = []
                if current_collection:  # 只在有效合集下添加文章
                    grouped_posts[current_collection].append(line)

        # 缓存数据
        self.posts_cache = grouped_posts
        self.is_cache_valid = True

        elapsed = time.time() - start_time
        print(f"[性能] 获取文章数据耗时: {elapsed:.3f}秒")
        return grouped_posts

    def build_image_upload_widget(self, label, current_path, on_upload_callback, width=200, height=150):
        def pick_image(e):
            file_path = self._pick_image_file(self.copy('选择图片', 'Choose an image'))
            if file_path:
                on_upload_callback(file_path)
        has_image = current_path and os.path.exists(current_path)
        preview = ft.Image(src=current_path, width=width, height=height, fit="cover", border_radius=10) if has_image else ft.Container(
            ft.Icon(ft.Icons.ADD_PHOTO_ALTERNATE_OUTLINED, size=36, color=self.CLR_TEXT_SECONDARY),
            width=width, height=height, bgcolor=self.CLR_BG, border_radius=10, alignment=ft.Alignment(0, 0))
        return ft.Column([
            *([ft.Text(label, size=14, color=self.CLR_TEXT)] if label else []),
            preview,
            ft.OutlinedButton(self.copy('更换图片', 'Replace image') if has_image else self.t('click_to_upload'),
                              icon=ft.Icons.UPLOAD_OUTLINED, on_click=pick_image),
        ], spacing=12)

    def process_config_image(self, source_path, target_field_name):
        """处理配置图片上传

        Args:
            source_path: 源图片路径
            target_field_name: 目标字段名 ('BackgroundImg' 或 'HeadImg')
        """
        try:
            from PIL import Image
            import sys

            # 目标目录：使用正确的基础路径
            if getattr(sys, 'frozen', False):
                # 打包后：使用 exe 所在目录
                base_path = os.path.dirname(os.path.abspath(sys.executable))
            else:
                # 开发环境：使用当前文件所在目录
                base_path = os.path.dirname(__file__)

            assets_path = os.path.join(base_path, 'public', 'assets')
            os.makedirs(assets_path, exist_ok=True)

            # 根据字段名确定目标文件名
            if target_field_name == 'BackgroundImg':
                target_filename = 'background.png'
            elif target_field_name == 'HeadImg':
                target_filename = 'head.png'
            else:
                raise ValueError(f"Unknown field: {target_field_name}")

            target_path = os.path.join(assets_path, target_filename)

            # 打开并转换图片
            img = Image.open(source_path)

            # 检查是否是 GIF
            ext = os.path.splitext(source_path)[1].lower()
            if ext == '.gif':
                img.seek(0)
                img.convert('RGBA').save(target_path, 'PNG')
            else:
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                img.save(target_path, 'PNG')

            print(f"[Image] Saved config image: {target_path}")

            # 返回相对路径（用于配置文件，格式：/assets/xxx.png）
            relative_path = f"/assets/{target_filename}"
            return relative_path

        except Exception as ex:
            print(f"[Image] Error processing config image: {ex}")
            import traceback
            traceback.print_exc()
            self.snack(f"处理图片失败: {ex}", True)
            return None

    def build_collection_group(self, display_name, collection_name, posts, is_default=False):
        expanded = collection_name in self.expanded_collections or (
            bool(self.search_query.strip()) and self.search_auto_expand)
        body = ft.Column(spacing=0, visible=expanded)
        toggle = ft.IconButton(icon=ft.Icons.EXPAND_MORE if expanded else ft.Icons.CHEVRON_RIGHT,
                               icon_color=self.CLR_TEXT_SECONDARY,
                               tooltip=self.copy('展开或收起合集', 'Expand or collapse collection'))

        def populate():
            body.controls = [self.build_post_item(line, collection_name) for line in posts] or [
                ft.Container(ft.Text(self.copy('这个合集还没有文章。', 'This collection is empty.'),
                                     color=self.CLR_TEXT_SECONDARY, size=13), padding=20)]

        def toggle_expand(e):
            body.visible = not body.visible
            if body.visible:
                self.expanded_collections.add(collection_name)
                if not body.controls:
                    populate()
            else:
                self.expanded_collections.discard(collection_name)
            toggle.icon = ft.Icons.EXPAND_MORE if body.visible else ft.Icons.CHEVRON_RIGHT
            self.page.update()

        toggle.on_click = toggle_expand
        if expanded:
            populate()
        actions = []
        if not is_default:
            def pick_image(e):
                from mainTools.path_utils import get_posts_path
                collection_path = os.path.join(get_posts_path(), collection_name)
                image = self._pick_image_file(self.copy('选择合集封面', 'Choose collection cover'))
                if image:
                    if os.path.exists(os.path.join(collection_path, 'image.png')):
                        self.show_image_replace_dialog(image, collection_name, collection_path)
                    else:
                        self.process_collection_image(image, collection_name, collection_path)
            actions = [
                ft.IconButton(icon=ft.Icons.IMAGE_OUTLINED, tooltip=self.t('click_upload_cover'), on_click=pick_image,
                              icon_color=self.CLR_TEXT_SECONDARY),
                ft.PopupMenuButton(icon=ft.Icons.MORE_HORIZ, tooltip=self.copy('合集操作', 'Collection actions'),
                    items=[ft.PopupMenuItem(content=self.t('delete_collection'), icon=ft.Icons.DELETE_OUTLINE,
                        on_click=lambda e: self.confirm(self.t('confirm_delete'),
                            self.t('confirm_delete_collection').format(collection_name),
                            lambda: self.do_del_coll(collection_name)))]),
            ]
        header = ft.Row([
            toggle,
            ft.TextButton(content=ft.Row([
                ft.Icon(ft.Icons.FOLDER_OUTLINED, size=20, color=self.CLR_ACCENT),
                ft.Text(display_name, size=14, weight=ft.FontWeight.W_600,
                        color=self.CLR_TEXT, expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(str(len(posts)), size=12, color=self.CLR_TEXT_SECONDARY),
            ], spacing=10), expand=True, on_click=toggle_expand),
            *actions,
        ], spacing=2)
        group = ft.Container(ft.Column([
            ft.Container(header, padding=ft.Padding(8, 6, 8, 6)), body,
        ], spacing=0), bgcolor=self.CLR_SURFACE, border=ft.Border.all(1, self.CLR_BORDER), border_radius=12)
        self.collection_widgets[collection_name] = group
        return group

    def build_post_item(self, line, source_collection, compact=False):
        post = self.parse_post(line)
        detail = self.copy('无合集', 'Uncollected') if source_collection == 'Markdowns' else source_collection
        if post['characters']:
            detail += '  /  ' + post['characters'] + self.copy(' 字符', ' characters')
        preview = ft.TextButton(
            content=ft.Row([
                ft.Container(ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, size=20, color=self.CLR_ACCENT),
                             padding=10, bgcolor=self.CLR_BG, border_radius=10),
                ft.Column([
                    ft.Text(post['title'], size=14, color=self.CLR_TEXT, weight=ft.FontWeight.W_500,
                            max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(detail, size=11, color=self.CLR_TEXT_SECONDARY,
                            max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ], spacing=5, expand=True),
            ], spacing=12), expand=True, height=70,
            tooltip=post['name'] + '.md',
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=10),
            on_click=lambda e: self.show_post_preview(post['name'], source_collection),
        )
        trailing = ft.Icon(ft.Icons.CHEVRON_RIGHT, size=18, color=self.CLR_TEXT_MUTED) if compact else ft.PopupMenuButton(
            icon=ft.Icons.MORE_HORIZ, tooltip=self.copy('文章操作', 'Post actions'),
            items=[
                ft.PopupMenuItem(content=self.copy('预览文章', 'Preview post'), icon=ft.Icons.VISIBILITY_OUTLINED,
                                on_click=lambda e: self.show_post_preview(post['name'], source_collection)),
                ft.PopupMenuItem(content=self.copy('移动到合集', 'Move to collection'), icon=ft.Icons.DRIVE_FILE_MOVE_OUTLINED,
                                on_click=lambda e: self.show_move_dialog(post['name'], source_collection)),
                ft.PopupMenuItem(content=self.t('delete_post'), icon=ft.Icons.DELETE_OUTLINE,
                                on_click=lambda e: self.confirm(self.t('confirm_delete'),
                                    self.t('confirm_delete_post').format(post['name']),
                                    lambda: self.do_del_post(post['name'], None if source_collection == 'Markdowns' else source_collection))),
            ])
        return ft.Container(ft.Row([preview, trailing], spacing=4), padding=ft.Padding(8, 0, 12, 0),
                             border=ft.Border(top=ft.BorderSide(1, self.CLR_BORDER_LIGHT)))

    def show_move_dialog(self, post, source):
        options = sorted(set(self.get_posts_grouped_by_collection()) | {'Markdowns'})
        targets = [name for name in options if name != source]
        if not targets:
            self.snack(self.copy('暂无其他合集。新建文章时可填写一个新合集名称。',
                                 'No other collection yet. Create one when adding a post.'))
            return
        target = ft.Dropdown(label=self.t('collection_name'), value=targets[0], width=380,
                             options=[ft.dropdown.Option(name, self.copy('无合集', 'Uncollected') if name == 'Markdowns' else name)
                                      for name in targets])
        def move(e):
            self.close_dlg(dialog)
            self.move_post_to_collection(post, source, target.value)
        dialog = ft.AlertDialog(title=ft.Text(self.copy('移动文章', 'Move post')),
                                content=ft.Column([ft.Text(post), target], tight=True, spacing=16),
                                actions=[ft.TextButton(self.t('cancel'), on_click=lambda e: self.close_dlg(dialog)),
                                         self.primary_button(self.copy('移动', 'Move'), ft.Icons.DRIVE_FILE_MOVE_OUTLINED, move)])
        self.open_dialog(dialog)

    def process_collection_image(self, source_path, collection_name, collection_path):
        """处理合集封面图片"""
        try:
            from PIL import Image

            # 确保目录存在
            os.makedirs(collection_path, exist_ok=True)

            # 目标路径
            target_path = os.path.join(collection_path, 'image.png')

            # 打开图片
            img = Image.open(source_path)

            # 检查是否是 GIF
            ext = os.path.splitext(source_path)[1].lower()
            if ext == '.gif':
                # GIF 保持动态效果，直接复制
                import shutil
                # 先转换为 PNG 序列帧或保存为 GIF
                # 这里简化处理：如果是 GIF，保存第一帧为 PNG
                img.seek(0)
                img.convert('RGBA').save(target_path, 'PNG')
            else:
                # 其他格式转换为 PNG
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                img.save(target_path, 'PNG')

            print(f"[Image] Saved collection image: {target_path}")

            # 自动调用 Generate 命令更新 JSON 文件
            try:
                # 确保 mainTools 目录在 Python 路径中
                if getattr(sys, 'frozen', False):
                    main_tools_path = os.path.join(sys._MEIPASS, 'mainTools')
                else:
                    main_tools_path = os.path.join(
                        os.path.dirname(__file__), 'mainTools')

                if main_tools_path not in sys.path:
                    sys.path.insert(0, main_tools_path)

                from commands import Generate
                generate_cmd = Generate()
                result = generate_cmd.execute()
                print(f"[Generate] Auto-generated after image upload")
            except Exception as gen_ex:
                print(f"[Generate] Warning: Failed to auto-generate: {gen_ex}")
                import traceback
                traceback.print_exc()

            # 刷新UI
            self.build_ui()
            self.snack(f"已设置 {collection_name} 的封面图片", False)

        except Exception as ex:
            print(f"[Image] Error processing image: {ex}")
            import traceback
            traceback.print_exc()
            self.snack(f"处理图片失败: {ex}", True)

    def show_image_replace_dialog(self, new_image_path, collection_name, collection_path):
        """显示图片替换确认对话框"""
        old_image_path = os.path.join(collection_path, 'image.png')

        # 创建预览
        preview_content = ft.Row([
            ft.Column([
                ft.Text(self.t('current_image'), size=14,
                        weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Image(
                        src=old_image_path,
                        width=200,
                            fit="contain",
                    ),
                    border=ft.Border.all(2, ft.Colors.GREY_400),
                    border_radius=8,
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            ft.Icon(ft.Icons.ARROW_FORWARD, size=32, color=self.CLR_ACCENT),
            ft.Column([
                ft.Text(self.t('new_image'), size=14,
                        weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Image(
                        src=new_image_path,
                        width=200,
                            fit="contain",
                    ),
                    border=ft.Border.all(2, ft.Colors.GREEN_400),
                    border_radius=8,
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
        ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)

        def confirm_replace():
            try:
                # 删除旧图片
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

                # 处理新图片
                self.process_collection_image(
                    new_image_path, collection_name, collection_path)
                self.close_dlg(dlg)

            except Exception as ex:
                self.snack(f"替换失败: {ex}", True)

        dlg = ft.AlertDialog(
            title=ft.Text(
                self.t('replace_cover_question').format(collection_name)),
            content=ft.Container(
                content=preview_content,
                width=600,
                height=250,
            ),
            actions=[
                ft.TextButton("取消", on_click=lambda e: self.close_dlg(dlg)),
                ft.Button(
                    self.t('replace'),
                    on_click=lambda e: confirm_replace(),
                    bgcolor=self.CLR_GOOD,
                    color=self.CLR_SURFACE,
                ),
            ],
        )

        self.open_dialog(dlg)
        self.page.update()

    def move_post_to_collection(self, post_name, source_collection, target_collection):
        def operation():
            from mainTools.move_post_command import MovePost
            result = MovePost().execute(post_name, source_collection, target_collection)
            if not result['success']:
                raise RuntimeError(result['message'])
            self.commands['Generate']().execute()
        self.run_operation(self.copy('移动文章', 'Move post') + ' / ' + post_name, operation,
                           lambda: self.expanded_collections.add(target_collection))

    def force_refresh(self):
        self.is_cache_valid = False
        if self.current_view == 'posts':
            self.refresh_post_results()
        else:
            self.build_ui()
        self.snack(self.copy('文章列表已刷新', 'Posts refreshed'))

    def incremental_refresh_posts(self):
        self.refresh_post_results()

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

    def get_stats(self):
        try:
            groups = self.get_posts_grouped_by_collection()
            return {'posts': sum(len(posts) for posts in groups.values()),
                    'collections': sum(name != 'Markdowns' for name in groups)}
        except Exception:
            return {'posts': 0, 'collections': 0}

    def snack(self, msg, error=False):
        if self._active_snack is not None:
            self._active_snack.open = False
        self._active_snack = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.ERROR_OUTLINE if error else ft.Icons.CHECK_CIRCLE_OUTLINE, size=20, color="#ffffff"),
                ft.Text(str(msg), color="#ffffff", size=13, expand=True, selectable=True),
            ], spacing=10), bgcolor=self.CLR_BAD if error else self.CLR_SIDEBAR,
            duration=6500 if error else 2800, show_close_icon=True,
        )
        self.page.show_dialog(self._active_snack)
        if hasattr(self, 'status_text'):
            self.status_text.value = str(msg).split('\n')[0]
        self.page.update()

    def close_dialog(self, dialog):
        self.close_dlg(dialog)

    def show_add_dialog(self, e):
        post = ft.TextField(label=self.t('post_name'), autofocus=True,
                            hint_text=self.copy('例如：我的第一篇文章', 'For example: My first post'),
                            border_radius=10, text_size=14)
        coll = ft.TextField(label=self.t('collection_name'), border_radius=10, text_size=14,
                            helper=self.copy('选填；留空归入「无合集」，新名称会创建合集。',
                                                  'Optional. A new name creates a collection.'))

        def add(e):
            name = (post.value or '').strip().removesuffix('.md')
            collection = (coll.value or '').strip()
            error = self.validate_post_name(name, collection)
            if error:
                post.error = error
                self.page.update()
                return
            post.error = None
            if self.busy:
                self.snack(self.copy('请等待当前操作完成。', 'Wait for the current task to finish.'), True)
                return
            self.close_dlg(dlg)
            self.do_add_post(name, collection or None)

        post.on_submit = add
        coll.on_submit = add
        dlg = ft.AlertDialog(title=ft.Text(self.t('add_post')),
                            content=ft.Container(ft.Column([post, coll], tight=True, spacing=20), width=420),
                            actions=[ft.TextButton(self.t('cancel'), on_click=lambda e: self.close_dlg(dlg)),
                                     self.primary_button(self.copy('创建文章', 'Create post'), ft.Icons.ADD, add)])
        self.open_dialog(dlg)

    def validate_post_name(self, name, collection):
        from mainTools.path_utils import get_posts_path
        if not name:
            return self.t('please_input_post')
        reserved = {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}
        for value in (name, collection):
            if value and (value in {'.', '..'} or re.search(r'[<>:"/\\|?*\x00-\x1f]', value)
                          or value.endswith(('.', ' ')) or value.split('.')[0].upper() in reserved):
                return self.copy('名称不能包含路径、特殊字符或系统保留名称。', 'Use a valid filename without paths or reserved characters.')
        if collection.casefold() in {'images', 'waterfallgraph'}:
            return self.copy('这是系统目录，请使用其他合集名称。', 'This folder is reserved. Choose another collection name.')
        if os.path.exists(os.path.join(get_posts_path(), collection or 'Markdowns', name + '.md')):
            return self.copy('同名文章已存在，请换一个名称。', 'A post with this name already exists.')
        return None

    def run_operation(self, label, operation, on_success=None):
        """Serialize commands that temporarily replace input; never block the UI."""
        if not self.operation_lock.acquire(blocking=False):
            self.snack(self.copy('请等待当前操作完成。', 'Wait for the current task to finish.'), True)
            return False
        self.busy = True
        self.status_text.value = label
        self.task_progress.visible = True
        self.page.update()

        async def run():
            try:
                result = await asyncio.to_thread(operation)
                if isinstance(result, str) and (result.startswith('Error:') or 'aborted.' in result):
                    raise RuntimeError(result)
                self.is_cache_valid = False
                if on_success:
                    on_success()
                if self.current_view == 'posts':
                    self.refresh_post_results()
                elif self.current_view == 'dashboard':
                    self.build_ui()
                self.snack(self.copy('已完成：', 'Completed: ') + label)
            except Exception as exc:
                self.snack(self.copy('操作失败：', 'Operation failed: ') + str(exc), True)
            finally:
                self.busy = False
                self.operation_lock.release()
                self.task_progress.visible = False
                self.page.update()
        self.page.run_task(run)
        return True

    def do_add_post(self, post, coll):
        def operation():
            error = self.validate_post_name(post, coll or '')
            if error:
                raise ValueError(error)
            with mock_input(post, coll or '', 'n'):
                return self.commands['AddPost']().execute()
        def reveal():
            self.expanded_collections.add(coll or 'Markdowns')
            self.search_query = ''
            if self.current_view == 'posts':
                self.search_field.value = ''
        return self.run_operation(self.t('add_post') + ' / ' + post, operation, reveal)

    def do_del_post(self, post, coll):
        def operation():
            with mock_input(post, coll or '', 'y'):
                return self.commands['DeletePost']().execute()
        self.run_operation(self.t('delete_post') + ' / ' + post, operation)

    def do_del_coll(self, coll):
        def operation():
            with mock_input(coll, 'y'):
                return self.commands['DeleteCollection']().execute()
        self.run_operation(self.t('delete_collection') + ' / ' + coll, operation)

    def exec_generate(self, e):
        self.run_operation(self.t('generate'), lambda: self.commands['Generate']().execute())

    def exec_init(self, e):
        """初始化博客 - 带详细进度条"""
        # 创建进度对话框
        progress_bar = ft.ProgressBar(width=500, value=0)
        status_text = ft.Text("准备初始化...", size=14, weight=ft.FontWeight.BOLD)
        detail_text = ft.Text("", size=12, color=self.CLR_TEXT_SECONDARY)
        log_text = ft.Text(
            "", size=11, color=self.CLR_TEXT, selectable=True)

        progress_dlg = ft.AlertDialog(
            title=ft.Text("初始化博客框架"),
            content=ft.Container(
                content=ft.Column([
                    progress_bar,
                    ft.Container(height=10),
                    status_text,
                    detail_text,
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Column(
                            [log_text], scroll=ft.ScrollMode.AUTO),
                        height=200,
                        bgcolor=self.CLR_ACCENT_SOFT,
                        border_radius=5,
                        padding=10,
                    ),
                ], tight=True, spacing=5),
                width=600,
            ),
            modal=True,
        )
        self.open_dialog(progress_dlg)
        self.page.update()

        def init_task():
            """在后台线程执行初始化"""
            try:
                # 创建一个自定义的 print 函数来捕获输出
                original_print = builtins.print

                def custom_print(*args, **kwargs):
                    """捕获 print 输出并显示在对话框中"""
                    message = ' '.join(str(arg) for arg in args)
                    log_text.value += message + '\n'
                    self.page.update()
                    original_print(*args, **kwargs)

                # 替换 print 函数
                builtins.print = custom_print

                try:
                    # 阶段1: 环境检查 (0-20%)
                    progress_bar.value = 0.05
                    status_text.value = "检查环境..."
                    detail_text.value = "检查 Git 和 Node.js"
                    self.page.update()

                    # 执行初始化命令
                    from mainTools.commands import InitBlog
                    init_cmd = InitBlog()

                    # 模拟进度更新（因为 InitBlog 内部有多个阶段）
                    def update_progress(stage, progress, message, detail=""):
                        progress_bar.value = progress
                        status_text.value = message
                        detail_text.value = detail
                        self.page.update()

                    # 开始执行
                    update_progress(1, 0.1, "检查环境...", "Git 和 Node.js")
                    time.sleep(0.3)

                    # 执行初始化（这会输出到 custom_print）
                    result = init_cmd.execute()

                    # 完成
                    progress_bar.value = 1.0
                    status_text.value = "初始化完成！"
                    detail_text.value = ""
                    self.page.update()

                    time.sleep(1)

                finally:
                    # 恢复原始 print 函数
                    builtins.print = original_print

                # 关闭进度对话框
                progress_dlg.open = False
                self.page.update()

                # 显示成功消息
                self.snack(self.t('operation_success'))

                # 刷新UI以显示所有功能
                self.build_ui()

            except Exception as ex:
                # 恢复原始 print 函数
                builtins.print = original_print

                # 关闭进度对话框
                progress_dlg.open = False
                self.page.update()

                # 显示错误消息
                self.snack(f"{self.t('error')}: {ex}", True)
                traceback.print_exc()

        # 使用Flet的run_thread在后台执行
        threading.Thread(target=lambda: self.page.run_thread(
            init_task), daemon=True).start()

    def exec_build(self, e):
        """构建项目"""
        # 创建进度对话框
        progress_bar = ft.ProgressBar(width=400, value=0)
        status_text = ft.Text("准备构建...", size=14)
        detail_text = ft.Text("", size=12, color=self.CLR_TEXT_SECONDARY)

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
        self.open_dialog(progress_dlg)
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
        """启动编辑器 - 带进度条和局域网选项"""
        # 如果已经在运行，直接打开窗口
        if self.editor_running and self.editor_url:
            self.open_editor_window(e)
            return

        # 创建局域网访问选择对话框
        def on_lan_choice(allow_lan):
            """用户选择是否允许局域网访问后的回调"""
            choice_dlg.open = False
            self.page.update()
            self._start_editor_with_option(allow_lan)

        choice_dlg = ft.AlertDialog(
            title=ft.Text("启动编辑器"),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("是否允许局域网内其他设备访问编辑器？", size=16,
                            weight=ft.FontWeight.BOLD),
                    ft.Container(height=10),
                    ft.Text("• 仅本机：只能在本机访问（127.0.0.1）",
                            size=13, color=self.CLR_TEXT),
                    ft.Text("• 局域网：局域网内设备可通过本机IP访问", size=13,
                            color=self.CLR_TEXT),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Text("注意：允许局域网访问会暴露编辑器给局域网内所有设备",
                                        size=12, color=self.CLR_WARN),
                        bgcolor=self.CLR_ACCENT_SOFT,
                        padding=10,
                        border_radius=8,
                    ),
                ], spacing=5),
                width=450,
            ),
            actions=[
                ft.TextButton(
                    "仅本机",
                    on_click=lambda e: on_lan_choice(False),
                    icon=ft.Icons.COMPUTER,
                ),
                ft.Button(
                    "允许局域网",
                    on_click=lambda e: on_lan_choice(True),
                    icon=ft.Icons.WIFI,
                    bgcolor=self.CLR_ACCENT,
                    color=self.CLR_SURFACE,
                ),
            ],
        )
        self.open_dialog(choice_dlg)
        self.page.update()

    def _start_editor_with_option(self, allow_lan=False):
        """实际启动编辑器（带局域网选项）"""
        # 如果已经在运行，直接打开窗口
        if self.editor_running and self.editor_url:
            self.open_editor_window(None)
            return

        # 保存局域网设置
        self.editor_allow_lan = allow_lan

        # 创建进度对话框
        progress_bar = ft.ProgressBar(width=400, value=0)
        status_text = ft.Text("准备启动编辑器...", size=14)
        detail_text = ft.Text("", size=12, color=self.CLR_TEXT_SECONDARY)

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
        self.open_dialog(progress_dlg)
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
                # 阶段1: 清理旧的开发服务器
                progress_bar.value = 0.05
                status_text.value = "清理旧的开发服务器..."
                detail_text.value = "检查端口占用"
                self.page.update()

                # 杀死所有 npm run dev 进程
                try:
                    if os.name == 'nt':
                        # Windows: 杀死所有 node.exe 进程（运行 vite 的）
                        subprocess.run('taskkill /F /IM node.exe /T',
                                       shell=True,
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)
                        print("[Editor] Killed existing node processes")
                        time.sleep(1)  # 等待端口释放
                    else:
                        # Linux/Mac: 杀死 vite 进程
                        subprocess.run(['pkill', '-f', 'vite'],
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)
                        print("[Editor] Killed existing vite processes")
                        time.sleep(1)
                except Exception as e:
                    print(
                        f"[Editor] Warning: Failed to kill old processes: {e}")

                # 阶段2: 启动开发服务器
                progress_bar.value = 0.1
                status_text.value = "启动开发服务器..."
                detail_text.value = "npm run dev"
                self.page.update()

                # 使用 path_utils 中的函数获取正确的基础路径
                from mainTools.path_utils import get_base_path
                base_path = get_base_path()

                print(f"[Editor] Base path: {base_path}")

                # 检查 package.json 是否存在
                package_json_path = os.path.join(base_path, 'package.json')
                if not os.path.exists(package_json_path):
                    raise Exception(
                        f"未找到 package.json，请确保在博客根目录运行\n路径: {package_json_path}")

                # 检查 node_modules 是否存在
                node_modules_path = os.path.join(base_path, 'node_modules')
                if not os.path.exists(node_modules_path):
                    raise Exception(
                        f"未找到 node_modules，请先运行 'npm install'\n路径: {node_modules_path}")

                # 启动开发服务器
                # 根据 allow_lan 决定是否添加 --host 参数
                dev_command = 'npm run dev -- --host 0.0.0.0' if allow_lan else 'npm run dev'

                if os.name == 'nt':
                    self.dev_server_process = subprocess.Popen(
                        dev_command,
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
                    if allow_lan:
                        cmd = ['npm', 'run', 'dev', '--', '--host', '0.0.0.0']
                    else:
                        cmd = ['npm', 'run', 'dev']
                    self.dev_server_process = subprocess.Popen(
                        cmd,
                        cwd=base_path,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True,
                        encoding='utf-8',
                        errors='replace'
                    )

                print(
                    f"[Editor] Dev server process started with PID: {self.dev_server_process.pid}")
                print(
                    f"[Editor] Command: {dev_command if os.name == 'nt' else cmd}")

                # 阶段3: 解析端口号
                progress_bar.value = 0.3
                status_text.value = "等待开发服务器就绪..."
                detail_text.value = "解析端口号"
                self.page.update()

                port_pattern = re.compile(
                    r'Local:\s+https?://(?:localhost|127\.0\.0\.1):(\d+)')
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
                            print(f"[Editor] Port detected: {frontend_port}")
                            break

                    if self.dev_server_process.poll() is not None:
                        raise Exception(
                            f"开发服务器启动失败 (退出码: {self.dev_server_process.returncode})")

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

                log_thread = threading.Thread(
                    target=output_dev_server_logs, daemon=True)
                log_thread.start()

                # 阶段4: 启动后端服务器
                progress_bar.value = 0.5
                status_text.value = "启动后端API服务器..."
                detail_text.value = "FastAPI server"
                self.page.update()

                # 生成端口和 token
                import secrets
                import socket

                def find_free_port():
                    """查找可用端口"""
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(('', 0))
                        s.listen(1)
                        port = s.getsockname()[1]
                    return port

                self.editor_port = find_free_port()
                self.editor_token = secrets.token_urlsafe(32)

                print(f"[Editor] Backend port: {self.editor_port}")
                print(f"[Editor] Auth token: {self.editor_token[:16]}...")

                # 用于捕获服务器启动错误
                server_error = []

                # 在独立线程启动 uvicorn（不使用 Flet 的 run_thread）
                def start_uvicorn_server():
                    try:
                        print(f"[SERVER] Thread started")

                        # 确保 mainTools 在路径中
                        maintools_path = os.path.join(
                            sys._MEIPASS if getattr(
                                sys, 'frozen', False) else os.path.dirname(__file__),
                            'mainTools'
                        )
                        if maintools_path not in sys.path:
                            sys.path.insert(0, maintools_path)

                        print(f"[SERVER] Importing editor_server...")

                        # 导入 editor_server 模块
                        from mainTools import editor_server

                        # 设置全局变量
                        editor_server.SERVER_PORT = self.editor_port
                        editor_server.AUTH_TOKEN = self.editor_token
                        editor_server.ALLOW_LAN_MODE = allow_lan

                        # 配置CORS
                        editor_server.configure_cors()

                        print(
                            f"[SERVER] Configuration set (LAN mode: {allow_lan})")
                        print(
                            f"[SERVER] Starting uvicorn on port {self.editor_port}...")

                        # 启动 uvicorn
                        import uvicorn

                        # 创建配置
                        # 根据用户选择决定绑定地址
                        bind_host = "0.0.0.0" if allow_lan else "127.0.0.1"
                        print(
                            f"[SERVER] Binding to {bind_host} (LAN: {allow_lan})")

                        config = uvicorn.Config(
                            editor_server.app,
                            host=bind_host,
                            port=self.editor_port,
                            log_level="info",
                            loop="asyncio",
                            access_log=False,
                        )

                        server = uvicorn.Server(config)

                        print(f"[SERVER] Uvicorn server created, starting...")

                        # 启动服务器（阻塞调用）
                        server.run()

                    except Exception as e:
                        error_msg = f"Server startup error: {e}"
                        print(f"[SERVER] {error_msg}")
                        import traceback
                        traceback.print_exc()
                        server_error.append(error_msg)

                # 启动服务器线程（使用标准 threading，不依赖 Flet）
                print(f"[Editor] Creating server thread...")
                server_thread = threading.Thread(
                    target=start_uvicorn_server, daemon=True)
                server_thread.start()
                self.editor_server_thread = server_thread

                print(
                    f"[Editor] Server thread started, waiting for it to be ready...")

                # 阶段5: 等待服务器就绪
                progress_bar.value = 0.7
                status_text.value = "等待后端服务器就绪..."
                detail_text.value = "检查健康状态"
                self.page.update()

                # 等待服务器启动（通过健康检查）
                max_wait = 30  # 增加等待时间到 15 秒
                server_ready = False

                import requests
                for i in range(max_wait):
                    # 检查是否有服务器启动错误
                    if server_error:
                        raise Exception(f"服务器启动失败: {server_error[0]}")

                    time.sleep(0.5)

                    try:
                        # 尝试访问健康检查端点
                        print(
                            f"[Editor] Health check attempt {i+1}/{max_wait} on port {self.editor_port}")
                        response = requests.get(
                            f"http://127.0.0.1:{self.editor_port}/api/health",
                            headers={"X-Auth-Token": self.editor_token},
                            timeout=2
                        )
                        if response.status_code == 200:
                            server_ready = True
                            print(
                                f"[Editor] Server is ready! Response: {response.json()}")
                            break
                        else:
                            print(
                                f"[Editor] Health check returned status {response.status_code}")
                    except requests.exceptions.ConnectionError as e:
                        # 服务器还未启动，继续等待
                        if i % 4 == 0:  # 每2秒打印一次
                            print(
                                f"[Editor] Server not ready yet, waiting... ({i+1}/{max_wait})")
                        continue
                    except Exception as e:
                        print(
                            f"[Editor] Health check error: {type(e).__name__}: {e}")
                        if i % 4 == 0:  # 每2秒打印一次
                            print(
                                f"[Editor] Waiting for server... ({i+1}/{max_wait})")
                        continue

                if not server_ready:
                    raise Exception("等待服务器启动超时")

                # 阶段6: 打开浏览器
                progress_bar.value = 0.9
                status_text.value = "打开浏览器..."
                detail_text.value = ""
                self.page.update()

                # 构建访问URL
                if allow_lan:
                    # 获取本机局域网IP
                    def get_local_ip():
                        try:
                            s = socket.socket(
                                socket.AF_INET, socket.SOCK_DGRAM)
                            s.connect(("8.8.8.8", 80))
                            ip = s.getsockname()[0]
                            s.close()
                            return ip
                        except:
                            return "127.0.0.1"

                    local_ip = get_local_ip()
                    self.editor_url = f"http://{local_ip}:{frontend_port}/#/editor?token={self.editor_token}&api_port={self.editor_port}"

                    # 自动配置防火墙的函数
                    def configure_firewall(e):
                        try:
                            # 显示进度
                            firewall_status = ft.Text(
                                "正在配置防火墙...", size=12, color=ft.Colors.BLUE)
                            lan_info_dlg.content.content.controls.append(
                                firewall_status)
                            self.page.update()

                            # Windows 防火墙规则
                            if os.name == 'nt':
                                # 添加前端端口规则
                                cmd1 = f'netsh advfirewall firewall add rule name="KMBlog Editor Frontend (Port {frontend_port})" dir=in action=allow protocol=TCP localport={frontend_port}'
                                result1 = subprocess.run(
                                    cmd1, shell=True, capture_output=True, text=True)

                                # 添加后端端口规则
                                cmd2 = f'netsh advfirewall firewall add rule name="KMBlog Editor Backend (Port {self.editor_port})" dir=in action=allow protocol=TCP localport={self.editor_port}'
                                result2 = subprocess.run(
                                    cmd2, shell=True, capture_output=True, text=True)

                                if result1.returncode == 0 and result2.returncode == 0:
                                    firewall_status.value = "防火墙规则已添加成功"
                                    firewall_status.color = ft.Colors.GREEN
                                else:
                                    firewall_status.value = "添加失败，请以管理员身份运行程序"
                                    firewall_status.color = ft.Colors.RED
                            else:
                                firewall_status.value = "仅支持 Windows 系统自动配置"
                                firewall_status.color = ft.Colors.ORANGE

                            self.page.update()
                        except Exception as ex:
                            firewall_status.value = f"配置失败: {str(ex)}"
                            firewall_status.color = ft.Colors.RED
                            self.page.update()

                    # 显示局域网访问信息
                    lan_info_dlg = ft.AlertDialog(
                        title=ft.Text("编辑器已启动（局域网模式）"),
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("本机访问地址：", size=14,
                                        weight=ft.FontWeight.BOLD),
                                ft.Container(
                                    content=ft.Text(
                                        f"http://localhost:{frontend_port}/#/editor?token={self.editor_token}&api_port={self.editor_port}",
                                        size=12,
                                        selectable=True,
                                    ),
                                    bgcolor=self.CLR_ACCENT_SOFT,
                                    padding=10,
                                    border_radius=5,
                                ),
                                ft.Container(height=10),
                                ft.Text("局域网访问地址：", size=14,
                                        weight=ft.FontWeight.BOLD),
                                ft.Container(
                                    content=ft.Text(
                                        self.editor_url,
                                        size=12,
                                        selectable=True,
                                    ),
                                    bgcolor=self.CLR_ACCENT_SOFT,
                                    padding=10,
                                    border_radius=5,
                                ),
                                ft.Container(height=15),
                                ft.Text("局域网内其他设备可使用上方地址访问", size=13,
                                        color=self.CLR_ACCENT),
                                ft.Container(height=5),
                                ft.Text(
                                    "防火墙配置提示：", size=12, weight=ft.FontWeight.BOLD, color=self.CLR_WARN),
                                ft.Text(
                                    f"  • 前端端口：{frontend_port}", size=11, color=self.CLR_ACCENT),
                                ft.Text(
                                    f"  • 后端端口：{self.editor_port}", size=11, color=self.CLR_ACCENT),
                                ft.Text("  • 如果其他设备无法访问，请点击下方按钮配置防火墙",
                                        size=11, color=self.CLR_ACCENT),
                            ], spacing=5),
                            width=650,
                        ),
                        actions=[
                            ft.ElevatedButton(
                                "配置防火墙",
                                on_click=configure_firewall,
                                bgcolor=self.CLR_WARN,
                                color=self.CLR_SURFACE,
                            ),
                            ft.TextButton(
                                "关闭", on_click=lambda e: self.close_dlg(lan_info_dlg)),
                        ],
                    )

                    print(f"[Editor] LAN mode - Local IP: {local_ip}")
                    print(f"[Editor] Frontend port: {frontend_port}")
                    print(f"[Editor] Backend port: {self.editor_port}")
                else:
                    self.editor_url = f"http://localhost:{frontend_port}/#/editor?token={self.editor_token}&api_port={self.editor_port}"
                    lan_info_dlg = None

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

                # 如果是局域网模式，显示访问信息对话框
                if allow_lan and lan_info_dlg:
                    self.open_dialog(lan_info_dlg)
                    self.page.update()

                # 刷新UI以显示新按钮
                self.build_ui()

                self.snack("编辑器已启动", False)

            except Exception as ex:
                # 关闭进度对话框
                progress_dlg.open = False
                self.page.update()

                # 生成详细的错误信息
                error_msg = str(ex)
                error_details = []

                # 分析错误类型并提供解决方案
                if "开发服务器启动失败" in error_msg:
                    returncode = self.dev_server_process.returncode if hasattr(
                        self, 'dev_server_process') and self.dev_server_process else None

                    if returncode == 4294963238 or returncode == -1073741515:
                        error_details = [
                            "npm 命令未找到或无法执行",
                            "",
                            "可能的原因：",
                            "1. Node.js/npm 未安装",
                            "2. npm 不在系统 PATH 中",
                            "3. 权限不足",
                            "",
                            "解决方案：",
                            "1. 安装 Node.js (https://nodejs.org/)",
                            "2. 重启电脑使 PATH 生效",
                            "3. 以管理员身份运行",
                            "",
                            "验证安装：在命令行运行",
                            "  node --version",
                            "  npm --version"
                        ]
                    else:
                        error_details = [
                            f"开发服务器启动失败 (退出码: {returncode})",
                            "",
                            "请检查：",
                            "1. 是否运行了 'npm install'",
                            "2. package.json 是否存在",
                            "3. 端口 5173 是否被占用",
                            "",
                            "手动测试：在博客目录运行",
                            "  npm run dev"
                        ]

                elif "未找到 package.json" in error_msg:
                    error_details = [
                        "博客框架未正确初始化",
                        "",
                        "解决方案：",
                        "1. 点击 '初始化博客框架' 按钮",
                        "2. 或确保 exe 在博客根目录中",
                        "",
                        "正确的目录结构：",
                        "  KMBlog/",
                        "  ├── KMblogManager.exe",
                        "  ├── package.json",
                        "  ├── node_modules/",
                        "  └── src/"
                    ]

                elif "未找到 node_modules" in error_msg:
                    error_details = [
                        "依赖未安装",
                        "",
                        "解决方案：",
                        "在博客目录运行：",
                        "  npm install",
                        "",
                        "或点击 '初始化博客框架' 按钮"
                    ]

                else:
                    error_details = [
                        f"{error_msg}",
                        "",
                        "请查看控制台输出获取详细信息",
                        "或参考 EDITOR_TROUBLESHOOTING.md"
                    ]

                # 显示详细错误对话框
                error_text = "\n".join(error_details)

                error_dlg = ft.AlertDialog(
                    title=ft.Text("启动编辑器失败", color=self.CLR_BAD),
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(
                                error_text,
                                size=13,
                                selectable=True,
                            ),
                        ], scroll=ft.ScrollMode.AUTO),
                        width=500,
                        height=400,
                    ),
                    actions=[
                        ft.TextButton(
                            "关闭", on_click=lambda e: self.close_dialog(error_dlg)),
                    ],
                )

                self.open_dialog(error_dlg)
                self.page.update()

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
            self.snack("已打开编辑器窗口", False)
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

                # 停止后端服务器线程（uvicorn 在 daemon 线程中，会自动结束）
                # 注意：uvicorn 运行在 daemon 线程中，主程序退出时会自动停止
                # 这里只需要标记状态
                if hasattr(self, 'editor_server_thread') and self.editor_server_thread:
                    print("[Editor] Backend server thread will stop automatically")

                # 重置状态
                self.editor_running = False
                self.editor_url = None
                self.dev_server_process = None
                self.editor_server_thread = None
                self.editor_port = None
                self.editor_token = None

                # 刷新UI
                self.build_ui()

                self.snack("编辑器已关闭", False)

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
        print(
            f"[Editor Monitor] Target URL: http://127.0.0.1:{self.editor_port}/api/health")
        print(f"[Editor Monitor] Auth Token: {self.editor_token[:10]}...")

        startup_wait = 0
        while startup_wait < 10:
            # 检查编辑器是否已被关闭
            if not self.editor_running:
                print("[Editor Monitor] Editor stopped, exiting monitor")
                return

            try:
                print(
                    f"[Editor Monitor] Startup attempt {startup_wait + 1}/10")
                response = requests.get(
                    f"http://127.0.0.1:{self.editor_port}/api/health",
                    headers={"X-Auth-Token": self.editor_token},
                    timeout=5
                )
                print(
                    f"[Editor Monitor] Startup response: status={response.status_code}, body={response.text[:100]}")
                if response.status_code == 200:
                    print("[Editor Monitor] Server started successfully")
                    break
            except requests.exceptions.Timeout as e:
                print(f"[Editor Monitor] Startup timeout: {e}")
            except requests.exceptions.ConnectionError as e:
                print(f"[Editor Monitor] Startup connection error: {e}")
            except Exception as e:
                print(
                    f"[Editor Monitor] Startup error: {type(e).__name__}: {e}")
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
                print(
                    f"[Editor Monitor] Health check #{check_count} at {time.strftime('%H:%M:%S')}")

                # 检查进程是否还活着（只在进程存在时检查）
                if self.editor_server:
                    poll_result = self.editor_server.poll()
                    if poll_result is not None:
                        print(
                            f"[Editor Monitor] Server process died! Exit code: {poll_result}")
                        break
                    else:
                        print(
                            f"[Editor Monitor] Server process is alive (PID: {self.editor_server.pid})")
                else:
                    print("[Editor Monitor] Server process is None, exiting monitor")
                    return

                # 发送健康检查请求
                print(
                    f"[Editor Monitor] Sending GET request to http://127.0.0.1:{self.editor_port}/api/health")
                start_time = time.time()

                response = requests.get(
                    f"http://127.0.0.1:{self.editor_port}/api/health",
                    headers={"X-Auth-Token": self.editor_token},
                    timeout=10  # 增加到10秒超时
                )

                elapsed = time.time() - start_time
                print(
                    f"[Editor Monitor] Response received in {elapsed:.2f}s: status={response.status_code}")

                if response.status_code == 200:
                    # 服务器正常响应，重置失败计数
                    print(
                        f"[Editor Monitor] Health check OK (consecutive_failures reset from {consecutive_failures} to 0)")
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    print(
                        f"[Editor Monitor] Health check failed with status {response.status_code} (consecutive_failures: {consecutive_failures}/{max_failures})")
                    print(
                        f"[Editor Monitor] Response body: {response.text[:200]}")

                print(f"[Editor Monitor] Sleeping for 10 seconds...")
                time.sleep(10)  # 减少检查频率到每10秒

            except requests.exceptions.Timeout as e:
                consecutive_failures += 1
                print(
                    f"[Editor Monitor] Health check timeout (consecutive_failures: {consecutive_failures}/{max_failures})")
                print(f"[Editor Monitor] Timeout details: {e}")
                time.sleep(10)
            except requests.exceptions.ConnectionError as e:
                consecutive_failures += 1
                print(
                    f"[Editor Monitor] Health check connection error (consecutive_failures: {consecutive_failures}/{max_failures})")
                print(f"[Editor Monitor] Connection error details: {e}")
                time.sleep(10)
            except requests.exceptions.RequestException as e:
                consecutive_failures += 1
                print(
                    f"[Editor Monitor] Health check request exception (consecutive_failures: {consecutive_failures}/{max_failures})")
                print(f"[Editor Monitor] Exception type: {type(e).__name__}")
                print(f"[Editor Monitor] Exception details: {e}")
                time.sleep(10)
            except Exception as e:
                print(
                    f"[Editor Monitor] Unexpected error: {type(e).__name__}: {e}")
                consecutive_failures += 1
                import traceback
                traceback.print_exc()
                time.sleep(10)

            # 如果连续失败达到阈值，停止服务器
            if consecutive_failures >= max_failures:
                print(
                    f"[Editor Monitor] Max failures reached ({consecutive_failures}/{max_failures}), stopping server...")
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
            ft.Text(self.t('migrate_desc'), size=13, color=self.CLR_TEXT),
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
        self.open_dialog(dlg)
        self.page.update()

    def confirm_migrate(self, dlg):
        """确认迁移，开始执行"""
        self.close_dlg(dlg)

        # 创建进度对话框
        progress_bar = ft.ProgressBar(width=400, value=0)
        status_text = ft.Text(self.t('migrating'), size=14)
        detail_text = ft.Text("", size=12, color=self.CLR_TEXT_SECONDARY)

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
        self.open_dialog(progress_dlg)
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

    def show_update_options_dialog(self, e):
        """显示更新选项对话框"""
        # 先显示检查中的对话框
        checking_dlg = ft.AlertDialog(
            title=ft.Text("检查更新"),
            content=ft.Container(
                content=ft.Column([
                    ft.ProgressRing(),
                    ft.Text("正在检查更新...", size=14),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                padding=20,
            ),
        )
        self.open_dialog(checking_dlg)
        self.page.update()

        # 在后台线程中检查更新
        def check_and_show():
            try:
                # 重新检查更新
                print("[更新检查] 用户点击更新按钮，开始检查...")

                # 检查框架更新
                try:
                    import sys
                    if 'mainTools.update_framework' in sys.modules:
                        import importlib
                        importlib.reload(
                            sys.modules['mainTools.update_framework'])

                    from mainTools.update_framework import FrameworkUpdater
                    framework_updater = FrameworkUpdater()
                    framework_result = framework_updater.check_for_updates()

                    if framework_result['success']:
                        self.update_info['has_updates'] = framework_result['has_updates']
                        self.update_info['commits_behind'] = framework_result.get(
                            'commits_behind', 0)
                        print(
                            f"[更新检查] 框架更新检查完成: has_updates={framework_result['has_updates']}, commits_behind={framework_result.get('commits_behind', 0)}")
                    else:
                        print(
                            f"[更新检查] 框架更新检查失败: {framework_result.get('message', '未知错误')}")
                except Exception as e:
                    print(f"[更新检查] 框架更新检查异常: {e}")
                    import traceback
                    traceback.print_exc()

                # 检查管理工具更新
                try:
                    if 'mainTools.update_manager' in sys.modules:
                        import importlib
                        importlib.reload(
                            sys.modules['mainTools.update_manager'])

                    from mainTools.update_manager import ManagerUpdater
                    manager_updater = ManagerUpdater()
                    manager_result = manager_updater.check_for_updates()

                    if manager_result['success']:
                        self.update_info['manager_has_update'] = manager_result['has_update']
                        self.update_info['manager_version'] = manager_result.get(
                            'latest_version', 'Unknown')
                        print(
                            f"[更新检查] 管理工具更新检查完成: has_update={manager_result['has_update']}, version={manager_result.get('latest_version', 'Unknown')}")
                    else:
                        print(
                            f"[更新检查] 管理工具更新检查失败: {manager_result.get('message', '未知错误')}")
                except Exception as e:
                    print(f"[更新检查] 管理工具更新检查异常: {e}")
                    import traceback
                    traceback.print_exc()

                # 使用 run_task 在主线程中更新 UI
                async def update_ui():
                    print("[更新检查] 准备更新 UI...")
                    # 关闭检查对话框
                    checking_dlg.open = False
                    self.page.update()
                    print("[更新检查] 检查对话框已关闭")

                    # 短暂延迟，确保对话框关闭动画完成
                    import asyncio
                    await asyncio.sleep(0.1)

                    # 显示更新选项对话框
                    self._show_update_options_dialog_content()
                    print("[更新检查] 更新选项对话框已显示")

                self.page.run_task(update_ui)

            except Exception as e:
                print(f"[更新检查] 检查更新失败: {e}")
                import traceback
                traceback.print_exc()
                # 错误时也要在主线程中关闭对话框
                try:
                    checking_dlg.open = False
                    self.page.update()
                except:
                    pass
                self.snack(f"检查更新失败: {e}", True)

        import threading
        threading.Thread(target=check_and_show, daemon=True).start()

    def _show_update_options_dialog_content(self):
        """显示更新选项对话框内容（内部方法）"""
        options = []

        # 框架更新选项
        if self.update_info['has_updates']:
            options.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CODE,
                                color=self.CLR_ACCENT, size=30),
                        ft.Column([
                            ft.Text("更新博客框架", size=16,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text(f"有 {self.update_info['commits_behind']} 个新提交",
                                    size=12, color=self.CLR_TEXT_SECONDARY),
                        ], spacing=2, expand=True),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT,
                                color=self.CLR_TEXT_MUTED),
                    ], spacing=15),
                    padding=15,
                    border=ft.Border.all(1, self.CLR_BORDER),
                    border_radius=8,
                    bgcolor=self.CLR_SURFACE,
                    on_click=lambda e: self.close_and_show_framework_update(
                        dlg),
                    ink=True,
                )
            )

        # 管理工具更新选项
        if self.update_info['manager_has_update']:
            options.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SETTINGS_APPLICATIONS,
                                color=self.CLR_ACCENT, size=30),
                        ft.Column([
                            ft.Text("更新管理工具", size=16,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text(f"最新版本: {self.update_info['manager_version']}",
                                    size=12, color=self.CLR_TEXT_SECONDARY),
                        ], spacing=2, expand=True),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT,
                                color=self.CLR_TEXT_MUTED),
                    ], spacing=15),
                    padding=15,
                    border=ft.Border.all(1, self.CLR_BORDER),
                    border_radius=8,
                    bgcolor=self.CLR_SURFACE,
                    on_click=lambda e: self.close_and_show_manager_update(dlg),
                    ink=True,
                )
            )

        # 如果没有更新
        if not options:
            options.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CHECK_CIRCLE,
                                color=self.CLR_GOOD, size=50),
                        ft.Text("已是最新版本", size=16, color=self.CLR_TEXT),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=30,
                )
            )

        content = ft.Column([
            ft.Text("选择更新项目", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            ft.Column(options, spacing=10),
        ], tight=True, scroll=ft.ScrollMode.AUTO)

        dlg = ft.AlertDialog(
            title=ft.Text(""),
            content=content,
            actions=[
                ft.TextButton("取消", on_click=lambda e: self.close_dlg(dlg)),
            ] if options and (self.update_info['has_updates'] or self.update_info['manager_has_update']) else [
                ft.TextButton("确定", on_click=lambda e: self.close_dlg(dlg)),
            ],
        )
        self.open_dialog(dlg)
        self.page.update()

    def close_and_show_framework_update(self, dlg):
        """关闭选项对话框并显示框架更新对话框"""
        self.close_dlg(dlg)
        import time
        time.sleep(0.1)  # 短暂延迟，确保对话框关闭
        self.show_update_framework_dialog(None)

    def close_and_show_manager_update(self, dlg):
        """关闭选项对话框并显示管理工具更新对话框"""
        self.close_dlg(dlg)
        import time
        time.sleep(0.1)  # 短暂延迟，确保对话框关闭
        # 直接调用管理工具更新（强制显示）
        self.check_manager_update(force_show=True)

    def show_update_framework_dialog(self, e):
        """显示更新框架对话框"""
        content = ft.Column([
            ft.Text(self.t('update_framework_title'), size=20,
                    weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            ft.Text(self.t('update_framework_desc'),
                    size=13, color=self.CLR_TEXT),
        ], tight=True)

        dlg = ft.AlertDialog(
            title=ft.Text(""),
            content=content,
            actions=[
                ft.TextButton(self.t('cancel'),
                              on_click=lambda e: self.close_dlg(dlg)),
                ft.Button(self.t('update_confirm'),
                          on_click=lambda e: self.confirm_update_framework(
                              dlg),
                          bgcolor=self.CLR_ACCENT,
                          color=ft.Colors.WHITE),
            ],
        )
        self.open_dialog(dlg)
        self.page.update()

    def confirm_update_framework(self, dlg):
        """确认更新框架，开始执行"""
        self.close_dlg(dlg)

        # 创建进度对话框
        progress_bar = ft.ProgressBar(width=400, value=0)
        status_text = ft.Text(self.t('updating'), size=14)
        detail_text = ft.Text("", size=12, color=self.CLR_TEXT_SECONDARY)
        log_text = ft.Text(
            "", size=11, color=self.CLR_TEXT_MUTED, selectable=True)

        progress_dlg = ft.AlertDialog(
            title=ft.Text(self.t('update_framework_title')),
            content=ft.Container(
                content=ft.Column([
                    progress_bar,
                    ft.Container(height=10),
                    status_text,
                    detail_text,
                    ft.Container(height=10),
                    ft.Container(
                        content=log_text,
                            bgcolor=self.CLR_ACCENT_SOFT,
                        border_radius=5,
                        padding=10,
                    ),
                ], tight=True, spacing=5),
                width=600,
            ),
            modal=True,
        )
        self.open_dialog(progress_dlg)
        self.page.update()

        def update_task():
            try:
                # 强制重新加载模块，避免缓存问题
                import sys
                if 'mainTools.update_framework' in sys.modules:
                    import importlib
                    importlib.reload(sys.modules['mainTools.update_framework'])

                from mainTools.update_framework import FrameworkUpdater
                updater = FrameworkUpdater()

                # 1. 检查 Git 状态
                status_text.value = self.t('checking_git')
                progress_bar.value = 0.1
                detail_text.value = "检查 Git 仓库状态..."
                self.page.update()

                git_status = updater.check_git_status()
                if not git_status['success']:
                    raise Exception(git_status.get('message', 'Git 检查失败'))

                if not git_status['is_git_repo']:
                    raise Exception('当前目录不是 Git 仓库')

                log_text.value += f"Git 状态检查完成\n"
                log_text.value += f"  分支: {git_status.get('current_branch', 'unknown')}\n"
                if git_status.get('has_changes'):
                    log_text.value += f"  警告: 检测到未提交的更改\n"
                self.page.update()

                # 2. 备份用户文件
                status_text.value = self.t('backing_up')
                progress_bar.value = 0.2
                detail_text.value = "备份用户数据..."
                self.page.update()

                backup_result = updater.backup_user_files()
                if not backup_result['success']:
                    raise Exception(backup_result.get('message', '备份失败'))

                log_text.value += f"\n备份完成\n"
                log_text.value += f"  位置: {backup_result['backup_path']}\n"
                log_text.value += f"  文件数: {len(backup_result['backed_up_files'])}\n"
                self.page.update()

                # 3. 拉取最新代码
                status_text.value = self.t('pulling_code')
                progress_bar.value = 0.5
                detail_text.value = "从 GitHub 拉取最新代码..."
                self.page.update()

                pull_result = updater.pull_latest_code()
                if not pull_result['success']:
                    log_text.value += f"\n代码拉取失败，正在恢复备份...\n"
                    self.page.update()
                    updater.restore_user_files(backup_result['backup_path'])
                    raise Exception(pull_result.get('message', '拉取代码失败'))

                log_text.value += f"\n代码拉取成功\n"
                self.page.update()

                # 4. 恢复用户文件
                status_text.value = self.t('restoring_files')
                progress_bar.value = 0.7
                detail_text.value = "恢复用户数据..."
                self.page.update()

                restore_result = updater.restore_user_files(
                    backup_result['backup_path'])
                if not restore_result['success']:
                    raise Exception(restore_result.get('message', '恢复文件失败'))

                log_text.value += f"\n用户文件恢复完成\n"
                self.page.update()

                # 5. 安装 npm 依赖
                status_text.value = "安装依赖..."
                progress_bar.value = 0.75
                detail_text.value = "npm install（这可能需要几分钟）..."
                self.page.update()

                log_text.value += f"\n开始安装 npm 依赖...\n"
                self.page.update()

                npm_result = updater.install_dependencies()
                if npm_result['success']:
                    log_text.value += f"npm 依赖安装完成\n"
                else:
                    log_text.value += f"npm 依赖安装失败: {npm_result.get('message', '未知错误')}\n"
                    log_text.value += f"  请手动运行 'npm install'\n"
                self.page.update()

                # 6. 比较配置差异
                status_text.value = self.t('generating_report')
                progress_bar.value = 0.9
                detail_text.value = "分析配置差异..."
                self.page.update()

                compare_result = updater.compare_configs(
                    backup_result['backup_path'])
                differences = compare_result.get(
                    'differences', {}) if compare_result['success'] else {}

                if differences:
                    log_text.value += f"\n检测到配置变化:\n"
                    for file_name, diff in differences.items():
                        new_fields = diff.get('new_fields', [])
                        modified_fields = diff.get('modified_fields', [])
                        if new_fields:
                            log_text.value += f"  {file_name}: 新增 {len(new_fields)} 个字段\n"
                        if modified_fields:
                            log_text.value += f"  {file_name}: 修改 {len(modified_fields)} 个字段\n"
                else:
                    log_text.value += f"\n无配置文件变化\n"
                self.page.update()

                # 7. 生成更新报告
                report_result = updater.generate_update_report(
                    backup_result['backup_path'], differences)
                if report_result['success']:
                    log_text.value += f"\n更新报告已生成\n"
                    log_text.value += f"  位置: UPDATE_REPORT.md\n"

                # 更新完成
                progress_bar.value = 1.0
                status_text.value = self.t('update_success')
                detail_text.value = "框架更新完成！"
                log_text.value += f"\n{'='*40}\n"
                log_text.value += f"更新完成\n"
                log_text.value += f"\n下一步:\n"
                if npm_result['success']:
                    log_text.value += f"1. npm 依赖已自动安装\n"
                    log_text.value += f"2. 运行 npm run dev 测试博客\n"
                    log_text.value += f"3. 检查 UPDATE_REPORT.md 了解详情\n"
                else:
                    log_text.value += f"1. 运行 npm install 安装依赖\n"
                    log_text.value += f"2. 运行 npm run dev 测试博客\n"
                    log_text.value += f"3. 检查 UPDATE_REPORT.md 了解详情\n"
                self.page.update()

                import time
                time.sleep(2)

                # 关闭进度对话框
                progress_dlg.open = False
                self.page.update()

                # 重置更新状态，移除 badge
                self.update_info['has_updates'] = False
                self.update_info['commits_behind'] = 0

                # 重新构建侧边栏以移除 badge
                self.build_ui()

                # 显示成功消息
                self.snack(self.t('update_success'))

                # 如果管理工具也有更新，提示用户
                if self.update_info['manager_has_update']:
                    time.sleep(1)
                    self.show_manager_update_reminder()

            except Exception as ex:
                # 更新失败
                progress_bar.value = 0
                status_text.value = self.t('update_failed')
                detail_text.value = str(ex)
                log_text.value += f"\n错误: {ex}\n"
                self.page.update()

                import time
                time.sleep(3)

                # 关闭进度对话框
                progress_dlg.open = False
                self.page.update()

                # 显示错误消息
                self.snack(f"{self.t('update_failed')}: {ex}", True)

        # 使用Flet的run_thread在后台执行
        import threading
        threading.Thread(target=lambda: self.page.run_thread(
            update_task), daemon=True).start()

    def show_manager_update_reminder(self):
        """提醒用户管理工具也有更新"""
        dlg = ft.AlertDialog(
            title=ft.Text("提示"),
            content=ft.Text(
                f"管理工具也有新版本 ({self.update_info['manager_version']})，是否立即更新？",
                size=14
            ),
            actions=[
                ft.TextButton("稍后", on_click=lambda e: self.close_dlg(dlg)),
                ft.Button(
                    "立即更新",
                    on_click=lambda e: self.close_and_update_manager(dlg),
                    bgcolor=self.CLR_ACCENT,
                    color=ft.Colors.WHITE
                ),
            ],
        )
        self.open_dialog(dlg)
        self.page.update()

    def close_and_update_manager(self, dlg):
        """关闭提醒对话框并更新管理工具"""
        self.close_dlg(dlg)
        import time
        time.sleep(0.1)
        self.check_manager_update()

    def check_manager_update(self, force_show=False):
        """检查管理工具更新

        Args:
            force_show: 是否强制显示对话框（即使没有更新）
        """
        try:
            print(f"[管理工具更新] 开始检查更新 (force_show={force_show})")
            from mainTools.update_manager import ManagerUpdater
            updater = ManagerUpdater()

            # 检查更新
            result = updater.check_for_updates()
            print(f"[管理工具更新] 检查结果: {result}")

            if not result['success']:
                print(f"[管理工具更新] 检查失败: {result.get('message', '未知错误')}")
                if force_show:
                    # 如果是用户主动点击，显示错误信息
                    self.snack(
                        f"检查更新失败: {result.get('message', '未知错误')}", True)
                return

            if not result['has_update']:
                print(
                    f"[管理工具更新] 已是最新版本: {result.get('current_version', 'unknown')}")
                if force_show:
                    # 如果是用户主动点击，显示"已是最新版本"
                    self.show_no_update_dialog(
                        result.get('current_version', 'unknown'))
                return

            # 显示更新对话框
            print(f"[管理工具更新] 发现新版本，显示更新对话框")
            self.show_manager_update_dialog(result, updater)

        except Exception as e:
            print(f"[管理工具更新] 检查失败 - 异常: {e}")
            import traceback
            traceback.print_exc()
            if force_show:
                self.snack(f"检查更新失败: {e}", True)

    def show_no_update_dialog(self, current_version):
        """显示"已是最新版本"对话框"""
        dlg = ft.AlertDialog(
            title=ft.Text("管理工具更新"),
            content=ft.Column([
                ft.Icon(ft.Icons.CHECK_CIRCLE, size=64,
                        color=self.CLR_GOOD),
                ft.Container(height=10),
                ft.Text("已是最新版本", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(height=5),
                ft.Text(f"当前版本: {current_version}",
                        size=14, color=self.CLR_TEXT_SECONDARY),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
            actions=[
                ft.Button("确定", on_click=lambda e: self.close_dlg(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        self.open_dialog(dlg)
        self.page.update()

    def show_manager_update_dialog(self, update_info, updater):
        """显示管理工具更新对话框"""
        try:
            print(f"[管理工具更新] 显示更新对话框")
            print(f"[管理工具更新] 更新信息: {update_info}")

            # 安全获取更新说明
            release_notes = update_info.get('release_notes', '无更新说明')
            if not release_notes or release_notes.strip() == '':
                release_notes = '无更新说明'

            # 截断过长的更新说明
            if len(release_notes) > 200:
                display_notes = release_notes[:200] + "..."
            else:
                display_notes = release_notes

            content = ft.Column([
                ft.Text("发现管理工具新版本", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Text(
                    f"当前版本: {update_info.get('current_version', 'unknown')}", size=14),
                ft.Text(
                    f"最新版本: {update_info.get('latest_version', 'unknown')}", size=14),
                ft.Container(height=10),
                ft.Text("更新说明:", size=14, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Text(
                        display_notes,
                        size=12,
                        color=self.CLR_TEXT
                    ),
                    height=100,
                    padding=10,
                    border=ft.Border.all(1, self.CLR_BORDER),
                    border_radius=5,
                ),
                ft.Container(height=10),
                ft.Text("是否立即更新管理工具？", size=13, color=self.CLR_TEXT),
                ft.Text("（程序将自动关闭并重启）", size=11, color=self.CLR_WARN),
            ], tight=True, scroll=ft.ScrollMode.AUTO)

            dlg = ft.AlertDialog(
                title=ft.Text("管理工具更新"),
                content=content,
                actions=[
                    ft.TextButton(
                        "稍后更新", on_click=lambda e: self.close_dlg(dlg)),
                    ft.Button(
                        "立即更新",
                        on_click=lambda e: self.confirm_manager_update(
                            dlg, update_info, updater),
                        bgcolor=self.CLR_ACCENT,
                        color=ft.Colors.WHITE
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            # 使用 overlay 而不是 dialog 属性，避免被其他对话框覆盖
            self.open_dialog(dlg)
            self.page.update()
            print(f"[管理工具更新] 对话框已添加到 overlay 并显示")

        except Exception as e:
            print(f"[管理工具更新] 显示对话框失败: {e}")
            import traceback
            traceback.print_exc()
            self.snack(f"显示更新对话框失败: {e}", True)

    def confirm_manager_update(self, dlg, update_info, updater):
        """确认更新管理工具"""
        self.close_dlg(dlg)

        # 显示下载进度对话框
        progress_bar = ft.ProgressBar(width=450, value=0)
        status_text = ft.Text("正在下载...", size=14, weight=ft.FontWeight.BOLD)
        detail_text = ft.Text("", size=12, color=self.CLR_TEXT_SECONDARY)
        log_text = ft.Text(
            "", size=11, color=self.CLR_TEXT, selectable=True)

        progress_dlg = ft.AlertDialog(
            title=ft.Text("更新管理工具"),
            content=ft.Container(
                content=ft.Column([
                    status_text,
                    ft.Container(height=5),
                    detail_text,
                    ft.Container(height=10),
                    progress_bar,
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Column(
                            [log_text], scroll=ft.ScrollMode.AUTO),
                        height=120,
                        bgcolor=self.CLR_ACCENT_SOFT,
                        border_radius=5,
                        padding=10,
                    ),
                ], tight=True, spacing=0),
                width=500,
            ),
            modal=True,
        )

        self.open_dialog(progress_dlg)
        self.page.update()

        # 进度回调函数（在主线程中更新 UI）
        def progress_callback(stage, progress, message):
            """进度回调 - 线程安全的 UI 更新"""
            async def update_ui():
                try:
                    # 更新进度条
                    progress_bar.value = progress

                    # 更新状态文本
                    stage_names = {
                        'download': '下载中',
                        'extract': '解压中',
                        'install': '安装中'
                    }
                    status_text.value = stage_names.get(stage, stage)
                    detail_text.value = message

                    # 添加日志
                    log_text.value += f"[{stage}] {message}\n"

                    # 更新 UI
                    self.page.update()
                except Exception as e:
                    print(f"[UI更新] 错误: {e}")

            # 使用 page.run_task 确保在主线程中更新 UI
            try:
                self.page.run_task(update_ui)
            except Exception as e:
                print(f"[进度回调] 错误: {e}")

        async def update_task():
            try:
                log_text.value += "开始更新流程...\n"
                log_text.value += f"下载地址: {update_info['download_url']}\n"
                log_text.value += f"文件名: {update_info['asset_name']}\n\n"
                self.page.update()

                # 执行更新（传入进度回调）
                result = updater.download_and_update(
                    update_info['download_url'],
                    update_info['asset_name'],
                    progress_callback=progress_callback
                )

                if result['success']:
                    log_text.value += "\n下载完成\n"
                    status_text.value = "更新完成"
                    detail_text.value = "程序即将关闭并自动重启..."
                    progress_bar.value = 1.0
                    self.page.update()

                    import time
                    time.sleep(2)

                    log_text.value += "正在关闭程序...\n"
                    self.page.update()

                    # 关闭程序
                    await self.page.window.close()
                else:
                    raise Exception(result.get('message', '更新失败'))

            except Exception as ex:
                import traceback
                error_details = traceback.format_exc()

                log_text.value += f"\n错误: {ex}\n"
                log_text.value += f"\n详细信息:\n{error_details}\n"
                status_text.value = "更新失败"
                detail_text.value = str(ex)
                progress_bar.value = 0
                self.page.update()

                import time
                time.sleep(3)

                progress_dlg.open = False
                self.page.update()
                self.snack(f"更新失败: {ex}", True)

                print(f"[管理工具更新] 错误详情:\n{error_details}")

        # 直接使用 run_task 执行异步任务
        self.page.run_task(update_task)

    def confirm(self, title, msg, callback):
        """Confirmation dialog — refined style"""
        def ok(e):
            self.close_dlg(dlg)
            callback()

        dlg = ft.AlertDialog(
            title=ft.Text(title, size=16, weight=ft.FontWeight.W_600),
            content=ft.Text(msg, size=13, color=self.CLR_TEXT_SECONDARY),
            actions=[
                ft.TextButton(self.t('cancel'), on_click=lambda e: self.close_dlg(dlg)),
                ft.ElevatedButton(self.t('confirm'), on_click=ok,
                                  bgcolor=self.CLR_BAD, color="#ffffff",
                                  style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=4))),
            ],
        )
        self.open_dialog(dlg)
        self.page.update()

    def close_dlg(self, dlg):
        dlg.open = False
        self._modal_open = False
        self.page.update()

    def show_post_preview(self, post_name, collection=None):
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
                posts_path, collection or 'Markdowns', f'{post_name}.md')
            print(f"Checking: {markdowns_path}")  # 调试
            if os.path.exists(markdowns_path):
                file_path = markdowns_path
                print(f"Found in Markdowns")  # 调试
            elif collection is None:
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
                    ft.Icon(ft.Icons.TITLE, size=20, color=self.CLR_ACCENT),
                    ft.Text(metadata.get('title', post_name),
                            size=18, weight=ft.FontWeight.BOLD),
                ], spacing=10),
            ]

            if metadata.get('date'):
                preview_items.append(ft.Row([
                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=16,
                            color=self.CLR_TEXT_SECONDARY),
                    ft.Text(f"日期: {metadata['date']}",
                            size=13, color=self.CLR_TEXT),
                ], spacing=8))

            if metadata.get('tags'):
                tags = metadata['tags'] if isinstance(
                    metadata['tags'], list) else [metadata['tags']]
                preview_items.append(ft.Row([
                    ft.Icon(ft.Icons.TAG, size=16, color=self.CLR_TEXT_SECONDARY),
                    ft.Text(f"标签: {', '.join(tags)}", size=13,
                            color=self.CLR_TEXT),
                ], spacing=8))

            if metadata.get('categories'):
                cats = metadata['categories'] if isinstance(metadata['categories'], list) else [
                    metadata['categories']]
                preview_items.append(ft.Row([
                    ft.Icon(ft.Icons.CATEGORY, size=16,
                            color=self.CLR_TEXT_SECONDARY),
                    ft.Text(f"分类: {', '.join(cats)}", size=13,
                            color=self.CLR_TEXT),
                ], spacing=8))

            if metadata.get('pre'):
                preview_items.append(ft.Container(height=10))
                preview_items.append(
                    ft.Text("简介:", size=14, weight=ft.FontWeight.BOLD))
                preview_items.append(ft.Container(
                    content=ft.Text(
                        metadata['pre'], size=13, color=self.CLR_TEXT),
                    padding=10,
                    bgcolor=self.CLR_ACCENT_SOFT,
                    border_radius=8,
                ))

            # 显示内容预览（前500字符）
            body = (content.split('---', 2)[-1] if content.startswith('---') else content).strip()
            if body:
                preview_items.append(ft.Container(height=10))
                preview_items.append(
                    ft.Text("内容预览:", size=14, weight=ft.FontWeight.BOLD))
                preview_items.append(ft.Container(
                    content=ft.Markdown(body[:12000] + ("…" if len(body) > 12000 else ""), selectable=True),
                    padding=10,
                    bgcolor=self.CLR_ACCENT_SOFT,
                    border_radius=8,
                ))

            dlg = ft.AlertDialog(
                title=ft.Text(f"{post_name}"),
                content=ft.Container(
                    content=ft.Column(preview_items, spacing=8,
                                      scroll=ft.ScrollMode.AUTO),
                    width=600,
                    height=400,
                ),
                actions=[
                    ft.TextButton(
                        self.t('close'), on_click=lambda e: self.close_dlg(dlg)),
                ],
            )
            self.open_dialog(dlg)
            self.page.update()

        except Exception as e:
            self.snack(f"预览失败: {e}", True)

    def build_settings_view(self):
        """配置管理视图"""
        config_fields = {}
        list_fields = {}
        links_data = []
        self.settings_status = ft.Text(self.copy('配置已加载', 'Settings loaded'), size=13,
                                       color=self.CLR_TEXT_SECONDARY, expand=True)
        def mark_dirty(e=None):
            self.settings_dirty = True
            self.settings_status.value = self.copy('有未保存的修改 · Ctrl+S 保存', 'Unsaved changes · Ctrl+S to save')
            self.settings_status.color = self.CLR_WARN
            self.page.update()


        # Never replace unreadable settings with defaults on save.
        config_loaded = True
        # 加载当前配置
        try:
            from mainTools.commands import GetConfig
            get_config_cmd = GetConfig()
            config_result = get_config_cmd.execute()
            current_config = json.loads(config_result)
        except Exception as e:
            self.snack(f"加载配置失败: {e}", True)
            current_config = {}
            config_loaded = False

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
            # BackgroundImg 和 HeadImg 将使用图片上传组件，不在这里处理
            ('BackgroundImgOpacity', self.t('bg_opacity'), 'number'),
            ('BackgroundImgBlur', self.t('bg_blur'), 'number'),
            ('PostsPerPage', self.t('posts_per_page'), 'number'),
            ('ChangeInfoAndTipPosition', self.t('change_info_tip_pos'), 'bool'),
        ]

        # 主题配置部分
        form_rows.append(ft.Divider())
        form_rows.append(ft.Text(self.t('theme_config'), size=20, weight=ft.FontWeight.BOLD))

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
                    value=str(value) if value != '' else '300',
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

        # 图片上传区域
        form_rows.append(ft.Divider())
        form_rows.append(
            ft.Text(self.t('image_config'), size=20, weight=ft.FontWeight.BOLD, color=self.CLR_TEXT))

        # 获取项目根目录
        if getattr(sys, 'frozen', False):
            # 打包后：使用 exe 所在目录
            base_path = os.path.dirname(os.path.abspath(sys.executable))
        else:
            # 开发环境
            base_path = os.path.dirname(__file__)

        # 获取配置中的图片路径（相对路径，如 /assets/background.png）
        bg_img_filename = current_config.get(
            'BackgroundImg', '/assets/background.png')
        head_img_filename = current_config.get('HeadImg', '/assets/head.png')

        # 转换为绝对路径
        # 配置文件中是 /assets/xxx.png，实际文件在 /public/assets/xxx.png
        if bg_img_filename.startswith('/assets/'):
            # /assets/xxx.png -> public/assets/xxx.png
            bg_img_relative = 'public' + bg_img_filename
        elif bg_img_filename.startswith('/'):
            bg_img_relative = bg_img_filename[1:]
        else:
            bg_img_relative = bg_img_filename

        if head_img_filename.startswith('/assets/'):
            # /assets/xxx.png -> public/assets/xxx.png
            head_img_relative = 'public' + head_img_filename
        elif head_img_filename.startswith('/'):
            head_img_relative = head_img_filename[1:]
        else:
            head_img_relative = head_img_filename

        bg_img_path = os.path.join(base_path, bg_img_relative)
        head_img_path = os.path.join(base_path, head_img_relative)

        # 调试输出
        print(f"[Config] Base path: {base_path}")
        print(f"[Config] Background config value: {bg_img_filename}")
        print(f"[Config] Background absolute path: {bg_img_path}")
        print(f"[Config] Background exists: {os.path.exists(bg_img_path)}")
        print(f"[Config] Head config value: {head_img_filename}")
        print(f"[Config] Head absolute path: {head_img_path}")
        print(f"[Config] Head exists: {os.path.exists(head_img_path)}")

        # 背景图片上传状态（保存相对路径）
        bg_img_uploaded = [bg_img_filename]
        head_img_uploaded = [head_img_filename]

        def on_bg_upload(file_path):
            """背景图片上传回调"""
            result = self.process_config_image(file_path, 'BackgroundImg')
            if result:
                bg_img_uploaded[0] = result
                self.snack(f"背景图片已上传", False)
                config_fields['BackgroundImg'].value = result
                images_section.controls[0].controls[-1] = self.build_image_upload_widget(
                    '', file_path, on_bg_upload, width=400, height=250)
                mark_dirty()

        def on_head_upload(file_path):
            """头像图片上传回调"""
            result = self.process_config_image(file_path, 'HeadImg')
            if result:
                head_img_uploaded[0] = result
                self.snack(f"头像图片已上传", False)
                config_fields['HeadImg'].value = result
                images_section.controls[2].controls[-1] = self.build_image_upload_widget(
                    '', file_path, on_head_upload, width=200, height=200)
                mark_dirty()

        # 图片上传组件
        images_section = ft.Column([
            # 背景图片
            ft.Column([
                ft.Text(
                    self.t('background_img'),
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=self.CLR_TEXT
                ),
                ft.Text(
                    "用于博客主页的背景图片，建议尺寸：1920x1080px" if self.current_lang == 'zh' else "Background image for blog homepage, recommended size: 1920x1080px",
                    size=12,
                    color="#718096"
                ),
                ft.Container(height=8),
                self.build_image_upload_widget(
                    "",  # 标签已在上面显示
                    bg_img_path,
                    on_bg_upload,
                    width=400,
                    height=250
                ),
            ], spacing=0),

            ft.Container(height=24),

            # 头像图片
            ft.Column([
                ft.Text(
                    self.t('head_img'),
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=self.CLR_TEXT
                ),
                ft.Text(
                    "用于个人信息面板的头像，建议尺寸：200x200px" if self.current_lang == 'zh' else "Avatar for personal info panel, recommended size: 200x200px",
                    size=12,
                    color="#718096"
                ),
                ft.Container(height=8),
                self.build_image_upload_widget(
                    "",  # 标签已在上面显示
                    head_img_path,
                    on_head_upload,
                    width=200,
                    height=200
                ),
            ], spacing=0),
        ], spacing=0)

        form_rows.append(ft.Container(content=images_section, padding=10))

        # 保存上传的图片文件名到配置字段
        config_fields['BackgroundImg'] = type(
            'obj', (object,), {'value': bg_img_uploaded[0]})()
        config_fields['HeadImg'] = type(
            'obj', (object,), {'value': head_img_uploaded[0]})()

        form_rows.append(ft.Divider())
        form_rows.append(ft.Text(self.copy('基本信息', 'General'), size=20, weight=ft.FontWeight.BOLD))
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

        # Utterances 评论配置
        form_rows.append(ft.Divider())
        form_rows.append(ft.Text('Utterances 评论配置' if self.current_lang == 'zh' else 'Utterances Comments Configuration',
                         size=20, weight=ft.FontWeight.BOLD))

        # 从配置中读取 Utterances 设置
        utterances_config = current_config.get('UtterancesConfig', {})

        # 尝试从 GitHub 部署配置中读取仓库信息
        github_repo = ''
        try:
            config_path = os.path.join(
                os.path.dirname(__file__), 'src', 'config.js')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 尝试从 GitHubToken 注释附近找到仓库信息
                    # 或者从之前保存的部署配置中读取
                    pass
        except:
            pass

        # 如果配置中没有仓库信息，从用户输入获取
        if not github_repo:
            github_repo = utterances_config.get('repo', '')

        # Utterances 启用开关
        utterances_enabled = ft.Checkbox(
            label='启用 Utterances 评论系统' if self.current_lang == 'zh' else 'Enable Utterances Comments',
            value=utterances_config.get('enabled', False),
        )
        form_rows.append(ft.Container(content=utterances_enabled, padding=5))

        # GitHub 仓库配置
        utterances_repo_field = ft.TextField(
            label='GitHub 仓库 (格式: username/repo)' if self.current_lang == 'zh' else 'GitHub Repository (format: username/repo)',
            value=github_repo,
            width=400,
            hint_text="例如: iiishop/KMblog",
        )

        # 从 GitHub 配置获取仓库信息的按钮
        def load_from_deploy_config(e):
            """从 GitHub 配置中加载仓库信息"""
            try:
                # 从 github_config.json 中读取
                github_config_file = os.path.join(
                    os.path.dirname(__file__), 'github_config.json')
                if os.path.exists(github_config_file):
                    with open(github_config_file, 'r', encoding='utf-8') as f:
                        github_config = json.load(f)
                        repo_name = github_config.get('repo_name', '')
                        if repo_name:
                            utterances_repo_field.value = repo_name
                            self.snack('已从 GitHub 配置中加载仓库信息', False)
                            self.page.update()
                            return

                self.snack('未找到 GitHub 配置，请手动输入仓库信息', False)
            except Exception as ex:
                self.snack(f'读取部署配置失败: {ex}', True)

        load_deploy_btn = ft.TextButton(
            '从GitHub配置加载' if self.current_lang == 'zh' else 'Load from GitHub Config',
            icon=ft.Icons.DOWNLOAD,
            on_click=load_from_deploy_config,
        )

        repo_row = ft.Row([
            utterances_repo_field,
            load_deploy_btn,
        ], spacing=10)

        form_rows.append(ft.Container(content=repo_row, padding=5))

        # Issue 映射方式
        utterances_issue_mapping = ft.Dropdown(
            label='Issue 映射方式' if self.current_lang == 'zh' else 'Issue Mapping',
            value=utterances_config.get('issueMapping', 'pathname'),
            options=[
                ft.dropdown.Option('pathname', 'pathname - 使用路径'),
                ft.dropdown.Option('url', 'url - 使用完整URL'),
                ft.dropdown.Option('title', 'title - 使用文章标题'),
                ft.dropdown.Option('og:title', 'og:title - 使用 Open Graph 标题'),
            ],
            width=400,
        )
        form_rows.append(ft.Container(
            content=utterances_issue_mapping, padding=5))

        # Issue 标签
        utterances_label_field = ft.TextField(
            label='Issue 标签' if self.current_lang == 'zh' else 'Issue Label',
            value=utterances_config.get('label', 'comment'),
            width=300,
            hint_text="例如: comment, blog-comment",
        )
        form_rows.append(ft.Container(
            content=utterances_label_field, padding=5))

        # 主题选择
        utterances_theme = ft.Dropdown(
            label='主题 (留空自动匹配博客主题)' if self.current_lang == 'zh' else 'Theme (leave empty to auto-match)',
            value=utterances_config.get('theme', ''),
            options=[
                ft.dropdown.Option('', '自动匹配 (Auto)'),
                ft.dropdown.Option('github-light', 'GitHub Light'),
                ft.dropdown.Option('github-dark', 'GitHub Dark'),
                ft.dropdown.Option('preferred-color-scheme',
                                   'Preferred Color Scheme'),
                ft.dropdown.Option('github-dark-orange', 'GitHub Dark Orange'),
                ft.dropdown.Option('icy-dark', 'Icy Dark'),
                ft.dropdown.Option('dark-blue', 'Dark Blue'),
                ft.dropdown.Option('photon-dark', 'Photon Dark'),
            ],
            width=400,
        )
        form_rows.append(ft.Container(content=utterances_theme, padding=5))

        # 帮助文本
        help_text = ft.Text(
            '提示: 使用 Utterances 需要先在 GitHub 仓库中安装 Utterances App\n'
            '访问 https://github.com/apps/utterances 进行安装' if self.current_lang == 'zh' else
            'Tip: You need to install Utterances App in your GitHub repository first\n'
            'Visit https://github.com/apps/utterances to install',
            size=12,
            color="#718096",
        )
        form_rows.append(ft.Container(content=help_text, padding=10))

        # 存储 Utterances 配置字段
        config_fields['UtterancesConfig'] = {
            'enabled': utterances_enabled,
            'repo': utterances_repo_field,
            'issueMapping': utterances_issue_mapping,
            'label': utterances_label_field,
            'theme': utterances_theme,
        }

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

        def build_link_row(link_data):
            name_field = ft.TextField(label=self.t('link_name'), value=link_data.get('name', ''),
                                      col={'xs': 12, 'md': 4}, on_change=mark_dirty, border_radius=10)
            url_field = ft.TextField(label=self.t('link_url'), value=link_data.get('url', ''),
                                     col={'xs': 10, 'md': 7}, on_change=mark_dirty, border_radius=10)
            entry = {'name': name_field, 'url': url_field}
            def remove_link(e):
                links_data.remove(entry)
                links_container.controls.remove(row)
                mark_dirty()
            row = ft.ResponsiveRow([
                name_field, url_field,
                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=self.CLR_BAD,
                              tooltip=self.t('remove_item'), col={'xs': 2, 'md': 1}, on_click=remove_link),
            ], spacing=10, run_spacing=10)
            links_data.append(entry)
            return row

        for link in links:
            links_container.controls.append(build_link_row(link))

        def add_link(e):
            links_container.controls.append(build_link_row({'name': '', 'url': ''}))
            mark_dirty()

        add_link_btn = ft.Button(
            self.t('add_link'),
            icon=ft.Icons.ADD,
            on_click=add_link,
        )

        form_rows.append(ft.Container(content=links_container, padding=10))
        form_rows.append(ft.Container(content=add_link_btn, padding=5))

        def save_config(e):
            """保存配置"""
            if not config_loaded:
                self.snack(self.copy('配置未能加载，修复配置文件后请重新打开管理工具。',
                                     'Settings could not be loaded. Repair config.js and reopen the manager.'), True)
                return
            try:
                invalid = False
                limits = {'BackgroundImgOpacity': (0, 1, float), 'BackgroundImgBlur': (0, 100, float),
                          'PostsPerPage': (1, 1000, int), 'transitionDuration': (0, 10000, int)}
                for key, (minimum, maximum, convert) in limits.items():
                    field = config_fields[key]
                    try:
                        value = convert(field.value)
                        if not minimum <= value <= maximum:
                            raise ValueError()
                        field.error = None
                    except (TypeError, ValueError):
                        field.error = self.copy(f'请输入 {minimum} 到 {maximum} 之间的有效数值',
                                                     f'Enter a valid number from {minimum} to {maximum}')
                        invalid = True
                for link in links_data:
                    name, url = (link['name'].value or '').strip(), (link['url'].value or '').strip()
                    link['url'].error = None
                    if (name or url) and (not name or not re.match(r'^(https?://|mailto:)', url)):
                        link['url'].error = self.copy('请填写名称和完整的 http(s) 或 mailto 链接',
                                                           'Enter a name and an http(s) or mailto URL')
                        invalid = True
                if invalid:
                    self.snack(self.copy('请检查基本信息、主题或社交链接中的标记字段。',
                                         'Check the marked fields in General, Theme or Social links.'), True)
                    self.page.update()
                    return
                # 收集基本配置值
                config_updates = {}
                for key, field in config_fields.items():
                    # 特殊处理 UtterancesConfig
                    if key == 'UtterancesConfig':
                        utterances_fields = field
                        config_updates['UtterancesConfig'] = {
                            'enabled': utterances_fields['enabled'].value,
                            'repo': utterances_fields['repo'].value.strip(),
                            'issueMapping': utterances_fields['issueMapping'].value,
                            'label': utterances_fields['label'].value.strip(),
                            'theme': utterances_fields['theme'].value,
                            'themeMapping': {
                                'day': 'github-light',
                                'dark': 'github-dark',
                                'night': 'github-dark',
                                'bright': 'github-light'
                            }
                        }
                    elif isinstance(field, ft.Checkbox):
                        config_updates[key] = field.value
                    elif isinstance(field, ft.Dropdown):
                        config_updates[key] = field.value
                    else:
                        value = field.value
                        # 尝试转换为正确的类型
                        if key in ['BackgroundImgOpacity', 'BackgroundImgBlur']:
                            value = float(value) if value else 0.0
                        elif key in ['PostsPerPage', 'transitionDuration']:
                            value = int(value) if value else (
                                10 if key == 'PostsPerPage' else 300)
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
                    self.settings_dirty = False
                    self.settings_status.value = self.copy('所有修改已保存', 'All changes saved')
                    self.settings_status.color = self.CLR_GOOD
                    self.snack(self.copy('配置已保存', 'Settings saved'))
                except Exception as pwd_ex:
                    self.snack(f"{result}\n密码保存失败: {pwd_ex}", True)

            except Exception as ex:
                self.snack(f"保存失败: {ex}", True)
                import traceback
                traceback.print_exc()

        self.save_settings = save_config

        # Keep the actual controls mounted across section and main navigation changes.
        def style_fields(control):
            if isinstance(control, (ft.TextField, ft.Dropdown)):
                control.border_radius = 10
                control.border_color = self.CLR_BORDER
                control.focused_border_color = self.CLR_ACCENT
                control.text_size = 14
                control.width = None
                if isinstance(control, ft.Dropdown):
                    control.on_select = mark_dirty
                else:
                    control.on_change = mark_dirty
            elif isinstance(control, ft.Checkbox):
                control.on_change = mark_dirty
            for child in getattr(control, 'controls', []):
                style_fields(child)
            content = getattr(control, 'content', None)
            if isinstance(content, ft.Control):
                style_fields(content)

        sections = []
        heading, controls = None, []
        for control in form_rows[1:]:
            if isinstance(control, ft.Divider):
                if heading is not None:
                    sections.append((heading, controls))
                heading, controls = None, []
            elif heading is None and isinstance(control, ft.Text):
                heading = control.value
            else:
                style_fields(control)
                field = getattr(control, 'content', None)
                if isinstance(field, (ft.TextField, ft.Dropdown)):
                    wide = field.label in [self.t('author_desc'), self.t('project_url'),
                                           self.t('crypto_password')] or field in list_fields.values()
                    control.col = {'xs': 12, 'md': 12 if wide else 6}
                controls.append(control)
        if heading is not None:
            sections.append((heading, controls))
        general = self.copy('基本信息', 'General')
        sections.sort(key=lambda section: section[0] != general)
        panels = [ft.Container(ft.Column([
            ft.Text(title, size=19, weight=ft.FontWeight.W_600, color=self.CLR_TEXT),
            ft.ResponsiveRow(controls, spacing=16, run_spacing=16),
        ], spacing=16), padding=24, bgcolor=self.CLR_SURFACE, border_radius=14,
            border=ft.Border.all(1, self.CLR_BORDER), visible=index == 0)
            for index, (title, controls) in enumerate(sections)]
        def select_section(e):
            for index, panel in enumerate(panels):
                panel.visible = index == int(e.control.value)
            self.page.update()
        selector = ft.Dropdown(value='0', width=240, dense=True, border_radius=10,
                               border_color=self.CLR_BORDER, text_size=14,
                               options=[ft.dropdown.Option(str(index), title) for index, (title, _) in enumerate(sections)],
                               on_select=select_section)
        return ft.Column([
            ft.Row([ft.Text(self.t('settings'), size=26, weight=ft.FontWeight.W_700,
                            color=self.CLR_TEXT, expand=True),
                    self.primary_button(self.t('save_config'), ft.Icons.SAVE_OUTLINED, save_config)]),
            ft.Row([selector, self.settings_status], spacing=16),
            ft.ListView(panels, spacing=0, expand=True),
        ], spacing=18, expand=True)

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
            ft.Text('如果仓库不存在，将自动创建', size=12, color=self.CLR_TEXT_SECONDARY),
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

        self.open_dialog(dlg)
        self.page.update()

    def verify_github_token(self, token_field, status_text):
        """验证GitHub Token"""
        token = token_field.value.strip()
        if not token:
            status_text.value = "请输入Token"
            status_text.color = ft.Colors.RED
            self.page.update()
            return

        from mainTools.github_commands import VerifyGitHubToken
        verify_cmd = VerifyGitHubToken()
        result = verify_cmd.execute(token)

        if result['success']:
            status_text.value = f"{result['message']}"
            status_text.color = ft.Colors.GREEN
        else:
            status_text.value = f"{result['message']}"
            status_text.color = ft.Colors.RED

        self.page.update()

    def start_github_deploy(self, token, repo_name):
        """开始GitHub部署（使用run_thread）"""
        # 创建详细进度对话框
        progress_bar = ft.ProgressBar(width=400, value=0)
        status_text = ft.Text("准备部署...", size=14)
        detail_text = ft.Text("", size=12, color=self.CLR_TEXT_SECONDARY)

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

        self.open_dialog(loading_dlg)
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
                    self.open_dialog(success_dlg)
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
