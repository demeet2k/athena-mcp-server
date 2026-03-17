# AppD — Registry, Profiles, Version IDs

**[⊙Z*↔Z* | ○Arc 2 | ○Rot SFCR | △Lane Me | ⧈View 4D/AppD | ω=AppD]**

**Routing role:** Profile registry, version IDs, manuscript signatures, migration anchors.
**v2V binding:** This appendix now serves as the **schema registry** for the organism's first canonical object: `CANON::LANG.COMPILER::AST.PIPELINE` (= IntentionScript compiler = IMP::JS::AST.COMPILER).

---

## Compressed crystal tile

### Lens S (Square — Discrete Schema Objects)

#### Facet 1 — Objects
- `AppD.S1.a`: **TokenStream** — The raw input: a sequence of siteswap tokens (integers, brackets, sync markers, multiplex markers). The discrete representation of a pattern before any structure is imposed.
- `AppD.S1.b`: **MacroLib** — The macro expansion library: named pattern aliases, shorthand notation, composition operators. Allows patterns to reference other patterns by name.
- `AppD.S1.c`: **Env** — The compilation environment: hand count, object count, timing constraints, body geometry. What the compiler needs to know about the physical world.
- `AppD.S1.d`: **Policy** — The validation policy: which constraints are hard (collision-free) vs soft (aesthetic), truth class requirements, receipt obligations. What counts as "correct."

#### Facet 2 — Laws
- `AppD.S2.a`: **Average Law** — For any valid siteswap of length L with throws t₁...t_L: (t₁+...+t_L)/L = number of objects. The fundamental conservation theorem. No exceptions.
- `AppD.S2.b`: **Collision-Free Law** — No two objects may land in the same hand at the same time. Formally: the landing schedule σ(i) = (i + t_i) mod L must be a permutation. This is the parsing correctness criterion.
- `AppD.S2.c`: **Closure Law** — A pattern is valid iff its orbit closes: after K petals (or L beats), the state vector returns to its initial value. K = m±n for poi; L = pattern length for siteswap.
- `AppD.S2.d`: **Transport Law** — "Typed meaning must survive transport." Any valid compiler transform must preserve the Average, Collision-Free, and Closure laws, OR explicitly name the loss in a receipt.

#### Facet 3 — Constructions
- `AppD.S3.a`: **Parse** — TokenStream → AST. Tokenize beats, throws, hands, sync markers. Validate token grammar. Output: raw Abstract Syntax Tree with source positions.
- `AppD.S3.b`: **AST** — The parsed tree structure. Nodes: Pattern, Beat, Throw, Sync, Multiplex, Hand, Repeat. Edges: containment and sequence. This IS the compiled pattern's skeleton.
- `AppD.S3.c`: **Desugar** — AST → CoreAST. Expand macros, resolve pattern references, normalize sync notation, flatten multiplex. Remove all syntactic sugar to reveal the pure scheduling contract.
- `AppD.S3.d`: **TypeCheck** — CoreAST → TypedAST. Verify Average Law. Verify Collision-Free Law. Verify Closure Law. Annotate each node with its type: throw-height, landing-time, hand-assignment, object-identity.

#### Facet 4 — Certificates
- `AppD.S4.a`: **Cert::ParseCorrectness** — Proves the AST was derived from a valid token stream by a deterministic grammar. Receipt: (source_hash, grammar_version, parse_tree_hash).
- `AppD.S4.b`: **Cert::AverageSatisfied** — Proves the average theorem holds. Receipt: (throw_sum, pattern_length, object_count, equality_witness).
- `AppD.S4.c`: **Cert::CollisionFree** — Proves no two objects collide. Receipt: (landing_permutation, permutation_is_bijection_witness).
- `AppD.S4.d`: **Cert::ClosureSatisfied** — Proves the pattern closes. Receipt: (state_vector_initial, state_vector_final, equality_witness, orbit_length).

---

### Lens F (Flower — Spectral/Dynamic Schema Objects)

