# -*- coding: utf-8 -*-
"""自动化板块只读聚合：只读文件、不搬数据（两层界面原则 C1）。

每个数字都从真实文件实时读取；读不到就给 None，前端显示"—"。
本模块不提供任何写操作、不拉起进程。

对外口径：通用自动化工具 + 自进步 AI 系统（Boss-Worker 分工、
playwright 按步骤执行、经验沉淀、PDCA 闭环）。
内部文件名（如 apply_progress.json）只用于读数，不在前端展示。
音乐与数字人跑在异机，本机只读展示、不接启停。"""
import re
import time
from pathlib import Path

ROOT = Path(r"~")


def _read_json(path):
    try:
        import json
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _latest(dirpath, files=False):
    """返回 (最新名, 总数)；读不到返回 (None, 0)。"""
    try:
        items = [x for x in Path(dirpath).iterdir()
                 if (x.is_file() if files else x.is_dir())]
        if not items:
            return None, 0
        items.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return items[0].name, len(items)
    except OSError:
        return None, 0


def _count_files(dirpath, suffix=None):
    """数目录下文件个数；读不到返回 None。"""
    try:
        items = [x for x in Path(dirpath).iterdir() if x.is_file()]
        if suffix:
            items = [x for x in items if x.suffix == suffix]
        return len(items)
    except OSError:
        return None


def _count_files_recursive(dirpath, suffix):
    """递归数目录下指定后缀文件个数；读不到返回 None。"""
    try:
        return len([x for x in Path(dirpath).rglob("*" + suffix)
                    if x.is_file()])
    except OSError:
        return None


def _py_files_depth2(dirpath):
    """数目录下两层以内的 .py 文件个数；读不到返回 None。"""
    try:
        root = Path(dirpath)
        n = len([x for x in root.iterdir()
                 if x.is_file() and x.suffix == ".py"])
        for d in root.iterdir():
            if d.is_dir():
                n += len([x for x in d.iterdir()
                          if x.is_file() and x.suffix == ".py"])
        return n
    except OSError:
        return None


def get_research():
    """研究层真实只读统计：FengInvest / Search-King / AIExport / 本地 SQL 库。
    全部实时数文件；读不到就 None，前端显示"—"。不读任何凭据。"""
    # FengInvest 量化脚本（tools/ 一级 .py 实数）
    try:
        fi_scripts = len([x for x in (ROOT / "FengInvest" / "tools").iterdir()
                          if x.is_file() and x.suffix == ".py"])
    except OSError:
        fi_scripts = None

    # Search-King 旗舰：scraper.py 存在 + 反爬后端模块数（从 argparse choices 实数）
    sk = ROOT / "Search-King"
    sk_backends = None
    try:
        txt = (sk / "scraper.py").read_text(encoding="utf-8", errors="ignore")
        m = re.search(r'choices=\[([^\]]*)\]', txt)
        if m:
            n = len(re.findall(r'"[^"]+"', m.group(1)))
            sk_backends = n or None
    except OSError:
        pass
    search_king = {"has_scraper": (sk / "scraper.py").is_file(),
                   "backends": sk_backends}

    # AIExport：聚合各家 AI 输出（一层目录数 + 两层内 .py 脚本数）
    ae = ROOT / "AIExport"
    try:
        ae_dirs = len([x for x in ae.iterdir() if x.is_dir()])
    except OSError:
        ae_dirs = None
    aiexport = {"exists": ae.is_dir(), "dirs": ae_dirs,
                "scripts": _py_files_depth2(ae)}

    # 本地 SQL 建库：FengInvest/data 下真实 .db 文件实数（含快照）
    sql = _count_files_recursive(ROOT / "FengInvest" / "data", ".db")
    sql_dbs = {"count": sql}

    return {"fenginvest_scripts": {"scripts": fi_scripts},
            "search_king": search_king,
            "aiexport": aiexport,
            "sql_dbs": sql_dbs}


