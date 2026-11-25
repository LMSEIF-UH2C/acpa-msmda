"""Preuves chiffrées de la retouche : empreintes, format, part modifiée, écart hors masque (réencodage JPEG)."""
import hashlib, json, sys
from pathlib import Path
import numpy as np
from PIL import Image
src, fin = Path(sys.argv[1]), Path(sys.argv[2])
out = {}
for image_id in sys.argv[3:]:
    a_path, b_path = src / f"{image_id}.jpg", fin / f"{image_id}.jpg"
    with Image.open(a_path) as a_im, Image.open(b_path) as b_im:
        assert b_im.format == "JPEG" and a_im.size == b_im.size
        prog = bool(b_im.info.get("progressive"))
        a, b = np.asarray(a_im.convert("RGB")).astype(int), np.asarray(b_im.convert("RGB")).astype(int)
        size = b_im.size
    m = np.asarray(Image.open(fin / f"masque_{image_id}.png")) > 0
    diff = np.abs(a - b).max(axis=2)
    out[image_id] = {
        "source_sha256": hashlib.sha256(a_path.read_bytes()).hexdigest(), "source_bytes": a_path.stat().st_size,
        "sha256": hashlib.sha256(b_path.read_bytes()).hexdigest(), "bytes": b_path.stat().st_size,
        "width": size[0], "height": size[1], "progressive": prog,
        "masked_pixels": int(m.sum()), "masked_percent": round(100 * float(m.mean()), 3),
        "outside_mask_mean_abs_diff": round(float(diff[~m].mean()), 3),
        "outside_mask_p99_abs_diff": int(np.percentile(diff[~m], 99)),
        "inside_mask_mean_abs_diff": round(float(diff[m].mean()), 1),
    }
    assert out[image_id]["bytes"] < 500_000
print(json.dumps(out, ensure_ascii=False, indent=1))
Path(fin / "stats.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
