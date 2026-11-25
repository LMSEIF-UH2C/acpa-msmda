"""Cherche la règle qui fixe transform sur la barre d'onglets, et la version de Streamlit servie."""
import json, sys
from playwright.sync_api import sync_playwright
JS = """() => {
  const bar = document.querySelector('.st-key-tabbar'); if (!bar) return {absente: true};
  const cs = getComputedStyle(bar);
  const rules = [];
  for (const sheet of Array.from(document.styleSheets)) {
    let list; try { list = sheet.cssRules; } catch (e) { continue; }
    const walk = (rs, media) => { for (const r of Array.from(rs || [])) {
      if (r.cssRules && !r.selectorText) { walk(r.cssRules, (r.conditionText || r.media && r.media.mediaText || '')); continue; }
      if (!r.selectorText || !r.style) continue;
      let ok = false; try { ok = bar.matches(r.selectorText); } catch (e) {}
      if (ok && (r.style.transform || r.style.animation || r.style.animationName || r.style.translate))
        rules.push({sel: r.selectorText.slice(0, 160), transform: r.style.transform, translate: r.style.translate,
                    animation: r.style.animation || r.style.animationName, prio: r.style.getPropertyPriority('transform'), media});
    }};
    walk(list, '');
  }
  const scripts = Array.from(document.scripts).map(s => s.src).filter(Boolean).map(s => s.split('/').pop()).slice(0, 5);
  return {transform: cs.transform, translate: cs.translate, animation: cs.animationName, classes: bar.className,
          regles: rules, scripts, version: (window.__streamlit && window.__streamlit.version) || null};
}"""
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(**p.devices["iPhone 13"]); pg = ctx.new_page()
    pg.goto(sys.argv[1], wait_until="domcontentloaded", timeout=90000); pg.wait_for_timeout(12000)
    for f in [pg.main_frame] + [fr for fr in pg.frames if fr != pg.main_frame]:
        try:
            m = f.evaluate(JS)
        except Exception:
            continue
        if not m.get("absente"):
            print(json.dumps({"frame": f.url[:70], **m}, ensure_ascii=False, indent=1)); break
    b.close()
