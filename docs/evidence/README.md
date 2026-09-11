# Validation evidence

Recorded 2026-09-11 on managed Linux, Node 24.19.0, Python 3.12.

Run `npm ci --ignore-scripts`, `npm test`, `npm audit`, and `node src/cli.mjs benchmark` from repository root. The test transcript records 13 passing tests, including generated Node CLI, Node library and Python CLI projects, malicious bundle fixtures, concurrency, lock recovery behavior, and real SDK stdio read/write/validation flows. No provider credentials or paid services are used.

The benchmark records 100 local template verification/render samples: median 0.741 ms, p95 3.638 ms. This is not a filesystem generation, concurrency throughput or comparative SOTA result. Generated project bytes and receipt digests are deterministic; filesystem timestamps are not part of that guarantee.

npm advisory audit reports zero vulnerabilities in the locked supported Node runtime at collection time. Generated MetaHarness has its own dependency audit and tests. Historical Python requirements are not installed and its service entry points reject execution.

## Fresh-read allocation optimization

A second pass replaces maximum-sized read buffers with actual file size plus one growth-detection byte, while retaining a fresh read and SHA256 verification on every preview. Aggregate manifest/template read buffers fell from 294,914 bytes to 2,307–2,485 bytes for the three shipped templates, a reduction of at least 99.15%. This is buffer allocation, not whole-process resident memory.

`read-optimization.json` records 40 warmups and 500 alternating full previews per implementation for each template. Rendered outputs are exactly equal. The extra EOF probe raised median latency by 13–15% (about 0.035–0.045 ms); p95 was mixed. The decision is justified by deterministic allocation reduction and handling partial reads, not a throughput or SOTA superiority claim. No stale-template cache was introduced. A new regression test modifies a template between previews and replaces it with a symlink; both are rejected.

To reproduce, fetch the merged baseline commit if using a shallow checkout, then run `node scripts/compare-read.mjs`. The comparison reads the immutable baseline implementation from Git and imports it with the same template root. It does not download dependencies or execute template content. `npm test` now reports 14 passing tests.
