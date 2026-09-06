# agency-agents-zh 开源角色库价值评估报告

> 评估对象：`/opt/agency-agents-zh/`（WSL Ubuntu-24.04，已克隆，MIT 协议）
> 评估日期：2026-08-23
> 评估方式：只读分析 + 抽样精读 22 个不同领域角色文件原文（非仅凭文件名）
> 结论先行：**推荐方案 B（精选扩充到 ≈45 个）**——见第 ③ 节。

---

## ① 总览与分类树

### 1.1 真实角色总量

- 库内标注：**275 个 AI 智能体人格**（AGENT-LIST.md，2026-08-21 更新），分 19 个部门。
- 目录实测：递归扫描得到约 291–317 个 `.md` 文件，差异来自：
  - `strategy/` 目录含约 16 份**编排方法论文档**（NEXUS 手册、playbooks、runbooks、coordination 模板），**不是独立 agent 人格**，不计入 275；
  - `examples/`、`cao_profiles/` 含已转换/示例副本；
  - `game-development/` 下 godot/unity/roblox/blender/unreal 子目录的引擎专属角色。
- 故**可作为"干活型 agent"导入的实际人格 ≈ 275 个**，另有约 16 份方法论（只读参考，不转 profile）。

### 1.2 分类树（按官方 19 部门 + 实测计数）

```
agency-agents-zh (≈275 人格 + 16 方法论)
├─ 工程部 Engineering (42)         ← 已导入 8 个（fe/be/arch/devops/ai/data/sec/code-reviewer）
├─ 安全部 Security (10)           ← 已导入 4 个（pen-test/compliance/appsec/sec-engineer）
├─ 设计部 Design (9)              ← 0 个（全新空白）
├─ 营销部 Marketing (42)          ← 已导入 2 个（xiaohongshu/zhihu）
├─ 付费媒体部 Paid-Media (7)      ← 0 个（全新空白）
├─ 销售部 Sales (9)               ← 0 个（全新空白）
├─ 金融部 Finance (9)             ← 0 个（全新空白）
├─ 人力资源部 HR (2)              ← 0 个（全新空白）
├─ 法务部 Legal (2)               ← 0 个（仅 compliance-auditor 同主题在安全部）
├─ 供应链部 Supply-Chain (5)      ← 0 个（全新空白）
├─ 产品部 Product (5)             ← 已导入 2 个（pm/sprint-prioritizer）
├─ 项目管理部 PM (7)              ← 0 个（全新空白）
├─ 测试部 Testing (9)             ← 0 个（仅 code-reviewer 同主题在已导入）
├─ 支持部 Support (7)             ← 0 个（全新空白）
├─ 专项部 Specialized (58)        ← 0 个（全新空白，含 C-level/垂直行业/编排者）
├─ 空间计算部 Spatial (6)         ← 0 个（全新空白）
├─ 游戏开发部 Game-Dev (20)       ← 0 个（全新空白，含引擎子目录）
├─ 学术部 Academic (6)            ← 0 个（全新空白）
├─ GIS 部 (13)                    ← 0 个（全新空白）
└─ 策略部 Strategy (≈16 方法论)    ← 非人格，不导入
```

### 1.3 质量观察（基于 22 份原文精读）

- 每个角色文件结构统一：`frontmatter(name/description/emoji/color)` + **身份与记忆** + **核心使命** + **关键规则** + **技术交付物（真实模板/代码/YAML）** + **工作流程**。质量**普遍很高**，是可直接作为 system prompt 使用的"能干活的"人格，而非空泛口号。
- 大量角色**针对中国场景深度本地化**：招聘（Boss直聘/猎聘）、合同（《民法典》/e签宝）、抖音/小红书/知乎/B站/私域、微信小程序、钉钉/飞书集成等——对国内业务舰队是稀缺增量。
- 交付物具体可落地（SEO 审计报告模板、抖音直播排品表、MEDDPICC 赢单评分、YARA 规则、SLO yaml、财务三表模型等），不是纯方法论。

---

## ② 与现有舰队对比

### 2.1 现有覆盖盘点

