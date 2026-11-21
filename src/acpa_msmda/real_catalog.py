"""Transparent descriptive matching of real tools; never invent ACPA criterion scores."""
from __future__ import annotations
import json
from pathlib import Path
from .context_engine import normalize_text, analyze_context
from .contracts import ContextRequest

DEFAULT_PATH=Path(__file__).resolve().parents[2]/"data"/"real_tools_catalog.json"
def load_real_tools(path=DEFAULT_PATH):
    raw=json.loads(Path(path).read_text(encoding="utf-8"))
    if raw.get("dataset_type")!="REAL_TOOLS_UNSCORED":
        raise ValueError("Expected real, unscored tool catalogue")
    tools=raw.get("tools",[])
    if not isinstance(tools,list) or len({t["id"] for t in tools})!=len(tools):
        raise ValueError("Invalid or duplicate tool records")
    return tools

def match_real_tools(context, path=DEFAULT_PATH):
    if not isinstance(context,str) or not context.strip():
        raise ValueError("Context is required")
    analysis=analyze_context(ContextRequest(context,"fr"))
    normalized=normalize_text(context)
    words=set(normalized.split())
    results=[]
    for t in load_real_tools(path):
        matched=[x for x in t["activities"]+t["uses"] if normalize_text(x) in words]
        cautions=[t["caution"]]
        if "connectivite_faible" in analysis.flags and t["requirement"]=="internet":
            cautions.append("Connexion requise ou modalités hors ligne non vérifiées.")
        if "budget_serre" in analysis.flags and t["requirement"]=="materiel":
            cautions.append("Coût du matériel à vérifier.")
        if matched:
            results.append({**t,"matched_terms":sorted(set(matched)),"cautions":cautions})
    results.sort(key=lambda t:(-len(t["matched_terms"]),t["name"].casefold()))
    return {"context_flags":list(analysis.flags),"matches":results,"method":"descriptive_keyword_matching","ranking_validated":False,"scores":None}
