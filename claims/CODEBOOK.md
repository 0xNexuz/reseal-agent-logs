# Claims codebook

How to turn a tool's public documentation into rows of `claims.csv`. Two
people code every tool **independently, before looking at any results**, then
compare.

## What to read

For each tool, its README, docs site, and any limits / security page, as they
stand at the pinned version. Save the date and the commit or package version
in the `source_version` column. Do not use blog posts or social media.

## One row = one statement about one property

Go through the docs top to bottom. Every time the text says something about
what tampering the tool does or does not catch, add a row.

| Column | What to write |
| --- | --- |
| `tool` | Tool name as in the results tables |
| `coder` | Your initials |
| `source` | File or page, e.g. `README.md` |
| `source_version` | Package version or commit, and the date read |
| `quote` | The exact words, at most 25 words |
| `property` | One code from the list below |
| `tier` | `T1`, `T1+`, `T2`, `T3`, `boundary`, or `any` if the text does not say |
| `strength` | `claims`, `claims_with_setup`, `disclaims` |
| `setup_needed` | If `claims_with_setup`: what must be configured |
| `headline` | `yes` if it is in a title, tagline, or the first screen of the README |
| `absolute_word` | Any of: tamper-proof, immutable, cannot, impossible, prove, guarantee - else blank |
| `notes` | Anything a second reader would need |

## Property codes

| Code | The tool says it detects ... | Attack |
| --- | --- | --- |
| `edit` | a changed record | A1, A2, A9 |
| `delete` | a removed record | A3 |
| `truncate` | records dropped from the end | A4 |
| `reorder` | records out of order | A5 |
| `insert` | an added record | A6, A7 |
| `backdate` | a changed or false time | A8 |
| `downgrade` | missing signatures or integrity data | A10 |
| `forge` | a log made by someone without the keys | A11 |
| `rewrite` | a log rewritten by the key holder / operator | A12 |
| `fork` | two different histories shown to two parties | A13 |
| `capture` | an action that never reached the recorder | A14 |

## Strength

- `claims` - the text says the tool does this, with no condition.
- `claims_with_setup` - it does this only when something extra is configured
  (a pinned key, an expected head, a witness, an anchor).
- `disclaims` - the text says the tool does **not** do this.

If the docs say nothing about a property, add no row. Silence is recorded by
the absence of a row.

## Rules for hard cases

1. Code what the words say to a careful first-time reader, not what the code
   does. Do not open the source.
2. A general slogan ("every action is verifiable") is coded once, as
   `property = edit`, `tier = any`, `headline = yes`, and flagged in `notes`
   as `general slogan`.
3. If one sentence covers several properties ("altering, deleting, inserting
   or reordering any entry is detectable"), add one row per property with the
   same quote.
4. If a headline claim is narrowed later on the same page, code both: the
   headline as `claims`, the later text as `disclaims` or `claims_with_setup`.
   That pair is what H3 measures.
5. When unsure between two codes, pick one and say why in `notes`.

## Comparing the two codings

Match rows by tool, property and tier. Agreement is computed on `strength`
(with "no row" as a fourth category). Report Cohen's kappa, then settle each
disagreement by re-reading the quote together; keep both original files.

## From claims to verdicts

For each tool x property x tier x setup, the result cell is labelled:

| Docs say | Verifier | Label |
| --- | --- | --- |
| claims | catches it | holds |
| claims | misses it | **claim violation** |
| claims_with_setup | catches it in that setup | holds with setup |
| claims_with_setup | misses it in that setup | **claim violation** |
| disclaims | misses it | disclosed limit |
| nothing | misses it | silent miss |
| disclaims or nothing | catches it | better than stated |
