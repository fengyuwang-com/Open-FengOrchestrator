# -*- coding: utf-8 -*-
"""服务控制面：一键拉起/停止本机服务。
铁律：状态一律以端口实测为准；启动命令来自各项目侦察结果（SERVICE_CMDS），不猜。"""
import json
import os
import re
import subprocess
import time
from pathlib import Path

import psutil

OBSERVED_PORTS = [23456, 23457, 8787, 8788, 8388, 9889, 8501, 3002]
STOP_GRACE = 6          # 停止后等待端口释放的秒数
START_WAIT = 25         # 拉起后等待端口监听的秒数
LOG_DIR = Path(r"~/FengOS/logs")   # 各服务启动子进程日志目录

# name -> {port, cmd:[...], cwd, wsl:bool, env:{K:V}, env_file:str}
# cmd 全部来自实际侦察：启动脚本 / 配置文件 / 历史命令，禁止编造。
SERVICE_CMDS = {
    "FengInvest": {
        "port": 23456, "cwd": r"~/FengInvest/fengweb",
        "cmd": ["node", "dist/index.js"],
    },
    "FengMedia": {
        "port": 23457, "cwd": r"~/FengMedia/webui",
        "cmd": ["node", "dist/index.js"],
    },
    "AIExport": {
        "port": 8787, "cwd": r"~/AIExport",
        "cmd": ["python", "webui/server.py"],
    },
    "webcli": {
        "port": 8788, "cwd": r"~/FengCloud",
        "cmd": [r"~/FengCloud/feng-webcli.exe"],
        "env_file": r"~/FengNAS/FengCloudPage/term_token.env",  # TOKEN -> WEBTOKEN
        "env_rename": {"TOKEN": "WEBTOKEN"},
    },
    "FlyGo": {
        "port": 8388,
        "cmd": [r"~/FlyGo/panel/target/debug/flygo.exe"],
    },
    "CAO": {
        "port": 9889, "wsl": True,
        "cmd": ["/root/.local/bin/cao-server"],
    },
    "MoneyPrinterTurbo": {
        # 来源：~/MoneyPrinterTurbo/webui.bat
        #   L9-10 默认 MPT_WEBUI_HOST=127.0.0.1 / MPT_WEBUI_PORT=8501；
        #   L52 启动形如 streamlit run .\webui\Main.py --server.address=.. --server.port=..
        #   .venv\Scripts\python.exe 实测存在且 streamlit 1.59.1 可用。
        # 注意：webui.bat 另有 8501 被占则顺延 8502-8599 的 bat 层逻辑；
        # 这里显式 pin --server.port=8501，探针只认 8501。
        "port": 8501, "cwd": r"~/MoneyPrinterTurbo",
        "cmd": [r"~/MoneyPrinterTurbo/.venv/Scripts/python.exe",
                "-m", "streamlit", "run", r"webui\Main.py",
                "--server.address=127.0.0.1", "--server.port=8501",
                "--browser.gatherUsageStats=False",
                "--logger.hideWelcomeMessage=True",
                "--server.showEmailPrompt=False"],
    },
    "TwentyCRM": {
        # 来源：~/FengOffice/docker-compose.yml
        #   services: server/worker/db/redis；server ports "127.0.0.1:3002:3000" (L9)。
        # WSL 内 docker compose config --services 已验证服务名；
        # twenty-server-1 等 4 容器实测运行中。wsl --cd 用 Windows 风格路径已验证可用。
        # 停止不用杀端口（3002 监听者是 wslrelay.exe，杀了会误伤转发）；
        # 用 stop_cmd 做 docker compose stop。
        "port": 3002, "wsl": True, "cwd": r"~/FengOffice",
        "cmd": ["docker", "compose", "up", "-d"],
        "stop_cmd": ["docker", "compose", "stop"],
    },
}


def _load_env_file(path):
    """读 KEY=VALUE 的 env 文件，返回 dict；不打印内容。"""
    env = {}
    try:
        for line in Path(path).read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"').strip("'")
    except OSError:
        pass
    return env


LOCAL_BINDS = ("127.0.0.1", "::1", "::", "0.0.0.0")


def _is_local(addr):
    """laddr 是否绑在本机回环/通配地址。tailscaled.exe 会以 Tailscale IP
    常驻 LISTEN tailscale serve 的代理端口（如 23456/23457），后端死了端口
    依旧"在线"——只认回环/全零绑定即可把 relay 排除，也防止 stop 误杀它。"""
    return addr and addr.ip in LOCAL_BINDS


def _listening_ports():
    ports = set()
    try:
        for c in psutil.net_connections(kind="inet"):
            if c.status == psutil.CONN_LISTEN and _is_local(c.laddr):
                ports.add(c.laddr.port)
    except (psutil.AccessDenied, OSError):
        pass
    return ports


def _pids_on_port(port):
    pids = set()
    try:
        for c in psutil.net_connections(kind="inet"):
            if c.status == psutil.CONN_LISTEN and c.laddr and \
                    c.laddr.port == port and c.pid and _is_local(c.laddr):
                pids.add(c.pid)
    except (psutil.AccessDenied, OSError):
        pass
    return pids


