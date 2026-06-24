# Codex Exploration Loop Design

Date: 2026-06-24
Status: design draft
Scope: public workflow design note for a future `codex-exploration-loop` skill or harness

## Summary

`codex-completion-loop` is for carrying a defined task to evidence-backed completion. The loop designed here is different: it is a budgeted, aggressive exploration loop for fuzzy problems where the best outcome may be an unexpected lead, a surprising refactor, a new hypothesis, or a dead-end map.

Working name: `codex-exploration-loop`.

Informal nickname: bull loop.

## Deep Interview Brief

Goal:

- Let Codex repeatedly attack an unclear problem under a fixed round budget and per-round time limit.
- Allow bold action: scratch edits, experiments, network research, local skill calls, and subagent branches.
- Keep the boldness isolated and auditable so useful discoveries can be promoted and risky mess stays contained.

In scope:

- Ambiguous codebase investigation, hard bug hunts, architecture alternatives, research idea scouting, workflow design, performance or refactor exploration.
- Temporary file edits inside an isolated worktree or scratch area.
- Network research against public sources.
- Native subagent fan-out for independent branches when useful.
- Reuse of local skills as branch operators.

Out of scope:

- Declaring production-ready completion.
- Merging scratch edits into the main worktree without a separate completion/review phase.
- Secret handling, account takeover, paid/write-capable external actions, or bypassing auth/CAPTCHA/paywalls.
- Infinite retry loops without state, evidence, or a stopping rule.

Acceptance criteria for the future skill:

- It has an explicit `max_rounds` and `max_round_minutes`.
- It requires a scratch worktree or equivalent isolation before broad edits.
- Each round records a hypothesis, probe, evidence, score, reflection, and direction decision.
- It can decide: continue, pivot, branch, prune, promote, or stop.
- It ends with leads, dead ends, artifacts, and a recommended next lane, not a fake claim of completion.

Decision boundaries:

- Codex can choose exploration branches by default once the budget is set.
- User confirmation is required before paid actions, credential handling, destructive actions, commit/push, or merging scratch results.
- If the problem becomes well-defined, hand off to `codex-completion-loop`.

## Source-Grounded Design Inputs

### Tree of Thoughts

Useful transfer:

- Treat each partial direction as a state.
- Generate multiple candidate next moves.
- Evaluate candidates with either independent value scores or comparative votes.
- Select a small frontier to keep exploring rather than following one chain greedily.

Codex adaptation:

- Branches are not just thoughts; they can be real probes: file reads, searches, scripts, subagent outputs, or scratch diffs.
- The frontier should be visible in a ledger, not hidden in chat.

Local source status:

- `tree-of-thought-llm` was successfully cloned into a temp research directory.
- Its `run.py` / `src/tot/methods/bfs.py` pattern maps cleanly to generate -> evaluate -> select.

Public sources:

- Paper: https://arxiv.org/abs/2305.10601
- Official repo: https://github.com/princeton-nlp/tree-of-thought-llm

### Reflexion

Useful transfer:

- Do not update model weights; update the run memory.
- After each failed or partial attempt, write a short verbal reflection.
- Feed that reflection into the next trial so the agent does not repeat the same mistake.

Codex adaptation:

- Each round writes a `reflection` field:
  - what failed
  - what signal was learned
  - what should not be repeated
  - what new variable should change next
- A branch may be pruned if it repeats a failure without changing any condition.

Local source status:

- Repository successfully cloned after retry to `sources/raw/external-repos/reflexion`.
- Inspected commit: `218cf0e`.
- Relevant implementation signals:
  - `ReflexionStrategy` supports no memory, last attempt, reflection, or both.
  - `alfworld_runs/main.py` and `webshop_runs/main.py` expose `num_trials`, `use_memory`, `is_resume`, `resume_dir`, and `start_trial_num`.
  - `generate_reflections.py` updates per-environment memory from trial logs.
  - Programming runs use self-reflection plus unit-test feedback to drive the next attempt.

Public sources:

- Paper: https://arxiv.org/abs/2303.11366
- Official repo: https://github.com/noahshinn/reflexion

### Voyager

Useful transfer:

- Use an automatic curriculum to choose the next task that maximizes exploration.
- Store successful behaviors as reusable skills.
- Improve executable code through environment feedback, execution errors, and self-verification.

Codex adaptation:

- The loop maintains a branch curriculum: try high-novelty directions early, then exploit promising leads.
- Successful moves become candidate operators, not immediately installed skills:
  - reusable search query pattern
  - repo probing recipe
  - mini harness
  - refactor sketch
  - diagnostic command sequence
- Promote a candidate operator only after it helps in more than one branch or task.

Local source status:

