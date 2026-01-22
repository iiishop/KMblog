# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['blog_manager.py'],
    pathex=[],
    binaries=[],
    datas=[('mainTools', 'mainTools')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='KMblogManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='C:\\Users\\iiishop\\AppData\\Local\\Temp\\e916b981-d7d4-486b-8b56-3f647da5a177',
)