def _spawn_async(cmd, cwd=None, env=None):
    """后台拉起：CREATE_NO_WINDOW 不弹黑窗；命令行与 stdout/stderr
    追加落到 LOG_DIR 下以 cwd（或可执行名）命名的 .log 子日志。"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    tag = Path(cwd).name if cwd else Path(cmd[1] if str(cmd[0]).lower() == "wsl" else cmd[0]).stem
    log = open(LOG_DIR / f"{tag}.log", "ab")
    log.write(f"\n===== {time.strftime('%Y-%m-%d %H:%M:%S')} :: {subprocess.list2cmdline(cmd)}\n".encode("utf-8"))
    log.flush()
    subprocess.Popen(cmd, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT,
                     creationflags=subprocess.CREATE_NO_WINDOW)
    log.close()


def service_status(name):
    cfg = SERVICE_CMDS[name]
    return cfg["port"] in _listening_ports()


_TS_MAP = {"data": None, "ts": 0.0}


def tailscale_paths():
    """tailscale serve 反代映射：本地目标端口 -> ts.net 上的路径（含监听端口）。
    返回 {本地端口: ts路径}，路径形如 ":23456" 或 "/ctrl"（443 时直接 "/"），
    供前端拼 TS_HOST；前端拿不到该映射时回退 http://<当前主机>:端口。120s 缓存。"""
    now = time.time()
    if _TS_MAP["data"] is not None and now - _TS_MAP["ts"] < 120:
        return _TS_MAP["data"]
    data = {}
    try:
        out = subprocess.run(["tailscale", "serve", "status", "--json"],
                             capture_output=True, timeout=8,
                             creationflags=subprocess.CREATE_NO_WINDOW)
        d = json.loads(out.stdout.decode("utf-8", errors="ignore") or "{}")
        for hostkey, web in (d.get("Web") or {}).items():
            listen = None
            h, _, p = hostkey.rpartition(":")
            listen = ":" + p if p and p != "443" else ""
            for path, h in (web.get("Handlers") or {}).items():
                proxy = (h or {}).get("Proxy", "")
                m = re.search(r"(?:127\.0\.0\.1|localhost):(\d+)", proxy)
                if not m:
                    continue
                local_port = int(m.group(1))
                if local_port not in data:
                    data[local_port] = listen + path.rstrip("/")
        _TS_MAP["data"] = data
        _TS_MAP["ts"] = now
    except Exception:
        pass
    return data


def start_service(name):
    """冷启动一个服务，返回 {ok, waited, error}。已在线则直接返回 ok。"""
    cfg = SERVICE_CMDS.get(name)
    if not cfg or not cfg.get("cmd"):
        return {"ok": False, "error": "no start command configured"}
    if service_status(name):
        return {"ok": True, "already": True}
    extra_env = {}
    if cfg.get("env_file"):
        extra_env.update(_load_env_file(cfg["env_file"]))
    extra_env.update(cfg.get("env") or {})
    for src, dst in (cfg.get("env_rename") or {}).items():
        if src in extra_env:
            extra_env[dst] = extra_env.pop(src)
    try:
        if cfg.get("wsl"):
            cmd = ["wsl", "--cd", cfg.get("cwd") or "~", "-e"] + cfg["cmd"]
            if extra_env:
                cmd = ["wsl", "--cd", cfg.get("cwd") or "~", "-e", "env"] + \
                      [f"{k}={v}" for k, v in extra_env.items()] + cfg["cmd"]
            _spawn_async(cmd)
        else:
            _spawn_async(cfg["cmd"], cwd=cfg.get("cwd") or None,
                         env={**os.environ, **extra_env})
    except Exception as e:
        return {"ok": False, "error": str(e)}
    deadline = time.time() + cfg.get("start_wait", START_WAIT)
    while time.time() < deadline:
        time.sleep(1.2)
        if service_status(name):
            return {"ok": True, "waited": round(cfg.get("start_wait", START_WAIT) - (deadline - time.time()), 1)}
    return {"ok": service_status(name), "waited": cfg.get("start_wait", START_WAIT),
            "error": None if service_status(name) else "port not listening after wait"}


def stop_service(name):
    """停止服务：有 stop_cmd 的走受管停止命令（如 docker compose stop），
    不碰端口进程（3002 的监听者是 wslrelay.exe 转发，杀了会误伤）；
    否则杀掉监听该端口的进程树（仅限受管端口，绝不碰别的端口）。"""
    cfg = SERVICE_CMDS.get(name)
    if not cfg:
        return {"ok": False, "error": "unknown service"}
    if cfg.get("stop_cmd"):
        try:
            if cfg.get("wsl"):
                cmd = ["wsl", "--cd", cfg.get("cwd") or "~", "-e"] + cfg["stop_cmd"]
                subprocess.run(cmd, capture_output=True, timeout=120,
                               creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.run(cfg["stop_cmd"], cwd=cfg.get("cwd") or None,
                               capture_output=True, timeout=120,
                               creationflags=subprocess.CREATE_NO_WINDOW |
                               subprocess.CREATE_NEW_PROCESS_GROUP)
        except Exception as e:
            return {"ok": False, "error": str(e)}
        deadline = time.time() + STOP_GRACE
        while time.time() < deadline:
            time.sleep(1.2)
            if not service_status(name):
                return {"ok": True}
        return {"ok": not service_status(name),
                "error": None if not service_status(name) else "port still listening after stop"}
    pids = _pids_on_port(cfg["port"])
    if not pids:
        return {"ok": True, "already": True}
    killed = []
    for pid in pids:
        try:
            p = psutil.Process(pid)
            for child in p.children(recursive=True):
                child.kill()
                killed.append(child.pid)
            p.kill()
            killed.append(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    psutil.wait_procs([psutil.Process(k) for k in killed if psutil.pid_exists(k)], timeout=STOP_GRACE)
    return {"ok": not service_status(name), "killed": killed}
