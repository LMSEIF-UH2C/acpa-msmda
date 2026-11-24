"""Annual cycle allocation independent of individual class sessions."""
from datetime import date

def validate_cycles(cycles):
    if not isinstance(cycles,list) or len(cycles)>30:
        raise ValueError("Invalid cycles")
    result=[]
    numbers=set()
    for c in cycles:
        if set(c)!={"number","start","end","activities"} or type(c["number"]) is not int or c["number"]<1 or c["number"] in numbers:
            raise ValueError("Invalid cycle")
        start,end=date.fromisoformat(c["start"]),date.fromisoformat(c["end"])
        if start>end or not isinstance(c["activities"],list) or not c["activities"] or any(not isinstance(a,str) or not a.strip() or len(a)>100 for a in c["activities"]):
            raise ValueError("Invalid allocation")
        numbers.add(c["number"])
        result.append(dict(c))
    result.sort(key=lambda c:c["start"])
    if any(a["end"]>=b["start"] for a,b in zip(result,result[1:])):
        raise ValueError("Overlapping cycles")
    return result

def cycle_at(cycles, when):
    day=when.isoformat() if isinstance(when,date) else date.fromisoformat(when).isoformat()
    return next((c for c in validate_cycles(cycles) if c["start"]<=day<=c["end"]),None)

def allows_session(cycles, when, number, activity):
    c=cycle_at(cycles,when)
    return c is not None and c["number"]==number and activity in c["activities"]
