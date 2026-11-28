"""Prepare an isolated experimental SQLite register from the existing documentary pilot."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from acpa_msmda.experimental_registry import import_snapshot
from acpa_msmda.real_catalog import DEFAULT_PATH

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--db",required=True)
    parser.add_argument("--date",required=True)
    args=parser.parse_args()
    manifest=json.loads((ROOT/"data/experimental_documentary_leads.json").read_text(encoding="utf-8"))
    print(json.dumps(import_snapshot(args.db,DEFAULT_PATH,manifest,observed_on=args.date),sort_keys=True))
