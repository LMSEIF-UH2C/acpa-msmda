"""ACPA/MSMDA public web demonstrator.

Uses the published heuristic engine and a fictional catalogue only.
No credentials, private modules, network APIs or database are required.
Not intended for student or other personal data.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from acpa_msmda.catalog import compare_catalog  # noqa: E402


LANGUAGE_NAMES = {"fr": "Français", "en": "English", "ar": "العربية"}
EXAMPLES = {
    "fr": "Basketball au collège, classe nombreuse, budget limité et sans connexion Internet",
    "en": "Basketball class, large group, limited budget and no internet",
    "ar": "كرة السلة قسم مكتظ ميزانية محدودة بدون انترنت",
}
WORDS = {
    "fr": {
        "subtitle": "Exploration des recommandations technopédagogiques en EPS",
        "caution": "DÉMONSTRATION SCIENTIFIQUE — outils fictifs, scores illustratifs et algorithme heuristique non validé. Ne pas utiliser pour des décisions concernant des élèves.",
        "privacy": "Ne saisissez aucun nom, dossier d'élève ou autre donnée personnelle. L'hébergeur traite les requêtes pendant la session.",
        "context": "Décrivez un contexte EPS fictif (1 à 1 000 caractères)",
        "run": "Analyser le contexte",
        "empty": "Veuillez saisir une description non vide.",
        "error": "Le calcul a échoué. Vérifiez la saisie.",
        "results": "Classement illustratif",
        "ranking_note": "Les scores sont relatifs aux cinq profils fictifs du catalogue. Une note de 100 ne signifie pas qu'un outil est parfait.",
        "rank": "Rang",
        "tool": "Profil fictif",
        "score": "Score composite / 10",
        "relative": "Score relatif / 100",
        "flags": "Contraintes et éléments détectés",
        "none": "Aucune expression de contexte reconnue par les règles actuelles.",
        "criteria": "Pondération des 18 critères",
        "criterion": "Critère",
        "weight": "Poids (%)",
        "details": "Détails techniques",
        "confidence": "Le moteur ne fournit pas d'indicateur de confiance validé.",
        "download": "Exporter les résultats (JSON)",
        "footer": "Moteur public ACPA/MSMDA v0.1.1 — données synthétiques uniquement. Il ne remplace pas une évaluation experte.",
    },
    "en": {
        "subtitle": "Exploring context-aware physical education technology recommendations",
        "caution": "RESEARCH DEMONSTRATION — fictional tools, illustrative scores and an unvalidated heuristic. Do not use for decisions about pupils.",
        "privacy": "Do not enter names, student records or other personal data. The hosting provider processes requests during the session.",
        "context": "Describe a fictional PE teaching context (1–1,000 characters)",
        "run": "Analyze context",
        "empty": "Please enter a non-empty description.",
        "error": "The calculation failed. Please check your input.",
        "results": "Illustrative ranking",
        "ranking_note": "Scores are relative to the five fictional catalogue profiles. A score of 100 does not mean perfect quality.",
        "rank": "Rank",
        "tool": "Fictional profile",
        "score": "Composite score / 10",
        "relative": "Relative score / 100",
        "flags": "Detected context features",
        "none": "No context phrases were recognized by the current rules.",
        "criteria": "Weights for 18 criteria",
        "criterion": "Criterion",
        "weight": "Weight (%)",
        "details": "Technical details",
        "confidence": "The engine does not report a validated confidence indicator.",
        "download": "Export results (JSON)",
        "footer": "ACPA/MSMDA public engine v0.1.1 — synthetic data only. Not a replacement for expert evaluation.",
    },
    "ar": {
        "subtitle": "استكشاف توصيات الأدوات الرقمية في التربية البدنية",
        "caution": "نسخة بحثية تجريبية — أدوات افتراضية ودرجات توضيحية وخوارزمية استدلالية غير متحقق من صلاحيتها. لا تستخدم لاتخاذ قرارات تخص التلاميذ.",
        "privacy": "لا تدخل أسماء أو سجلات التلاميذ أو أي بيانات شخصية. يعالج مزود الاستضافة الطلبات خلال الجلسة.",
        "context": "صف سياقاً افتراضياً لتدريس التربية البدنية (من 1 إلى 1000 حرف)",
        "run": "تحليل السياق",
        "empty": "يرجى إدخال وصف غير فارغ.",
        "error": "تعذر إجراء التحليل. تحقق من المدخلات.",
        "results": "ترتيب توضيحي",
        "ranking_note": "الدرجات نسبية ضمن خمسة نماذج افتراضية فقط. الدرجة 100 لا تعني جودة مثالية.",
        "rank": "الترتيب",
        "tool": "نموذج افتراضي",
        "score": "الدرجة المركبة / 10",
        "relative": "الدرجة النسبية / 100",
        "flags": "عناصر السياق المكتشفة",
        "none": "لم تتعرف القواعد الحالية على عبارات سياقية.",
        "criteria": "أوزان المعايير الثمانية عشر",
        "criterion": "المعيار",
        "weight": "الوزن (%)",
        "details": "تفاصيل تقنية",
        "confidence": "لا يوفر المحرك مؤشراً موثوقاً للتحقق من الثقة.",
        "download": "تصدير النتائج (JSON)",
        "footer": "المحرك العام ACPA/MSMDA v0.1.1 — بيانات اصطناعية فقط. لا يحل محل التقييم الخبير.",
    },
}
FLAG_LABELS = {
    "connectivite_faible": "Connexion limitée / Limited connectivity / اتصال محدود",
    "grand_effectif": "Grand effectif / Large group / قسم مكتظ",
    "budget_serre": "Budget limité / Limited budget / ميزانية محدودة",
    "inclusion": "Inclusion / Accessibility / الإدماج",
}

st.set_page_config(page_title="ACPA/MSMDA — Démonstration", page_icon="🏃", layout="wide")
st.title("ACPA / MSMDA")
language = st.selectbox("Langue · Language · اللغة", ("fr", "en", "ar"), format_func=lambda x: LANGUAGE_NAMES[x])
labels = WORDS[language]
st.caption(labels["subtitle"])
st.warning(labels["caution"], icon="⚠️")
st.info(labels["privacy"], icon="🔒")

with st.form("context_form"):
    context = st.text_area(labels["context"], value=EXAMPLES[language], max_chars=1000, height=130)
    submitted = st.form_submit_button(labels["run"], type="primary")

if submitted:
    if not context.strip():
        st.error(labels["empty"])
        st.session_state.pop("acpa_result", None)
    else:
        try:
            outcome = compare_catalog(context.strip(), language)
        except (ValueError, TypeError, OSError, json.JSONDecodeError):
            st.error(labels["error"])
            st.session_state.pop("acpa_result", None)
        else:
            st.session_state["acpa_result"] = (language, outcome)

previous = st.session_state.get("acpa_result")
if previous is not None and previous[0] == language:
    result = previous[1]
    st.subheader(labels["results"])
    st.caption(labels["ranking_note"])
    recommendations = result["recommendations"]
    rows = [
        {
            labels["rank"]: index,
            labels["tool"]: item["name"],
            labels["score"]: item["raw_score"],
            labels["relative"]: item["relative_score"],
        }
        for index, item in enumerate(recommendations, start=1)
    ]
    st.dataframe(rows, hide_index=True, use_container_width=True)

    st.subheader(labels["flags"])
    flags = result.get("flags", [])
    if flags:
        st.write(" · ".join(FLAG_LABELS.get(flag, flag) for flag in flags))
    else:
        st.write(labels["none"])

    with st.expander(labels["criteria"]):
        weights = [
            {
                labels["criterion"]: name,
                labels["weight"]: round(result["alpha"][f"C{i}"] * 100, 2),
            }
            for i, name in enumerate(result["criteria_labels"], start=1)
        ]
        st.dataframe(weights, hide_index=True, use_container_width=True)
        st.caption(labels["confidence"])

    with st.expander(labels["details"]):
        st.json({
            "language": result["language"],
            "flags": result["flags"],
            "validation_status": result["validation_status"],
            "catalogue_status": result["catalogue_status"],
        })

    st.download_button(
        labels["download"],
        data=json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False),
        file_name="acpa_msmda_demonstration.json",
        mime="application/json",
    )

st.divider()
st.caption(labels["footer"])
