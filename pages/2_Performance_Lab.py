"""Mesurer et analyser : séries de mesures d'une classe, bilan et exports."""
from __future__ import annotations

import json
import sys
import uuid
from datetime import date
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from acpa_msmda import session_context as ctx  # noqa: E402
from acpa_msmda.measurements import (comparison, cooper_speed_kmh, fr, parse_series, pupil_codes,  # noqa: E402
                                     report_html, series_csv, series_indicators, comparable_series)
from acpa_msmda.reliability import agreement
from acpa_msmda.measurements import Indicator
from acpa_msmda.pdf import measurements_pdf  # noqa: E402
from acpa_msmda.i18n import current, t  # noqa: E402
from acpa_msmda.ui import LAB, PRIVACY_NOTE, configure_page, page_header  # noqa: E402

TESTS = json.loads((ROOT / "data" / "performance_tests.json").read_text(encoding="utf-8"))["tests"]
EVIDENCE = json.loads((ROOT / "data" / "scientific_evidence.json").read_text(encoding="utf-8"))
DIRECTIONS = {"Non précisé": None, "Valeur plus élevée": True, "Valeur plus faible": False}

S = st.session_state
configure_page(LAB)
page_header(LAB, PRIVACY_NOTE)
ctx.render_context(st, S, fields=("activity", "level", "class_size", "cycle_number", "lesson_number"), expanded=False)

domain = st.selectbox(t("Domaine"), ["Tous"] + sorted({x["domain"] for x in TESTS}), format_func=t,
                      **ctx.bind(S, "lab_domain", "Tous"))
choices = [x for x in TESTS if domain == "Tous" or x["domain"] == domain]
# Keep existing domain filter and instrument IDs; group choices without hiding any.
evidence_by_id = {x["id"]: x for x in EVIDENCE["instruments"]}
choices.sort(key=lambda x: evidence_by_id[x["id"]]["group"] != "institutional")
group_labels = dict(zip(("institutional", "complementary"), EVIDENCE["group_labels"][current()]))
names = {x["id"]: t(x["name"]) for x in TESTS}
choice_labels = {x["id"]: names[x["id"]] + " · " + group_labels[evidence_by_id[x["id"]]["group"]] for x in choices}
if ctx.store(S).get("lab_test") not in {x["id"] for x in choices}:
    ctx.put(S, "lab_test", choices[0]["id"])
test_id = st.selectbox(t("Épreuve"), [x["id"] for x in choices], format_func=choice_labels.get, **ctx.bind(S, "lab_test"))
test = next(x for x in TESTS if x["id"] == test_id)
signed = bool(test.get("signed"))
st.caption(t("Mesure : {m} ({u}). Protocole : {p}", m=t(test["measure"]), u=t(test["unit"]), p=t(test["protocol_note"])))

evidence = evidence_by_id[test_id]
st.caption(group_labels[evidence["group"]])
if evidence.get("citation"):
    st.caption(evidence["citation"] + " · " + t("Référence déclarée : {source}", source=t(evidence["source_label"])))
else:
    st.caption(t("Référence déclarée : {source}", source=evidence["source_label"]))
with st.expander("ⓘ " + t("Statut scientifique et sources")):
    st.warning(t("Protocole à confirmer ; validation empirique de cette implémentation non établie."))
    st.caption(t("Référence déclarée : {source}", source=evidence["source_label"]))
    if evidence.get("citation"):
        st.write(evidence["citation"])
    for url in evidence["reference_urls"] + evidence.get("other_reference_urls", []):
        st.markdown("[" + ("DOI" if "doi.org/" in url else url) + "](" + url + ")")
    st.write(evidence["teacher_info"][current()])
    st.caption(t(test["protocol_note"]))
