import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda.journal import full_backup, restore_full, cycle_backup
from acpa_msmda.timetable import generate
from acpa_msmda.cycle_plan import check_journal
from acpa_msmda.aps_specialties import catalog_category

class JournalBackupTests(unittest.TestCase):
    def setUp(self):
        self.cycles=[{"number":1,"start":"2026-11-02","end":"2026-11-22","activities":["Triple saut"]}]
        self.slots=[{"group":"TC1","level":"Lycée","weekday":0,"start_minute":840,"duration":60}]
        self.breaks=[["2026-11-09","2026-11-15"]]
        self.entries=generate(self.cycles,self.slots,self.breaks,[])
    def test_full_roundtrip(self):
        self.assertEqual(restore_full(full_backup(self.cycles,self.entries,self.slots,self.breaks)),(self.cycles,self.entries,self.slots,self.breaks))
    def test_previous_version(self):
        self.assertEqual(restore_full(cycle_backup(self.cycles,self.entries)),(self.cycles,self.entries,[],[]))
    def test_incompatible(self):
        with self.assertRaises(ValueError):
            check_journal([dict(self.cycles[0],activities=["Saut en hauteur"])],self.entries)
        with self.assertRaises(ValueError):
            restore_full(b'{"version":3}')
    def test_specialty(self):
        self.assertEqual(catalog_category("Triple saut"),"Athlétisme")
        self.assertEqual(catalog_category("Course en durée"),"Endurance")
        self.assertEqual(catalog_category("APS locale"),"Autre")