def get_automation():
    today = time.strftime("%Y-%m-%d")

    # 通用任务执行记录（内部读数：<private-repo> data/runtime/apply_progress.json）
    prog = _read_json(ROOT / "<private-repo>" / "data" / "runtime" / "apply_progress.json")
    if isinstance(prog, list):
        ts = [x.get("timestamp", "")[:10] for x in prog if x.get("timestamp")]
        tasks = {
            "total": len(prog),
            "done": sum(1 for x in prog if x.get("status") == "submitted"),
            "today": sum(1 for t in ts if t == today),
            "latest": max(ts) if ts else None,
        }
    else:
        tasks = {"total": None, "done": None, "today": None, "latest": None}

    # 经验沉淀：ATS 攻略数 + 可复用脚本学习记录数
    n_guides = _count_files(ROOT / "<private-repo>" / "data" / "ats-knowledge", ".md")
    learned = _read_json(ROOT / "feng-job-hunter" / "data" / "scripts" / "learned_log.json")
    n_learned = len(learned) if isinstance(learned, dict) else None
    loop = {"records": tasks["total"], "guides": n_guides, "learned": n_learned}

    # 小说采集：Novel-Scraper 章节映射 + 成品体积
    cmap = _read_json(ROOT / "Novel-Scraper" / "chapter_map.json")
    try:
        txt_mb = round((ROOT / "Novel-Scraper" /
                        "novel_离婚后_禁欲大佬爬墙偷吻小孕妻.txt").stat().st_size / 1e6, 1)
    except OSError:
        txt_mb = None
    novel = {"chapters": len(cmap) if isinstance(cmap, dict) else None, "txt_mb": txt_mb}

    # 填表执行：feng-auto-fill CLI 入口 + profiles 数
    try:
        profiles = [x for x in (ROOT / "feng-auto-fill" / "profiles").iterdir()]
        n_profiles = len(profiles)
    except OSError:
        n_profiles = None
    autofill = {
        "has_cli": (ROOT / "feng-auto-fill" / "src" / "feng_auto_fill" / "__main__.py").is_file(),
        "profiles": n_profiles,
    }

    # 桌面语音：TTS-UI 打包产物是否存在
    tts = {"has_exe": (ROOT / "TTS-UI" / "dist" / "TTS-UI.exe").is_file()}

    # 音乐生成：FengMedia tools/fengmusician 全套工具数（跑在异机 NVIDIA GPU，本机只读）
    mus_dir = ROOT / "FengMedia" / "tools" / "fengmusician"
    music = {"tools": _count_files(mus_dir, ".py"),
             "has_gate": (mus_dir / "quality_gate.py").is_file(),
             "remote": True}

    # 内容管线：FengMedia projects / published 最新
    latest_proj, n_proj = _latest(ROOT / "FengMedia" / "projects")
    latest_pub, n_pub = _latest(ROOT / "FengMedia" / "published", files=True)
    fengmedia = {"projects": n_proj, "latest_project": latest_proj,
                 "published": n_pub, "latest_published": latest_pub}

    # self-operating-computer：空壳（只有 .git）→ 规划中
    try:
        soc_files = [x.name for x in (ROOT / "self-operating-computer").iterdir()
                     if x.name != ".git"]
    except OSError:
        soc_files = None
    soc = {"planned": True, "empty": (soc_files == [])}

    # 数字人：MuseTalk 真人路线已验证（异机），动漫 VRM 线验证中；一律只读展示
    avatar = {"musetalk": "verified", "vrm": "verifying", "remote": True}

    # 自我改进中枢两仓：FengOrchestrator（AI 指挥 AI 舰队编排）与 FengASNI（多机 Profile 中枢）
    # 都是靠 MD 文档迭代自身规则的典型，只读存在性核验，不搬数据
    orch_md = _count_files(ROOT / "FengOrchestrator" / "docs", ".md")
    try:
        orch_skills = len([x for x in (ROOT / "FengOrchestrator" / "skills").iterdir() if x.is_dir()])
    except OSError:
        orch_skills = None
    orchestrator = {"exists": (ROOT / "FengOrchestrator" / "README.md").is_file(),
                    "docs": orch_md, "skills": orch_skills}
    asni_profiles = _count_files(ROOT / "FengASNI" / "Profiles")
    asni_shared = _count_files(ROOT / "FengASNI" / "Shared")
    asni = {"exists": (ROOT / "FengASNI" / "README.md").is_file(),
            "profiles": asni_profiles, "shared": asni_shared}

    return {"caps": {
        "research": get_research(),
        "novel": novel,
        "tasks": tasks,
        "loop": loop,
        "autofill": autofill,
        "tts": tts,
        "music": music,
        "fengmedia": fengmedia,
        "soc": soc,
        "avatar": avatar,
        "orchestrator": orchestrator,
        "asni": asni,
    }}
