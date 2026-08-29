# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:/CodexProjects/BannerlordConsoleAssistant/launcher.py'],
    pathex=['D:/CodexProjects/BannerlordConsoleAssistant/src'],
    binaries=[],
    datas=[('D:/CodexProjects/BannerlordConsoleAssistant/src/bannerlord_assistant/data/commands.json', 'bannerlord_assistant/data')],
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
    name='BannerlordConsoleAssistant',
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
)
