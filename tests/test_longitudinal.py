import unittest
from acpa_msmda.longitudinal import parse_long_csv, export_long_csv, paired_panel

REG = {"sprint": {"unit": "s"}}
HEADER = "participant;group;instrument;unit;occasion;date;protocol;value\n"
ROWS = "E02;G1;sprint;s;post;2026-02-02;P1;4\nE01;G1;sprint;s;pre;2026-01-01;P1;5,5\nE02;G1;sprint;s;pre;2026-01-01;P1;6\nE01;G1;sprint;s;post;2026-02-02;P1;\n"

class LongitudinalTests(unittest.TestCase):
    def test_pairing_and_missing(self):
        rows = parse_long_csv((HEADER+ROWS).encode(), REG)
        self.assertEqual(parse_long_csv(export_long_csv(rows), REG), rows)
        panel = paired_panel(rows, "sprint", "P1", ["pre","post"])
        self.assertEqual(panel["participants"], ["E02"])
        self.assertEqual(panel["values"], [[6.0,4.0]])
        self.assertEqual(panel["n_excluded"], 1)
    def test_invalid_inputs(self):
        for invalid in (ROWS+ROWS, ROWS.replace(";4\n",";nan\n"), ROWS.replace(";s;post",";m;post"), ROWS.replace("E02;G1;sprint;s;pre","E02;G2;sprint;s;pre"), ROWS.replace(";4\n",";-4\n")):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                parse_long_csv((HEADER+invalid).encode(), REG)
    def test_reverse_time(self):
        rows = parse_long_csv((HEADER+ROWS).encode(), REG)
        with self.assertRaises(ValueError):
            paired_panel(rows, "sprint", "P1", ["post","pre"])
