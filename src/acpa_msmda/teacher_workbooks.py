"""Teacher-facing Excel backups. Existing JSON validators remain the source of truth.

The workbook has ordinary, readable tables, not embedded JSON. Never execute formulas.
Legacy JSON is supported only through the offline migration script.
"""
from __future__ import annotations

import csv
import io
import json
import zipfile
from openpyxl import Workbook, load_workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from . import formative_backup as fb, journal, curriculum

MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
MAX_FILE = 10 * 1024 * 1024
MAX_EXPANDED = 150 * 1024 * 1024
META = "ACPA"
LESSONS = ("Séances", ("ID séance","Type","APS","Niveau","Effectif","Cycle","Séance","Groupe"))
CRITERIA = ("Critères", ("ID séance","ID critère","Dimension","Critère"))
PUPILS = ("Codes élèves", ("ID séance","Code élève"))
OBS = ("Observations", ("ID séance","Code élève","ID critère","Niveau observé"))
CYCLES = ("Cycles", ("number","start","end","activity"))
ENTRIES = ("Journal", journal.FIELDS)
SLOTS = ("Créneaux", ("group","level","weekday","duration","start_minute"))
BREAKS = ("Interruptions", ("start","end"))
PROJECTS = ("Projets", curriculum.FIELDS)


def _cell(ws, value, header=False):
    c = WriteOnlyCell(ws, value=value)
    if isinstance(value, str):
        c.data_type = "s"  # including strings beginning with =, +, -, @
    if header:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="006233")
    return c


def _sheet(wb, name, fields, rows):
    ws = wb.create_sheet(name)
    ws.freeze_panes = "A2"
    for i, field in enumerate(fields, 1):
        ws.column_dimensions[get_column_letter(i)].width = min(44, max(15, len(field) + 4))
    ws.append([_cell(ws, field, True) for field in fields])
    for row in rows:
        ws.append([_cell(ws, value) for value in row])


def _save(kind, tables):
    wb = Workbook(write_only=True)
    _sheet(wb, META, ("Format","Version"), [(kind, 1)])
    for (name, fields), rows in tables:
        _sheet(wb, name, fields, rows)
    out = io.BytesIO()
    wb.save(out)
    raw = out.getvalue()
    if len(raw) > MAX_FILE:
        raise ValueError("Workbook too large")
    return raw


def _read(raw, kind, specs):
    """Reject oversized archives, foreign sheets, formulas and unexpected cell types."""
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_FILE:
        raise ValueError("Invalid workbook size")
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            items = z.infolist()
            if len(items) > 100 or sum(i.file_size for i in items) > MAX_EXPANDED:
                raise ValueError("Workbook expansion limit")
            if any("externalLinks" in i.filename or "vbaProject" in i.filename for i in items):
                raise ValueError("External links or macros are not allowed")
        wb = load_workbook(io.BytesIO(raw), read_only=True, data_only=False, keep_links=False)
        try:
            expected = {META, *(name for name, _ in specs)}
            if set(wb.sheetnames) != expected:
                raise ValueError("Unexpected sheets")
            result = {}
            for name, fields in [(META, ("Format","Version")), *specs]:
                rows = []
                ws = wb[name]
                if ws.max_column is not None and ws.max_column > len(fields):
                    raise ValueError("Unexpected columns")
                # The worksheet dimension supplied by the file is not trusted.
                ws.reset_dimensions()
                limit = 362000 if name == OBS[0] else 31000 if name == PUPILS[0] else 4000
                for row in ws.iter_rows():
                    if len(rows) > limit or len(row) > len(fields):
                        raise ValueError("Worksheet limit")
                    if any(c.data_type in ("f", "e", "b", "d") for c in row):
                        raise ValueError("Unsupported cell or formula")
                    vals = tuple(c.value for c in row)
                    vals += (None,) * (len(fields) - len(vals))
                    if any(v is not None for v in vals):
                        rows.append(vals)
                if not rows or rows[0] != fields:
                    raise ValueError("Unexpected columns")
                result[name] = rows[1:]
            if result.pop(META) != [(kind, 1)]:
                raise ValueError("Unexpected backup type or version")
            return result
        finally:
            wb.close()
    except Exception as exc:
        raise ValueError("Invalid Excel backup") from exc


def _string(v):
    return "" if v is None else v


