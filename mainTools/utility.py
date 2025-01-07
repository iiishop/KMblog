import os
import re
from datetime import datetime

def parse_markdown_metadata(file_path):
    """
    解析 Markdown 文件中的元数据
    """
    with open(file_path, 'r') as file:
        content = file.read()
        metadata = {}
        title_match = re.search(r'^title:\s*(.+)$', content, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
    return metadata

def read_markdowns(dir_path):
    """
    读取给定目录中的 Markdown 文件
    """
    return [
        os.path.join(dir_path, file)
        for file in os.listdir(dir_path)
        if file.endswith('.md')
    ]

def find_first_image(dir_path):
    """
    查找给定目录中的第一个图片文件
    """
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif']
    for file in os.listdir(dir_path):
        if any(file.endswith(ext) for ext in image_extensions):
            return os.path.join(dir_path, file)
    return None