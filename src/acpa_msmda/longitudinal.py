"""Validated, portable long-format observations. No names or implicit imputation."""
from __future__ import annotations

import csv
import io
import math
import re
from datetime import date

FIELDS = ("participant", "group", "instrument", "unit", "occasion", "date", "protocol", "value")
MAX_ROWS = 30000
MAX_BYTES = 4_000_000
CODE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,39}$")


def parse_long_csv(data: bytes, registry: dict, delimiter: str = ";") -> list[dict]:
    """Strict UTF-8 CSV; blank value means missing, never zero. Reject entire invalid import."""
    if delimiter not in (";", ",") or len(data) > MAX_BYTES:
        raise ValueError("Invalid delimiter or file size")
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig")), delimiter=delimiter)
    if tuple(reader.fieldnames or ()) != FIELDS:
        raise ValueError("Expected columns: " + delimiter.join(FIELDS))
    rows, keys, groups = [], set(), {}
    for line, row in enumerate(reader, 2):
        if len(rows) >= MAX_ROWS or None in row or any(v is None for v in row.values()):
            raise ValueError(f"Invalid row or row limit: {line}")
        row = {k: v.strip() for k, v in row.items()}
        for field in ("participant", "group", "occasion", "protocol"):
            if not CODE.fullmatch(row[field]):
                raise ValueError(f"Invalid coded field {field}: {line}")
        test = registry.get(row["instrument"])
        if test is None or row["unit"] != test["unit"]:
            raise ValueError(f"Unknown instrument or incompatible unit: {line}")
        try:
            if date.fromisoformat(row["date"]).isoformat() != row["date"]:
                raise ValueError()
            value = None if row["value"] == "" else float(row["value"].replace(",", "."))
            if value is not None and (not math.isfinite(value) or (value < 0 and not test.get("signed"))):
                raise ValueError()
        except ValueError:
            raise ValueError(f"Invalid date or measurement: {line}") from None
        key = (row["participant"], row["instrument"], row["protocol"], row["occasion"])
        if key in keys:
            raise ValueError(f"Duplicate observation: {line}")
        if row["participant"] in groups and groups[row["participant"]] != row["group"]:
            raise ValueError(f"Inconsistent participant group: {line}")
        keys.add(key)
        groups[row["participant"]] = row["group"]
        row["value"] = value
        rows.append(row)
    if not rows:
        raise ValueError("No observations")
    return rows


def export_long_csv(rows: list[dict]) -> bytes:
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter=";", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8-sig")


def paired_panel(rows: list[dict], instrument: str, protocol: str, occasions: list[str], group: str | None = None) -> dict:
    """Explicit complete-case panel; pairing by participant, not row order."""
    if len(occasions) < 2 or len(set(occasions)) != len(occasions):
        raise ValueError("Select distinct occasions")
    panel, dates = {}, {}
    for row in rows:
        if row["instrument"] != instrument or row["protocol"] != protocol or (group is not None and row["group"] != group):
            continue
        if row["occasion"] not in occasions:
            continue
        person = row["participant"]
        values = panel.setdefault(person, {})
        if row["occasion"] in values:
            raise ValueError("Duplicate observation")
        values[row["occasion"]] = row["value"]
        dates.setdefault(person, {})[row["occasion"]] = row["date"]
    complete = {}
    for person, values in sorted(panel.items()):
        if all(values.get(o) is not None for o in occasions):
            ordered_dates = [dates[person][o] for o in occasions]
            if any(a >= b for a, b in zip(ordered_dates, ordered_dates[1:])):
                raise ValueError("Selected occasions must be chronologically ordered")
            complete[person] = [values[o] for o in occasions]
    return {"occasions": occasions, "participants": list(complete), "values": list(complete.values()),
            "n_total": len(panel), "n_complete": len(complete), "n_excluded": len(panel)-len(complete)}


def group_summary(rows: list[dict], instrument: str, protocol: str, occasions: list[str]) -> list[dict]:
    """Descriptive means on complete participants, separately for each fixed group."""
    from statistics import mean, stdev
    groups = sorted({r["group"] for r in rows if r["instrument"] == instrument and r["protocol"] == protocol})
    result = []
    for group in groups:
        panel = paired_panel(rows, instrument, protocol, occasions, group)
        for j, occasion in enumerate(occasions):
            values = [v[j] for v in panel["values"]]
            result.append({"group": group, "occasion": occasion, "n": len(values),
                           "n_total": panel["n_total"], "n_excluded": panel["n_excluded"],
                           "mean": mean(values) if values else None,
                           "sd": stdev(values) if len(values) > 1 else None})
    return result


