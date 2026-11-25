"""Retouche locale des logos commerciaux des illustrations du Laboratoire.

Usage :
  python -I retouche_logos.py apercu  <dossier_source> <zones.json> <sortie_dossier> [id ...]
  python -I retouche_logos.py retouche <dossier_source> <zones.json> <sortie_dossier> [id ...]

Pour chaque zone (polygone en coordonnées de l'image d'origine), un masque est calculé par une règle de couleur :
  light : pixels clairs et peu saturés (logo blanc ou gris sur fond coloré) ;
  dark  : pixels sombres (logo foncé sur fond clair) ;
  all   : tout le polygone.
Les composantes connexes peuvent être filtrées (taille, contact avec les bords haut ou bas du polygone), puis le masque
est dilaté et comblé par inpainting OpenCV (Telea) à partir des pixels voisins. Rien d'autre n'est modifié.
L'enregistrement JPEG réutilise les tables de quantification et le sous-échantillonnage de l'original.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, JpegImagePlugin


def channels(arr):
    rgb = arr.astype(np.float32)
    mx, mn = rgb.max(2), rgb.min(2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1.0), 0.0)
    lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    return mx, sat, lum


def region_mask(arr, reg):
    h, w = arr.shape[:2]
    poly = np.array(reg["poly"], np.int32)
    inside = np.zeros((h, w), np.uint8)
    cv2.fillPoly(inside, [poly], 1)
    for hole in reg.get("exclude", []):
        cv2.fillPoly(inside, [np.array(hole, np.int32)], 0)
    inside = inside.astype(bool)
    mx, sat, lum = channels(arr)
    rule = reg.get("rule", "light")
    if rule == "all":
        sel = inside.copy()
    elif rule == "light":
        sel = inside & (mx >= reg.get("v", 150)) & (sat <= reg.get("s", 0.22))
        if "hyst" in reg:
            # Hystérésis : pixels plus faibles (queue de la virgule) gardés s'ils touchent un pixel net.
            weak = inside & (mx >= reg["hyst"].get("v", 105)) & (sat <= reg["hyst"].get("s", 0.38))
            n_w, lab_w = cv2.connectedComponents(weak.astype(np.uint8), connectivity=8)
            seeds = np.unique(lab_w[sel & weak])
            sel = np.isin(lab_w, seeds[seeds > 0]) | sel
    elif rule == "dark":
        sel = inside & (lum <= reg.get("l", 120))
    elif rule == "tint":
        sel = inside & (sat >= reg.get("s_min", 0.06)) & (mx <= reg.get("v_max", 222)) & (mx >= reg.get("v_min", 110))
    else:
        raise ValueError(rule)
    t = reg.get("thin_only", 0)
    if t:
        # Ne garde que les tracés fins (bandes) : les aplats épais (feuille, papier) sont retirés de la sélection.
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (t, t))
        thick = cv2.morphologyEx(sel.astype(np.uint8), cv2.MORPH_OPEN, kernel)
        thick = cv2.dilate(thick, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))).astype(bool)
        sel = sel & ~thick
    x0, y0, bw, bh = cv2.boundingRect(poly)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(sel.astype(np.uint8), 8)
    keep = np.zeros((h, w), bool)
    for i in range(1, n):
        x, y, ww, hh, area = stats[i]
        if area < reg.get("min_area", 4) or area > reg.get("max_area", 10 ** 9):
            continue
        if ww > reg.get("max_w", 10 ** 9) or hh > reg.get("max_h", 10 ** 9):
            continue
        edges = reg.get("exclude_edge", [])
        if "top" in edges and y <= y0 + 1:
            continue
        if "bottom" in edges and y + hh >= y0 + bh - 1:
            continue
        if "left" in edges and x <= x0 + 1:
            continue
        if "right" in edges and x + ww >= x0 + bw - 1:
            continue
        keep |= lab == i
    c = reg.get("close_mask", 0)
    if c:
        # Fusionne des éléments voisins (trois bandes) en une seule zone, pour ne pas laisser les intervalles.
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (c, c))
        keep = cv2.morphologyEx(keep.astype(np.uint8), cv2.MORPH_CLOSE, kernel).astype(bool) & inside
    d = reg.get("dilate", 2)
    if d:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * d + 1, 2 * d + 1))
        keep = cv2.dilate(keep.astype(np.uint8), kernel).astype(bool)
    return keep & (inside if reg.get("clip", False) else np.ones_like(inside))


def valid_pixels(arr, kind):
    """Pixels voisins autorisés pour le remplissage : même matière que le fond (tissu foncé, chaussure blanche...)."""
    mx, sat, lum = channels(arr)
    if kind == "dark":
        return lum < 110
    if kind == "light":
        return (lum > 175) & (sat < 0.12)
    if kind == "blue":
        return (sat > 0.42) & (mx > 60) & (arr[..., 2] > arr[..., 0])
    if kind == "skin":
        return (arr[..., 0] > arr[..., 2]) & (sat > 0.2)
    return np.ones(arr.shape[:2], bool)


def fill_average(arr, result, m, kind, feather):
    """Remplit le masque par moyenne gaussienne normalisée des seuls pixels voisins valides, à plusieurs échelles."""
    if not m.any():
        return result
    ys, xs = np.nonzero(m)
    pad = 40
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, arr.shape[0])
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad + 1, arr.shape[1])
    sub = arr[y0:y1, x0:x1].astype(np.float32)
    msub = m[y0:y1, x0:x1]
    valid = (valid_pixels(arr[y0:y1, x0:x1], kind) & ~msub).astype(np.float32)
    est = np.zeros_like(sub)
    done = np.zeros(msub.shape, bool)
    for sigma in (2.0, 4.0, 8.0, 16.0):
        num = cv2.GaussianBlur(sub * valid[..., None], (0, 0), sigma)
        den = cv2.GaussianBlur(valid, (0, 0), sigma)
        ok = (den > 0.02) & msub & ~done
        est[ok] = num[ok] / den[ok][..., None]
        done |= ok
    est[~done] = sub[~done]
    alpha = cv2.GaussianBlur(msub.astype(np.float32), (0, 0), feather)
    alpha = np.maximum(alpha, msub.astype(np.float32))[..., None]
    region = result[y0:y1, x0:x1]
    result[y0:y1, x0:x1] = alpha * est + (1 - alpha) * region
    return result


def image_mask(arr, regions):
    mask = np.zeros(arr.shape[:2], bool)
    for reg in regions:
        mask |= region_mask(arr, reg)
    return mask


def zoom_tile(arr, box, scale, overlay=None, poly=None, label=""):
    x0, y0, x1, y1 = box
    crop = Image.fromarray(arr[y0:y1, x0:x1])
    crop = crop.resize((round(crop.width * scale), round(crop.height * scale)), Image.LANCZOS)
    draw = ImageDraw.Draw(crop, "RGBA")
    if overlay is not None:
        ys, xs = np.nonzero(overlay[y0:y1, x0:x1])
        for x, y in zip(xs, ys):
            draw.rectangle([x * scale, y * scale, (x + 1) * scale - 1, (y + 1) * scale - 1], fill=(255, 0, 255, 120))
    if poly is not None:
        pts = [((px - x0) * scale, (py - y0) * scale) for px, py in poly]
        draw.line(pts + [pts[0]], fill=(255, 200, 0, 255), width=2)
        font = ImageFont.load_default()
        for gx in range((x0 // 10 + 1) * 10, x1, 10):
            X = (gx - x0) * scale
            draw.line([(X, 0), (X, crop.height)], fill=(0, 160, 255, 150 if gx % 50 == 0 else 50), width=1)
            if gx % 50 == 0:
                draw.text((X + 2, crop.height - 12), str(gx), fill=(0, 90, 200, 255), font=font)
        for gy in range((y0 // 10 + 1) * 10, y1, 10):
            Y = (gy - y0) * scale
            draw.line([(0, Y), (crop.width, Y)], fill=(0, 160, 255, 150 if gy % 50 == 0 else 50), width=1)
            if gy % 50 == 0:
                draw.text((2, Y + 1), str(gy), fill=(0, 90, 200, 255), font=font)
    tile = Image.new("RGB", (crop.width, crop.height + 14), "white")
    ImageDraw.Draw(tile).text((3, 1), label, fill="black", font=ImageFont.load_default())
    tile.paste(crop, (0, 14))
    return tile


def sheet(tiles, out, columns=2):
    rows = [tiles[i:i + columns] for i in range(0, len(tiles), columns)]
    width = max(sum(t.width + 6 for t in r) for r in rows)
    height = sum(max(t.height for t in r) + 6 for r in rows)
    canvas = Image.new("RGB", (width, height), (190, 190, 190))
    y = 0
    for r in rows:
        x = 0
        for t in r:
            canvas.paste(t, (x, y))
            x += t.width + 6
        y += max(t.height for t in r) + 6
    canvas.save(out)


def box_of(poly, margin, shape):
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    return (max(min(xs) - margin, 0), max(min(ys) - margin, 0),
            min(max(xs) + margin, shape[1]), min(max(ys) + margin, shape[0]))


def main():
    mode, src, zones_path, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    zones = json.loads(zones_path.read_text(encoding="utf-8"))
    ids = sys.argv[5:] or sorted(zones)
    out.mkdir(parents=True, exist_ok=True)
    for image_id in ids:
        spec = zones[image_id]
        regions = spec["regions"]
        with Image.open(src / f"{image_id}.jpg") as im:
            qtables, sampling = im.quantization, JpegImagePlugin.get_sampling(im)
            arr = np.array(im.convert("RGB"))
        scale = spec.get("zoom", 3)
        if mode == "apercu":
            tiles = []
            for k, reg in enumerate(regions):
                m = region_mask(arr, reg)
                box = box_of(reg["poly"], 8, arr.shape)
                z = reg.get("zoom", scale)
                tiles.append(zoom_tile(arr, box, z, None, reg["poly"], f"#{k} {reg.get('note', '')}"))
                tiles.append(zoom_tile(arr, box, z, m, reg["poly"], f"#{k} masque ({int(m.sum())} px)"))
            sheet(tiles, out / f"apercu_{image_id}.png", 2 * spec.get("columns", 1))
            print(image_id, "aperçu :", len(regions), "zones")
            continue
        # Remplissage morphologique (par défaut) : l'ouverture retire un détail clair et fin (bande, virgule
        # blanche) sans jamais éclaircir ; la fermeture retire un détail sombre et fin (virgule grise sur chaussure
        # blanche) sans jamais assombrir. Aucune couleur voisine ne peut couler dans la zone. L'inpainting Telea
        # reste disponible zone par zone (fill = "inpaint").
        result = arr.astype(np.float32)
        mask = np.zeros(arr.shape[:2], bool)
        inpaint_mask = np.zeros(arr.shape[:2], bool)
        cache = {}
        for reg in regions:
            m = region_mask(arr, reg)
            mask |= m
            method = reg.get("fill", spec.get("fill", "avg"))
            if method == "inpaint":
                inpaint_mask |= m
                continue
            if method == "avg":
                result = fill_average(arr, result, m, reg.get("valid", "dark"), reg.get("feather", 0.8))
                continue
            se = reg.get("se", spec.get("se", 9))
            key = (method, se)
            if key not in cache:
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (se, se))
                op = cv2.MORPH_OPEN if method == "open" else cv2.MORPH_CLOSE
                filtered = cv2.morphologyEx(arr, op, kernel)
                cache[key] = cv2.GaussianBlur(filtered, (0, 0), 0.8).astype(np.float32)
            filtered = cache[key]
            if method == "open":
                filtered = np.minimum(filtered, arr.astype(np.float32))
            else:
                filtered = np.maximum(filtered, arr.astype(np.float32))
            alpha = cv2.GaussianBlur(m.astype(np.float32), (0, 0), reg.get("feather", 0.8))
            alpha = np.maximum(alpha, m.astype(np.float32))[..., None]
            result = alpha * filtered + (1 - alpha) * result
        result = np.clip(np.rint(result), 0, 255).astype(np.uint8)
        if inpaint_mask.any():
            bgr = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
            fixed = cv2.inpaint(bgr, inpaint_mask.astype(np.uint8) * 255, spec.get("radius", 4), cv2.INPAINT_TELEA)
            fixed = cv2.cvtColor(fixed, cv2.COLOR_BGR2RGB)
            result[inpaint_mask] = fixed[inpaint_mask]
        changed = np.any(result != arr, axis=2)
        mask |= changed
        Image.fromarray(result).save(out / f"{image_id}.jpg", "JPEG", qtables=qtables, subsampling=sampling,
                                     progressive=True, optimize=True)
        Image.fromarray((mask * 255).astype(np.uint8)).save(out / f"masque_{image_id}.png", optimize=True)
        tiles = []
        for k, reg in enumerate(regions):
            box = box_of(reg["poly"], 8, arr.shape)
            tiles.append(zoom_tile(arr, box, scale, None, None, f"{image_id} #{k} avant"))
            tiles.append(zoom_tile(result, box, scale, None, None, f"{image_id} #{k} après"))
        sheet(tiles, out / f"avant_apres_{image_id}.png", 2 * spec.get("columns", 1))
        print(image_id, "retouché :", int(mask.sum()), "px masqués,", f"{100 * mask.mean():.3f} % de l'image")


if __name__ == "__main__":
    main()
