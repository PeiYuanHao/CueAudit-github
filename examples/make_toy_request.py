"""Generate invented local inputs for a smoke test, never paper results."""
import csv
import json
from pathlib import Path


def main():
    target = Path("data/toy")
    target.mkdir(parents=True, exist_ok=True)
    with (target / "manifest.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["label", "cue", "expected_cue", "split"])
        for i in range(40):
            label = str(i % 2)
            writer.writerow([label, label, label, "train"])
    request = {"dataset": "invented-smoke-test", "depth": "screen", "candidates": [
        {"hypothesis": "An invented metadata cue may predict the label",
         "module": "metadata", "manifest": "manifest.csv", "split": "train",
         "expected_column": "expected_cue"}]}
    (target / "request.json").write_text(json.dumps(request, indent=2), encoding="utf-8")
    print("Invented inputs created under data/toy.")


if __name__ == "__main__":
    main()
