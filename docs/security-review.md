# Security review

Scope: supported Node v2 template renderer, writer, MCP and CLI; legacy launcher and package exposure. Reviewed 2026-09-11.

| Finding | Evidence | Remediation |
|---|---|---|
| Executable remote templates | Legacy project_generator.py calls Cookiecutter without hook restrictions | Supported renderer does no evaluation, fetching or hook execution; legacy core imports retired |
| Arbitrary output paths | Legacy request.output_dir passed directly to Cookiecutter | Caller receives only template/name fields; private operator root |
| Unbounded execution/output | Legacy communicate calls and runtime pip installs | No generation subprocess; fixed validation deadline/output/environment |
| Network auth disabled by default | Historical config and README | Legacy network launcher and API retired; supported stdio only |
| Committed virtual environments | Tracked interpreter links and executable wrappers | Removed; npm lockfile pins runtime |

Threat actors include malicious MCP input and tampered template bytes. The repository, pinned dependencies, operator process and private output root are trusted. Template integrity is checked each render. Directory/file names are bounded and validated independently of content. Generated code must still be reviewed before execution: an approved template can intentionally contain code, though Dynamo does not execute it during generation.

Validation uses dedicated temporary projects, never a requested shell command. MCP tools disclose no secrets. Subprocess environment passes PATH only. The operator owns PATH and the checked-out repository. Advisory evidence is npm audit against the committed lockfile, recorded in docs/evidence/npm-audit.json. This does not prove absence of unknown vulnerabilities.

Legacy files are historical and are not an alternative supported service. Running them after modifying import retirement guards explicitly leaves this security boundary. No production credentials were inspected or used. Remaining deployment gates are isolated OS account, protected root parents, reviewed template contributions and documented crash recovery.

RuFlo `@claude-flow/cli@3.25.6 security scan --target dynamo-mcp/src --depth deep --type all` reported zero findings on 2026-09-11. This heuristic result supplements the manual trust-boundary review and adversarial tests; it does not establish proof of safety. Independent agent review found failed validation lacked MCP `isError`; that reporting defect was corrected before publication.
