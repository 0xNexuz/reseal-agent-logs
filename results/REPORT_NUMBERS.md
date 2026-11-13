# Numbers quoted in the report

Recomputed from the trial files in `results/main`, `results/robust_n100` and `results/layer`, and from the two claims sheets, by `python -m reseal.numbers`.

## Run size and checks

- Main run (default, strong; 1,000 events; seeds 0-4): 4212 trials; 864 cells; cells whose outcome differs between seeds: 0; clean logs accepted 50/50; benign controls flagged 0/220; control rows that do not apply: 30; attack rows that do not apply (the attack changes nothing): 10
- Robustness run (default, strong; 100 events; seeds 5-9): 4172 trials; 876 cells; cells whose outcome differs between seeds: 0; clean logs accepted 50/50; benign controls flagged 0/220; control rows that do not apply: 30; attack rows that do not apply (the attack changes nothing): 10
- Checkpoint run (checkpoint, checkpoint-stale, baseline default; 1,000 events; seeds 0-4): 5286 trials; 1095 cells; cells whose outcome differs between seeds: 0; clean logs accepted 65/65; benign controls flagged 0/295; control rows that do not apply: 30; attack rows that do not apply (the attack changes nothing): 70
- Distinct cells, main plus checkpoint run: 1959
- Cells shared by the main and robustness runs: 840; with a different outcome: 0

## Detection counts, main run (refused / shown)

| Test | Setup | halo-record | witnesskit | signet | agent-receipts | tool-e |
| --- | --- | --- | --- | --- | --- | --- |
| A1, A2, A5-A8 each, lowest | default | 20/20 | 20/20 | 20/20 | 20/20 | 0/20 |
| A1, A2, A5-A8 each, lowest | strong | 20/20 | 20/20 | 20/20 | 20/20 | 0/20 |
| A3 not the final record | default | 15/15 | 15/15 | 15/15 | 15/15 | 0/15 |
| A3 not the final record | strong | 15/15 | 15/15 | 15/15 | 15/15 | 0/15 |
| A3 final record | default | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 |
| A3 final record | strong | 5/5 | 5/5 | 0/5 | 5/5 | 0/5 |
| A4 truncate | default | 0/10 | 0/10 | 0/10 | 0/10 | 0/10 |
| A4 truncate | strong | 10/10 | 10/10 | 0/10 | 10/10 | 0/10 |
| A10 strip | default | 20/20 | 20/20 | 20/20 | 20/20 | 15/15 |
| A10 strip | strong | 20/20 | 20/20 | 20/20 | 20/20 | 15/15 |
| A10 strip, first record | default | 5/5 | 5/5 | 5/5 | 5/5 | 0/0 |
| A10 strip, first record | strong | 5/5 | 5/5 | 5/5 | 5/5 | 0/0 |
| A11 rebuild, no keys | default | 0/40 | 40/40 | 0/40 | 40/40 | 0/40 |
| A11 rebuild, no keys | strong | 40/40 | 40/40 | 40/40 | 40/40 | 0/40 |
| A12 operator rewrite | default | 0/40 | 0/40 | 0/40 | 0/40 | 0/40 |
| A12 operator rewrite | strong | 40/40 | 40/40 | 0/40 | 40/40 | 0/40 |
| A13 fork | default | 0/20 | 0/20 | 0/20 | 0/20 | 0/20 |
| A13 fork | strong | 20/20 | 20/20 | 0/20 | 20/20 | 0/20 |
| A14 omission | default | 0/20 | 0/20 | 0/20 | 0/20 | 0/20 |
| A14 omission | strong | 0/20 | 0/20 | 0/20 | 0/20 | 0/20 |
| A9 field sweep | default | 100/100 | 73/73 | 98/98 | 110/125 | 100/135 |
| A9 field sweep | strong | 100/100 | 73/73 | 98/98 | 110/125 | 100/135 |

