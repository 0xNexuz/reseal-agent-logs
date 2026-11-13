# Claims Cards

One card per tool. Each row compares what the tool's documentation says with what its own verifier did in ReSeal. `default` is the quick-start setup; `strong` is the strongest setup ReSeal wired in. Counts are tampered logs refused / tampered logs shown.


## halo-record 0.2.47

- Default setup: verify_log() on the JSONL chain (what `halo verify` runs)
- Strong setup: verify_log() plus verify_completeness() against a witness checkpoint held outside the operator, with the expected subject pinned

| Tampering | Attacker | Docs say | Default | Strong | Verdict (default / strong) |
| --- | --- | --- | --- | --- | --- |
| change a record | T1 | detects it | 40/40 | 40/40 | holds / holds |
| remove one record (any position) | T1 | detects it with a head held by someone else | 15/20 | 20/20 | needs setup (disclosed) / holds with setup |
| cut records off the end | T1 | detects it with external witness checkpoints | 0/10 | 10/10 | needs setup (disclosed) / holds with setup |
| swap two records | T1 | detects it | 20/20 | 20/20 | holds / holds |
| add a forged or duplicate record | T1 | nothing | 40/40 | 40/40 | caught (unstated) / caught (unstated) |
| change a record's time | T1 | nothing | 20/20 | 20/20 | caught (unstated) / caught (unstated) |
| strip signature or integrity fields | T1 | nothing | 20/20 | 20/20 | caught (unstated) / caught (unstated) |
| rebuild the log without the original keys | T1+ | does not detect it | 0/40 | 40/40 | disclosed limit / better than stated |
| operator rebuilds the log with the real keys | T2 | does not detect it | 0/40 | 40/40 | disclosed limit / better than stated |
| operator shows a different history | T3 | detects it with external witness checkpoints | 0/20 | 20/20 | needs setup (disclosed) / holds with setup |
| action never reached the recorder | boundary | does not detect it | 0/20 | 0/20 | disclosed limit / disclosed limit |

Statements coded:

- "Tamper-evident audit trails for AI agents — hash-chained Runtime Records" (README.md, 0.2.47 PyPI 2026-11-13)
- "a chain you hold yourself proves records were not edited, relative to a head someone already holds" (README.md, 0.2.47 PyPI 2026-11-13)
- "given a chain head someone already holds, any edit, reordering, or deletion in the records behind it becomes detectable" (README.md, 0.2.47 PyPI 2026-11-13)
- "only checkpoints held outside the operator prove none were removed" (README.md, 0.2.47 PyPI 2026-11-13)
- "a chain proves internal consistency, not history" (README.md, 0.2.47 PyPI 2026-11-13)
- "an operator could drop a record and re-seal, and the new file would verify" (README.md, 0.2.47 PyPI 2026-11-13)
- "Checkpoints make rewriting committed history detectable" (README.md, 0.2.47 PyPI 2026-11-13)
- "neither the chain nor the witness proves that every real-world action passed through the recorder" (README.md, 0.2.47 PyPI 2026-11-13)

## witnesskit 0.1.0

- Default setup: verify_chain(pack, trusted_keys=[pub]) - the issuer key is pinned, as the README requires
- Strong setup: default plus expected_head (a head hash held outside the operator)

| Tampering | Attacker | Docs say | Default | Strong | Verdict (default / strong) |
| --- | --- | --- | --- | --- | --- |
| change a record | T1 | detects it | 40/40 | 40/40 | holds / holds |
| remove one record (any position) | T1 | detects it | 15/20 | 20/20 | claim not met / holds |
| cut records off the end | T1 | detects it with expected_head | 0/10 | 10/10 | needs setup (disclosed) / holds with setup |
| swap two records | T1 | detects it | 20/20 | 20/20 | holds / holds |
| add a forged or duplicate record | T1 | detects it | 40/40 | 40/40 | holds / holds |
| change a record's time | T1 | detects it with monotonic-timestamp check | 20/20 | 20/20 | holds without the setup / holds with setup |
| strip signature or integrity fields | T1 | nothing | 20/20 | 20/20 | caught (unstated) / caught (unstated) |
| rebuild the log without the original keys | T1+ | detects it | 40/40 | 40/40 | holds / holds |
| operator rebuilds the log with the real keys | T2 | does not detect it | 0/40 | 40/40 | disclosed limit / better than stated |
| operator shows a different history | T3 | nothing | 0/20 | 20/20 | silent miss / caught (unstated) |
| action never reached the recorder | boundary | nothing | 0/20 | 0/20 | silent miss / silent miss |

