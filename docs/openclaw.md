# Five-role public workspaces and OpenClaw adapter

The repository includes full public workspaces under `openclaw/workspaces/`.
Each role has AGENTS.md, SOUL.md, TOOLS.md, IDENTITY.md, USER.md, HEARTBEAT.md and
SOURCE.md. Selected original method instructions for Identify and Executive are
retained separately in ORIGINAL_METHOD.md. The remaining operational files are
release additions, not verbatim historical workspaces. See
[provenance](../openclaw/provenance.json).

The inspected runtime reports OpenClaw 2026.3.12 (6472949). Its current role
registrations use `openai-codex/gpt-5.5`. This is a current configuration
observation, not proof of historical experiment settings. Historical sampling
parameters were not established. Public configuration uses a model placeholder.

## Offline contract demo

Install the core package, then run from the repository root:

```powershell
python examples/make_toy_request.py
python examples/run_five_roles.py --mode offline --output outputs/five-role-demo
```

This exercises all five handoffs with deterministic response fixtures and actual
host measurements on invented metadata. It makes zero model calls and tests
wiring/evidence integrity, not autonomous reasoning. Choose a fresh output
directory per run; existing evidence is never overwritten.

## Prepare an isolated runtime

```powershell
python examples/prepare_openclaw.py --destination outputs/public-runtime --model YOUR_PROVIDER/YOUR_MODEL
```

The script copies only public templates and writes an isolated configuration with
separate agent directories. It never reads or changes your private OpenClaw
configuration and does not copy credentials, memories, channels or bindings.
Supply a provider/model available in your own installation.

Locate your installed `node_modules/openclaw/openclaw.mjs` entry point and Node
executable. These paths stay local. Validate in PowerShell:

```powershell
$env:OPENCLAW_CONFIG_PATH = (Resolve-Path outputs/public-runtime/openclaw.json).Path
$env:OPENCLAW_STATE_DIR = (Resolve-Path outputs/public-runtime/state).Path
node YOUR_OPENCLAW_ENTRY config validate
```

These variables affect the current shell. The Python adapter sets them only for
its child processes. Configure provider authentication in the isolated runtime
using provider environment variables or the installed OpenClaw authentication
mechanism. Auth is per-agent; do not assume an existing main-agent login is shared.

## Live five-role execution

After provider setup, explicitly opt into model calls:

```powershell
python examples/run_five_roles.py --mode live --output outputs/live-demo --openclaw-entry YOUR_OPENCLAW_ENTRY --config outputs/public-runtime/openclaw.json --state outputs/public-runtime/state
```

Add `--node YOUR_NODE_EXECUTABLE` when Node is not on PATH. The adapter invokes
`agent --local --agent ... --session-id ... --message ... --json --timeout ...`
once per role, using fresh run-specific sessions. It uses no `--deliver` or
external communication channel. Live model calls consume provider usage and send
the supplied task/evidence to the selected provider.

The public model turns have execution tools disabled. A trusted Python bridge
runs registered measurements after Executive selects approved candidate indices.
Quantitative acknowledges the exact report hash. This restricted bridge is a
new adapter, not the broader original tool configuration.

See [the handoff protocol](../openclaw/protocol.md) for schemas, stops and failure
handling. Reports, role replies and hashes stay under ignored local directories.
Failure stops the chain; no live-to-offline fallback is performed.

## Validation boundary

The offline chain, artifact-hash checks, response parsing and isolated preparation
are tested. The prepared configuration was validated against the installed
OpenClaw schema. Live provider turns have not been executed for this release.
Provider compatibility and stochastic schema compliance require local checks.
The restricted example uses an approved candidate catalog and no visual samples;
it does not demonstrate blind discovery or historical result reproduction.

No private settings, auth files, sessions, memories or research results are included.
