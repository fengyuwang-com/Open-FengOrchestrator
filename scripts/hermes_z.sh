#!/usr/bin/env bash
#
# hermes_z.sh
# ============================================================================
# Hermes Agent 一键单次调用封装（oneshot / -z），供 ZCode / 外层 orchestrator
# 用一条命令驱动 Hermes 完成一个小任务，并拿到稳定的、机器可读的结果。
#
# 用法（在 Git Bash 下直接运行）：
#   bash scripts/hermes_z.sh "战略目标提示词"
#   bash scripts/hermes_z.sh -m deepseek-v4-flash "文字问答"
#   bash scripts/hermes_z.sh -w "在隔离工作树里写文件并跑代码"
#   bash scripts/hermes_z.sh -u /tmp/usage.json "产出用法统计"
#   bash scripts/hermes_z.sh -d /path/to/dir "在该目录下干活"
#   bash scripts/hermes_z.sh -s "隔离安全模式（临时 HERMES_HOME + 安全参数）"
#   bash scripts/hermes_z.sh -L logs/fleet "每次调用归集记录到 logs/fleet/fleet.tsv"
#
# 参数：
#   $1            提示词 / 战略目标（可含空格，整个引用即可）
#   -m MODEL      覆盖模型（配合默认 provider；默认读取 Hermes 配置）
#   -w            开启 --worktree 隔离工作树（hermes 自建临时目录）
#   -u FILE       将 token 用量 JSON 写到 FILE（对应 hermes --usage-file）
#   -d DIR        先 cd 到 DIR 再执行，作为本次任务工作目录
#   -s            隔离安全模式：mktemp -d 建临时 HERMES_HOME，经 HERMES_HOME
#                 环境变量传给 hermes（CLI 无 --home 参数，仅支持该环境变量），
#                 并追加安全参数 --safe-mode 与 -t safe（工具白名单：web +
#                 vision + image_gen，无 terminal）。输出块标记 safe=1。
#                 注意：临时 HOME 无任何凭据，若 hermes 因此重新认证失败，
#                 错误会原样出现在 stderr，本脚本不绕过。
#   -L DIR        归集日志目录（默认 logs/fleet/，相对仓库根）。每次调用追加
#                 一行到 DIR/fleet.tsv（制表符分隔：ISO 时间、任务摘要前 40
#                 字符、ok、exit_code、elapsed_sec、total_tokens 若有；文件
#                 不存在时先写表头）；若给了 -u，把 usage json 复制为
#                 DIR/usage-<时间戳>.json。
#
# 归一化输出（机器可读，供外层解析）：
#   <FENG_HERMES_BEGIN>
#   ... 关键元数据键值对（key=value）...
#   ... 结果文本 / 失败说明（含关键字标记，帮助判别）...
#   <FENG_HERMES_END>
#
# 退出码语义（与 hermes -z 对齐，归一化）：
#   0  成功（hermes 主进程完整跑完）
#   1  失败 / 无响应（hermes 报错、超时或主进程异常）
#   2  部分完成（hermes 返回部分完成）
#   3  用法错误（参数缺失 / 非法 flag）
#   4  hermes 可执行文件不存在或不可执行
#
# 注意：
#   * 从不打印任何 API key / 敏感凭据。
#   * 不硬编码 Windows 盘符，使用 /c/... 或 cygpath 形式路径。
#   * 绝不修改 hermes 的 config.yaml；-s 仅通过环境变量与命令行参数隔离。
# ============================================================================

set -u

# 仓库根 = scripts/ 的上一级
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 优先用 PATH 里的 hermes；否则回退到本机绝对路径
if [ -x "${HERMES_BIN:-}" ]; then :; else
    HERMES_BIN="$(command -v hermes 2>/dev/null)" || true
    [ -z "${HERMES_BIN:-}" ] && HERMES_BIN="/c/Users/yourusername/AppData/Local/hermes/hermes-agent/venv/Scripts/hermes"
fi

