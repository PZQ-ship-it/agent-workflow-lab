# 本地 Skills 的 Goal 机制候选清单

日期：2026-06-24

这里的 goal 机制指 Codex `/goal` 式的长期目标约束：明确 objective、持续推进、记录状态、遇到可恢复失败继续尝试、在真正完成或连续阻塞后才标记完成/blocked。它适合有状态、有验证、有批处理或多阶段闭环的 skill；不适合纯咨询、纯写作或必须频繁等人确认的 skill。

## 判断标准

- 强候选：已有 manifest/status/checkpoint、批处理、可恢复执行、自动验证、QA 或 eval loop。
- 中候选：有阶段产物和验证，但存在强人类确认 gate；可以只把 goal 绑定到单一阶段。
- 弱候选：主要是规划、访谈、评论、写作、一次性检索；goal 价值有限，容易制造“假完成”。

## S 级：最值得优先引入

| Skill | 适合原因 | 建议 goal 边界 |
| --- | --- | --- |
| `resilient-llm-benchmark` | 本身就是 checkpoint、append-only results、retry/backoff、sharding、status manifest 的长任务。 | “完成某个 benchmark run 的全部 shard，并生成结果/失败清单/成本记录”。 |
| `skill-eval-optimizer` | static check、eval pack、trace、deterministic checks、rerun after patch，天然是测试-修复-复测闭环。 | “把目标 skill 从当前状态推进到 eval pack 通过，并留下 trace/summary”。 |
| `skill-product-evaluator` | 在行为 eval 外增加 benchmark/rubric、judge bundle、产品质量报告，适合多轮证据收集。 | “完成某 skill 的产品质量评估报告，含 benchmark mapping、cases、judge input bundle”。 |
| `scenario-agent-run-optimizer` | trace/log/prompt/tool/eval 到诊断和改进建议，适合 evidence-driven 优化循环。 | “从指定运行证据中定位失败原因，提出并验证最小改动”。 |
| `codex-completion-loop` | 已经是 native Codex 的完成闭环约束。 | 更适合作为 goal 机制的通用适配层，而不是单独业务 skill。 |

## A 级：很适合，但要尊重阶段 gate

| Skill | 适合原因 | 建议 goal 边界 |
| --- | --- | --- |
| `image-to-editable-ppt` | 有 deck/page manifest、page jobs、page result、repair queue、final validation。 | “完成一次图片/PDF 到可编辑 PPT 的 run，直到 final validation 或明确 page blocker”。 |
| `ppt-deck-build` | page-worker、work order、manifest、job status、finalize，非常适合 run-level goal。 | “完成已确认 storyboard/layout 后的 deck build draft”，不要跨到 render QA。 |
| `ppt-render-qa-loop` | PowerPoint render、截图、QA report、repair backlog，是标准视觉验收闭环。 | “完成 deck 的 render QA，并输出 pass/fail/needs_human_acceptance”。 |
| `manuscript-to-ppt-workflow` | 全流程很长且 gate 明确。 | 不建议一个 goal 跑完整 PPT；建议每个 stage 一个 goal。 |
| `academic-research-suite` | 有 workflow router、academic pipeline、experiment agent、integrity gate、state tracker。 | “推进当前研究阶段到下一个可验证 artifact/gate”。 |

## A-/B 级：适合检索、爬取、整理类 goal

