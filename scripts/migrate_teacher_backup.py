"""Offline migration of legacy ACPA backups; no upload or network access."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from acpa_msmda import teacher_workbooks as x, formative_backup as fb, journal, curriculum


def read(path):
    with path.open("rb") as f:
        raw = f.read(x.MAX_FILE + 1)
    if len(raw) > x.MAX_FILE:
        raise ValueError("Fichier trop volumineux")
    return raw


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("kind", choices=["formative","journal","projects"])
    p.add_argument("source", type=Path)
    p.add_argument("destination", type=Path)
    p.add_argument("--journal", type=Path, help="Journal associé pour valider les projets de cycle")
    a = p.parse_args()
    try:
        if a.destination.suffix.lower() != ".xlsx":
            raise ValueError("La destination doit se terminer par .xlsx")
        raw = read(a.source)
        if a.kind == "formative":
            result = x.formative_xlsx(*fb.load_backup(raw))
            x.restore_formative_xlsx(result)
        elif a.kind == "journal":
            result = x.journal_xlsx(*journal.restore_workspace(raw))
            x.restore_journal_xlsx(result)
        else:
            if a.journal is None:
                raise ValueError("--journal est obligatoire pour les projets")
            context = read(a.journal)
            cycles = (x.restore_journal_xlsx(context) if a.journal.suffix.lower()==".xlsx"
                      else journal.restore_workspace(context))[0]
            result = x.projects_xlsx(curriculum.import_projects(raw,cycles),cycles)
            x.restore_projects_xlsx(result,cycles)
        with a.destination.open("xb") as f:
            f.write(result)
    except (ValueError,OSError) as exc:
        p.exit(1, f"Migration refusée : {exc}\n")
    print("Classeur Excel créé et vérifié. Sauvegarde originale conservée.")


if __name__ == "__main__":
    main()
