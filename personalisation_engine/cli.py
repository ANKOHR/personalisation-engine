"""Local-only command line interface with atomic output writes."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from .core import SchemaError, run, validate
from .fixtures import generate
from .report import encode, render

class InputError(ValueError):
    pass

def write(path, value):
    path = Path(path)
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as stream:
            temporary = stream.name
            stream.write(value if isinstance(value, str) else encode(value))
        os.replace(temporary, path)
    except OSError as exc:
        raise InputError(f"WriteError: {path}: {exc}") from exc
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)

def read(path):
    path = Path(path)
    try:
        def pairs(items):
            obj = {}
            for key, value in items:
                if key in obj:
                    raise ValueError(f"duplicate JSON key {key}")
                obj[key] = value
            return obj
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)
    except json.JSONDecodeError as exc:
        raise InputError(f"ParseError: {path}: line {exc.lineno}: {exc.msg}") from exc
    except (UnicodeError, ValueError) as exc:
        raise InputError(f"ParseError: {path}: line 1: {exc}") from exc
    except OSError as exc:
        raise InputError(f"MissingInput: {path}: {exc}. Use pe fixtures --out demo or supply input.json.") from exc

def load(directory):
    directory = Path(directory)
    if not directory.is_dir():
        raise InputError(f"MissingInput: {directory}: expected directory. Use pe fixtures --out demo.")
    path = directory / "input.json"
    if not any(directory.iterdir()):
        return {"synthetic": False, "as_of": "1970-01-01", "records": []}
    data = read(path)
    try:
        return validate(data)
    except SchemaError as exc:
        raise SchemaError(f"{path}: {exc}") from exc

def parser():
    p = argparse.ArgumentParser(description="Create opening lines from supplied evidence, without network access.")
    sub = p.add_subparsers(dest="command", required=True)
    f = sub.add_parser("fixtures", help="Generate labelled synthetic data", epilog="Example: pe fixtures --out demo")
    f.add_argument("--out", required=True)
    for name, helptext in [("run", "Compute and persist opening lines"), ("validate", "Validate prospect schema and evidence dates"), ("preview", "Preview opening lines with cited evidence")]:
        s = sub.add_parser(name, help=helptext, description=helptext, epilog=f"Example: pe {name} --input demo")
        s.add_argument("--input", required=True)
        if name == "run":
            s.add_argument("--result", default=".pe/results.json")
    r = sub.add_parser("report", help="Render computed results with provenance", epilog="Example: pe report --format md")
    r.add_argument("--format", choices=("md", "json"), default="md")
    r.add_argument("--result", default=".pe/results.json")
    r.add_argument("--out")
    return p

def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "fixtures":
            generate(args.out, write)
            print(f"SYNTHETIC: 200 labelled records written to {args.out}; tiny/input.json contains 5 records.")
        elif args.command in ("run", "validate", "preview"):
            data = load(args.input)
            result = run(data)
            if args.command == "run":
                write(args.result, result)
                print(f"{'SYNTHETIC' if data['synthetic'] else 'REAL user-declared'} inputs: {result['counts']['records']} records; {result['counts']['generated']} opening lines. Results: {args.result}")
            elif args.command == "validate":
                print(f"{'SYNTHETIC' if data['synthetic'] else 'REAL user-declared'}: schema valid; {len(data['records'])} records. Source truth unverified.")
            else:
                print(render(result, "md"), end="")
        else:
            result = read(args.result)
            try:
                output = render(result, args.format)
            except (KeyError, TypeError, AttributeError) as exc:
                raise SchemaError(f"{args.result}: results schema invalid: {exc}") from exc
            if args.out:
                write(args.out, output)
            else:
                print(output, end="")
        return 0
    except (InputError, SchemaError) as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
