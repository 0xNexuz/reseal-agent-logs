# Sketch: carrying the checkpoint on OpenTelemetry GenAI telemetry

Status: a proposal. **Not tested with an OpenTelemetry SDK.** What is tested
is the same mechanism on a plain JSON-lines log (`plain-jsonl` baseline with
the `checkpoint` setup in `results/layer/`).

Read against the OpenTelemetry GenAI semantic conventions at commit e6658f1
(6 November 2026, https://github.com/open-telemetry/semantic-conventions-genai).
At that commit the agent and tool pages define, among others, an
`invoke_agent` span and an `execute_tool {gen_ai.tool.name}` span with the
attributes `gen_ai.operation.name`, `gen_ai.tool.name` and
`gen_ai.tool.call.id`. All are marked "Development". A search of the `docs/`
and `model/` folders for "tamper", "integrity", "checkpoint" and "digest"
finds nothing: the conventions say what a span describes, not how a reader
could tell that the exported spans were later changed.

## The missing layer, in telemetry terms

1. **Record.** Treat each finished agent or tool span, as exported, as one
   record. Use a canonical JSON form of the span (sorted keys, no extra
   whitespace) so that two exporters agree on its bytes.
2. **Running digest.** The exporter keeps `d_k = SHA-256(d_{k-1} || SHA-256(record_k))`
   with `d_0` = 32 zero bytes, and a count `k`, per trace or per agent session.
3. **Checkpoint event.** Every N spans or T seconds the exporter emits one
   small event carrying:

   | Attribute (proposed name) | Type | Meaning |
   | --- | --- | --- |
   | `audit.checkpoint.count` | int | records covered so far |
   | `audit.checkpoint.digest` | string | hex of the running digest at that count |
   | `audit.checkpoint.algorithm` | string | `sha256-prefix-v1` |
   | `audit.checkpoint.scope` | string | what the count is over, e.g. the `gen_ai.conversation.id` |

4. **Second receiver.** The event is sent to a collector the operator does
   not control (an auditor, a customer, a transparency service as in RFC
   9943). This is the whole point: the count and digest are useless if only
   the operator holds them.
5. **Check.** Given exported spans and the latest checkpoint for that scope,
   recompute the digest over the first `count` records and compare
   (`reseal/checkpoint.py`, `check`).

## What this does and does not give

- Any change to, removal of or insertion among spans covered by a checkpoint
  is refused, whoever made it, including the operator.
- Spans after the last checkpoint are not covered. The interval N or T is the
  exposure window (measured in `results/layer/` with a stale checkpoint).
- A span that was never exported is invisible. Nothing here addresses that.
- Span export is not ordered or lossless by default. A real mapping has to
  fix an order (for example by span end time and id within the scope) and
  decide what a dropped span means. That is the main open design question and
  the reason this is a sketch.
