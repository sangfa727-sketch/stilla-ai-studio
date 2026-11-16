# PyInstaller one-folder build for Windows.
# Build from the repository root:
#   python -m pip install -e ".[desktop,dev,image,packaging]"
#   python -m PyInstaller --noconfirm packaging/stilla.spec

from pathlib import Path

from PyInstaller.utils.hooks import collect_all

ROOT = Path(SPECPATH).resolve().parent.parent
PROTOTYPE = ROOT / "apps" / "desktop-prototype"

if not (PROTOTYPE / "index.html").is_file():
    raise SystemExit(f"Desktop prototype assets are missing: {PROTOTYPE}")

webview_datas, webview_binaries, webview_hiddenimports = collect_all("webview")

a = Analysis(
    [str(ROOT / "stilla" / "desktop" / "app.py")],
    pathex=[str(ROOT)],
    binaries=webview_binaries,
    datas=webview_datas + [(str(PROTOTYPE), "apps/desktop-prototype")],
    hiddenimports=webview_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="STILLA-AI-Studio",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="STILLA-AI-Studio",
)
