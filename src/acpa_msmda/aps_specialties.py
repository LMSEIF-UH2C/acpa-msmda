"""Precise teaching activities, independent of recommendation categories."""
import json
from pathlib import Path
from .session_context import APS

def registry():
    path=Path(__file__).resolve().parents[2]/"data"/"aps_specialties.json"
    return json.loads(path.read_text(encoding="utf-8"))["groups"]

def categories():
    return {a["label"]:a["catalog_category"] for g in registry() for a in g["activities"]}

def catalog_category(label):
    return categories().get(label, label if label in APS else "Autre")

def valid_specialty(label):
    return isinstance(label,str) and 0<len(label.strip())<=100 and label==label.strip() and not any(c in label for c in "\n\r\t") and "/" not in label
