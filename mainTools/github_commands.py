"""
GitHub 相关命令 - 用于部署博客到 GitHub Pages
优化版本：差异检查、增量上传
"""
import os
import json
import base64
import hashlib
from urllib import request, error
from path_utils import get_base_path


# ============== 辅助函数 ==============

def normalize_path(path):
    """规范化路径：统一分隔符、移除空部分"""
    normalized = path.strip().replace('\\', '/')
    return '/'.join(p for p in normalized.split('/') if p)


def calculate_git_sha(content):
    """计算文件内容的Git SHA-1哈希值"""
    if isinstance(content, str):
        content = content.encode('utf-8')
    # Git的blob SHA计算方式：sha1("blob " + filesize + "\0" + content)
    header = f"blob {len(content)}\0".encode('utf-8')
    return hashlib.sha1(header + content).hexdigest()


def collect_directory_files(directory_path, prefix=''):
    """收集目录下的所有文件

    Args:
        directory_path: 目录路径
        prefix: 日志前缀

    Returns:
        dict: {相对路径: 文件内容(bytes)}
    """
    files = {}
    for root, dirs, filenames in os.walk(directory_path):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            rel_path = os.path.relpath(
                file_path, directory_path).replace('\\', '/')
            if prefix:
                print(f"[收集文件] {prefix}: {rel_path}")
            with open(file_path, 'rb') as f:
                files[rel_path] = f.read()
    return files


# ============== 配置管理 ==============

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

    def get_tree_files(self, owner, repo_name, tree_sha):
        """递归获取树中所有文件的路径和SHA"""
        url = f'{self.BASE_URL}/repos/{owner}/{repo_name}/git/trees/{tree_sha}?recursive=1'
        try:
            tree = self._request(url)
            files = {}
            for item in tree.get('tree', []):
                if item['type'] == 'blob':  # 只关注文件，不包括目录
                    files[item['path']] = item['sha']
            return files
        except Exception as e:
            print(f"[差异检查] 获取远程文件列表失败: {e}")
            return {}

    def upload_files(self, owner, repo_name, branch, files_dict, commit_message, use_diff=True):
        """批量上传文件到指定分支
        files_dict: {relative_path: file_content}
        use_diff: 是否使用差异检查（默认True）
        """
        # 获取当前分支的最新commit
        branch_info = self.get_branch(owner, repo_name, branch)
        if not branch_info:
            raise Exception(f"Branch '{branch}' not found")

        base_tree_sha = branch_info['commit']['commit']['tree']['sha']

        # 差异检查
        if use_diff:
            print(f"[差异检查] 开始检查文件差异...")
            remote_files = self.get_tree_files(owner, repo_name, base_tree_sha)
            print(f"[差异检查] 远程有 {len(remote_files)} 个文件")

            # 计算本地文件SHA并比对
            changed_files = {}
            new_files = {}
            unchanged_count = 0

            for path, content in files_dict.items():
                normalized_path = normalize_path(path)  # 使用辅助函数
                local_sha = calculate_git_sha(content)  # 使用辅助函数
                remote_sha = remote_files.get(normalized_path)

                if remote_sha is None:
                    new_files[normalized_path] = content
                elif remote_sha != local_sha:
                    changed_files[normalized_path] = content
                else:
                    unchanged_count += 1

            print(
                f"[差异检查] 新增: {len(new_files)} 个, 修改: {len(changed_files)} 个, 未变: {unchanged_count} 个")

            # 只处理有变化的文件
            files_to_upload = {**new_files, **changed_files}

            if not files_to_upload:
                print(f"[差异检查] 没有文件需要上传，跳过")
                return branch_info['commit']['sha']

            print(f"[差异检查] 将上传 {len(files_to_upload)} 个有变化的文件")
            files_dict = files_to_upload

        # 创建blob对象
        blobs = {}
        seen_paths = set()

        print(f"[upload_files] 开始处理 {len(files_dict)} 个文件...")
        for file_path, content in files_dict.items():
            normalized_path = normalize_path(file_path)  # 使用辅助函数

            # 去重检查
            if normalized_path in seen_paths:
                print(f"警告: 跳过重复路径 {normalized_path}")
                continue
            seen_paths.add(normalized_path)

            # 确保内容是bytes
            if isinstance(content, str):
                content = content.encode('utf-8')

            try:
                blob_url = f'{self.BASE_URL}/repos/{owner}/{repo_name}/git/blobs'
                blob_data = {
                    'content': base64.b64encode(content).decode('utf-8'),
                    'encoding': 'base64'
                }
                blob = self._request(blob_url, method='POST', data=blob_data)
                blobs[normalized_path] = blob['sha']
                print(f"[upload_files] blob 创建成功: {normalized_path}")
            except Exception as e:
                print(f"警告: 创建blob失败 {normalized_path}: {e}")
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
            # 使用base_tree保留未修改的文件（差异更新模式）
            if use_diff:
                print(f"[upload_files] 使用差异更新模式（保留未修改文件）")
                tree_data = {
                    'base_tree': base_tree_sha,
                    'tree': tree_items
                }
            else:
                print(f"[upload_files] 使用完全覆盖模式")
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


