param(
  [Parameter(Mandatory = $true)]
  [string]$ListId,
  [string]$AppRegion = "",
  [string]$ListRegion = "",
  [string]$DetailRegion = "",
  [string]$EntryPoint = "",
  [ValidateSet("auto", "row_slots")]
  [string]$CandidateMode = "",
  [string[]]$RowSlot = @(),
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
  "configure-list",
  "--list-id", $ListId
)
if ($AppRegion) { $ArgsList += @("--app-region", $AppRegion) }
if ($ListRegion) { $ArgsList += @("--list-region", $ListRegion) }
if ($DetailRegion) { $ArgsList += @("--detail-region", $DetailRegion) }
if ($EntryPoint) { $ArgsList += @("--entry-point", $EntryPoint) }
if ($CandidateMode) { $ArgsList += @("--candidate-mode", $CandidateMode) }
foreach ($Slot in $RowSlot) {
  $ArgsList += @("--row-slot", $Slot)
}
& $Python @ArgsList
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}
