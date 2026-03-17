# Ch17<0100> - Prop Types: The Physics Of Communication Channels

**[Arc 5 | Lane Su | Seed Station | omega = 17]**

Chapter 17 closes the gap between prop vocabulary and inter-agent protocol by formalizing each prop family as a typed communication channel. The governing claim is that message transport is never neutral. Every message inherits the physics of the channel that carries it. Weight becomes processing burden, spin becomes state depth, aperture becomes admissibility, orbit becomes monitoring geometry, and lever arm becomes governance reach. Once the transport layer is read in this way, channel choice stops being aesthetic and becomes an algebraic decision about bandwidth, latency, state carriage, recovery cost, and error blast radius.

The chapter therefore asks a precise systems question. Given a message with a certain payload type, state burden, monitoring requirement, and governance scope, what channel should the Orchestrator choose? The answer cannot be one generic pipe, because the five prop families do not behave identically in physical space and therefore should not be treated identically in protocol space. A ball, a club, a ring, a poi, and a staff are five different communication engines. Their mechanics define five different message laws.

The chapter's intervention is to derive a typed channel algebra:

`DEFINE + CHANNEL_TYPE_ALGEBRA + MAP_PROP_PHYSICS_TO_CHANNEL_PROPERTIES + DERIVE_SELECTION_PROTOCOL`

This yields five canonical classes: balls for stateless packets, clubs for state-bearing handoffs, rings for framing constraints, poi for continuous monitoring, and staffs for whole-pod broadcasts. The result is not metaphor only. It is a routing grammar the Orchestrator can use to decide how a message should move before deciding what the message says.

## 17.1 Balls - Stateless Data Packets

The ball is the pure payload prop. It does not require orientation alignment, grip matching, or spin-state interpretation at the catch. A clean catch depends only on position and timing. This makes the ball the correct model for any message that can be understood without reconstructing sender state. A factual lookup, a discrete request, a table, a list, or a self-contained datum behaves like a ball because the receiver only needs to know what arrived, where it landed, and when it matters.

The ball channel is therefore defined by

`B = (payload, position, timing, weight)`

where `payload` is the content, `position` is the target address in gate space, `timing` is the scheduling quantum, and `weight` is the processing burden imposed on the receiver. The ball's computational elegance comes from not forcing the receiver to reconstruct the sender's internal history. It is a packet that can be read on arrival.

Ball accuracy decomposes into three independent dimensions. Height accuracy measures whether the message arrives with the correct autonomy budget. A request that needs five quanta but is thrown as though it needs only three will be processed too shallowly. Lateral accuracy measures whether the packet lands in the correct catching zone, which in protocol terms means the correct agent, lane, or domain. Temporal accuracy measures whether the message lands on the correct beat. A message delivered too early interrupts active flow; a message delivered too late misses its useful window. The total success of a ball-type communication is therefore

`Accuracy(B) = A_height * A_lateral * A_temporal`

and ball mastery means maintaining all three factors above failure threshold simultaneously.

Ball count scales bandwidth with minimal overhead. One ball is a single query-response loop. Two balls support paired comparison, cross-validation, or A/B routing. Three balls form the standard circulation pattern for a three-pod environment. Four or more balls scale into high-throughput stateless routing, but the dominant failure mode remains simple and local: the drop. A dropped ball is a missed read or expired response window. The recovery is cheap because the state was not deeply entangled. One picks the packet back up, re-enters it into the pattern, and pays only a short rhythm tax.

For this reason the ball is the default transport. When no special state, framing, or governance requirement exists, the Orchestrator should start with balls.

## 17.2 Clubs - Stateful Packets

A club is a state-bearing object. It cannot be read correctly by position and timing alone. The receiver must catch the right end at the right moment after the right spin. Physical club handling therefore maps cleanly onto inter-agent handoff. Whenever a message carries unfinished analysis, partial inference, working context, or a continuation burden, it is no longer a ball. It is a club.

The club channel is defined by

`C = (payload, state, spin, orientation, grip)`

