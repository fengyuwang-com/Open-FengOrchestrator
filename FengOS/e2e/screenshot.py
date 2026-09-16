# -*- coding: utf-8 -*-
"""FengOS E2E 截图回归门（T10 / D8）。
流程：PC 1440 + 点击档案卡 + 手机 375 各截图 → 与 e2e/baseline/ 基线做像素差异对比。
稳定化：页面加 ?static=1，app.js 检测后固定 Math.random 种子并冻结动画循环/实时图表。
判定：尺寸不同直接 FAIL；逐像素容差比较（RGB 每通道差 >16 记为差异像素），差异比例 >5% FAIL，
     并输出差异区域坐标范围。基线不存在时先落基线。
用法：python e2e/screenshot.py   （PASS 退出码 0，FAIL 退出码 1）
"""
import sys
from pathlib import Path
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent.parent
OUT = ROOT / "shots"
BASE = Path(__file__).parent / "baseline"
OUT.mkdir(exist_ok=True)
URL = "http://127.0.0.1:8765/?static=1"
CH_TOL = 16        # 单通道容差
RATIO_LIMIT = 0.05 # 差异像素比例上限 5%

SHOTS = ["pc_1440.png", "pc_1440_click.png", "mobile_375.png"]

def shot(page, width, height, name):
    page.set_viewport_size({"width": width, "height": height})
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)  # 等开场动画播完（金箔豐字+标题约4秒+过渡）
    page.wait_for_function("window._planets && window._planets.length > 0", timeout=15000)
    page.screenshot(path=str(OUT / name), full_page=False)
    print("saved", OUT / name)

def main_star_xy(page):
    """主星世界坐标 -> 屏幕坐标（不点击，仅计算）"""
    return page.evaluate("""() => {
      const p = window._planets[0];           // 帝国主星（排序后第 0 个 = 最大项目）
      const v = new THREE.Vector3();
      p.mesh.getWorldPosition(v);
      v.project(window._cam);
      return { x: (v.x * 0.5 + 0.5) * innerWidth, y: (-v.y * 0.5 + 0.5) * innerHeight };
    }""")

def compare(name):
    """与基线对比，返回 (ok, 摘要)"""
    cur = OUT / name
    ref = BASE / name
    if not cur.exists():
        return False, f"{name}: 当前截图缺失"
    if not ref.exists():
        return True, f"{name}: 首跑，已存为基线"
        # caller 负责复制
    a = Image.open(ref).convert("RGB")
    b = Image.open(cur).convert("RGB")
    if a.size != b.size:
        return False, f"{name}: 尺寸不同 baseline={a.size} current={b.size} → FAIL"
    diff = ImageChops.difference(a, b)
    px = diff.getdata()
    total = len(px)
    xs, ys, ndiff = [], [], 0
    W, H = a.size
    for i, d in enumerate(px):
        if d[0] > CH_TOL or d[1] > CH_TOL or d[2] > CH_TOL:
            ndiff += 1
            xs.append(i % W); ys.append(i // W)
    ratio = ndiff / total
    bbox = f"差异区域 x[{min(xs)}~{max(xs)}] y[{min(ys)}~{max(ys)}]" if ndiff else "无差异像素"
    ok = ratio <= RATIO_LIMIT
    return ok, f"{name}: diff={ratio*100:.2f}% ({ndiff}/{total}px) {bbox} {'PASS' if ok else 'FAIL(>5%)'}"

def main():
    first_run = not (BASE / "pc_1440.png").exists()
    results, ok_all = [], True
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_page()
        shot(page, 1440, 900, "pc_1440.png")
        # 点击主星，出档案卡（点击后等弹出动画播完）
        pos = main_star_xy(page)
        page.mouse.click(pos["x"], pos["y"])
        page.wait_for_timeout(1600)
        card_visible = page.evaluate("""() => {
          const c = document.getElementById('card');
          return c && c.style.display !== 'none' && c.offsetParent !== null;
        }""")
        commits_ok = False
        try:
            page.wait_for_function(
                "document.querySelectorAll('#cardCommits .commit').length > 0", timeout=8000)
            commits_ok = True
        except Exception:
            pass
        page.screenshot(path=str(OUT / "pc_1440_click.png"), full_page=False)
        print("saved", OUT / "pc_1440_click.png", "| card_visible =", card_visible,
              "| commits =", commits_ok)
        if not card_visible:
            print("FAIL: 档案卡未出现"); b.close(); sys.exit(1)
        if not commits_ok:
            print("FAIL: 档案卡内未出现 git 提交摘要"); b.close(); sys.exit(1)
        shot(page, 375, 812, "mobile_375.png")
        b.close()

    BASE.mkdir(exist_ok=True)
    if first_run:
        for n in SHOTS:
            (OUT / n).replace(BASE / n)
            results.append(f"{n}: 首跑，已存为基线")
    else:
        for n in SHOTS:
            ok, msg = compare(n)
            results.append(msg)
            ok_all = ok_all and ok

    print("-" * 60)
    for r in results:
        print(r)
    print("PASS" if ok_all else "FAIL")
    sys.exit(0 if ok_all else 1)

if __name__ == "__main__":
    main()
