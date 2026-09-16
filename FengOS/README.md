# FengOS 统一观景台

> 2026-09-13 改版：默认界面 = **统一观景台**（蓝白简洁仪表盘，聚合各系统入口 + 今日战报 + 项目表 + 生命体征，只读铁律"只聚合不搬数据"），设计宪法见 [DESIGN.md](DESIGN.md)。旧版黑金 3D 星系降级为画册页，保留在 **/galaxy**。

## 一键启动

```bash
cd ~/FengOS
python -m uvicorn server.main:app --port 8765
```

浏览器打开 http://127.0.0.1:8765 （观景台）；画册页 http://127.0.0.1:8765/galaxy

## 开机自启（T9）

Windows 计划任务 `FengOS-Autostart`（系统启动时以用户 <user> 运行 `scripts/start_fengos.bat`，
后台最小化窗口拉起 `python -m uvicorn server.main:app --host 0.0.0.0 --port 8765`）。
注：不用 pythonw——pythonw 下 stderr 为 None，uvicorn 日志写入会崩。

防火墙放行规则：`FengOS-8765`（TCP 8765 入站允许，供 Tailscale 网内访问）。

## 回滚（一键）

```bat
schtasks /Delete /TN "FengOS-Autostart" /F
netsh advfirewall firewall delete rule name="FengOS-8765"
del ~/FengOS/scripts/start_fengos.bat
```

## 手机访问（Tailscale）

手机连上 Tailscale 后，浏览器打开 **http://100.101.102.103:8765**（本机 Tailscale IP）。
要求 uvicorn 以 `--host 0.0.0.0` 启动（start_fengos.bat 已内置）；仅限 Tailscale 内网，严禁对外发布。

## 结构

- `server/main.py` — FastAPI 入口（`/` 页面、`/api/projects`、`/api/system`、`/api/rescan`）
- `server/scanner.py` — 项目扫描器：扫 FengProj 子目录（README/package.json/.git 等判定），git log 取活跃度，PROJECT_MAP.md 取描述。缓存于 `data/projects_cache.json`（1 小时失效，`/api/rescan` 强制重扫）
- `server/probe.py` — psutil 真实探针：CPU/内存/磁盘/监听端口/Top 进程/服务探活（Immich 2283、Jellyfin 8096、PostgreSQL 5432、Tailscale 进程探测）
- `web/index.html` — 统一观景台（原生 JS，零外部依赖）
- `web/galaxy.html` + `web/app.js` — 旧版 3D 星系画册（CDN 引 GSAP/three.js/ECharts）
  - 开场：黑屏 → 金色粒子汇聚 → FENG OS 逐字 → 镜头推进（GSAP，手机端粒子减半）
  - 星系：three.js，星球大小=代码量、亮度=活跃度、连线=共同依赖，点击弹档案卡
  - 心电图：ECharts CPU/内存 5 秒刷新 + 服务状态灯
- `e2e/screenshot.py` — Playwright 双分辨率截图（1440px / 375px）→ `shots/`

## 依赖

Python 3.14+，`pip install fastapi uvicorn psutil`（国内镜像：`-i https://pypi.tuna.tsinghua.edu.cn/simple`）。截图需 playwright + chromium。

## 红线

数据全部来自本机真实扫描/探针，无假数据；仅供内网使用，严禁对外发布。
