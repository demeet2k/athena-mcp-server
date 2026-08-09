# KC144 Project Atlas MCP Surface V2

`ATHENA.PROJECT_ATLAS.MCP_SURFACE.V2` projects the read-only V1 Project Atlas into a bounded, indexed, replay-identifiable federated MCP query interface.

It is a **query membrane**, not a new identity system.

```text
CONFIGURED GIT / ATHENA_GIT_ROOT ─┐
                                  ├─> FEDERATED KC144 SNAPSHOT ─> QUERY INDEX
RUNTIME SOURCE GIT ───────────────┤              │                    │
                                  │              │ PATLASV2.*         ├─ summary
LIVE MCP TOOLS + PROMPTS ─────────┘              │                    ├─ resolve
                                                 │                    ├─ list
                                                 └─ federation ───────└─ route -> RETURN
```

## Ancestry

V2 is developed from exact V1 candidate `fc376ffa76864f173049164db9206295b96ec85b` / PR #295.

Architectural integration is child PR #310. Qualification-only PR #311 targets `master` only because the repository CI trigger runs on PRs whose base is `master`.

`QUALIFICATION_PR != INTEGRATION_PR`.

Until V1 is accepted, V2 remains a child candidate. If V1 changes, V2 must rebase to the accepted ancestry and requalify; a green old child head is not current evidence.

## Three distinct project planes

V2 explicitly refuses:

`CONFIGURED_GIT_HEAD != RUNTIME_GIT_HEAD`.

### Configured Git

`ATHENA_GIT_ROOT` is the Git plane owned by `GitBackend`, commonly the canonical/private brain.

Its native coordinate is:

`<repo, ref/head, tree, path, object_sha>`.

### Runtime-source Git

MCP definitions belong to the runtime package/repository frontier, not automatically to `ATHENA_GIT_ROOT`.

Runtime provenance resolves in this order:

1. `ATHENA_RUNTIME_GIT_ROOT` exact checkout;
2. package source checkout only when `athena_mcp/` is directly below its `.git` root;
3. `ATHENA_RUNTIME_REPOSITORY` + exact 40-hex `ATHENA_RUNTIME_GIT_HEAD` host attestation;
4. `HOLD_RUNTIME_PROVENANCE`.

`PACKAGE_VERSION != RUNTIME_SOURCE_HEAD`.

A source checkout yields `OBSERVED_LOCAL_GIT`. Host-configured repository/head identity yields `HOST_CONFIGURED_UNVERIFIED`: exact identity coordinates, not independent promotion verification.

When only repository+head is known, MCP definitions can be exactly head-qualified but the runtime Git tree remains unknown:

`UNKNOWN_RUNTIME_TREE != EMPTY_RUNTIME_TREE`.

### MCP virtual surface

Every live installed `TOOLS + PROMPTS` definition is projected using the runtime-source repository/head.

`MCP_DEFINITION_COORDINATE_REQUIRES_RUNTIME_SOURCE_HEAD`.

MCP definitions never borrow the configured brain HEAD.

## Federated query index

Each stable snapshot compiles `ATHENA.PROJECT_ATLAS.QUERY_INDEX.V2` across visible records.

Indexed maps:

- `by_source`;
- `by_poid`;
- `by_address`;
- `by_return`;
- `by_path`;
- `by_raw_mcp_name`;
- `by_typed_mcp`;
- `by_project_gid`;
- `by_reference_gid`;
- `by_directory`;
- `by_blob`.

The index is deterministically sorted, de-duplicated, order-invariant and duplicate-invariant. Its digest is included in the snapshot identity.

`QUERY_INDEX != SEMANTIC_IDENTITY`.

Exact resolver modes are explicitly visible:

- `TYPED_MCP`;
- `POID`;
- `PROJECT_ADDRESS`;
- `RETURN_URI`;
- `OPEN_WORLD`.

List calls seed from source/station/reference/directory indexes where applicable, then apply remaining filters. Indexing changes lookup cost and replayability; it does not change object meaning.

## Replay identity

Every stable federated observation has:

