---
name: cao-fleet
description: 通过 CAO（awslabs/cli-agent-orchestrator，跑在 WSL 的 localhost:9889）控制面 API 召唤与管理 AI agent 舰队。当董事长要求"召唤/派/拉起 N 个 agent"、"研究一下 XX 架构/主题"、"开一堆干事的会话"、"看干事们在干嘛/有没有摸鱼"（查 sessions/terminals 状态与输出）、"给某个干事派活/发消息"时使用。自研闭源封装，不依赖开源 skill。
---

# CAO 舰队召唤

用 CAO 控制面 API 批量拉起 AI agent（干事）会话、派首条任务、查状态、读输出。CAO server 跑在 WSL 里（`localhost:9889`，Windows 侧可直接访问）。

## 快速开始

```bash
# 1. 探测可用 provider / profile（spawn 前必做，见下方坑1）
bash "~/.zcode/skills/cao-fleet/scripts/cao_fleet.sh" probe

# 2. 批量召唤 N 个独立 agent，各带首条任务（deferred-init 秒回）
bash "~/.zcode/skills/cao-fleet/scripts/cao_fleet.sh" spawn \
  --profile developer --provider hermes --count 3 \
  --message "研究我们的舰队架构，输出一份结论" --workdir /root/fleet-orchestrator

# 3. 查状态 / 发消息 / 读输出
bash "...\cao_fleet.sh" list
bash "...\cao_fleet.sh" status <session_name>
bash "...\cao_fleet.sh" say <terminal_id> "继续，给出结论"
bash "...\cao_fleet.sh" out <terminal_id>
```

## 核心概念（必须理解再动手）

- **Session = 一个 tmux 会话**，可含多个 terminal（agent 窗口）。批量召唤两种姿势：
  - **N 个独立 agent**：循环 `POST /sessions`，各管各的（推荐，简单）
  - **同会话舰队**（supervisor/worker 协作）：先 `POST /sessions` 建主 agent，再 `POST /sessions/{session_name}/terminals` 加副手，会话内通过 MCP `assign`/`send_message` 互相协作
- **Spawn 会真实拉起 provider CLI**（tmux + 等初始化，默认同步阻塞至多 60s）；带 `initial_message` 则走 deferred-init 秒回。批量召唤**必须带 initial_message**，否则 HTTP 会逐个卡到超时。
- **每次 spawn 前必须先 `probe`**：本机 codex/opencode_cli 的 `installed=true` 是假阳性（binary 是 Windows npm shim，WSL 里跑不起来）。只看 provider 表不可靠。

## 常用 API 端点（脚本已封装，手搓时用）

| 操作 | 请求 |
|---|---|
| 建会话（spawn agent） | `POST /sessions?agent_profile=P&provider=PR&session_name=N&working_directory=D` body 可带 `{"initial_message":"任务","env_vars":{...}}` → 201 返回 terminal 对象（`id` 8位hex） |
| 同会话加 agent | `POST /sessions/{name}/terminals?agent_profile=P&defer_init=true` |
| 列会话 | `GET /sessions` |
| 会话详情（含 terminals 列表） | `GET /sessions/{name}` |
| 给 agent 发消息（即时） | `POST /terminals/{id}/input?message=...` |
| 给 agent 发消息（inbox 持久队列） | `POST /terminals/{id}/inbox/messages?receiver_id={id}&sender_id={谁}&message=...` |
| 查收件箱回执 | `GET /terminals/{id}/inbox/messages?limit=50&status=delivered`（pending/delivered/failed） |
| 读输出 | `GET /terminals/{id}/output?mode=full|last`（**不接受 tail**） |
| 记忆：写（MCP 工具，agent 内调） | `memory_store`（content/scope=global\|project\|session\|agent/key/tags） |
| 记忆：查 | `GET /memory?scope=project&limit=20`、`GET /memory/{key}` |
| 记忆：某 terminal 注入块 | `GET /terminals/{id}/memory-context`（新 spawn 自动注入 `<cao-memory>` 块） |
| 终止 | `DELETE /sessions/{name}` / `POST /terminals/{id}/exit` |
| 可用 provider / profile | `GET /agents/providers`、`GET /agents/profiles` |

