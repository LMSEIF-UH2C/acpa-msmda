import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from global_identity import make_index,collect,compare
class GlobalTests(unittest.TestCase):
    def test_cross_only(self):
        i=make_index()
        for r in ("apple:1","apple:2","sill:1"):collect(i,r,["Same"])
        e,d,s=compare(i);self.assertEqual(len(e),2)
    def test_short(self):
        i=make_index()
        for r in ("apple:1","sill:1"):collect(i,r,["AI"])
        e,d,s=compare(i);self.assertEqual(len(e),0);self.assertEqual(s[0]["cross_source_pairs_upper_bound"],1)
    def test_deferred(self):
        i=make_index()
        for n in range(30):collect(i,"apple:"+str(n),["Same"])
        collect(i,"sill:1",["Same"])
        e,d,s=compare(i);self.assertEqual(len(e),0);self.assertEqual(d[0]["cross_source_pairs_upper_bound"],30)
    def test_multiple_signals(self):
        i=make_index()
        for r in ("apple:1","fdroid:1"):collect(i,r,["Example"],["org.example"],["https://github.com/example/repo"])
        e,d,s=compare(i);self.assertEqual(next(iter(e.values())),{"name","identifier_string","repository_url"})
    def test_repo_not_subpage(self):
        i=make_index()
        collect(i,"github:1",urls=["https://github.com/example/repo"])
        collect(i,"catalog:1",urls=["https://github.com/example/repo/issues"])
        self.assertEqual(len(compare(i)[0]),0)
    def test_unicode(self):
        i=make_index();collect(i,"apple:1",["École"]);collect(i,"sill:1",["E\u0301COLE"])
        self.assertEqual(len(compare(i)[0]),1)
