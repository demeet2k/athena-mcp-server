# KC144 Project Relation Graph V3

Status: **candidate child of unmerged Project Atlas MCP Surface V2; not canonical, not published, not deployed**.

Private work order: `demeet2k/Athena#508`.

Exact parent at branch creation:

- repository: `demeet2k/athena-mcp-server`
- V2 PR: `#310`
- parent head: `c7445bcd70a354e5deb912add6716d7e5191e02c`
- V3 integration PR: `#335`
- qualification-only PR: `#336`
- V2 parent snapshot namespace: `PATLASV2.*`

## 1. Why V3 exists

V1 made project objects exactly addressable. V2 made those addresses queryable and routable across configured Git, runtime Git and MCP planes. V2 `athena_project_route` is deliberately a **KC144 station route**. It answers how two exact objects are positioned on the project chart; it does not assert that one object imports, contains, references, tests, supports or semantically equals the other.

V3 adds a second geometry: a typed relation graph over exact Project Atlas manifestations.

```text
GEOMETRIC NAVIGATION: PROJECT_KC144 station -> station
STRUCTURAL NAVIGATION: PVTX --typed witnessed edge--> PVTX
NATIVE RETURN:         each endpoint -> exact head-qualified Git/MCP witness
```

The distinction is constitutional:

`COORDINATE_ADJACENCY != STRUCTURAL_EDGE != SEMANTIC_EQUIVALENCE`.

## 2. POID is not a federated vertex

A critical V3 invariant follows directly from V2's configured/runtime clocks.

Project Atlas POID is intentionally stable over path identity:

```text
POID = f(repo, path, git_type)
```

Therefore the same repository path may have the **same POID** in both configured and runtime planes, or at two exact Git heads. That stability is useful, but it means bare POID is not sufficient to identify one node in a federated V2 snapshot.

V3 introduces an exact manifestation coordinate:

```text
PVTX = digest(<plane, repo, head, POID>)
```

Namespace: `PVTX.*`.

The laws are:

`POID != FEDERATED_VERTEX_ID`.

`SAME_POID_ACROSS_FRONTIERS != SAME_MANIFESTATION`.

`AMBIGUOUS_POID_ACROSS_FRONTIERS -> HOLD_AMBIGUOUS_VERTEX`.

A query may use bare POID only when exactly one PVTX carrying that POID exists in the current exact snapshot. Otherwise the graph returns all candidate PVTX IDs and refuses to choose silently.

This gives a clean factorization:

```text
stable project identity       exact graph manifestation
POID -----------------------> PVTX(<plane,repo,head,POID>)
```

## 3. Graph object

For one exact V2 snapshot `s`:

`G_s = (V_s, E_s)`

where:

- `V_s` is the exact PVTX manifestation set available in the supplied atlas;
- each PVTX retains its source POID plus plane/repo/head/path/object witness;
- `E_s` is the deterministically extracted typed relation set;
- every edge endpoint must be a member of `V_s`;
- every edge carries the same `PATLASV2.*` snapshot witness;
- graph identity is `PATLASG3.<digest>` over exact sorted PVTX receipts + typed edge receipts + snapshot coordinate.

Graph identity is not a promotion receipt:

`PATLASG3 != RELEASE_RECEIPT != DEPLOYMENT_RECEIPT`.

## 4. Edge contract

A V3 relation is represented as:

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

`edge_id = PEDGE.<digest>` is derived from the relation as stated and its **exact PVTX endpoints**, not from list position. Edge enumeration therefore cannot change identity.

The POID fields remain visible for stable project-level navigation; PVTX fields prevent frontier collapse.

### 4.1 Exact Git hierarchy

`DIR_CONTAINS(parent_tree, child_entry)` and inverse `DIR_PARENT_OF(child_entry, parent_tree)` are emitted only when the exact parent tree record exists in the same `<plane,repo,head>` frontier.

Extractor: `git_tree_hierarchy_v1`.

Evidence: exact Git tree paths under one head.

A missing parent tree record yields `HOLD_EDGE`; V3 never invents a synthetic root POID/PVTX.

### 4.2 Python import relations

Python imports are parsed with the Python AST. Local module candidates are indexed only inside the same exact `<plane,repo,head>` frontier.

- `PY_IMPORTS`
- `PY_RELATIVE_IMPORTS`

A local edge is emitted only after unique module resolution. Relative import resolution respects package level. External or otherwise unresolved imports are retained in `unresolved_imports` with standing `UNRESOLVED_EXTERNAL_OR_LOCAL_UNKNOWN`.

Ambiguous local module resolution is not downgraded to unknown-external; it produces a witnessed `HOLD_EDGE`.

`IMPORT_STRING != RESOLVED_LOCAL_IMPORT`.

`UNRESOLVED_IMPORT -> CONSERVE_UNKNOWN`.

### 4.3 Same-blob alias

Records sharing the same Git object SHA at the same frontier receive symmetric `SAME_BLOB_ALIAS` edges. They retain distinct POIDs and distinct PVTX IDs.

`SAME_BLOB_ALIAS != SAME_OBJECT`.

The extractor uses a deterministic star over a sorted PVTX group rather than materializing every pair. This preserves connectivity while bounding edge growth.

### 4.4 Exact path reference

`EXACT_PATH_REFERENCE` is intentionally narrow. V3 currently extracts scalar strings from parseable Python, JSON and TOML carriers and emits an edge only when the normalized scalar equals one exact repository-relative path in the same frontier.

