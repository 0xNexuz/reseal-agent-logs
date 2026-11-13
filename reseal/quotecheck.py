"""Check that every coded quote appears in the saved documentation snapshot.

Sprint work (13 Nov 2026 onward).

    python -m reseal.quotecheck claims/claims_coder1.csv
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

SNAP = Path(__file__).resolve().parent.parent / "claims" / "snapshots"

# (tool, source column) -> snapshot file
SOURCES = {
    ("halo-record", "README.md"): "halo_record.README.md",
    ("halo-record", "LIMITS.md"): "halo_record.LIMITS.md",
    ("witnesskit", "README.md"): "witnesskit.README.md",
    ("witnesskit", "SECURITY.md"): "witnesskit.SECURITY.md",
    ("signet", "README.md"): "signet.repo.README.md",
    ("signet", "docs/SECURITY.md"): "signet.SECURITY.md",
    ("agent-receipts", "README.md"): "obsigna.README.md",
}


def norm(text: str) -> str:
    """Drop markdown marks and collapse whitespace, so only the words count."""
    text = text.replace("—", "-").replace("–", "-")
    text = re.sub(r"[*`]", "", text).replace("|", " ")
    return re.sub(r"\s+", " ", text).strip().lower()


def check(path) -> list[tuple[str, str, str]]:
    """Return (tool, source, quote) for every quote not found in its snapshot."""
    missing = []
    cache: dict[str, str] = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["quote"].startswith("[paraphrase"):
                continue  # the unnamed tool: quotes are withheld on purpose
            name = SOURCES.get((r["tool"], r["source"]))
            if name is None or not (SNAP / name).exists():
                missing.append((r["tool"], r["source"], "no snapshot: " + r["quote"]))
                continue
            if name not in cache:
                cache[name] = norm((SNAP / name).read_text(encoding="utf-8"))
            # a quote may join two table cells or two phrases with ':' or '|'
            parts = [p for p in re.split(r"\s*[:|]\s+", r["quote"]) if p.strip()]
            if not all(norm(p) in cache[name] for p in parts):
                missing.append((r["tool"], r["source"], r["quote"]))
    return missing


def main(argv=None):
    paths = (argv or sys.argv[1:]) or ["claims/claims_coder1.csv"]
    bad = 0
    for p in paths:
        miss = check(p)
        bad += len(miss)
        for tool, source, quote in miss:
            print(f"NOT FOUND  {p}  {tool}  {source}: {quote}")
        print(f"{p}: {len(miss)} quote(s) not found")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
