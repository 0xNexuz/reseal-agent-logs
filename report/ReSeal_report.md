# ReSeal: Do Tamper-Evident Agent Logs Hold Up Against Their Own Operator?

Eleazar Ekhosu (Independent researcher)

With Apart Research. Research conducted at the AI x Epistemics Research Sprint, November 13 to 15, 2026.

## Abstract

Open-source tools now promise "tamper-evident" logs of what an AI agent did, each with a verifier that prints a pass verdict. We test whether that verdict changes when the log is changed. ReSeal records one seeded agent workload through five such tools and an unprotected baseline, applies 14 kinds of tampering, and asks each tool's own verifier to judge the result, in its default and strongest documented setups. Each tool's documented claims are coded twice and compared with its verifier's behaviour. Four of five tools refuse every edited argument or verdict and every reordered, inserted or backdated record. By default all five accept a truncated log, a log rebuilt by the operator with the real keys, and a forked history. Three refuse these once a head hash or record count is held outside the operator, one leaves that comparison to the user, and one accepts altered records outright (reported unnamed). Documentation and behaviour part mostly at the last record: every tool accepts its deletion by default, and only one README says so. We then confirm the long-known remedy in its smallest form, an outside checkpoint of a record count and a prefix digest. With it every tool, even the unprotected baseline, refuses every change to the records it covers. A pass verdict from a default setup shows that a log is consistent with itself, not that it is the log that was written.

## 1. Introduction

When an AI agent takes a consequential action, the operator's own log is usually the only record of it. This sprint's Track 2 brief puts it the same way and asks: "What minimal tamper-evident layer is missing from today's AI observability standards?" [12]. Open-source tools already offer an answer. They chain records with hashes, sign them, and ship a verifier that prints a verdict.

A green "verified" is itself a claim about the world. It is only worth trusting if the verifier would have said something different had the log been changed. That is an empirical question. So far each tool has answered it only for its own design [1].

This matters for AI safety because agent logs are evidence. Incident review, oversight and audits against safety commitments rest on records the audited party holds, and the party with the strongest reason to change a log, the operator, also holds the storage and the signing keys.

**Threat model.** We test five kinds of attacker. An *outside editor* changes stored records and does not repair integrity fields. A *re-sealer* rebuilds the whole log with the tool's own library but without the original keys. The *operator* rebuilds the log with the real keys. A *forking operator* shows a different history that shares a prefix with the real one. The last case is a control: the action never reached the recorder. We assume the cryptography is sound and attack only logs we generated ourselves.

**Contributions.**

1. ReSeal, an open harness (built before the sprint, Appendix B) that records one seeded agent workload through each tool's own API, applies 14 kinds of tampering, and asks the tool's own verifier for a verdict.
2. A head-to-head measurement of five shipped tools and a baseline under the same attacks. To our knowledge it is the first to run each tool's own verifier against one tampering suite.
3. A claims-versus-behaviour comparison, coded twice, giving one Claims Card per tool.
4. A confirmation, across these tools, of the long-known remedy in its smallest form: a count and a prefix digest held outside the operator. It is a partial answer to the Track 2 question: tested on log files, only sketched for telemetry.

## 2. Related Work

**Single-system evaluations.** Agent Flight Recorder [1] combines hash chaining, Merkle batching and on-chain anchoring. It reports that edit, delete, reorder and fork tampering are all detected, at about 48 microseconds of added median latency per event. It injects each attack at ten positions in one log, evaluates only its own system, and leaves comparison against deployed alternatives to future work. We reuse the idea of varying the position, and add multi-record truncation, key-holder rewrites and a field-by-field sweep.

**Conformance suites.** Prakash [9] scores four vendors' agent-governance artifacts against an open receipt specification. Adapters translate each vendor's artifact into that specification; the vendors' own verifiers are not run, and no tampering campaign is reported. Sharif's conformance corpus [10] offers 184 test vectors for verifiers of one draft format [3]; each invalid vector plants one defect. Both test conformance to a format. ReSeal tests what shipped verifiers accept.

