"""Synthetic fixtures, no randomness. Expectations are hand-counted constants."""
import json
from pathlib import Path

def fixture(count=200):
    records = []
    for i in range(count):
        group = i % 5
        signals = [] if group == 4 else [{"kind": ("launch", "hiring", "research", "launch")[group], "fact": "great company" if group == 3 else f"Project {i:03d} published a technical update", "source": f"https://example.invalid/prospect/{i:03d}", "date": "2026-09-01"}]
        records.append({"id": f"p{i:03d}", "company": f"Synthetic Prospect {i:03d}", "signals": signals, "expected_eligible": group < 3})
    return {"synthetic": True, "description": "SYNTHETIC fixture. All prospects and events are invented.", "as_of": "2026-09-30", "records": records}

def generate(out, writer):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    writer(out / "input.json", fixture())
    writer(out / "expectations.json", {"synthetic": True, "description": "SYNTHETIC hand-computed ground truth: 40 cycles of 3 eligible and 2 abstentions.", "counts": {"records": 200, "generated": 120, "abstained": 80, "labelled": 200, "true_positives": 120, "false_positives": 0, "true_negatives": 80, "false_negatives": 0}})
    writer(out / "tiny" / "input.json", fixture(5))
    writer(out / "SYNTHETIC.md", "<!-- SYNTHETIC fixture -->\nAll JSON files declare synthetic: true. JSON does not permit header comments.\n")