# ============== 命令类 ==============

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
            dist_files = collect_directory_files(dist_path)
            for rel_path in dist_files:
                print(f"[收集文件] dist: {rel_path}")

            report_progress(f"找到 {len(dist_files)} 个 dist 文件", 45)
            print(f"[收集文件完整列表] dist 文件: {sorted(dist_files.keys())}")

            # 添加 .nojekyll 文件以禁用 Jekyll 处理
            # 这样 GitHub Pages 会直接提供静态文件，不会忽略下划线开头的文件
            dist_files['.nojekyll'] = b''
            print("[收集文件] 添加 .nojekyll 文件以禁用 Jekyll")

            # 收集 public 目录的文件
            report_progress("正在收集 public 文件...", 50)
            public_files = collect_directory_files(public_path)
            for rel_path in public_files:
                print(f"[收集文件] public: {rel_path}")

            report_progress(f"找到 {len(public_files)} 个 public 文件", 60)
            print(f"[收集文件完整列表] public 文件: {sorted(public_files.keys())}")

            # 推送 dist 到默认分支（使用差异更新）
            report_progress(f"正在推送到 {default_branch} 分支...", 65)

            # 差异上传dist文件
            api.upload_files(
                username, repo_name, default_branch,
                dist_files,
                f'Deploy blog [{len(dist_files)} files]',
                use_diff=True  # 启用差异检查
            )

            report_progress(f"{default_branch} 分支推送完成", 80)

            # 推送 public 到 source 分支（使用差异更新）
            report_progress("正在推送到 source 分支...", 85)

            # 差异上传public文件
            api.upload_files(
                username, repo_name, 'source',
                public_files,
                f'Update source [{len(public_files)} files]',
                use_diff=True  # 启用差异检查
            )

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

    def _update_configs_for_deploy(self, repo_name, api):
        """自动修改 src/config.js 以适应 GitHub Pages"""
        try:
            base_path = get_base_path()

            # 获取用户名以构建 URL
            success, username = api.verify_token()
            if not success:
                raise Exception("无法获取 GitHub 用户名，部署终止")

            # 判断是否是个人主页仓库 (username.github.io)
            is_personal_site = repo_name == f"{username}.github.io"

            if is_personal_site:
                project_url = f"https://{username}.github.io"
            else:
                project_url = f"https://{username}.github.io/{repo_name}"

            # 修改 src/config.js 的 ProjectUrl
            src_config_path = os.path.join(base_path, 'src', 'config.js')

            if os.path.exists(src_config_path):
                with open(src_config_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                import re
                # 修改ProjectUrl
                content = re.sub(
                    r"ProjectUrl\s*:\s*['\"].*?['\"]",
                    f"ProjectUrl: '{project_url}'",
                    content
                )

                with open(src_config_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                print(f"[配置] ProjectUrl 已更新为: {project_url}")

        except Exception as e:
            print(f"[配置] 调整失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def execute(self, token, repo_name):
        """执行完整部署"""
        from commands import Generate, Build

        try:
            api = GitHubAPI(token)

            # Step 0: 调整配置
            print("[FullDeploy] 正在调整配置文件...")
            self._update_configs_for_deploy(repo_name, api)

            # Step 1: Generate
            print("[FullDeploy] 正在生成配置...")
            generate_cmd = Generate()
            generate_result = generate_cmd.execute()

            # Step 2: Build
            print("[FullDeploy] 正在构建项目...")
            build_cmd = Build()
            build_result = build_cmd.execute()

            # Step 3: Push
            print("[FullDeploy] 正在推送到 GitHub...")
            push_cmd = PushToGitHub()
            push_result = push_cmd.execute(token, repo_name)

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
