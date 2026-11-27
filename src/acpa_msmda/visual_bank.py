"""Repères visuels facultatifs du Laboratoire EPS (banque visuelle ACPA/MSMDA).

Source unique : ``assets/visual-bank/manifest.json``.
- 14 épreuves ont une illustration pédagogique (JPEG dans ``assets/lab/``), générée par IA et acceptée par le
  porteur du projet : non normative, elle ne remplace jamais le protocole écrit. Chaque illustration a un texte
  alternatif (ce que montre l'image et le matériel représenté), affiché sous l'image et traduit en arabe et en anglais.
- 18 épreuves ont un pictogramme de famille OpenMoji (CC BY-SA 4.0), qui n'illustre pas le protocole.

Une image absente ou illisible n'empêche rien : la page affiche le protocole écrit, seul de référence.
Aucun téléchargement à l'exécution : seuls les fichiers déposés dans le dépôt sont lus.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .i18n import t

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "assets" / "visual-bank" / "manifest.json"
OPENMOJI_CREDIT = "OpenMoji (openmoji.org), CC BY-SA 4.0"
ILLUSTRATION_NOTE = ("Repère visuel. Pour réaliser l’épreuve, suivre le protocole et vérifier le matériel, "
                     "les distances et les conditions de mesure.")
PICTOGRAM_NOTE = "Repère de la famille d’épreuves."


@dataclass(frozen=True)
class Visual:
    test_id: str
    kind: str              # « illustration » ou « pictogramme »
    path: Path
    note: str              # avertissement affiché sous le visuel (source française, traduit à l'affichage)
    credit: str
    alt: str = ""          # texte alternatif : ce que montre l'image (source française, traduit à l'affichage)

    @property
    def available(self) -> bool:
        return self.path.is_file() and self.path.stat().st_size > 0


@lru_cache(maxsize=1)
def manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def icon_path(icon_id: str) -> Path | None:
    entry = next((i for i in manifest()["icons"] if i["id"] == icon_id), None)
    return ROOT / entry["path"] if entry else None


def visual_for(test_id: str) -> Visual | None:
    """Repère visuel prévu pour une épreuve (disponible ou non), ou None si aucun n'est prévu."""
    data = manifest()
    specific = next((x for x in data["lab_specific"] if x["id"] == test_id), None)
    if specific:
        return Visual(test_id, "illustration", ROOT / specific["path"],
                      ILLUSTRATION_NOTE, "ACPA/MSMDA", specific.get("alt", ""))
    generic = next((x for x in data["lab_generic"] if x["id"] == test_id), None)
    if generic:
        path = icon_path(generic["icon"])
        if path is None:
            return None
        return Visual(test_id, "pictogramme", path, PICTOGRAM_NOTE, OPENMOJI_CREDIT)
    return None


def render(st, test_id: str) -> bool:
    """Affiche le repère visuel d'une épreuve s'il existe ; renvoie True si quelque chose a été affiché."""
    visual = visual_for(test_id)
    if visual is None or not visual.available:
        return False
    if visual.kind == "pictogramme":
        icon, text = st.columns([1, 5], vertical_alignment="center")
        icon.image(str(visual.path), width=56)
        from .lab_results import ltr

        text.caption(t(visual.note) + " " + t("Pictogramme : {credit}.", credit=ltr(visual.credit)))
        return True
    with st.expander(t("Illustration pédagogique")):
        st.image(str(visual.path), width="stretch")
        if visual.alt:
            st.caption(t(visual.alt))
        st.caption(t(visual.note))
    return True


def alt_texts() -> list[str]:
    """Textes alternatifs des illustrations (source française), pour le contrôle des traductions."""
    return [x["alt"] for x in manifest()["lab_specific"] if x.get("alt")]


def credits() -> list[str]:
    """Crédits à afficher dans l'application et dans toute redistribution."""
    lines = [t("Pictogrammes : OpenMoji, projet open source d'emojis et d'icônes, licence CC BY-SA 4.0 "
               "(creativecommons.org/licenses/by-sa/4.0), fichiers non modifiés.")]
    lines.append(t("Illustrations pédagogiques : ACPA/MSMDA ; licence CC BY 4.0 "
                   "(creativecommons.org/licenses/by/4.0), dans la mesure des droits détenus. "
                   "Provenance et crédits détaillés : "
                   "https://github.com/LMSEIF-UH2C/acpa-msmda/blob/main/assets/visual-bank/LICENCE-ILLUSTRATIONS.md"))
    return lines
