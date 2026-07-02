param(
  [Parameter(Mandatory=$true)][string]$RunDir,
  [string]$Output
)
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $Here
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
  $Python = "python"
}
$env:PYTHONPATH = Join-Path $Root "src"
$cmd = @("-m", "wechat_mini_capture.cli", "export-review", "--run-dir", $RunDir)
if ($Output) { $cmd += @("--output", $Output) }
& $Python @cmd
