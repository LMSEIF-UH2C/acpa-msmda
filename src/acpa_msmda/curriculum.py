"""Curricular context with explicit separation of source and teacher text."""
import json
from pathlib import Path
from .cycle_plan import validate_cycles
from .session_context import LEVELS

def profiles():
    return json.loads((Path(__file__).resolve().parents[2]/"data"/"curriculum_profiles.json").read_text(encoding="utf-8"))["profiles"]

FIELDS=("group","cycle","level","profile","grade","module","institutional","reference","diagnostic","target","progression","assessment")

def validate_projects(projects,cycles):
    if not isinstance(projects,list) or len(projects)>500: raise ValueError("Invalid projects")
    numbers={c["number"] for c in validate_cycles(cycles)}
    registry={p["id"]:p for p in profiles()}
    seen=set()
    for p in projects:
        if not isinstance(p,dict) or set(p)!=set(FIELDS): raise ValueError("Invalid project")
        if type(p["cycle"]) is not int or p["cycle"] not in numbers or p["level"] not in LEVELS or p["profile"] not in registry: raise ValueError("Invalid context")
        for k in FIELDS:
            if k=="cycle": continue
            if not isinstance(p[k],str) or len(p[k])>(30 if k=="group" else 2000): raise ValueError("Invalid text")
        key=(p["group"],p["cycle"])
        if not p["group"].strip() or key in seen: raise ValueError("Duplicate project")
        seen.add(key)
        if p["profile"]=="MA" and not any(g["id"]==p["grade"] and g["category"]==p["level"] for g in registry["MA"]["levels"]): raise ValueError("Invalid grade")
        if p["institutional"].strip() and not p["reference"].strip(): raise ValueError("Source required")
    return [dict(p) for p in projects]

def export_projects(projects,cycles):
    return json.dumps({"version":1,"kind":"acpa-cycle-projects","projects":validate_projects(projects,cycles)},ensure_ascii=False).encode()

def import_projects(raw,cycles):
    if len(raw)>5*1024*1024: raise ValueError("File too large")
    try:
        d=json.loads(raw)
        if d.get("version")!=1 or d.get("kind")!="acpa-cycle-projects": raise ValueError("Invalid backup")
        return validate_projects(d["projects"],cycles)
    except (TypeError,KeyError,AttributeError,RecursionError,ValueError) as exc: raise ValueError("Invalid backup") from exc
