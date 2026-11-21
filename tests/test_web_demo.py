"""Smoke tests for the public EPS catalogue interface."""
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
APP=Path(__file__).resolve().parents[1]/"app.py"
def start():
    return AppTest.from_file(str(APP),default_timeout=30).run()
class PublicCatalogueTests(unittest.TestCase):
    def test_catalogue_loads(self):
        app=start()
        self.assertFalse(app.exception)
        self.assertTrue(len(app.metric)>=3)
    def test_search_empty_context(self):
        app=start()
        self.assertFalse(app.exception)
        app.text_area[0].set_value(" ").run()
        self.assertFalse(app.exception)
    def test_catalogue_filter(self):
        app=start()
        self.assertFalse(app.exception)
        app.text_input[0].set_value("Kinovea").run()
        self.assertFalse(app.exception)
    def test_input_length_limit(self):
        app=start()
        self.assertEqual(app.text_area[0].proto.max_chars,1000)
if __name__=="__main__":unittest.main()