`PATLASV2.<digest>`.

The digest covers:

- configured repo/head/tree/atlas digest;
- runtime provenance;
- runtime repo/head/tree/atlas digest when available;
- MCP repo/head/surface digest;
- live MCP `TOOLS + PROMPTS` signature;
- query-index digest;
- federation digest.

Equivalent summary/resolve/list/route reads on one stable frontier expose the same snapshot ID. A configured-head change, runtime-head change, or live MCP-surface change changes it.

`PROJECT_ATLAS_SNAPSHOT_ID != PROMOTION_RECEIPT`.

Every query result has `authority=NONE`.

## Surface

### `athena_project_atlas_summary`

Returns bounded top-level state only:

- snapshot ID;
- separate configured/runtime heads;
- configured Git atlas digest/counts;
- runtime provenance and runtime Git digest/counts when tree is available;
- MCP repo/head/count/surface digest/live signature;
- query-index version/digest/counts;
- federation roots/digest;
- completeness coordinates;
- dirty/branch observations;
- pagination limits and laws.

Optional CAS inputs:

- `expected_head` = exact configured Git commit;
- `expected_runtime_head` = exact runtime-source Git commit.

### `athena_project_resolve`

Exact identifiers:

- POID;
- full Project Atlas address;
- exact `athena+git://...` RETURN;
- exact `athena+mcp://...` RETURN;
- typed MCP namespaces `tool:<name>`, `prompt:<name>`, `mcp:tool:<name>`, `mcp:prompt:<name>`.

Open-world identifiers include raw Git path and raw MCP name. They may be ambiguous across planes.

Typed MCP prefixes are reserved namespaces: a Git filename literally equal to `tool:athena_project_route` does not hijack the MCP locator.

If zero matches in a complete universe: `HOLD_NOT_FOUND`.

If runtime provenance is missing: `HOLD_RUNTIME_PROVENANCE`.

If runtime HEAD is known but its Git tree is unavailable and an open-world uniqueness claim cannot be proven: `HOLD_RUNTIME_TREE_UNAVAILABLE`.

If multiple records match: `HOLD_AMBIGUOUS`, with bounded candidates.

No configured-first, runtime-first, MCP-first or textual-order tie break is permitted.

### `athena_project_list`

Sources:

- `all`;
- `git` = configured/runtime Git union;
- `configured_git`;
- `runtime_git`;
- `mcp`.

Filters:

- path prefix;
- native type;
- PROJECT_KC144 GID/row/column;
- KC144 reference GID;
- parent directory;
- MCP kind;
- POID prefix.

Pagination is deterministic: default 50, max 100, explicit non-negative offset, `next_offset=null` at exhaustion.

If the requested union includes an unknown runtime tree, standing is explicitly partial rather than pretending the missing tree is empty.

### `athena_project_route`

1. Acquire one stable federated snapshot.
2. Resolve source exactly through the witnessed index.
3. Resolve destination exactly.
4. HOLD on missing/ambiguous endpoints.
5. Compute deterministic V1 PROJECT_KC144 station route.
6. Return both native RETURN witnesses.
7. Record `cross_repository`, `cross_version`, and `cross_frontier` separately.
8. Cross-frontier routes emit federation digest and both `<repo,head>` coordinates.

`wrap=false` uses ordinary grid navigation; `wrap=true` uses the 12×12 torus.

`PROJECT_ROUTE != SEMANTIC_EQUIVALENCE`.

### `athena://project-atlas`

Read-only bounded federated summary. Full navigation remains tool-mediated.

## Freshness calculus

The live frontier is:

```text
F = <ConfiguredGitHEAD, RuntimeSourceFrontier, MCPSurfaceSignature>
RuntimeSourceFrontier = <status, mode, repo, head, root, attestation_level>
MCPSurfaceSignature = digest(TOOLS, PROMPTS)
```

For each query:

