# H6 EXECUTION CUT-05 — coupled H01→H06 integration

## Parent evidence

- H6 CUT-02 RED: 6/6 intended parent REDs provider-confirmed.
- H6 CUT-03 root facade: exact-head syntax, full unit, critical-invariant, smoke and trusted promotion-qualification jobs completed SUCCESS on `80f47b21a8bc26ece6032f9d4b89e96d9c987e9e`.
- H6 CUT-04 cold boot: two independent child processes reopened durable state and emitted identical query/root digests with no durable mutation; `COLD_BOOT_MATCH`.

## Residual closed by this cut

The qualified root facade exposed H01–H06 decisions but `compile_query` intentionally returned empty H03/H04/H05 arrays. Therefore `H6_CONTRACT_FACADE_QUALIFIED != H6_COUPLED_ROOT`.

CUT-05 adds only two read-only operations to the same facade:

- `navrun_observe` — deterministic H03 observation-only route-run receipt; no persistence or authority.
- `compile_integrated` — calls the inherited H06 root compile, runs requested H04 BridgeDecisions and H05 EvidenceDecisions, creates H03 RouteProposals, and gates each route on its declared required transforms and claims.

## Coupling law

```text
H01 identity
-> H02 projection
-> H03 route proposal
-> H04 required transform admission
<-> H05 required evidence sufficiency
-> H06 integrated admission / typed holds
```

A graph path can be reachable and still be held because its required bridge or claim is not admitted/sufficient.

## Tests

`tests/test_h6_integrated.py` covers:

- positive fully coupled admission;
- deterministic observation-only NAVRUN identity;
- incomplete bridge hold;
- missing required bridge hold;
- duplicate evidence hold;
- missing required evidence hold;
- unreachable route hold despite good bridge/evidence.

The stacked workflow `.github/workflows/h6-integrated.yml` runs both inherited H6 facade tests and the coupled integration suite.

## Firewalls

```text
ROUTE_PASS != BRIDGE_PASS
BRIDGE_PASS != EVIDENCE_PASS
NAVRUN_OBSERVATION != CLAIM_TRUTH
H6_INTEGRATED_ADMISSION != EXECUTION_AUTHORITY
INTEGRATED_MECHANISM_PASS != H6_ROOT_CLOSED
```

## Successor

If provider integration qualification passes, extend the independent-process cold-boot cartridge so the child processes reconstruct and exercise the full H01/H02/H03/H04/H05/H06 coupled circuit. Only that full-circuit cold match plus a closure receipt can justify `H6_ROOT_CLOSED`.
