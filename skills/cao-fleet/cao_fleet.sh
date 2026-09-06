#!/bin/bash
# cao_fleet.sh — CAO 舰队召唤/管理 CLI（自研闭源）
# 用法:
#   cao_fleet.sh probe                    探测可用 provider/profile（spawn 前必做）
#   cao_fleet.sh spawn --profile P --provider PR --count N --message "任务" [--workdir DIR] [--name PREFIX]
#   cao_fleet.sh list                     列所有 cao- 会话
#   cao_fleet.sh status <session>         会话详情（terminals 列表）
#   cao_fleet.sh say <terminal_id> <msg>  给 agent 发消息
#   cao_fleet.sh out <terminal_id>        读 agent 最新输出
#   cao_fleet.sh kill <session>           删除会话（连 tmux 一起清）
# 环境: CAO_API 默认 http://localhost:9889（Windows 侧直连 WSL 内 cao-server）
set -euo pipefail
export PYTHONIOENCODING=utf-8

API="${CAO_API:-http://localhost:9889}"

# WSL 内真实探测 binary 可执行性（provider 表 installed=true 可能是假阳性）
# 注意 < /dev/null：否则 wsl 子进程会继承管道 stdin，把 while 循环剩余输入读走导致丢行
# --version 失败（Windows shim 报 exec: node not found）时退出码非 0 → 判不可用
probe_binary() {
  local name="$1" binary="$2"
  local out="" rc=0
  out=$(MSYS_NO_PATHCONV=1 wsl -d Ubuntu-24.04 -- bash -lc "command -v '$binary' >/dev/null 2>&1 && timeout 5 '$binary' --version 2>&1" </dev/null 2>/dev/null) || rc=$?
  if [ "$rc" -eq 0 ] && [ -n "$out" ]; then
    echo "  ✓ $name 可用: $(echo "$out" | head -1)"
  else
    echo "  ✗ $name 不可用（binary 缺失、非 WSL 可执行或 --version 失败）"
  fi
}

cmd_probe() {
  echo "== providers =="
  local providers
  providers=$(curl -sf --max-time 10 "$API/agents/providers" 2>/dev/null || echo '[]')
  echo "$providers" | python -c "
import json,sys
for p in json.load(sys.stdin):
    print(f\"  {p.get('name','?'):16s} binary={p.get('binary','?')!r} installed={p.get('installed')}\")
" 2>/dev/null || echo "$providers"
  echo "== 真实可执行性探测 =="
  # MSYS 管道会把 Windows python 的输出 \n 转成 \r\n，必须 tr 掉 \r 再按 tab 分割
  echo "$providers" | python -c "
import json,sys
for p in json.load(sys.stdin):
    if p.get('installed'):
        print(f\"{p.get('name')}\t{p.get('binary','')}\")
" 2>/dev/null | tr -d '\r' | while IFS=$'\t' read -r n b; do
    [ -n "$n" ] && probe_binary "$n" "$b"
  done
  echo "== profiles =="
  curl -sf --max-time 10 "$API/agents/profiles" | python -c "
import json,sys
for p in json.load(sys.stdin):
    print(f\"  {p.get('name','?'):18s} {p.get('description','')[:60]}\")
" 2>/dev/null || curl -sf --max-time 10 "$API/agents/profiles"
}

cmd_spawn() {
  local profile="" provider="" message="" workdir="" prefix="cao" count=1
  while [ $# -gt 0 ]; do
    case "$1" in
      --profile) profile="$2"; shift 2;;
      --provider) provider="$2"; shift 2;;
      --count) count="$2"; shift 2;;
      --message) message="$2"; shift 2;;
      --workdir) workdir="$2"; shift 2;;
      --name) prefix="$2"; shift 2;;
      *) echo "未知参数: $1"; exit 1;;
    esac
  done
  [ -n "$profile" ] || { echo "缺少 --profile（如 developer/reviewer）"; exit 1; }
  [ -n "$message" ] || { echo "缺少 --message（首条任务；批量召唤必须带，否则逐个阻塞60s）"; exit 1; }
  [ "$count" -ge 1 ] 2>/dev/null || { echo "--count 须为正整数"; exit 1; }
  [ -n "$workdir" ] || workdir="/root/fleet-orchestrator"
  # 工作目录白名单校验：系统路径会被 500 拒
  case "$workdir" in
    /|/bin|/usr/bin|/etc|/var|/tmp|/root|/proc) echo "✗ 工作目录 $workdir 被 CAO 屏蔽，请用子目录"; exit 1;;
  esac

  echo "== 召唤 $count 个 agent（profile=$profile provider=${provider:-default} dir=$workdir）=="
  local fail=0
  for i in $(seq 1 "$count"); do
    local name="${prefix}-$(date +%H%M%S)-$i"
    local body="{\"initial_message\": $(python -c "import json,sys; print(json.dumps(sys.argv[1]))" "$message")}"
    echo "→ POST /sessions name=$name"
    local resp
    resp=$(curl -s --max-time 90 -X POST \
      "$API/sessions?agent_profile=$profile&session_name=$name&working_directory=$workdir${provider:+&provider=$provider}" \
      -H "Content-Type: application/json" -d "$body")
    if echo "$resp" | python -c "import json,sys; d=json.load(sys.stdin); sys.exit(0 if 'id' in d else 1)" 2>/dev/null; then
      echo "$resp" | python -c "
