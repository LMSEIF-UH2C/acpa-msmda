"""Generate planned lessons from recurring class slots and annual cycles."""
from datetime import date, timedelta
from uuid import uuid4
from .cycle_plan import check_journal, cycle_at
from .journal import validate_entries, MAX_ENTRIES
from .session_context import LEVELS

def generate(cycles, slots, interruptions, entries):
    existing=validate_entries(entries)
    cycles=check_journal(cycles,existing)
    if not isinstance(slots,list) or len(slots)>100:
        raise ValueError("Invalid slots")
    if not isinstance(interruptions,list) or len(interruptions)>100:
        raise ValueError("Invalid interruptions")
    breaks=[]
    for start,end in interruptions:
        a,b=date.fromisoformat(start),date.fromisoformat(end)
        if a>b: raise ValueError("Invalid interruption")
        breaks.append((a,b))
    seen=set()
    for s in slots:
        if set(s)!={"group","level","weekday","duration","start_minute"}:
            raise ValueError("Invalid slot fields")
        if not isinstance(s["group"],str) or not s["group"].strip() or len(s["group"])>30 or s["level"] not in LEVELS:
            raise ValueError("Invalid class")
        for k,lo,hi in (("weekday",0,6),("duration",15,240),("start_minute",0,1439)):
            if type(s[k]) is not int or not lo<=s[k]<=hi: raise ValueError("Invalid slot")
        if s["start_minute"]+s["duration"]>1440: raise ValueError("Invalid duration")
        key=(s["group"],s["weekday"])
        if key in seen: raise ValueError("One session per class and day in this version")
        seen.add(key)
    ordered=sorted(slots,key=lambda s:(s["weekday"],s["start_minute"]))
    for i,s in enumerate(ordered):
        for other in ordered[i+1:]:
            if s["weekday"]==other["weekday"] and other["start_minute"]<s["start_minute"]+s["duration"]:
                raise ValueError("Overlapping teaching slots")
    keys={(e["group"],e["date"]) for e in existing}
    counters={}
    for e in existing:
        k=(e["group"],e["cycle"])
        counters[k]=max(counters.get(k,0),e["lesson"])
    new=[]
    for c in cycles:
        day=date.fromisoformat(c["start"])
        end=date.fromisoformat(c["end"])
        if (end-day).days>366: raise ValueError("Cycle exceeds one year")
        while day<=end:
            if not any(a<=day<=b for a,b in breaks):
                for s in ordered:
                    key=(s["group"],day.isoformat())
                    if s["weekday"]!=day.weekday() or key in keys: continue
                    k=(s["group"],c["number"])
                    counters[k]=counters.get(k,0)+1
                    new.append({"id":uuid4().hex,"date":day.isoformat(),"group":s["group"],"level":s["level"],"activity":c["activities"][0],"cycle":c["number"],"lesson":counters[k],"duration":s["duration"],"objectives":"","status":"Prévue","reflection":""})
                    keys.add(key)
                    if len(existing)+len(new)>MAX_ENTRIES: raise ValueError("Journal capacity exceeded")
            day+=timedelta(days=1)
    return validate_entries(existing+new)
