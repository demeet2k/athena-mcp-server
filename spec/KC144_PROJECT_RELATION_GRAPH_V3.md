# KC144 Project Relation Graph V3

Status: **candidate child of unmerged Project Atlas MCP Surface V2; not canonical, not published, not deployed**.

Private work order: `demeet2k/Athena#508`.

Exact ancestry at V3 branch creation:

- repository: `demeet2k/athena-mcp-server`
- V2 integration PR: `#310`
- exact V2 parent head: `c7445bcd70a354e5deb912add6716d7e5191e02c`
- V3 integration PR: `#335`
- V3 qualification-only PR: `#336`
- V2 snapshot namespace: `PATLASV2.*`

`QUALIFICATION_PR != INTEGRATION_PR != PROMOTION`.

## 1. Purpose: add a second navigation geometry

Project Atlas V1 makes tracked project objects exactly addressable. V2 makes those addresses queryable across configured Git, runtime Git, and live MCP planes and supplies a KC144 station route. That station route is geometric. It does not prove that one project object imports, contains, references, tests, supports, or semantically equals another.

V3 adds a **typed, witnessed project-relation graph** while preserving the V1/V2 coordinate system:

```text
NATIVE IDENTITY
    |
    v
POID stable path identity
    |
    v
PVTX exact federated manifestation
    |
    +------> PROJECT_KC144 / KC144_REFERENCE
    |                    |
    |                    +--> V2 geometric station route
    |
    +------> V3 typed relation graph
                         |
                         v
                       RETURN
```

Constitutional distinction:

`COORDINATE_ADJACENCY != STRUCTURAL_EDGE != SEMANTIC_EQUIVALENCE`.

## 2. Exact V3 vertex identity: POID is not enough

V1 POID is intentionally stable over project path identity:

```text
POID = f(repo, path, git_type)
```

That means the same POID can legitimately occur in both V2 `configured_git` and `runtime_git` planes, or at different exact heads. A federated graph therefore cannot use POID alone as its node key.

V3 introduces the exact manifestation coordinate:

```text
PVTX = digest(<plane, repo, head, POID>)
```

Namespace: `PVTX.*`.

Laws:

- `POID != FEDERATED_VERTEX_ID`
- `SAME_POID_ACROSS_FRONTIERS != SAME_MANIFESTATION`
- `AMBIGUOUS_POID_ACROSS_FRONTIERS -> HOLD_AMBIGUOUS_VERTEX`

A graph query should use exact PVTX. Bare POID is accepted only when exactly one PVTX manifestation carries that POID in the current exact snapshot. If multiple manifestations exist, V3 returns the candidate PVTX coordinates and refuses to choose silently.

## 3. Exact V2 snapshot adapter

V2 does not expose a single flat V1 atlas. Its exact runtime snapshot is:

```text
ATHENA.KC144.FEDERATED_RUNTIME_PROJECT_ATLAS.V2

<
  configured_git,
  runtime_git,
  runtime_git_is_configured,
  runtime_provenance,
  runtime_tree_available,
  mcp_surface,
  federation,
  live_surface_signature,
  query_index,
  PATLASV2 snapshot_id
>
```

V3 therefore uses an explicit adapter:

`ATHENA.PROJECT_ATLAS.V2_TO_RELATION_GRAPH.V3.ADAPTER.v1`.

Its plane rules are exact:

1. Every configured record is tagged `source=configured_git`.
2. A distinct runtime atlas is tagged `source=runtime_git`.
3. If `runtime_git_is_configured=true`, V2 has already proven that runtime and configured trees are the same runtime manifestation, so V3 does **not** manufacture a duplicate runtime plane.
4. MCP surface records are tagged `source=mcp` and become exact PVTX vertices.
5. MCP virtual records never pass through Git hierarchy/import/path extractors.
6. Optional MCP geometric edges may be compiled only as `KC144_GRID_ADJACENT` with `COORDINATE_ONLY` authority.

Laws:

- `V2_SNAPSHOT_PLANES != FLAT_V1_ATLAS`
- `CONFIGURED_GIT_VERTEX != RUNTIME_GIT_VERTEX_UNLESS_V2_COLLAPSES_RUNTIME_TO_CONFIGURED`
- `MCP_VIRTUAL_VERTEX != GIT_BLOB_VERTEX`
- `UNKNOWN_RUNTIME_TREE != EMPTY_RUNTIME_TREE`

