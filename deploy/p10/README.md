# P10 authorized persistent MCP host

This capsule deploys one already-published, digest-addressed Athena image. It
does not rebuild the runtime, record the bearer token, grant promotion
authority, or claim that a host exists before an authorized target passes the
live witness.

## Frozen runtime

- source commit:
  `52d0e2abf282aee5f8bf233521989bc2c8969989`
- image:
  `ghcr.io/demeet2k/athena-mcp-server@sha256:31458783d4aeb28e0a4036cb4fab39a2f2bc1f4ef6e3025d126c78a865162ad2`
- container UID: `10001`
- internal endpoint: `http://127.0.0.1:8080/mcp`
- required external endpoint: `https://<authorized-host>/mcp`

## Host installation

The host needs Docker Compose and an HTTPS reverse proxy. `Caddyfile` is
provided for a host-managed Caddy service; the container itself binds only to
loopback.

Create a host-local environment file outside the repository:

```text
ATHENA_MCP_BEARER_TOKEN=<at-least-32-random-characters>
ATHENA_MCP_ALLOWED_ORIGINS=https://<authorized-browser-origin>
ATHENA_P10_HOSTNAME=<authorized-hostname>
ATHENA_P10_LOCAL_PORT=8080
```

Authenticate the host to GHCR without writing a token into this repository,
then start the exact digest:

```bash
docker compose --env-file /secure/path/athena-p10.env \
  -f deploy/p10/compose.yaml pull
docker compose --env-file /secure/path/athena-p10.env \
  -f deploy/p10/compose.yaml up -d
```

Install `deploy/p10/Caddyfile` in the host Caddy configuration and reload
Caddy. The public `/healthz` route must report the exact frozen source commit,
`commit_source: build-locked-file`, and `promotion_ready: false`.

## Authorization and witness

The target contract is generated only inside the
`p10-persistent-host` GitHub Environment. The workflow requires:

- an authorized HTTPS URL ending exactly in `/mcp`;
- a stable target identifier and authorization reference;
- persistence class `managed-service`, `orchestrated-service`, or
  `self-hosted-service`;
- environment secret `ATHENA_P10_BEARER_TOKEN`.

The witness crosses the real Streamable HTTP boundary and verifies:

- MCP initialization;
- required tool and resource catalogs;
- exact build-locked source commit;
- frozen federation graph;
- exact v2 identity;
- two-hop v2 route and reciprocal two-hop return;
- explicit `athena-108d-v1` fallback;
- equality of tool and resource cutover receipts;
- non-promotional runtime state.

The emitted target and witness artifacts contain no secret value. A successful
P10 witness proves the endpoint boundary but still cannot promote the runtime;
control-plane admission and IC10 remain separate gates.

## Provider evidence and persistence window

A live witness is not admitted from an endpoint response alone. The dispatch
must also supply a secret-free provider record containing the provider ID,
logical account or project scope, deployment ID, authorization reference,
exact digest and source pins, deployment timestamp, protected secret-store
reference, and an HTTPS provider evidence URL. Unknown fields fail closed so
tokens, passwords, client secrets, and free-form notes cannot enter receipts.

`deploy/p10/provider-evidence.example.json` is intentionally unresolved. Its
null fields are activation inputs, not defaults and not claims.

The environment-gated workflow now runs at least three complete MCP samples
at least 20 seconds apart. Every sample must independently preserve:

- exact image and build-locked source attestation;
- required tools and resources plus the frozen graph;
- v2 identity and the two-hop forward route;
- the reciprocal two-hop return plan;
- explicit `athena-108d-v1` fallback;
- equal tool/resource cutover receipts; and
- the non-promotion boundary.

The resulting receipt spans at least 40 seconds and records no bearer value.
Provider evidence and repeated observations prove a persistent boundary only;
they do not authorize merge or IC10 promotion.
## Activation handoff packet

The live workflow no longer accepts a loose set of provider fields. A single
`athena.persistent-host-activation-packet/v1` object binds the authorized
provider, account scope, deployment, target, endpoint, authorization, protected
secret-store reference, exact immutable lineage, and fixed witness plan.

`deploy/p10/activation-packet.example.json` is intentionally
`UNRESOLVED`. Every authority-dependent field is `null`, live-witness
authorization is false, and the template cannot compile into executable
handoff artifacts.

After an authorized operator supplies a complete secret-free packet, the
workflow's default preflight compiles and uploads only:

- `p10-target.json`;
- `p10-provider-evidence.json`; and
- `p10-activation-handoff.json`.

Preflight does not contact the endpoint and emits
`PASS_AUTHORIZED_WITNESS_HANDOFF_NOT_EXECUTED`. The separate
`execute_live_witness` switch defaults to false. Setting it true still
requires approval through the protected `p10-persistent-host` environment
and the separately stored `ATHENA_P10_BEARER_TOKEN`.

The packet cannot weaken the three-sample / 20-second / 40-second observation
window, alter the exact source or image, record secret material, claim merge or
promotion, remove reciprocal return, remove the explicit
`athena-108d-v1` fallback, or bypass IC10.

