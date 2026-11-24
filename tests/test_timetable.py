import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda.timetable import generate

class TimetableTests(unittest.TestCase):
    def setUp(self):
        self.cycles=[{"number":1,"start":"2026-11-02","end":"2026-11-22","activities":["Triple saut"]}]
        self.slots=[{"group":"TC1","level":"Lycée","weekday":0,"start_minute":480,"duration":60},{"group":"TC2","level":"Lycée","weekday":2,"start_minute":540,"duration":60}]
    def test_generate(self):
        result=generate(self.cycles,self.slots,[["2026-11-09","2026-11-15"]],[])
        self.assertEqual(len(result),4)
        self.assertEqual({e["activity"] for e in result},{"Triple saut"})
        self.assertEqual([e["lesson"] for e in result if e["group"]=="TC1"],[1,2])
        self.assertEqual(generate(self.cycles,self.slots,[["2026-11-09","2026-11-15"]],result),result)
    def test_overlap(self):
        with self.assertRaises(ValueError):
            generate(self.cycles,self.slots+[dict(self.slots[0],group="TC3")],[],[])
    def test_invalid_interruption(self):
        with self.assertRaises(ValueError):
            generate(self.cycles,self.slots,[["2026-11-10","2026-11-09"]],[])

    def test_moroccan_rules(self):
        base=self.slots[0]
        for slot in (dict(base,start_minute=840),dict(base,start_minute=870)):
            with self.assertRaises(ValueError):
                generate([], [slot], [], [])
        generate([], [dict(base,start_minute=900)], [], [])
        for second in (dict(base,weekday=1),dict(base,weekday=2,start_minute=479),dict(base,weekday=5,start_minute=600)):
            with self.assertRaises(ValueError):
                generate([], [base,second], [], [])
        generate([], [base,dict(base,weekday=2)], [], [])
        generate([], [dict(base,start_minute=840)], [], [],profile="generic")
