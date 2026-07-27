# P10 authorized HTTPS endpoint and persistent witness capsule

This is a provider-neutral handoff for one already-published image. It does
not rebuild or republish P09, choose a hosting account, provision a secret,
claim a deployment, admit a witness, merge a PR, or promote the runtime.

The only deployable image is:

`ghcr.io/demeet2k/athena-mcp-server@sha256:31458783d4aeb28e0a4036cb4fab39a2f2bc1f4ef6e3025d126c78a865162ad2`

Its build-locked source is:

`52d0e2abf282aee5f8bf233521989bc2c8969989`

The committed state is `READY_AWAITING_AUTHORIZED_TARGET`. All provider,
account, deployment, endpoint, secret-store, and persistent-witness fields in
`host-contract.json` deliberately remain null.

## Host requirements

Use an already-authorized persistent container host with:

- OCI digest selection (never a mutable tag);
- restart policy `unless-stopped` or the provider-equivalent persistent policy;
- UID/GID `10001:10001`, a read-only root filesystem, no Linux capabilities,
  and `no-new-privileges`;
- container port `8080`, with the published port bound only to loopback or a
  private service network;
- a host-managed secret named `ATHENA_MCP_BEARER_TOKEN` containing at least
  32 characters;
- optional browser-origin allowlisting through
  `ATHENA_MCP_ALLOWED_ORIGINS`;
- externally trusted TLS 1.2 or newer at one stable HTTPS authority;
- exact forwarding of `/healthz` and streaming `/mcp` traffic to port 8080;
- no HTTP downgrade and no redirect between the supplied URL and either exact
  endpoint.

The TLS terminator must preserve the original host, set the forwarded scheme
to `https`, support long-lived streaming request/response bodies, and leave
authentication to the container. `/healthz` is public but contains no secret.
Every `/mcp` request must cross the runtime bearer boundary.

## Preparation

Validate the committed null-authority state:

```bash
python scripts/p10_preflight.py validate \
  deploy/p10/host-contract.json \
  --mode prepared \
  --output p10-prepared-preflight.json
```

`compose.yaml` is a host-neutral container example. Resolve the bearer token
from the authorized host secret manager into the environment; do not put it
in an environment file inside the repository, a shell argument, a container
label, or a deployment receipt.

```bash
docker compose -f deploy/p10/compose.yaml pull
docker compose -f deploy/p10/compose.yaml up -d
```

The compose surface binds the service to loopback so an authorized TLS
terminator remains mandatory. It does not select or install a reverse proxy.

## Deployment authorization and secret rotation

Record only non-secret authorization metadata:

- provider identifier and logical account scope;
- persistent deployment identifier and persistence class;
- change-control or authority reference, actor, and timestamp;
- exact HTTPS `/mcp` endpoint;
- secret-store reference, never the secret value.

The manual witness workflow materializes those fields into a secret-free
authorized contract. Locally, the same operation reads non-secret metadata
from `ATHENA_P10_*` environment variables and the bearer token only from
`ATHENA_MCP_BEARER_TOKEN`:

```bash
python scripts/p10_preflight.py materialize-authorized \
  deploy/p10/host-contract.json \
  --output p10-authorized-host-contract.json
python scripts/p10_preflight.py validate \
  p10-authorized-host-contract.json \
  --mode authorized \
  --output p10-authorized-preflight.json
```

Rotate the secret in the host secret manager, restart or roll the service so
all replicas receive the new value, update the protected GitHub Environment
secret with the same value, and immediately rerun the witness. Never retain
the prior value in files or logs.

## Persistent witness

After the authorized digest is live, run:

```bash
python scripts/p10_persistent_witness.py \
  p10-authorized-host-contract.json \
  --output p10-persistent-witness.json
```

The probe reads no token argument. It checks trusted HTTPS without redirects,
public health, unauthenticated rejection, invalid-token rejection, the exact
build-locked commit, Streamable HTTP MCP initialization, the exact 174-tool
and 27-resource inventories, v2 identity, the reciprocal forward/return
route, explicit `athena-108d-v1` fallback, equal cutover receipts, and
`promotion_ready: false`. It emits only a deterministic, content-addressed,
secret-free receipt.

A local or mocked run is labeled
`PASS_LOCAL_SIMULATION_NOT_PERSISTENT` and can never create the legal
`PASS_PERSISTENT_HTTPS_WITNESS` outcome.

## Rollback, admission, and promotion

Rollback stops routing to the endpoint and selects an explicitly authorized
immutable digest. It never moves a tag or rewrites P09. The explicit
`athena-108d-v1` fallback remains available.

Preparation is not deployment. Deployment is not witness admission. Witness
admission is not promotion. Only the Athena control plane can admit a P10
receipt, and IC10 remains the sole promotion authority.
