"""Deterministic lesson timing and balanced group planning."""
from fractions import Fraction

def redistribute_minutes(weights, duration):
    """Largest-remainder allocation; preserve zero phases and exact total."""
    if not isinstance(duration, int) or not 15 <= duration <= 240:
        raise ValueError("Invalid lesson duration")
    if len(weights) != 5 or any(not isinstance(w, int) or w < 0 for w in weights):
        raise ValueError("Invalid phase weights")
    if not sum(weights):
        weights = (5, 10, 30, 10, 5)
    quotas = [Fraction(w * duration, sum(weights)) for w in weights]
    result = [int(q) for q in quotas]
    order = sorted(range(5), key=lambda i: (quotas[i] - result[i], -i), reverse=True)
    for i in order[:duration-sum(result)]:
        result[i] += 1
    return result

def balanced_groups(count, target):
    """Group sizes differing by at most one, with no empty groups."""
    if not 1 <= count <= 150 or not 1 <= target <= 150:
        raise ValueError("Invalid group parameters")
    groups = (count + target - 1) // target
    base, extra = divmod(count, groups)
    return [base+1]*extra + [base]*(groups-extra)


def adaptation_notes(profile, equipment_limited, space_limited, connectivity, devices):
    """Non-prescriptive, explicit constraints; no inference about pupil ability."""
    from .i18n import t
    notes = []
    if profile == "Découverte":
        notes.append(t("Privilégier la variante simplifiée, une démonstration et un seul critère observable à la fois."))
    elif profile == "Approfondissement":
        notes.append(t("Proposer la variante complexifiée seulement après maîtrise de la situation de base."))
    else:
        notes.append(t("Proposer des variantes de difficulté et laisser les élèves évoluer selon leur maîtrise."))
    if equipment_limited:
        notes.append(t("Répartir le matériel entre ateliers et alterner pratique et observation brève sans attente prolongée."))
    if space_limited:
        notes.append(t("Réduire les déplacements simultanés, délimiter les zones et conserver des distances de sécurité."))
    if connectivity != "Disponible":
        notes.append(t("Préparer les supports à l’avance et prévoir une alternative utilisable sans Internet."))
    if devices == "Aucun":
        notes.append(t("Utiliser des démonstrations, des repères visuels et des fiches papier."))
    return notes
