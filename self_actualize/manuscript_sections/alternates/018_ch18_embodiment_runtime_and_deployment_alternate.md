# CHAPTER 18: EMBODIMENT, RUNTIME, AND DEPLOYMENT

Witness Status: freshest compatible alternate branch; preserved for later reconciliation; not canonical in the current spine.
Canonical Branch Lock: `Ch17 Prop Types -> Ch18 Style Grammar -> Ch19 ...`
Preservation Note: this file remains a witness to the runtime/deployment branch and is excluded from the top-level manuscript build.

## 18.0 Prolegomenon

The previous chapters established the manuscript's internal maturity conditions:
manifestation, routing, swarm synthesis, witness-bearing replay, publication, safety
regimes, and temporal continuity. Yet a system may satisfy all of those and still remain
inert if it never enters runtime. The present chapter formalizes the passage from lawful
manuscript object to lawful deployed process. Embodiment is the act by which a
proof-carrying structure becomes situated in an environment. Runtime is the active
execution regime in which policies, routes, witnesses, interrupts, and repairs operate
under real conditions. Deployment is the staged installation of that runtime into
increasingly demanding environments without abandoning safety, trust, scope, or replay
discipline.

This chapter is necessary because the ontology of a manuscript and the ontology of a
running system are not identical. A theorem, route packet, or export bundle may be lawful
in the atlas while remaining unembodied. Once deployed, however, new burdens appear:
environment mismatch, policy conflict, trust gating, operational load, rollback cost, and
the asymmetry between what the system proves abstractly and what it can maintain under
live constraints. The chapter therefore specifies the lawful transform

`E_emb : P_x -> R_x`,

where `P_x` is a proof-carrying object and `R_x` is a runtime-bearing embodied object.

Let the embodied runtime object be

`R = (d, e, r, pi, tau, omega, Lambda)`,

where:

- `d` is deployment identity
- `e` is environment profile
- `r` is runtime state
- `pi` is active policy family
- `tau` is burden or truth state
- `omega` is support and replay shell
- `Lambda` is deployment ledger

The central law of the chapter is:

`a manuscript object becomes lawfully embodied only when it can execute inside a declared environment profile, under a typed runtime policy, with deployment-stage safety, trust, rollback, and replay conditions made explicit.`

This law has four immediate corollaries.

First, deployment is not proof of success. It is only the beginning of exposure to
reality.

Second, embodiment is always partial. No deployment instantiates the whole manuscript; it
instantiates an admissible subset.

Third, runtime state must be tracked as a first-class object rather than inferred
retrospectively from outputs.

Fourth, rollback under stress is not failure of embodiment. It is part of mature
embodiment.

This chapter therefore supplies the lawful interface between crystal and world.

## 18.S Embodiment Objects

### 18.S.1 Deployment

The first square-lens object is deployment. A deployment is a concrete installation of a
bounded manuscript capability into a runtime context. It is not merely "running the
system." It is the typed event by which a capability class crosses from atlas legality
into operational exposure.

Define the deployment object:

`d = (a_d, chi_d, sigma_d, tau_d, omega_d)`,

where:

- `a_d` is deployment address
- `chi_d` is deployment class
- `sigma_d` is the capability subset or manifest being deployed
- `tau_d` is the current deployment burden state
- `omega_d` is the support shell and deployment witness bundle

A deployment class may be:

- `LocalTest`
- `SandboxRuntime`
- `CollaboratorRuntime`
- `LiveProduction`
- `FederatedRuntime`

A lawful deployment requires:

- `CapabilityBounded(d) = 1`
- `ScopeDeclared(d) = 1`
- `RollbackPrepared(d) = 1`
- `EnvironmentDeclared(d) = 1`

Definition 18.1 (Lawful Deployment). A deployment is lawful if and only if the deployed
capability subset, environment assumptions, support shell, and rollback route are all
explicit before execution begins.

This distinguishes mature deployment from improvisational activation.

### 18.S.2 Environment Profile

