import unittest
from pathlib import Path
from acpa_msmda.lab_display import trajectory_records

class LabDisplayTests(unittest.TestCase):
    def test_small_data_unchanged(self):
        rows,n=trajectory_records(["a","b"],[[1,2],[3,4]],["pre","post"])
        self.assertEqual(n,2)
        self.assertEqual(rows[-1],{"participant":"b","occasion":"post","value":4})
    def test_large_panel_display_only(self):
        ids=list(range(1000))
        values=[[i+j for j in range(60)] for i in ids]
        before=[row[:] for row in values]
        rows,n=trajectory_records(ids,values,list(range(60)))
        self.assertEqual(n,83)
        self.assertEqual(len(rows),4980)
        self.assertEqual(values,before)
        self.assertEqual(len(ids),1000)
    def test_no_partial_trajectory(self):
        self.assertEqual(trajectory_records(["a"],[[1,2,3]],["a","b","c"],max_rows=2),([],0))
    def test_misalignment(self):
        with self.assertRaises(ValueError):
            trajectory_records(["a"],[[1]],["a","b"])
    def test_subject_limit(self):
        rows,n=trajectory_records(list(range(150)),[[1,2]]*150,["pre","post"])
        self.assertEqual((len(rows),n),(200,100))
    def test_exports_do_not_trigger_rerun(self):
        root=Path(__file__).resolve().parents[1]
        page=(root/"pages/2_Performance_Lab.py").read_text(encoding="utf-8")
        renderer=(root/"src/acpa_msmda/lab_results.py").read_text(encoding="utf-8")
        for key in ("lab_study_analysis_export","lab_mv_download"):
            self.assertIn('export_key="'+key+'"',page)
        self.assertIn('key=export_key, on_click="ignore"',renderer)
