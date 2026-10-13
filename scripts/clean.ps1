$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")

Push-Location $root
try {
    $buildPath = Join-Path $root "build"
    if (Test-Path -LiteralPath $buildPath) {
        $intermediateDirectories = @("obj", "tests", "verify", "verify_obj", "CMakeFiles", "x64", ".vs")
        $intermediateExtensions = @(".obj", ".pch", ".idb", ".pdb", ".ilk", ".res", ".exp", ".lib", ".iobj", ".ipdb", ".tlog", ".lastbuildstate")

        Get-ChildItem -LiteralPath $buildPath -Directory -Recurse -Force |
            Where-Object { $_.Name -in $intermediateDirectories } |
            Sort-Object FullName -Descending |
            Remove-Item -Recurse -Force

        Get-ChildItem -LiteralPath $buildPath -File -Recurse -Force |
            Where-Object { $_.Extension.ToLowerInvariant() -in $intermediateExtensions } |
            Remove-Item -Force
    }
    Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
    Write-Host "Clean complete. Preserved build/dist executables, spec files, INI files, data, logs, and output."
} finally {
    Pop-Location
}
