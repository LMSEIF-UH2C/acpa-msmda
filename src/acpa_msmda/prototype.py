"""Demonstration scoring pipeline, not validated for production use."""
from dataclasses import dataclass
from typing import Mapping, Sequence
from .contracts import CRITERIA_COUNT, CriterionVector, WeightVector, ContextRequest

# Demonstration terms only. No statistical classifier, automatic language detection,
LEXICON = {
    'basketball': ('basketball', 'basket', 'كرة السلة'),
    'athletics': ('athlétisme', 'athletics', 'ألعاب القوى'),
    'budget': ('budget', 'cost', 'coût', 'ميزانية'),
    'offline': ('hors ligne', 'offline', 'sans connexion', 'بدون إنترنت'),
    'accessibility': ('handicap', 'inclusion', 'accessibilité', 'disability', 'إعاقة'),
}
# Weight multipliers are illustrative and must be reviewed against primary rules.
BOOSTS = {'budget': {13: 1.0}, 'offline': {5: 1.0}, 'accessibility': {11: 1.0}}

@dataclass(frozen=True)
class ContextResult:
    language: str
    flags: tuple[str, ...]
    weights: WeightVector

@dataclass(frozen=True)
class ToolRecord:
    identifier: str
    name: str
    criteria: CriterionVector
    safety_risk: bool = False

@dataclass(frozen=True)
class Recommendation:
    identifier: str
    name: str
    raw_score: float
    relative_score: float
    explanation: str


def analyze(request: ContextRequest) -> ContextResult:
    text = request.text.casefold()
    flags = tuple(key for key, terms in LEXICON.items() if any(term.casefold() in text for term in terms))
    weights = [1.0] * CRITERIA_COUNT
    for flag in flags:
        for index, bonus in BOOSTS.get(flag, {}).items():
            weights[index] += bonus
    total = sum(weights)
    return ContextResult(request.language, flags, WeightVector(tuple(x / total for x in weights)))


def rank(tools: Sequence[ToolRecord], weights: WeightVector, safety_penalty: float = 0.15) -> list[Recommendation]:
    if not (0 <= safety_penalty < 1):
        raise ValueError('Safety penalty must be in [0,1)')
    if not tools:
        return []
    if len({x.identifier for x in tools}) != len(tools):
        raise ValueError('Duplicate tool identifiers')
    scored = []
    for tool in tools:
        raw = sum(a*b for a,b in zip(weights.values, tool.criteria.values))
        if tool.safety_risk:
            raw *= (1-safety_penalty)
        scored.append((tool,raw))
    low, high = min(s for _,s in scored),max(s for _,s in scored)
    result=[]
    for tool,raw in scored:
        relative = 100*(raw-low)/(high-low) if high>low else 100.0
        result.append(Recommendation(tool.identifier, tool.name, round(raw,4), round(relative,1),
            'Score composite illustratif; classement relatif au catalogue fourni, sans validation experte.'))
    return sorted(result,key=lambda x:(-x.raw_score,x.identifier))


def demonstrate(query: str, language: str = 'fr') -> dict:
    """Entirely synthetic two-item demo, no connection to actual tool benchmarks."""
    context=analyze(ContextRequest(query,language))
    tools=[ToolRecord('SYN-A','Outil fictif A',CriterionVector(tuple([6.0]*18))),
           ToolRecord('SYN-B','Outil fictif B',CriterionVector(tuple([7.0]*18)))]
    recommendations=rank(tools,context.weights)
    return {'flags': list(context.flags),'weights': list(context.weights.values),
            'recommendations':[r.__dict__ for r in recommendations],
            'status':'DEMONSTRATION SYNTHETIQUE NON VALIDEE'}
