# CHAPTER 17: PROP TYPES - THE PHYSICS OF COMMUNICATION CHANNELS

## Cross-Synthesis: Siteswap Architecture (Ch12-16) x Agent Protocol (Ch11 Section 11.3)

**Station:** `<0100>` - Arc 5, Su Rail  
**Prerequisites:** Chapters 11-16 complete; pod scaling vocabulary established  
**Deliverables:** typed channel-physics algebra for five prop families, the Prop x Count bandwidth matrix, the state-complexity hierarchy, single-to-quad scaling laws, the VTG geometric trace library as monitoring protocol, and the club-spin algebra as session-handoff protocol  
**Forward References:** Chapter 18, Chapter 19, Chapter 20

## D/Q/I Framework

**Desire.** Formalize each physical prop family as a typed communication channel with specific physics - bandwidth, latency, state burden, monitoring mode, and failure signature - so the Orchestrator can select the correct carrier for each inter-agent message.

**Question.** What algebra maps prop physics such as weight, rotation, grip, and trajectory geometry onto communication properties such as payload carriage, state transmission, framing power, monitoring continuity, scope, and recovery cost?

**Improvement.** Define a channel-type algebra, map prop physics to channel properties, and derive a disciplined selection protocol rather than relying on ad hoc channel choice.

## 17.0 Channel-Type Algebra

The core thesis of this chapter is that prop families are not ornamental variants of one generic juggling medium. Each prop realizes a distinct communication physics. The correct abstraction is therefore not "message passing" in the generic sense, but **typed channel selection** under prop-specific law.

Let the prop-family set be

$$
\mathfrak{P} = \{\mathcal{B}, \mathcal{C}, \mathcal{R}, \mathcal{P}, \mathcal{S}\},
$$

where:

- `\mathcal{B}` is the ball family
- `\mathcal{C}` is the club family
- `\mathcal{R}` is the ring or hoop family
- `\mathcal{P}` is the poi family
- `\mathcal{S}` is the staff family

Each family is assigned a channel-physics signature

$$
\Xi(\mathcal{X}) =
(\operatorname{BW}, \operatorname{Lat}, \operatorname{St}, \operatorname{Fr}, \operatorname{Mon}, \operatorname{Sc}, \operatorname{Risk}, \operatorname{Rec}),
$$

where:

- `\operatorname{BW}` is usable bandwidth
- `\operatorname{Lat}` is latency
- `\operatorname{St}` is state-carriage burden
- `\operatorname{Fr}` is framing power
- `\operatorname{Mon}` is monitoring continuity
- `\operatorname{Sc}` is scope of effect
- `\operatorname{Risk}` is failure impact
- `\operatorname{Rec}` is recovery cost

The channel families differ because the physical invariants differ. A ball is governed by position and timing. A club adds rotational state. A ring defines admissible aperture. A poi realizes continuous orbit. A staff extends reach across the entire workspace. Communication physics therefore inherits directly from manipulation physics.

Let a message requirement be typed as

$$
m = (\pi, \sigma, \rho, \mu, \omega, \gamma),
$$

where:

- `\pi` is payload mass
- `\sigma` is required state carriage
- `\rho` is framing burden
- `\mu` is monitoring continuity requirement
- `\omega` is scope demand
- `\gamma` is governance priority

Then the channel-selection problem is to compute a prop family `\mathcal{X}^*(m)` that maximizes fitness while minimizing blast radius:

$$
\mathcal{X}^*(m) =
\operatorname*{arg\,max}_{\mathcal{X} \in \mathfrak{P}}
\frac{
\operatorname{BW}(\mathcal{X}) \cdot \operatorname{Match}(\mathcal{X},m)
}{
\operatorname{Risk}(\mathcal{X}) \cdot (1 + \operatorname{DR}_{\mathcal{X}})
}.
$$

Equivalently, good orchestration is the art of matching the least dangerous sufficient prop to the message's real requirements.

## 17.1 Balls - Stateless Data Packets: Position, Accuracy, Timing

### 17.1.1 The Ball as Pure Payload

A ball has no internal state that materially affects a valid catch. Its spin is irrelevant. Its orientation is irrelevant. Its grip history is irrelevant once it is airborne. A clean reception depends on only two primary variables: where the ball lands and when it lands. This makes the ball the canonical model of **stateless transfer**.

Define the ball channel by

