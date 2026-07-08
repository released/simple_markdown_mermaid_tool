param(
    [int]$Port = 8765,
    [switch]$NoOpen
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")

$argsList = @("src\main.py", "--port", $Port)
if ($NoOpen) {
    $argsList += "--no-open"
}

Push-Location $root
try {
    python @argsList
} finally {
    Pop-Location
}
