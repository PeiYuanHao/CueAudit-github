"""Fixed-rule execution with explicit evidence and termination states."""
import math
import hashlib
from pathlib import Path
from .modules import REGISTRY, Unsupported
from .verification import verify

DEFAULT_THRESHOLDS = {"alignment": 0.80, "cramers_v": 0.50,
                      "foreground_class_gap": 0.10, "mean_drop_pp": 30.0}


def screening_rules(metrics, thresholds):
    triggers = []
    for key in ("alignment", "cramers_v", "foreground_class_gap"):
        if key in metrics:
            value = metrics[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError("Screening metrics must be finite fractions")
            if value > thresholds[key] and not (key in ("alignment", "cramers_v") and metrics.get("degenerate")):
                triggers.append(key)
    if not any(k in metrics for k in ("alignment", "cramers_v", "foreground_class_gap")):
        raise ValueError("Module returned no supported screening metrics")
    return triggers


def audit(request, base=Path(".")):
    if not isinstance(request, dict):
        raise ValueError("Request must be a JSON object")
    base = Path(base)
    thresholds = dict(DEFAULT_THRESHOLDS)
    custom = request.get("thresholds", {})
    if not isinstance(custom, dict) or set(custom) - set(thresholds):
        raise ValueError("Unknown threshold settings")
    thresholds.update(custom)
    for key, value in thresholds.items():
        upper = 100 if key == "mean_drop_pp" else 1
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= upper:
            raise ValueError("Invalid threshold")
    depth = request.get("depth", "screen")
    if depth not in ("screen", "verify"):
        raise ValueError("depth must be screen or verify")
    budget = request.get("max_verifications")
    if budget is not None and (type(budget) is not int or budget < 0):
        raise ValueError("max_verifications must be a nonnegative integer")
    candidates = request.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("At least one candidate is required")
    findings, attempts = [], 0
    for candidate in candidates:
        if not isinstance(candidate, dict) or not candidate.get("hypothesis"):
            raise ValueError("Each candidate needs a hypothesis")
        module = candidate.get("module")
        record = {"hypothesis": candidate["hypothesis"], "module": module,
                  "inputs": {k: v for k, v in candidate.items() if k not in ("review_note", "verification")},
                  "measurement": {}, "screen_triggers": [], "verification": None,
                  "model_promoted": None, "status": "unsupported"}
        record["provenance"] = {"implementation": f"cueaudit.modules:{module}",
                                "manifest_sha256": None, "verification_sha256": None}
        for field, spec in (("manifest_sha256", candidate),
                            ("verification_sha256", candidate.get("verification"))):
            if isinstance(spec, dict) and isinstance(spec.get("manifest"), str):
                source = base / spec["manifest"]
                if source.is_file():
                    record["provenance"][field] = hashlib.sha256(source.read_bytes()).hexdigest()
        note = candidate.get("review_note")
        if note:
            record["review_lead"] = {"observation": note, "status": "review_only"}
        if module not in REGISTRY:
            record["reason"] = "No registered measurement module"
            findings.append(record)
            continue
        try:
            metrics = REGISTRY[module](candidate, base)
            record["measurement"] = metrics
            record["screen_triggers"] = screening_rules(metrics, thresholds)
            promoted = bool(record["screen_triggers"])
            record["status"] = "screen_promoted" if promoted else "screen_below_threshold"
        except Unsupported as exc:
            record["reason"] = str(exc)
            findings.append(record)
            continue
        except Exception as exc:
            record["status"], record["reason"] = "failed", f"{type(exc).__name__}: {exc}"
            findings.append(record)
            continue
        # Explicit subset-rule hypotheses can request verification without an
        # aggregate promotion, with the rationale retained in the report.
        override = candidate.get("verification_reason")
        if depth == "verify" and (promoted or override):
            if override:
                record["verification_reason"] = override
            if budget is not None and attempts >= budget:
                record["status"] = "verification_incomplete"
                record["reason"] = "Verification budget exhausted"
            else:
                attempts += 1
                try:
                    result = verify(candidate.get("verification"), base)
                    record["verification"] = result
                    record["model_promoted"] = result["mean_drop_pp"] > thresholds["mean_drop_pp"]
                    record["status"] = "verified"
                except Unsupported as exc:
                    record["status"], record["reason"] = "verification_unsupported", str(exc)
                except Exception as exc:
                    record["status"], record["reason"] = "verification_failed", f"{type(exc).__name__}: {exc}"
        findings.append(record)
    return {"schema_version": "1.0", "dataset": request.get("dataset", "unnamed"),
            "depth": depth, "thresholds": thresholds, "findings": findings,
            "limitations": "Association, model response and qualitative review leads are separate evidence. Below-threshold and unsupported routes do not establish absence of shortcuts."}