import json,sys
d=json.load(sys.stdin)
print(f\"  ✓ terminal_id={d.get('id')} status={d.get('status')} name={d.get('name')} session={d.get('session_name')}\")
"
    else
      echo "  ✗ 失败: $(echo "$resp" | head -c 300)"
      fail=$((fail+1))
    fi
    sleep 1
  done
  [ "$fail" -eq 0 ] || { echo "== $fail/$count 个召唤失败 ==" >&2; exit 1; }
}

cmd_list() {
  local resp
  resp=$(curl -sf --max-time 10 "$API/sessions") || { echo "错误: 无法获取会话列表（CAO server $API 不可达或无会话）" >&2; exit 1; }
  echo "$resp" | python -c "
import json,sys
rows=json.load(sys.stdin)
print(f\"共 {len(rows)} 个会话\")
for s in rows:
    print(f\"  {s.get('name','?'):32s} {s.get('status','?')}  terminals={len(s.get('terminals',[]))}\")
"
}

cmd_status() {
  [ -n "$1" ] || { echo "用法: status <session_name>"; exit 1; }
  local resp
  resp=$(curl -sf --max-time 10 "$API/sessions/$1") || { echo "错误: 会话 $1 不存在（HTTP 404 或 server 不可达）" >&2; exit 1; }
  echo "$resp" | python -c "
import json,sys
d=json.load(sys.stdin)
s=d.get('session',d)
print(f\"会话: {s.get('name')} 状态: {s.get('status','?')}\")
for t in d.get('terminals',[]):
    print(f\"  terminal_id={t.get('id')}  provider={t.get('provider','?')}  profile={t.get('agent_profile','?')}  活跃={t.get('last_active','?')}\")
"
}

cmd_say() {
  [ -n "$1" ] && [ -n "$2" ] || { echo "用法: say <terminal_id> <消息>"; exit 1; }
  local tid="$1"; shift
  local msg="$*"
  curl -sf --max-time 30 -X POST "$API/terminals/$tid/input?message=$(python -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$msg")" \
    && echo "  ✓ 已投递到 $tid"
}

cmd_out() {
  [ -n "$1" ] || { echo "用法: out <terminal_id>"; exit 1; }
  local resp
  resp=$(curl -sf --max-time 15 "$API/terminals/$1/output?mode=last") || { echo "错误: terminal $1 不存在或无输出" >&2; exit 1; }
  echo "$resp" | head -c 3000
}

cmd_kill() {
  [ -n "$1" ] || { echo "用法: kill <session_name>"; exit 1; }
  curl -sf --max-time 15 -X DELETE "$API/sessions/$1" || { echo "错误: 会话 $1 不存在（HTTP 404 或 server 不可达）" >&2; exit 1; }
  echo "  ✓ 已删除会话 $1"
}

case "${1:-}" in
  probe) cmd_probe ;;
  spawn) shift; cmd_spawn "$@" ;;
  list) cmd_list ;;
  status) cmd_status "${2:-}" ;;
  say) shift; cmd_say "$@" ;;
  out) cmd_out "${2:-}" ;;
  kill) cmd_kill "${2:-}" ;;
  *) sed -n '2,11p' "${BASH_SOURCE[0]}"; exit 1;;
esac
