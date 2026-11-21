"""Trouver une technologie : suggestions selon le contexte et fiches du catalogue."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from acpa_msmda import session_context as ctx  # noqa: E402
from acpa_msmda.real_catalog import load_real_tools, match_real_tools  # noqa: E402
from acpa_msmda.ui import PRIVACY_NOTE, SEARCH, configure_page  # noqa: E402

DOCUMENTED = ("OFFICIAL_SOURCE_FEATURES_ONLY", "FEATURES_VERIFIED_ON_OFFICIAL_SITE")
PAGE_SIZE = 12

S = st.session_state
configure_page(SEARCH)
st.title(SEARCH.title)
st.caption(SEARCH.summary)

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
        st.info("Aucun outil documenté ne correspond. Parcourez le catalogue ci-dessous : "
                "une solution sans application peut aussi convenir.")
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

filtered = [
    t for t in catalogue
    if (category == "Toutes" or t["category"] == category)
    and name.casefold() in t["name"].casefold()
    and (include_pending or t.get("evidence_status") in DOCUMENTED)
]
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
st.caption("Vérifiez les conditions d'utilisation et l'âge minimal requis avant tout usage avec des élèves.")
