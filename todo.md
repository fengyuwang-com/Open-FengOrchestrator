# FengOrchestrator — 待办（MVP 之后的后续项）

> 用途：MVP 先行，本文件收集所有"以后再做"的项，纳入 git 追踪，逐条勾选。
> 更新约定：每完成一项 → 勾选 `[x]` + 标注日期；新增项 → 追加，注明来源/理由。

---

## 已完成（MVP 之内）
- [x] 2026-08-15 文档：`docs/部署与使用方案.md` + README 导航/状态更新
- [x] 2026-08-15 本机 Hermes 配置改为 OpenCode Zen/go（`provider: custom` + `base_url` + `deepseek-v4-flash`），改前备份
- [x] 2026-08-15 单干事端到端试跑：Hermes 生成并运行 `hello_worker.py`，校验通过，返回归集
- [x] 2026-08-15 WSL(Ubuntu-24.04)：uv 0.12.5 + 克隆安装 cli-agent-orchestrator v2.4.1（commit c64c9fa），4 个 cao CLI 验证可跑
- [x] 2026-08-15 MVP：封装 `hermes -z` 为 ZCode 可调用命令，完成端到端验证
- [x] 2026-08-15 **webcli 网页命令行应用（Hermes 干事驱动）**：FastAPI/WS 后端 + 单页前端 + 冒烟验收；Hermes 全程担任后端审查/修复（4 处安全健壮性问题）、前端审查/修复（显示顺序）、最终端到端验收。详见 `webcli/`。
- [x] 2026-08-15 **Tailscale 网络基座确认**：本机 Tailscale 已运行（IP `100.101.102.103`），多台设备在线 → 远程/跨设备访问前提成立，后端默认安全绑定 `127.0.0.1`
- [x] 2026-08-16 **webcli Rust 单二进制重写（用户点名）**：axum + portable-pty(ConPTY) + xterm.js 真·交互式终端（可跑 python REPL / vim / opencode 等全屏 TUI）；R1 后端/R2 前端 Hermes 并行产出 + 主集成编译修错（axum API 适配、clippy 清零）；release 单 exe 已部署 FengCloud；移除 Python 版（单命令模式+高危拦截，git 历史可回滚）
- [x] 2026-08-16 **10 个 Hermes 并行实验（5 分钟限时）**：9/10 完成，墙钟 301s vs 串行估算 ~21.6min（加速比 ~4.3x）；结论：墙钟由最慢干事决定，>4 个 agent 收益递减（H4 benchmark 佐证）
- [x] 2026-08-16 **舰队问题修复（10 干事研究成果落地）**：hermes_z.sh 新增 `-s` 安全模式（临时 HERMES_HOME + 工具白名单）与 `-L` 任务/成本归集（logs/fleet/fleet.tsv 台账）；Hermes 接入 MCP filesystem server（14 工具，`mcp__filesystem__*` 前缀，docs/mcp.md）；CAO 控制面 API 已跑通（WSL localhost:9889，sessions/terminals/events/workflows 齐全）

---

## 待办（MVP 之后）

### 编排演进
- [ ] **三项目自主进化机制待激活**：FengInvest/FengMedia/FlyGo 已安装 MISSION.md+docs/自主进化机制.md（可撤销，删 MISSION.md 即停用）；待①董事长改写各项目 MISSION 总目标/DoD ②配置定时点火器投喂节拍 prompt 方才生效。
- [x] 2026-09-10 **自主进化第二轮深度研究（必须写代码吗）**：结论=写代码非必要条件，定案混合路线（文档层治理不变+补评分/任务生成/停止条件三个最小脚本件），已写入 docs/自主进化通用方案.md 第五节；三份桌面复盘已归档 docs/archive/（桌面原件移除）。
- [x] 2026-09-10 **自主进化通用方案**：桌面三份通宵复盘（FengInvest/FengMedia/FlyGo）已合并为 docs/自主进化通用方案.md，含联网调研的业界五要素对照与指示模板。原桌面文档未删除。
- [ ] **CAO 全量编排实跑**（保持待办）：写 Hermes provider profile（`hermes chat --yolo`），经 `cao launch` + tmux 长驻会话驱动；验证会话审计、完成检测、`cao session list/read`。注：日常指挥已可走 cao-ceo Skill + cao-fleet，本项为 CAO 原生全能力验证。
- [x] 2026-08-15 **多 Worker 并行**：3 个 `hermes -z` 并行子进程实测真并行（wall-clock ≈ 单任务耗时，无串行）；webcli 改造即用 4 Hermes 并行分块（结构/测试/文档/CI），归集联调成功
- [x] **审批门已由 Code 在回路原生覆盖**（保障层拆穿结论，2026-08-23，无需自建）：CEO agent 在回路直接问董事长 = 天然审批门；签字验收打包呈批在 cao-ceo skill 里。原"hermes -z 强制 auto-approve 补审批门"方案作废。
- [ ] **跨 provider 混合舰队**：验证 OpenCode/Codex(修复后)/Claude(若安装) 与 Hermes 混用、模型中立。

