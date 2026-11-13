# ReSeal results

Events per log: 1000. Seeds: [0, 1, 2, 3, 4]. Positions: first, middle, penultimate, final. Trials: 5286.

Each cell is **detected / trials**. Detected means the tool's own verifier did not accept the tampered log.

## Tools and setups

| Tool | Version | Default setup | Strong setup |
| --- | --- | --- | --- |
| halo-record | 0.2.47 | verify_log() on the JSONL chain (what `halo verify` runs) | verify_log() plus verify_completeness() against a witness checkpoint held outside the operator, with the expected subject pinned |
| witnesskit | 0.1.0 | verify_chain(pack, trusted_keys=[pub]) - the issuer key is pinned, as the README requires | default plus expected_head (a head hash held outside the operator) |
| signet | 0.11.0 | audit_verify_chain(dir) and audit_verify_signatures(dir), no pinned keys (what `signet verify --chain` / `signet audit --verify` run) | default plus trusted_agent_keys=[agent public key] held outside the operator |
| agent-receipts | 0.16.0 | verify_chain(receipts, public_key) - the issuer key is a required argument | default plus expected_length and expected_final_hash held outside the operator |
| tool-e |  | the SDK's own check on every receipt | same as default - no stronger offline check is documented |
| plain-jsonl |  | none: the log is accepted if every line parses as JSON | same as default |

## Attacks, checkpoint setup

| ID | Attack | Tier | halo-record | witnesskit | signet | agent-receipts | tool-e | plain-jsonl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | edit a tool argument | T1 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 |
| A2 | flip a policy verdict | T1 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 |
| A3 | delete one record | T1 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 |
| A4 | truncate the tail | T1 | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 |
| A5 | swap two adjacent records | T1 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 |
| A6 | insert a forged record | T1 | 20/20 | 20/20 | 20/20 | 20/20 | 15/20 | 15/20 |
| A7 | replay a duplicate record | T1 | 20/20 | 20/20 | 20/20 | 20/20 | 15/20 | 15/20 |
| A8 | backdate a timestamp | T1 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 |
| A10 | strip integrity fields (downgrade) | T1 | 20/20 | 20/20 | 20/20 | 20/20 | 15/15 | n/a |
| A11 | rebuild without the original keys | T1+ | 40/40 | 40/40 | 40/40 | 40/40 | 40/40 | 40/40 |
| A12 | operator rewrite with real keys | T2 | 40/40 | 40/40 | 40/40 | 40/40 | 40/40 | 40/40 |
| A13 | fork: same prefix, different suffix | T3 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 |
| A14 | capture omission (boundary control) | boundary | 0/20 | 0/20 | 0/20 | 0/20 | 0/20 | 0/20 |

### A9 field coverage, checkpoint setup

| Tool | Stored fields changed | Detected | Fields whose change was accepted |
| --- | --- | --- | --- |
| halo-record | 20 | 100/100 | none |
| witnesskit | 20 | 73/73 | none |
| signet | 25 | 98/98 | none |
| agent-receipts | 25 | 125/125 | none |
| tool-e | 27 | 135/135 | none |
| plain-jsonl | 14 | 43/43 | none |

## Attacks, checkpoint-stale setup

| ID | Attack | Tier | halo-record | witnesskit | signet | agent-receipts | tool-e | plain-jsonl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | edit a tool argument | T1 | 20/20 | 20/20 | 20/20 | 20/20 | 10/20 | 10/20 |
| A2 | flip a policy verdict | T1 | 20/20 | 20/20 | 20/20 | 20/20 | 10/20 | 10/20 |
| A3 | delete one record | T1 | 15/20 | 15/20 | 15/20 | 15/20 | 10/20 | 10/20 |
| A4 | truncate the tail | T1 | 0/10 | 0/10 | 0/10 | 0/10 | 0/10 | 0/10 |
| A5 | swap two adjacent records | T1 | 20/20 | 20/20 | 20/20 | 20/20 | 10/20 | 10/20 |
| A6 | insert a forged record | T1 | 20/20 | 20/20 | 20/20 | 20/20 | 10/20 | 10/20 |
| A7 | replay a duplicate record | T1 | 20/20 | 20/20 | 20/20 | 20/20 | 10/20 | 10/20 |
| A8 | backdate a timestamp | T1 | 20/20 | 20/20 | 20/20 | 20/20 | 10/20 | 10/20 |
| A10 | strip integrity fields (downgrade) | T1 | 20/20 | 20/20 | 20/20 | 20/20 | 15/15 | n/a |
| A11 | rebuild without the original keys | T1+ | 40/40 | 40/40 | 40/40 | 40/40 | 40/40 | 20/40 |
| A12 | operator rewrite with real keys | T2 | 40/40 | 20/40 | 40/40 | 40/40 | 40/40 | 20/40 |
| A13 | fork: same prefix, different suffix | T3 | 20/20 | 10/20 | 20/20 | 20/20 | 20/20 | 10/20 |
| A14 | capture omission (boundary control) | boundary | 0/20 | 0/20 | 0/20 | 0/20 | 0/20 | 0/20 |

