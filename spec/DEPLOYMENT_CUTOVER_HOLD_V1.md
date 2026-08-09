# ATHENA Deployment CUTOVER_HOLD V1

## Status

`ATHENA.CUTOVER.HOLD.1` is a pure, non-effectful binding gate layered on
`ATHENA.DEPLOYMENT.2`. It converts already-produced evidence into a replayable
coordination packet and then stops.

```text
PLAN_ONLY
  + checksum-valid isolated canary witness
  + exact expected/observed activation base
  + supplied single-writer quiescence observation
  + explicit authority reference
  -> CUTOVER_HOLD
  != SINGLE_WRITER_CUTOVER
  != ACTIVATION_RECEIPT
```

The compiler has no registry, cluster, secret, state-volume, writer-control, or
traffic adapter. It cannot perform the transition after the hold.

## Versions

```text
plan                    ATHENA.ACTIVATION.PLAN.2
canary witness          ATHENA.ISOLATED.CANARY.WITNESS.1
canary assessment       ATHENA.CANARY.ASSESSMENT.2
quiescence observation  ATHENA.SINGLE.WRITER.QUIESCENCE.OBSERVATION.1
quiescence assessment   ATHENA.SINGLE.WRITER.QUIESCENCE.ASSESSMENT.1
hold packet             ATHENA.CUTOVER.HOLD.1
hold verification       ATHENA.CUTOVER.HOLD.VALIDATION.1
```

## Input 1: activation plan

The plan must replay as an unmodified `PLAN_ONLY` object. The hold compiler
checks:

- embedded `plan_digest` over canonical JSON without the digest field;
- digest-pinned target image;
- full 40-character source head;
- explicit expected-current-image reference;
- snapshot reference and SHA-256;
- secret, attestation, and SBOM references;
- `replicas == 1`;
- CAS image and snapshot coordinates equal the top-level plan coordinates;
- a declared `CUTOVER_HOLD` stage.

A valid plan is still not evidence that its expected current image or snapshot
was observed in production.

## Input 2: isolated canary witness

The canary validator accepts only the exact same-digest restart witness shape:

```text
schema           ATHENA.ISOLATED.CANARY.WITNESS.1
observer         ATHENA.ISOLATED.CANARY.OBSERVER.1
comparison       REPLICATED_SAME_DIGEST_STATE_RESTART
assessment       PROMOTE / PASS
minimum samples  30
minimum window   60 seconds
```

It recomputes both the assessment and witness digests and requires:

- target image and source head equal the activation plan;
- all eight canary gates equal `PASS`;
- no failed gates;
- tool, resource, deployment-manifest, and restart-replay structural matches;
- registered state matched after restart;
- every authority bit in the canary witness remains false.

The repository fixture preserves the hosted v3.3.0 witness:

```text
image
  ghcr.io/demeet2k/athena-mcp-server@
  sha256:d7eada158c5f202dd7a061218188d0c00b7317c867bedc742857a7b90298d8be

source head
  11211341adf599ae78784cce4ded39f21ee71ef7

workflow run
  31305555129

witness digest
  sha256:53b4236273a6db8d1c80335ba07f3e8927a47d5596ae5bd1efcee9dc145bac87
```

That fixture demonstrates input compatibility. It does not identify a current
production deployment or production state snapshot.

## Input 3: single-writer quiescence observation

The observation is external evidence supplied to the pure assessor:

```json
{
  "schema": "ATHENA.SINGLE.WRITER.QUIESCENCE.OBSERVATION.1",
  "observed_current_image_ref": "repository@sha256:<64 hex>",
  "active_writer_count": 0,
  "previous_writer_stopped": true,
  "candidate_writer_started": false,
  "write_fence_active": true,
  "write_fence_ref": "external-reference",
  "snapshot_after_write_fence": true,
  "state_snapshot_verified": true,
  "state_snapshot_ref": "external-reference",
  "state_snapshot_digest": "sha256:<64 hex>",
  "observer_ref": "external-reference",
  "observed_at": "external timestamp"
}
```

`QUIESCENT / PASS` requires every condition simultaneously:

```text
observed current image == plan expected current image
active writer count    == 0
previous writer stopped == true
candidate started       == false
write fence active      == true
snapshot after fence    == true
snapshot verified       == true
snapshot ref/digest     == plan snapshot ref/digest
observer/timestamp      != empty
```

