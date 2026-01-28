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
        'yaml',
        'json',
        'subprocess',
        'threading',
        'webbrowser',
        # FastAPI 和 uvicorn 相关
        'fastapi',
        'fastapi.routing',
        'fastapi.middleware',
        'fastapi.middleware.cors',
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'pydantic',
        'pydantic.fields',
        'starlette',
        'starlette.routing',
        'starlette.middleware',
        'starlette.middleware.cors',
        'anyio',
        'h11',
        'httptools',
        'websockets',
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
        'test',
        'unittest',
        'pytest',
        'pip',
        'jupyter',
        'notebook',
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
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口（发布版本）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='public/favicon.ico' if os.path.exists('public/favicon.ico') else None,
)
