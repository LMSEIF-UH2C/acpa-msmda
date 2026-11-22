"""Score sur 18 critères : formule, pertinence, pénalité, contexte."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import unittest
from acpa_msmda import scoring
from acpa_msmda.context_engine import coefficients

UNIFORM = [1 / 18] * 18


def blank(**values):
    scores = {c: "NR" for c in scoring.CODES}
    scores.update(values)
    scores.setdefault("risque", 0)
    return scores


def test_undocumented_fiche_gets_neutral_score():
    assert scoring.score(blank(), UNIFORM) == 50.0


def test_shrinkage_pulls_sparse_fiche_towards_neutral():
    one = scoring.score(blank(C6=10.0), UNIFORM)
    many = scoring.score(blank(**{c: 10.0 for c in scoring.CODES}), UNIFORM)
    assert 50 < one < many <= 100


def test_safety_penalty():
    base = scoring.score(blank(C6=8.0), UNIFORM)
    assert abs(scoring.score(blank(C6=8.0, risque=1), UNIFORM) - base * 0.85) <= 0.1


def test_offline_context_raises_offline_criterion():
    offline = coefficients(("connectivite_faible",)).values
    fiche = blank(C6=10.0, C14=2.0)
    assert scoring.score(fiche, offline) > scoring.score(fiche, UNIFORM)


def test_relevance_rule():
    assert not scoring.relevant(blank(C13="SO"))
    assert not scoring.relevant(blank(C13=2.0))
    assert scoring.relevant(blank(C13=5.0))
    assert scoring.relevant(blank())


def test_out_of_scale_rejected():
    for bad in (blank(C1=11.0), blank(risque=2)):
        try:
            scoring.score(bad, UNIFORM)
        except ValueError:
            continue
        raise AssertionError("valeur hors échelle acceptée")


def test_strengths_and_weaknesses():
    fiche = blank(C6=10.0, C14=9.0, C11=8.0, C2=7.0, C15=2.0)
    assert scoring.strengths(fiche) == ["C6", "C14", "C11"]
    assert scoring.weaknesses(fiche) == ["C15"]


class ScoringTests(unittest.TestCase):
    def test_undocumented_fiche_gets_neutral_score(self):
        test_undocumented_fiche_gets_neutral_score()

    def test_shrinkage_pulls_sparse_fiche_towards_neutral(self):
        test_shrinkage_pulls_sparse_fiche_towards_neutral()

    def test_safety_penalty(self):
        test_safety_penalty()

    def test_offline_context_raises_offline_criterion(self):
        test_offline_context_raises_offline_criterion()

    def test_relevance_rule(self):
        test_relevance_rule()

    def test_out_of_scale_rejected(self):
        test_out_of_scale_rejected()

    def test_strengths_and_weaknesses(self):
        test_strengths_and_weaknesses()

if __name__ == "__main__":
    unittest.main()
