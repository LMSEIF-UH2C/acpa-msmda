"""Banc d'essai visuel de lab_results.render (mêmes données que tests/test_lab_results.py)."""
import sys
sys.path.insert(0, "/home/claude/acpa-msmda/src"); sys.path.insert(0, "/home/claude/acpa-msmda/tests")
import streamlit as st
import numpy as np
from acpa_msmda import i18n, lab_results as lr
from acpa_msmda.ui import LAB, configure_page
configure_page(LAB)
import test_lab_results as T
m = st.query_params.get("m", "paired_t")
res = T.results(); x = np.asarray(T.PANEL)
res["descriptive"] = {"n_eligible": 26, "n_complete": 24, "n_excluded": 2}
args = {"paired_t": {"panel_values": [r[:2] for r in T.PANEL], "columns": T.OCC[:2]},
        "repeated_anova": {"panel_values": T.PANEL, "columns": T.OCC},
        "mixed_anova": {"group_panels": [T.PANEL[:12], T.PANEL[12:]], "group_labels": ["TC1", "TC2"], "columns": T.OCC},
        "one_way": {"samples": T.GROUPS, "group_labels": ["TC1", "TC2", "1B1"]},
        "regression": {"matrix": x[:, [2, 0, 1]], "columns": ["Sprint T3", "Sprint T1", "Sprint T2"]},
        "moderation": {"matrix": x[:, [2, 0, 1]], "columns": ["Y", "X", "M"]},
        "pearson": {"panel_values": [r[:2] for r in T.PANEL], "columns": T.OCC[:2]},
        "descriptive": {"panel_values": T.PANEL, "columns": T.OCC}}[m]
r = res[m]
if m in ("paired_t", "repeated_anova", "pearson"): r.update({"n_eligible": 26, "n_complete": 24, "n_excluded": 2, "scipy_version": "1.18.1"})
lr.render(st, m, m, r, export_key="k", file_name="a.json", chart_args={**args, "unit": "s"},
          panel_values=args.get("panel_values"), columns=args.get("columns"))
