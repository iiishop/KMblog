"""
KMBlog Manager 自动更新工具
从 GitHub Releases 下载最新版本并自动替换
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
import zipfile
import requests
from datetime import datetime


class ManagerUpdater:
    """管理工具更新器"""
    
    GITHUB_API = "https://api.github.com/repos/iiishop/KMblog/releases/latest"
    
    def __init__(self):
        self.current_exe = sys.executable if getattr(sys, 'frozen', False) else None
        self.is_frozen = getattr(sys, 'frozen', False)
        self.current_version = self._get_current_version()
    
    def _get_current_version(self):
        """获取当前版本号"""
        try:
            # 尝试从 VERSION 文件读取
            if self.is_frozen:
                # 打包后，VERSION 文件在临时目录
                version_file = os.path.join(sys._MEIPASS, 'VERSION')
            else:
                # 开发环境，VERSION 文件在项目根目录
                version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'VERSION')
            
            if os.path.exists(version_file):
                with open(version_file, 'r', encoding='utf-8') as f:
                    return f.read().strip()
        except Exception as e:
            print(f"[版本检测] 读取 VERSION 文件失败: {e}")
        
        # 默认版本号
        return "1.0.0"
        
    def check_for_updates(self):
        """检查是否有新版本
        
        Returns:
            dict: {
                'success': bool,
                'has_update': bool,
                'latest_version': str,
                'download_url': str,
                'release_notes': str
            }
        """
        try:
            print("[管理工具更新] 检查最新版本...")
            
            # 获取最新 release 信息
            response = requests.get(self.GITHUB_API, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            latest_version = release_data.get('tag_name', '').lstrip('v')
            release_notes = release_data.get('body', '')
            
            # 查找对应平台的下载链接
            platform = self._get_platform()
            download_url = None
            
            for asset in release_data.get('assets', []):
                asset_name = asset.get('name', '').lower()
                # 检查平台和文件类型匹配
                if platform in asset_name:
                    # Windows: .zip
                    # macOS: .dmg 优先，.tar.gz 作为备选
                    # Linux: .tar.gz
                    if sys.platform == 'win32' and 'zip' in asset_name:
                        download_url = asset.get('browser_download_url')
                        break
                    elif sys.platform == 'darwin':
                        if 'dmg' in asset_name:
                            download_url = asset.get('browser_download_url')
                            break
                        elif 'tar.gz' in asset_name and not download_url:
                            # 如果没找到 DMG，使用 tar.gz 作为备选
                            download_url = asset.get('browser_download_url')
                    elif sys.platform == 'linux' and 'tar.gz' in asset_name:
                        download_url = asset.get('browser_download_url')
                        break
            
            if not download_url:
                return {
                    'success': False,
                    'message': f'未找到适用于 {platform} 平台的下载文件'
                }
            
            # 版本比较
            has_update = self._compare_versions(self.current_version, latest_version)
            
            print(f"[管理工具更新] 当前版本: {self.current_version}")
            print(f"[管理工具更新] 最新版本: {latest_version}")
            print(f"[管理工具更新] 需要更新: {has_update}")
            print(f"[管理工具更新] 下载地址: {download_url}")
            
            return {
                'success': True,
                'has_update': has_update,
                'current_version': self.current_version,
                'latest_version': latest_version,
                'download_url': download_url,
                'release_notes': release_notes,
                'asset_name': os.path.basename(download_url)
            }
            
        except requests.RequestException as e:
            return {
                'success': False,
                'message': f'网络请求失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'检查更新失败: {str(e)}'
            }
    
    def _get_platform(self):
        """获取当前平台和架构"""
        if sys.platform == 'win32':
            return 'windows'
        elif sys.platform == 'darwin':
            # macOS: 检测架构
            import platform
            machine = platform.machine().lower()
            if machine == 'arm64' or machine == 'aarch64':
                return 'macos-apple-silicon'
            else:
                return 'macos-intel'
        else:
            return 'linux'
    
    def _compare_versions(self, current, latest):
        """比较版本号
        
        Args:
            current: 当前版本 (如 "1.0.0")
            latest: 最新版本 (如 "1.0.1")
            
        Returns:
            bool: 如果最新版本更高则返回 True
        """
        try:
            # 移除 'v' 前缀
            current = current.lstrip('v')
            latest = latest.lstrip('v')
            
            # 分割版本号
            current_parts = [int(x) for x in current.split('.')]
            latest_parts = [int(x) for x in latest.split('.')]
            
            # 补齐长度
            max_len = max(len(current_parts), len(latest_parts))
            current_parts += [0] * (max_len - len(current_parts))
            latest_parts += [0] * (max_len - len(latest_parts))
            
            # 逐位比较
            for c, l in zip(current_parts, latest_parts):
                if l > c:
                    return True
                elif l < c:
                    return False
            
            # 版本号相同
            return False
            
        except Exception as e:
            print(f"[版本比较] 错误: {e}")
            # 如果比较失败，保守起见返回 False
            return False
    
    def download_and_update(self, download_url, asset_name, progress_callback=None):
        """下载并更新管理工具
        
        Args:
            download_url: 下载地址
            asset_name: 文件名
            progress_callback: 进度回调函数 callback(stage, progress, message)
                - stage: 阶段名称 ('download', 'extract', 'install')
                - progress: 进度 0.0-1.0
                - message: 状态消息
            
        Returns:
            dict: 更新结果
        """
        def report_progress(stage, progress, message):
            """报告进度"""
            print(f"[管理工具更新] [{stage}] {progress:.1%} - {message}")
            if progress_callback:
                try:
                    progress_callback(stage, progress, message)
                except Exception as e:
                    print(f"[管理工具更新] 进度回调错误: {e}")
        
        try:
            print(f"[管理工具更新] 开始更新流程")
            print(f"[管理工具更新] is_frozen: {self.is_frozen}")
            print(f"[管理工具更新] current_exe: {self.current_exe}")
            
            if not self.is_frozen:
                return {
                    'success': False,
                    'message': '当前不是打包版本，无法自动更新'
                }
            
            report_progress('download', 0.0, '准备下载...')
            print(f"[管理工具更新] 下载地址: {download_url}")
            print(f"[管理工具更新] 文件名: {asset_name}")
            
            # 创建临时目录
            temp_dir = tempfile.mkdtemp(prefix='kmblog_manager_update_')
            print(f"[管理工具更新] 临时目录: {temp_dir}")
            
            download_path = os.path.join(temp_dir, asset_name)
            
            # 下载文件
            report_progress('download', 0.05, '连接服务器...')
            response = requests.get(download_url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            report_progress('download', 0.1, f'开始下载 ({total_size / 1024 / 1024:.1f} MB)...')
            
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            # 下载进度占 10% - 60%
                            progress = 0.1 + (downloaded / total_size) * 0.5
                            report_progress('download', progress, 
                                          f'下载中... {downloaded / 1024 / 1024:.1f} / {total_size / 1024 / 1024:.1f} MB')
            
            report_progress('download', 0.6, '下载完成')
            print(f"[管理工具更新] 文件大小: {os.path.getsize(download_path)} bytes")
            
            # 解压文件
            report_progress('extract', 0.65, '开始解压...')
            extract_dir = os.path.join(temp_dir, 'extracted')
            os.makedirs(extract_dir, exist_ok=True)
            
            if asset_name.endswith('.zip'):
                print("[管理工具更新] 使用 ZIP 解压")
                with zipfile.ZipFile(download_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            elif asset_name.endswith('.dmg'):
                print("[管理工具更新] 处理 DMG 文件 (macOS)")
                # macOS DMG 需要挂载后提取
                report_progress('extract', 0.7, '挂载 DMG...')
                
                # 挂载 DMG
                mount_point = os.path.join(temp_dir, 'dmg_mount')
                os.makedirs(mount_point, exist_ok=True)
                
                result = subprocess.run(
                    ['hdiutil', 'attach', download_path, '-mountpoint', mount_point, '-nobrowse'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    return {
                        'success': False,
                        'message': f'挂载 DMG 失败: {result.stderr}'
                    }
                
                try:
                    # 查找 .app 文件
                    app_name = None
                    for item in os.listdir(mount_point):
                        if item.endswith('.app'):
                            app_name = item
                            break
                    
                    if not app_name:
                        return {
                            'success': False,
                            'message': '在 DMG 中未找到 .app 文件'
                        }
                    
                    # 复制 .app 到临时目录
                    app_source = os.path.join(mount_point, app_name)
                    app_dest = os.path.join(extract_dir, app_name)
                    shutil.copytree(app_source, app_dest)
                    
                finally:
                    # 卸载 DMG
                    subprocess.run(['hdiutil', 'detach', mount_point], capture_output=True)
                
            elif asset_name.endswith('.tar.gz'):
                print("[管理工具更新] 使用 TAR.GZ 解压")
                import tarfile
                with tarfile.open(download_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(extract_dir)
            else:
                return {
                    'success': False,
                    'message': f'不支持的压缩格式: {asset_name}'
                }
            
            report_progress('extract', 0.75, '解压完成')
            
            # 列出解压后的文件
            print("[管理工具更新] 解压后的文件:")
            for root, dirs, files in os.walk(extract_dir):
                level = root.replace(extract_dir, '').count(os.sep)
                indent = ' ' * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    print(f"{subindent}{file}")
            
            # 查找新的可执行文件
            report_progress('install', 0.8, '查找可执行文件...')
            new_exe = self._find_executable(extract_dir)
            if not new_exe:
                return {
                    'success': False,
                    'message': '未找到可执行文件（查找 KMblogManager 或 KMblogManager.exe）'
                }
            
            print(f"[管理工具更新] 找到新版本: {new_exe}")
            
            # 创建更新脚本
            report_progress('install', 0.9, '创建更新脚本...')
            update_script = self._create_update_script(new_exe, self.current_exe)
            print(f"[管理工具更新] 更新脚本: {update_script}")
            
            report_progress('install', 0.95, '准备执行更新...')
            
            # 执行更新脚本并退出当前程序
            if sys.platform == 'win32':
                # Windows: 使用 cmd 执行批处理脚本
                print("[管理工具更新] 启动 Windows 更新脚本")
                subprocess.Popen(
                    ['cmd', '/c', update_script],
                    creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.DETACHED_PROCESS
                )
            else:
                # Unix: 使用 sh 执行脚本
                print("[管理工具更新] 启动 Unix 更新脚本")
                subprocess.Popen(
                    ['sh', update_script],
                    start_new_session=True
                )
            
            report_progress('install', 1.0, '更新脚本已启动')
            
            return {
                'success': True,
                'message': '更新脚本已启动，程序即将关闭',
                'should_exit': True
            }
            
        except requests.RequestException as e:
            print(f"[管理工具更新] 下载失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'下载失败: {str(e)}'
            }
        except Exception as e:
            print(f"[管理工具更新] 更新失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'更新失败: {str(e)}'
            }
    
    def _find_executable(self, directory):
        """在目录中查找可执行文件"""
        for root, dirs, files in os.walk(directory):
            for file in files:
                if sys.platform == 'win32':
                    if file.lower() == 'kmblogmanager.exe':
                        return os.path.join(root, file)
                else:
                    if file == 'KMblogManager':
                        full_path = os.path.join(root, file)
                        if os.access(full_path, os.X_OK):
                            return full_path
            
            # macOS: 查找 .app 包
            if sys.platform == 'darwin':
                for dir_name in dirs:
                    if dir_name.endswith('.app'):
                        app_path = os.path.join(root, dir_name)
                        exe_path = os.path.join(app_path, 'Contents', 'MacOS', 'KMblogManager')
                        if os.path.exists(exe_path):
                            return app_path  # 返回 .app 路径
        
        return None
    
    def _create_update_script(self, new_exe, old_exe):
        """创建更新脚本"""
        if sys.platform == 'win32':
            # Windows 批处理脚本
            script_path = os.path.join(tempfile.gettempdir(), 'kmblog_update.bat')
            
            script_content = f"""@echo off
