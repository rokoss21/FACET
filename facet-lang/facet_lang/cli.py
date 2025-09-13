from __future__ import annotations
import argparse, sys, json
from .canon import canonize
from .errors import FacetError


def main(argv=None):
    p = argparse.ArgumentParser("facet")
    sub = p.add_subparsers(dest="cmd", required=True)
    pc = sub.add_parser("canon")
    pc.add_argument("input", help=".facet file path or - for stdin")
    pc.add_argument("--resolve", choices=["host","all"], default="host")
    pc.add_argument("--var", action="append", default=[], help="k=v host var")
    pc.add_argument("--import-root", action="append", default=[], help="allow import root")
    pc.add_argument("--strict-merge", action="store_true")

    pl = sub.add_parser("lint")
    pl.add_argument("input", help=".facet file path or - for stdin")
    pl.add_argument("--import-root", action="append", default=[], help="allow import root")

    args = p.parse_args(argv)

    if args.cmd in ("canon","lint"):
        if args.input == "-":
            text = sys.stdin.read()
        else:
            text = open(args.input, "r", encoding="utf-8").read()
        host_vars = {}
        for kv in getattr(args, 'var', []) or []:
            if "=" not in kv:
                print(f"--var expects k=v, got: {kv}", file=sys.stderr)
                return 2
            k, v = kv.split("=", 1)
            host_vars[k] = v
        try:
            out = canonize(text, host_vars=host_vars, resolve_mode=getattr(args,'resolve','host'),
                           import_roots=getattr(args,'import_root',[]), strict_merge=getattr(args,'strict_merge',False))
            if args.cmd == "canon":
                print(json.dumps(out, ensure_ascii=False, indent=2))
            else:
                print("OK")
        except FacetError as e:
            print(str(e), file=sys.stderr)
            return 1

if __name__ == "__main__":
    raise SystemExit(main())
