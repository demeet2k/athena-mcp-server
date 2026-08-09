# KC144 Project Atlas MCP Surface V2

`ATHENA.PROJECT_ATLAS.MCP_SURFACE.V2` projects the read-only V1 Project Atlas into a bounded federated MCP query interface.

It is a **query membrane**, not a new identity system.

```text
CONFIGURED GIT / ATHENA_GIT_ROOT ─┐
                                  ├─> FEDERATED KC144 PROJECT SNAPSHOT
RUNTIME SOURCE GIT ───────────────┤          │
                                  │          ├─ summary
LIVE MCP TOOLS + PROMPTS ─────────┘          ├─ resolve
                                             ├─ list
                                             └─ route -> native RETURN
```

## Ancestry

V2 is developed from the exact V1 candidate:

`fc376ffa76864f173049164db9206295b96ec85b`.

Until V1 is accepted, V2 remains a child candidate. If V1 is rebased, changed or merged under a different commit, V2 must rebase and requalify; a green old child head is not current evidence.

## Three distinct project planes

V2 explicitly refuses the earlier accidental collapse:

`CONFIGURED_GIT_HEAD != RUNTIME_GIT_HEAD`.

### 1. Configured Git

`ATHENA_GIT_ROOT` is the Git plane already owned by `GitBackend`. In ATHENA deployments this is commonly the canonical/private Git brain.

Its exact coordinate is independently observed as:

`<repo, ref/head, tree, path, object_sha>`.

### 2. Runtime-source Git

MCP definitions belong to the runtime package/repository frontier, not automatically to `ATHENA_GIT_ROOT`.

Exact runtime provenance is resolved in this priority order:

1. `ATHENA_RUNTIME_GIT_ROOT` — explicit exact runtime checkout;
2. package source checkout — accepted only when `athena_mcp/` sits directly beneath that checkout's `.git` root;
3. `ATHENA_RUNTIME_REPOSITORY` + exact 40-hex `ATHENA_RUNTIME_GIT_HEAD` attestation;
4. otherwise `HOLD_RUNTIME_PROVENANCE`.

A wheel version alone is **not** an exact Git source coordinate.

`PACKAGE_VERSION != RUNTIME_SOURCE_HEAD`.

When runtime provenance includes a checkout, V2 also compiles its full Git tree atlas. When only repository+head attestation exists, MCP objects are exactly head-qualified but runtime tree enumeration remains unavailable.

### 3. MCP virtual surface

Every live installed `TOOLS + PROMPTS` definition is projected as an MCP virtual object using the **runtime-source repository/head**.

It is never qualified by the configured/private brain HEAD.

`MCP_DEFINITION_COORDINATE_REQUIRES_RUNTIME_SOURCE_HEAD`.

If exact runtime provenance is missing, MCP coordinates HOLD rather than borrowing another Git clock.

## Surface

### `athena_project_atlas_summary`

Returns only bounded top-level state:

- separate configured and runtime heads;
- configured Git atlas digest/counts;
- runtime-source provenance and, when available, runtime Git tree/digest/counts;
- installed MCP surface repo/head/count/digest plus live surface signature;
- federation digest;
- dirty/branch observations;
- pagination limits and laws.

It does **not** return every atlas record.

Optional CAS inputs:

- `expected_head` = configured Git HEAD;
- `expected_runtime_head` = runtime-source Git HEAD.

Both are exact 40-hex commit identities.

### `athena_project_resolve`

Accepted exact identifiers:

- `POID.*`;
- exact Git path, including legal dot-prefixed paths such as `.github/...`;
- full `PROJECT_KC144...` address;
- exact native `athena+git://...` or `athena+mcp://...` RETURN URI;
- exact MCP name;
- typed MCP aliases `tool:<name>`, `prompt:<name>`, `mcp:tool:<name>`, `mcp:prompt:<name>`;
- MCP virtual locator path.

Resolution spans:

- `configured_git`;
- `runtime_git` when exact runtime tree is available;
- `mcp`.

A plain path appearing in both Git repositories is ambiguous by design.

If zero records match and runtime provenance is complete: `HOLD_NOT_FOUND`.

If zero records match but runtime provenance is incomplete: `HOLD_RUNTIME_PROVENANCE` because the searched universe is incomplete.

If more than one record matches: `HOLD_AMBIGUOUS` with at most 20 bounded candidate summaries.

No textual-order, configured-Git-first, or MCP-first tie break is permitted.

### `athena_project_list`

Deterministic bounded page over the federated record set.

Sources:

- `all`;
- `git` = union of configured/runtime Git planes;
- `configured_git`;
- `runtime_git`;
- `mcp`.

Filters:

- path prefix;
- native type;
- PROJECT_KC144 GID/row/column;
- KC144 reference GID;
- parent directory;
- MCP kind `{tool,prompt}`;
- POID prefix.

Pagination:

- default `50`;
- maximum `100`;
- explicit non-negative offset;
- `next_offset=null` at exhaustion.

