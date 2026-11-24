"""Concevoir une séance : phases, activités, supports et export."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from acpa_msmda import session_context as ctx  # noqa: E402
from acpa_msmda.scenario_engine import export_scenario_csv, recommend_phase_tools, validate_scenario  # noqa: E402
from acpa_msmda.scenario_templates import apply_template, load_templates, scenario_checks  # noqa: E402
from acpa_msmda.learning_library import load_situations, details, diagram_svg, apply_situation, selected_situation
from acpa_msmda.pdf import scenario_pdf, situation_pdf
from acpa_msmda.teaching_photos import clean_photo
from acpa_msmda.adaptive_studio import redistribute_minutes, balanced_groups, adaptation_notes  # noqa: E402
from acpa_msmda.i18n import t, tj  # noqa: E402
from acpa_msmda.ui import PRIVACY_NOTE, STUDIO, configure_page, page_header  # noqa: E402

PHASE_NAMES = ("Diagnostic", "Mise en activité", "Apprentissage", "Régulation", "Évaluation")
PHASE_MINUTES = (5, 10, 30, 10, 5)
SUPPORTS = ("Vidéo", "Audio", "Quiz", "QR code", "Fiche numérique", "Démonstration", "Capteurs", "Analyse vidéo")
MODALITIES = ("Présentiel", "Hybride", "À distance", "Classe inversée", "Autonomie accompagnée")

S = st.session_state
configure_page(STUDIO)
page_header(STUDIO, PRIVACY_NOTE)

if ctx.get(S, "guided_path") == "offline" and ctx.get(S, "connectivity") == "Aucune":
    st.info(t("Prévoyez des consignes imprimées, des démonstrations et des critères observables sans Internet."))
    st.page_link("pages/3_Espace_Enseignant.py", label=t("Organiser les ateliers"))
templates = load_templates()
left, right = st.columns([3, 1], vertical_alignment="bottom")
with left:
    selected = st.selectbox(t("Partir d'un modèle"), ["Séance vierge"] + [x["title"] for x in templates],
                            format_func=t, key="studio_template")
with right:
    if st.button(t("Charger le modèle"), disabled=selected == "Séance vierge", use_container_width=True):
        apply_template(next(x for x in templates if x["title"] == selected), S)
        ctx.put(S, "illustrated_situation", None)
        ctx.put(S, "teaching_photo", None)
        st.rerun()

ctx.render_context(st, S, fields=("activity", "level", "class_size", "duration", "connectivity",
                                  "devices", "cycle_number", "lesson_number", "equipment", "objectives"))
with st.expander(t("Bibliothèque de situations illustrées")):
    matching = [s for s in load_situations() if s["activity"] == ctx.get(S, "activity")
                and s["level"] == ctx.get(S, "level")]
    if not matching:
        st.caption(t("Aucune situation illustrée pour cette activité et ce niveau."))
    else:
        choices = {s["id"]: s for s in matching}
        sid = st.selectbox(t("Situation d’apprentissage"), list(choices),
                           format_func=lambda key: t(choices[key]["title"]))
        situation = choices[sid]
        d = details(situation)
        st.image(diagram_svg(situation["diagram"]), use_container_width=True)
        st.caption(t("Schéma indicatif, non à l’échelle. Bleu : pratiquants. Orange : défenseurs. Flèches : directions proposées."))
        st.caption(t("Proposition pédagogique à adapter et à valider."))
        for label, field in (("Objectif", "objective"), ("Organisation", "organisation"),
                             ("Critère de réussite", "success"), ("Simplifier", "easier"),
                             ("Complexifier", "harder"), ("Sécurité", "safety")):
            st.write("**" + t(label) + "** : " + d[field])
        if st.button(t("Remplacer la phase d’apprentissage"), key="apply_situation"):
            apply_situation(situation, S)
            st.rerun()
        st.download_button(t("Fiche illustrée (PDF)"), situation_pdf(situation),
                           f"{sid}.pdf", "application/pdf", key="situation_pdf")
    if selected_situation(S) and st.button(t("Retirer le schéma du scénario")):
        ctx.put(S, "illustrated_situation", None)
        st.rerun()
with st.expander(t("Photo pédagogique personnelle")):
    st.caption(t("Utilisez une photo de matériel ou de terrain sans personne identifiable. L’image est envoyée au serveur pour cette session ; elle peut figurer dans le PDF exporté."))
    if st.checkbox(t("Je dispose des droits et aucune personne identifiable ne figure sur la photo."), key="photo_permission"):
        uploaded = st.file_uploader(t("Photo JPEG ou PNG (5 Mo maximum)"), type=["jpg", "jpeg", "png"], key="photo_upload")
        if uploaded is not None and st.button(t("Ajouter la photo au scénario")):
            try:
                ctx.put(S, "teaching_photo", clean_photo(uploaded.getvalue()))
                ctx.put(S, "photo_context", (ctx.get(S, "activity"), ctx.get(S, "level")))
            except ValueError:
                st.error(t("Image invalide ou trop volumineuse."))
    photo = ctx.get(S, "teaching_photo") if ctx.get(S, "photo_context") == (ctx.get(S, "activity"), ctx.get(S, "level")) else None
    if ctx.get(S, "teaching_photo"):
        if photo:
            st.image(photo, use_container_width=True)
        if st.button(t("Supprimer la photo du scénario")):
            ctx.put(S, "teaching_photo", None)
            st.rerun()
modality = st.selectbox(t("Modalité"), MODALITIES, format_func=t, **ctx.bind(S, "modality", "Présentiel"))
prerequisites = st.text_input(t("Prérequis"), max_chars=300, **ctx.bind(S, "prerequisites", ""))

with st.expander(t("Adapter la séance à votre contexte")):
    current_minutes = [ctx.store(S).get(f"minutes_{i}", m) for i, m in enumerate(PHASE_MINUTES)]
    proposed = redistribute_minutes(current_minutes, int(ctx.get(S, "duration")))
    st.caption(t("Répartition proportionnelle proposée ; vérifiez les durées minimales nécessaires à la sécurité et aux apprentissages."))
    for phase, old, new in zip(PHASE_NAMES, current_minutes, proposed):
        st.write(f"{t(phase)} : {old} → {new} min")
    if st.button(t("Appliquer les durées proposées"), disabled=current_minutes == proposed):
        for i, minutes in enumerate(proposed):
            ctx.put(S, f"minutes_{i}", minutes)
        st.rerun()
    target = st.number_input(t("Effectif maximum souhaité par groupe"), min_value=1, max_value=150, **ctx.bind(S, "group_target", 6))
    sizes = balanced_groups(int(ctx.get(S, "class_size")), int(target))
    st.write(t("{n} groupes proposés", n=len(sizes)) + " : " + " / ".join(map(str, sizes)))
    st.caption(t("Organisation indicative : adaptez les groupes à l’espace, au matériel et aux besoins des élèves."))
    profile = st.selectbox(t("Maîtrise actuelle du groupe"), ["Hétérogène", "Découverte", "Approfondissement"],
                           format_func=t, **ctx.bind(S, "ability_profile", "Hétérogène"))
    limited_equipment = st.checkbox(t("Matériel limité"), **ctx.bind(S, "limited_equipment", False))
    limited_space = st.checkbox(t("Espace limité"), **ctx.bind(S, "limited_space", False))
    advice = adaptation_notes(profile, limited_equipment, limited_space, ctx.get(S, "connectivity"), ctx.get(S, "devices"))
    for note in advice:
        st.write("• " + note)
    export_advice = st.checkbox(t("Inclure les adaptations dans les exports"), **ctx.bind(S, "export_adaptations", False))

st.subheader(t("Déroulement"))
st.caption(t("Adaptez les activités, supports, critères de réussite et durées."))
connectivity = ctx.get(S, "connectivity")
rows = []
for i, (phase, default_minutes) in enumerate(zip(PHASE_NAMES, PHASE_MINUTES)):
    minutes_now = ctx.store(S).get(f"minutes_{i}", default_minutes)
    with st.expander(f"{i + 1}. {t(phase)} · " + t("{n} min", n=minutes_now), expanded=i == 2):
        col1, col2 = st.columns([3, 1])
        with col1:
            action = st.text_area(t("Activité, consignes et rôle des élèves"), max_chars=600,
                                  **ctx.bind(S, f"action_{i}", ""))
            supports = st.multiselect(t("Supports"), SUPPORTS, format_func=t, placeholder=t("Choisir un ou plusieurs supports"), **ctx.bind(S, f"supports_{i}", []))
            evaluation = st.text_input(t("Critères de réussite et retour aux élèves"), max_chars=300,
                                       **ctx.bind(S, f"evaluation_{i}", ""))
        with col2:
            minutes = int(st.number_input(t("Durée (min)"), min_value=0, max_value=240,
                                          **ctx.bind(S, f"minutes_{i}", default_minutes)))
        rows.append({"Phase": phase, "Durée (min)": minutes, "Activité / consignes": action,
                     "Supports": tj(supports), "Évaluation / feedback": evaluation})
        suggestions = recommend_phase_tools(phase, connectivity=connectivity, limit=5)
        if suggestions:
            st.markdown("**" + t("Outils à explorer pour cette phase") + "**")
            for tool in suggestions:
                label = tool["name"] + " · " + t(tool["category"])
                if not tool["documented"]:
                    label += " · " + t("à confirmer")
                st.markdown(f"- [{label}]({tool['source_url']})")
                if tool["notes"]:
                    st.caption(" ; ".join(tool["notes"]))
        else:
            st.caption(t("Aucun outil documenté pour cette phase. Un support non numérique peut convenir."))

duration = int(ctx.get(S, "duration"))
st.subheader(t("Répartition du temps"))
total_minutes = sum(r["Durée (min)"] for r in rows)
for row in rows:
    st.write(f"**{t(row['Phase'])}** · " + t("{n} min", n=row["Durée (min)"]))
    st.progress(row["Durée (min)"] / total_minutes if total_minutes else 0.0)
validation = validate_scenario(rows, duration)
if validation["balanced"]:
    st.success(t("Les phases occupent exactement la durée prévue : {n} min.", n=duration))
else:
    st.warning(t("Les phases totalisent {used} min pour une séance de {n} min (écart : {gap} min).",
                 used=validation["used_minutes"], n=duration, gap=f"{validation['difference_minutes']:+d}"))
issues = scenario_checks(rows, ctx.get(S, "objectives") or "")
with st.expander(t("Points à compléter : {n}", n=len(issues))):
    if issues:
        for issue in issues:
            st.write("• " + issue)
    else:
        st.write(t("Objectifs, activités et critères de réussite sont renseignés."))

metadata = {t("APS"): t(ctx.get(S, "activity")), t("Niveau"): t(ctx.get(S, "level")), t("Modalité"): t(modality),
            t("Effectif"): ctx.get(S, "class_size"), t("Durée (min)"): duration,
            t("Connexion"): t(ctx.CONNECTIVITY_LABELS[connectivity]),
            t("Appareils"): t(ctx.get(S, "devices")), t("Objectifs"): ctx.get(S, "objectives"),
            t("Prérequis"): prerequisites, t("Matériel et contraintes"): ctx.get(S, "equipment")}
for field, label in (("cycle_number", t("Numéro du cycle")), ("lesson_number", t("Numéro de séance"))):
    if ctx.get(S, field):
        metadata[label] = ctx.get(S, field)
if export_advice:
    metadata[t("Adaptations proposées")] = "\n".join(advice)
    metadata[t("Organisation indicative des groupes")] = " / ".join(map(str, sizes))
pdf_col, csv_col = st.columns([2, 1])
pdf_col.download_button(t("Scénario (PDF)"), scenario_pdf(metadata, rows, validation, issues, situation=selected_situation(S), photo=photo),
                        "scenario_seance_eps.pdf", "application/pdf", type="primary",
                        icon=":material/picture_as_pdf:", use_container_width=True)
csv_col.download_button(t("Tableur (CSV)"), export_scenario_csv(metadata, rows),
                        "scenario_seance_eps.csv", "text/csv", use_container_width=True)
