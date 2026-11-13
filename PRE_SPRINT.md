# Pre-sprint disclosure

The sprint rules allow building on earlier work if it is clearly marked. This
file is that mark. Everything listed here existed **before** the sprint opened
on 13 November 2026. Anything not listed here is sprint work.

Built with AI assistance (Claude), as the sprint rules permit. The author is
responsible for all of it.

## 8 November 2026

- Read the sprint page and chose Track 2.
- Surveyed prior work on tamper-evident agent logs and wrote the project plan.
- Chose the research questions and hypotheses (see `HYPOTHESES.md`).

## 9 November 2026

Code written (all files in this commit are pre-existing):

- `reseal/workload.py` - seeded synthetic agent workload.
- `reseal/adapters/` - adapter contract and adapters for halo-record,
  WitnessKit, Signet, Agent Receipts (obsigna) and a fifth tool, reported
  as Tool E and kept out of this repository (see README).
- `reseal/attacks.py` - attacks A1-A14, including the A9 field sweep.
- `reseal/controls.py` - benign controls C0-C4.
- `reseal/runner.py`, `reseal/report.py`, `reseal/cli.py` - run and summarise.
- `tests/test_harness.py` - 40 checks on the harness itself.
- `claims/CODEBOOK.md`, `claims/claims_template.csv` - claims coding scheme
  (empty sheet; no claims coded yet).

Runs made:

- Two pilot runs: a smoke run (100 events, 1 seed) and a timing run (1,000 events, 1 seed) to
  confirm the harness works end to end. Their numbers are **pilot output, not
  results**: they will not be reported. The reported experiment is re-run from
  scratch during the sprint with the full design.
- Pilot output is kept out of this repository until any maintainer who needs
  a heads-up has had one.

## 11 November 2026

- Read the official report template and updated
  `docs/SUBMISSION_CHECKLIST.md` to match it.
- Re-checked Signet's README for a stronger audit-log setting. None is
  documented beyond pinned keys; server co-signed (bilateral) receipts exist
  and are left to wire in during the sprint.
- Re-confirmed one pilot observation with a standalone script and drafted a
  private note to that tool's maintainer. Neither is in this repository.
- No change to attacks, adapters or the workload.

Known caveat: the author and the AI assistant have both seen pilot output.
The claims codebook asks coders to work before seeing results, so claims
coding in the sprint is either done by a coder who has not seen the pilot, or
this is stated as a limitation in the report.

Not done before the sprint:

- No claims were coded from any tool's documentation.
- No results tables, figures or report text were written.
- Agent Flight Recorder, nono, AI Action Ledger were not integrated.
- The strong setups were chosen from a first read of each tool's code and
  README; they are re-checked against each tool's full docs during the sprint.

## What is new in the sprint (13-15 November 2026)

13 November:

- Documentation snapshots saved for each tool (`claims/snapshots/`).
- Claims coded twice from those snapshots: `claims/claims_coder1.csv` (the
  AI assistant that built the harness) and `claims/claims_coder2.csv` (a
  separate instance given only the codebook and the snapshots).
- The reported runs, all from scratch: `results/main/` (1,000 events, seeds 0
  to 4), `results/robust_n100/` (100 events, seeds 5 to 9) and
  `results/layer/` (checkpoint setups and the plain-log baseline).
- New code: `reseal/checkpoint.py` (the outside checkpoint),
  `reseal/adapters/plain.py` (unprotected baseline), `reseal/analyze.py`
  (labels, Claims Cards, strict reading), `reseal/figure.py`,
  `reseal/numbers.py` (recomputes every number in the report),
  `reseal/quotecheck.py`, `reseal/agreement.py`, `reseal/merge.py`,
  `tests/test_analyze.py`, `tests/test_checkpoint.py`, `report/build.py`.
- The report: `report/ReSeal_report.md` and `.pdf`. A draft was put through
  a mock review by fresh AI reviewers and revised.
- The fifth tool was moved out of the repository and renamed Tool E in all
  files. The two earlier commits were rewritten for that purpose only: the
  adapter file became a stub and the tool's name was replaced. Their dates
  and messages are the original ones. Later commits were made in batches, so
  their times show when work was saved, not when it was done.

Changes to pre-sprint code during the sprint, all small:

- `reseal/adapters/__init__.py`: the fifth adapter is loaded only when
  present; the plain-log baseline is registered.
- `reseal/runner.py`: no version or verifier messages are written for a
  withheld tool; the two checkpoint setups wrap the tool's default verifier.
- No attack, control, workload or named-tool adapter was changed after the
  pilot.
