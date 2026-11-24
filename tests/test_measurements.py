"""Measurement series: parsing, indicators, comparison, exports and the page journey."""
import csv
import io
import sys
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from acpa_msmda.measurements import (comparison, cooper_speed_kmh, parse_series, pupil_codes,  # noqa: E402
                                     report_html, series_csv, series_indicators, comparable_series)

LAB = "pages/2_Performance_Lab.py"


class ParsingTests(unittest.TestCase):
    def test_codes_are_anonymous_and_padded(self):
        self.assertEqual(pupil_codes(3), ["E01", "E02", "E03"])
        self.assertEqual(pupil_codes(120)[-1], "E120")

    def test_absent_comma_and_blank_lines(self):
        r = parse_series("12,5\n\nabs\n11.8", 5)
        self.assertEqual(r.errors, [])
        self.assertEqual(r.values, [12.5, None, None, 11.8, None])

    def test_rejects_text_negative_and_too_many_lines(self):
        self.assertTrue(parse_series("douze", 3).errors)
        self.assertTrue(parse_series("-4", 3).errors)
        self.assertFalse(parse_series("-4", 3, signed=True).errors)
        self.assertTrue(parse_series("1\n2\n3\n4", 3).errors)
        self.assertTrue(parse_series("", 3).errors)


class IndicatorTests(unittest.TestCase):
    def test_every_ratio_has_its_basis(self):
        inds = series_indicators([10.0, None, 14.0, 12.0], "s")
        measured = inds[0]
        self.assertEqual(measured.value, "3 / 4")
        self.assertAlmostEqual(measured.ratio, 0.75)
        self.assertIn("1 absent", measured.basis)
        self.assertIn("12,00 s", inds[1].value)

    def test_comparison_without_direction_avoids_progress_wording(self):
        inds, deltas = comparison([10, 12, None, 9], [11, 12, 8, 7], None)
        labels = [i.label for i in inds]
        self.assertNotIn("Variation favorable", labels)
        self.assertEqual(inds[0].value, "1 / 3")
        self.assertEqual(deltas, [1, 0, None, -2])

    def test_lower_is_better(self):
        inds, _ = comparison([5.0, 5.2], [4.8, 5.4], False)
        self.assertEqual(inds[0].label, "Variation favorable")
        self.assertEqual(inds[0].value, "1 / 2")

    def test_french_number_format_and_unit_on_variation(self):
        inds, _ = comparison([5.4, 5.9], [5.2, 6.0], False, "s")
        self.assertEqual(inds[-1].value, "-0,05 s")

    def test_cooper_speed(self):
        self.assertAlmostEqual(cooper_speed_kmh(2400), 12.0)


class ExportTests(unittest.TestCase):
    def test_csv_long_format_and_formula_safety(self):
        data = series_csv([{"label": "=cmd", "date": "2026-11-21", "test_name": "Sprint 30 m", "unit": "s",
                            "codes": ["E01", "E02"], "values": [5.1, None]}])
        rows = list(csv.reader(io.StringIO(data.decode("utf-8-sig"))))
        self.assertEqual(rows[0], ["Séance", "Date", "Épreuve", "Unité", "Élève", "Valeur", "Code du groupe (non nominatif)", "Numéro du cycle", "Numéro de séance", "Conditions de mesure"])
        self.assertEqual(rows[1][0], "'=cmd")
        self.assertEqual(rows[2][5], "")

    def test_html_report_escapes_text(self):
        inds = series_indicators([1.0, 2.0], "m")
        page = report_html("<b>x</b>", "ctx", [("S1", inds)], ["Élève", "S1"], [["E01", "1"]], ["note"]).decode()
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", page)
        self.assertIn("2 / 2", page)


def lab():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    app.switch_page(LAB).run()
    return app


def save(app, label, text):
    app.text_input(key="w:series_label").set_value(label).run()
    app.text_area(key="w:series_text").set_value(text).run()
    next(b for b in app.button if b.label == "Enregistrer la série").click().run()


