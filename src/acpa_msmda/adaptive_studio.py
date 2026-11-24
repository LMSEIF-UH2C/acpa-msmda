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
