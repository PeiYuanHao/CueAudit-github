# CueAudit

**Evidence-guided shortcut screening and verification for visual datasets.**

[中文说明](README.zh-CN.md)

CueAudit connects candidate cue hypotheses to executable measurements, fixed
screening rules, and paired model-response evidence. Association, model sensitivity,
and qualitative review leads retain separate evidential status.

This repository is a **curated core-framework release**, refactored from local
screening scripts and the five-role audit workflow. It provides reusable components
and sanitized role templates. It does not contain the manuscript, experimental
results, datasets, trained weights, historical agent sessions, or private runtime
configuration. It is not a complete experiment-reproduction package.

## Quick start

Python 3.10 or newer is required. The metadata core uses only the standard library.
On Windows, run these commands in PowerShell in your chosen Python environment:

```powershell
git clone https://github.com/PeiYuanHao/CueAudit-github.git
cd CueAudit-github
python -m pip install -e .
python examples/make_toy_request.py
python -m cueaudit.cli data/toy/request.json --output outputs/toy-audit.json
python -m unittest discover -s tests -v
```

The example generator creates **invented smoke-test inputs** locally. It contains
no research dataset or saved findings. Generated inputs and reports are ignored
by Git. Reports may contain your input descriptions and file references; review
them before sharing.

For image measurements and color interventions:

```powershell
python -m pip install -e ".[images]"
```

## Core workflow

1. **Identify:** propose a potentially unintended cue and a measurable hypothesis.
2. **Executive:** select a registered measurement, inputs and verification depth.
3. **Quantitative:** run scripts and parse numerical evidence.
4. **Qualitative:** retain uncertain observations as review leads.
5. **Summarize:** assemble association, model response and limitations separately.

The core Python runner is deterministic. Full public OpenClaw workspaces and a
restricted five-role adapter are included. The offline contract demo checks
handoffs without model calls; explicit live mode invokes an isolated runtime.
Numerical evidence stays host-computed. See [OpenClaw integration](docs/openclaw.md).

```powershell
python examples/run_five_roles.py --mode offline --output outputs/five-role-demo
```

## Measurements

| Module | Required CSV columns by default | Measurement |
| --- | --- | --- |
| `metadata` | `label`, `cue` | Uncorrected Cramer's V; optional expected-cue alignment |
| `color` | `label`, `image` | Dominant mean RGB channel on resized images |
| `corner_patch` | `label`, `image` | Brightest of four corner regions |
| `foreground` | `label`, `image` | HSV/RGB foreground proxy and class-mean coverage gap |

Color and corner measurements are simple proxies, not universal cue detectors.
Background screening requires supplied metadata; no raw-image background detector
is claimed. Foreground masks are heuristic, not ground-truth segmentations.

Default escalation policies are strict `>` comparisons:

- Alignment > 0.80, **or** Cramer's V > 0.50, **or** foreground class gap > 0.10.
- Mean paired ID/OOD accuracy degradation > 30 percentage points for model escalation.

These policies are configurable operational rules, not significance tests or
universal shortcut definitions. Missing inputs stay unsupported; a budget stop
stays incomplete. A below-threshold route does not establish absence of shortcuts.
Explicit subset hypotheses may request verification with a recorded rationale.

## Inputs, verification and extension

See [the request and evidence specification](docs/interface.md) for manifests,
custom modules, status semantics and paired verifier inputs.

`cueaudit/interventions.py` exposes the extracted OpenCV LAB grayscale normalization
and masked color-transfer functions. Foreground, background and full-image swaps
use caller-supplied masks. Dataset-specific background-conflict, patch-randomization,
training and classifier-evaluation runners are outside this core release. Model
verification parses evidence produced by a user-supplied evaluation script; it does
not train models or manufacture verifier outputs.

## Source organization

```text
cueaudit/          statistics, modules, image features, interventions, pipeline, CLI
agents/            concise role descriptions
openclaw/          full public workspaces, configuration template and protocol
docs/              interface, OpenClaw setup, extraction scope
examples/          local invented-input generator
tests/             mathematical, state-transition and image checks
```

See [release scope](docs/release-scope.md) for extraction boundaries and limitations.
No experimental performance claims are published in this repository.
