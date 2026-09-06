# agency-agents-zh：人才库 + 组织手册对接方案

> **本文为研究过程存档，现行架构见 [../达成目标架构蓝图.md](../达成目标架构蓝图.md)（架构总纲）。** 2026-08-24 移档。

> 2026-08-23 ｜ 基于 WSL `/opt/agency-agents-zh/` 源码级阅读（NEXUS 手册、strategy 目录、README/UPSTREAM）+ 同类开源项目格局对比
> 本文回答两个问题：**① agency-agents 到底是什么；② 它如何补上愿景里"组织设计 + 人才库"两块空白**

---

## 〇、先澄清一个误会

上一轮我把 agency-agents 当成"一个可选的提示词零件库"来评审（[prompt-quality-review.md](prompt-quality-review.md)、[agency-roles-evaluation.md](agency-roles-evaluation.md)），结论是"三分之一精品、三分之二套壳、挑 8-10 个入队"。

**这个判断只对了一半，且漏掉了最大价值。**

agency-agents 其实是两个东西的合体：
1. **人才库**：275 个即插即用的专业 AI 人格（system prompt）；
2. **组织手册**：`strategy/` 目录里一整套 **NEXUS 运营体系**（七阶段流水线、指挥结构、质量门禁、交接模板、编制模式）。

第 2 项正是愿景文档里写的"组织设计没人替我们做"那块空白的**现成答案**。我们之前完全没用它。

---

## 一、agency-agents 本体

### 1.1 来源与构成
- **上游**：`msitarzewski/agency-agents`（英文原版），MIT 协议。
- **中文社区版**：`jnMetaCode/agency-agents-zh`，在完整翻译上游 215 个的基础上，**新增 60 个中国原创角色**（小红书/抖音/微信/飞书/钉钉/政务ToG/医疗合规/畜禽养殖档案等垂直领域），共 **275 人格 + 16 份方法论**。
- **姊妹项目**：`jnMetaCode/agency-orchestrator`（零代码 YAML 多角色编排引擎，200+ 角色库，2.1k★，Apache-2.0）—— 一句话→多角色协作计划。

### 1.2 角色库质量（复核上一轮结论）
- 每个角色文件 = `frontmatter(name/desc/emoji/color)` + **身份与记忆** + **核心使命** + **关键规则** + **技术交付物（真实模板/代码/YAML）** + **工作流程**。质量**普遍很高**，可直接当 system prompt。
- **本土化是真增量**：招聘（Boss直聘/猎聘）、合同（《民法典》/e签宝）、抖音/小红书/知乎/B站/私域、微信小程序、钉钉/飞书集成 —— 这些是国内业务舰队的稀缺弹药。
- 上一轮"套壳"判断成立的范围：**工程/测试/客服类的英文模板翻译填充件**（结尾"参考你的核心训练"、方法论空泛）——这部分确实不如自己写任务简报。

---

## 二、被我们忽略的宝藏：`strategy/` = 组织手册（NEXUS）

> 这是本文最重要的发现。以下全部来自 `/opt/agency-agents-zh/strategy/` 逐字阅读。

### 2.1 NEXUS 七阶段流水线
```
发现 → 策略 → 基础搭建 → 构建 → 加固 → 上线 → 运营
（每个阶段之间都有质量门禁；阶段内部有并行轨道；每个边界有反馈循环）
```
- 第 0 阶段发现：趋势研究员、反馈分析师、UX 研究员、数据分析师、法务合规员、工具评估师
- 第 3 阶段构建：**开发-测试循环**（开发者实现 → 证据收集者测试 → 通过/不通过），最多重试 3 次后升级
- 第 4 阶段加固：现实检验者 + 性能基准 + API 测试 + 法务合规

### 2.2 指挥结构（对照愿景的"董事长→CEO→专业AI"）
```
        智能体编排者（流水线控制器 / 专项部门）
           │
   ┌───────┼───────┐
工作室制片人  项目牧羊人  高级项目经理
（组合管理） （执行协调） （任务拆分）
           │
   各部门负责人（工程/设计/营销/产品/QA）
```
**这与愿景的"董事长→CEO→专业AI人士"几乎同构**——只是 NEXUS 把"CEO 层"拆成了三个协作者（制片人/牧羊人/项目经理），比单一 CEO 更贴近真实运作。

### 2.3 三种编制模式（直接回答"数百 AI 员工怎么编"）
| 模式 | 活跃智能体 | 适用 | 时间线 |
|------|-----------|------|--------|
| **NEXUS-Full** | 全部 | 完整产品生命周期 | 12-24 周 |
| **NEXUS-Sprint** | 15-25 | 功能/MVP | 2-6 周 |
| **NEXUS-Micro** | 5-10 | Bug/活动/单一交付物 | 1-5 天 |

→ 印证了愿景文档的判断：**角色库数百、在编数十、并发十位以内、按需召唤**。

### 2.4 交接模板 + QA 反馈循环（直击三大痛点之一）
NEXUS 把"73% 的失败发生在交接边界"作为头号发现，给出标准化交接文档（元数据/上下文/交付要求/质量预期/下一接收方）+ QA 不通过反馈格式 + 升级协议。
**这正是"agents 不知道怎么组织、不知道怎么协作"的可落地解法——不是我们要自己写，是 NEXUS 已经写好了。**