$$
\mathcal{B} = (\text{payload}, \text{position}, \text{timing}, \text{weight}).
$$

Here:

- `payload` is the content being conveyed
- `position` is the destination address in the crystal or pod space
- `timing` is the read quantum at which the packet should be handled
- `weight` is the processing burden imposed by the message

The defining law of the ball is that the receiver does not need to reconstruct the sender's hidden context in order to use the packet. The content is intended to be self-sufficient at the point of receipt.

Ball traffic is therefore optimal for:

- factual queries
- direct lookups
- table transfer
- list transfer
- structured outputs whose semantics are local and explicit

When no framing burden, hidden state, or full-pod governance condition is present, the ball is the default prop.

### 17.1.2 The Three Accuracy Dimensions

Ball accuracy decomposes into three independent dimensions.

**Height accuracy** measures whether the packet was thrown with the correct autonomy budget. In pod terms, this is whether the task arrived tagged with the correct processing depth and allowed time. Underthrowing forces a shallow response; over-throwing wastes cycle height and slows rhythm.

**Lateral accuracy** measures whether the packet lands in the correct catching zone. In pod terms, this is routing correctness. A valid packet delivered to the wrong specialist is still a channel failure.

**Temporal accuracy** measures beat alignment. A packet that arrives before the receiving agent is ready or after the read window closes is mistimed even if its content is correct.

These combine multiplicatively:

$$
\operatorname{Accuracy}(\mathcal{B}) =
A_{\text{height}} \cdot A_{\text{lateral}} \cdot A_{\text{temporal}}.
$$

This multiplicative law matters because each factor is load-bearing. High routing accuracy does not compensate for severe mistiming, and perfect timing does not redeem wrong-lane delivery. Practical mastery requires all three factors to remain simultaneously above operational threshold.

### 17.1.3 Ball Count: Single Through Quad

Ball count scales linearly at first because state overhead is minimal.

| Count | Physical reading | Channel reading | Canonical use |
| --- | --- | --- | --- |
| 1 ball | single toss | one-to-one packet | quick factual query |
| 2 balls | paired exchange | paired comparison | A/B validation or dual lookup |
| 3 balls | cascade or fountain | tri-pod data circulation | ordinary round-robin traffic |
| 4 balls | dense packet field | low-overhead multi-route flow | stable pod-scale traffic |

The ball is the easiest family to scale because coupling overhead is low. Additional balls increase throughput without drastically increasing state burden.

### 17.1.4 Ball Failure: The Dropped Packet

A dropped ball is the cleanest failure mode in the chapter. The packet was not received inside its valid window. The failure is explicit, local, and cheap to diagnose.

In pod coordination, a dropped ball usually means:

- the Orchestrator did not read an agent output in time
- the message landed outside the active read window
- the message was lost locally but did not silently corrupt downstream state

Recovery is correspondingly cheap. The packet can be re-thrown, re-queried, or re-read with only local rhythm damage. This is why ball traffic should dominate whenever the message does not require stronger physics.

## 17.2 Clubs - Stateful Packets: Rotation, Orientation, Grip

### 17.2.1 The Club as Persistent-State Carrier

A club is not merely a differently shaped ball. A club carries rotational state that the receiver must understand. The catch depends on spin count, orientation, and grip relation. This makes the club the natural model of **stateful handoff**.

Define the club channel by

$$
\mathcal{C} = (\text{payload}, \text{state}, \text{spin}, \text{orientation}, \text{grip}).
$$

Here:

- `payload` is the content being passed
- `state` is the sender's carried context
- `spin` is the processing depth or maturity of the work
- `orientation` is the correct entry point for reading
- `grip` is the continuation posture expected of the receiver

This family is correct when the packet cannot be separated from the process that produced it. Drafts, partial analyses, unresolved syntheses, and work-in-progress crystals are club traffic, not ball traffic.

### 17.2.2 The Club-Spin Algebra as Session-Handoff Protocol

Spin count is the chapter's maturity code.

- `flat` means raw source material
- `1` means first-pass output
- `2` means revised output
- `3` means verification-ready output

Let `\operatorname{spin}(A \to B)` denote the maturity contributed before handoff from agent `A` to agent `B`. Sequential refinement composes additively, but only up to the verified ceiling:

$$
\operatorname{spin}(A \to B) + \operatorname{spin}(B \to C) \leq 3.
$$

Thus:

