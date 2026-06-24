# Codex Harness Support Assessment for Exploration Loop

Date: 2026-06-24
Status: design constraint
Related:

- `notes/2026-06-24-codex-exploration-loop-design.zh.md`
- `notes/2026-06-24-codex-exploration-loop-implementation-plan.zh.md`
- `notes/2026-06-24-official-codex-first-exploration-architecture.zh.md`

## Verdict

The exploration-loop design can be supported smoothly by Codex if v1 is treated as a
skill-led interactive workflow with a small ledger harness, and v1.5 composes
official Codex runtime mechanisms instead of building a parallel agent platform:

- `SKILL.md` defines the loop protocol, round gates, scoring, reflection, and output.
- A Python helper persists state, initializes run directories, and records round results.
- Git worktrees, sandbox settings, approval policy, and repo instructions provide isolation.
- Subagents are bounded branch scouts, not an unbounded swarm.
- `codex exec` plus output schemas can run scripted branch workers.
- Automations, Codex SDK, or app-server integration are optional v2 layers for unattended or programmatic runs.

It should not be implemented as a fully autonomous Voyager-style daemon inside a skill alone.
A skill can guide Codex, load references, and run helper scripts, but it cannot by itself
guarantee hard wall-clock interrupts, future scheduled wakeups, or long-lived autonomous
curriculum management across many turns.

## Official Codex Surface Checked

- Codex Skills: skills package instructions, resources, and optional scripts; they are the right surface for reusable workflows.
- Codex Subagents: Codex can spawn specialized agents in parallel and collect their results; subagents inherit sandbox policy and consume extra tokens.
- Codex config: `sandbox_mode`, `approval_policy`, `sandbox_workspace_write.network_access`, `agents.max_threads`, `agents.job_max_runtime_seconds`, and `skills.config` provide relevant controls.
- Codex CLI: `codex exec` supports scripted runs, JSON events, output schemas, output files, sandbox selection, profiles, and resume.
- Codex automations: thread automations can wake a thread on a schedule, and standalone automations can run fresh scheduled work; both use sandbox settings.
- Codex SDK/app-server: useful when a separate trusted runner must own scheduling, approvals, streamed events, and resume.

## Support Matrix

| Mechanism | Codex support | Design decision |
|---|---:|---|
| Skill packaging | Strong | Put the exploration protocol in `codex-exploration-loop`. Keep scripts optional and stdlib-only. |
| Local/repo instructions | Strong | Let `AGENTS.md` define repo safety, public/private boundaries, and project conventions. |
| Worktree isolation | Strong | Use scratch worktrees by default for edit-heavy exploration. Record dirty status before creating the worktree. |
| Sandbox and approvals | Strong, environment-dependent | Treat destructive, paid, credential, commit/push, and merge actions as explicit gates. |
| Public network/MCP/browser search | Strong, environment-dependent | Allow as a declared action class; log every source and provider. |
| Round count budget | Strong | `max_rounds` is easy to enforce in the skill loop and ledger. |
| Per-round time budget | Partial | Treat `max_round_minutes` as a soft round budget in v1; use command timeouts where possible. Hard round interruption needs SDK/app-server or an external watchdog. |
| JSONL ledger/frontier state | Strong | Use the harness script as the durable state layer; do not rely on chat memory alone. |
| Reflexion-style memory | Strong | Store all reflections in JSONL; feed only compact recent reflections back into the active branch prompt. |
| ToT-style frontier search | Strong | Maintain `frontier.json` with branch scores and round decisions. |
| Voyager-style skill library | Partial | Keep discovered tricks as candidate operators first. Promote to real Codex skills only after repeatable evidence. |
| Subagent branch scouts | Strong when available | Use bounded fanout; lead agent must integrate, score, and log results. Provide serial fallback. |
| Scripted branch workers | Strong | Prefer `codex exec` with `--output-schema`, `--json`, `--profile`, and `--sandbox` over custom model-call workers. |
| Local skill routing | Partial | Skills are invoked by Codex behavior, not as stable function calls. The lead agent must explicitly route and log sub-skill outputs. |
| Scheduled continuation | Partial | Codex app automations can do heartbeat-style continuation. CLI-only skill use should not promise unattended continuation. |
| Long overnight run | Partial | Requires automation, SDK/app-server, or another runner with checkpointing and safety policy. |
| Exact daemon-like autonomy | Weak in skill-only v1 | Defer to v2; if needed, orchestrate Codex through automations, SDK, or app-server rather than rebuilding the agent loop. |

## Required Design Adjustments

1. Split time budgets into two terms:
   - `round_timebox_minutes`: a soft decision checkpoint for the lead agent.
   - `command_timeout_seconds`: a hard timeout for shell/subprocess probes where available.

2. Extend the ledger script with recoverable round state:
   - `start-round`: writes a pending round file.
   - `finish-round`: validates and appends to `ledger.jsonl`.
   - `abort-round`: records interruption, timeout, or human stop without corrupting the ledger.

3. Make subagents opt-in by mode and feature availability:
   - `scout`: no subagents.
   - `standard`: subagents only when the user asks or branches are clearly independent.
   - `bull`: subagents allowed, but capped by configured thread limits and round budget.

4. Make path containment a first-class safety check:
   - All edit probes run inside the scratch worktree or declared writable run directory.
   - Before recursive delete or move on Windows, resolve and verify the target path.

5. Separate v1 and v2 responsibilities:
   - v1: skill + ledger script + manual/interactive Codex execution.
   - v1.5: add `codex exec` round workers and JSON schemas.
   - v2: Codex SDK/app-server or automations for recurring, unattended, or exact-timeboxed runs.

6. Add an explicit "do not rebuild Codex" rule:
   - no custom LLM loop,
   - no custom subagent pool,
   - no custom approval/sandbox layer,
   - no custom scheduler when Codex automations fit.

## Implementation Consequence

Build the skill and ledger harness first, then run a two-round public fixture in this lab.
Only after that fixture shows useful frontier movement should we add a programmatic runner.
This keeps the "bold exploration" behavior real, but avoids pretending a `SKILL.md` alone can
enforce process-level scheduling and interruption.