# Optional discovery library; never feeds unverified instruments into measurement.
LIBRARY = json.loads((ROOT / "data" / "lab_library.json").read_text(encoding="utf-8"))
library_labels = {
    "fr": ("Bibliothèque scientifique complémentaire", "Rechercher un instrument ou un auteur", "Famille documentaire", "Toutes les familles", "Instruments spécialisés inclus", "Piste documentaire — protocole et droits à vérifier. Aucun calcul ni diagnostic disponible.", "Ressources trouvées", "Consulter la source ou la recherche bibliographique", "Aucun résultat"),
    "en": ("Complementary scientific library", "Search for an instrument or author", "Resource family", "All families", "Include specialized instruments", "Documentary lead — check protocol and rights. No scoring or diagnosis available.", "Resources found", "Open source or bibliographic search", "No results"),
    "ar": ("المكتبة العلمية التكميلية", "البحث عن أداة أو مؤلف", "فئة الموارد", "جميع الفئات", "إدراج الأدوات المتخصصة", "مرجع استكشافي — تحقق من البروتوكول والحقوق. لا حساب أو تشخيص متاح.", "الموارد الموجودة", "فتح المصدر أو البحث الببليوغرافي", "لا نتائج"),
}[current()]
with st.expander(library_labels[0]):
    query = st.text_input(library_labels[1], key="lab_library_query").strip().casefold()
    groups = LIBRARY["groups"]
    group_names = {g["id"]: g["label"][current()] for g in groups}
    group_names["all"] = library_labels[3]
    family = st.selectbox(library_labels[2], ["all"] + list(g["id"] for g in groups),
                          format_func=group_names.get, key="lab_library_family")
    specialized = st.checkbox(library_labels[4], key="lab_library_specialist")
    matches = [(g, item) for g in groups for item in g["entries"]
               if (family == "all" or family == g["id"])
               and (specialized or item["level"] != "specialist")
               and (not query or query in (item["name"] + " " + item["citation"] + " " + " ".join(g["label"].values())).casefold())]
    st.caption(f"{library_labels[6]} : {len(matches)}")
    st.caption(library_labels[5])
    if matches:
        item_names = {item["id"]: item["name"] for _, item in matches}
        item_id = st.selectbox(library_labels[0], list(item_names), format_func=item_names.get, key="lab_library_item")
        group, item = next((g, i) for g, i in matches if i["id"] == item_id)
        st.markdown("**" + item["name"] + "**")
        st.caption(group["label"][current()])
        st.write(item["citation"])
        st.markdown("[" + library_labels[7] + "](" + item["url"] + ")")
    else:
        st.info(library_labels[8])

