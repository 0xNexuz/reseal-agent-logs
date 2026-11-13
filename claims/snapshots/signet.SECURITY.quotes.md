<!-- Signet docs/SECURITY.md and README.md, github.com/Prismer-AI/signet main branch, read 2026-11-13 and 2026-11-11.
     Short quotes only, as retrieved through a web reader; check against the source before citing. -->

README.md
- "Delete or reorder entries and the SHA-256 hash chain breaks."
- "Modify any field — tool name, parameters, timestamp, signer — and the Ed25519 signature breaks."
- "SHA-256 hash chain for tamper-evident audit log"
- "This is what "append-only" actually looks like in practice."
- "Signet is first an evidence layer: it proves what happened."

docs/SECURITY.md, Audit Log Integrity > Tamper detection
- Modify a receipt: "Signature verification fails (signet audit --verify)"
- Delete a record: "Hash chain breaks at the gap (signet verify --chain)"
- Reorder records: "Hash chain breaks (prev_hash mismatch)"
- Modify and re-sign: "Requires the private key; public key verification catches if different key used"
- Truncate log tail: "Detectable if expected record count is known"

docs/SECURITY.md, Audit Log Integrity > Limitations
- "Audit log is local. An attacker with filesystem access can delete the entire log."
- "No remote attestation server (planned for v2)."
- "Hash chain proves ordering and integrity, not completeness — a compromised agent could skip logging (--no-log)."

docs/SECURITY.md, Threat Model > What Signet proves
- "The audit log has not been tampered with (hash chain intact)"
