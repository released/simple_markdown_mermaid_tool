param(
    [bool]$CloseRunningTool = $true
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$exeName = "MarkdownMermaidTool"
$workPath = Join-Path $root "build\obj\pyinstaller"
$specPath = Join-Path $workPath "spec"
$outputPath = Join-Path $root "build"

if ($CloseRunningTool) {
    $proc = Get-Process -Name $exeName -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Host "Closing running $exeName.exe before build..."
        $proc | Stop-Process -Force
        Start-Sleep -Milliseconds 300
    }
}

Push-Location $root
try {
    New-Item -ItemType Directory -Force -Path $specPath | Out-Null
    python -m PyInstaller `
        --noconfirm `
        --onefile `
        --noconsole `
        --workpath (Join-Path $workPath "work") `
        --specpath $specPath `
        --distpath $outputPath `
        --name $exeName `
        --add-data "$(Join-Path $root 'src\markdown_mermaid_tool\static');markdown_mermaid_tool\static" `
        (Join-Path $root "src\main.py")
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE."
    }

    $exePath = Join-Path $outputPath "$exeName.exe"
    if (-not (Test-Path -LiteralPath $exePath -PathType Leaf)) {
        throw "PyInstaller completed without the expected executable: $exePath"
    }
    Write-Host "Built: $exePath"
} finally {
    Pop-Location
}
