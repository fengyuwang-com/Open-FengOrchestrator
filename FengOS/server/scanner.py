# -*- coding: utf-8 -*-
"""项目扫描器：扫 ~ 子目录，产出真实项目清单。只读。
另负责收编 GitHub 远端自有仓库（fengyuwang-com 名下，含私有），三处 API 统一口径。"""
import calendar
import json
import os
import re
import subprocess
import threading
import time
import urllib.request
from pathlib import Path

ROOT = Path(r"~")
SELF = ROOT / "FengOS"
CACHE_FILE = Path(__file__).parent.parent / "data" / "projects_cache.json"
REMOTE_CACHE_FILE = Path(__file__).parent.parent / "data" / "remote_repos.json"

# 明确排除名单（小写 slug）：xbtlin/ai-berkshire 非自有，违者混入计数。
OWN_EXCLUDED_SLUGS = {"ai-berkshire"}

REMOTE_OWNER = "fengyuwang-com"
REMOTE_TTL = 600  # 远端仓库清单缓存 10 分钟，过期后台线程刷新

SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", ".next", "venv", ".venv",
    "__pycache__", "target", ".gradle", "site-packages", ".idea", ".vscode",
    "coverage", ".pytest_cache", "vendor", "shots",
}
CODE_EXT = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".c", ".cpp",
    ".h", ".cs", ".vue", ".svelte", ".sh", ".ps1", ".html", ".css", ".sql",
    ".kt", ".swift", ".php", ".rb", ".lua", ".dart", ".ipynb",
}

# 扩展名 -> 完整语言名（档案卡显示用）
LANG_NAMES = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".tsx": "TSX",
    ".jsx": "JSX", ".go": "Go", ".rs": "Rust", ".java": "Java", ".c": "C",
    ".cpp": "C++", ".h": "C/C++头", ".cs": "C#", ".vue": "Vue", ".svelte": "Svelte",
    ".sh": "Shell", ".ps1": "PowerShell", ".html": "HTML", ".css": "CSS",
    ".sql": "SQL", ".kt": "Kotlin", ".swift": "Swift", ".php": "PHP",
    ".rb": "Ruby", ".lua": "Lua", ".dart": "Dart", ".ipynb": "Jupyter",
}

_MARKERS = {
    "package.json": "Node.js",
    "pyproject.toml": "Python",
    "requirements.txt": "Python",
    "Cargo.toml": "Rust",
    "go.mod": "Go",
    "pom.xml": "Java",
    "composer.json": "PHP",
}


def _load_map_descriptions():
    """从 PROJECT_MAP.md 提取 项目名 -> 一句话描述。"""
    desc = {}
    try:
        text = (ROOT / "PROJECT_MAP.md").read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return desc
    for m in re.finditer(r"\*\*(.+?)(?:/\*\*)?\s*/?\*\*\s*\|\s*(.+?)\|", text):
        name = m.group(1).strip().rstrip("/")
        d = m.group(2).strip()
        if d:
            desc[name.lower()] = d
    return desc


def _git_last_commit(path: Path):
    """返回最近提交时间戳（秒），无 git 返回 None。"""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ct"],
            cwd=str(path), capture_output=True, text=True, timeout=8,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        s = out.stdout.strip()
        if out.returncode == 0 and s.isdigit():
            return int(s)
    except Exception:
        pass
    return None


