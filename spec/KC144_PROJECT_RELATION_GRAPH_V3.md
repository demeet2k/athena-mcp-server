# KC144 Project Relation Graph V3

Status: **candidate child of unmerged Project Atlas MCP Surface V2; not canonical, not published, not deployed**.

Private work order: `demeet2k/Athena#508`.

Exact parent at branch creation:

- repository: `demeet2k/athena-mcp-server`
- V2 PR: `#310`
- parent head: `c7445bcd70a354e5deb912add6716d7e5191e02c`
- V2 parent snapshot namespace: `PATLASV2.*`

## 1. Why V3 exists

V1 made project objects exactly addressable. V2 made those addresses queryable and routable across configured Git, runtime Git and MCP planes. V2 `athena_project_route` is deliberately a **KC144 station route**. It answers how two exact objects are positioned on the project chart; it does not assert that one object imports, contains, references, tests, supports or semantically equals the other.

V3 adds a second geometry: a typed relation graph over exact Project Atlas identities.

```text
GEOMETRIC NAVIGATION: PROJECT_KC144 station -> station
STRUCTURAL NAVIGATION: POID --typed witnessed edge--> POID
NATIVE RETURN:         each endpoint -> exact head-qualified Git/MCP witness
```

The distinction is constitutional:

`COORDINATE_ADJACENCY != STRUCTURAL_EDGE != SEMANTIC_EQUIVALENCE`.

## 2. Graph object

For one exact V2 snapshot `s`:

`G_s = (V_s, E_s)`

where:

- `V_s` is the exact Project Atlas POID set available in the supplied atlas;
- `E_s` is the deterministically extracted typed relation set;
- every edge endpoint must be a member of `V_s`;
- every edge carries the same `PATLASV2.*` snapshot witness;
- graph identity is `PATLASG3.<digest>` over the exact sorted vertex receipts + typed edge receipts + snapshot coordinate.

Graph identity is not a promotion receipt:

`PATLASG3 != RELEASE_RECEIPT != DEPLOYMENT_RECEIPT`.

## 3. Edge contract

A V3 relation is represented as:

```text
E = <
  edge_id,
  kind,
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

`edge_id = PEDGE.<digest>` is derived from the relation as stated, not from list position. Edge enumeration therefore cannot change identity.

### 3.1 Exact Git hierarchy

`DIR_CONTAINS(parent_tree, child_entry)` and inverse `DIR_PARENT_OF(child_entry, parent_tree)` are emitted only when the exact parent tree record exists in the same `<plane,repo,head>` frontier.

Extractor: `git_tree_hierarchy_v1`.

Evidence: exact Git tree paths under one head.

A missing parent tree record yields `HOLD_EDGE`; V3 never invents a synthetic root POID.

### 3.2 Python import relations

Python imports are parsed with the Python AST. Local module candidates are indexed only inside the same exact `<plane,repo,head>` frontier.

- `PY_IMPORTS`
- `PY_RELATIVE_IMPORTS`

A local edge is emitted only after unique module resolution. Relative import resolution respects package level. External or otherwise unresolved imports are retained in `unresolved_imports` with standing `UNRESOLVED_EXTERNAL_OR_LOCAL_UNKNOWN`.

`IMPORT_STRING != RESOLVED_LOCAL_IMPORT`.

`UNRESOLVED_IMPORT -> CONSERVE_UNKNOWN`.

### 3.3 Same-blob alias

Records sharing the same Git object SHA at the same frontier receive symmetric `SAME_BLOB_ALIAS` edges. They retain distinct POIDs and path coordinates.

`SAME_BLOB_ALIAS != SAME_OBJECT`.

The extractor uses a deterministic star over a sorted POID group rather than materializing all pair combinations. This keeps connectivity while bounding edge growth.

### 3.4 Exact path reference

`EXACT_PATH_REFERENCE` is intentionally narrow. V3 currently extracts scalar strings from parseable Python, JSON and TOML carriers and emits an edge only when the normalized scalar equals one exact repository-relative path in the same frontier.

No substring, embedding, filename similarity or narrative inference is used.

`REFERENCE != RUNTIME_DEPENDENCY`.

### 3.5 Optional KC144 coordinate overlay

`KC144_GRID_ADJACENT` is optional and disabled by default. When enabled, it connects exact POIDs whose PROJECT_KC144 stations are cardinal neighbors on the non-wrapped 12x12 chart.

These edges have authority `COORDINATE_ONLY` and loss witness:

`GEOMETRIC_ADJACENCY_HAS_NO_DEPENDENCY_OR_SEMANTIC_EQUIVALENCE CLAIM`.

This permits one graph engine to traverse the geometric overlay when explicitly requested without contaminating the default structural graph.

## 4. Determinism and replay

The graph compiler sorts vertices by POID/plane and canonicalizes edges by content-derived edge ID. Duplicate emitted edges collapse by exact edge identity.

Required invariants:

1. reversing input record order leaves graph ID unchanged;
2. changing the witnessed edge set changes graph ID;
3. same blob does not collapse path objects;
4. every edge endpoint is resolvable in the exact vertex set;
5. every edge snapshot equals the graph snapshot;
6. extraction failure is recorded as HOLD/unknown, not converted to absence-as-proof.

## 5. Navigation algorithms

V3 currently supplies internal bounded query primitives; it does **not** silently add a new canonical MCP ABI.

### 5.1 Neighbors

`neighbors(poid, direction, kinds, offset, limit, expected_snapshot_id, expected_graph_id)`

- directions: `out`, `in`, `both`;
- edge kinds are explicit;
- `limit <= 100`;
- stale snapshot/graph CAS fails closed;
- unknown vertex fails closed.

### 5.2 BFS

BFS provides deterministic minimum-edge traversal over an explicit edge-kind set.

Default kinds are structural only. Geometric edges are excluded unless explicitly selected.

### 5.3 Dijkstra

Dijkstra exists only with caller-supplied non-negative finite weights for **every selected edge kind**. There is no hidden project-value scalarization.

Returned receipt contains the exact weights and scalar cost.

`PATH_COST_WEIGHTS_ARE_EXPLICIT_INPUT_NOT_HIDDEN_TRUTH`.

### 5.4 Cost vector

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

## 6. Hold lattice

V3 query/build operations preserve explicit non-success states, including:

- `HOLD_EDGE`
- `HOLD_STALE_SNAPSHOT`
- `HOLD_STALE_GRAPH`
- `HOLD_UNKNOWN_VERTEX`
- `HOLD_EXPANSION_LIMIT`
- `HOLD_DEPTH_LIMIT`
- `HOLD_NO_PATH`

Unknown is never silently coerced to zero edges or zero cost.

## 7. Navigation layers

The full Project Atlas stack now separates four objects that were easy to conflate:

```text
NATIVE GIT/MCP IDENTITY
        |
        v
PROJECT_KC144 / KC144_REFERENCE projections
        |
        +--> V2 GEOMETRIC ROUTE (station path)
        |
        +--> V3 RELATION GRAPH (typed witnessed POID edges)
                         |
                         v
                  NATIVE RETURN
```

A future semantic/claim graph can be layered above V3, but only with its own evidence and authority classes. V3 does not infer `supports`, `contradicts`, `causes`, or `is equivalent to` from source-code adjacency.

## 8. Promotion boundary

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
