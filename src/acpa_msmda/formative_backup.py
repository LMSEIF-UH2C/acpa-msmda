"""Versioned portable backups for formative assessments."""
import json
from .formative import DIMENSIONS, LEVELS
from .session_context import APS, LEVELS as SCHOOL_LEVELS

MAX_BYTES = 5 * 1024 * 1024
MAX_LESSONS = 200

def validate_lesson(value, archived=False):
    if not isinstance(value, dict) or set(value) != {"context","criteria","records"}:
        raise ValueError("Invalid lesson")
    c = value["context"]
    if not isinstance(c, (list,tuple)) or len(c)!=6:
        raise ValueError("Invalid context")
    activity, level, count, cycle, lesson, group = c
    if activity not in APS or level not in SCHOOL_LEVELS or type(count) is not int or not 1<=count<=150:
        raise ValueError("Invalid context")
    if any(type(n) is not int or not 0<=n<=10000 for n in (cycle,lesson)):
        raise ValueError("Invalid lesson number")
    if not isinstance(group,str) or len(group)>30 or (archived and (not group.strip() or not cycle or not lesson)):
        raise ValueError("Invalid group")
    criteria = value["criteria"]
    if not isinstance(criteria,list) or len(criteria)>12:
        raise ValueError("Invalid criteria")
    clean = []
    keys = set()
    for row in criteria:
        if not isinstance(row,(tuple,list)) or len(row)!=3:
            raise ValueError("Invalid criterion")
        key, dim, label = row
        if not isinstance(key,str) or key != str(len(clean)+1) or dim not in DIMENSIONS or not isinstance(label,str) or not label.strip() or len(label)>200:
            raise ValueError("Invalid criterion")
        keys.add(key)
        clean.append((key,dim,label))
    records = value["records"]
    if not isinstance(records,dict) or len(records)>count:
        raise ValueError("Invalid records")
    allowed = {f"E{i:03d}" for i in range(1,count+1)}
    for code, observations in records.items():
        if code not in allowed or not isinstance(observations,dict):
            raise ValueError("Invalid pupil code")
        if any(key not in keys or level not in LEVELS for key,level in observations.items()):
            raise ValueError("Invalid observation")
    return {"context":tuple(c),"criteria":clean,"records":records}

def load_backup(raw):
    if not isinstance(raw,bytes) or not raw or len(raw)>MAX_BYTES:
        raise ValueError("Invalid file size")
    try:
        value=json.loads(raw.decode("utf-8"))
        if not isinstance(value,dict) or set(value)!={"version","current","history"} or type(value["version"]) is not int or value["version"]!=1:
            raise ValueError("Invalid backup version")
        entries=value["history"]
        if not isinstance(entries,list) or len(entries)>MAX_LESSONS:
            raise ValueError("Invalid history")
        history={}
        for entry in entries:
            item=validate_lesson(entry,archived=True)
            if item["context"] in history:
                raise ValueError("Duplicate lesson")
            history[item["context"]]=item
        current=validate_lesson(value["current"]) if value["current"] is not None else None
        if current is None and not history:
            raise ValueError("Empty backup")
        return current,history
    except (TypeError,ValueError,RecursionError,UnicodeError,KeyError) as exc:
        raise ValueError("Invalid backup") from exc

def make_backup(current,history):
    raw=json.dumps({"version":1,"current":current,"history":list(history.values())},ensure_ascii=False,allow_nan=False).encode("utf-8")
    load_backup(raw)
    return raw