## Detection counts, checkpoint run (refused / shown)

| Test | Setup | halo-record | witnesskit | signet | agent-receipts | tool-e | plain-jsonl |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A1, A2, A5-A8 each, lowest | checkpoint | 20/20 | 20/20 | 20/20 | 20/20 | 15/20 | 15/20 |
| A1, A2, A5-A8 each, lowest | checkpoint-stale | 20/20 | 20/20 | 20/20 | 20/20 | 10/20 | 10/20 |
| A1, A2, A5-A8 each, lowest | default | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/20 |
| A3 not the final record | checkpoint | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 | 15/15 |
| A3 not the final record | checkpoint-stale | 15/15 | 15/15 | 15/15 | 15/15 | 10/15 | 10/15 |
| A3 not the final record | default | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/15 |
| A3 final record | checkpoint | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| A3 final record | checkpoint-stale | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 |
| A3 final record | default | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/5 |
| A4 truncate | checkpoint | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 |
| A4 truncate | checkpoint-stale | 0/10 | 0/10 | 0/10 | 0/10 | 0/10 | 0/10 |
| A4 truncate | default | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/10 |
| A10 strip | checkpoint | 20/20 | 20/20 | 20/20 | 20/20 | 15/15 | 0/0 |
| A10 strip | checkpoint-stale | 20/20 | 20/20 | 20/20 | 20/20 | 15/15 | 0/0 |
| A10 strip | default | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| A10 strip, first record | checkpoint | 5/5 | 5/5 | 5/5 | 5/5 | 0/0 | 0/0 |
| A10 strip, first record | checkpoint-stale | 5/5 | 5/5 | 5/5 | 5/5 | 0/0 | 0/0 |
| A10 strip, first record | default | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| A11 rebuild, no keys | checkpoint | 40/40 | 40/40 | 40/40 | 40/40 | 40/40 | 40/40 |
| A11 rebuild, no keys | checkpoint-stale | 40/40 | 40/40 | 40/40 | 40/40 | 40/40 | 20/40 |
| A11 rebuild, no keys | default | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/40 |
| A12 operator rewrite | checkpoint | 40/40 | 40/40 | 40/40 | 40/40 | 40/40 | 40/40 |
| A12 operator rewrite | checkpoint-stale | 40/40 | 20/40 | 40/40 | 40/40 | 40/40 | 20/40 |
| A12 operator rewrite | default | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/40 |
| A13 fork | checkpoint | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 |
| A13 fork | checkpoint-stale | 20/20 | 10/20 | 20/20 | 20/20 | 20/20 | 10/20 |
| A13 fork | default | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/20 |
| A14 omission | checkpoint | 0/20 | 0/20 | 0/20 | 0/20 | 0/20 | 0/20 |
| A14 omission | checkpoint-stale | 0/20 | 0/20 | 0/20 | 0/20 | 0/20 | 0/20 |
| A14 omission | default | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/20 |
| A9 field sweep | checkpoint | 100/100 | 73/73 | 98/98 | 125/125 | 135/135 | 43/43 |
| A9 field sweep | checkpoint-stale | 100/100 | 73/73 | 98/98 | 125/125 | 135/135 | 43/43 |
| A9 field sweep | default | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/43 |

- `checkpoint`, all tools, every attack except the control: 2149/2169 refused
  - accepted: A6  at final: 10 trials, tools ['plain-jsonl', 'tool-e']
  - accepted: A7  at final: 10 trials, tools ['plain-jsonl', 'tool-e']
  - accepted at the first or middle record: 0

