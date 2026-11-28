import pathlib,sys,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from identity_registry import Register
from integrate_legacy import integrate
class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.r=Register(pathlib.Path(self.tmp.name)/"db.sqlite",True)
        self.data={"source":[("a",{"kind":"test"})],"record":[("a:1","a",{"source":"a"}),("a:2","a",{"source":"a"})],"observation":[("o","a:1",{"record":"a:1"})],"legacy_candidate":[("a:1","a:2",{"signals":["name"]})]}
    def tearDown(self):self.r.close();self.tmp.cleanup()
    def test_replay(self):
        self.assertEqual(integrate(self.r,self.data),"integrated")
        self.assertEqual(integrate(self.r,self.data),"already_integrated")
        self.assertEqual(self.r.db.execute("SELECT count(*) FROM record").fetchone()[0],2)
    def test_rollback(self):
        with self.assertRaises(RuntimeError):integrate(self.r,self.data,True)
        self.assertEqual(self.r.db.execute("SELECT count(*) FROM record").fetchone()[0],0)
        self.assertEqual(self.r.db.execute("SELECT count(*) FROM integration_checkpoint").fetchone()[0],0)
        self.assertEqual(integrate(self.r,self.data),"integrated")
    def test_changed_manifest(self):
        integrate(self.r,self.data);self.data["record"][0][2]["extra"]="changed"
        with self.assertRaises(ValueError):integrate(self.r,self.data)
