# -*- coding: utf-8 -*-
"""项目规模与引用图谱：真实统计总代码行数、全量提交数、项目间引用关系。
只读 + 磁盘缓存（1 小时），禁止假数据。"""
import json
import os
import re
import subprocess
import time
from pathlib import Path

from .scanner import SKIP_DIRS, CODE_EXT, build_own_projects

ROOT = Path(r"~")
CACHE = Path(__file__).parent.parent / "data" / "graph_cache.json"
CACHE_TTL = 3600
FILE_CAP = 1500          # 每项目最多读取的代码文件数
FILE_BYTES = 300_000     # 单文件参与引用扫描的最大字节

_CACHE = {"data": None, "ts": 0}


def _git_total_commits(path: Path):
    try:
        out = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=str(path), capture_output=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        s = out.stdout.decode("utf-8", errors="replace").strip()
        if out.returncode == 0 and s.isdigit():
            return int(s)
    except Exception:
        pass
    return 0


def _walk_code_files(path: Path):
    n = 0
    stack = [path]
    while stack and n < FILE_CAP:
        cur = stack.pop()
        try:
            for entry in os.scandir(cur):
                if entry.is_dir(follow_symlinks=False):
                    if entry.name.lower() not in SKIP_DIRS and not entry.name.startswith("."):
                        stack.append(entry.path)
                elif entry.is_file(follow_symlinks=False):
                    ext = os.path.splitext(entry.name)[1].lower()
                    if ext in CODE_EXT:
                        n += 1
                        yield entry.path
        except OSError:
            continue


def build_graph():
    # 铁律：只统计董事长自己的仓库（统一自有口径，见 scanner.build_own_projects）：
    # 本机 own 减排除名单 + GitHub 远端收编。别人的开源项目绝不混进数字。
    own_all = build_own_projects()
    # 节点图只画本机有代码的（远端-only 无 loc，画出来全是空点）；
    # totals.projects 仍按全量自有清单计，与 /api/projects、/api/daily-report 三处一致。
    projects = [p for p in own_all if p.get("source") != "remote"]
    names = [p["name"] for p in projects]
    # 词边界正则：项目名中 _/- 视作词字符，避免子串误报
    patterns = {n: re.compile(rf"(?<![A-Za-z0-9_]){re.escape(n)}(?![A-Za-z0-9_])", re.I)
                for n in names}
    nodes = []
    edges = {}
    total_loc = 0
    lang_loc = {}

    for p in projects:
        base = Path(p["path"])
        loc = 0
        refs = {n: 0 for n in names if n != p["name"]}
        for fpath in _walk_code_files(base):
            fp = Path(fpath)
            try:
                if fp.stat().st_size > FILE_BYTES:
                    continue
                text = fp.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            lines = text.count("\n") + 1
            loc += lines
            low = text.lower()
            for other, pat in patterns.items():
                if other != p["name"] and other.lower() in low and pat.search(text):
                    refs[other] += 1
        total_loc += loc
        lang_loc[p["lang"]] = lang_loc.get(p["lang"], 0) + loc
        nodes.append({
            "name": p["name"], "loc": loc, "files": p["files"],
            "lang": p["lang"], "activity": p["activity"],
            "lastCommitDaysAgo": p["lastCommitDaysAgo"],
        })
        for other, cnt in refs.items():
            if cnt > 0:
                key = f"{p['name']}->{other}"
                edges[key] = {"from": p["name"], "to": other, "refs": cnt}

    total_commits = 0
    for p in projects:
        if p.get("git"):
            total_commits += _git_total_commits(Path(p["path"]))

    edge_list = sorted(edges.values(), key=lambda e: -e["refs"])
    return {
        "ok": True,
        "totals": {
            "projects": len(own_all),
            "remoteOnly": len(own_all) - len(projects),
            "loc": total_loc,
            "commits": total_commits,
            "langs": len(lang_loc),
        },
        "langLoc": sorted([{"lang": k, "loc": v} for k, v in lang_loc.items()],
                          key=lambda x: -x["loc"]),
        "nodes": sorted(nodes, key=lambda n: -n["loc"]),
        "edges": edge_list,
    }


def get_graph(force=False):
    if not force and _CACHE["data"] and time.time() - _CACHE["ts"] < CACHE_TTL:
        return _CACHE["data"]
    if not force and CACHE.exists():
        try:
            data = json.loads(CACHE.read_text(encoding="utf-8"))
            if time.time() - data.get("builtAt", 0) < CACHE_TTL:
                _CACHE["data"] = data
                _CACHE["ts"] = time.time()
                return data
        except Exception:
            pass
    data = build_graph()
    data["builtAt"] = int(time.time())
    CACHE.parent.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    _CACHE["data"] = data
    _CACHE["ts"] = time.time()
    return data
