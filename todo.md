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
- [x] 2026-08-16 **webcli Rust 单二进制重写（用户点名）**：axum + portable-pty(ConPTY) + xterm.js 真·交互式终端（可跑 python REPL / vim / opencode 等全屏 TUI）；R1 后端/R2 前端 Hermes 并行产出 + 主集成编译修错（axum API 适配、clippy 清零）；release 单 exe 已部署到部署机；移除 Python 版（单命令模式+高危拦截，git 历史可回滚）
- [x] 2026-08-16 **10 个 Hermes 并行实验（5 分钟限时）**：9/10 完成，墙钟 301s vs 串行估算 ~21.6min（加速比 ~4.3x）；结论：墙钟由最慢干事决定，>4 个 agent 收益递减（H4 benchmark 佐证）
- [x] 2026-08-16 **舰队问题修复（10 干事研究成果落地）**：hermes_z.sh 新增 `-s` 安全模式（临时 HERMES_HOME + 工具白名单）与 `-L` 任务/成本归集（logs/fleet/fleet.tsv 台账）；Hermes 接入 MCP filesystem server（14 工具，`mcp__filesystem__*` 前缀，docs/mcp.md）；CAO 控制面 API 已跑通（WSL localhost:9889，sessions/terminals/events/workflows 齐全）

---

## 待办（MVP 之后）

### 编排演进
- [ ] **CAO 全量编排实跑**：写 Hermes provider profile（`hermes chat --yolo`），经 `cao launch` + tmux 长驻会话驱动；验证会话审计、完成检测、`cao session list/read`。
- [x] 2026-08-15 **多 Worker 并行**：3 个 `hermes -z` 并行子进程实测真并行（wall-clock ≈ 单任务耗时，无串行）；webcli 改造即用 4 Hermes 并行分块（结构/测试/文档/CI），归集联调成功
- [ ] **审批门**：当前 `hermes -z` 强制 auto-approve(YOLO)；需为"董事长只签不拆"补一层审批门（跑前批准/跑后打回）。参考 `tool-restrictions` / allowlist 收窄权限。
- [ ] **跨 provider 混合舰队**：验证 OpenCode/Codex(修复后)/Claude(若安装) 与 Hermes 混用、模型中立。

### Hermes / 环境治理
- [x] 2026-08-15 **hermes -z 封装标准化**：`scripts/hermes_z.sh` 已成可复用脚本（参数=战略目标、`--usage-file` token 用量、返回码 0/1/2 归一化 + FENG_HERMES 机器可读块），文档见 `scripts/HERMES_Z_README.md`
- [ ] **修复本机棋子**：codex(`~/.codex` 残留)/opencode(`.exe` 缺失) 二选一修复或清理，避免"装太多/坏的"。
- [ ] **WSL 与 Windows 边界**：明确 hermes 走 Windows 本机、awslabs 走 WSL 的目录/权限边界；uv 源保持清华 TUNA 镜像。

### 仓库同步
- [x] 2026-08-15 **多远程同步**：配置双远程（GitHub + 内网镜像）双推，令牌仅用于建仓/推送，推送后清洗 remote URL、不残留明文令牌。
- [ ] **gitee 令牌凭据持久化（备选）**：当前双推需手动带令牌；可考虑 `git config gitee` 用 msys credential helper 存令牌，免重复粘贴。
- [ ] **CI/镜像**：如需自动同步，考虑 gitee 镜像仓库(WebHook/gitee-repo-mirror)双向同步。

### 安全与成本
- [ ] **密钥纪律核查**：确认任何 key/token 不进 git（含 gitee 令牌、Zen key、OpenRouter 残留）。
- [ ] **成本核算**：记录各次 `--usage-file` 的 token 用量，评估多 worker 并行的成本拐点。

---

