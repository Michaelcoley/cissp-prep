#!/usr/bin/env python3
"""Capture viewport-only (above-the-fold) screenshots to see exactly what
the user sees on first load on each device."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path("/Users/mike/cissp")
HTML = ROOT / "cissp-prep.html"
OUT = ROOT / "screenshots_fold"
OUT.mkdir(exist_ok=True)

VIEWPORTS = {
    "iphone_15_pro_max":   {"w": 430,  "h": 932,  "scale": 3, "is_mobile": True},
    "iphone_15_landscape": {"w": 932,  "h": 430,  "scale": 3, "is_mobile": True},
    "ipad_pro_11_portrait":{"w": 834,  "h": 1194, "scale": 2, "is_mobile": True},
    "ipad_pro_11_land":    {"w": 1194, "h": 834,  "scale": 2, "is_mobile": True},
    "ipad_pro_13_portrait":{"w": 1032, "h": 1376, "scale": 2, "is_mobile": True},
    "iphone_se":           {"w": 375,  "h": 667,  "scale": 2, "is_mobile": True},
}
VIEWS = ["dashboard", "read", "practice", "exam", "flash", "stats"]
iphone_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
ipad_ua   = "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"


async def capture(playwright, vp_name: str, vp: dict):
    ua = iphone_ua if "iphone" in vp_name else ipad_ua
    browser = await playwright.chromium.launch(headless=True)
    ctx = await browser.new_context(
        viewport={"width": vp["w"], "height": vp["h"]},
        device_scale_factor=vp["scale"],
        user_agent=ua,
        is_mobile=vp["is_mobile"],
        has_touch=vp["is_mobile"],
    )
    page = await ctx.new_page()
    await page.goto(f"file://{HTML}", wait_until="domcontentloaded")
    await page.evaluate("localStorage.setItem('cissp.unlocked', '1');")
    await page.reload(wait_until="domcontentloaded")
    await page.wait_for_selector("#app", state="visible", timeout=5000)
    await page.wait_for_timeout(500)
    for view in VIEWS:
        nav = await page.query_selector(f'nav.bottom button[data-view="{view}"]')
        if nav:
            await nav.click()
            await page.wait_for_timeout(400)
        out_path = OUT / f"{vp_name}__{view}.png"
        # full_page=False = viewport screenshot only
        await page.screenshot(path=out_path, full_page=False)
    await ctx.close()
    await browser.close()


async def main():
    async with async_playwright() as p:
        for vp_name, vp in VIEWPORTS.items():
            print(f"=== {vp_name} ({vp['w']}x{vp['h']}) ===")
            await capture(p, vp_name, vp)
        print(f"Done. Screenshots in {OUT}")


if __name__ == "__main__":
    asyncio.run(main())
