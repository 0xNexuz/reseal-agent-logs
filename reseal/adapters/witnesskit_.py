"""WitnessKit adapter (https://github.com/major-matters/witnesskit).

WitnessKit defines no on-disk format; ReSeal stores the tool's own
``Chain.to_json()`` evidence pack as one JSON file.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

from .base import ACCEPTED, REJECTED, Adapter, Run, Verdict


class WitnessKitAdapter(Adapter):
    name = "witnesskit"
    package = "witnesskit"
    text_format = True
    native_format = False
    signed = True
    default_setup = "verify_chain(pack, trusted_keys=[pub]) - the issuer key is pinned, as the README requires"
    strong_setup = "default plus expected_head (a head hash held outside the operator)"

    def log_file(self, logdir: Path) -> Path:
        return logdir / "trail.json"

    def record(self, events, logdir, *, strong, secrets=None):
        from witnesskit import Chain, generate_keypair

        logdir.mkdir(parents=True, exist_ok=True)
        if secrets:
            key = base64.b64decode(secrets["key"])
            pub = base64.b64decode(secrets["pub"])
        else:
            key, pub = generate_keypair()
        trail = Chain(key, actor="agent-7")
        for e in events:
            trail.append(
                e["kind"],
                {"tool": e["tool"], "args": e["args"], "verdict": e["verdict"], "outcome": e["outcome"]},
                timestamp=e["ts"],
            )
        self.log_file(logdir).write_text(json.dumps(trail.to_json()), encoding="utf-8")
        # The pinned public key is part of the tool's default verification.
        external = {"pub": base64.b64encode(pub).decode()}
        if strong:
            external["head"] = trail.head_hash
        return Run(logdir, external,
                   {"key": base64.b64encode(key).decode(), "pub": base64.b64encode(pub).decode()})

    def verify(self, logdir, external, *, strong):
        from witnesskit import verify_chain

        try:
            pack = json.loads(self.log_file(logdir).read_text(encoding="utf-8"))
        except ValueError as exc:
            return Verdict(REJECTED, f"unparseable: {exc}")
        kwargs = {"trusted_keys": [external["pub"]]}
        if strong:
            kwargs["expected_head"] = external.get("head")
        res = verify_chain(pack, **kwargs)
        return Verdict(ACCEPTED if res["valid"] else REJECTED, res.get("reason", ""))

    def load(self, logdir):
        pack = json.loads(self.log_file(logdir).read_text(encoding="utf-8"))
        return pack["entries"], {k: v for k, v in pack.items() if k != "entries"}

    def dump(self, records, aux, logdir):
        pack = dict(aux or {})
        pack["entries"] = records
        self.log_file(logdir).write_text(json.dumps(pack), encoding="utf-8")

    def edit_arg(self, rec):
        rec["payload"]["args"]["_edited"] = 1

    def flip_verdict(self, rec):
        p = rec["payload"]
        p["verdict"] = "allowed" if p["verdict"] == "blocked" else "blocked"

    def backdate(self, rec):
        rec["timestamp"] = "2020-01-01T00:00:00Z"

    def strip_integrity(self, rec):
        rec.pop("signature", None)

    def fresh_identity(self, rec):
        pass  # entries carry no id beyond seq
