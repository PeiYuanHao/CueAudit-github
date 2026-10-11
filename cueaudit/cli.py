import argparse
import json
from pathlib import Path
from .pipeline import audit


def main():
    parser = argparse.ArgumentParser(description="Run registered CueAudit measurements")
    parser.add_argument("request", type=Path, help="JSON request; paths relative to this file")
    parser.add_argument("--output", type=Path, required=True, help="Local report destination")
    args = parser.parse_args()
    try:
        request = json.loads(args.request.read_text(encoding="utf-8-sig"))
        report = audit(request, args.request.resolve().parent)
        text = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False)
    except (ValueError, OSError, TypeError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text + "\n", encoding="utf-8")
    print("Audit report written.")
    failed = {"failed", "verification_failed"}
    if any(f["status"] in failed for f in report["findings"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
