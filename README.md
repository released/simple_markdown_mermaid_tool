# Simple Markdown Mermaid Tool

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

PyInstaller is used only for packaging. The source app itself uses the Python standard library.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_exe.ps1
```

Output:

```text
build\MarkdownMermaidTool.exe
```

## Vendor JavaScript

The preview uses:

- `marked` for Markdown parsing.
- `mermaid` for Mermaid diagrams.

Local copies can be refreshed with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\download_vendor.ps1
```

If local vendor files are missing, the browser UI falls back to jsDelivr CDN.