- `checkpoint-stale`, all tools, every attack except the control: 1869/2169 refused
  - accepted: A1  at final: 10 trials, tools ['plain-jsonl', 'tool-e']
  - accepted: A1  at penultimate: 10 trials, tools ['plain-jsonl', 'tool-e']
  - accepted: A11 delete at final: 5 trials, tools ['plain-jsonl']
  - accepted: A11 delete at penultimate: 5 trials, tools ['plain-jsonl']
  - accepted: A11 edit at final: 5 trials, tools ['plain-jsonl']
  - accepted: A11 edit at penultimate: 5 trials, tools ['plain-jsonl']
  - accepted: A12 delete at final: 10 trials, tools ['plain-jsonl', 'witnesskit']
  - accepted: A12 delete at penultimate: 10 trials, tools ['plain-jsonl', 'witnesskit']
  - accepted: A12 edit at final: 10 trials, tools ['plain-jsonl', 'witnesskit']
  - accepted: A12 edit at penultimate: 10 trials, tools ['plain-jsonl', 'witnesskit']
  - accepted: A13  at final: 10 trials, tools ['plain-jsonl', 'witnesskit']
  - accepted: A13  at penultimate: 10 trials, tools ['plain-jsonl', 'witnesskit']
  - accepted: A2  at final: 10 trials, tools ['plain-jsonl', 'tool-e']
  - accepted: A2  at penultimate: 10 trials, tools ['plain-jsonl', 'tool-e']
  - accepted: A3  at final: 30 trials, tools ['agent-receipts', 'halo-record', 'plain-jsonl', 'signet', 'tool-e', 'witnesskit']
  - accepted: A3  at penultimate: 10 trials, tools ['plain-jsonl', 'tool-e']
  - accepted: A4 1 at -: 30 trials, tools ['agent-receipts', 'halo-record', 'plain-jsonl', 'signet', 'tool-e', 'witnesskit']
  - accepted: A4 10 at -: 30 trials, tools ['agent-receipts', 'halo-record', 'plain-jsonl', 'signet', 'tool-e', 'witnesskit']
  - accepted: A5  at final: 10 trials, tools ['plain-jsonl', 'tool-e']
  - accepted: A5  at penultimate: 10 trials, tools ['plain-jsonl', 'tool-e']
  - accepted: A6  at final: 10 trials, tools ['plain-jsonl', 'tool-e']
  - accepted: A6  at penultimate: 10 trials, tools ['plain-jsonl', 'tool-e']
  - accepted: A7  at final: 10 trials, tools ['plain-jsonl', 'tool-e']
  - accepted: A7  at penultimate: 10 trials, tools ['plain-jsonl', 'tool-e']
  - accepted: A8  at final: 10 trials, tools ['plain-jsonl', 'tool-e']
  - accepted: A8  at penultimate: 10 trials, tools ['plain-jsonl', 'tool-e']
  - accepted at the first or middle record: 0

## Fields whose change was accepted (A9, default setup)

- halo-record: 20 stored fields; accepted: none
- witnesskit: 20 stored fields; accepted: none
- signet: 25 stored fields; accepted: none
- agent-receipts: 25 stored fields; accepted: proof.created, proof.proofPurpose, proof.verificationMethod
- tool-e: 27 stored fields; accepted: agent_id, index, query_hash, response_hash, root_hash, timestamp, tool_name

## Agreement between the two claim codings

- Cells: 55; agreeing: 37; raw agreement 0.673; Cohen's kappa 0.524
- Agreement by tool: {'agent-receipts': 0.545, 'halo-record': 0.545, 'signet': 0.455, 'tool-e': 1.0, 'witnesskit': 0.818}

## Claims versus behaviour, by coder (default / strong)


coder 1:

| Tool | Claim holds | Disclosed limit | Caught, not claimed | Silent miss | Claim not met |
| --- | --- | --- | --- | --- | --- |
| halo-record | 2 / 5 | 6 / 1 | 3 / 5 | 0 / 0 | 0 / 0 |
| witnesskit | 5 / 7 | 2 / 0 | 1 / 3 | 2 / 1 | 1 / 0 |
| signet | 2 / 3 | 4 / 3 | 3 / 3 | 1 / 1 | 1 / 1 |
| agent-receipts | 2 / 3 | 1 / 0 | 4 / 7 | 3 / 1 | 1 / 0 |
| tool-e | 0 / 0 | 0 / 0 | 1 / 1 | 8 / 8 | 2 / 2 |

