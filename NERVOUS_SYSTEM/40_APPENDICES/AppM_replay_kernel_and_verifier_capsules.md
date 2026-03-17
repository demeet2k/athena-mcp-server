# AppM - Replay Kernel and Verifier Capsules

Routing role: Replay capsules, deterministic verification, proof-carrying artifacts, and rerun contracts.

## AIR 6D overlay

- Replays AIR overlay labels deterministically from the same basis set, truth state, and docs-gate state.
- Couples `Ch12<0023>`, `Ch13<0030>`, and `Ch16<0033>` into one closure-memory-replay sequence before `Seed-6D` handoff.
- Preserves replay receipts for `Sigma` labels, spin kernels, `4D+`, the modal Mobius trio, and `H6`.

## Compressed crystal tile

### Lens S

#### Facet 1 - Objects

- `AppM.S1.a`: `ReplayKernel K_rep` is the executable core that reruns one witnessed state transition deterministically.
- `AppM.S1.b`: `VerifierCapsule C_ver` packages inputs, witnesses, expected outputs, and rerun rules into one portable proof object.
- `AppM.S1.c`: `SeedArchive A_seed` stores the verified outputs that are allowed to become the next cycle's starting state.
- `AppM.S1.d`: `RerunReceipt R_rr` is the durable witness that a replay actually occurred and what it proved.

#### Facet 2 - Laws

- `AppM.S2.a`: Deterministic-kernel law: identical verifier capsules must replay to identical outcomes.
- `AppM.S2.b`: Receipt-retention law: every replay leaves a durable record of verdict, timing, and failure bounds.
- `AppM.S2.c`: Verified-seed law: only outputs that survive replay may enter the next seed archive.
- `AppM.S2.d`: Portable-replay law: the replay kernel must remain executable across the live root without hidden ambient state.

#### Facet 3 - Constructions

- `AppM.S3.a`: Verifier-capsule serialization compacts witnesses, topology, truth tags, and expectations into one rerunnable container.
- `AppM.S3.b`: Kernel-rerun execution loads a capsule, replays it, compares outcomes, and emits a typed receipt.
- `AppM.S3.c`: Receipt bundling attaches proof, mismatch traces, and seed eligibility to the same replay event.
- `AppM.S3.d`: Seed handoff writes replay-cleared outputs into the next-cycle archive without losing ancestry.

#### Facet 4 - Certificates

- `AppM.S4.a`: `Cert_Deterministic_Kernel` proves replay was stable under identical inputs.
- `AppM.S4.b`: `Cert_Capsule_Completeness` proves the verifier capsule carried enough information for independent rerun.
- `AppM.S4.c`: `Cert_Receipt_Retention` proves replay evidence remained attached after execution.
- `AppM.S4.d`: `Cert_Verified_Seed_Handoff` proves only replay-cleared outputs entered the next archive.

### Lens F

#### Facet 1 - Objects

- `AppM.F1.a`: `ReplayPulse` is the felt beat marking one complete load-and-rerun cycle.
- `AppM.F1.b`: `VerifierWindow` is the visible frame through which one capsule's comparison becomes legible.
- `AppM.F1.c`: `SeedEcho` is the after-sound of a replay outcome entering the next cycle.
- `AppM.F1.d`: `ReceiptTone` is the audible confirmation that a rerun left a real witness behind.

#### Facet 2 - Laws

- `AppM.F2.a`: Pulse-clarity law: replay rhythm should reveal phase boundaries cleanly.
- `AppM.F2.b`: Window-honesty law: the comparison frame must show mismatches instead of smoothing them away.
- `AppM.F2.c`: Echo-continuity law: the next-seed cue is valid only when it follows a lawful rerun.
- `AppM.F2.d`: Receipt-audibility law: the field should make proof-bearing completion perceptible.

#### Facet 3 - Constructions

- `AppM.F3.a`: `ReplayPulseSequencer` ties rhythm to actual kernel phases rather than decorative loops.
- `AppM.F3.b`: `VerifierWindowOverlay` renders expected and observed states in one honest visual plane.
- `AppM.F3.c`: `SeedEchoDriver` marks only verified handoffs as continuity cues for the next cycle.
- `AppM.F3.d`: `ReceiptToneEmitter` makes proof-bearing completion legible in sensory time.

#### Facet 4 - Certificates