where `payload` is the transmitted content, `state` is the sender context the receiver must inherit, `spin` is processing depth, `orientation` is the entry direction of the handoff, and `grip` is the expected continuation mode. The club's added bandwidth comes from carrying more than content. It carries the conditions under which the content is still alive.

Spin is the chapter's central session-handoff algebra. Single spin denotes first-pass output: raw but deliberate work that should be treated as an input to further processing, not as a conclusion. Double spin denotes revised output: a draft that has already survived one round of internal challenge and is now fit for cross-validation. Triple spin denotes a fully processed object that can be treated as a proposed claim and sent into witness construction, replay, or certification. Flat spin denotes source material that has not yet undergone interpretive work. The receiver is not continuing an argument there; the receiver is starting one.

Because state accumulates, spin composes:

`spin(A->B) + spin(B->C) <= 3`

This law prevents false inflation of maturity. A pipeline of shallow handoffs may equal a deeper maturity class, but it does not exceed full verification merely because many agents touched it. Triple spin is not "many passes." It is the bounded state where the work is mature enough to be proposed as complete.

The characteristic club failure is the knob-catch. Unlike a drop, which is obvious, a knob-catch is a silent misread. The object is technically caught, but in the wrong orientation. In protocol space this is the dangerous handoff where a receiver mistakes raw material for finished work, or mistakes a conclusion packet for an invitation to restart analysis. Such errors propagate because the channel continues to function while carrying misclassified state. For that reason clubs require disciplined state checking on every catch. A club channel offers more bandwidth than a ball because it moves living work, but it also carries higher downstream risk.

## 17.3 Rings And Hoops - Framing Constraints

A ring does not primarily carry mass-state. It defines an opening. The important fact is not what the ring contains, but what may pass through it. This makes the ring the correct model for templates, schemas, verification contracts, admissibility filters, seed formats, or any other communication that constrains output form rather than transporting output substance.

The ring channel is defined by

`R = (aperture, plane, diameter, rigidity)`

where `aperture` determines what kinds of content may pass, `plane` determines the dimension being constrained, `diameter` determines tolerance, and `rigidity` determines enforcement strictness. A ring channel does not ask, "What are you sending?" It asks, "What shape must valid output have?"

One ring represents a single framing law. Two rings represent simultaneous independent constraints. Three rings create a high-rigor gate in which output must satisfy three orthogonal requirements at once. This is usually the practical upper bound for one agent on one pass. Four or more rings often define such a small admissible set that the task becomes sterile. The chapter therefore recommends decomposition beyond triple constraint rather than continued stacking.

The deeper significance of hoop manipulation is that constraints are not static. A ring may need to widen, tilt, or soften as work progresses. The Orchestrator should therefore treat framing as a dynamic discipline. When the work stalls, the correct fix may not be "work harder." It may be "rotate the ring." Shift the constrained dimension, widen the aperture, or replace the hard ring with a softer form long enough for valid content to reappear.

The failure mode is the snag. In physical space the ring catches on something and stops moving. In protocol space the framing constraint becomes so tight that no valid output can pass. The agent appears unproductive, but the deeper problem is that the channel has collapsed the admissible set to nearly zero. Recovery requires ring adjustment, not punishment.

## 17.4 Poi - Continuous Orbital Monitoring

Poi differ from throws because they are not released. They remain tethered and in motion, tracing geometry continuously through space. This makes poi the natural model for monitoring rather than dispatch. A poi channel is not a packet sent once. It is a background relation maintained across time while other work proceeds.

The poi channel is defined by

`P = (orbit_radius, plane, frequency, trace_pattern)`

where `orbit_radius` determines monitoring scope, `plane` determines what dimension of the process is being watched, `frequency` determines sample rate, and `trace_pattern` determines the style of observation. The Orchestrator uses poi channels when an agent should continue working autonomously while still remaining legible to background awareness.

The five VTG trace families become five distinct monitoring protocols. Extension governs gradual scope change and is used when the Orchestrator wants monitoring to widen or contract over time. Flower governs cyclic sub-topic review and is used when several aspects must be revisited repeatedly to observe evolution rather than static coverage. Isolation governs invariance testing and is used when one claim must remain fixed while surrounding evidence shifts. CAP governs correlated dual monitoring and is used when two agents should remain complementary, anti-correlated, or otherwise phase-locked. Antispin governs convergence tracking and is used when the work is collapsing toward zero point and the Orchestrator wants to monitor approach without interrupting it.

