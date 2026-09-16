# MCP（Model Context Protocol）接入调研与落地

> 调研时间：2026-08-15　|　环境：Windows 10，Hermes Agent（`~/AppData/Local/hermes`）　|　Node v24.12.0 / npx 11.6.2　|　Python 3.11.15

---

## 一、MCP 是什么

MCP（Model Context Protocol，模型上下文协议）是 Anthropic 于 2024 年底提出的开放标准，用来统一"AI 应用 ↔ 外部工具/数据"之间的连接方式。类比 USB-C：以前每个外设（文件系统、数据库、GitHub、浏览器）都要自己造一根专用线缆（定制集成），MCP 规定了一个通用接口——MCP server 负责把某个能力（一组工具）以标准 JSON-RPC 协议暴露出来，MCP client（这里就是 Hermes）在启动时自动发现这些工具并注册为可调用的工具。

对 Hermes 来说，接入 MCP 的收益很直接：**不用改 Hermes 源码、不用写原生 tool，就能让 Agent 使用整个 MCP 生态里现成的工具**。Hermes 内置了原生 MCP client，启动时读取 `config.yaml` 里的 `mcp_servers` 配置，连接每个 server、发现其工具，然后以 `mcp__<server>__<tool>` 的命名注册进工具注册表，自动注入所有平台（CLI / Telegram / Discord 等）的工具集。

两种传输方式：

- **stdio（本地进程）**：`command` + `args`，Hermes 拉起子进程并通过 stdin/stdout 通信。如 `npx -y @modelcontextprotocol/server-filesystem`。
- **HTTP（远程）**：`url` + `headers`，连接远端 MCP 端点。

---

## 二、对"干事舰队"的价值

本项目（FengOrchestrator）的定位是"干事舰队"——一批可编排的自动化干事。MCP 给每个干事挂载外部能力提供了一条标准通道：

| 干事场景 | 可用 MCP server（举例） | 效果 |
|---|---|---|
| 文件/文档操作 | `@modelcontextprotocol/server-filesystem` | 干事可读写受控目录，跨会话管理文档 |
| 浏览器自动化 | Playwright / Puppeteer MCP | 干事可做页面巡检、抓取、表单操作 |
| 数据库 | PostgreSQL / MySQL / SQLite MCP | 干事直连库做查询、迁移、报表 |
| Gitee / GitHub | `@modelcontextprotocol/server-github`（Gitee 有社区版） | 干事建 issue、提 PR、管理仓库 |
| 搜索/网页 | Brave Search / Fetch MCP | 干事检索资料、抓网页 |
| 内部 API | 自研 HTTP MCP server | 把内部系统能力暴露给所有干事 |

核心价值：

1. **解耦**：外部能力以独立进程/服务存在，干事侧零代码接入；server 升级、替换不影响舰队主体。
2. **标准化**：所有干事共用同一套 MCP 发现/调用机制，命名规则统一（`mcp__<server>__<tool>`），便于编排层统一管控。
3. **安全边界**：Hermes 对 stdio MCP 子进程做环境变量过滤（只传 PATH/HOME 等安全变量 + `env` 里显式指定的），API key 不会意外泄露给 MCP server；工具错误信息里的凭据样式字符串也会自动脱敏。
4. **按需裁剪**：`mcp_servers.<name>.tools.include` 可只暴露部分工具，比如不让干事看到 `delete_workspace` 这类危险操作。

---

## 三、Hermes 配置方法

### 3.1 配置位置与格式（调研结论）

配置文件：`~/AppData/Local/hermes/config.yaml`（即 `~/.hermes/config.yaml`，本机 `HERMES_HOME` 指向 `AppData\Local\hermes`）。

顶层键名为 **`mcp_servers`**（注意：不是 `mcp`、不是 `servers`）。每个 server 一个条目，两种传输二选一：

```yaml
# stdio 传输（本地进程）：
mcp_servers:
  filesystem:
    command: "npx"                                   # 必填：可执行程序
    args: ["-y", "@modelcontextprotocol/server-filesystem", "~/FengOrchestrator"]  # 可选：参数
    env:                                             # 可选：只把这些环境变量传给子进程
      SOME_VAR: "value"
    timeout: 120                                     # 可选：单次工具调用超时（秒），默认 120
    connect_timeout: 60                              # 可选：初始连接超时（秒），默认 60

# HTTP 传输（远程）：
mcp_servers:
  remote_api:
    url: "https://mcp.example.com/mcp"               # 必填：端点 URL
    headers:                                         # 可选：请求头（如鉴权）
      Authorization: "Bearer sk-..."
```

一个条目里 `command` 与 `url` 互斥，二选一。

### 3.2 命令行辅助（不需要手改 YAML）

```bash
hermes mcp list          # 查看已配置的 server
hermes mcp add <name> --command npx --args ...       # 添加（会先连一下、发现工具、问你要哪些）
hermes mcp test <name>   # 测试连接 + 列出发现的工具
hermes mcp remove <name> # 删除
hermes mcp catalog       # 查看 Nous 官方审核过的 MCP 目录
hermes mcp install <name># 一键安装目录里的 MCP（如 n8n、linear）
```

注意：`hermes mcp add` 在无 TTY 环境（脚本/CI）里最后的"Enable all N tools? [Y/n/select]"交互会直接取消；建议在交互终端里用，或直接手写 YAML（本报告就是手写 YAML 方案）。

### 3.3 前置条件

