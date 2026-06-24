# Codex Exploration Loop Implementation Plan

Date: 2026-06-24
Status: implementation-ready plan draft
Depends on: `notes/2026-06-24-codex-exploration-loop-design.zh.md`
Harness support assessment: `notes/2026-06-24-codex-harness-support-assessment.zh.md`
Official-mechanism architecture: `notes/2026-06-24-official-codex-first-exploration-architecture.zh.md`

## Summary

Implement `codex-exploration-loop` in three layers:

1. A Codex skill that controls behavior, budgets, safety gates, branch decisions, local-skill routing, and final output shape.
2. A small ledger adapter that creates the exploration directory, initializes scratch worktree metadata, appends ledger JSONL records, validates schemas, and summarizes frontier state.
3. Official Codex runtime mechanisms for heavier execution: permissions profiles, sandbox/worktree modes, native subagents, MCP, `codex exec`, output schemas, automations, SDK, or app-server.

Do not begin with a custom autonomous daemon. Start with a skill-first loop that Codex can run interactively, add ledger support for repeatability, then use official Codex mechanisms for heavier operation. Treat hard scheduling, unattended continuation, and exact wall-clock interruption as v2 concerns that need Codex automations, SDK/app-server, or an external runner that orchestrates Codex rather than replacing it.

Non-goal:

- do not rebuild Codex's model/tool loop,
- do not create a custom subagent scheduler,
- do not create a custom sandbox or approval system,
- do not create a custom long-run scheduler where Codex automations fit.

## Source Lessons To Implement

### Tree of Thoughts -> Frontier Search

Observed implementation:

- `solve()` keeps current candidates `ys`.
- Each step generates `new_ys`.
- It evaluates candidates by `value` or `vote`.
- It selects a frontier by greedy top-k or probabilistic sample.
- It logs step state into `infos`.

Codex transfer:

- Candidate state becomes an exploration branch.
- `new_ys` becomes proposed probes.
- `value/vote` becomes a branch score or critic comparison.
- `select_new_ys` becomes the next frontier.
- `infos` becomes `ledger.jsonl`.

Implementation rule:

- Every round must end with a frontier decision: `continue`, `pivot`, `branch`, `prune`, `promote`, or `stop`.

### Reflexion -> Trial Memory

Observed implementation:

- `num_trials` controls iterative attempts.
- `use_memory` decides whether prior reflections feed the next trial.
- `is_resume`, `resume_dir`, and `start_trial_num` make long runs resumable.
- `generate_reflections.py` reads trial logs and adds concise plans to memory.
- Programming runs store `reflections`, `implementations`, and `test_feedback`.

Codex transfer:

- Each branch keeps a compact memory of recent reflections.
- Reflections should diagnose a failed or partial probe and prescribe what to change next.
- Keep only the last few reflections in the active prompt, but store all reflections in the ledger.
- Resume should read `brief.md`, `frontier.json`, and `ledger.jsonl`.

Implementation rule:

- Reflection must be delta-oriented: "what to change next", not a generic summary.

### Voyager -> Curriculum, Critic, Skill Library, Checkpoint

Observed implementation:

- `Voyager` wires ActionAgent, CurriculumAgent, CriticAgent, SkillManager, and EventRecorder.
- `learn()` repeatedly proposes a next task, rolls out attempts, checks success, adds successful skills, updates completed/failed tasks, and stops at `max_iterations`.
- `CurriculumAgent` records completed and failed tasks and uses observation/context to propose next tasks.
- `CriticAgent` decides success and critique from environment observations.
- `SkillManager` persists reusable code and retrieves relevant skills.
- `EventRecorder` stores events and supports resume.

Codex transfer:

- CurriculumAgent becomes a lightweight branch scheduler.
- CriticAgent becomes a scoring rubric plus optional adversarial check.
- SkillManager becomes a candidate-operator library, not automatically installed Codex skills.
- EventRecorder becomes the exploration ledger and artifact manifest.

Implementation rule:

- Do not promote a discovered operator into a real skill until it proves reusable beyond one lucky branch.

## Target Artifact

Create a global skill:

```text
<global-codex-skills>\codex-exploration-loop\
  SKILL.md
  agents\openai.yaml
  references\ledger-schema.md
  references\worktree-isolation.md
  references\branch-operators.md
  references\official-codex-mechanisms.md
  references\codex-exec-round-workers.md
  references\automation-and-sdk-runner.md
  schemas\round-result.schema.json
  prompts\lead-controller.prompt.md
  prompts\round-worker.prompt.md
  scripts\explore_ledger.py
```

Then sync to the registered skills storage repo:

```text
<skills-storage-repo>\skills\codex-exploration-loop\
```