echo KMBlog Manager 更新脚本
echo ========================

echo 等待程序关闭...
timeout /t 3 /nobreak >nul

echo 备份旧版本...
if exist "{old_exe}.backup" del "{old_exe}.backup"
move "{old_exe}" "{old_exe}.backup"

echo 复制新版本...
copy "{new_exe}" "{old_exe}"

echo 启动新版本...
start "" "{old_exe}"

echo 清理临时文件...
timeout /t 2 /nobreak >nul
rmdir /s /q "{os.path.dirname(new_exe)}"

echo 更新完成！
del "%~f0"
"""
        elif sys.platform == 'darwin' and new_exe.endswith('.app'):
            # macOS .app 更新脚本
            script_path = os.path.join(tempfile.gettempdir(), 'kmblog_update.sh')
            
            # 获取当前 .app 的路径
            if old_exe.endswith('.app'):
                old_app = old_exe
            else:
                # 从可执行文件路径推导 .app 路径
                old_app = old_exe
                while old_app and not old_app.endswith('.app'):
                    old_app = os.path.dirname(old_app)
            
            script_content = f"""#!/bin/bash
echo "KMBlog Manager 更新脚本"
echo "========================"

echo "等待程序关闭..."
sleep 3

echo "备份旧版本..."
if [ -d "{old_app}.backup" ]; then
    rm -rf "{old_app}.backup"
