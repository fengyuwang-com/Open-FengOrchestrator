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
| [`docs/愿景与路线图.md`](docs/愿景与路线图.md) | **最高纲领**（2026-08-23）：一位真人 + 数百 AI 员工、AI 带领 AI（董事长→CEO→专业 AI 人士）、三大痛点、开源栈满足度评估、四阶段路线 |
| [`docs/达成目标架构蓝图.md`](docs/达成目标架构蓝图.md) | **架构总纲**（2026-08-24，两份蓝图合并）：五层系统（意图/组织/人才/执行/保障）、人才库建设战略（三条供应链+HR 五步入编流水线+淘汰机制）、复用白名单+组织级参照（OneManCompany 等）、"保障层 4/5 原生已覆盖"拆穿结论 |
| [`docs/选型与研究.md`](docs/选型与研究.md) | 40+ 项目调研清单、排名、判断依据、被淘汰项 |
| [`docs/落地方案.md`](docs/落地方案.md) | 目标机器实施蓝图、里程碑、风险与备选 |
| [`docs/部署与使用方案.md`](docs/部署与使用方案.md) | 董事长视角使用蓝图：角色图解、本机实况、首期用 Hermes 验证手感 |
| [`docs/舰队各司其职.md`](docs/舰队各司其职.md) | **角色分工编排**（2026-08-16 实测）：6 个内置角色、assign/handoff/send_message 三机制、supervisor 指挥 vs workflow 流水线两条路线、自定义角色写法 |
| [`docs/archive/agency-agents-人才库与组织手册对接.md`](docs/archive/agency-agents-人才库与组织手册对接.md) | 研究过程存档（2026-08-24 归档）：agency-agents-zh 深挖——275 人才库 + NEXUS 组织手册的对接研究，结论已并入架构总纲 |
| [`docs/CEO-Playbook-v0.md`](docs/CEO-Playbook-v0.md) | **CEO 层作战手册**（2026-08-23）：NEXUS 可执行化——5 步标准动作、三编制选择、七阶段裁剪、质量门禁、NEXUS 交接模板 |
| [`skills/cao-ceo/SKILL.md`](skills/cao-ceo/SKILL.md) | **董事长指挥层 Skill**：一句话目标 → 自动按 NEXUS 调兵遣将（判编制→拆阶段→召唤→卡门禁→回报），复用 cao-fleet，召唤时自动注入知识源（docs/ + FENGMEM.md），验收 spawn reviewer 打分，审批在回路直接问董事长 |
| [`skills/cao-fleet/`](skills/cao-fleet/) | **自研 skill（随本仓库开源）**：CAO 舰队召唤（SKILL.md + cao_fleet.sh + agents.yaml）。实际使用位置在 `~/.zcode/skills/cao-fleet/`（ZCode 调用），本目录为版本管理副本，改动后需同步两边 |
| [`agency-roles/导入清单.md`](agency-roles/导入清单.md) | **人才库导入记录**（2026-08-23）：263 profile 全量装入（19 部门零剔除）、86 个【在编】核心标记、部门分布、MIT 署名已全量修复 |

---

## 一句话结论

> 执行层 = **`awslabs/cli-agent-orchestrator`**（真·指挥外部 CLI 舰队，实测 $0.0095/场）；
> 人才库 = **agency-agents-zh** 全量 263 profile 入编 CAO（86 个【在编】核心）；
> 组织层 = **NEXUS 手册**（七阶段/质量门禁/交接模板）落成 **CEO Playbook + cao-ceo Skill**；
> 保障层 = 审批在回路 / 记忆 Code+FENGMEM / 通知 poller / 验收 reviewer agent —— **4/5 原生已覆盖，唯一缺口知识供给已在 Skill 里解决**。
> 你只当董事长发一句目标＋签审批单。

---

## 状态

✅ 调研完成　✅ 选型锁定　✅ 人才库 263 全量入编（MIT 署名已全量修复，2026-08-23）　✅ 五层架构成型（cao-ceo Skill 一句话触发）
🔄 当前：用 cao-ceo Skill 打一场真实 Micro 小实战，验证「一句话→调兵→干完回报」整条链路

_日期：2026-08-23 ｜ 执行层骨架：cli-agent-orchestrator v2.4.1 ｜ 许可证：AGPL-3.0 (GNU Affero General Public License v3.0)，角色派生部分 MIT（见 [`agency-roles/NOTICE.md`](agency-roles/NOTICE.md)）_
