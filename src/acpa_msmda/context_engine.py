"""Rule-based, demonstrative context analysis and criterion weighting.

The heuristic engine is not calibrated against real observations.
"""
import re
import unicodedata
from dataclasses import dataclass
from typing import Sequence
from .contracts import CRITERIA_COUNT, CriterionVector, WeightVector, ContextRequest
from .prototype import ToolRecord, Recommendation, rank

LEXICON = {
 'sports_collectifs': ('football','basketball','volleyball','handball','rugby','soccer','كرة السلة','كرة القدم','كرة اليد','الكرة الطائرة'),
 'sports_individuels': ('athletisme','natation','gymnastique','judo','tennis','athletics','swimming','gymnastics','سباحة','ألعاب القوى','جمباز','الجري'),
 'niveaux': ('college','lycee','primaire','baccalaureat','brevet','school','ثانوي','ابتدائي'),
 'contraintes': ('budget','effectif','infrastructure','handicap','rural','تكلفة','ميزانية','disability'),
}
CONTEXT_BOOSTS = {
 'connectivite_faible': {'C6': .25,'C3': .20,'C2': .15},
 'grand_effectif': {'C9': .20,'C11': .18,'C15': .16},
 'budget_serre': {'C14': .30,'C18': .25,'C7': .10},
 'inclusion': {'C12': .30,'C11': .20,'C4': .15},
}

# Arabe : formes d'une même lettre ramenées à une seule, et article ou préfixe collé retiré, pour que
# « الجري » et « جري », « كرة » et « كره » se rejoignent. Appliqué au texte comme au vocabulaire.
_AR_LETTERS = str.maketrans({'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ٱ': 'ا', 'ة': 'ه', 'ى': 'ي', 'ؤ': 'و', 'ئ': 'ي',
                             'ـ': None})
_AR_AND = re.compile(r'(?<!\w)و(?=[\u0621-\u064a]{3,})')
_AR_PREFIX = re.compile(r'(?<!\w)(?:وال|فال|بال|كال|لل|ال)(?=[\u0621-\u064a]{2,})')


def normalize_text(text: str) -> str:
    text = unicodedata.normalize('NFKD', text.casefold())
    text = ''.join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r'[^\w\s]', ' ', text)
    if re.search(r'[\u0600-\u06ff]', text):
        text = _AR_PREFIX.sub('', _AR_AND.sub('', text.translate(_AR_LETTERS)))
    return text


_EN_WORDS = {'the', 'and', 'with', 'for', 'without', 'my', 'students', 'pupils', 'class', 'no', 'need',
             'running', 'lesson', 'kids', 'children', 'team', 'teams', 'to', 'in', 'of', 'a', 'an', 'tool', 'app'}
_FR_WORDS = {'le', 'la', 'les', 'des', 'du', 'de', 'avec', 'pour', 'sans', 'eleves', 'une', 'un', 'et', 'en',
             'seance', 'classe', 'course', 'au', 'aux', 'mes', 'outil', 'application', 'connexion'}


def detect_language(text: str) -> str:
    """Langue probable d'une demande : arabe si l'écriture arabe domine, sinon anglais ou français
    selon les mots outils les plus fréquents (français par défaut)."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 'fr'
    arabic = sum('\u0600' <= c <= '\u06ff' for c in letters)
    if arabic / len(letters) >= 0.3:
        return 'ar'
    words = normalize_text(text).split()
    en = sum(w in _EN_WORDS for w in words)
    fr = sum(w in _FR_WORDS for w in words)
    if re.search(r'[éèêàùçôî]', text.casefold()):
        fr += 1
    return 'en' if en > fr else 'fr'

def tokenize(text: str) -> tuple[str, ...]:
    return tuple(x for x in normalize_text(text).split() if len(x) > 2 and x not in {'les','des','une','pour','avec','the','and','dans'})

def _whole_phrase(phrase: str, normalized_text: str) -> bool:
    if not phrase.strip():
        return False
    return bool(re.search(r'(?<!\w)' + re.escape(phrase.strip()) + r'(?!\w)', normalized_text))

def extract_flags(text: str, lexicon=LEXICON) -> tuple[str, ...]:
    canonical = normalize_text(text)
    canonical = re.sub(r'(?<!\w)و(?=[\u0621-\u064a]{3,})', '', canonical)
    flags = {category for category, phrases in lexicon.items() if any(_whole_phrase(normalize_text(term), canonical) for term in phrases)}
    patterns = {
      'connectivite_faible': ('sans connexion','hors ligne','offline','internet faible','بدون انترنت','بدون اتصال','لا يوجد انترنت','انترنت ضعيف','connexion instable','pas de wifi','sans internet','no internet','without internet','no wifi','poor connectivity','limited internet','unstable connection'),
      'grand_effectif': ('grand effectif','classe nombreuse','large class','large group','many students','عدد كبير','قسم مكتظ','فصل مكتظ','تلاميذ كثر'),
      'budget_serre': ('budget limité','petit budget','budget serre','budget serré','sans budget','faible budget','low budget','limited budget','small budget','tight budget','on a budget','low cost','تكلفة منخفضة','ميزانية محدودة','ميزانية ضعيفة','ميزانية قليلة','ميزانية'),
      'inclusion': ('handicap','inclusion','accessibilité','accessibilite','disability','accessibility','inclusive','special needs','إعاقة','ذوي الاعاقة','احتياجات خاصة','ادماج'),
    }
    for flag,phrases in patterns.items():
        if any(_whole_phrase(normalize_text(phrase), canonical) for phrase in phrases): flags.add(flag)
    # Negative formulations should not imply a constraint. This is a limited
    # deterministic guard, not linguistic negation understanding.
    if any(_whole_phrase(p, canonical) for p in ('sans contrainte budgetaire','aucune contrainte budgetaire','budget illimite','unlimited budget','no budget limit','unrestricted budget','ميزانية غير محدودة')):
        flags.discard('budget_serre')
    if any(_whole_phrase(p, canonical) for p in ('connexion stable','internet stable','good internet','stable connection','reliable internet','اتصال مستقر')):
        flags.discard('connectivite_faible')
    return tuple(sorted(flags))

@dataclass(frozen=True)
class Analysis:
    language: str
    tokens: tuple[str,...]
    flags: tuple[str,...]
    weights: WeightVector
    confidence: float | None # unsupported until evaluation; None rather than fabricated metric

def coefficients(flags: Sequence[str]) -> WeightVector:
    alpha={f'C{i}':1/18 for i in range(1,19)}
    for flag in set(flags):
        for key,bonus in CONTEXT_BOOSTS.get(flag,{}).items():
            alpha[key]+=bonus
    total=sum(alpha.values())
    return WeightVector(tuple(alpha[f'C{i}']/total for i in range(1,19)))

def analyze_context(request: ContextRequest) -> Analysis:
    tokens=tokenize(request.text)
    flags=extract_flags(request.text)
    return Analysis(request.language,tokens,flags,coefficients(flags),None)

def evaluate(request: ContextRequest, tools: Sequence[ToolRecord], safety_penalty:float=.15) -> dict:
    analysis=analyze_context(request)
    recommendations=rank(tools,analysis.weights,safety_penalty=safety_penalty)
    return {'language':analysis.language,'tokens':list(analysis.tokens),'flags':list(analysis.flags),
      'alpha':{f'C{i}':analysis.weights.values[i-1] for i in range(1,19)},
      'confidence':None,'recommendations':[r.__dict__ for r in recommendations],
      'validation_status':'ILLUSTRATIVE_ONLY'}
