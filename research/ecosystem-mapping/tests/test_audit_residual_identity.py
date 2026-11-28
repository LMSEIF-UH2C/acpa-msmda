import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from audit_residual_identity import parse_link,field_audit
class ResidualTests(unittest.TestCase):
    def test_apple(self):self.assertEqual(parse_link("https://apps.apple.com/fr/app/demo/id123456"),("apple","123456"))
    def test_play(self):self.assertEqual(parse_link("https://play.google.com/store/apps/details?id=org.demo"),("google_play","org.demo"))
    def test_fdroid(self):self.assertEqual(parse_link("https://f-droid.org/en/packages/org.demo/"),("fdroid","org.demo"))
    def test_github(self):
        self.assertEqual(parse_link("https://github.com/Owner/Repo.git"),("github_repository_url","owner/repo"))
        self.assertEqual(parse_link("https://github.com/Owner/Repo/issues"),("other_url",None))
    def test_host(self):self.assertEqual(parse_link("https://apps.apple.com.example.org/id123"),("other_url",None))
    def test_nested_counts(self):
        rows=[{"id":"x","links":[{"url":"https://apps.apple.com/app/id123"},{"url":"https://apps.apple.com/app/id456"}]}]
        r=field_audit(rows);self.assertEqual(r["url_paths_record_counts"]["links.[].url"],1);self.assertEqual(r["multi_identifier_records_by_type"]["apple"],1)
