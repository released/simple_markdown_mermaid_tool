# HANDOFF.md

## Current State

### Layout audit 2026-10-20

- Selected as the workspace Python directory-layout golden sample.
- PyInstaller work/spec output moved to `build/obj/pyinstaller`; the usable EXE
  stays at `build/MarkdownMermaidTool.exe`. Old outputs were not purged.
- Build: `scripts/build_exe.ps1 -CloseRunningTool $false` PASS. Existing
  `pkg_resources` deprecation warning noted; dependencies were not upgraded.
- `PC_TOOL_TEST_EXE=1; python -m unittest discover -s tests -v`: PASS, 2 tests,
  source and isolated packaged-EXE HTTP/static resource smoke.
- `scripts/clean_python.bat`: isolated sentinel/repeat-clean and actual cleanup
  PASS; all 6 protected existing build files unchanged by SHA-256.
- Browser visual/DPI and PDF/PNG/JPG exports: NOT RUN in this folder-only audit.
- Shared batch/publication status: `#READ_ME_FIRST#/PROJECT_LAYOUT_MIGRATION.md`.

The tool is implemented as a local Python HTTP server with a static browser UI.

Important files:

- `src\main.py` - entry point.
- `src\markdown_mermaid_tool\app_server.py` - HTTP server, APIs, file dialogs, MD/INI load.
- `src\markdown_mermaid_tool\settings.py` - INI state model and persistence.
- `src\markdown_mermaid_tool\exporter.py` - HTML/PDF/PNG/JPG generation.
- `src\markdown_mermaid_tool\static\app.js` - UI behavior.
- `src\markdown_mermaid_tool\static\renderer.js` - Markdown/Mermaid rendering.

## Known Tradeoffs

- HTML export is self-contained when local vendor JavaScript is present.
- PDF/PNG/JPG require Edge or Chrome in a common install path or in PATH.
- PNG/JPG use Chromium DevTools full-page capture after measuring the rendered document.
- PDF uses the measured document size for a single long page when it is within Chromium's page-size limit.

## Next Useful Improvements

- Add an editable image-height option for PNG/JPG.
- Add save-back-to-source Markdown support if source file editing becomes a requirement.
- Add a small regression test around `generate_outputs`.