**provider 枚举**：`kiro_cli`(默认) `claude_code` `codex` `kimi_cli` `copilot_cli` `opencode_cli` `hermes` `cursor_cli` `antigravity_cli` `mock_cli`(仅测试)
**本机内置 profile**：`code_supervisor` `developer` `reviewer` `memory_manager` `retrospector` `workflow_scout`

## 本机 provider 实况（2026-08-16 验证）

- ✅ **opencode_cli**：Linux 原生 v1.18.18，**模型统一走 opencode-go（Zen 网关）`deepseek-v4-flash`**（全局配置 `/root/.config/opencode/opencode.json`，不依赖 DeepSeek 官方余额）
- ✅ **hermes**：Windows hermes-agent v0.18.2 经 `/usr/local/bin/hermes` wrapper（`exec .../hermes.exe "$@"`）interop 运行，TUI 在 tmux 里可用，走 Windows config.yaml（同为 opencode-go + deepseek-v4-flash）
- ⚠️ **codex**：CAO 显示 installed 但实际是 Windows npm shim（`exec node not found`），WSL 里不可用
- ❌ 其余 provider（kiro/claude_code/kimi/copilot/cursor/antigravity）：未装

## 记忆（Memory）链路——已验证

- 写：agent 通过 MCP `memory_store` 工具落库（需 opencode.json 里该 agent `cao-mcp-server*: true`，否则弹确认框卡死）
- 读：新 spawn 的 agent 自动注入 `<cao-memory>` 块（`GET /terminals/{id}/memory-context`）
- 侧车：spawn 带 `&memory_manager=true` 会多起一个 memory_manager terminal 负责梳理记忆（需先 `cao install memory_manager --provider opencode_cli` 装 agent 定义，否则报 "Agent not found"）
- 默认 scope 是 **project**（不是 global！查 `GET /memory?scope=project`）

## 三个坑（必读）

1. **provider 假阳性**：spawn 前用 `probe` 验证——脚本会调 `wsl bash -lc "command -v X && timeout 5 X --version"` 真实验证 binary 在 WSL 内可执行。起不来的 provider 会 500 `initialization timed out`。
2. **工作目录白名单**：`/`、`/bin`、`/usr/bin`、`/etc`、`/var`、`/tmp`、`/root`、`/proc` 等系统路径**精确屏蔽**，会 500 `Working directory not allowed`。用 `/root/fleet-orchestrator` 这类子目录或 `~/xxx`。
3. **同步阻塞**：无 `initial_message` 时 POST 会阻塞等 provider 初始化（上限 60s）。批量必带 message。
4. **opencode 需要认证**：WSL 里 opencode 的 auth.json 在 `~/.local/share/opencode/auth.json`（不是 CAO 指定的 /root/.aws/opencode/）。Windows 的 auth 在 `~/.local/share/opencode/auth.json`，`cp` 过去并 `chmod 600` 即可（已有 deepseek + opencode-go 两个凭据）。没认证时 agent 会显示 "Free limit reached" 且不干活。
5. **PATH 陷阱**：WSL PATH 含 Windows npm 目录，`opencode` 可能解析到 Windows shim 报 `not found`。已建软链 `/usr/local/bin/opencode → /opt/node/lib/node_modules/opencode-ai/bin/opencode.exe`（Linux ELF），不要删。

## 摸鱼监控（董事长场景）

```bash
# 所有干事会话一览（名称/状态）
bash "...\cao_fleet.sh" list
# 指定会话里每个 agent 的最新输出
bash "...\cao_fleet.sh" out <terminal_id>
```

`GET /sessions` 只列 `cao-` 前缀会话；`DELETE /sessions/{name}` 会连 tmux 一起清掉。

## 编排（Workflows）与定时（Flows）

不是简单批量 spawn 的首选，跳过；复杂多角色协同才需要 `POST /workflows/runs` 提交 spec。