| Skill | 适合原因 | 建议 goal 边界 |
| --- | --- | --- |
| `paper-review-source-intel` | 官方/公开源路由、manifest、证据语料、blocker 记录。 | “完成某主题/venue 的一批 first-source evidence corpus”。 |
| `code-model-benchmark-intel` | code/model/dataset/benchmark 多源收集，适合公开证据批处理。 | “完成某 repo/model/benchmark 的 normalized JSONL/CSV/Markdown report”。 |
| `conference-workshop-intel` | CFP、program、accepted papers、awards 等时效源，需要 crawl timestamp。 | “完成某会议/年份/主题的官方证据包与趋势摘要”。 |
| `early-signal-intel` | 早期讨论源、RSS/论坛/Reddit/Bluesky 等，需限量抓取和 manifest。 | “完成一次 bounded early-signal scan，记录 limits/blockers”。 |
| `chinese-ai-signal-crawler` | 中文媒体/公众号/B站/AnySearch 路由，天然需要状态和来源区分。 | “完成某主题的中文传播信号采集与主源交叉校验”。 |
| `zhihu-public-intel` | 有 auth loop、fallback、normalize outputs，容易被登录/验证码阻塞。 | “完成某话题的知乎公开样本采集，或明确 auth blocker”。 |
| `professor-direction-mapper` | 多源证据、学生 spine delegated lane、当前/历史方向判断。 | “完成一位老师的 direction map”；批量时每人一个子 goal 更稳。 |
| `ra-mainline-literature-orchestrator` | work orders、batch、status、artifact repo、merge results，非常适合批量 goal。 | “完成某 rank 范围的文献 work orders、下载/manifest/summary 合并”。 |

## B 级：适合加局部 goal

| Skill | 适合原因 | 建议边界 |
| --- | --- | --- |
| `paper-pdf-to-structured-html` | PDF 提取、渲染、figure/table recovery、manifest，可恢复性强。 | 单篇论文一个 goal；不要把整个 reading project 混成一个 goal。 |
| `latex-pdf-final-review` | compile、extract text、render pages、check refs/terminology/layout warnings。 | “完成一次最终审阅并给出 blocking/non-blocking list”。 |
| `thesis-figure-pipeline` | 数据到图、脚本、PNG/PDF、LaTeX sync、视觉 QA。 | “刷新一组图并验证论文页面渲染”。 |
| `codex-visual-acceptance` | screenshot/render evidence、视觉迭代。 | 作为 UI/PDF/figure goal 的验收子阶段。 |
| `paper-term-glossary-builder` | 可批量从论文/HTML 建 glossary，但完成标准需定义清楚。 | “覆盖指定论文/章节的术语表并完成去重/来源标注”。 |

## 不建议优先引入

| 类型 | 代表 skill | 原因 |
| --- | --- | --- |
| 访谈/澄清/规划 | `codex-deep-interview`, `scope-negotiator`, `codex-consensus-plan`, `assumption-auditor` | 主要价值来自人类选择，不适合自动持续推进。 |
| 写作模板 | `intro-drafter`, `tech-paper-template`, `benchmark-paper-template`, `research-proposal`, `academic-letter-architect`, `humanizer` | 多数是一次性生成或修订，goal 成本高于收益。 |
| 评审类 | `academic-paper-reviewer`, `project-design-reviewer`, `research-experiment-design-reviewer` | 可以输出 review artifact，但不应自动宣称问题已解决。 |
| 教学/陪练 | `guided-learning` | 人在循环里，goal 容易破坏节奏。 |
| 单次工具 | `screenshot`, `pdf` 的简单读取场景 | 一次性动作，不需要长期 goal。 |

## 建议改造顺序

1. 先改 `skill-eval-optimizer`：它可以反过来评估其他 skill 的 goal-mode 是否有效，是最好的元工具。
2. 再改 `resilient-llm-benchmark`：契约最清晰，能验证 checkpoint/resume/blocked 的语义。
3. 然后改 PPT page-worker 组：`image-to-editable-ppt`、`ppt-deck-build`、`ppt-render-qa-loop`，收益很高但必须严守 human gate。
4. 最后改情报/爬取类：统一 manifest、quota、auth blocker、source freshness 和 final synthesis 的完成定义。

## 推荐统一加入的段落

每个强候选 skill 可以新增一个 `Goal Mode` 小节，包含：

- `Objective shape`：goal 应该怎样写，粒度多大。
- `State artifact`：manifest/status/checkpoint 文件路径。
- `Progress loop`：每轮推进什么、何时验证、何时重试。
- `Completion criteria`：哪些文件、测试、报告存在才算 complete。
- `Blocked criteria`：连续遇到什么外部条件才允许 blocked。
- `Human gate`：哪些阶段必须停下来等用户确认，不能用 goal 自动跨过。