Follow the existing skill storage sync contract:

- validate global and repo copies,
- compare file-level SHA-256,
- update catalog if needed,
- commit and push the storage repo unless the user says otherwise.

## Skill Contract

### Trigger

Use when the user asks Codex to explore a fuzzy problem with a time/round budget, attack an unclear bug, search for surprising designs, brute-force possible approaches, run a "loop" that is not completion-oriented, or keep trying in a sandbox for potentially surprising discoveries.

Do not use for:

- a well-defined implementation task,
- finalizing a known solution,
- review-only requests,
- credential setup,
- high-risk external actions.

### Required Inputs

If absent, choose safe defaults and state them:

- `question`: restate the fuzzy target.
- `max_rounds`: default 6.
- `max_round_minutes`: default 10.
- `mode`: `scout`, `standard`, or `bull`; default `standard`.
- `workspace`: current repo unless the user names another one.

Ask one question only if the answer changes safety or cost:

- destructive edits allowed?
- paid or authenticated network allowed?
- commit/push allowed?

Default answer:

- destructive edits, paid calls, credential handling, commit/push, and merge are not allowed without explicit confirmation.
- scratch edits, public network search, local commands, and local skills are allowed in the scratch area.

### Modes

Scout:

- 3 rounds.
- 5 minutes per round.
- no broad edits.
- used for cheap uncertainty reduction.

Standard:

- 6 rounds.
- 10 minutes per round.
- scratch worktree for edits.
- network and local skills allowed.

Bull:

- 10 rounds.
- 15 minutes per round.
- scratch worktree required.
- subagents allowed.
- branch fanout allowed.
- explicit user confirmation before any paid, credential, destructive, commit/push, or merge action.

## Harness Script

Use a Python standard-library script so it runs on Windows without extra dependencies.
This script is a ledger adapter, not an agent runner.

`scripts/explore_ledger.py` commands:

```powershell
python scripts\explore_ledger.py init `
  --root <workspace> `
  --slug <slug> `
  --question "<question>" `
  --max-rounds 6 `
  --max-round-minutes 10 `
  --mode standard `
  --scratch-worktree <path>

python scripts\explore_ledger.py start-round `
  --run-dir <run-dir> `
  --round 1 `
  --branch-id b001 `
  --timebox-minutes 10

python scripts\explore_ledger.py finish-round `
  --run-dir <run-dir> `
  --record-json <json>

python scripts\explore_ledger.py abort-round `
  --run-dir <run-dir> `
  --reason timeout

python scripts\explore_ledger.py append-round `
  --run-dir <run-dir> `
  --record-json <json>

python scripts\explore_ledger.py frontier `
  --run-dir <run-dir>

python scripts\explore_ledger.py digest `
  --run-dir <run-dir>
```

Generated structure:

```text
explorations/<YYYY-MM-DD>-<slug>/
  brief.md
  ledger.jsonl
  frontier.json
  branches/
    b001.md
  artifacts/
  scratch-worktree.md
  final-digest.md
```

The script should not run Codex or call LLMs. It only manages state files. Codex remains the loop controller.

`max_round_minutes` is a soft decision checkpoint in v1. Use command-level timeouts for shell probes when possible, but do not promise exact wall-clock interruption without an external runner.

## Official Codex Runtime Use

Prefer official Codex surfaces before adding custom orchestration.

### `codex exec` Round Workers

Use `codex exec` for scripted branch workers when an exploration round should run
without interactive steering and produce a machine-readable result.

Template:

```powershell
codex exec `
  --cd <scratch-worktree> `
  --sandbox workspace-write `
  --profile codex-exploration-standard `
  --output-schema <skill-dir>\schemas\round-result.schema.json `
  --output-last-message <run-dir>\artifacts\b001-round-001.json `
  --json `
  "<round-worker prompt>"
```

Use `codex exec resume --last` only when the next round should continue the same
non-interactive session. Otherwise start a fresh worker and pass the compact
branch memory explicitly.

Avoid `--dangerously-bypass-approvals-and-sandbox` except inside a disposable
runner that is already isolated outside the target repo.

### Permission Profiles

Provide templates for:

- `codex-exploration-scout`: read-heavy, no broad writes.
- `codex-exploration-standard`: `workspace-write`, scratch worktree writes, controlled network.
- `codex-exploration-bull`: scratch worktree writes, bounded subagents, explicit gates for paid/auth/destructive actions.

Do not edit user-level Codex config automatically. The skill should recommend or
use existing profiles when available and record the active profile in the ledger.

### Subagents

Use native subagents for independent branch scouts. Respect configured thread
limits and per-worker runtime limits. The lead agent owns scoring, pruning, and
ledger integration.