**Conceptual limits.** Zhao et al. [2] argue that a claim about an agent is auditable only when its policy, its scope, the records that would settle it and a decision rule are fixed before any verdict. They note that verification authenticates the entries it is given and, without an independent checkpoint, cannot rule out a rewritten chain. That an operator can rewrite a self-held chain is therefore known in principle.

**Outside checkpoints.** The remedy is old. Certificate Transparency [13] has logs publish signed tree heads that monitors compare, and Crosby and Wallach [14] give auditors commitments and incremental proofs from a logger that is never trusted. Zhao et al. [2] recommend anchoring an agent log with a checkpoint held by another party. We do not improve on these designs. We measure which shipped agent-log tools have such a check, whether it is on, and what its smallest form does for the tools that lack it.

**Formats and standards.** An individual IETF draft [3] defines an agent audit record format in which hash chaining is required while signatures, external timestamps and Merkle batch anchoring are optional. RFC 9943 [4] defines transparency services that issue receipts and requires non-equivocation. OpenTelemetry's GenAI conventions [11] define agent and tool spans; at the commit we read they contain no integrity, digest or checkpoint attribute.

**The gap.** Searches of arXiv, GitHub, PyPI and the web on 8 and 13 November 2026 found no study that runs shipped tools' own verifiers against one tampering suite, and none that sets a tool's documented claims against its verifier's behaviour. ReSeal does both.

## 3. Methods

**Tools.** We test five open-source tools that claim tamper-evidence for agent records, ship a verifier that runs offline, and install from PyPI: halo-record 0.2.47 [5], WitnessKit 0.1.0 [6], Signet (signet-auth 0.11.0) [7], Agent Receipts (obsigna 0.16.0) [8], and a fifth tool reported as Tool E. Tool E is unnamed because its result looks like a defect and its maintainer has not been contacted (Appendix A). These are young projects, and we make no claim about how widely they are used. A sixth column is a *baseline*: a plain JSON-lines log whose "verifier" accepts any file that parses. Agent Flight Recorder [1] is not on a package index and could not be installed in our environment, so it was read but not run.

**Adapters.** One adapter per tool calls only that tool's public recording and verifying code. A verdict of "accepted" means the verifier vouched for the log. Any refusal counts as detected, including an explicit "cannot vouch" and a verifier that cannot parse the tampered file.

**Three setups.** *Default* is what the quick start gives. *Strong* is the strongest verification the tool documents, with the extra state held outside the attacker's reach (Table 1). *Checkpoint* is the default verifier plus the ReSeal checkpoint described below. Attacks never touch outside state.

| Tool | Default setup | Strong setup adds |
| --- | --- | --- |
| halo-record | Hash-chain check | Witness checkpoint (record count, head, root) held outside the operator |
| WitnessKit | Chain and signature check with the issuer key pinned | Expected head hash held outside |
| Signet | Chain check and signature check, no pinned key | Agent public key pinned |
| Agent Receipts | Chain and signature check against a given public key | Expected length and final hash held outside |
| Tool E | Per-receipt proof check | Nothing: no stronger offline setup is documented |

*Table 1. What each setup verifies. The strong setups are not like for like: Signet's adds a key but no state about the log's length or head. Its verifier reports a record count and leaves the comparison with an expected count to the user, so we did not make it. The checkpoint setup gives every tool the same outside state.*

**The ReSeal checkpoint.** Two values are kept by someone other than the operator: a record count *n*, and a running SHA-256 digest over the first *n* records in order (d<sub>0</sub> is 32 zero bytes; d<sub>k</sub> = SHA-256(d<sub>k-1</sub> || SHA-256(record k as canonical JSON))). A presented log passes if it has at least *n* records and its first *n* give the same digest. It needs no keys and knows nothing about the tool. It is about 40 lines of code (`reseal/checkpoint.py`), and by construction it must refuse any change to the records it covers. The run checks that it does so through each tool's own file format without false alarms, and shows what stays uncovered. We test it taken after the last record, and taken *stale*, after the first 90% of the log.

