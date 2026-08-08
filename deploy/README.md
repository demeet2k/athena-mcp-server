# ATHENA DEPLOYMENT.1

This directory converts the 3.1 package and OCI image into explicit activation intent. It does **not** claim that a host, cluster, route, secret, or production database has been activated.

## Non-collapse law

```text
wheel != image != tag != digest != deployment plan != applied workload
      != healthy process != ready organism != traffic cutover != empirical truth
```

Production activation requires an exact `repository@sha256:...` image reference. Mutable tags are navigation labels only.

## Secure HTTP surface

The container exposes a bounded one-request/one-response JSON-RPC adapter:

- `POST /mcp` — bearer-authenticated JSON-RPC.
- `GET /livez` — process liveness.
- `GET /readyz` — local C/I/E/P/R/V/O/M/S/X plus schema readiness.
- `GET /healthz` — combined process and local readiness packet.
- `GET /metrics` — bounded Prometheus text metrics.

This is deliberately named `ATHENA.JSONRPC.HTTP.ADAPTER.1`; it does not claim MCP Streamable HTTP, SSE, resumable streams, or transport semantics that are not implemented. Terminate TLS and enforce network policy at a trusted ingress or service mesh.

## SQLite persistence law

ATHENA 3.1 uses SQLite WAL and therefore deploys with:

```text
replicas = 1
strategy = Recreate
volume access = ReadWriteOnce
active writers = exactly one
```

Never mount the same database read-write into active old and candidate pods. A canary must use a fresh or snapshot-cloned database until explicit single-writer cutover. Active-active scaling requires a separately implemented transactional backend.

## Compose activation

```bash
export ATHENA_IMAGE='ghcr.io/demeet2k/athena-mcp-server@sha256:<exact digest>'
export ATHENA_TOKEN_FILE="$PWD/.secrets/athena-http-token"
docker compose -f deploy/compose.yaml up -d
curl --fail http://127.0.0.1:8765/readyz
```

The compose file binds only to loopback, runs UID/GID 65532, drops all capabilities, uses a read-only root filesystem and mounts the database in a named volume.

## Kubernetes rendering

Create the token secret outside Git:

```bash
kubectl create secret generic athena-http-auth --from-literal=token='<long random token>'
```

Render an exact image digest:

```bash
python deploy/render.py \
  --image 'ghcr.io/demeet2k/athena-mcp-server@sha256:<exact digest>' \
  --output /tmp/athena.yaml \
  --receipt /tmp/athena-render-receipt.json
```

Validate before applying:

```bash
kubectl apply --dry-run=server -f /tmp/athena.yaml
kubectl apply -f /tmp/athena.yaml
kubectl rollout status deployment/athena-mcp
```

## Canary and rollback

1. Witness a pre-cutover database backup or storage snapshot.
2. Start the exact candidate digest against an isolated clone.
3. Observe readiness, schema status, replay integrity, error rate, p95 latency and restart count.
4. Evaluate those observations through `athena_deployment_assess_canary`.
5. Hold unless the decision is `PROMOTE` and a separate cutover authority exists.
6. Stop the old writer before mounting production state into the new writer.
7. Roll back on readiness, schema, replay, error-budget, latency or restart failure.

Rollback restores the previous image digest and the witnessed state snapshot. It never performs an unreviewed data rewrite.