usage() {
    local s="$(basename "$0")"
    cat <<EOF
用法: bash $s [选项] "<提示词/战略目标>"

选项:
  -m MODEL   覆盖模型（默认读取 Hermes 配置）
  -w         开启 --worktree 隔离工作树
  -u FILE    token 用量 JSON 输出到 FILE
  -d DIR     先切换到 DIR 目录再执行
  -s         隔离安全模式（临时 HERMES_HOME + --safe-mode + -t safe 白名单）
  -L DIR     归集日志目录（默认 logs/fleet/，相对仓库根）
  -h         显示本帮助

示例:
  bash $s "用一句话说明你今天能帮我干什么"
  bash $s -w "在隔离工作树里写一个 hello.py 并运行"
  bash $s -u /tmp/usage.json "跑一个任务并输出 token 用量"
  bash $s -s "在隔离安全模式下跑一个任务"
  bash $s -L /tmp/fleetlog "跑一个任务并归集记录"
EOF
}

# ---------- 参数解析（-z 提示词必须是第一个位置参数） ----------
MODEL=""
WORKTREE=0
USAGE_FILE=""
WORKDIR=""
PROMPT=""
SAFE=0
LOGDIR=""

# 柔性解析：选项可放在提示词之前或之后。首个非选项 token 起拼成提示词。
while [ $# -gt 0 ]; do
    case "$1" in
        -m) MODEL="${2:-}"; [ -z "$MODEL" ] && { usage; exit 3; }; shift 2 ;;
        -w) WORKTREE=1; shift ;;
        -u) USAGE_FILE="${2:-}"; [ -z "$USAGE_FILE" ] && { usage; exit 3; }; shift 2 ;;
        -d) WORKDIR="${2:-}"; [ -z "$WORKDIR" ] && { usage; exit 3; }; shift 2 ;;
        -s) SAFE=1; shift ;;
        -L) LOGDIR="${2:-}"; [ -z "$LOGDIR" ] && { usage; exit 3; }; shift 2 ;;
        -h|--help) usage; exit 3 ;;
        -*)
            echo "[FENG_HERMES] 未知参数: $1" >&2
            usage; exit 3
            ;;
        *)
            # 首个非选项 token 起拼成提示词（其余位置参数用空格连接）
            if [ -z "$PROMPT" ]; then
                PROMPT="$1"
            else
                PROMPT="$PROMPT $1"
            fi
            shift
            ;;
    esac
done

# 无提示词则显示帮助
if [ -z "${PROMPT:-}" ]; then
    usage
    exit 3
fi

# -u 的 MSYS 绝对路径（/tmp/...、/c/...）须转为 Windows 路径再传给原生
# Windows 的 hermes.exe，否则文件会落到 C:\tmp\... 等错位位置（Windows
# Python 不识别 MSYS 路径）。相对路径行为不变（hermes 相对自身 cwd 解析）。
if [ -n "$USAGE_FILE" ] && [ "${USAGE_FILE#/}" != "$USAGE_FILE" ] && command -v cygpath >/dev/null 2>&1; then
    USAGE_FILE="$(cygpath -w "$USAGE_FILE" 2>/dev/null || echo "$USAGE_FILE")"
fi

# ---------- 归集日志：字段与目录（调用前固定，供各退出路径使用） ----------
ISO_TIME="$(date +%Y-%m-%dT%H:%M:%S%z 2>/dev/null || date +%Y-%m-%dT%H:%M:%S)"
# 任务摘要：换行/制表符折叠为空格，取前 40 字符（保证 TSV 列不串位）
SUMMARY="$(printf '%s' "$PROMPT" | tr '\r\n\t' ' ' | cut -c1-40)"

# 目录解析：-L 传绝对路径（/... 或 C:\...）则原样使用；相对路径相对仓库根
if [ -z "$LOGDIR" ]; then
    LOGDIR="$REPO_ROOT/logs/fleet"
elif [ "${LOGDIR#/}" = "$LOGDIR" ] && [ "${LOGDIR:1:1}" != ":" ]; then
    LOGDIR="$REPO_ROOT/$LOGDIR"
fi

