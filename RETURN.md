# Return to Athena

This repository is a `runtime` participant, not the federation root.

1. Resolve `athena.repo.runtime-mcp@federation-consumer-0.1.0` from
   `.athena/repo.json`.
2. Verify the frozen snapshot graph digest
   `sha256:82a3f9e2369394f39080b795476342688b95e35dcfcda3fe6a8be0212618d8d1`.
3. Verify P05 release candidate `KC144.MYC.P05.RC1` at control commit
   `13cda0bed07a881d42446e3a282eb1ba84ea9b45`.
4. Require the vendored P05 cold replay verdict
   `PASS[CANONICAL_COLD_REPLAY_10_OF_10]`; the alternate P04 overlay remains
   quarantined at 0/11 exact return closures.
5. Read `.athena/receipts/p06-runtime-cutover.json` or call
   `athena_federation_cutover_receipt`.
6. Follow the forward route `edge.q-shrink-to-control` then
   `edge.control-to-runtime`; return through `edge.runtime-to-control` then
   `edge.control-to-q-shrink`.
7. Preserve `athena://crystal-108d` as the explicit
   `athena-108d-v1` fallback. A fallback answer is not v2 traversal or
   promotion evidence.
8. On rollback, select predecessor commit
   `0ee038011295873ba037a3cac25de18544439293`; do not rewrite history.
9. Stop if the exact identity, carrier, witness, reverse edge, or deployment
   witness is absent. Record the defect in `.athena/status.json`.

This return is `compensated`: it preserves identity, role, provenance, runtime
answer provenance, rollback, and authority boundaries. Runtime receipts are
witnesses; only the Athena control plane can admit them. No deployment, merge,
or promotion is claimed by P06.
