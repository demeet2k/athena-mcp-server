# Prop Channel Algebra

Generated: `2026-03-09T20:31:39.127816+00:00`
Command: `python -m self_actualize.runtime.derive_prop_channel_algebra`
Station: `<0100>`
Verdict: `OK`

This crystal formalizes Chapter 17 as typed communication-channel algebra rather than pure metaphor.

## Scope

- chapter: `Chapter 17: Prop Types - The Physics Of Communication Channels`
- address: `Arc 5 / Su Rail / Seed`
- prerequisites: `Ch11, Ch12, Ch13, Ch14, Ch15, Ch16`
- forward references: `Ch18, Ch19, Ch20`

## Deliverables

- typed channel-physics algebra for five prop families
- prop x count bandwidth matrix
- state-complexity hierarchy
- single-to-quad scaling
- VTG trace library as monitoring protocol
- club-spin session-handoff algebra

## Bandwidth Progression

- `ring`: `0.618`
- `poi`: `0.618`
- `ball`: `1.0`
- `club`: `1.618`
- `staff`: `2.618`

## Prop Families

### Ball

- channel type: `stateless_data_packet`
- state model: `stateless`
- bandwidth: `1.0`
- error mode: `drop`
- impact: `local`
- recovery: `1-2 beats`
- physical read: caught by position and timing alone
- communication read: self-contained message requiring no sender-state knowledge
- definition fields: `payload, position, timing, weight`

Use cases:
  - factual query
  - lookup request
  - formatted data transfer
  - routine one-shot packet

Count profiles:
  - `1`: one-to-one query - quick factual question
  - `2`: comparison lane - A/B testing or cross-validation
  - `3`: full three-pod circulation - standard multi-agent round-robin
  - `4+`: full pod-scale data routing - high-volume stateless coordination

Key formulas:
  - `B = (payload, position, timing, weight)`
  - `Accuracy(B) = A_height * A_lateral * A_temporal`
### Club

- channel type: `stateful_packet`
- state model: `stateful_spin_orientation_grip`
- bandwidth: `1.618`
- error mode: `knob_catch`
- impact: `propagating`
- recovery: `3-5 beats`
- physical read: clean catch depends on spin count, handle direction, and grip alignment
- communication read: work-in-progress or context-bearing handoff that requires state alignment
- definition fields: `payload, state, spin, orientation, grip`

Use cases:
  - analysis handoff
  - work-in-progress transfer
  - partial D/Q/I bundle
  - verification pipeline stage transfer

Count profiles:
  - `1`: one stateful handoff - passing one analysis between two agents
  - `2`: dual stateful streams - bidirectional handoff
  - `3`: full three-pod stateful loop - round-robin WIP coordination
  - `4+`: full pod-scale state routing - large stateful coordination

Key formulas:
  - `C = (payload, state, spin, orientation, grip)`
  - `spin(A->B) + spin(B->C) <= 3`
### Ring

- channel type: `framing_constraint`
- state model: `aperture_plane_diameter`
- bandwidth: `0.618`
- error mode: `snag`
- impact: `blocking`
- recovery: `2-3 beats`
- physical read: defines a boundary or aperture rather than carrying mass-state
- communication read: schema, template, or verification frame that content must pass through
- definition fields: `aperture, plane, diameter, rigidity`

Use cases:
  - seed format
  - verification contract
  - schema or template
  - multi-constraint framing

Count profiles:
  - `1`: one framing constraint - single schema or template
  - `2`: dual constraint stack - must satisfy two independent schemas
  - `3`: triple constraint stack - high-rigor output gate
  - `4+`: usually counterproductive - decompose instead of stacking

Key formulas:
  - `R = (aperture, plane, diameter, rigidity)`
### Poi

- channel type: `continuous_monitoring_channel`
- state model: `orbit_plane_trace`
- bandwidth: `0.618`
- error mode: `tangle`
- impact: `narrowing`
- recovery: `3-4 beats`
- physical read: continuous tethered orbit tracing geometry through space
- communication read: always-on background monitoring with adjustable monitoring geometry
- definition fields: `orbit_radius, plane, frequency, trace_pattern`

Use cases:
  - long-running task monitoring
  - convergence tracking
  - invariance testing
  - dual-agent correlated monitoring

Count profiles:
  - `1`: one monitoring channel - minimum background awareness
  - `2`: dual monitoring channel - standard dual monitoring
  - `3`: three monitoring channels - pod-scale background monitoring
  - `4`: monitoring-only mode - all limbs dedicated to monitoring

Key formulas:
  - `P = (orbit_radius, plane, frequency, trace_pattern)`
### Staff

- channel type: `broadcast_override_channel`
- state model: `full_pod_broadcast`
- bandwidth: `2.618`
- error mode: `collision`
- impact: `global`
- recovery: `5+ beats`
- physical read: sweeps through the entire workspace and forces all other motion to clear
- communication read: broadcast or governance directive reaching all agents at once
- definition fields: `payload, scope, priority, lever_arm`

Use cases:
  - global seed update
  - priority override
  - session start or stop
  - whole-pod governance directive

Count profiles:
  - `1`: one broadcast channel - one whole-pod directive
  - `2`: dual broadcast channel - seed plus constraint or parallel broadcast
  - `3+`: message flooding - avoid except in exceptional governance cases

Key formulas:
  - `S = (payload, scope=ALL, priority=OVERRIDE, lever_arm)`

## VTG Monitoring Modes

- `extension`: gradual scope adjustment - widening or narrowing research scope (`radius_delta_per_cycle`)
- `flower`: cyclic sub-topic exploration - agent should revisit n aspects repeatedly (`petal_count`)
- `isolation`: invariance testing - checking whether a claim survives context change (`fixed_point_address`)
- `cap`: correlated dual-agent monitoring - tracking complementary or anti-correlated outputs (`correlation_target`)
- `antispin`: convergence tracking - monitoring D/Q/I collapse toward zero point (`convergence_threshold`)

## Selection Function

- `Channel* = argmax[(BW(C) * Match(C, message)) / (Risk(C) * (1 + DR_C))]`

## Practical Heuristics

- default to balls for routine stateless queries
- upgrade to clubs when the handoff carries sender-state or work-in-progress context
- use rings when setting schemas, seeds, or verification frames
- use poi for background monitoring, convergence tracking, or correlated observation
- use staff sparingly for governance broadcasts that every agent must hear simultaneously