| 来源 | 角色 | 性质 |
|------|------|------|
| 已导入 15 | fe/be/software-arch/devops/ai/data/sec-engineer/code-reviewer、pen-tester/compliance-auditor/appsec-engineer、pm/sprint-prioritizer、xiaohongshu-operator/zhihu-strategist | 技术交付 + 产品 + 2 个中文社媒 |
| Hermes（通用干事） | 通用编程/执行，无专业纵深 | 万金油，但**不具领域方法论** |
| ZCode（主/秘书） | 规划、派单、协调 | 不亲自出专业活 |

### 2.2 各领域增益判断（"各司其职"真实增量）

**A. 完全空白、价值高（强烈建议补）—— 这些是舰队当前最大短板：**
- **设计**（UI/UX/Brand/图像提示词）：0 覆盖，产品与增长强依赖。
- **营销增长**（除小红书/知乎外的抖音/微信/B站/私域/SEO/内容/直播）：0 覆盖，董事长最关心的"出活获客"几乎全缺。
- **金融**（财务分析/税务/反欺诈/发票）：0 覆盖。
- **销售**（MEDDPICC 赢单/外呼/方案）：0 覆盖，B2B 变现缺。
- **法务**（合同审查/政策撰写）：仅 compliance 同主题，缺合同实操。
- **HR / 支持 / 测试（QA）/ 项目管理**：0 或仅边缘覆盖。

**B. 与 Hermes 重叠、需谨慎（避免重复造轮子）：**
- 通用编程类（senior-developer、rapid-prototyper、git-workflow-master、cms/wordpress/drupal 购物车、mobile-app-builder）：Hermes 已能覆盖大部分；仅当需**极致专业纵深/特定栈**（如 Three.js 高端前端、微信小程序、飞书/钉钉集成、嵌入式/FPGA）才值得单立。
- 多个"架构/架构师"变体（software-architect 已导入；backend-architect 已导入；security-architect、multi-agent-systems-architect、autonomous-optimization-architect 与已导入高度重叠）。

**C. 垂直/小众、与本舰队无关（建议排除）：**
- 游戏开发 20 个（godot/unity/unreal/roblox/blender）、空间计算 6 个（visionOS/XR/Metal）、GIS 13 个、学术 6 个。
- 专项部里的垂直业务人格：healthcare、real-estate、hospitality、livestock、loan-officer、grant-writer、travel-planner、gaokao/study-abroad advisor、french/korean market、C-level 高管（CTO/CFO/CMO/COO/CPO/CEO）等——这些是独立业务机器人，对"技术+增长"舰队价值低，且 C-level 与 ZCode 自身规划职能重叠。

### 2.3 干活型 vs 纯方法论型

- **干活型（≈95%）**：绝大多数角色可派任务直接产出（写代码、写方案、审合同、做 SEO 审计、策划抖音脚本）。可全部转 CAO profile。
- **纯方法论/非人格（≈5%）**：`strategy/` 整个目录（NEXUS 编排手册、playbooks、runbooks、coordination 模板）= 部署哲学，**不应转成单个 agent**，应作为 ZCode 的参考 playbook 阅读。
- 边界型：`specialized/agents-orchestrator`、`specialized/workflow-architect`、`multi-agent-systems-architect` 属"元编排"人格，对舰队有理论价值但易与 CAO 控制面本身职责打架，建议最多保留 1 个。

---

## ③ 推荐策略 + 具体名单

### 3.1 三方案对比与选择

| 方案 | 内容 | 判断 |
|------|------|------|
| **A 全量转 275** | 全部导入 | ❌ 臃肿：大量垂直/游戏/GIS/学术/小众人格永不触发；近义重复引发选错 agent；MIT 署名合规风险放大（见④）。**（后注：董事长最终裁决全量导入，本文推荐方案 B 作废；署名问题已于 2026-08-23 由脚本内置修复）** |
| **B 精选 ≈45** | 15 已导入 + ≈30 新高价值 | ✅ **推荐**：补齐舰队真实短板（设计/增长/金融/销售/法务/QA/支持），剔除重叠与小众，可控可维护。 |
| **C 维持 15** | 不扩 | ❌ 浪费已验证的优质资产；增长/设计/财务/销售等董事长高频需求无解。 |

