"""Vérifie que les tests de contexte partagé détectent une régression réelle.

Copie le dépôt dans un dossier temporaire, casse volontairement la recopie du
magasin vers les widgets (session_context.bind), puis lance les tests de
contexte : ils DOIVENT échouer. Le script échoue si la mutation passe inaperçue.

Usage : python scripts/mutation_check.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = "src/acpa_msmda/session_context.py"
ORIGINAL = "    session[widget_key] = data[key]\n"
MUTANT = "    session.setdefault(widget_key, data[key])\n"


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / "repo"
        shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        source = (copy / TARGET).read_text(encoding="utf-8")
        if ORIGINAL not in source:
            print("Ligne à muter introuvable : mettre à jour scripts/mutation_check.py")
            return 2
        (copy / TARGET).write_text(source.replace(ORIGINAL, MUTANT), encoding="utf-8")
        result = subprocess.run([sys.executable, "-m", "unittest", "tests.test_shared_context"],
                                cwd=copy, capture_output=True, text=True)
    if result.returncode == 0:
        print("ÉCHEC : la persistance a été cassée mais les tests passent encore.")
        return 1
    print("OK : la mutation est détectée par les tests de contexte partagé.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