- Hermes 的 Python venv 里需要 `mcp` 包：`~/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -c "import mcp"`（本机已装好，无需操作）。
- npx/uvx 类 server 需要 Node.js（本机 v24.12.0 ✓）。
- 国内网络：`~/.npmrc` 已配 `registry=https://registry.npmmirror.com`，npx 拉包走镜像（本机已配 ✓）。

### 3.4 命名规则与生效时机

- 工具命名：`mcp__<server>__<tool>`（本机实测为双下划线；老版本文档写作 `mcp_<server>_<tool>`，以下划线为权威）。例如 server `filesystem` 的工具 `list_directory` → `mcp__filesystem__list_directory`。
- 生效时机：**改配置后需重启 Hermes**（新开会话/新进程即生效，无热加载）。
- 会话内可用 `/reload-mcp` 重载 MCP server。

---

## 四、已接入的 server 与验证输出

### 4.1 接入：filesystem MCP（无外部 key）

在 `config.yaml` 中加入（修改前已备份为 `config.yaml.bak-mcp-20260815235303`；未触碰 provider / api_key 等任何凭据配置）：

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "~/FengOrchestrator"]
    connect_timeout: 120
```

server 名 `filesystem`，root 目录限定为 `~/FengOrchestrator`（安全沙箱：server 只能访问该目录，防越权读写）。

### 4.2 验证 1：`hermes mcp list` / `hermes mcp test filesystem`

```
MCP Servers:

  Name             Transport                      Tools        Status
  ──────────────── ────────────────────────────── ──────────── ──────────
  filesystem       npx -y @modelcontextproto...   all          ✓ enabled

  Testing 'filesystem'...
  Transport: stdio → npx
  Auth: none
  ✓ Connected (8859ms)
  ✓ Tools discovered: 14
```

发现的 14 个工具：`read_file`、`read_text_file`、`read_media_file`、`read_multiple_files`、`write_file`、`edit_file`、`create_directory`、`list_directory`、`list_directory_with_sizes`、`directory_tree`、`move_file`、`search_files`、`get_file_info`、`list_allowed_directories`。

### 4.3 验证 2：`hermes -z` 工具列表含 MCP 工具（关键输出）

命令：`hermes -z "列出你当前可用的所有工具名，含 MCP 的"`，输出中 MCP 部分：

```
MCP (filesystem):
mcp__filesystem__create_directory
mcp__filesystem__directory_tree
mcp__filesystem__edit_file
mcp__filesystem__get_file_info
mcp__filesystem__list_allowed_directories
mcp__filesystem__list_directory
mcp__filesystem__list_directory_with_sizes
mcp__filesystem__move_file
mcp__filesystem__read_file
mcp__filesystem__read_media_file
mcp__filesystem__read_multiple_files
mcp__filesystem__read_text_file
mcp__filesystem__search_files
mcp__filesystem__write_file
```

### 4.4 验证 3：实际调用 MCP 工具（端到端）

命令：`hermes -z "用 MCP filesystem 工具列出 ~/FengOrchestrator 的顶层目录内容…"`，Agent 实际调用了 MCP 工具并返回：

```
项目根目录 ~/FengOrchestrator 的顶层内容如下：

文件（4 个）:
  .gitignore   372 B    Git 忽略规则
  README.md    1.9 KB   项目说明
  todo.md      4.2 KB   待办清单

文件夹（4 个）:
  .git/  .zcode/  docs/  scripts/  webcli/
```

→ **MCP 工具已真正可用**：发现、注册、调用、返回全链路打通。

### 4.5 排坑记录

| 现象 | 原因 | 处理 |
|---|---|---|
| `hermes mcp add` 在脚本环境卡住/取消 | 最后的工具选择是 TTY 交互，非交互环境无输入 | 改用直接写 YAML |
| 取消后 config.yaml 被压成精简版（注释全没了） | `hermes mcp add` 取消时重写了配置文件 | 用事先备份恢复，再手写 YAML |
| npx 首次拉包慢 | 默认走 npmjs 官方源 | `~/.npmrc` 配 npmmirror 镜像 |

---

## 五、后续建议

1. **浏览器 MCP**：接入 Playwright MCP（`npx -y @playwright/mcp`），给干事页面巡检/抓取能力，与现有 webcli 形成互补。
2. **数据库 MCP**：按需接 PostgreSQL/MySQL MCP（本地 stdio 或远端 HTTP），干事查数、报表自动化。
3. **Gitee MCP**：本项目托管在 Gitee，接 Gitee 的 MCP 或自研薄封装 server，让干事直接建 issue / 提 PR / 触发 CI，与 `webcli`、`hermes_z.sh` 封装形成完整闭环。
4. **自研 HTTP MCP server**：把舰队内部系统（编排、状态、报表）暴露成 MCP，所有干事统一挂载。
5. **工具裁剪**：每个 server 用 `tools.include` 白名单，只暴露必要工具，降低误操作面。
6. **鉴权收敛**：需要 key 的 server 一律用 `env` 显式传变量，key 放 `.env` 或密钥库，绝不写进 config.yaml / 文档 / 代码（本次未引入任何 key）。
7. **配置即代码**：`mcp_servers` 段落建议沉淀到本仓库（脱敏后），新环境一条命令复现接入。

---

## 附：本次改动清单

- `~/AppData/Local/hermes/config.yaml` — 新增 `mcp_servers.filesystem` 段（其余未动）
- `~/AppData/Local/hermes/config.yaml.bak-mcp-20260815235303` — 修改前备份
- `~/FengOrchestrator/docs/mcp.md` — 本报告
- 未触碰：provider / api_key（Zen key）相关配置；未写入任何密钥。
