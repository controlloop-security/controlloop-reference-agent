# Scenario: exfiltration triangle

A pull request that wires the support agent to the **public inbox** is
**blocked in CI** with one combined finding: the agent can now read
confidential order data, take instructions from anyone on the internet,
and send email out. Each of those alone was fine. Together they are the
classic prompt-injection-to-exfiltration path, and the gate names all
three legs in one finding instead of three unrelated ones.

> **DO NOT MERGE.** This pull request *is* the artifact. Merging it puts
> the third leg onto `main`, which breaks the base scenario for everyone
> who forks this repository and removes the diff the proof depends on.

## What the pull request does

Support asked for tickets to reach the agent straight from the inbox
instead of being pasted in by a person. So this pull request adds:

| | Change |
| --- | --- |
| **code** | `src/order_support/inbox.py`, which reads unread tickets from the public mailbox and hands their text to the agent unchanged |
| **a declaration** | `external_inputs` in `controlloop.yaml`: `widgetworks-order-support-agent` takes input from `customer support inbox` |

The two legs that were already there, on `main`, come from the existing
`tool_capabilities` block: `Look up an order` reads `confidential` data
and `Reply to customer` communicates externally. Nothing about them
changes here.

## What the gate does

See `expected/exfiltration-triangle.json` for the exact finding, and
ControlLoop's `docs/reference/reference-agent.md` for the recorded
terminal output.

Exit code `1`.

## How to read that

**One finding, three legs.** The message names each leg and the path to
it: sensitive-data access through `Issue a refund` (declared
`confidential`), untrusted input from `customer support inbox`, external
communication through `Reply to customer`. Remove any one leg and the finding goes away; the rule never
fires on two.

**The declaration is what the gate sees.** Discovery cannot read "this
agent is wired to the public inbox" out of `inbox.py`; the repository
declares it, and the declaration is authoritative. Had the agent card
published a `url` instead, the gate would have *inferred* an input and
reported the same triangle at `medium`, below the blocking threshold,
asking for exactly this declaration.

## What it proves

| Claim | Where |
| --- | --- |
| The base state has two legs and no triangle finding | `main`: `controlloop gate scenarios/order-support-agent` passes |
| The pull request adds the third leg and produces one top-severity finding | `policy.exfiltration-triangle`, CRITICAL; exit `1` |
| The finding names all three legs and the path establishing each | `expected/exfiltration-triangle.json` → `blocking_run.ceiling_finding.message` |
| Removing any one leg clears the finding | the rule's own tests in `controlloop-security/controlloop`; here, revert either file |