# Separate imported study data from existing classroom series.
from acpa_msmda.longitudinal import parse_long_csv, export_long_csv, paired_panel, group_summary, FIELDS
study_labels = {
    "fr": ("Étude longitudinale (CSV)", "Utilisez uniquement des codes non nominatifs. Les données restent dans cette session ; exportez avant de quitter.", "Télécharger le modèle CSV", "Importer un CSV UTF-8", "Valider et remplacer les données de l'étude", "Import accepté", "Import refusé", "Exporter les données de l'étude", "Instrument", "Protocole", "Groupe", "Tous les groupes", "Temps de mesure (ordre chronologique)", "Construire le panel apparié", "Participants complets / total", "Effacer les données de l'étude", "Observations", "Séparateur CSV", "Vérifiez les dates, codes, unités et doublons. Le fichier précédent est conservé en cas d'échec."),
    "en": ("Longitudinal study (CSV)", "Use non-identifying codes only. Data stay in this session; export before leaving.", "Download CSV template", "Import UTF-8 CSV", "Validate and replace study data", "Import accepted", "Import rejected", "Export study data", "Instrument", "Protocol", "Group", "All groups", "Occasions (chronological order)", "Build paired panel", "Complete participants / total", "Clear study data", "Observations", "CSV delimiter", "Check dates, codes, units and duplicates. Previous data are retained on failure."),
    "ar": ("دراسة طولية (CSV)", "استخدم رموزا غير اسمية فقط. تبقى البيانات في هذه الجلسة؛ صدّرها قبل المغادرة.", "تنزيل نموذج CSV", "استيراد CSV بترميز UTF-8", "التحقق واستبدال بيانات الدراسة", "تم قبول الاستيراد", "تم رفض الاستيراد", "تصدير بيانات الدراسة", "الأداة", "البروتوكول", "المجموعة", "جميع المجموعات", "أوقات القياس بالترتيب الزمني", "إنشاء لوحة القياسات المزدوجة", "المشاركون المكتملون / المجموع", "مسح بيانات الدراسة", "الملاحظات", "فاصل CSV", "تحقق من التواريخ والرموز والوحدات والتكرار. تبقى البيانات السابقة عند الفشل."),
}[current()]
with st.expander(study_labels[0]):
    st.caption(study_labels[1])
    registry = {x["id"]: x for x in TESTS}
    st.download_button(study_labels[2], data=(";".join(FIELDS)+"\n").encode("utf-8-sig"),
                       file_name="study_template.csv", mime="text/csv", key="lab_study_template")
    delimiter = st.selectbox(study_labels[17], [";", ","], key="lab_study_delimiter")
    upload = st.file_uploader(study_labels[3], type=["csv"], key="lab_study_upload")
    if st.button(study_labels[4], key="lab_study_import", disabled=upload is None):
        try:
            S["lab_study_rows"] = parse_long_csv(upload.getvalue(), registry, delimiter)
        except (ValueError, UnicodeError):
            st.error(study_labels[6] + ". " + study_labels[18])
        else:
            st.success(study_labels[5])
    study_rows = S.get("lab_study_rows", [])
    if study_rows:
        st.caption(f"{study_labels[16]} : {len(study_rows)}")
        st.download_button(study_labels[7], export_long_csv(study_rows), "study.csv", "text/csv", key="lab_study_export")
        instrument = st.selectbox(study_labels[8], sorted({r["instrument"] for r in study_rows}),
                                  format_func=names.get, key="lab_study_instrument")
        subset = [r for r in study_rows if r["instrument"] == instrument]
        protocol = st.selectbox(study_labels[9], sorted({r["protocol"] for r in subset}), key="lab_study_protocol")
        subset = [r for r in subset if r["protocol"] == protocol]
        group = st.selectbox(study_labels[10], [None] + sorted({r["group"] for r in subset}),
                             format_func=lambda v: study_labels[11] if v is None else v, key="lab_study_group")
        subset = [r for r in subset if group is None or r["group"] == group]
        occasions = st.multiselect(study_labels[12], sorted({r["occasion"] for r in subset}), key="lab_study_occasions")
        if st.button(study_labels[12+1], key="lab_study_panel", disabled=len(occasions)<2):
            try:
                panel = paired_panel(study_rows, instrument, protocol, occasions, group)
            except ValueError:
                st.error(study_labels[18])
            else:
                st.write(f"{study_labels[14]} : {panel['n_complete']} / {panel['n_total']}")
                st.dataframe([{ "participant": p, **dict(zip(occasions, vals))}
                              for p, vals in zip(panel["participants"], panel["values"])], hide_index=True)
                if panel["values"]:
                    import pandas as pd
                    import altair as alt
                    trajectory = pd.DataFrame([{"participant": p, "occasion": o, "value": v}
                                                for p, vals in zip(panel["participants"], panel["values"])
                                                for o, v in zip(occasions, vals)])
                    st.altair_chart(alt.Chart(trajectory).mark_line(point=True).encode(
                        x=alt.X("occasion:N", sort=occasions, title=study_labels[12]),
                        y=alt.Y("value:Q", title=t(registry[instrument]["unit"])),
                        color=alt.Color("participant:N", legend=None),
                        tooltip=["participant", "occasion", "value"]), use_container_width=True)
                if group is None:
                    summary = group_summary(study_rows, instrument, protocol, occasions)
                    if summary:
                        st.dataframe(summary, hide_index=True)
                        import pandas as pd
                        import altair as alt
                        frame = pd.DataFrame(summary).dropna(subset=["mean"])
                        if not frame.empty:
                            st.altair_chart(alt.Chart(frame).mark_line(point=True).encode(
                                x=alt.X("occasion:N", sort=occasions, title=study_labels[12]),
                                y=alt.Y("mean:Q", title=t("Moyenne")+" ("+t(registry[instrument]["unit"])+")"),
                                color=alt.Color("group:N", title=study_labels[10]),
                                tooltip=["group", "occasion", "n", "mean"]), use_container_width=True)

        if st.button(study_labels[15], key="lab_study_clear"):
            S.pop("lab_study_rows", None)
            st.rerun()

