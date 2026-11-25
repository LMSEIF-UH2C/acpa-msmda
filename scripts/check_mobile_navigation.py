"""REC-Y002: browser-level checks of the fixed navigation on narrow viewports.

Requires a running Streamlit app and Playwright browsers (CI-only dependency).
Does not emulate Streamlit Cloud's authenticated management overlay.
"""
import os

from playwright.sync_api import sync_playwright

URL = os.environ.get("ACPA_TEST_URL", "http://127.0.0.1:8501")
WIDTHS = (320, 375, 390, 414, 430)
LANGUAGES = ("fr", "ar", "en")

CHECK = """() => {
  const bar = document.querySelector('.st-key-tabbar');
  const links = [...bar.querySelectorAll('a[data-testid="stPageLink-NavLink"]')];
  const v = window.visualViewport;
  const viewport = {left: v?.offsetLeft || 0, width: v?.width || innerWidth,
                    top: v?.offsetTop || 0, height: v?.height || innerHeight};
  const rect = e => {
    const r = e.getBoundingClientRect();
    return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,
            width:r.width,height:r.height};
  };
  return {viewport, bar:rect(bar), links:links.map(e => {
    const r = rect(e);
    const hit = document.elementFromPoint((r.left+r.right)/2,(r.top+r.bottom)/2);
    return {...r, clickable: !!hit && e.contains(hit)};
  }), position:getComputedStyle(bar).position, direction:getComputedStyle(bar).direction};
}"""


def check(page, label, lang):
    nav = page.locator(".st-key-tabbar")
    nav.wait_for(state="visible", timeout=60000)
    nav.locator('a[data-testid="stPageLink-NavLink"]').nth(4).wait_for(state="visible")
    # Check once after styles settle, and again after scrolling.
    page.wait_for_timeout(600)
    for phase in ("initial", "scrolled"):
        if phase == "scrolled":
            page.locator('[data-testid="stMain"]').evaluate(
                "(el) => el.scrollTop = el.scrollHeight"
            )
            page.wait_for_timeout(150)
        data = page.evaluate(CHECK)
        v, b = data["viewport"], data["bar"]
        prefix = f"{label} {lang} {phase}: {data}"
        assert data["position"] == "fixed", prefix
        assert data["direction"] == ("rtl" if lang == "ar" else "ltr"), prefix
        assert len(data["links"]) == 5, prefix
        assert b["left"] >= v["left"] - 1 and b["right"] <= v["left"] + v["width"] + 1, prefix
        assert abs((b["left"] + b["right"])/2 - (v["left"] + v["width"]/2)) <= 2, prefix
        assert b["top"] >= v["top"] - 1 and b["bottom"] <= v["top"] + v["height"] + 1, prefix
        for r in data["links"]:
            assert r["left"] >= b["left"] - 1 and r["right"] <= b["right"] + 1, prefix
            assert r["top"] >= b["top"] - 1 and r["bottom"] <= b["bottom"] + 1, prefix
            assert r["width"] >= 24 and r["height"] >= 44 and r["clickable"], prefix
    print(f"PASS {label} {lang}", flush=True)


def main():
    with sync_playwright() as p:
        for engine in (p.chromium, p.webkit):
            browser = engine.launch()
            for width in WIDTHS:
                for lang in LANGUAGES:
                    page = browser.new_page(viewport={"width":width,"height":844},
                                            device_scale_factor=2, has_touch=True,
                                            is_mobile=True)
                    page.goto(f"{URL}/?lang={lang}", wait_until="domcontentloaded")
                    check(page, f"{engine.name}-{width}", lang)
                    page.close()
            browser.close()


if __name__ == "__main__":
    main()
