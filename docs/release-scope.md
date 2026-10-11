# Core release scope

This release separates reusable algorithms from dataset-specific experiments and
private runtime state. Core source was manually curated and refactored; no private
source-tree history was imported.

## Extraction map

| Original component | Public component | Changes |
| --- | --- | --- |
| `first_stage_screening.py` and `run_paper_experiments.py` categorical checks | `cueaudit/statistics.py` | Standalone contingency computation, input validation and explicit mapping semantics |
| `first_stage_screening.py` color/corner measurements | `cueaudit/features.py` | Isolated proxies; removed benchmark loading and generated experiment variants |
| `plant_quantitative_analysis.py` foreground mask | `cueaudit/features.py` | Retained RGB/HSV thresholds and maximum-side resizing; removed dataset traversal and analysis outputs |
| `color5.py` LAB transformations | `cueaudit/interventions.py` | Extracted grayscale normalization and masked color transfer; removed VLM calls, authentication, training and private paths |
| Identify/Executive role definitions and manuscript workflow | `agents/`, `cueaudit/pipeline.py` | Sanitized five-role contracts and a new deterministic runner |
| Paired ID/OOD workflow | `cueaudit/verification.py` | New generic evidence parser; no training runs or stored model metrics |

The Python pipeline, manifest interface, provenance records, CLI and tests are
release engineering additions. They are not claimed to be the exact software
snapshot used in the historical experiments. Selected method-bearing
Identify/Executive instructions are retained with source digests; the other
inspected SOUL.md files were generic assistant templates. New operational
workspaces and the restricted five-role adapter are marked as release additions.
Complete historical workspaces and conversations remain excluded.

## Excluded

- Manuscript and supplementary PDFs, figures, tables and numerical findings.
- Experiment scripts tied to specific datasets, benchmark results and reports.
- Datasets, sample/contact-sheet images, model checkpoints and predictions.
- Agent memories, messages, task databases, logs and private OpenClaw settings.
- API credentials, authentication files, local account identifiers and machine paths.

Demonstrations generate invented inputs locally and exercise the five-role
protocol with offline fixtures or an explicitly selected live provider. CI runs
functional checks, not the research experiments. The core release supports reuse
of the framework; it does not reproduce or substantiate manuscript results.

No reuse license has been selected in this initial release. Public availability
does not itself grant a permissive software license.
