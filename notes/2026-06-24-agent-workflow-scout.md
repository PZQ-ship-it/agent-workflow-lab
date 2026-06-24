# Agent Workflow Scout: First Cross-Channel Pass

Date: 2026-06-24
Status: first synthesis

## Goal

Start a public, evidence-backed map of how people are currently using Codex, Claude Code, and adjacent coding-agent tools around skills, harnesses, loops, subagents, hooks, MCP, and long-running workflows.

## RALPLAN-DR

Principles:

- Keep public notes clean: no secrets, cookies, platform tokens, full copied articles, or raw social-media dumps.
- Treat official docs as feature-grounding, and social platforms as adoption and vocabulary signals.
- Prefer small, repeatable channel probes over heavy crawling.
- Record blockers as data; do not force a brittle crawler path.

Decision drivers:

- This repo is public.
- The topic changes quickly, so first-pass artifacts should be updateable.
- The most valuable output is a source ledger plus experiment queue, not a giant pile of raw captures.

Viable options:

- Broad crawl first: maximizes recall, but risks noisy copyrighted data and platform-state leakage.
- Curated scout first: lower recall, but safer and easier to turn into a durable public map.

Decision:

- Use curated scout first. Keep raw captures local and ignored; publish a compact signal ledger and synthesis.

## What Was Searched

- AnySearch: official web, Claude/Codex workflow articles, WeChat discovery, foreign forum discovery.
- Zhihu MCP: authenticated keyword search and selected full article capture for high-signal Chinese long-form posts.
- Xiaohongshu crawler: low-frequency keyword search for Codex/Claude workflow notes.
- Chinese AI media helper: public page route tested; topic-specific AnySearch was used instead after a helper script compatibility bug.
- Early-signal helper: HN Algolia and RSS for OpenAI / Google research feeds.

## What We Learned

The main pattern is not "Codex versus Claude Code"; it is "how to build a reliable environment around coding agents." The recurring primitives are:

- persistent project rules: `AGENTS.md`, `CLAUDE.md`, project memory files;
- reusable procedures: `SKILL.md`, skills directories, templates, references, scripts;
- execution harnesses: tool dispatch, permissions, sandboxing, browser/terminal access, worktrees;
- state loops: todo systems, goals, background jobs, status files, eval/improvement loops;
- context isolation: subagents, reviewer agents, worktree-isolated tasks;
- verification: tests, benchmarks, traces, CI gates, formal specs, human acceptance criteria.

Chinese platforms are already packaging these as practical recipes:

- "Claude plans, Codex executes";
- "Claude + Codex automation workflow";
- `/goal` vs `/loop`;
- "do not use Codex/Claude naked";
- skill libraries for research, self-media, AI infra, and video workflows.

HN and foreign forums show a more implementation-heavy branch:

- minimal coding-agent harnesses;
- portable harness packaging;
- tmux/worktree orchestration;
- single-tool or few-tool harness experiments;
- concern over token efficiency, permissions, and context bloat.

## Channel Notes

Zhihu was the strongest Chinese long-form lane. It surfaced concrete repositories and workflows, especially AI-Infra-Auto-Driven-SKILLS and Learn Claude Code style harness pedagogy.

Xiaohongshu was useful for trend and adoption signals. Filtered search failed because the platform DOM changed, but the basic keyword search returned 44 notes. Do not rely on it for precise technical truth; use it to spot phrases and workflows worth verifying elsewhere.

WeChat was best used as public URL discovery in this pass. Full extraction should be URL-specific and copyright-aware.

HN was strong for open-source harness discovery. The immediate follow-up list is Zot, Pu.sh, VAEN, Relaymux, LiteHarness, and related Show HN threads.

AnySearch was useful after the user approved saving the generated key to the private user-level skill `.env`. The key is not stored in this repo.

## Next Experiments

1. **Two-agent handoff**: give Claude-style planning notes to Codex execution, then reverse the pairing. Measure handoff clarity, rework, and verification quality.
2. **Skill vs AGENTS.md**: encode the same small workflow as project rules, a skill, and a script-backed harness. Compare trigger reliability and maintenance cost.
3. **Harness minimalism**: clone or inspect a minimal harness project such as Pu.sh or Zot, then reproduce the core loop with a tiny local fixture.
4. **Loop exit conditions**: design a `/goal`-like long-running task with explicit stop rules, status file, and validation command.
5. **Subagent boundary**: split one review task into security, correctness, tests, and maintainability agents; compare with a single-agent review.

## Non-Goals

- No bulk reposting of social-media content.
- No private account data or raw cookies in the repo.
- No claim that one tool is universally better.
- No heavy crawler setup until the public source ledger proves a channel is worth deeper monitoring.
