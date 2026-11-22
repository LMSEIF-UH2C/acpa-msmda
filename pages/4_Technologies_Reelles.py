"""Trouver une technologie : suggestions selon le contexte et fiches du catalogue."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from acpa_msmda import feedback  # noqa: E402
from acpa_msmda import session_context as ctx  # noqa: E402
from acpa_msmda.real_catalog import load_real_tools, match_pending_tools, match_real_tools  # noqa: E402
from acpa_msmda.ui import PRIVACY_NOTE, SEARCH, configure_page, page_header  # noqa: E402

DOCUMENTED = ("OFFICIAL_SOURCE_FEATURES_ONLY", "FEATURES_VERIFIED_ON_OFFICIAL_SITE")
PAGE_SIZE = 12

S = st.session_state


def _vote(tool_id: str, useful: bool) -> None:
    """Enregistre l'avis donné sur une fiche (un avis par fiche et par session, modifiable)."""
    if feedback.apply_vote(ctx.store(S).setdefault("votes", {}), tool_id, useful):
        ctx.put(S, "vote_flash", "Merci, votre avis est enregistré.")


configure_page(SEARCH)
flash = ctx.store(S).pop("vote_flash", None)
if flash:
    st.toast(flash, icon=":material/thumb_up:")
page_header(SEARCH)

st.subheader("Suggestions pour votre séance")
if st.button("Partir de ma séance : " + ctx.summary(S), icon=":material/assignment:"):
    ctx.put(S, "search_context", ctx.search_query(S))
    ctx.put(S, "search_query", ctx.search_query(S))
context = st.text_area("Activité, objectif et contraintes",
                       placeholder="Ex. endurance, 35 élèves, sans connexion, budget limité",
                       max_chars=1000, height=95, **ctx.bind(S, "search_context", ""))
st.caption(PRIVACY_NOTE)
if st.button("Voir les suggestions", type="primary", use_container_width=True):
    if context.strip():
        ctx.put(S, "search_query", context.strip())
    else:
        ctx.put(S, "search_query", None)
        st.warning("Décrivez votre activité ou vos contraintes pour obtenir des suggestions.")

query = ctx.store(S).get("search_query")
if query:
    result = match_real_tools(query)
    if not result["matches"]:
        st.info(
            "Voici des pistes pour votre contexte. Les fiches vérifiées ne couvrent pas encore "
            "toutes les activités et contraintes : consultez les applications à vérifier "
            "ci-dessous, ou adaptez une solution pédagogique sans application."
        )
        st.markdown("**Alternatives directement utilisables en séance**")
        st.markdown(
            "- Observation entre pairs avec une grille simple de critères.\n"
            "- Chronométrage et relevé des performances sur papier.\n"
            "- Organisation d'ateliers tournants et comparaison des progrès."
        )
    for tool in result["matches"][:8]:
        with st.expander(f"{tool['name']} · {tool['category']}"):
            st.write("Correspond à : " + ", ".join(tool["matched_terms"]))
            if tool.get("features"):
                st.write("Fonctions : " + ", ".join(tool["features"][:4]))
            if tool.get("platforms"):
                st.caption("Plateformes : " + ", ".join(tool["platforms"]))
            for note in tool.get("cautions", []):
                if note:
                    st.caption(note)
            if tool.get("source_url"):
                st.link_button("Site de l'éditeur", tool["source_url"])
    if len(result["matches"]) > 8:
        st.caption(f"{len(result['matches']) - 8} autres outils correspondent : précisez votre recherche.")
    scores = {k: feedback.score(v) for k, v in feedback.tallies().items()}
    leads = match_pending_tools(query, votes=scores)
    if leads:
        st.markdown("**Autres pistes à vérifier**")
        st.caption("Applications réelles repérées dans les magasins ; leurs fonctions n'ont pas encore été "
                   "vérifiées. Celles jugées utiles par d'autres enseignants apparaissent en premier.")
        for tool in leads:
            with st.expander(f"{tool['name']} · {tool['category']}"):
                st.write("Correspond à : " + ", ".join(tool["matched_terms"]))
                if tool.get("source_url"):
                    st.link_button("Voir l'application", tool["source_url"])

st.divider()
st.subheader("Catalogue")
catalogue = load_real_tools()
left, right = st.columns(2)
with left:
    category = st.selectbox("Famille d'outils", ["Toutes"] + sorted({t["category"] for t in catalogue}))
with right:
    name = st.text_input("Nom de l'outil", placeholder="Ex. Kinovea")
include_pending = st.toggle("Inclure les fiches en cours de documentation", value=False)
pending_count = sum(t.get("evidence_status") not in DOCUMENTED for t in catalogue)
if not include_pending:
    st.caption(f"Seules les fiches dont les fonctions ont été vérifiées sur le site de l'éditeur sont affichées. "
               f"{pending_count} autres outils sont en cours de documentation : activez l'interrupteur pour les voir.")

opinions = feedback.tallies()
filtered = [
    t for t in catalogue
    if (category == "Toutes" or t["category"] == category)
    and name.casefold() in t["name"].casefold()
    and (include_pending or t.get("evidence_status") in DOCUMENTED)
]
# Les fiches jugées utiles par les enseignants remontent. L'ordre est figé pour la visite en cours :
# une fiche ne change pas de place sous le doigt de l'enseignant qui vient de voter.
ranking = ctx.store(S).setdefault("ranking", {k: feedback.score(v) for k, v in opinions.items()})
filtered.sort(key=lambda t: -ranking.get(t["id"], 0))
if not filtered:
    st.info("Aucune fiche ne correspond à ces filtres."
            + ("" if include_pending else " Activez l'interrupteur pour inclure les fiches en cours de documentation."))
pages = max(1, (len(filtered) + PAGE_SIZE - 1) // PAGE_SIZE)
page = st.number_input("Page", min_value=1, max_value=pages, value=1, step=1) if pages > 1 else 1
for tool in filtered[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]:
    documented = tool.get("evidence_status") in DOCUMENTED
    with st.expander(f"{tool['name']} · {tool['category']}"):
        if not documented:
            st.caption("Fiche en cours de documentation : fonctionnalités non vérifiées.")
        if tool.get("features"):
            st.write("Fonctions : " + ", ".join(tool["features"]))
        if tool.get("platforms"):
            st.write("Plateformes : " + ", ".join(tool["platforms"]))
        if tool.get("pricing"):
            st.write("Tarif : " + tool["pricing"])
        if tool.get("offline"):
            st.write("Hors connexion : " + tool["offline"])
        if tool.get("caution") and documented:
            st.caption(tool["caution"])
        if tool.get("source_url"):
            st.link_button("Site de l'éditeur", tool["source_url"])
        st.caption(feedback.label(opinions.get(tool["id"])))
        mine = ctx.store(S).get("votes", {}).get(tool["id"])
        yes, no = st.columns(2)
        yes.button("Utile en séance", key=f"yes_{tool['id']}", icon=":material/thumb_up:",
                   type="primary" if mine is True else "secondary", use_container_width=True,
                   on_click=_vote, args=(tool["id"], True))
        no.button("Pas utile", key=f"no_{tool['id']}", icon=":material/thumb_down:",
                  type="primary" if mine is False else "secondary", use_container_width=True,
                  on_click=_vote, args=(tool["id"], False))
st.caption("Vos avis sont anonymes : seuls la fiche, l'avis et la date sont enregistrés. "
           "Ils font remonter les outils utiles pour tous les enseignants.")
st.caption("Vérifiez les conditions d'utilisation et l'âge minimal requis avant tout usage avec des élèves.")