### Hermes / 环境治理
- [x] 2026-08-15 **hermes -z 封装标准化**：`scripts/hermes_z.sh` 已成可复用脚本（参数=战略目标、`--usage-file` token 用量、返回码 0/1/2 归一化 + FENG_HERMES 机器可读块），文档见 `scripts/HERMES_Z_README.md`
- [ ] **修复本机棋子**：codex(`~/.codex` 残留)/opencode(`.exe` 缺失) 二选一修复或清理，避免"装太多/坏的"。
- [ ] **WSL 与 Windows 边界**：明确 hermes 走 Windows 本机、awslabs 走 WSL 的目录/权限边界；uv 源保持清华 TUNA 镜像。

### 仓库同步
- [x] 2026-08-15 **gitee 私有仓库**：接入用户提供的 gitee 令牌 → 建私有仓 `FengOrchestrator`(private:true) + 添 `gitee` 远程 + 双远程同步（gitee 与 GitHub 均指向 HEAD `9f95304`）。令牌仅用于建仓/推送，推送后已清洗 remote URL、不残留明文令牌。
- [ ] **gitee 令牌凭据持久化（备选）**：当前双推需手动带令牌；可考虑 `git config gitee` 用 msys credential helper 存令牌，免重复粘贴。
- [ ] **CI/镜像**：如需自动同步，考虑 gitee 镜像仓库(WebHook/gitee-repo-mirror)双向同步。

### 安全与成本
- [ ] **密钥纪律核查**：确认任何 key/token 不进 git（含 gitee 令牌、Zen key、OpenRouter 残留）。
- [ ] **成本核算**：记录各次 `--usage-file` 的 token 用量，评估多 worker 并行的成本拐点。