Statements coded:

- "Every action becomes a signed, hash-chained log entry; any later tamper is detected and located." (README.md, 0.1.0 PyPI 2026-11-13)
- "Alter an entry's content | hash recomputation" (SECURITY.md, commit 25dde68 2026-11-13)
- "Delete an entry | sequence-number gap + broken prev_hash link" (SECURITY.md, commit 25dde68 2026-11-13)
- "Insert a fake entry | downstream seq/link mismatch; a forged entry fails signature/issuer" (SECURITY.md, commit 25dde68 2026-11-13)
- "Reorder entries | sequence-number mismatch" (SECURITY.md, commit 25dde68 2026-11-13)
- "Forge a whole trail | issuer pinning (signer not in trusted_keys)" (SECURITY.md, commit 25dde68 2026-11-13)
- "Truncate / roll back | only with a known expected_head" (SECURITY.md, commit 25dde68 2026-11-13)
- "Backwards-dated entry | optional monotonic-timestamp check" (SECURITY.md, commit 25dde68 2026-11-13)
- "The signing key-holder can re-sign a rewritten chain." (SECURITY.md, commit 25dde68 2026-11-13)
- "Tamper-evident, not tamper-proof" (README.md, 0.1.0 PyPI 2026-11-13)

## signet 0.11.0

- Default setup: audit_verify_chain(dir) and audit_verify_signatures(dir), no pinned keys (what `signet verify --chain` / `signet audit --verify` run)
- Strong setup: default plus trusted_agent_keys=[agent public key] held outside the operator

| Tampering | Attacker | Docs say | Default | Strong | Verdict (default / strong) |
| --- | --- | --- | --- | --- | --- |
| change a record | T1 | detects it | 40/40 | 40/40 | holds / holds |
| remove one record (any position) | T1 | detects it | 15/20 | 15/20 | claim not met / claim not met |
| cut records off the end | T1 | detects it with an expected record count kept by the verifier | 0/10 | 0/10 | needs setup (disclosed) / setup left to the user (disclosed) |
| swap two records | T1 | detects it | 20/20 | 20/20 | holds / holds |
| add a forged or duplicate record | T1 | nothing | 40/40 | 40/40 | caught (unstated) / caught (unstated) |
| change a record's time | T1 | nothing | 20/20 | 20/20 | caught (unstated) / caught (unstated) |
| strip signature or integrity fields | T1 | nothing | 20/20 | 20/20 | caught (unstated) / caught (unstated) |
| rebuild the log without the original keys | T1+ | detects it with pinned public key | 0/40 | 40/40 | needs setup (disclosed) / holds with setup |
| operator rebuilds the log with the real keys | T2 | does not detect it | 0/40 | 0/40 | disclosed limit / disclosed limit |
| operator shows a different history | T3 | nothing | 0/20 | 0/20 | silent miss / silent miss |
| action never reached the recorder | boundary | does not detect it | 0/20 | 0/20 | disclosed limit / disclosed limit |

Statements coded:

- "Modify any field — tool name, parameters, timestamp, signer — and the Ed25519 signature breaks." (README.md, commit f179591 2026-11-13)
- "The audit log has not been tampered with (hash chain intact)" (docs/SECURITY.md, commit f179591 2026-11-13)
- "Delete or reorder entries and the SHA-256 hash chain breaks." (README.md, commit f179591 2026-11-13)
- "Truncate log tail: Detectable if expected record count is known" (docs/SECURITY.md, commit f179591 2026-11-13)
- "Modify and re-sign: Requires the private key; public key verification catches if different key used" (docs/SECURITY.md, commit f179591 2026-11-13)
- "Modify and re-sign: Requires the private key" (docs/SECURITY.md, commit f179591 2026-11-13)
- "Hash chain proves ordering and integrity, not completeness — a compromised agent could skip logging" (docs/SECURITY.md, commit f179591 2026-11-13)

