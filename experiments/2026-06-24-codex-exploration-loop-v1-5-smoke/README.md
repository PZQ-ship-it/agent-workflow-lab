# Codex Exploration Loop v1.5 Smoke

Date: 2026-06-24

Purpose: verify that `codex-exploration-loop` v1.5 can prepare portable `codex exec` round-worker artifacts and import a schema-valid worker result into the same ledger/frontier flow.

Commands:

```powershell
python <skill-dir>\scripts\explore_ledger.py init `
  --root <agent-workflow-lab> `
  --root-label '<agent-workflow-lab>' `
  --output-dir <agent-workflow-lab>\experiments `
  --slug codex-exploration-loop-v1-5-smoke `
  --question "Can v1.5 prepare and import schema-backed codex exec round-worker artifacts without leaking local paths?" `
  --max-rounds 3 `
  --round-timebox-minutes 5 `
  --mode scout

python <skill-dir>\scripts\explore_ledger.py prepare-worker `
  --run-dir experiments\2026-06-24-codex-exploration-loop-v1-5-smoke `
  --round 1 `
  --branch-id b001 `
  --workspace '<scratch-or-workspace>' `
  --probe "Inspect v1.5 worker artifacts and prove they can be imported into the ledger." `
  --portable

python <skill-dir>\scripts\explore_ledger.py finish-worker `
  --run-dir experiments\2026-06-24-codex-exploration-loop-v1-5-smoke `
  --worker-output experiments\2026-06-24-codex-exploration-loop-v1-5-smoke\artifacts\b001-round-001.result.json

python <skill-dir>\scripts\explore_ledger.py digest `
  --run-dir experiments/2026-06-24-codex-exploration-loop-v1-5-smoke
```

Result:

- `prepare-worker --portable` created a prompt, PowerShell `codex exec` runner, copied schema, and relative worker manifest.
- `finish-worker` imported `b001-round-001.result.json` with total score `2.75`.
- `frontier.json` marked `b001` as `promoted`.
- Path scan over the experiment directory found no local absolute paths or private Codex home references.

Note: the worker result is a mock schema-valid output, not a live model run. This keeps the smoke deterministic while verifying the v1.5 adapter contract.

Additional live check: a temporary real `codex exec --output-schema` worker reached the official CLI, but the remote responses API returned HTTP 502 twice. The adapter path was therefore not blocked on a live model result; the failure was recorded with `abort-round` in a temporary, non-committed run directory.