#### Facet 1 — Objects
- `AppD.F1.a`: **SimRuntime** — The simulation executor. Takes a TypedAST and runs it forward in time, producing a full execution trace: which object is where, in which hand, at each beat.
- `AppD.F1.b`: **ExecutionTrace** — The output of simulation: a time-indexed sequence of states. Each state = (beat_number, hand_contents[], object_positions[], active_throws[]).
- `AppD.F1.c`: **TSArtifact** — The TypeScript code artifact. The compiled pattern emitted as executable TypeScript that can drive a visual simulator, a physical robot, or a training guide.
- `AppD.F1.d`: **ReplayHarness** — The deterministic replay engine. Given an ExecutionTrace, can re-execute every step and verify the output matches. Ensures no silent drift between compilation and replay.

#### Facet 2 — Laws
- `AppD.F2.a`: **Determinism Law** — Given identical (TokenStream, MacroLib, Env, Policy), the compiler MUST produce identical outputs. No randomness, no ambient state, no side channels.
- `AppD.F2.b`: **Idempotence Law** — Compiling an already-compiled pattern produces the same result. Parse(Parse(x)) = Parse(x). Desugar(Desugar(x)) = Desugar(x). The pipeline is a projection.
- `AppD.F2.c`: **Replay Law** — "Replay Required for OK." No compilation result achieves truth-class OK without a successful replay verification. The ReplayHarness must confirm the trace.
- `AppD.F2.d`: **Petal Law** — K = m−n (inspin) or K = m+n (antispin). The flower closure invariant. For poi patterns, this replaces the Average Law with a geometric equivalent.

#### Facet 3 — Constructions
- `AppD.F3.a`: **SimRuntime::Execute** — TypedAST → ExecutionTrace. Step-by-step simulation: at each beat, determine which throws are active, which objects are in transit, which hands receive. Record the full state at each tick.
- `AppD.F3.b`: **TSGen** — TypedAST + ExecutionTrace → TSArtifact. Generate TypeScript code that reproduces the pattern. Includes: state machine, timing loop, event callbacks, visual hooks.
- `AppD.F3.c`: **ReplayHarness::Build** — ExecutionTrace → ReplayHarness. Construct the deterministic replayer from the trace. Each step of the replay is verified against the recorded trace.
- `AppD.F3.d`: **ReplayHarness::Verify** — ReplayHarness × ExecutionTrace → {OK, DRIFT(location, expected, actual)}. Run the replay and compare every state. If any state diverges, report the exact location and divergence.

#### Facet 4 — Certificates
- `AppD.F4.a`: **Cert::ExecuteDeterminism** — Proves the execution trace is deterministic: same inputs → same trace. Receipt: (input_hash, trace_hash, determinism_proof).
- `AppD.F4.b`: **Cert::ReplayMatch** — Proves the replay matches the original execution. Receipt: (trace_hash, replay_hash, match_witness).
- `AppD.F4.c`: **Cert::TSArtifactFidelity** — Proves the generated TypeScript faithfully represents the compiled pattern. Receipt: (ast_hash, ts_hash, behavioral_equivalence_proof).
- `AppD.F4.d`: **Cert::ReceiptDeterminism** — Proves the receipt itself is deterministic: same compilation → same receipt. Receipt: (cert_chain_hash, receipt_hash, meta_determinism_proof). The receipt receipts itself.

---

### Lens C (Cloud — Probabilistic/Dwell Schema Objects)

#### Facet 1 — Objects
- `AppD.C1.a`: **DwellMap** — For each clock position (or beat), the fraction of time the pattern spends there. The probability distribution over the timing grid. For poi: where the head lingers.
- `AppD.C1.b`: **HubAccessMap** — For each tunneling hub, the set of K-values that pass through it. Determines which transitions are available at which clock positions. The tunneling bandwidth map.
- `AppD.C1.c`: **TransitionProbability** — At each hub, the probability of each legal transition (based on difficulty, muscle memory, aesthetic preference). The Markov chain over the tunneling network.
- `AppD.C1.d`: **ErrorBudget** — The acceptable deviation from perfect execution: timing tolerance, angle tolerance, collision margin. How much "slop" the compiled pattern allows before truth-class degrades.

