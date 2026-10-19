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

## Examples

Every command and every line of output below was really run against this
repository. Nothing here is illustrative.

### Set up

ControlLoop has no published package yet, so clone it next to this
repository and run it from source. You need Python 3.12, git, and
[uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/controlloop-security/controlloop
git clone https://github.com/controlloop-security/controlloop-reference-agent
(cd controlloop && uv sync --locked)
cd controlloop-reference-agent
alias controlloop='uv run --project ../controlloop controlloop'
```

Run every example below from the root of this repository, and always
pass the scenario directory: with no path, ControlLoop scans the whole
repository, which has no manifest of its own.

### Scan the approved agent

`scan` reports what an agent can do right now. The report opens with the
single worst thing it can reach.

```bash
controlloop scan scenarios/order-support-agent
```

```text
! WORST REACHABLE  financial-action: widgetworks-order-support-agent can invoke
  Issue a refund

✓ PASSED

• material change: not evaluated

! MEDIUM   policy.undeclared-tools: Tool 'Look up an order' is reachable but not
  declared in controlloop.yaml.
    at agent-card.json

! MEDIUM   policy.undeclared-tools: Tool 'Reply to customer' is reachable but
  not declared in controlloop.yaml.
    at agent-card.json

! MEDIUM   policy.undeclared-tools: Tool 'Issue a refund' is reachable but not
  declared in controlloop.yaml.
    at agent-card.json

Suppressions: none declared
```

For a step-by-step walkthrough of this agent (running it, drafting a
manifest, building the capability graph, and gating a change), see
[`scenarios/order-support-agent/SCAN.md`](scenarios/order-support-agent/SCAN.md).

### Gate a change that adds a dangerous tool

`gate` compares a branch against `main` the way CI compares a pull
request against its base. On `scenario/capability-expansion`, the support
agent gains a bulk-refund tool:

```bash
git checkout scenario/capability-expansion
controlloop gate scenarios/order-support-agent
```

```text
! WORST REACHABLE  destructive-action: widgetworks-order-support-agent can
  invoke Bulk refund orders

✕ DEPLOYMENT BLOCKED

• material change: not evaluated

✕ HIGH     policy.destructive-or-financial-action: Agent gained new direct
  invokes access to 'Bulk refund orders', classified as destructive-action and
  financial-action.
    at agent-card.json
```

The four `policy.undeclared-tools` findings that follow are trimmed here.
The gate exits `1`, which fails the CI check.

### Gate a change that removes authority

Taking authority away passes, and the report still names what was given
up:

```bash
git checkout scenario/capability-reduction
controlloop gate scenarios/support-triage-agent
```

```text
! WORST REACHABLE  sensitive-data-access: support-triage-agent can invoke Read a
  customer record

✓ PASSED

• REDUCED  destructive-action: support-triage-agent no longer invokes Purge
  ticket history
• REDUCED  sensitive-data-access: support-triage-agent no longer invokes Purge
  ticket history
• REDUCED  write-access: support-triage-agent no longer invokes Purge ticket
  history
✓ PASSED   capability reduced only -- no new authority gained

• no findings
```

### Gate a coding agent's widened permission

ControlLoop reads coding agents' own configuration too. On
`scenario/allow-list-widened`, a Claude Code allow rule goes from
`Bash(npm test)` to `Bash(*)`:

```bash
git checkout scenario/allow-list-widened
controlloop gate scenarios/storefront-agent-config
```

```text
! WORST REACHABLE  code-execution: Claude Code can invoke PostToolUse command
  hook (Edit|Write)

✕ DEPLOYMENT BLOCKED

Authority:
  • This change gives Claude Code the power to use `Bash(*)` without asking (a
    wildcard) (`.claude/settings.json`, rule `Bash(*)`). No approval is
    recorded.

• no material capability change

✕ HIGH     policy.widened-permission-rule: Allow rule for 'Claude Code' widened
  from 'Bash(npm test)' to 'Bash(*)'.
    at .claude/settings.json
```

### Gate an MCP server whose package changed

On `scenario/mcp-package-drift`, an MCP server keeps its name but runs a
new package version:

```bash
git checkout scenario/mcp-package-drift
controlloop gate scenarios/storefront-agent-config
```

```text
✕ DEPLOYMENT BLOCKED

Authority:
  • This change gives Claude Code the power to start MCP server `catalog-docs`
    by running `npx -y @widgetworks-example/catalog-docs-mcp@1.5.0`, whose
    declaration or tool list changed (`.mcp.json`, server `catalog-docs`). No
    approval is recorded.

• no material capability change

✕ HIGH     policy.mcp-server-identity-change: Server 'catalog-docs' kept its
  name but its identity changed: package version from '1.4.2' to '1.5.0', args
  from '-y @widgetworks-example/catalog-docs-mcp@1.4.2' to '-y
  @widgetworks-example/catalog-docs-mcp@1.5.0', declaration digest.
    at .mcp.json
```

The `WORST REACHABLE` line is the same as in the previous example and is
trimmed here.

### Gate against your organization's approved components (Team)

The three `scenario/team-*` branches run a Team gate with the
organization's policy bundle committed in the gate's own cache, so they
work with no platform behind them. Set the token to the offline value the
scenarios use:

```bash
git checkout scenario/team-unsanctioned-grant
CONTROLLOOP_TEAM_TOKEN=offline-reference-scenario-not-a-secret \
  controlloop gate scenarios/storefront-agent-config
```

```text
! REVIEW REQUIRED

Authority:
  • This change gives Claude Code the power to start MCP server `catalog-search`
    by running `npx -y @widgetworks-example/catalog-search-mcp@2.1.0`
    (`.mcp.json`, server `catalog-search`). No approval is recorded.
  • This change gives Claude Code the power to start MCP server `web-fetch` by
    running `npx -y @webfetch-tools/web-fetch-mcp@0.3.1` (`.mcp.json`, server
    `web-fetch`). No approval is recorded.

• GAINED  code-execution: Claude Code invokes catalog-search
• GAINED  code-execution: Claude Code invokes web-fetch

! MEDIUM   policy.unsanctioned-agent-component: The mcp_server `web-fetch` is
  not approved by organization policy version 12: its package is not the
  approved package (constraint `package`).
    at .mcp.json
```

The gate exits `3` (review required). Trimmed here: the `TEAM STATUS` and
`TEAM UPLOAD` lines on standard error, which say the gate used its cached
bundle because no platform answered; the `WORST REACHABLE` line; and two
`policy.mcp-server-identity-change` findings for the new servers. The
whole run is in
[Your first Team gate](https://github.com/controlloop-security/controlloop/blob/main/docs/guides/first-team-gate.md).

### Notes

- Each `gate` run writes `evidence.json` to the current directory, the
  retainable record of the verdict. Pass `--evidence-path` to put it
  elsewhere, or `--format json` or `--format sarif` to print it instead
  of the text report.
- Exit codes: `0` passed, `1` blocked, `3` review required. The full
  table is in the
  [CLI reference](https://github.com/controlloop-security/controlloop/blob/main/docs/reference/cli.md).
- Each scenario branch records the exact verdict and findings CI asserts
  in `expected/*.json` under its scenario directory. The
  `capability-expansion`, `ceiling-breach`, and `capability-reduction`
  branches also explain their change in a `SCENARIO` note at the
  repository root.

## Issues and pull requests

This repository is for demonstration only and does not accept support
requests. For questions, bugs, or feature requests about the ControlLoop
CLI, use
[`controlloop-security/controlloop`](https://github.com/controlloop-security/controlloop/issues).

## License

Apache License 2.0, the same as ControlLoop.