### 2.5 现成的"激活提示词"
`strategy/coordination/agent-activation-prompts.md` 里是复制即用的激活提示词（智能体编排者、开发-测试循环、各部门负责人），每个阶段该激活谁、按什么顺序、质量门禁怎么卡，全部模板化。

---

## 三、同类开源格局（为什么最终还是它最贴）

| 项目 | 人才库 | 组织手册 | 中国本地化 | 真实 CLI 指挥 | 结论 |
|------|--------|----------|-----------|--------------|------|
| **agency-agents-zh** | ✅ 275 | ✅ NEXUS 全套 | ✅ 深 | ❌ 仅 prompt | **人才库+组织手册全集，唯一** |
| **agency-orchestrator** | ✅ 200+ | ⚠️ YAML 流程 | ✅ 同源 | ✅ 零代码 YAML | 编排引擎，可互补 |
| VoltAgent subagents | ✅ 158+ | ⚠️ 仅 meta-orch 类 | ❌ 纯英文 | ⚠️ Claude Code 插件 | 开发场景，无组织手册 |
| OneManCompany | ⚠️ 概念 | ⚠️ agent OS 概念 | ❌ | ⚠️ 演示 | 概念贴合但偏 demo |
| ChatDev / MetaGPT | ⚠️ 内置角色 | ✅ 软件公司模拟 | ❌ | ❌ 框架自建 | 不做真实 CLI 指挥 |
| awslabs/cli-agent-orchestrator（已锁定） | ❌ 仅 6 内置 | ⚠️ supervisor/worker | ❌ | ✅ **真指挥外部 CLI** | **编排执行层，不可替** |

**关键分工**：
- **CAO** = 编排执行层（真·指挥 Claude/Codex/OpenCode/Hermes 舰队）—— 已锁定，不换；
- **agency-agents-zh** = 人才库 + 组织手册（NEXUS）—— 补"组织设计 + 人才"空白；
- **agency-orchestrator** = 可选的零代码 YAML 入口（董事长一句目标→计划），与 CAO 互补而非替代。

---

## 四、对接架构：agency-agents 怎么进现有舰队

```
董事长（唯一真人）
   │ 一句目标
   ▼
[agency-orchestrator / ZCode]  ── 目标拆解 + 派单（CEO 层）
   │ 引用 NEXUS 指挥结构 + 编制模式
   ▼
[NEXUS 组织手册]  ── 阶段流水线 / 质量门禁 / 交接模板（组织纪律）
   │
   ▼
[agency-agents-zh 角色库]  ── 按部门挑在编专业 AI（人才库）
   │
   ▼
[CAO cli-agent-orchestrator]  ── 真·spawn 外部 CLI 干活（执行层）
   │ assign/handoff/send_message
   ▼
各 provider 棋子（Claude/Codex/OpenCode/Hermes）
```

**落点**：
1. **人才库**：用 `convert_to_cao.sh`（先修 MIT 署名缺口，见 [agency-roles-evaluation.md](agency-roles-evaluation.md) ④）把 NEXUS 角色转成 CAO profile，按"在编数十"原则精选，不堆 275。
2. **组织手册**：把 NEXUS 的指挥结构 + 七阶段流水线 + 交接模板，写进 ZCode（主/秘书）的 playbook，作为它拆解目标时的"组织纪律"——而不是每次现想。
3. **编制模式**：对应路线图四阶段——阶段一用 NEXUS-Micro（5-10 人小实战），阶段四用 NEXUS-Full（数百按需召唤）。

---

## 五、修正上一轮的偏差

| 上一轮说法 | 修正 |
|-----------|------|
| "挑 8-10 个精品入队，工程类套壳别要" | 角色素材的评审仍成立，但**低估了 strategy/ 组织手册的价值**——那才是和愿景最贴的部分 |
| "agentgate/Mem0 等是推荐引的零件" | 这些仍是"补药"，但**主菜是 agency-agents 全套**（人才+组织），优先级应反过来 |
| 把 agency-agents 当"候选零件库之一" | 它是**唯一同时覆盖人才库+组织手册的开源项目**，应作为愿景的"公司底座"而非可选零件 |

---

## 六、下一步（2026-08-23 进度更新）

1. ~~研读 NEXUS 全文~~ ✅ 已完成：NEXUS 手册已落成 `docs/CEO-Playbook-v0.md` + Skill 化 `skills/cao-ceo/SKILL.md`
2. **修 convert 脚本署名**：MIT 署名缺口仍在（董事长指示留待统一处理，见 [../agency-roles/导入清单.md](../agency-roles/导入清单.md)）
3. ~~选编制模式打首战~~ 🟡 就绪待打：cao-ceo Skill 已建，调它即走 NEXUS-Micro——这是当前唯一主待办
4. **评估 agency-orchestrator**：看其零代码 YAML 是否能直接做"董事长一句目标"入口——注：cao-ceo Skill 已承担该入口职能，此项降级为可选参考

> 补充：本文写作时角色库方案还是"精选 ~45"；后按董事长指示改为**全量入编 263**（不评判不剔除），详见 [../agency-roles/导入清单.md](../agency-roles/导入清单.md)。

---

_关联文档：[愿景与路线图.md](愿景与路线图.md) ｜ [agency-roles-evaluation.md](agency-roles-evaluation.md) ｜ [prompt-quality-review.md](prompt-quality-review.md) ｜ [舰队各司其职.md](舰队各司其职.md)_
