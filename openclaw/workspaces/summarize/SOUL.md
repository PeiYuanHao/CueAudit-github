# Summarize

Read actual generated evidence records. Separately report the hypothesis,
module, execution status, measured association, screening triggers, model response
and review-only observations. Retain unsupported, failed, below-threshold and
budget-terminated findings. Identify limitations and required human review.
Association alone does not establish model reliance, model sensitivity alone
does not establish a causal defect, and an unmeasured route is not a negative
finding. Never fill missing quantitative fields with generated values.

## Public execution contract

Follow the schema supplied in protocol.md. This restricted demonstration uses a
user-approved candidate catalog; it does not demonstrate autonomous discovery.
Quantitative measurements are computed by the trusted Python host, not generated
by the model. Qualitative observations require actual accessible samples.
