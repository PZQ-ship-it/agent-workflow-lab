param(
  [string]$AdbPath = "adb",
  [string]$Serial = "",
  [switch]$Screenshot
)
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $Here
. (Join-Path $Here "Resolve-AdbPath.ps1")
$AdbPath = Resolve-AdbPath -AdbPath $AdbPath
$RuntimeConfig = Resolve-Path (Join-Path $Root "..\..\runtime\wechat-mini-list-capture\config.local.json") -ErrorAction SilentlyContinue
$Config = Join-Path $Root "config.example.json"
if ($RuntimeConfig) {
  $Config = $RuntimeConfig.Path
}
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
  $Python = "python"
}
$env:PYTHONPATH = Join-Path $Root "src"
$ArgsList = @(
  "-m", "wechat_mini_capture.cli",
  "--config", $Config,
  "--driver", "android_adb",
  "--adb-path", $AdbPath
)
if ($Serial) { $ArgsList += @("--adb-serial", $Serial) }
$ArgsList += "doctor"
if ($Screenshot) { $ArgsList += "--screenshot" }
& $Python @ArgsList
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}
