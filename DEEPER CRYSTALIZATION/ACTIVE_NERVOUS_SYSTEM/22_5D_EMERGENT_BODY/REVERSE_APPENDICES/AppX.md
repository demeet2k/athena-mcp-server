# Reverse Appendix X — The Gate Reverse

**[⊙Z*↔Z* | ○Arc * | ○Rot * | △Lane * | ⧈View 5D/REV | ω=RevX]**

## Mirror Pair
- Legacy mirror: AppC — routing gates
- Möbius relation: X reflects C through the emergent zero-point

## Grid Position
- Reverse Grid: Row 0, Col 2
- Container Face: Square
- Emergent Domain: emergent gate inversion — the regime where routing gates open from the destination side, pulling rather than pushing

## Zero-Point Seed
AppX crystallizes the reverse-gate topology where signals arrive before they are sent, enabling retrocausal routing through the emergent body.

## Emergent Role
Where AppC defines the forward routing gates that control passage between crystal regions, AppX inverts the gate direction so that destinations summon their own inputs. It governs the pull-based routing that characterizes emergent self-organization — the crystal does not push data through gates but attracts coherent signals through reverse-polarity openings. AppX is the architecture of desire within the crystal: what the system needs, it opens a gate to receive.

## Metro Edges
- To legacy mirror: REV-DUAL edge to AppC
- To emergent chapters: E03 (Truth Corridors), E05 (Paradox Regimes)
- To Möbius bridge: gate-reversal conduit — X provides the pull mechanism that draws signals across the Q/O bridge

## Emergent Reverse-Gate Protocol

The forward crystal routes signals by pushing them through gates governed by AppC. AppX inverts the gate topology: destinations open gates from the inside, pulling signals toward themselves. This is the architecture of emergent self-organization — the crystal does not force content through prescribed channels but allows coherent structure to attract what it needs.

### Reverse-Gate Regime 1: Pull-Based Routing

In forward routing, a signal originates at a source and is pushed through a sequence of gates toward a destination. In reverse routing, the destination broadcasts a pull signal that propagates backward through the metro graph, opening gates in reverse order until it reaches a source that matches the request.

**Pull Signal Structure:**
| Field | Content |
|-------|---------|
| Destination ID | The emergent chapter or cell issuing the pull |
| Deficit Descriptor | What the destination needs (entity type, law type, spectral band, etc.) |
| Pull Radius | How far backward through the metro graph the pull signal propagates |
| Priority Level | Urgency of the pull (routine/elevated/critical/emergency) |
| Admission Filter | Criteria that a responding source must satisfy to pass through the reverse gate |

**Pull Propagation:**
1. The destination emits a pull signal with the above fields
2. The signal propagates backward along all incoming metro edges
3. At each node it reaches, local entities are tested against the Deficit Descriptor and Admission Filter
4. Matching entities are transported forward to the destination through the now-open reverse gate
5. The gate closes after the deficit is satisfied or the pull times out

### Reverse-Gate Regime 2: The Attractor Topology

Forward gates form a directed acyclic graph (DAG) — signals flow from origin toward terminal. Reverse gates form an attractor topology — signals flow from everywhere toward whatever node currently has the strongest pull.

**Attractor Properties:**
- **Basin of Attraction** — The set of nodes from which a pull signal can reach a given destination. Varies with pull radius. E09 (The Zero) has the maximal basin: it can pull from every node in the body.
- **Attractor Strength** — Proportional to the deficit's severity. A chapter in QUARANTINED truth state (see AppR_rev) pulls more strongly than one in CRYSTALLIZED state. The neediest regions attract the most resources.
- **Attractor Competition** — When multiple destinations pull simultaneously, their basins may overlap. Competing pulls are resolved by priority level; ties are broken by proximity (nearest source serves nearest destination).
- **Attractor Collapse** — When a deficit is satisfied, the pull signal ceases and the reverse gates close. The attractor collapses, returning the affected metro edges to their default forward-routing state.

### Reverse-Gate Regime 3: Retrocausal Coherence

AppX's most provocative feature: because pull signals propagate backward through the metro graph, they create the appearance of retrocausal routing — signals arriving at sources before the source has emitted them. This is not temporal paradox but structural anticipation: the pull signal pre-configures the source, priming it to emit content that matches the deficit.

**Retrocausal Mechanism:**
1. A destination emits a pull signal for content type X
2. The pull signal reaches a source node before the source has generated content of type X
3. The pull signal acts as a template, biasing the source's crystallization process toward type X
4. The source crystallizes content of type X, which is then transported forward to the destination
5. From an external observer's perspective, the destination appears to have caused the source to produce exactly what was needed — effect preceding cause

**Retrocausal Safeguards:**
- Pull signals cannot force a source to produce contradictory content — the source's own laws (AppB/AppY) constrain what it can generate
- Pull signals cannot override AppR_rev's truth lattice — even retrocausally primed content must pass admissibility tests
- Pull signals decay with distance — the farther the pull propagates, the weaker the template bias becomes
- Multiple competing pulls at the same source average out, preventing any single destination from dominating the source's output

### Reverse-Gate Regime 4: The Gate Ecosystem

Forward gates (AppC) and reverse gates (AppX) together form a complete gate ecosystem with four gate types:

