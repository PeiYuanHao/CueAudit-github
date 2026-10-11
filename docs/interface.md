# Request and evidence interface

The CLI accepts a JSON object. Paths in the request are relative to the request
file; image paths are relative to their CSV manifest. The output path is relative
to the current working directory. UTF-8 CSV (including BOM) is accepted.

Example request shape (the referenced user files must be supplied):

```json
{
  "dataset": "user-dataset",
  "depth": "verify",
  "max_verifications": 2,
  "candidates": [
    {
      "hypothesis": "Background metadata may predict the target",
      "module": "metadata",
      "manifest": "metadata.csv",
      "label_column": "label",
      "cue_column": "background",
      "expected_column": "expected_background",
      "split_column": "split",
      "split": "train",
      "verification": {
        "manifest": "paired-accuracy.csv",
        "intervention": "label-preserving background conflict evaluation",
        "producer": "user evaluation script and configuration identifier"
      }
    }
  ]
}
```

Use `depth: "screen"` to collect only association evidence. Omitting
`max_verifications` permits all eligible candidates; zero permits none.
The budget counts attempted verification routes, including unsuccessful attempts.
It does not estimate GPU time, training seeds, money or language-model tokens.

`expected_column` is optional: it supplies a predeclared expected cue per sample.
Alignment is the fraction matching that mapping, not a post-hoc optimal matching.
The separately reported majority decoding accuracy is never used as alignment.
Without an expected mapping, the metadata module screens only Cramer's V.
Degenerate categorical tables retain V=0 and do not trigger categorical escalation.
Subset selection can be represented by a dedicated manifest. An explicit nonempty
`verification_reason` permits model verification even when aggregate screening is
below threshold, and remains visible in the report for review.

An image request sets `module` to `color`, `corner_patch` or `foreground`, and
provides `label` and `image` columns (or `label_column`/`image_column` overrides).
Optional split filtering works identically. Foreground coverage resizes to maximum
side 512 with bilinear interpolation and uses the extracted OpenCV-HSV mask.
Color and corner proxies resize to 32 by 32; corner windows are 6 by 6 pixels.

## Model evidence

Provide a CSV containing `seed,id_accuracy,ood_accuracy`. Each row must describe
one paired run of the same trained classifier. Seed identifiers must be unique,
and accuracies must be finite fractions in [0,1]. The parser computes
`100 * (id_accuracy - ood_accuracy)` per row and its arithmetic mean.
Per-pair drops are rounded to 12 decimal places to remove floating-point
subtraction noise at exact policy boundaries.

Declare the evaluation-producing script/configuration and intervention in the
request. The parser checks the file format; the user is responsible for verifying
that the recorded seeds are independent, pairing is valid, labels are preserved,
and intervention artifacts do not invalidate interpretation. The core does not
perform confidence intervals, significance testing or seed bootstrap analyses.

## Evidence states

| Status | Meaning |
| --- | --- |
| `unsupported` | No module or required screening inputs |
| `failed` | Screening execution or input validation failed |
| `screen_below_threshold` | Measured evidence below the screening policies |
| `screen_promoted` | Screening policy triggered; no model evidence yet |
| `verification_incomplete` | Verification budget exhausted |
| `verification_unsupported` | Required model evidence unavailable |
| `verification_failed` | Invalid model evidence or execution error |
| `verified` | Paired evidence parsed; inspect `model_promoted` separately |

`review_note` is retained as `review_lead` with `review_only` status and never
changes numerical decisions. `verified` does not mean a causal defect is confirmed.
Screening metrics and triggers remain present even if verification fails.
Reports record the declared input specification, source manifest hashes,
measurement module, actual metrics, thresholds, verifier source and limitations.
Keep external scripts and image inputs available for complete replay.

## Custom modules

For trusted local Python extensions, call
`cueaudit.modules.register(name, function)` before `cueaudit.audit(request, base)`.
The function accepts `(candidate, base_path)` and returns a dictionary of parsed
measurements containing at least one of `alignment`, `cramers_v`, or
`foreground_class_gap`. Return values must be finite fractions. Missing inputs
raise `Unsupported`; other exceptions produce `failed` records. Never supply
free-form agent-generated numbers as quantitative evidence. The CLI does not
load arbitrary commands or plugins from JSON requests.
