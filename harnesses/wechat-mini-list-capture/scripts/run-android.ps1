param(
  [string]$Config,
  [string]$RunId,
  [string]$ListId,
  [int]$MaxItems = 0,
  [int]$MaxRounds = 200,
  [string]$AdbPath = "adb",
  [string]$Serial = ""
)
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $Here
. (Join-Path $Here "Resolve-AdbPath.ps1")
$AdbPath = Resolve-AdbPath -AdbPath $AdbPath
$RuntimeConfig = Resolve-Path (Join-Path $Root "..\..\runtime\wechat-mini-list-capture\config.local.json") -ErrorAction SilentlyContinue
if (-not $Config) {
  if ($RuntimeConfig) {
    $Config = $RuntimeConfig.Path
  } else {
    $Config = Join-Path $Root "config.example.json"
  }
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
$ArgsList += "run-desktop"
if ($RunId) { $ArgsList += @("--run-id", $RunId) }
if ($ListId) { $ArgsList += @("--list-id", $ListId) }
if ($MaxItems -gt 0) { $ArgsList += @("--max-items", "$MaxItems") }
$ArgsList += @("--max-rounds", "$MaxRounds")
& $Python @ArgsList
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}
