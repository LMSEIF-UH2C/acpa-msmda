import io,json,pathlib,sys,tempfile,unittest,urllib.error
from email.message import Message
P=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(P))
from apple_checkpoint_adapter import provider,validate_query,main
from checkpoint_blocks import block
from plan_collection_v03 import identity

def query(term="test"):
    q={"term":term,"country":"ma","entity":"software","limit":50}
    q["request_id"]=identity(q);return q

class Response(io.BytesIO):
    def geturl(self):return "https://itunes.apple.com/search?term=test"

class Tests(unittest.TestCase):
    def test_facts_minimization(self):
        calls=[]
        data={"resultCount":1,"results":[{"trackId":123,"trackName":"Test","description":"Do not retain","artworkUrl100":"https://example.com/icon"}]}
        f=provider(lambda req,timeout:Response(json.dumps(data).encode()),calls.append)
        status,r=f(query())
        self.assertEqual(status,"ok");self.assertEqual(calls,[4]);self.assertEqual(r["facts"],[{"trackId":123,"trackName":"Test"}])
        self.assertFalse(r["raw_retained"]);self.assertEqual(len(r["response_sha256"]),64)
    def test_zero_is_success(self):
        status,r=provider(lambda *a,**kw:Response(b'{"resultCount":0,"results":[]}'),lambda n:None)(query())
        self.assertEqual((status,r["returned"]),("ok",0))
    def test_bad_count_is_error(self):
        status,r=provider(lambda *a,**kw:Response(b'{"resultCount":2,"results":[]}'),lambda n:None)(query())
        self.assertEqual(status,"error");self.assertNotIn("returned",r)
    def test_invalid_market(self):
        with self.assertRaises(ValueError):validate_query(dict(query(),country="xx"))
    def test_http_block_and_resume(self):
        calls=[]
        def opener(req,timeout):
            calls.append(req.full_url);h=Message();h["Retry-After"]="60";raise urllib.error.HTTPError(req.full_url,429,"Rate limited",h,None)
        f=provider(opener,lambda n:None)
        with tempfile.TemporaryDirectory() as d:
            out=pathlib.Path(d);plan=[query("one"),query("two")]
            a=block(plan,out,f,2,"apple-facts-v03");b=block(plan,out,f,2,"apple-facts-v03")
            self.assertTrue(a["blocked"]);self.assertEqual(a["new_attempts"],1);self.assertEqual(b["new_attempts"],0);self.assertEqual(len(calls),1)
    def test_transport_error(self):
        def fail(*a,**kw):raise TimeoutError("timeout")
        s,r=provider(fail,lambda n:None)(query());self.assertEqual(s,"error");self.assertEqual(r["error_type"],"TimeoutError")
if __name__=="__main__":unittest.main()