fi
mv "{old_app}" "{old_app}.backup"

echo "安装新版本..."
cp -R "{new_exe}" "{old_app}"

echo "启动新版本..."
open "{old_app}"

echo "清理临时文件..."
sleep 2
rm -rf "{os.path.dirname(new_exe)}"

echo "更新完成！"
rm "$0"
"""
        else:
            # Unix shell 脚本（Linux 或 macOS 非 .app）
            script_path = os.path.join(tempfile.gettempdir(), 'kmblog_update.sh')
            
            script_content = f"""#!/bin/bash
echo "KMBlog Manager 更新脚本"
echo "========================"

echo "等待程序关闭..."
sleep 3

echo "备份旧版本..."
if [ -f "{old_exe}.backup" ]; then
    rm "{old_exe}.backup"
fi
mv "{old_exe}" "{old_exe}.backup"

echo "复制新版本..."
cp "{new_exe}" "{old_exe}"
chmod +x "{old_exe}"

echo "启动新版本..."
"{old_exe}" &

echo "清理临时文件..."
sleep 2
rm -rf "{os.path.dirname(new_exe)}"

echo "更新完成！"
rm "$0"
"""
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        if sys.platform != 'win32':
            os.chmod(script_path, 0o755)
        
        return script_path


class UpdateManager:
    """更新管理命令（用于命令行）"""
    description = "Update KMBlog Manager to the latest version"
    
    def execute(self):
        updater = ManagerUpdater()
        
        # 检查更新
        check_result = updater.check_for_updates()
        if not check_result['success']:
            return f"检查更新失败: {check_result.get('message', '未知错误')}"
        
        if not check_result['has_update']:
            return "已是最新版本"
        
        print(f"\n发现新版本: {check_result['latest_version']}")
        print(f"\n更新说明:\n{check_result['release_notes']}\n")
        
        # 询问是否更新
        response = input("是否立即更新？(y/n): ")
        if response.lower() != 'y':
            return "已取消更新"
        
        # 执行更新
        update_result = updater.download_and_update(
            check_result['download_url'],
            check_result['asset_name']
        )
        
        if update_result['success']:
            print("\n更新成功！程序将在 3 秒后关闭...")
            import time
            time.sleep(3)
            sys.exit(0)
        else:
            return f"更新失败: {update_result.get('message', '未知错误')}"
