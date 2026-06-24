# Agent Workflow Method Comparison

Status: draft
Last updated: 2026-06-24

## Purpose

This note turns the first scouting pass into a working comparison map. It is meant to guide experiments: when a new pattern appears, classify what problem it solves, what evidence would prove it useful, and how it tends to fail.

## Quick Decision Table

| Method | Solves | Use when | Avoid when | Test with |
|---|---|---|---|---|
| Project rules (`AGENTS.md`, `CLAUDE.md`) | Persistent local norms | The rule should apply almost every session in this repo | The instruction is long, rare, or workflow-specific | Run the same repo task with and without the rule file |
| Skill | Reusable SOP / capability pack | A repeated workflow needs instructions, references, templates, or scripts | It is a one-off note or pure project background | Compare trigger reliability and output quality across 3 prompts |
| Harness | Execution environment around the model | Reliability depends on tools, permissions, state, verification, or repeatability | A simple chat answer is enough | Rerun the same task and compare trace, diff, tests, and recovery |
| Loop | Repeated improvement toward a stop condition | Work needs implement -> verify -> fix -> report cycles | No exit condition or evidence exists | Force one failing case and see if the loop converges or spins |
| Goal / long-running task state | Durable objective and stop criteria | The task spans many turns or long background work | The objective is vague or acceptance is subjective | Resume after context loss and check whether state is enough |
| Subagent | Context isolation and specialization | Exploration, review, or domain checks would pollute main context | The split has no clear output contract | Compare single-agent review vs specialized reviewer set |
| Hook | Deterministic lifecycle guardrail | A rule must fire at prompt/tool/stop boundaries | False positives would block normal work too often | Seed risky commands/prompts and measure block/allow accuracy |
| MCP / tool server | Structured external capability | The agent needs live external state or app/API access | Browser/shell is simpler and reliable enough | Run the same lookup through MCP and fallback route |
| Worktree isolation | Parallel safe execution | Multiple agents/tasks may edit code concurrently | Single tiny change or no git repo | Run two edits in parallel and inspect merge/conflict behavior |
| Eval / trace loop | Measurable harness improvement | There are recurring failures and enough traces to score | No stable task set or success metric exists | Convert 5 failures into eval cases and measure before/after |

## Method Notes

### Project Rules

Project rules are the lowest-friction control layer. They should hold stable facts the agent must see nearly every time: package manager, test commands, architecture boundaries, safety rules, repo-specific conventions, and required verification.

Good signs:

- The rule is short.
- The rule applies often.
- Violating it causes real rework or risk.
- It does not need a long explanation.

Common failures:

- Turning rules into a long knowledge dump.
- Mixing durable repo rules with temporary task notes.
- Hiding workflow details that should become a skill.

First experiment:

- Pick one repo task.
- Run once with minimal rules and once with a stronger `AGENTS.md`.
- Compare unnecessary file reads, command choice, verification coverage, and final diff scope.

### Skill

A skill is a portable workflow asset. It is best when the agent needs a named capability that can be loaded only when relevant: review procedure, paper digest pipeline, benchmark protocol, release checklist, visual QA loop, or domain-specific troubleshooting path.

Use a skill when:

- The same workflow repeats across tasks or repos.
- The instructions are too long for always-on project rules.
- The workflow benefits from templates, scripts, references, or assets.
- You want explicit invocation like `$skill-name`.

Do not use a skill when:

- It is just a single command.
- It only applies to one file in one repo.
- It contains private context that should not travel.
- It has no clear trigger condition.

Failure modes:

- Over-broad descriptions trigger at the wrong time.
- Over-narrow descriptions never trigger.
- The skill duplicates project rules and becomes stale.
- Scripts inside the skill are brittle compared with simpler instructions.

First experiment:

- Encode the same workflow as a skill and as project rules.
- Try 3 prompts: explicit invocation, implicit relevant prompt, and unrelated prompt.
- Record trigger accuracy and output quality.

