"""Matching transparent des références documentées du catalogue réel."""
from __future__ import annotations
import json
from pathlib import Path
from .context_engine import normalize_text,analyze_context
from .contracts import ContextRequest
DEFAULT_PATH=Path(__file__).resolve().parents[2]/"data"/"real_tools_catalog.json"
def load_real_tools(path=DEFAULT_PATH):
    raw=json.loads(Path(path).read_text(encoding="utf-8"))
    if raw.get("dataset_type")!="REAL_TOOLS_UNSCORED":raise ValueError("Catalogue incompatible")
    items=raw.get("tools",[])
    if not isinstance(items,list) or len({t["id"] for t in items})!=len(items):raise ValueError("Identifiants invalides")
    return items
def match_real_tools(context,path=DEFAULT_PATH):
    if not isinstance(context,str) or not context.strip():raise ValueError("Contexte requis")
    analysis=analyze_context(ContextRequest(context,"fr"))
    words=set(normalize_text(context).split())
    matches=[]
    for t in load_real_tools(path):
        if t.get("evidence_status")!="OFFICIAL_SOURCE_FEATURES_ONLY":continue
        matched=[term for term in t.get("activities",[])+t.get("uses",[]) if normalize_text(term) in words]
        if not matched:continue
        cautions=[t.get("caution","")]
        if "connectivite_faible" in analysis.flags and t.get("requirement")=="internet":cautions.append("Connexion requise ou modalités hors ligne non vérifiées.")
        if "budget_serre" in analysis.flags and t.get("requirement")=="materiel":cautions.append("Coût du matériel à vérifier.")
        matches.append({**t,"matched_terms":sorted(set(matched)),"cautions":cautions})
    matches.sort(key=lambda t:(-len(t["matched_terms"]),t["name"].casefold()))
    return {"context_flags":list(analysis.flags),"matches":matches,"method":"descriptive_keyword_matching","ranking_validated":False,"scores":None}
