# A -> B Klein-4 Inversion Spec

## Seed Identity

`A` is a seed-kernel object, not a manuscript-scale body. This spec freezes the lawful 4x4 holographic seed kernel and defines the first-order inverse seed `B` without changing seed grammar.

Required decision-complete sections:
- `Seed Identity`
- `Source Witness`
- `Inversion Operator`
- `A -> B Mapping`
- `Equivalent Representations`
- `Invariants Preserved`
- `Involution Law`
- `Acceptance Tests`

Canonical `A` instance:

```text
1 2 3 4
3 4 1 2
4 3 2 1
2 1 4 3
```

## Source Witness

- Authority mode: `LOCAL_ONLY`
- Canonical basis: `repo 4x4 holographic seed / Klein-4 kernel language`
- Docs gate: `BLOCKED`

Local witnesses:
- `self_actualize/promoted_live_roots/atlasforge_framework/atlasforge/klein4/klein4.py`
- `self_actualize/promoted_live_roots/atlasforge_framework/atlasforge/holographic_seed/holographic_seed.py`
- `self_actualize/promoted_live_roots/atlasforge_framework/atlasforge/latin/latin.py`
- `self_actualize/live_docs_gate_status.md`

## Inversion Operator

- Operator id: `K4-COMPLEMENT`
- Symbol rule: `C(x) = 5 - x`
- Bit rule: `v -> v XOR 11 on Z2 x Z2`
- Group action: `(1,1)`
- Coordinate rule: `Address is preserved: B[r,c] = C(A[r,c]).`

## A -> B Mapping

Law:

```text
B = C(A)
```

Canonical `B` instance:

```text
4 3 2 1
2 1 4 3
1 2 3 4
3 4 1 2
```

Coordinate bijection:
- `R1C1`: `1 (00, Water) -> 4 (11, Fire)`
- `R1C2`: `2 (01, Earth) -> 3 (10, Air)`
- `R1C3`: `3 (10, Air) -> 2 (01, Earth)`
- `R1C4`: `4 (11, Fire) -> 1 (00, Water)`
- `R2C1`: `3 (10, Air) -> 2 (01, Earth)`
- `R2C2`: `4 (11, Fire) -> 1 (00, Water)`
- `R2C3`: `1 (00, Water) -> 4 (11, Fire)`
- `R2C4`: `2 (01, Earth) -> 3 (10, Air)`
- `R3C1`: `4 (11, Fire) -> 1 (00, Water)`
- `R3C2`: `3 (10, Air) -> 2 (01, Earth)`
- `R3C3`: `2 (01, Earth) -> 3 (10, Air)`
- `R3C4`: `1 (00, Water) -> 4 (11, Fire)`
- `R4C1`: `2 (01, Earth) -> 3 (10, Air)`
- `R4C2`: `1 (00, Water) -> 4 (11, Fire)`
- `R4C3`: `4 (11, Fire) -> 1 (00, Water)`
- `R4C4`: `3 (10, Air) -> 2 (01, Earth)`

## Equivalent Representations

- Symbol view: `1 <-> 4`, `2 <-> 3`
- Bit view: `00 <-> 11`, `01 <-> 10`
- Group view: apply Klein-4 complement element `(1,1)`
- Tetradic/elemental view: `Water <-> Fire`, `Earth <-> Air`
- Coordinate view: each address is preserved and complemented in place

## Invariants Preserved

- Seed admissibility: `True`
- Bidiagonal property: `True`
- Local 2x2 coverage count preserved: `True`
- Addressability preserved: `True`
- Coordinate count preserved: `True`

## Involution Law

```text
C(C(A)) = A
```

- Self-inverse operator: `True`
- Holds for canonical instance: `True`

Recovered `A`:

```text
1 2 3 4
3 4 1 2
4 3 2 1
2 1 4 3
```

## Acceptance Tests

- `operator_consistency`: `True`
- `involution`: `True`
- `structural_preservation`: `True`
- `coordinate_bijection`: `True`
- `scope_guard`: `True`

## Scope Guard

This step stays formal and seed-local. It explicitly excludes:
- `category inversion`
- `seed-to-flower duality`
- `continuous-wave duals`
- `corpus-wide routing updates`