### Harness

Harness is the environment around the model: tool surface, permissions, context loading, memory, sandbox, worktree, tests, traces, state files, and feedback loops. It is not one feature; it is the system that lets a model act reliably.

Use harness thinking when:

- The task fails because the agent lacks tools, feedback, or state.
- Repeated prompts are being used to patch the same structural gap.
- The important question is repeatability, not one successful run.
- You need auditability or handoff.

Failure modes:

- Building a big framework before the workflow is stable.
- Adding orchestration where a checklist would work.
- Capturing too much raw state and creating privacy risk.
- Optimizing for demos instead of failure recovery.

First experiment:

- Inspect a minimal harness such as Pu.sh or Zot.
- Recreate only the smallest loop: read files, edit, run check, recover from failed edit.
- Compare against ordinary agent usage on the same fixture.

### Loop

A loop is useful only if it has state, evidence, and a stopping rule. "Keep trying" is not a loop design; it is a risk.

Good loop ingredients:

- Fixed objective.
- Explicit state file or progress markers.
- A validator or observable signal.
- Retry budget or escalation rule.
- Final report format.

Useful loop types:

- implement -> test -> fix;
- benchmark -> profile -> patch -> rerun;
- trace -> classify failure -> add eval -> improve harness;
- discover -> triage -> act -> verify -> remember.

Failure modes:

- Infinite polishing.
- Silent objective drift.
- Re-running expensive checks without learning.
- Treating flaky signals as truth.

First experiment:

- Create a tiny failing test fixture.
- Ask an agent loop to fix it with max 3 attempts.
- Measure whether it records attempts, stops correctly, and explains residual risk.

### Goal / Long-Running State

A goal or durable state record is for tasks that outlive a single turn. It should preserve objective, constraints, acceptance criteria, evidence, blockers, and current step.

Use it when:

- Work may run for hours or across context compaction.
- The task has multiple milestones.
- A human may leave and come back later.
- The agent must know when not to continue.

Failure modes:

- Goal is too broad.
- Acceptance criteria are not observable.
- State file becomes a diary instead of an operational record.
- The agent marks completion because budget/time is low, not because evidence passes.

First experiment:

- Use a `SPEC.md`, `PLAN.md`, and `STATUS.md` stack for a small feature.
- Interrupt after one milestone.
- Resume and check whether another agent can continue from disk state only.

### Subagent

Subagents are best understood as context isolation with a role and output contract. Parallelism is useful, but not the core reason to use them.

Use subagents for:

- security review;
- test gap analysis;
- codebase search;
- design critique;
- source collection;
- competing implementation options.

Keep in lead agent:

- final decision;
- cross-cutting tradeoffs;
- user-facing summary;
- file edits unless delegation is explicitly intended.

Failure modes:

- Vague delegation produces vague summaries.
- Too many agents multiply noise.
- Subagents independently rediscover the same context.
- The lead agent accepts findings without evidence.

First experiment:

- Review one diff with a single agent.
- Review the same diff with 4 subagents: correctness, security, tests, maintainability.
- Compare unique findings, false positives, and time/cost.

### Hook

Hooks are deterministic guardrails at lifecycle boundaries. They are stronger than instructions because they run outside the model's discretion.

Use hooks for:

- secret scanning before prompt submission or commit;
- blocking destructive shell commands;
- enforcing post-turn validation;
- injecting small, current context;
- logging tool use for audit.

Avoid hooks when:

- The rule requires nuanced human judgment.
- False positives would derail normal work.
- The same behavior can be achieved with a simpler command or test.

Failure modes:

- Brittle regex blocks legitimate work.
- Hook output pollutes context.
- Hidden hook behavior makes the system hard to debug.
- Stop hooks create unwanted continuation loops.

First experiment:

- Write a tiny prompt/tool guard that blocks obvious secret-like strings and destructive commands.
- Run 10 allow/block examples.
- Track false positive and false negative cases.

