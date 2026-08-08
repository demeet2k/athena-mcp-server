# BIONANOMACHINE MECHANISM KERNEL V1

Version: `BNMK.1`

Resource: `athena://bio/nanomachines/v1`

Knowledge source: `demeet2k/Athena` artifact `ATHENA.BIONANOMACHINE.MECHANISM.KERNEL.V1`.

## Scope

BNMK is a bounded mechanism/analogy library. It does not make new biological truth claims and has no canonical semantic-mutation authority.

Constitutional laws:

```text
BIOLOGICAL_MECHANISM != SOFTWARE_IMPLEMENTATION
MECHANISTIC_ANALOGY != CAUSAL_EQUIVALENCE
USER_SEED != VERIFIED_EMPIRICAL_CONSTANT
STRUCTURAL_SIMILARITY != SHARED_EVOLUTIONARY_ORIGIN
SIMULATION != OBSERVATION
TRANSFER_OPERATOR != BIOLOGICAL_CLAIM
INTERFACE_MATCH_PROXY != PHYSICAL_IMPEDANCE
AVAILABLE_TEST != APPLICABLE_TEST
PARTS_LIST != ASSEMBLED_CAPABILITY
ROUTE_EXISTS != INTERFACE_MATCHED
```

## KC144 carrier

Rows are 12 mechanism archetypes and columns are 12 machine facets:

```text
R01 rotary gradient transducer
R02 rotary propulsion motor
R03 processive track walker
R04 contractile sliding actuator
R05 template translation assembler
R06 template copy + proofreader
R07 frontier unwinding translocase
R08 topological stress editor
R09 tagged selective degrader
R10 isolated refolding chamber
R11 gated boundary secretion conduit
R12 contractile puncture injector

C01 identity_role
C02 energy_drive
C03 input_cargo
C04 output_work
C05 substrate_track
C06 geometry_topology
C07 state_cycle
C08 coupling_gating
C09 fidelity_error_control
C10 assembly_maintenance
C11 failure_recovery
C12 interface_transfer
```

Coordinate law:

```text
gid = 12*(row-1)+column
```

The generated atlas contains exactly 144 unique cells.

## Seed registry

The runtime preserves 14 user-seeded machines:

```text
ATP_SYNTHASE
BACTERIAL_FLAGELLAR_MOTOR
KINESIN
DYNEIN
MYOSIN
RIBOSOME
DNA_POLYMERASE
HELICASE
TOPOISOMERASE
PROTEASOME
GROEL_GROES_CHAPERONIN
TYPE_III_SECRETION_SYSTEM
TYPE_VI_SECRETION_SYSTEM
BACTERIOPHAGE_TAIL_ASSEMBLY
```

The catalog deliberately does not encode the user-provided RPM or bases-per-second values as verified constants.

## Tools

### `athena_bionano_catalog`

Returns the 12 rows, 12 columns, 14 seeds, KC144 law and epistemic firewalls. `include_atlas=true` returns all 144 cells.

### `athena_bionano_compile`

Compiles a known seed to:

```text
L4=<structure,drive,work,integrity>
K12=<identity,energy,input,output,substrate,geometry,cycle,gating,fidelity,assembly,failure,interface>
KC144=row x 12 cells
```

Unknown machine IDs return `HOLD_UNKNOWN_MACHINE`.

### `athena_bionano_transfer`

Returns a computational analogy candidate with portable operators, nonportable biological context and transfer loss. Authority remains `COMPUTATIONAL_ANALOGY_ONLY`.

### `athena_bionano_interface_match`

Compares normalized 6D interface profiles:

```text
phi=<rate,latency,error_tolerance,statefulness,reversibility,coupling>
d=||phi_p-phi_c||_2/sqrt(6)
match=1-clip(d,0,1)
```

This is a compatibility proxy only, inspired by the interface-matching lesson of the supplied Smith chart.

### `athena_bionano_convergence_gate`

Bounded witness library:

```text
nth term nonzero -> divergence witness
ratio/root <1    -> absolute-convergence witness under test assumptions
ratio/root =1    -> HOLD
contraction q<1  -> contraction witness under declared metric/domain
spectral radius<1 -> scoped discrete linear-stability witness
boundary/inapplicable/absent -> HOLD
```

No test is silently generalized beyond its assumptions.

### `athena_bionano_assembly`

For the T4-like phage visual seed, returns the 15 supplied exploded-drawing labels and sequence:

```text
attachment -> penetration/sheath contraction -> payload injection -> spent/empty external particle
```

Authority is `USER_VISUAL_ASSEMBLY_PACKET`, not independent biological verification.

For other machines it returns generic functional modules only and explicitly states that these are not native molecular subunit inventories.

## Runtime composition

BNMK is wired through `AorDevelopmentSurface`, making the six tools part of `AOR_DEVELOPMENT_TOOLS`. The existing server already unions that set into the MCP tool surface and dispatches it before the core tool chain.

BNMK therefore reuses the current authority, rate-limit, server, and transport architecture rather than adding a second control plane.

## Tests

`tests/test_bionanomachine_kernel.py` checks:

- 12 rows / 12 columns / 144 unique GIDs;
- all 14 seed machines;
- 4D + 12D compilation;
- HOLD on unknown IDs;
- analogy authority boundary;
- bounded interface matching;
- convergence/stability witness boundaries;
- 15-part phage visual BOM and four-stage sequence;
- AOR surface tool/resource registration.

## Promotion boundary

```text
CODE_EXISTS != TESTED
TESTED != CURRENT
CURRENT != CANONICAL
CANONICAL != TRUSTED_BIOLOGICAL_TRUTH
```

Merge only after exact-head CI passes. Updating the separate Athena canonical runtime pin is a subsequent witnessed mutation.
