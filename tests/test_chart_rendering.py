"""Regression: teacher charts must not depend on Altair rendering."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ChartRenderingTests(unittest.TestCase):
    def test_native_charts(self):
        for name in ("2_Performance_Lab.py","5_Studio_Pedagogique.py"):
            source=(ROOT/"pages"/name).read_text(encoding="utf-8")
            self.assertNotIn("st.bar_chart(",source)
            self.assertNotIn("st.line_chart(",source)
            self.assertIn("st.progress(",source)
if __name__=="__main__":unittest.main()
