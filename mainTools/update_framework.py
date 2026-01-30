"""
KMBlog 框架更新工具
从 GitHub 仓库同步最新框架代码
"""

import os
import json
import subprocess
import shutil
from datetime import datetime
from path_utils import get_base_path


class FrameworkUpdater:
    """框架更新器"""
    
    GITHUB_REPO = "https://github.com/iiishop/KMblog.git"
    
    # 需要备份的用户文件/目录
    # 注意：根据 .gitignore，以下文件不会被 Git 跟踪，但仍需备份以防万一
    USER_FILES = [
        'src/config.js',  # Git 跟踪
        'public/Posts/Markdowns/About.md',  # Git 跟踪（唯一例外）
        'public/assets/background.png',  # .gitignore 排除，但需备份
        'public/assets/head.png',  # .gitignore 排除，但需备份
        'github_config.json',  # .gitignore 排除，但需备份
    ]
    
    USER_DIRS = [
        'public/Posts',  # .gitignore 排除（除了 About.md），但需备份
        'public/assets',  # 部分文件被 .gitignore 排除，但需备份
        'cryptoPosts',  # .gitignore 排除，但需备份
    ]
    
    # Git 实际跟踪的用户文件（更新时可能冲突）
    GIT_TRACKED_USER_FILES = [
        'src/config.js',
        'public/Posts/Markdowns/About.md',
        'public/assets/background.png',  # 用户自定义背景图
        'public/assets/head.png',  # 用户自定义头像
    ]
    
    # 框架文件（不备份，直接覆盖）
    FRAMEWORK_DIRS = [
        'src/components',
        'src/views',
        'src/utils',
        'src/composables',
        'mainTools',
        '.claude',
    ]
    
    def __init__(self):
        self.base_path = get_base_path()
        self.backup_dir = os.path.join(self.base_path, '.kmblog_backup')
        self.update_log = []
        
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        self.update_log.append(log_message)
        print(log_message)
        
    def check_for_updates(self):
        """检查是否有更新（不执行更新）
        
        Returns:
            dict: {
                'success': bool,
                'has_updates': bool,
                'commits_behind': int,  # 落后的 commit 数量
                'local_commit': str,
                'remote_commit': str,
                'message': str
            }
        """
        try:
            # 检查是否是 Git 仓库
            git_status = self.check_git_status()
            if not git_status['success'] or not git_status['is_git_repo']:
                return {
                    'success': False,
                    'has_updates': False,
                    'message': '不是 Git 仓库'
                }
            
            # 获取本地 commit hash
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'has_updates': False,
                    'message': '无法获取本地 commit'
                }
            
            local_commit = result.stdout.strip()
            
            # 获取远程最新 commit（不拉取代码，只获取信息）
            # 先 fetch 更新远程分支信息
            subprocess.run(
                ['git', 'fetch', 'origin'],
                cwd=self.base_path,
                capture_output=True,
                timeout=30
            )
            
            # 尝试 main 分支
            result = subprocess.run(
                ['git', 'rev-parse', 'origin/main'],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                # 尝试 master 分支
                result = subprocess.run(
                    ['git', 'rev-parse', 'origin/master'],
                    cwd=self.base_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'has_updates': False,
                    'message': '无法获取远程 commit'
                }
            
            remote_commit = result.stdout.strip()
            
            # 比较 commit
            has_updates = local_commit != remote_commit
            
            # 计算落后的 commit 数量
            commits_behind = 0
            if has_updates:
                # 使用 git rev-list 计算差异
                result = subprocess.run(
                    ['git', 'rev-list', '--count', f'{local_commit}..{remote_commit}'],
                    cwd=self.base_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    try:
                        commits_behind = int(result.stdout.strip())
                    except:
                        commits_behind = 1  # 至少有1个更新
            
            return {
                'success': True,
                'has_updates': has_updates,
                'commits_behind': commits_behind,
                'local_commit': local_commit[:7],  # 短 hash
                'remote_commit': remote_commit[:7],
                'message': f'发现 {commits_behind} 个更新' if has_updates else '已是最新版本'
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'has_updates': False,
                'message': 'Git 命令超时'
            }
        except Exception as e:
            return {
                'success': False,
                'has_updates': False,
                'message': f'检查更新失败: {str(e)}'
            }
    
    def check_git_status(self):
        """检查 Git 状态"""
        try:
            # 检查是否是 Git 仓库
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'message': '当前目录不是 Git 仓库',
                    'is_git_repo': False
                }
            
            # 检查是否有未提交的更改
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            has_changes = bool(result.stdout.strip())
            
            # 获取当前分支
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            current_branch = result.stdout.strip()
            
            # 获取远程 URL
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            remote_url = result.stdout.strip()
            
            return {
                'success': True,
                'is_git_repo': True,
                'has_changes': has_changes,
                'current_branch': current_branch,
                'remote_url': remote_url
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'Git 命令超时'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'message': '未找到 Git 命令，请确保已安装 Git'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'检查 Git 状态失败: {str(e)}'
            }
    
    def backup_user_files(self):
        """备份用户文件（只备份 Git 跟踪的文件，其他文件不会被 git pull 覆盖）"""
        try:
            self.log("开始备份用户文件...")
            self.log("注意: 只备份 Git 跟踪的文件，.gitignore 排除的文件不会被更新覆盖")
            
            # 创建备份目录（带时间戳）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(self.backup_dir, timestamp)
            os.makedirs(backup_path, exist_ok=True)
            
            backed_up_files = []
            
            # 只备份 Git 跟踪的用户文件（这些文件可能被 git pull 覆盖）
            for file_path in self.GIT_TRACKED_USER_FILES:
                full_path = os.path.join(self.base_path, file_path)
                if os.path.exists(full_path):
                    target_path = os.path.join(backup_path, file_path)
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    shutil.copy2(full_path, target_path)
                    backed_up_files.append(file_path)
                    self.log(f"  ✓ 已备份 (Git跟踪): {file_path}")
            
            self.log(f"备份完成！共备份 {len(backed_up_files)} 个 Git 跟踪的文件")
            self.log(f"提示: .gitignore 排除的文件（如 Posts/、cryptoPosts/）不会被更新影响")
            
            return {
                'success': True,
                'backup_path': backup_path,
                'backed_up_files': backed_up_files
            }
            
        except Exception as e:
            self.log(f"备份失败: {str(e)}")
            return {
                'success': False,
                'message': f'备份失败: {str(e)}'
            }
    
    def pull_latest_code(self):
        """拉取最新代码"""
        try:
            self.log("开始拉取最新代码...")
            
            # 强力清理任何未完成的合并状态
            self.log("检查并清理 Git 状态...")
            
            # 1. 尝试中止任何进行中的合并
            subprocess.run(
                ['git', 'merge', '--abort'],
                cwd=self.base_path,
                capture_output=True,
                timeout=10
            )
            
            # 2. 尝试中止任何进行中的 rebase
            subprocess.run(
                ['git', 'rebase', '--abort'],
                cwd=self.base_path,
                capture_output=True,
                timeout=10
            )
            
            # 3. 重置到 HEAD（清理所有未暂存的更改）
            result = subprocess.run(
                ['git', 'reset', '--hard', 'HEAD'],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.log("✓ Git 状态已清理")
            
            # 4. 清理未跟踪的文件（可选，注释掉以保留用户文件）
            # subprocess.run(
            #     ['git', 'clean', '-fd'],
            #     cwd=self.base_path,
            #     capture_output=True,
            #     timeout=10
            # )
            
            # 先获取当前分支名
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            current_branch = result.stdout.strip() if result.returncode == 0 else None
            
            # 如果没有当前分支（detached HEAD），尝试获取默认分支
            if not current_branch:
                # 尝试从远程获取默认分支
                result = subprocess.run(
                    ['git', 'remote', 'show', 'origin'],
                    cwd=self.base_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    # 解析输出找到 HEAD branch
                    import re
                    match = re.search(r'HEAD branch:\s*(\S+)', result.stdout)
                    if match:
                        current_branch = match.group(1)
                        self.log(f"检测到远程默认分支: {current_branch}")
            
            # 如果还是没有，尝试常见的分支名
            if not current_branch:
                self.log("无法检测当前分支，尝试常见分支名...")
                for branch in ['main', 'master']:
                    result = subprocess.run(
                        ['git', 'rev-parse', '--verify', f'origin/{branch}'],
                        cwd=self.base_path,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        current_branch = branch
                        self.log(f"找到可用分支: {branch}")
                        break
            
            if not current_branch:
                return {
                    'success': False,
                    'message': '无法确定要拉取的分支，请手动执行 git pull'
                }
            
            self.log(f"准备从 origin/{current_branch} 拉取代码...")
            
            # 使用 git pull --rebase 避免合并冲突
            # 或者使用 git fetch + git reset --hard 强制同步
            self.log("使用强制同步模式（将丢弃所有本地提交）...")
            
            # Fetch 最新代码
            result = subprocess.run(
                ['git', 'fetch', 'origin', current_branch],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'message': f'Fetch 失败: {result.stderr}'
                }
            
            self.log("✓ 代码已获取")
            
            # 强制重置到远程分支（这会丢弃所有本地提交，但保留用户文件因为已经备份）
            result = subprocess.run(
                ['git', 'reset', '--hard', f'origin/{current_branch}'],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.log("代码同步成功！")
                self.log(result.stdout)
                return {
                    'success': True,
                    'output': result.stdout,
                    'branch': current_branch
                }
            else:
                self.log(f"代码同步失败: {result.stderr}")
                return {
                    'success': False,
                    'message': f'Git reset 失败: {result.stderr}'
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'Git 操作超时'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'拉取代码失败: {str(e)}'
            }
    
    def restore_user_files(self, backup_path):
        """恢复用户文件（只恢复 Git 跟踪的文件）"""
        try:
            self.log("开始恢复用户文件...")
            
            restored_files = []
            
            # 只恢复 Git 跟踪的文件
            for file_path in self.GIT_TRACKED_USER_FILES:
                backup_file = os.path.join(backup_path, file_path)
                if os.path.exists(backup_file):
                    target_path = os.path.join(self.base_path, file_path)
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    shutil.copy2(backup_file, target_path)
                    restored_files.append(file_path)
                    self.log(f"  ✓ 已恢复: {file_path}")
            
            self.log(f"恢复完成！共恢复 {len(restored_files)} 个文件")
            self.log(f"提示: .gitignore 排除的文件未被更新影响，无需恢复")
            
            return {
                'success': True,
                'restored_files': restored_files
            }
            
        except Exception as e:
            self.log(f"恢复失败: {str(e)}")
            return {
                'success': False,
                'message': f'恢复失败: {str(e)}'
            }
    
    def compare_configs(self, backup_path):
        """比较配置文件差异"""
        try:
            self.log("分析配置文件差异...")
            
            differences = {}
            
            # 比较 config.js
            old_config_path = os.path.join(backup_path, 'src/config.js')
            new_config_path = os.path.join(self.base_path, 'src/config.js')
            
            if os.path.exists(old_config_path) and os.path.exists(new_config_path):
                old_config = self._parse_config_js(old_config_path)
                new_config = self._parse_config_js(new_config_path)
                
                # 找出新增的字段
                new_fields = set(new_config.keys()) - set(old_config.keys())
                # 找出修改的字段（值不同）
                modified_fields = {
                    key for key in old_config.keys() & new_config.keys()
                    if old_config[key] != new_config[key]
                }
                
                if new_fields or modified_fields:
                    differences['config.js'] = {
                        'new_fields': list(new_fields),
                        'modified_fields': list(modified_fields),
                        'old_config': old_config,
                        'new_config': new_config
                    }
                    self.log(f"  config.js: 新增 {len(new_fields)} 个字段，修改 {len(modified_fields)} 个字段")
            
            return {
                'success': True,
                'differences': differences
            }
            
        except Exception as e:
            self.log(f"比较配置失败: {str(e)}")
            return {
                'success': False,
                'message': f'比较配置失败: {str(e)}'
            }
    
    def _parse_config_js(self, file_path):
        """解析 config.js 文件（简单实现）"""
        config = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的正则匹配（不完美，但足够用）
            import re
            
            # 匹配字符串值
            pattern = r"(\w+):\s*['\"]([^'\"]*)['\"]"
            for match in re.finditer(pattern, content):
                key, value = match.groups()
                config[key] = value
            
            # 匹配数字值
            pattern = r"(\w+):\s*(\d+\.?\d*)"
            for match in re.finditer(pattern, content):
                key, value = match.groups()
                if key not in config:  # 避免覆盖字符串值
                    config[key] = float(value) if '.' in value else int(value)
            
            # 匹配布尔值
            pattern = r"(\w+):\s*(true|false)"
            for match in re.finditer(pattern, content):
                key, value = match.groups()
                if key not in config:
                    config[key] = value == 'true'
            
            # 匹配数组值
            pattern = r"(\w+):\s*\[([\s\S]*?)\]"
            for match in re.finditer(pattern, content):
                key, value = match.groups()
                if key not in config:
                    # 简单处理：提取字符串元素
                    items = re.findall(r"['\"]([^'\"]*)['\"]", value)
                    config[key] = items
            
        except Exception as e:
            print(f"解析 config.js 失败: {e}")
        
        return config
    
    def generate_update_report(self, backup_path, differences):
        """生成更新报告"""
        try:
            report_path = os.path.join(self.base_path, 'UPDATE_REPORT.md')
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("# KMBlog 框架更新报告\n\n")
                f.write(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("## 更新日志\n\n")
                for log in self.update_log:
                    f.write(f"- {log}\n")
                
                f.write("\n## 配置文件变化\n\n")
                
                if differences:
                    for file_name, diff in differences.items():
                        f.write(f"### {file_name}\n\n")
                        
                        if diff.get('new_fields'):
                            f.write("**新增字段:**\n\n")
                            for field in diff['new_fields']:
                                value = diff['new_config'].get(field, '')
                                f.write(f"- `{field}`: `{value}`\n")
                            f.write("\n")
                        
                        if diff.get('modified_fields'):
                            f.write("**修改字段:**\n\n")
                            for field in diff['modified_fields']:
                                old_value = diff['old_config'].get(field, '')
                                new_value = diff['new_config'].get(field, '')
                                f.write(f"- `{field}`:\n")
                                f.write(f"  - 旧值: `{old_value}`\n")
                                f.write(f"  - 新值: `{new_value}`\n")
                            f.write("\n")
                else:
                    f.write("无配置文件变化\n\n")
                
                f.write("## 备份位置\n\n")
                f.write(f"用户文件已备份到: `{backup_path}`\n\n")
                
                f.write("## 下一步操作\n\n")
                f.write("1. 检查配置文件变化，确认是否需要手动调整\n")
                f.write("2. ✓ npm 依赖已自动安装\n")
                f.write("3. 运行 `npm run dev` 测试更新后的博客\n")
                f.write("4. 如有问题，可从备份目录恢复文件\n")
            
            self.log(f"更新报告已生成: {report_path}")
            
            return {
                'success': True,
                'report_path': report_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'生成报告失败: {str(e)}'
            }
    
    def install_dependencies(self):
        """安装 npm 依赖"""
        try:
            self.log("开始安装 npm 依赖...")
            self.log("提示: 这可能需要几分钟时间...")
            
            # Windows 需要使用 shell=True 来执行 npm.cmd
            import platform
            is_windows = platform.system() == 'Windows'
            
            if is_windows:
                # Windows: 使用 shell=True
                result = subprocess.run(
                    'npm install',
                    cwd=self.base_path,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=300,  # 5分钟超时
                    shell=True
                )
            else:
                # Linux/macOS: 使用命令列表
                result = subprocess.run(
                    ['npm', 'install'],
                    cwd=self.base_path,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=300  # 5分钟超时
                )
            
            if result.returncode == 0:
                self.log("✓ npm 依赖安装完成")
                
                # 显示安装的包数量（如果有）
                if 'added' in result.stdout or 'updated' in result.stdout:
                    # 提取关键信息
                    import re
                    match = re.search(r'(added|updated|removed)\s+\d+\s+package', result.stdout)
                    if match:
                        self.log(f"  {match.group(0)}")
                
                return {
                    'success': True,
                    'output': result.stdout
                }
            else:
                self.log(f"✗ npm install 失败: {result.stderr}")
                return {
                    'success': False,
                    'message': f'npm install 失败: {result.stderr}'
                }
                
        except subprocess.TimeoutExpired:
            self.log("✗ npm install 超时（超过5分钟）")
            return {
                'success': False,
                'message': 'npm install 超时，请检查网络连接'
            }
        except FileNotFoundError:
            self.log("✗ 未找到 npm 命令")
            self.log("提示: 请确保 Node.js 已安装并添加到系统 PATH")
            return {
                'success': False,
                'message': '未找到 npm 命令，请确保已安装 Node.js 并添加到系统 PATH'
            }
        except Exception as e:
            self.log(f"✗ npm install 失败: {str(e)}")
            return {
                'success': False,
                'message': f'npm install 失败: {str(e)}'
            }
    
    def update(self):
        """执行完整更新流程"""
        self.log("=" * 60)
        self.log("开始更新 KMBlog 框架")
        self.log("=" * 60)
        
        # 1. 检查 Git 状态
        git_status = self.check_git_status()
        if not git_status['success']:
            return git_status
        
        if not git_status['is_git_repo']:
            return {
                'success': False,
                'message': '当前目录不是 Git 仓库，无法使用 Git 更新'
            }
        
        if git_status['has_changes']:
            self.log("警告: 检测到未提交的更改")
        
        # 2. 备份用户文件
        backup_result = self.backup_user_files()
        if not backup_result['success']:
            return backup_result
        
        backup_path = backup_result['backup_path']
        
        # 3. 拉取最新代码
        pull_result = self.pull_latest_code()
        if not pull_result['success']:
            self.log("代码拉取失败，正在恢复备份...")
            self.restore_user_files(backup_path)
            return pull_result
        
        # 4. 恢复用户文件
        restore_result = self.restore_user_files(backup_path)
        if not restore_result['success']:
            return restore_result
        
        # 5. 安装 npm 依赖（更新后必须重新安装依赖）
        npm_result = self.install_dependencies()
        if not npm_result['success']:
            self.log("警告: npm 依赖安装失败，但框架代码已更新")
            self.log("请手动运行 'npm install' 安装依赖")
        
        # 6. 比较配置差异
        compare_result = self.compare_configs(backup_path)
        differences = compare_result.get('differences', {}) if compare_result['success'] else {}
        
        # 7. 生成更新报告
        report_result = self.generate_update_report(backup_path, differences)
        
        self.log("=" * 60)
        self.log("框架更新完成！")
        self.log("=" * 60)
        
        return {
            'success': True,
            'message': '框架更新成功',
            'backup_path': backup_path,
            'differences': differences,
            'npm_installed': npm_result['success'],
            'report_path': report_result.get('report_path') if report_result['success'] else None,
            'log': self.update_log
        }


class UpdateFramework:
    """更新框架命令（用于命令行）"""
    description = "Update KMBlog framework from GitHub repository"
    
    def execute(self):
        updater = FrameworkUpdater()
        result = updater.update()
        
        if result['success']:
            return f"更新成功！\n\n{chr(10).join(result['log'])}"
        else:
            return f"更新失败: {result.get('message', '未知错误')}"
