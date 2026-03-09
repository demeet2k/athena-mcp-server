# EDGE SCHEMA

## 1. Definition

An edge (LinkEdge) records a meaning-transfer between two atoms in the mycelium graph.

## 2. LinkEdge Record

```
e = (EdgeID, Kind, Src, Dst, Scope, Corridor, WitnessPtr, ReplayPtr, Payload, EdgeVer)
```

## 3. Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `EdgeID` | string | yes | Unique ID: `E-XXXX` |
| `Kind` | enum | yes | One of the closed basis K |
| `Src` | GlobalAddr | yes | Source atom address |
| `Dst` | GlobalAddr | yes | Destination atom address |
| `Scope` | string | yes | `intra-chapter`, `cross-chapter`, `chapter-appendix`, `source-chapter` |
| `Corridor` | object | yes | Truth class + budget constraints |
| `WitnessPtr` | string | conditional | Path to evidence artifact (required for OK) |
| `ReplayPtr` | string | conditional | Path to deterministic re-check recipe (required for OK) |
| `Payload` | object | no | Structured data per Kind |
| `EdgeVer` | string | yes | Version of this edge record |

## 4. Edge Kind Basis (closed set)

```
K = {REF, EQUIV, MIGRATE, DUAL, GEN, INST, IMPL, PROOF, CONFLICT}
```

| Kind | Meaning | Payload |
|------|---------|---------|
| `REF` | Dependency required to interpret destination | reference path |
| `EQUIV` | Semantic equivalence bridge | fwd/bwd maps + invariants |
| `MIGRATE` | Version evolution | compat matrix + rollback recipe |
| `DUAL` | Adjacent-lens representation swap | adjacency profile |
| `GEN` | Generalization (child→parent) | typed obligations |
| `INST` | Instantiation (parent→child) | typed obligations |
| `IMPL` | Spec → implementation binding | conformance evidence |
| `PROOF` | Claim → proof binding | replay recipe |
| `CONFLICT` | Contradiction packet | minimal witness set + quarantine |

## 5. Navigation Edges

Navigation edges (orbit, rail, arc triad) are REF edges with standardized NavPayload:

```yaml
Payload:
  Nav:
    NavRole: ORBIT_NEXT | RAIL_NEXT | ARC_TRIAD
    Arc: 0..6
    Rot: 0..2
    Lane: Su | Me | Sa
    Ord: integer
```

## 6. Tabular Format

Edges are stored in markdown tables in `85_EDGES/`:

```markdown
| EdgeID | Kind | Src | Dst | Scope | Corridor | Witness |
|--------|------|-----|-----|-------|----------|---------|
| E-0001 | REF | Ch01<0000>.S1.a | Ch09<0020>.C2.b | cross-chapter | AMBIG | — |
```
