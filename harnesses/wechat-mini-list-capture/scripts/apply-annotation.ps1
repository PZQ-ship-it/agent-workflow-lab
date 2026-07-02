param(
  [Parameter(Mandatory = $true)]
  [string]$Annotation,
  [string]$ListId = "",
  [string]$ScreenImage = "",
  [string]$Config = ""
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
$ArgsList = @(
  "-m", "wechat_mini_capture.cli",
  "--config", $Config,
  "apply-annotation",
  "--annotation", $Annotation
)
if ($ListId) { $ArgsList += @("--list-id", $ListId) }
if ($ScreenImage) { $ArgsList += @("--screen-image", $ScreenImage) }
& $Python @ArgsList
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}
