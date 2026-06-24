# AGENTS.md

## Language

- 默认用中文沟通；代码、命令、API 名称保留英文。
- 面向公开仓库写作时，优先使用简洁英文或中英混排，但不要暴露个人路径、账号、token、cookie、API key。

## Repository Role

- 本仓库用于观察、理解和测试 Codex / Claude / agentic coding 工具的新用法。
- 关注对象包括但不限于：skills、agents、subagents、harness、loop、hooks、MCP、eval、prompt/workflow patterns。
- 仓库是 public；所有记录默认可公开，私密实验数据和凭据不得入库。

## Working Style

- 新发现先落到 `sources/` 或 `notes/`，再抽象到 `maps/`。
- 新测试先写最小实验记录，再决定是否沉淀成 harness 或 reusable workflow。
- 区分事实、推测、体验判断和待验证问题。
- 版本敏感结论需要写明日期、来源链接或本地验证命令。

## Safety

- 不提交 `.env`、token、cookies、账号凭据、私有聊天记录、付费内容全文或个人敏感信息。
- 如果需要复现实验，优先使用公开样例、合成数据和可公开日志。
- 不把其他仓库的大段私有内容复制进来；只记录公开链接、摘要和自己的测试结论。

## Verification

- 修改后至少运行 `git status --short --branch`。
- 涉及脚本或 harness 时，优先添加可重复执行的最小命令，并记录验证结果。
