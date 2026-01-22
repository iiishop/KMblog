"""
GitHub 相关命令 - 用于部署博客到 GitHub Pages
"""
import os
import json
import base64
import shutil
from urllib import request, error, parse as urlparse
from path_utils import get_base_path


class GitHubConfig:
    """GitHub 配置管理"""
    CONFIG_FILE = 'github_config.json'

    @staticmethod
    def get_config_path():
        base_path = get_base_path()
        return os.path.join(base_path, GitHubConfig.CONFIG_FILE)

    @staticmethod
    def load():
        """加载GitHub配置"""
        config_path = GitHubConfig.get_config_path()
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    @staticmethod
    def save(token, repo_name):
        """保存GitHub配置"""
        config_path = GitHubConfig.get_config_path()
        config = {
            'token': token,
            'repo_name': repo_name
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return config


class GitHubAPI:
    """GitHub API 封装"""
    BASE_URL = 'https://api.github.com'

    def __init__(self, token):
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'KMBlog-Manager'
        }

    def _request(self, url, method='GET', data=None):
        """发送HTTP请求"""
        req = request.Request(url, headers=self.headers, method=method)
        if data:
            req.data = json.dumps(data).encode('utf-8')
            req.add_header('Content-Type', 'application/json')

        try:
            with request.urlopen(req) as response:
                response_body = response.read().decode('utf-8')
                # 处理 204 No Content 响应（DELETE 请求）
                if response.status == 204 or not response_body:
                    return {}
                return json.loads(response_body)
        except error.HTTPError as e:
            error_msg = e.read().decode('utf-8')
            try:
                error_json = json.loads(error_msg)
                raise Exception(
                    f"GitHub API Error: {error_json.get('message', error_msg)}")
            except:
                raise Exception(f"GitHub API Error: {e.code} - {error_msg}")

    def verify_token(self):
        """验证token有效性"""
        url = f'{self.BASE_URL}/user'
        try:
            user = self._request(url)
            return True, user.get('login', 'Unknown')
        except Exception as e:
            return False, str(e)

    def get_repo(self, owner, repo_name):
        """获取仓库信息"""
        url = f'{self.BASE_URL}/repos/{owner}/{repo_name}'
        try:
            return self._request(url)
        except:
            return None

    def create_repo(self, repo_name):
        """创建新仓库"""
        url = f'{self.BASE_URL}/user/repos'
        data = {
            'name': repo_name,
            'description': 'KMBlog - Personal Blog',
            'private': False,
            'auto_init': True
        }
        return self._request(url, method='POST', data=data)

    def get_default_branch(self, owner, repo_name):
        """获取默认分支"""
        repo = self.get_repo(owner, repo_name)
        return repo.get('default_branch', 'main') if repo else 'main'

    def get_branch(self, owner, repo_name, branch):
        """获取分支信息"""
        url = f'{self.BASE_URL}/repos/{owner}/{repo_name}/branches/{branch}'
        try:
            return self._request(url)
        except:
            return None

    def create_branch(self, owner, repo_name, branch, from_branch='main'):
        """创建新分支"""
        # 获取源分支的SHA
        source_branch = self.get_branch(owner, repo_name, from_branch)
        if not source_branch:
            raise Exception(f"Source branch '{from_branch}' not found")

        sha = source_branch['commit']['sha']

        # 创建新分支引用
        url = f'{self.BASE_URL}/repos/{owner}/{repo_name}/git/refs'
        data = {
            'ref': f'refs/heads/{branch}',
            'sha': sha
        }
        return self._request(url, method='POST', data=data)

    def _create_nested_tree(self, owner, repo_name, tree_items, tree_url):
        """创建嵌套树来处理超过300个文件的情况
        按照目录结构组织，而不是使用虚拟目录
        """
        print(f"[nested_tree] 开始按目录结构组织 {len(tree_items)} 个文件...")

        # 按顶级目录分组
        dir_groups = {}
        root_files = []

        for item in tree_items:
            path = item['path']
            if '/' in path:
                # 有子目录的文件
                top_dir = path.split('/')[0]
                if top_dir not in dir_groups:
                    dir_groups[top_dir] = []
                dir_groups[top_dir].append(item)
            else:
                # 根目录文件
                root_files.append(item)

        print(
            f"[nested_tree] 找到 {len(root_files)} 个根文件，{len(dir_groups)} 个顶级目录")

        # 为每个目录创建子树
        final_tree_items = []

        # 处理根目录文件
        final_tree_items.extend(root_files)

        # 处理每个顶级目录
        for dir_name, items in dir_groups.items():
            if len(items) <= 300:
                # 目录内文件数 <= 300，直接创建子树
                # 需要去掉顶级目录前缀
                subtree_items = []
                for item in items:
                    # 移除顶级目录前缀
                    subpath = '/'.join(item['path'].split('/')[1:])
                    subtree_items.append({
                        'path': subpath,
                        'mode': item['mode'],
                        'type': item['type'],
                        'sha': item['sha']
                    })

                subtree_data = {'tree': subtree_items}
                subtree = self._request(
                    tree_url, method='POST', data=subtree_data)

                # 将子树作为目录添加到主树
                final_tree_items.append({
                    'path': dir_name,
                    'mode': '040000',  # 目录模式
                    'type': 'tree',
                    'sha': subtree['sha']
                })
                print(
                    f"[nested_tree] 目录 '{dir_name}' 子树创建成功 ({len(items)} 个文件)")
            else:
                # 目录内文件数 > 300，需要递归分组
                print(
                    f"[nested_tree] 警告：目录 '{dir_name}' 有 {len(items)} 个文件，需要进一步分组")
                # 这里可以进一步递归，但通常不会出现单个目录超过300文件的情况
                # 简单处理：分批创建多个子树然后合并
                raise Exception(f"目录 '{dir_name}' 内文件过多({len(items)})，暂不支持")

        # 创建最终的根树
        main_tree_data = {'tree': final_tree_items}
        main_tree = self._request(tree_url, method='POST', data=main_tree_data)
        print(f"[nested_tree] 主树创建成功，sha: {main_tree['sha']}")

        return main_tree

    def upload_files(self, owner, repo_name, branch, files_dict, commit_message):
        """批量上传文件到指定分支
        files_dict: {relative_path: file_content}
        """
        # 获取当前分支的最新commit
        branch_info = self.get_branch(owner, repo_name, branch)
        if not branch_info:
            raise Exception(f"Branch '{branch}' not found")

        base_tree_sha = branch_info['commit']['commit']['tree']['sha']

        # 创建blob对象，并验证/去重路径
        blobs = {}
        seen_paths = set()

        print(f"[upload_files] 开始处理 {len(files_dict)} 个文件...")
        for file_path, content in files_dict.items():
            # 规范化路径（移除双斜杠、特殊字符等）
            normalized_path = file_path.strip().replace('\\', '/')
            normalized_path = '/'.join(p for p in normalized_path.split('/') if p)

            # GitHub 支持 UTF-8 路径，不需要 URL 编码
            # 直接使用规范化后的路径
            encoded_path = normalized_path

            print(f"[upload_files] 处理文件: {file_path} -> {encoded_path}")

            # 去重检查
            if encoded_path in seen_paths:
                print(f"警告: 跳过重复路径 {encoded_path}")
                continue

            seen_paths.add(encoded_path)

            # 读取文件内容
            if isinstance(content, str):
                content = content.encode('utf-8')

            try:
                blob_url = f'{self.BASE_URL}/repos/{owner}/{repo_name}/git/blobs'
                blob_data = {
                    'content': base64.b64encode(content).decode('utf-8'),
                    'encoding': 'base64'
                }
                blob = self._request(blob_url, method='POST', data=blob_data)
                blobs[encoded_path] = blob['sha']
                print(f"[upload_files] blob 创建成功: {encoded_path}")
            except Exception as e:
                print(f"警告: 创建blob失败 {encoded_path}: {e}")
                continue

        # 如果没有文件，直接返回
        print(f"[upload_files] 共创建了 {len(blobs)} 个 blob")
        if not blobs:
            raise Exception("没有有效的文件可上传")

        # 创建tree
        tree_url = f'{self.BASE_URL}/repos/{owner}/{repo_name}/git/trees'
        tree_items = [
            {
                'path': path,
                'mode': '100644',
                'type': 'blob',
                'sha': sha
            }
            for path, sha in sorted(blobs.items())  # 排序以确保一致性
        ]

        print(f"[upload_files] 准备上传 {len(tree_items)} 个文件到GitHub...")
        print(f"[upload_files] tree items 列表（前10个和最后5个）:")
        if tree_items:
            for item in tree_items[:10]:
                print(f"  - {item['path']}")
            if len(tree_items) > 15:
                print(
                    f"  ... (共 {len(tree_items)} 个文件，中间 {len(tree_items)-15} 个略去) ...")
                for item in tree_items[-5:]:
                    print(f"  - {item['path']}")
            elif len(tree_items) > 10:
                for item in tree_items[10:]:
                    print(f"  - {item['path']}")

        # 处理超过300个文件的情况 - 使用嵌套树
        if len(tree_items) > 300:
            print(f"[upload_files] 文件数 {len(tree_items)} 超过300个限制，使用嵌套树策略...")
            tree = self._create_nested_tree(
                owner, repo_name, tree_items, tree_url)
        else:
            print(f"[upload_files] 不使用 base_tree（完全覆盖模式）")
            tree_data = {
                'tree': tree_items
            }

            try:
                tree = self._request(tree_url, method='POST', data=tree_data)
                print(f"[upload_files] tree 创建成功，sha: {tree['sha']}")
            except Exception as e:
                print(f"树创建错误详情: {e}")
                print(f"树项数: {len(tree_items)}")
                raise Exception(f"创建树失败: {e}")

        # 创建commit
        commit_url = f'{self.BASE_URL}/repos/{owner}/{repo_name}/git/commits'
        commit_data = {
            'message': commit_message,
            'tree': tree['sha'],
            'parents': [branch_info['commit']['sha']]
        }
        print(f"[upload_files] 正在创建 commit...")
        commit = self._request(commit_url, method='POST', data=commit_data)
        print(f"[upload_files] commit 创建成功，sha: {commit['sha']}")

        # 更新分支引用
        ref_url = f'{self.BASE_URL}/repos/{owner}/{repo_name}/git/refs/heads/{branch}'
        ref_data = {
            'sha': commit['sha'],
            'force': True
        }
        print(f"[upload_files] 正在更新分支引用...")
        self._request(ref_url, method='PATCH', data=ref_data)
        print(f"[upload_files] 分支引用已更新，{branch} 现在指向 {commit['sha']}")

        return commit['sha']

    def delete_all_files(self, owner, repo_name, branch):
        """删除分支中的所有文件 - 通过删除并重建分支"""
        try:
            print(f"[delete_all_files] 开始清空分支 {branch}...")

            # 获取默认分支（通常是 main 或 master）
            repo = self.get_repo(owner, repo_name)
            default_branch = repo.get('default_branch', 'main')

            print(f"[delete_all_files] 默认分支: {default_branch}")

            # 如果要删除的分支不是默认分支，可以直接删除并重建
            if branch != default_branch:
                print(f"[delete_all_files] {branch} 不是默认分支，尝试删除...")
                try:
                    ref_url = f'{self.BASE_URL}/repos/{owner}/{repo_name}/git/refs/heads/{branch}'
                    self._request(ref_url, method='DELETE')
                    print(f"[delete_all_files] 分支 {branch} 已删除")

                    # 从默认分支重新创建
                    self.create_branch(
                        owner, repo_name, branch, default_branch)
                    print(
                        f"[delete_all_files] 从 {default_branch} 重新创建了 {branch}")
                    return
                except Exception as e:
                    print(f"[delete_all_files] 删除分支失败: {e}")
                    # 如果是 404，说明分支不存在，直接创建即可
                    if "404" in str(e):
                        print(f"[delete_all_files] 分支 {branch} 不存在，创建新分支...")
                        try:
                            self.create_branch(
                                owner, repo_name, branch, default_branch)
                            print(
                                f"[delete_all_files] 从 {default_branch} 创建了 {branch}")
                            return
                        except Exception as create_error:
                            print(f"[delete_all_files] 创建分支失败: {create_error}")
                            raise
                    else:
                        # 其他错误，尝试备用方案
                        print(f"[delete_all_files] 尝试备用方案...")

            # 备用方案：直接覆盖（在上传时不使用 base_tree）
            print(f"[delete_all_files] 分支清空策略：在上传时使用完全覆盖方式")

        except Exception as e:
            print(f"[delete_all_files] 错误: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"清空分支失败: {str(e)}")


class VerifyGitHubToken:
    """验证GitHub Token"""
    description = "Verifies GitHub access token."

    def execute(self, token):
        """验证token"""
        api = GitHubAPI(token)
        is_valid, result = api.verify_token()

        if is_valid:
            return {
                'success': True,
                'username': result,
                'message': f'Token验证成功！用户名: {result}'
            }
        else:
            return {
                'success': False,
                'message': f'Token验证失败: {result}'
            }


class SaveGitHubConfig:
    """保存GitHub配置"""
    description = "Saves GitHub configuration."

    def execute(self, token, repo_name):
        """保存配置"""
        GitHubConfig.save(token, repo_name)
        return {
            'success': True,
            'message': f'配置已保存: {repo_name}'
        }


class LoadGitHubConfig:
    """加载GitHub配置"""
    description = "Loads GitHub configuration."

    def execute(self):
        """加载配置"""
        return GitHubConfig.load()


class PushToGitHub:
    """推送到GitHub"""
    description = "Pushes blog content to GitHub repository."

    def execute(self, token, repo_name, progress_callback=None):
        """
        推送内容到GitHub
        progress_callback: 进度回调函数 callback(message, percent)
        """
        def report_progress(msg, percent):
            if progress_callback:
                progress_callback(msg, percent)

        try:
            base_path = get_base_path()
            dist_path = os.path.join(base_path, 'dist')
            public_path = os.path.join(base_path, 'public')

            # 验证目录存在
            if not os.path.exists(dist_path):
                raise Exception("dist 目录不存在，请先构建项目")
            if not os.path.exists(public_path):
                raise Exception("public 目录不存在")

            report_progress("正在连接 GitHub...", 5)
            api = GitHubAPI(token)

            # 验证token
            is_valid, username = api.verify_token()
            if not is_valid:
                raise Exception(f"Token验证失败: {username}")

            report_progress(f"已连接为用户: {username}", 10)

            # 检查仓库是否存在
            repo = api.get_repo(username, repo_name)
            if not repo:
                report_progress(f"仓库不存在，正在创建 {repo_name}...", 15)
                repo = api.create_repo(repo_name)
                report_progress("仓库创建成功", 20)
            else:
                report_progress(f"找到仓库: {repo_name}", 20)

            # 获取默认分支
            default_branch = api.get_default_branch(username, repo_name)
            report_progress(f"默认分支: {default_branch}", 25)

            # 确保 source 分支存在
            source_branch = api.get_branch(username, repo_name, 'source')
            if not source_branch:
                report_progress("创建 source 分支...", 30)
                api.create_branch(username, repo_name,
                                  'source', default_branch)

            # 收集 dist 目录的文件
            report_progress("正在收集 dist 文件...", 35)
            dist_files = {}
            for root, dirs, files in os.walk(dist_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(
                        file_path, dist_path).replace('\\', '/')
                    print(f"[收集文件] dist: {rel_path}")
                    with open(file_path, 'rb') as f:
                        dist_files[rel_path] = f.read()

            report_progress(f"找到 {len(dist_files)} 个 dist 文件", 45)
            print(f"[收集文件完整列表] dist 文件: {sorted(dist_files.keys())}")

            # 添加 .nojekyll 文件以禁用 Jekyll 处理
            # 这样 GitHub Pages 会直接提供静态文件，不会忽略下划线开头的文件
            dist_files['.nojekyll'] = b''
            print("[收集文件] 添加 .nojekyll 文件以禁用 Jekyll")

            # 收集 public 目录的文件
            report_progress("正在收集 public 文件...", 50)
            public_files = {}
            for root, dirs, files in os.walk(public_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(
                        file_path, public_path).replace('\\', '/')
                    print(f"[收集文件] public: {rel_path}")
                    with open(file_path, 'rb') as f:
                        public_files[rel_path] = f.read()

            report_progress(f"找到 {len(public_files)} 个 public 文件", 60)
            print(f"[收集文件完整列表] public 文件: {sorted(public_files.keys())}")

            # 推送 dist 到默认分支（先清空，再上传）
            report_progress(f"正在清空 {default_branch} 分支原有内容...", 63)
            api.delete_all_files(username, repo_name, default_branch)

            report_progress(f"正在推送到 {default_branch} 分支...", 65)

            # 直接上传所有dist文件（不分批，确保所有文件在一个commit中）
            api.upload_files(
                username, repo_name, default_branch,
                dist_files,
                f'Deploy blog [{len(dist_files)} files]'
            )

            report_progress(f"推送进度: {len(dist_files)}/{len(dist_files)}", 80)
            report_progress(f"{default_branch} 分支推送完成", 80)

            # 推送 public 到 source 分支（先清空，再上传）
            report_progress("正在清空 source 分支原有内容...", 83)
            api.delete_all_files(username, repo_name, 'source')

            report_progress("正在推送到 source 分支...", 85)

            # 直接上传所有public文件（不分批）
            api.upload_files(
                username, repo_name, 'source',
                public_files,
                f'Update source [{len(public_files)} files]'
            )

            report_progress(
                f"推送进度: {len(public_files)}/{len(public_files)}", 90)
            report_progress("source 分支推送完成", 95)

            repo_url = f"https://github.com/{username}/{repo_name}"
            pages_url = f"https://{username}.github.io/{repo_name}/"

            report_progress("推送完成！", 100)

            return {
                'success': True,
                'message': f'推送成功！\n仓库: {repo_url}\nPages: {pages_url}',
                'repo_url': repo_url,
                'pages_url': pages_url
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'推送失败: {str(e)}'
            }


class FullDeploy:
    """完整部署流程：Generate -> Build -> Push"""
    description = "Complete deployment: Generate, Build, and Push to GitHub."

    def _update_configs_for_deploy(self, repo_name, api, progress_callback=None):
        """自动修改 vite.config.js 和 src/config.js 以适应 GitHub Pages"""
        def report_progress(msg, percent):
            print(f"[Step 0 调试] {msg}")
            if progress_callback:
                progress_callback(msg, percent)

        try:
            base_path = get_base_path()
            report_progress(f"基础路径: {base_path}", 1)

            # 获取用户名以构建 URL
            report_progress("正在获取 GitHub 用户名...", 2)
            success, username = api.verify_token()
            if not success:
                raise Exception("无法获取 GitHub 用户名，部署终止")

            report_progress(f"用户名: {username}", 3)

            # 判断是否是个人主页仓库 (username.github.io)
            is_personal_site = repo_name == f"{username}.github.io"
            report_progress(
                f"仓库类型: {'个人主页' if is_personal_site else '普通项目'}", 4)

            if is_personal_site:
                project_url = f"https://{username}.github.io"
                vite_base = "/"
            else:
                project_url = f"https://{username}.github.io/{repo_name}"
                vite_base = f"/{repo_name}/"

            report_progress(f"项目URL: {project_url}", 5)
            report_progress(f"Vite base: {vite_base}", 6)

            # 1. 修改 vite.config.js 的 base
            vite_config_path = os.path.join(base_path, 'vite.config.js')
            report_progress(f"检查 vite.config.js: {vite_config_path}", 7)

            if os.path.exists(vite_config_path):
                report_progress("文件存在，开始修改...", 8)
                with open(vite_config_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                report_progress(f"读取 {len(lines)} 行", 9)

                with open(vite_config_path, 'w', encoding='utf-8') as f:
                    base_added = False
                    for i, line in enumerate(lines):
                        if 'base:' in line and not base_added:
                            report_progress(f"在第 {i+1} 行找到 base，进行替换", 10)
                            f.write(f"  base: '{vite_base}',\n")
                            base_added = True
                        elif 'export default defineConfig({' in line and not base_added:
                            report_progress(
                                f"在第 {i+1} 行找到 defineConfig，插入 base", 11)
                            f.write(line)
                            f.write(f"  base: '{vite_base}',\n")
                            base_added = True
                        else:
                            f.write(line)

                    if not base_added:
                        report_progress(
                            "警告：未找到 base 配置或 defineConfig，略过修改", 12)

                report_progress("vite.config.js 修改完成", 13)
            else:
                report_progress(
                    f"警告: vite.config.js 不存在: {vite_config_path}", 13)

            # 2. 修改 src/config.js 的 ProjectUrl
            src_config_path = os.path.join(base_path, 'src', 'config.js')
            report_progress(f"检查 src/config.js: {src_config_path}", 14)

            if os.path.exists(src_config_path):
                report_progress("文件存在，开始修改...", 15)
                with open(src_config_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                report_progress(f"读取文件内容，大小: {len(content)} 字节", 16)

                import re
                old_content = content
                # 改进的正则表达式，支持更多格式
                content = re.sub(
                    r"ProjectUrl\s*:\s*['\"].*?['\"]",
                    f"ProjectUrl: '{project_url}'",
                    content
                )

                if old_content != content:
                    report_progress("ProjectUrl 已修改", 17)
                else:
                    report_progress("警告：ProjectUrl 未找到或未修改", 17)
                    # 尝试直接查找和替换
                    if 'ProjectUrl:' in content:
                        report_progress("找到 ProjectUrl:，尝试替换...", 17.5)
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if 'ProjectUrl:' in line:
                                report_progress(
                                    f"在第 {i+1} 行找到 ProjectUrl: {line[:60]}", 17.6)

                with open(src_config_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                report_progress("src/config.js 修改完成", 18)
            else:
                report_progress(
                    f"警告: src/config.js 不存在: {src_config_path}", 18)

            report_progress("Step 0 完成！", 20)

        except Exception as e:
            report_progress(f"ERROR: {str(e)}", 19)
            import traceback
            traceback.print_exc()
            raise

    def execute(self, token, repo_name, progress_callback=None):
        """执行完整部署"""
        from commands import Generate, Build

        def report_progress(msg, percent):
            print(f"[FullDeploy] {msg}")
            if progress_callback:
                progress_callback(msg, percent)

        try:
            api = GitHubAPI(token)

            # Step 0: Pre-config
            report_progress("Step 0/3: 正在自动调整配置文件...", 5)
            self._update_configs_for_deploy(repo_name, api, report_progress)
            report_progress("配置文件已调整", 8)

            # Step 1: Generate
            report_progress("Step 1/3: 正在生成配置文件...", 10)
            try:
                generate_cmd = Generate()
                report_progress("Generate 命令创建完成，开始执行...", 12)
                generate_result = generate_cmd.execute()
                report_progress(
                    f"Generate 执行完成，结果: {generate_result[:100]}", 25)
            except Exception as e:
                report_progress(f"ERROR in Generate: {str(e)}", 15)
                import traceback
                traceback.print_exc()
                raise

            # Step 2: Build
            report_progress("Step 2/3: 正在构建项目...", 30)
            try:
                build_cmd = Build()
                report_progress("Build 命令创建完成，开始执行...", 35)
                build_result = build_cmd.execute()
                report_progress(f"Build 执行完成，结果: {build_result[:100]}", 50)
            except Exception as e:
                report_progress(f"ERROR in Build: {str(e)}", 40)
                import traceback
                traceback.print_exc()
                raise

            # Step 3: Push
            report_progress("Step 3/3: 正在推送到 GitHub...", 55)

            def push_progress(msg, percent):
                # 将 push 的进度映射到 55-100
                adjusted_percent = 55 + (percent / 100) * 45
                report_progress(msg, adjusted_percent)

            push_cmd = PushToGitHub()
            report_progress("PushToGitHub 命令创建完成，开始执行...", 58)
            push_result = push_cmd.execute(token, repo_name, push_progress)

            if push_result['success']:
                return {
                    'success': True,
                    'message': f"部署完成！\n\n{push_result['message']}",
                    'repo_url': push_result.get('repo_url'),
                    'pages_url': push_result.get('pages_url')
                }
            else:
                return push_result

        except Exception as e:
            return {
                'success': False,
                'message': f'部署失败: {str(e)}'
            }
