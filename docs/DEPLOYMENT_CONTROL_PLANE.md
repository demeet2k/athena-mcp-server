# DEPLOYMENT.1 — host activation control plane

ATHENA 3.1 adds the missing boundary between a distributable package and a running service. The implementation consists of four coupled but non-identical layers:

```text
DEPLOYMENT.1 contract
  -> JSONRPC.HTTP.ADAPTER.1 process
  -> OCI image + supply-chain attestations
  -> external activation controller and receipt
```

## Runtime organ

The canonical package root is `DeploymentHubServer -> HubServer -> Server`. It remains one runtime root; the deployment layer adds four tools, three resources and one prompt without nesting a second server.

The deployment organ is measured by the same runtime-truth overlay as the other KC144 organs. A live surface means only that the contract can be discovered and invoked. It does not mean a container exists, a registry object was pulled, or traffic was moved.

## HTTP host

`athena-mcp-http` owns one shared `DeploymentHubServer` and serializes dispatch around its SQLite-backed state. It refuses to listen when required schema verification fails. Optional migration is explicit and additive. Off-loopback binding requires a bearer token unless an unsafe development override is supplied.

The adapter implements JSON-RPC over HTTP at `/mcp`, not MCP Streamable HTTP or SSE. This narrower truth prevents transport cosplay while still enabling container and cluster health management.

## Deployment algebra

```text
ACTIVATION_ELIGIBLE
  = exact_digest
  ∧ release_asset_integrity
  ∧ external_secret_ref
  ∧ backup_witness
  ∧ isolated_canary
  ∧ readiness
  ∧ schema_currency
  ∧ replay_integrity
  ∧ bounded_error_latency_restart_metrics
  ∧ cutover_authority
  ∧ single_writer_quiescence
```

Any missing observation produces `HOLD`. Any failed gate produces `ROLLBACK`. `PROMOTE` means only that supplied observations satisfy the bounded policy.

## Supply chain

The 3.1 release transaction builds and publishes:

- a Python wheel;
- a multi-platform OCI image;
- BuildKit provenance and SBOM attestations attached to the image;
- an application SPDX document;
- a container attestation carrying the exact OCI digest;
- a digest-rendered Kubernetes manifest;
- a release manifest, release attestation and SHA-256 ledger.

Tags are never accepted as production image identity. Kubernetes and the activation plan use the registry digest.

## Persistence and topology

SQLite WAL is a single-writer organ. The provided Kubernetes topology uses `replicas: 1`, `strategy: Recreate`, `ReadWriteOnce` storage and one service endpoint. Canaries operate on isolated state. This preserves ledger causality and avoids silently converting filesystem sharing into distributed transaction semantics.

## Authority boundary

```text
release certificate != deployment authority
image digest != activation receipt
readyz PASS != empirical truth
canary PROMOTE != traffic mutation
```

A real deployment must return infrastructure identity, exact image digest, state snapshot reference, secret reference, observations, cutover event and rollback availability from the executing environment.
