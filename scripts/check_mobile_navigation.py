"""REC-Y002: browser-level checks of the fixed navigation on narrow viewports.

Requires a running Streamlit app and Playwright browsers (CI-only dependency).
Does not emulate Streamlit Cloud's authenticated management overlay.
"""
import os
from io import BytesIO
from pathlib import Path

from PIL import Image

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


HOME_CHECK = """() => {
  const cards = [...document.querySelectorAll('.st-key-core_evaluate,.st-key-core_find,.st-key-core_prepare,.st-key-home_eps')];
  const rect = e => {const r=e.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom}};
  const textRect = e => {const range=document.createRange();range.selectNodeContents(e);const r=range.getBoundingClientRect();return {left:r.left,right:r.right}};
  const hero = document.querySelector('.st-key-hero');
  return {hero: !!hero, colors: {
    red:getComputedStyle(document.documentElement).getPropertyValue('--blue').trim().toLowerCase(),
    green:getComputedStyle(document.documentElement).getPropertyValue('--green').trim().toLowerCase()
  }, cards:cards.map(c => {
    const title=c.querySelector('button p,a[data-testid="stPageLink-NavLink"] p');
    const desc=c.querySelector('[data-testid="stCaptionContainer"] p');
    const icon=c.querySelector('[data-testid="stIconMaterial"]');
    return {card:rect(c), title:title && rect(title), titleText:title && textRect(title), desc:desc && rect(desc),
      icon:icon && rect(icon), direction:getComputedStyle(c).direction};
  })};
}"""



def check_hero_rim(page):
    """Check the rendered white rim on all four straight edges of the banner."""
    hero = page.locator(".st-key-hero")
    layers = hero.evaluate("""el => {
      const rim = getComputedStyle(el, '::before');
      const wave = getComputedStyle(el, '::after');
      return {width:rim.borderTopWidth, color:rim.borderTopColor,
        position:rim.position, pointer:rim.pointerEvents,
        rimZ:Number(rim.zIndex), waveZ:Number(wave.zIndex)};
    }""")
    assert layers["width"] == "2px" and layers["color"] == "rgb(255, 255, 255)", layers
    assert layers["position"] == "absolute" and layers["pointer"] == "none", layers
    assert layers["rimZ"] > layers["waveZ"], layers
    # Device scale factor is 2: the 2 CSS-pixel white rim spans about 4 image pixels.
    # Sample away from rounded corners and tolerate fractional-pixel rasterization.
    with Image.open(BytesIO(hero.screenshot(scale="device"))) as rendered:
        img = rendered.convert("RGB")
    w, h = img.size
    def white(x, y):
        return min(img.getpixel((x, y))) >= 240
    for f in (.2, .35, .5, .65, .8):
        x, y = round((w - 1) * f), round((h - 1) * f)
        bands = {
            "top": sum(white(x, k) for k in range(1, 9)),
            "bottom": sum(white(x, h - 1 - k) for k in range(1, 9)),
            "left": sum(white(k, y) for k in range(1, 9)),
            "right": sum(white(w - 1 - k, y) for k in range(1, 9)),
        }
        assert all(n >= 2 for n in bands.values()), (f, bands, img.size)


def check_home(page, label, lang):
    page.locator(".st-key-home_eps").wait_for(state="visible", timeout=60000)
    data = page.evaluate(HOME_CHECK)
    assert data["hero"] and len(data["cards"]) == 4, data
    check_hero_rim(page)
    assert data["colors"] == {"red": "#c1272d", "green": "#006233"}, data
    for item in data["cards"]:
        c, t, d, i = (item[k] for k in ("card", "title", "desc", "icon"))
        assert t and d and i, item
        assert c["left"] <= i["left"] + 1 and i["right"] <= c["right"] + 1, item
        assert c["top"] <= i["top"] + 1 and i["bottom"] <= c["bottom"] + 1, item
        assert t["bottom"] <= d["top"] + 2, item
        if lang == "ar":
            assert abs(item["titleText"]["right"] - d["right"]) <= 5, item
            assert t["right"] <= i["left"] + 2 and d["right"] <= i["left"] + 2, item
        else:
            assert abs(item["titleText"]["left"] - d["left"]) <= 5, item
            assert t["left"] >= i["right"] - 2 and d["left"] >= i["right"] - 2, item
    if label.endswith("-390"):
        target = Path("mobile-home-captures")
        target.mkdir(exist_ok=True)
        page.screenshot(path=str(target / f"{label}-{lang}.png"))


def check(page, label, lang):
    nav = page.locator(".st-key-tabbar")
    nav.wait_for(state="visible", timeout=60000)
    nav.locator('a[data-testid="stPageLink-NavLink"]').nth(4).wait_for(state="visible")
    # Check once after styles settle, and again after scrolling.
    page.wait_for_timeout(600)
    check_home(page, label, lang)
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