No unbounded atlas response is available through this RPC.

### `athena_project_route`

1. Compile/resolve one federated exact snapshot.
2. Resolve source exactly.
3. Resolve destination exactly.
4. HOLD if either endpoint is missing or ambiguous.
5. Compute deterministic V1 PROJECT_KC144 station navigation.
6. Return bounded endpoint records and both native RETURN witnesses.
7. If endpoints lie on different `<repo,head>` frontiers, return an explicit federation transition carrying the federation digest and both repository heads.

`wrap=false` uses ordinary grid navigation.

`wrap=true` uses the 12×12 toroidal route.

`PROJECT_ROUTE != SEMANTIC_EQUIVALENCE`.

`CROSS_REPO_ROUTE_REQUIRES_EXACT_REPO_HEAD`.

### `athena://project-atlas`

Read-only bounded federated summary resource. Full navigation remains tool-mediated.

## Freshness algorithm

The live project frontier is factorized because the three planes may change independently:

```text
F = <ConfiguredGitHEAD, RuntimeSourceFrontier, MCPSurfaceSignature>
MCPSurfaceSignature = digest(TOOLS, PROMPTS)
RuntimeSourceFrontier = <status, mode, repo, head, root>
```

For query `q(expected_head, expected_runtime_head)`:

```text
G0 = configured Git status/head
R0 = resolve exact runtime source frontier
S0 = digest(current TOOLS, current PROMPTS)

if expected_head != null and expected_head != G0.head:
    HOLD_STALE_CONFIGURED_HEAD

if expected_runtime_head != null:
    if R0 unresolved: HOLD_RUNTIME_PROVENANCE
    if expected_runtime_head != R0.head: HOLD_STALE_RUNTIME_HEAD

K0 = <G0.head, R0, S0>
if cache.key == K0:
    candidate = cache.value
else:
    compile configured atlas pinned to G0.head
    compile runtime atlas pinned to R0.head when checkout exists
    compile MCP surface at <R0.repo,R0.head>
    federate exact roots

G1 = configured Git status/head
R1 = resolve runtime source frontier again
S1 = digest(current TOOLS, current PROMPTS)

if G1.head == G0.head == candidate.configured_head
   and R1 == R0
   and S1 == S0:
    cache(K0, candidate)
    use candidate
else:
    invalidate cache and retry once

if any coordinate remains moving:
    HOLD_VOLATILE_FRONTIER
```

Dirty worktree state is observed separately and does not rewrite committed atlas identity.

`CONFIGURED_HEAD_CHANGE -> RECOMPILE`.

`RUNTIME_HEAD_CHANGE -> RECOMPILE`.

`MCP_SURFACE_CHANGE -> RECOMPILE`.

## Read-only metering firewall

The normal MCP dispatcher records runtime-tool usage as learned operational telemetry. That would make a Project Atlas read mutate persistent runtime-learning state merely because the project observed itself.

Therefore the V2 calls register themselves into the dispatcher's non-self-metering set before post-call accounting:

`PROJECT_QUERY != PERSISTENT_STATE_MUTATION`.

This changes process-local dispatch accounting only; it grants no Git, semantic, Y1, release or execution authority.

## Composition

V2 is composed through `AorDevelopmentSurface`:

- `project_atlas_protocol.py` — schemas/resource;
- `project_atlas_runtime_provenance.py` — exact runtime-source resolver;
- `project_atlas_surface.py` — bounded federated read-only behavior;
- `AOR_DEVELOPMENT_TOOLS/RESOURCES` — modular exposure;
- `SURFACE.2` — required mature surface group;
- `COMPOSITION.2` — resident organ + read-only probe.

No Project Atlas branch is added to the central `Server.call_tool` switch.

## Laws

```text
V2_DEPENDS_ON_V1
KC144_STATION != OBJECT_IDENTITY
POID != OID != MID != VID
CONFIGURED_GIT_HEAD != RUNTIME_GIT_HEAD
PACKAGE_VERSION != RUNTIME_SOURCE_HEAD
MCP_VIRTUAL_OBJECT != GIT_BLOB
MCP_DEFINITION_COORDINATE_REQUIRES_RUNTIME_SOURCE_HEAD
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
```

## Promotion boundary

V2 intentionally does **not** change the canonical package/release version while it is a child of an unmerged V1 PR.

Before canonical promotion:

1. V1 must be accepted or V2 must rebase to its accepted successor ancestry.
2. Exact rebased V2 head must pass the full syntax/unit/critical-invariants/smoke lattice.
3. The public package/protocol/release coordinate must advance lawfully for the newly canonical RPC surface.
4. Clean-wheel installation must expose the same query surface.
5. Production runtime configuration must supply an exact runtime-source frontier when the package is not running from a source checkout.
6. Publication and deployment remain separately authorized transitions.

`CANDIDATE_SURFACE != RELEASE_VERSION`.