## agent-receipts 0.16.0

- Default setup: verify_chain(receipts, public_key) - the issuer key is a required argument
- Strong setup: default plus expected_length and expected_final_hash held outside the operator

| Tampering | Attacker | Docs say | Default | Strong | Verdict (default / strong) |
| --- | --- | --- | --- | --- | --- |
| change a record | T1 | detects it | 40/40 | 40/40 | holds / holds |
| remove one record (any position) | T1 | detects it | 15/20 | 20/20 | claim not met / holds |
| cut records off the end | T1 | nothing | 0/10 | 10/10 | silent miss / caught (unstated) |
| swap two records | T1 | detects it | 20/20 | 20/20 | holds / holds |
| add a forged or duplicate record | T1 | nothing | 40/40 | 40/40 | caught (unstated) / caught (unstated) |
| change a record's time | T1 | nothing | 20/20 | 20/20 | caught (unstated) / caught (unstated) |
| strip signature or integrity fields | T1 | nothing | 20/20 | 20/20 | caught (unstated) / caught (unstated) |
| rebuild the log without the original keys | T1+ | nothing | 40/40 | 40/40 | caught (unstated) / caught (unstated) |
| operator rebuilds the log with the real keys | T2 | does not detect it | 0/40 | 40/40 | disclosed limit / better than stated |
| operator shows a different history | T3 | nothing | 0/20 | 20/20 | silent miss / caught (unstated) |
| action never reached the recorder | boundary | nothing | 0/20 | 0/20 | silent miss / silent miss |

Statements coded:

- "cryptographically signed, hash-chained records that can't be quietly altered after the fact" (README.md, obsigna 0.16.0 PyPI 2026-11-13)
- "with cryptographic proof the log hasn't been tampered with after the fact" (README.md, obsigna 0.16.0 PyPI 2026-11-13)
- "The receipt chain shows exactly which actions it took, in what order" (README.md, obsigna 0.16.0 PyPI 2026-11-13)
- "Anyone with code execution in the agent can forge receipts." (README.md, obsigna 0.16.0 PyPI 2026-11-13)

## tool-e (unnamed)

- Default and strong setup: the SDK's own receipt check; it documents no stronger offline setup.

| Tampering | Attacker | Docs say | Default | Strong | Verdict (default / strong) |
| --- | --- | --- | --- | --- | --- |
| change a record | T1 | detects it | 0/40 | 0/40 | claim not met / claim not met |
| remove one record (any position) | T1 | nothing | 0/20 | 0/20 | silent miss / silent miss |
| cut records off the end | T1 | nothing | 0/10 | 0/10 | silent miss / silent miss |
| swap two records | T1 | nothing | 0/20 | 0/20 | silent miss / silent miss |
| add a forged or duplicate record | T1 | nothing | 0/40 | 0/40 | silent miss / silent miss |
| change a record's time | T1 | nothing | 0/20 | 0/20 | silent miss / silent miss |
| strip signature or integrity fields | T1 | nothing | 15/15 | 15/15 | caught (unstated) / caught (unstated) |
| rebuild the log without the original keys | T1+ | detects it | 0/40 | 0/40 | claim not met / claim not met |
| operator rebuilds the log with the real keys | T2 | nothing | 0/40 | 0/40 | silent miss / silent miss |
| operator shows a different history | T3 | nothing | 0/20 | 0/20 | silent miss / silent miss |
| action never reached the recorder | boundary | nothing | 0/20 | 0/20 | silent miss / silent miss |

Statements coded:

- [paraphrase: each call gets a proof that cannot be forged or altered afterwards]
- [paraphrase: tamper-evident audit trails]