```text
G0 = configured Git head
R0 = runtime source frontier
S0 = live MCP signature
validate optional configured/runtime expected-head CAS
K0 = <G0,R0,S0>

if cache.key != K0:
    compile configured tree pinned to G0
    compile runtime tree pinned to R0.head when checkout exists
    compile MCP definitions at <R0.repo,R0.head>
    federate roots
    build deterministic query index
    compute PATLASV2 snapshot ID

G1,R1,S1 = reobserve all three clocks
if <G1,R1,S1> == <G0,R0,S0>:
    accept/cache snapshot
else:
    invalidate and retry once

if still moving:
    HOLD_VOLATILE_FRONTIER
```

Dirty worktree state is observed separately from committed identity.

## Read-only metering firewall

The ordinary MCP dispatcher records tool usage as learned operational telemetry. Project Atlas reads register their four RPCs as non-self-metering before post-call accounting.

`PROJECT_QUERY != PERSISTENT_STATE_MUTATION`.

This grants no Git, semantic, Y1, release, deployment or execution authority.

## Composition

V2 composes through `AorDevelopmentSurface`:

- `project_atlas_protocol.py` — bounded RPC schemas/resource;
- `project_atlas_runtime_provenance.py` — runtime-source resolver;
- `project_atlas_query_index.py` — deterministic federated index;
- `project_atlas_surface.py` — snapshot/query/router membrane;
- `AOR_DEVELOPMENT_TOOLS/RESOURCES` — modular exposure;
- `SURFACE.2` — required mature surface group;
- `COMPOSITION.2` — resident organ + read-only probe.

No Project Atlas branch is added to the central `Server.call_tool` switch.

Machine contract: `spec/KC144_PROJECT_ATLAS_MCP_SURFACE_V2.json`.

Schema: `schemas/project_atlas_mcp_surface_v2.schema.json`.

## Core laws

```text
V2_DEPENDS_ON_V1
KC144_STATION != OBJECT_IDENTITY
POID != OID != MID != VID
CONFIGURED_GIT_HEAD != RUNTIME_GIT_HEAD
PACKAGE_VERSION != RUNTIME_SOURCE_HEAD
MCP_VIRTUAL_OBJECT != GIT_BLOB
MCP_DEFINITION_COORDINATE_REQUIRES_RUNTIME_SOURCE_HEAD
UNKNOWN_RUNTIME_TREE != EMPTY_RUNTIME_TREE
QUERY_INDEX != SEMANTIC_IDENTITY
PROJECT_ATLAS_SNAPSHOT_ID != PROMOTION_RECEIPT
PROJECT_QUERY != PROMOTION_AUTHORITY
PROJECT_QUERY != PERSISTENT_STATE_MUTATION
PROJECT_ROUTE != SEMANTIC_EQUIVALENCE
AMBIGUOUS_RESOLVE -> HOLD
STALE_CONFIGURED_HEAD -> HOLD
STALE_RUNTIME_HEAD -> HOLD
CONFIGURED_HEAD_CHANGE -> RECOMPILE
RUNTIME_HEAD_CHANGE -> RECOMPILE
MCP_SURFACE_CHANGE -> RECOMPILE
MOVING_PROJECT_FRONTIER -> BOUNDED_RETRY -> HOLD
CROSS_REPO_ROUTE_REQUIRES_EXACT_REPO_HEAD
RPC_SURFACE_EXISTENCE != CANONICAL_RPC_PROMOTION
GREEN_CHILD_HEAD != ACCEPTED_ANCESTRY
QUALIFICATION_PR != INTEGRATION_PR
```

## Promotion boundary

V2 intentionally does **not** change the canonical package/release version while it is a child of unmerged V1.

Before canonical promotion:

1. V1 must be accepted or V2 rebased to its accepted successor ancestry.
2. Exact rebased V2 head must pass the complete qualification lattice.
3. Public package/protocol/release identity must advance lawfully for the new canonical RPC surface.
4. A clean-wheel installed-surface witness must verify the V2 ABI.
5. Production configuration must supply exact runtime-source provenance when not running from a source checkout.
6. Publication requires separate authority.
7. Deployment requires separate authority.

`CANDIDATE_SURFACE != RELEASE_VERSION`.
