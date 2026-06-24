$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$promptPath = Join-Path $scriptDir 'b001-round-001.prompt.md'
$schemaPath = Join-Path $scriptDir 'b001-round-001.schema.json'
$resultPath = Join-Path $scriptDir 'b001-round-001.result.json'
$eventsPath = Join-Path $scriptDir 'b001-round-001.events.jsonl'
$prompt = Get-Content -Raw -Encoding UTF8 $promptPath
$codexArgs = @(
  'exec',
  '--cd',
  '<scratch-or-workspace>',
  '--sandbox',
  'workspace-write',
  '--output-schema',
  $schemaPath,
  '--output-last-message',
  $resultPath,
  '--json',
  '-'
)
$prompt | & codex @codexArgs 2>&1 | Tee-Object -FilePath $eventsPath