LOGDIR_OK=0
if mkdir -p "$LOGDIR" 2>/dev/null; then
    LOGDIR_OK=1
else
    echo "[FENG_HERMES] 警告: 无法创建归集日志目录: $LOGDIR（本次跳过日志）" >&2
fi

# 追加一行归集记录；文件不存在时先写表头（列名同字段语义）
fleet_log() {
    local ok="$1" code="$2" elapsed="$3" tokens="$4"
    [ "$LOGDIR_OK" -eq 1 ] || return 0
    local f="$LOGDIR/fleet.tsv"
    [ -f "$f" ] || printf 'iso_time\tsummary\tok\texit_code\telapsed_sec\ttotal_tokens\n' > "$f"
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$ISO_TIME" "$SUMMARY" "$ok" "$code" "$elapsed" "$tokens" >> "$f" 2>/dev/null || true
}

# ---------- 前置检查：hermes 可执行 ----------
if [ ! -x "$HERMES_BIN" ]; then
    echo "[FENG_HERMES] hermes 可执行文件不存在或不可执行: $HERMES_BIN" >&2
    fleet_log 0 4 0.000 ""
    echo "<FENG_HERMES_BEGIN>"
    echo "ok=0"
    echo "error=hermes_binary_not_found"
    echo "hermes_bin=$HERMES_BIN"
    echo "<FENG_HERMES_END>"
    exit 4
fi

# 若指定 -d，先切换工作目录
if [ -n "$WORKDIR" ]; then
    if ! cd "$WORKDIR" 2>/dev/null; then
        echo "[FENG_HERMES] 无法切换到工作目录: $WORKDIR" >&2
        fleet_log 0 3 0.000 ""
        echo "<FENG_HERMES_BEGIN>"
        echo "ok=0"
        echo "error=workdir_not_found"
        echo "workdir=$WORKDIR"
        echo "<FENG_HERMES_END>"
        exit 3
    fi
fi

# ---------- 隔离安全模式：临时 HERMES_HOME ----------
SAFE_HOME=""
if [ "$SAFE" -eq 1 ]; then
    SAFE_HOME_UNIX="$(mktemp -d 2>/dev/null)"
    if [ -z "$SAFE_HOME_UNIX" ] || [ ! -d "$SAFE_HOME_UNIX" ]; then
        echo "[FENG_HERMES] 无法创建临时 HERMES_HOME（mktemp -d 失败）" >&2
        fleet_log 0 1 0.000 ""
        echo "<FENG_HERMES_BEGIN>"
        echo "ok=0"
        echo "error=safe_home_mktemp_failed"
        echo "safe=1"
        echo "<FENG_HERMES_END>"
        exit 1
    fi
    # Git Bash 的 /tmp/... 是 MSYS 映射路径，须转成 Windows 绝对路径再传给
    # 原生 Windows 的 hermes.exe，否则 Python 侧 os.environ 解析会错位
    if command -v cygpath >/dev/null 2>&1; then
        SAFE_HOME="$(cygpath -w "$SAFE_HOME_UNIX" 2>/dev/null || echo "$SAFE_HOME_UNIX")"
    else
        SAFE_HOME="$SAFE_HOME_UNIX"
    fi
fi

# ---------- 组装 hermes 参数 ----------
HERMES_ARGS=(-z "$PROMPT")
[ "$WORKTREE" -eq 1 ] && HERMES_ARGS+=(--worktree)
[ -n "$MODEL" ] && HERMES_ARGS+=(-m "$MODEL")
[ -n "$USAGE_FILE" ] && HERMES_ARGS+=(--usage-file "$USAGE_FILE")

# 安全模式追加的 CLI 安全参数（hermes --help 实证）：
#   --safe-mode   禁用全部自定义：用户 config、AGENTS.md/memory 注入、插件、MCP
#                 （隐含 --ignore-user-config 与 --ignore-rules）
#   -t safe       工具白名单：内置 safe toolset = web + vision + image_gen，无 terminal
SAFE_ENV=()
if [ "$SAFE" -eq 1 ]; then
    HERMES_ARGS+=(--safe-mode -t safe)
    SAFE_ENV+=("HERMES_HOME=$SAFE_HOME")
