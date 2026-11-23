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
                                     report_html, series_csv, series_indicators)
from acpa_msmda.pdf import measurements_pdf  # noqa: E402
from acpa_msmda.i18n import t  # noqa: E402
from acpa_msmda.ui import LAB, PRIVACY_NOTE, configure_page, page_header  # noqa: E402

TESTS = json.loads((ROOT / "data" / "performance_tests.json").read_text(encoding="utf-8"))["tests"]
DIRECTIONS = {"Non précisé": None, "Valeur plus élevée": True, "Valeur plus faible": False}

S = st.session_state
configure_page(LAB)
page_header(LAB, PRIVACY_NOTE)
ctx.render_context(st, S, fields=("activity", "level", "class_size", "cycle_number", "lesson_number"), expanded=False)

domain = st.selectbox(t("Domaine"), ["Tous"] + sorted({x["domain"] for x in TESTS}), format_func=t,
                      **ctx.bind(S, "lab_domain", "Tous"))
choices = [x for x in TESTS if domain == "Tous" or x["domain"] == domain]
names = {x["id"]: t(x["name"]) for x in TESTS}
if ctx.store(S).get("lab_test") not in {x["id"] for x in choices}:
    ctx.put(S, "lab_test", choices[0]["id"])
test_id = st.selectbox(t("Épreuve"), [x["id"] for x in choices], format_func=names.get, **ctx.bind(S, "lab_test"))
test = next(x for x in TESTS if x["id"] == test_id)
signed = bool(test.get("signed"))
st.caption(t("Mesure : {m} ({u}). Protocole : {p}", m=t(test["measure"]), u=t(test["unit"]), p=t(test["protocol_note"])))

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
                               "date": when.isoformat(), "codes": codes, "values": parsed.values})
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
        if len(mine) > 1:
            others = [i for i in ids if i != last_id]
            first_id = st.selectbox(t("Comparer avec"), others, index=0, format_func=titles.get)
            first = next(s for s in mine if s["id"] == first_id)
            direction = DIRECTIONS[st.radio(t("Pour cette épreuve, le meilleur résultat est la"), list(DIRECTIONS),
                                            format_func=t, horizontal=True, **ctx.bind(S, f"direction_{test_id}", "Non précisé"))]

        def aligned(serie):
            values = dict(zip(serie["codes"], serie["values"]))
            return [values.get(code) for code in union]

        union = sorted(set(last["codes"]) | (set(first["codes"]) if first else set()))
        deltas = None
        if first:
            indicators, deltas = comparison(aligned(first), aligned(last), direction, last["unit"])
            sections.append((t("Évolution : {a} puis {b}", a=titles[first["id"]], b=titles[last_id]), indicators))

        for heading, indicators in sections:
            st.subheader(heading)
            for ind in indicators:
                st.markdown(f"**{ind.label}** · {ind.value}")
                if ind.ratio is not None:
                    st.progress(ind.ratio)
                st.caption(ind.basis)

        header = [t("Élève")] + ([titles[first["id"]]] if first else []) + [titles[last_id]]
        if first:
            header.append(t("Variation"))
        if test_id == "cooper":
            header.append(t("Vitesse moyenne (km/h)"))
        table = []
        last_values = aligned(last)
        first_values = aligned(first) if first else None
        for i, code in enumerate(union):
            row = [code]
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
        if test_id == "cooper":
            notes.append(t("Vitesse moyenne = distance (m) / 200. Ce n'est pas une VMA mesurée."))
        for note in notes:
            st.caption(note)

        st.subheader(t("Exporter"))
        context_line = ctx.summary(S) + " · " + t("Épreuve : {name} ({u})", name=t(test["name"]), u=t(test["unit"]))
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