**→ 推荐 B。理由**：库质量高但分布极不均（工程/营销/专项占多数且含大量重复与垂直噪音），舰队需要的是"补齐非工程职能"，而非"再堆工程变体"。精选 ≈45 能在不臃肿前提下，把单点技术舰队升级为"技术+产品+增长+职能"的完整舰队。

### 3.2 推荐纳入的具体名单（≈45，含已导入 15）

**一、已导入保留（15）**
`frontend-developer, backend-architect, software-architect, devops-automator, ai-engineer, data-engineer, security-engineer, code-reviewer, penetration-tester, compliance-auditor, application-security-engineer, (产品) product-manager, sprint-prioritizer, xiaohongshu-operator, zhihu-strategist`

**二、工程补强（新增 4，避开与 Hermes 重叠）**
- `engineering-sre`（站点可靠性，独立价值高）
- `engineering-prompt-engineer` **或** `specialized/prompt-engineer`（**二选一**，见④重复项）
- `engineering-multi-agent-systems-architect`（舰队编排相关，与 agents-orchestrator 二选一）
- `engineering-incident-response-commander`（运维事故指挥，可选）

**三、设计（新增 5，当前完全空白）**
- `design-ui-designer, design-ux-researcher, design-ux-architect, design-brand-guardian, design-image-prompt-engineer`

**四、营销增长（新增 9，当前仅 2 个社媒）**
- 旗舰平台：`marketing-douyin-strategist, marketing-wechat-official-account（或 wechat-operator）, marketing-bilibili-strategist`
- 通用能力：`marketing-content-creator, marketing-seo-specialist, marketing-growth-hacker, marketing-private-domain-operator（私域）, marketing-ecommerce-operator（或 china-ecommerce-operator）, marketing-livestream-commerce-coach`
- *说明：营销部 42 个里约 15 个是平台变体（抖音/小红书×2/知乎/B站/快手/微博/微信×2/TikTok/Instagram/LinkedIn/Reddit/Twitter/视频号），结构雷同；建议只保留 3–4 个董事长实际运营的旗舰平台 + 1 个通用内容创作者 + SEO + 增长黑客 + 私域 + 电商，避免 15 个近义 agent。*

**五、付费媒体（新增 2–3，按需）**
- `paid-media-ppc-strategist, paid-media-paid-social-strategist, paid-media-creative-strategist`（做投流时启用）

**六、销售（新增 3–4）**
- `sales-deal-strategist（MEDDPICC 赢单）, sales-outbound-strategist, sales-proposal-strategist, sales-coach`

**七、金融（新增 3）**
- `finance-financial-analyst, finance-tax-strategist（中国税务）, finance-fraud-detector（可选）`

**八、法务（新增 2）**
- `legal-contract-reviewer, legal-policy-writer`

**九、HR / 支持 / 项目管理（新增 3–4）**
- `hr-recruiter, support-support-responder, project-management-meeting-notes-specialist（或 jira-workflow-steward）, customer-success-manager（specialized）`

**十、测试 QA（新增 2–3，code-reviewer 已覆盖代码评审）**
- `testing-api-tester, testing-performance-benchmarker, testing-reality-checker`

**十一、专项精选（新增 2–3，剔除垂直噪音）**
- `specialized-mcp-builder`（舰队工具链相关，价值高）
- `specialized-workflow-architect`（或 automation-governance-architect）
- `data-privacy-officer` / `specialized-ai-policy-writer`（合规邻接，可选）

**明确排除（不纳入）：** 游戏开发 20、空间计算 6、GIS 13、学术 6、`strategy/` 方法论、专项部中 healthcare/real-estate/hospitality/livestock/loan/grant/travel/gaokao/study-abroad/french-korean-market 等垂直人格、C-level 高管系列（与 ZCode 规划职能重叠）。

> 以上新增约 30 个，加已导入 15，**合计 ≈45**，落在 30–50 目标区间。

