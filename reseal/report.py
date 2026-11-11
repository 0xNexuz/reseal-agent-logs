"""Turn trials.csv into summary tables (Markdown + JSON)."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


def load(out_dir) -> tuple[list[dict], dict]:
    out = Path(out_dir)
    with open(out / "trials.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["applicable"] = r["applicable"] == "True"
        r["detected"] = r["detected"] == "True"
    return rows, json.loads((out / "meta.json").read_text(encoding="utf-8"))


def _rate(rs) -> str:
    rs = [r for r in rs if r["applicable"]]
    if not rs:
        return "n/a"
    d = sum(r["detected"] for r in rs)
    return f"{d}/{len(rs)}"


def summarise(rows, meta) -> dict:
    tools = list(meta["tools"])
    setups = meta["setups"]
    by = defaultdict(list)
    for r in rows:
        by[(r["kind"], r["tool"], r["setup"], r["id"])].append(r)

    def ids(kind):
        seen = []
        for r in rows:
            if r["kind"] == kind and (r["id"], r["name"], r["tier"]) not in seen:
                seen.append((r["id"], r["name"], r["tier"]))
        return seen

    summary = {"attacks": {}, "controls": {}, "coverage": {}}
    for id_, name, tier in ids("attack"):
        summary["attacks"][id_] = {
            "name": name, "tier": tier,
            "cells": {t: {s: _rate(by[("attack", t, s, id_)]) for s in setups} for t in tools}}
    for id_, name, _ in ids("control"):
        summary["controls"][id_] = {
            "name": name,
            # for controls we report false alarms = detected
            "cells": {t: {s: _rate(by[("control", t, s, id_)]) for s in setups} for t in tools}}
    for t in tools:
        summary["coverage"][t] = {}
        for s in setups:
            rs = by[("coverage", t, s, "A9")]
            missed = sorted({r["variant"] for r in rs if not r["detected"]})
            summary["coverage"][t][s] = {"fields": len({r["variant"] for r in rs}),
                                         "rate": _rate(rs), "undetected_fields": missed}
    return summary


def markdown(rows, meta) -> str:
    s = summarise(rows, meta)
    tools = list(meta["tools"])
    setups = meta["setups"]
    L = []
    L.append("# ReSeal results\n")
    L.append(f"Events per log: {meta['n_events']}. Seeds: {meta['seeds']}. "
             f"Positions: {', '.join(meta['positions'])}. Trials: {meta['trials']}.\n")
    L.append("Each cell is **detected / trials**. Detected means the tool's own verifier did not "
             "accept the tampered log.\n")
    L.append("## Tools and setups\n")
    L.append("| Tool | Version | Default setup | Strong setup |")
    L.append("| --- | --- | --- | --- |")
    for t, m in meta["tools"].items():
        L.append(f"| {t} | {m['version']} | {m['default_setup']} | {m['strong_setup']} |")
    for setup in setups:
        L.append(f"\n## Attacks, {setup} setup\n")
        L.append("| ID | Attack | Tier | " + " | ".join(tools) + " |")
        L.append("| --- | --- | --- | " + " | ".join("---" for _ in tools) + " |")
        for id_, a in s["attacks"].items():
            L.append(f"| {id_} | {a['name']} | {a['tier']} | "
                     + " | ".join(a["cells"][t][setup] for t in tools) + " |")
        L.append(f"\n### A9 field coverage, {setup} setup\n")
        L.append("| Tool | Stored fields changed | Detected | Fields whose change was accepted |")
        L.append("| --- | --- | --- | --- |")
        for t in tools:
            c = s["coverage"][t][setup]
            missed = ", ".join(f"`{m}`" for m in c["undetected_fields"]) or "none"
            L.append(f"| {t} | {c['fields']} | {c['rate']} | {missed} |")
    L.append("\n## Benign controls (false alarms / trials)\n")
    for setup in setups:
        L.append(f"\n**{setup} setup**\n")
        L.append("| ID | Harmless change | " + " | ".join(tools) + " |")
        L.append("| --- | --- | " + " | ".join("---" for _ in tools) + " |")
        for id_, c in s["controls"].items():
            L.append(f"| {id_} | {c['name']} | " + " | ".join(c["cells"][t][setup] for t in tools) + " |")
    bad = [b for b in meta["baselines"] if b["status"] != "accepted"]
    L.append("\n## Baseline check\n")
    L.append("Every clean log was accepted before attacks ran."
             if not bad else f"WARNING: {len(bad)} clean log(s) were not accepted: {bad}")
    return "\n".join(L) + "\n"


def write(out_dir) -> Path:
    rows, meta = load(out_dir)
    out = Path(out_dir)
    (out / "summary.json").write_text(json.dumps(summarise(rows, meta), indent=2), encoding="utf-8")
    (out / "SUMMARY.md").write_text(markdown(rows, meta), encoding="utf-8")
    return out / "SUMMARY.md"
