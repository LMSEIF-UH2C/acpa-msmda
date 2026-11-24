"""Presentation-only limits; never modify scientific analysis inputs."""
def trajectory_records(participants, values, occasions, max_rows=5000, max_subjects=100):
    if len(participants) != len(values):
        raise ValueError("Participants and values must align")
    if max_rows < 1 or max_subjects < 1:
        raise ValueError("Positive display limits required")
    if not occasions:
        return [], 0
    if any(len(row) != len(occasions) for row in values):
        raise ValueError("Occasions and values must align")
    n = min(len(participants), max_subjects, max_rows // len(occasions))
    # Stable display-only prefix, not a statistical sample.
    return ([{"participant": p, "occasion": o, "value": v}
             for p, row in zip(participants[:n], values[:n])
             for o, v in zip(occasions, row)], n)


from contextlib import contextmanager
import logging


@contextmanager
def chart_guard(st, lang):
    """Isolate optional chart construction/rendering from results and exports."""
    try:
        yield
    except Exception:
        logging.getLogger(__name__).exception("Optional Lab chart unavailable")
        st.warning({"fr": "Graphique indisponible. Les tableaux, calculs et exports restent accessibles.",
                    "en": "Chart unavailable. Tables, calculations and exports remain accessible.",
                    "ar": "الرسم غير متاح. تبقى الجداول والحسابات والتصدير متاحة."}[lang])