all_series = ctx.store(S).setdefault("series", [])
class_size = int(ctx.get(S, "class_size"))
codes = pupil_codes(class_size)

entry, report = st.tabs([t("Saisir une série"), t("Bilan")])

with entry:
    st.caption(t("Codes élèves {a} à {b}, dans l'ordre de votre liste de classe. "
                 "Gardez la correspondance code et élève en dehors de l'application.", a=codes[0], b=codes[-1]))
    left, right = st.columns(2)
    with left:
        label = st.text_input(t("Nom de la série"), max_chars=60, **ctx.bind(S, "series_label", t("Séance 1")))
    with right:
        when = st.date_input(t("Date"), format="DD/MM/YYYY", **ctx.bind(S, "series_date", date.today()))
    group = st.text_input(t("Code du groupe (non nominatif)"),max_chars=30,**ctx.bind(S,"measurement_group",""))
    protocol = st.text_input(t("Conditions de mesure"), max_chars=300,
                             help=t("Précisez le matériel, le protocole et les conditions de réalisation."),
                             **ctx.bind(S, "measurement_protocol", ""))
    raw = st.text_area(t("Résultats en {u}, une valeur par ligne", u=t(test["unit"])),
                       placeholder="12,5\n13,1\nabs\n11,8", height=180, max_chars=6000,
                       help=t("Ligne vide ou « abs » : élève absent. Virgule ou point acceptés.")
                            + (" " + t("Valeurs négatives acceptées pour cette épreuve.") if signed else ""),
                       **ctx.bind(S, "series_text", ""))
    if st.button(t("Enregistrer la série"), type="primary", use_container_width=True):
        parsed = parse_series(raw, class_size, signed=signed)
        if parsed.errors:
            for message in parsed.errors:
                st.error(message)
        else:
            all_series.append({"id": uuid.uuid4().hex[:8], "test_id": test_id, "test_name": test["name"],
                               "unit": test["unit"], "label": label.strip() or t("Série"),
                               "date": when.isoformat(), "codes": codes, "values": parsed.values,
                               "group": group.strip(), "activity": ctx.get(S,"activity"), "level": ctx.get(S,"level"), "protocol": protocol.strip(), "cycle": ctx.get(S, "cycle_number"),
                               "lesson": ctx.get(S, "lesson_number")})
            ctx.put(S, "series_text", "")
            ctx.put(S, "lab_flash", t("Série « {label} » enregistrée : {n} / {total} élèves mesurés. "
                                      "Ouvrez l'onglet Bilan.", label=label,
                                      n=sum(v is not None for v in parsed.values), total=class_size))
            st.rerun()
    flash = ctx.store(S).pop("lab_flash", None)
    if flash:
        st.success(flash)