---

## ④ 风险与成本

### 4.1 资源占用与冷启动
- **存储成本可忽略**：CAO agent profile 本质是 markdown（system prompt + 权限块），275 个也只占用几十 MB；"全量转"不会让系统变慢。
- **真实成本在"生成（spawn）"时**：每个 agent 冷启动 ≈60s + 走 opencode-go 模型网关的 token 消耗。因此"全量导入"的代价不是磁盘，而是**误用/滥用导致的 token 浪费与决策负担**。
- **结论**：反对 A 的主因不是算力，而是**（a）选 agent 时的认知负担、（b）近义重复导致派错人、（c）大量永不触发的僵尸 profile 增加维护与审计面**。

### 4.2 近义重复（实测确认，必须去重）
1. **小红书 ×2**：`marketing-xiaohongshu-operator` 与 `marketing-xiaohongshu-specialist` 同主题重复（已导入前者即可）。
2. **Prompt 工程师 ×2**：`engineering/engineering-prompt-engineer` 与 `specialized/prompt-engineer` 高度重叠——**只留 1 个**（`design-image-prompt-engineer` 是图像方向，可区分保留）。
3. **威胁检测 ×2**：`engineering-threat-detection-engineer` 与 `security-threat-detection-engineer` 重复——安全部已覆盖，二选一。
4. **SRE / 事故响应 / SecOps 重叠**：`engineering-sre`、`engineering-incident-response-commander`、`security-incident-responder`、`security-senior-secops` 职责交叉，建议最多保留 SRE + 1 个事故响应。
5. **销售 / 支持 / 社媒 集群内部**各自 5–9 个变体，结构雷同，均按"旗舰 + 通用"原则收敛。
6. **C-level 系列**（CTO/CFO/CMO/COO/CPO/CEO）互相近似且可由 ZCode 主 agent 承担，不单列。

### 4.3 MIT 协议合规（✅ 已于 2026-08-23 修复）
- 协议：`MIT License`，版权 `© 2025 Michael Sitarzewski（英文原版） / © 2026 jnMetaCode（中文翻译与本地化）`。
- MIT 要求：**"The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software."**
- ~~**当前 convert_to_cao.sh 的缺陷**：转换时只提取 `name/description/emoji` 并把正文（已剥离 frontmatter）写入 cao_profile，**完全丢弃了原作者署名与版权声明**。生成的 15 个 profile 里没有任何 MIT 署名——这违反 MIT 的署名保留条款。~~
- **已修复（2026-08-23）**：convert_all_full.sh 内置署名逻辑（正文顶部嵌上游仓库链接+双版权+派生说明），全量重新生成后双侧验证 260/260 零缺失；后续再生成自动携带，不会复发。详见 NOTICE.md 与 agency-roles/导入清单.md。

### 4.4 其他风险
- 部分角色内置中国平台/工具假设（Boss直聘、e签宝、抖音算法等），若董事长业务不涉国内社媒/招聘，则相关人格价值归零——名单已按"国内增长导向"预设，可按实际业务裁撤。
- 角色内容含示例代码片段与 `${VAR}` 占位符，已存在 CAO 环境变量扫描器的误报（`fix_placeholders.sh` 做了 `${X}→$X` 中和）；新增含变量的角色需复跑该修复。
- 语言：角色全中文，与舰队中文语境一致，无本地化额外成本。

---

## ⑤ 结论（一句话）

**推荐方案 B：在已导入 15 个基础上精选新增约 30 个高价值人格（重点是设计/营销增长/金融/销售/法务/QA/支持 + 少量工程与设计工具链专项），剔除游戏/GIS/学术/垂直行业与小众 C-level 等无关项及近义重复，并先修复 convert 脚本的 MIT 署名缺失后再扩量——用最小维护成本把"单点技术舰队"升级为"技术+增长+职能"的完整舰队。**
（后注 2026-08-24：董事长最终裁决为全量导入（方案 A 作废本文判断），署名问题已于 2026-08-23 修复；本报告保留作为评估过程记录。）