The second embodiment object is the environment profile. A system does not deploy into
"the world" generically. It deploys into a typed environment with specific constraints,
affordances, interfaces, and hazards.

Define the environment profile:

`e = (I_e, O_e, C_e, H_e, T_e)`,

where:

- `I_e` is the family of ingress channels and observations
- `O_e` is the family of output channels and actions
- `C_e` is the environment constraint family
- `H_e` is the hazard family
- `T_e` is the trust and permission model

An environment profile may include:

1. latency and timing conditions
2. resource ceilings
3. available APIs or physical channels
4. human oversight presence
5. allowed and forbidden action classes
6. trust gates and escalation rules

Define environment compatibility:

`Compat(d, e) = 1 iff the deployment class and environment profile admit the same action and risk grammar.`

Theorem 18.2 (Environment-Profile Theorem). No embodied runtime is lawful without an
explicit environment profile, because deployment safety, trust gating, and rollback
conditions cannot be computed from capability manifests alone.

This theorem makes embodiment situated rather than abstract.

### 18.S.3 Runtime Record

The third square-lens embodiment object is the runtime record. Once deployed, the system
enters a stateful execution stream. That stream must be recorded as a first-class object,
not merely inferred from logs after failure.

Define the runtime record:

`r_t = (x_t, pi_t, chi_t, tau_t, omega_t, Lambda_t)`,

where:

- `x_t` is the current embodied state
- `pi_t` is the active policy or workflow
- `chi_t` is the current runtime mode
- `tau_t` is the current burden or truth state
- `omega_t` is the current witness support
- `Lambda_t` is the runtime ledger and event history

Runtime modes may include:

- `Idle`
- `Observe`
- `Plan`
- `Act`
- `Pause`
- `Quarantine`
- `Rollback`

A valid runtime record must satisfy:

- `StateAddressed(r_t) = 1`
- `ModeTyped(r_t) = 1`
- `LedgerBound(r_t) = 1`

Definition 18.3 (Runtime Reality). A deployed system is runtime-real only to the extent
that its current state, mode, and support shell are explicitly capturable as a runtime
record.

This law prevents embodiment from collapsing into opaque behaviorism.

### 18.S.4 Embodiment Subset Law

No runtime ever instantiates the entire manuscript. Every embodiment installs only a
bounded subset of the full capability space.

Let the full manuscript capability space be

`M_full`.

A deployment installs only a subset

`M_emb subseteq M_full`.

The embodiment subset law states:

`a runtime is lawful only if the embodied subset is explicit, auditable, and smaller than or equal to the capability, trust, and safety envelope of its environment.`

Formally:

`SubsetLaw(d, e) = 1 iff M_emb subseteq E_safe(e)`,

where `E_safe(e)` is the environment's admissible execution envelope.

Theorem 18.4 (Embodiment Subset Theorem). Every lawful deployment must declare not only
what the system can do in principle, but which subset is actually present in the runtime
and why that subset is admissible in the target environment.

This closes the Square lens.

## 18.F Deployment Dynamics

### 18.F.1 Rollout

The first Flower-lens dynamic is rollout. Rollout is the initial insertion of a
deployment object into a live environment. It is the dynamic complement of the deployment
object itself.

Define rollout:

`R_out : (d, e) -> r_0`,

where `r_0` is the initial runtime record.

A lawful rollout requires:

- `PreflightPassed(d, e) = 1`
- `HazardsScanned(e) = 1`
- `TrustGateOpen(e) = 1`
- `RollbackHookInstalled(d) = 1`

Rollout is not instantaneous release. It is the first bounded activation event. The
system may still run under reduced autonomy, restricted outputs, or heightened monitoring.

Define rollout success:

`RolloutOK(r_0) = 1`

if the initial runtime record exists and no immediate environment conflict or safety
contradiction appears.

Theorem 18.5 (Rollout Gate Theorem). A rollout is lawful only if preflight, hazard scan,
trust gate, and rollback hook all succeed before the first live actuation.

