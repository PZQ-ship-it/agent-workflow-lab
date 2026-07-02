# WeChat Mini List Capture Harness

Status: local harness, first runnable scaffold.

This harness helps capture a simple two-layer WeChat mini-program workflow:

1. a list page with infinite scroll;
2. list items that open detail pages;
3. detail pages that can be scrolled to the bottom;
4. redacted review exports for human confirmation.

It intentionally works from visible UI state. It does not copy cookies, tokens,
headers, localStorage, or private API calls.

## Storage Layout

- `harnesses/wechat-mini-list-capture/`: public-safe code and templates.
- `runtime/wechat-mini-list-capture/`: ignored local screenshots, OCR text,
  checkpoints, and logs.
- `D:\todo\projects\wechat-mini-list-capture`: planning, decisions, and
  sanitized review/export records.

## One-Command Flow After Opening The Mini Program

Open the target mini program and leave the first list visible, then run:

```powershell
.\scripts\bootstrap-after-open.ps1
```

If a previous terminal is still asking for row-slot coordinates, press
`Ctrl+C` first.

If no local config exists, the script first runs visual OCR calibration for the
current list. It detects the blue mini-program window, finds white list cards,
writes `config.local.json`, and saves an annotated screenshot under
`runtime/wechat-mini-list-capture/`.

For the cautious first pass, stop after annotation:

```powershell
.\scripts\bootstrap-after-open.ps1 -SkipRun
```

Review the annotated image once. If the app/list/item boxes look right, run
`.\scripts\bootstrap-after-open.ps1 -MaxItems 3`. If you already trust the
visual calibration, `.\scripts\bootstrap-after-open.ps1 -MaxItems 3` can
calibrate and start the sample run in one command.

For the second list, manually switch the tab once, then run:

```powershell
.\scripts\calibrate-visible-list.ps1 -ListId list_b
.\scripts\run-desktop.ps1 -ListId list_b -MaxItems 3
```

## Manual Commands

```powershell
.\scripts\doctor.ps1
.\scripts\doctor-android.ps1 -Screenshot
.\scripts\calibrate-visible-list.ps1 -ListId list_a
.\scripts\calibrate-android.ps1 -ListId list_a
.\scripts\calibrate-visible-list.ps1 -ListId list_b
.\scripts\calibrate-desktop.ps1
.\scripts\run-desktop.ps1
.\scripts\run-android.ps1 -ListId list_a -MaxItems 3
.\scripts\export-review.ps1
```

Prefer `calibrate-visible-list.ps1` first. It captures the current screen,
runs OCR inside the detected mini-program window, infers card candidates,
writes `config.local.json`, and saves an annotated screenshot under
`runtime/wechat-mini-list-capture/`.

If the window detector misses, keep the mini program centered and visible, or
pass a manual rectangle:

```powershell
.\scripts\calibrate-visible-list.ps1 -ListId list_a -AppRegion "700,90,1260,1160"
```

Use the older `calibrate-desktop.ps1` only when OCR inference is unusable.

## No-Mouse Android Mode

To avoid taking over the Windows mouse, use a real Android device or emulator
with ADB. The harness then uses `adb exec-out screencap -p`,
`adb shell input tap`, `adb shell input swipe`, and Android back key events.

```powershell
.\scripts\doctor-android.ps1 -Screenshot
.\scripts\calibrate-android.ps1 -ListId list_a
.\scripts\run-android.ps1 -ListId list_a -MaxItems 3
```

If more than one ADB device is connected, pass `-Serial <adb-device-id>`.
If `adb` is not on PATH, pass `-AdbPath "C:\path\to\adb.exe"`.
When Platform Tools was installed through WinGet, the Android scripts also try
to discover the WinGet `Google.PlatformTools` `adb.exe` path automatically.

## Safety Notes

- Keep raw screenshots and OCR under `runtime/`; this folder is gitignored.
- Put only sanitized CSV/JSON summaries in `D:\todo`.
- Treat OCR/LLM outputs as candidates until reviewed.
- Do not use this harness to bypass login, CAPTCHA, membership, private APIs,
  or platform safeguards.
