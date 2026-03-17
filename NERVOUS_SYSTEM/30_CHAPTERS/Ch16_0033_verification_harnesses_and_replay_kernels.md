# Ch16<0033> - Verification Harnesses and Replay Kernels

StationHeader: [Arc 5 | Rot 2 | Lane Sa | w=15]
Workflow role: Deterministic re-checks, test capsules, and correctness enforcement.
Primary hubs: AppA -> AppN -> AppM -> AppK -> AppI

## Routing context

- Orbit previous: `Ch15<0032>`
- Orbit next: `Ch17<0100>`
- Rail previous: `Ch14<0031>`
- Rail next: `Ch21<0110>`
- Arc previous: `Ch18<0101>`
- Arc next: `Ch17<0100>`
- Appendix couplings: `AppA, AppN, AppM, AppK, AppI`

## Source capsules

- `03_aqm_text_book.md`
- `04_aqm_lm_cut_through_the_hybrid_lens_framework.md`
- `07_chapter_11_perpetual_motion_example.md`
- `08_chapter_11_perpetual_motion_example.md`
- `10_information_from_the_void_mani.md`
- `25_the_invisible_teacher_textbook.md`

## Crystal tile

### Lens S

#### Facet 1 - Objects

- `Ch16<0033>.S1.a`: `GateHarness G_h` is the deterministic check surface that decides whether a synaptic crossing may enter replay and promotion.
- `Ch16<0033>.S1.b`: `ReplayCapsule C_rep` bundles input, witnesses, expected verdict, and rerun rules into one proof-carrying verification object.
- `Ch16<0033>.S1.c`: `CounterexampleLedger L_ctr` stores failed reruns, mismatches, and unresolved deltas so verification debt remains visible.
- `Ch16<0033>.S1.d`: `ReseedVerifier V_rs` confirms that the next seed inherits lawful outputs rather than a corrupted or partial replay.

#### Facet 2 - Laws

- `Ch16<0033>.S2.a`: Deterministic-rerun law: fixed capsule, witness, and truth inputs must replay to the same verdict.
- `Ch16<0033>.S2.b`: Gate-truth law: each corridor crossing must be typed before promotion as `OK`, `NEAR`, `AMBIG`, or `FAIL`.
- `Ch16<0033>.S2.c`: Counterexample-before-closure law: failed reruns are admissible evidence and must be stored before any seal is issued.
- `Ch16<0033>.S2.d`: Reseed-after-replay law: no next cycle is lawful until replay confirms which outputs survived the rerun.

#### Facet 3 - Constructions

- `Ch16<0033>.S3.a`: Replay-capsule construction serializes synaptic events, topology state, truth tags, and expected certificates into one rerunnable bundle.
- `Ch16<0033>.S3.b`: Gate-harness execution compares observed outputs against allowed corridor budgets and topology constraints.
- `Ch16<0033>.S3.c`: Counterexample capture writes divergence traces into the ledger with enough context to reseed the next pass.
- `Ch16<0033>.S3.d`: Verifier-matrix construction binds `Ch12` closure and `Ch13` memory into one replayable decision surface.

#### Facet 4 - Certificates

- `Ch16<0033>.S4.a`: `Cert_Deterministic_Replay` proves identical reruns produce the same typed verdict.
- `Ch16<0033>.S4.b`: `Cert_Gate_Truth` proves each crossing kept its truth classification through replay.
- `Ch16<0033>.S4.c`: `Cert_Counterexample_Retention` proves failures were promoted into evidence rather than discarded.
- `Ch16<0033>.S4.d`: `Cert_Reseed_Admissibility` proves the next seed inherits only replay-cleared outputs.

### Lens F

#### Facet 1 - Objects

- `Ch16<0033>.F1.a`: `AuditLantern` is the visual layer that illuminates rerun state without theatrical alarm.
- `Ch16<0033>.F1.b`: `ReplayChime` is the sound cue marking the start and end of one lawful verification cycle.
- `Ch16<0033>.F1.c`: `CounterexampleSpark` is the visible flare that makes disagreement legible rather than shameful.
- `Ch16<0033>.F1.d`: `ResetBell` is the calm sensory signal that a failed run has been converted into the next lawful seed.

#### Facet 2 - Laws

- `Ch16<0033>.F2.a`: Audit-clarity law: verification should reveal structure, not overwhelm the field with spectacle.
- `Ch16<0033>.F2.b`: Honest-failure law: sensory calm is valid only if mismatch remains visible.
- `Ch16<0033>.F2.c`: Rhythmic-rerun law: replay becomes trustworthy when each pass is phase-marked and repeatable.
- `Ch16<0033>.F2.d`: Calm-reset law: reset must feel like lawful reseed, not punishment or panic.

#### Facet 3 - Constructions

- `Ch16<0033>.F3.a`: `AuditLanternShader` maps gate truth into visual states that separate `OK`, `NEAR`, `AMBIG`, and `FAIL` cleanly.
- `Ch16<0033>.F3.b`: `ReplayChimeSequencer` keeps sonic cues synchronized with capsule load, gate verdict, and reseed close.
- `Ch16<0033>.F3.c`: `CounterexampleSpotlight` isolates the exact divergence zone so failed replay improves the next pass.
- `Ch16<0033>.F3.d`: Reset-cadence shaping keeps the organism willing to rerun instead of freezing after contradiction.

