$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")

Push-Location $root
try {
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "build", "dist", "*.spec"
    Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
    Write-Host "Clean complete."
} finally {
    Pop-Location
}