### 3.1 Snapshot completeness is not content-extractor completeness

The V2 snapshot can know an exact Git tree without embedding every blob body in the durable snapshot. Content-derived V3 extractors such as Python imports and exact scalar path references therefore require an exact Git object reader for each Git plane they inspect.

V3 records three independent coverage dimensions:

```text
SNAPSHOT STATUS
  = is the PATLASV2 federation itself GENERATED or partial?

TREE COVERAGE
  = which configured/runtime Git trees are actually enumerated?

CONTENT-READER COVERAGE
  = for which Git planes can V3 read the exact blob object bodies?
```

The states are deliberately distinct:

```text
GENERATED snapshot + all required blob readers
    -> EXACT_V2_SNAPSHOT

GENERATED snapshot + missing required blob reader(s)
    -> EXACT_V2_SNAPSHOT_PARTIAL_CONTENT

non-GENERATED / provenance-hold snapshot
    -> PARTIAL_V2_SNAPSHOT
```

Laws:

- `PARTIAL_V2_SNAPSHOT -> PARTIAL_GRAPH_COVERAGE_RECEIPT`
- `EXACT_V2_SNAPSHOT != COMPLETE_CONTENT_EXTRACTION_IF_BLOB_READERS_MISSING`

This prevents absence of an import/reference edge from being mistaken for evidence that the relation does not exist when the relevant blob body was never observed.

### 3.2 Runtime content root

If the caller supplies an explicit `runtime_root`, that is used. Otherwise V3 derives the runtime content root from exact `RESOLVED` V2 `runtime_provenance.root` when present.

`RUNTIME_CONTENT_ROOT_DEFAULTS_TO_EXACT_V2_RUNTIME_PROVENANCE_ROOT`.

The configured checkout root remains an explicit adapter input because V1/V2 deliberately exclude local checkout location from durable committed-frontier identity.

## 4. Graph object and two-stage replay identity

For one exact V2 snapshot `s`:

```text
G_s = (V_s, E_s)
```

where:

- `V_s` is the exact PVTX manifestation set available through the adapter;
- every PVTX retains its source POID plus plane/repo/head/path/object witness;
- `E_s` is the deterministically extracted typed relation set;
- every edge endpoint must be in `V_s`;
- every edge carries the same `PATLASV2.*` snapshot witness.

V3 deliberately separates **what graph was emitted** from **what the observation process was capable of emitting**.

### 4.1 Base graph identity

The kernel first computes a base graph identity from the exact snapshot, exact vertices, and emitted typed edges:

```text
BASE_PATLASG3 = digest(
  graph_schema,
  exact_snapshot_id,
  sorted_exact_PVTX_receipts,
  sorted_typed_edge_receipts
)
```

This answers: *given this supplied record set and these emitted edges, what exact V/E graph exists?*

### 4.2 Adapted graph identity

When the graph is compiled from a V2 runtime snapshot, CAS uses an adapted identity with schema:

`ATHENA.PROJECT_ATLAS.RELATION_GRAPH.V3.ADAPTED_IDENTITY.v1`.

```text
PATLASG3 = digest(
  adapter_schema/version,
  BASE_PATLASG3,
  exact_PATLASV2_snapshot_id,
  snapshot_status,
  runtime_provenance_status,
  runtime_tree_available,
  runtime_git_is_configured,
  content_reader_planes,
  required_content_planes,
  missing_content_reader_planes,
  exact_extraction_option_profile
)
```

This distinction is necessary because equal visible edge sets do **not** imply equal observations. For example, a relation class can be absent because:

1. the extractor ran and found no relation;
2. the extractor was disabled by policy;
3. the extractor was enabled but the relevant blob plane was unreadable.

Those three states have different epistemic meaning. If they shared one graph ID, a stale-graph CAS check could silently erase the difference between observed absence and unobserved possibility.

Therefore:

- `GRAPH_ID_BINDS_EXTRACTION_PROFILE_AND_COVERAGE`
- `SAME_VISIBLE_EDGES_WITH_DIFFERENT_OBSERVABILITY != SAME_GRAPH_RECEIPT`
- `BASE_GRAPH_ID != ADAPTED_GRAPH_ID` as a namespace role distinction, even when both use `PATLASG3.*` formatting
- V2-adapted graph queries use the **adapted** graph ID for `expected_graph_id` CAS.

