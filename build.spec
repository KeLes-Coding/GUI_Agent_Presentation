# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# ============================================
# 核心修改区域：确保包含离线资源
# ============================================
added_files = [
    # 1. 使用本地化后的 HTML 作为主入口
    ('index_local.html', '.'), 
    
    # 2. 包含下载的离线资源包 (MathJax/Fonts/Icons)
    ('assets', 'assets'),

    # 3. 其他原有资源
    ('css', 'css'),
    ('js', 'js'),
    ('slides', 'slides'),
]
# ============================================

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='GUI_Agent_Presentation_Offline', # 改个名方便区分
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # 设为 False 隐藏黑框
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)