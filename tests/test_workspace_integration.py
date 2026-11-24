import unittest
import sys
import json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acpa_msmda import session_context as ctx
from acpa_msmda.journal import workspace_backup, restore_workspace, full_backup
from acpa_msmda.timetable import generate

class WorkspaceTests(unittest.TestCase):
    def test_specialty(self):
        state={}
        ctx.put(state,"activity","Athlétisme")
        ctx.put(state,"activity_specialty","Triple saut")
        self.assertEqual(ctx.activity_label(state),"Triple saut")
        self.assertIn("Triple saut",ctx.summary(state))
        self.assertIn("triple saut",ctx.search_query(state).lower())
        ctx.put(state,"activity","Football")
        self.assertEqual(ctx.activity_label(state),"Football")
        ctx.put(state,"activity","Athlétisme")
        self.assertEqual(ctx.activity_label(state),"Athlétisme")
    def test_workspace(self):
        cycles=[{"number":1,"start":"2026-11-02","end":"2026-11-22","activities":["Triple saut"]}]
        slots=[{"group":"TC1","level":"Lycée","weekday":0,"start_minute":840,"duration":60}]
        breaks=[["2026-11-09","2026-11-15"]]
        entries=generate(cycles,slots,breaks,[])
        projects=[{"group":"TC1","cycle":1,"level":"Lycée","profile":"MA","grade":"TC","module":"","institutional":"","reference":"","diagnostic":"","target":"Coordination","progression":"","assessment":""}]
        raw=workspace_backup(cycles,entries,slots,breaks,projects)
        self.assertEqual(restore_workspace(raw),(cycles,entries,slots,breaks,projects))
        self.assertEqual(restore_workspace(full_backup(cycles,entries,slots,breaks)),(cycles,entries,slots,breaks,[]))
        invalid=json.loads(raw)
        invalid["projects"][0]["cycle"]=99
        with self.assertRaises(ValueError):
            restore_workspace(json.dumps(invalid).encode())
