"""Mesure la barre d'onglets sur iPhone 13 émulé, avec Chromium et WebKit : position, transformation, recouvrement."""
import json, sys
from playwright.sync_api import sync_playwright
URL = sys.argv[1]
OUT = sys.argv[2]
JS = """() => {
  const bar = document.querySelector('.st-key-tabbar');
  if (!bar) return {absente: true};
  const r = bar.getBoundingClientRect(); const cs = getComputedStyle(bar);
  const chain = []; let el = bar.parentElement;
  while (el && chain.length < 40) { const c = getComputedStyle(el);
    if (c.transform !== 'none' || c.filter !== 'none' || c.backdropFilter !== 'none' || c.willChange.includes('transform') || c.contain.includes('paint') || c.perspective !== 'none')
      chain.push({tag: el.tagName, testid: el.getAttribute('data-testid'), cls: (el.className||'').toString().slice(0,60), transform: c.transform, filter: c.filter, backdrop: c.backdropFilter, willChange: c.willChange, contain: c.contain});
    el = el.parentElement; }
  return {gauche: Math.round(r.left), droite: Math.round(r.right), largeur: Math.round(r.width), bas: Math.round(r.bottom),
          fenetre: window.innerWidth, hauteur: window.innerHeight, transform: cs.transform, left: cs.left, position: cs.position,
          largeur_doc: document.documentElement.scrollWidth, ancetres_qui_creent_un_bloc: chain};
}"""
res = {}
with sync_playwright() as p:
    for name in sys.argv[3].split(","):
        dev = dict(p.devices["iPhone 13"])
        if name != "chromium":
            dev.pop("is_mobile", None) if False else None
        b = getattr(p, name).launch()
        ctx = b.new_context(**dev); pg = ctx.new_page()
        pg.goto(URL, wait_until="domcontentloaded", timeout=90000); pg.wait_for_timeout(12000)
        frames = [pg] + [f for f in pg.frames if f != pg.main_frame]
        found = None
        for f in [pg.main_frame] + [fr for fr in pg.frames if fr != pg.main_frame]:
            try:
                m = f.evaluate(JS)
                if not m.get("absente"):
                    found = {"frame": f.url[:80], **m}; break
            except Exception as e:
                continue
        res[name] = found or {"absente_partout": True, "frames": [f.url[:80] for f in pg.frames]}
        pg.screenshot(path=f"{OUT}/tabbar_{name}.png")
        b.close()
print(json.dumps(res, ensure_ascii=False, indent=1))