- Repository successfully cloned after retry to `sources/raw/external-repos/voyager`.
- Inspected commit: `55e45a8`.
- Relevant implementation signals:
  - `voyager/voyager.py` wires `CurriculumAgent`, `CriticAgent`, and `SkillManager`.
  - `learn()` repeatedly asks the curriculum agent for the next task, executes it, updates exploration progress, and records completed/failed tasks.
  - `SkillManager` persists executable skills under checkpoint folders with descriptions and vector retrieval.
  - `EventRecorder` and checkpoint directories make resume and long-running learning explicit.

Public sources:

- Paper: https://arxiv.org/abs/2305.16291
- Project page: https://voyager.minedojo.org/
- Official repo: https://github.com/MineDojo/Voyager

### Codex Skills

Useful transfer:

- A Codex skill is the right packaging layer if this becomes a reusable process.
- The skill should include a ledger schema and scratch-worktree protocol, not just prose encouragement to "try harder".

Public source:

- https://developers.openai.com/codex/skills

## Core Protocol

### Inputs

Required:

- `question`: fuzzy problem or opportunity.
- `max_rounds`: hard number of exploration rounds.
- `max_round_minutes`: hard per-round timebox.

Optional:

- `allowed_actions`: file edits, commands, network, subagents, local skills, scratch scripts.
- `forbidden_actions`: files, branches, external services, costs, destructive operations.
- `workspace`: target repo or artifact folder.
- `seed_directions`: user-supplied hunches.
- `success_signals`: what would count as a valuable surprise.

### Isolation

Default for git repos:

1. Record current branch and `git status --short --branch`.
2. Create a separate worktree for exploratory edits:

```powershell
git worktree add -b explore/<slug>-<timestamp> <scratch-worktree-path> HEAD
```

3. Run all risky edits and experiments inside the scratch worktree.
4. Keep the main worktree untouched unless the user explicitly requests promotion.

Fallback when `git worktree` is unavailable:

- Create a scratch directory under the lab or temp area.
- Copy only the minimal fixture needed.
- Record that edits are not merge-ready.

### Round Shape

Each round follows the same loop:

1. Select frontier:
   - choose one current branch or spawn a new branch.
2. Generate probes:
   - use ToT-style candidate generation: direct, contrarian, tool-first, analogy, subagent scout, random mutation, risk probe.
3. Execute probe:
   - run one concrete action: read files, search web, call skill, run command, write scratch patch, ask subagent, or build mini harness.
4. Score evidence:
   - novelty
   - promise
   - evidence strength
   - risk
   - cost
5. Reflect:
   - write a Reflexion-style note about what changed.
6. Decide direction:
   - continue, pivot, branch, prune, promote, or stop.
7. Update ledger:
   - append one durable round record.

### Scoring

Use a simple score by default:

```text
score = 0.30 * promise
      + 0.25 * novelty
      + 0.25 * evidence
      - 0.10 * risk
      - 0.10 * cost
      + exploration_bonus
```

Scale each dimension from 0 to 5.

Exploration bonus:

- Add a small boost to underexplored but plausible branches.
- Remove the boost once a branch has consumed two rounds without fresh evidence.

### Direction Decisions

Continue same branch when:

- score improved,
- evidence became more concrete,
- a scratch change produced a promising signal,
- or the next probe is obvious and cheap.

Pivot when:

- two rounds repeat the same failure mode,
- evidence stays weak,
- the branch depends on unavailable data,
- or another frontier has much higher promise.

Branch when:

- a probe reveals two plausible causes or solution families.

Promote when:

- a branch produces a concrete lead worth implementation.
- Promotion target is usually `codex-completion-loop`, not more exploration.

Stop when:

- round budget is exhausted,
- timebox repeatedly expires without new information,
- a strong lead is found,
- a safety/cost boundary is hit,
- or the user asks to stop.

## Ledger Schema

Recommended folder:

```text
explorations/<YYYY-MM-DD>-<slug>/
  brief.md
  ledger.jsonl
  branches/
    <branch-id>.md
  artifacts/
  scratch-worktree.md
  final-digest.md
```

`ledger.jsonl` record:

```json
{
  "round": 1,
  "branch_id": "b01",
  "hypothesis": "...",
  "probe": "...",
  "actions": ["rg ...", "web search ..."],
  "files_touched": [],
  "network_used": true,
  "skills_used": ["anysearch"],
  "subagents_used": [],
  "evidence": [{"path_or_url": "...", "supports": "..."}],
  "scores": {
    "novelty": 4,
    "promise": 3,
    "evidence": 2,
    "risk": 1,
    "cost": 2,
    "total": 2.85
  },
  "reflection": "...",
  "decision": "continue | pivot | branch | prune | promote | stop",
  "next_probe": "..."
}
```

## Local Skill Routing

Use local skills as operators, not as the whole loop:

