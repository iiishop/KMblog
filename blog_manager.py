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
if getattr(sys, 'frozen', False):
    # 打包后：mainTools 在临时目录
    sys.path.insert(0, os.path.join(sys._MEIPASS, 'mainTools'))
else:
    # 开发环境
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mainTools'))

from mainTools.commands import Command


class BlogManagerGUI:
    def __init__(self, page: ft.Page):
        self.page = page

        # 初始化缩放因子（必须在 setup_page 之前）
        self.scale_factor = 1.0

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
        """设置页面属性"""
        self.page.title = "KMBlog Manager"

        # 获取屏幕分辨率并自适应窗口大小
        try:
            # 尝试获取屏幕尺寸
            screen_width = self.page.window.width if hasattr(
                self.page.window, 'width') else 1920
            screen_height = self.page.window.height if hasattr(
                self.page.window, 'height') else 1080

            # 如果无法获取，使用默认值
            if not screen_width or screen_width == 0:
                screen_width = 1920
            if not screen_height or screen_height == 0:
                screen_height = 1080

            print(f"[窗口] 检测到屏幕尺寸: {screen_width}x{screen_height}")

            # 根据屏幕分辨率计算合适的窗口大小
            # 目标：窗口占屏幕的 80-85%
            if screen_height <= 1080:
                # 1080p 或更小：使用较小的窗口
                window_width = min(1100, int(screen_width * 0.85))
                window_height = min(750, int(screen_height * 0.85))
                self.scale_factor = 0.85  # 缩放因子
                print(f"[窗口] 使用 1080p 优化尺寸")
            elif screen_height <= 1440:
                # 2K (1440p)：使用中等窗口
                window_width = min(1280, int(screen_width * 0.80))
                window_height = min(900, int(screen_height * 0.80))
                self.scale_factor = 1.0  # 标准尺寸
                print(f"[窗口] 使用 2K 标准尺寸")
            else:
                # 4K 或更大：使用较大窗口
                window_width = min(1600, int(screen_width * 0.75))
                window_height = min(1100, int(screen_height * 0.75))
                self.scale_factor = 1.15  # 放大因子
                print(f"[窗口] 使用 4K 优化尺寸")

            self.page.window.width = window_width
            self.page.window.height = window_height

            print(
                f"[窗口] 设置窗口尺寸: {window_width}x{window_height} (缩放: {self.scale_factor})")

        except Exception as e:
            # 如果出错，使用默认值
            print(f"[窗口] 无法检测屏幕尺寸，使用默认值: {e}")
            self.page.window.width = 1280
            self.page.window.height = 900
            self.scale_factor = 1.0

        self.page.padding = 0
        self.page.bgcolor = ft.Colors.GREY_50

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
            self.build_ui()
            print(f"[UI刷新] UI已重新构建")
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
                'editor_closed': '✅ 编辑器已关闭',
                'close_failed': '关闭失败',
                'configuring_firewall': '正在配置防火墙...',
                'firewall_success': '✅ 防火墙规则已添加成功！',
                'firewall_failed_admin': '❌ 添加失败，请以管理员身份运行程序',
                'firewall_failed': '❌ 配置失败',
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
                'editor_closed': '✅ Editor Closed',
                'close_failed': 'Close Failed',
                'configuring_firewall': 'Configuring firewall...',
                'firewall_success': '✅ Firewall rule added successfully!',
                'firewall_failed_admin': '❌ Failed, please run as administrator',
                'firewall_failed': '❌ Configuration failed',
                'has_commits': '{} new commits available',
                'latest_version': 'Latest version: {}',
                'cancel_btn': 'Cancel',
                'replace': 'Replace',
                'replace_cover_question': 'Replace cover image of {}?',
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
        action_buttons = []

        # 检查是否已初始化
        is_initialized = self.is_blog_initialized()

        if not is_initialized:
            # 未初始化：只显示初始化按钮（大号、醒目）
            action_buttons.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ROCKET_LAUNCH,
                                size=64, color=ft.Colors.WHITE),
                        ft.Text(self.t('init_blog'), size=20, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
                        ft.Text(self.t('click_to_init'), size=14, color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                                text_align=ft.TextAlign.CENTER),
                    ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=400,
                    height=200,
                    padding=30,
                    bgcolor=ft.Colors.PURPLE_600,
                    border_radius=16,
                    shadow=ft.BoxShadow(
                        blur_radius=20, color=ft.Colors.with_opacity(0.3, ft.Colors.PURPLE_600)),
                    on_click=self.exec_init,
                    animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
                )
            )
        else:
            # 已初始化：显示所有功能按钮
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
                self.action_btn(self.t('update_framework'), ft.Icons.SYSTEM_UPDATE,
                                self.show_update_options_dialog, ft.Colors.DEEP_PURPLE_600, '更新',
                                badge=(self.update_info['commits_behind'] + (1 if self.update_info['manager_has_update'] else 0)) if (self.update_info['has_updates'] or self.update_info['manager_has_update']) else None),
            ]

            # 编辑器按钮 - 根据状态显示不同的按钮
            if self.editor_running:
                action_buttons.append(
                    self.action_btn('打开编辑器', ft.Icons.OPEN_IN_BROWSER,
                                    self.open_editor_window, ft.Colors.PURPLE_600, '打开已运行的编辑器')
                )
                action_buttons.append(
                    self.action_btn(self.t('close_editor'), ft.Icons.STOP_CIRCLE,
                                    self.stop_editor, ft.Colors.RED_600, '停止编辑器服务')
                )
            else:
                action_buttons.append(
                    self.action_btn('启动编辑器', ft.Icons.EDIT,
                                    self.start_editor, ft.Colors.PURPLE_600, '本地Markdown编辑器')
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

    def action_btn(self, text, icon, onclick, color, desc="", badge=None):
        """操作按钮 - 改进版（支持徽章）

        Args:
            text: 按钮文本
            icon: 图标
            onclick: 点击事件
            color: 背景颜色
            desc: 描述文本
            badge: 徽章数字（如果 > 0 则显示红色徽章）
        """
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

        # 按钮内容
        button_content = ft.Column([
            ft.Icon(icon, size=36, color=ft.Colors.WHITE),
            ft.Text(text, size=14, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
            ft.Text(desc, size=11, color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                    text_align=ft.TextAlign.CENTER) if desc else ft.Container(height=0),
        ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        # 如果有徽章，使用 Stack 叠加徽章
        if badge and badge > 0:
            content = ft.Stack([
                button_content,
                ft.Container(
                    content=ft.Text(
                        str(badge) if badge < 100 else "99+",
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    bgcolor=ft.Colors.RED_600,
                    border_radius=12,
                    padding=ft.Padding(6, 2, 6, 2),
                    right=5,
                    top=5,
                    shadow=ft.BoxShadow(
                        blur_radius=4,
                        color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK)
                    ),
                ),
            ])
        else:
            content = button_content

        return ft.Container(
            content=content,
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
        """可复用的图片上传组件

        Args:
            label: 标签文字
            current_path: 当前图片路径（完整路径）
            on_upload_callback: 上传回调函数 callback(file_path)
            width: 图片宽度
            height: 图片高度
        """
        # 检查图片是否存在
        has_image = current_path and os.path.exists(current_path)

        # 调试输出
        print(
            f"[ImageWidget] Label: {label}, Path: {current_path}, Exists: {has_image}")

        def pick_image(e):
            """打开文件选择器"""
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)

            file_path = filedialog.askopenfilename(
                title=f"选择{label}",
                filetypes=[
                    ("图片文件", "*.png *.jpg *.jpeg *.webp *.gif"),
                    ("PNG", "*.png"),
                    ("JPEG", "*.jpg *.jpeg"),
                    ("WebP", "*.webp"),
                    ("GIF", "*.gif"),
                    ("所有文件", "*.*")
                ]
            )

            root.destroy()

            if file_path:
                on_upload_callback(file_path)

        # 构建图片显示内容
        if has_image:
            image_content = ft.Image(
                src=current_path,
                width=width,
                height=height,
                fit="cover",
                border_radius=8,
            )
            overlay = ft.Container(
                content=ft.Icon(ft.Icons.EDIT, size=24, color="#FFFFFF"),
                width=width,
                height=height,
                bgcolor=ft.Colors.with_opacity(0.7, "#000000"),
                border_radius=8,
                alignment=ft.Alignment(0, 0),
                visible=False,
            )
        else:
            image_content = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ADD_PHOTO_ALTERNATE,
                            size=36, color="#718096"),
                    ft.Text(self.t('click_to_upload'),
                            size=12, color="#A0AEC0"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                width=width,
                height=height,
                bgcolor=ft.Colors.with_opacity(0.05, "#FFFFFF"),
                border_radius=8,
                alignment=ft.Alignment(0, 0),
            )
            overlay = ft.Container()

        return ft.Container(
            content=ft.Column([
                ft.Text(label, size=14, weight=ft.FontWeight.BOLD,
                        color="#FFFFFF"),
                ft.Container(height=8),
                ft.Container(
                    content=ft.Stack([image_content, overlay]),
                    on_click=pick_image,
                    ink=True,
                    border=ft.Border.all(
                        1, ft.Colors.with_opacity(0.2, "#FFFFFF")),
                    border_radius=8,
                ),
            ], spacing=0),
            padding=10,
        )

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

        # 检查是否有封面图片
        from mainTools.path_utils import get_posts_path
        collection_path = os.path.join(get_posts_path(), collection_name)
        image_path = os.path.join(collection_path, 'image.png')
        has_image = os.path.exists(image_path)

        # 创建文件选择器（用于选择图片）
        def pick_image(e):
            """打开文件选择器选择图片"""
            # 使用 tkinter 的文件对话框
            import tkinter as tk
            from tkinter import filedialog

            # 创建隐藏的 tkinter 窗口
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)

            # 打开文件选择对话框
            file_path = filedialog.askopenfilename(
                title=f"选择 {collection_name} 的封面图片",
                filetypes=[
                    ("图片文件", "*.png *.jpg *.jpeg *.webp *.gif"),
                    ("PNG", "*.png"),
                    ("JPEG", "*.jpg *.jpeg"),
                    ("WebP", "*.webp"),
                    ("GIF", "*.gif"),
                    ("所有文件", "*.*")
                ]
            )

            root.destroy()

            if file_path:
                # 检查是否已有图片
                img_path = os.path.join(collection_path, 'image.png')
                if os.path.exists(img_path):
                    self.show_image_replace_dialog(
                        file_path, collection_name, collection_path)
                else:
                    self.process_collection_image(
                        file_path, collection_name, collection_path)

        def handle_file_pick(result, coll_name, coll_path):
            """处理文件选择结果（已废弃，使用 tkinter 代替）"""
            pass

        # 构建图片上传区域（仅支持点击上传，Flet 不支持从外部拖放文件）
        image_upload_area = ft.Container(
            content=ft.Stack([
                ft.Image(
                    src=image_path,
                    width=150,
                    height=100,
                    fit="cover",
                    border_radius=8,
                ) if has_image else ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ADD_PHOTO_ALTERNATE,
                                size=36, color=ft.Colors.GREY_400),
                        ft.Text(self.t('click_upload_cover'),
                                size=12, color=ft.Colors.GREY_500),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    width=150,
                    height=100,
                    bgcolor=ft.Colors.GREY_200,
                    border_radius=8,
                    alignment=ft.Alignment(0, 0),
                ),
                # 悬停时显示更换按钮
                ft.Container(
                    content=ft.Icon(ft.Icons.EDIT, size=24,
                                    color=ft.Colors.WHITE),
                    width=150,
                    height=100,
                    bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLACK),
                    border_radius=8,
                    alignment=ft.Alignment(0, 0),
                    visible=False,
                ) if has_image else ft.Container(),
            ]),
            padding=ft.Padding(0, 10, 0, 0),
            on_click=pick_image if not is_default else None,
            ink=True if not is_default else False,
        ) if not is_default else ft.Container()

        # 构建头部容器（增加高度以显示图片）
        header_content = ft.Column([
            ft.Row([
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
            # 显示封面图片（如果有）或上传按钮
            image_upload_area,
        ], spacing=5)

        header_container = ft.Container(
            content=header_content,
            padding=ft.Padding(12, 12, 12, 12),
            bgcolor=ft.Colors.BLUE_GREY_50 if not is_default else ft.Colors.GREY_100,
            border_radius=8,
            on_click=toggle_expand,
            ink=True,
        )

        # 不再使用 DragTarget，直接返回容器
        header = header_container

        # 文章列表 (展开时显示) - 移除拖拽功能
        posts_list = None
        if is_expanded:
            post_widgets = []
            for post_line in posts:
                post_widgets.append(self.build_post_item(
                    post_line, collection_name))

            posts_list = ft.Container(
                content=ft.Column(post_widgets, spacing=8),
                padding=ft.Padding(35, 10, 10, 10),
            )

        return ft.Column([
            header,
            posts_list if posts_list else ft.Container(),
        ], spacing=5)

    def build_post_item(self, line, source_collection):
        """构建文章项（不可拖拽）"""
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

        def on_hover(e):
            if e.data == "true":
                e.control.bgcolor = ft.Colors.BLUE_100
            else:
                e.control.bgcolor = ft.Colors.BLUE_50
            e.control.update()

        def on_delete(e):
            e.stop_propagation()
            self.confirm(
                self.t('confirm_delete'),
                self.t('confirm_delete_post').format(post_name),
                lambda: self.do_del_post(
                    post_name, None if source_collection == 'Markdowns' else source_collection)
            )

        # 构建文章卡片（不可拖拽）
        post_card = ft.Container(
            content=ft.Row([
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
        )

        return post_card

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
            self.snack(f"✅ 已设置 {collection_name} 的封面图片", False)

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
                        height=150,
                        fit="contain",
                    ),
                    border=ft.Border.all(2, ft.Colors.GREY_400),
                    border_radius=8,
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            ft.Icon(ft.Icons.ARROW_FORWARD, size=32, color=ft.Colors.BLUE_600),
            ft.Column([
                ft.Text(self.t('new_image'), size=14,
                        weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Image(
                        src=new_image_path,
                        width=200,
                        height=150,
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
                    bgcolor=ft.Colors.GREEN_600,
                    color=ft.Colors.WHITE,
                ),
            ],
        )

        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

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

    def close_dialog(self, dialog):
        """关闭对话框的辅助方法"""
        dialog.open = False
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
        """初始化博客 - 带详细进度条"""
        # 创建进度对话框
        progress_bar = ft.ProgressBar(width=500, value=0)
        status_text = ft.Text("准备初始化...", size=14, weight=ft.FontWeight.BOLD)
        detail_text = ft.Text("", size=12, color=ft.Colors.GREY_600)
        log_text = ft.Text(
            "", size=11, color=ft.Colors.GREY_700, selectable=True)

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
                        bgcolor=ft.Colors.GREY_100,
                        border_radius=5,
                        padding=10,
                    ),
                ], tight=True, spacing=5),
                width=600,
            ),
            modal=True,
        )
        self.page.overlay.append(progress_dlg)
        progress_dlg.open = True
        self.page.update()

        def init_task():
            """在后台线程执行初始化"""
            try:
                import time

                # 创建一个自定义的 print 函数来捕获输出
                original_print = __builtins__.print

                def custom_print(*args, **kwargs):
                    """捕获 print 输出并显示在对话框中"""
                    message = ' '.join(str(arg) for arg in args)
                    log_text.value += message + '\n'
                    self.page.update()
                    original_print(*args, **kwargs)

                # 替换 print 函数
                __builtins__.print = custom_print

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
                    __builtins__.print = original_print

                # 关闭进度对话框
                progress_dlg.open = False
                self.page.update()

                # 显示成功消息
                self.snack(self.t('operation_success'))

                # 刷新UI以显示所有功能
                self.build_ui()

            except Exception as ex:
                # 恢复原始 print 函数
                __builtins__.print = original_print

                # 关闭进度对话框
                progress_dlg.open = False
                self.page.update()

                # 显示错误消息
                self.snack(f"{self.t('error')}: {ex}", True)
                import traceback
                traceback.print_exc()

        # 使用Flet的run_thread在后台执行
        import threading
        threading.Thread(target=lambda: self.page.run_thread(
            init_task), daemon=True).start()

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
                            size=13, color=ft.Colors.GREY_700),
                    ft.Text("• 局域网：局域网内设备可通过本机IP访问", size=13,
                            color=ft.Colors.GREY_700),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Text("⚠️ 注意：允许局域网访问会暴露编辑器给局域网内所有设备",
                                        size=12, color=ft.Colors.ORANGE_700),
                        bgcolor=ft.Colors.ORANGE_50,
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
                    bgcolor=ft.Colors.BLUE_600,
                    color=ft.Colors.WHITE,
                ),
            ],
        )
        self.page.overlay.append(choice_dlg)
        choice_dlg.open = True
        self.page.update()

    def _start_editor_with_option(self, allow_lan=False):
        """实际启动编辑器（带局域网选项）"""
        # 如果已经在运行，直接打开窗口
        if self.editor_running and self.editor_url:
            self.open_editor_window(e)
            return

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
                            print(f"[Editor] ✅ Port detected: {frontend_port}")
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
                        print(f"[SERVER] ❌ {error_msg}")
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
                                f"[Editor] ✅ Server is ready! Response: {response.json()}")
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
                                    firewall_status.value = "✅ 防火墙规则已添加成功！"
                                    firewall_status.color = ft.Colors.GREEN
                                else:
                                    firewall_status.value = "❌ 添加失败，请以管理员身份运行程序"
                                    firewall_status.color = ft.Colors.RED
                            else:
                                firewall_status.value = "⚠️ 仅支持 Windows 系统自动配置"
                                firewall_status.color = ft.Colors.ORANGE

                            self.page.update()
                        except Exception as ex:
                            firewall_status.value = f"❌ 配置失败: {str(ex)}"
                            firewall_status.color = ft.Colors.RED
                            self.page.update()

                    # 显示局域网访问信息
                    lan_info_dlg = ft.AlertDialog(
                        title=ft.Text("✅ 编辑器已启动（局域网模式）"),
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
                                    bgcolor=ft.Colors.GREY_100,
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
                                    bgcolor=ft.Colors.BLUE_50,
                                    padding=10,
                                    border_radius=5,
                                ),
                                ft.Container(height=15),
                                ft.Text("📱 局域网内其他设备可使用上方地址访问", size=13,
                                        color=ft.Colors.BLUE_700),
                                ft.Container(height=5),
                                ft.Text(
                                    "⚠️ 防火墙配置提示：", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700),
                                ft.Text(
                                    f"  • 前端端口：{frontend_port}", size=11, color=ft.Colors.ORANGE_600),
                                ft.Text(
                                    f"  • 后端端口：{self.editor_port}", size=11, color=ft.Colors.ORANGE_600),
                                ft.Text("  • 如果其他设备无法访问，请点击下方按钮配置防火墙",
                                        size=11, color=ft.Colors.ORANGE_600),
                            ], spacing=5),
                            width=650,
                        ),
                        actions=[
                            ft.ElevatedButton(
                                "🔧 自动配置防火墙",
                                on_click=configure_firewall,
                                bgcolor=ft.Colors.ORANGE_400,
                                color=ft.Colors.WHITE,
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
                    self.page.dialog = lan_info_dlg
                    lan_info_dlg.open = True
                    self.page.update()

                # 刷新UI以显示新按钮
                self.build_ui()

                self.snack("✅ 编辑器已启动！", False)

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
                            "❌ npm 命令未找到或无法执行",
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
                            f"❌ 开发服务器启动失败 (退出码: {returncode})",
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
                        "❌ 博客框架未正确初始化",
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
                        "❌ 依赖未安装",
                        "",
                        "解决方案：",
                        "在博客目录运行：",
                        "  npm install",
                        "",
                        "或点击 '初始化博客框架' 按钮"
                    ]

                else:
                    error_details = [
                        f"❌ {error_msg}",
                        "",
                        "请查看控制台输出获取详细信息",
                        "或参考 EDITOR_TROUBLESHOOTING.md"
                    ]

                # 显示详细错误对话框
                error_text = "\n".join(error_details)

                error_dlg = ft.AlertDialog(
                    title=ft.Text("启动编辑器失败", color=ft.Colors.RED_700),
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

                self.page.overlay.append(error_dlg)
                error_dlg.open = True
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
        self.page.overlay.append(checking_dlg)
        checking_dlg.open = True
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
                                color=ft.Colors.DEEP_PURPLE_600, size=30),
                        ft.Column([
                            ft.Text("更新博客框架", size=16,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text(f"有 {self.update_info['commits_behind']} 个新提交",
                                    size=12, color=ft.Colors.GREY_600),
                        ], spacing=2, expand=True),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT,
                                color=ft.Colors.GREY_400),
                    ], spacing=15),
                    padding=15,
                    border=ft.Border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    bgcolor=ft.Colors.WHITE,
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
                                color=ft.Colors.BLUE_600, size=30),
                        ft.Column([
                            ft.Text("更新管理工具", size=16,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text(f"最新版本: {self.update_info['manager_version']}",
                                    size=12, color=ft.Colors.GREY_600),
                        ], spacing=2, expand=True),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT,
                                color=ft.Colors.GREY_400),
                    ], spacing=15),
                    padding=15,
                    border=ft.Border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    bgcolor=ft.Colors.WHITE,
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
                                color=ft.Colors.GREEN_600, size=50),
                        ft.Text("已是最新版本", size=16, color=ft.Colors.GREY_700),
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
        self.page.overlay.append(dlg)
        dlg.open = True
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
                    size=13, color=ft.Colors.GREY_700),
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
                          bgcolor=ft.Colors.DEEP_PURPLE_600,
                          color=ft.Colors.WHITE),
            ],
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def confirm_update_framework(self, dlg):
        """确认更新框架，开始执行"""
        self.close_dlg(dlg)

        # 创建进度对话框
        progress_bar = ft.ProgressBar(width=400, value=0)
        status_text = ft.Text(self.t('updating'), size=14)
        detail_text = ft.Text("", size=12, color=ft.Colors.GREY_600)
        log_text = ft.Text(
            "", size=11, color=ft.Colors.GREY_500, selectable=True)

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
                        height=150,
                        bgcolor=ft.Colors.GREY_100,
                        border_radius=5,
                        padding=10,
                    ),
                ], tight=True, spacing=5),
                width=600,
            ),
            modal=True,
        )
        self.page.overlay.append(progress_dlg)
        progress_dlg.open = True
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

                log_text.value += f"✓ Git 状态检查完成\n"
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

                log_text.value += f"\n✓ 备份完成\n"
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
                    log_text.value += f"\n✗ 代码拉取失败，正在恢复备份...\n"
                    self.page.update()
                    updater.restore_user_files(backup_result['backup_path'])
                    raise Exception(pull_result.get('message', '拉取代码失败'))

                log_text.value += f"\n✓ 代码拉取成功\n"
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

                log_text.value += f"\n✓ 用户文件恢复完成\n"
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
                    log_text.value += f"✓ npm 依赖安装完成\n"
                else:
                    log_text.value += f"⚠ npm 依赖安装失败: {npm_result.get('message', '未知错误')}\n"
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
                    log_text.value += f"\n⚠ 检测到配置变化:\n"
                    for file_name, diff in differences.items():
                        new_fields = diff.get('new_fields', [])
                        modified_fields = diff.get('modified_fields', [])
                        if new_fields:
                            log_text.value += f"  {file_name}: 新增 {len(new_fields)} 个字段\n"
                        if modified_fields:
                            log_text.value += f"  {file_name}: 修改 {len(modified_fields)} 个字段\n"
                else:
                    log_text.value += f"\n✓ 无配置文件变化\n"
                self.page.update()

                # 7. 生成更新报告
                report_result = updater.generate_update_report(
                    backup_result['backup_path'], differences)
                if report_result['success']:
                    log_text.value += f"\n✓ 更新报告已生成\n"
                    log_text.value += f"  位置: UPDATE_REPORT.md\n"

                # 更新完成
                progress_bar.value = 1.0
                status_text.value = self.t('update_success')
                detail_text.value = "框架更新完成！"
                log_text.value += f"\n{'='*40}\n"
                log_text.value += f"✓ 更新完成！\n"
                log_text.value += f"\n下一步:\n"
                if npm_result['success']:
                    log_text.value += f"1. ✓ npm 依赖已自动安装\n"
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
                log_text.value += f"\n✗ 错误: {ex}\n"
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
                    bgcolor=ft.Colors.BLUE_600,
                    color=ft.Colors.WHITE
                ),
            ],
        )
        self.page.overlay.append(dlg)
        dlg.open = True
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
                        color=ft.Colors.GREEN_600),
                ft.Container(height=10),
                ft.Text("已是最新版本", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(height=5),
                ft.Text(f"当前版本: {current_version}",
                        size=14, color=ft.Colors.GREY_600),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
            actions=[
                ft.Button("确定", on_click=lambda e: self.close_dlg(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        self.page.dialog = dlg
        dlg.open = True
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
                        color=ft.Colors.GREY_700
                    ),
                    height=100,
                    padding=10,
                    border=ft.Border.all(1, ft.Colors.GREY_300),
                    border_radius=5,
                ),
                ft.Container(height=10),
                ft.Text("是否立即更新管理工具？", size=13, color=ft.Colors.GREY_700),
                ft.Text("（程序将自动关闭并重启）", size=11, color=ft.Colors.ORANGE_700),
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
                        bgcolor=ft.Colors.BLUE_600,
                        color=ft.Colors.WHITE
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            # 使用 overlay 而不是 dialog 属性，避免被其他对话框覆盖
            self.page.overlay.append(dlg)
            dlg.open = True
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
        detail_text = ft.Text("", size=12, color=ft.Colors.GREY_600)
        log_text = ft.Text(
            "", size=11, color=ft.Colors.GREY_700, selectable=True)

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
                        bgcolor=ft.Colors.GREY_100,
                        border_radius=5,
                        padding=10,
                    ),
                ], tight=True, spacing=0),
                width=500,
            ),
            modal=True,
        )

        self.page.overlay.append(progress_dlg)
        progress_dlg.open = True
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
                    log_text.value += "\n✓ 下载完成！\n"
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

                log_text.value += f"\n✗ 错误: {ex}\n"
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
            # BackgroundImg 和 HeadImg 将使用图片上传组件，不在这里处理
            ('BackgroundImgOpacity', self.t('bg_opacity'), 'number'),
            ('BackgroundImgBlur', self.t('bg_blur'), 'number'),
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

        # 图片上传区域
        form_rows.append(ft.Divider())
        form_rows.append(
            ft.Text('图片配置', size=20, weight=ft.FontWeight.BOLD, color="#FFFFFF"))

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
                self.snack(f"✅ 背景图片已上传", False)
                self.build_ui()  # 刷新界面以显示新图片

        def on_head_upload(file_path):
            """头像图片上传回调"""
            result = self.process_config_image(file_path, 'HeadImg')
            if result:
                head_img_uploaded[0] = result
                self.snack(f"✅ 头像图片已上传", False)
                self.build_ui()  # 刷新界面以显示新图片

        # 图片上传组件
        images_section = ft.Column([
            # 背景图片
            ft.Column([
                ft.Text(
                    self.t('background_img'),
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color="#FFFFFF"
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
                    color="#FFFFFF"
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
                            self.snack('✅ 已从 GitHub 配置中加载仓库信息', False)
                            self.page.update()
                            return

                self.snack('⚠️ 未找到 GitHub 配置，请手动输入仓库信息', False)
            except Exception as ex:
                self.snack(f'❌ 读取部署配置失败: {ex}', True)

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
            '💡 提示: 使用 Utterances 需要先在 GitHub 仓库中安装 Utterances App\n'
            '访问 https://github.com/apps/utterances 进行安装' if self.current_lang == 'zh' else
            '💡 Tip: You need to install Utterances App in your GitHub repository first\n'
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

        add_link_btn = ft.Button(
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
                    self.snack(f"{result}\n{pwd_result}", False)
                except Exception as pwd_ex:
                    self.snack(f"{result}\n密码保存失败: {pwd_ex}", True)

            except Exception as ex:
                self.snack(f"保存失败: {ex}", True)
                import traceback
                traceback.print_exc()

        save_btn = ft.Button(
            self.t('save_config'),
            icon=ft.Icons.SAVE,
            on_click=save_config,
            bgcolor=ft.Colors.GREEN_600,
            color=ft.Colors.WHITE,
        )

        # 添加底部保存按钮（方便滚动到最后时保存）
        form_rows.append(ft.Divider())
        form_rows.append(ft.Container(content=save_btn, padding=10))

        # 创建顶部固定的保存提示区域
        save_reminder = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE,
                        color=ft.Colors.BLUE_600, size=20),
                ft.Text(
                    self.t('config_save_reminder'),
                    size=13,
                    color=ft.Colors.BLUE_700,
                    expand=True,
                ),
                ft.Button(
                    self.t('save_config'),
                    icon=ft.Icons.SAVE,
                    on_click=save_config,
                    bgcolor=ft.Colors.GREEN_600,
                    color=ft.Colors.WHITE,
                    height=36,
                ),
            ], spacing=10),
            bgcolor=ft.Colors.BLUE_50,
            padding=15,
            border_radius=8,
            border=ft.Border.all(1, ft.Colors.BLUE_200),
        )

        return ft.Column([
            save_reminder,
            ft.Container(height=10),
            ft.Container(
                content=ft.Column(
                    form_rows,
                    scroll=ft.ScrollMode.AUTO,
                ),
                expand=True,
            ),
        ], expand=True, spacing=0)

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
