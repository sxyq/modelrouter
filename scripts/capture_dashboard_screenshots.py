#!/usr/bin/env python3
"""capture_dashboard_screenshots.py - Captures verified browser screenshots of the live dashboard.
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ARTIFACTS_DIR = Path("/Users/sunyiyang/.gemini/antigravity/brain/da124a70-d201-482c-9053-2a7576d9eb73")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path="/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
        )
        # Use large desktop viewport (1440 x 1080)
        page = browser.new_page(viewport={"width": 1440, "height": 1080})
        
        print("Navigating to http://127.0.0.1:8765/ ...")
        page.goto("http://127.0.0.1:8765/", wait_until="networkidle")
        time.sleep(3) # Wait for initial fetch and render

        # 1. Capture Hero Cockpit & Dual Model Section (Tab 0)
        hero_png = ARTIFACTS_DIR / "v8_dual_model_dashboard_hero.png"
        page.screenshot(path=str(hero_png), full_page=False)
        print(f"Captured hero viewport screenshot: {hero_png}")

        # 2. Switch to Tab 5 (Version Lifecycle & Graphical Rails Tree)
        print("Switching to Tab 5 (版本生命周期总账与版本树)...")
        page.evaluate("switchTab(5)")
        time.sleep(2)
        
        tree_png = ARTIFACTS_DIR / "v8_dual_model_dashboard_version_tree.png"
        page.screenshot(path=str(tree_png), full_page=False)
        print(f"Captured version tree screenshot: {tree_png}")

        # 3. Capture Full Page on Tab 0
        page.evaluate("switchTab(0)")
        time.sleep(1)
        full_png = ARTIFACTS_DIR / "v8_dual_model_dashboard_tab0_full.png"
        page.screenshot(path=str(full_png), full_page=True)
        print(f"Captured full page screenshot: {full_png}")

        browser.close()
        print("All screenshots successfully captured.")

if __name__ == "__main__":
    main()