This theorem makes deployment entrance guarded rather than impulsive.

### 18.F.2 Staged Adoption

The second deployment dynamic is staged adoption. Embodiment is not all-or-nothing. It
progresses through staged trust and capability thresholds.

Let the adoption tiers be:

`Tier_0 < Tier_1 < Tier_2 < ... < Tier_n`.

A staged adoption dynamic has the form

`r^(k) -> r^(k+1)`

only if

`TierGate_k(r^(k), e) = 1`.

Tier gates may depend on:

1. successful prior runtime behavior
2. absence of hazardous drift
3. trust accumulation
4. adequate witness retention
5. acceptable operational burden

Define the adoption score:

`A_k = alpha * P_perf + beta * T_trust + gamma * W_wit - lambda_1 * H_haz - lambda_2 * B_ops`.

Promotion requires

`A_k >= theta_k`.

Definition 18.6 (Staged Adoption). A deployment is staged when its runtime autonomy,
capability subset, or environment access grows only by passing explicit tier gates.

This is the chapter's law of gradual embodiment.

### 18.F.3 Migration

The third deployment dynamic is migration. A runtime may need to move between
environments, hosts, tool planes, trust models, or operating shells. Embodiment must
therefore be portable under revalidation rather than assumed stable by relocation alone.

Define migration:

`G_dep : (d, e_1, r_1) ~> (d', e_2, r_2)`.

A migration is lawful only if:

- `EnvironmentMapDeclared(e_1, e_2) = 1`
- `CapabilitySubsetRevalidated = 1`
- `TrustModelRechecked = 1`
- `SupportShellUpdated = 1`

Migration is not merely technical relocation. It is semantic relocation into a different
operational world. It may therefore require:

1. subset shrinkage
2. new hazard thresholds
3. new trust gates
4. new rollback paths

Theorem 18.7 (Deployment Migration Theorem). A runtime may migrate lawfully only when
the target environment receives a fresh embodiment contract rather than inheriting the
source environment's contract by default.

This theorem is the operational analog of migration manifests in temporal continuity.

### 18.F.4 Rollback Under Stress

The final deployment dynamic is rollback under stress. Embodiment must know how to
retreat when conditions degrade.

Define runtime stress:

`S_rt = alpha * M_mismatch + beta * C_conflict + gamma * T_trust_drop + delta * B_overload + epsilon * H_haz`.

If

`S_rt >= theta_rollback`,

rollback becomes lawful or mandatory.

Rollback under stress may take several forms:

1. revert to an earlier runtime tier
2. revert to a narrower capability subset
3. re-enter sandbox mode
4. fully suspend deployment

Let the rollback operator be:

`B_dep : r_t -> r_t'_safe`,

with `t' < t` or with a lower-risk runtime shell.

Theorem 18.8 (Stress Rollback Theorem). A mature deployment is not one that never rolls
back, but one that can retreat under stress without losing lineage, replay, or safety
discipline.

This closes the Flower lens.

## 18.C Deployment Safety

### 18.C.1 Environment Mismatch

The first Cloud-lens burden object is environment mismatch. A deployment may be lawful in
one environment and unlawful in another.

Define mismatch:

`M_env(d, e) = alpha * D_IO + beta * D_trust + gamma * D_constraint + delta * D_timing`,

where:

- `D_IO` is the difference between expected and actual input or output channels
- `D_trust` is the difference in permission and oversight structure
- `D_constraint` is the difference in safety or operation constraints
- `D_timing` is latency or scheduling mismatch

If

`M_env(d, e) >= theta_env`,

then deployment must either remain restricted, be migrated differently, or be halted.

Theorem 18.9 (Environment Mismatch Theorem). No runtime may assume transferability of
lawful behavior across environments without an explicit environment-difference
calculation and revalidation.

This theorem makes embodiment context-sensitive.

### 18.C.2 Policy Conflict

