import pathlib,sys,tempfile,unittest,urllib.error,json
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from wikidata_checkpoint_adapter import plan,validate,provider,MODE
from checkpoint_blocks import block,recover
class WDCheckpointTests(unittest.TestCase):
    def test_plan(self):self.assertEqual(len(set(validate(plan()))),4)
    def test_wrong_plan(self):
        p=plan();p[0]["qid"]="Q1"
        with self.assertRaises(ValueError):validate(p)
    def test_blocked_no_retries(self):
        with tempfile.TemporaryDirectory() as d:
            out=pathlib.Path(d);calls=[]
            def denied(q):calls.append(q);return "blocked",{"http_status":429}
            block(plan(),out,denied,2,mode=MODE,validator=validate,stop_on_error=True)
            block(plan(),out,denied,2,mode=MODE,validator=validate,stop_on_error=True)
            self.assertEqual(len(calls),1)
    def test_error_no_retries(self):
        with tempfile.TemporaryDirectory() as d:
            out=pathlib.Path(d);calls=[]
            def fail(q):calls.append(q);return "error",{}
            block(plan(),out,fail,2,mode=MODE,validator=validate,stop_on_error=True)
            block(plan(),out,fail,2,mode=MODE,validator=validate,stop_on_error=True)
            self.assertEqual(len(calls),1)
    def test_valid_empty(self):
        class Response:
            status=200
            def __init__(self,url):self.url=url
            def __enter__(self):return self
            def __exit__(self,*a):pass
            def geturl(self):return self.url
            def read(self,n):return b'{"head":{"vars":["item","en","fr","ar"]},"results":{"bindings":[]}}'
        s,p=provider(lambda req,timeout:Response(req.full_url),lambda n:None)(plan()[0]);self.assertEqual(s,"ok");self.assertEqual(p["returned"],0)
    def test_http_429(self):
        def fail(req,timeout):raise urllib.error.HTTPError(req.full_url,429,"blocked",{"Retry-After":"60"},None)
        s,p=provider(fail,lambda n:None)(plan()[0]);self.assertEqual(s,"blocked");self.assertEqual(p["retry_after"],"60")
