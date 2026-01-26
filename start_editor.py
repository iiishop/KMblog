#!/usr/bin/env python
"""
快速启动Markdown编辑器的脚本
"""

import sys
import os

# 添加mainTools到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mainTools'))

from commands import StartEditor

if __name__ == "__main__":
    print("正在启动Markdown编辑器...")
    editor = StartEditor()
    editor.execute()
