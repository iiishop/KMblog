import os
import re
from datetime import datetime
# Util functions


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
