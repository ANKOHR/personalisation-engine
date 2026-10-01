"""Reports distinguish input provenance from measured fixture agreement."""
import json

def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"

def render(result, fmt):
    banner = "SYNTHETIC fixtures: invented inputs; no real prospect data." if result["synthetic"] else "REAL inputs: user-declared data entered by Henry; source truth is not independently verified."
    honesty = "Counts are computed from explicit inputs. Label agreement measures selection only. Outreach effectiveness, time saved and money saved are unmeasured; no estimates are reported."
    if fmt == "json":
        return encode({"provenance_banner": banner, "honesty": honesty, **result})
    lines = ["# Personalisation Engine report", "", banner, "", honesty, "", f"As of: {result['as_of']}", "", "## Computed counts", ""]
    lines.extend(f"- {k}: {v}" for k, v in result["counts"].items())
    lines.extend(["", "## Opening lines and provenance", ""])
    for row in result["rows"]:
        lines.append(f"- {row['id']}: {row['line'] or 'ABSTAIN: ' + row['reason']}")
        if row["evidence"]:
            lines.append(f"  Source: {row['evidence']['source']}; date: {row['evidence']['date']}; kind: {row['evidence']['kind']}")
    return "\n".join(lines) + "\n"
