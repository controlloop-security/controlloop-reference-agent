# Storefront agent configuration

A fictional storefront ("Widgetworks") whose coding agents, dev container
and pre-commit hooks are configured the way a careful team would configure
them. It demonstrates ControlLoop's agent authority diff, and Clone-time
protection: the files that install tools and run scripts every time the
repository is opened or committed to.

On `main` it is the approved starting point:

| File | What it grants |
| --- | --- |
| `.claude/settings.json` | A Prettier hook after edits, `Bash(npm test)` without asking, `Read(./.env)` denied, and a marketplace pinned to a commit |
| `.mcp.json` | One MCP server, `catalog-docs`, pinned to version `1.4.2` |
| `.github/workflows/claude-review.yml` | A review workflow with a read-only token |
| `.pre-commit-config.yaml` | One hook repository, `widgetworks-example/storefront-hooks`, pinned to a full commit SHA |

Each scenario branch changes one thing, the way a real pull request would:

| Branch | The change | The incident pattern |
| --- | --- | --- |
| `scenario/session-start-harvester-hook` | A `SessionStart` hook that runs `node .github/setup.js` | The committed-hook payloads of the Miasma worm, Mini Shai-Hulud, and CVE-2026-25725 |
| `scenario/mcp-package-drift` | `catalog-docs` moves from `1.4.2` to `1.5.0` under the same name | A server's code changing behind a name a reviewer already trusts |
| `scenario/allow-list-widened` | `Bash(npm test)` becomes `Bash(*)` | A one-line change that hands the agent every shell command |
| `scenario/agent-workflow-id-token` | The review workflow gets `id-token: write` and `--dangerously-skip-permissions` | An agent that can mint cloud credentials and never asks |
| `scenario/pinned-plugin-added` | A plugin from the pinned marketplace is enabled | A benign change that must not fail |
| `scenario/devcontainer-extension-added` | A new `.devcontainer/devcontainer.json` auto-installs the extension `widgetworks-example.storefront-tools` with no `@version`, and runs `node .devcontainer/post-create.js` as its `postCreateCommand` | A poisoned marketplace extension, or a setup step, that installs and runs on every machine that opens the repository |
| `scenario/pre-commit-rev-moved` | The hook repository's `rev` moves from a full commit SHA to the tag `v2.4.0` | Hook code that can change upstream, then run on every commit, with no change in this repository |

## Clone-time scenarios: what the gate says

Both were run with ControlLoop 0.7.1 (`controlloop gate
scenarios/storefront-agent-config --default-branch main`):

- `scenario/devcontainer-extension-added` is **blocked** (exit `1`) by
  `policy.agent-hook-command-change` at `high`: "Added: Setting
  'postCreateCommand' for host 'Dev Containers' runs `node
  .devcontainer/post-create.js`." The unpinned extension is reported by
  `policy.unpinned-agent-component` at `medium`: "Added: Editor extension
  widgetworks-example.storefront-tools (editor-extension) has no commit or
  digest pin."
- `scenario/pre-commit-rev-moved` **passes** (exit `0`) at the default
  `high` threshold, with one `policy.unpinned-agent-component` finding at
  `medium` naming the hook repository and saying it has no commit or digest
  pin. That rule reports a changed pin or source at `medium`, so a
  repository that sets `severity_threshold = "medium"` in
  `controlloop.toml` blocks this change (checked with the same version).

The pre-commit branch starts from the commit on `main` that adds the
SHA-pinned `.pre-commit-config.yaml`, so the gate sees the `rev` move
rather than a new file.

## The Team scenarios: an approved-components list

Three more branches run the same storefront as a **Team** repository whose
organization keeps a list of approved agent components. They prove the paid gate on a real repository against a real
policy bundle, with no platform deployed:

| Branch | The change | The outcome |
| --- | --- | --- |
| `scenario/team-sanctioned-grant` | Adds the MCP server `catalog-search`, which the bundle approves by package, version range, and digest | Passes (exit `0`); the grant is judged `sanctioned` by bundle version `12` |
| `scenario/team-unsanctioned-grant` | Also adds `web-fetch`, running `@webfetch-tools/web-fetch-mcp` under a name the bundle approves only for `@widgetworks-example/web-fetch-mcp` | Review required (exit `3`); one `policy.unsanctioned-agent-component` finding naming constraint `package` |
| `scenario/team-no-published-bundle` | The same two servers, with no published bundle | Passes (exit `0`); both grants are `unevaluated`, with no finding, and the evidence says so |

Each branch commits three things beside the change:

- `controlloop.toml` turns Team on, with an endpoint nothing listens on
  and `team_fail_mode = "open"`.
- `.controlloop/team-cache/policy.json` is the organization's effective
  policy as the gate caches it. Every approved-component constraint field is in it.
  `command_pattern` and `pin_required` cover the hook and marketplace
  already on `main`, which a change that leaves them alone does not
  re-judge.
- `expected/<scenario>.json` is recorded from a real gate run, including
  the sanction judgments and the bundle version that made them.

The gate says on standard error that the platform could not be reached,
and records `policy_source: stale_cache` and `entitlement_state:
unreachable` in its evidence. That is how a Team gate behaves offline
when its repository chose to fail open. It is shown here on purpose: a
real Team repository would keep the default `closed` fail mode and a
reachable endpoint.

## Everything here is inert

- `.github/setup.js` on the hook branch does nothing and exits. It stands
  in for a harvester; it reads no file, no environment variable, and no
  network.
- `@widgetworks-example/catalog-docs-mcp` is a fictional package. Nothing
  in this repository installs or runs it.
- The workflow lives under `scenarios/`, so GitHub never runs it, and it
  names a secret without holding one.
- `widgetworks-example/claude-plugins` is a fictional repository and the
  commit it is pinned to is made up.
- `widgetworks-example/storefront-hooks` and its commit and tag, and the
  extension `widgetworks-example.storefront-tools`, are fictional. Nothing
  here installs them.
- `.devcontainer/post-create.js` on the dev container branch does nothing
  and exits.

## Expectations

Each branch commits `expected/<scenario>.json`, recorded from a real
`controlloop gate` run: the verdict, the exit code, the rules that fired,
the authority statements, and the blast radius. The ControlLoop
reference-scenario workflow runs the published Action against each branch
and asserts them.
