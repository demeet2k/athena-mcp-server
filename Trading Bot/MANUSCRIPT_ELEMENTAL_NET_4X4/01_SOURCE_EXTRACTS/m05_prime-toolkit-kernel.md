# PRIME Toolkit Kernel

        - `doc_id`: `M05`
        - `source`: `Memory Docs/PRIME Toolkit kernel.docx`
        - `primary crystal`: `yes`
        - `cluster`: `numeric`
        - `elements`: `earth`
        - `modes`: `kernel, verification`
        - `word_count`: `11339`
        - `paragraph_count`: `1787`

        ## Quick Preview

        PRIME Toolkit kernel | 1) Kernel state Σ (one engine, many projections) | Every run is a single state machine (\Sigma) that evolves under a fixed κ-contract.

        ## Early Headings

        - PRIME Toolkit kernel
- 1) Kernel state Σ (one engine, many projections)
- Every run is a single state machine (\Sigma) that evolves under a fixed κ-contract.
- [\boxed{\Sigma ;=; (Q,; C,; P,; T,; \mathcal L,; \kappa)}]
- Q — Typed work queue (targets)
- FactorTask(n)
- DesertTask(I) (interval)
- ConstellationTask(H, I|n) (offset set (H), search interval or anchor)

        ## Extracted Text

        PRIME Toolkit kernel