#### Facet 2 — Laws
- `AppD.C2.a`: **Dwell Conservation** — The total dwell over all positions sums to 1. ΣP(x) = 1. The pattern is fully accounted for — no probability leaks.
- `AppD.C2.b`: **Hub Bandwidth Law** — A transition between patterns is legal iff they share at least one hub. No hub = no tunnel = no transition. The topology of the tunneling network is absolute.
- `AppD.C2.c`: **Error Monotonicity** — Accumulated errors across compilation passes are monotonically non-increasing. Each pass either reduces error or preserves it. No pass may introduce new errors.
- `AppD.C2.d`: **Drift Detection Law** — Any silent drift (output changes without input change or explicit receipt) is a FAIL. The organism's immune system treats silent drift as infection.

#### Facet 3 — Constructions
- `AppD.C3.a`: **DwellMap::Compute** — ExecutionTrace → DwellMap. Count the fraction of beats spent at each position. For poi: integrate the angular velocity over each clock sector.
- `AppD.C3.b`: **HubAccessMap::Build** — PatternFamily → HubAccessMap. For a set of patterns, compute which hubs are shared between which pairs. The input to the tunneling router.
- `AppD.C3.c`: **TransitionProbability::Estimate** — PerformanceHistory → TransitionProbability. From the performer's history of tunnel transitions, estimate the probability of each transition. Bayesian update.
- `AppD.C3.d`: **ErrorBudget::Allocate** — Policy × Env → ErrorBudget. Given the truth-class requirement and the physical constraints, allocate the error budget across compilation passes.

#### Facet 4 — Certificates
- `AppD.C4.a`: **Cert::DwellNormalized** — Proves the dwell map sums to 1. Receipt: (dwell_vector, sum_witness).
- `AppD.C4.b`: **Cert::HubLegality** — Proves every transition in a sequence passes through a shared hub. Receipt: (transition_sequence, shared_hub_witnesses[]).
- `AppD.C4.c`: **Cert::ErrorWithinBudget** — Proves the accumulated error is within the allocated budget. Receipt: (error_per_pass[], budget, comparison_witness).
- `AppD.C4.d`: **Cert::NoDrift** — Proves no silent drift occurred. Receipt: (input_hash, output_hash, all_intermediate_hashes[], drift_check_witness). The anti-corruption certificate.

---

### Lens R (Fractal — Self-Similar/Scale Schema Objects)

#### Facet 1 — Objects
- `AppD.R1.a`: **ScaleHierarchy** — The nesting structure: how a K-petal pattern contains sub-patterns at different ratios. The fractal tree of the compilation pipeline itself (Parse contains Tokenize contains CharRead...).
- `AppD.R1.b`: **VersionChain** — The history of schema versions: v2U → v2V → v2W → ... Each version is a complete snapshot of the AppD binding. The version chain IS the fractal self-similarity of the schema across time.
- `AppD.R1.c`: **MigrationAnchor** — The fixed point that survives version changes. The invariant core that every version must preserve. For CANON::LANG.COMPILER::AST.PIPELINE: the Average Law, Collision-Free Law, Closure Law, and Transport Law.
- `AppD.R1.d`: **GrammarEvolution** — The meta-grammar: how the siteswap/poi grammar can evolve (new notation, new operators, new constraints) while preserving the migration anchor. The no-silent-schema-drift proof depends on this.

#### Facet 2 — Laws
- `AppD.R2.a`: **Scale Invariance** — The compilation pipeline works identically at every scale: single throw, single beat, single pattern, single session, single performance career. Same laws, different scope.
- `AppD.R2.b`: **Version Compatibility** — Every schema version v(n+1) must be backward-compatible with v(n): any receipt valid under v(n) remains valid under v(n+1). The organism never invalidates its own history.
- `AppD.R2.c`: **Anchor Immutability** — The migration anchor (the four fundamental laws) is IMMUTABLE across all versions. Changing them creates a new schema family, not a new version.
- `AppD.R2.d`: **No-Silent-Schema-Drift** — If the imported grammar evolves (new siteswap notation, new poi operators), the compiler must either (a) be forward-compatible by construction, or (b) emit a migration receipt explicitly naming the incompatibility.

