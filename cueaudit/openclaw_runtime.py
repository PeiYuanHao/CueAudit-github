"""Isolated workspace preparation and explicit CLI transport (release additions)."""
import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path

ROLES = ("identify", "executive", "quantitative", "qualitative", "summarize")


def prepare(repository, destination, model):
    repository, destination = Path(repository).resolve(), Path(destination).resolve()
    if destination.exists():
        raise ValueError("Destination already exists; choose a fresh local directory")
    if not isinstance(model, str) or "/" not in model or "CHOOSE_" in model:
        raise ValueError("Supply a locally available provider/model identifier")
    template = json.loads((repository / "openclaw/config.example.json").read_text(encoding="utf-8"))
    template["agents"]["defaults"]["model"] = {"primary": model, "fallbacks": []}
    for entry, role in zip(template["agents"]["list"], ROLES):
        entry["workspace"] = str(destination / "workspaces" / role)
        entry["agentDir"] = str(destination / "state" / "agents" / entry["id"] / "agent")
    # Build every file from public templates; never inspect private runtime state.
    destination.mkdir(parents=True)
    for role in ROLES:
        shutil.copytree(repository / "openclaw/workspaces" / role, destination / "workspaces" / role)
    (destination / "state").mkdir()
    path = destination / "openclaw.json"
    path.write_text(json.dumps(template, indent=2) + "\n", encoding="utf-8")
    return path


def parse_reply(stdout):
    """Accept only the documented CLI JSON payload shape and one JSON object."""
    envelope = json.loads(stdout)
    result = envelope.get("result", envelope)
    payloads = result.get("payloads", [])
    text = "\n".join(p.get("text", "") for p in payloads)
    if text.strip().startswith("```json") and text.strip().endswith("```"):
        text = text.strip()[7:-3].strip()
    reply = json.loads(text)
    if not isinstance(reply, dict):
        raise ValueError("Agent reply must be a JSON object")
    return reply


class OpenClawTransport:
    """Five sequential local turns; no channel delivery or implicit private config."""
    def __init__(self, node, entry, config, state, timeout=120):
        self.node, self.entry = str(node), str(Path(entry).resolve())
        self.config, self.state = Path(config).resolve(), Path(state).resolve()
        if not Path(self.entry).is_file() or not self.config.is_file():
            raise ValueError("OpenClaw entry point and isolated config must exist")
        settings = json.loads(self.config.read_text(encoding="utf-8"))
        expected = {r + "_agent" for r in ROLES}
        entries = settings.get("agents", {}).get("list", [])
        if {e.get("id") for e in entries} != expected:
            raise ValueError("Use the prepared five-role config")
        for e in entries:
            if not Path(e["agentDir"]).resolve().is_relative_to(self.state):
                raise ValueError("Agent state must stay within the isolated state directory")
            if not Path(e["workspace"]).resolve().is_relative_to(self.config.parent / "workspaces"):
                raise ValueError("Workspaces must stay within the prepared runtime")
        if settings.get("channels") or settings.get("bindings") or settings.get("plugins"):
            raise ValueError("This adapter uses a channel-free public runtime")
        if settings.get("tools") != {"profile": "minimal", "deny": ["session_status"]}:
            raise ValueError("Public model turns must use the prepared no-execution tool policy")
        self.timeout = timeout
        self.run_id = uuid.uuid4().hex

    def __call__(self, role, message):
        if role not in ROLES:
            raise ValueError("Unknown role")
        env = dict(os.environ)
        env["OPENCLAW_CONFIG_PATH"] = str(self.config)
        env["OPENCLAW_STATE_DIR"] = str(self.state)
        env.pop("OPENCLAW_PROFILE", None)
        command = [self.node, self.entry, "agent", "--local", "--agent", role + "_agent",
                   "--session-id", "cueaudit-" + self.run_id + "-" + role,
                   "--message", message, "--json", "--timeout", str(self.timeout)]
        completed = subprocess.run(command, env=env, capture_output=True, text=True,
                                   encoding="utf-8", timeout=self.timeout + 30)
        if completed.returncode:
            # Runtime/provider stderr can contain local settings; do not echo it.
            raise RuntimeError(f"OpenClaw role {role} failed (exit {completed.returncode}); inspect local runtime logs")
        return parse_reply(completed.stdout)
