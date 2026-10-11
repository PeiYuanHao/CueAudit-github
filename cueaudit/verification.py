"""Parse externally generated, paired ID/OOD classifier evidence."""
import csv
import math
from .modules import Unsupported


def verify(spec, base):
    if not isinstance(spec, dict) or not spec.get("manifest"):
        raise Unsupported("Verification requires a paired accuracy manifest")
    if not spec.get("intervention") or not spec.get("producer"):
        raise Unsupported("Declare the intervention and evidence-producing script")
    path = (base / spec["manifest"]).resolve()
    if not path.is_file():
        raise Unsupported("Verification manifest is unavailable")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not {"seed", "id_accuracy", "ood_accuracy"}.issubset(reader.fieldnames or []):
            raise Unsupported("Verification requires seed, id_accuracy, ood_accuracy")
        rows = list(reader)
    if not rows:
        raise Unsupported("No paired verifier evidence")
    seeds, drops = set(), []
    for row in rows:
        seed = row["seed"]
        if not seed or seed in seeds:
            raise ValueError("Seed identifiers must be nonempty and unique")
        seeds.add(seed)
        a, b = float(row["id_accuracy"]), float(row["ood_accuracy"])
        if not all(math.isfinite(v) and 0 <= v <= 1 for v in (a, b)):
            raise ValueError("Accuracy must be a finite fraction in [0, 1]")
        # Remove floating-point subtraction noise at exact policy boundaries.
        drops.append(round(100 * (a - b), 12))
    return {"n_pairs": len(drops), "paired_drops_pp": drops,
            "mean_drop_pp": sum(drops) / len(drops),
            "intervention": spec["intervention"], "producer": spec["producer"],
            "source": spec["manifest"],
            "limitations": "Parsed supplied evidence; training independence and label preservation require review."}
