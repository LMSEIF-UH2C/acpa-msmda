"""Synthetic educational-technology catalogue: no product facts or expert ratings."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Sequence
from .contracts import CriterionVector
from .prototype import ToolRecord

CATALOG_PATH = Path(__file__).resolve().parents[2] / 'data' / 'synthetic_tools.json'
CRITERION_NAMES = (
 'Précision des capteurs','Latence et temps de réponse','Fiabilité système',
 'Sécurité des données','Interopérabilité','Fonctionnement hors ligne',
 'Consommation énergétique','Efficacité apprentissage moteur','Engagement élèves',
 'Motivation intrinsèque','Facilité d’usage enseignant','Accessibilité et inclusion',
 'Alignement programme EPS','Coût total de possession','Scalabilité',
 'Support et maintenance','Intégration systèmes existants','Retour sur investissement'
)

def load_catalog(path: Path | str = CATALOG_PATH) -> tuple[ToolRecord, ...]:
    path = Path(path)
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('dataset_type') != 'SYNTHETIC_DEMONSTRATION':
        raise ValueError('Catalogue must explicitly be synthetic demonstration data')
    items=data.get('tools')
    if not isinstance(items,list) or not items:
        raise ValueError('Catalogue must contain a non-empty list of tools')
    records=[]
    for item in items:
        if not isinstance(item,dict) or not isinstance(item.get('id'),str) or not item['id'].strip():
            raise ValueError('Every catalogue record needs a non-empty ID')
        if not isinstance(item.get('name'),str) or not item['name'].strip():
            raise ValueError('Every catalogue record needs a non-empty name')
        if item.get('evidence_status') != 'SYNTHETIC_NOT_EVALUATED':
            raise ValueError('Unsupported evidence status')
        if not isinstance(item.get('criteria'), list):
            raise ValueError('Criteria must be a list')
        if not isinstance(item.get('safety_risk', False), bool):
            raise ValueError('Safety risk must be a boolean')
        records.append(ToolRecord(item['id'], item['name'], CriterionVector(tuple(item['criteria'])), item.get('safety_risk', False)))
    if len({r.identifier for r in records}) != len(records):
        raise ValueError('Duplicate catalogue IDs')
    return tuple(records)

def compare_catalog(query: str, language: str='fr', path: Path | str = CATALOG_PATH) -> dict:
    from .contracts import ContextRequest
    from .context_engine import evaluate
    result=evaluate(ContextRequest(query,language),load_catalog(path))
    result['catalogue_status']='SYNTHETIC_NOT_EXPERT_EVALUATED'
    result['criteria_labels']=list(CRITERION_NAMES)
    result['relative_score_warning']='Relative scores change when catalogue membership changes; 100 is not evidence of perfect quality.'
    return result