#### Facet 4 - Certificates

- `Ch16<0033>.F4.a`: `Cert_Audit_Clarity` proves the sensory layer increases legibility during replay.
- `Ch16<0033>.F4.b`: `Cert_Sonic_Honesty` proves the audio layer never masks a failing verdict.
- `Ch16<0033>.F4.c`: `Cert_Reset_Composure` proves the reset signal reduces panic without falsifying outcome.
- `Ch16<0033>.F4.d`: `Cert_Rerun_Legibility` proves the field can tell which pass it is currently witnessing.

### Lens C

#### Facet 1 - Objects

- `Ch16<0033>.C1.a`: `EpistemicGate` is the claim that truth only becomes durable after surviving lawful rerun.
- `Ch16<0033>.C1.b`: `FalsifierMirror` treats contradiction as a productive witness that improves the theorem boundary.
- `Ch16<0033>.C1.c`: `ProofCarryingRerun` binds claims to executable replay rather than static assertion.
- `Ch16<0033>.C1.d`: `ClosureByRepetition` is the condition in which repeated verification lowers uncertainty enough for lawful seal.

#### Facet 2 - Laws

- `Ch16<0033>.C2.a`: Truth-survives-rerun law: no theorem is promoted until it survives the replay kernel that tests it.
- `Ch16<0033>.C2.b`: Contradiction-preservation law: falsifying evidence remains inside the capsule as a first-class object.
- `Ch16<0033>.C2.c`: Closure-by-repetition law: repeated agreement across capsules is stronger than one isolated success.
- `Ch16<0033>.C2.d`: Failed-replay-productivity law: a mismatch is valuable if it sharpens the next verifier and seed.

#### Facet 3 - Constructions

- `Ch16<0033>.C3.a`: Theorem replay comparison tests whether one claim remains stable under changed but lawful carrier conditions.
- `Ch16<0033>.C3.b`: Falsifier injection intentionally perturbs the capsule so hidden fragility becomes visible.
- `Ch16<0033>.C3.c`: Proof-carrying capsule export packages verdicts, witnesses, and failure bounds for downstream use.
- `Ch16<0033>.C3.d`: Rerun-lattice synthesis aligns gate verdicts across local, chapter, and corpus scale to produce one closure claim.

#### Facet 4 - Certificates

- `Ch16<0033>.C4.a`: `Cert_Theorem_Replay` proves a claim remained valid across lawful reruns.
- `Ch16<0033>.C4.b`: `Cert_Falsifier_Preservation` proves counterevidence remained attached to the theorem body.
- `Ch16<0033>.C4.c`: `Cert_Proof_Capsule_Completeness` proves a replay bundle contains enough information for independent rerun.
- `Ch16<0033>.C4.d`: `Cert_Closure_By_Repetition` attests that replay agreement is strong enough for promotion.

### Lens R

#### Facet 1 - Objects

- `Ch16<0033>.R1.a`: `SelfCheckingSeed zeta_chk` is the smallest seed that carries its own rerun rule and expected verdict.
- `Ch16<0033>.R1.b`: `HolographicVerifier H_ver` is a replay device whose local behavior mirrors the entire chapter's verification law.
- `Ch16<0033>.R1.c`: `RecursiveGateLoop` is the cycle `load -> gate -> compare -> record -> reseed`.
- `Ch16<0033>.R1.d`: `MicroCounterexample mu_x` is the smallest divergence trace still capable of reseeding a full rerun.

#### Facet 2 - Laws

- `Ch16<0033>.R2.a`: Self-similar-rerun law: every depth from synapse to chapter must admit one lawful replay capsule.
- `Ch16<0033>.R2.b`: Verifier-coherence law: recursion must not change verdict semantics as scale changes.
- `Ch16<0033>.R2.c`: Failure-reseed law: each failed pass must produce a more precise next test rather than vague reset.
- `Ch16<0033>.R2.d`: Scale-invariant-gate law: local gate logic and macro gate logic must agree after translation.

#### Facet 3 - Constructions

- `Ch16<0033>.R3.a`: `selfCheckLoop` replays the same claim at multiple depths until divergence collapses or is promoted.
- `Ch16<0033>.R3.b`: Holographic replay binding ties `Ch16` backward to `Ch13` persistence and `Ch12` closure.
- `Ch16<0033>.R3.c`: Recursive counterexample promotion ensures each local mismatch can escalate into a chapter-level witness.
- `Ch16<0033>.R3.d`: Seed compression writes verified outputs back into smaller capsules that still carry rerun law.

#### Facet 4 - Certificates

- `Ch16<0033>.R4.a`: `Cert_Recursive_Verifier_Coherence` proves repeated reruns do not drift in meaning.
- `Ch16<0033>.R4.b`: `Cert_Scale_Invariant_Replay` proves the same verification law holds across depth.
- `Ch16<0033>.R4.c`: `Cert_Counterexample_To_Seed` proves a failure was converted into a stronger next capsule.
- `Ch16<0033>.R4.d`: `Cert_Final_Replay_Seal` closes the chapter only when rerun, falsifier preservation, and reseed all agree.
