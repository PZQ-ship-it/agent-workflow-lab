$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $Here
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
  $Python = "python"
}
$env:PYTHONPATH = Join-Path $Root "src"
& $Python -m wechat_mini_capture.cli --config (Join-Path $Root "config.example.json") calibrate-desktop
