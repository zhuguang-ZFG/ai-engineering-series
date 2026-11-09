# Run from the book repository root. Downloads are limited to a full pinned commit.
$ErrorActionPreference = 'Stop'
$bookRepo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$runtimeDir = Join-Path $bookRepo '.scratch\deepseek-runtime'
$sourceDir = Join-Path $runtimeDir 'pinned-cordis\src'
$factsPath = Join-Path $bookRepo 'deepseek\facts\cordis-20261110.json'
$facts = Get-Content -LiteralPath $factsPath -Raw -Encoding utf8 | ConvertFrom-Json
$commit = $facts.source.commit
if ($commit -ne 'fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159') {
    throw 'Unexpected source commit; review the experiment before changing the pin.'
}
New-Item -ItemType Directory -Force -Path $sourceDir | Out-Null
foreach ($file in $facts.source_sha256.PSObject.Properties.Name) {
    if ($file -notmatch '^[a-z-]+\.ts$') { throw "Invalid source filename: $file" }
    $endpoint = "repos/deepseek-ai/deepseek-harness/contents/vendor/cordis/src/${file}?ref=$commit"
    $responseText = & gh api $endpoint
    if ($LASTEXITCODE -ne 0) { throw "Source download failed: $file" }
    $response = $responseText | ConvertFrom-Json
    if ($response.encoding -ne 'base64') { throw "Unexpected source encoding: $file" }
    [System.IO.File]::WriteAllBytes((Join-Path $sourceDir $file),
        [Convert]::FromBase64String($response.content))
}
& python (Join-Path $PSScriptRoot 'verify-evidence.py') --source-root $sourceDir
if ($LASTEXITCODE -ne 0) { throw 'Source or example verification failed.' }
& npm.cmd install --prefix $runtimeDir --ignore-scripts --no-audit --no-fund `
    '@deepseek-ai/cordis@4.1.0' '@deepseek-ai/cosmokit@1.9.0' '@standard-schema/spec@1.1.0' 'tsx@4.23.13'
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
Write-Output 'Ready. Run the check-cordis.mjs command from examples/README.md.'