- single-spin plus single-spin yields double-spin maturity
- double-spin plus single-spin saturates at triple-spin maturity
- triple-spin should not be rethrown as if it were merely more draft work; it should move to witness, replay, or certification

This algebra gives the Orchestrator a rigorous session-handoff rule. Not every handoff is equal. The receiver must know whether it is inheriting source, draft, or candidate claim.

### 17.2.3 Club Count: Single Through Triple

Club scaling is harder than ball scaling at every count because every catch is also a state read.

| Count | Physical reading | Channel reading | Canonical use |
| --- | --- | --- | --- |
| 1 club | single manipulation | one stateful handoff | passing one draft between agents |
| 2 clubs | reciprocal pass | two concurrent state streams | bidirectional draft exchange |
| 3 clubs | cascade | tri-pod state circulation | round-robin WIP coordination |
| 4 clubs | dense pattern | high-risk state mesh | reserved for mature pods only |

The cost of additional clubs is not merely more traffic. It is more simultaneous hidden context that must remain aligned.

### 17.2.4 Club Failure: The Knob-Catch

The knob-catch is the signature club failure. The packet is caught, but its state is misread. This is more dangerous than a dropped ball because the pattern continues under false interpretation.

In pod terms, the Orchestrator may:

- read a raw draft as a finished result
- read a verification-ready output as raw input
- misread the correct continuation mode for the receiver

The downstream pipeline continues, but corrupted state now propagates. Club traffic therefore requires active state verification at every handoff, not merely content ingestion.

## 17.3 Rings and Hoops - Framing Packets: Aperture, Geometry, Constraint

### 17.3.1 The Ring as Boundary Definition

A ring does not primarily transport payload. It defines the aperture through which valid content must pass. This makes the ring the correct prop family for **framing constraints**, schemas, contracts, and admissibility surfaces.

Define the ring channel by

$$
\mathcal{R} = (\text{aperture}, \text{plane}, \text{diameter}, \text{rigidity}),
$$

where:

- `aperture` defines what may pass
- `plane` defines which dimension is being constrained
- `diameter` defines tolerance width
- `rigidity` defines how strictly the constraint is enforced

Seeds, formatting contracts, proof obligations, and verification schemas belong naturally to this family. Rings tell the system not what to say, but what counts as saying it validly.

### 17.3.2 Ring Count: Single Through Triple

Ring count is constraint stacking.

| Count | Physical reading | Channel reading | Canonical use |
| --- | --- | --- | --- |
| 1 ring | single frame | one schema | one active contract |
| 2 rings | double frame | dual constraint | format plus witness |
| 3 rings | triple frame | triple admissibility gate | crystal plus proof plus compression |
| 4 rings | over-stack | near-empty valid set | decompose instead of stack |

The practical rule is that more than triple-ring framing usually becomes counterproductive. If four or more independent frames are needed, the task should usually be split rather than overconstrained.

### 17.3.3 Hoop Manipulation as Dynamic Constraint Adjustment

Real hoops do not remain static. They roll, tilt, widen, contract, and reorient. The corresponding communication principle is that framing contracts are dynamic rather than frozen.

The Orchestrator may need to:

- widen the aperture during exploratory phases
- tighten the diameter during closure
- rotate the plane when the wrong dimension is being constrained
- soften rigidity when the task has not yet earned hard admissibility

The ring family therefore models not only framing, but the live management of framing across a D/Q/I cycle.

### 17.3.4 Ring Failure: The Snag

A ring-snag occurs when the frame catches what should have passed through it. In pod terms, the constraint blocks all viable output. The agent is not failing; the admissibility aperture is misdrawn.

Typical symptoms include:

- repeated null output
- stalled expansion
- impossibly narrow formatting requirements
- proof demands that exceed current stage maturity

Recovery is an aperture operation: widen, rotate, soften, or temporarily remove the ring and revert to lower-constraint traffic.

## 17.4 Poi - Continuous Orbital Packets: VTG Geometry as Monitoring Protocol

### 17.4.1 The Poi as Always-On Monitor

Poi are sustained in orbit rather than released. They remain tethered under continuous tension. This makes poi the natural model for **continuous background monitoring**.

Define the poi channel by

$$
\mathcal{P} = (\text{orbit\_radius}, \text{plane}, \text{frequency}, \text{trace\_pattern}),
$$

where:

