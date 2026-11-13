# Numbers quoted in the report

Recomputed from `results/main/trials.csv`, `results/robust_n100/trials.csv` and `results/main/labels.csv` by `python -m reseal.numbers`.

## Run size and checks

- Main run trials: 4212 (1000 events per log, seeds [0, 1, 2, 3, 4])
- Robustness run trials: 4172
- Clean logs accepted before attacks: 50/50
- Cells in the main run: 864; cells whose outcome differs between seeds: 0
- Cells shared by the two runs: 840; with a different outcome: 0
- Benign controls flagged: 0/220

## Detection counts (refused / shown)

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
| A10 strip | default | 20/20 | 20/20 | 20/20 | 20/20 | 15/20 |
| A10 strip | strong | 20/20 | 20/20 | 20/20 | 20/20 | 15/20 |
| A10 strip, first record | default | 5/5 | 5/5 | 5/5 | 5/5 | 0/5 |
| A10 strip, first record | strong | 5/5 | 5/5 | 5/5 | 5/5 | 0/5 |
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

## Fields whose change was accepted (A9, default setup)

- halo-record: 20 stored fields; accepted: none
- witnesskit: 20 stored fields; accepted: none
- signet: 25 stored fields; accepted: none
- agent-receipts: 25 stored fields; accepted: proof.created, proof.proofPurpose, proof.verificationMethod
- tool-e: 27 stored fields; accepted: agent_id, index, query_hash, response_hash, root_hash, timestamp, tool_name

## Claims versus behaviour (Table 2), default / strong

| Tool | Claim holds | Disclosed limit | Caught, not claimed | Silent miss | Claim not met |
| --- | --- | --- | --- | --- | --- |
| halo-record | 3 / 5 | 5 / 1 | 3 / 5 | 0 / 0 | 0 / 0 |
| witnesskit | 6 / 7 | 2 / 0 | 1 / 3 | 2 / 1 | 0 / 0 |
| signet | 3 / 4 | 4 / 3 | 3 / 3 | 1 / 1 | 0 / 0 |
| agent-receipts | 3 / 3 | 1 / 0 | 4 / 7 | 3 / 1 | 0 / 0 |
| tool-e | 0 / 0 | 0 / 0 | 0 / 0 | 9 / 9 | 2 / 2 |

- Default-setup misses of the four named tools: 18 = {'disclosed': 12, 'silent miss': 6}
- Their silent misses: [('capture', 'agent-receipts'), ('capture', 'witnesskit'), ('fork', 'agent-receipts'), ('fork', 'signet'), ('fork', 'witnesskit'), ('truncate', 'agent-receipts')]
- Claims not met: [('tool-e', 'edit', 'default'), ('tool-e', 'edit', 'strong'), ('tool-e', 'forge', 'default'), ('tool-e', 'forge', 'strong')]