### Automations And SDK/App-Server

Use thread automations when the same conversation should wake up on a schedule.
Use standalone or project automations when each run should be independent.
Use SDK/app-server only when a trusted external controller must own scheduling,
approvals, streamed events, or resume.

The external controller must call Codex surfaces. It must not directly rebuild
the model/tool execution loop.

## Worktree Isolation

Default command when target is a git repo:

```powershell
git status --short --branch
git worktree add -b explore/<slug>-<timestamp> <scratch-worktree-path> HEAD
```

If worktree creation fails:

- stop if edits are needed,
- continue read-only if the task can be explored without edits,
- or ask the user whether a scratch copy is acceptable.

Promotion rule:

- Exploration output is not merged.
- A promoted lead becomes a separate `codex-completion-loop` task in the main repo or a clean branch.

## Branch Model

`frontier.json`:

```json
{
  "active": ["b001"],
  "branches": {
    "b001": {
      "status": "active",
      "hypothesis": "...",
      "last_score": 2.8,
      "rounds": [1],
      "recent_reflections": ["..."],
      "next_probe": "..."
    }
  }
}
```

Branch statuses:

- `active`: eligible for next round.
- `paused`: useful but blocked by cost, auth, data, or dependency.
- `pruned`: likely dead end.
- `promoted`: yielded a lead for completion/review.
- `merged`: combined into another branch.

## Round Record

Use this JSONL shape:

```json
{
  "round": 1,
  "started_at": "2026-06-24T00:00:00+08:00",
  "ended_at": "2026-06-24T00:08:12+08:00",
  "timebox_minutes": 10,
  "branch_id": "b001",
  "hypothesis": "A stale cache explains the failure.",
  "probe": "Search cache writes and run the focused failing test after clearing cache.",
  "actions": [
    {"kind": "shell", "summary": "rg cache", "result": "found three writers"},
    {"kind": "edit", "summary": "scratch patch to disable cache", "result": "test changed failure mode"}
  ],
  "network_used": false,
  "skills_used": [],
  "subagents_used": [],
  "files_touched": ["..."],
  "evidence": [
    {"path_or_url": "...", "supports": "...", "confidence": "medium"}
  ],
  "scores": {
    "novelty": 3,
    "promise": 4,
    "evidence": 3,
    "risk": 2,
    "cost": 2,
    "total": 3.0
  },
  "reflection": "Cache is involved but not the only cause; next probe should isolate invalidation timing.",
  "decision": "continue",
  "next_probe": "Instrument invalidation order in scratch branch."
}
```

## Scoring And Selection

Default total:

```text
total = 0.30 * promise
      + 0.25 * novelty
      + 0.25 * evidence
      - 0.10 * risk
      - 0.10 * cost
      + exploration_bonus
```

Selection strategy:

- Keep top 2 active branches by total.
- Keep 1 diversity branch if it has high novelty and low cost.
- Prune branches with two stale rounds and no new evidence.
- Pivot when the top branch is blocked or low-evidence after repeated probes.

## Local Skill Operators

The exploration skill can call other skills as branch operators:

- `anysearch`: public source search.
- `deep-think-reasoning`: generate or critique lanes.
- `codex-native-subagent-team`: run independent branch scouts.
- `codex-adversarial-qa`: attack a promising lead before promotion.
- `reporting-trace-maintainer`: record project-relevant discoveries.
- `codex-completion-loop`: implement a promoted lead.
- `skill-eval-optimizer`: test the exploration skill itself.

Operator rule:

- Operator output must be converted into a round record. Do not let a sub-skill become an unlogged side quest.

## Subagent Use

Subagents are allowed in `bull` mode by default, and in `standard` only when there are independent branches.

Subagent prompt:

```text
Explore branch <branch-id> for <question>.
Budget: <minutes> minutes.
Workspace: <scratch worktree or read-only repo>.
Allowed: <actions>.
Forbidden: credentials, paid calls, commit/push, destructive cleanup outside scratch.
Return:
- hypothesis tested
- probes run
- evidence paths/URLs
- surprising leads
- dead ends
- score suggestion
- next decision
```

Lead agent must integrate, score, and log the result.

## Output Shape

Final response:

```text
Exploration complete
- Budget used:
- Run dir:
- Scratch worktree:

Best leads
1. ...

Dead ends
- ...

Artifacts
- ...

Recommended next lane
- completion-loop / adversarial-qa / continue-exploration / human decision

Not done
- ...
```

## RALPLAN-DR

Principles:

- Exploration is not completion; its output is leads and evidence.
- Boldness belongs in isolation, not the main worktree.
- Every loop must have state, reflection, and a decision.
- Successful tricks become candidate operators first, real skills later.

