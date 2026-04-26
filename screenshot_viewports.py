#!/usr/bin/env python3
"""Render cissp-prep.html at iPhone Pro Max + iPad viewports and screenshot
each major view, then inspect for layout issues.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path("/Users/mike/cissp")
HTML = ROOT / "cissp-prep.html"
OUT = ROOT / "screenshots"
OUT.mkdir(exist_ok=True)

# Viewports to test (logical pixels)
VIEWPORTS = {
    "iphone_15_pro_max":   {"w": 430,  "h": 932,  "scale": 3, "ua": "Mobile Safari iPhone"},
    "iphone_15_landscape": {"w": 932,  "h": 430,  "scale": 3, "ua": "Mobile Safari iPhone"},
    "ipad_pro_11":         {"w": 834,  "h": 1194, "scale": 2, "ua": "Safari iPad"},
    "ipad_pro_13":         {"w": 1032, "h": 1376, "scale": 2, "ua": "Safari iPad"},
    "iphone_se":           {"w": 375,  "h": 667,  "scale": 2, "ua": "Mobile Safari iPhone"},
}

# Views to capture (after unlocking)
VIEWS = ["dashboard", "read", "practice", "exam", "flash", "stats"]

PASSWORD = "SecureGreatness!2026"


async def capture(playwright, vp_name: str, vp: dict):
    iphone_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
    ipad_ua   = "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
    ua = iphone_ua if "iphone" in vp_name else ipad_ua
    browser = await playwright.chromium.launch(headless=True)
    ctx = await browser.new_context(
        viewport={"width": vp["w"], "height": vp["h"]},
        device_scale_factor=vp["scale"],
        user_agent=ua,
        is_mobile=True,
        has_touch=True,
    )
    page = await ctx.new_page()
    await page.goto(f"file://{HTML}", wait_until="domcontentloaded")
    # Set localStorage unlocked flag and reload (skip the gate)
    await page.evaluate("localStorage.setItem('cissp.unlocked', '1');")
    await page.reload(wait_until="domcontentloaded")
    # Pause to let app boot
    await page.wait_for_selector("#app", state="visible", timeout=5000)
    await page.wait_for_timeout(400)

    issues = []
    # Per-view screenshots + layout checks
    for view in VIEWS:
        # Click the nav button for this view if present
        nav_btn = await page.query_selector(f'nav.bottom button[data-view="{view}"]')
        if nav_btn:
            await nav_btn.click()
            await page.wait_for_timeout(300)
        out_path = OUT / f"{vp_name}__{view}.png"
        await page.screenshot(path=out_path, full_page=True)
        # Check for horizontal scroll
        h_scroll = await page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 1")
        client_w = await page.evaluate("document.documentElement.clientWidth")
        scroll_w = await page.evaluate("document.documentElement.scrollWidth")
        if h_scroll:
            issues.append(f"{vp_name}/{view}: horizontal scroll (clientW={client_w}, scrollW={scroll_w})")
        # Check for elements wider than viewport
        overflow = await page.evaluate("""
            (() => {
                const all = document.querySelectorAll('*');
                const vw = document.documentElement.clientWidth;
                const overflowing = [];
                for (const e of all){
                    const r = e.getBoundingClientRect();
                    if (r.right > vw + 2){
                        overflowing.push({tag: e.tagName, cls: e.className.toString().slice(0, 60), w: Math.round(r.width), right: Math.round(r.right)});
                    }
                }
                return overflowing.slice(0, 10);
            })();
        """)
        if overflow:
            issues.append(f"{vp_name}/{view}: {len(overflow)} overflowing elements; sample: {overflow[:3]}")
        # Check tap target sizes (Apple HIG: 44pt min; we check 36px lower bound).
        # A checkbox/radio inside a <label> inherits the label's tap area, so
        # check the LABEL's bounds for those inputs.
        if "iphone" in vp_name and vp["w"] < 600:
            small_btns = await page.evaluate("""
                (() => {
                    const all = document.querySelectorAll('button, a, input[type=checkbox], input[type=radio]');
                    const small = [];
                    for (const e of all){
                        let target = e;
                        // For checkboxes/radios, use the wrapping label's bounds.
                        if (e.tagName === 'INPUT'){
                            const lbl = e.closest('label');
                            if (lbl) target = lbl;
                        }
                        const r = target.getBoundingClientRect();
                        if (r.width === 0 && r.height === 0) continue;
                        if (r.width < 36 || r.height < 36){
                            small.push({tag: e.tagName, cls: (e.className||'').toString().slice(0, 40), w: Math.round(r.width), h: Math.round(r.height), txt: (e.textContent||'').trim().slice(0, 30)});
                        }
                    }
                    return small.slice(0, 8);
                })();
            """)
            if small_btns:
                issues.append(f"{vp_name}/{view}: {len(small_btns)} undersized tap targets <36px; sample: {small_btns[:3]}")
    await ctx.close()
    await browser.close()
    return issues


async def main():
    async with async_playwright() as p:
        all_issues = []
        for vp_name, vp in VIEWPORTS.items():
            print(f"=== {vp_name} ({vp['w']}x{vp['h']}) ===")
            issues = await capture(p, vp_name, vp)
            for i in issues:
                print("  ⚠ " + i)
            if not issues:
                print("  ✓ no issues")
            all_issues.extend(issues)
        print()
        print(f"Total issues: {len(all_issues)}")
        print(f"Screenshots in: {OUT}")


if __name__ == "__main__":
    asyncio.run(main())
