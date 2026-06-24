# Codex Exploration Loop v2.0 Failure Smoke

Date: 2026-06-24

Purpose: verify that the v2.0 runner records a failed planned round through `abort-round` instead of silently succeeding.

Method:

- Created a normal exploration run.
- Wrote a runner plan with one round whose mode is intentionally invalid: `invalid-mode`.
- Ran `run-plan --max-rounds 1 --max-failures 1 --digest`.

Result:

- The runner prepared a pending round, detected the invalid mode, and called `abort-round`.
- `ledger.jsonl` contains one aborted record with `decision = stop`.
- `runner-state.json` ended with `status = failed`, `rounds_attempted = 1`, `rounds_completed = 0`, `failures = 1`, and `reason = max failures reached: 1`.
- `frontier.json` has no active branches.
- Path scan over this experiment directory found no local absolute paths or private Codex home references.

This smoke is deterministic and does not call a live model or external service.
