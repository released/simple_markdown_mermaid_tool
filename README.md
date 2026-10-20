# Simple Markdown Mermaid Tool

## Safe clean

`scripts/clean_python.bat` removes allowlisted compiler/PyInstaller work files and .pyc/.pyo inside known __pycache__ folders. It never recursively purges build/obj or caches: EXE/INI/DLL/log/data/unknown files remain even there, and only empty directories are removed. `/?`, `-h` and `--help` do not delete anything. Codex verifies this automatically when creating/changing clean scripts.


Local Markdown/Mermaid editor with live preview and export.

## Features

- Left pane Markdown editor.
- Right pane live rendered preview.
- Top toolbar for Markdown path, INI path, output name, output directory, and output formats.
- Output name defaults to the loaded Markdown file stem:
  - `README.md` becomes `README`
  - `application.md` becomes `application`
- Generate selected `html`, `pdf`, `png`, and `jpg` files.
- HTML export is always available.
- PDF/PNG/JPG export uses installed Microsoft Edge or Google Chrome in headless mode.
- Long Mermaid flowcharts are measured after rendering; PNG/JPG use full-page image capture and PDF uses a single long page when Chromium allows it.
- INI saves user-modified paths, output name, output directory, and format selections.

## Run

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_tool.ps1
```

The script starts a local server and opens:

```text
http://127.0.0.1:8765/
```

If the port is already used, the server automatically binds another available port and prints the URL.

## Demo

Load:

```text
demo_code\sample.md
```

Then click `Generate`. The default output directory is `output`.

## Optional Build

This project is the workspace Python **directory-layout** reference. Its browser
UI and standard-library implementation are not mandatory for other Python tools.
See workspace `#READ_ME_FIRST#/PROJECT_LAYOUT.md` for the shared convention.

PyInstaller is used only for packaging. The source app itself uses the Python standard library.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_exe.ps1
```

Output:

```text
build\MarkdownMermaidTool.exe
```

Packaging intermediates and generated spec files are under
`build\obj\pyinstaller`, not the repository root. Existing older `dist`/build
outputs are not silently removed by this layout change.

## Clean

```bat
scripts\clean_python.bat
```

Removes compiler/cache intermediates only. The executable, INI files, logs,
exported reports, unknown delivery files, and existing `dist` outputs are retained.

## Vendor JavaScript

The preview uses:

- `marked` for Markdown parsing.
- `mermaid` for Mermaid diagrams.

Local copies can be refreshed with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\download_vendor.ps1
```

If local vendor files are missing, the browser UI falls back to jsDelivr CDN.
