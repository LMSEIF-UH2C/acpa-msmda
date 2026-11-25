"""Compare avant/après sur des zones choisies : python -I compare_zoom.py <avant.jpg> <apres.jpg> <sortie.png> <echelle> x0,y0,x1,y1 ..."""
import sys
from PIL import Image, ImageDraw, ImageFont
a, b = Image.open(sys.argv[1]).convert("RGB"), Image.open(sys.argv[2]).convert("RGB")
scale = float(sys.argv[4]); tiles = []
from pathlib import Path as _P
_font = _P(__file__).resolve().parents[0] / "DejaVuSans.ttf"
f = ImageFont.truetype(str(_font), 11) if _font.exists() else ImageFont.load_default()
for spec in sys.argv[5:]:
    x0, y0, x1, y1 = map(int, spec.split(","))
    pair = []
    for im, lab in ((a, "avant"), (b, "après")):
        c = im.crop((x0, y0, x1, y1)); c = c.resize((round(c.width * scale), round(c.height * scale)), Image.LANCZOS)
        t = Image.new("RGB", (c.width, c.height + 14), "white"); ImageDraw.Draw(t).text((2, 1), f"{lab} {spec}", fill="black", font=f); t.paste(c, (0, 14)); pair.append(t)
    row = Image.new("RGB", (pair[0].width * 2 + 6, pair[0].height), (190, 190, 190)); row.paste(pair[0], (0, 0)); row.paste(pair[1], (pair[0].width + 6, 0)); tiles.append(row)
W = sum(t.width + 8 for t in tiles); H = max(t.height for t in tiles)
if W > 2400:
    W = max(t.width for t in tiles); H = sum(t.height + 8 for t in tiles); out = Image.new("RGB", (W, H), (150, 150, 150)); y = 0
    for t in tiles: out.paste(t, (0, y)); y += t.height + 8
else:
    out = Image.new("RGB", (W, H), (150, 150, 150)); x = 0
    for t in tiles: out.paste(t, (x, 0)); x += t.width + 8
out.save(sys.argv[3]); print(out.size)
