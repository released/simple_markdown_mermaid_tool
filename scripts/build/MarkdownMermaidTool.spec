# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

project_root = Path(SPECPATH).resolve().parents[1]
a = Analysis(
    [str(project_root / "src" / "main.py")],
    pathex=[],
    binaries=[],
    datas=[(str(project_root / "src" / "markdown_mermaid_tool" / "static"),
            "markdown_mermaid_tool/static")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# Tk file dialogs need Tcl/Tk. Exclude only the unused Tcl test harness,
# not its runtime, encoding data, native dialogs, licenses or app assets.
test_data = "tcl8/8.5/tcltest-2.5.7.tm"
removed = [entry for entry in a.datas
           if entry[0].replace("\\", "/").lower() == test_data]
if len(removed) != 1:
    raise RuntimeError("Tcl test-data layout changed; reassess before excluding anything.")
a.datas = [entry for entry in a.datas if entry not in removed]

pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name="MarkdownMermaidTool",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
