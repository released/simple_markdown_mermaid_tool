# AGENTS.md

## Project Purpose

This project builds a standalone local Markdown/Mermaid preview and export tool.

- Users edit Markdown in the left pane.
- Users preview rendered Markdown and Mermaid diagrams in the right pane.
- Users load Markdown and INI paths from the top toolbar.
- Users export HTML/PDF/PNG/JPG from the current editor content.
- User settings are persisted in an INI file.

## Local Rules

- Keep the layout aligned with the sibling simple tools:
  - `src\`
  - `scripts\`
  - `docs\`
  - `demo_code\`
  - root `README.md`, `AGENTS.md`, `SELF_CHECK.md`, `HANDOFF.md`
- Keep the Python runtime dependency-free unless a requirement is explicitly approved.
- Keep the browser UI static and served by the local stdlib HTTP server.
- HTML export must continue to work even if Edge/Chrome headless export is unavailable.
- Do not refactor unrelated files when adjusting output formats or UI layout.

## Verification Expectations

- Workspace directory-layout reference: `#READ_ME_FIRST#/PROJECT_LAYOUT.md`.
- This project is the Python directory-layout golden sample, not a dependency/template requirement for every Python tool.
- PyInstaller work/spec files belong under `build/obj/pyinstaller`; the deliverable stays at `build/MarkdownMermaidTool.exe`.
- Run `scripts/clean_python.bat` only for compiler/cache cleanup; preserve EXE, INI, outputs, logs, and unknown files.
- Run `python -m unittest discover -s tests -v` for source layout/resource smoke. After building the EXE, set `PC_TOOL_TEST_EXE=1` to include the isolated packaged-resource HTTP test; the default skip is not an EXE verification result.

Run syntax checks:

```powershell
python -m compileall src
```

Run the tool:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_tool.ps1
```

Build optional executable:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_exe.ps1
```

Expected output:

- `build\MarkdownMermaidTool.exe`