- `orbit_radius` sets monitoring scope
- `plane` selects the aspect being monitored
- `frequency` sets update rate
- `trace_pattern` sets monitoring mode

The defining feature of poi communication is that the channel remains live while other traffic continues. Poi do not replace balls or clubs; they watch them.

### 17.4.2 The VTG Trace Families as Monitoring Modes

Visual Trace Geometry provides a precise monitoring vocabulary.

| VTG family | Physical trace | Monitoring protocol | Canonical use |
| --- | --- | --- | --- |
| extension | expanding or contracting circles | scope adjustment | widen or narrow research radius |
| flower | repeated petal cycle | cyclic multi-aspect review | cover `n` subtopics repeatedly |
| isolation | fixed-point hover | invariance testing | hold one claim constant while context moves |
| cap | synchronized dual orbits | correlated dual monitoring | track complementary agents together |
| antispin | inward-pointing petals | convergence monitoring | track collapse toward zero-point |

The point is not metaphorical ornament. The VTG families give the Orchestrator a typed library for continuous observation.

### 17.4.3 Poi Count: Single Through Quad

Poi count measures simultaneous background awareness.

| Count | Physical reading | Channel reading | Canonical use |
| --- | --- | --- | --- |
| 1 poi | single tether | one live monitor | one background agent |
| 2 poi | standard pair | dual monitor | the default two-channel watch field |
| 3 poi | extended body pattern | tri-monitor field | advanced pod monitoring |
| 4 poi | full-body mode | monitoring-only field | maximal observation with minimal active throws |

At high count, poi trade active intervention capacity for persistent awareness. Quad-poi is therefore best understood as monitoring-only mode rather than mixed traffic mode.

### 17.4.4 Poi Failure: The Tangle

The poi failure is the tangle. The monitor does not disappear, but orbital freedom collapses into knotting. In pod terms, the Orchestrator becomes fixated on one detail and loses the wider trajectory.

The recovery law is:

1. stop the knotting feedback
2. clear the fixation
3. re-establish the orbit deliberately

Poi traffic therefore trains the Orchestrator to distinguish attention from fixation.

## 17.5 Staff - Broadcast Channels: Extended Reach and Lever Mechanics

### 17.5.1 The Staff as Full-Pod Broadcast

A staff spans the whole active workspace. When it moves, everything must clear its path. This makes the staff the proper model of **broadcast and override**.

Define the staff channel by

$$
\mathcal{S} = (\text{payload}, \text{scope} = \text{ALL}, \text{priority} = \text{OVERRIDE}, \text{lever\_arm}).
$$

The essential properties are:

- scope is global to the pod
- priority overrides local traffic
- leverage amplifies the effect of one motion across the whole field

This family should be used for:

- pod-wide seed updates
- global resets
- session start or stop directives
- synchronized governance maneuvers
- full-pod priority changes

### 17.5.2 Staff Count: Single Through Double

Staff count scales aggressively and therefore must remain tightly bounded.

| Count | Physical reading | Channel reading | Canonical use |
| --- | --- | --- | --- |
| 1 staff | single sweep | one full-pod broadcast | standard governance action |
| 2 staves | dual sweep | dual concurrent broadcast | seed plus binding constraint |
| 3 staves | saturated field | governance flood | generally unlawful in practice |

Two staves already approach the threshold beyond which governance traffic begins to crowd out productive work.

### 17.5.3 Contact Staff as Continuous Governance

Contact staff does not operate by discrete release and recatch. It rolls continuously across the body. This is the correct physical analogue for **continuous governance**: the Orchestrator is shaping the full pod in real time through continuous micro-adjustment rather than punctuated broadcast.

This mode is powerful but expensive. It is appropriate only when whole-pod coherence matters more than local autonomy.

### 17.5.4 Staff Failure: The Collision

The staff collision is the most expensive failure in the chapter. A bad sweep disrupts the entire workspace. In pod terms, an ambiguous or contradictory broadcast scrambles all agents at once.

This is why staff traffic must be rare, deliberate, and pre-verified. The broader the scope, the stronger the admissibility requirement before release.

## 17.6 The Unified Prop x Count Bandwidth Matrix

### 17.6.1 The Complete Channel Selection Table

The five families form a golden progression in usable bandwidth and corresponding risk:

| Prop family | Channel type | Relative bandwidth | Canonical failure | Failure radius | Typical recovery |
| --- | --- | --- | --- | --- | --- |
| Ring | framing constraint | `phi^-1` | snag | local block | 2-3 beats |
| Poi | continuous monitor | `phi^-1` | tangle | narrowed awareness | 3-4 beats |
| Ball | stateless packet | `1` | drop | local miss | 1-2 beats |
| Club | stateful handoff | `phi` | knob-catch | downstream propagation | 3-5 beats |
| Staff | broadcast override | `phi^2` | collision | pod-wide disruption | 5+ beats |

The progression matters for two reasons. First, it establishes that throughput and blast radius rise together. Second, it demonstrates that channel selection is a risk-bandwidth tradeoff rather than a prestige hierarchy.

### 17.6.2 State-Complexity Hierarchy

Bandwidth alone is insufficient. Each family also carries a different state-complexity burden.

Define channel state complexity `\kappa` by the number of hidden variables that must be held correctly for lawful use:

$$
\kappa(\mathcal{B}) = 0,\qquad
\kappa(\mathcal{R}) = 1,\qquad
\kappa(\mathcal{P}) = 2,\qquad
\kappa(\mathcal{C}) = 3,\qquad
\kappa(\mathcal{S}) = 4.
$$

The ordering is justified as follows:

- balls carry no hidden continuation state
- rings add one framing layer
- poi add continuous orbital state
- clubs add carried sender state plus maturity and orientation burden
- staffs add global coupled-state burden because the entire pod must remain consistent under the broadcast

Thus the operational hierarchy is:

$$
\mathcal{B} < \mathcal{R} < \mathcal{P} < \mathcal{C} < \mathcal{S}
$$

with respect to state-complexity burden.

### 17.6.3 Count Scaling Law

Let `n` be prop count. Then effective bandwidth is not simply `n` times single-prop bandwidth because coupling overhead grows with count:

$$
\operatorname{EffBW}(\mathcal{X}, n)
=
n \cdot \operatorname{BW}(\mathcal{X}) \cdot Y(\mathcal{X},n),
$$

where `Y(\mathcal{X},n)` is the yield factor after coupling overhead, collision burden, and recovery fragility are applied.

For balls, `Y` decays slowly.  
For clubs, `Y` decays faster because state alignment grows combinatorially.  
For rings, `Y` decays through over-constraint.  
For poi, `Y` decays through attention fragmentation.  
For staffs, `Y` decays sharply because global collision risk dominates.

This explains why pod maturity is not measured by how many channels can be opened in theory, but by which families remain clean as count rises.

### 17.6.4 The Channel Selection Protocol

Let

$$
\operatorname{Match}(\mathcal{X},m)
=
w_{\pi} M_{\pi} + w_{\sigma} M_{\sigma} + w_{\rho} M_{\rho}
+ w_{\mu} M_{\mu} + w_{\omega} M_{\omega} + w_{\gamma} M_{\gamma},
$$

where each `M_*` scores the fit between the message's requirement and the channel family's physics. Then the Orchestrator selects

$$
\mathcal{X}^*(m) =
\operatorname*{arg\,max}_{\mathcal{X} \in \mathfrak{P}}
\frac{
\operatorname{EffBW}(\mathcal{X},n)\cdot \operatorname{Match}(\mathcal{X},m)
}{
\operatorname{Risk}(\mathcal{X})\cdot (1+\operatorname{DR}_{\mathcal{X}})
}.
$$

Operationally, the rule reduces to:

- default to **balls** for routine packets
- upgrade to **clubs** when process state must travel
- use **rings** when the primary need is framing or admissibility
- use **poi** when the channel is observational and continuous
- use **staff** only when the message truly must reach and override the whole pod

The physics of communication channels is therefore not a metaphor layered on top of juggling. It is a lawful transfer of juggling physics into orchestration theory.

## Chapter 17 Zero-Point Compression

Each prop family realizes a distinct communication law: balls carry stateless payload under position-and-timing physics; clubs carry stateful process under spin-and-orientation physics; rings carry admissibility under aperture-and-rigidity physics; poi carry continuous monitoring under orbital trace physics; staffs carry governance under full-field leverage physics. Bandwidth scales through a golden progression, state-complexity rises with hidden coordination burden, and count amplifies both yield and coupling cost. The Orchestrator's task is therefore not merely to send a message, but to choose the correct physical law under which that message should move.

CHAPTER 17 - PROP TYPES: THE PHYSICS OF COMMUNICATION CHANNELS
