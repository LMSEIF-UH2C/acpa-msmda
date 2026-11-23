"""Original schematic illustrations and multilingual learning situations."""
import json
from pathlib import Path
from . import i18n

DATA = Path(__file__).resolve().parents[2] / "data" / "learning_situations.json"

def load_situations():
    return json.loads(DATA.read_text(encoding="utf-8"))["situations"]

def details(situation):
    return situation.get(i18n.current(), situation["fr"])

def diagram_svg(kind):
    """Schematic, not a scale drawing. Blue circles: attackers, orange: defenders."""
    head = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 220" width="720" height="440"><rect width="360" height="220" rx="12" fill="#eaf3ef"/><rect x="15" y="15" width="330" height="190" rx="5" fill="none" stroke="#72958a" stroke-width="2"/><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="#1552f8"/></marker></defs>'
    def player(x,y,color="#1552f8"):
        return f'<circle cx="{x}" cy="{y}" r="12" fill="{color}" stroke="white" stroke-width="2"/>'
    def arrow(x,y,a,b):
        return f'<path d="M{x} {y}L{a} {b}" stroke="#1552f8" stroke-width="3" stroke-dasharray="6 4" marker-end="url(#arrow)" fill="none"/>'
    if kind == "triangle":
        body = arrow(85,110,220,55)+arrow(85,110,220,165)+player(70,110)+player(240,45)+player(240,175)+player(160,110,"#e87924")
    elif kind == "overload":
        body = arrow(90,55,265,55)+arrow(90,165,265,165)+''.join(player(65,y) for y in (45,110,175))+player(175,85,"#e87924")+player(175,145,"#e87924")
    elif kind == "net":
        body = '<path d="M180 18V202" stroke="#425b68" stroke-width="5" stroke-dasharray="5 3"/><rect x="235" y="65" width="65" height="90" rx="8" fill="#c7e7ff" stroke="#1552f8"/>'+arrow(90,55,245,100)+''.join(player(x,y) for x,y in ((65,55),(95,155),(260,55),(290,165)))
    elif kind == "lanes":
        body = '<path d="M15 78H345M15 142H345" stroke="white" stroke-width="3"/><path d="M280 15V205" stroke="#72958a" stroke-dasharray="5 4"/>'+''.join(player(50,y)+arrow(70,y,265,y) for y in (47,110,175))
    elif kind == "loop":
        body = '<rect x="55" y="45" width="250" height="130" rx="60" fill="none" stroke="#1552f8" stroke-width="4"/>'+arrow(140,45,235,45)+arrow(220,175,125,175)+player(120,45)+player(240,175)
    else:
        raise ValueError("Unknown diagram")
    return head+body+"</svg>"
