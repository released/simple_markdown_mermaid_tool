# SELF_CHECK.md

## Verified EXE slimming 2026-10-25

- Exact comparable EXE 12902984 -> 12875387 bytes (27597 saved).
- Formal SHA: 0B53FA841A7BD75ADA4F7096289021488E554B87AF8B89D320BE253F9B1A3928.
- Original pre-task delivery was 12903348 bytes; fresh same-toolchain baseline
  is used for the comparison, not metadata from an older build.
- PASS canonical scripts/build_exe.ps1 -CloseRunningTool $false; Python 3.13 /
  PyInstaller 6.13.0, one-file/windowless, no new install requirement or UPX.
- PASS archive comparison: 1000 -> 999 entries; only tcltest-2.5.7.tm omitted.
  Its compressed size was 28007 bytes. No added entries; base_library.zip's ordering
  differs but all 155 member payloads match. Every other archive payload matches.
- PASS hash-matched owned parent/child processes, confirmed owned loopback listener,
  embedded page/JS/CSS/Mermaid/marked resources, synthetic Markdown load, INI save/
  reload, HTML-only export and identical exported HTML hashes.
- PASS all four actual Tcl/Tk native file/folder pickers opened and canceled with
  empty results. No mocked import, user INI, external browser or remote request.
- PASS extracted actual build-close block: graceful exit 0 and bounded force fallback
  (-1 for the synthetic sleep host); foreign same-named copy preserved in both cases.
- PASS seven alternating AB/BA timing pairs after warmups and before-candidate
  calibration. No concurrent compilation. Gate max(floor, 10% median, 3*MAD),
  memory 5%; floors startup50/50-request-HTTP5/CPU16ms, memory1MiB.
  - StartupMs: 6734.4750 -> 6687.9609; limit 8642.4750.
  - PeakBytes: 39485440.0000 -> 39456768.0000; limit 41459302.0000.
  - CpuMs: 2718.7500 -> 2781.2500; limit 3027.7500.
  - WorkflowMs: 948.0713 -> 951.2688; limit 1103.0713.
  Startup includes mandatory process/listener-ownership probe overhead, not browser
  rendering. CPU and peak values sum the owned bootloader/server processes.
- PASS revised exact-name/work-path clean: 28 protected fixtures plus source,
  unknown .pyz/.pkg/.toc/other-location archives retained, known package/compiler
  files removed; Python caches/help/idempotence/native and source junction checks.
  Final actual clean: 1 additional compiler ZIP removed; all 8 protected actual
  files, root INI hashes and source spec unchanged. The earlier classifier failure
  and its 11-file compiler cleanup remain documented, not hidden.
- PASS shared verifier default-native regression: 17 protected sentinels/source,
  help/idempotence; no unrelated actual native clean rerun.
- Raw numeric evidence: docs/verification/exe-slimming-20261025.json.
- NOT RUN: browser visual/DPI/clean-PC/PDF/PNG/JPG rerun; unchanged payload evidence
  reused. Long nested extraction fixture failed before timing, short test-owned
  temporary paths used. This does not add general long-path support to the app.


## File-only Python clean follow-up (2026-10-21)

- Changed scripts/clean.ps1, scripts/clean_python.bat and new companion clean_intermediates.ps1. Final cross-profile review found the earlier cleaner still purged whole build/obj/cache folders; replaced it with file allowlists and empty-directory-only removal.
- PASS: shared verify_clean_preservation.ps1 with -CleanActualProject -CheckNestedDelivery -CheckPythonCaches -CheckReparseRejection. Twenty-three protected fixture files plus source retained, including EXE/INI/unknowns inside obj AND root/source caches; known obj/pyc/PYO removed, help/idempotence passed, both native and source/cache junctions rejected before native deletion.
- PASS: actual clean protected delivery hashes unchanged (6 files). Source/application behavior unchanged from the previously verified baseline; no application rebuild/version bump solely for clean changes. No new packaging or hardware/GUI acceptance claim.
- No private runtime files or new EXEs staged; ordinary reviewed publication only to the existing origin.


## Layout Verification 2026-10-20

### Root-cache clean follow-up (2026-10-20)

- Added the exact root `__pycache__` to the existing checked cache targets; unknown build/user-output folders remain protected.
- PASS on resume: actual clean, root/source cache removal, 9 protected build sentinels plus source, idempotence, and junction rejection before deletion. 6 actual protected build files retained unchanged; source and isolated frozen-EXE HTTP/resource tests both PASS.
- Publication evidence is recorded in workspace `PROJECT_LAYOUT_MIGRATION.md`.

- PASS: `scripts/build_exe.ps1 -CloseRunningTool $false`; EXE generated under
  `build`, work/spec under `build/obj/pyinstaller`.
- PASS: `python -m compileall -q src`.
- PASS: `$env:PC_TOOL_TEST_EXE='1'; python -m unittest discover -s tests -v`,
  2 tests, source and packaged embedded-resource HTTP smoke.
- PASS: actual `scripts/clean_python.bat`, 6 protected build files SHA-256 unchanged.
- PASS: isolated clean sentinels and repeat-clean (9 build files plus source).
- NOT RUN: browser visual/DPI testing and PDF/PNG/JPG export regression.
- Existing PyInstaller dependency warning: `pkg_resources` deprecation.

## Manual Checks

- Run `scripts\run_tool.ps1`.
- Load `demo_code\sample.md`.
- Confirm the editor appears on the left and preview appears on the right.
- Confirm the output name becomes `sample`.
- Save an INI file and reload it.
- Select HTML and click Generate.
- Select PDF/PNG/JPG when Edge or Chrome is installed and click Generate.

## Automated Checks

```powershell
python -m compileall src
```

```powershell
python src\main.py --no-open
```

Stop the server with `Ctrl+C`.

## Expected Files

- `output\sample.html`
- `output\sample.pdf` when Edge/Chrome is available and PDF is selected.
- `output\sample.png` when Edge/Chrome is available and PNG is selected.
- `output\sample.jpg` when Edge/Chrome and PowerShell System.Drawing conversion are available and JPG is selected.
