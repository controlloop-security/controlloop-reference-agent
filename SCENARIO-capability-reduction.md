# Scenario: capability reduction

Branch `scenario/capability-reduction`.

## The change

Against the declared base on `main`, this branch:

- **removes a tool** — the `purge-ticket-history` skill is deleted from
  `agent-card.json`;
- **narrows a permission** — `dynamodb:DeleteItem` and `s3:DeleteObject`
  are dropped from `iam/policy.json`.

Nothing is gained. Authority only shrinks.

## Real recorded output

```
$ controlloop gate scenarios/support-triage-agent
! WORST REACHABLE  sensitive-data-access: support-triage-agent can invoke Read
  a customer record

✓ PASSED

• REDUCED  destructive-action: support-triage-agent no longer invokes Purge
  ticket history
• REDUCED  sensitive-data-access: support-triage-agent no longer invokes Purge
  ticket history
• REDUCED  write-access: support-triage-agent no longer invokes Purge ticket
  history
✓ PASSED   capability reduced only -- no new authority gained

• no findings

$ echo $?
0
```

What that output shows:

| | |
| --- | --- |
| The change | a tool removed and a permission narrowed |
| The verdict | the gate passes, exit 0 |
| The reductions | each named **by material class** — `destructive-action`, `sensitive-data-access`, `write-access` |
| The findings | `• no findings` — the reduction produces none |

## Why the merge-base path matters

Naming a reduction by material class needs a `MaterialChangeSummary`,
which needs both sides' full graphs, which only the merge-base baseline
path builds, including for a scan root that is a subdirectory of the
repository, as every scenario here is.

It is also why the base scenario deliberately carries **no committed
baseline**: a committed baseline holds only `effective_authority`, not
the graphs, and short-circuits the merge-base path.
