import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from streamlit.testing.v1 import AppTest
from acpa_msmda.lab_display import chart_guard
from acpa_msmda.longitudinal import parse_long_csv

ROOT = Path(__file__).resolve().parents[1]

class LabRuntimeTests(unittest.TestCase):
    def test_altair_serialization(self):
        import altair as alt
        import pandas as pd
        chart = alt.Chart(pd.DataFrame({"occasion":["T1","T2"],"value":[1,2]})).mark_line().encode(x="occasion:N", y="value:Q")
        self.assertIn("encoding", chart.to_dict())

    def test_chart_failure_isolated(self):
        st = Mock()
        with self.assertLogs("acpa_msmda.lab_display", level="ERROR"):
            with chart_guard(st, "fr"):
                raise TypeError("unexpected keyword argument 'closed'")
        st.warning.assert_called_once()
        self.assertIn("exports", st.warning.call_args.args[0])

    def test_longitudinal_render_and_fallback(self):
        csv = "participant;group;instrument;unit;occasion;date;protocol;value\\n"
        for g in ("A","B"):
            for i in range(4):
                for j in range(4):
                    csv += f"{g}{i};{g};cooper;m;T{j+1};2026-01-0{j+1};P1;{1500+100*i+20*j+i*j}\\n"
        rows = parse_long_csv(csv.replace("\\n","\n").encode(), {"cooper":{"unit":"m"}})
        app = AppTest.from_file(str(ROOT/"pages/2_Performance_Lab.py"), default_timeout=60)
        app.session_state["lang"] = "fr"
        app.session_state["lab_study_rows"] = rows
        app.run()
        app.checkbox(key="lab_study_enabled").set_value(True).run()
        app.multiselect(key="lab_study_occasions").set_value(["T1","T2","T3","T4"]).run()
        app.button(key="lab_study_panel").click().run()
        self.assertFalse(app.exception, str(app.exception))
        self.assertGreaterEqual(len(app.get("arrow_vega_lite_chart")), 2)
        with patch("altair.Chart", side_effect=TypeError("unexpected keyword argument 'closed'")):
            app.button(key="lab_study_panel").click().run()
        self.assertFalse(app.exception, str(app.exception))
        self.assertTrue(any("Graphique indisponible" in w.value for w in app.warning))
        self.assertGreaterEqual(len(app.dataframe), 2)
        self.assertGreaterEqual(len(app.get("download_button")), 2)
