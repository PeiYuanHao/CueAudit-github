# Five-role handoff protocol

Status: newly specified for the public release. The original session messages and
their routing identifiers are not published. Return one JSON object, without
commentary or additional keys. Each turn receives an INPUT_JSON envelope.

The example driver supplies a caller-approved candidate catalog. Free-form
candidate discovery and unrestricted tool execution remain outside this adapter.
Manifest paths, thresholds, depth and budgets remain controlled by the caller.

| Role | Input | Exact output keys |
| --- | --- | --- |
| Identify | Dataset description and candidate catalog | `candidates`, `uncertainties` |
| Executive | Identify output, caller depth and budget | `selected_indices`, `routing_reason` |
| Quantitative | Host-computed report, reference and SHA-256 | `report_ref`, `report_sha256`, `execution_status` |
| Qualitative | Explicit sample-access scope and hypotheses | `review_leads`, `limitations` |
| Summarize | Evidence reference/hash and the two analysis handoffs | `evidence_ref`, `evidence_sha256`, `limitations`, `review_leads` |

## Identify

`candidates` is a list of objects with exactly `index` (integer from the supplied
catalog) and `rationale` (string). `uncertainties` is a list. Propose no unapproved
indices, numerical results or file paths. This example measures routing of known
candidate definitions, not blind discovery.

## Executive

`selected_indices` is a nonempty list of unique indices proposed by Identify.
`routing_reason` is a string. Do not change the caller's execution policy.
After this turn the trusted Python driver executes the selected measurement
modules, retaining unsupported routes and failures in the report.

## Quantitative

Copy the supplied `report_ref` and `report_sha256` exactly. Set
`execution_status` to `host_computed`. The host already performed the numerical
work. Do not recompute or add values through model generation.

## Qualitative

This minimal metadata-only example supplies no visual samples. Return
`review_leads: []` and a string `limitations` explaining that visual observations
are unavailable. Do not claim to have inspected images.

## Summarize

Copy `evidence_ref` and `evidence_sha256` exactly. Return a string `limitations`
and preserve the empty `review_leads`. The artifact reference, rather than a
rewritten numerical table, is authoritative. Association is distinct from model
reliance and causal confirmation.

## Execution and stops

The driver runs Identify -> Executive -> host measurement -> Quantitative ->
Qualitative -> Summarize. Roles are separate sequential turns. Every role reply
is checked before the next step. Invalid JSON, forbidden selection, changed
artifact hashes, timeout or provider failure stops execution. Earlier files are
retained locally, and no completed trace is produced on failure. The driver does
not silently replace a failed live turn with an offline fixture.

The final handoff trace records role output hashes, the numerical evidence hash,
execution mode and `historical_experiment: false`. Outputs and runtime state stay
under ignored local directories. They are demonstration artifacts, not manuscript
findings.