_创建：2026-08-15 ｜ 状态：MVP 已通，待办按优先级推进_
- [x] 2026-08-16 **CAO Web UI 跑通**：WSL 内 vite dev server(:5173) + cao-server(:9889) 代理连通；修 3 个坑——①node_modules 用 Windows node 装的 rolldown 平台绑定不匹配 → Linux node 完整重装；②vite 进程随 WSL 会话退出被杀 → setsid 脱离会话；③Windows 侧访问走 WSL2 localhost 转发（删 portproxy 后仍通，原生转发正常）。访问 http://localhost:5173/，一键启动脚本已放 C:\path\to\your-projects\start_cao_ui.sh
- [x] 2026-08-16 **cao-fleet skill（闭源自研）**：封装 CAO 控制面 API 召唤/管理 agent 舰队。`~/.zcode/skills/cao-fleet/`（SKILL.md + scripts/cao_fleet.sh：probe/spawn/list/status/say/out/kill）。修 3 个环境坑：①WSL 装 Linux 版 opencode（npmmirror，bin 是 ELF 只是名字带 .exe）；②auth.json 复制到 `~/.local/share/opencode/`（DeepSeek + opencode-go 两凭据）；③`/usr/local/bin/opencode` 软链压过 Windows npm shim。端到端实测：单 agent + 3 agent 舰队均真实响应（DeepSeek V4 Pro，~3-6s/task，~7.4K tokens/agent）
- [x] 2026-08-16 **仓库可见性核对**：确认发布前仓库可见性符合预期（公开版开箱即用），历史提交扫描无真实密钥泄露
- [x] 2026-08-16 **cao-fleet skill 审核 + probe 修 3 bug**：四项审核（调用可用/CAO 物尽其用/provider 覆盖/命令说明）完成。cao_fleet.sh probe 修 3 bug——①MSYS 管道 `\r` 行尾污染 binary 名（加 `tr -d '\r'`）；②wsl 子进程抢读管道 stdin 致探测行丢失（加 `< /dev/null`）；③codex Windows shim 报错被当版本号假阳性（改判退出码）。修复后 probe 准确：opencode ✓ 1.18.18、codex ✗
- [x] 2026-08-16 **发现账户余额不足**：实测 spawn 时 agent 能启动但模型层报 Insufficient Balance。**充值前舰队召唤不可用**；CAO 其余闲置能力（inbox 协作/memory 记忆/workflow 编排/SSE 监控）与 hermes 接入 WSL（Windows wrapper 零安装方案）为下一步候选
- [x] 2026-08-16 **统一模型网关：opencode-go + deepseek-v4-flash（用户定规）**：修正方向——不充 DeepSeek 官方余额，统一走 OpenCode Zen 网关。全局配置 `/root/.config/opencode/opencode.json` 指定 `model: opencode-go/deepseek-v4-flash`（`$schema` 写入曾两次被 shell 转义吃掉，最后用 Write 工具直写 WSL 路径解决）。`opencode run` 实测网关通；CAO spawn 的 agent 均显示 "Build · DeepSeek V4 Flash (2x usage) OpenCode Go"，$0.00 正常干活
- [x] 2026-08-16 **hermes 接入 WSL（零安装 wrapper 方案）**：`/usr/local/bin/hermes` wrapper（`exec /mnt/c/Users/yourusername/AppData/Local/hermes/hermes-agent/venv/Scripts/hermes.exe "$@"`），interop 跑 Windows hermes-agent v0.18.2（已登录、config 走 opencode-go）。CAO 探测到 hermes installed=True，spawn 实测真实响应（状态栏 ⚕ deepseek-v4-flash YOLO，回复"通"）。风险确认：Windows TUI 在 tmux 里 raw-mode 兼容可用，无需 Linux 版
- [x] 2026-08-16 **CAO memory 记忆链路打通**：三处修——①`cao install memory_manager --provider opencode_cli` 装侧车 agent 定义（否则报 "Agent not found: memory_manager"）；②opencode.json 给 developer 加 `cao-mcp-server*: true`（否则工具确认框卡死）；③默认 scope 是 project 不是 global。验证：agent 经 memory_store 落库 `chairman-prefers-chinese`（董事长偏好中文交流，示例键），新 spawn 的 agent 自动注入 `<cao-memory>` 块
- [x] 2026-08-16 **inbox 协作验证通过**：同会话双 agent（developer + reviewer）建立成功；inbox/messages 投递（message_id=1, status=delivered），reviewer 真实回复。派活回执机制落地可用
- [x] 2026-08-16 **舰队各司其职研究 + 文档**（子 agent 源码级深挖 + mock_cli 零 token 实测）：6 个内置角色（code_supervisor 首席协调永不写码 / developer 全权执行 / reviewer 只读审核门 / memory_manager 记忆侧车 / retrospector 复盘 / workflow_scout 定位）；assign（非阻塞派活）/ handoff（阻塞接力）/ send_message（异步归集）三机制实测跑通；workflow script tier 三步流水线（研究→开发→审核）实测 completed；产出 `docs/舰队各司其职.md`（两条路线：supervisor 会话指挥 vs workflow 流水线 + 自定义 frontend/backend/researcher 角色写法 + 模型网关与分工正交说明）
- [x] 2026-08-16 **官方做法精读对照**（子 agent 逐字读 fleet-coordinator / supervisor+worker 协议 skill / examples/assign / examples/orchestration）：官方"舰队"指跨机 CAO 节点（本机多 agent 是 supervisor/worker 协作）；核心答案=supervisor 永不写码 + 三 MCP 工具闭环 + 空闲投递纪律（派完就收手，禁止 sleep/echo 占终端）；补进文档：supervisor 铁律（任务描述落盘+绝对路径）、worker 协议（handoff 不回调/绝不拿自己 terminal_id 当 receiver_id/先写文件再报）、examples/assign 教科书示例、reviewer 裁决格式 + dev 四段式收尾、agent-routing 能力路由
- [x] 2026-08-16 **官方 examples/assign 实战跑通**（子 agent 全流程实测，真实 token）：install 3 profiles（provider 覆盖 opencode_cli）→ POST /sessions 起 analysis_supervisor（v2.4.1 无 spawn 端点）→ 同回合 assign×3 + handoff 全秒回（非阻塞）→ 3 分析师 10s 内派发、全程并行、回传差 4s → 生成 5300 字中文报告（数值与输入一致）。≈79K in / 21K out，**≈$0.0095，4 分钟**。坑：opencode_cli 冷启动 ~60s 超 handoff 超时 → supervisor 自动降级 assign；output 端点是 tmux 屏幕捕获（ANSI 噪声），结构化记录走 SQLite。已补进 docs/舰队各司其职.md「实战验证」
