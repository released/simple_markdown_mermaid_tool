# SELF_CHECK.md

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
