# ReSeal

Adversarial tests for tamper-evident audit logs of AI agents.

Many tools now promise a "tamper-evident" or "verifiable" record of what an AI
agent did. ReSeal runs one fixed set of attacks against each tool and asks its
own verifier to judge the result. The output is a table per tool showing which
tampering it catches, in its default setup and in its strongest documented one.

Built for the Apart Research **AI x Epistemics Research Sprint** (13-15 Nov
2026), Track 2: Trust Infrastructure.

> **Status: pre-sprint scaffold.** See [PRE_SPRINT.md](PRE_SPRINT.md) for
> exactly what existed before the sprint started. Sprint work is everything
> committed from 13 Nov 2026 onward.

## What it does

1. Generates one seeded synthetic agent run (model calls, tool calls, file
   writes, approvals, delegations).
2. Records that run with each tool's own recording API.
3. Tampers with the stored log in 14 ways, at four positions.
4. Runs the tool's own verifier and records whether it accepts the log.
5. Runs harmless changes too (file copy, CRLF, re-serialised JSON) to count
   false alarms.

## Attacks

| ID | Attack | Attacker |
| --- | --- | --- |
| A1 | Edit a tool argument | T1 outside editor |
| A2 | Flip a policy verdict | T1 |
| A3 | Delete one record | T1 |
| A4 | Truncate the tail (1 and 10 records) | T1 |
| A5 | Swap two adjacent records | T1 |
| A6 | Insert a forged record | T1 |
| A7 | Replay a duplicate record | T1 |
| A8 | Backdate a timestamp | T1 |
| A9 | Change each stored field of one record, one at a time | T1 |
| A10 | Strip signature / integrity fields | T1 |
| A11 | Rebuild the log with the tool's library, without the original keys | T1+ |
| A12 | Rebuild the log with the real signing keys | T2 operator |
| A13 | Fork: same prefix, different suffix, real keys | T3 |
| A14 | Capture omission (the action never reached the recorder) | boundary control |

A14 is expected to pass unseen everywhere: no hash can show an action that was
never recorded. It marks the line between integrity and completeness.

## Tools

| Tool | Package | Notes |
| --- | --- | --- |
| halo-record | `halo-record` | hash chain; external witness checkpoints |
| WitnessKit | `witnesskit` | signed hash chain; optional expected head |
| Signet | `signet-auth` | signed receipts; hash-chained audit log |
| Agent Receipts | `obsigna` | signed receipt chain; optional expected length and final hash |
| Tool E | withheld | a fifth tool, unnamed for now |

Versions are pinned in `requirements.lock`.

## Run it

Python 3.12 or newer.

```
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.lock
pip install -e .

python -m pytest -q             # checks on the harness itself
python -m reseal tools          # installed tool versions
python -m reseal run --n 1000 --seeds 0 1 2 3 4 --out results/main
```

`results/main/SUMMARY.md` holds the tables, `trials.csv` every single trial.

## Reading a result

A cell such as `3/4` means the verifier refused 3 of 4 tampered logs. Before
calling a miss a failure, check the tool's own documentation: a limit the tool
states openly is a disclosed limit, not a broken promise. The claims sheet in
`claims/` records what each tool says about itself.

## Add a tool

Write one `Adapter` subclass in `reseal/adapters/` (see `base.py`) and list it
in `reseal/adapters/__init__.py`. An adapter may only call the tool's public
recording and verifying code.

## Ground rules

- Attacks run only on logs this harness generates locally.
- A suspected flaw is reported to the tool's maintainer before details are
  published (`docs/DISCLOSURE_TEMPLATE.md`).
- Each tool is judged first against its own claims.

## Licence

MIT.
