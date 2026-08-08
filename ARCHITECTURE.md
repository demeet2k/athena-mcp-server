# Architecture

0. Git causal persistence — literal history and checkpoint CAS.
1. CCR — deterministic functional identity for reusable capability.
2. JSPACE — typed semantic multigraph over objects, versions, events, manifestations, agents and mutations.
3. SCALE — `S0 event → S1 delta → S2 relation → S3 motif → S4 generator → S5 organ law`.
4. KC144 — immutable 12×12 host topology; coordinate is never identity.
5. Polycoordinate/transform runtime — open-world charts, executable derivations, measured holonomy, exact visible-output coordinates.
6. COLLECTIVE V1 — HIVE/SWARM/PACK/FLOCK/HERD/POD geometry, dynamic width, roles, bounded topology, quorum/inhibition, reserve and homeostasis.
7. COLLECTIVE GROWTH — demand allocation, bridge accounting, FISSION/FUSE/HOLD pressure, alarm propagation, lifecycle/apoptosis.
8. COLLECTIVE MEMORY V2 — persistent pheromones, typed JSPACE invalidation, observed-RGO calibration, topology CAS/rollback, failure antibodies.
9. COLLECTIVE LEARNING V3 — measured resource metabolism, bounded rollbackable learned policy, counterfactuals, elder authority, antibody evolution, multiscale pheromones.
10. COLLECTIVE ECOLOGY V4 — task regimes, contextual-UCB experiment selection, causal-confidence credit/residual, worker budget scheduling, learned diffusion, executable regression witnesses, uncertainty-banded rollouts, topology→JSPACE recovery sagas.
11. COLLECTIVE SCIENCE V5 — full-covariance contextual uncertainty + empirical interval calibration, active information-gain experiment design, factorial interaction and delayed credit, learned transition dynamics, multi-period scheduling, stronger constrained witness cells, learned regime geometry, Pareto-front organization search, and projection-edge compensation algebra.
12. Runtime — hydrate, conditional writes, telemetry, adoption, replayable sessions, exact final emission.

## Objective hierarchy

Base:

`J = w_O·O - w_C·C`.

Normalized organization comparison:

`RGO = mean(O)/(1+mean(C))`.

V2: `predicted_RGO -> observed_RGO -> calibrated_RGO`.

V3: `explicit observed reward -> bounded versioned policy update -> rollbackable policy state`.

V4: `context + regime + arm history -> <mean,uncertainty,UCB>` plus `outcome -> <credit,causal confidence,residual>`.

V5: `correlated context -> <posterior mean,covariance,calibrated interval>`; `hypotheses + candidate experiments -> expected information gain`; `observed factorial/delayed outcomes -> identified/qualified credit`; `observed action transitions -> shrinkage transition model`; `candidate organizations -> non-dominated Pareto frontier`.

## Current developmental metabolism

`HYDRATE`
`-> MEMORY/ANTIBODY/ELDER`
`-> COARSE+LEARNED REGIME`
`-> BAYES/CALIBRATION`
`-> LIVE HYPOTHESES`
`-> ACTIVE EXPERIMENT DESIGN`
`-> PARETO FRONTIER`
`-> COLLECTIVE PLAN`
`-> MULTIPERIOD RESOURCE SCHEDULE`
`-> EXECUTE/METER`
`-> QUORUM/FALSIFICATION/WITNESS`
`-> OBSERVE`
`-> DIRECT/INTERACTION/DELAYED CREDIT`
`-> BAYES/BANDIT/POLICY UPDATE`
`-> TRANSITION MODEL UPDATE`
`-> LEARNED-TRANSITION ROLLOUT`
`-> PHEROMONE/DIFFUSION/IMMUNE/ELDER`
`-> JSPACE/TOPOLOGY/PROJECTION/COMPENSATION`
`-> LIFECYCLE`
`-> FINALIZE/VERIFY/COMMIT`.

## Authority surfaces

- semantic state: expected-VID / semantic event-head authority;
- Git state: expected Git HEAD;
- topology state: expected topology version;
- V3 learned policy: expected policy version;
- V4/V5 bandit/Bayesian/transition state: observational predictive evidence only, never semantic authority;
- causal-credit state: attribution evidence, with identification class and residual rather than hidden causal promotion;
- diffusion/pheromone: routing priors, not dependency truth;
- learned regimes: transfer neighborhoods, not object identity;
- Pareto front: tradeoff set, not a canonical single winner;
- projection/compensation: semantic recovery operations with separate Git consequences.

