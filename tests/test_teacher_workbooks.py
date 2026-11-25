import io
import sys
import unittest
from pathlib import Path
from openpyxl import load_workbook
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from acpa_msmda import teacher_workbooks as x, formative_backup as fb, journal, curriculum


class TeacherWorkbookTests(unittest.TestCase):
    def setUp(self):
        self.lesson = {"context": ("Endurance", "Collège", 3, 1, 1, "G01"),
                       "criteria": [("1", "Motrice", "=1+1"), ("2", "Sociale", "التعاون")],
                       "records": {"E001": {"1": "Acquis"}, "E002": {}}}
        self.cycles = [{"number": 1, "start": "2026-09-07", "end": "2026-10-17",
                        "activities": ["Triple saut"]}]
        self.project = {"group":"TC1","cycle":1,"level":"Lycée","profile":"MA","grade":"TC",
                        "module":"","institutional":"","reference":"","diagnostic":"Observation initiale",
                        "target":"Coordination des bonds","progression":"","assessment":""}
        self.entry = {"id":"s1","date":"2026-09-07","group":"TC1","activity":"Triple saut",
                      "level":"Lycée","cycle":1,"lesson":1,"duration":60,"objectives":"=1+1",
                      "status":"Prévue","reflection":""}

    def test_formative_full_roundtrip(self):
        history = {self.lesson["context"]: self.lesson}
        raw = x.formative_xlsx(self.lesson, history)
        self.assertEqual(x.restore_formative_xlsx(raw), fb.load_backup(fb.make_backup(self.lesson, history)))
        wb = load_workbook(io.BytesIO(raw))
        self.assertEqual(wb["Critères"]["D2"].data_type, "s")
        self.assertEqual(wb["Critères"]["D2"].value, "=1+1")
        self.assertEqual(wb["Critères"]["D3"].value, "التعاون")
        wb.close()

    def test_blank_active(self):
        active = {"context": ("Endurance","Collège",3,0,0,""), "criteria": [], "records": {}}
        self.assertEqual(x.restore_formative_xlsx(x.formative_xlsx(active, {})), (active, {}))

    def test_history_only(self):
        history = {self.lesson["context"]: self.lesson}
        self.assertEqual(x.restore_formative_xlsx(x.formative_xlsx(None, history)), (None, history))

    def test_journal_roundtrip(self):
        slots = [{"group":"TC1","level":"Lycée","weekday":0,"duration":60,"start_minute":480}]
        interruptions = [["2026-09-14","2026-09-14"]]
        args = (self.cycles,[self.entry],slots,interruptions,[self.project])
        self.assertEqual(x.restore_journal_xlsx(x.journal_xlsx(*args)),
                         journal.restore_workspace(journal.workspace_backup(*args)))

    def test_empty_journal(self):
        self.assertEqual(x.restore_journal_xlsx(x.journal_xlsx([],[],[],[],[])), ([],[],[],[],[]))

    def test_projects_roundtrip(self):
        self.assertEqual(x.restore_projects_xlsx(x.projects_xlsx([self.project],self.cycles),self.cycles),[self.project])

    def test_formula_rejected(self):
        wb = load_workbook(io.BytesIO(x.formative_xlsx(self.lesson,{})))
        wb["Critères"]["D2"] = "=1+1"
        out = io.BytesIO()
        wb.save(out)
        wb.close()
        with self.assertRaises(ValueError):
            x.restore_formative_xlsx(out.getvalue())

    def test_wrong_format(self):
        for raw in (b"not a workbook", x.journal_xlsx([],[],[],[],[])):
            with self.assertRaises(ValueError):
                x.restore_formative_xlsx(raw)

    def test_report_numeric_and_literal(self):
        raw = "Code,Mesure,Commentaire\n001,12.5,=1+1\n002,,سلام\n".encode()
        wb = load_workbook(io.BytesIO(x.report_xlsx(raw,numeric_columns=(1,))))
        ws = wb["Export"]
        self.assertEqual(ws["A2"].value,"001")
        self.assertEqual(ws["B2"].value,12.5)
        self.assertEqual(ws["C2"].data_type,"s")
        self.assertIsNone(ws["B3"].value or None)
        wb.close()


if __name__ == "__main__":
    unittest.main()
