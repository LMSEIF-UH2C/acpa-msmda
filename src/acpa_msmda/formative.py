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
