
import sys, argparse
from .parser import to_json, parse_facet
from .errors import FACETError

def cmd_to_json(args):
    with open(args.file, "r", encoding="utf-8") as f:
        txt = f.read()
    print(to_json(txt))

def cmd_lint(args):
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            txt = f.read()
        parse_facet(txt)
        print(f"OK: {args.file}")
    except FACETError as e:
        print(f"ERROR {e.code}: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    ap = argparse.ArgumentParser(prog="facet", description="FACET reference CLI (minimal)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("to-json", help="Convert FACET to canonical JSON")
    p1.add_argument("file"); p1.set_defaults(func=cmd_to_json)

    p2 = sub.add_parser("lint", help="Lint FACET file (basic checks)")
    p2.add_argument("file"); p2.set_defaults(func=cmd_lint)

    args = ap.parse_args(); args.func(args)

if __name__ == "__main__":
    main()