No substring, embedding, filename similarity or narrative inference is used.

`REFERENCE != RUNTIME_DEPENDENCY`.

### 4.5 Optional KC144 coordinate overlay

`KC144_GRID_ADJACENT` is optional and disabled by default. When enabled, it connects exact PVTX manifestations whose PROJECT_KC144 stations are cardinal neighbors on the non-wrapped 12x12 chart **inside the same exact frontier**.

These edges have authority `COORDINATE_ONLY` and loss witness:

`GEOMETRIC_ADJACENCY_HAS_NO_DEPENDENCY_OR_SEMANTIC_EQUIVALENCE CLAIM`.

This permits the same graph engine to traverse an explicit geometric overlay without contaminating the default structural graph.

## 5. Determinism and replay

The graph compiler sorts vertices by PVTX and canonicalizes edges by content-derived edge ID. Duplicate emitted edges collapse only by exact edge identity.

Required invariants:

1. reversing input record order leaves graph ID unchanged;
2. changing the witnessed edge set changes graph ID;
3. same blob does not collapse path objects;
4. same POID in two planes/heads produces two PVTX manifestations;
5. bare POID lookup with multiple PVTX manifestations fails closed;
6. every edge PVTX endpoint is resolvable in the exact vertex set;
7. every edge snapshot equals the graph snapshot;
8. extraction failure is recorded as HOLD/unknown, not converted to absence-as-proof.

## 6. Navigation algorithms

V3 currently supplies internal bounded query primitives; it does **not** silently add a new canonical MCP ABI.

### 6.1 Locator resolution

Preferred locator: exact `PVTX.*`.

Convenience locator: `POID.*` only when exactly one matching PVTX exists in the current graph snapshot.

Possible outcomes:

```text
PVTX exact                    -> RESOLVED
POID with one PVTX            -> RESOLVED
POID with >1 PVTX             -> HOLD_AMBIGUOUS_VERTEX
unknown PVTX/POID             -> HOLD_UNKNOWN_VERTEX
```

### 6.2 Neighbors

`neighbors(locator, direction, kinds, offset, limit, expected_snapshot_id, expected_graph_id)`

- directions: `out`, `in`, `both`;
- edge kinds are explicit;
- `limit <= 100`;
- stale snapshot/graph CAS fails closed;
- ambiguous/unknown locator fails closed.

### 6.3 BFS

BFS provides deterministic minimum-edge traversal over an explicit edge-kind set.

Default kinds are structural only. Geometric edges are excluded unless explicitly selected.

### 6.4 Dijkstra

Dijkstra exists only with caller-supplied non-negative finite weights for **every selected edge kind**. There is no hidden project-value scalarization.

Returned receipt contains the exact weights and scalar cost.

`PATH_COST_WEIGHTS_ARE_EXPLICIT_INPUT_NOT_HIDDEN_TRUTH`.

### 6.5 Cost vector

Every successful route also returns a non-scalar diagnostic vector:

```text
C(route) = <
  structural_hops,
  authority_friction,
  uncertainty,
  plane_crossings,
  coordinate_hops
>
```

This vector is descriptive. It is not a truth score.

## 7. Hold lattice

V3 query/build operations preserve explicit non-success states, including:

- `HOLD_EDGE`
- `HOLD_STALE_SNAPSHOT`
- `HOLD_STALE_GRAPH`
- `HOLD_UNKNOWN_VERTEX`
- `HOLD_AMBIGUOUS_VERTEX`
- `HOLD_EXPANSION_LIMIT`
- `HOLD_DEPTH_LIMIT`
- `HOLD_NO_PATH`

Unknown is never silently coerced to zero edges or zero cost.

## 8. Navigation layers

The Project Atlas stack now separates five objects that are easy to conflate:

```text
STABLE PROJECT PATH IDENTITY (POID)
        |
        v
EXACT FEDERATED MANIFESTATION (PVTX = plane+repo+head+POID)
        |
        +--> PROJECT_KC144 / KC144_REFERENCE projections
        |            |
        |            +--> V2 GEOMETRIC ROUTE (station path)
        |
        +--> V3 RELATION GRAPH (typed witnessed PVTX edges)
                         |
                         v
                  NATIVE RETURN
```

A future semantic/claim graph can be layered above V3, but only with its own evidence and authority classes. V3 does not infer `supports`, `contradicts`, `causes`, or `is equivalent to` from source-code adjacency.

## 9. Qualification membrane

The repository's CI workflows trigger only for PRs targeting `master`. V3 therefore uses two PRs with different semantics:

- `#335`: integration ancestry into the V2 branch;
- `#336`: qualification-only PR to `master` so existing CI/release workflows execute.

`QUALIFICATION_PR != INTEGRATION_PR != PROMOTION`.

A green qualification-only PR is an execution witness for the exact candidate head. It does not change the intended ancestry and must not be treated as merge authority.

## 10. Promotion boundary

V3 is a child experiment of an unmerged V2 lineage. Green tests prove only the tested candidate head.

Before any canonical MCP graph RPC promotion, separately require:

1. accepted V1/V2 ancestry;
2. exact rebased V3 head;
3. full current CI and V3.4 release qualification;
4. protocol/package version decision;
5. clean installed-wheel surface witness if RPCs are added;
6. private brain integration/review;
7. separate publication authority;
8. separate deployment authority.

No V3 code path grants itself publication, deployment or promotion authority.
