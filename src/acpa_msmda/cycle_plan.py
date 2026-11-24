"""Annual cycle allocation independent of individual class sessions."""
from datetime import date
from .aps_specialties import valid_specialty
from copy import deepcopy

def validate_cycles(cycles):
    if not isinstance(cycles,list) or len(cycles)>30:
        raise ValueError("Invalid cycles")
    result=[]
    numbers=set()
    for c in cycles:
        if not isinstance(c,dict) or set(c)!={"number","start","end","activities"} or type(c["number"]) is not int or c["number"]<1 or c["number"] in numbers:
            raise ValueError("Invalid cycle")
        start,end=date.fromisoformat(c["start"]),date.fromisoformat(c["end"])
        if start>end or not isinstance(c["activities"],list) or not c["activities"] or any(not isinstance(a,str) or not a.strip() or len(a)>100 for a in c["activities"]):
            raise ValueError("Invalid allocation")
        numbers.add(c["number"])
        result.append(deepcopy(c))
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


def check_journal(cycles, entries):
    """Every scheduled lesson must match the single assigned activity."""
    clean=validate_cycles(cycles)
    for cycle in clean:
        if len(cycle["activities"]) != 1 or not valid_specialty(cycle["activities"][0]):
            raise ValueError("Select one catalog activity per cycle")
    for entry in entries:
        if not allows_session(clean,entry["date"],entry["cycle"],entry["activity"]):
            raise ValueError("Lesson outside assigned cycle")
    return clean
