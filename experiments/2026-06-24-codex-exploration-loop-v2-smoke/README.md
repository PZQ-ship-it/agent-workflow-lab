# Codex Exploration Loop v2.0 Smoke

Date: 2026-06-24

Purpose: verify that `codex-exploration-loop` v2.0 can orchestrate multiple bounded exploration rounds through a local runner plan while still using Codex-native worker surfaces instead of rebuilding an agent loop.

Confirmed surfaces:

- Local CLI: `codex-cli 0.93.45`
- `codex exec --help` includes `--output-schema`, `--output-last-message`, `--json`, `--sandbox`, `--profile`, and `resume`.
- OpenAI Codex glossary describes Automations as scheduled/recurring tasks, `codex exec` as non-interactive CLI execution, Codex SDK as programmatic workflow support, and app-server as a local JSON-RPC server for threads, turns, approvals, history, and streamed events.

Commands:

```powershell
python <skill-dir>\scripts\explore_ledger.py init `
  --root <agent-workflow-lab> `
  --root-label '<agent-workflow-lab>' `
  --output-dir <agent-workflow-lab>\experiments `
  --slug codex-exploration-loop-v2-smoke `
  --question "Can v2.0 orchestrate multiple bounded exploration rounds through a runner plan without rebuilding Codex's agent loop?" `
  --max-rounds 3 `
  --round-timebox-minutes 4 `
  --mode scout

python <skill-dir>\scripts\explore_ledger.py write-plan `
  --run-dir experiments\2026-06-24-codex-exploration-loop-v2-smoke

python <skill-dir>\scripts\explore_ledger.py run-plan `
  --run-dir experiments\2026-06-24-codex-exploration-loop-v2-smoke `
  --plan experiments\2026-06-24-codex-exploration-loop-v2-smoke\runner-plan.json `
  --max-rounds 2 `
  --digest
```

Result:

- Runner executed two deterministic `mock` rounds.
- Round 1 decision: `continue`.
- Round 2 decision: `promote`.
- `runner-state.json` ended with `status = stopped`, `reason = decision=promote`, `rounds_attempted = 2`, `rounds_completed = 2`, `failures = 0`.
- `frontier.json` marked `b001` as `promoted`.
- Path scan over this experiment directory found no local absolute paths or private Codex home references.

This smoke intentionally does not call a live model; it validates the runner contract deterministically.
