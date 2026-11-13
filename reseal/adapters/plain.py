"""Baseline: a plain JSONL log with no integrity mechanism at all.

Sprint work (13 Nov 2026 onward). Its "verifier" accepts any file that parses.
It shows what the attack suite scores against no protection, and what the
outside checkpoint adds on its own.
"""

from __future__ import annotations

import json
from pathlib import Path

from .base import ACCEPTED, REJECTED, Adapter, Run, Verdict


class PlainAdapter(Adapter):
    name = "plain-jsonl"
    package = ""
    text_format = True
    native_format = True
    signed = False
    baseline = True
    default_setup = "none: the log is accepted if every line parses as JSON"
    strong_setup = "same as default"

    def log_file(self, logdir: Path) -> Path:
        return logdir / "log.jsonl"

    def record(self, events, logdir, *, strong, secrets=None):
        logdir.mkdir(parents=True, exist_ok=True)
        self.dump([dict(e) for e in events], None, logdir)
        return Run(logdir=logdir, external={}, secrets={})

    def verify(self, logdir, external, *, strong):
        try:
            records, _ = self.load(logdir)
        except ValueError as exc:
            return Verdict(REJECTED, f"unparseable: {exc}")
        return Verdict(ACCEPTED, f"{len(records)} lines parse")

    def load(self, logdir):
        text = self.log_file(logdir).read_text(encoding="utf-8")
        return [json.loads(ln) for ln in text.split("\n") if ln.strip()], None

    def dump(self, records, aux, logdir):
        body = "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in records)
        self.log_file(logdir).write_text(body, encoding="utf-8")

    def edit_arg(self, rec):
        rec["args"]["_edited"] = 1

    def flip_verdict(self, rec):
        rec["verdict"] = "allowed" if rec["verdict"] == "blocked" else "blocked"

    def backdate(self, rec):
        rec["ts"] = "2020-01-01T00:00:00Z"
