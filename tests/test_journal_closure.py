import unittest
from datetime import date
from acpa_msmda.journal import validate_entries, MAX_ENTRIES, workspace_backup, restore_workspace
from acpa_msmda.timetable import generate

def entry(i, group="1AC"):
    return dict(id=str(i),date="2026-11-24",group=group,activity="Endurance",level="Collège",cycle=1,lesson=1,duration=60,objectives="",status="Prévue",reflection="")

class JournalClosureTests(unittest.TestCase):
    def test_duplicate_class_day(self):
        with self.assertRaises(ValueError):
            validate_entries([entry(1),entry(2)])
    def test_distinct_classes_same_day(self):
        self.assertEqual(len(validate_entries([entry(1),entry(2,"2AC")])),2)
    def test_annual_capacity(self):
        self.assertEqual(MAX_ENTRIES,3000)
        cycles=[dict(number=1,start="2026-09-01",end="2027-06-30",activities=["Endurance"])]
        slots=[dict(group=str(i),level="Collège",weekday=day,duration=60,start_minute=480+i*60) for i in range(8) for day in (0,3,5,6)]
        entries=generate(cycles,slots,[],[])
        self.assertGreater(len(entries),1000)
        self.assertEqual(restore_workspace(workspace_backup(cycles,entries,slots,[],[]))[1],entries)
    def test_malformed_inputs(self):
        for slots,interruptions in (([None],[]),([], [None]),([], ["ab"]),([], [[1,2]])):
            with self.assertRaises(ValueError):
                generate([],slots,interruptions,[])