The assessor records an observation digest and an assessment digest. It does
not stop a process, install a fence, inspect a database, or verify a snapshot.

## Input 4: authority reference

`cutover_authority_ref` is bound as opaque data. The compiler records:

```text
reference_bound         true|false
independently_verified  false
authorizes_this_packet  false
```

Binding a reference is deliberately weaker than validating the authority,
identity, scope, freshness, revocation state, or signature represented by that
reference.

## Hold algorithm

```text
P  = validate activation plan
C  = validate canary witness against P.target
Q  = assess quiescence against P.expected_current and P.snapshot
A  = nonempty authority reference

if !P: HOLD_ACTIVATION_PLAN_INVALID
if !C: HOLD_CANARY_WITNESS_INVALID
if Q.current missing: HOLD_MISSING_CURRENT_IMAGE_OBSERVATION
if Q.current malformed: HOLD_INVALID_CURRENT_IMAGE_OBSERVATION
if Q.current != P.expected_current: HOLD_STALE_ACTIVATION_BASE
if any other Q gate fails: HOLD_SINGLE_WRITER_NOT_QUIESCENT
if !A: HOLD_MISSING_CUTOVER_AUTHORITY_REFERENCE

if no hold reason:
    status   = CUTOVER_HOLD
    decision = BOUND_AT_CUTOVER_HOLD
else:
    status   = HOLD
    decision = first fail-closed reason
```

Unknown values never become defaults, zeroes, matches, or authorization.

## Packet bindings

A complete packet binds:

- activation-plan digest and validation digest;
- target image and source head;
- expected and observed current image;
- snapshot reference and digest;
- canary witness, canary assessment, and canary validation digests;
- canary workflow run;
- quiescence observation and assessment digests;
- quiescence observer and timestamp;
- opaque authority reference;
- CAS equality results;
- rollback contract inherited from the plan;
- all false execution-authority bits;
- a canonical `packet_digest`.

The packet intentionally omits the plan's token-secret reference. The compiler
requires that a plan contains a secret reference but does not propagate it into
the coordination packet.

## Replay verifier

`athena_deployment_verify_cutover_hold` independently receives all expected
coordinates and checks:

- packet version, status, decision, completeness, and empty hold list;
- canonical packet digest;
- plan, target image, source, current image, and snapshot bindings;
- canary-witness digest;
- quiescence-assessment digest;
- authority-reference equality while authority verification remains false;
- all execution-authority bits remain false;
- all CAS equalities are true;
- the next transition remains disallowed by this packet.

Verifier `PASS` means the supplied packet bytes match the supplied expectations.
It is not a fresh cluster observation and cannot prove that quiescence persists.

## MCP surface

```text
athena_deployment_assess_quiescence
athena_deployment_cutover_hold
athena_deployment_verify_cutover_hold

athena://deployment/cutover-hold
athena_deployment_cutover_hold prompt
```

The surface is installed additively after `DEPLOYMENT.2`; the existing plan,
canary-assessment, and activation-receipt policy remains unchanged.

## Non-authority invariant

Every packet carries:

```text
cluster_apply_authorized        false
cutover_authorized              false
production_secret_provisioned   false
production_state_contacted      false
state_mutation_authorized       false
traffic_activation_authorized   false
```

Canonical laws:

```text
CANARY_PROMOTE != CUTOVER_AUTHORITY
AUTHORITY_REFERENCE_BOUND != AUTHORITY_VERIFIED
QUIESCENCE_ASSESSMENT_PASS != WRITER_STOPPED_BY_THIS TOOL
CUTOVER_HOLD != SINGLE_WRITER_CUTOVER
PACKET_VERIFIED != ACTIVATION_RECEIPT
ARTIFACT_CREATED != TRAFFIC_ACTIVATED
```

## Required successor

A separate effectful executor, outside this organ, must freshly:

1. authenticate and validate the authority reference;
2. re-observe the current production image;
3. re-observe snapshot identity and integrity;
4. re-observe the write fence and zero-writer state;
5. reject stale CAS coordinates;
6. execute the single-writer transition only within granted scope;
7. emit `ATHENA.ACTIVATION.RECEIPT.1`;
8. submit that receipt to the existing receipt verifier.

No part of this specification authorizes that executor or supplies its
infrastructure coordinates.
