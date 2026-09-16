# -*- coding: utf-8 -*-
"""D4 画册模式关键屏截图（自查用）：序言屏 / 项目战报屏 / 跋屏，存 shots/album_*.png。
用法：python e2e/album_shots.py   （需 uvicorn 8765 已启动）
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT = ROOT / "shots"
URL = "http://127.0.0.1:8765/?static=1&album=1"  # ?album=1 = PC 预览入口（默认关闭）

def main():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_page(viewport={"width": 375, "height": 812})
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_timeout(8000)  # 开场播完
        # 序言屏
        page.wait_for_function("document.querySelector('#album .apage')", timeout=10000)
        page.wait_for_timeout(1500)
        page.screenshot(path=str(OUT / "album_prelude.png"))
        print("saved album_prelude.png")
        # 项目战报屏（第 2 页 = 活跃度最高的项目，含懒加载提交摘要）
        page.evaluate("showAlbumPage(1, 1)")
        page.wait_for_timeout(1800)
        page.wait_for_function("document.querySelectorAll('#album .acommits .commit').length > 0", timeout=8000)
        page.wait_for_timeout(600)
        page.screenshot(path=str(OUT / "album_project.png"))
        n = page.evaluate("albumPages.length")
        proj_name = page.evaluate("albumPages[1].p.name")
        print("saved album_project.png | pages =", n, "| first project =", proj_name)
        # 跋屏（最后一页）
        page.evaluate(f"showAlbumPage({n - 1}, 1)")
        page.wait_for_timeout(1800)
        page.screenshot(path=str(OUT / "album_epilogue.png"))
        print("saved album_epilogue.png")
        # 顺带验证真实数据 + 关闭按钮回主界面
        total_files = page.evaluate("PROJECTS.reduce((a,p)=>a+p.files,0)")
        print("total files (真实接口) =", total_files)
        page.evaluate("closeAlbum()")
        page.wait_for_timeout(1200)
        closed = page.evaluate("document.getElementById('album').style.display === 'none'")
        print("closeAlbum back to main =", closed)
        b.close()
        if not closed:
            sys.exit(1)

if __name__ == "__main__":
    main()
