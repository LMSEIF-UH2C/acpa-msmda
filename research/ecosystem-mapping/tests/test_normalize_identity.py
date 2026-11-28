import pathlib,sys,unittest
P=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(P))
from normalize_identity import add,candidates,name_key,repo_url,report
class Tests(unittest.TestCase):
    def test_source_id_repetition(self):
        d={};add(d,"apple","1",["Old"]);add(d,"apple","1",["New"])
        self.assertEqual(len(d),1);self.assertEqual(d[("apple","1")]["names"],{"Old","New"})
    def test_same_name_not_merge(self):
        d={};add(d,"apple","1",["Timer"]);add(d,"fdroid","pkg",["Timer"])
        e,f=candidates(d);self.assertEqual(len(d),2);self.assertEqual(len(e),1)
        self.assertEqual(report(d,e,f,{})["automatic_cross_id_merges"],0)
    def test_repository_link_candidate(self):
        d={};add(d,"fdroid","pkg",["A"],repo=["x/y"]);add(d,"github","2",["B"],repo=["x/y"],fork=True)
        e,_=candidates(d);self.assertEqual(next(iter(e.values())),{"repository_url"});self.assertEqual(len(d),2)
    def test_namespace_collision(self):
        d={};add(d,"apple","123");add(d,"github","123");self.assertEqual(len(d),2);self.assertFalse(candidates(d)[0])
    def test_bundle_not_proof(self):
        d={};add(d,"apple","1",package=["com.x.a"]);add(d,"fdroid","com.x.a",package=["com.x.a"])
        e,_=candidates(d);self.assertEqual(next(iter(e.values())),{"identifier_string"})
    def test_unicode(self):
        self.assertEqual(name_key("École–EPS"),name_key("E\u0301cole EPS"))
        self.assertEqual(name_key("تقييم"),"تقييم")
    def test_url(self):
        self.assertEqual(repo_url("https://github.com/X/Y.git"),"x/y")
        self.assertEqual(repo_url("https://github.com.evil.test/x/y"),"")
        self.assertEqual(repo_url("https://github.com/x/y/issues"),"")
    def test_large_group_deferred(self):
        d={}
        for i in range(31):add(d,"apple",str(i),["Timer"])
        e,f=candidates(d);self.assertEqual(len(e),0);self.assertEqual(f,[{"rule":"name","size":31}]);self.assertEqual(len(d),31)
if __name__=="__main__":unittest.main()
