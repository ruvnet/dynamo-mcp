# Validation evidence

Recorded 2026-09-11 on managed Linux, Node 24.19.0, Python 3.12.

Run `npm ci --ignore-scripts`, `npm test`, `npm audit`, and `node src/cli.mjs benchmark` from repository root. The test transcript records 13 passing tests, including generated Node CLI, Node library and Python CLI projects, malicious bundle fixtures, concurrency, lock recovery behavior, and real SDK stdio read/write/validation flows. No provider credentials or paid services are used.

The benchmark records 100 local template verification/render samples: median 0.741 ms, p95 3.638 ms. This is not a filesystem generation, concurrency throughput or comparative SOTA result. Generated project bytes and receipt digests are deterministic; filesystem timestamps are not part of that guarantee.

npm advisory audit reports zero vulnerabilities in the locked supported Node runtime at collection time. Generated MetaHarness has its own dependency audit and tests. Historical Python requirements are not installed and its service entry points reject execution.
