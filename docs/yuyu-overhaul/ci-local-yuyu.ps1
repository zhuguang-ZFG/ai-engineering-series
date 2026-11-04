# 御舆（product=book）本地 CI 等价跑：docs/YUYU-OVERHAUL-SPEC.md · Task M4 Step 3
# 用法：powershell -File docs/yuyu-overhaul/ci-local-yuyu.ps1
# 全程写到 docs/yuyu-overhaul/logs/ci-local-yuyu-<时间戳>.log，最后打印结论行。
#
# 两个坑（都是本机实跑踩出来的，别再改回去）：
# 1. Windows PowerShell 5.1 里，原生命令的 stderr 一旦经 `2>&1` 并进成功流，会被包成
#    ErrorRecord；若此时 $ErrorActionPreference=Stop，它就是终止性错误。`python -m unittest`
#    把进度点写在 stderr，所以 09:54 那次在「general tests」全过的情况下炸成 NativeCommandError。
#    → Step 内部临时降到 Continue，判断只认 $LASTEXITCODE。
# 2. Tee-Object / Add-Content 在 5.1 下默认写成 UTF-16/ANSI，中文进日志会变问号。
#    → 自己用 .NET 以 UTF-8（无 BOM）落盘，Log 是唯一写日志的口子。

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)))

# 原生命令（python）输出 UTF-8；5.1 默认按控制台代码页解码，中文会变问号。
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$logDir = "docs/yuyu-overhaul/logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$log = Join-Path $logDir ("ci-local-yuyu-{0}.log" -f (Get-Date -Format "yyyyMMdd-HHmmss"))

function Log($text) {
  [System.IO.File]::AppendAllText($log, $text + "`r`n", $script:utf8NoBom)
}

# 原生 stderr 经 2>&1 会被包成 ErrorRecord；空行上 ToString() 给出的是类型名
# System.Management.Automation.RemoteException，Exception.Message 才是真空串（本机实测）。
function Txt($o) {
  if ($o -is [System.Management.Automation.ErrorRecord]) { return $o.Exception.Message }
  return [string]$o
}

function Step($name, $argv) {
  Log "## $name"
  Log ("+ " + ($argv -join " "))
  $prev = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  $out = @(& $argv[0] $argv[1..($argv.Length - 1)] 2>&1 | ForEach-Object { Txt $_ })
  $code = $LASTEXITCODE
  $ErrorActionPreference = $prev
  Log ($out -join "`r`n")
  $out | ForEach-Object { Write-Host $_ }
  Log ("-> exit $code")
  if ($code -ne 0) { throw "$name 退出码 $code（日志：$log）" }
}

"=== ci-local-yuyu · {0} · {1} ===" -f (Get-Date -Format "s"), (Get-Location) |
  ForEach-Object { Log $_; Write-Host $_ }

# 离线护栏：秒级、不写 dist、不联网。放在最前面，让便宜的红先红。
# 这四条都是 docs/yuyu-overhaul/TEST-CONTRACT.md 表里登记过的独立口径，
# bookctl check --fast 的六步不覆盖它们（六步是被 README/STRUCTURE 钉住的契约，
# 加一步要同步改宣称，所以在这里串，不动六步）。
foreach ($guard in "check_site_links", "check_block_markers", "check_crossrefs",
                   "check_bilingual_parity") {
  Step "guard $guard" @("python", "docs/yuyu-overhaul/$guard.py")
}

Step "bookctl check --fast"  @("python", "scripts/bookctl.py", "check", "--fast")
Step "build book both --pdf" @("python", "scripts/bookctl.py", "build", "--product", "book", "--lang", "both", "--pdf")

# check_artifact_claims.py 比的是 CI（Noto CJK）那套页数；本机是微软雅黑，必定报红。
# 依据：docs/yuyu-overhaul/PDF-PAGES.md「这台机器上 check_artifact_claims.py 必定报红，且不是坏了」
# 与 docs/yuyu-overhaul/BASELINE.md「改造前的既有红灯」第 2 条。
# 这里只放行「页数类失败 + README 仍写着 CI 的 516/552」；任何其他失败照常红。
# 反过来，如果 README 被改成本机页数来凑绿，这条脚本要拦住 —— SPEC 明令禁止谎报。
Log "## check_artifact_claims（只允许字体口径的页数例外）"
$readme = Get-Content -Raw -Encoding UTF8 README.md
if ($readme -notmatch '516' -or $readme -notmatch '552') {
  throw "README 里找不到 CI(Noto) 的 516/552 页数宣称了。不能为了本机变绿改 README —— 见 PDF-PAGES.md。"
}
$prev = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$claims = @(& python scripts/check_artifact_claims.py 2>&1 | ForEach-Object { Txt $_ })
$code = $LASTEXITCODE
$ErrorActionPreference = $prev
Log ($claims -join "`r`n")
$claims | ForEach-Object { Write-Host $_ }
Log ("-> exit $code")
$stale = @($claims | Where-Object { $_ -match '\[STALE\]' })
foreach ($line in $stale) {
  if ($line -notmatch 'has \d+ pages, README says (516|552)(\s+\[STALE\])?\s*$') {
    throw "check_artifact_claims 报的不是「雅黑 vs Noto 页数」这一类，不能用例外放行：$line"
  }
}
if ($stale.Count -lt 1) {
  throw "check_artifact_claims 一条都没报红，说明本机 dist 已经是 CI 口径或 README 被改过 —— 先查清再放行。"
}
"EXCEPTION: 放行 $($stale.Count) 条页数差异（README=CI/Noto 516·552，本机=雅黑实际页数），日志 $log" |
  ForEach-Object { Log $_; Write-Host $_ }

"ci-local-yuyu OK" | ForEach-Object { Log $_; Write-Host $_ }
