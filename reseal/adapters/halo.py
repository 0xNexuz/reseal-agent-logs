"""halo-record adapter (https://github.com/bkuan001/halo-record)."""

from __future__ import annotations

import json
from pathlib import Path

from .base import ACCEPTED, INCONCLUSIVE, REJECTED, Adapter, NotApplicable, Run, Verdict

SUBJECT = "acme"

_KIND = {  # workload kind -> halo action.type
    "tool_call": "tool_call",
    "model_call": "tool_call",
    "file_write": "write",
    "approval": "tool_call",
    "delegation": "agent_message",
}


class HaloAdapter(Adapter):
    name = "halo-record"
    package = "halo-record"
    text_format = True
    native_format = True
    signed = False
    default_setup = "verify_log() on the JSONL chain (what `halo verify` runs)"
    strong_setup = ("verify_log() plus verify_completeness() against a witness checkpoint "
                    "held outside the operator, with the expected subject pinned")

    def log_file(self, logdir: Path) -> Path:
        return logdir / "audit.jsonl"

    def record(self, events, logdir, *, strong, secrets=None):
        from halo_record import Notary, Recorder, build

        logdir.mkdir(parents=True, exist_ok=True)
        path = self.log_file(logdir)
        rec = Recorder(str(path))
        for e in events:
            r = build(
                _KIND[e["kind"]], "security", tool=e["tool"], tool_input=e["args"],
                session_id="run-1", agent={"id": e["actor"]},
                decision="allowed" if e["verdict"] == "allowed" else "denied",
                outcome={"status": "ok" if e["outcome"] == "success" else "error"},
                ts=e["ts"], subject=SUBJECT,
                verification={"status": e["verdict"], "verifier": "gate/1"},
            )
            rec.append(r)
        external = {}
        if strong and events:
            # The witness log lives outside the directory the attacker controls.
            wdir = logdir.parent / (logdir.name + "__witness")
            wdir.mkdir(parents=True, exist_ok=True)
            notary = Notary(str(wdir / "witness.jsonl"))
            records, _ = self.load(logdir)
            notary.witness(records)
            external = {"witness": str(wdir / "witness.jsonl"), "subject": SUBJECT}
        return Run(logdir=logdir, external=external, secrets={})

    def verify(self, logdir, external, *, strong):
        from halo_record import Notary, verify_completeness, verify_log

        msgs: list[str] = []
        ok = verify_log(str(self.log_file(logdir)), out=msgs.append)
        last = msgs[-1] if msgs else ""
        if not ok:
            return Verdict(REJECTED, last)
        if not strong:
            return Verdict(ACCEPTED, last)
        try:
            records, _ = self.load(logdir)
        except ValueError as exc:
            return Verdict(REJECTED, f"unparseable: {exc}")
        cps = Notary(external["witness"]).checkpoints()
        res = verify_completeness(records, cps, expected_subject=external["subject"])
        if res.get("ok") is True:
            return Verdict(ACCEPTED, "witnessed and complete")
        if res.get("ok") is None:
            return Verdict(INCONCLUSIVE, res.get("why", "unwitnessed"))
        return Verdict(REJECTED, res.get("why", "completeness check failed"))

    def load(self, logdir):
        text = self.log_file(logdir).read_text(encoding="utf-8")
        return [json.loads(ln) for ln in text.split("\n") if ln.strip()], None

    def dump(self, records, aux, logdir):
        body = "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in records)
        self.log_file(logdir).write_text(body, encoding="utf-8")

    # -- hooks -------------------------------------------------------------
    def edit_arg(self, rec):
        inp = rec["action"]["input"]
        inp["summary"] = str(inp.get("summary", "")) + " [edited]"

    def flip_verdict(self, rec):
        v = rec["verification"]
        v["status"] = "allowed" if v["status"] == "blocked" else "blocked"

    def backdate(self, rec):
        rec["ts"] = "2020-01-01T00:00:00Z"

    def strip_integrity(self, rec):
        rec.pop("integrity", None)

    def fresh_identity(self, rec):
        import uuid

        rec["record_id"] = str(uuid.uuid4())

    def edit_uncovered(self, rec):
        raise NotApplicable
