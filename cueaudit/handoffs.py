"""Public five-role handoff driver; numerical evidence stays host-computed."""
import copy
import hashlib
import json
from pathlib import Path
from .pipeline import audit


def run_roles(task, transport, output, repository):
    """transport(role, message) returns a validated role JSON object.

    Candidates and allowed execution parameters come from the caller's request.
    Agents may select and describe them, but cannot modify manifests or policies.
    This restricted adapter is a new release example, not historical orchestration.
    """
    output, repository = Path(output).resolve(), Path(repository).resolve()
    if output.exists():
        raise ValueError("Choose a fresh output directory to avoid overwriting evidence")
    if not isinstance(task, dict) or not isinstance(task.get("request"), dict):
        raise ValueError("Task requires an explicit audit request")
    request = copy.deepcopy(task["request"])
    base = Path(task["base"]).resolve()
    candidates = request.get("candidates", [])
    if not candidates:
        raise ValueError("A user-approved candidate catalog is required")
    output.mkdir(parents=True)
    trace = []

    def turn(role, payload, keys):
        workspace = repository / "openclaw/workspaces" / role
        instructions = "\n\n".join((workspace / f).read_text(encoding="utf-8") for f in ("AGENTS.md", "SOUL.md", "TOOLS.md"))
        contract = (repository / "openclaw/protocol.md").read_text(encoding="utf-8")
        message = instructions + "\n\n" + contract + "\n\nINPUT_JSON:\n" + json.dumps(payload, ensure_ascii=False)
        reply = transport(role, message)
        if not isinstance(reply, dict) or set(reply) != set(keys):
            raise ValueError(f"{role} output does not match the protocol")
        path = output / (role + ".json")
        path.write_text(json.dumps(reply, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
        trace.append({"role": role, "output": path.name,
                      "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        return reply

    catalog = [{"index": i, "hypothesis": c["hypothesis"], "module": c.get("module")}
               for i, c in enumerate(candidates)]
    identified = turn("identify", {"dataset": request.get("dataset"), "catalog": catalog}, ["candidates", "uncertainties"])
    if not isinstance(identified["candidates"], list) or not isinstance(identified["uncertainties"], list):
        raise ValueError("Identify fields must be lists")
    proposed = set()
    for item in identified["candidates"]:
        if not isinstance(item, dict) or set(item) != {"index", "rationale"} or type(item["index"]) is not int or not 0 <= item["index"] < len(candidates) or not isinstance(item["rationale"], str):
            raise ValueError("Identify must reference only approved candidate indices")
        proposed.add(item["index"])
    routed = turn("executive", {"identify": identified, "depth": request.get("depth", "screen"),
                               "max_verifications": request.get("max_verifications")}, ["selected_indices", "routing_reason"])
    indices = routed["selected_indices"]
    if not isinstance(indices, list) or not indices or any(type(i) is not int or i not in proposed for i in indices) or len(set(indices)) != len(indices) or not isinstance(routed["routing_reason"], str):
        raise ValueError("Executive must select unique proposed candidate indices")
    request["candidates"] = [candidates[i] for i in indices]
    report = audit(request, base)
    report_path = output / "audit.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    report_hash = hashlib.sha256(report_path.read_bytes()).hexdigest()
    numerical = turn("quantitative", {"report_ref": "audit.json", "report_sha256": report_hash,
                                     "evidence": report}, ["report_ref", "report_sha256", "execution_status"])
    if numerical != {"report_ref": "audit.json", "report_sha256": report_hash, "execution_status": "host_computed"}:
        raise ValueError("Quantitative must acknowledge the exact host-computed artifact")
    qualitative = turn("qualitative", {"sample_access": "none", "candidate_hypotheses": catalog}, ["review_leads", "limitations"])
    if qualitative["review_leads"] != [] or not isinstance(qualitative["limitations"], str):
        raise ValueError("This metadata-only example provides no visual samples")
    summary = turn("summarize", {"evidence_ref": "audit.json", "evidence_sha256": report_hash,
                                "quantitative": numerical, "qualitative": qualitative},
                   ["evidence_ref", "evidence_sha256", "limitations", "review_leads"])
    if summary["evidence_ref"] != "audit.json" or summary["evidence_sha256"] != report_hash or summary["review_leads"] != [] or not isinstance(summary["limitations"], str):
        raise ValueError("Summary must preserve evidence reference and review-only status")
    artifact = {"mode": getattr(transport, "mode", "openclaw_live"), "historical_experiment": False,
                "trace": trace, "evidence_ref": "audit.json", "evidence_sha256": report_hash}
    (output / "handoff-trace.json").write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    return artifact


class OfflineTransport:
    """Deterministic protocol fixture; performs no language-model calls."""
    mode = "offline_contract_demo"

    def __call__(self, role, message):
        payload = json.loads(message.rsplit("INPUT_JSON:\n", 1)[1])
        if role == "identify":
            return {"candidates": [{"index": c["index"], "rationale": "User-supplied invented cue"} for c in payload["catalog"]], "uncertainties": ["Fixture; no autonomous discovery"]}
        if role == "executive":
            return {"selected_indices": [c["index"] for c in payload["identify"]["candidates"]], "routing_reason": "Execute supplied candidates within caller policy"}
        if role == "quantitative":
            return {"report_ref": payload["report_ref"], "report_sha256": payload["report_sha256"], "execution_status": "host_computed"}
        if role == "qualitative":
            return {"review_leads": [], "limitations": "No visual samples supplied"}
        if role == "summarize":
            return {"evidence_ref": payload["evidence_ref"], "evidence_sha256": payload["evidence_sha256"], "limitations": "Invented protocol demonstration; no historical findings or causal confirmation", "review_leads": []}
        raise ValueError("Unknown role")
