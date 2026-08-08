# ATHENA COLLECTIVE RUNTIME V1

## Purpose

Convert hive/colony/swarm/pack/herd/flock/school/pod collective-intelligence priors into explicit control laws for ATHENA. Biological systems are design evidence, not claims of equivalence.

The runtime optimizes useful group capability after coordination cost:

`J = w_O·O - w_C·C`

with cost vector

`C = [communication, duplication, switching, synchronization, congestion, failure_propagation, integration, maintenance]`

and output vector

`O = [quality, throughput, velocity, resilience, accuracy, innovation, retained_knowledge, integration]`.

A normalized comparison surface is

`RGO = mean(O) / (1 + mean(C))`.

The controller MUST prefer higher RGO over larger worker count, greater connectivity, or stronger consensus.

## Constitutional laws

1. `MAX_GROWTH != MAX_ACTIVITY`.
2. `MAX_INTEGRATION != MAX_CONNECTIVITY`.
3. `CONSENSUS_SCORE != EVIDENCE_SCORE`.
4. Reserve capacity is a capability; target reserve MUST be greater than zero when capacity permits.
5. Add workers only while marginal output exceeds marginal coordination/operating cost.
6. Strong intra-module ties plus sparse inter-module bridges are preferred to indiscriminate all-to-all communication.
7. Positive recruitment MUST be paired with inhibition, contradiction routing, stop conditions, and attractor evaporation.
8. A bridge is justified only when expected future routing/reuse savings exceed build + maintenance + locked-capacity cost.
9. Failure information propagates along dependency/relevance edges, not by default global broadcast.
10. Growth can be throttled by homeostasis when evidence, reserve, latency, error, congestion, duplication, or contagion leaves its safe band.

## Collective forms

### HIVE
Use for persistent, divisible, repetitive work with reusable infrastructure. Favor builders, verifiers, integrators, archivists, sentinels, scouts, and bridge builders. Stigmergic state is first-class.

### SWARM
Use for uncertain exploratory volatile search. Favor heterogeneous scouts, verifier diversity, independent hypotheses, quorum convergence, inhibition, and evaporation.

### PACK
Use for one hard coupled target. Favor complementary positions: builder/chaser/flanker/verifier/integrator/sentinel/catalyst. Team width is hardness-sensitive and stops at diminishing marginal return.

### FLOCK
Use for rapidly changing shared state. Maintain separation/alignment/cohesion through bounded-neighbor communication rather than global synchronization.

### HERD
Use for migration across versions/media/architectures. Protect invariants and vulnerable core state while maintaining reachability and rollback.

### POD
Use for cultural/procedural memory and longitudinal transfer. Strong local culture plus sparse weak ties supports specialization without siloing.

## Mode selector

Task signals are normalized to `[0,1]`:

`S = <hardness, uncertainty, divisibility, coupling, volatility, risk, migration, repetition, reuse, innovation, latency_sensitivity, evidence_sensitivity>`.

The runtime computes scores for each collective form and selects the maximum. Scores remain visible so callers can inspect near-ties instead of treating classification as magical authority.

## Dynamic swarm sizing

Let `n` be active workers, `N` the available capacity after protected reserve, `B(n)` saturating benefit, and `C(n)` coordination + operating + switching cost.

`n* = argmax_{1<=n<=N} [B(n)-C(n)]`.

The implementation then applies an anti-bloat rule: choose the smallest `n` within 2% of maximal predicted utility. This converts diminishing returns into explicit termination rather than token/agent accumulation.

## Role allocation

For chosen form `F`, the role probability vector `p_F` is converted into exact integer counts by largest-remainder allocation:

`sum_r count(r) = active_workers`.

Reserve workers are outside the active role allocation and remain surge capacity.

## Topology

Default neighborhood degree is bounded approximately by

`k = ceil(log2 n)`

clamped to `[1,n-1]` for `n>1`.

Bridge budget grows sublinearly:

`b = ceil(sqrt(n)) - 1`.

The purpose is to move expected communication from dense `O(n^2)` behavior toward bounded local `O(kn)` behavior while preserving reachability.

## Quorum + inhibition

For candidate `i`:

`net_i = support_i * ((1-e_s)+e_s*evidence_i) - g*inhibition_i - 0.5*contradiction_i`.

Commit only when:

`net_top >= q`

and

`net_top - net_runnerup >= delta_q`

and contradiction remains below the blocking band.

Risk and evidence sensitivity raise `q`; risk raises the required winning margin. High support with weak evidence can therefore remain exploratory.

## Stigmergic update

Artifact-route importance evolves as

`rho = exp(-lambda * age)`

`evaporated = old * rho`

`deposit = clamp(weighted(quality, novelty, evidence, reuse, bridge_value, downstream_gain) - penalties(staleness, contradiction))`

`new = clamp(evaporated + gain * deposit * (1-evaporated))`.

Thus evidence/reuse can strengthen a route, while age/staleness/contradiction removes inherited privilege.

## Homeostasis

The runtime observes:

`H = <context_saturation, duplication, latency, error_rate, stale_ratio, contagion, reserve_fraction, evidence_quality, bridge_overhead, coordination_overhead>`.

Threshold violations emit explicit corrective actions. Multiple critical violations produce RED state and should throttle growth until repaired.

## Collective coordinate

Every plan may be attached to the output coordinate atlas as:

`COLLECTIVE = <F,R,N,D,Q,C,O,H,L>`

where:

- `F`: collective form;
- `R`: role allocation;
- `N`: active workers, bounded-neighbor degree, bridge budget, reserve;
- `D`: demand/task signal field;
- `Q`: quorum threshold, inhibition gain, evaporation rate;
- `C`: unit cost and marginal stop threshold;
- `O`: predicted net utility / later measured outputs;
- `H`: reserve/homeostatic state;
- `L`: lineage/native caller coordinate.

This coordinate is additive to KC144/JSPACE/SCALE/polycoordinate coordinates; it does not replace them.

## MCP operations

`athena_collective_plan` selects form, team width, roles, topology, quorum, inhibition, evaporation, stop threshold, reserve, and returns the COLLECTIVE coordinate.

`athena_collective_evaluate` scores a concrete organization with cost/output vectors and RGO.

`athena_collective_quorum` performs evidence-sensitive commitment with inhibition/contradiction.

`athena_stigmergy_update` computes reinforcement + evaporation for artifact/routing priority.

`athena_collective_health` evaluates homeostatic pressure and corrective actions.

## Persistence contract

The controller itself is deterministic and side-effect free. Canonical persistence remains the responsibility of existing ATHENA mutation/crystallization primitives. A caller that wants a collective plan to become organism state SHOULD include `collective_coordinate` in the open-world `coordinates` map passed to `athena_finalize_output`, or commit it into the relevant canonical object via expected-VID CAS.

This separation prevents an advisory control calculation from silently becoming canonical truth.
