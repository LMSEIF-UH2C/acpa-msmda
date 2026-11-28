import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from audit_identity_sensitivity import native_link,link_edges,name_overlap,legacy_groups
from normalize_identity import add
class SensitivityTests(unittest.TestCase):
    def test_native_apple(self):self.assertEqual(native_link("https://apps.apple.com/fr/app/demo/id123"),("apple","123"))
    def test_apple_nonlisting(self):self.assertIsNone(native_link("https://apps.apple.com/account/id123"))
    def test_fdroid(self):self.assertEqual(native_link("https://f-droid.org/en/packages/org.demo/"),("fdroid","org.demo"))
    def test_play_not_fdroid(self):self.assertIsNone(native_link("https://play.google.com/store/apps/details?id=org.demo"))
    def test_native_namespace(self):
        e,g,f=link_edges([{"id":"a","source_url":"https://apps.apple.com/app/id123"}],{("fdroid","123"):{} })
        self.assertFalse(e)
    def test_multiple_local_same_listing(self):
        e,g,f=link_edges([{"id":"a","source_url":"https://apps.apple.com/app/id123"},{"id":"b","source_url":"https://apps.apple.com/fr/app/id123"}],{("apple","123"):{} })
        self.assertEqual(len(e),2);self.assertEqual(len(g[("apple","123")]),2)
    def test_name_normalization(self):self.assertTrue(name_overlap(["École"],["E\u0301COLE"]))
    def test_group_no_merge(self):
        items={}
        for i in range(31):add(items,"fdroid",str(i),names=["same" if i<2 else str(i)],repo=["owner/repo"])
        g=legacy_groups(items)[0];self.assertEqual(g["pair_upper_bound"],465);self.assertEqual(g["pairs_with_shared_normalized_name"],1)
