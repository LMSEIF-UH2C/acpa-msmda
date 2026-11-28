"""Read-only compatibility bridge to the cumulative observation model.

A legacy catalogue row is a source record, not an adjudicated product.
No new sources, identity inference, scores, or recommendations are produced.
"""
from __future__ import annotations

from datetime import date
import hashlib
import json
from pathlib import Path


def _decode(raw: bytes) -> list[dict]:
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict) or data.get("dataset_type") != "REAL_TOOLS_UNSCORED":
        raise ValueError("Catalogue incompatible")
    items = data.get("tools", [])
    if not isinstance(items, list):
        raise ValueError("Identifiants invalides")
    if any(not isinstance(t, dict) or not isinstance(t.get("id"), str)
           or not t["id"].strip() for t in items):
        raise ValueError("Identifiants invalides")
    if len({t["id"] for t in items}) != len(items):
        raise ValueError("Identifiants invalides")
    return items


def load_legacy_rows(path) -> list[dict]:
    """Return the original legacy dictionaries without modifying any field."""
    return _decode(Path(path).read_bytes())


def _canonical_digest(row: dict) -> str:
    # Hash the canonical decoded object; not a hash of a raw API response.
    return hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False,
                                      separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def catalogue_snapshot(path, *, observed_on: str) -> dict:
    """Produce a metadata-only graph projection of an observed legacy snapshot.

    The date refers to the observation of the local catalogue, never inferred
    as a product release or original acquisition date. A repeated identical
    observation on the same day has the same key; different dates or payloads
    are preserved independently. The entire input is read once.
    """
    if not isinstance(observed_on, str):
        raise ValueError("Observation date required")
    try:
        if date.fromisoformat(observed_on).isoformat() != observed_on:
            raise ValueError("Noncanonical date")
    except ValueError as exc:
        raise ValueError("Observation date must be YYYY-MM-DD") from exc
    raw = Path(path).read_bytes()
    rows = _decode(raw)
    snapshot_sha = hashlib.sha256(raw).hexdigest()
    locator = "data/real_tools_catalog.json"
    records, observations = {}, {}
    for row in rows:
        native = row["id"]
        key = "catalog:" + native
        payload_sha = _canonical_digest(row)
        observation = f"obs:{key}:{observed_on}:{snapshot_sha}:{payload_sha}"
        records[key] = {"source": "catalog", "source_id": native,
                        "kind_hint": "unknown"}
        observations[observation] = {"record": key, "date": observed_on,
                                     "locator": locator + "#sha256=" + snapshot_sha,
                                     "payload_sha256": payload_sha}
    return {
        "schema_version": 1,
        "snapshot": {"sha256": snapshot_sha, "bytes": len(raw),
                     "observed_on": observed_on,
                     "payload_hash_kind": "canonical_legacy_row_json",
                     "record_count": len(rows)},
        "sources": {"catalog": {"kind": "local_snapshot", "locator": locator}},
        "records": records,
        "observations": observations,
        "entities": {},
        "evidence": {},
        "assertions": {},
    }