**Workload and attacks.** A seeded generator produces 1,000 agent events per run (tool calls, model calls, file writes, approvals, delegations, each with a policy verdict), and the same events are recorded through every tool. There are fourteen attacks, A1 to A14 (Appendix C maps them to Figure 1's rows). Nine edit stored records: change an argument, flip a policy verdict, delete, truncate, swap, insert, replay, backdate, or strip integrity fields. One changes every stored field of one record, one field at a time. Two rebuild the whole log through the tool's own recorder, without and with the real keys. One forks the history. The last is the control. Positional attacks run at the first, middle, penultimate and final record.

**Benign controls.** Five harmless changes measure false alarms: a harness load and re-save, a file copy, CRLF line endings, re-serialised JSON, and a trailing newline.

**Unit of evidence.** Verifiers are deterministic. One *cell* is one tool, setup, attack, variant and position. Five seeds and a second log length (100 events, five other seeds) are replicates that test whether an outcome depends on content or length. Seventy-seven field-sweep cells exist on only one or two seeds, because those fields appear only in some workloads. They are not independent samples, so we report exact counts.

**Claims coding.** For each tool we saved the README packaged with the tested version, plus the limits or security document that README points to. Each statement about tampering was coded as property, attacker and strength: *claims*, *claims with setup*, or *disclaims*. No statement means *silent*. Two coders worked from a written codebook. Coder 1 was the AI assistant that built the harness, and it had seen pilot results. Coder 2 was a separate instance of the same model that was given only the codebook and the saved documents, with no access to code or results. halo-record's LIMITS.md was saved after coder 1 had finished, so only coder 2 coded it. We report Cohen's kappa on the governing statement for each tool and property (55 cells), and we report every disagreement.

**Labels.** Each tool, property and setup gets one label. *Claim holds*: the documentation claims detection and the verifier detects. *Disclosed limit*: the documentation says the tampering is not detected, or needs extra setup, and it is missed. *Caught, not claimed*: detected although the documentation is silent or disclaims it. *Silent miss*: missed and never mentioned. *Claim not met*: the documentation claims detection and the verifier accepts the log. Two rules were fixed on 13 November, after the pilot and before the reported run: a specific statement governs over a headline, and where several statements apply the most cautious one governs. The codebook, written before the sprint, counts every deletion as deletion, and our main labels follow it. Section 4.3 also gives the result when deletion of the last record is counted as truncation.

**Harness checks.** Forty-eight tests in the public repository (56 with the withheld Tool E adapter) assert properties of ReSeal itself: clean logs verify, every attack changes the file, the field sweep changes exactly one field, attacks never touch the original or the outside state, the checkpoint accepts a log that only grew, and every coded quote appears word for word in the saved documentation.

**A correction to the harness.** The checkpoint run exposed a trial that was not an attack: stripping the proof from Tool E's first record changes nothing, because that proof is empty. An earlier draft counted it as a miss. The runner now records such trials as not applicable, Tool E's rows were re-run, and a scan of every tool, attack and position found no other case.

**What did not work.** Signet's server co-signed receipts looked like a stronger setup, but its Python SDK refuses to append them to the audit log (a type error), so they were left out.

## 4. Results

The main run covers 864 cells (default and strong setups) on up to five seeds: 4,212 trials, of which 40 are recorded as not applicable (30 benign controls that do not fit a tool's file format, and 10 attacks that change nothing, explained in Section 3). Every clean log was accepted before any attack ran. No cell changed outcome between seeds, and the 100-event run agreed with the main run in all 840 cells they share. No benign control raised a false alarm in any setup (0 of 220 applicable trials in the main run, 0 of 295 in the checkpoint run). The checkpoint run adds 1,095 cells and 5,286 trials.

### 4.1 What the verifiers did

**Outside editor.** In the default setup, four tools refused every log with an edited, swapped, inserted, replayed, backdated or stripped record. Tool E accepted every edited, swapped, inserted, replayed and backdated log. Deletion depends on position: the same four tools refused a deletion at the first, middle or penultimate record and accepted deletion of the final record. All five tools accepted a log with its last 1 or last 10 records cut off. The unprotected baseline accepted everything, as it must.

**Rebuild without the keys.** WitnessKit and Agent Receipts refused every rebuilt log, because their quick start already takes the issuer's public key. halo-record and Signet accepted every one. halo-record's chain is unsigned, and its README says so. Signet's default checks use the public key carried inside each receipt.

**Operator.** In the default setup all five tools accepted every log rebuilt with the real keys and every forked history. In the strong setup halo-record, WitnessKit and Agent Receipts refused all of them, and also refused truncation. Signet's strongest documented setup, a pinned key, cannot help against the key holder and still accepted truncation; its audit verifier takes no expected count, although its security page says truncation is "Detectable if expected record count is known". Tool E has no stronger setup.

**Field coverage.** halo-record, WitnessKit and Signet refused a change to any stored field. Agent Receipts accepted changes to three fields inside its proof block (creation time, purpose, key reference). Its README notes that the receipt hash excludes the proof block, so this is a design choice, and the receipt's own time and issuer fields are covered. Tool E accepted changes to 7 of its 27 stored fields: agent identifier, index, query hash, response hash, root hash, timestamp and tool name.

**Control.** No setup flagged an action that was never recorded, as expected.

### 4.2 The outside checkpoint

This part is a confirmation, not a discovery. With a checkpoint taken after the last record (Figure 1C), every tool refused every change to the recorded log, as it must: every edit, deletion, truncation, swap, rebuild and fork. That includes Signet, whose verifier takes no expected count, Tool E, and the unprotected baseline. In all, 2,149 of 2,169 tampered logs were refused. The 20 accepted are one case: a forged or duplicated record added after the last one, on Tool E and on the baseline, whose own checks accept any record. A checkpoint says nothing about records that arrive after it. Covering those is the job of a chain or a signature, and the four working tools did it.

A checkpoint protects only what it covers (Figure 1D). With the stale checkpoint, no tool accepted any tampering at the first or middle record. In the uncovered tail each tool fell back to its own default check: all six accepted deletion of the last record and truncation, WitnessKit accepted operator rewrites and forks there, and Tool E and the baseline accepted every outside edit. Panel D flatters the other tools on rebuilds. Our rebuild re-records the whole log, and those tools put fresh identifiers or times in every record, so the covered part changed too. An operator who kept the covered part and rebuilt only the tail would pass, as WitnessKit's row shows. The window between checkpoints is therefore the real design parameter, and it is set by how often the outside party receives a new count and digest.

![Four panels showing, for ten kinds of tampering and six columns, whether each verifier refused all, none or some tampered logs: default setup, strongest documented setup, default with an outside checkpoint, and default with a stale checkpoint](../results/fig_main.png)

*Figure 1. What each tool's own verifier refused. A: default setup. B: strongest documented setup. C: default setup plus the ReSeal checkpoint, taken after the last record. D: the same with a stale checkpoint that covers the first 90% of the log. Each cell pools five seeds. A fraction is tampered logs refused out of tampered logs shown; for the field sweep it is fields.*

### 4.3 Claims versus behaviour

The two codings agreed on 37 of 55 cells (Cohen's kappa 0.52). That is below the 0.6 we set in advance, so, as planned for that case, counts are given under both codings. Table 2 shows coder 1's sheet, and Appendix C lists every difference.

| Tool | Claim holds | Disclosed limit | Caught, not claimed | Silent miss | Claim not met |
| --- | --- | --- | --- | --- | --- |
| halo-record | 2 | 6 | 3 | 0 | 0 |
| WitnessKit | 5 | 2 | 1 | 2 | 1 |
| Signet | 2 | 4 | 3 | 1 | 1 |
| Agent Receipts | 2 | 1 | 4 | 3 | 1 |
| Tool E | 0 | 0 | 1 | 8 | 2 |

*Table 2. Default setup, coder 1: eleven kinds of tampering per tool, labelled by what the documentation says and what the verifier did.*

The four named tools miss 22 of their 44 default-setup cells. Coder 1 reads 13 of these as disclosed, 6 as silent and 3 as claims not met. Coder 2 reads 10, 8 and 4. On either sheet most misses are disclosed.

How many documented claims of the named tools fail is not settled. It is between zero and four, depending on the coder and on one definition, and up to six if any unconditional statement is allowed to govern (the stricter reading in `results/REPORT_NUMBERS.md`). Coder 1's three are deletion claims by WitnessKit, Signet and Agent Receipts, and each fails only when the deleted record is the last one. The codebook, written before the sprint, counts that as deletion, and Table 2 follows it. Counted as truncation, which is byte for byte the same change, none of the three fails, because WitnessKit and Signet say truncation needs an expected head or count. Coder 2 agrees on WitnessKit only and adds three other cells (Appendix C).

What does not depend on the coder is narrower. Every tool accepts deletion of its last record by default. halo-record says so in its README. WitnessKit and Signet say it in a security page. Agent Receipts says it only in a code docstring, which our coding did not cover.

Tool E's README says, in paraphrase, that each call gets a proof that cannot be forged or altered afterwards. Its verifier accepted altered records and logs rebuilt without the original keys. Both coders mark both claims as not met.

Appendix B scores the four hypotheses written before the runs: three were supported and one in part.

## 5. Discussion and Limitations

**What is new here.** That a self-held chain cannot stop its key holder is known [2], and outside checkpoints are decades old [13, 14]. The measurements add two things. First, which shipped agent-log tools have the check and whether it is on: three have it, none by default, one leaves the comparison to the user, and one fails earlier. Second, where documentation and behaviour part: mostly in silence about forks and the last record, and in one tool outright. The checkpoint run adds a confirmation. The smallest form of the remedy, two numbers, is enough for every record it covers, even on a log with no protection.

**Implications.** Whoever relies on an agent log should ask who holds the head. A verify result that uses only what the operator stores is evidence against an outside editor and nothing more. Tool builders can print what was not checked next to the pass verdict, as halo-record already does, put the expected head or count in the quick start, and say on the first screen that the default cannot see truncation or a fork.

**For standards.** A format that requires chaining and leaves anchoring optional [3] describes the default setups we tested. For telemetry, the two checkpoint values could ride on existing spans as a periodic event sent to a collector the operator does not control. `docs/OTEL_MAPPING.md` sketches this for the OpenTelemetry GenAI conventions [11]. We did not test it with an OpenTelemetry SDK; the plain-log baseline with a checkpoint is the tested stand-in.

**Limitations.**

- Five tools, one version each, chosen by us from tools with an offline verifier on PyPI. Hosted services and other language SDKs are untested, we have no adoption data, and deterministic outcomes support no claim beyond these versions and attacks. Cost and latency were not measured, and Agent Flight Recorder, the closest prior system, was not run.
- The workload is synthetic. The results describe verifiers, not real deployments.
- Outside state is assumed honest and intact. We do not test an attacker who can replace it, key theft, or the cryptography. The checkpoint result holds by construction for the records covered. The open questions are untested: who holds the checkpoint, how often it is taken, and an operator who shows different checkpoints to different holders.
- Claims were coded from each README and the limits or security page it points to, not from docstrings or specifications. Both coders are instances of one AI model, and they agree only moderately. Coder 2 was blind to code and results but is not a human reader. Labels in Table 2 are one coder's reading; the ranges in Section 4.3 are the summary to rely on.
- Tool E is unnamed, so readers cannot reproduce its column yet. A SHA-256 commitment to its adapter is published so the later release can be checked, and the sprint organisers can have the name and adapter on request (Appendix A).

**Future work.** A human claims coder, more tools including hosted ones, attacks on the checkpoint holder, and the telemetry mapping built and tested.

## 6. Conclusion

One tampering suite, run against five open-source agent audit-log tools, shows that four of them catch outside edits and that all five, by default, accept a truncated log, a log rewritten by the operator, and a forked history. Three refuse these once a head hash, a count or a checkpoint is held by someone else, and with a 40-line outside checkpoint all of them do, for every record it covers. A "verified" result is only as strong as the state the verifier holds that the operator does not. A new tool needs one ReSeal adapter to get its own column and Claims Card.

## Code and Data

Code, the claims sheets, saved documentation snapshots and every trial are in the project repository: github.com/0xNexuz/reseal-agent-logs. It leaves out the Tool E adapter (Appendix A). The file `results/REPORT_NUMBERS.md` recomputes every number in this report from the trial files. No dataset with personal data is used; the workload is synthetic.

## Author Contributions

E.E. entered the sprint, commissioned and oversaw the work, decided how the unnamed tool's result would be handled, and reviewed and approved this report. The hands-on work was done with an AI assistant, as the LLM Usage Statement describes.

## References

[1] L. Bindschaedler, Q. Botha, C. Siebenbrunner. Agent Flight Recorder: Tamper-Evident Audit Trails with On-Chain Anchoring for Long-Horizon Tool-Using Agents. arXiv:2609.01931, 2026. https://arxiv.org/abs/2609.01931

[2] Y. Zhao, J. Li, L. Li, Y. Nian, J. Liu, X. Zhou, X. Hu. Auditable Claims about AI Agents. arXiv:2610.07459, 2026. https://arxiv.org/abs/2610.07459

[3] R. Sharif. Agent Audit Trail: A Standard Logging Format for Autonomous AI Systems. Internet-Draft draft-sharif-agent-audit-trail-09, 26 October 2026. Individual submission, not endorsed by the IETF. https://datatracker.ietf.org/doc/draft-sharif-agent-audit-trail/

[4] H. Birkholz, A. Delignat-Lavaud, C. Fournet, Y. Deshpande, S. Lasker. An Architecture for Trustworthy and Transparent Digital Supply Chains. RFC 9943, June 2026. https://www.rfc-editor.org/rfc/rfc9943.html

[5] halo-record 0.2.47. README as packaged on PyPI and LIMITS.md at tag v0.2.47, read 13 November 2026. https://github.com/bkuan001/halo-record

[6] WitnessKit 0.1.0. README as packaged on PyPI and SECURITY.md at commit 25dde68, read 13 November 2026. https://github.com/major-matters/witnesskit

[7] Signet (signet-auth 0.11.0). README and docs/SECURITY.md at commit f179591, read 13 November 2026. https://github.com/Prismer-AI/signet

[8] Agent Receipts (obsigna 0.16.0). README as packaged on PyPI, read 13 November 2026. https://github.com/agent-receipts/obsigna

[9] S. Prakash. I tested 4 AI agent-governance tools against an open spec - here's the matrix. DEV Community, 23 May 2026. https://dev.to/sunilprakash/i-tested-4-ai-agent-governance-tools-against-an-open-spec-heres-the-matrix-4l2a

[10] R. Sharif. Agent Audit Trail conformance corpus. Commit c8e3d94, 1 November 2026. https://github.com/razashariff/aat-conformance

[11] OpenTelemetry. Semantic conventions for generative AI systems: agent, framework and tool-execution spans. Commit e6658f1, 6 November 2026. https://github.com/open-telemetry/semantic-conventions-genai

[12] Apart Research. AI x Epistemics Research Sprint, Track 2: Trust Infrastructure. Read 13 November 2026. https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15

[13] B. Laurie, A. Langley, E. Kasper. Certificate Transparency. RFC 6962, June 2013. https://www.rfc-editor.org/rfc/rfc6962.html

[14] S. A. Crosby, D. S. Wallach. Efficient Data Structures for Tamper-Evident Logging. 18th USENIX Security Symposium, 2009. https://www.usenix.org/conference/usenixsecurity09/technical-sessions/presentation/efficient-data-structures-tamper-evident

## Appendix A: Limitations and Dual-Use / Ethical Considerations

**What the results establish.** For the versions tested, on logs we generated, each count in Figure 1 is what that tool's own verifier returned. The results do not show how any tool is deployed in practice, and they say nothing about hosted services, other SDKs or later versions. Section 5 lists the limits in full.

**Dual use.** The attacks are ordinary file operations: edit, delete, cut the tail, or rebuild a log with the tool's own library. Anyone who can write to a log can already do them. ReSeal runs them only on logs it creates. A table of what each verifier accepts could still help a dishonest operator choose a weak setup. We think the benefit to auditors, buyers and maintainers is larger, for two reasons. For the four named tools, every miss is either already in the tool's documentation or follows directly from having no state outside the operator. And the remedy is a configuration step, not a secret.

**Disclosure.** Tool E's result looks like a defect and not a documented limit. Its maintainer has not been told, and no report is scheduled at the time of writing. While that is so we withhold its name, its version, verbatim quotes from its documentation and the steps to reproduce the result, and the public repository leaves out its adapter and its documentation snapshot. Its trial rows are published without name, version or verifier messages. To keep this checkable, `results/TOOL_E_COMMITMENT.md` publishes a SHA-256 digest of the withheld adapter, so that the file released later can be matched to the one used here, and the sprint organisers can have the name and the adapter on request. This still costs public reproducibility for one of five columns. We accept that cost.

**Fairness to maintainers.** Results for the named tools concern documented behaviour of public releases on one date. Documentation changes, so each quote carries a version or commit. Three of the four named tools state most of their limits clearly, and the report says so. These are small, young projects, and nothing here is evidence about their use in production.

**Risk of over-reading.** Figure 1 is not a ranking. A tool with more dark cells is not safer for a deployer who never holds the outside state. Passing every ReSeal attack also does not make a log trustworthy: no check here can see an action that was never recorded. The checkpoint is not a product. It moves trust to whoever holds it and says nothing about records written after it.

**Data and people.** No personal data and no human subjects. The workload is synthetic. Nothing was run against any system other than our own machine.

## Appendix B: Pre-sprint work

The harness was built before the sprint and is marked as pre-existing in the repository (PRE_SPRINT.md and the first commit, dated 11 November 2026). The dates are the author's statement: the first two commits were rewritten once, on 13 November, to remove the unnamed tool's name.

| When | What | Status |
| --- | --- | --- |
| 8 Nov | Track choice, survey of prior work, research questions and hypotheses | Pre-existing |
| 9 Nov | Workload generator, five tool adapters, attacks A1 to A14, controls, runner, 40 harness tests, claims codebook (empty sheet) | Pre-existing |
| 9 Nov | Two pilot runs to check the harness works (a 100-event smoke run and a 1,000-event timing run, one seed each). Their numbers are not reported here | Pre-existing |
| 11 Nov | Template read; one pilot observation re-checked with a standalone script | Pre-existing |
| 13 to 15 Nov | Both claim codings, every run reported here, the baseline, the checkpoint, the claims-versus-behaviour analysis, Claims Cards, figure, and this report | Sprint work |

Four hypotheses were written before the reported runs, but after two pilot runs, so we read the outcomes as descriptive (Table 3). Three were supported: defaults catch naive edits but accept an operator rewrite (H1), truncation and final-record deletion are the common misses without outside state (H2), and at least one verifier accepts a changed stored field (H4). One was supported only in part: headline wording claims more than the limits section (H3) clearly for Tool E, and for the named tools only at the last record.

| | Hypothesis (written 8 to 9 Nov) | Result |
| --- | --- | --- |
| H1 | Defaults catch naive edits but accept an operator rewrite; catching it needs state held outside the operator | Supported. 4 of 5 catch naive edits, 5 of 5 accept the rewrite, 3 of 5 refuse it with their own outside state, 5 of 5 with the checkpoint |
| H2 | Truncation and final-record deletion are the most common misses without outside state | Supported. They are the only outside-editor misses of the four tools that catch edits, and all five miss them |
| H3 | Headline wording claims more than the tool's own limits section | Partly. Clear for Tool E. For the named tools it shows only at the last record, and the coders agree on one case of three |
| H4 | At least one verifier accepts a changed stored field or stripped integrity fields | Supported. Tool E (7 fields), Agent Receipts (3 proof-metadata fields, by design) |

*Table 3. Hypotheses committed before the reported run, and outcomes.*

Hypotheses H1 to H4 were written on 8 and 9 November and committed before the reported runs. The pilot runs of 9 November mean they were not written blind to all data, and H4 in particular may reflect a pilot observation. No attack, control, workload or named-tool adapter was changed after the pilot. Sprint-day work was committed in batches, so commit times show when work was saved, not when it was done.

<!-- CLAIMS_CARDS -->

## LLM Usage Statement

An AI assistant (Claude, Anthropic) did most of the hands-on work. It surveyed prior work, proposed the research question, wrote the harness, ran the experiments, produced both claim codings (the second as a separate instance with no access to code or results), ran a mock review of a draft, and drafted this report. The author entered the sprint, commissioned and oversaw the work, made the disclosure decision, reviewed the results and the text, and takes responsibility for every claim. Every number in the report is recomputed from the trial files by a script in the repository, every coded quote is checked against the saved documents by a test, and every reference was opened and read.
