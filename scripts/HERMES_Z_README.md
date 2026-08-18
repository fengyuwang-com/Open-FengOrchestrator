# hermes_z.sh — Hermes 单次调用封装（ZCode / orchestrator 用）

> 目标：让外层 orchestrator 用**一条命令**驱动 Hermes 完成一个小任务，并拿到**稳定、机器可读、归一化**的结果。
> 平台：Git Bash（bash shell），不依赖 WSL，不硬编码盘符（内部用 `/c/...` 形式）。

## 用法

```bash
bash scripts/hermes_z.sh "<提示词/战略目标>"
bash scripts/hermes_z.sh -m deepseek-v4-flash "纯文本问答"
bash scripts/hermes_z.sh -w "在隔离工作树里干一个写文件+跑代码的活"
bash scripts/hermes_z.sh -u /tmp/usage.json "干完并输出 token 用量"
bash scripts/hermes_z.sh -d /some/tmp/dir "在当前工作目录写一个脚本并运行"
```

参数（选项可放在提示词前或后）：

| 参数 | 含义 |
|------|------|
| `<提示词>`（位置参数，首个非选项 token 起拼接） | 战略目标 / 任务描述，可含空格 |
| `-m MODEL` | 覆盖模型（`model=` 元数据里体现；`--provider` 沿用配置，不单独传） |
| `-w` | 开 `--worktree` 隔离工作树 |
| `-u FILE` | token 用量 JSON 写到 FILE（对应 `--usage-file`） |
| `-d DIR` | 先 `cd DIR` 再执行，作为本次任务工作目录 |
| `-h` | 用法帮助 |

## 归一化输出（机器可读）

stdout 固定包裹：

```
<FENG_HERMES_BEGIN>
ok=1                      # 1 成功 / 0 失败
exit_code=0               # Hermes 原始退出码（0/1/2）
elapsed_sec=16.989        # 耗时秒（毫秒精度）
model=deepseek-v4-flash
worktree=0
workdir=/path/to/cwd
usage_file=/tmp/usage.json
result_marker=done        # done / partial / failed
usage_json_path=/tmp/usage.json
---result-start---
<Hermes 输出内容块，即结果文本>
---result-end---
---stderr-start---        # 仅 exit_code!=0 时出现，辅助诊断
<stderr（报错）>
---stderr-end---
<FENG_HERMES_END>
```

外层解析只需取 `---result-start---` 与 `---result-end---` 之间文本；状态判据统一用 `ok` + `result_marker` + `exit_code`。
**本脚本绝不打印任何 API key / 凭据。**

## 退出码语义（归一化封装）

Hermes 自身语义 → 本脚本透传为相同退出码：

| exit_code | 封装后 result_marker | 含义 |
|-----------|----------------------|------|
| `0` | `done` | 成功，Hermes 完整产出结果内容块 |
| `1` | `failed` | 失败 / 无响应，或 Hermes 主进程异常 |
| `2` | `partial` | 部分完成 |

另外封装层自用：
| 3 | 用法错误（缺提示词 / 非法 flag / 目录不可切） |
| 4 | `hermes` 可执行文件不存在或不可执行 |

实测注意：Hermes 对"能产出内容块的报错"（如 HTTP 401 Model not supported）仍返回 `0` 并把报错作为内容块返回——这是 Hermes `-z` 功能式调用的既有行为。本脚本**如实透传、不做臆造**，因此 `exit_code` 永远是 Hermes 的真实值，外层以 `ok`+`result_marker`+`result` 内容为准。

## 调用示例（真实跑通摘录，已脱敏 key）

**样例 A — 纯文本问答**
```bash
bash scripts/hermes_z.sh "用一句话说明你今天能帮我干什么"
```
`exit_code=0, ok=1, result_marker=done`；结果块返回 "我能在这个 FengOrchestrator 项目里陪你干活……"。

**样例 B — 写文件 + 跑代码（隔离目录 + 用量）**
```bash
D=$(mktemp -d /tmp/fleet-mvp-XXXXXX)
bash scripts/hermes_z.sh -d "$D" -u "$D/usage.json" \
  "在当前工作目录写 add.py，定义 add(a,b) 并 print(add(20,22))，运行并报告结果"
rm -rf "$D"   # 用完清理
```
输出：`add.py` 写进 `$D`（非仓库）、运行得 `42`、`exit_code=0`；
`$D/usage.json` 含 token 用量：`total_tokens=283752, input_tokens=2952, output_tokens=4960, model=deepseek-v4-flash, provider=custom`。

## ZCode 如何以子进程方式调用她（一句话结论）

**ZCode 直接把整条命令当普通子进程跑即可**：
```
bash scripts/hermes_z.sh -u /tmp/u.json "<任务提示词>"
```
ZCode 读子进程 exit code 判定成败（0/1/2/3/4），再从 stdout 的 `<FENG_HERMES_BEGIN>`…`<FENG_HERMES_END>` 块里按 `ok`/`result_marker`/`exit_code` 和 `---result---` 标记截取结果文本与 token 用量，无需任何交互（Hermes `-z` 自动 auto-approve 工具）。写文件类任务务必配 `-d <临时目录>`，避免产物落进仓库。
