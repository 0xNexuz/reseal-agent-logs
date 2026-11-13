# Research questions and hypotheses

Written on 8-9 November 2026, before the experiment. Committed before any
reported run so the story cannot be fitted to the data afterwards.

Note added 13 November: two pilot runs were made on 9 November (see
`PRE_SPRINT.md`), so these were not written blind to all data. H4 in
particular may reflect a pilot observation. The report reads the outcomes as
descriptive, not confirmatory.

## Questions

1. **Claims.** What security properties do agent audit-log tools claim, and is
   the headline wording stronger than the limits each tool documents?
2. **Behaviour.** Under one fixed attack suite and the attacker tiers below,
   which attacks does each tool's verifier catch, by default and in its
   strongest documented setup?
3. **Gap.** How often does a claimed property fail (a claim violation), and
   how often does a tool fail silently on something it never disclaimed?
4. **Minimal layer.** Which mechanisms together catch every attack in the
   suite up to the capture boundary, and how could they ride on OpenTelemetry
   GenAI spans?

## Attacker tiers

| Tier | Who | Can do |
| --- | --- | --- |
| T1 | Outside editor | Edit stored log bytes; does not repair integrity fields |
| T1+ | Public re-seal | Rebuild the log with the tool's own library, without the original keys |
| T2 | Operator | Rebuild the log with the real signing keys |
| T3 | Equivocating operator | Show a different history that shares a prefix (a fork) |
| boundary | - | The action never reached the recorder |

T1+ was added on 9 November while building the harness: for a hash chain with
no signatures, anyone who can write the file can also recompute the hashes, so
"outside editor" and "operator" are not the only two cases.

## Hypotheses

- **H1.** Default setups catch naive edits (T1) but accept an operator rewrite
  (T2). Catching the operator needs state held outside the operator, and that
  is off by default.
- **H2.** Tail truncation, and deleting the final record, are the most common
  misses for setups with no external state.
- **H3.** Headline wording ("tamper-proof", "immutable", "prove", "cannot be
  altered") claims more than the same tool's own limits section.
- **H4.** At least one verifier accepts a record after a change to a stored
  field (A9) or after its integrity fields are stripped (A10).

## Analysis plan

- Unit: one trial = one tampered log judged by one verifier.
- Design: 5 tools or more x 2 setups x 5 seeds x 1,000 events; positional
  attacks at first, middle, penultimate and final record.
- Outcome: detected = the verifier does not accept the log.
- Reported: detection counts per tool x attack x setup with the raw
  trials file; false alarms on benign controls; fields whose change is
  accepted (A9).
- Each miss is labelled from the claims sheet: disclosed limit, silent, or
  claim violation. Two coders code the claims independently before seeing
  results; agreement is reported as Cohen's kappa.
- Verdicts are deterministic given a seed, so no significance tests are
  planned; seeds and positions show whether a result depends on where the
  tampering lands.

## What would count against us

- If every miss is a limit the tool already discloses, the finding is about
  defaults and wording, not broken tools, and the report says so.
- If the two coders disagree widely (kappa below 0.6), claim-violation counts
  are reported as ranges, not points.