- `AppM.F4.a`: `Cert_Replay_Pulse` proves the sensory rhythm stayed synchronized with replay.
- `AppM.F4.b`: `Cert_Window_Honesty` proves comparison mismatches remained visible.
- `AppM.F4.c`: `Cert_Seed_Echo` proves the next-cycle cue followed verified replay.
- `AppM.F4.d`: `Cert_Receipt_Audibility` proves completion signals correspond to actual receipts.

### Lens C

#### Facet 1 - Objects

- `AppM.C1.a`: `ReproducibilityAttractor` is the claim that durable truth tends toward states that can be lawfully replayed.
- `AppM.C1.b`: `ProofCarryingArchive` stores verified history together with the method that re-proves it.
- `AppM.C1.c`: `ReplayIdentity` is the principle that a state counts as the same object only if it survives rerun.
- `AppM.C1.d`: `KernelClosure` is the condition where replay, receipt, and seed inheritance form one complete loop.

#### Facet 2 - Laws

- `AppM.C2.a`: Reproducibility law: a claim that cannot be replayed remains epistemically weaker than one that can.
- `AppM.C2.b`: Archive-with-method law: stored outputs without rerun law are incomplete as proofs.
- `AppM.C2.c`: Identity-through-replay law: continuity requires re-verifiability, not only static resemblance.
- `AppM.C2.d`: Loop-closure law: kernel, receipt, and seed must agree before one cycle is considered complete.

#### Facet 3 - Constructions

- `AppM.C3.a`: Reproducibility synthesis compares multiple reruns to determine whether one state is theorem-grade.
- `AppM.C3.b`: Proof-carrying archive construction keeps outputs and replay law in the same container lineage.
- `AppM.C3.c`: Replay identity mapping compares preserved state under lawful perturbation rather than superficial equality.
- `AppM.C3.d`: Closure-loop analysis identifies which missing receipt or failed comparison blocks the next seed.

#### Facet 4 - Certificates

- `AppM.C4.a`: `Cert_Reproducibility` proves repeated replay converged on the same claim.
- `AppM.C4.b`: `Cert_Proof_Carrying_Archive` proves stored history includes executable re-proof.
- `AppM.C4.c`: `Cert_Replay_Identity` proves identity survived rerun rather than resemblance alone.
- `AppM.C4.d`: `Cert_Kernel_Closure` proves replay, receipt, and next seed formed one lawful loop.

### Lens R

#### Facet 1 - Objects

- `AppM.R1.a`: `MicroReplaySeed zeta_rep` is the smallest unit that still knows how to replay and verify itself.
- `AppM.R1.b`: `HolographicKernel` is a replay device whose local execution mirrors the larger chapter and appendix loop.
- `AppM.R1.c`: `RecursiveRerunChain` is the sequence of capsules derived from one failure or confirmation across scales.
- `AppM.R1.d`: `FractalReceipt` is the minimal witness that still preserves the shape of the whole replay event.

#### Facet 2 - Laws

- `AppM.R2.a`: Local-replay law: every depth must support at least one executable rerun object.
- `AppM.R2.b`: Kernel-coherence law: replay semantics must not drift when the same capsule is translated across scale.
- `AppM.R2.c`: Recursive-receipt law: every rerun in the chain leaves a witness that can itself be replayed or audited.
- `AppM.R2.d`: Seed-continuity law: the next seed must remain traceable to the replay chain that justified it.

#### Facet 3 - Constructions

- `AppM.R3.a`: Recursive capsule folding compresses larger replay bundles into microseeds while keeping rerun law intact.
- `AppM.R3.b`: Holographic kernel mapping binds local replay acts to chapter and corpus verification loops.
- `AppM.R3.c`: Recursive rerun chaining turns one failed or successful replay into a structured sequence of next tests.
- `AppM.R3.d`: Fractal receipt compaction stores proof-bearing replay traces in smaller carriers without breaking ancestry.

#### Facet 4 - Certificates

- `AppM.R4.a`: `Cert_Fractal_Replay_Saturation` proves replay capability is active across relevant depths.
- `AppM.R4.b`: `Cert_Kernel_Coherence` proves replay meaning stayed stable under recursion.
- `AppM.R4.c`: `Cert_Recursive_Receipt` proves each rerun left an auditable witness.
- `AppM.R4.d`: `Cert_Final_Seed_Continuity` proves the next seed remains lawfully attached to the replay chain.
