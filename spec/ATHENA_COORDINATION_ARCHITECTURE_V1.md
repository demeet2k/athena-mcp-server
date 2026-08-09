# ATHENA COORDINATION ARCHITECTURE V1

Coordinate: `COORDINATION=<MB,CM,DG,EG,BT,P1,P2,P3.2,OI,AD>`.

Effective runtime coordinate: `ATHENA.RUNTIME.UNIFIED.10` over scientific carrier `ATHENA.RUNTIME.UNIFIED.9`.

Effective mature-organ inventory: `ATHENA.ORGAN.INVENTORY.1.1` over base registry `ATHENA.ORGAN.INVENTORY.1`.

## 1. Separate authority planes

`Y1 = semantic/canonical claim authority`.

`MB = Message Board work-presence / coordination-claim / message authority`.

`Y1 != MB`.

Message Board ownership of coordination claims does not replace Y1 `? → + → ! → #`. Y1 semantic authority does not authorize work presence or board messages by itself.

## 2. Message Board V1

Message Board is the sole shared authority for presence claims and coordination messages in this plane.

`BOARD_STATE != EXECUTION_AUTHORITY != WORLD_TRUTH`.

A presence claim coordinates work ownership; it does not prove that the claimed task is correct, complete, useful, or true.

## 3. Cohesion Mesh V1

Cohesion matchmaking/request-offer/coalition/SOLO-vs-PARTY comparison is advisory.

`COHESION != CLAIM_AUTHORITY`

`COHESION != ASSIGNMENT_AUTHORITY`

`COHESION != EXECUTION_AUTHORITY`.

A ranked match is an option, not an assignment.

## 4. Duplicate guard

The duplicate membrane projects current Message Board occupancy into treatment options without mutating board state.

`FUZZY_SIMILARITY != DUPLICATE_PROOF`.

`PARTITION_ASSERTION != PARTITION_PROOF`.

`REPLICA != INDEPENDENT_EVIDENCE`.

`JOIN_OPTION != JOIN_EXECUTED`.

## 5. Evidence coverage guard

SOLO-vs-PARTY comparison fails closed when matched mission coverage is incomplete or evidence references are reused.

`PARTIAL_MATCHED_SUBSET_OR_REUSED_EVIDENCE != SUFFICIENT_COMPARATIVE_EVIDENCE`.

`CAUSAL_EFFECT = UNKNOWN`.

`PROMOTION_AUTHORITY = FALSE`.

The guard may withhold comparative treatment interpretation; it cannot create a causal claim by itself.

## 6. Bootstrap treatment

Bootstrap Cohesion treatment is a read-only steering projection.

`BOOT_HOLD != TREATMENT_EXECUTION`.

`TREATMENT_PROJECTION != CLAIM_MUTATION != ASSIGNMENT`.

It cannot clear Message Board holds or execute treatment decisions.

## 7. Party coordination V1

Party coordination is a Git-shared multi-goal coordination layer over Message Board V1.

Formation/join/state/list/observe requires explicit board/current-work semantics. Party observations may produce bounded coordination reward candidates but never mutate global XP authority.

`PARTY_OBSERVATION != RESULT_TRUTH`.

## 8. Party Channel V2

Party-scoped messages are routed through Message Board V1.

`PARTY_CHANNEL_TRANSPORT = MESSAGE_BOARD_V1`.

`MESSAGE_POST != XP_AWARD`.

`ACK != RESULT_TRUTH`.

## 9. Party Reward Provenance V3 → V3.2

### V3 — attributable result provenance

Party results carry attributable `RESULT` / `VERIFY` provenance events through Message Board.

The sender must still hold the frozen/current work claim and recipients must remain current party members. Source-XP provenance is uniqueness-bounded and root-work diversity is preserved.

`PARTY_RESULT != RESULT_TRUTH`.

`PARTY_RESULT != GLOBAL_XP_AUTHORITY`.

`SOURCE_XP_REUSE != NEW_REWARD`.

### V3.1 — envelope coherence membrane

Only exact V3 result packets are accepted. Inner `RESULT` / `VERIFY` role must agree with the enclosing Message Board role before inherited reward processing.

`V3_PACKET_VERSION_REQUIRED`.

`INNER_RESULT_VERIFY_MUST_MATCH_OUTER_MESSAGE_BOARD_ROLE`.

Envelope coherence validates attribution shape; it does not establish result truth.

### V3.2 — finite XP membrane

Before any inherited Message Board read/mutation, source-XP scan, or receipt construction, imported `base_xp` must coerce to a finite, non-boolean, non-negative real. Finite numeric-string compatibility remains allowed.

`BASE_XP_MUST_BE_FINITE_NON_BOOLEAN_BEFORE_PARTY_REWARD_PROCESSING`.

`FINITE_NUMERIC_VALIDATION != UPSTREAM_XP_VERIFICATION_OR_MINT_AUTHORITY`.

V3.2 changes no reward formula and grants no new authority.

## 10. ORGAN_INVENTORY.1 / 1.1

Mature coordination organs are declared explicitly. File/module/tool existence is insufficient.

Each descriptor carries:

`<id,version,integration_class,authority_plane,tools,resources,manifest_layer,omega_key,critical_tests,source/spec refs,laws>`.

The stable base registry remains `ATHENA.ORGAN.INVENTORY.1`; the effective coordination view is `ATHENA.ORGAN.INVENTORY.1.1`, which replaces the historical active Party V3 descriptor with Party V3.2 while preserving V3/V3.1 source and witness lineage.

## 11. ARCHITECTURE_DRIFT.1

For declared mature organs:

`Drift = DeclaredMature - (ObservedRuntime ∩ SURFACE ∩ EffectiveManifest ∩ OMEGA ∩ CriticalWitnesses)`.

Runtime promotion readiness requires the live Runtime/SURFACE/EffectiveManifest/OMEGA intersection. Repository CI adds critical-test and source/spec witnesses.

Unclassified live surfaces remain `OBSERVE_EXPANSION_FRONTIER`; they are neither hidden nor auto-canonicalized.

## 12. Recursive successor

The first effective inventory cohort covers Message Board/Cohesion/Party through V3.2 only.

`Freshness Train` is the first named internal/bootstrap expansion candidate. It is intentionally **not** mature yet because its authority, mutation, freshness-read and observation semantics have not been admitted into this constitution.

Subsequent cohorts should be admitted one family at a time after authority/mutation semantics are reconstructed—for example Frontier/Rehydration/Campaign, QHUG Pareto, Mythic, Bionanomachine, operational-basis and other extension families.

No cohort gains maturity solely because it is old, large, popular, already imported, already callable, or already tested somewhere in the broad unit pool.
