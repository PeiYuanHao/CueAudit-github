"""Invented handoff demo; live mode is explicit and requires provider setup."""
import argparse
import json
from pathlib import Path
from cueaudit.handoffs import run_roles, OfflineTransport
from cueaudit.openclaw_runtime import OpenClawTransport


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", type=Path, default=Path("data/toy/request.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=["offline", "live"], default="offline")
    parser.add_argument("--node", default="node")
    parser.add_argument("--openclaw-entry", type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--state", type=Path)
    args = parser.parse_args()
    if args.mode == "live" and not all((args.openclaw_entry, args.config, args.state)):
        parser.error("Live mode requires --openclaw-entry, --config and --state")
    transport = OfflineTransport() if args.mode == "offline" else OpenClawTransport(
        args.node, args.openclaw_entry, args.config, args.state)
    task = {"request": json.loads(args.request.read_text(encoding="utf-8-sig")),
            "base": str(args.request.resolve().parent)}
    run_roles(task, transport, args.output, Path(__file__).resolve().parents[1])
    print("Five-role handoff completed; inspect local artifacts. Mode:", args.mode)


if __name__ == "__main__":
    main()
