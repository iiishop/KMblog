import os
import sys


def get_base_path():
    """
    获取基础路径（项目根目录）
    当打包成exe时，需要正确处理路径
    """
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe
        return os.path.dirname(sys.executable)
    else:
        # 如果是开发环境
        # 如果当前文件在mainTools目录下，返回上级目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir.endswith('mainTools'):
            return os.path.dirname(current_dir)
        return current_dir


def get_posts_path():
    """获取Posts目录路径"""
    return os.path.join(get_base_path(), 'src', 'Posts')


def get_assets_path():
    """获取assets目录路径"""
    return os.path.join(get_base_path(), 'src', 'assets')
