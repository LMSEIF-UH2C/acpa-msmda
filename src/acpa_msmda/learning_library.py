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
    elif kind == "racket":
        body = '<path d="M180 18V202" stroke="#425b68" stroke-width="5" stroke-dasharray="5 3"/><rect x="255" y="70" width="65" height="80" rx="5" fill="#c7e7ff" stroke="#1552f8"/>'+player(70,110)+player(235,45)+arrow(85,110,280,110)
    elif kind in ("balance", "mirror"):
        def mat(x):
            return f'<rect x="{x}" y="55" width="125" height="110" rx="6" fill="#c7e7ff" stroke="#72958a"/>'
        def figure(x):
            return f'<circle cx="{x}" cy="85" r="9" fill="#1552f8"/><path d="M{x} 98V130M{x-22} 110H{x+22}M{x} 130L{x-20} 150M{x} 130L{x+20} 150" fill="none" stroke="#1552f8" stroke-width="5"/>'
        body = mat(35)+mat(200)+figure(97)+(figure(262) if kind=="mirror" else player(262,110))
    else:
        raise ValueError("Unknown diagram")
    return head+body+"</svg>"


def apply_situation(situation, session):
    """Explicitly replace the learning phase only; keep class context and timings."""
    from . import session_context as ctx
    d = details(situation)
    ctx.put(session, "action_2", " ".join(d[k] for k in ("organisation", "easier", "harder", "safety")))
    ctx.put(session, "evaluation_2", d["success"])
    ctx.put(session, "illustrated_situation", situation["id"])


def selected_situation(session):
    from . import session_context as ctx
    selected = ctx.get(session, "illustrated_situation")
    return next((s for s in load_situations() if s["id"] == selected
                 and s["activity"] == ctx.get(session, "activity")
                 and s["level"] == ctx.get(session, "level")), None)


def diagram_drawing(kind):
    """Convert the controlled, original SVG subset into a ReportLab vector drawing."""
    from xml.etree import ElementTree as ET
    from reportlab.graphics.shapes import Drawing, Rect, Circle, Line, Path, Polygon
    from reportlab.lib.colors import HexColor
    import re
    import math

    drawing = Drawing(360, 220)
    root = ET.fromstring(diagram_svg(kind))
    def color(value):
        return None if value in (None, "none") else HexColor(value) if value.startswith("#") else HexColor("#ffffff")
    for el in root:
        tag = el.tag.rsplit("}", 1)[-1]
        a = el.attrib
        def n(key, default=0):
            return float(a.get(key, default))
        style = dict(fillColor=color(a.get("fill")), strokeColor=color(a.get("stroke")),
                     strokeWidth=n("stroke-width", 1))
        if tag == "rect":
            drawing.add(Rect(n("x"), 220-n("y")-n("height"), n("width"), n("height"),
                             rx=n("rx"), ry=n("rx"), **style))
        elif tag == "circle":
            drawing.add(Circle(n("cx"), 220-n("cy"), n("r"), **style))
        elif tag == "path":
            # The authored diagrams use absolute M/L and horizontal/vertical commands only.
            tokens = re.findall(r"[MLHV]|-?\\d+(?:\\.\\d+)?", a["d"])
            p = Path(**style)
            if "stroke-dasharray" in a:
                p.strokeDashArray = [float(x) for x in a["stroke-dasharray"].split()]
            i, x, y, previous = 0, 0, 0, None
            while i < len(tokens):
                cmd = tokens[i]
                i += 1
                old = (x, y)
                if cmd in ("M", "L"):
                    x, y = float(tokens[i]), float(tokens[i+1])
                    i += 2
                elif cmd == "H":
                    x = float(tokens[i]); i += 1
                elif cmd == "V":
                    y = float(tokens[i]); i += 1
                else:
                    raise ValueError("Unsupported diagram command")
                if cmd == "M":
                    p.moveTo(x, 220-y)
                else:
                    p.lineTo(x, 220-y)
                    previous = old
            drawing.add(p)
            if a.get("marker-end") and previous:
                angle = math.atan2(y-previous[1], x-previous[0])
                points = [x, 220-y]
                for offset in (-.5, .5):
                    points.extend([x-9*math.cos(angle+offset), 220-y+9*math.sin(angle+offset)])
                drawing.add(Polygon(points, fillColor=HexColor("#1552f8"), strokeColor=None))
    return drawing
