# -*- mode: python ; coding: utf-8 -*-

import os

# 获取项目根目录
block_cipher = None
project_root = os.path.abspath('.')

a = Analysis(
    ['blog_manager.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        ('mainTools', 'mainTools'),
        # 如果需要包含其他文件，在这里添加
        # ('public/favicon.ico', 'public'),
    ],
    hiddenimports=[
        'flet',
        'flet.core',
        'flet.utils',
        'PIL',
        'PIL.Image',
        'cryptography',
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.primitives.ciphers',
        'cryptography.hazmat.primitives.ciphers.aead',
        'cryptography.hazmat.primitives.kdf',
        'cryptography.hazmat.primitives.kdf.pbkdf2',
        'requests',
        'markdown',
        'yaml',
        'json',
        'subprocess',
        'threading',
        'webbrowser',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的大型模块以减小体积
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tkinter',
        'test',
        'unittest',
        'pytest',
        # 排除更多不需要的模块
        'IPython',
        'jupyter',
        'notebook',
        'sphinx',
        'setuptools',
        'distutils',
        'pip',
        'wheel',
        # 排除测试相关
        '_pytest',
        'py.test',
        'nose',
        # 排除文档和示例
        'doctest',
        'pydoc',
        'pydoc_data',
        # 排除其他大型库
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'wx',
        'tornado',
        'django',
        'flask',
        'sqlalchemy',
        # 排除 XML 处理（如果不需要）
        'xml.dom',
        'xml.sax',
        'xmlrpc',
        # 排除邮件相关
        'email',
        'smtplib',
        'imaplib',
        'poplib',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KMblogManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # 启用 strip 移除调试符号（Linux/macOS）
    upx=True,  # 启用 UPX 压缩
    upx_exclude=[
        # 排除某些不应该被 UPX 压缩的文件
        'vcruntime140.dll',
        'python3.dll',
        'python311.dll',
    ],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='public/favicon.ico' if os.path.exists('public/favicon.ico') else None,
)
