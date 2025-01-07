import re
# Utility function to parse Markdown metadata
def parse_markdown_metadata(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        metadata = {}
        title_match = re.search(r'^title:\s*(.+)$', content, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
    return metadata