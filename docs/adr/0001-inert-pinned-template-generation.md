# ADR 0001: Inert pinned template generation

Status: accepted for v2 alpha. Date: 2026-09-11.

## Context

The existing Python implementation passed caller supplied output paths to Cookiecutter, installed packages at runtime, executed template hooks, and collected process output without a deadline. Its network authentication defaulted to disabled. Committed virtual environments were not reproducible deployment artifacts.

Cookiecutter intentionally executes Python and shell hooks, including pre-prompt hooks: https://cookiecutter.readthedocs.io/en/stable/advanced/hooks.html . Disabling one hook stage is insufficient as a complete template trust policy.

## Decision

Ship three reviewed, inert JSON bundles with manifest SHA256 pins. Replace only the literal name token with a restricted slug; do not evaluate expressions. Enforce bounds before writing. Reject traversal, hooks fields and paths, duplicate case-insensitive output names and file/directory collisions. Do not accept remote template registrations through MCP.

Use operator-created private output roots and exclusive root locks. Reserve each project directory, stage content, and atomically rename the complete source directory. Reject existing names. Retire Python entry points and unsafe API/core imports; remove tracked virtual environments. Keep historical source for provenance, excluded from the compatibility Python package.

Use the official TypeScript MCP SDK 2.0.0, pinned in package-lock.json. The official SDK documentation identifies the maintained language implementations: https://modelcontextprotocol.io/docs/sdk . Stdio is the only transport. Six fixed tools expose domain operations and validation, with no shell or caller path capability.

## Alternatives and tradeoffs

Sandboxed Cookiecutter would preserve arbitrary community templates but requires a real isolation boundary, verified images, network policy and hook review. A hook-disable flag alone leaves other template and filesystem risks. Arbitrary Jinja rendering offers more expressiveness but adds execution surface. The chosen implementation trades broad template compatibility for an auditable local capability and no generation network cost.

## Consequences

Legacy clients must migrate. Operators approve template changes through reviewed commits and digest updates. Hashes detect corruption but do not authenticate a compromised repository. Same-user hostile processes and power loss durability remain outside the guarantee. A crash requires explicit lock recovery. No SOTA superiority claim is made; benchmarks are fixture measurements. Future remote template ingestion must include isolation and provenance validation before it can enter this supported path.
