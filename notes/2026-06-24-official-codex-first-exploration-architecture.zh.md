# Official Codex First Exploration Architecture

Date: 2026-06-24
Status: architecture revision
Related:

- `notes/2026-06-24-codex-exploration-loop-design.zh.md`
- `notes/2026-06-24-codex-exploration-loop-implementation-plan.zh.md`
- `notes/2026-06-24-codex-harness-support-assessment.zh.md`

## Design Turn

The exploration loop can be heavier than a pure skill, but it should be heavier by
composing official Codex mechanisms, not by building a separate agent framework.

The project should avoid reimplementing:

- model/tool loops,
- subagent scheduling,
- sandbox and approval policy,
- worktree isolation,
- recurring wake-up scheduling,
- final-output schema validation,
- plugin or skill distribution.

The custom code we write should stay narrow:

- ledger and frontier persistence,
- schema files for round results,
- prompt templates for branch workers,
- adapters that call official Codex surfaces,
- digest generation from logged records.

## Three-Layer Architecture

### Layer 1: Skill Protocol

Use `codex-exploration-loop` as the authoring surface.

Responsibilities:

- decide when this workflow applies,
- define modes, budgets, branch decisions, scoring, reflection, and output shape,
- route to other local skills when useful,
- explain what must be logged at each round,
- keep safety gates human-readable.

Use official skill mechanisms:

- `SKILL.md` for instructions and metadata,
- `references/` for ledger schema, worktree rules, branch operators, and official-mechanism notes,
- `scripts/` only for local deterministic helpers,
- `agents/openai.yaml` only for appearance/dependencies if needed,
- plugin packaging later if the skill needs distribution.

### Layer 2: Official Codex Runtime

Use Codex runtime mechanisms as the execution substrate.

Mechanisms to rely on first:

- AGENTS.md and repo-local instructions for durable project policy.
- Codex skills and progressive disclosure for workflow routing.
- Codex permissions profiles, sandbox modes, approval policy, and network policy for boundaries.
- Codex app worktrees where available; otherwise plain Git worktrees.
- Native subagents for bounded branch scouts.
- MCP/connectors/web search for external tools and data.
- `codex exec` for scripted round workers.
- `--output-schema`, `--output-last-message`, and `--json` for machine-readable worker results.
- `codex exec resume` for non-interactive continuation where that is the right surface.

Round worker pattern:

```powershell
codex exec `
  --cd <scratch-worktree> `
  --sandbox workspace-write `
  --profile codex-exploration-standard `
  --output-schema <round-result.schema.json> `
  --output-last-message <round-result.json> `
  --json `
  "<round prompt>"
```

Do not use `--dangerously-bypass-approvals-and-sandbox` except inside a separately
isolated disposable runner. The normal mode should prefer `workspace-write` plus
explicit permission profiles.

### Layer 3: Official Long-Run Orchestration

Use Codex app automations, SDK, or app-server only when the run needs capabilities
that an interactive skill cannot provide.

Recommended mapping:

| Need | Official surface |
|---|---|
| Same conversation wakes up on a schedule | Thread automation |
| Independent recurring search or triage | Standalone or project automation |
| Scripted one-shot branch worker | `codex exec` |
| Resume a scripted run | `codex exec resume` |
| Custom UI or trusted external controller | Codex SDK or app-server |
| External tool surface | MCP/connectors |
| Team distribution | Plugin packaging |

The external runner, if we add one later, should orchestrate Codex. It should not
call the base model API and rebuild Codex's tool loop from scratch.

## Heavier v1.5, Not a Custom Agent Platform

The right "slightly heavier" version is:

1. Skill protocol.
2. Ledger helper.
3. JSON output schema for round workers.
4. Prompt templates for lead and branch workers.
5. Optional `codex exec` adapter for branch rounds.
6. Optional permission-profile templates.
7. Optional automation prompt templates.

The wrong heavier version is:

- a Python daemon that owns the model loop,
- a custom process pool that pretends to be subagents,
- a custom web crawler where MCP/search already exists,
- an ad hoc sandbox instead of Codex permissions/worktrees,
- a private scheduler instead of Codex automations for heartbeat runs.

## Revised Build Order

1. Build the skill and ledger helper.
2. Add `round-result.schema.json`.
3. Add `round-worker.prompt.md` and `lead-controller.prompt.md`.
4. Add `official-codex-mechanisms.md` as the skill reference explaining when to use skill, subagents, `codex exec`, automations, and SDK/app-server.
5. Run an interactive two-round scout.
6. Run one `codex exec` synthetic round against the schema.
7. Only then evaluate whether app automation or SDK/app-server adds value.

This gives the loop real operational weight while keeping Codex as the harness.