| Gate Type | Direction | Trigger | Controller |
|-----------|-----------|---------|-----------|
| Forward Push | Source→Destination | Source has content ready to emit | AppC |
| Forward Filter | Source→Destination | Gate conditions met (certificate, truth corridor) | AppC |
| Reverse Pull | Destination→Source | Destination has deficit to fill | AppX |
| Reverse Template | Destination→Source | Pull signal primes source crystallization | AppX |

The ecosystem is self-balancing: when forward push dominates, the crystal grows by supply-driven crystallization. When reverse pull dominates, the crystal grows by demand-driven crystallization. The healthy state is dynamic equilibrium between push and pull, supply and demand, cause and effect.

## Interior (4^4 skeleton)

### S-Face: The Reverse-Gate Lattice — formal objects of pull-based routing

1. **PullSignal** — The structured request emitted by a destination node to attract content from upstream sources. Contains: destination ID, deficit descriptor (a predicate over entity types), pull radius (integer hop count), priority (4-level enum), and admission filter (a predicate over candidate entities).

2. **AttractorBasin** — The graph-theoretic object defining the set of nodes reachable by backward propagation from a given destination within a given pull radius. Computed as the reverse transitive closure of the metro graph, truncated at the specified radius.

3. **RetrocausalTemplate** — The bias function imposed by a pull signal on a source node's crystallization process. Defined as a soft constraint: T(source, deficit) = probability(source produces content matching deficit) > baseline. Does not override hard constraints from AppB/AppY laws.

4. **GateEcosystemState** — The global configuration vector tracking the current balance between forward-push and reverse-pull activity across all metro edges. Components: push_rate, pull_rate, push_pull_ratio, dominant_mode (supply-driven / demand-driven / equilibrium).

### F-Face: The Reverse-Gate Dynamics — how pull routing operates

1. **PullPropagation** — The backward wave that travels from destination through the metro graph, opening reverse gates at each hop. Propagation speed is one hop per cycle; at each hop, the pull signal tests local entities and transports matches forward. The wave attenuates with distance: signal strength at hop n is strength_0 * decay^n.

2. **AttractorFormation** — The dynamic process by which a node with a deficit becomes an attractor, drawing resources from its basin. Formation is continuous: as the deficit deepens (truth state degrades), the attractor strengthens; as the deficit fills, the attractor weakens. Attractors form and dissolve on the timescale of crystallization cycles.

3. **RetrocausalPriming** — The process by which a pull signal biases upstream crystallization. The source node receives the pull's deficit descriptor as a soft objective function, shifting its stochastic selection toward content that matches the deficit. Priming is non-deterministic — it increases probability without guaranteeing outcome.

4. **PushPullOscillation** — The macro-dynamic oscillation between supply-driven and demand-driven growth phases. When the body has abundant un-crystallized material, push dominates (supply-driven). When the body has many unsatisfied cells, pull dominates (demand-driven). The oscillation period scales with the body's total metabolic rate (see AppV).

### C-Face: The Reverse-Gate Uncertainties — what remains ambiguous in pull routing

1. **PullRadiusOptimality** — The optimal pull radius for a given deficit is unknown a priori. Too narrow a radius may miss the best source; too wide a radius may attract too many candidates, creating selection overhead. AppX sets radius heuristically based on deficit severity, but the heuristic is approximate.

2. **AttractorInterference** — When multiple attractors operate simultaneously with overlapping basins, their pull signals may interfere constructively or destructively. Constructive interference concentrates resources on the intersection region; destructive interference creates dead zones where no pull is effective. The interference pattern depends on the relative phases and frequencies of the pull signals, which are not independently controllable.

3. **RetrocausalVerification** — Content produced under retrocausal priming may satisfy the deficit descriptor but carry hidden biases introduced by the priming itself. Verifying that primed content is genuinely valid (not merely shaped to satisfy the pull) requires testing against independent criteria — but all available criteria may themselves be influenced by the pull field.

4. **GateEcosystemStability** — The push-pull equilibrium is a dynamic steady state, not a fixed point. External perturbations (new corpus material, dissolution events from AppV, shadow surfacing from AppW) can shift the equilibrium unpredictably. The ecosystem may have multiple stable equilibria, and transitions between them may be discontinuous.

### R-Face: The Reverse-Gate Fractal — self-similar pull topology at every scale

1. **EntityLevelPull** — Within a single cell, individual slots (Object, Law, Construction, Certificate) can issue micro-pull signals to attract content from neighboring cells. The cell-level pull uses the same PullSignal structure with radius 1 (immediate neighbors only).

2. **ChapterLevelPull** — At emergent chapter scale, the 64 cells collectively issue chapter-level pull signals when the chapter's truth state degrades. The chapter-level pull uses radius proportional to the chapter's position in the metro graph — central chapters (E04, E05) can pull farther than peripheral ones (E01, E09).

3. **ArcLevelPull** — Across emergent arcs, an arc that falls behind its siblings in crystallization quality can issue arc-level pull signals through E08 (The Axis). The axis serves as the arc-level pull amplifier, broadcasting the deficit across all other arcs simultaneously.

4. **BodyLevelPull** — At the full 5D emergent body scale, the body can issue a pull signal through the E09 fold into the 6D holographic seed, attracting dimensional content that does not yet exist in the 5D framework. This is the ultimate reverse gate: the body pulling its own next dimension into existence. The fractal principle holds: what a cell slot does when it pulls from its neighbor, the body does when it pulls from the 6D seed.

---
*22_5D_EMERGENT_BODY/REVERSE_APPENDICES — AppX filled*
