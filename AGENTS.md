# AGENTS.md

## Verified packaging size contract (2026-10-25)

- Canonical source spec: scripts/build/MarkdownMermaidTool.spec. Generated work stays
  under build/obj/pyinstaller; never treat the source spec as disposable.
- Exclude only the reviewed tcl8/8.5/tcltest-2.5.7.tm test harness. Keep Tcl/Tk,
  encodings/dialogs, Python/SSL/runtime DLLs, offline Mermaid/marked and licenses.
- If package layout changes, fail closed and have Codex reassess the exact exclusion;
  do not blanket-exclude modules or ask the user to run the audit manually.
- Clean recognizes only exact internal .toc/PYZ/.pkg/base_library.zip names in this
  tool's named work directory. Other package/archive files remain protected.
- Codex invokes the shared clean verifier with -CheckPythonCaches
  -PyInstallerName MarkdownMermaidTool plus nested/reparse/actual checks.
- Build-close logic matches the full canonical EXE path, tries normal close, and
  revalidates PID/start/path before fallback; never close foreign same-named copies.
- Actual scope/raw results: SELF_CHECK.md and docs/verification/exe-slimming-20261025.json.


## File-only Python Clean

Clean must preflight all cache/source paths before calling the companion `scripts/clean_intermediates.ps1`. Remove allowlisted compiler/PyInstaller files in build/obj and only .pyc/.pyo inside root/source/test/script __pycache__; never recursively purge obj/cache folders. Preserve EXE/INI/unknown files inside those folders; remove only empty directories. Keep both cleaner/helper when reusing this profile and run expanded preservation tests automatically.


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

- The Python clean also removes the explicitly named project-root `__pycache__`; do not scan private output trees for arbitrary folders to purge.

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
