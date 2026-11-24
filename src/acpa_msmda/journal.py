"""Portable teaching journal; no pupil names or roster storage."""
import csv
import io
import json
from datetime import date
from .session_context import APS, LEVELS
from .scenario_engine import safe_cell

STATUSES=("Prévue","Réalisée","Reportée","Annulée")
FIELDS=("id","date","group","activity","level","cycle","lesson","duration","objectives","status","reflection")
MAX_ENTRIES=1000

def validate_entries(entries):
    if not isinstance(entries,list) or len(entries)>MAX_ENTRIES:
        raise ValueError("Invalid journal")
    ids=set()
    clean=[]
    for e in entries:
        if not isinstance(e,dict) or set(e)!=set(FIELDS):
            raise ValueError("Invalid fields")
        for key,limit in (("id",40),("date",10),("group",30),("objectives",800),("reflection",1500)):
            if not isinstance(e[key],str) or len(e[key])>limit:
                raise ValueError("Invalid text")
        if not e["id"] or e["id"] in ids or not e["group"].strip():
            raise ValueError("Invalid identifier")
        ids.add(e["id"])
        if date.fromisoformat(e["date"]).isoformat()!=e["date"]:
            raise ValueError("Invalid date")
        if e["activity"] not in APS or e["level"] not in LEVELS or e["status"] not in STATUSES:
            raise ValueError("Invalid category")
        for key,low,high in (("cycle",0,10000),("lesson",0,10000),("duration",15,240)):
            if type(e[key]) is not int or not low<=e[key]<=high:
                raise ValueError("Invalid number")
        clean.append(dict(e))
    return clean

def backup(entries):
    return json.dumps({"version":1,"entries":validate_entries(entries)},ensure_ascii=False).encode("utf-8")

def restore(raw):
    if not isinstance(raw,bytes) or len(raw)>10*1024*1024:
        raise ValueError("Invalid file size")
    try:
        data=json.loads(raw.decode("utf-8"))
        if not isinstance(data,dict) or set(data)!={"version","entries"} or type(data["version"]) is not int or data["version"]!=1:
            raise ValueError("Invalid version")
        return validate_entries(data["entries"])
    except (ValueError,TypeError,KeyError,RecursionError) as exc:
        raise ValueError("Invalid journal backup") from exc

def export_csv(entries):
    from .i18n import t
    out=io.StringIO()
    writer=csv.writer(out)
    writer.writerow([t(x) for x in ("Date","Code du groupe (non nominatif)","Activité physique ou sportive","Niveau","Cycle","Séance","Durée (min)","Objectifs de la séance","Statut de la séance","Bilan pédagogique")])
    for e in sorted(validate_entries(entries),key=lambda e:(e["date"],e["group"],e["lesson"])):
        writer.writerow([e["date"],safe_cell(e["group"]),t(e["activity"]),t(e["level"]),e["cycle"],e["lesson"],e["duration"],safe_cell(e["objectives"]),t(e["status"]),safe_cell(e["reflection"])])
    return out.getvalue().encode("utf-8-sig")
