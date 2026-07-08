$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$vendor = Join-Path $root "src\markdown_mermaid_tool\static\vendor"
New-Item -ItemType Directory -Force -Path $vendor | Out-Null

$files = @(
    @{
        Url = "https://cdn.jsdelivr.net/npm/marked/marked.min.js"
        Out = "marked.min.js"
    },
    @{
        Url = "https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"
        Out = "mermaid.min.js"
    }
)

foreach ($file in $files) {
    $outPath = Join-Path $vendor $file.Out
    Write-Host "Downloading $($file.Url)"
    Invoke-WebRequest -Uri $file.Url -OutFile $outPath
    Write-Host "Saved $outPath"
}
