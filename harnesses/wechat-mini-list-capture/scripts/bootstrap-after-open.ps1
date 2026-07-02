param(
  [switch]$SkipRun,
  [int]$MaxItems = 0
)
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $Here
$RuntimeConfig = Join-Path $Root "..\..\runtime\wechat-mini-list-capture\config.local.json"

& (Join-Path $Here "doctor.ps1")

if (-not (Test-Path $RuntimeConfig)) {
  Write-Host "No local config found. Running visual OCR calibration for the current screen as list_a." -ForegroundColor Yellow
  Write-Host "For list_b, switch to the second list later and run: .\scripts\calibrate-visible-list.ps1 -ListId list_b" -ForegroundColor Yellow
  & (Join-Path $Here "calibrate-visible-list.ps1") -ListId list_a
}

if (-not $SkipRun) {
  if ($MaxItems -gt 0) {
    & (Join-Path $Here "run-desktop.ps1") -MaxItems $MaxItems
  } else {
    & (Join-Path $Here "run-desktop.ps1")
  }
}
