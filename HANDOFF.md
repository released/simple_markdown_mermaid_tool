# HANDOFF.md

## Verified EXE slimming 2026-10-25

- Exact comparable EXE 12902984 -> 12875387 bytes (27597 saved).
- Formal SHA: 0B53FA841A7BD75ADA4F7096289021488E554B87AF8B89D320BE253F9B1A3928.
- Packaging source spec keeps the existing one-file/windowless format and explicitly
  disables UPX. All archive payloads match the baseline except the omitted Tcl test
  harness; base_library.zip differs only in member order, all 155 payloads equal.
- Canonical build PASS. Owned frozen-EXE checks PASS: four actual native pickers
  opened/canceled, local HTTP/assets, synthetic Markdown/INI save+reload and equal
  exported HTML SHA. Seven alternating performance pairs PASS; raw JSON retained.
- Build-close block itself tested in graceful and forced scenarios: exact target
  closed, another same-named copy in a different directory remained alive.
- Initial clean checker misclassified known PYZ compiler output; log retained.
  Cleanup is now narrower, with exact work-path/name recognition. Final actual
  clean removed one base-library compiler ZIP after 11 earlier intermediates;
  8 protected actual files/source spec/INI hashes unchanged. 28 sentinels, cache,
  help/idempotence and both native/source junction rejection PASS.
- EXE remains ignored/untracked by existing repository policy; never force-add it.
  Commit/remote outcome is in shared EXE_SLIMMING_PROGRESS.md.
- NOT RUN: browser visual/DPI, clean-PC or PDF/PNG/JPG rerun; their code/assets/runtime
  payloads are unchanged. A long nested extraction fixture failed; short owned
  temporary fixtures succeeded. No arbitrary long-path support claim is made.


## File-only Python clean follow-up (2026-10-21)

- Changed scripts/clean.ps1, scripts/clean_python.bat and new companion clean_intermediates.ps1. Final cross-profile review found the earlier cleaner still purged whole build/obj/cache folders; replaced it with file allowlists and empty-directory-only removal.
- PASS: shared verify_clean_preservation.ps1 with -CleanActualProject -CheckNestedDelivery -CheckPythonCaches -CheckReparseRejection. Twenty-three protected fixture files plus source retained, including EXE/INI/unknowns inside obj AND root/source caches; known obj/pyc/PYO removed, help/idempotence passed, both native and source/cache junctions rejected before native deletion.
- PASS: actual clean protected delivery hashes unchanged (6 files). Source/application behavior unchanged from the previously verified baseline; no application rebuild/version bump solely for clean changes. No new packaging or hardware/GUI acceptance claim.
- No private runtime files or new EXEs staged; ordinary reviewed publication only to the existing origin.


## Current State

### Root-cache clean follow-up (2026-10-20)

- Added the exact root `__pycache__` to the existing checked cache targets; unknown build/user-output folders remain protected.
- PASS on resume: actual clean, root/source cache removal, 9 protected build sentinels plus source, idempotence, and junction rejection before deletion. 6 actual protected build files retained unchanged; source and isolated frozen-EXE HTTP/resource tests both PASS.
- Publication evidence is recorded in workspace `PROJECT_LAYOUT_MIGRATION.md`.

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
