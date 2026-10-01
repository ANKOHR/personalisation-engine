# Personalisation Engine

A CPU-only, offline Python CLI that creates prospect-specific opening lines by quoting supplied evidence. It does not call language models or access the network. Hypothesis: explicit facts, deterministic selection and named abstentions make opening lines auditable.

## Quickstart

Python 3.10 or later, setuptools and pytest available locally:

```powershell
python -m pip install --no-build-isolation --no-deps -e .
pe fixtures --out demo
pe run --input demo
pe report --format md
python -m pytest -q
```

On Windows, if pip reports that its Scripts directory is not on PATH, add that reported directory to the current shell PATH or use `python -m personalisation_engine.cli` in place of `pe`. The installed pe entry point was tested directly.

The demo produces 200 labelled synthetic prospects, 120 lines and 80 abstentions. These counts describe fixtures, not market demand or outreach effectiveness. `demo/tiny/input.json` is the five-record version with the same three eligible and two abstention cases.

## Input reference

A directory contains `input.json`. JSON is the only supported input format. Other formats require manual conversion, and a nonempty directory without input.json produces MissingInput. An empty directory is accepted as zero real user-declared records with an explicit placeholder as_of of 1970-01-01.

```json
{
  "synthetic": false,
  "as_of": "2026-09-30",
  "records": [{
    "id": "prospect-1",
    "company": "Example Ltd",
    "signals": [{
      "kind": "hiring",
      "fact": "Posted a platform engineer vacancy",
      "source": "C:\\Users\\Henry\\notes.md",
      "date": "2026-09-29"
    }]
  }]
}
```

Henry enters real data by hand and declares synthetic false. Sources can be URLs, paths or manual note references; they are never fetched or independently verified. `as_of` is the user-supplied evaluation date, never the system clock. Optional `description` is text. Optional record `expected_eligible` is a hand-checked boolean used only for evaluation, never generation.

Records require unique nonempty ids and company names (maximum 200 characters), plus a signals array. Signals require kind launch, hiring or research, fact (maximum 10,000 characters), source (maximum 2,000) and ISO date no later than as_of. Unknown fields, negative amounts (amount fields are unsupported), duplicate ids, future dates, control characters, em dash characters and excessive strings are rejected with SchemaError. Unicode and Windows paths are supported through UTF-8 and JSON escaping. Duplicate JSON keys are rejected. Malformed JSON reports file and line; semantic duplicate-key errors report line 1 as the parser has no positional metadata for them.

Selection excludes facts equal to great company, innovative company or industry leader (case-insensitive) and sources equal to unknown. Missing or generic evidence yields `no_specific_sourced_fact`. Remaining candidates sort by date, kind, fact and source, selecting the last. This quotes a fact without inventing an inferred benefit or relationship. It cannot recognise every generic claim, verify facts, or guarantee a reader will find a line compelling. Missing required fields are errors rather than abstentions.

## Commands

```powershell
pe fixtures --out demo
pe validate --input demo
pe preview --input demo/tiny
pe run --input demo --result .pe/results.json
pe report --format md --out report.md
pe report --format json --result .pe/results.json
```

Each subcommand includes help and an example. `run` persists computed rows; `report` renders that snapshot, so rerun after changing inputs. `preview` computes without persistence. Output files are replaced atomically. WriteError leaves no partial destination file and preserves an existing destination. No database is required.

## Architecture

```text
input.json -> CLI parse + schema validation -> pure core selection
                                               -> computed counts + rows
                                               -> .pe/results.json
                                               -> Markdown / JSON report
fixtures.py -> labelled input + independent expectations.json
```

## Honesty boundary

All counts derive from supplied records. Reports show a provenance banner: synthetic fixtures or real inputs declared by Henry. Real input claims are unverified. Selection agreement against supplied labels is measured; the quality, truth and commercial impact of lines are unmeasured. Time saved and money saved are unmeasured and no estimates are reported. No hypothetical savings feature exists. Fixture agreement is not proof of real-world accuracy.

Synthetic JSON carries `synthetic: true` and a SYNTHETIC description because JSON does not allow header comments. The fixture Markdown file has a synthetic header comment. All fixture prospects and events are invented, using example.invalid sources. Generation has no randomness and therefore no seed. Identical inputs yield byte-identical result files and reports; no wall-clock times appear in outputs.

## Acceptance and evidence

Tests check the independent hand count: 40 repetitions of three eligible facts, one generic fact and one empty evidence list. Therefore 200 records, 120 generated lines, 80 abstentions, 120 true positives, 80 true negatives and zero false positives or negatives. Tests mutate both evidence and labels to demonstrate that counts are computed. The timed fixture workflow must finish in less than five seconds. See BUILD-DONE.txt and EVIDENCE.md for local measured results.

Named failures: ParseError includes file and line; MissingInput gives a usage hint; SchemaError includes offending field and file; WriteError identifies the destination with temporary file cleanup. Commands return exit code 2 for named failures. Local filenames and source facts may contain Markdown syntax; JSON is the canonical structured report for automated consumption.

## Two-week improvement hook and verdict

The evidence window starts on the first real-use day, which has not been recorded. Henry should keep trial data privately, not commit it. Hand-check at least 20 generated lines after two weeks and record incorrect or irrelevant lines divided by checked lines, plus days used. No measured real-use rate exists yet. If error exceeds 10 percent, fix the leading documented failure cause and repeat the sample, or kill with the reason. If never used, kill.

Verdict is pending the evidence window, not falsely recorded as complete. Record date, sample size, errors, days used, revenue or buyer evidence, action and reason in VERDICT.md. Expand if daily use or revenue supports it; integrate if overlap with a sibling is substantial; commercialise if a buyer would pay as-is; maintain as portfolio evidence otherwise; kill if unused or unable to meet acceptance criteria. Publishing is a separate authorised verification step and is not performed by this build.