1) Kernel state Σ (one engine, many projections)
Every run is a single state machine (\Sigma) that evolves under a fixed κ-contract.
[\boxed{\Sigma ;=; (Q,; C,; P,; T,; \mathcal L,; \kappa)}]
Q — Typed work queue (targets)
A deterministic queue of tasks, each with a domain label, corridor descriptor pointer, and budget slice.
FactorTask(n)
DesertTask(I) (interval)
ConstellationTask(H, I|n) (offset set (H), search interval or anchor)
SpectrumTask(window|dataset_ref)
CrossTask(...) (hybrids-of-hybrids)
Each task record includes:
task_id (stable)
domain ∈ {factor, desert, constellation, spectrum, cross}
corridor_id
budget (time/ops/memory caps)
priority (derived deterministically from telemetry + κ)
C — Corridor descriptor (candidate sets + constraints + jump operators)
The corridor is the only place search is allowed to happen. A corridor descriptor is:
[\boxed{C = (\mathcal X,; \mathcal K,; \mathcal R,; \mathcal N,; \mathcal J,; \mathcal Z,; \epsilon_\kappa)}]
(\mathcal X): candidate representation (sets, intervals, residue classes, peak buckets)
(\mathcal K): hard constraints (necessary conditions, admissibility guards)
(\mathcal R): rotation maps (chart changes)
(\mathcal N): nullifiers (necessary-condition projectors; never drop true witnesses)
(\mathcal J): compiled jump operators (wheels, tables, meet-in-middle indices)
(\mathcal Z): zero-point gates (collapse-to-certificate operators)
(\epsilon_\kappa): uncertainty envelope for Tier-2 signals at this κ
Invariant: corridors may shrink; they may not silently change meaning. Any change to (\mathcal X,\mathcal K,\mathcal R,\mathcal N,\mathcal J,\mathcal Z) must be ledgered.
P — Proof store (certificates only)
The proof store is a multiset of Tier-3 objects (certificates) plus their hashes.
T — Telemetry store (cost + stability)
Telemetry records:
rejection rates by nullifier stage
corridor size estimates
module costs (time/ops)
κ-consistency/stability signals (routing-only; never truth)
𝓛 — Ledger chain (immutable replay record)
Ledger is a hash-linked chain ({\mathcal L_\kappa}) containing operator specs, κ parameters, candidate artifacts (labeled), and certificate hashes.
2) Output contract (truth barrier)
2.1 Tier discipline
All runtime outputs are typed into one of three tiers:
Tier 1 (Identities): exact equalities in a declared topology (e.g., (\bmod p), integer equality).
Tier 2 (Signals): bounded observables used only for routing; must carry κ and (\epsilon_\kappa).
Tier 3 (Certificates): verifiable proof objects; the only tier allowed to assert truth.
2.2 Certificate-first rule (the runtime cannot lie)
The runtime may output “CERTIFIED” only if it outputs the certificate payload, verifier spec/version, and the certificate hash in the ledger.
2.3 Domain truth objects (Tier 3)
The kernel asserts truth only through these certificate types:
PrimeCertificate(p)
FactorCertificate(n,d) (witness (1<d<n) and (d\mid n))
ValuationCertificate(n,p,α) (exact (v_p(n)=α))
FactorizationLedger(n) (complete certified factorization)
DesertCertificate(I) (interval prime-free)
ConstellationCertificate(H,n) (all (n+h) prime-certified)
PrimePowerCertificate(p,k) (exact event (p^k), plus prime cert for (p))
Everything else—scores, peaks, coherence fields, candidate sets—is Tier-2 signal and must remain labeled as such.
3) The κ-RG runtime loop (complete algorithm)
At each κ, the runtime must declare apertures, bandwidth/smoothing (if spectral), budgets, thresholds, (\epsilon_\kappa), determinism policy, and seeds—immutable for that κ run.
3.1 Seven-move execution cycle (per κ)
For κ from (\kappa_0) upward:
Move 0 — Initialize
Load datasets by hash (if any)
Load or derive corridor state (C)
Open ledger entry (\mathcal L_\kappa)
Move 1 — Rotate (chart selection)
Apply a typed rotation (R \in \mathcal R) to map corridors into shadow frames that linearize constraints (residue/log/diagonal/power/orbit/dual charts).Output: rotated corridor (C^{(R)}) (Tier-1 identity about chart equivalence) + routing signals.
Move 2 — Nullify (necessary conditions stack)
Apply a cascade of nullifiers (N_1,\dots,N_s \in \mathcal N):[C_{i+1} := N_i(C_i)]Each nullifier must be sound: it may not remove true witnesses.Record rejection rates in telemetry.
Move 3 — Compile jumps (indexers/wheels/tables)
From the surviving corridor, compile jump operators (\mathcal J):
wheels (CRT residue routing)
meet-in-middle ratio indices
prime-bank masks
spectrum peak buckets → discrete candidate setsThese are “reverse-spin” operators that make later search cheap.
Move 4 — Spin (bounded traversal)
Traverse only allowed corridors under budget slices, generating candidate witnesses (Tier-2 only).Rules:
traversal must be deterministic given κ policy + seeds
candidates must remain labeled (never asserted)
Move 5 — Collapse (zero-point gates)
Attempt certificate collapse through gates (\mathcal Z):
prime certification gate
divisor/valuation gates
desert coverage/survivor-proof gate
constellation member-proof gate
prime-power exact identity gate
A collapse gate either:
emits a certificate (Tier-3), or
shrinks the corridor to below the certification threshold (M_{\text{cert}}) so exhaustive certification becomes possible (still must emit certificates).
Move 6 — Commit (verify + ledger)
Before commit:
verify every produced certificate with its verifier spec/version
hash payloads, link into (\mathcal L_\kappa), write prev_hash and entry_hash
Stop if desired proof artifacts are achieved; otherwise κ escalates under the escalation policy.
4) Routing policy (one queue, many domains)
Routing is deterministic under telemetry + κ.For each task popped from (Q):
If it can be collapsed via a 2-way hybrid within current corridor size → do it.
Else attempt 3-way pivot.
Else attempt 4-way fusion.
Else mark task INCOMPLETE and consider κ escalation.
Cross-domain routing is allowed only through:
certified witnesses (hard facts), or
necessary-condition constraints (safe nullifiers)
No other cross-domain leakage is allowed.
5) κ escalation (how resolution increases)
κ-refinement increases aperture/bandwidth/budget only when corridors cannot collapse within current uncertainty; κ-consistency rejects unstable signals and controls proof cost, never substitutes for certificates.
Escalate κ only if at least one trigger holds:
corridor size remains above (M_{\text{cert}})
κ-consistency indicates instability at current resolution
nullifier rejection rate too low (filters too weak)
budgets exhausted without collapse
Escalation actions (must be explicit + ledgered):
increase sieve cutoff (B(\kappa))
enlarge wheel modulus (W(\kappa)) within caps
increase spectral bandwidth (T_\kappa) and adjust smoothing (\sigma_\kappa)
adjust thresholds, restarts, and budgets
6) Minimal correctness theorem (runtime-level)
If:
Tier-3 is the only truth tier,
every commit verifies all certificates,
every ledger entry is hash-linked and replayable,
then the runtime cannot emit a false arithmetic claim, regardless of scheduling or heuristics, because truth is asserted only by proof objects.
Module A — Factorization engine (micro → macro) — FINAL SPEC (PRIME Toolkit)
This module is the certificate-perfect factorizer: it can be aggressive about search and heuristics, but it is incapable of claiming a factor unless divisibility is verified, and incapable of claiming “fully factored” unless the product identity verifies exactly.
A.0 State + gates (what the module actually runs)
Inputs
integer block (t>1)
corridor (C) (budgets, branch policy, determinism/seed policy)
constants (\mathbf H) (bank primes, wheel primes, limits, restart policy, prime-cert policy)
Truth gates (the only truth exits)
Prime gate (Z_0^{\text{prime}}(t)) → PrimeCertificate(t) or NOT-PRIME
Divisor gate (Z_0^{\text{div}}(t,d)) accepts only if (1<d<t) and (t\bmod d=0); emits FactorCertificate(t,d)
Output types
Either a certified split (t = d\cdot (t/d)) with FactorCertificate(t,d), or “no success under budget” with a residual plan, or partial unresolved blocks.
A.1 Filter cascade (ultra-cheap → cheap → moderate → expensive → cert)
This is not “try algorithms until something works.” It’s a deterministic staged weapon chain where each stage either:
emits a certified witness (divisor/valuation/prime), or
emits nothing but telemetry/residuals (Tier-2), or
escalates by policy.
Stage 0 — Ultra-cheap: bank gcd + valuation extraction (Square lens)
Goal: annihilate all small-prime structure at near-zero cost.
Prime bank mask (M_{\text{bank}}=\prod_{p\le P_{\max}} p) (or chunked masks) from (\mathbf H).
Compute (g=\gcd(t,M_{\text{bank}})).
If (g>1): fully factor (g) (it’s “small”), extract exact multiplicities using valuation certificates, and divide them out of (t) (ledger update).
If residue becomes 1 → done for this block; if residue is prime → attach PrimeCertificate and done.
Certificates emitted here:
ValuationCertificate(t,p,α) for each extracted prime power
(optional) GcdCertificate as a witness for the bank extraction step
Stage 1 — Cheap: perfect-power shatter (Fractal lens)
Goal: convert “hard” composites into repeated smaller blocks by exact structure detection.
If (t=r^k) for any (k\in[2,\text{POWER_K_MAX}]) (from (\mathbf H)), verify exactly and emit PerfectPowerCertificate(t=r^k), then push (r) back into the work queue (k) times.
Stage 2 — Cheap-to-moderate: diagonal near-square scan with minesweeper wheel (Diagonal lens)
Goal: kill almost all “a-values” using a necessary QR filter, then only test survivors.
This is your ratio-index / jump-table pattern applied to Fermat-style difference of squares.
For odd (t):
set (a=\lceil\sqrt{t}\rceil)
precompute QR wheel allowed residues (A_W(t)) and jump table (\text{next}{A_W}) so we skip directly between admissible residues:[a \leftarrow a + \text{next}{A_W}(a\bmod W)]
For each tested (a) (bounded by FERMAT_LIMIT): compute (b^2=a^2-t). If (b^2) is a square, set (d=a-b).
Apply (Z_0^{\text{div}}(t,d)). If accepted, emit SquareDifferenceCertificate and push ((d, t/d)) into queue.
Wheel growth is deterministic: if diagonal waste is high and rejection too low, add primes to the wheel up to (W_{\max}), and ledger it.
Stage 3 — Moderate: chaotic mixing with degeneracy-managed restarts (Cloud lens)
Goal: run Pollard/Brent-style mixing to produce gcd witnesses, but avoid spending the whole budget in “bad orbits.”
For up to RHO_RESTARTS:
run mixing up to RHO_BUDGET steps to produce (d=\gcd(|x-y|,t)).
accept only if (1<d<t) and (t\bmod d=0) (randomness affects time-to-find, never correctness).
if degeneracy signatures trigger early (stagnant gcd batches, short cycles, involution traps), restart with logged parameters and seed.
on success, emit FactorCertificate(t,d) and push ((d,t/d)).
If no factor under policy budgets, mark block INCOMPLETE (partial output permitted, false certainty forbidden).
Stage 4 — Expensive: ECM / NFS escalation (macro weapon)
When the earlier lenses stall, escalate by corridor policy:
ECM for medium factors, NFS-ready relation pipeline for large composite blocks.The key invariant stays the same: any split must pass (Z_0^{\text{div}}), and final correctness is a ledger proof.
A.2 Ratio indexing (meet-in-the-middle factor hunting)
This module treats “meet-in-middle” as a compiled jump operator family (\mathcal J), not a one-off trick.
Canonical form
If your factor witness can be rearranged into:[\text{key}(L) = \text{key}(R)]you must build an index on the cheaper side and reduce the search to hash lookups.
Concrete instantiation (diagonal lens):
left side generates admissible (a\bmod W) residues via QR sets (A_W(t))
right side is “squarehood” check of (b^2=a^2-t)
jump compilation converts dense scanning into sparse stepping.
General rule: whenever a search can be expressed as a constraint of the form “membership in a precomputed allowed set,” compile it into a jump table (reverse-spin) and ledger the build parameters.
A.3 Hierarchical propagation (Nullifier N1 + recursive shatter)
Once any certified divisor is found, it becomes a hard nullifier for every “is-prime” hypothesis about that block:
[d\mid n,\ 1<d<n \Rightarrow n\ \text{composite}.]This is Nullifier N1 (witness-based annihilation).
Operational consequences
The moment FactorCertificate(t,d) exists, all prime-claims for (t) are invalidated; the block is replaced by two smaller blocks ((d,t/d)) in the queue.
Recursion is mandatory: each new block is re-entered into the lens chain until prime-gated or exhausted.
Perfect-power shatter amplifies this: a single certificate can spawn (k) sub-blocks (structured recursion).
A.4 The canonical macro chain (how the toolkit actually routes)
The recommended factorization chain (macro “hybrid-of-hybrids”) is:
[\boxed{\mathbb H^\star_{\text{fact}} := \mathbb M_3\circ \mathbb M_2\circ \mathbb M_1}]where:
( \mathbb M_1 ): dust-stripper (bank gcd + perfect power shatter)
( \mathbb M_2 ): resonance miner (diagonal wheel)
( \mathbb M_3 ): chaos breaker (cloud mixing w/ degeneracy control)
This chain is applied recursively to every unresolved block, always gated by prime/divisor truth gates.
A.5 Completion: FactorizationLedger (what “done” means)
A complete output must include:
target (n)
sorted factors ((p,\alpha))
PrimeCertificate(p) for each (p)
ValuationCertificate(p,\alpha) for each multiplicity
exact division transcript reducing remainder to 1
constants (\mathbf H) used, telemetry, and hashes
status = VERIFIED or PARTIAL
If budget ends early, output certified factors + unresolved blocks, never a complete claim.
Module B — Prime deserts toolkit (gap discovery + certification) — FINAL SPEC (PRIME Toolkit)
A prime desert is an interval (I=[N,,N+L-1]) that contains no primes, proven by one of the DesertCertificate formats (A/B/C).This module is the desert counterpart to factorization: it runs a κ-guided cascade that turns “likely desert” signals into a provable prime-free interval with replayable evidence.
B.0 Objects, masks, and the desert corridor
B.0.1 B-sieve mask and period
Fix a cutoff (B). Let[P_B = \prod_{p\le B} p,\qquadA_B(n)=\mathbf 1[\gcd(n,P_B)=1].]Interpretation:
(A_B(n)=0): hard-killed (composite by small prime)
(A_B(n)=1): survivor (a “pore” in the sieve medium)
This is the “band-gap medium”: deserts are long runs where constraints align to suppress survivors.
B.0.2 Survivor set on an interval
For (I=[N,N+L-1]),[\mathrm{Surv}_B(I)={n\in I: A_B(n)=1}.]Survivors are computed by segmented marking or wheel lookup.
B.0.3 Desert zero point
The interval is certifiable prime-free when:
Type A: (\mathrm{Surv}_B(I)=\varnothing) (full coverage), or
Type B: every survivor has a verified composite certificate.
B.1 Desert candidate generation (segmented, κ-guided)
This is the high-throughput stage: generate many candidate intervals cheaply, then spend compute only where the corridor collapses.
B.1.1 Segmented scan (no giant arrays)
For large (N), never allocate a global array. Use segmented marking of multiples of primes (\le B) on each interval window ([N,N+L]) and extract survivors.
Algorithm: SegmentedSurvivors(N, L, B)
Build a canonical PrimeStream(B) (deterministic, digest-pinned).
Allocate a segment mark array of length (L) (bit/byte).
For each prime (p\le B):
find first multiple (m=\lceil N/p\rceil p)
mark all (m,m+p,\dots\le N+L-1) (with boundary handling (m=p) if needed)
Survivors are positions unmarked (equivalently gcd=1 w.r.t. (P_B)).
Output:
survivor list (S=\mathrm{Surv}_B(I))
marking transcript digest (for replay compression)
B.1.2 κ-guided schedule (B escalation only on candidates)
Use the deterministic schedule:
Coarse scan at small (B) to find candidate deserts.
Increase (B) only on candidate intervals.
Stop increasing (B) when the survivor count is small enough that direct certification is cheap.
Policy variables:
(B_0) initial cutoff
growth rule (B\leftarrow \text{NextB}(B)) (e.g., multiply by 2 or jump to next primorial threshold)
survivor threshold (S_{\max}) (e.g., 0 for Type A attempt, or small number for Type B)
B.2 Nonlinear “hologram rule” (alignment-first search)
Never treat desert search as linear enumeration. Treat it as constraint alignment: deserts appear when many periodic constraints align to cover a contiguous offset set; therefore search for CRT-like alignment structure and only then certify.
B.2.1 Band-gap interpretation and deterministic engineered deserts
The sieve mask creates a periodic medium with period (P_B).
Long deserts are band gaps caused by alignment of periodic constraints.
Deterministic constructions (factorial, CRT coverings) generate guaranteed gaps and serve as test vectors.
B.2.2 CRT covering generator (constructive candidate engine)
To engineer a certified desert of length (L), choose primes (q_1,\dots,q_L) and impose:[N \equiv -j \pmod{q_j}\quad(1\le j\le L)]Then (q_j\mid (N+j)) and ([N+1,N+L]) is composite-only by construction.
This produces Type C certificates (CRT covering certificate).
B.2.3 Wheel run-length mining (alignment amplifier)
At a chosen (B), compute residue set:[\mathcal R_B={r\in[0,P_B):\gcd(r,P_B)=1}.]The longest run of zeros of (A_B) within one period corresponds to the largest gap between consecutive residues in (\mathcal R_B). This gives deterministic hard-desert candidates and tells the scan where to zoom.
B.3 Edge localization (don’t certify whole oceans)
Deserts are found by localizing edges, then certifying only the refined neighborhood.
B.3.1 Edge signal (Tier-2 only)
Define local porosity:[\rho_B([N,N+L-1])=\frac{1}{L}\sum_{n\in[N,N+L-1]} A_B(n).]Define edge signal:[E_B(N;L)=\rho_B([N,N+L-1])-\rho_B([N-L,N-1]).]Large (|E_B|) suggests a boundary.
B.3.2 κ-edge stability rule
An edge is promoted as a candidate boundary only if it persists as (B) increases and the edge location stabilizes within (\epsilon_\kappa).
B.4 Certification (three certificate types; one collapse condition)
Certification is the only place deserts become “true.” The module outputs one of the following:
Type A — Hard coverage / pure sieve (DesertCertificate-A)
Goal: prove (A_B(n)=0) for all (n\in I) by providing, for each (n), a witness small prime (p_n\le B) such that (p_n\mid n).
Payload (compressible):
interval (I)
cutoff (B)
witness structure: either
per-site witnesses (p_n), or
compressed wheel residue proof / segmented sieve transcript
Verifier: checks (p_n\le B) and (n\bmod p_n=0) for all sites (with boundary handling when (n=p_n)).
Type B — Coverage + survivor proofs (DesertCertificate-B)
Goal: certify prime-free interval when survivors exist.
Payload:
interval (I)
cutoff (B)
survivor list (S=\mathrm{Surv}_B(I))
for each survivor (s\in S), a CompositeCertificate(s) (factor witness or accepted composite proof)
Verifier: recomputes survivor status by checking (\gcd(n,P_B)=1) (or using the sieve transcript), checks each survivor certificate.
Type C — CRT covering certificate (DesertCertificate-C)
Goal: certify ([N+1,N+L]) composite-only by explicit congruences (q_j\mid(N+j)).
Payload:
length (L)
moduli (q_1,\dots,q_L)
CRT solution (N\bmod Q)
statement (q_j\mid(N+j)) for each (j)
Verifier: checks each congruence.
B.5 The practical collapse chain (4-way quartet, explicit)
Desert certification is a 4-way hybrid collapse:
Signal lens proposes candidate valley intervals (Tier-2)
Sieve lens hard-kills most sites (proof evidence for non-survivors)
Survivor lens enumerates pores precisely (finite list)
Composite lens certifies each survivor composite using the factor micro-chain
Collapse (zero point):[S=\varnothing\quad\text{or}\quad \forall s\in S,\ \mathrm{CompositeCertificate}(s)\ \text{verified}.]
The key integration rule is explicit: only run factorization on survivors (sparse), then emit DesertCertificate(I,B,S,certs).
B.6 Deterministic run procedure (the complete algorithm)
Procedure: DesertSearchAndCertify(N0, L, κ-policy)
Initialize (B=B_0).
Generate candidate windows using one of:
wheel run-length mining (hard desert candidates), or
edge signal peaks, or
CRT covering generator (engineered test deserts).
For each candidate interval (I):
compute survivors (S=\mathrm{Surv}_B(I)) via segmented scan
if (|S|=0): emit DesertCertificate-A (coverage proof) and stop for this (I)
else if (|S|\le S_{\max}):run CompositeMicroChain(s) on each (s\in S) (bounded), gather composite certs; emit DesertCertificate-B and stop
else: mark (I) as “still porous” and push to κ-refinement
κ-refinement step: increase (B) only for surviving candidate intervals, repeat until collapse rule triggers.
All steps must ledger:
(B), prime stream digest, segment policy id, survivor digest, and certificate hashes.
Module C — Prime constellation search (k-tuples) — FINAL SPEC (PRIME Toolkit)
A prime constellation is an offset pattern (H={h_1,\dots,h_k}\subset\mathbb Z) realized at anchor (n) when every (n+h_i) is prime. The module’s job is to (1) generate anchors efficiently, (2) annihilate impossible anchors early, (3) concentrate search via κ-refinement, and (4) emit only Tier-3 truth: ConstellationCertificate(H,n).
C.0 Definitions and corridor objects
C.0.1 Pattern and anchor domain
Pattern (H\subset\mathbb Z) finite (typically (0\in H) by convention).
Search domain: either an interval (I=[N,N+L)) of anchors or a set of candidate anchors supplied by another module (spectral/CRT/etc.).
C.0.2 Constellation witness set
For a candidate anchor (n), define:[X(n;H) := {n+h: h\in H}.]A successful constellation produces:
PrimeCertificate(n+h) for all (h\in H)
bundled as ConstellationCertificate(H,n).
C.0.3 κ-corridor for constellations
A constellation corridor at cutoff (B) is:[C_B(H,I)=\left(\mathcal X,\mathcal K,\mathcal N,\mathcal J,\mathcal Z,\epsilon_\kappa\right)]where:
(\mathcal X): anchor candidates (interval + residue classes, or explicit list)
(\mathcal K): admissibility + local congruence constraints
(\mathcal N): nullifiers (infeasibility projectors)
(\mathcal J): jump operators (wheel steps, residue indices)
(\mathcal Z): collapse gates (prime certification)
(\epsilon_\kappa): routing uncertainty (Tier-2 only)
C.1 Stage 1 — Admissibility gate (local obstruction test)
Admissibility is the first truth-preserving annihilator: if (H) is locally obstructed, it can never occur.
C.1.1 Local obstruction definition
For a prime (p), the pattern (H) is obstructed mod (p) if the set of residues ({-h \bmod p: h\in H}) covers all classes mod (p). Then for every (n), at least one (n+h\equiv 0\pmod p), so the constellation cannot be all prime.
C.1.2 Admissibility test (finite, deterministic)
Compute for each prime (p\le p_{\text{adm}}) (config):[S_p(H)={-h\bmod p: h\in H}.]If (|S_p(H)|=p) for any (p), reject (H) (no search performed).
Output:
either REJECT_PATTERN(H, p) (Tier-1 obstruction identity)
or ADMISSIBLE(H) (Tier-1 pass record; not a certificate)
C.2 Stage 2 — Wheel infeasibility annihilation (Nullifier N2)
This is the core “kill 99.99% cheaply” move, directly from your doc:
If (n \bmod P_B) is not in the allowed residue set, the pattern cannot occur at cutoff (B).
C.2.1 Wheel modulus
Let:[P_B=\prod_{p\le B} p.]In practice we don’t materialize (P_B); we track residues per prime and compile a wheel stepper.
C.2.2 Allowed residues per prime
For each prime (p\le B), an anchor residue (r=n\bmod p) is allowed iff:[r \not\equiv -h \pmod p \quad\forall h\in H](so none of the (n+h) are divisible by (p)).
Define:[R_p(H)=\mathbb Z/p\mathbb Z \setminus S_p(H).]
C.2.3 Nullifier N2 (infeasibility projector)
An anchor (n) survives cutoff (B) iff:[n\bmod p\in R_p(H)\quad \forall p\le B.]Nullifier N2 removes all anchors that violate any of these constraints.
Soundness: N2 only removes anchors that are guaranteed composite in at least one constellation component at cutoff (B); it never removes true constellations.
C.3 Jump compilation (turn constraints into stepping)
The point is to avoid scanning every (n). We compile the constraints into a deterministic stepper.
C.3.1 Residue wheel stepper
Choose a wheel modulus (W=\prod_{p\le B_w} p) (subset, small enough to step efficiently). Precompute the allowed residue set mod (W):
[R_W(H)={r\bmod W:\ r\bmod p\in R_p(H)\ \forall p\le B_w}.]
Then compile next_W[r] that jumps from one allowed residue to the next (cyclic). This is the same jump-table idea used elsewhere in your toolkit.
Traversal rule:
Anchor stream: (n = N + \delta)
Maintain (r = n \bmod W)
Jump: (n \leftarrow n + \text{next}_W[r])
This yields a sparse anchor stream containing only N2-survivors for the wheel primes.
C.3.2 Multi-prime sieve refinement (fast rejection)
For primes (p\le B) not in the wheel, do per-anchor residue checks (very cheap) and reject early.
C.4 Pattern-aware κ-refinement (stability flow)
Once you have a survivor stream, you refine in κ by increasing (B) and/or (W) only when the corridor remains too wide to certify.
C.4.1 Joint score (Tier-2 routing only)
Define a joint score for an anchor (n) based on how “prime-like” the constellation components look under cheap tests (e.g., no small factors, strong pseudoprime filters). This score routes attention but asserts nothing.
C.4.2 κ escalation rules (constellation-specific)
Escalate when:
survivor density after N2 remains high
score field is unstable across κ
budget spent without certificate collapse
Escalation actions:
increase (B) (more primes in N2)
increase (B_w) (bigger wheel)
tighten candidate interval around stable high-score anchors (edge localization)
All κ changes are ledgered as corridor updates.
C.5 Collapse gates (certificate production)
A constellation becomes truth only through the collapse gate:
C.5.1 Prime certification for all offsets (Z_const)
Given anchor (n), attempt to certify each (n+h) is prime using the kernel’s prime gate policy (deterministic primality test suite). If any fails, reject anchor and continue.
If all pass:[\boxed{\text{emit } \mathrm{ConstellationCertificate}(H,n)}]containing:
(H), (n)
PrimeCertificate(n+h) for every (h\in H)
replay bundle: wheel settings, (B,B_w), residue policy, and hashes.
C.6 Complete deterministic algorithm
Procedure: ConstellationSearch(H, I, κ-policy)
Admissibility gate: if obstructed, stop.
Initialize (B=B_0), choose wheel bound (B_w\le B), compile (R_W(H)) and next_W.
Iterate anchors in (I) using the wheel stepper:
For each anchor (n):
Apply residual checks for primes (p\le B) (not in wheel) → reject quickly if any (n+h\equiv 0\pmod p)
Optional Tier-2 scoring (routing)
If anchor survives and is prioritized: run collapse gate (Z_{\text{const}}(n))
If no certificate and corridor too wide:
κ-refine: increase (B) and/or (B_w), recompile, and continue on narrowed candidate region.
Output either:
a set of ConstellationCertificate(H,n) hits, or
NO-HIT-UNDER-BUDGET with ledgered telemetry (never a false claim).
Module D — Spectral reconstruction engine (peaks → candidates → certs) — FINAL SPEC (PRIME Toolkit)
This module turns a continuous/aggregate spectral field into a finite set of discrete arithmetic claims, then collapses those claims into Tier-3 certificates (primes, prime powers, deserts, constellations) and writes a replay ledger. It is explicitly designed to be bidirectional: spectra propose candidates; certified arithmetic objects validate or refute spectral structure.
D.0 Objects and the spectral corridor
D.0.1 Spectral field and κ-parameterization
At each κ, the module defines a spectral field (F_\kappa) and derived detection statistic (D_\kappa). κ controls bandwidth, smoothing, windowing, and resolution.
(F_\kappa(u)): a spectral transform / field over coordinate (u) (log-scale typical).
(D_\kappa(u)): a scalar detection statistic built from (F_\kappa) designed to spike at structure.
Contract: (F_\kappa) and (D_\kappa) are Tier-2 signals only; they route search but never assert truth.
D.0.2 Peak set and candidate map
Let peaks be:[\mathcal P_\kappa = \text{TopPeaks}(D_\kappa; \tau_\kappa)]with deterministic thresholding and tie breaks.
Map peaks into a finite candidate set:[\boxed{\mathcal C(u^*,\eta_\kappa) \subset \mathbb N}]where (\eta_\kappa) is the κ-uncertainty envelope around peak location/shape.
D.0.3 Prime-power harmonic model
Spectral peaks often include “harmonics” caused by prime powers (p^k). The module includes an explicit deconvolution step that separates the base prime line from its power overtones.
D.1 Build (F_\kappa) and (D_\kappa) (signal construction)
D.1.1 Spectral field (F_\kappa)
Choose a deterministic transform family (by configuration) that is appropriate for the dataset:
log-domain windowed transforms (e.g., cosine-like transforms on log x)
correlation transforms on residue/wheel density sequences
transform of indicator streams (survivor sequences (A_B(n)), constellation residue feasibility, etc.)
The toolkit only needs the contract:
input stream → (F_\kappa(u)) computed deterministically at κ
κ declares window (T_\kappa), smoothing (\sigma_\kappa), and coordinate grid.
D.1.2 Detection statistic (D_\kappa)
Compute (D_\kappa) as a robust functional of (F_\kappa), e.g.:
magnitude (|F_\kappa(u)|)
normalized contrast (|F|/\text{local_median})
multi-band coherence (peaks stable across adjacent κ)
The document’s core requirement is that (D_\kappa) is explicitly derived from (F_\kappa) and is the peak-picking surface.
Telemetry tracked:
peak counts vs threshold
peak stability across κ
computational cost per κ
D.2 Peak picking (log-time) → finite candidates (\mathcal C(u^*,\eta_\kappa))
D.2.1 Peak picking in log-time
Use deterministic peak selection:
local maxima in (D_\kappa)
non-maximum suppression by neighborhood width
keep top (M) peaks or all above (\tau_\kappa)
compute peak attributes: location, amplitude, curvature, width
This yields (\mathcal P_\kappa).
D.2.2 Candidate mapping
Each peak (u^*) produces a candidate bucket:[\mathcal C(u^*,\eta_\kappa)={n\in\mathbb N:\ \phi(n)\in[u^*-\eta_\kappa,\ u^*+\eta_\kappa]}]where (\phi) is your chosen mapping (commonly (\phi(n)=\log n), or log-spacing of structured anchors).
Implementation choices are modular; the invariant is:
a peak maps to a finite candidate set with size controlled by κ and budget.
This matches the doc’s “map peaks to finite candidate set (\mathcal C(u^*,\eta_\kappa)).”
D.2.3 Candidate compression (corridor formation)
Apply cheap arithmetic nullifiers immediately to candidates:
gcd with prime bank
wheel residue infeasibility for constellation patterns (if known)
local sieve survival tests for deserts
This makes (\mathcal C) sparse before cross-domain dispatch.
D.3 Prime-power deconvolution (harmonic stripping)
This is the spectral “separate fundamentals from overtones” step.
D.3.1 Harmonic signature
If primes (p) induce a feature at (\log p), prime powers (p^k) can induce features at (k\log p).
D.3.2 Deconvolution rule (discrete)
Given candidate set (\mathcal C), build a directed relation:[n \rightarrow n^{1/k}\ \text{if } n \approx p^k \text{ (integer check)}]and split candidates into:
base candidates likely to be primes
overtone candidates likely to be prime powers
Then attempt:
PrimePowerCertificate(p,k) if (n=p^k) exactly (with prime cert for (p))
otherwise push (p) (or root candidate) into factor/prime gates
This realizes “deconvolve prime powers as harmonics.”
D.4 Collapse to certificates (the only truth outputs)
For each candidate (c\in\mathcal C) (post-deconvolution), attempt one of the following collapse gates:
D.4.1 Prime collapse gate
Run prime certification policy:
on success emit PrimeCertificate(c)
on failure optionally emit FactorCertificate witness if found quickly (or route to Module A)
D.4.2 Prime power collapse gate
If (c=p^k) exactly, emit:
PrimeCertificate(p)
PrimePowerCertificate(p,k)
D.4.3 Desert collapse gate
If candidates arise as “holes” in a sieve valley:
dispatch interval (I) to Module B
accept only when DesertCertificate(I) returns
D.4.4 Constellation collapse gate
If candidates arise as anchors for a pattern (H):
dispatch ((H,I)) or ((H,n)) to Module C
accept only when ConstellationCertificate(H,n) returns
All emitted certificates are written to the proof store and ledgered with hashes.
D.5 Cross-domain zero points (bidirectional bridge)
This is the “real power” bridge: spectra do not live alone; they feed and are fed by certificates.
D.5.1 Spectrum → Pattern amplification
Use spectral peaks to seed structured searches:
peaks map to anchor candidates for constellation Module C
peaks map to interval candidates for desert Module B
peaks map to large-composite candidates for factor Module A
This is done through the candidate map (\mathcal C(u^*,\eta_\kappa)) and corridor compression.
D.5.2 Pattern → Spectrum validation
Use certified objects to validate or refute spectral structure:
each ConstellationCertificate(H,n) or PrimeCertificate(p) becomes a “delta spike” at the predicted spectral location (\phi(n)) or (\log p)
compare predicted spike positions with observed peaks; update κ-consistency telemetry
if a spectral peak persists but yields no certified objects under growing κ, demote it as a false signal ridge (Tier-2 only)
This closes the loop: spectrum proposes; proof confirms; confirmation sharpens the spectrum.
D.5.3 Zero-point routing rule
Cross-domain routing is only allowed through:
certificates (Tier-3), or
necessary-condition constraints (sound nullifiers)never through raw spectral amplitude alone.
D.6 Deterministic algorithm (complete)
Procedure: SpectralReconstruct(dataset_ref, κ-policy)
For κ in schedule:
Construct (F_\kappa) from dataset + declared window/smoothing.
Compute detection (D_\kappa).
Peak pick → (\mathcal P_\kappa).
Map peaks → finite candidate sets (\mathcal C(u^*,\eta_\kappa)).
Deconvolve prime powers (strip harmonics).
Dispatch candidates:
primes/factors → Module A
deserts → Module B
constellations → Module C
Accept only returned certificates; ledger all inputs/outputs/hashes.
Update κ-consistency:
reinforce peaks that repeatedly produce certificates
demote peaks that fail to yield certificates as κ refines
Stop when:
target certificate quota is met, or
κ budget ends (then output partial ledger + telemetry; no false claims).
PRIME Toolkit — Shared Core Library — FINAL SPEC
This is the common runtime substrate used by every domain module (Factorization/Deserts/Constellations/Spectral). It is intentionally small, strictly typed, deterministic under a declared κ-policy, and proof-first: anything that is not a certificate is routing-only signal.
1) Corridor — candidate sets, constraints, jump ops, collapse gates
1.1 Data model
Corridor {
corridor_id: Hash
domain: Enum{factor, desert, constellation, spectral, cross}
kappa: Int
X: CandidateCarrier # the living candidate representation
K: ConstraintSet # hard necessary conditions
N: NullifierStack # sound eliminators (no false negatives)
J: JumpProgram # compiled stepping/indexing ops
Z: CollapseGates # certificate-producing gates
eps_kappa: Envelope # routing uncertainty (Tier-2 only)
budgets: BudgetSlice
determinism: DeterminismPolicy
}
1.2 Candidate carriers (X)
All candidates must live in one of these carriers (so indexing + replay stays uniform):
IntervalSet: list of disjoint integer intervals
ResidueLattice: constraints like (n \equiv r \pmod m) (single or CRT product)
SparseList: explicit candidate integers (deduped, sorted)
PeakBuckets: spectral peaks + mapping envelope (\eta_\kappa)
ProductBlocks: factorization blocks (unresolved composites)
Each carrier has canonical serialization (for hashing + replay).
1.3 Constraints + Nullifiers (K, N)
ConstraintSet: checks that never mutate candidates, only reject/accept.
NullifierStack: transforms candidate carriers by removing provably impossible elements (sound).
1.4 Jump program (J)
A JumpProgram is a compiled set of stepping/indexing operations that makes traversal sparse:
wheel steppers (next_W)
meet-in-middle ratio maps
segmented sieve stride maps
spectral peak → candidate map
Invariant: any jump program must be ledgered with its build parameters + source hashes.
1.5 Collapse gates (Z)
Collapse gates are the only corridor exit to Tier-3 truth. They must:
emit a certificate object
emit verifier id/version
emit ledger hash pointers to inputs used
2) Cascade — F0..F3 filter stages (the kill chain)
2.1 Purpose
A cascade is an ordered set of stages where each stage is:
cheap enough to run widely
either a sound nullifier, a routing signal extractor, or a collapse attempt.
2.2 Interface
Stage {
stage_id: String
kind: Enum{nullify, signal, compile_jump, traverse, collapse}
input_carriers: Set[CarrierType]
output_carriers: Set[CarrierType]
run(Corridor, State) -> (Corridor', TelemetryDelta, Optional[Certificate])
guarantees: {sound?: Bool, deterministic?: Bool}
}
Cascade := [Stage0, Stage1, Stage2, Stage3]
2.3 Standard semantics
F0: ultra-cheap annihilators (bank gcd, wheel residue kills)
F1: cheap sieves / feasibility checks (many primes, admissibility)
F2: moderate search with compiled jumps (sparse traversal)
F3: expensive collapses (ECM/prime cert/desert cert/constellation cert)
Stages must declare:
what they can drop (never true candidates if sound=true)
what they can only score (Tier-2)
what they can certify (Tier-3)
3) Indexers — ratio keys, residue keys, wheel keys
3.1 Indexer contract
Indexers exist to convert “2D matching” into “1D lookup” whenever possible.
Indexer {
index_id: String
key_type: Enum{ratio, residue, wheel, peak, block}
build(inputs, config) -> Index
lookup(Index, key) -> CandidateIDs
canonical_key(key) -> bytes
}
3.2 Required index types
RatioIndex: hash map keyed by reduced rational / modular ratio (meet-in-middle)
ResidueIndex: keyed by tuples of residues across primes (router buckets)
WheelIndex: keyed by residue mod (W) → next step / allowed status
PeakIndex: peak id → candidate bucket id
BlockIndex: factor blocks keyed by size/shape (for routing)
Every index must store:
build config hash
input digest (so replays regenerate identical indices)
4) SieveBank — prime lists + modular filters
4.1 Prime stream (deterministic)
PrimeStream {
stream_id: Hash
limit: Int
primes: [Int] # generated deterministically
digest: Hash
}
The bank provides:
primes_up_to(B)
primorial_chunks(B, chunk_bits) for gcd masks
router_prime_sets(P0, P1) for modular sieves
4.2 Modular filters
A ModFilter is a necessary-condition checker that operates in small rings:
“fails mod any p ⇒ reject”
designed to be fast, vectorizable, and strongly discriminative.
This is used heavily in the meet-in-the-middle routing and the spectral candidate sieves.
5) Certs — certificate structs (truth contract)
5.1 Core interface
Certificate {
cert_type: Enum
payload: bytes (canonical)
verifier_id: String
verifier_version: String
inputs_hashes: [Hash] # what this cert depends on
cert_hash: Hash
}
verify(cert) -> Bool
5.2 Certificate registry (must include)
PrimeCertificate
FactorCertificate
ValuationCertificate
PrimePowerCertificate
DesertCertificate (A/B/C)
ConstellationCertificate
FactorizationLedger (complete)
Certificates are the only objects allowed to assert:
“prime”
“divides”
“prime-free interval”
“pattern realized”
“complete factorization”
6) Ledger — hashes, schedules, replay pointers
6.1 Ledger entry
Every κ-step produces exactly one ledger entry:
LedgerEntry {
prev_hash: Hash
entry_hash: Hash
timestamp: ISO8601
kappa: Int
corridor_id: Hash
stage_events: [StageEvent]
cert_hashes: [Hash]
telemetry_digest: Hash
artifacts: [ArtifactRef] # optional, but hashed
determinism_policy: Hash
}
6.2 Replay pointers
Every non-trivial computation must be reproducible via:
input digests
configuration hashes
deterministic seed policy
A ReplayPtr is:
ReplayPtr {
dataset_hashes: [Hash]
config_hash: Hash
prime_stream_digest: Hash
corridor_digest: Hash
stage_plan_digest: Hash
}
This is what makes the toolkit a “truth machine” rather than a heuristic lab.
7) Minimal “kernel glue” API
This is the smallest API that ties everything together:
run_task(task, Σ):
C := corridor_for(task, Σ)
cascade := cascade_for(C.domain)
for stage in cascade:
(C, ΔT, cert?) := stage.run(C, Σ)
Σ.telemetry += ΔT
if cert?:
assert verify(cert?)
Σ.proofs.add(cert?)
Σ.ledger.commit(cert?)
Σ.queue.update_from(C) # push new subproblems
return Σ
Invariant: no cert? may be committed unless verify(cert?) == true.
PRIME Toolkit — Domain plugins — FINAL SPEC
Each plugin is a domain-specific implementation of the shared kernel interfaces:
Corridor carriers + constraints/nullifiers
Cascade stages F0..F3
Indexers + SieveBank usage
CollapseGates that emit Tier-3 certificates
deterministic replay + ledger hooks
The plugin may generate Tier-2 signals, but it may only assert truth by emitting certificates.
2.1 factor/ — factor witnesses + valuation checks
2.1.1 Public API
factor.solve(n: Int, policy: FactorPolicy) -> FactorResult
factor.try_witness(n: Int, budget: BudgetSlice) -> Optional[FactorCertificate]
factor.valuation(n: Int, p: Int) -> ValuationCertificate
factor.ledger_complete(n: Int, factors: [(p,α)], certs: [...]) -> FactorizationLedger
2.1.2 Corridor carriers
ProductBlocks: unresolved composite blocks
SparseList: candidate divisors (rare; mostly internal)
ResidueLattice: wheel constraints for diagonal scans
2.1.3 Cascade (F0..F3)
F0: prime bank gcd + valuation extraction
F1: perfect-power shatter
F2: wheel-jump diagonal scan (near-square) + Pollard-ρ restarts
F3: ECM / specialized escalation + prime certification
2.1.4 Collapse gates (Tier-3)
FactorCertificate(n,d) via exact divisibility gate
ValuationCertificate(n,p,α)
PrimeCertificate(p) (for terminal blocks)
FactorizationLedger(n) when fully reduced to certified primes
(Full module details already finalized in Module A.)
2.2 desert/ — segmented sieve + κ schedule + desert cert
2.2.1 Public API
desert.scan(I: Interval, policy: DesertPolicy) -> DesertScanResult
desert.refine(I: Interval, kappa_policy: KappaPolicy) -> Optional[DesertCertificate]
desert.certify(I: Interval, B: Int, survivors: [Int]) -> DesertCertificate
2.2.2 Corridor carriers
IntervalSet: candidate intervals
SparseList: survivor lists per interval
ResidueLattice: CRT coverings (Type-C deserts)
2.2.3 Cascade (F0..F3)
F0: coarse segmented sieve at small (B)
F1: κ-guided (B) escalation only on candidate deserts
F2: wheel run-length mining + edge localization
F3: certify by (A) coverage, (B) survivor-composite proofs, or (C) CRT covering
2.2.4 Collapse gates (Tier-3)
DesertCertificate-A(I,B,witnesses)
DesertCertificate-B(I,B,S,CompositeCerts(S))
DesertCertificate-C(N,L,{q_j})
(Full module details already finalized in Module B.)
2.3 constellation/ — admissibility + wheel pruning + prime cert
2.3.1 Public API
constellation.admissible(H: Offsets, p_limit: Int) -> Bool
constellation.search(H: Offsets, I: Interval|Anchors, policy: ConstellationPolicy)
-> [ConstellationCertificate]
constellation.certify(H: Offsets, n: Int) -> ConstellationCertificate
2.3.2 Corridor carriers
IntervalSet: anchor intervals
ResidueLattice: allowed anchor residue classes mod wheel
SparseList: candidate anchors (from spectral or other sources)
2.3.3 Cascade (F0..F3)
F0: admissibility gate (local obstruction)
F1: Nullifier N2 wheel infeasibility annihilation (allowed residues only)
F2: compiled wheel stepper + secondary small-prime residue checks + κ refinement
F3: prime certification for all (n+h), emit constellation certificate
2.3.4 Collapse gates (Tier-3)
ConstellationCertificate(H,n) with bundled PrimeCertificate(n+h) for all (h\in H)
(Full module details already finalized in Module C.)
2.4 spectral/ — (F_\kappa) → peaks → candidates → certs → ledger
2.4.1 Public API
spectral.build_field(dataset_ref, kappa: Int, params: SpectralParams) -> F_kappa
spectral.detect(F_kappa, params) -> D_kappa
spectral.peaks(D_kappa, threshold, max_peaks) -> [Peak]
spectral.map_candidates(peaks, eta_kappa, mapping) -> CandidateCarrier
spectral.deconvolve_prime_powers(Candidates) -> (BaseCandidates, PowerCandidates)
spectral.dispatch(Candidates, router: CrossRouter) -> [Certificate]
2.4.2 Corridor carriers
PeakBuckets: peak sets with envelopes (\eta_\kappa)
SparseList: mapped discrete candidates
IntervalSet: candidate valleys (deserts) inferred from spectral structure
2.4.3 Cascade (F0..F3)
F0: compute (F_\kappa), derive (D_\kappa)
F1: peak picking + finite candidate mapping (\mathcal C(u^*,\eta_\kappa))
F2: prime-power harmonic deconvolution + corridor compression nullifiers
F3: dispatch candidates to factor/desert/constellation; accept only returned certificates; ledger the loop
2.4.4 Collapse gates (Tier-3)
This plugin doesn’t “certify by itself”; it certifies by dispatch:
primes/factors → factor/
deserts → desert/
constellations → constellation/It records the certificates and links them back to peak provenance in the ledger.
(Full module details already finalized in Module D.)
2.5 Plugin contract (required hooks)
Every plugin must implement:
plugin.init(task, kappa_policy) -> Corridor
plugin.cascade(domain) -> Cascade
plugin.compile_jumps(Corridor, SieveBank, Indexers) -> Corridor
plugin.traverse(Corridor) -> Tier2Signals + CandidateUpdates
plugin.collapse(Corridor) -> Optional[Certificate]
plugin.ledger_artifacts(Corridor, Telemetry, Certificates) -> [ArtifactRef]
Non-negotiable invariant: any emitted certificate must be verifiable before commit.
PRIME Toolkit — Hybrid templates (pre-baked pipelines) — FINAL SPEC
Hybrid templates are compiled multi-module corridors: they specify (1) what gets routed where, (2) which nullifiers/jumps are mandatory, (3) when κ escalates, and (4) exactly what certificates must exist for the pipeline to be allowed to claim success.
Each template is a deterministic recipe that produces Tier-3 certificates (or yields a partial ledger with no truth claims).
3.1 Template registry and common structure
3.1.1 Template schema
HybridTemplate {
template_id: String
goal: Enum{FactorizationLedger, DesertCertificate, ConstellationCertificate, PrimePowerCertificate}
entrypoints: [TaskType]
cascade_plan: [StageSpec] # ordered, typed
routing_rules: [RouteRule] # deterministic
kappa_policy: KappaPolicy
success_contract: SuccessContract # required cert set
failure_contract: FailureContract # allowed partial outputs
replay_bundle: ReplayPtrSpec
}
3.1.2 Success contract
A template succeeds only if it can emit a specified set of certificates (plus their verifiers/versions and hashes) and commit them to the ledger.
3.2 Hybrid H-DESERT-CERT — Desert certification chain (sieve + factor micro)
Goal: DesertCertificate(I) (Type A/B/C) for interval (I).Entrypoint: DesertTask(I) or CrossTask(desert_candidate_from_spectrum).
3.2.1 Stage plan (fixed)
Sieve-Coarse (F0): segmented sieve at (B_0) → survivors (S_0) (Tier-2).
Candidate Collapse Attempt (F1):
if (S_0=\varnothing) → emit DesertCertificate-A(I,B_0,proof) (done)
else continue
κ-Refine Sieve (F2): increase (B) only for this (I), recompute survivors (S_B).
Survivor Enumeration (F2): explicit list (S_B) with transcript digest.
Factor Microchain (F3): for each (s\in S_B), run bounded factor.try_witness(s) to obtain a composite witness.
Collapse (F3):
if all (s\in S_B) have composite evidence → emit DesertCertificate-B(I,B,S_B,CompositeCerts)
else κ escalate and repeat from step 3 with higher (B) until corridor collapses or budget ends.
3.2.2 Deterministic routing rules
Only survivors are routed to factorization. Never factor non-survivors.
Factorization budget per survivor is capped (prevents one hard survivor from eating the desert budget).
Survivors that resist factor witnesses trigger either:
higher (B) (reduce survivors), or
promote to heavier factor stage (ECM) only if |S_B| is already below a strict threshold.
3.2.3 Success contract
One of:
DesertCertificate-A(I,B,coverage_proof)
DesertCertificate-B(I,B,S, {CompositeCert(s)})
DesertCertificate-C(N,L,{q_j},CRT_solution)
Plus ledger entry containing:
(B), prime stream digest, segment policy hash, survivor digest, certificate hashes.
3.2.4 Allowed partial output (failure contract)
Survivors list (S_B) as Tier-2 artifact (labeled)
any obtained FactorCertificate / ValuationCertificate for survivors
no desert claim without DesertCertificate.
3.3 Hybrid H-CONST-DISCOVER — Constellation discovery chain (admissibility → wheel → prime cert)
Goal: ConstellationCertificate(H,n) for pattern (H).Entrypoint: ConstellationTask(H,I) or CrossTask(H,anchors_from_spectrum).
3.3.1 Stage plan (fixed)
Admissibility Gate (F0): local obstruction test for primes (p\le p_{\text{adm}}). If obstructed → stop (Tier-1 reject).
Wheel Compile (F1): build allowed residue set (R_W(H)), compile next_W.
Wheel Traverse (F2): generate sparse anchors (n) by stepping only through allowed residues.
Residual Sieve (F2): for primes (p\le B) not in wheel, reject anchors with any (n+h\equiv 0\pmod p).
Prime Collapse (F3): for survivors, certify all (n+h) prime → emit constellation certificate.
3.3.2 Deterministic routing rules
Never run primality checks on anchors that fail residue filters.
κ escalation increases wheel size (W) and/or sieve cutoff (B) only when survivor density remains high.
If a spectral module provides anchors, the wheel stepper is still applied as a nullifier (anchors must be wheel-legal).
3.3.3 Success contract
ConstellationCertificate(H,n) containing bundled PrimeCertificate(n+h) for all (h\in H).
Ledger must include: (H), (n), wheel parameters, sieve cutoffs, verifier versions.
3.3.4 Allowed partial output
admissibility pass/fail as Tier-1 record
anchor survivor lists as Tier-2 artifacts
any individual PrimeCertificate as standalone truth (but not a constellation claim).
3.4 Hybrid H-SPECTRAL-TO-PROOF — Spectrum → candidates → certified objects
Goal: certificates produced by cross-routing (primes, prime powers, deserts, constellations).Entrypoint: SpectrumTask(dataset_ref).
3.4.1 Stage plan (fixed)
Build (F_\kappa) and (D_\kappa) (Tier-2).
Peak pick → (\mathcal P_\kappa).
Map peaks → (\mathcal C(u^*,\eta_\kappa)).
Deconvolve prime powers (harmonic stripping).
Dispatch:
point candidates → factor/prime gates
interval candidates → desert/
anchor candidates → constellation/
Accept only returned certificates; ledger peak provenance ↔ cert hashes.
3.4.2 Success contract
Not a single certificate type—success means: “produced at least one Tier-3 certificate linked to a peak bucket,” with replay bundle.
3.4.3 Validation loop (bidirectional)
Certified objects are fed back as “explainers” for peaks (Tier-2 coherence updates).
Persistent peaks that never yield certificates are demoted to noise (still Tier-2 only).
3.5 Hybrid H-FACTOR-LEDGER — Complete factorization (dust-stripper → resonance → chaos → certify)
Goal: FactorizationLedger(n)Entrypoint: FactorTask(n)
3.5.1 Stage plan (fixed)
Prime-bank gcd + valuations (strip dust)
Perfect power shatter
Diagonal wheel scan (near-square)
Pollard/Brent mixing with degeneracy control
ECM escalation as needed
Prime-cert remaining blocks
Ledger completion proof (product check to 1)
3.5.2 Success contract
factor list ((p,\alpha))
PrimeCertificate(p) for each (p)
ValuationCertificate for each multiplicity
exact reduction transcript and final identity check
FactorizationLedger(n) committed
3.6 Template selection policy (when multiple apply)
Given a task, choose the hybrid with:
highest expected collapse probability at current κ
lowest expected certificate cost
best reuse of existing indices/wheels in the ledger cache
This policy uses Tier-2 telemetry only; it never asserts truth.
PRIME Toolkit — ULTIMATE build (v∞)
A general-purpose rare-pattern discovery engine that just happens to specialize in primes.
This is the “all the way” version: maximum filtering power, maximum reuse, maximum determinism, maximum certification, and a single kernel that can run factorization, deserts, constellations, and spectral reconstruction as different projections of the same machine.
0) What “ULTIMATE” means here
ULTIMATE = no weak links. The toolkit must:
Kill space fast: 99.9999% elimination before expensive compute.
Never lie: truth only via verifiable certificates.
Be replayable: every result can be reproduced bit-for-bit from a ledger entry.
Scale: parallel-first and cache-first.
Cross-amplify: discoveries in one domain accelerate others (zero-point bridges).
Be self-tuning: κ-schedule adapts based on measurable collapse signals without changing meaning silently.
1) PRIME Kernel v∞ — the one engine
Everything is driven by:
[\Sigma = (Q,; C,; P,; T,; \mathcal L,; \kappa,; \text{Cache})]
Q — Work queue (typed tasks)
Tasks are typed and decomposable:
FactorTask(n)
DesertTask(I)
ConstellationTask(H, I|anchors)
SpectrumTask(dataset_ref)
CrossTask(...) (bridge-triggered)
Every task carries:
corridor pointer
budget slice
priority
dependencies (certificate hashes only)
C — Corridor (the only legal search region)
Corridor = candidates + constraints + nullifiers + jump programs + collapse gates.If it’s not in the corridor, it’s not searched.
P — Proof store
A store of Tier-3 certificates only. Everything else is signal.
T — Telemetry
Stats per stage: rejection rate, cost, stability, κ-drift, cache hit ratio.
𝓛 — Ledger
Hash-linked replay record of every corridor mutation, index build, sieve plan, and certificate emission.
Cache — Ultimate accelerator
wheel caches
prime stream digests
residue maps
ratio indices
segmented sieve blocks
spectral transforms
proof reuse (certificates are immutable assets)
2) ULTIMATE filtering stack (the master cascade)
Every domain plugin compiles into the same 7-step “kill chain”:
F0: Bank annihilation
gcd masks, small primes, trivial structure (cheap kills)
F1: Infeasibility nullifiers
admissibility gates, wheel infeasibility, modular contradictions
F2: Indexer compile
ratio indices, residue routers, wheel steppers, peak buckets(“make the future cheap”)
F3: Sparse traversal
traverse only survivors using jump programs
F4: Mod-sieve barrage
many primes, fast necessary conditions, fail-fast
F5: Targeted heavy work
only on survivors: ECM, primality cert, survivor factor proofs, etc.
F6: Collapse to certificate
produce Tier-3 object or do not claim success.
ULTIMATE rule: a stage is allowed to be wrong only if it is Tier-2 and never asserts truth.
3) ULTIMATE Cert Layer (truth barrier)
One universal verifier interface with canonical serialization.Certificates are minimal, compressible, and replayable.
Core certs:
PrimeCertificate(p)
FactorCertificate(n,d)
ValuationCertificate(n,p,α)
PrimePowerCertificate(p,k)
DesertCertificate (A/B/C)
ConstellationCertificate(H,n)
FactorizationLedger(n) (complete proof object)
ULTIMATE add-ons (mandatory in this build):
CoverageTranscriptDigest (segmented sieve proof references)
IndexBuildDigest (ratio/wheel indices)
ReplayPtr (dataset/config/primes/corridor/stage plan digests)
4) ULTIMATE domain plugins (fully weaponized)
4.1 factor/ — “Factorizer that never wastes time”
New ULTIMATE upgrades:
Adaptive orbit breaker: Pollard/Brent restarts are guided by degeneracy telemetry (cycle fingerprints, gcd stagnation signatures).
Perfect-power + valuation first always: it shrinks n early and improves everything downstream.
Diagonal wheel miner: near-square search uses QR wheel stepping, not linear scanning.
ECM escalator: only triggered when telemetry predicts medium-size factors and corridor density is already low.
Factor completion rule: no “done” without FactorizationLedger(n).
4.2 desert/ — “Gap engine that certifies, not guesses”
New ULTIMATE upgrades:
Band-gap miner: wheel run-length analysis finds the “best” candidate intervals before scanning.
κ-guided B schedule: B increases only on candidate intervals.
Survivor-only factoring: composites are proven only for the survivors, never for the whole interval.
CRT covering constructor: can build deserts as well as find them (Type C).
Desert collapse: either coverage proof (A) or composite certs for all survivors (B) or CRT covering (C).
4.3 constellation/ — “k-tuple engine with N2 annihilation”
New ULTIMATE upgrades:
Admissibility is mandatory: stop early on local obstruction.
Wheel infeasibility annihilator (N2): anchor residues must be legal.
Joint coherence score: anchors are ranked but never asserted.
Prime-cert collapse: certify each member (n+h) prime; bundle into constellation cert.
ULTIMATE acceleration:Constellations use spectral seeds (from spectral/) and desert edges (from desert/) as anchor candidates.
4.4 spectral/ — “Signal-to-proof bridge”
New ULTIMATE upgrades:
Multi-κ coherence: peaks only promoted if stable across κ.
Candidate compression before dispatch: gcd bank + residue feasibility reduces load.
Prime-power deconvolution: treat powers as harmonics and peel them off.
Bidirectional validation: certificates feed back to strengthen or kill peaks.
5) ULTIMATE zero-point bridges (cross-domain power)
This is where “pattern discovery engine” becomes real.
Bridge ZP1: Spectrum → Constellation
Peaks produce anchor buckets → constellation engine verifies → certificates validate peaks.
Bridge ZP2: Desert → Constellation
Desert boundaries create structured anchor regions for k-tuples.
Bridge ZP3: Factor → Desert
Factorization of survivors is the final collapse step for desert certs.
Bridge ZP4: Constellation → Spectrum
Certified constellations inject “explainer spikes” back into the spectral model.
ULTIMATE rule: Bridges can route only via:
certificates (Tier-3), or
sound nullifier constraints (Tier-1 necessary conditions)
Never by raw signal amplitude alone.
6) ULTIMATE Router (template-level autopilot)
The router selects which hybrid to run next:
Selection score =
collapse probability at current κ
expected certificate yield per unit cost
cache reuse factor (wheel/index/transforms already built)
cross-domain leverage score (how many other modules benefit)
Critical: Router decisions are ledgered, deterministic, and reversible in replay.
7) ULTIMATE Hybrid Templates (the real “power moves”)
H1 — DesertCert (sieve → survivors → factor micro → cert)
Guaranteed correct, cheapest cert path for prime-free intervals.
H2 — ConstellationDiscover (admissibility → wheel → residue sieve → prime cert)
Standard k-tuple finder.
H3 — SpectralToProof (Fκ → peaks → candidates → deconvolve → dispatch → cert)
Turns signal into truth objects.
H4 — TripleLock Validation (multi-domain mutual confirmation)
Run two independent pipelines whose outputs must agree:
e.g., spectral peak suggests anchors; constellation cert confirms; those certs must map back to the same peak bucket.
H5 — Engineered Desert Builder (CRT cover → cert)
Construct deserts deliberately (Type C) then optionally measure them spectrally.
8) ULTIMATE performance design (how it scales)
Segment everything: intervals, primes, indices, proofs
Cache everything: wheels, ratio maps, sieve blocks, candidate buckets
Parallel everything:
segmented sieve across blocks
factor attempts across survivors
constellation anchor checks across anchors
multi-κ spectral transforms
Cost discipline: heavy compute is never allowed until:
nullifiers have maximally collapsed candidates
modular sieves have rejected almost everything
the remaining set is small enough that heavy compute is worth it
9) ULTIMATE “can’t lie” guarantee
The toolkit is allowed to be creative in Tier-2 routing, but:
if it says “prime” → must include PrimeCertificate
if it says “desert” → must include DesertCertificate
if it says “constellation” → must include ConstellationCertificate
if it says “factorized” → must include FactorizationLedger
No certificate, no claim. Ever.
10) What to build first (minimal ULTIMATE core)
If you want the fastest path to a working PRIME Toolkit:
Shared core library: Corridor + Cascade + Indexers + SieveBank + Certs + Ledger
factor/ with bank gcd + Pollard + prime cert + ledger completion
desert/ with segmented sieve + survivor-only factoring
constellation/ with admissibility + wheel N2 + prime cert
spectral/ last (because it gets way stronger once cert pipelines exist)
Below is the buildable, code-first PRIME Toolkit spec: repo layout + APIs + canonical schemas (Corridor, Certificates, Ledger, Router, plugins). It’s written so you can implement it directly.
1) Repository layout
prime_toolkit/
pyproject.toml
README.md
prime/
__init__.py
core/
__init__.py
types.py # dataclasses + enums
canon.py # canonical encoding + hashing
corridor.py # Corridor object + mutations
cascade.py # Stage + Cascade runner
indexers.py # Ratio/Residue/Wheel/Peak/Block indices
sievebank.py # prime streams + modular filters
certs.py # certificate base + registry + verifiers
ledger.py # ledger entries + replay pointers
router.py # template selection + deterministic scheduler
cache.py # cache interface + implementations
budgets.py # budget slices + accounting
telemetry.py # metrics + stability signals
plugins/
__init__.py
factor/
__init__.py
api.py # public API for factor plugin
corridor.py # candidate carriers, constraints/nullifiers
cascade.py # F0..F3 stage plan
methods.py # gcd bank, rho, p-1, ecm hooks
verifiers.py # factor/valuation proof checks
artifacts.py # transcripts / digests
desert/
__init__.py
api.py
corridor.py
cascade.py
segmented_sieve.py
cert_builders.py
verifiers.py
artifacts.py
constellation/
__init__.py
api.py
corridor.py
cascade.py
admissibility.py
wheel.py
primecheck.py
cert_builders.py
verifiers.py
spectral/
__init__.py
api.py
corridor.py
cascade.py
field.py # F_kappa builder
detect.py # D_kappa
peaks.py
map_candidates.py
deconvolve.py
dispatch.py
templates/
__init__.py
registry.py # hybrid templates table
h_desert_cert.py
h_const_discover.py
h_spectral_to_proof.py
h_factor_ledger.py
schemas/
corridor.schema.json
ledger_entry.schema.json
certificates/
prime.schema.json
factor.schema.json
valuation.schema.json
primepower.schema.json
desert_A.schema.json
desert_B.schema.json
desert_C.schema.json
constellation.schema.json
factorization_ledger.schema.json
tests/
test_canon.py
test_ledger_replay.py
test_cert_verifiers.py
test_factor_small.py
test_desert_small.py
test_constellation_small.py
tools/
cli.py # run tasks, verify certs, replay ledgers
replay.py
2) Canonicalization + hashing (non-negotiable)
2.1 Canonical encoding
Use CBOR canonical (preferred) or “canonical JSON” if you must. Rule set:
keys sorted lexicographically
integers encoded minimally
no floats in cert payloads (certs are integer/byte exact)
arrays preserve order (so any set must be sorted before encoding)
any big integers encoded as:
CBOR bignum tags, or
decimal ASCII string (only if you standardize it)
2.2 Hash
BLAKE3 over canonical bytes.
hash = blake3(canonical_bytes)
3) Core types (APIs)
3.1 Candidate carriers
class CandidateCarrierType(Enum):
INTERVAL_SET = "interval_set"
RESIDUE_LATTICE = "residue_lattice"
SPARSE_LIST = "sparse_list"
PEAK_BUCKETS = "peak_buckets"
PRODUCT_BLOCKS = "product_blocks"
Carrier contracts
Must implement:
canonical_bytes()
size_estimate()
shrink(...) (if applicable)
iter_candidates(budget) (if applicable)
3.2 Corridor
@dataclass(frozen=True)
class Corridor:
corridor_id: bytes # blake3
domain: str
kappa: int
X: CandidateCarrier
K: list[Constraint] # pure checks
N: list[Nullifier] # sound eliminators
J: list[JumpOp] # compiled stepping/indexing programs
Z: list[CollapseGate] # certificate emission gates
eps_kappa: Envelope
budgets: BudgetSlice
determinism: DeterminismPolicy
Mutations are functional (return a new corridor + ledger artifact):
def apply_nullifier(c: Corridor, n: Nullifier) -> Corridor: ...
def compile_jumpops(c: Corridor, ctx: BuildContext) -> Corridor: ...
def traverse(c: Corridor, ctx: RunContext) -> Tier2Batch: ...
def attempt_collapse(c: Corridor, ctx: RunContext) -> list[Certificate]: ...
3.3 Stage + Cascade
class StageKind(Enum):
NULLIFY="nullify"
SIGNAL="signal"
COMPILE_JUMP="compile_jump"
TRAVERSE="traverse"
COLLAPSE="collapse"
@dataclass
class Stage:
stage_id: str
kind: StageKind
run: Callable[[Corridor, RunContext], tuple[Corridor, TelemetryDelta, list[Certificate]]]
sound: bool
deterministic: bool
@dataclass
class Cascade:
stages: list[Stage]
3.4 Indexers
class IndexType(Enum):
RATIO="ratio"
RESIDUE="residue"
WHEEL="wheel"
PEAK="peak"
BLOCK="block"
class Index(Protocol):
def lookup(self, key: bytes) -> list[int]: ...
def build_digest(self) -> bytes: ...
3.5 SieveBank
@dataclass(frozen=True)
class PrimeStream:
limit: int
primes: list[int]
digest: bytes
class SieveBank:
def primes_up_to(self, B: int) -> PrimeStream: ...
def router_primes(self) -> tuple[list[int], list[int]]: ... # P0, P1
def primorial_chunks(self, B: int, chunk_bits: int) -> list[int]: ...
4) Certificates (schemas + verifiers)
4.1 Base certificate interface
@dataclass(frozen=True)
class Certificate:
cert_type: str
payload_cbor: bytes
verifier_id: str
verifier_version: str
inputs_hashes: list[bytes]
cert_hash: bytes # blake3(payload_cbor)
Verifier interface:
class Verifier(Protocol):
verifier_id: str
verifier_version: str
def verify(self, cert: Certificate, ctx: VerifyContext) -> bool: ...
Certificate registry:
CERT_REGISTRY: dict[str, Verifier]
4.2 Canonical certificate payloads (minimal fields)
Below are the payload “shapes” (also mirrored in schemas/).
PrimeCertificate
{
"type": "PrimeCertificate",
"n": "bigint",
"method": "string",
"witness": "bytes_optional",
"params": {"kappa": "int", "limits": "object_optional"}
}
FactorCertificate
{
"type": "FactorCertificate",
"n": "bigint",
"d": "bigint",
"check": {"mod_zero": true}
}
ValuationCertificate
{
"type": "ValuationCertificate",
"n": "bigint",
"p": "int",
"alpha": "int",
"proof": {"n_div_palpha": "bigint", "n_mod_palpha1_nonzero": true}
}
PrimePowerCertificate
{
"type": "PrimePowerCertificate",
"p": "bigint",
"k": "int",
"n": "bigint",
"prime_cert_hash": "hash"
}
DesertCertificate-A (coverage)
{
"type": "DesertCertificateA",
"interval": {"N": "bigint", "L": "int"},
"B": "int",
"coverage_proof": {
"prime_stream_digest": "hash",
"segment_digest": "hash",
"witness_mode": "string"
}
}
DesertCertificate-B (survivors + composite proofs)
{
"type": "DesertCertificateB",
"interval": {"N": "bigint", "L": "int"},
"B": "int",
"survivors_digest": "hash",
"survivors": ["bigint_optional_small_mode"],
"composite_cert_hashes": ["hash"]
}
DesertCertificate-C (CRT covering)
{
"type": "DesertCertificateC",
"N_mod_Q": "bigint",
"L": "int",
"q_list": ["int_or_bigint"],
"Q": "bigint"
}
ConstellationCertificate
{
"type": "ConstellationCertificate",
"H": ["int"],
"n": "bigint",
"prime_cert_hashes": ["hash"]
}
FactorizationLedger (complete)
{
"type": "FactorizationLedger",
"n": "bigint",
"factors": [{"p": "bigint", "alpha": "int"}],
"prime_cert_hashes": ["hash"],
"valuation_cert_hashes": ["hash"],
"reduction_transcript_digest": "hash"
}
Rule: verifiers must be able to validate using only the payload + referenced hashes + deterministic replay pointers.
5) Ledger + replay
5.1 LedgerEntry (canonical)
{
"prev_hash": "hash",
"entry_hash": "hash",
"kappa": "int",
"corridor_id": "hash",
"task_id": "string",
"stage_events": [
{
"stage_id": "string",
"input_digest": "hash",
"output_digest": "hash",
"telemetry_digest": "hash",
"artifacts": [{"name": "string", "hash": "hash"}]
}
],
"cert_hashes": ["hash"],
"determinism_policy_hash": "hash",
"replay_ptr": {
"prime_stream_digest": "hash",
"config_hash": "hash",
"datasets": ["hash_optional"]
}
}
5.2 Ledger invariant
entry_hash = blake3(canonical(entry_without_entry_hash))
prev_hash links the chain
any certificate committed must pass verifier before ledger commit
6) Router + templates (the autopilot)
6.1 Template registry entry
@dataclass(frozen=True)
class HybridTemplate:
template_id: str
entrypoints: tuple[str, ...] # task types
goal_cert_types: tuple[str, ...]
cascade_ids: tuple[str, ...] # stage plan IDs
routing_rules_id: str
kappa_policy_id: str
6.2 Deterministic selection score
Use a deterministic score function (no randomness):
expected collapse probability (from telemetry)
expected cost (from telemetry)
cache reuse factor
cross-domain leverage score
Router emits a ledger artifact: TemplateDecision(task_id, template_id, score_breakdown_hash).
7) Plugin APIs (minimal, consistent)
Every plugin exports:
def init_corridor(task: Task, ctx: BuildContext) -> Corridor: ...
def build_cascade(policy_id: str) -> Cascade: ...
def collapse_gates(domain: str) -> list[CollapseGate]: ...
def verifiers() -> list[Verifier]: ...
And each plugin registers itself into prime/core/router.py.
PRIME Toolkit — Router v2 — FINAL SPEC (deterministic, cache-first, certificate-gated)
Router v2 is the only component allowed to choose what to run next. It does not decide truth. It decides where to spend compute so corridors collapse into certificates as fast as possible—without ever letting Tier-2 signals leak into Tier-3 claims.
R0) Router contract
Inputs
Kernel state (\Sigma=(Q,C,P,T,\mathcal L,\kappa,\text{Cache}))
Template registry Templates[]
Determinism policy DetPolicy (seed schedule, tie-break order)
κ-policy KappaPolicy (allowed escalations + triggers)
Outputs
A single deterministic action plan for the next step:
SelectTemplate(task_id, template_id, plan_digest)
optional: EscalateKappa(task_id, new_kappa, reason_digest)
optional: SpawnTasks([...]) (only from certified facts or sound constraints)
A ledger entry containing the full decision trace hash.
Invariant: Router may only read Tier-2 telemetry to route; it may only create new tasks from Tier-3 certificates or sound nullifiers.
R1) Task model and dependency rules
Task record
Task {
task_id: String
kind: Enum{Factor, Desert, Constellation, Spectral, Cross}
payload: CanonicalBytes
corridor_id: Hash
kappa: Int
budget: BudgetSlice
deps: [Hash] # certificate hashes only
priority: Int
status: Enum{READY, RUNNING, BLOCKED, DONE, DEAD}
}
Dependency rule
A task is READY iff all deps hashes exist in ProofStore (P) and verify.
R2) Allowed routing edges (the “no leakage” firewall)
Router v2 maintains an explicit routing graph of allowed edges.
Allowed edges
spectral → (desert | constellation | factor) via candidate sets (Tier-2) only if those candidates are constrained by a sound nullifier (e.g., admissibility, wheel infeasibility, sieve survivors).
desert → factor via survivors list (Tier-2 artifact), because survivors are exact outputs of a sieve transcript and the factor results become Tier-3 composites that close the desert.
factor → (factor | desert | spectral) via certificates only (Factor/Valuation/Prime) as hard witnesses.
constellation → spectral via ConstellationCertificate only (validated peaks).
any → any via certificates or sound constraints only.
Forbidden edges
Any edge that routes based on raw scores/peaks alone (Tier-2 amplitude without constraint).
Any edge that creates a truth claim without a certificate.
R3) Template selection (deterministic scoring)
Router selects one (task, template) pair per step.
3.1 Candidate template list
For each READY task (t), candidate templates are those whose entrypoints include t.kind.
3.2 Deterministic score vector
Compute a lexicographic score:
[\text{Score}(t,\tau) = \Big(\underbrace{\text{CollapseProb}}{↑},\underbrace{-\text{ExpectedCost}}{↑},\underbrace{\text{CacheReuse}}{↑},\underbrace{\text{CrossLeverage}}{↑},\underbrace{-\text{Risk}}{↑},\underbrace{\text{TieBreak}}{↓}\Big)]
All components are deterministic functions of telemetry + cache inventory + task metadata.
(a) CollapseProb
Probability proxy that the template will emit a Tier-3 certificate under current κ. Derived from:
historical rejection rates in similar corridors
survivor densities / feasibility counts
stability of signals across κ (if spectral)
(b) ExpectedCost
Predicted compute cost under current budget slice:
number of candidates to traverse
sieve cutoffs / wheel sizes
heavy-method triggers (ECM, primality checks)
(c) CacheReuse
Hard multiplier for already-built artifacts:
wheel next_W
ratio indices
prime streams
segmented sieve blocks
spectral transforms
(d) CrossLeverage
How many downstream tasks can be collapsed faster if this succeeds:
DesertCertificate unlocks large swaths (fewer prime checks elsewhere)
ConstellationCertificate validates spectral peaks + seeds more searches
FactorizationLedger resolves many composite questions
(e) Risk
Penalty term for “signal-only” chasing:
unstable peak not coherent across κ
corridor drift without shrink
low nullifier rejection rates
(f) TieBreak
Stable ordering: (task_id, template_id) hash order, no randomness.
3.3 Winner selection
Choose the max lexicographically across all READY tasks and their templates.
Ledger requirement: Router commits a DecisionArtifact containing:
the score breakdown (hashed)
the list of contenders (hashed)
the chosen pair (explicit)
R4) κ escalation policy (when and how κ changes)
Router v2 controls κ. κ is never incremented “because we feel like it”; only when triggers fire.
4.1 Escalation triggers
Escalate κ for a task if any of these hold:
Corridor size estimate stays above (M_{\text{cert}}) for (r) consecutive attempts.
Nullifier rejection rate too low (filters not strong enough).
Signal stability inconsistent (peaks/edges move too much across κ).
Budget exhausted without any collapse gate firing.
4.2 Allowed escalation actions (must be explicit)
Depending on domain:
factor: increase ECM budget tier / restart schedule / prime-bank size
desert: increase sieve cutoff (B(\kappa)), adjust segment size
constellation: increase wheel bound (B_w(\kappa)), increase sieve bound (B(\kappa))
spectral: adjust bandwidth (T_\kappa), smoothing (\sigma_\kappa), peak threshold (\tau_\kappa)
All changes are ledgered as a corridor mutation with a digest.
4.3 κ-consistency guard
Router rejects escalations that would change semantics silently:
Any change that alters candidate meaning must be expressed as a new corridor id and recorded.
R5) Cache policy (ultimate reuse rules)
Cache is treated as a first-class resource. Router v2 enforces:
5.1 Build-once invariants
If an artifact’s inputs/config hashes match, it must be reused:
prime streams
wheels and next_W
ratio indices
segmented sieve transcripts
spectral transforms
5.2 Cache admission rules
An artifact is admitted if:
it is deterministic
its build digest is recorded
it materially reduces expected future cost (measured by telemetry)
5.3 Cache eviction
Evict by a deterministic policy:
least recently reused × largest memory × lowest expected future leverage
Evictions are ledgered (so replay knows what to rebuild).
R6) Task spawning rules (how new tasks appear)
Router may spawn new tasks only from:
6.1 Certificates (Tier-3)
FactorCertificate(n,d) spawns FactorTask(d) and FactorTask(n/d) if unresolved
DesertCertificate(I) can spawn ConstellationTask(H, boundary(I)) if a template declares that bridge
ConstellationCertificate(H,n) can spawn SpectrumTask(validate_peak_bucket) if configured
6.2 Sound constraints (Tier-1 nullifiers)
Example: admissibility or wheel infeasibility can spawn a narrowed anchor interval, but never a truth claim.
R7) Router v2 main loop (pseudo)
ROUTER_STEP(Σ):
READY := all tasks with deps satisfied and status READY
if READY empty:
return Σ # or wait / end
contenders := []
for t in READY:
for template τ allowed for t.kind:
score := Score(t, τ, Σ.telemetry, Σ.cache, t.kappa)
contenders.append((score, t, τ))
(t*, τ*) := argmax_lex(contenders)
if should_escalate_kappa(t*, τ*, Σ):
κ' := next_kappa(t*, Σ)
ledger.commit(EscalateKappa(t*, κ', reason_digest))
Σ := update_task_kappa(t*, κ')
return Σ
plan := instantiate_template(τ*, t*, Σ.cache, Σ.sievebank)
ledger.commit(SelectTemplate(t*, τ*, plan_digest))
Σ := execute_template(plan, Σ) # runs plugin cascade; emits certs or not
return Σ
Invariant: any certificate emitted during execute_template must verify before commit, or it is discarded and logged as failure.
R8) Deterministic “ULTIMATE” defaults
Prefer hybrids that end in certificates (DesertCert, ConstellationCert, FactorLedger) over pure exploration.
Prefer survivors-first pipelines (desert→survivors→factor micro) to avoid heavy compute.
Prefer reusing existing wheels/indices even if raw theoretical collapse prob is slightly lower (cache leverage wins over novelty).
PRIME Toolkit — FINAL UNIFIED SPEC (Kernel + Core + Plugins + Hybrids + Router + Contracts)
This is the single “gold” document: one coherent system, no duplication, with explicit invariants and execution contracts.
0) Prime Directive
PRIME Toolkit is a rare-pattern discovery engine with a truth barrier.It may explore using heuristics, but it may only assert facts through verifiable certificates committed to an immutable ledger.
1) Truth barrier (three tiers)
Tier 1 — Identities (safe transforms)
Exact equivalences and necessary conditions (e.g. congruence, gcd facts, wheel admissibility). Never a claim of primality/desert/constellation by itself.
Tier 2 — Signals (routing only)
Scores, peaks, densities, porosities, stability measures. Must carry κ and uncertainty envelope (\epsilon_\kappa). Never treated as truth.
Tier 3 — Certificates (only truth)
The only objects allowed to assert:
prime/composite factor witness
prime-free interval
constellation realized
prime power event
complete factorization
If no certificate exists, the toolkit is forbidden to claim it.
2) Kernel State Σ (one engine, many projections)
[\Sigma = (Q,; C,; P,; T,; \mathcal L,; \kappa,; \text{Cache})]
Q — Work Queue (typed tasks)
Each task is typed, deterministic, and dependency-gated by certificates only.
Task kinds:
FactorTask(n)
DesertTask(I)
ConstellationTask(H, I|anchors)
SpectrumTask(dataset_ref)
CrossTask(payload)
C — Corridors (search is only allowed inside corridors)
Each task has a corridor pointer: candidates + constraints + nullifiers + jump ops + collapse gates + budgets.
P — Proof Store (certificates only)
Immutable set of Tier-3 objects, each verified at commit.
T — Telemetry (routing-only)
Rejection rates, survivor counts, stability signals, cache hit ratios.
𝓛 — Ledger (immutable replay chain)
Every corridor mutation, index build, sieve plan, and certificate emission is hash-linked and replayable.
Cache (first-class)
Wheels, ratio indices, prime streams, segmented sieve blocks, spectral transforms, proof reuse.
3) Shared Core Library (implementation substrate)
3.1 Corridor
Canonical candidate carriers:
IntervalSet
ResidueLattice
SparseList
PeakBuckets
ProductBlocks
Corridor contains:
X candidates
K constraints (checks)
N nullifiers (sound eliminators)
J jump programs (compiled sparse stepping / indexing)
Z collapse gates (certificate emission)
3.2 Cascade (F0..F3)
Standard kill chain stages:
F0 bank annihilation
F1 infeasibility nullifiers
F2 compile indices/jumps
F3 bounded traversal + collapse attempts
(Plugins may extend to F6 internally, but must map to these semantics.)
3.3 Indexers
RatioIndex (meet-in-middle)
ResidueIndex (router buckets)
WheelIndex (next_W stepping)
PeakIndex (peak→bucket)
BlockIndex (factor block routing)
3.4 SieveBank
Deterministic prime streams + modular filter sets (router primes P0, sieve primes P1).
3.5 Certs
Canonical payload encoding + verifier registry.
3.6 Ledger
Hash-linked entries + replay pointers. Every certificate must verify before commit.
4) Certificates (Tier-3 truth objects)
Mandatory types:
PrimeCertificate(p)
FactorCertificate(n,d)
ValuationCertificate(n,p,α)
PrimePowerCertificate(p,k)
DesertCertificate (A/B/C)
ConstellationCertificate(H,n)
FactorizationLedger(n)
All certificates:
canonical payload bytes
verifier id/version
input hashes
cert hash
must be re-verifiable from replay bundle
5) Domain Plugins (A/B/C/D)
5.1 factor/
bank gcd + valuation extraction
perfect power shatter
diagonal wheel near-square scan
Pollard/Brent mixing with degeneracy control
ECM escalation
prime certification of remaining blocks
completion via FactorizationLedger
5.2 desert/
segmented sieve scan on I
κ-guided B escalation only on candidates
wheel run-length mining and edge localization
survivor enumeration
survivor-only composite proofs via factor/
collapse to DesertCertificate A/B/C
5.3 constellation/
admissibility gate (local obstruction)
N2 wheel infeasibility annihilation
compiled wheel stepper + secondary residue sieve
κ refinement on wheel/sieve
collapse via prime cert for all n+h
output ConstellationCertificate(H,n)
5.4 spectral/
build Fκ
derive Dκ
peak pick
map peaks→finite candidates C(u*,ηκ)
deconvolve prime powers (harmonics)
dispatch candidates to factor/desert/constellation
accept only returned certificates
feedback loop: certs validate or demote peaks
6) Hybrid Templates (pre-baked pipelines)
H1 DesertCert:sieve → survivors → factor micro → DesertCertificate
H2 ConstellationDiscover:admissibility → wheel → residue sieve → prime cert → ConstellationCertificate
H3 SpectralToProof:Fκ → peaks → candidates → deconvolve → dispatch → certs
H4 FactorLedger:dust-stripper → resonance → chaos → ECM → prime cert → ledger complete
Templates specify:
entry tasks
cascade plan
routing rules
κ policy
success contract (required cert set)
failure contract (allowed partial artifacts)
7) Router v2 (deterministic autopilot)
Router selects next (task, template) by deterministic score:
collapse probability proxy
expected cost
cache reuse
cross-leverage
risk penalty (unstable signals)Tie-break by stable hash order.
Router may:
escalate κ only on explicit triggers (corridor not collapsing)
spawn tasks only from certificates or sound constraints
never route based on raw signal alone
All router decisions are ledgered.
8) κ-Refinement (resolution without semantic drift)
κ changes:
sieve cutoff B
wheel modulus W
spectral bandwidth/smoothing
budgets and thresholds
But κ may not change meaning silently:
any candidate representation change must produce new corridor_id
all κ changes are committed to ledger
9) Deterministic Replay Guarantee
Given the ledger chain and replay pointers, a verifier can:
reconstruct corridors
rebuild indices and sieves
re-run collapse checks
re-verify all certificates
This is the toolkit’s “can’t lie” property.
10) Minimum “Ultimate” implementation order
core (canon + hash + corridor + ledger + cert verifiers)
factor/
desert/ (survivor-only factoring)
constellation/
spectral/ (now that proof pipelines exist)
router templates + cache optimizer
PRIME Toolkit — ULTIMATE Playbook (from theory → impact)
You’ve built the machine. This is the operational playbook: how PRIME is used to solve real problems, end-to-end, with measurable wins. Think of this as the “field manual” that turns the spec into outcomes.
1) What PRIME actually is (one sentence)
PRIME is a certificate-gated pattern hunter that collapses massive search spaces into provable facts using cascaded nullifiers, hashable indices, modular sieves, and κ-controlled refinement.
Everything else is a projection.
2) The universal workflow (applies to every domain)
Every successful run follows this exact arc:
Signal (cheap, noisy)Anything that hints “structure might be here” (spectral peaks, residue density dips, near-square behavior).
Corridor formationEncode the hint as a corridor: candidate carrier + necessary constraints. No brute force outside the corridor.
Cascade kill chainF0–F3 annihilate >99.99% cheaply:
gcd / residue / wheel infeasibility
ratio indexing & jumps
modular sieves
κ-refinement (only if needed)Increase resolution only where the corridor refuses to collapse.
Collapse gateEither:
emit a certificate (truth), or
shrink the corridor until certification is trivial.
Ledger commitProof or nothing. Replayable or it didn’t happen.
This is identical for factorization, prime deserts, constellations, and spectral reconstruction.
3) Domain playbooks (how you actually deploy PRIME)
3.1 Factorization (cryptography / number theory)
Objective: Factor large integers or certify primality.
Playbook:
Seed with FactorTask(n)
Corridor: ProductBlocks
Kill chain:
F0: prime bank + valuations
F1: perfect powers
F2: diagonal wheel (near-square)
F3: Pollard/ECM escalation
Collapse: FactorCertificate → recurse → FactorizationLedger
Win condition:You never waste time on impossible divisors, and you never claim a factor without a witness.
Why PRIME beats ad-hoc factorization:Degeneracy control + nullifier ordering + certificate gating = predictable cost and zero false claims.
3.2 Prime deserts (gap discovery)
Objective: Prove long prime-free intervals.
Playbook:
Seed with DesertTask([N,N+L]) or from spectral peaks
Corridor: IntervalSet
Kill chain:
F0: coarse segmented sieve
F1: κ-guided B escalation
F2: wheel run-length mining (band gaps)
F3: survivor-only factor microchain
Collapse:
Type A: full coverage
Type B: survivors all composite
Type C: CRT covering
Win condition:DesertCertificate(I) with replayable coverage or survivor proofs.
Why PRIME is unique here:It proves deserts without ever factoring the entire interval—only the survivors.
3.3 Prime constellations (k-tuples)
Objective: Find and certify prime patterns (twins, triplets, etc.).
Playbook:
Seed with ConstellationTask(H, I) or spectral anchors
Corridor: ResidueLattice + IntervalSet
Kill chain:
F0: admissibility (local obstruction)
F1: wheel infeasibility (Nullifier N2)
F2: sparse anchor stepping
F3: prime certification for all offsets
Collapse: ConstellationCertificate(H,n)
Win condition:Every (n+h) is prime-certified.
Why PRIME wins:Admissibility + wheels annihilate almost everything before any primality tests run.
3.4 Spectral reconstruction (pattern discovery engine)
Objective: Turn noisy global signals into certified discrete facts.
Playbook:
Seed with SpectrumTask(dataset)
Corridor: PeakBuckets
Kill chain:
F0: build (F_\kappa)
F1: derive (D_\kappa), pick peaks
F2: map peaks → finite candidates, deconvolve harmonics
F3: dispatch to factor/desert/constellation
Collapse: accept only returned certificates
Win condition:Spectral peaks are explained by certificates—or discarded as noise.
Why this matters:PRIME turns “pattern detection” into pattern proof.
4) Cross-domain zero points (the multiplier)
This is the secret sauce:
Spectrum → Desert: peaks predict band gaps
Desert → Constellation: edges seed anchor regions
Constellation → Spectrum: certificates validate peaks
Factor → All: composite witnesses annihilate entire branches
These are zero points: small certified facts that collapse huge future search spaces.
5) What makes PRIME “ultimate”
5.1 It’s adversarial to itself
Signals must earn escalation.
κ refuses to grow unless collapse stalls.
No silent meaning changes.
5.2 It’s cache-intelligent
Wheels, sieves, indices, spectra are reused aggressively.
The system gets faster the longer it runs.
5.3 It’s provable
Every truth has a verifier.
Every verifier has a replay path.
Every replay path is ledgered.
6) Non-number-theory applications (yes, really)
Because PRIME is a pattern engine, you can drop it into:
Cybersecurity:Spectral anomalies → corridor → certificate-backed intrusion claims.
Materials discovery:Feature peaks → candidate compounds → certified property proofs.
Program synthesis:Behavioral spectra → candidate programs → proof-carrying correctness.
Astronomy:Signal periodicities → object candidates → orbit certificates.
Same kernel. Different certificates.