with report:
    mine = sorted((s for s in all_series if s["test_id"] == test_id), key=lambda s: s["date"])
    if not mine:
        st.info(t("Aucune série enregistrée pour cette épreuve. Saisissez une série dans l'onglet précédent."))
    else:
        titles = {s["id"]: f"{s['label']} ({date.fromisoformat(s['date']).strftime('%d/%m/%Y')})" for s in mine}
        ids = [s["id"] for s in mine]
        last_id = st.selectbox(t("Série à analyser"), ids, index=len(ids) - 1, format_func=titles.get)
        last = next(s for s in mine if s["id"] == last_id)
        sections = [(titles[last_id], series_indicators(last["values"], last["unit"]))]

        first = None
        direction = None
        reliability_mode = False
        agreement_result = None
        if len(mine) > 1:
            others = [s["id"] for s in mine if s["id"] != last_id and comparable_series(s,last)]
            if not others:
                st.info(t("Aucune série antérieure comparable : vérifiez le groupe, le cycle, les codes et les conditions de mesure."))
            else:
                first_id = st.selectbox(t("Comparer avec"), others, index=0, format_func=titles.get)
                candidate = next(s for s in mine if s["id"] == first_id)
                if st.checkbox(t("Les codes correspondent aux mêmes élèves et les conditions d’observation sont comparables."), key=f"match_{first_id}_{last_id}"):
                    first = candidate
                    reliability_mode = st.radio(t("Type d’analyse"), ["Évolution pédagogique","Fiabilité test-retest"],format_func=t,key=f"analysis_{first_id}_{last_id}") == "Fiabilité test-retest"
                    if reliability_mode:
                        if not st.checkbox(t("Mesures répétées sans changement réel attendu, avec protocole identique."),key=f"stable_{first_id}_{last_id}"):
                            first = None
                    else:
                        direction = DIRECTIONS[st.radio(t("Pour cette épreuve, le meilleur résultat est la"), list(DIRECTIONS),
                                                    format_func=t, horizontal=True, **ctx.bind(S, f"direction_{test_id}", "Non précisé"))]

        def aligned(serie):
            values = dict(zip((int(code[1:]) for code in serie["codes"]), serie["values"]))
            return [values.get(code) for code in union]

        union = sorted({int(code[1:]) for code in last["codes"]} | ({int(code[1:]) for code in first["codes"]} if first else set()))
        deltas = None
        if first:
            indicators, deltas = comparison(aligned(first), aligned(last), direction, last["unit"])
            if reliability_mode:
                agreement_result = agreement(aligned(first), aligned(last))
                if agreement_result is None:
                    st.warning(t("Au moins trois paires complètes sont nécessaires au calcul ; un effectif faible reste insuffisant pour une estimation précise."))
                else:
                    result = agreement_result
                    basis = t("Sur {n} élève(s) mesuré(s) aux deux séances.", n=result["n"])
                    indicators = [Indicator(t(label),fr(result[key],3)+" "+t(last["unit"]),None,basis)
                                  for label,key in [("Biais moyen","bias"),("SEM","sem"),("MDC95","mdc95"),("Limite inférieure d’accord","lower"),("Limite supérieure d’accord","upper")]]
                    if result["icc"] is not None:
                        indicators.append(Indicator("ICC(A,1)",fr(result["icc"],3),None,basis))
                    sections.append((t("Fiabilité test-retest"),indicators))
            else:
                sections.append((t("Évolution : {a} puis {b}", a=titles[first["id"]], b=titles[last_id]), indicators))

        if first:
            with st.expander("ⓘ " + t("Statut scientifique et sources")):
                method_ids = ("icc_a1", "bland_altman", "sem_mdc") if reliability_mode else ("paired_dz",)
                for method in EVIDENCE["methods"]:
                    if method["id"] in method_ids:
                        st.markdown("**" + method.get("citation", method["id"]) + "**")
                        st.caption(method["teacher_info"][current()])
                        st.markdown("[DOI](" + method["reference"] + ")")

        for heading, indicators in sections:
            st.subheader(heading)
            for ind in indicators:
                st.markdown(f"**{ind.label}** · {ind.value}")
                if ind.ratio is not None:
                    st.progress(ind.ratio)
                st.caption(ind.basis)

        if agreement_result is not None:
            import altair as alt
            import pandas as pd
            result = agreement_result
            points = alt.Chart(pd.DataFrame(result["points"])).mark_circle(size=65).encode(x=alt.X("mean:Q",title=t("Moyenne des deux mesures")),y=alt.Y("difference:Q",title=t("Différence après moins avant")))
            lines = alt.Chart(pd.DataFrame({"limit":[result["lower"],result["bias"],result["upper"]]})).mark_rule(strokeDash=[5,4]).encode(y="limit:Q")
            st.subheader("Bland-Altman")
            st.altair_chart(points+lines,use_container_width=True)
        header = [t("Élève")] + ([titles[first["id"]]] if first else []) + [titles[last_id]]
        if first:
            header.append(t("Variation"))
        if test_id == "cooper":
            header.append(t("Vitesse moyenne (km/h)"))
        table = []
        last_values = aligned(last)
        first_values = aligned(first) if first else None
        for i, code in enumerate(union):
            row = [f"E{code:03d}"]
            if first:
                row.append("" if first_values[i] is None else fr(first_values[i]))
            row.append(t("abs") if last_values[i] is None else fr(last_values[i]))
            if first:
                row.append("" if deltas[i] is None else fr(round(deltas[i], 3), sign=True))
            if test_id == "cooper":
                row.append("" if last_values[i] is None else fr(cooper_speed_kmh(last_values[i]), 2))
            table.append(row)
        st.subheader(t("Détail par élève"))
        st.dataframe([dict(zip(header, row)) for row in table], hide_index=True, use_container_width=True)

        notes = [t("Indicateurs descriptifs calculés uniquement à partir des valeurs saisies ; aucune norme ni aucun barème n'est appliqué."),
                 t("Une variation entre deux séries ne suffit pas à établir un progrès : conditions de mesure, "
                   "protocole et erreur de mesure doivent être comparables.")]
        if reliability_mode:
            notes.append(t("SEM et MDC95 supposent des erreurs indépendantes de variance comparable. Les limites d’accord supposent des différences approximativement normales et de dispersion stable. Les estimations restent exploratoires, sans intervalle de confiance de l’ICC."))
        for serie in ([first, last] if first else [last]):
            notes.append(t("Conditions de mesure") + " · " + titles[serie["id"]] + " : " + (serie.get("protocol") or t("Non précisé")))
        if first and (not first.get("protocol") or not last.get("protocol") or first.get("protocol") != last.get("protocol")):
            st.warning(t("Conditions de mesure non renseignées ou différentes : interprétez la comparaison avec prudence."))
        if test_id == "cooper":
            notes.append(t("Vitesse moyenne = distance (m) / 200. Ce n'est pas une VMA mesurée."))
        for note in notes:
            st.caption(note)

        st.subheader(t("Exporter"))
        context_line = " · ".join([t(last.get("activity","")),t(last.get("level","")),last.get("group",""),t("{n} élèves",n=len(last["codes"]))]) + " · " + t("Épreuve : {name} ({u})", name=t(test["name"]), u=t(test["unit"]))
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(t("Bilan (PDF)"),
                               measurements_pdf(t("Bilan") + " · " + t(test["name"]), context_line, sections, header, table, notes),
                               f"bilan_{test_id}.pdf", "application/pdf", type="primary", use_container_width=True)
            st.download_button(t("Bilan imprimable (HTML)"),
                               report_html(t("Bilan") + " · " + t(test["name"]), context_line, sections, header, table, notes),
                               f"bilan_{test_id}.html", "text/html", use_container_width=True,
                               help=t("S'ouvre dans le navigateur ; « Imprimer » permet de l'enregistrer en PDF."))
        with c2:
            st.download_button(t("Données (CSV)"), series_csv(mine), f"mesures_{test_id}.csv", "text/csv",
                               use_container_width=True)

        with st.expander(t("Gérer les séries")):
            for serie in mine:
                col_a, col_b = st.columns([3, 1])
                col_a.write(titles[serie["id"]])
                if col_b.button(t("Supprimer"), key=f"del_{serie['id']}"):
                    all_series.remove(serie)
                    st.rerun()

st.caption(t("L'application ne sauvegarde pas les séries : elles disparaissent au rechargement ou à la fermeture "
             "de la page. Exportez-les pour les conserver."))
