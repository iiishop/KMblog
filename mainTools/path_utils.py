import os
import sys


def get_base_path():
    """
    获取基础路径（项目根目录）
    当打包成exe时，需要正确处理路径
    
    重要：
    - 打包后：返回 exe 文件所在的目录（用户的工作目录）
    - 开发时：返回项目根目录
    """
    if getattr(sys, 'frozen', False):
        # 打包后的 exe：返回 exe 所在目录
        # sys.executable 是 exe 的完整路径
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        # 开发环境：从当前文件位置推断项目根目录
        # 当前文件在 mainTools 目录下，返回上级目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir.endswith('mainTools'):
            return os.path.dirname(current_dir)
        return current_dir


def get_posts_path():
    """获取Posts目录路径"""
    return os.path.join(get_base_path(), 'public', 'Posts')


def get_assets_path():
    """获取assets目录路径"""
    return os.path.join(get_base_path(), 'public', 'assets')
