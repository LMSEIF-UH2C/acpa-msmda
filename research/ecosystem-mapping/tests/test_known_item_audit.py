import pathlib,sys,unittest
P=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(P))
from known_item_audit import check
from normalize_identity import add
class Tests(unittest.TestCase):
    def test_namespace(self):
        d={};add(d,"apple","123",["A"]);add(d,"github","123",["A"],repo=["a/a"])
        self.assertEqual(check(d,[{"source":"apple","key":"123"}])["results"][0]["matched_source_ids"],["123"])
    def test_name_not_identity(self):
        d={};add(d,"fdroid","p.other",["Same name"])
        self.assertEqual(check(d,[{"source":"fdroid","key":"p.target","name":"Same name"}])["results"][0]["status"],"NOT_OBSERVED")
    def test_repo_candidate(self):
        d={};add(d,"github","9",repo=["a/b"],phases=["pilot"])
        self.assertEqual(check(d,[{"source":"github","key":"a/b"}])["results"][0]["phases"],["pilot"])
    def test_ambiguous(self):
        d={};add(d,"github","9",repo=["a/b"]);add(d,"github","10",repo=["a/b"])
        self.assertEqual(check(d,[{"source":"github","key":"a/b"}])["results"][0]["status"],"AMBIGUOUS")
if __name__=="__main__":unittest.main()
