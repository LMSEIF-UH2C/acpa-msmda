"""Run the actual published heuristic ACPA/MSMDA engine on synthetic data.

Usage: python run_engine.py --language fr --query "basketball sans internet"
No network calls, telemetry, student data or persistence.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from acpa_msmda.catalog import compare_catalog  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="ACPA/MSMDA heuristic engine demonstration")
    parser.add_argument("--language", choices=("fr", "ar", "en"), default="fr")
    parser.add_argument("--query", default="basketball sans connexion", help="Fictitious pedagogical context only")
    args = parser.parse_args()
    result = compare_catalog(args.query, args.language, ROOT / "data" / "synthetic_tools.json")
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