### A9 field coverage, checkpoint-stale setup

| Tool | Stored fields changed | Detected | Fields whose change was accepted |
| --- | --- | --- | --- |
| halo-record | 20 | 100/100 | none |
| witnesskit | 20 | 73/73 | none |
| signet | 25 | 98/98 | none |
| agent-receipts | 25 | 125/125 | none |
| tool-e | 27 | 135/135 | none |
| plain-jsonl | 14 | 43/43 | none |

## Attacks, default setup

| ID | Attack | Tier | halo-record | witnesskit | signet | agent-receipts | tool-e | plain-jsonl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | edit a tool argument | T1 | n/a | n/a | n/a | n/a | n/a | 0/20 |
| A2 | flip a policy verdict | T1 | n/a | n/a | n/a | n/a | n/a | 0/20 |
| A3 | delete one record | T1 | n/a | n/a | n/a | n/a | n/a | 0/20 |
| A4 | truncate the tail | T1 | n/a | n/a | n/a | n/a | n/a | 0/10 |
| A5 | swap two adjacent records | T1 | n/a | n/a | n/a | n/a | n/a | 0/20 |
| A6 | insert a forged record | T1 | n/a | n/a | n/a | n/a | n/a | 0/20 |
| A7 | replay a duplicate record | T1 | n/a | n/a | n/a | n/a | n/a | 0/20 |
| A8 | backdate a timestamp | T1 | n/a | n/a | n/a | n/a | n/a | 0/20 |
| A10 | strip integrity fields (downgrade) | T1 | n/a | n/a | n/a | n/a | n/a | n/a |
| A11 | rebuild without the original keys | T1+ | n/a | n/a | n/a | n/a | n/a | 0/40 |
| A12 | operator rewrite with real keys | T2 | n/a | n/a | n/a | n/a | n/a | 0/40 |
| A13 | fork: same prefix, different suffix | T3 | n/a | n/a | n/a | n/a | n/a | 0/20 |
| A14 | capture omission (boundary control) | boundary | n/a | n/a | n/a | n/a | n/a | 0/20 |

### A9 field coverage, default setup

| Tool | Stored fields changed | Detected | Fields whose change was accepted |
| --- | --- | --- | --- |
| halo-record | 0 | n/a | none |
| witnesskit | 0 | n/a | none |
| signet | 0 | n/a | none |
| agent-receipts | 0 | n/a | none |
| tool-e | 0 | n/a | none |
| plain-jsonl | 14 | 0/43 | `actor`, `args.approver`, `args.bytes`, `args.path`, `args.query`, `args.request`, `args.scope`, `args.to_agent`, `i`, `kind`, `outcome`, `tool`, `ts`, `verdict` |

## Benign controls (false alarms / trials)


**checkpoint setup**

| ID | Harmless change | halo-record | witnesskit | signet | agent-receipts | tool-e | plain-jsonl |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C0 | harness load and re-save, no change | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 |
| C1 | copy to a new directory | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 |
| C2 | CRLF line endings | 0/5 | n/a | 0/5 | n/a | n/a | 0/5 |
| C3 | re-serialised JSON (key order, spacing) | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 |
| C4 | extra trailing newline | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 |

**checkpoint-stale setup**

| ID | Harmless change | halo-record | witnesskit | signet | agent-receipts | tool-e | plain-jsonl |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C0 | harness load and re-save, no change | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 |
| C1 | copy to a new directory | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 |
| C2 | CRLF line endings | 0/5 | n/a | 0/5 | n/a | n/a | 0/5 |
| C3 | re-serialised JSON (key order, spacing) | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 |
| C4 | extra trailing newline | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 |

**default setup**

| ID | Harmless change | halo-record | witnesskit | signet | agent-receipts | tool-e | plain-jsonl |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C0 | harness load and re-save, no change | n/a | n/a | n/a | n/a | n/a | 0/5 |
| C1 | copy to a new directory | n/a | n/a | n/a | n/a | n/a | 0/5 |
| C2 | CRLF line endings | n/a | n/a | n/a | n/a | n/a | 0/5 |
| C3 | re-serialised JSON (key order, spacing) | n/a | n/a | n/a | n/a | n/a | 0/5 |
| C4 | extra trailing newline | n/a | n/a | n/a | n/a | n/a | 0/5 |

## Baseline check

Every clean log was accepted before attacks ran.
