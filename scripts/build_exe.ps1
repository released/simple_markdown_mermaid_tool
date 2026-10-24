param(
    [bool]$CloseRunningTool = $true
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$exeName = "MarkdownMermaidTool"
$workPath = Join-Path $root "build\obj\pyinstaller"
$buildSpec = Join-Path $PSScriptRoot "build\MarkdownMermaidTool.spec"
$outputPath = Join-Path $root "build"

if ($CloseRunningTool) {
    $targetExe = [IO.Path]::GetFullPath((Join-Path $outputPath "$exeName.exe"))
    foreach ($running in @(Get-Process -Name $exeName -ErrorAction SilentlyContinue)) {
        try { $runningPath = $running.Path; $started = $running.StartTime } catch { continue }
        if (-not [string]::Equals($runningPath, $targetExe, [StringComparison]::OrdinalIgnoreCase)) { continue }
        $targetPid = $running.Id
        if ($running.MainWindowHandle -ne [IntPtr]::Zero) { [void]$running.CloseMainWindow() }
        if (-not $running.WaitForExit(5000)) {
            $current = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
            if ($current -and $current.StartTime -eq $started -and
                [string]::Equals($current.Path, $targetExe, [StringComparison]::OrdinalIgnoreCase)) {
                # The local HTTP server has no unsaved-document close dialog.
                Stop-Process -Id $targetPid -Force -ErrorAction Stop
                if (-not $current.WaitForExit(5000)) { throw "Exact build target PID $targetPid did not exit." }
            }
        }
    }
}

Push-Location $root
try {
    New-Item -ItemType Directory -Force -Path $workPath | Out-Null
    python -m PyInstaller `
        --noconfirm `
        --workpath (Join-Path $workPath "work") `
        --distpath $outputPath `
        $buildSpec
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
