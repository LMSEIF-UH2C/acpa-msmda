"""Trouver une technologie : suggestions selon le contexte et fiches du catalogue."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from acpa_msmda import feedback  # noqa: E402
from acpa_msmda import session_context as ctx  # noqa: E402
from acpa_msmda.real_catalog import load_real_tools, recommend  # noqa: E402
from acpa_msmda import scoring  # noqa: E402
from acpa_msmda import store_info  # noqa: E402
from acpa_msmda import i18n  # noqa: E402
from acpa_msmda.i18n import t, tj  # noqa: E402
from acpa_msmda.keywords import label as keyword_label  # noqa: E402
from acpa_msmda.ui import PRIVACY_NOTE, SEARCH, configure_page, page_header  # noqa: E402

DOCUMENTED = ("OFFICIAL_SOURCE_FEATURES_ONLY", "FEATURES_VERIFIED_ON_OFFICIAL_SITE")
PAGE_SIZE = 12
REC_STEP = 10

S = st.session_state


def _vote(tool_id: str, useful: bool) -> None:
    """Enregistre l'avis donné sur une fiche (un avis par fiche et par session, modifiable)."""
    if feedback.apply_vote(ctx.store(S).setdefault("votes", {}), tool_id, useful):
        ctx.put(S, "vote_flash", t("Merci, votre avis est enregistré."))


def _vote_buttons(tool: dict, prefix: str) -> None:
    """Deux boutons d'avis sous une fiche ; l'avis choisi est mis en valeur."""
    mine = ctx.store(S).get("votes", {}).get(tool["id"])
    yes, no = st.columns(2)
    yes.button(t("Utile en séance"), key=f"{prefix}yes_{tool['id']}", icon=":material/thumb_up:",
               type="primary" if mine is True else "secondary", use_container_width=True,
               on_click=_vote, args=(tool["id"], True))
    no.button(t("Pas utile"), key=f"{prefix}no_{tool['id']}", icon=":material/thumb_down:",
              type="primary" if mine is False else "secondary", use_container_width=True,
              on_click=_vote, args=(tool["id"], False))


def _evaluation(tool: dict) -> None:
    """Score de l'application pour la demande, points forts et points de vigilance."""
    rated = tool.get("criteria_scores")
    if not rated or tool.get("criteria_total") is None:
        return
    st.markdown("**" + t("Score : {n}/100", n=f"{tool['criteria_total']:.0f}") + "**")
    st.progress(min(1.0, tool["criteria_total"] / 100))
    strong, weak = scoring.strengths(rated), scoring.weaknesses(rated)
    if strong:
        st.write(t("Points forts : ") + tj(scoring.PUBLIC_LABELS[c] for c in strong))
    if weak:
        st.write(t("Points de vigilance : ") + tj(scoring.PUBLIC_LABELS[c] for c in weak))
    st.caption(t("D'après les informations publiées par l'éditeur."))


def _store_block(tool: dict) -> None:
    """Fonctions annoncées et informations de la fiche du magasin."""
    announced = store_info.announced(tool)
    if announced:
        st.write(t("Fonctions annoncées par l'éditeur : ") + tj(announced))
    rows = store_info.details(tool)
    if rows:
        st.caption(" · ".join(f"{label}{i18n.colon()}{value}" for label, value in rows))
    note = store_info.source_note(tool)
    if note:
        st.caption(note)


def _show_more() -> None:
    ctx.put(S, "rec_shown", ctx.store(S).get("rec_shown", REC_STEP) + REC_STEP)


configure_page(SEARCH)
flash = ctx.store(S).pop("vote_flash", None)
if flash:
    st.toast(flash, icon=":material/thumb_up:")
page_header(SEARCH)

st.subheader(t("Suggestions pour votre séance"))
if st.button(t("Partir de ma séance : ") + ctx.summary(S), icon=":material/assignment:"):
    ctx.put(S, "search_context", ctx.search_query(S))
    ctx.put(S, "search_query", ctx.search_query(S))
context = st.text_area(t("Activité, objectif et contraintes"),
                       placeholder=t("Ex. endurance, 35 élèves, sans connexion, budget limité"),
                       max_chars=1000, height=95, **ctx.bind(S, "search_context", ""))
st.caption(t(PRIVACY_NOTE))
if st.button(t("Voir les suggestions"), type="primary", use_container_width=True):
    if context.strip():
        ctx.put(S, "search_query", context.strip())
    else:
        ctx.put(S, "search_query", None)
        st.warning(t("Décrivez votre activité ou vos contraintes pour obtenir des suggestions."))

