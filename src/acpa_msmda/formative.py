"""Formative assessment: descriptive mastery, never an automatic grade."""
from collections import Counter
import csv
import io

DIMENSIONS = ("Motrice", "Cognitive", "Méthodologique", "Sociale")
LEVELS = ("Non observé", "À construire", "En cours d’acquisition", "Acquis", "Maîtrise avancée")

def summarize_observations(values):
    """Separate unobserved entries from observed mastery."""
    values = list(values)
    if any(v not in LEVELS for v in values):
        raise ValueError("Unknown observation level")
    counts = Counter(values)
    observed = len(values) - counts[LEVELS[0]]
    return {"total": len(values), "observed": observed,
            "counts": {level: counts[level] for level in LEVELS},
            "coverage": observed / len(values) if values else None}

def observation_export(criteria, records):
    from .scenario_engine import safe_cell
    from .i18n import t
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([t(x) for x in ("Code", "Dimension", "Critère de réussite", "Niveau observé")])
    for code, observations in sorted(records.items()):
        for key, dimension, criterion in criteria:
            level = observations.get(key, LEVELS[0])
            if level not in LEVELS:
                raise ValueError("Unknown observation level")
            writer.writerow([safe_cell(code), t(dimension), safe_cell(criterion), t(level)])
    return output.getvalue().encode("utf-8-sig")


def snapshot(context, criteria, records):
    """Independent copy of a lesson; group code is not a pupil identifier."""
    from copy import deepcopy
    activity, level, count, cycle, lesson, group = context
    if not group or cycle < 1 or lesson < 1:
        raise ValueError("Group, cycle and lesson required")
    return {"context": tuple(context), "criteria": deepcopy(criteria), "records": deepcopy(records)}

def compare_lessons(before, after):
    """Ordinal transitions only; missing observations never count as regression."""
    a, b = before["context"], after["context"]
    if a[:4] != b[:4] or a[5] != b[5] or a[4] >= b[4]:
        raise ValueError("Incompatible lessons")
    if before["criteria"] != after["criteria"]:
        raise ValueError("Incompatible criteria")
    results = []
    for key, dimension, label in before["criteria"]:
        counts = {"higher": 0, "same": 0, "lower": 0, "missing": 0}
        transitions = []
        for i in range(1, a[2]+1):
            code = f"E{i:03d}"
            old = before["records"].get(code, {}).get(key, LEVELS[0])
            new = after["records"].get(code, {}).get(key, LEVELS[0])
            if old not in LEVELS or new not in LEVELS:
                raise ValueError("Unknown observation level")
            if LEVELS[0] in (old, new):
                status = "missing"
            elif LEVELS.index(new) > LEVELS.index(old):
                status = "higher"
            elif LEVELS.index(new) < LEVELS.index(old):
                status = "lower"
            else:
                status = "same"
            counts[status] += 1
            transitions.append((code, old, new, status))
        results.append({"criterion": label, "dimension": dimension, **counts, "transitions": transitions})
    return results