The adapter receipt exposes both `base_graph_id` and `adapted_graph_id`, plus `identity_basis_digest`, extraction profile, and coverage receipt, so replay can reconstruct why the graph CAS identity has that value.

Graph identity is replay identity, not authority:

`PATLASG3 != PROMOTION_RECEIPT != RELEASE_RECEIPT != DEPLOYMENT_RECEIPT`.

## 5. Edge contract

A V3 relation is:

```text
E = <
  edge_id,
  kind,
  src_vertex_id,
  dst_vertex_id,
  src_poid,
  dst_poid,
  plane,
  extractor,
  evidence,
  witness,
  confidence,
  authority,
  loss,
  snapshot_id,
  RETURN(src,dst)
>
```

`edge_id` uses the `PEDGE.*` namespace and is content-derived from the relation as stated and the **exact PVTX endpoints**, never from list position.

Stable POIDs remain visible for project-level identity while exact PVTX endpoints prevent frontier collapse.

## 6. Native structural edge classes

### 6.1 Git hierarchy

`DIR_CONTAINS(parent_tree, child_entry)` and inverse `DIR_PARENT_OF(child_entry, parent_tree)` are emitted only when the exact parent tree record exists in the same `<plane,repo,head>` frontier.

Extractor: `git_tree_hierarchy_v1`.

Evidence: `EXACT_GIT_TREE`.

No synthetic root object is invented. Missing parent tree data yields a witnessed `HOLD_EDGE`.

### 6.2 Python imports

Python imports are parsed with the Python AST and resolved only against the local-module index of the same exact `<plane,repo,head>` frontier.

Kinds:

- `PY_IMPORTS`
- `PY_RELATIVE_IMPORTS`

Relative import resolution respects package level. A local edge is emitted only after unique resolution.

External or otherwise unresolved imports are conserved as:

`UNRESOLVED_EXTERNAL_OR_LOCAL_UNKNOWN`.

Ambiguous local module resolution yields `HOLD_EDGE`; it is not downgraded to unknown-external.

Laws:

- `IMPORT_STRING != RESOLVED_LOCAL_IMPORT`
- `UNRESOLVED_IMPORT -> CONSERVE_UNKNOWN`
- `AMBIGUOUS_EDGE_TARGET -> HOLD_EDGE`

### 6.3 Same-blob alias

Records sharing one exact Git object SHA in the same frontier receive symmetric `SAME_BLOB_ALIAS` edges while retaining distinct POIDs and PVTX identities.

`SAME_BLOB_ALIAS != SAME_OBJECT`.

The implementation uses a deterministic star over the sorted alias group instead of an unbounded all-pairs expansion. Connectivity is retained while edge growth stays bounded.

### 6.4 Exact path reference

`EXACT_PATH_REFERENCE` is intentionally conservative. V3 currently extracts scalar strings from parseable Python, JSON, and TOML and emits an edge only when the normalized scalar equals exactly one repository-relative path in the same frontier.

No substring, filename-similarity, embeddings, or narrative inference are used.

Authority: `REFERENCE_OBSERVATION`.

Loss law: `REFERENCE_DOES_NOT_IMPLY_RUNTIME_DEPENDENCY`.

## 7. Optional KC144 geometric overlay

`KC144_GRID_ADJACENT` is disabled by default. When explicitly enabled, it links exact PVTX manifestations whose PROJECT_KC144 stations are cardinal neighbors inside one exact frontier.

Authority: `COORDINATE_ONLY`.

Loss witness:

`GEOMETRIC_ADJACENCY_HAS_NO_DEPENDENCY_OR_SEMANTIC_EQUIVALENCE CLAIM`.

Thus the same graph engine can traverse the KC144 overlay without pretending geometry is dependency.

## 8. Determinism and replay invariants

Required invariants:

1. Reversing input record order does not change the base graph identity.
2. Changing the witnessed edge set changes the base graph identity.
3. Same blob does not collapse distinct project objects.
4. Same POID in two planes/heads produces two PVTX manifestations.
5. Bare-POID lookup with multiple PVTX manifestations fails closed.
6. Every edge PVTX endpoint resolves in the exact vertex set.
7. Every edge snapshot equals the graph snapshot.
8. MCP virtual objects are not interpreted as Git blobs.
9. Missing blob readers produce partial-content receipts rather than false negative edges.
10. Extraction failure remains HOLD/unknown rather than absence-as-proof.
11. Equal visible V/E under different extraction profiles produces different adapted graph IDs.
12. Equal visible V/E under different reader coverage produces different adapted graph IDs.
13. Recompiling the same exact V2 snapshot with the same extraction profile and coverage reproduces the same adapted graph ID.