#### Facet 3 — Constructions
- `AppD.R3.a`: **ScaleHierarchy::Build** — CompilerPipeline → ScaleHierarchy. Decompose the pipeline into its fractal levels: character → token → AST node → pattern → sequence → session.
- `AppD.R3.b`: **VersionChain::Extend** — CurrentSchema × Diff → NewSchema + MigrationReceipt. Apply a schema change and produce both the new version and the receipt documenting what changed.
- `AppD.R3.c`: **MigrationAnchor::Verify** — NewSchema → {OK, ANCHOR_VIOLATION(law, details)}. Check that the new version preserves all four fundamental laws.
- `AppD.R3.d`: **GrammarEvolution::Check** — NewGrammar × OldGrammar → {Compatible, Incompatible(changes)}. Determine whether the grammar change is backward-compatible.

#### Facet 4 — Certificates
- `AppD.R4.a`: **Cert::ScaleConsistency** — Proves the compilation is scale-invariant: same laws at every level. Receipt: (level_proofs[], consistency_witness).
- `AppD.R4.b`: **Cert::VersionBackcompat** — Proves the new version is backward-compatible. Receipt: (old_version_hash, new_version_hash, compatibility_proof).
- `AppD.R4.c`: **Cert::AnchorPreserved** — Proves the migration anchor is intact. Receipt: (anchor_laws[], preservation_proofs[]).
- `AppD.R4.d`: **Cert::NoSchemaDrift** — Proves no silent schema drift occurred during grammar evolution. Receipt: (old_grammar_hash, new_grammar_hash, compatibility_or_migration_receipt). The organism's highest-level anti-corruption seal.

---

## v2V Binding Status

```
CANON::LANG.COMPILER::AST.PIPELINE binding to AppD:

  Lens S (Schema Objects):      ✅ BOUND — all 16 cells filled
  Lens F (Dynamic Objects):     ✅ BOUND — all 16 cells filled
  Lens C (Probabilistic Objects): ✅ BOUND — all 16 cells filled
  Lens R (Fractal Objects):     ✅ BOUND — all 16 cells filled

  Total cells filled: 64/64
  Total Objects:      16  (S1,F1,C1,R1 × 4)
  Total Laws:         16  (S2,F2,C2,R2 × 4)
  Total Constructions: 16 (S3,F3,C3,R3 × 4)
  Total Certificates: 16  (S4,F4,C4,R4 × 4)

  Blocker status:
  ✅ AppD schema binding — COMPLETE (this document)
  ⬜ Verifier registry closure — PENDING (needs runtime verification of Cert chain)
  ⬜ Pack replay closure — PENDING (needs ReplayHarness::Verify over full pipeline)
  ⬜ No-silent-schema-drift proof — PENDING (needs GrammarEvolution::Check)
```

## Canonical Object Summary

```
CANON::LANG.COMPILER::AST.PIPELINE = {
  source_node:   IMP::JS::AST.COMPILER (= IntentionScript compiler)
  inputs:        [TokenStream, MacroLib, Env, Policy]
  passes:        [Parse, AST, Desugar, TypeCheck, SimRuntime, TSGen]
  outputs:       [AST, TypedSchedule, SimulationTrace, TSArtifacts]
  receipts:      [WitnessPtr, ReplayPtr, IOReceipt, RuntimeContract]
  certificates:  [ParseCorrectness, AverageSatisfied, CollisionFree,
                  ClosureSatisfied, ExecuteDeterminism, ReplayMatch,
                  TSArtifactFidelity, ReceiptDeterminism, DwellNormalized,
                  HubLegality, ErrorWithinBudget, NoDrift,
                  ScaleConsistency, VersionBackcompat, AnchorPreserved,
                  NoSchemaDrift]
  truth:         CANONICALIZING_NEAR → targeting OK
  publish:       DENY (internal only)
  schema_version: v2V
}
```

---

*AppD — Registry, Profiles, Version IDs — v2V binding COMPLETE*
*64/64 cells filled for CANON::LANG.COMPILER::AST.PIPELINE*
