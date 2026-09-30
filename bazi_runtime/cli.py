from __future__ import annotations
import argparse,json,sys
from .protocol import analyze_v1

def main(argv=None):
    ap=argparse.ArgumentParser(prog="bazi-runtime")
    ap.add_argument("--input","-i",help="JSON input file; stdin if omitted")
    ap.add_argument("--pretty",action="store_true")
    ns=ap.parse_args(argv)
    try:
        if ns.input:
            with open(ns.input, encoding="utf-8") as handle:
                data = json.load(handle)
        else:
            data = json.load(sys.stdin)
        out = analyze_v1(data)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        ap.error(str(exc))
    print(json.dumps(out,ensure_ascii=False,indent=2 if ns.pretty else None))
if __name__=="__main__": main()
