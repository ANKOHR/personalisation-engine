"""Pure validation and selection. No inference or hypothetical savings."""
from datetime import date
import re

class SchemaError(ValueError):
    """An input field violates the documented schema."""

KINDS = ("launch", "hiring", "research")
GENERIC = {"great company", "innovative company", "industry leader"}

def fail(field, message):
    raise SchemaError(f"{field}: {message}")

def fields(obj, allowed, required, field):
    if not isinstance(obj, dict):
        fail(field, "must be an object")
    for key in sorted(set(obj) - set(allowed)):
        fail(f"{field}.{key}", "unknown field")
    for key in required:
        if key not in obj:
            fail(f"{field}.{key}", "required field missing")

def string(value, field, limit=10000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        fail(field, f"must be nonempty text of at most {limit} characters")
    if any(ord(c) < 32 for c in value) or chr(8212) in value:
        fail(field, "control characters and em dash characters are forbidden")
    return value

def day(value, field):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        fail(field, "must be an ISO date YYYY-MM-DD")

def validate(data):
    fields(data, ("synthetic", "as_of", "records", "description"), ("synthetic", "as_of", "records"), "input")
    if type(data["synthetic"]) is not bool:
        fail("synthetic", "must be boolean")
    cutoff = day(data["as_of"], "as_of")
    if "description" in data:
        string(data["description"], "description")
    if not isinstance(data["records"], list):
        fail("records", "must be an array")
    seen = set()
    for i, record in enumerate(data["records"]):
        prefix = f"records[{i}]"
        fields(record, ("id", "company", "signals", "expected_eligible"), ("id", "company", "signals"), prefix)
        for key in ("id", "company"):
            string(record[key], f"{prefix}.{key}", 200)
        if record["id"] in seen:
            fail(f"{prefix}.id", "duplicate id")
        seen.add(record["id"])
        if "expected_eligible" in record and type(record["expected_eligible"]) is not bool:
            fail(f"{prefix}.expected_eligible", "must be boolean")
        if not isinstance(record["signals"], list):
            fail(f"{prefix}.signals", "must be an array")
        for j, signal in enumerate(record["signals"]):
            sp = f"{prefix}.signals[{j}]"
            fields(signal, ("kind", "fact", "source", "date"), ("kind", "fact", "source", "date"), sp)
            if signal["kind"] not in KINDS:
                fail(f"{sp}.kind", "must be launch, hiring, or research")
            string(signal["fact"], f"{sp}.fact")
            string(signal["source"], f"{sp}.source", 2000)
            if day(signal["date"], f"{sp}.date") > cutoff:
                fail(f"{sp}.date", "future date relative to as_of")
    return data

def opening(record):
    candidates = [s for s in record["signals"] if s["fact"].strip().casefold() not in GENERIC and s["source"].strip().casefold() != "unknown"]
    if not candidates:
        return {"id": record["id"], "company": record["company"], "eligible": False, "line": None, "evidence": None, "reason": "no_specific_sourced_fact"}
    signal = sorted(candidates, key=lambda s: (s["date"], s["kind"], s["fact"], s["source"]))[-1]
    return {"id": record["id"], "company": record["company"], "eligible": True,
            "line": f'I noticed {record["company"]} reported "{signal["fact"]}".',
            "evidence": dict(signal), "reason": "explicit_sourced_fact"}

def run(data):
    validate(data)
    rows = [opening(r) for r in sorted(data["records"], key=lambda r: r["id"])]
    labels = {r["id"]: r["expected_eligible"] for r in data["records"] if "expected_eligible" in r}
    counts = {"records": len(rows), "generated": sum(r["eligible"] for r in rows), "abstained": sum(not r["eligible"] for r in rows), "labelled": len(labels), "true_positives": 0, "false_positives": 0, "true_negatives": 0, "false_negatives": 0}
    for r in rows:
        if r["id"] in labels:
            key = ("true_" if r["eligible"] == labels[r["id"]] else "false_") + ("positives" if r["eligible"] else "negatives")
            counts[key] += 1
    return {"synthetic": data["synthetic"], "as_of": data["as_of"], "counts": counts, "rows": rows}