class LabJourneyTests(unittest.TestCase):
    def test_two_series_give_a_comparison_and_exports(self):
        app = lab()
        app.number_input(key="w:class_size").set_value(4).run()
        app.selectbox(key="w:lab_test").set_value("sprint30").run()
        app.text_input(key="w:measurement_group").set_value("G01").run()
        app.text_input(key="w:measurement_protocol").set_value("Même piste, même chronomètre").run()
        app.number_input(key="w:cycle_number").set_value(1).run()
        app.number_input(key="w:lesson_number").set_value(1).run()
        save(app, "Début de cycle", "5,4\n5,9\nabs\n6,1")
        self.assertFalse(app.exception)
        self.assertTrue(any("3 / 4" in s.value for s in app.success))
        app.date_input(key="w:series_date").set_value(__import__("datetime").date(2027, 1, 15)).run()
        app.number_input(key="w:lesson_number").set_value(2).run()
        save(app, "Fin de cycle", "5,2\n6,0\n5,8\n5,9")
        next(c for c in app.checkbox if c.key and c.key.startswith("match_")).check().run()
        app.radio(key="w:direction_sprint30").set_value("Valeur plus faible").run()
        self.assertFalse(app.exception)
        text = " ".join(m.value for m in app.markdown)
        self.assertIn("Variation favorable", text)
        self.assertIn("2 / 3", text)
        self.assertCountEqual([b.proto.label for b in app.get("download_button")],
                              ["Bilan (PDF)", "Bilan imprimable (HTML)", "Données (CSV)"])

    def test_scientific_information_in_three_languages(self):
        import json
        evidence = json.loads((ROOT / "data/scientific_evidence.json").read_text(encoding="utf-8"))
        instrument = next(x for x in evidence["instruments"] if x["id"] == "cooper")
        for lang in ("fr", "ar", "en"):
            with self.subTest(lang=lang):
                app = AppTest.from_file(str(ROOT / LAB), default_timeout=30)
                app.session_state["lang"] = lang
                app.session_state["acpa_store"] = {"lab_test": "cooper"}
                app.run()
                self.assertEqual(app.selectbox(key="w:lab_test").value, "cooper")
                self.assertFalse(app.exception)
                self.assertTrue(any(instrument["citation"] in m.value for m in app.caption))
                self.assertTrue(any(instrument["teacher_info"][lang] in m.value for m in app.markdown))

    def test_reliability_journey_with_scientific_information(self):
        app = lab()
        app.number_input(key="w:class_size").set_value(4).run()
        app.selectbox(key="w:lab_test").set_value("sprint30").run()
        app.text_input(key="w:measurement_group").set_value("G01").run()
        app.text_input(key="w:measurement_protocol").set_value("Même protocole").run()
        app.number_input(key="w:cycle_number").set_value(1).run()
        app.number_input(key="w:lesson_number").set_value(1).run()
        app.date_input(key="w:series_date").set_value(__import__("datetime").date(2026, 11, 1)).run()
        save(app, "Test", "5\n6\n7\n8")
        app.number_input(key="w:lesson_number").set_value(2).run()
        app.date_input(key="w:series_date").set_value(__import__("datetime").date(2026, 11, 2)).run()
        save(app, "Retest", "5\n6\n7\n8")
        next(c for c in app.checkbox if c.key and c.key.startswith("match_")).check().run()
        next(r for r in app.radio if r.key and r.key.startswith("analysis_")).set_value("Fiabilité test-retest").run()
        next(c for c in app.checkbox if c.key and c.key.startswith("stable_")).check().run()
        self.assertFalse(app.exception)
        text = " ".join(m.value for m in app.markdown)
        self.assertIn("ICC(A,1)", text)
        self.assertIn("Koo & Li (2016)", text)
        self.assertIn("Weir (2005)", text)
        self.assertIn("Bland", text)
        self.assertCountEqual([b.proto.label for b in app.get("download_button")],
                              ["Bilan (PDF)", "Bilan imprimable (HTML)", "Données (CSV)"])

    def test_invalid_line_is_reported_not_saved(self):
        app = lab()
        app.number_input(key="w:class_size").set_value(3).run()
        save(app, "Essai", "12\ndouze")
        self.assertTrue(app.error)
        self.assertFalse(app.session_state["acpa_store"].get("series"))

    def test_series_survive_a_detour(self):
        app = lab()
        app.number_input(key="w:class_size").set_value(2).run()
        save(app, "S1", "10\n11")
        app.switch_page("pages/5_Studio_Pedagogique.py").run()
        app.switch_page(LAB).run()
        self.assertEqual(len(app.session_state["acpa_store"]["series"]), 1)


class ScientificTests(unittest.TestCase):
    def test_standard_deviation_and_effect_size(self):
        inds = series_indicators([1.0,2.0,3.0,None],"m")
        self.assertEqual(next(i.value for i in inds if i.label=="Écart-type (échantillon)"),"1,00 m")
        inds,_=comparison([1,2,3,None],[2,4,6,9],True,"m")
        self.assertEqual(next(i.value for i in inds if i.label=="Taille d’effet appariée (d_z)"),"+2,000")
        inds,_=comparison([1,2],[2,3],True,"m")
        self.assertFalse(any("d_z" in i.label for i in inds))

    def test_eligibility(self):
        a=dict(group="G01",cycle=1,activity="Athlétisme",level="Collège",test_id="sprint30",unit="s",protocol="P1",codes=["E01","E02"],date="2026-10-01",lesson=1)
        b=dict(a,date="2026-10-08",lesson=2)
        self.assertTrue(comparable_series(a,b))
        for key,value in [("group","G02"),("protocol",""),("cycle",2),("level","Lycée"),("activity","Endurance"),("codes",["E02","E01"]),("lesson",1),("unit","m")]:
            self.assertFalse(comparable_series(a,dict(b,**{key:value})),key)


if __name__ == "__main__":
    unittest.main()