fi

# ---------- 执行并计时 ----------
# 分别捕获 stdout（结果内容块）与 stderr（报错），便于下面归一化输出
STDOUT_FILE="/tmp/hermes_z_stdout.$$"
STDERR_FILE="/tmp/hermes_z_stderr.$$"
START_NS=$(date +%s%N)
env "${SAFE_ENV[@]}" "$HERMES_BIN" "${HERMES_ARGS[@]}" >"$STDOUT_FILE" 2>"$STDERR_FILE"
RC=$?
END_NS=$(date +%s%N)

# 计算耗时（秒，毫秒精度），Git Bash /bin/date 下兼容
elapsed_ms=$(( (END_NS - START_NS) / 1000000 ))
elapsed_sec=$(awk -v m="$elapsed_ms" 'BEGIN{printf "%.3f", m/1000}')

STDOUT_RAW=$(cat "$STDOUT_FILE" 2>/dev/null)
STDERR_RAW=$(cat "$STDERR_FILE" 2>/dev/null)
rm -f "$STDOUT_FILE" "$STDERR_FILE"

# ---------- 归集记录：fleet.tsv 一行 + usage json 副本 ----------
TOTAL_TOKENS=""
if [ -n "$USAGE_FILE" ] && [ -f "$USAGE_FILE" ]; then
    # 从 usage json 提取 total_tokens（缺失 / null 时为空字符串）
    TOTAL_TOKENS="$(grep -o '"total_tokens"[[:space:]]*:[[:space:]]*[0-9]*' "$USAGE_FILE" 2>/dev/null | head -1 | grep -o '[0-9]*$')"
    if [ "$LOGDIR_OK" -eq 1 ]; then
        # 时间戳与本次调用 ISO 时间同源（去符号），便于与 fleet.tsv 行关联；
        # 注意 tr 集合中 '-' 必须放最后，否则 Git Bash 的 tr 会当作范围报错
        USAGE_TS="$(printf '%s' "$ISO_TIME" | tr -d ':+-')"
        cp "$USAGE_FILE" "$LOGDIR/usage-${USAGE_TS}.json" 2>/dev/null || true
    fi
fi
fleet_log "$([ "$RC" -eq 0 ] && echo 1 || echo 0)" "$RC" "$elapsed_sec" "$TOTAL_TOKENS"

# ---------- 归一化输出 ----------
if [ "$RC" -eq 0 ]; then RESULT_MARKER="done"; elif [ "$RC" -eq 2 ]; then RESULT_MARKER="partial"; else RESULT_MARKER="failed"; fi
echo "<FENG_HERMES_BEGIN>"
echo "ok=$([ "$RC" -eq 0 ] && echo 1 || echo 0)"
echo "exit_code=$RC"
echo "elapsed_sec=$elapsed_sec"
echo "model=${MODEL:-<default>}"
echo "worktree=$WORKTREE"
echo "workdir=${WORKDIR:-$(pwd)}"
echo "usage_file=${USAGE_FILE:-<none>}"
echo "safe=$SAFE"
[ "$SAFE" -eq 1 ] && echo "safe_home=$SAFE_HOME"
echo "logdir=$LOGDIR"
echo "result_marker=$RESULT_MARKER"
# token 用量摘要（若提供了 --usage-file 且文件存在，脱敏打印简要统计）
if [ -n "$USAGE_FILE" ] && [ -f "$USAGE_FILE" ]; then
    echo "usage_json_path=$USAGE_FILE"
else
    echo "usage_json_path=<none>"
fi
echo "---result-start---"
echo "$STDOUT_RAW"
echo "---result-end---"
# 仅在退出码非 0 时附带 stderr 便于诊断；成功时内容块在 stdout 已含，不刷屏
if [ "$RC" -ne 0 ] && [ -n "$STDERR_RAW" ]; then
    echo "---stderr-start---"
    echo "$STDERR_RAW"
    echo "---stderr-end---"
fi
echo "<FENG_HERMES_END>"

exit "$RC"
