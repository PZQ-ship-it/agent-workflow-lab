# Agent Workflow Taxonomy

Status: draft
Last updated: 2026-06-24

## Purpose

This map keeps the vocabulary grounded. It should help compare new patterns without treating every new label as a new category.

## Working Categories

### Skill

A reusable procedure or capability pack that tells an agent how to perform a class of tasks.

Initial test questions:

- Is it reusable across repos or only meaningful inside one project?
- Does it include concrete steps, scripts, templates, or assets?
- Does it change agent behavior enough to justify being separate from README / AGENTS.md?

### Harness

A repeatable execution wrapper for running, measuring, or verifying agent work.

Initial test questions:

- What input does it standardize?
- What output or trace does it capture?
- Can the same task be rerun and compared later?

### Loop

A repeated cycle that moves work toward a stopping condition, such as implement -> test -> inspect -> fix.

Initial test questions:

- What is the exit condition?
- What evidence prevents infinite polishing?
- Which step is automated, and which step requires human judgment?

### Agent / Subagent

A role-specialized worker used to split context, search space, responsibility, or verification.

Initial test questions:

- Is the split by domain, file area, risk type, or phase?
- What should remain with the lead agent?
- What output contract makes delegation useful?

### Hook

An automatic intervention at a tool, prompt, file, or lifecycle boundary.

Initial test questions:

- Is it advisory, blocking, or transformative?
- What false positives would annoy the user?
- What evidence should it see before firing?

### MCP / Tool Server

A structured integration that gives the agent access to external state, search, APIs, local apps, or specialized runtimes.

Initial test questions:

- Is the tool more reliable than browser or shell fallback?
- What auth and privacy boundary does it create?
- How should failures degrade?

## Comparison Axes

- Reusability: one repo, one domain, or many domains.
- Evidence: anecdote, public example, local test, repeated benchmark.
- Cost: setup, runtime, maintenance, context budget.
- Risk: privacy, destructive actions, stale assumptions, hidden state.
- Human role: requester, reviewer, planner, executor, or evaluator.
