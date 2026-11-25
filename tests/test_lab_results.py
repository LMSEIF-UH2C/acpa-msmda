"""Restitution des analyses du Laboratoire en trois niveaux : contenu, prudence, langues, graphiques, page."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from acpa_msmda import i18n, lab_results as lr, lab_statistics as ls  # noqa: E402
from acpa_msmda.longitudinal import parse_long_csv  # noqa: E402

RNG = np.random.default_rng(26)
PANEL = (RNG.normal(10, 2, (24, 1)) + RNG.normal(0, .8, (24, 3)) + np.array([0, .8, 1.5])).round(2).tolist()
GROUPS = [RNG.normal(10, 2, 20).round(2).tolist(), RNG.normal(11, 2, 20).round(2).tolist(), RNG.normal(12, 2, 20).round(2).tolist()]
OCC = ["T1", "T2", "T3"]


def results():
    a, b = zip(*[(r[0], r[1]) for r in PANEL])
    x = np.asarray(PANEL)
    return {
        "pearson": ls.correlate(a, b, "pearson"), "spearman": ls.correlate(a, b, "spearman"),
        "paired_t": ls.paired_test(a, b, "t"), "wilcoxon": ls.paired_test(a, b, "wilcoxon"),
        "repeated_anova": ls.repeated_anova(PANEL), "friedman": ls.friedman(PANEL),
        "mixed_anova": ls.mixed_anova([PANEL[:12], PANEL[12:]]),
        "paired_posthoc": {"contrasts": ls.paired_posthoc(PANEL), "occasion_labels": OCC},
        "welch": {**ls.independent_test(GROUPS[0], GROUPS[1], "welch"), "group_labels": ["A", "B"]},
        "mann_whitney": {**ls.independent_test(GROUPS[0], GROUPS[1], "mann_whitney"), "group_labels": ["A", "B"]},
        "one_way": ls.one_way(GROUPS),
        "regression": ls.regression(x[:, 2], x[:, :2]),
        "moderation": ls.regression(x[:, 2], x[:, :2], moderation=True),
    }


CAUSAL = ("provoque", "entraîne", "cause l", "grâce à", "améliore")


class Content(unittest.TestCase):
    def tearDown(self):
        i18n.use("fr")

    def test_every_method_has_three_levels(self):
        i18n.use("fr")
        for method, result in results().items():
            before = copy.deepcopy(result)
            r = lr.build(method, result, panel_values=PANEL if method in ("repeated_anova", "friedman") else None, columns=OCC)
            self.assertEqual(result, before, method)                       # résultats jamais modifiés
            self.assertTrue(r.indicators or r.tables, method)               # comprendre / analyser
            self.assertTrue(r.interpretation, method)
            self.assertTrue(r.conditions and r.limits, method)
            self.assertTrue(lr.investigate_payload(result).startswith("{"), method)

    def test_no_invented_interval_or_effect(self):
        i18n.use("fr")
        res = results()
        for method in ("spearman", "wilcoxon", "mann_whitney", "friedman"):
            labels = [i.label for i in lr.build(method, res[method]).indicators]
            self.assertFalse(any("IC 95" in x for x in labels), method)
        wil = lr.build("wilcoxon", res["wilcoxon"])
        self.assertNotIn("dz", [i.label for i in wil.indicators])
        self.assertTrue(any("aucune n'est affichée" in x for x in wil.interpretation))
        pear = lr.build("pearson", res["pearson"])
        self.assertIn(lr.ci(res["pearson"]["ci95"]), [i.value for i in pear.indicators])

    def test_values_match_engine(self):
        i18n.use("en")
        res = results()["paired_t"]
        r = lr.build("paired_t", res)
        shown = {i.label: i.value for i in r.indicators}
        self.assertEqual(shown["Effect size (dz)"], f"{res['dz']:.2f}")
        self.assertEqual(shown["Mean difference (after − before)"], f"{res['mean_difference']:+.2f}")

    def test_cautious_wording(self):
        i18n.use("fr")
        for method, result in results().items():
            text = " ".join(lr.build(method, result).interpretation).casefold()
            for word in CAUSAL:
                self.assertNotIn(word, text, method)
        no = lr.build("welch", {"n1": 5, "n2": 5, "t": .3, "df": 8.0, "p": .77, "mean_difference": .2, "ci95": [-1, 1.4],
                                "group_labels": ["A", "B"]})
        self.assertIn("ne prouve pas son absence", " ".join(no.interpretation))

    def test_method_specific_conditions(self):
        i18n.use("fr")
        res = results()
        self.assertIn("Holm", " ".join(lr.build("paired_posthoc", res["paired_posthoc"]).conditions))
        self.assertIn("Greenhouse", " ".join(lr.build("repeated_anova", res["repeated_anova"]).conditions))
        self.assertNotEqual(lr.build("welch", res["welch"]).conditions, lr.build("pearson", res["pearson"]).conditions)

    def test_three_languages(self):
        res = results()["one_way"]
        texts = {}
        for lang in ("fr", "ar", "en"):
            i18n.use(lang)
            r = lr.build("one_way", res)
            texts[lang] = " ".join(r.interpretation + r.conditions + r.limits + [t for t, _ in r.tables])
        self.assertTrue(any("؀" <= c <= "ۿ" for c in texts["ar"]))
        self.assertIn("between groups", texts["en"])
        self.assertNotIn("différence", texts["ar"] + texts["en"])
        i18n.use("fr")
        self.assertEqual(lr.pval(.0004), "< 0,001")
        i18n.use("en")
        self.assertEqual(lr.pval(.0234), "0.023")


class EdgeCases(unittest.TestCase):
    def tearDown(self):
        i18n.use("fr")

    def test_zero_correlation_is_not_negative(self):
        i18n.use("fr")
        text = " ".join(lr.build("pearson", {"n": 10, "r": 0.0, "p": 1.0, "ci95": [-.6, .6]}).interpretation)
        self.assertNotIn("négative", text)
        self.assertIn("Coefficient nul", text)
        self.assertIn("négative", " ".join(lr.build("spearman", {"n": 10, "rho": -.4, "p": .2}).interpretation))

    def test_p_rounding_stays_on_the_right_side(self):
        i18n.use("en")
        self.assertEqual(lr.pval(.04996), "0.04996")
        self.assertEqual(lr.pval(.0501), "0.0501")
        self.assertEqual(lr.pval(.05), "0.050")
        self.assertEqual(lr.pval(.0234), "0.023")
        self.assertIn("p = 0.04996", lr._decision(.04996, "différence"))
        self.assertIn("A statistically significant", lr._decision(.04996, "différence"))
        self.assertIn("No statistically significant", lr._decision(.05004, "différence"))

    def test_posthoc_and_friedman_notes(self):
        i18n.use("fr")
        r = lr.build("paired_posthoc", results()["paired_posthoc"])
        self.assertTrue(any("ne sont pas ajustés simultanément" in x for x in r.limits))
        self.assertTrue(any("Après un test de Friedman" in x for x in r.conditions))
        self.assertIn("IC 95 % non corrigé", r.tables[0][1][0])

    def test_descriptive_boxes_use_all_complete_cases(self):
        big = (RNG.normal(10, 2, (250, 2))).round(2).tolist()
        figure, notes = lr.chart("descriptive", {}, panel_values=big, columns=OCC[:2])
        data = next(iter(figure.to_dict()["datasets"].values()))
        first = next(d for d in data if d["key"] == "T1")
        self.assertEqual(first["n"], 250)
        self.assertAlmostEqual(first["median"], float(np.median([r[0] for r in big])))
        self.assertAlmostEqual(first["mean"], float(np.mean([r[0] for r in big])))

    def test_display_limits_are_reported(self):
        big = (RNG.normal(10, 2, (250, 2))).round(2).tolist()
        _, notes = lr.chart("paired_t", {}, panel_values=big, columns=OCC[:2], participants=list(range(250)))
        self.assertTrue(any("100/250" in n for n in notes))
        many = RNG.normal(0, 1, (6000, 2)).tolist()
        _, notes = lr.chart("pearson", {}, matrix=many, columns=["X", "Y"])
        self.assertTrue(any("5000/6000" in n for n in notes))

    def test_values_match_engine_for_each_method(self):
        i18n.use("en")
        res = results()
        expect = {"pearson": ("Strength of the relation (r)", res["pearson"]["r"], 2),
                  "spearman": ("Strength of the relation (ρ)", res["spearman"]["rho"], 2),
                  "repeated_anova": ("Effect size (η²p)", res["repeated_anova"]["partial_eta2"], 2),
                  "friedman": ("Kendall's concordance (W)", res["friedman"]["kendall_W"], 2),
                  "mixed_anova": ("Effect size (η²p)", res["mixed_anova"]["group_time"]["partial_eta2"], 2),
                  "mann_whitney": ("Effect size (rank-biserial)", res["mann_whitney"]["rank_biserial"], 2),
                  "one_way": ("Effect size (η²)", res["one_way"]["eta2"], 2),
                  "regression": ("Proportion of variance explained (R²)", res["regression"]["r2"], 2),
                  "wilcoxon": ("Wilcoxon statistic (W)", res["wilcoxon"]["W"], 1)}
        for method, (label, value, digits) in expect.items():
            shown = {i.label: i.value for i in lr.build(method, res[method]).indicators}
            self.assertEqual(shown[label], f"{value:.{digits}f}", method)
        welch = {i.label: i.value for i in lr.build("welch", res["welch"]).indicators}
        self.assertEqual(welch["Mean difference (A − B)"], f"{res['welch']['mean_difference']:+.2f}")
        self.assertEqual(welch["95% CI of the difference"], "[{:.2f}, {:.2f}]".format(*res["welch"]["ci95"]))

    def test_precheck_and_labels_follow_method(self):
        i18n.use("fr")
        self.assertIn("Relation monotone", lr.precheck("spearman"))
        self.assertNotIn("Relation monotone", lr.precheck("welch"))
        self.assertEqual(lr.variable_labels("pearson"), ("Première variable", "Seconde variable"))
        self.assertIn("modérateur", lr.variable_labels("moderation")[1])
        self.assertEqual(lr.variable_labels("regression")[0], "Variable expliquée (Y)")


class Charts(unittest.TestCase):
    def test_chart_for_each_method(self):
        res = results()
        x = np.asarray(PANEL)
        args = {"pearson": {"panel_values": [r[:2] for r in PANEL], "columns": OCC[:2]},
                "spearman": {"panel_values": [r[:2] for r in PANEL], "columns": OCC[:2]},
                "paired_t": {"panel_values": [r[:2] for r in PANEL], "columns": OCC[:2]},
                "wilcoxon": {"panel_values": [r[:2] for r in PANEL], "columns": OCC[:2]},
                "repeated_anova": {"panel_values": PANEL, "columns": OCC},
                "friedman": {"panel_values": PANEL, "columns": OCC},
                "paired_posthoc": {"panel_values": PANEL, "columns": OCC},
                "mixed_anova": {"group_panels": [PANEL[:12], PANEL[12:]], "group_labels": ["A", "B"], "columns": OCC},
                "welch": {"samples": GROUPS[:2], "group_labels": ["A", "B"]},
                "mann_whitney": {"samples": GROUPS[:2], "group_labels": ["A", "B"]},
                "one_way": {"samples": GROUPS, "group_labels": ["A", "B", "C"]},
                "regression": {"matrix": x[:, [2, 0, 1]], "columns": ["Y", "X1", "X2"]},
                "moderation": {"matrix": x[:, [2, 0, 1]], "columns": ["Y", "X", "M"]}}
        reg = {"regression": ls.regression(x[:, 2], x[:, :2]), "moderation": ls.regression(x[:, 2], x[:, :2], moderation=True)}
        for method, kw in args.items():
            figure, _ = lr.chart(method, reg.get(method, res.get(method, {})), **kw)
            spec = figure.to_dict()
            self.assertTrue("layer" in spec or "mark" in spec, method)
        desc, notes = lr.chart("descriptive", {}, panel_values=PANEL, columns=OCC)
        self.assertIn("layer", desc.to_dict())
        self.assertTrue(any("tous les cas complets" in n for n in notes))


def lab_app(method, occasions):
    csv = "participant;group;instrument;unit;occasion;date;protocol;value\n"
    for g, shift in (("A", 0), ("B", 1.5)):
        for i, row in enumerate(PANEL[:12]):
            for j, v in enumerate(row):
                csv += f"{g}{i};{g};cooper;m;T{j+1};2026-01-0{j+1};P1;{1500 + 100 * (v + shift):.0f}\n"
    rows = parse_long_csv(csv.encode(), {"cooper": {"unit": "m"}})
    app = AppTest.from_file(str(ROOT / "pages/2_Performance_Lab.py"), default_timeout=90)
    app.session_state["lang"] = "fr"
    app.session_state["lab_study_rows"] = rows
    app.run()
    app.checkbox(key="lab_study_enabled").set_value(True).run()
    if method in ("paired_t", "repeated_anova"):
        app.selectbox(key="lab_study_group").set_value("A").run()
    app.multiselect(key="lab_study_occasions").set_value(occasions).run()
    app.selectbox(key="lab_study_method").set_value(method).run()
    if method != "descriptive":
        app.checkbox(key="lab_study_assumptions").set_value(True).run()
    return app


class Page(unittest.TestCase):
    def test_no_raw_json_by_default(self):
        app = lab_app("paired_t", ["T1", "T2"])
        app.button(key="lab_study_panel").click().run()
        self.assertFalse(app.exception, str(app.exception))
        labels = [m.label for m in app.metric]
        self.assertIn("Taille d'effet (dz)", labels)
        self.assertIn("Participants analysés", labels)
        expanders = [e.label for e in app.expander]
        self.assertTrue(any(x.startswith("Analyser") for x in expanders))
        self.assertTrue(any(x.startswith("Investiguer") for x in expanders))
        investigate = next(e for e in app.expander if e.label.startswith("Investiguer"))
        self.assertEqual(len(app.json), len(investigate.json))   # JSON seulement dans « Investiguer »
        self.assertGreaterEqual(len(app.get("arrow_vega_lite_chart")), 1)
        # Carte « Comprendre » d'abord ; le détail des participants vient après, dans un volet replié.
        order = [e.label for e in app.expander]
        detail = next(i for i, x in enumerate(order) if x.startswith("Participants complets") or "/" in x)
        self.assertGreater(detail, next(i for i, x in enumerate(order) if x.startswith("Investiguer")))

    def test_chart_failure_keeps_results_and_export(self):
        app = lab_app("repeated_anova", ["T1", "T2", "T3"])
        with patch("altair.Chart", side_effect=TypeError("unexpected keyword argument 'closed'")):
            app.button(key="lab_study_panel").click().run()
        self.assertFalse(app.exception, str(app.exception))
        self.assertTrue(any("Graphique indisponible" in w.value for w in app.warning))
        self.assertIn("Taille d'effet (η²p)", [m.label for m in app.metric])
        self.assertIn("Exporter le résultat (JSON)", [d.proto.label for d in app.get("download_button")])


if __name__ == "__main__":
    unittest.main()
