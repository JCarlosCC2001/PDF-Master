# -*- mode: python ; coding: utf-8 -*-
# PDF Master.spec
# ---------------
# Archivo de configuracion de PyInstaller para PDF Master.
# Uso:
#   pyinstaller "PDF Master.spec"
#   (o ejecutar build.bat)

import os
from pathlib import Path

ROOT = Path(os.path.abspath(SPECPATH))

datas = []

assets_dir = ROOT / "assets"
if assets_dir.exists():
    datas.append((str(assets_dir), "assets"))

config_json = ROOT / "config.json"
if config_json.exists():
    datas.append((str(config_json), "."))

hiddenimports = [
    "PyQt6.QtCore",
    "PyQt6.QtGui",
    "PyQt6.QtWidgets",
    "PyQt6.QtPrintSupport",
    "pymupdf",
    "fitz",
    "pikepdf",
    "PIL",
    "PIL.Image",
    "PIL.ImageQt",
    "img2pdf",
    "reportlab",
    "reportlab.pdfgen",
    "reportlab.lib",
    "reportlab.lib.pagesizes",
]

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "scipy", "test", "unittest"],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PDF Master",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "assets" / "icon.ico"),
    version_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="PDF Master",
)