## 9. Navigation calculus

V3 currently provides internal bounded graph primitives. It intentionally does **not** add canonical MCP graph RPC names yet.

### 9.1 Locator resolution

```text
exact PVTX             -> RESOLVED
POID with one PVTX     -> RESOLVED
POID with >1 PVTX      -> HOLD_AMBIGUOUS_VERTEX
unknown locator        -> HOLD_UNKNOWN_VERTEX
```

### 9.2 Neighbors

`neighbors(locator, direction, kinds, offset, limit, expected_snapshot_id, expected_graph_id)`

- `direction ∈ {out,in,both}`;
- edge kinds are explicit;
- page limit is bounded at 100;
- stale snapshot/graph CAS fails closed;
- ambiguous or unknown locator fails closed;
- `expected_graph_id` compares against the adapted graph ID when using the V2 adapter.

### 9.3 BFS

BFS returns deterministic minimum-edge traversal over an explicit edge-kind set.

Default route domain is structural only. Geometric edges are excluded unless selected.

### 9.4 Dijkstra

Dijkstra exists only with explicit caller-supplied finite non-negative weights for **every selected edge kind**.

There is no hidden project-value scalarization.

`PATH_COST_WEIGHTS_ARE_EXPLICIT_INPUT_NOT_HIDDEN_TRUTH`.

### 9.5 Route cost vector

Every successful route returns a descriptive vector:

```text
C(route) = <
  structural_hops,
  authority_friction,
  uncertainty,
  plane_crossings,
  coordinate_hops
>
```

This vector is not a truth score.

`PATH_COST != TRUTH`.

## 10. Hold lattice

V3 preserves explicit non-success states including:

- `HOLD_EDGE`
- `HOLD_STALE_SNAPSHOT`
- `HOLD_STALE_GRAPH`
- `HOLD_UNKNOWN_VERTEX`
- `HOLD_AMBIGUOUS_VERTEX`
- `HOLD_EXPANSION_LIMIT`
- `HOLD_DEPTH_LIMIT`
- `HOLD_NO_PATH`

Unknown is never silently converted to zero edges, zero cost, or negative evidence.

## 11. Authority and semantic boundary

V3 is a **structural observation graph**, not a semantic claim graph.

It does not infer from adjacency that one object:

- supports another claim;
- contradicts another claim;
- causes another state;
- is equivalent to another object;
- is approved for execution;
- is canonical.

Those relations require separate evidence/authority contracts.

Core laws:

- `EDGE != CLAIM_OF_SEMANTIC_EQUIVALENCE`
- `KC144_GRID_ADJACENT != DEPENDS_ON`
- `GRAPH_QUERY != PROMOTION_AUTHORITY`
- `ROUTE != EXECUTION`
- `STRUCTURAL_GRAPH_ROUTE != KC144_GEOMETRIC_ROUTE != EXECUTION`
- `EDGE_CLASS_CHANGE_REQUIRES_GRAPH_SCHEMA_BUMP`

## 12. Qualification membrane

Repository PR workflows qualify changes only when a PR targets `master`, while the intended V3 ancestry is V3 -> V2 -> V1. Therefore V3 uses two PRs with distinct meanings:

- `#335`: **integration ancestry**, targeting the unmerged V2 branch;
- `#336`: **qualification only**, targeting `master` so current CI/release workflows execute on the exact V3 head.

A green #336 is an execution witness for the candidate head, not authority to merge #336.

`QUALIFICATION_PR != INTEGRATION_PR != PROMOTION`.

## 13. Promotion boundary

V3 remains a child experiment of unmerged V2. Before any canonical MCP graph RPC promotion, separately require:

1. accepted V1/V2 ancestry;
2. exact rebased V3 candidate;
3. full current CI success on that exact candidate head;
4. current V3.4 release-distribution qualification on the same head;
5. explicit protocol/package version decision before exposing graph RPC names;
6. clean installed-wheel surface witness if RPCs are added;
7. private Athena brain integration/review;
8. separate publication authority;
9. separate deployment authority.

No V3 code path grants itself publication, deployment, merge, or promotion authority.