def git_recent_commits(path: Path, n: int = 3):
    """返回最近 n 条提交 [{date, summary}]，无 git 返回 []。
    Windows 下 git 输出为 UTF-8，手动解码避免 GBK 乱码。"""
    try:
        out = subprocess.run(
            ["git", "log", f"-{n}", "--date=short", "--format=%ad%x09%s"],
            cwd=str(path), capture_output=True, timeout=8,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if out.returncode != 0:
            return []
        text = out.stdout.decode("utf-8", errors="replace")
        commits = []
        for line in text.splitlines():
            line = line.strip()
            if "\t" not in line:
                continue
            d, s = line.split("\t", 1)
            if d and s:
                commits.append({"date": d, "summary": s[:120]})
        return commits
    except Exception:
        return []


def _count_files(path: Path, cap=8000):
    """统计代码文件数与总字节。跳过 node_modules 等。"""
    n = 0
    size = 0
    ext_count = {}
    stack = [path]
    while stack and n < cap:
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
                        try:
                            size += entry.stat().st_size
                        except OSError:
                            pass
                        ext_count[ext] = ext_count.get(ext, 0) + 1
        except OSError:
            continue
    return n, size, ext_count


def _dep_tags(path: Path):
    tags = []
    try:
        pkg = path / "package.json"
        if pkg.exists():
            data = json.loads(pkg.read_text(encoding="utf-8", errors="ignore"))
            for key in ("dependencies", "devDependencies"):
                for dep in list((data.get(key) or {}).keys())[:40]:
                    if dep in ("react", "vue", "next", "three", "express", "fastify",
                               "typescript", "vite", "playwright", "puppeteer", "svelte"):
                        tags.append(dep)
        py = path / "pyproject.toml"
        req = path / "requirements.txt"
        text = ""
        if py.exists():
            text = py.read_text(encoding="utf-8", errors="ignore")
        elif req.exists():
            text = req.read_text(encoding="utf-8", errors="ignore")
        for dep in ("fastapi", "flask", "django", "psutil", "playwright",
                    "openai", "pandas", "numpy", "torch", "aiohttp"):
            if re.search(rf"(?i)[\"'>=]{dep}[\"'>=\s<~]", text) or re.search(rf"(?i)^{dep}\b", text, re.M):
                tags.append(dep)
    except Exception:
        pass
    return sorted(set(tags))[:6]


def _readme_first_line(path: Path):
    for name in ("README.md", "readme.md", "Readme.md", "README.MD", "README"):
        try:
            p = path / name
            if p.exists():
                for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                    line = line.strip().lstrip("# ").strip()
                    if line and not line.startswith(("<", "![", "[!")):
                        return line[:80]
        except OSError:
            continue
    return ""


def _git_origin(path: Path):
    """返回 origin 远端 URL（小写化），无则 None。"""
    try:
        out = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=str(path), capture_output=True, text=True, timeout=8,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip().lower()
    except Exception:
        pass
    return None


# 自有仓库判定：任一 remote URL（fetch/push）归属自己的账号即算（公开数据，不涉及任何凭据）。
# 注意：remote 命中只证明"有自己账号的 remote"，最终 own 还要过 OWN_EXCLUDED_SLUGS 排除名单
# （如 xbtlin/ai-berkshire——origin 是上游 fork 源，gitee push 只是镜像，非自有项目）。
OWN_REMOTE_MARKS = ("github.com/fengyuwang-com", "gitee.com/fengyuwang-com")


def _git_all_remotes(p):
    """返回该仓库所有 remote URL 拼接文本；失败返回空串。"""
    try:
        r = subprocess.run(["git", "-C", str(p), "remote", "-v"],
                           capture_output=True, text=True, timeout=10)
        return r.stdout or ""
    except Exception:
        return ""


def _own_slugs(remote_text):
    """从 remote -v 文本提取 fengyuwang-com/xxx 的仓库名集合（小写 slug）。"""
    slugs = set()
    for line in remote_text.splitlines():
        m = re.search(r"(https?://\S+|git@\S+)", line)
        if not m:
            continue
        mm = re.search(r"fengyuwang-com/([^/.]+)", m.group(1), re.I)
        if mm:
            slugs.add(mm.group(1).lower())
    return slugs


def _repo_slug(url):
    """从远端 URL 提取 归属/仓库名，用于同名仓库去重。"""
    if not url:
        return None
    m = re.search(r"[/:]([^/:]+)/([^/]+?)(?:\.git)?/?$", url)
    return f"{m.group(1)}/{m.group(2)}".lower() if m else None


# 嵌套 git 仓发现：只向下钻非项目目录（无 README/标记文件）最多 3 层，跳过工作树/镜像区
_NESTED_DRILL_MAX = 3
_NESTED_SKIP_TOP = {"_mirror_work", "FengOS"}


def _discover_projects():
    """ROOT 一层 + 少量容器目录内嵌的 git 仓（如 ReadyO/FengClaw）。返回 (name, Path)。"""
    found = []
    seen = set()
    for name in sorted(os.listdir(ROOT)):
        p = ROOT / name
        if not p.is_dir() or name.startswith(".") or name in _NESTED_SKIP_TOP:
            continue
        found.append((name, p))
        seen.add(p.resolve())
        # 疑似"外层壳"才下钻：自身无 README 且无 .git
        has_marker = any((p / r).exists() for r in ("README.md", "readme.md", ".git"))
        if has_marker:
            continue
        try:
            subs = sorted(os.listdir(p))
        except OSError:
            continue
        for sub in subs:
            sp = p / sub
            if not sp.is_dir() or sub in SKIP_DIRS or sub.startswith("."):
                continue
            if (sp / ".git").exists() or any((sp / r).exists() for r in ("README.md", "readme.md")):
                rp = sp.resolve()
                if rp not in seen:
                    seen.add(rp)
                    found.append((f"{name} {sub}", sp))
    return found


def scan_projects():
    """扫描全仓，返回项目列表。"""
    map_desc = _load_map_descriptions()
    now = int(time.time())
    projects = []
    try:
        entries = _discover_projects()
    except OSError:
        return []
    for name, p in entries:
        if not p.is_dir():
            continue
        # 项目判定：有标记文件或 .git
        kind = None
        marker = None
        for mk, k in _MARKERS.items():
            if (p / mk).exists():
                kind, marker = k, mk
                break
        has_git = (p / ".git").exists()
        has_readme = any((p / r).exists() for r in ("README.md", "readme.md"))
        if not (kind or has_git or has_readme):
            continue
        if kind is None:
            kind = "其他" if not has_git else "Git 仓库"
        commits = _git_last_commit(p)
        nfiles, size, exts = _count_files(p)
        lang = LANG_NAMES.get(max(exts, key=exts.get), "未知") if exts else "未知"
        desc = map_desc.get(name.lower()) or _readme_first_line(p) or "（无描述）"
        # 活跃度：最近提交距今天数 -> 0-100
        if commits:
            days = max(0, (now - commits) // 86400)
            activity = max(5, 100 - days * 2) if days <= 45 else max(5, 30 - days // 10)
        else:
            days, activity = None, 5
        origin = _git_origin(p) if has_git else ""
        remotes = _git_all_remotes(p) if has_git else ""
        own_slugs = _own_slugs(remotes) - OWN_EXCLUDED_SLUGS  # 排除名单兜底（见模块头注释）
        projects.append({
            "name": name,
            "path": str(p),
            "type": kind,
            "desc": desc,
            "files": nfiles,
            "codeKB": round(size / 1024),
            "lang": lang,
            "lastCommit": commits,
            "lastCommitDaysAgo": days,
            "activity": activity,
            "deps": _dep_tags(p),
            "git": has_git,
            "own": bool(own_slugs),
            # 去重键：优先自有 slug（跨目录同名克隆合并），否则按本地目录
            "repo": sorted(own_slugs)[0] if own_slugs else None,
            "slug": sorted(own_slugs)[0] if own_slugs else None,
        })
    # 同一远端仓库在本地有多份克隆时，保留最近提交的那份
    by_repo = {}
    for p in projects:
        key = f"own:{p['slug']}" if p["slug"] else f"local:{p['name']}"
        cur = by_repo.get(key)
        if not cur or (p["lastCommit"] or 0) > (cur["lastCommit"] or 0):
            by_repo[key] = p
    projects = sorted(by_repo.values(), key=lambda x: -x["activity"])
    CACHE_FILE.parent.mkdir(exist_ok=True)
    CACHE_FILE.write_text(
        json.dumps({"scannedAt": now, "count": len(projects), "projects": projects},
                   ensure_ascii=False), encoding="utf-8")
    return projects


def load_projects(force=False):
    """带缓存的读取；缓存超过 1 小时或强制时重扫。"""
    if not force and CACHE_FILE.exists():
        try:
            data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            if time.time() - data.get("scannedAt", 0) < 3600:
                return _apply_exclusions(data["projects"])
        except Exception:
            pass
    return scan_projects()


def _apply_exclusions(projects):
    """对缓存/扫描结果兜底应用排除名单（老缓存里的 ai-berkshire 仍标 own=True）。"""
    for p in projects:
        if (p.get("slug") or "").lower() in OWN_EXCLUDED_SLUGS:
            p["own"] = False
            p["slug"] = None
            p["repo"] = None
    return projects


# ---------------------------------------------------------------------------
# 远端自有仓库收编：GitHub fengyuwang-com 名下全部仓库（含私有，gh CLI 只读，
# 失败降级匿名公开 API；10 分钟磁盘缓存 + 后台线程刷新，绝不阻塞 API）。
# ---------------------------------------------------------------------------

_remote_state = {"repos": None, "fetchedAt": 0, "refreshing": False}
_remote_lock = threading.Lock()


def _gh_remote_repos():
    """gh CLI 拉取自有账号全部仓库（含私有；只读，不碰任何凭据）。失败返回 None。"""
    try:
        out = subprocess.run(
            ["gh", "repo", "list", REMOTE_OWNER, "--limit", "300",
             "--json", "name,description,isFork,isPrivate,isArchived,updatedAt,primaryLanguage"],
            capture_output=True, timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if out.returncode != 0:
            return None
        data = json.loads(out.stdout.decode("utf-8", errors="replace"))
        return data if isinstance(data, list) else None
    except Exception:
        return None


def _api_remote_repos():
    """降级：匿名 GitHub API 拉公开仓库（分页，每页 10s 超时）。失败返回 None。"""
    repos = []
    try:
        for page in (1, 2):
            url = f"https://api.github.com/users/{REMOTE_OWNER}/repos?per_page=100&page={page}"
            req = urllib.request.Request(url, headers={"User-Agent": "FengOS"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="replace"))
            if not isinstance(data, list):
                return None
            if not data:
                break
            repos.extend(data)
    except Exception:
        return None
    return [{
        "name": r.get("name"),
        "description": r.get("description") or "",
        "isFork": bool(r.get("fork")),
        "isPrivate": False,
        "isArchived": bool(r.get("archived")),
        "updatedAt": r.get("updated_at"),
        "primaryLanguage": {"name": r["language"]} if r.get("language") else None,
    } for r in repos]


def _normalize_remote_repos(raw):
    """gh / 公开 API 两种原始结构 -> 统一字段；顺带过滤排除名单。"""
    out = []
    for r in raw:
        name = str(r.get("name") or "").strip()
        if not name or name.lower() in OWN_EXCLUDED_SLUGS:
            continue
        pl = r.get("primaryLanguage")
        lang = (pl.get("name") if isinstance(pl, dict) else pl) or "未知"
        ts = _parse_iso(r.get("updatedAt"))
        out.append({
            "slug": name.lower(),
            "name": name,
            "desc": (r.get("description") or "").strip(),
            "fork": bool(r.get("isFork")),
            "private": bool(r.get("isPrivate")),
            "archived": bool(r.get("isArchived")),
            "updatedAt": ts,
            "lang": lang,
        })
    return out


def _parse_iso(s):
    """GitHub ISO8601 UTC 时间 -> epoch 秒；解析失败返回 None。"""
    if not s:
        return None
    try:
        return int(calendar.timegm(time.strptime(str(s)[:19], "%Y-%m-%dT%H:%M:%S")))
    except (ValueError, TypeError):
        return None


def _write_remote_cache(repos):
    try:
        REMOTE_CACHE_FILE.parent.mkdir(exist_ok=True)
        REMOTE_CACHE_FILE.write_text(
            json.dumps({"fetchedAt": int(time.time()), "repos": repos},
                       ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def _refresh_remote_async():
    """后台线程刷新远端清单；带 refreshing 防抖，失败静默（下次过期再试）。"""

    def worker():
        raw = _gh_remote_repos()
        if raw is None:
            raw = _api_remote_repos()
        if raw is not None:
            repos = _normalize_remote_repos(raw)
            _remote_state["repos"] = repos
            _remote_state["fetchedAt"] = int(time.time())
            _write_remote_cache(repos)
        with _remote_lock:
            _remote_state["refreshing"] = False

    with _remote_lock:
        if _remote_state["refreshing"]:
            return
        _remote_state["refreshing"] = True
    threading.Thread(target=worker, daemon=True, name="fengos-remote-repos").start()


def get_remote_repos():
    """远端自有仓库清单（10 分钟缓存 + 后台线程刷新）。

    铁律：绝不阻塞——缓存过期先回旧值并后台刷新；完全没有数据时降级返回 []。
    """
    now = time.time()
    if _remote_state["repos"] is None and REMOTE_CACHE_FILE.exists():
        try:
            data = json.loads(REMOTE_CACHE_FILE.read_text(encoding="utf-8"))
            if isinstance(data.get("repos"), list):
                _remote_state["repos"] = _normalize_remote_repos(data["repos"])
                _remote_state["fetchedAt"] = data.get("fetchedAt", 0)
        except (OSError, ValueError):
            pass
    fresh = _remote_state["repos"] is not None and now - _remote_state["fetchedAt"] < REMOTE_TTL
    if not fresh and not _remote_state["refreshing"]:
        _refresh_remote_async()
    return _remote_state["repos"] or []


def build_own_projects():
    """统一自有口径（/api/projects、/api/graph、/api/daily-report 三处共用）：
    本机 own（已减排除名单）+ GitHub 远端 fengyuwang-com 全部仓库；同 slug 本机优先。
    远端拉不到时自动降级为只返回本机扫描结果。"""
    local = [p for p in load_projects() if p.get("own")]
    merged = {}
    for p in local:
        q = dict(p)
        q["source"] = "local"
        merged[(p.get("slug") or p["name"]).lower()] = q
    for r in get_remote_repos():
        if r["slug"] in merged:
            continue
        days = None
        activity = 5
        if r["updatedAt"]:
            days = max(0, (int(time.time()) - r["updatedAt"]) // 86400)
            activity = max(5, 100 - days * 2) if days <= 45 else max(5, 30 - days // 10)
        merged[r["slug"]] = {
            "name": r["name"],
            "path": "",
            "type": "GitHub 远端",
            "desc": r["desc"] or "（远端仓库，本机未克隆）",
            "files": 0,
            "codeKB": 0,
            "lang": r["lang"],
            "lastCommit": r["updatedAt"],
            "lastCommitDaysAgo": days,
            "activity": activity,
            "deps": [],
            "git": False,
            "own": True,
            "repo": r["slug"],
            "slug": r["slug"],
            "source": "remote",
            "private": r["private"],
            "fork": r["fork"],
            "archived": r["archived"],
            "url": f"https://github.com/{REMOTE_OWNER}/{r['name']}",
        }
    return list(merged.values())