Decision drivers:

- The user wants time/round driven exploratory force, not plan-driven closure.
- ToT, Reflexion, and Voyager all show that useful loops need frontier, memory, critique, and persistence.
- Native Codex can implement most of this at the skill/harness layer without a custom daemon.

Viable options:

1. Skill only.
   - Pro: fastest, portable.
   - Con: state management is manual and fragile.
2. Skill plus tiny ledger harness.
   - Pro: practical balance; state is durable while Codex remains controller.
   - Con: needs script maintenance.
3. Full autonomous harness.
   - Pro: best for overnight runs.
   - Con: too much machinery before eval evidence if it rebuilds Codex.
4. Skill plus ledger plus official Codex runtime adapters.
   - Pro: heavier and more repeatable while still using Codex permissions, subagents, `codex exec`, output schemas, automations, and SDK/app-server.
   - Con: requires more reference docs and a small schema/prompt bundle.

Decision:

- Build option 4 incrementally: option 2 first, then `codex exec` schema-backed round workers, then automations or SDK/app-server only after a dry-run proves value.

Rejected:

- Do not fold this into `codex-completion-loop`; it has a different stop condition and risk model.

## ADR

Decision:

- Implement `codex-exploration-loop` as a new skill with a Python ledger adapter and official Codex runtime adapters.

Status:

- Proposed for implementation.

Consequences:

- Requires new skill files and storage-repo sync.
- Requires a small public-safe fixture experiment in `agent-workflow-lab`.
- Uses Codex mechanisms before custom harness code.
- Keeps long-running autonomy optional rather than mandatory.

## Implementation Steps

1. Create global skill folder with `skill-creator`.
2. Add `SKILL.md` with triggers, modes, workflow, boundaries, and output contract.
3. Add references:
   - `ledger-schema.md`
   - `worktree-isolation.md`
   - `branch-operators.md`
   - `official-codex-mechanisms.md`
   - `codex-exec-round-workers.md`
   - `automation-and-sdk-runner.md`
4. Add `schemas/round-result.schema.json`.
5. Add prompt templates:
   - `prompts/lead-controller.prompt.md`
   - `prompts/round-worker.prompt.md`
6. Add `scripts/explore_ledger.py`.
7. Validate with `quick_validate.py`.
8. Create a tiny lab fixture under `experiments/` for a 2-round dry run.
9. Run the dry run manually:
   - initialize run dir,
   - append two synthetic/real round records,
   - generate digest,
   - verify ignored scratch/source boundaries.
10. Run one `codex exec` synthetic round with `--output-schema`.
11. Sync the skill to `<skills-storage-repo>\skills\codex-exploration-loop`.
12. Run repo/global parity check and commit/push storage repo.

## Test Plan

Static:

- `quick_validate.py <skill-dir>`
- `python scripts\explore_ledger.py --help`
- `python scripts\explore_ledger.py init ...`
- `python scripts\explore_ledger.py start-round ...`
- `python scripts\explore_ledger.py finish-round ...`
- `python scripts\explore_ledger.py abort-round ...`
- `python scripts\explore_ledger.py append-round ...`
- `python scripts\explore_ledger.py frontier ...`
- `python scripts\explore_ledger.py digest ...`
- validate `schemas/round-result.schema.json` with one known-good round result and one invalid result.
- run a synthetic `codex exec --output-schema ...` worker if the local Codex CLI is available.

Behavior:

- Run a 2-round scout in `<agent-workflow-lab>` against a tiny fixture.
- Confirm the main worktree is not edited by scratch actions.
- Confirm `ledger.jsonl`, `frontier.json`, and `final-digest.md` are produced.
- Confirm the final response recommends a next lane rather than claiming completion.
- Confirm the `codex exec` worker output can be appended to the same ledger without custom parsing.

Risk tests:

- Missing git repo: falls back to read-only or scratch copy.
- Dirty worktree: records status and still creates worktree from HEAD.
- Invalid JSON append: fails closed without corrupting `ledger.jsonl`.
- User asks for commit/push during exploration: requires explicit confirmation or defers to completion loop.
- `codex exec` worker returns invalid schema: log the failed worker output as an artifact and require lead-agent review.

## Open Questions

- Should the first skill default run dir live in target repo `explorations/` or in `agent-workflow-lab/experiments/` when the target repo is public-sensitive?
- Should `bull` mode automatically suggest subagents, or only use them when explicitly requested in the prompt?
- Should branch scores be manually assigned by Codex or supported by a deterministic helper that recomputes totals?
- Should the first implementation include `codex exec` as a documented manual command only, or a thin adapter command that prepares prompts and paths?