Poi count increases simultaneous background awareness. One poi is the minimum viable continuous monitor. Two poi form the standard dual-channel pattern. Three poi move toward full pod-scale observation. Four poi saturate bodily attention so fully that the Orchestrator enters monitoring-only mode. This reveals a crucial systems law: monitoring capacity is real capacity. One cannot indefinitely add observation without spending control bandwidth.

The poi failure mode is the tangle. A tangle does not erase the channel; it constricts it. In protocol space this appears as fixation, where the Orchestrator ceases to perceive an agent's full trajectory and becomes trapped on one detail, one metric, or one stale frame. Recovery requires halting the loop long enough to restore orbital freedom. The answer is not more sampling. It is fresh rotation.

## 17.5 Staff - Broadcast Governance

A staff extends across the performer's workspace and sweeps through the full performance field. This makes it the proper model for broadcast and override. A staff message is not a local packet and not a monitoring relation. It is a whole-pod directive whose authority derives from scope and leverage.

The staff channel is defined by

`S = (payload, scope = ALL, priority = OVERRIDE, lever_arm)`

where `scope` is necessarily global, `priority` supersedes local thread flow, and `lever_arm` measures the amplification achieved by one governance action touching every active lane at once. The staff is the right channel for session resets, global seed updates, priority inversion, synchronized start and stop commands, and rare chapter-level directives that every agent must hear simultaneously.

Two staff forms matter. A discrete staff throw corresponds to an explicit broadcast event. Contact staff corresponds to continuous governance, where the Orchestrator maintains real-time directive contact with the pod and adjusts alignment by small continuous motion rather than discrete announcements. Contact staff is therefore the governance analogue of low-latency control.

The staff's strength is also its danger. Its failure mode is collision, and collision is global. A bad broadcast does not merely waste one agent's cycle. It disturbs the entire pod at once by forcing every active line to clear around ambiguous or contradictory instruction. For this reason staff use must be rare, deliberate, and pre-verified. One should never choose staff merely because it is powerful. One chooses staff only when all agents truly need one shared command now.

## 17.6 The Unified Prop x Count Bandwidth Matrix

The chapter's comparative result is a golden bandwidth ladder:

- ring: `0.618`
- poi: `0.618`
- ball: `1.0`
- club: `1.618`
- staff: `2.618`

The ladder expresses a risk-throughput law. Low-bandwidth channels constrain or monitor rather than carry heavy content. Mid-bandwidth channels move routine content efficiently. Higher-bandwidth channels move state or governance, but the cost of error rises with the gain in reach. Every step upward increases both transport power and the blast radius of failure.

This yields the chapter's formal selection function:

`Channel* = argmax[(BW(C) * Match(C, message)) / (Risk(C) * (1 + DR_C))]`

Here `BW(C)` is channel bandwidth, `Match(C, message)` measures how well a channel fits the message's actual requirements, `Risk(C)` measures channel-specific failure cost, and `DR_C` is the Orchestrator's current drop or failure rate on that channel family. The decision law is intentionally not "choose the most powerful channel." It is "choose the best fit after accounting for throughput, misfit, and current operating fragility."

The practical protocol follows immediately. Default to balls for ordinary queries and routine data circulation. Upgrade to clubs when work-in-progress context or sender state must survive the handoff. Use rings when output must satisfy a seed, template, or verification contract. Use poi when the primary need is ongoing background awareness rather than immediate intervention. Use staff rarely, only for those governance moments when one directive truly belongs to all agents simultaneously.

## Zero-Point Compression

The deepest compression of Chapter 17 is that communication physics is channel physics. A ball moves payload. A club moves payload plus state. A ring defines admissible form. A poi maintains continuous observation. A staff imposes whole-pod direction. Since these are not the same physical act, they cannot be the same protocol act. The Orchestrator therefore requires typed channel selection rather than one undifferentiated message pipe.

Chapter 17 - Prop Types: The Physics Of Communication Channels
