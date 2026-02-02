import os
import re
from datetime import datetime
import requests
# Util functions


# GitHub 代理配置（为中国大陆用户加速）
GITHUB_PROXIES = [
    {
        'name': '直连 GitHub',
        'api': 'https://api.github.com',
        'raw': 'https://raw.githubusercontent.com',
        'release': 'https://github.com',
        'git': 'https://github.com/iiishop/KMblog.git',
    },
    {
        'name': 'ghproxy.com 镜像',
        'api': 'https://api.github.com',  # API 仍使用官方
        'raw': 'https://ghproxy.com/https://raw.githubusercontent.com',
        'release': 'https://ghproxy.com/https://github.com',
        'git': 'https://ghproxy.com/https://github.com/iiishop/KMblog.git',
    },
    {
        'name': 'mirror.ghproxy.com 镜像',
        'api': 'https://api.github.com',
        'raw': 'https://mirror.ghproxy.com/https://raw.githubusercontent.com',
        'release': 'https://mirror.ghproxy.com/https://github.com',
        'git': 'https://mirror.ghproxy.com/https://github.com/iiishop/KMblog.git',
    },
]


def get_working_github_proxy(timeout=5):
    """获取可用的 GitHub 代理

    Args:
        timeout: 测试超时时间（秒）

    Returns:
        dict: 可用的代理配置，如果都不可用则返回直连配置
    """
    print("[代理检测] 测试 GitHub 连接速度...")

    for proxy in GITHUB_PROXIES:
        try:
            # 测试 API 连接
            test_url = f"{proxy['api']}/repos/iiishop/KMblog"
            response = requests.get(test_url, timeout=timeout)

            if response.status_code == 200:
                print(f"[代理检测] ✓ {proxy['name']} 可用")
                return proxy
            else:
                print(f"[代理检测] ✗ {proxy['name']} 返回状态码 {response.status_code}")
        except Exception as e:
            print(f"[代理检测] ✗ {proxy['name']} 失败: {type(e).__name__}")

    # 如果所有代理都失败，返回直连
    print("[代理检测] 使用直连 GitHub")
    return GITHUB_PROXIES[0]


def get_github_git_url(proxy=None, timeout=5):
    """获取可用的 Git 仓库 URL

    Args:
        proxy: 可选的代理配置，如果未提供则自动检测
        timeout: 测试超时时间（秒）

    Returns:
        str: 可用的 Git URL
    """
    if proxy is None:
        proxy = get_working_github_proxy(timeout)

    return proxy['git']


def read_file_safe(file_path):
    encodings = ['utf-8', 'gbk', 'gb18030', 'utf-16', 'latin-1']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    # Fallback with error ignore
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()


def parse_markdown_metadata(file_path):
    content = read_file_safe(file_path)
    metadata = parse_markdown(content)
    return metadata


def parse_markdown(content):
    import yaml
    metadata_regex = r'^---\n([\s\S]*?)\n---'
    match = re.search(metadata_regex, content)

    if match:
        meta = yaml.safe_load(match.group(1))
        return meta
    else:
        return {}


def read_markdowns(directory, relative_to=None):
    markdowns = []
    for file in os.listdir(directory):
        if file.endswith('.md'):
            file_path = os.path.join(directory, file)
            markdowns.append(file_path)
    return markdowns


def find_first_image(directory, relative_to=None):
    for file in os.listdir(directory):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            file_path = os.path.join(directory, file)
            return file_path
    return None