The second deployment burden object is policy conflict. The active runtime policy may
clash with local environment rules, external oversight, or manuscript constitutional law.

Let active policy be `pi_t`, environment policy be `pi_e`, and manuscript constitutional
policy be `pi_m`. Policy conflict exists when:

- `pi_t not-subseteq pi_e`
- or `pi_t not-subseteq pi_m`

Define conflict score:

`C_pol = alpha * C_scope + beta * C_action + gamma * C_trust + delta * C_safety`.

A conflict becomes actionable when

`C_pol >= theta_pol`.

The lawful responses are:

1. policy narrowing
2. staged downgrade
3. migration
4. rollback
5. lockout

Proposition 18.10 (Policy Narrowing Proposition). A deployment under policy conflict
should first narrow capability subset before considering broader failure declarations,
unless the conflict is immediately safety-critical.

This provides the local repair law for policy mismatch.

### 18.C.3 Trust Gating

The third Cloud-lens burden object is trust gating. Operational runtime cannot be
separated from trust state.

Define trust state:

`T(d, e, t) in [0, 1]`.

Trust state depends on:

1. prior performance
2. witness retention
3. environmental oversight
4. social or organizational trust ledgers
5. recent hazard events

A capability subset `M_emb` is only active if

`T(d, e, t) >= theta_trust(M_emb)`.

Thus larger or riskier subsets require higher trust.

Trust gating can therefore:

1. unlock actions
2. throttle actions
3. demote runtime tier
4. trigger rollback or quarantine

Theorem 18.11 (Trust-Gating Theorem). Runtime capability must be gated not only by
internal correctness but by current trust state relative to the risk and scope of the
embodied subset.

This theorem makes trust operationally constitutive rather than merely social commentary.

### 18.C.4 Operational Burden

The fourth deployment burden object is operational burden. Even a safe and trusted
deployment may become unlawful if it imposes too much maintenance load, latency pressure,
monitoring complexity, or rollback cost.

Define operational burden:

`B_ops = alpha * B_monitor + beta * B_repair + gamma * B_oversight + delta * B_compute + epsilon * B_rollback`.

A deployment is operationally admissible only if

`B_ops <= B_max(e, chi_d, u_d)`,

where the bound depends on environment, deployment class, and audience or oversight
class.

Operational burden matters because a theoretically lawful runtime may still be a poor
deployment if it exhausts the host ecology faster than it returns value.

Theorem 18.12 (Operational Burden Theorem). A deployment is not lawful merely because it
is correct; it must also be supportable within the burden budget of its environment and
oversight context.

This closes the Cloud lens.

## 18.R Deployment Artifacts

### 18.R.1 Deployment Records

The first Fractal-lens artifact is the deployment record. Every rollout or embodiment
event must create a persistent record.

Define:

`D_rec = (a_d, chi_d, e, M_emb, tau_d, omega_d, Lambda_d, t_d)`,

where `t_d` is the deployment epoch.

A valid deployment record preserves:

1. what subset was deployed
2. into which environment
3. under which trust and safety rules
4. with which support shell
5. at which release or runtime epoch

This record is the temporal and operational anchor of embodiment.

### 18.R.2 Rollout Certificates

The second artifact is the rollout certificate. It certifies that preflight, environment
checks, and trust gates were satisfied before live activation.

Define:

`C_roll = (a_d, e, omega_pre, tau_roll, chi_roll)`,

where `omega_pre` is preflight support and `chi_roll` is rollout class.

A rollout certificate is lawful only if it explicitly states:

1. what was checked
2. what was not checked
3. what risk remains
4. what rollback path exists

This prevents deployment ceremony from becoming empty ritual.

### 18.R.3 Migration Packets

The third artifact is the migration packet. When a runtime moves across environments or
deployment tiers, the migration event must be capturable as a first-class object.

Define:

`p_mig = (a_src, a_tgt, e_src, e_tgt, Delta_emb, omega_mig, tau_mig)`.

This packet captures:

1. source runtime identity
2. target runtime identity
3. environment shift
4. embodied-subset change
5. migration witnesses
6. post-migration burden state

A migration packet is lawful only if backward re-entry remains possible or archival
replacement is explicit.

### 18.R.4 Runtime Replay Bundles

The final artifact is the runtime replay bundle. A live deployment must remain replayable
as a runtime event, not merely as a static export.

Define:

`Omega_rt = (D_rec, C_roll, Lambda_rt, S_check, eta_return)`,

where:

- `Lambda_rt` is the runtime ledger
- `S_check` is the runtime checkpoint family
- `eta_return` is the rollback or re-entry hook

A runtime replay bundle is lawful if:

- `Replayable(Omega_rt) = 1`
- `EnvironmentContextPreserved = 1`
- `TierHistoryPreserved = 1`

Theorem 18.13 (Runtime Replay Theorem). An embodied runtime becomes manuscript-real only
when its live behavior can be reconstructed as a bounded runtime process rather than
inferred from isolated outputs.

This closes the Fractal lens and the chapter as a whole.

## 18.5 Runtime Schema and Algorithms

Algorithm 18.1 - Environment Compatibility Check

```python
from dataclasses import dataclass


@dataclass
class EnvironmentProfile:
    io_channels: float
    trust_model: float
    constraint_fit: float
    timing_fit: float


def environment_mismatch(
    io_diff: float,
    trust_diff: float,
    constraint_diff: float,
    timing_diff: float,
    a: float = 1.0,
    b: float = 1.0,
    c: float = 1.0,
    d: float = 1.0,
) -> float:
    return (
        a * io_diff
        + b * trust_diff
        + c * constraint_diff
        + d * timing_diff
    )
```

Algorithm 18.2 - Deployment Gate

```python
def deployment_allowed(
    preflight_ok: bool,
    hazard_scan_ok: bool,
    trust_gate_open: bool,
    rollback_ready: bool,
) -> bool:
    return preflight_ok and hazard_scan_ok and trust_gate_open and rollback_ready
```

Algorithm 18.3 - Trust-Gated Capability Check

```python
def capability_unlocked(trust_state: float, required_trust: float) -> bool:
    return trust_state >= required_trust
```

Algorithm 18.4 - Stress Rollback Gate

```python
def rollback_under_stress(
    mismatch: float,
    policy_conflict: float,
    trust_drop: float,
    overload: float,
    hazard: float,
    threshold: float,
) -> bool:
    stress = mismatch + policy_conflict + trust_drop + overload + hazard
    return stress >= threshold
```

These runtime kernels instantiate the chapter's live deployment logic: environment
matching, rollout gating, trust-gated capability, and rollback under stress.

## 18.6 Integrated Theorems

Theorem 18.14 (Embodiment Contract Theorem). A proof-carrying manuscript object becomes
embodied only when a bounded capability subset is installed into a declared environment
profile under runtime, trust, and rollback law.

Theorem 18.15 (Staged Adoption Theorem). A mature deployment expands by tiered trust and
support gates rather than by all-at-once activation.

Theorem 18.16 (Migration Revalidation Theorem). Every change of environment or
deployment tier requires a fresh embodiment contract rather than inherited validity.

Theorem 18.17 (Trust-Gated Runtime Theorem). Operational capability must be modulated by
live trust state relative to the risk and scope of the embodied subset.

Theorem 18.18 (Runtime Replay Theorem). A runtime is manuscript-real only when its live
execution remains reconstructible as a bounded process with preserved environment
context.

## 18.7 Chapter Output Contract

A valid Chapter 18 output must include:

1. deployment, environment profile, runtime record, and embodiment subset law
2. rollout, staged adoption, migration, and rollback-under-stress dynamics
3. environment mismatch, policy conflict, trust gating, and operational burden
4. deployment records, rollout certificates, migration packets, and runtime replay
   bundles

CHAPTER 18 - EMBODIMENT, RUNTIME, AND DEPLOYMENT
