# -*- coding: utf-8 -*-
"""FengOS 指挥中心 FastAPI 后端。"""
import json
import subprocess
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .automation import get_automation
from .daily import get_daily_report
from .graph import get_graph
from .probe import get_system
from .scanner import build_own_projects, git_recent_commits, load_projects, scan_projects
from .services import SERVICE_CMDS, service_status, start_service, stop_service, tailscale_paths

WEB = Path(__file__).parent.parent / "web"
ROOT = Path(r"~")

REMOTE_COUNT_CACHE = Path(__file__).parent.parent / "data" / "remote_count.json"
REMOTE_COUNT_TTL = 3600  # GitHub 组织仓库数缓存 1 小时

app = FastAPI(title="FengOS", docs_url=None, redoc_url=None)


def _query_github_org_repos():
    """只读查 github.com/fengyuwang-com 组织仓库清单（复用本机 gh 登录态，不碰凭据）。"""
    out = subprocess.run(
        ["gh", "repo", "list", "fengyuwang-com", "--limit", "200",
         "--json", "name,isFork,isPrivate"],
        capture_output=True, timeout=60,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout.decode("utf-8", errors="replace"))
    except ValueError:
        return None


def get_remote_count(force=False):
    """口径注脚数据源：GitHub 自有组织仓库数 vs 本地已克隆自有仓。

    远端查不到时回退磁盘缓存（标 stale），都没有则 ok=False（前端显示—），绝不编数字。
    """
    if not force and REMOTE_COUNT_CACHE.exists():
        try:
            data = json.loads(REMOTE_COUNT_CACHE.read_text(encoding="utf-8"))
            if time.time() - data.get("fetchedAt", 0) < REMOTE_COUNT_TTL:
                return data
        except (OSError, ValueError):
            pass
    local = load_projects()
    local_slugs = {(p.get("repo") or "").split("/")[-1].lower()
                   for p in local if p.get("own") and p.get("repo")}
    local_slugs.discard("")
    repos = _query_github_org_repos()
    if repos is None:
        if REMOTE_COUNT_CACHE.exists():
            try:
                data = json.loads(REMOTE_COUNT_CACHE.read_text(encoding="utf-8"))
                data["stale"] = True
                return data
            except (OSError, ValueError):
                pass
        return {"ok": False, "localOwn": len(local_slugs)}
    remote_names = {str(r.get("name", "")).lower() for r in repos if r.get("name")}
    payload = {
        "ok": True,
        "fetchedAt": int(time.time()),
        "github": {
            "total": len(repos),
            "nonFork": sum(1 for r in repos if not r.get("isFork")),
            "fork": sum(1 for r in repos if r.get("isFork")),
            "private": sum(1 for r in repos if r.get("isPrivate")),
            "public": sum(1 for r in repos if not r.get("isPrivate")),
        },
        "localOwn": len(local_slugs),
        "matched": len(remote_names & local_slugs),
        "uncloned": len(remote_names - local_slugs),
    }
    try:
        REMOTE_COUNT_CACHE.parent.mkdir(exist_ok=True)
        REMOTE_COUNT_CACHE.write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass
    return payload


@app.get("/")
async def index():
    return FileResponse(WEB / "index.html")


@app.get("/galaxy")
async def galaxy():
    """旧版黑金 3D 画册页（已降级为展示页，见 DESIGN.md §2）。"""
    return FileResponse(WEB / "galaxy.html")


@app.get("/api/projects")
async def projects(all: bool = False):
    # 默认只返回董事长自有仓库（投资人口径）：本机 own + GitHub 远端收编（source 区分）；
    # ?all=1 才追加本机上的第三方开源。远端拉不到时自动降级为纯本机结果。
    data = build_own_projects()
    if all:
        data = data + [p for p in load_projects() if not p.get("own")]
    return JSONResponse({
        "ok": True,
        "count": len(data),
        "projects": data,
    })


@app.get("/api/rescan")
async def rescan():
    data = scan_projects()
    return JSONResponse({"ok": True, "rescanned": True, "count": len(data)})


@app.get("/api/project/{name}/commits")
async def project_commits(name: str):
    """某项目仓库最近 1~3 条 git 提交（懒加载，真实 git log）。"""
    # 防路径穿越：只允许已扫描到的项目名
    names = {p["name"]: p["path"] for p in load_projects()}
    if name not in names:
        return JSONResponse({"ok": False, "commits": []})
    p = Path(names[name])
    if not p.is_dir() or ROOT not in p.resolve().parents:
        return JSONResponse({"ok": False, "commits": []})
    return JSONResponse({"ok": True, "name": name, "commits": git_recent_commits(p, 3)})


@app.get("/api/daily-report")
async def daily_report(days: int = 1):
    """近期动态：聚合各仓库近 N 天 git 提交（5 分钟内存缓存；当日无数据回退近 7 天并标注）。"""
    days = 7 if days not in (1, 7) else days
    return JSONResponse(get_daily_report(days))


@app.get("/api/graph")
async def graph(force: bool = False):
    """项目规模与引用图谱：总代码行数/全量提交数/项目间真实引用（1 小时缓存）。"""
    return JSONResponse(get_graph(force=force))


@app.get("/api/remote-count")
async def remote_count(force: bool = False):
    """口径注脚数据源：GitHub 自有组织仓库数 vs 本地已克隆自有仓（1 小时缓存）。

    铁律：只统计自有，不把第三方拼进来；前端读不到远端时显示—，绝不编数字。
    """
    return JSONResponse(get_remote_count(force=force))


@app.get("/api/controls")
async def controls():
    """受管服务一览：端口实测在线状态 + 是否配置了启动命令。"""
    return JSONResponse({"ok": True, "services": [
        {"name": n, "port": c["port"], "online": service_status(n),
         "ts": tailscale_paths().get(c["port"]),
         "startable": bool(c.get("cmd")), "wsl": bool(c.get("wsl"))}
        for n, c in SERVICE_CMDS.items()
    ]})


@app.post("/api/service/{name}/start")
def service_start(name: str):
    """改用同步 def：FastAPI 自动放线程池跑，拉起等待不阻塞事件循环卡整页。"""
    if name not in SERVICE_CMDS:
        raise HTTPException(404, "unknown service")
    return JSONResponse(start_service(name))


@app.post("/api/service/{name}/stop")
def service_stop(name: str):
    """同步 def 同上：停止等待也放线程池。"""
    if name not in SERVICE_CMDS:
        raise HTTPException(404, "unknown service")
    return JSONResponse(stop_service(name))


@app.get("/api/automation")
async def automation():
    """自动化板块只读聚合：各能力卡数字来自真实文件，不搬数据。"""
    return JSONResponse({"ok": True, **get_automation()})


@app.get("/api/system")
async def system():
    return JSONResponse(get_system())


app.mount("/static", StaticFiles(directory=WEB), name="static")
app.mount("/wallpapers", StaticFiles(directory=WEB / "wallpapers"), name="wallpapers")
