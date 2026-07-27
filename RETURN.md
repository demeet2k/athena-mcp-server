# Return to Athena

This repository is a `runtime` participant, not the federation root.

1. Read `.athena/repo.json` and resolve
   `athena.repo.runtime-mcp@federation-consumer-0.1.0`.
2. Verify `MCP/data/athena_federation_v2/snapshot.json` and require graph
   digest `sha256:82a3f9e2369394f39080b795476342688b95e35dcfcda3fe6a8be0212618d8d1`.
3. Follow `edge.runtime-mcp-to-control` in `.athena/edges.jsonl`.
4. Carry the local manifest, exact repository commit, route receipt, and frozen
   P05 source commit `13cda0bed07a881d42446e3a282eb1ba84ea9b45`.
5. Resolve the consumed control snapshot at
   `github://demeet2k/Athena@13cda0bed07a881d42446e3a282eb1ba84ea9b45/crystal/v2/release-candidate.json`.
6. Preserve canonical lock parent `1b177fa2e3a4860487497210dcfbc122a287d693` and selected lineage `git-brain-v2`.
7. If the exact identity, carrier, witness, or reverse edge is missing, stop
   with the defect recorded in `.athena/status.json`.
8. A response marked `athena-108d-v1` is a legacy fallback, not a v2 graph
   traversal and not promotion evidence.

This return is `compensated`: it preserves identity, role, provenance, runtime
answer provenance, and authority boundaries. Runtime receipts are witnesses;
only the Athena control plane can admit them into a promoted federation.
