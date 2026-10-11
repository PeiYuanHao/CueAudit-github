"""Uncorrected categorical association, adapted from the screening scripts."""
import math
from collections import Counter, defaultdict


def categorical(cues, labels, expected=None):
    if not cues or len(cues) != len(labels):
        raise ValueError("Cue and label arrays must have equal, nonzero length")
    xs, ys = sorted(set(cues)), sorted(set(labels))
    cells = Counter(zip(cues, labels))
    nx, ny = Counter(cues), Counter(labels)
    n = len(cues)
    chi2 = sum((cells[x, y] - nx[x] * ny[y] / n) ** 2 /
               (nx[x] * ny[y] / n) for x in xs for y in ys)
    denom = n * min(len(xs) - 1, len(ys) - 1)
    v = math.sqrt(chi2 / denom) if denom else 0.0
    grouped = defaultdict(Counter)
    for x, y in zip(cues, labels):
        grouped[x][y] += 1
    metrics = {"n": n, "cramers_v": v, "chi2": chi2,
               "majority_decoding_accuracy": sum(max(c.values()) for c in grouped.values()) / n,
               "degenerate": denom == 0}
    if expected is not None:
        if len(expected) != n or any(x == "" for x in expected):
            raise ValueError("Expected cue must be supplied for every sample")
        metrics["alignment"] = sum(a == b for a, b in zip(cues, expected)) / n
        metrics["conflict"] = 1 - metrics["alignment"]
    return metrics


def foreground(values, labels):
    if not values or len(values) != len(labels):
        raise ValueError("Coverage and labels must have equal, nonzero length")
    groups = defaultdict(list)
    for value, label in zip(values, labels):
        if not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError("Foreground coverage must be a finite fraction")
        groups[label].append(value)
    if len(groups) < 2:
        raise ValueError("Class-gap screening requires at least two classes")
    means = {k: sum(v) / len(v) for k, v in sorted(groups.items())}
    return {"n": len(values), "class_means": means,
            "foreground_class_gap": max(means.values()) - min(means.values())}
