"""Signet adapter (https://github.com/Prismer-AI/signet), Python SDK signet-auth."""

from __future__ import annotations

import json
import secrets as _secrets
import shutil
from pathlib import Path

from .base import ACCEPTED, REJECTED, Adapter, Run, Verdict

AGENT = "agent-7"


class SignetAdapter(Adapter):
    name = "signet"
    package = "signet-auth"
    text_format = True
    native_format = True
    signed = True
    default_setup = ("audit_verify_chain(dir) and audit_verify_signatures(dir), "
                     "no pinned keys (what `signet verify --chain` / `signet audit --verify` run)")
    strong_setup = "default plus trusted_agent_keys=[agent public key] held outside the operator"

    def _audit_files(self, logdir: Path) -> list[Path]:
        return sorted((logdir / "audit").glob("*.jsonl"))

    def log_file(self, logdir: Path) -> Path:
        files = self._audit_files(logdir)
        return files[0] if files else logdir / "audit" / "log.jsonl"

    def record(self, events, logdir, *, strong, secrets=None):
        from signet_auth import SigningAgent

        logdir.mkdir(parents=True, exist_ok=True)
        if secrets:
            shutil.copytree(secrets["keys"], logdir / "keys")
            agent = SigningAgent(AGENT, signet_dir=str(logdir))
        else:
            agent = SigningAgent.create(AGENT, owner="operator", signet_dir=str(logdir))
        for e in events:
            agent.sign(
                e["tool"],
                params={"kind": e["kind"], "args": e["args"], "verdict": e["verdict"],
                        "outcome": e["outcome"], "event_ts": e["ts"]},
            )
        pub = agent.public_key
        agent.close()
        # Keys are the operator's; move them out of what is handed to a verifier.
        keydir = logdir.parent / (logdir.name + "__keys")
        if keydir.exists():
            shutil.rmtree(keydir)
        shutil.move(str(logdir / "keys"), str(keydir))
        external = {"pub": pub} if strong else {}
        return Run(logdir, external, {"keys": str(keydir), "pub": pub})

    def verify(self, logdir, external, *, strong):
        from signet_auth import audit_verify_chain, audit_verify_signatures

        try:
            chain = audit_verify_chain(str(logdir))
            if not chain.valid:
                return Verdict(REJECTED, f"chain break: {chain.break_point}")
            kwargs = {}
            if strong:
                kwargs["trusted_agent_keys"] = [external["pub"]]
            sigs = audit_verify_signatures(str(logdir), **kwargs)
            if sigs.failures:
                return Verdict(REJECTED, f"{len(sigs.failures)} signature failure(s)")
            return Verdict(ACCEPTED, f"{chain.total_records} records, {sigs.valid} signatures valid")
        except Exception as exc:  # the verifier raises on corrupt input
            return Verdict(REJECTED, f"{type(exc).__name__}: {exc}")

    def load(self, logdir):
        recs = []
        for f in self._audit_files(logdir):
            recs += [json.loads(ln) for ln in f.read_text(encoding="utf-8").split("\n") if ln.strip()]
        return recs, None

    def dump(self, records, aux, logdir):
        files = self._audit_files(logdir)
        target = files[0] if files else self.log_file(logdir)
        target.parent.mkdir(parents=True, exist_ok=True)
        for f in files[1:]:
            f.unlink()
        target.write_text(
            "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in records), encoding="utf-8")

    def edit_arg(self, rec):
        rec["receipt"]["action"]["params"]["args"]["_edited"] = 1

    def flip_verdict(self, rec):
        p = rec["receipt"]["action"]["params"]
        p["verdict"] = "allowed" if p["verdict"] == "blocked" else "blocked"

    def backdate(self, rec):
        rec["receipt"]["ts"] = "2020-01-01T00:00:00.000Z"

    def strip_integrity(self, rec):
        rec["receipt"].pop("sig", None)

    def fresh_identity(self, rec):
        rec["receipt"]["id"] = "rec_" + _secrets.token_hex(16)
        rec["receipt"]["nonce"] = "rnd_" + _secrets.token_hex(16)
