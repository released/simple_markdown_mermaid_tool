# SELF_CHECK.md

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
