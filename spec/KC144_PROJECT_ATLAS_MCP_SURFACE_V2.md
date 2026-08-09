# KC144 Project Atlas MCP Surface V2

`ATHENA.PROJECT_ATLAS.MCP_SURFACE.V2` projects the read-only V1 Project Atlas into a bounded native MCP query interface.

It is a **query membrane**, not a new identity system.

```text
V1 PROJECT ATLAS
    ↓ exact configured Git HEAD
V2 SNAPSHOT
    ↓
{summary, resolve, list, route, resource}
    ↓
native Git/MCP RETURN
```

## Ancestry

V2 is developed from the exact V1 candidate:

`fc376ffa76864f173049164db9206295b96ec85b`.

Until V1 is accepted, V2 remains a child candidate. If V1 is rebased, changed or merged under a different commit, V2 must rebase and requalify; a green old child head is not current evidence.

## Surface

### `athena_project_atlas_summary`

Returns only bounded top-level state:

- exact `repo/ref/head/tree`;
- Git atlas digest and counts;
- installed MCP surface count/digest;
- federation digest;
- current dirty/branch observation;
- pagination limits and laws.

It does **not** return every atlas record.

### `athena_project_resolve`

Accepted exact identifiers:

- `POID.*`;
- exact Git path, including legal dot-prefixed paths such as `.github/...`;
- full `PROJECT_KC144...` address;
- exact native `athena+git://...` or `athena+mcp://...` RETURN URI;
- exact MCP name;
- typed MCP aliases `tool:<name>`, `prompt:<name>`, `mcp:tool:<name>`, `mcp:prompt:<name>`;
- the MCP virtual locator path.

If zero records match: `HOLD_NOT_FOUND`.

If more than one record matches: `HOLD_AMBIGUOUS` with at most 20 bounded candidate summaries.

No textual-order or Git-before-MCP tie break is permitted.

### `athena_project_list`

Deterministic bounded page over Git + MCP records.

Filters:

- source `{all,git,mcp}`;
- path prefix;
- Git/native type;
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

1. Compile/resolve one exact snapshot.
2. Resolve source exactly.
3. Resolve destination exactly.
4. HOLD if either endpoint is missing or ambiguous.
5. Compute the deterministic V1 PROJECT_KC144 station route.
6. Return bounded endpoint records and both native RETURN witnesses.

`wrap=false` uses ordinary grid navigation.

`wrap=true` uses the 12×12 toroidal route.

`PROJECT_ROUTE != SEMANTIC_EQUIVALENCE`.

### `athena://project-atlas`

Read-only bounded summary resource. Full navigation remains tool-mediated.

## Freshness algorithm

For query `q(expected_head)`:

```text
G0 = configured Git status/head
if expected_head != null and expected_head != G0.head:
    HOLD_STALE_HEAD
compile atlas pinned to immutable SHA G0.head
G1 = configured Git status/head
if G1.head == G0.head == atlas.head:
    use snapshot
else:
    invalidate cache and retry once
if still moving:
    HOLD_VOLATILE_HEAD
```

The snapshot cache key is the exact Git HEAD. Dirty worktree state is observed separately and does not rewrite committed atlas identity.

## Read-only metering firewall

The normal MCP dispatcher records runtime-tool usage as learned operational telemetry. That would make a Project Atlas read mutate persistent runtime-learning state merely because the project observed itself.

Therefore the V2 calls register themselves into the dispatcher's non-self-metering set before post-call accounting:

`PROJECT_QUERY != PERSISTENT_STATE_MUTATION`.

This changes process-local dispatch accounting only; it grants no Git, semantic, Y1, release or execution authority.

## Composition

V2 is composed through `AorDevelopmentSurface`:

- `project_atlas_protocol.py` — schemas/resource;
- `project_atlas_surface.py` — bounded read-only behavior;
- `AOR_DEVELOPMENT_TOOLS/RESOURCES` — modular exposure;
- `SURFACE.2` — required mature surface group;
- `COMPOSITION.2` — resident organ + read-only probe.

No new Project Atlas branch is added to the central `Server.call_tool` switch.

## Laws

```text
V2_DEPENDS_ON_V1
KC144_STATION != OBJECT_IDENTITY
POID != OID != MID != VID
MCP_VIRTUAL_OBJECT != GIT_BLOB
PROJECT_QUERY != PROMOTION_AUTHORITY
PROJECT_QUERY != PERSISTENT_STATE_MUTATION
PROJECT_ROUTE != SEMANTIC_EQUIVALENCE
AMBIGUOUS_RESOLVE -> HOLD
STALE_EXPECTED_HEAD -> HOLD
MOVING_HEAD -> BOUNDED_RETRY -> HOLD
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
5. Publication and deployment remain separately authorized transitions.

`CANDIDATE_SURFACE != RELEASE_VERSION`.
