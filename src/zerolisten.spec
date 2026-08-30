# -*- mode: python ; coding: utf-8 -*-
# ZeroListen PyInstaller 打包配置 (onedir 模式)。
# 运行方式: python -m PyInstaller --noconfirm --clean zerolisten.spec
#
# 注意:
#   1. 必须使用 64 位 Python 3.11(Argos Translate 的 ctranslate2 无 32 位包)。
#   2. 打包后还需把 tts_cli.js / node_modules / 模型文件 拷到 dist\ZeroListen\,
#      见 build.bat。

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

datas = []
binaries = []

# Argos Translate 及其底层引擎带有数据文件/动态库, 需一并收集。
for pkg in ["argostranslate", "ctranslate2", "sentencepiece", "pycountry"]:
    try:
        datas += collect_data_files(pkg)
    except Exception:
        pass
    try:
        binaries += collect_dynamic_libs(pkg)
    except Exception:
        pass

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["PyQt5", "PyQt6", "PySide2", "PySide6", "tkinter"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ZeroListen",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="ZeroListen",
)
