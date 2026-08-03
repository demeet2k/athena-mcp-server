# Athena federation contract

This directory makes `demeet2k/athena-mcp-server` a typed participant in the Athena Git Brain.
It does not copy the Athena corpus or grant this repository global authority.

- Resource: `athena.repo.runtime-mcp@contract-proposal-0.1.0`
- Role: `runtime`
- Authority domain: `runtime-navigation`
- Base content witness: `0ee038011295873ba037a3cac25de18544439293`
- Control-plane schema commit: `3d33fbcd6248fc2dc2991fbbab5e93a7eb184246`
- State: `BOUND_NOT_CUTOVER`

`repo.json` declares the local surface. `exports.jsonl` exposes bounded
identities. `imports.lock.json` pins the control-plane schema. `edges.jsonl`
contains the forward declaration and its explicit return edge. `status.json`
preserves blockers instead of promoting them away.
