param(
  [string]$Config,
  [string]$RunId,
  [string]$ListId,
  [int]$MaxItems = 0
)
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $Here
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
$cmd = @("-m", "wechat_mini_capture.cli", "--config", $Config, "run-desktop")
if ($RunId) { $cmd += @("--run-id", $RunId) }
if ($ListId) { $cmd += @("--list-id", $ListId) }
if ($MaxItems -gt 0) { $cmd += @("--max-items", "$MaxItems") }
& $Python @cmd
