"""Command line: ``python -m reseal run`` / ``python -m reseal report``."""

from __future__ import annotations

import argparse

from . import adapters, report, runner


def main(argv=None):
    p = argparse.ArgumentParser(prog="reseal", description="Adversarial tests for AI-agent audit logs")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="run the attack matrix")
    r.add_argument("--tools", nargs="*", default=None, help=f"default: all ({[c.name for c in adapters.ALL]})")
    r.add_argument("--n", type=int, default=200, help="events per log")
    r.add_argument("--seeds", type=int, nargs="*", default=[0])
    r.add_argument("--setups", nargs="*", default=["default", "strong"])
    r.add_argument("--out", default="results/run")
    r.add_argument("--keep", action="store_true", help="keep tampered logs on disk")

    s = sub.add_parser("report", help="write SUMMARY.md and summary.json for a finished run")
    s.add_argument("--out", default="results/run")

    sub.add_parser("tools", help="list tools and their installed versions")

    a = p.parse_args(argv)
    if a.cmd == "run":
        runner.run_matrix(tools=a.tools, seeds=tuple(a.seeds), n=a.n, setups=tuple(a.setups),
                          out_dir=a.out, keep=a.keep)
        print("wrote", report.write(a.out))
    elif a.cmd == "report":
        print("wrote", report.write(a.out))
    else:
        for cls in adapters.ALL:
            print(f"{cls.name:16s} {runner._version(cls()):10s} signed={cls.signed}")


if __name__ == "__main__":
    main()
