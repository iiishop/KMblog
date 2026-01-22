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
                return json.loads(response.read().decode('utf-8'))
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

    def upload_files(self, owner, repo_name, branch, files_dict, commit_message):
        """批量上传文件到指定分支
        files_dict: {relative_path: file_content}
        """
        # 获取当前分支的最新commit
        branch_info = self.get_branch(owner, repo_name, branch)
        if not branch_info:
            raise Exception(f"Branch '{branch}' not found")

        base_tree_sha = branch_info['commit']['commit']['tree']['sha']

        # 创建blob对象
        blobs = {}
        for file_path, content in files_dict.items():
            # 读取文件内容
            if isinstance(content, str):
                content = content.encode('utf-8')

            blob_url = f'{self.BASE_URL}/repos/{owner}/{repo_name}/git/blobs'
            blob_data = {
                'content': base64.b64encode(content).decode('utf-8'),
                'encoding': 'base64'
            }
            blob = self._request(blob_url, method='POST', data=blob_data)
            blobs[file_path] = blob['sha']

        # 创建tree
        tree_url = f'{self.BASE_URL}/repos/{owner}/{repo_name}/git/trees'
        tree_items = [
            {
                'path': path,
                'mode': '100644',
                'type': 'blob',
                'sha': sha
            }
            for path, sha in blobs.items()
        ]

        tree_data = {
            'base_tree': base_tree_sha,
            'tree': tree_items
        }
        tree = self._request(tree_url, method='POST', data=tree_data)

        # 创建commit
        commit_url = f'{self.BASE_URL}/repos/{owner}/{repo_name}/git/commits'
        commit_data = {
            'message': commit_message,
            'tree': tree['sha'],
            'parents': [branch_info['commit']['sha']]
        }
        commit = self._request(commit_url, method='POST', data=commit_data)

        # 更新分支引用
        ref_url = f'{self.BASE_URL}/repos/{owner}/{repo_name}/git/refs/heads/{branch}'
        ref_data = {
            'sha': commit['sha'],
            'force': True
        }
        self._request(ref_url, method='PATCH', data=ref_data)

        return commit['sha']

    def delete_all_files(self, owner, repo_name, branch):
        """删除分支中的所有文件"""
        # 获取当前分支的tree
        branch_info = self.get_branch(owner, repo_name, branch)
        if not branch_info:
            return

        # 创建空tree
        tree_url = f'{self.BASE_URL}/repos/{owner}/{repo_name}/git/trees'
        tree_data = {'tree': []}
        tree = self._request(tree_url, method='POST', data=tree_data)

        # 创建commit
        commit_url = f'{self.BASE_URL}/repos/{owner}/{repo_name}/git/commits'
        commit_data = {
            'message': 'Clear all files',
            'tree': tree['sha'],
            'parents': [branch_info['commit']['sha']]
        }
        commit = self._request(commit_url, method='POST', data=commit_data)

        # 更新分支引用
        ref_url = f'{self.BASE_URL}/repos/{owner}/{repo_name}/git/refs/heads/{branch}'
        ref_data = {'sha': commit['sha'], 'force': True}
        self._request(ref_url, method='PATCH', data=ref_data)


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
                    with open(file_path, 'rb') as f:
                        dist_files[rel_path] = f.read()

            report_progress(f"找到 {len(dist_files)} 个 dist 文件", 45)

            # 收集 public 目录的文件
            report_progress("正在收集 public 文件...", 50)
            public_files = {}
            for root, dirs, files in os.walk(public_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(
                        file_path, public_path).replace('\\', '/')
                    with open(file_path, 'rb') as f:
                        public_files[rel_path] = f.read()

            report_progress(f"找到 {len(public_files)} 个 public 文件", 60)

            # 推送 dist 到默认分支
            report_progress(f"正在推送到 {default_branch} 分支...", 65)

            # 分批上传（GitHub API限制）
            batch_size = 100
            dist_items = list(dist_files.items())
            for i in range(0, len(dist_items), batch_size):
                batch = dict(dist_items[i:i+batch_size])
                api.upload_files(
                    username, repo_name, default_branch,
                    batch,
                    f'Deploy blog [{i+1}-{min(i+batch_size, len(dist_items))}/{len(dist_items)}]'
                )
                progress = 65 + (i / len(dist_items)) * 15
                report_progress(
                    f"推送进度: {i+len(batch)}/{len(dist_items)}", progress)

            report_progress(f"{default_branch} 分支推送完成", 80)

            # 推送 public 到 source 分支
            report_progress("正在推送到 source 分支...", 85)

            public_items = list(public_files.items())
            for i in range(0, len(public_items), batch_size):
                batch = dict(public_items[i:i+batch_size])
                api.upload_files(
                    username, repo_name, 'source',
                    batch,
                    f'Update source [{i+1}-{min(i+batch_size, len(public_items))}/{len(public_items)}]'
                )
                progress = 85 + (i / len(public_items)) * 10
                report_progress(
                    f"推送进度: {i+len(batch)}/{len(public_items)}", progress)

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

    def execute(self, token, repo_name, progress_callback=None):
        """执行完整部署"""
        from commands import Generate, Build

        def report_progress(msg, percent):
            if progress_callback:
                progress_callback(msg, percent)

        try:
            # Step 1: Generate
            report_progress("Step 1/3: 正在生成配置文件...", 10)
            generate_cmd = Generate()
            generate_result = generate_cmd.execute()
            report_progress("配置文件生成完成", 25)

            # Step 2: Build
            report_progress("Step 2/3: 正在构建项目...", 30)
            build_cmd = Build()
            build_result = build_cmd.execute()
            report_progress("项目构建完成", 50)

            # Step 3: Push
            report_progress("Step 3/3: 正在推送到 GitHub...", 55)

            def push_progress(msg, percent):
                # 将 push 的进度映射到 55-100
                adjusted_percent = 55 + (percent / 100) * 45
                report_progress(msg, adjusted_percent)

            push_cmd = PushToGitHub()
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
