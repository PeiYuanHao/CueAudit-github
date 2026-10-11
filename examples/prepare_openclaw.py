"""Create a fresh isolated runtime from public files only."""
import argparse
from pathlib import Path
from cueaudit.openclaw_runtime import prepare

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--model", required=True, help="Your provider/model identifier")
    args = parser.parse_args()
    path = prepare(Path(__file__).resolve().parents[1], args.destination, args.model)
    print("Prepared isolated runtime:", path)