### MCP / Tool Server

MCP or tool servers are for structured access to external state: search engines, Figma, browser state, APIs, databases, local apps, or domain runtimes.

Use MCP when:

- The tool has a stable schema and beats ad hoc browser/shell use.
- Auth can stay local and private.
- The result needs provenance or structured fields.
- Failure modes can degrade gracefully.

Failure modes:

- Tool login state silently expires.
- The MCP route is less reliable than a simple CLI/API call.
- Tool responses are treated as authoritative without cross-checking.
- Credentials leak into logs or repo files.

First experiment:

- Choose one lookup task.
- Run it through MCP and through a fallback public route.
- Compare completeness, speed, failure clarity, and citation quality.

### Worktree Isolation

Worktree isolation is a harness technique for keeping multiple tasks from colliding. It matters when agents work in parallel or when a task is risky enough to deserve a separate branch.

Use it when:

- Multiple agents will edit overlapping repos.
- Tasks can be independently branched and tested.
- A failed attempt should be discarded cleanly.
- You need clean diffs per task.

Failure modes:

- Shared caches, ports, or generated artifacts still collide.
- Merge overhead exceeds benefits.
- Agents modify parent repo state by accident.
- Worktree names and task IDs drift apart.

First experiment:

- Create two small feature branches via worktrees.
- Run separate tasks in each.
- Merge or compare diffs and record conflicts.

### Eval / Trace Loop

Eval loops are for improving the harness itself. The unit is not a single answer; it is a recurring failure class turned into a measurable test.

Use it when:

- You have repeated failures.
- You can capture traces or examples.
- Success can be scored by a script, rubric, or human label.
- You want to compare harness changes without changing the base model.

Failure modes:

- Eval set is too small or too tailored to one fix.
- Metrics reward superficial behavior.
- Trace data contains private content.
- Improvements overfit to easy cases.

First experiment:

- Collect 5 failures from one workflow.
- Write expected outcome criteria.
- Change one harness component.
- Rerun and compare before/after.

## Observed Trend Map

| Trend | Evidence signal | What to test next |
|---|---|---|
| Claude plans, Codex executes | Xiaohongshu, Reddit, WeChat discovery | Two-agent handoff with fixed task and acceptance criteria |
| Do not use agents "naked" | Zhihu, Xiaohongshu, official harness framing | Compare bare prompt vs project rules vs skill/harness |
| Skills as portable SOP | OpenAI docs, Anthropic docs, Zhihu AI-Infra skills | Build one repo-agnostic skill and test trigger reliability |
| Harness minimalism | HN Pu.sh, Zot, simpler harness posts | Reproduce minimal read/edit/test loop |
| Long-running supervision | OpenAI long-running work, Xiaohongshu long-task notes | SPEC/PLAN/STATUS experiment with interruption/resume |
| Multi-agent review | Official subagents, forum examples | Compare one reviewer vs role-specialized reviewers |
| Packaging agent setups | VAEN, plugin/skill repos | Decide whether this repo needs a template bundle format |

## Ranking For This Repo

Most valuable to test first:

1. Skill vs project rules vs script-backed harness.
2. Claude planning -> Codex execution handoff.
3. Minimal harness loop on a tiny local fixture.
4. Subagent review boundaries.
5. Long-running goal/state file pattern.

Not first:

- Heavy social-platform crawling.
- Large multi-agent teams.
- Full custom MCP servers.
- Fully autonomous background agents.

## Working Conclusion

The useful axis is not tool brand. The useful axis is: where does the control live?

- In always-on project memory: use project rules.
- In reusable procedural knowledge: use a skill.
- In deterministic lifecycle enforcement: use hooks.
- In external capability access: use MCP.
- In context isolation: use subagents.
- In repeatable execution and verification: use a harness.
- In long-horizon state and stop criteria: use goals / status files.

The next step is to run small experiments that change one control layer at a time.
