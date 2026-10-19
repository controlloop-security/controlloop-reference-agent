# controlloop-reference-agent

> **⚠️ DELIBERATELY VULNERABLE — DO NOT DEPLOY, DO NOT REUSE CODE FROM THIS REPOSITORY.**
>
> Every agent, tool declaration, and capability manifest in this repository is
> constructed on purpose to exhibit specific, unsafe capability patterns —
> capability expansion, ceiling breaches, unresolvable tool bindings,
> widened agent permissions, and similar findings — so that
> [ControlLoop](https://github.com/controlloop-security/controlloop) has a real,
> versioned target to scan in CI and in its own documentation. None of it is
> safe, none of it is production code, and none of it should be copied into a
> real agent.

## What this is

A fixture repository maintained alongside the ControlLoop CLI. It holds a
small set of scenario agents, each demonstrating one class of capability
finding that ControlLoop detects. It exists to prove, with real, runnable,
scanned output rather than a description, that the scanner behaves as
documented against agents that are not synthetic unit-test fixtures.

## How it is used

- This repository is a companion to
  [`controlloop-security/controlloop`](https://github.com/controlloop-security/controlloop),
  the open-source CLI that implements the scanner. It contains no scanner
  code of its own.
- `main` holds each scenario's approved starting point. Each `scenario/*`
  branch is one pull request's worth of change on top of it, so the gate
  compares the branch against `main` exactly as it would compare a real
  pull request against its base.
- ControlLoop's reference-scenario workflow runs the published GitHub
  Action against every branch on a schedule and on every release, and
  asserts the verdict, findings, and statements each branch records in its
  `expected/*.json`. A scenario that stops matching current ControlLoop
  behavior is a bug in this repository, not a change to the scanner's
  contract.

## Scenarios

Each scenario directory is its own scan root: point `controlloop` at the
directory, not at the repository root.

| Directory | Demonstrates |
| --- | --- |
| [`scenarios/order-support-agent/`](scenarios/order-support-agent/) | The base "currently approved" support agent, runnable with `uv run order-support`. See [`SCAN.md`](scenarios/order-support-agent/SCAN.md) for a walkthrough with real output |
| [`scenarios/support-triage-agent/`](scenarios/support-triage-agent/) | The base for a capability reduction: a gate that passes while naming what was given up |
| [`scenarios/research-crew/`](scenarios/research-crew/) | A CrewAI crew whose publishing agent builds its tool list at runtime: zero findings, and still not safe |
| [`scenarios/research-graph/`](scenarios/research-graph/) | A LangGraph graph with a runtime router and an unreadable publish step |
| [`scenarios/support-desk/`](scenarios/support-desk/) | An OpenAI Agents SDK desk where a customer-facing agent reaches a refund in three handoffs |
| [`scenarios/storefront-agent-config/`](scenarios/storefront-agent-config/) | Coding-agent configuration (Claude Code settings, hooks, MCP servers, plugins, an agent-running workflow) and the approved-components list |

| Branch | The change | Result |
| --- | --- | --- |
| `scenario/capability-expansion` | The support agent gains a bulk-refund tool, an API route, and a broad IAM grant | Blocked |
| `scenario/ceiling-breach` | The support agent gains a skill its capability ceiling prohibits, with every pattern rule suppressed | Blocked by the ceiling alone |
| `scenario/capability-reduction` | The triage agent loses its purge tool and delete permissions | Passes, naming each reduction |
| `scenario/session-start-harvester-hook` | A `SessionStart` hook that runs `node .github/setup.js` | Blocked |
| `scenario/mcp-package-drift` | An MCP server's package version changes under the same name | Blocked |
| `scenario/allow-list-widened` | `Bash(npm test)` becomes `Bash(*)` | Blocked |
| `scenario/agent-workflow-id-token` | The review workflow gets `id-token: write` and skips permission prompts | Blocked |
| `scenario/pinned-plugin-added` | A plugin from the pinned marketplace is enabled | Passes |
| `scenario/team-sanctioned-grant` | A Team gate: an MCP server the organization approved | Passes |
| `scenario/team-unsanctioned-grant` | A Team gate: an MCP server running a lookalike package | Review required |
| `scenario/team-no-published-bundle` | A Team gate with no published policy bundle | Passes, with both grants unevaluated |

Do not merge a scenario branch into `main`. The branch is the artifact:
merging it would move the change into the baseline and remove the diff the
scenario depends on.

## Issues and pull requests

This repository is for demonstration only and does not accept support
requests. For questions, bugs, or feature requests about the ControlLoop
CLI, use
[`controlloop-security/controlloop`](https://github.com/controlloop-security/controlloop/issues).

## License

Apache License 2.0, the same as ControlLoop.
