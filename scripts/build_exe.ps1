param(
    [bool]$CloseRunningTool = $true
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$exeName = "MarkdownMermaidTool"

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
    pyinstaller `
        --noconfirm `
        --clean `
        --onefile `
        --noconsole `
        --name $exeName `
        --add-data "src\markdown_mermaid_tool\static;markdown_mermaid_tool\static" `
        "src\main.py"

    New-Item -ItemType Directory -Force -Path "build" | Out-Null
    Copy-Item -Force "dist\$exeName.exe" "build\$exeName.exe"
    Write-Host "Built: $(Join-Path $root "build\$exeName.exe")"
} finally {
    Pop-Location
}
