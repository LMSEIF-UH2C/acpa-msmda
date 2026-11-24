import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from acpa_msmda.formative import LEVELS, snapshot, compare_lessons, summarize_observations
from acpa_msmda.formative_backup import make_backup, load_backup
from acpa_msmda.pdf import formative_comparison_pdf
from acpa_msmda import i18n

class FormativeTests(unittest.TestCase):
    def setUp(self):
        self.a=("Basketball","Collège",3,1,1,"G01")
        self.b=("Basketball","Collège",3,1,2,"G01")
        self.criteria=[("1","Motrice","Réussir une passe")]
        self.before=snapshot(self.a,self.criteria,{"E001":{"1":LEVELS[1]},"E002":{"1":LEVELS[3]}})
        self.after=snapshot(self.b,self.criteria,{"E001":{"1":LEVELS[3]},"E002":{"1":LEVELS[2]},"E003":{"1":LEVELS[4]}})

    def test_comparison(self):
        result=compare_lessons(self.before,self.after)[0]
        self.assertEqual((result["higher"],result["same"],result["lower"],result["missing"]),(1,0,1,1))
        self.assertEqual(summarize_observations([LEVELS[0],LEVELS[1]])["observed"],1)
        with self.assertRaises(ValueError):
            compare_lessons(self.after,self.before)
        for lang in ("fr","ar","en"):
            try:
                i18n.use(lang)
                self.assertTrue(formative_comparison_pdf(self.b,1,[result]).startswith(b"%PDF"))
            finally:
                i18n.use("fr")

    def test_roundtrip(self):
        current,history=load_backup(make_backup(self.after,{self.a:self.before}))
        self.assertEqual(current,self.after)
        self.assertEqual(history,{self.a:self.before})
        self.assertEqual(compare_lessons(history[self.a],current),compare_lessons(self.before,self.after))

    def test_reject_bad_backups(self):
        raw=make_backup(self.after,{self.a:self.before})
        for mutate in (
            lambda v:v.update(version=2),
            lambda v:v["history"].append(v["history"][0]),
            lambda v:v["current"]["records"].update(E999={"1":LEVELS[3]}),
            lambda v:v["current"]["records"]["E001"].update({"1":"unknown"}),
            lambda v:v["current"]["criteria"].append(v["current"]["criteria"][0]),
        ):
            v=json.loads(raw)
            mutate(v)
            with self.assertRaises(ValueError):
                load_backup(json.dumps(v).encode())
        with self.assertRaises(ValueError):
            load_backup(b"not JSON")