def formative_xlsx(current, history):
    current, history = fb.load_backup(fb.make_backup(current, history))
    lessons, criteria, pupils, observations = [], [], [], []
    items = ([("active", current)] if current is not None else []) + [
        ("archive", item) for item in history.values()
    ]
    for sid, (kind, item) in enumerate(items, 1):
        lessons.append((sid, kind, *item["context"]))
        criteria.extend((sid, *c) for c in item["criteria"])
        for code, values in item["records"].items():
            pupils.append((sid, code))
            observations.extend((sid, code, key, value) for key, value in values.items())
    return _save("formative", [(LESSONS, lessons), (CRITERIA, criteria), (PUPILS, pupils), (OBS, observations)])


def restore_formative_xlsx(raw):
    rows = _read(raw, "formative", [LESSONS, CRITERIA, PUPILS, OBS])
    items = {}
    active = None
    archive = []
    for sid, kind, activity, level, count, cycle, lesson, group in rows[LESSONS[0]]:
        if type(sid) is not int or sid < 1 or sid in items or kind not in ("active","archive"):
            raise ValueError("Invalid lesson key")
        item = {"context":[activity,level,count,cycle,lesson,_string(group)],"criteria":[],"records":{}}
        items[sid] = item
        if kind == "active":
            if active is not None:
                raise ValueError("Duplicate active lesson")
            active = item
        else:
            archive.append(item)
    try:
        for sid, key, dim, label in rows[CRITERIA[0]]:
            items[sid]["criteria"].append([key,dim,label])
        for sid, code in rows[PUPILS[0]]:
            records = items[sid]["records"]
            if code in records:
                raise ValueError("Duplicate pupil")
            records[code] = {}
        for sid, code, key, value in rows[OBS[0]]:
            obs = items[sid]["records"][code]
            if key in obs:
                raise ValueError("Duplicate observation")
            obs[key] = value
    except (KeyError, TypeError) as exc:
        raise ValueError("Unknown lesson or pupil") from exc
    return fb.load_backup(json.dumps({"version":1,"current":active,"history":archive},ensure_ascii=False).encode())


def _dict_rows(records, fields):
    return ([r[k] for k in fields] for r in records)


def _records(rows, fields, text_fields):
    return [{k: _string(v) if k in text_fields else v for k,v in zip(fields,row)} for row in rows]


def journal_xlsx(cycles, entries, slots, interruptions, projects):
    c,e,s,b,p = journal.restore_workspace(journal.workspace_backup(cycles,entries,slots,interruptions,projects))
    return _save("journal", [
        (CYCLES, [(x["number"],x["start"],x["end"],x["activities"][0]) for x in c]),
        (ENTRIES, _dict_rows(e,ENTRIES[1])), (SLOTS,_dict_rows(s,SLOTS[1])),
        (BREAKS,b), (PROJECTS,_dict_rows(p,PROJECTS[1]))])


def restore_journal_xlsx(raw):
    rows = _read(raw,"journal",[CYCLES,ENTRIES,SLOTS,BREAKS,PROJECTS])
    cycles = [{"number":n,"start":a,"end":b,"activities":[activity]} for n,a,b,activity in rows[CYCLES[0]]]
    entries = _records(rows[ENTRIES[0]],ENTRIES[1],set(ENTRIES[1])-{"cycle","lesson","duration"})
    slots = _records(rows[SLOTS[0]],SLOTS[1],{"group","level"})
    projects = _records(rows[PROJECTS[0]],PROJECTS[1],set(PROJECTS[1])-{"cycle"})
    payload = {"version":4,"cycles":cycles,"entries":entries,"slots":slots,
               "interruptions":rows[BREAKS[0]],"projects":projects}
    return journal.restore_workspace(json.dumps(payload,ensure_ascii=False).encode())


def projects_xlsx(projects, cycles):
    validated = curriculum.validate_projects(projects,cycles)
    return _save("projects",[(PROJECTS,_dict_rows(validated,PROJECTS[1]))])


def restore_projects_xlsx(raw, cycles):
    rows = _read(raw,"projects",[PROJECTS])
    projects = _records(rows[PROJECTS[0]],PROJECTS[1],set(PROJECTS[1])-{"cycle"})
    return curriculum.validate_projects(projects,cycles)


def report_xlsx(raw, *, delimiter=","):
    """Convert existing localized CSV reports into a real workbook, preserving text exactly."""
    wb = Workbook(write_only=True)
    reader = csv.reader(io.StringIO(raw.decode("utf-8-sig")),delimiter=delimiter)
    fields = next(reader, None)
    if not fields:
        raise ValueError("Empty report")
    _sheet(wb,"Export",fields,reader)
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()