## Bayesian/calibration boundary

V5 full-covariance contextual state uses

`A = λI + Σwφφᵀ`, `θ̂=A⁻¹b`, `Σ=A⁻¹`.

Predictive intervals are calibrated only from retained **pre-update** predictions and later observations. Empirical coverage can widen/narrow interval scale, but does not prove the underlying reward model is correct or transport calibration across distribution shift.

`POSTERIOR != TRUTH` and `COVERAGE_CALIBRATION != MODEL_VALIDITY`.

## Active experiment boundary

For explicit hypotheses and caller-supplied outcome likelihoods, V5 ranks candidate experiments by expected entropy reduction adjusted by feasibility/cost/risk. Ethics remains a hard eligibility gate.

`EXPECTED_INFORMATION_GAIN != EVIDENCE` and `DESIGN != RESULT`.

## Causal boundary

V4 one-step intervention credit retains causal confidence/residual. V5 additionally supports:

- main present-vs-absent contrasts;
- pairwise `μ11-μ10-μ01+μ00` interactions only when all four cells exist;
- delayed `ΔY × causal_confidence × discount^delay` credit.

A missing factorial cell remains `UNIDENTIFIED`; a numerical interaction is not promoted to causal without design confidence. Temporal delay alone never proves cause.

## Transition/rollout boundary

V5 learns action-conditioned feature deltas with shrinkage toward zero. Unobserved features remain unchanged/unknown. Learned-transition rollouts remain `SIMULATE_ONLY` and cannot train their own model.

`TRANSITION_MODEL != WORLD_TRUTH`; `ROLLOUT != EXECUTION`.

## Resource/scheduling boundary

Automatically observable: MCP tool calls and wall time.

Caller-observable optional dimensions include tokens, compute, retrieval, storage, attention, CPU/GPU time, energy, memory and network bytes.

Unknown dimensions remain `UNKNOWN`, never zero.

V5 multi-period scheduling respects explicit dependencies, durations, worker capacity, horizon and known budgets through bounded beam search. It deliberately returns no global optimality proof.

## Witness boundary

V5 witness cells execute repository-owned unittest references only and add Python isolation, sanitized environment, temporary HOME, timeout, Python socket denial, and POSIX resource limits where available. They are stronger process cells, but not OS/VM-level hermetic sandboxes.

## Projection/compensation boundary

V4 projection remains a cross-store recovery saga:

`PREPARED -> SEMANTIC_APPLIED -> GIT_COMMITTED? -> COMPLETED`

with `ABORTED` before semantic effects and `COMPENSATION_REQUIRED` after partial effects.

V5 adds a narrow semantic inverse: active edges whose parsed attributes contain the exact projection ID can be retracted under current semantic-head CAS, with `COMPENSATE_EDGE` events. The saga may become `COMPENSATED`. If a Git commit exists, Git compensation remains separately required; V5 does not rewrite Git history automatically.

## Non-negotiable science firewall

- identity != coordinate
- tested != current != canonical != integrated
- UNKNOWN != N/A
- UNKNOWN_COST != ZERO_COST
- prediction != observation
- posterior != truth
- calibration != model validity
- expected information gain != evidence
- experiment design != experiment result
- counterfactual != observation
- UCB != truth
- bandit/Bayesian prediction != reward
- association != causation
- attribution != causal proof
- missing factorial contrast != zero interaction
- temporal delay != causation
- learned policy != canonical truth
- learned regime != semantic identity
- transition model != world truth
- rollout != execution/commit
- bounded schedule != global optimum
- diffusion posterior != causal path
- pheromone != authority
- elder != oracle
- regression pass != universal proof
- witness cell != hermetic sandbox
- Pareto frontier != single best action
- projection saga != atomic transaction
- semantic compensation != Git rollback
- local success != global authority
- pruning removes active routing privilege, never required lineage

## Coordinate fibers

`COLLECTIVE=<F,R,N,D,Q,C,O,H,L>`

`COLLECTIVE_LEARNING=<B,P,CF,E,A,MS,L>`

`COLLECTIVE_ECOLOGY=<RG,X,CR,WS,DF,RW,RO,PS,L>`

`COLLECTIVE_SCIENCE=<BY,CAL,ED,IX,DL,TR,SC,WC,RG,PF,CP,L>`.
