#!/usr/bin/env python3
"""
cao_notify_poller.py  --  CAO 舰队「干完自动提醒 / 定点交活」自建方案（fallback）

背景：AO 的 `ao run --notify` 只能推送 *AO 自己* 的工作流结果，不监听 CAO 的 agent 产出。
      我们舰队真正要的是：CAO 里某个干事（terminal）干完了 / 收到 inbox 新消息 -> 推到群里。
      本脚本轮询 CAO 控制面（localhost:9889）每个 terminal 的 inbox，发现新消息就 POST 到 webhook。

安全纪律：
  - webhook 地址只从环境变量 CAO_WEBHOOK_URL 读取，绝不硬编码任何 token / access_token。
  - 测试可用本地监听（python3 -m http.server 或本机 nc）或 webhook.site 临时地址，绝不接真实企业机器人。
  - 不打印任何密钥；消息正文按需截断。

用法：
  export CAO_WEBHOOK_URL="http://127.0.0.1:8899/wh"   # 测试用本地监听
  python3 cao_notify_poller.py --once                 # 跑一轮（cron 用）
  python3 cao_notify_poller.py --loop --interval 30   # 常驻轮询
  python3 cao_notify_poller.py --selftest             # 只验证「推送到 webhook」这条链路

cron 示例（每天 08:00 交活）：
  0 8 * * * CAO_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=xxx /usr/bin/python3 /path/cao_notify_poller.py --once >> /var/log/cao_notify.log 2>&1
  （注意：上面的 access_token 请改用密钥管理/环境变量注入，不要明文写进 crontab）
"""
import os, sys, json, time, urllib.request, urllib.error

CAO_BASE = os.environ.get("CAO_BASE", "http://localhost:9889")
WEBHOOK_URL = os.environ.get("CAO_WEBHOOK_URL", "")
STATE_FILE = os.environ.get("CAO_STATE_FILE", "/tmp/cao_inbox_seen.json")
POLL_INTERVAL = int(os.environ.get("CAO_POLL_INTERVAL", "30"))
HTTP_TIMEOUT = 8
EXCERPT_LIMIT = 1500


def get_json(path):
    url = CAO_BASE + path
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def post_webhook(text):
    if not WEBHOOK_URL:
        print("[warn] CAO_WEBHOOK_URL 未设置，跳过推送")
        return False
    # 仿 AO：通用 {text} 形状（钉钉/飞书/企微需按域名改 msgtype，见 AO notify.ts）
    payload = json.dumps({"text": text}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        WEBHOOK_URL, data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
            body = r.read().decode("utf-8", "replace")
        print("[ok] 推送成功 HTTP %s: %s" % (r.status, body[:120]))
        return True
    except urllib.error.HTTPError as e:
        print("[warn] 推送被拒 HTTP %s: %s" % (e.code, e.read().decode("utf-8", "replace")[:200]))
        return False
    except Exception as e:
        print("[warn] 推送失败: %s" % e)
        return False


def load_seen():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()


def save_seen(seen):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(seen), f)
    except Exception as e:
        print("[warn] 无法写状态文件 %s: %s" % (STATE_FILE, e))


def normalize_message(session, term, msg):
    """把一条 inbox 消息规范成纯文本摘要（容错：字段名不确定就 dump 整个对象）。"""
    mid = msg.get("id") or msg.get("message_id") or hash(json.dumps(msg, sort_keys=True))
    sender = msg.get("from") or msg.get("sender") or msg.get("sender_name") or msg.get("sender_id") or "unknown"
    content = (msg.get("content") or msg.get("text") or msg.get("body") or msg.get("message") or "").strip()
    if not content and isinstance(msg, dict):
        content = json.dumps(msg, ensure_ascii=False)
    if len(content) > EXCERPT_LIMIT:
        content = content[:EXCERPT_LIMIT] + "…"
    text = "🔔 CAO 收件箱新消息\n会话: %s\n终端: %s\n来自: %s\n\n%s" % (session, term, sender, content)
    return mid, text


def poll_once():
    seen = load_seen()
    new_count = 0
    try:
        sessions = get_json("/sessions")
    except Exception as e:
        print("[warn] 获取 /sessions 失败: %s" % e)
        return 0
    if not isinstance(sessions, list):
        return 0
    for s in sessions:
        sname = s.get("name") or s.get("id")
        if not sname:
            continue
        try:
            terminals = get_json("/sessions/%s/terminals" % sname)
        except Exception as e:
            print("[warn] 获取 terminals 失败(%s): %s" % (sname, e))
            continue
        if not isinstance(terminals, list):
            continue
        for t in terminals:
            tid = t.get("id") or t.get("name")
            if not tid:
                continue
            try:
                inbox = get_json("/terminals/%s/inbox/messages" % tid)
            except Exception as e:
                continue
            msgs = inbox if isinstance(inbox, list) else inbox.get("messages", [])
            for m in msgs:
                mid, text = normalize_message(sname, tid, m)
                key = "%s/%s/%s" % (sname, tid, mid)
                if key in seen:
                    continue
                seen.add(key)
                new_count += 1
                post_webhook(text)
    save_seen(seen)
    return new_count


def selftest():
    if not WEBHOOK_URL:
        print("[error] 请先设置 CAO_WEBHOOK_URL")
        return 1
    ok = post_webhook("🔧 cao_notify_poller 自检：推送链路正常（这是一条测试消息，可忽略）")
    return 0 if ok else 1


def main():
    args = sys.argv[1:]
    if "--selftest" in args:
        return selftest()
    if "--once" in args:
        n = poll_once()
        print("[info] 本轮新增消息 %d 条" % n)
        return 0
    # default: loop
    print("[info] 常驻轮询 CAO=%s 间隔=%ss" % (CAO_BASE, POLL_INTERVAL))
    while True:
        try:
            n = poll_once()
            if n:
                print("[info] 推送 %d 条新消息 @ %s" % (n, time.strftime("%H:%M:%S")))
        except Exception as e:
            print("[warn] 轮询异常: %s" % e)
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    sys.exit(main())
