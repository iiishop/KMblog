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