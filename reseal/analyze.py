"""Join results with coded claims: labels, Claims Cards and the main figure.

Sprint work (13 Nov 2026 onward).

    python -m reseal.analyze --out results/main --claims claims/claims_coder1.csv
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from .report import load

# property -> (attack ids, attacker tier, positions used or None for all)
INTERIOR = ("first", "middle", "penultimate")
PROPERTIES = [
    ("edit", ("A1", "A2"), "T1", None, "change a record"),
    ("delete", ("A3",), "T1", INTERIOR, "remove a record that is not the last"),
    ("truncate", ("A4", "A3"), "T1", ("-", "final"), "drop records from the end"),
    ("reorder", ("A5",), "T1", None, "swap two records"),
    ("insert", ("A6", "A7"), "T1", None, "add a forged or duplicate record"),
    ("backdate", ("A8",), "T1", None, "change a record's time"),
    ("downgrade", ("A10",), "T1", None, "strip signature or integrity fields"),
    ("forge", ("A11",), "T1+", None, "rebuild the log without the original keys"),
    ("rewrite", ("A12",), "T2", None, "operator rebuilds the log with the real keys"),
    ("fork", ("A13",), "T3", None, "operator shows a different history"),
    ("capture", ("A14",), "boundary", None, "action never reached the recorder"),
]

# Does ReSeal's strong setup switch on the setup a "claims_with_setup" row names?
# Signet's docs name an expected record count for truncation; its verifier has no
# such option, so the strong setup (a pinned key) does not provide it.
SETUP_NOT_WIRED = {("signet", "truncate")}

def public(tool: str) -> str:
    """The fifth tool is recorded as ``tool-e`` at the source; nothing to map."""
    return tool


def load_claims(path) -> dict:
    """(tool, property) -> list of claim rows."""
    by = defaultdict(list)
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            by[(r["tool"], r["property"])].append(r)
    return by


def claim_for(claims, tool, prop, tier):
    """Pick the claim that governs one tool x property x tier.

    A row for the exact tier wins over an 'any' row; a general slogan is used
    only when nothing more specific exists.
    """
    rows = claims.get((tool, prop), [])
    exact = [r for r in rows if r["tier"] == tier]
    anyt = [r for r in rows if r["tier"] == "any" and "general slogan" not in r["notes"]]
    slogan = [r for r in rows if r["tier"] == "any" and "general slogan" in r["notes"]]
    for group, kind in ((exact, "specific"), (anyt, "specific"), (slogan, "slogan")):
        if group:
            order = {"disclaims": 0, "claims_with_setup": 1, "claims": 2}
            # the most cautious statement governs
            r = sorted(group, key=lambda x: order[x["strength"]])[0]
            return r["strength"], kind, r
    return "silent", "none", None


def outcome(rows) -> tuple[str, int, int]:
    rows = [r for r in rows if r["applicable"]]
    if not rows:
        return "n/a", 0, 0
    d = sum(r["detected"] for r in rows)
    if d == len(rows):
        return "caught", d, len(rows)
    if d == 0:
        return "missed", d, len(rows)
    return "partial", d, len(rows)


def label(strength, kind, setup, out, wired=True) -> str:
    if out == "n/a":
        return "not applicable"
    caught = out == "caught"
    if strength == "claims" and kind == "slogan":
        return "holds (headline only)" if caught else "headline not met"
    if strength == "claims":
        return "holds" if caught else "claim not met"
    if strength == "claims_with_setup":
        if setup == "default":
            return "holds without the setup" if caught else "needs setup (disclosed)"
        if not wired:
            return "holds without the setup" if caught else "setup left to the user (disclosed)"
        return "holds with setup" if caught else "claim not met"
    if strength == "disclaims":
        return "better than stated" if caught else "disclosed limit"
    return "caught (unstated)" if caught else "silent miss"



# -- sensitivity: a stricter reading of the documentation ----------------------
#
# The main labels let a specific statement govern over a headline, and count
# deletion of the last record as truncation (a tool that says "truncation needs
# an expected head" has disclosed it). The strict reading does neither: any
# unconditional "claims" statement about a property governs, and deleting the
# last record is a deletion.
STRICT_PROPERTIES = [
    ("edit", ("A1", "A2"), None), ("delete", ("A3",), None), ("truncate", ("A4",), None),
    ("reorder", ("A5",), None), ("insert", ("A6", "A7"), None), ("backdate", ("A8",), None),
    ("downgrade", ("A10",), None), ("forge", ("A11",), None), ("rewrite", ("A12",), None),
    ("fork", ("A13",), None), ("capture", ("A14",), None),
]


def strict_violations(rows, claims, tools, setups):
    """(tool, property, setup, refused, shown) where an unconditional claim meets a miss."""
    by = defaultdict(list)
    for r in rows:
        if r["kind"] == "attack" and r["applicable"]:
            by[(r["tool"], r["setup"], r["id"])].append(r)
    out = []
    for tool in tools:
        for prop, ids, _ in STRICT_PROPERTIES:
            if not any(c["strength"] == "claims" for c in claims.get((tool, prop), [])):
                continue
            for setup in setups:
                rs = [r for i in ids for r in by[(tool, setup, i)]]
                d = sum(r["detected"] for r in rs)
                if rs and d < len(rs):
                    out.append((tool, prop, setup, d, len(rs)))
    return out


def build(out_dir, claims_path):
    rows, meta = load(out_dir)
    claims = load_claims(claims_path)
    tools = list(meta["tools"])
    by = defaultdict(list)
    for r in rows:
        if r["kind"] == "attack":
            by[(r["tool"], r["setup"], r["id"])].append(r)
    table = []
    for tool in tools:
        for prop, ids, tier, positions, desc in PROPERTIES:
            strength, kind, crow = claim_for(claims, public(tool), prop, tier)
            for setup in meta["setups"]:
                rs = []
                for i in ids:
                    for r in by[(tool, setup, i)]:
                        if positions is None or r["position"] in positions:
                            # A3 only counts toward truncate at the final position
                            if prop == "truncate" and i == "A3" and r["position"] != "final":
                                continue
                            rs.append(r)
                out, d, n = outcome(rs)
                wired = (public(tool), prop) not in SETUP_NOT_WIRED
                table.append({
                    "tool": public(tool), "property": prop, "attacker": tier, "what": desc,
                    "setup": setup, "detected": d, "trials": n, "outcome": out,
                    "docs_say": strength, "claim_kind": kind,
                    "label": label(strength, kind, setup, out, wired),
                    "quote": (crow or {}).get("quote", ""),
                    "setup_needed": (crow or {}).get("setup_needed", ""),
                })
    return table, meta, rows


def write_labels(table, out_dir):
    p = Path(out_dir) / "labels.csv"
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(table[0]))
        w.writeheader()
        w.writerows(table)
    return p


def cards(table, meta, claims=None) -> str:
    L = ["# Claims Cards\n",
         "One card per tool. Each row compares what the tool's documentation says with what its "
         "own verifier did in ReSeal. `default` is the quick-start setup; `strong` is the "
         "strongest setup ReSeal wired in. Counts are tampered logs refused / tampered logs "
         "shown.\n"]
    tools = []
    for r in table:
        if r["tool"] not in tools:
            tools.append(r["tool"])
    for tool in tools:
        m = next((v for k, v in meta["tools"].items() if public(k) == tool), {})
        named = tool != "tool-e"
        L.append(f"\n## {tool}" + (f" {m.get('version', '')}" if named else " (unnamed)") + "\n")
        if named:
            L.append(f"- Default setup: {m.get('default_setup', '')}")
            L.append(f"- Strong setup: {m.get('strong_setup', '')}\n")
        else:
            L.append("- Default and strong setup: the SDK's own receipt check; it documents no "
                     "stronger offline setup.\n")
        L.append("| Tampering | Attacker | Docs say | Default | Strong | Verdict (default / strong) |")
        L.append("| --- | --- | --- | --- | --- | --- |")
        props = []
        for r in table:
            if r["tool"] == tool and r["property"] not in props:
                props.append(r["property"])
        for p in props:
            d = next(r for r in table if r["tool"] == tool and r["property"] == p and r["setup"] == "default")
            s = next((r for r in table if r["tool"] == tool and r["property"] == p and r["setup"] == "strong"), d)
            says = {"claims": "detects it", "claims_with_setup": f"detects it with {d['setup_needed']}",
                    "disclaims": "does not detect it", "silent": "nothing"}[d["docs_say"]]
            if d["claim_kind"] == "slogan":
                says = "headline only"
            cell = lambda r: "n/a" if r["outcome"] == "n/a" else f"{r['detected']}/{r['trials']}"
            L.append(f"| {d['what']} | {d['attacker']} | {says} | {cell(d)} | {cell(s)} | "
                     f"{d['label']} / {s['label']} |")
        if claims:
            seen = []
            for (t, _prop), rows in claims.items():
                for r in rows:
                    item = (r["quote"], r["source"], r["source_version"])
                    if t == tool and item not in seen:
                        seen.append(item)
            if seen:
                L.append("\nStatements coded:\n")
                for quote, source, version in seen:
                    text = quote if quote.startswith("[") else f'"{quote}"'
                    L.append(f"- {text} ({source}, {version})" if named else f"- {text}")
    return "\n".join(L) + "\n"


def figure(rows, meta, path):
    """Detection rate per attack x tool, default and strong side by side."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap

    tools = list(meta["tools"])
    by = defaultdict(list)
    names = {}
    for r in rows:
        if r["kind"] in ("attack", "coverage") and r["applicable"]:
            by[(r["tool"], r["setup"], r["id"])].append(r["detected"])
            names[r["id"]] = (r["name"], r["tier"])
    order = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12", "A13", "A14"]
    order = [a for a in order if a in names]
    ramp = LinearSegmentedColormap.from_list("blue", ["#ffffff", "#cde2fb", "#6da7ec", "#256abf", "#0d366b"])
    ink, muted = "#1f1f1c", "#6b6a66"
    setups = meta["setups"]
    fig, axes = plt.subplots(1, len(setups), figsize=(11.0, 5.6), sharey=True)
    for ax, setup in zip(axes, setups):
        grid = []
        for a in order:
            row = []
            for t in tools:
                v = by.get((t, setup, a))
                row.append(sum(v) / len(v) if v else float("nan"))
            grid.append(row)
        ax.imshow(grid, cmap=ramp, vmin=0, vmax=1, aspect="auto")
        for i, a in enumerate(order):
            for j, t in enumerate(tools):
                v = by.get((t, setup, a))
                if not v:
                    ax.text(j, i, "n/a", ha="center", va="center", fontsize=8, color=muted)
                    continue
                rate = sum(v) / len(v)
                ax.text(j, i, f"{sum(v)}/{len(v)}", ha="center", va="center", fontsize=8,
                        color="#ffffff" if rate > 0.6 else ink)
        ax.set_xticks(range(len(tools)))
        ax.set_xticklabels([public(t).replace("tool-e", "Tool E\n(unnamed)").replace("agent-receipts", "Agent\nReceipts")
                            .replace("halo-record", "halo-\nrecord").replace("witnesskit", "Witness-\nKit")
                            .replace("signet", "Signet") for t in tools], fontsize=8.5, color=ink)
        ax.xaxis.tick_top()
        ax.set_title(f"{setup.capitalize()} setup", fontsize=10.5, color=ink, pad=34, loc="left", fontweight="bold")
        ax.set_xticks([x - 0.5 for x in range(1, len(tools))], minor=True)
        ax.set_yticks([y - 0.5 for y in range(1, len(order))], minor=True)
        ax.grid(which="minor", color="#ffffff", linewidth=2)
        ax.tick_params(which="both", length=0)
        for s in ax.spines.values():
            s.set_visible(False)
    axes[0].set_yticks(range(len(order)))
    axes[0].set_yticklabels([f"{a}  {names[a][0]}  [{names[a][1]}]" for a in order], fontsize=8.5, color=ink)
    fig.text(0.01, 0.015, "Cells: tampered logs the tool's own verifier refused / tampered logs shown. "
             "Darker = more refused. A14 is a control no hash can catch.",
             fontsize=8, color=muted)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(path, dpi=200, facecolor="#ffffff")
    plt.close(fig)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/main")
    ap.add_argument("--claims", default="claims/claims_coder1.csv")
    a = ap.parse_args(argv)
    table, meta, rows = build(a.out, a.claims)
    print("wrote", write_labels(table, a.out))
    p = Path(a.out) / "CLAIMS_CARDS.md"
    p.write_text(cards(table, meta, load_claims(a.claims)), encoding="utf-8")
    print("wrote", p)
    print("wrote", figure(rows, meta, Path(a.out) / "fig_detection.png"))
    counts = defaultdict(int)
    for r in table:
        counts[(r["setup"], r["label"])] += 1
    claims = load_claims(a.claims)
    strict = strict_violations(rows, claims, list(meta["tools"]), meta["setups"])
    (Path(a.out) / "strict_reading.json").write_text(json.dumps(
        [dict(tool=t, property=p, setup=s, refused=d, shown=n) for t, p, s, d, n in strict], indent=2),
        encoding="utf-8")
    (Path(a.out) / "label_counts.json").write_text(
        json.dumps({f"{k[0]}|{k[1]}": v for k, v in sorted(counts.items())}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