def parse_long_xlsx(data: bytes, registry: dict) -> list[dict]:
    """Read the first sheet of an XLSX workbook, values only, with the CSV schema."""
    import zipfile
    import xml.etree.ElementTree as ET
    if len(data) > MAX_BYTES:
        raise ValueError("Workbook too large")
    ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            infos = z.infolist()
            if len(infos)>500 or sum(i.file_size for i in infos)>32_000_000:
                raise ValueError("Workbook expansion limit")
            # Reject complex workbooks instead of silently choosing a different sheet.
            book = ET.fromstring(z.read("xl/workbook.xml"))
            sheets = book.findall("s:sheets/s:sheet", ns)
            if len(sheets) != 1:
                raise ValueError("Workbook must contain one sheet")
            rel = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
            rid = sheets[0].get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
            target = next(r.get("Target") for r in rel if r.get("Id")==rid)
            path = target.lstrip("/") if target.startswith("/") else "xl/"+target
            if not re.fullmatch(r"xl/worksheets/sheet[0-9]+\.xml", path):
                raise ValueError("Unsupported sheet path")
            strings = []
            if "xl/sharedStrings.xml" in z.namelist():
                root = ET.fromstring(z.read("xl/sharedStrings.xml"))
                strings = ["".join(t.text or "" for t in si.findall(".//s:t", ns)) for si in root.findall("s:si", ns)]
            root = ET.fromstring(z.read(path))
            output = io.StringIO()
            writer = csv.writer(output, delimiter=";")
            for index, row in enumerate(root.findall("s:sheetData/s:row", ns)):
                if index > MAX_ROWS:
                    raise ValueError("Row limit")
                values = [""] * len(FIELDS)
                used = set()
                for c in row.findall("s:c", ns):
                    ref = c.get("r","")
                    m = re.fullmatch(r"([A-Z])([1-9][0-9]*)", ref)
                    if not m or c.find("s:f", ns) is not None:
                        raise ValueError("Unsupported cell or formula")
                    col = ord(m.group(1))-65
                    if col >= len(FIELDS) or col in used:
                        raise ValueError("Unexpected column")
                    used.add(col)
                    typ = c.get("t","n")
                    v = c.findtext("s:v", default="", namespaces=ns)
                    if typ == "s":
                        pos = int(v)
                        if pos < 0:
                            raise ValueError("Invalid shared string")
                        v = strings[pos]
                    elif typ == "inlineStr":
                        v = "".join(t.text or "" for t in c.findall(".//s:t",ns))
                    elif typ not in ("n","str","d"):
                        raise ValueError("Unsupported cell type")
                    # Excel serial dates are intentionally not guessed. Use ISO text.
                    values[col] = v
                if any(values):
                    writer.writerow(values)
            return parse_long_csv(output.getvalue().encode(), registry)
    except (zipfile.BadZipFile, KeyError, IndexError, StopIteration, ET.ParseError, OSError, RuntimeError) as exc:
        raise ValueError("Invalid or unsupported XLSX") from exc


def multivariable_panel(rows: list[dict], variables: list[tuple[str,str,str]], group: str) -> dict:
    """Join explicit (instrument, protocol, occasion) selections by participant.
    Eligible denominator is the union of participants observed for selected variables.
    One group only; no imputation and no implicit aggregation.
    """
    if not group or len(variables)<2 or len(set(variables))!=len(variables):
        raise ValueError("Select distinct variables and one group")
    selected=set(variables)
    panel={}
    for row in rows:
        key=(row["instrument"],row["protocol"],row["occasion"])
        if row["group"]!=group or key not in selected:
            continue
        person=panel.setdefault(row["participant"],{})
        if key in person:
            raise ValueError("Duplicate observation")
        person[key]=row["value"]
    complete={p:[v[k] for k in variables] for p,v in sorted(panel.items())
              if all(v.get(k) is not None for k in variables)}
    return {"participants":list(complete),"values":list(complete.values()),
            "n_total":len(panel),"n_complete":len(complete),"n_excluded":len(panel)-len(complete)}
