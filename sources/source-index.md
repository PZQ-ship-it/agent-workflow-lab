# Source Index

Status: seed
Last updated: 2026-06-24

Use this file for public links worth reading or testing. Prefer primary sources and runnable examples.

## Queue

| Date added | Topic | Source | Claim to inspect | Status |
|---|---|---|---|---|
| 2026-06-24 | Skills | TBD | When is a reusable skill better than project docs? | todo |
| 2026-06-24 | Harness | TBD | What makes an agent harness repeatable? | todo |
| 2026-06-24 | Loop | TBD | Which loop patterns reliably improve output quality? | todo |
| 2026-06-24 | Exploration loop | Tree of Thoughts paper and repo: https://arxiv.org/abs/2305.10601 / https://github.com/princeton-nlp/tree-of-thought-llm | Generate -> evaluate -> select frontier for deliberate search. | inspected-local-repo |
| 2026-06-24 | Exploration loop | Reflexion paper and repo: https://arxiv.org/abs/2303.11366 / https://github.com/noahshinn/reflexion | Verbal reflection after failed/partial trials as reusable run memory. | inspected-local-repo |
| 2026-06-24 | Exploration loop | Voyager paper, project, and repo: https://arxiv.org/abs/2305.16291 / https://voyager.minedojo.org/ / https://github.com/MineDojo/Voyager | Automatic curriculum, executable skill library, and environment-feedback-driven open-ended exploration. | inspected-local-repo |
| 2026-06-24 | Skill packaging | OpenAI Codex Skills: https://developers.openai.com/codex/skills | Whether the exploration loop should become a reusable Codex skill package. | source-linked |
| 2026-06-24 | Harness support | OpenAI Codex Subagents: https://developers.openai.com/codex/subagents | Whether branch-parallel exploration can use native subagents and what approval/sandbox inheritance implies. | source-linked |
| 2026-06-24 | Harness support | OpenAI Codex Configuration Reference: https://developers.openai.com/codex/config-reference | Which sandbox, approval, skill, and agent-thread controls constrain exploration-loop execution. | source-linked |
| 2026-06-24 | Harness support | OpenAI Codex Automations: https://developers.openai.com/codex/app/automations | Whether time-driven or recurring exploration should be handled as a skill-only behavior or an automation/runner layer. | source-linked |
| 2026-06-24 | Harness support | OpenAI Codex SDK and App Server: https://developers.openai.com/codex/sdk / https://developers.openai.com/codex/app-server | Whether long-running or programmatic exploration needs an external trusted runner. | source-linked |
| 2026-06-24 | Harness support | OpenAI Codex CLI Reference: https://developers.openai.com/codex/cli/reference | Whether scripted exploration rounds should use `codex exec`, JSON events, output schemas, profiles, sandbox flags, and resume instead of a custom worker loop. | source-linked |
| 2026-06-24 | Harness support | OpenAI Codex Customization: https://developers.openai.com/codex/concepts/customization | Whether skills should remain the authoring format and plugins the distribution unit. | source-linked |
| 2026-06-24 | Claude workflows | TBD | How do Claude project/workflow patterns differ from Codex? | todo |

## Source Quality Notes

- Prefer official docs, public repos, issue discussions, postmortems, and reproducible demos.
- Treat social posts as leads unless they include code, traces, or concrete examples.
- Record the date when a claim is version-sensitive.
