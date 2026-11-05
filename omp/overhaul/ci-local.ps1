param(
    [string]$OutDir = ".scratch/spec-finish/build"
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

function Invoke-CheckedPython {
    param([string[]]$Arguments)
    & python @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "python failed ($LASTEXITCODE): $($Arguments -join ' ')"
    }
}

Push-Location $repoRoot
try {
    Invoke-CheckedPython @("omp/overhaul/audit_structure.py", "--check")
    Invoke-CheckedPython @("omp/overhaul/audit_delivery.py")
    Invoke-CheckedPython @("scripts/bookctl.py", "build", "--product", "book", "--lang", "zh", "--out-dir", (Join-Path $OutDir "book"))
    Invoke-CheckedPython @("scripts/bookctl.py", "build", "--product", "omp", "--lang", "zh", "--pdf", "--out-dir", (Join-Path $OutDir "omp"))
    Write-Host "ci-local OK"
} finally {
    Pop-Location
}
