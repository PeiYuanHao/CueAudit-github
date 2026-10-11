# Optional five-role OpenClaw setup

The original audit workflow uses OpenClaw to coordinate five roles. This release
provides sanitized role instructions and a standalone Python runner. It does not
bundle OpenClaw, install it, modify your agent configuration, or implement an
automatic five-agent dispatcher. The core can be used without OpenClaw.

Using your own installed OpenClaw version and its workspace configuration:

1. Create separate workspaces for Identify, Executive, Quantitative, Qualitative
   and Summarize, with the names of your choice.
2. Use the corresponding Markdown file in `agents/` as each role's instructions.
   Keep existing runtime-required files and personal settings separate.
3. Give Quantitative access to the installed `cueaudit` command and local input
   manifests. Restrict execution to approved scripts and measurement modules.
4. Route Identify's hypotheses to Executive; Executive prepares a JSON request.
5. Quantitative runs `cueaudit request.json --output outputs/audit.json`, then
   supplies the generated report. Qualitative supplies review notes separately.
6. Summarize reads actual reports and separates data association, model evidence,
   unsupported routes, failures and review leads.

OpenClaw-specific workspace paths, agent IDs, provider settings, service URLs,
authentication and communication channels must be configured locally. No private
`openclaw.json`, credentials, session histories, memories or messaging accounts
are part of this repository. These templates describe role contracts; they do not
assert that a particular OpenClaw installation has been configured or tested.

For a new dataset, provide its intended task, label definitions, split information,
accessible samples, allowed measurements and verification budget. Do not assume
that the absence of a registered route proves the absence of shortcuts.
