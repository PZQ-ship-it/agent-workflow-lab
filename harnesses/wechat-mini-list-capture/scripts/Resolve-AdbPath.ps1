function Resolve-AdbPath {
  param(
    [string]$AdbPath = "adb"
  )

  if ($AdbPath -and $AdbPath -ne "adb") {
    return $AdbPath
  }

  $Command = Get-Command adb -ErrorAction SilentlyContinue
  if ($Command) {
    return $Command.Source
  }

  $WingetPackages = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages"
  if (Test-Path $WingetPackages) {
    $Candidate = Get-ChildItem $WingetPackages -Recurse -Filter adb.exe -ErrorAction SilentlyContinue |
      Where-Object { $_.FullName -like "*Google.PlatformTools*" } |
      Select-Object -First 1
    if ($Candidate) {
      return $Candidate.FullName
    }
  }

  return $AdbPath
}
