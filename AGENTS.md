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
