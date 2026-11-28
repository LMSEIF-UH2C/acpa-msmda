import json
import pathlib
import sys
import tempfile
import unittest
P=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(P))
from checkpoint_blocks import block
from plan_collection_v03 import identity
def plan():
    q=[{"term":str(i),"country":"ma","entity":"software","limit":200} for i in range(7)]
    for x in q:x["request_id"]=identity(x)
    return q
class Tests(unittest.TestCase):
    def test_resume(self):
        with tempfile.TemporaryDirectory() as d:
            calls=[];f=lambda q:(calls.append(q["request_id"]) or "ok",{"fixture":True})
            p=plan();a=block(p,pathlib.Path(d),f,3);b=block(p,pathlib.Path(d),f,4)
            self.assertEqual((a["new_attempts"],b["reused_successes"],b["new_attempts"]),(3,3,4))
            self.assertTrue(b["complete_success"]);self.assertEqual(len(set(calls)),7)
    def test_corruption(self):
        with tempfile.TemporaryDirectory() as d:
            out=pathlib.Path(d);p=plan();block(p,out,lambda q:("ok",{}),1)
            f=next(out.glob("*.record.json"));r=json.loads(f.read_text());r["payload"]={"changed":1};f.write_text(json.dumps(r))
            with self.assertRaises(ValueError):block(p,out,lambda q:("ok",{}),1)
    def test_plan_change(self):
        with tempfile.TemporaryDirectory() as d:
            out=pathlib.Path(d);p=plan();block(p,out,lambda q:("ok",{}),1)
            with self.assertRaises(ValueError):block(p[::-1],out,lambda q:("ok",{}),1)
    def test_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            out=pathlib.Path(d);p=plan();a=block(p,out,lambda q:("blocked",{"http":429}),7);b=block(p,out,lambda q:("ok",{}),7)
            self.assertEqual(a["new_attempts"],1);self.assertEqual(b["new_attempts"],0);self.assertTrue(b["blocked"])
if __name__=="__main__":unittest.main()