query = ctx.store(S).get("search_query")
if query:
    if ctx.store(S).get("rec_query") != query:  # nouvelle demande : on repart des premiers résultats
        ctx.put(S, "rec_query", query)
        ctx.put(S, "rec_shown", REC_STEP)
        ctx.put(S, "rec_ranking", {k: feedback.score(v) for k, v in feedback.tallies().items()})
    result = recommend(query, votes=ctx.store(S)["rec_ranking"])
    matches = result["matches"]
    if not matches:
        st.info(t("Aucune application du catalogue ne correspond à ces mots. Précisez l'activité "
                  "(ex. course, basket, gymnastique) ou le besoin (chronométrage, vidéo, évaluation)."))
        st.markdown("**" + t("Alternatives directement utilisables en séance") + "**")
        st.markdown("\n".join("- " + t(x) for x in (
            "Observation entre pairs avec une grille simple de critères.",
            "Chronométrage et relevé des performances sur papier.",
            "Organisation d'ateliers tournants et comparaison des progrès.")))
    else:
        verified = sum(t["verified"] for t in matches)
        st.markdown("**" + t("{n} applications correspondent", n=len(matches)) + "** · "
                    + t("{n} à fonctions vérifiées", n=verified))
        st.caption(t("Classées selon vos besoins, vos contraintes et les avis des enseignants. Les fiches "
                     "« À vérifier » sont des applications réelles dont les fonctions n'ont pas encore été contrôlées."))
        shown = ctx.store(S).get("rec_shown", REC_STEP)
        opinions = feedback.tallies()
        for tool in matches[:shown]:
            status = t("Fonctions vérifiées") if tool["verified"] else t("À vérifier")
            total = tool["criteria_total"]
            label = f"{tool['name']} · {status}" + (f" · {total:.0f}/100" if total is not None else "")
            with st.expander(label):
                if tool["verified"]:
                    st.badge(status, icon=":material/verified:", color="green")
                else:
                    st.badge(status, icon=":material/pending:", color="orange")
                st.write(t("Correspond à : ") + tj(keyword_label(k) for k in tool["matched_terms"]))
                _evaluation(tool)
                st.caption(t(tool["category"]))
                if tool.get("features"):
                    st.write(t("Fonctions : ") + tj(tool["features"][:4]))
                if tool.get("platforms"):
                    st.caption(t("Plateformes : ") + tj(tool["platforms"]))
                _store_block(tool)
                if tool.get("offline_hint") and (tool.get("store") or {}).get("uses_internet") is not False:
                    st.caption(t("Fonctionnement hors connexion annoncé par l'éditeur."))
                for note in tool.get("cautions", []):
                    if note:
                        st.caption(t(note))
                if tool.get("source_url"):
                    st.link_button(t("Voir l'application"), tool["source_url"])
                st.caption(feedback.label(opinions.get(tool["id"])))
                _vote_buttons(tool, "rec_")
        if len(matches) > shown:
            st.button(t("Afficher {n} de plus ({rest} restantes)", n=min(REC_STEP, len(matches) - shown),
                        rest=len(matches) - shown), on_click=_show_more, use_container_width=True)

st.divider()
st.subheader(t("Catalogue"))
catalogue = load_real_tools()
left, right = st.columns(2)
with left:
    category = st.selectbox(t("Famille d'outils"), ["Toutes"] + sorted({x["category"] for x in catalogue}), format_func=t)
with right:
    name = st.text_input(t("Nom de l'outil"), placeholder=t("Ex. Kinovea"))
include_pending = st.toggle(t("Inclure les fiches à vérifier"), value=True)
pending_count = sum(t.get("evidence_status") not in DOCUMENTED for t in catalogue)
if not include_pending:
    st.caption(t("Seules les fiches dont les fonctions ont été vérifiées sur le site de l'éditeur sont affichées. "
                 "{n} autres applications sont à vérifier : activez l'interrupteur pour les voir.", n=pending_count))

opinions = feedback.tallies()
filtered = [
    x for x in catalogue
    if (category == "Toutes" or x["category"] == category)
    and name.casefold() in x["name"].casefold()
    and (include_pending or x.get("evidence_status") in DOCUMENTED)
]
# Les fiches jugées utiles par les enseignants remontent. L'ordre est figé pour la visite en cours :
# une fiche ne change pas de place sous le doigt de l'enseignant qui vient de voter.
ranking = ctx.store(S).setdefault("ranking", {k: feedback.score(v) for k, v in opinions.items()})
filtered.sort(key=lambda x: -ranking.get(x["id"], 0))
if not filtered:
    st.info(t("Aucune fiche ne correspond à ces filtres.")
            + ("" if include_pending else " " + t("Activez l'interrupteur pour inclure les fiches à vérifier.")))
pages = max(1, (len(filtered) + PAGE_SIZE - 1) // PAGE_SIZE)
page = st.number_input(t("Page"), min_value=1, max_value=pages, value=1, step=1) if pages > 1 else 1
for tool in filtered[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]:
    documented = tool.get("evidence_status") in DOCUMENTED
    with st.expander(f"{tool['name']} · {t(tool['category'])}"):
        if not documented:
            st.caption(t("Fonctions non vérifiées en séance."))
        if tool.get("features"):
            st.write(t("Fonctions : ") + tj(tool["features"]))
        _store_block(tool)
        for note in store_info.cautions(tool):
            st.caption(note)
        if tool.get("platforms"):
            st.write(t("Plateformes : ") + tj(tool["platforms"]))
        if tool.get("pricing"):
            st.write(t("Tarif : ") + t(tool["pricing"]))
        if tool.get("offline"):
            st.write(t("Hors connexion : ") + t(tool["offline"]))
        if tool.get("caution") and documented:
            st.caption(t(tool["caution"]))
        if tool.get("source_url"):
            st.link_button(t("Site de l'éditeur"), tool["source_url"])
        st.caption(feedback.label(opinions.get(tool["id"])))
        _vote_buttons(tool, "")
st.caption(t("Vos avis sont anonymes : seuls la fiche, l'avis et la date sont enregistrés. "
             "Ils font remonter les outils utiles pour tous les enseignants."))
st.caption(t("Vérifiez les conditions d'utilisation et l'âge minimal requis avant tout usage avec des élèves."))
