"""Registered executable measurements; paths resolve relative to the manifest."""
import csv
from pathlib import Path
from .statistics import categorical, foreground


class Unsupported(ValueError):
    """Required measurement inputs are unavailable."""


def read_rows(candidate, base):
    if "manifest" not in candidate:
        raise Unsupported("A CSV manifest is required")
    path = (base / candidate["manifest"]).resolve()
    if not path.is_file():
        raise Unsupported("Manifest is unavailable")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames or []
        required = [candidate.get("label_column", "label")]
        if candidate.get("split") is not None:
            required.append(candidate.get("split_column", "split"))
        if any(k not in fields for k in required):
            raise Unsupported("Required label or split column is unavailable")
        rows = list(reader)
    if candidate.get("split") is not None:
        rows = [r for r in rows if r[candidate.get("split_column", "split")] == str(candidate["split"])]
    if not rows:
        raise Unsupported("No samples are available for the selected split")
    if any(not r.get(required[0]) for r in rows):
        raise ValueError("Every sample must have a label")
    return path, fields, rows


def metadata(candidate, base):
    _, fields, rows = read_rows(candidate, base)
    cue = candidate.get("cue_column", "cue")
    expected = candidate.get("expected_column")
    if cue not in fields or (expected and expected not in fields):
        raise Unsupported("Required cue columns are unavailable")
    if any(not r.get(cue) for r in rows):
        raise ValueError("Every sample must have a measured cue")
    return categorical([r[cue] for r in rows],
                       [r[candidate.get("label_column", "label")] for r in rows],
                       [r[expected] for r in rows] if expected else None)


def images(candidate, base):
    from .features import measure
    path, fields, rows = read_rows(candidate, base)
    column = candidate.get("image_column", "image")
    if column not in fields:
        raise Unsupported("Image column is unavailable")
    values = []
    for row in rows:
        image = path.parent / row[column]
        if not row[column] or not image.is_file():
            raise Unsupported("A referenced image is unavailable")
        values.append(measure(image, candidate["module"]))
    labels = [r[candidate.get("label_column", "label")] for r in rows]
    if candidate["module"] == "foreground":
        return foreground(values, labels)
    return categorical(values, labels)


REGISTRY = {"metadata": metadata, "color": images, "corner_patch": images,
            "foreground": images}


def register(name, function):
    """Register a trusted Python measurement returning parsed numeric metrics."""
    if name in REGISTRY:
        raise ValueError("Module already registered")
    REGISTRY[name] = function
