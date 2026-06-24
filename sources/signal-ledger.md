# Agent Workflow Signal Ledger

Status: first scout
Last updated: 2026-06-24

This ledger tracks public signals about how people use Codex, Claude Code, and adjacent coding-agent harnesses. It separates source type from confidence: official docs and first-party blogs explain intended design; forums, Zhihu, Xiaohongshu, WeChat, and HN show adoption, vocabulary, pain points, and folk workflows.

## Channel Status

| Channel | Route used | Status | Notes |
|---|---|---|---|
| Official / primary web | AnySearch + RSS | usable | Strongest lane for concepts and feature boundaries. |
| Zhihu | authenticated `zhihu-mcp` | usable | High-density Chinese long-form articles; good for taxonomy and local practice patterns. |
| Xiaohongshu | `xhs-explore` Chrome bridge | usable with caveat | Basic search worked; filtered search failed because page DOM changed. Keep low-volume. |
| WeChat public articles | AnySearch `site:mp.weixin.qq.com` discovery | discovery only | Good for finding public article URLs; full article extraction needs URL-specific tooling and copyright-aware summaries. |
| Hacker News | official Algolia API via `early-signal-intel` | usable | Strong for engineering diffusion and Show HN harness projects. |
| Reddit / foreign forums | AnySearch discovery | discovery only | Search snippets found relevant discussions; direct Reddit detail capture not run in this pass. |
| Chinese AI media | public homepage capture + AnySearch | partial | Public pages were broad and not topic-specific; use targeted URLs next. |

## Primary / Official Signals

| Source | URL | Signal |
|---|---|---|
| OpenAI, Harness engineering | https://openai.com/index/harness-engineering/ | Frames Codex use as environment design, intent specification, and feedback loops rather than one-off prompting. |
| OpenAI, Codex harness / App Server | https://openai.com/index/unlocking-the-codex-harness/ | Positions Codex as a shared harness behind multiple surfaces, with shell/file tools, sandboxing, MCP, and skills participating in the loop. |
| OpenAI Developers, Agent Skills | https://developers.openai.com/codex/skills | Treats skills as packaged task-specific instructions, resources, and optional scripts for Codex. |
| OpenAI Developers, Subagents | https://developers.openai.com/codex/subagents | Defines project/user-scoped custom agents and spawned sessions with separate configuration. |
| OpenAI Cookbook, agent improvement loop | https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop | Shows an eval/trace-driven improvement flywheel where feedback becomes evals and harness changes. |
| Anthropic, Claude Code extension surface | https://code.claude.com/docs/en/features-overview | Gives the Claude-side vocabulary: `CLAUDE.md`, skills, subagents, hooks, MCP, plugins, and code intelligence. |
| Anthropic blog, steering Claude Code | https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more | Presents multiple control layers for Claude Code behavior and when to use them. |
| Martin Fowler, harness engineering | https://martinfowler.com/articles/harness-engineering.html | Useful neutral framing: agent = model + harness; the outer harness improves first-pass success and self-correction. |

## Chinese Long-Form Signals

| Source | URL | Signal |
|---|---|---|
| Zhihu: AI-Infra-Auto-Driven-SKILLS | https://zhuanlan.zhihu.com/p/2042740770457772060 | Strong concrete example of cross-Codex/Claude `SKILL.md` workflows for AI infra benchmark, profiler, SOTA loops, and incident triage. |
| Zhihu: Agent Harness from Learn Claude Code | https://zhuanlan.zhihu.com/p/2038602261274810271 | Explains harness as tools + knowledge + observation + action interfaces + permissions; highlights loop, task system, subagents, context compact, team protocol, worktree isolation. |
| Zhihu: Codex harness engineering summary | https://zhuanlan.zhihu.com/p/2025539662488315010 | Chinese synthesis of Codex harness concepts: AGENTS.md, skills, subagents, hooks, long-horizon tasks, durable project memory. |
| Zhihu: Claude Code / Codex process workflows | https://zhuanlan.zhihu.com/p/2050637986371523099 | Signal that everyday creators are turning agent use into repeatable media/content workflows, not only coding workflows. |
| Zhihu: Claude Code extension mechanisms | https://zhuanlan.zhihu.com/p/2010113968333668931 | Local Chinese explanation of Claude Code MCP, hook, skill, subagent, and plugin mechanisms. |

## Xiaohongshu Signals