### 推进实录（2026-08-16 → 2026-08-23）
- [x] 2026-08-16 **CAO Web UI 跑通**：WSL 内 vite dev server(:5173) + cao-server(:9889) 代理连通；修 3 个坑——①node_modules 用 Windows node 装的 rolldown 平台绑定不匹配 → Linux node 完整重装；②vite 进程随 WSL 会话退出被杀 → setsid 脱离会话；③Windows 侧访问走 WSL2 localhost 转发（删 portproxy 后仍通，原生转发正常）。访问 http://localhost:5173/，一键启动脚本已放 ~/FengCloud/start_cao_ui.sh
- [x] 2026-08-16 **cao-fleet skill（闭源自研）**：封装 CAO 控制面 API 召唤/管理 agent 舰队。`~/.zcode/skills/cao-fleet/`（SKILL.md + scripts/cao_fleet.sh：probe/spawn/list/status/say/out/kill）。修 3 个环境坑：①WSL 装 Linux 版 opencode（npmmirror，bin 是 ELF 只是名字带 .exe）；②auth.json 复制到 `~/.local/share/opencode/`（DeepSeek + opencode-go 两凭据）；③`/usr/local/bin/opencode` 软链压过 Windows npm shim。端到端实测：单 agent + 3 agent 舰队均真实响应（DeepSeek V4 Pro，~3-6s/task，~7.4K tokens/agent）
- [x] 2026-08-16 **GitHub 仓库改为 PRIVATE**：发现 FengOrchestrator 在 GitHub 上实际是 PUBLIC（gitee 一直私有），已 gh repo edit 改私有并验证；历史提交扫描无真实密钥泄露
- [x] 2026-08-16 **cao-fleet skill 审核 + probe 修 3 bug**：四项审核（调用可用/CAO 物尽其用/provider 覆盖/命令说明）完成。cao_fleet.sh probe 修 3 bug——①MSYS 管道 `\r` 行尾污染 binary 名（加 `tr -d '\r'`）；②wsl 子进程抢读管道 stdin 致探测行丢失（加 `< /dev/null`）；③codex Windows shim 报错被当版本号假阳性（改判退出码）。修复后 probe 准确：opencode ✓ 1.18.18、codex ✗
- [x] 2026-08-16 **发现 DeepSeek 余额耗尽**：实测 spawn 时 agent 能启动但模型层报 Insufficient Balance；查 `api.deepseek.com/user/balance` 确认余额 -0.03 CNY（赠送额度耗尽转负）。**充值前舰队召唤不可用**；CAO 其余闲置能力（inbox 协作/memory 记忆/workflow 编排/SSE 监控）与 hermes 接入 WSL（Windows wrapper 零安装方案）为下一步候选
- [x] 2026-08-16 **统一模型网关：opencode-go + deepseek-v4-flash（用户定规）**：修正方向——不充 DeepSeek 官方余额，统一走 OpenCode Zen 网关。全局配置 `/root/.config/opencode/opencode.json` 指定 `model: opencode-go/deepseek-v4-flash`（`$schema` 写入曾两次被 shell 转义吃掉，最后用 Write 工具直写 WSL 路径解决）。`opencode run` 实测网关通；CAO spawn 的 agent 均显示 "Build · DeepSeek V4 Flash (2x usage) OpenCode Go"，$0.00 正常干活
- [x] 2026-08-16 **hermes 接入 WSL（零安装 wrapper 方案）**：`/usr/local/bin/hermes` wrapper（`exec /mnt/c/Users/<user>/AppData/Local/hermes/hermes-agent/venv/Scripts/hermes.exe "$@"`），interop 跑 Windows hermes-agent v0.18.2（已登录、config 走 opencode-go）。CAO 探测到 hermes installed=True，spawn 实测真实响应（状态栏 ⚕ deepseek-v4-flash YOLO，回复"通"）。风险确认：Windows TUI 在 tmux 里 raw-mode 兼容可用，无需 Linux 版
- [x] 2026-08-16 **CAO memory 记忆链路打通**：三处修——①`cao install memory_manager --provider opencode_cli` 装侧车 agent 定义（否则报 "Agent not found: memory_manager"）；②opencode.json 给 developer 加 `cao-mcp-server*: true`（否则工具确认框卡死）；③默认 scope 是 project 不是 global。验证：agent 经 memory_store 落库 `chairman-prefers-chinese`（董事长喜欢用中文交流），新 spawn 的 agent 自动注入 `<cao-memory>` 块
- [x] 2026-08-16 **inbox 协作验证通过**：同会话双 agent（developer + reviewer）建立成功；inbox/messages 投递（message_id=1, status=delivered），reviewer 真实回复。派活回执机制落地可用
- [x] 2026-08-16 **舰队各司其职研究 + 文档**（子 agent 源码级深挖 + mock_cli 零 token 实测）：6 个内置角色（code_supervisor 首席协调永不写码 / developer 全权执行 / reviewer 只读审核门 / memory_manager 记忆侧车 / retrospector 复盘 / workflow_scout 定位）；assign（非阻塞派活）/ handoff（阻塞接力）/ send_message（异步归集）三机制实测跑通；workflow script tier 三步流水线（研究→开发→审核）实测 completed；产出 `docs/舰队各司其职.md`（两条路线：supervisor 会话指挥 vs workflow 流水线 + 自定义 frontend/backend/researcher 角色写法 + 模型网关与分工正交说明）
- [x] 2026-08-16 **官方做法精读对照**（子 agent 逐字读 fleet-coordinator / supervisor+worker 协议 skill / examples/assign / examples/orchestration）：官方"舰队"指跨机 CAO 节点（本机多 agent 是 supervisor/worker 协作）；核心答案=supervisor 永不写码 + 三 MCP 工具闭环 + 空闲投递纪律（派完就收手，禁止 sleep/echo 占终端）；补进文档：supervisor 铁律（任务描述落盘+绝对路径）、worker 协议（handoff 不回调/绝不拿自己 terminal_id 当 receiver_id/先写文件再报）、examples/assign 教科书示例、reviewer 裁决格式 + dev 四段式收尾、agent-routing 能力路由
- [x] 2026-08-16 **官方 examples/assign 实战跑通**（子 agent 全流程实测，真实 token）：install 3 profiles（provider 覆盖 opencode_cli）→ POST /sessions 起 analysis_supervisor（v2.4.1 无 spawn 端点）→ 同回合 assign×3 + handoff 全秒回（非阻塞）→ 3 分析师 10s 内派发、全程并行、回传差 4s → 生成 5300 字中文报告（数值与输入一致）。≈79K in / 21K out，**≈$0.0095，4 分钟**。坑：opencode_cli 冷启动 ~60s 超 handoff 超时 → supervisor 自动降级 assign；output 端点是 tmux 屏幕捕获（ANSI 噪声），结构化记录走 SQLite。已补进 docs/舰队各司其职.md「实战验证」
- [x] 2026-08-23 **复用 AO 的 notify+cron 实现"定点交活"（子 agent 完成）**：读 AO v0.18.0 源码确认 --notify 三出口兜底推送、域名自动适配钉钉/飞书/企微、cron=OS crontab 组合、hermes-cli provider 调 `hermes -z` 经 wrapper→本机 hermes→opencode-go 网关。实测：① --notify 真发 HTTP POST（本地监听收到通用 {text}）；②hermes-cli 链路接线 100% 正确，但网关回 401 Insufficient balance——**opencode-go 网关是预付费、额度已耗尽，并非免费**。落地：AO 定时多专家简报可复用+crontab；CAO 干事干完提醒用自建 cao_notify_poller.py（已写、推送链路实测、真实 inbox 未端到端）。交付：cao_notify_poller.py / ao_test.yaml / notify_listener.py / cao_probe.py；WSL 装 /usr/local/bin/ao v0.18.0 + 原生 Node22。（原"后台进行中"僵尸条目已删，以本完成版为准）
- [x] 2026-08-23 **安全事件：网关 api_key 明文泄露到子 agent output 文件（已于同日闭环，见下）**：子 agent 调查 hermes 配置时脱敏正则失效，opencode-go 网关 api_key 明文落入 agent transcript（~/.zcode/cli/agents/sess_b9a25acb-.../agent_8e24d20a-.../output.txt，grep 确认含 1 处 sk- 模式）。处置：①去 opencode.ai 轮换该 key；②轮换后删除此 output 文件。与 DeepSeek/gitee 凭据无关。
- [x] 2026-08-23 **导入 agency-agents-zh 角色库到 CAO 舰队（子 agent 完成）**：精选 15 个角色（前端/后端架构/软件架构/DevOps/AI/数据/安全×3/代码审查/合规/产品×2/小红书/知乎），自写 convert_to_cao.sh 转 CAO opencode 格式，cao install --provider opencode_cli 导入 15/15 成功（cao profile list 共 39）。前端开发者(React计数器)+小红书运营(种草笔记) 经控制面 API 实测真出活。默认 deepseek-v4-flash 网关欠费 401，改用免费模型 opencode/hy3-free（?model= 覆盖、不改 config）旁路验证整条 pipeline 正常，成本 $0.00。交付：convert_to_cao.sh / install_cao.sh / fix_placeholders.sh + cao_profiles/*.md；CAO 控制面已常驻 127.0.0.1:9889。
- [x] 2026-08-23 **安全事件闭环（key 已轮换 + 验证出活）**：含明文网关 key 的 3 文件（output.txt/task.output/transcript.jsonl）本地删除、grep 确认无 sk- 残留；用户提供新 opencode-go key，已写入 WSL 两处 auth.json（/root/.aws/opencode/auth.json + /root/.local/share/opencode/auth.json，len 67、deepseek key 不变）；CAO opencode_cli worker 经新 key 成功调网关、agent 真实出活（/opt/react_answer.txt 写出 React 解释），无 401/403。旧 key 在 opencode.ai 侧已可视为失效（新 key 启用后旧 key 应停用）。
- [x] 2026-08-23 **端到端验证 poller 推送链（子 agent 完成）**：hy3-free 起 analysis_supervisor+data_analyst 两会话，POST /terminals/{id}/inbox/messages 注入 inbox 消息，跑 cao_notify_poller.py --once，本地 127.0.0.1:8899 收到两条 HTTP 200 POST（含完整 inbox 正文），成本 $0.00；CAO 会话已 DELETE 清理。目标②"跑通后自测"闭环。poller 已补 sender_id/message 字段白名单让输出更干净。（原"后台进行中"僵尸条目已删，以本完成版为准）
- [x] 2026-08-23 **安全事件本地清零 + key 已轮换（闭环）**：含明文 key 的 3 文件本地删除、grep 确认目录无 sk- 残留；用户提供新 opencode-go key 已写入 WSL auth.json 两处并验证出活（见下条），本安全事件正式闭环。
- [x] 2026-08-23 **新 opencode-go key 配置与网关恢复验证**：用户提供新 key，写入 WSL 两处 auth.json（len 67）；裸 urllib 直连被 Cloudflare 1010 拦截（非 key 问题），改经 CAO opencode_cli worker 实证——session cao-key_test6 起 terminal 10e434eb，agent 写出 /opt/react_answer.txt（React 解释），无 401/403。网关访问恢复。
- [x] 2026-08-23 **成果入库推送**：30 文件 commit（agency-roles/ 15 角色+转换脚本+上游 MIT LICENSE+NOTICE 派生声明、cao_notify_poller.py、AO notify 验证脚本、评估文档）；gitee 推送成功（bdc4520..3693fb8）；GitHub 直连被墙（443 不通）暂未推，需代理后补推。
- [x] 2026-08-23 **275 角色价值评估（两份报告）**：`docs/agency-roles-evaluation.md`（推荐精选扩充至~45，剔除重复）+ `docs/prompt-quality-review.md`（12 角色纯读提示词评审）：结论=部分有用——合同审查(12)/HR招聘(12)/小红书(11)/Outbound销售(11)/产品经理(11)/财务分析(11) 是真本土化精品可直接入队；工程/测试/客服类是翻译填充套壳件(6-7分)不值得。策略：挑 8-10 个精品纳编，别被数量唬住。
- [x] 2026-08-23 **新装 6 个新领域 CAO profile**：UX 架构师/增长黑客/财务分析师/合同审查专家/API 测试员/Outbound 策略师（CAO agents 目录 19→25）。注：API 测试员经评审偏弱可移除；HR 招聘(12 分)尚未装。
- [x] 2026-08-23 **清理与止损**：删 CAO 残留测试 session（key_test2/3/4）；按董事长反馈停止高成本逐角色 spawn 实测（费 token 且慢），改为纯读提示词评审（零网关消耗）。
- [ ] 2026-08-23 **舰队定编 + 真实多角色实战**（待董事长看完报告拍板）：装 HR 招聘、删花架子（API 测试员），然后 3-4 个精品角色跑一场小型真实任务实战，验证「各司其职+干完自动回报」整条链路；全程控制 token 量级。
- [ ] **TTS UI v3 收尾与签字**（2026-08-24）：四棒接力完成后呈董事长验收。
- [ ] **模型已切 ox-alpha-free（免费）**（2026-08-24）：观察断线率，评估免费网关稳定性。
- [x] 2026-08-23 **开源格局研究 + 架构蓝图**：搜同类项目（原版 agency-agents 147k★纯英文/VoltAgent 158+开发向/ChatDev/MetaGPT 不指挥CLI/agency-orchestrator 零代码YAML入口）；确认人才库锁定 agency-agents-zh 一家足够（原版翻译+52中国原创+NEXUS组织手册）；发现 strategy/ 目录 NEXUS 组织手册=愿景"组织设计空白"的现成答案。产出：docs/达成目标架构蓝图.md（五层架构：意图/组织/人才/执行/保障）+ docs/agency-agents-人才库与组织手册对接.md
- [x] 2026-08-23 **CEO Playbook v0 + cao-ceo Skill**：NEXUS 落成可执行手册（docs/CEO-Playbook-v0.md，5步标准动作/三编制/七阶段/质量门禁/NEXUS交接模板）；包装成 skills/cao-ceo/SKILL.md（复用 cao-fleet 脚本、召唤时自动注入知识源 docs/+FENGMEM.md、验收 spawn reviewer 打分、审批在回路直接问董事长）。校验 playbook 引用 profile 全部存在
- [x] 2026-08-23 **人才库全量导入 263 profile**：董事长指示"没资格评判小众、全部装上"——作废上一版剔除方案（convert_all_to_cao.sh），重写 convert_all_full.sh 全量扫 19 部门 260 角色零剔除导入；游戏5/GIS13/学术6/空间计算6/C-level/垂直行业 100% 进来；86 个标【在编】核心（仅标记不影响可召唤性）；agent-store 共 263（含 CAO 原有3）；同步仓库 agency-roles/cao_profiles/263；MIT 署名随后于同日全量修复（见下条）
- [x] 2026-08-23 **保障层拆穿（过度设计纠正）**：之前推荐的 5 个独立保障工具中 4 个多余——审批门=Code 在回路直接问（不引 AgentGate）、记忆=Code原生+FENGMEM（不引 MemPalace）、通知=cao_notify_poller 已有（不引钉钉框架）、验收=spawn reviewer agent（不引 promptfoo）；唯一真缺口=知识供给，已由 cao-ceo skill 召唤时自动注入 docs/+FENGMEM.md 解决（不引 RAGFlow）
- [x] 2026-08-23 **FENGMEM.md 会话记忆建立**：按全局规则建 ~/FengOrchestrator/FENGMEM.md，7 轮全程记录（评估→架构→全量导入→Skill 化）
- [x] 2026-08-23 **MIT 署名合规全量修复**：convert_all_full.sh 内置署名逻辑（正文顶部嵌上游仓库链接+双版权+派生说明）→ 重新生成 WSL agent-store 260 个 → 同步仓库 cao_profiles/ → 双侧 python 验证 260/260 零缺失；NOTICE.md 更新为全量口径；导入清单.md 合规项转已修复。合规债清零
- [x] 2026-08-24 **TTS UI 三场实战**：v1 Edge 引擎（972 行，干事跑偏纠偏后交付 + CEO 修 tungstenite WS 握手 bug）/ v2 曼波整合（任务书防呆四要素预写后一次过零打回）/ v3 真舰队协同（PM→设计师→开发→QA 四棒接力，hermes+opencode 混编，模型 ox-alpha-free，进行中）。经验教训已回写 CEO-Playbook §八与 cao-ceo SKILL.md

---

_创建：2026-08-15 ｜ 状态：MVP 已通，五层架构成型且经 TTS UI 实战验证，当前主待办 = TTS UI v3 舰队协同收尾_

## 2026-09-13
- [x] 2026-09-13 **两层原则审查+文章**：审查完成（FengInvest 标杆不动 / FengMedia 写操作收进对话 / FlyGo 加客户 Skill 层 / FengOS 为统一观景台 / TTS-UI 不适用）；业界对位确认（chat-first / Generative UI / MCP Apps / local-first）；学术级文章已写 [fengyuwang_com/TWO-LAYER-INTERFACE.md](../../../fengyuwang_com/TWO-LAYER-INTERFACE.md)；架构总纲 §〇.1 + README 已同步立规。

## 2026-09-12
- [x] CAO 舰队 Web 大屏上线：构建官方 Web UI（web/ npm build）拷入 site-packages，tmux 托管 cao-server，localhost:9889 浏览器可开；召唤 4 干事（2 忙 2 闲）实况演示
