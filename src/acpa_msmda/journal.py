"""Portable teaching journal; no pupil names or roster storage."""
import csv
import io
import json
from datetime import date
from .session_context import LEVELS
from .aps_specialties import valid_specialty
from .scenario_engine import safe_cell

STATUSES=("Prévue","Réalisée","Reportée","Annulée")
FIELDS=("id","date","group","activity","level","cycle","lesson","duration","objectives","status","reflection")
MAX_ENTRIES=3000

def validate_entries(entries):
    if not isinstance(entries,list) or len(entries)>MAX_ENTRIES:
        raise ValueError("Invalid journal")
    ids=set()
    group_days=set()
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
        group_day=(e["group"].strip(),e["date"])
        if group_day in group_days:
            raise ValueError("Duplicate class and date")
        group_days.add(group_day)
        if date.fromisoformat(e["date"]).isoformat()!=e["date"]:
            raise ValueError("Invalid date")
        if not valid_specialty(e["activity"]) or e["level"] not in LEVELS or e["status"] not in STATUSES:
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
        writer.writerow([e["date"],safe_cell(e["group"]),safe_cell(t(e["activity"])),t(e["level"]),e["cycle"],e["lesson"],e["duration"],safe_cell(e["objectives"]),t(e["status"]),safe_cell(e["reflection"])])
    return out.getvalue().encode("utf-8-sig")


def cycle_backup(cycles, entries):
    from .cycle_plan import check_journal
    clean=validate_entries(entries)
    return json.dumps({"version":2,"cycles":check_journal(cycles,clean),"entries":clean},ensure_ascii=False).encode("utf-8")

def restore_cycles(raw):
    from .cycle_plan import check_journal
    if not isinstance(raw,bytes) or len(raw)>10*1024*1024:
        raise ValueError("Invalid file size")
    try:
        data=json.loads(raw.decode("utf-8"))
        if not isinstance(data,dict) or set(data)!={"version","cycles","entries"} or type(data["version"]) is not int or data["version"]!=2:
            raise ValueError("Invalid version")
        entries=validate_entries(data["entries"])
        return check_journal(data["cycles"],entries),entries
    except (ValueError,TypeError,KeyError,RecursionError,AttributeError) as exc:
        raise ValueError("Invalid cycle backup") from exc


def full_backup(cycles, entries, slots, interruptions):
    from .timetable import generate
    payload=json.loads(cycle_backup(cycles,entries))
    generate([],slots,interruptions,[])
    payload.update(version=3,slots=slots,interruptions=interruptions)
    return json.dumps(payload,ensure_ascii=False).encode("utf-8")

def restore_full(raw):
    from .timetable import generate
    if not isinstance(raw,bytes) or len(raw)>10*1024*1024:
        raise ValueError("Invalid file size")
    try:
        payload=json.loads(raw.decode("utf-8"))
        if not isinstance(payload,dict):
            raise ValueError("Invalid payload")
        if payload.get("version")==2:
            cycles,entries=restore_cycles(raw)
            return cycles,entries,[],[]
        if type(payload.get("version")) is not int or payload["version"]!=3 or set(payload)!={"version","cycles","entries","slots","interruptions"}:
            raise ValueError("Invalid version")
        cycles,entries=restore_cycles(json.dumps({"version":2,"cycles":payload["cycles"],"entries":payload["entries"]}).encode())
        slots,interruptions=payload["slots"],payload["interruptions"]
        generate([],slots,interruptions,[])
        return cycles,entries,slots,interruptions
    except (ValueError,TypeError,KeyError,RecursionError,AttributeError) as exc:
        raise ValueError("Invalid journal backup") from exc


def workspace_backup(cycles, entries, slots, interruptions, projects):
    from .curriculum import validate_projects
    payload=json.loads(full_backup(cycles,entries,slots,interruptions))
    payload.update(version=4,projects=validate_projects(projects,cycles))
    raw=json.dumps(payload,ensure_ascii=False).encode("utf-8")
    if len(raw)>10*1024*1024:
        raise ValueError("Backup exceeds file size limit")
    return raw

def restore_workspace(raw):
    from .curriculum import validate_projects
    if not isinstance(raw,bytes) or len(raw)>10*1024*1024:
        raise ValueError("Invalid file size")
    try:
        payload=json.loads(raw.decode("utf-8"))
        if not isinstance(payload,dict):
            raise ValueError("Invalid payload")
        if type(payload.get("version")) is int and payload["version"] in (2,3):
            return (*restore_full(raw),[])
        if type(payload.get("version")) is not int or payload["version"]!=4 or set(payload)!={"version","cycles","entries","slots","interruptions","projects"}:
            raise ValueError("Invalid version")
        projects=payload.pop("projects")
        payload["version"]=3
        cycles,entries,slots,interruptions=restore_full(json.dumps(payload,ensure_ascii=False).encode("utf-8"))
        return cycles,entries,slots,interruptions,validate_projects(projects,cycles)
    except (ValueError,TypeError,KeyError,RecursionError,AttributeError) as exc:
        raise ValueError("Invalid workspace backup") from exc