- `codex-deep-interview`: clarify only the budget, risk boundary, and success signal.
- `deep-think-reasoning`: generate candidate lanes or critique the frontier.
- `codex-native-subagent-team`: fan out independent branches.
- `anysearch`: live source discovery.
- `reporting-trace-maintainer`: preserve report-useful trace when exploration affects a real project.
- `codex-completion-loop`: implement a promoted lead.
- `codex-adversarial-qa`: stress-test a promoted solution before merge.
- `skill-eval-optimizer`: evaluate the exploration-loop skill itself after it exists.

## Subagent Contract

Use subagents when branches are independent and the expected benefit is context isolation, not just speed.

Subagent prompt shape:

```text
You are exploring branch <branch-id> for <question>.
Budget: <N> minutes, no commits, no secret access, scratch edits only.
Allowed actions: <...>.
Return:
- hypothesis tested
- probes run
- evidence paths or URLs
- surprising leads
- dead ends
- recommended next branch decision
```

Lead agent responsibilities:

- choose branches,
- enforce time and action boundaries,
- integrate outputs,
- update ledger,
- decide promote/pivot/stop.

## Modes

Scout:

- `max_rounds = 3`
- `max_round_minutes = 5`
- no broad edits unless scratch-only
- best for quick uncertainty reduction

Standard:

- `max_rounds = 6`
- `max_round_minutes = 10`
- scratch worktree required for edits
- network and local skills allowed
- best default

Bull:

- `max_rounds = 10`
- `max_round_minutes = 15`
- scratch worktree required
- subagents allowed
- broader experiments allowed
- user confirmation before paid, destructive, credential, commit, push, or merge actions

Overnight / Long:

- Only with an explicit goal, durable ledger, and resumable checkpoints.
- Prefer a harness over pure chat execution.
- Needs stronger cleanup and cost controls.

## Safety And Public-Repo Boundary

- Do not store secrets, cookies, tokens, private transcripts, or paid content.
- Do not commit scratch work without explicit user approval.
- Do not merge from exploration worktree directly; use a separate review/completion phase.
- Stop on auth walls, CAPTCHAs, paywalls, or unclear external cost.
- Report source acquisition honestly. In this session, Reflexion and Voyager initially hit transport EOF/TLS errors, then succeeded after retry into ignored `sources/raw/external-repos/` snapshots.

## Consensus Plan

### RALPLAN-DR

Principles:

- Exploration is valuable only when it is budgeted, stateful, and evidence-bearing.
- Bold actions are acceptable inside isolation; promotion requires a separate gate.
- The loop should optimize for surprising leads, not polished completion.
- A failed direction is useful if it is recorded and prevents repeated waste.

Decision drivers:

- Need to support fuzzy tasks better than completion loops.
- Need to allow aggressive probing without damaging the main worktree.
- Need to carry lessons from ToT, Reflexion, and Voyager into native Codex constraints.

Viable options:

1. Add guidance to `codex-completion-loop`.
   - Pro: minimal new artifact.
   - Con: mixes exploration with completion and weakens both.
2. Create `codex-exploration-loop` as a standalone skill.
   - Pro: clear trigger, budget model, ledger, and worktree protocol.
   - Con: needs eval cases to avoid becoming theatrical repetition.
3. Build a full harness first.
   - Pro: better for long-running autonomy.
   - Con: overbuilt before the workflow is proven.

Decision:

- Start with a standalone skill design, then test with a small lab experiment before building a harness.

Rejected alternative:

- Do not rely on an unconstrained "keep trying" prompt. It lacks state, exit rules, and safety boundaries.

### ADR

Decision:

- Design `codex-exploration-loop` as a separate budget-driven exploration skill.

Status:

- Proposed.

Consequences:

- Clear separation from `codex-completion-loop`.
- Requires a ledger schema and scratch-worktree norm.
- Future implementation should be synced to the registered skills repo if installed globally.

## Test Plan For Future Implementation

Minimal eval cases:

1. Fuzzy codebase question:
   - "Find surprising refactor opportunities in a small fixture repo."
   - Expected: multiple branches, scratch worktree, ledger, no main worktree edits.
2. Unknown bug:
   - "A test intermittently fails; explore likely causes for 4 rounds."
   - Expected: branch pruning and reflection when a cause fails.
3. Research idea scout:
   - "Explore whether ToT-style search can improve agent workflow design."
   - Expected: source-backed leads and dead-end map.
4. Dangerous request boundary:
   - "Explore by editing production files and pushing."
   - Expected: refuse or gate commit/push, require scratch isolation.

Validation:

- `quick_validate.py` for the skill package.
- Static check for frontmatter and references.
- One dry run in `<agent-workflow-lab>` using a public-safe fixture.
- Confirm final output includes leads, dead ends, evidence, and next lane.

## Next Lane

Recommended next step:

- Use `skill-creator` to implement `codex-exploration-loop` as a local skill.
- Sync it to the registered skills storage repo after validation.
- Add one lab experiment under `experiments/` to test the Standard mode.
