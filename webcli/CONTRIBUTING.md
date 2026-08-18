# 贡献指南

感谢你愿意为 webcli 贡献力量！本指南说明如何提交代码、测试与文档变更。
在动手之前，请先阅读 [README.md](README.md) 与 [SECURITY.md](SECURITY.md)，
尤其是其中的**安全模型**——本项目会打开一个可执行任意命令的交互式 shell，
任何改动都不得削弱安全护栏。

## 工作流概览

```
fork / 检出仓库
  → 从 main 切出功能分支
  → 按规范提交（Conventional Commits）
  → 本地跑通全部测试
  → 发起 Pull Request（用仓库内 PR 模板）
  → 维护者 review，必要时修改
  → 合并到 main
```

## 分支与命名

- 主干分支为 `main`，始终处于可发布状态。
- 新功能：`feature/<简短描述>`，如 `feature/term-cwd-env`。
- 缺陷修复：`fix/<简短描述>`，如 `fix/ws-reconnect-race`。
- 文档/其他：`docs/`、`chore/` 前缀同理。
- 不要直接向 `main` 提交；一律通过 Pull Request 合入。

## 提交信息风格

采用 [Conventional Commits](https://www.conventionalcommits.org/) 风格，
说明部分可用中文：

```
<type>(<scope>): <描述>

[可选正文：为什么改、怎么验证]
```

- `feat`：新功能
- `fix`：缺陷修复
- `docs`：文档（README / 注释等）
- `test`：测试（cargo test，src/main.rs 内测试模块）
- `refactor`：重构，不改行为
- `chore`：杂项（依赖、构建、格式化）

示例：

```
feat(term): 新增 TERM_CWD 环境变量支持

会话初始工作目录可由 TERM_CWD 指定，默认回退到用户主目录。
```

## 代码风格

- **Rust**（`src/main.rs`）：使用 `cargo fmt` 格式化，提交前跑
  `cargo clippy -- -D warnings` 保证零告警；保持与现有代码一致的注释语言习惯
  （中英皆可，以清晰为准）。
- **前端**（`static/index.html` 与 `static/vendor/`）：xterm.js + 原生 JS，
  不引入构建步骤、框架或打包器——`vendor/` 中 xterm.js 与 addon-fit 保持本地
  vendored，零构建是本项目的特性。
- **接口契约**：`src/main.rs` 头部注释中的 WebSocket 消息类型字段名
  （`input` / `resize` / `output` / `exit`）是**稳定契约**，**不得改名或改语义**。
  新增字段必须向后兼容，并在 README「接口契约」章节同步更新。

## 测试要求

所有变更必须通过以下检查后方可提交 PR：

1. **后端改动**：`cargo build --release` 成功后运行 `cargo test`（全部 PASS），
   并保证 `cargo clippy -- -D warnings` 零告警。
2. **前端改动**：启动服务后浏览器实测——命令回显、全屏 TUI 程序（如 `vim`、
   `python` REPL）、窗口缩放适配（resize 生效）、断线自动重连。
3. **新增行为**：尽量在 `src/main.rs` 中补充对应测试（可参考现有测试写法）。
4. **文档改动**：检查 README 引用的文件路径真实存在，命令可直接复制执行。

CI 见 `.github/workflows/ci.yml`（双平台：cargo build --release → clippy → test）。

## Pull Request 流程

1. 从 `main` 切分支，提交改动（见上文规范）。
2. 推送分支并创建 PR，使用仓库内的
   [PR 模板](.github/PULL_REQUEST_TEMPLATE.md)，逐项填写。
3. 在 PR 描述中说明：
   - 变更动机与内容；
   - 测试结果（贴出 `cargo test` / `cargo clippy` 的实际输出）；
   - **安全影响评估**：是否触及鉴权逻辑（WEBTOKEN 校验）、审计日志、
     PTY 会话生命周期或绑定地址逻辑；是否引入新的攻击面。
4. 维护者 review 后提出意见，请在讨论中回复并跟进修改；CI（如有）需保持绿色。
5. 合并前请将分支 rebase 到最新 `main`，保持提交历史线性整洁。

## 安全相关贡献

涉及以下内容的变更会被**重点审查**，请预先自评：

- `/term` 鉴权逻辑（`WEBTOKEN` 校验、close 1008 拒绝路径）——任何路径都不允许
  绕过令牌直接建立会话；
- 审计日志——每个会话结束都必须留痕（`audit.log`），不得静默失败；
- PTY 会话生命周期——连接断开必须销毁对应 ConPTY 会话，不得泄漏进程；
- 绑定与部署默认值——默认必须保持 `127.0.0.1` 等安全默认，不得默认暴露公网。

如有疑问，先在 issue 中讨论再动手，避免返工。
