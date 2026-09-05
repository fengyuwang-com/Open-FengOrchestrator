# Open-FengOrchestrator — 董事长舰队：AI 指挥 AI 编程编排方案（Open 版）

> 开源 · 模型中立 · 真·AI 指挥 AI 编程 · 多 coding agent 舰队编排
>
> 定位：**纯研究与计划仓库**（不做实际部署，提供选型依据 + 落地蓝图）

---

## 这是什么

在「开源 + 多模型兼容 + 真·AI指挥AI编程(上层发战略目标、下层多个独立 coding agent 各干各的、你只审批签字)」这个交叉点上，
调研 40+ 开源项目后给出的**结论与落地方案**。

### 使用者画像（董事长）
- 只发**一句战略目标**；
- 不写编程指令、不拆任务、不审 diff、不点"运行"；
- 最多在**审批单上签字**。

### 舰队棋子（锁定）
Claude Code ｜ Codex CLI ｜ OpenCode ｜ Hermes ｜ OpenClaw(可选) ｜ Z Code(可选)

> 明确**不需要**：Gemini CLI、Aider、OpenHands。

---

## 文档导航

| 文件 | 内容 |
|---|---|
| [`docs/选型与研究.md`](docs/选型与研究.md) | 40+ 项目调研清单、排名、判断依据、被淘汰项 |
| [`docs/落地方案.md`](docs/落地方案.md) | 目标机器实施蓝图、里程碑、风险与备选 |
| [`docs/部署与使用方案.md`](docs/部署与使用方案.md) | 董事长视角使用蓝图：角色图解、本机实况、首期用 Hermes 验证手感 |
| [`docs/舰队各司其职.md`](docs/舰队各司其职.md) | **角色分工编排**（2026-08-16 实测）：6 个内置角色、assign/handoff/send_message 三机制、supervisor 指挥 vs workflow 流水线两条路线、自定义角色写法 |
| [`skills/cao-fleet/`](skills/cao-fleet/) | **自研 skill（随本仓库开源）**：CAO 舰队召唤（SKILL.md + cao_fleet.sh + agents.yaml）。实际使用位置在 `~/.zcode/skills/cao-fleet/`（ZCode 调用），本目录为版本管理副本，改动后需同步两边 |

---

## 一句话结论

> 用 **`awslabs/cli-agent-orchestrator`** 做骨架，
> 配内置 **`code_supervisor`** 首席协调（自动拆解 → 并行 assign → handoff 归集结果），
> 舰队 = Claude Code / Codex / OpenCode / Hermes，
> 你只当董事长发目标＋签审批单。

---

## 状态

✅ 调研完成　✅ 选型锁定　🔄 本机首期：用 Hermes 验证「董事长→CEO→干事」手感　⬜ 目标机器部署

_日期：2026-08-15 ｜ 骨架版本：cli-agent-orchestrator v2.4.1 ｜ 许可证：AGPL-3.0 (GNU Affero General Public License v3.0)_
