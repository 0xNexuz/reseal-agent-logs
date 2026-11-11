"""Agent Receipts adapter (https://github.com/agent-receipts/obsigna), SDK obsigna.

ReSeal stores the chain as a JSON list of the SDK's own receipt objects
(serialised exactly as its ``ReceiptStore`` does). The SDK also ships an SQLite store; the JSON
list is used so every attack can address a single record.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path

from .base import ACCEPTED, REJECTED, Adapter, Run, Verdict

_TYPE = {
    "tool_call": "data.api.write",
    "model_call": "data.api.read",
    "file_write": "filesystem.file.modify",
    "approval": "system.application.control",
    "delegation": "system.command.execute",
}


def _phash(args: dict) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(args, sort_keys=True).encode()).hexdigest()


class ObsignaAdapter(Adapter):
    name = "agent-receipts"
    package = "obsigna"
    text_format = True
    native_format = False
    signed = True
    default_setup = "verify_chain(receipts, public_key) - the issuer key is a required argument"
    strong_setup = "default plus expected_length and expected_final_hash held outside the operator"

    def log_file(self, logdir: Path) -> Path:
        return logdir / "receipts.json"

    def record(self, events, logdir, *, strong, secrets=None):
        from obsigna import (ActionInput, ActionTarget, ChainEmitInput, InMemoryEmitter, Issuer,
                             Outcome, Principal, ReceiptChain, generate_key_pair, hash_receipt)

        logdir.mkdir(parents=True, exist_ok=True)
        if secrets:
            priv, pub = secrets["priv"], secrets["pub"]
        else:
            kp = generate_key_pair()
            priv, pub = kp.private_key, kp.public_key
        emitter = InMemoryEmitter()
        chain = ReceiptChain(chain_id="chain-run-1", private_key=priv,
                             verification_method="did:example:agent-7#key-1", emitter=emitter)
        for e in events:
            chain.emit(ChainEmitInput(
                issuer=Issuer(id="did:example:agent-7"),
                principal=Principal(id="did:example:operator"),
                action=ActionInput(
                    type=_TYPE[e["kind"]], risk_level="low",
                    target=ActionTarget(system=e["tool"], resource=e["verdict"]),
                    parameters_hash=_phash(e["args"]),
                ),
                outcome=Outcome(status="success" if e["outcome"] == "success" else "failure"),
                action_timestamp=e["ts"],
            ))
        receipts = emitter.received
        # Same serialisation the SDK's own ReceiptStore uses (store.py insert()).
        data = []
        for r in receipts:
            d = r.model_dump(by_alias=True, exclude_none=True)
            d["credentialSubject"]["chain"].setdefault("previous_receipt_hash", None)
            data.append(d)
        self.log_file(logdir).write_text(json.dumps(data), encoding="utf-8")
        external = {"pub": pub}
        if strong and receipts:
            external["length"] = len(receipts)
            external["final_hash"] = hash_receipt(receipts[-1])
        return Run(logdir, external, {"priv": priv, "pub": pub})

    def verify(self, logdir, external, *, strong):
        from obsigna import AgentReceipt, verify_chain

        try:
            raw = json.loads(self.log_file(logdir).read_text(encoding="utf-8"))
            receipts = [AgentReceipt.model_validate(r) for r in raw]
        except Exception as exc:  # the SDK refuses records that do not parse
            return Verdict(REJECTED, f"unparseable: {type(exc).__name__}")
        kwargs = {}
        if strong:
            kwargs = {"expected_length": external.get("length"),
                      "expected_final_hash": external.get("final_hash")}
        res = verify_chain(receipts, external["pub"], **kwargs)
        return Verdict(ACCEPTED if res.valid else REJECTED, res.error or f"broken_at={res.broken_at}")

    def load(self, logdir):
        return json.loads(self.log_file(logdir).read_text(encoding="utf-8")), None

    def dump(self, records, aux, logdir):
        self.log_file(logdir).write_text(json.dumps(records), encoding="utf-8")

    def edit_arg(self, rec):
        rec["credentialSubject"]["action"]["parameters_hash"] = "sha256:" + "ab" * 32

    def flip_verdict(self, rec):
        t = rec["credentialSubject"]["action"]["target"]
        t["resource"] = "allowed" if t.get("resource") == "blocked" else "blocked"

    def backdate(self, rec):
        rec["credentialSubject"]["action"]["timestamp"] = "2020-01-01T00:00:00Z"

    def strip_integrity(self, rec):
        rec.pop("proof", None)

    def fresh_identity(self, rec):
        rec["id"] = f"urn:uuid:{uuid.uuid4()}"
