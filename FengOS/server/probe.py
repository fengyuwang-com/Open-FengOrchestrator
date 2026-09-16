# -*- coding: utf-8 -*-
"""系统探针：psutil 真实数据，禁止假数据。"""
import socket
import threading
import time
from collections import deque

import psutil

# 服务状态灯：名称 -> 端口（本机探活）
SERVICES = {
    "Immich": 2283,
    "Jellyfin": 8096,
    "PostgreSQL": 5432,
    "Tailscale": None,  # 特判：无固定本地监听端口，尝试 41641/ UDP 不可 TCP 探，改为进程探测
}


def _port_open(port, host="127.0.0.1", timeout=0.3):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _proc_alive(keyword):
    for p in psutil.process_iter(["name"]):
        try:
            if keyword.lower() in (p.info["name"] or "").lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


# ============ CPU/内存历史采样（后台线程每 1.2s 一拍，预热 30 点，心电图开屏即有形态） ============
HIST_LEN = 30
_hist_ts = deque(maxlen=HIST_LEN)
_hist_cpu = deque(maxlen=HIST_LEN)
_hist_mem = deque(maxlen=HIST_LEN)
_hist_lock = threading.Lock()


def _sample_once():
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory().percent
    with _hist_lock:
        _hist_ts.append(int(time.time() * 1000))
        _hist_cpu.append(round(cpu, 1))
        _hist_mem.append(round(mem, 1))


def _start_history_thread():
    def _loop():
        while True:
            try:
                _sample_once()
            except Exception:
                pass
            time.sleep(1.2)
    t = threading.Thread(target=_loop, daemon=True, name="fengos-probe-history")
    t.start()


_start_history_thread()


def get_system():
    cpu = psutil.cpu_percent(interval=0.15)
    mem = psutil.virtual_memory()
    disks = psutil.disk_usage("C:\\")
    # 监听端口
    listeners = {}
    try:
        for c in psutil.net_connections(kind="inet"):
            if c.status == psutil.CONN_LISTEN and c.laddr:
                listeners[c.laddr.port] = True
    except (psutil.AccessDenied, OSError):
        pass
    ports = sorted(listeners.keys())
    # CPU 占用 Top 进程
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent"]):
        try:
            procs.append({
                "pid": p.info["pid"],
                "name": (p.info["name"] or "")[:32],
                "cpu": p.info["cpu_percent"] or 0.0,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    top = sorted(procs, key=lambda x: -x["cpu"])[:10]
    # 服务状态灯
    services = {}
    for name, port in SERVICES.items():
        if port is not None:
            services[name] = _port_open(port)
        else:
            services[name] = _proc_alive("tailscaled") or _port_open(41641, host="100.100.100.100")
    with _hist_lock:
        history = {"ts": list(_hist_ts), "cpu": list(_hist_cpu), "mem": list(_hist_mem)}
    return {
        "ts": int(time.time() * 1000),
        "cpu": cpu,
        "history": history,
        "cpuCores": psutil.cpu_count(),
        "mem": mem.percent,
        "memUsedGB": round(mem.used / 1e9, 2),
        "memTotalGB": round(mem.total / 1e9, 2),
        "diskC": disks.percent,
        "listenPorts": ports,
        "portCount": len(ports),
        "procCount": len(procs),
        "topProcs": top,
        "services": services,
    }
