import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/"video"

class VideoAssetsTests(unittest.TestCase):
    def test_local_only_policy(self):
        html=(ROOT/"index.html").read_text(encoding="utf-8")
        js=(ROOT/"app.js").read_text(encoding="utf-8")
        self.assertIn("connect-src 'none'",html)
        self.assertIn("media-src blob:",html)
        self.assertIn("URL.createObjectURL(file)",js)
        self.assertIn("URL.revokeObjectURL(url)",js)
        self.assertNotRegex(js,r"\b(?:fetch|XMLHttpRequest|WebSocket|sendBeacon)\s*\(")
        for asset in ("app.js","style.css"):
            self.assertTrue((ROOT/asset).is_file())
    def test_interface_ids(self):
        html=(ROOT/"index.html").read_text(encoding="utf-8")
        js=(ROOT/"app.js").read_text(encoding="utf-8")
        ids=re.findall(r'\bid="([^"]+)"',html)
        self.assertEqual(len(ids),len(set(ids)))
        self.assertTrue(set(re.findall(r'\$\("([^"]+)"\)',js)).issubset(ids))
