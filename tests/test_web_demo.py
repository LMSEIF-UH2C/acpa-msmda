"""Mobile-first public interface smoke tests."""
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
APP=Path(__file__).resolve().parents[1]/"app.py"
def start():
    return AppTest.from_file(str(APP),default_timeout=30).run()
class MobileHomepageTests(unittest.TestCase):
    def test_load(self):
        app=start()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.metric),0)
    def test_empty_search(self):
        app=start()
        app.button[4].click().run()
        self.assertFalse(app.exception)
        self.assertGreaterEqual(len(app.warning),1)
    def test_context_search(self):
        app=start()
        app.text_area[0].set_value("endurance course").run()
        app.button[4].click().run()
        self.assertFalse(app.exception)
    def test_catalogue_filter(self):
        app=start()
        app.text_input[0].set_value("Kinovea").run()
        self.assertFalse(app.exception)
    def test_navigation_targets_registered(self):
        source=APP.read_text(encoding="utf-8")
        self.assertIn("st.navigation(",source)
        for page in ("2_Performance_Lab.py","3_Espace_Enseignant.py","4_Technologies_Reelles.py","5_Studio_Pedagogique.py"):
            self.assertTrue((APP.parent/"pages"/page).is_file())
            self.assertIn(page,source)
    def test_professional_navigation(self):
        source=APP.read_text(encoding="utf-8")
        self.assertIn(":material/search:",source)
        self.assertIn(":material/monitoring:",source)
        self.assertNotIn("🔎",source)
        self.assertNotIn("📚",source)
    def test_max_length(self):
        app=start()
        self.assertEqual(app.text_area[0].proto.max_chars,1000)
if __name__=="__main__":unittest.main()
