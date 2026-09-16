# -*- coding: utf-8 -*-
"""近期动态聚合器：遍历已扫描项目缓存，对每个 .git 仓库跑 git log 聚合当日提交。
只读操作；带 5 分钟内存缓存，避免每次请求扫 58 个仓库。"""
import subprocess
import time
from pathlib import Path

from .scanner import build_own_projects

_CACHE = {"key": None, "data": None, "ts": 0}
CACHE_TTL = 300  # 5 分钟


def _git_log_since(path: Path, days: int):
    """返回 (提交数, 最新提交 {date, ts, summary})。Windows 下捕获 bytes 手动 UTF-8 解码防 GBK 乱码。"""
    try:
        out = subprocess.run(
            ["git", "log", f"--since={days} days ago",
             "--date=format:%m-%d %H:%M", "--format=%ad%x09%ct%x09%s"],
            cwd=str(path), capture_output=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if out.returncode != 0:
            return 0, None
        text = out.stdout.decode("utf-8", errors="replace")
        count = 0
        latest = None
        for line in text.splitlines():
            line = line.strip()
            if "\t" not in line:
                continue
            parts = line.split("\t", 2)
            if len(parts) < 3:
                continue
            d, ts, s = parts
            count += 1
            if latest is None and s:
                try:
                    latest = {"date": d, "ts": int(ts), "summary": s[:120]}
                except ValueError:
                    latest = {"date": d, "ts": 0, "summary": s[:120]}
        return count, latest
    except Exception:
        return 0, None


def build_daily_report(days: int = 1):
    """聚合近 days 天有提交的项目。days=1 无数据时自动回退 7 天并标注。"""
    # 投资人口径：统一自有清单（本机 own 减排除名单 + GitHub 远端收编，见 scanner.build_own_projects）
    projects = build_own_projects()
    items = []
    total = 0
    for p in projects:
        if not p.get("git"):
            continue
        path = Path(p["path"])
        if not path.is_dir():
            continue
        count, latest = _git_log_since(path, days)
        if count <= 0 or latest is None:
            continue
        total += count
        items.append({
            "name": p["name"],
            "count": count,
            "latest": latest["summary"],
            "time": latest["date"],
            "ts": latest["ts"],
        })
    items.sort(key=lambda x: -x["ts"])
    fallback = False
    if days == 1 and not items:
        return build_daily_report(7) | {"fallback": True}
    return {
        "ok": True,
        "days": days,
        "fallback": fallback,
        "totalCommits": total,
        "activeProjects": len(items),
        "scannedProjects": len(projects),
        "items": items,
    }


def get_daily_report(days: int = 1):
    """带 5 分钟内存缓存的对外入口。"""
    key = days
    now = time.time()
    if _CACHE["key"] == key and _CACHE["data"] and now - _CACHE["ts"] < CACHE_TTL:
        return _CACHE["data"]
    data = build_daily_report(days)
    _CACHE["key"] = key
    _CACHE["data"] = data
    _CACHE["ts"] = now
    return data