| Note title | Author | Engagement snapshot | Signal |
|---|---|---|---|
| Claude规划 Codex执行 我的新工作流 | 零一界 01-Lab | 508 likes / 790 collects / 52 comments | A popular folk pattern: Claude plans, Codex executes. Worth testing as a two-agent workflow. |
| 我的 Claude + Codex 自动化协作工作流 | LoneRanger | 593 likes / 1107 collects / 84 comments | Strong adoption signal for combining the two tools into an automation workflow. |
| 双持AI：Claude Code + Codex = AI GOD! | 富贵托肯 | 392 likes / 635 collects / 36 comments | "Dual wielding" is a recurring Chinese social-platform framing. |
| /goal 和 /loop，到底哪个更卷啊 | 硅基解码 Decoder Only | 237 likes / 341 collects / 27 comments | `goal` and `loop` are visible enough to become comparison vocabulary. |
| 用 Codex 调度其他AI来自动化你的工作日常 | 赛博味儿酒咖 | 32 likes / 47 collects / 3 comments | Early signal around Codex as an orchestrator, not just a coding assistant. |
| Claude Code 监工让 Codex 连续工作8小时 | Feiskyer | 73 likes / 132 collects / 3 comments | Long-running supervision is becoming a social-media use case. |

## WeChat / Chinese Public Article Discovery

| Source | URL | Signal |
|---|---|---|
| Codex and Claude Code practical comparison | https://mp.weixin.qq.com/s/NPzwT-5_qt9ncWxYaaQpYg | Public WeChat article comparing tool positioning and workflow fit. |
| Claude Skills complete guide | https://mp.weixin.qq.com/s/x9UpqjuYzLb7I2ZZ932bNg | Public WeChat article focused on skills vs MCP vs subagents. |
| Ruanyf weekly issue: Claude Code Skills and Subagents practice | https://github.com/ruanyf/weekly/issues/8442 | Chinese developer-community pointer to practical skill/subagent notes. |
| Guyuehome Claude Code practice guide | https://www.guyuehome.com/wap/detail?id=2043185571431477249 | Chinese secondary source on Claude Code practice, research automation, and production configuration. |

## Foreign Forum / HN Signals

| Source | URL | Signal |
|---|---|---|
| HN: Claude 3.7 Sonnet and Claude Code | https://news.ycombinator.com/item?id=43163011 | Large discussion volume around Claude Code's initial public positioning. |
| HN: OpenAI Codex CLI | https://news.ycombinator.com/item?id=44006398 | HN discussion around OpenAI Codex as a terminal coding agent. |
| HN: Zot coding-agent harness | https://www.zot.sh | Show HN signal that people are building their own harnesses around coding agents. |
| HN: Pu.sh coding-agent harness in shell | https://pu.dev/ | Minimal harness signal: small shell implementation with tools, compaction, checkpoint/resume, tests. |
| HN: VAEN portable coding-agent harnesses | https://github.com/sjhalani7/vaen | Packaging and portability signal: share skills, MCP servers, and harness setup as artifacts. |
| HN: Relaymux tmux meta-harness | https://github.com/mupt-ai/relaymux | Local orchestration signal: tmux/worktree/subagent coordination over CLI agents. |
| Reddit: Claude Code full stack discussion | https://www.reddit.com/r/ClaudeAI/comments/1osu1f8/understanding_claude_codes_full_stack_mcp_skills/ | Discovery signal for community confusion and taxonomy demand. |
| Reddit: Claude plans, Codex executes | https://www.reddit.com/r/ClaudeCode/comments/1tjb36w/claude_code_plans_codex_executes_anyone_else/ | Cross-tool orchestration pattern echoed outside Chinese platforms. |

## First-Round Interpretation

- The center of gravity is shifting from "which model writes better code" to "which harness gives the model the right memory, tools, verification, and delegation boundaries."
- `skill` is becoming the portable SOP unit: useful when a repeated workflow needs instructions, references, and sometimes deterministic scripts.
- `harness` is the environment around the model: tool surface, permissions, state, compaction, evals, sandboxes, worktrees, and feedback loops.
- `loop` is not just repetition; it needs an exit condition, evidence, and state. Social platforms are already comparing `/goal`, `/loop`, and long-running supervision patterns.
- `subagent` is mainly about context isolation and specialization. Parallelism is a benefit, but the deeper value is keeping exploratory work out of the main context.
- Chinese social platforms emphasize practical recipes and tool-combination workflows; HN emphasizes implementation minimalism, portability, and harness design tradeoffs.

## Follow-Up Queue

1. Read official OpenAI and Anthropic pages directly and update `maps/taxonomy.md` with source-backed definitions.
2. Turn the "Claude plans, Codex executes" pattern into a small experiment.
3. Inspect HN harness projects: Zot, Pu.sh, VAEN, Relaymux, LiteHarness.
4. Extract one WeChat article at a time only when needed; summarize sparingly with URL citation.
5. Use Xiaohongshu detail fetch for 2-3 high-signal notes, but do not bulk capture comments.