- Default-setup misses of the four named tools: 22 = {'Disclosed limit': 13, 'Claim not met': 3, 'Silent miss': 6}
- Their silent misses: [('capture', 'agent-receipts'), ('capture', 'witnesskit'), ('fork', 'agent-receipts'), ('fork', 'signet'), ('fork', 'witnesskit'), ('truncate', 'agent-receipts')]
- Claims not met: [('agent-receipts', 'delete', 'default'), ('signet', 'delete', 'default'), ('signet', 'delete', 'strong'), ('tool-e', 'edit', 'default'), ('tool-e', 'edit', 'strong'), ('tool-e', 'forge', 'default'), ('tool-e', 'forge', 'strong'), ('witnesskit', 'delete', 'default')]
- Strict reading, claims not met: [('witnesskit', 'delete', 'default', '15/20'), ('signet', 'delete', 'default', '15/20'), ('signet', 'delete', 'strong', '15/20'), ('agent-receipts', 'delete', 'default', '15/20'), ('tool-e', 'edit', 'default', '0/40'), ('tool-e', 'edit', 'strong', '0/40'), ('tool-e', 'forge', 'default', '0/40'), ('tool-e', 'forge', 'strong', '0/40')]

coder 2:

| Tool | Claim holds | Disclosed limit | Caught, not claimed | Silent miss | Claim not met |
| --- | --- | --- | --- | --- | --- |
| halo-record | 2 / 4 | 3 / 1 | 3 / 6 | 1 / 0 | 2 / 0 |
| witnesskit | 5 / 6 | 2 / 0 | 1 / 4 | 2 / 1 | 1 / 0 |
| signet | 4 / 5 | 4 / 4 | 1 / 1 | 1 / 1 | 1 / 0 |
| agent-receipts | 2 / 2 | 1 / 1 | 4 / 8 | 4 / 0 | 0 / 0 |
| tool-e | 0 / 0 | 0 / 0 | 1 / 1 | 8 / 8 | 2 / 2 |

- Default-setup misses of the four named tools: 22 = {'Claim not met': 4, 'Disclosed limit': 10, 'Silent miss': 8}
- Their silent misses: [('capture', 'witnesskit'), ('delete', 'agent-receipts'), ('fork', 'agent-receipts'), ('fork', 'halo-record'), ('fork', 'signet'), ('fork', 'witnesskit'), ('rewrite', 'agent-receipts'), ('truncate', 'agent-receipts')]
- Claims not met: [('halo-record', 'delete', 'default'), ('halo-record', 'truncate', 'default'), ('signet', 'forge', 'default'), ('tool-e', 'edit', 'default'), ('tool-e', 'edit', 'strong'), ('tool-e', 'forge', 'default'), ('tool-e', 'forge', 'strong'), ('witnesskit', 'delete', 'default')]
- Strict reading, claims not met: [('halo-record', 'delete', 'default', '15/20'), ('halo-record', 'truncate', 'default', '0/10'), ('witnesskit', 'delete', 'default', '15/20'), ('signet', 'delete', 'default', '15/20'), ('signet', 'delete', 'strong', '15/20'), ('signet', 'forge', 'default', '0/40'), ('agent-receipts', 'capture', 'default', '0/20'), ('agent-receipts', 'capture', 'strong', '0/20'), ('tool-e', 'edit', 'default', '0/40'), ('tool-e', 'edit', 'strong', '0/40'), ('tool-e', 'forge', 'default', '0/40'), ('tool-e', 'forge', 'strong', '0/40')]

- Label cells that differ between coders: 25 of 110; of these, cells where one coder says the tampering was missed and the labels differ: 10
