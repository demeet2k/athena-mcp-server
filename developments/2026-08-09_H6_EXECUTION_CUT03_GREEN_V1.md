# H6 EXECUTION CUT-03 — minimal GREEN constitutional facade

## Coordinates

- exact runtime parent: `429a480a80eeefb9e2bff1ea3015adf571d76b0e`
- semantic brain: `demeet2k/Athena@f32eb817d48de73a0c591b0f7fb3561e4f08e7da`
- RED predecessor: PR #308 / `ATHENA.H6.EXECUTION.CUT02.RED.RECEIPT.V1`
- RED provider observation: 6/6 intended REDs confirmed

## Treatment shape

One production module: `athena_mcp/h6_root.py`.

It is a read-only facade over current `AthenaCore` + `CrystalRuntime` primitives and adds no new SQLite table, scheduler, execution engine, public MCP registration or promotion path.

### H01
`identity_decide` normalizes exact navigation, candidate OIDs and explicit `ALIAS_OF` edges into a typed identity decision while preserving ambiguity and making no mutation.

### H02
`projection_decide` reads the existing coordinate registry and classifies current hash/index KC144 seating as `PROJECTION_ONLY`; it never upgrades `stable_gid` into constitutional semantic authority.

### H03
`route_propose` normalizes existing graph routing into a shared RouteProposal ABI with source VID, steps, gate state, cost/gain vectors and proposal-only authority.

### H04
`bridge_decide` separates transform storage from bridge admission. Admission requires preserved/lost invariants, validity corridor, evidence references, counterexamples and reverse/compensation/irreversibility. ISOMORPHISM additionally requires a real reverse transform with reciprocal direction.

### H05
`evidence_decide` normalizes evidence identity/lineage groups, independence floor, freshness and counterevidence into a read-only evidence standing. It has no promotion authority.

### H06
`compile_query` binds request/goal, identity targets, semantic VIDs, Git head, topology version, prompt digest, evidence floor, authority envelope, completion/stop predicates and return target into one deterministic QueryBundle/H6 root receipt. It checks current semantic VIDs and surfaces identity/projection/version holds; execution authority remains false.

## Tests

- `tests/test_h6_root.py` promotes the exact six CUT-02 RED contracts into normal GREEN regression tests.
- `tests/test_h6_root_adversarial.py` adds ambiguity, unknown object, unreachable route, complete/fake reverse bridge, independent/stale/conflicted evidence, unresolved identity and stale semantic VID cases.

## Evidence ceiling

A focused/full-CI pass can establish only this bounded facade's mechanism behavior on the exact candidate head.

```text
H6_GREEN_TEST != H6_ROOT_CLOSED
EXACT_HEAD_CI != COLD_BOOT
H6_ADMISSION != EXECUTION_AUTHORITY
H05_EVIDENCE_SUFFICIENCY != PROMOTION_AUTHORITY
MECHANISM_PASS != BEHAVIORAL_GAIN
```

## Successor

After exact-head CI and current-master comparison, build the integrated cold-boot cartridge. `H6_ROOT_CLOSED` is withheld until a fresh process reconstructs and recompiles H01→H06 from durable state and the H6 root closure receipt matches.
