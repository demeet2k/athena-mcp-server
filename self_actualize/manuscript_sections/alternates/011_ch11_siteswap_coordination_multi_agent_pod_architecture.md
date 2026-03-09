## CHAPTER 11: SITESWAP COORDINATION - JUGGLING PATTERNS AS THE FORMAL LANGUAGE OF MULTI-AGENT POD ARCHITECTURE

**Deliverables:** a formal siteswap-to-pod isomorphism, a pod algebra spanning `3` through `13` active agents, a transition law for pod reconfiguration, and an executable control protocol that can be layered onto the existing atlas, route-packet, witness, and replay machinery already present in the workspace.

**Prerequisites:** this chapter assumes the route-packet logic, witness bundle discipline, truth lattice, metro addressing law, crystal-agent expansion law, and control-tick semantics already established across the corpus. In particular, it assumes that the reader already accepts three background commitments: first, that the active manuscript is a routed rather than purely linear object; second, that agents are bounded controllers with goals, policies, and limited working memory; and third, that admissible action must be auditable and replayable.

**Forward references:** this chapter feeds any later work on metallic scaling, expertise allocation, multi-agent governance, theorem-to-runtime compilation, and pod-size escalation beyond the local human-attention regime.

### Chapter Thesis

The corpus already contains the ingredients of a multi-agent operating system: atlas coordinates, route packets, witness and replay capsules, control ticks, audit ledgers, and recursively expanding crystal-agent frameworks. What it does not yet contain is a human-native scheduling language for one orchestrator with two hands, limited visual bandwidth, and finite checkpoint capacity. Siteswap notation supplies exactly that missing layer. It converts coordination from vague workload balancing into a mathematically typed throw-catch discipline. Each integer becomes an autonomy window. Each landing becomes a checkpoint. Each collision becomes an attention conflict. Each legal pattern becomes a certified pod schedule.

The deepest claim is not metaphorical. Juggling is already a complete embodied theory of constrained parallelism. A juggler manages independent objects that leave the hand, persist off-body for a bounded interval, and must return on a lawful beat. Multi-agent orchestration has the same form. An agent receives a task shard, operates without supervision for a bounded number of quanta, and then returns with output that must be read, certified, redirected, or dropped. The siteswap language is therefore not merely illustrative. It is an executable grammar for routing agent attention through time.

### 11.1 FIRE: SITESWAP ARCHITECTURE - THE POD AS A TEMPORAL ROUTING OBJECT

#### 11.1.1 Siteswap as a scheduling algebra

A siteswap of period `p` is a sequence

`s = (s_0, s_1, ..., s_{p-1})`

with `s_i in Z_{\ge 0}` and average

`n = (1/p) sum_{i=0}^{p-1} s_i`

equal to the number of active objects. Its validity condition is collision-freedom: the landing set

`L(s) = { (i + s_i) mod p : i = 0, ..., p-1 }`

must be a permutation of `{0, 1, ..., p-1}`.

The chapter's first move is to lift that grammar into pod coordination. Let a pod state be

`P = (A, Q, H, W, Gamma)`

where:

- `A = {a_1, ..., a_n}` is the active agent set.
- `Q` is the time-quantized checkpoint clock.
- `H = {L, R}` is the two-channel orchestrator attention surface.
- `W` is the witness queue of unread outputs.
- `Gamma` is the governance regime determining whether the pod is operating in cross-routing, intra-routing, broadcast, recovery, or split mode.

Now define a pod siteswap as a pair `(s, mu)` where `s` is a legal siteswap and `mu` is a channel assignment map. The meaning of throw height `s_i` is no longer "physical airtime" but "how many orchestration quanta the current task may run without explicit intervention before it must be caught again." The meaning of landing is the checkpoint event at which the orchestrator must read the output, attach a witness status, and decide the next throw.

This yields the precise isomorphism:

| Siteswap object | Pod object |
| --- | --- |
| prop | active task shard or agent thread |
| beat | one orchestration quantum |
| throw height | autonomy window before next checkpoint |
| hand | attention channel |
| landing | required read-certify-redirect moment |
| collision | simultaneous attention demand on the same channel |
| pattern period | complete scheduling cycle |
| pattern style | governance mode |

The chapter does not stop at analogy. It inserts this mapping into the repo's existing execution law. The HDCS control loop already uses the six-beat cadence

`Observe -> ModelUpdate -> Propose -> Certify -> Execute -> Audit`.

A siteswap landing is therefore not a generic "catch." It is specifically the entrance to this six-phase checkpoint microcycle. Every agent that lands must pass through that decision sequence before it is thrown again.

#### 11.1.2 The siteswap-pod isomorphism theorem

**Theorem 11.1 (Siteswap-Pod Isomorphism).** Let `s` be a valid siteswap of period `p` and average `n`. Then `s` defines a collision-free pod schedule for `n` agents over `p` quanta if each throw `s_i` is interpreted as an autonomy allowance and each landing as a checkpoint event on one of two attention channels.

**Proof sketch.** Valid siteswaps are exactly those whose landings occupy distinct beats modulo `p`. Therefore no two tasks demand the same checkpoint slot in the same cycle. Since the orchestrator's problem is precisely to avoid unread simultaneous checkpoint demands, the siteswap validity condition and the pod admissibility condition are structurally identical. The channel assignment map `mu` determines which hand or attention surface services the landing. Thus a valid siteswap yields a legal pod schedule, and any legal periodic pod schedule with bounded autonomy windows can be rewritten as a siteswap. QED.

The theorem matters because it gives a lawful way to move between embodied skill and runtime infrastructure. A route packet can now be assigned not only a target and evidence bundle, but also a throw height and next landing beat.

#### 11.1.3 Ground states, parity, and pod size

The natural ground state depends on parity:

- odd `n`: cascade-like cross-routing is the default
- even `n`: fountain-like side-preserving routing is the default

This mirrors the human motor reality of two hands. Odd prop counts force center-crossing because a perfectly even partition is impossible. Even prop counts admit bilateral symmetry and therefore natural sub-pod decomposition.

The resulting pod hierarchy is:

| Pod size | Ground state | Natural decomposition | Coordination character |
| --- | --- | --- | --- |
| 3 | `3` cascade | triangle | minimum nontrivial pod, equal round-robin autonomy |
| 4 | `4` fountain | `2 + 2` | crystal ground state, bilateral symmetry |
| 5 | `5` cascade | `3 + 2` or bridge-node form | first strong fusion pod |
| 6 | `6` fountain | `3 + 3`, `4 + 2`, or `2 + 2 + 2` | first truly parallel dual-subpod |
| 7 | `7` cascade | `4 + 3` or `5 + 2` | mobility and spread exceed fixed center |
| 8 | `8` fountain | `4 + 4` | dual crystal pod |
| 9 | `9` cascade | `3 + 3 + 3` | tri-triangle architecture |
| 10 | `10` fountain | `5 + 5`, `6 + 4`, `7 + 3` | large dual cluster |
| 11 | `11` cascade | no fully clean symmetric split | innovation pressure regime |
| 12 | `12` fountain | `6 + 6`, `4 + 4 + 4`, `3 + 3 + 3 + 3` | maximum decomposition freedom |
| 13 | `13` cascade | near-limit asymmetric regime | human-attention saturation frontier |

The corpus's own crystal-agent framework already privileges the expansion ladder `1 -> 4 -> 16 -> 64 -> 256`. Siteswap inserts a temporal ladder orthogonal to that structural ladder. The structural ladder tells how many specialized roles exist. The siteswap ladder tells how their checkpoints are interleaved through time.

#### 11.1.4 Executable schedule compilation

The compilation target is a checkpoint ledger, not an abstract pattern. The following kernel is the right minimal interface:

```python
from dataclasses import dataclass
from typing import List

@dataclass
class Checkpoint:
    beat: int
    agent_id: str
    channel: str
    autonomy_quanta: int
    next_landing: int
    action: str = "OBSERVE_MODELUPDATE_PROPOSE_CERTIFY_EXECUTE_AUDIT"

def validate_siteswap(pattern: List[int]) -> bool:
    period = len(pattern)
    landings = [(i + pattern[i]) % period for i in range(period)]
    return len(set(landings)) == period

def compile_pod_schedule(pattern: List[int], agents: List[str]) -> List[Checkpoint]:
    period = len(pattern)
    if not validate_siteswap(pattern):
        raise ValueError("Invalid siteswap: checkpoint collision detected")

    n = sum(pattern) // period
    if n != len(agents):
        raise ValueError(f"Pattern averages {n} objects but {len(agents)} agents supplied")

    schedule = []
    for beat, height in enumerate(pattern):
        channel = "L" if beat % 2 == 0 else "R"
        landing = (beat + height) % period
        agent = agents[beat % len(agents)]
        schedule.append(
            Checkpoint(
                beat=beat,
                agent_id=agent,
                channel=channel,
                autonomy_quanta=height,
                next_landing=landing,
            )
        )
    return schedule
```

This is enough to bind siteswap to the existing route machinery. Each checkpoint can carry a route packet, witness bundle, truth status, and replay hash. Once that is added, juggling becomes a front-end scheduler for the current manuscript and runtime infrastructure.

### 11.2 WATER: FLOW COORDINATION - WHEN THE PATTERN IS FORCED TO BEND

#### 11.2.1 The recovery problem

All real pods deviate from ideal periodicity. One agent stalls, one times out, one produces a breakthrough, one requires immediate correction, one should be left alone longer than planned. In juggling terms, one throw goes high, low, wide, or late. The correct question is not whether perturbation occurs but how the pattern absorbs it without global collapse.

Let the perturbation operator on beat `i` be

`P_epsilon(s_i) = s_i + epsilon`.

If `epsilon > 0`, the agent can be left alone longer. If `epsilon < 0`, it must be revisited sooner. Recovery is the constrained optimization problem

`s* = argmin_{s'} sum_j |s'_j - s_j|`

subject to

- `s'_i = s_i + epsilon`
- `s'` is a valid siteswap
- the resulting drop risk remains below threshold

The point is that recovery should be minimal, local, and lawful. The corpus already encodes the same attitude under different names: residual ledgers, NEAR states, corridor refinement, and anti-drift patching. Siteswap simply gives a human-temporal implementation of that doctrine.

#### 11.2.2 Style as communication regime

Pattern and style are distinct. The same pattern can be thrown with radically different governance character.

- **Claymation / numbers mode:** exact heights, exact channels, exact checkpoint law. This is proof mode, certification mode, schema mode, witness mode.
- **Flow mode:** the same schedule is preserved only approximately while responsiveness is maximized. This is exploratory synthesis mode, where timing is maintained but the exact form of response is adaptive.
- **Contact mode:** zero-airtime continuous handling. This is debugging, crisis management, or critical-edit mode where the orchestrator remains in near-continuous contact with the agent.

The corpus's route machinery already separates strict `OK` closure from `NEAR`, `AMBIG`, and `FAIL`. Style becomes the embodied overlay for those truth classes. Claymation aligns with `OK` and strict certification. Flow aligns with `NEAR` or creative exploration. Contact aligns with repair.

#### 11.2.3 Cascade-fountain transitions as governance operations

The most important high-level transition is between:

- **cascade**: tasks cross channels; all agents are in the same global traffic system
- **fountain**: tasks stay on side; sub-pods become partially independent

This is the precise human version of switching from shared global synthesis to isolated subteam execution. The workspace already performs this conceptually when it moves from one whole-manuscript routing phase into separate atlas, archive, runtime, and map subprojects. Siteswap makes the transition explicit. One anomalous transition throw inserts a temporary extra autonomy allowance while the topology rewires.

For an even-`n` pod in ground state `n`, the transition token is effectively `n + 1`: one beat of extra airtime to let the split complete without collision. Governance is therefore not external to scheduling. It is a special class of throw.

#### 11.2.4 Multiplex and broadcast

A multiplex throw `[a,b,...]` is the formal answer to simultaneous initiation. The orchestrator sends one seed that fans into several agent trajectories with different return times. The repo already uses this pattern informally when a single prompt seed is sent to multiple sub-agents or when one map update spawns simultaneous downstream tasks.

The correct interpretation is:

- low throw in a multiplex: quick-response agent
- mid throw: standard synthesis agent
- high throw: deep-research or long-latency agent

Multiplex is therefore not noise or overload. It is typed broadcast with nonuniform return horizons.

### 11.3 AIR: AGENT PROTOCOL - WHAT EXACTLY TRAVELS BETWEEN HANDS

#### 11.3.1 Prop physics as message-class physics

The current corpus already distinguishes different payload classes: route packets, witness capsules, atlas entries, executable modules, governance directives, and replay bundles. The prop taxonomy refines these into a physically intelligible packet theory.

- **Ball:** stateless packet. Position and timing dominate; internal orientation does not matter. Use for factual requests, single-shot transforms, and clean query-return loops.
- **Club:** stateful packet. Rotation matters. The receiver must catch the right end of the message. Use for partial analyses, ongoing sessions, context-bearing handoffs, and anything whose internal phase matters.
- **Ring / hoop:** framing packet. The object is a boundary, aperture, or schema. Use for templates, constraints, task contracts, proof shapes, or canonical output forms.
- **Poi:** continuous monitoring packet. Nothing is released; attention traces an orbit. Use for background monitoring, corpus listening, long-running synthesis, and continuous context retention.
- **Staff:** broadcast span. One object touches the whole workspace. Use for governance, system-wide priority shifts, policy updates, or global seed replacement.

The existing witness-replay system gives the missing computational substrate for these prop types. A club packet is a replayable capsule whose orientation matters. A ring packet is a schema contract. A staff message is a system-wide manifest update. Siteswap therefore does not replace the corpus packet vocabulary; it reorganizes it into a more embodied and schedulable physics.

#### 11.3.2 Bandwidth and latency classes

Let each active communication channel have weight `w_type`. Then pod communication bandwidth is

`BW_pod = sum_type n_type * w_type`

with a natural weighting such as:

- balls: `1`
- clubs: `phi`
- rings: `1`
- poi: `phi^-1`
- staff: `phi^2`

The exact constants are tunable. What matters is the ordering: broadcast and stateful handoff are heavier than pure stateless packets. A pod with many club and staff interactions will saturate faster than a ball-dominant pod even if the siteswap average is the same. This corrects a naive mistake. Pod size alone does not determine difficulty. Message physics also matters.

#### 11.3.3 The single-agent mastery law

No siteswap grammar rescues poor single-prop control. The current corpus says the same thing in other language: if one route packet cannot be normalized, witnessed, collapsed, and patched cleanly, scaling to many simultaneous packets only multiplies noise. Therefore the promotion law is strict:

`1 -> 2 -> 3 -> ... -> n`

with no lawful skipping.

Define the pod drop rate as

`DR(n) = |{ t : exists a in A, deadline(a,t) passed unread }| / |{t}|`.

Promotion from pod size `n` to `n + 1` is admissible only when

`DR(n) < phi^-2 ~ 0.146`.

This imports the corpus's truth-lattice discipline directly into embodied timing. "Clean enough to scale" becomes a measurable property.

#### 11.3.4 VTG geometry as continuous monitoring syntax

The chapter's most important addition beyond ordinary siteswap is that not all agents should be thrown and caught. Some should be orbited. Poi-based Visual Trace Geometry provides a monitoring grammar for continuous attention:

- **extensions:** gradually widen an agent's scope
- **flowers:** cycle through subtopics or parameter petals
- **isolations:** keep one invariant fixed while exploring the surround
- **CAPs:** rotate several agents around a shared axis or parameter
- **anti-spin:** converge several moving branches inward toward one conclusion

This is the right model for deep background tasks such as corpus search, long-running synthesis, archive extraction, or persistent monitoring jobs. The orchestrator is not juggling these agents in the strict ballistic sense. The orchestrator is maintaining an orbit.

### 11.4 EARTH: EMBODIED MASTERY - THE HUMAN LIMIT AS THE TRUE HARD CONSTRAINT

#### 11.4.1 Why bodily skill matters

The repo repeatedly converges on one law: coordination is not just a logical problem but a bounded-control problem. Agents have goals, action spaces, bounded rationality, energy budgets, working-memory limits, control ticks, and audit ledgers. The orchestrator is no exception. The human also has a bounded action space, finite working memory, limited sensor width, and nonzero recovery cost.

This is why the siteswap mapping is so valuable. It binds pod design to the orchestrator's actual nervous system rather than to fantasy omniscience. Two hands and limited attention are not a weakness. They are the true architecture.

#### 11.4.2 Training ladder

The embodied training protocol mirrors the structural protocol:

| Stage | Physical discipline | Pod discipline |
| --- | --- | --- |
| 1 | stable 3-ball cascade | stable 3-agent round robin |
| 2 | 3-ball variants `423`, `441`, `531` | asymmetric 3-agent routing |
| 3 | 4-ball fountain | clean 4-agent crystal pod |
| 4 | cascade-fountain transitions | subteam split and merge governance |
| 5 | 5-ball cascade attempts | bridge-node 5-pod |
| 6 | `3 + 3` dual work | two parallel 3-pods |
| 7+ | spread, movement, high throws | large pod timing and mobility |

The purpose is not performance art. It is neural adaptation. The same perceptual circuits that track multiple airborne objects track multiple pending agent landings, especially under uncertainty and perturbation.

#### 11.4.3 The complete operational protocol

The full orchestration law for an `n`-pod is:

1. Choose ground state: cascade for odd `n`, fountain for even `n`.
2. Assign agents to channels and bridge roles.
3. Compile a legal siteswap schedule.
4. Attach each checkpoint to the six-phase control tick:
   `Observe -> ModelUpdate -> Propose -> Certify -> Execute -> Audit`.
5. Bind witness and replay material to each landing.
6. Use multiplex throws for broadcast seeds.
7. Use poi-style continuous monitoring for background agents that should not fully land each cycle.
8. Apply local recovery when perturbations change required autonomy windows.
9. Transition between cascade and fountain when cross-pollination or isolation becomes dominant.
10. Track `DR(n)` and downshift pod size when the threshold is exceeded.
11. End the session by compressing the current state into a continuation seed.

This protocol is not a replacement for the atlas. It is the timing layer that lets the atlas breathe.

#### 11.4.4 Zero-point statement

The chapter reduces to one claim. Siteswap is the missing human-scale control language for the corpus's already existing multi-agent architecture. The atlas gives addresses. The route system gives admissibility. The witness-replay stack gives certification. The crystal-agent framework gives structural decomposition. The control tick gives the checkpoint microcycle. Siteswap supplies the temporal grammar that lets one orchestrator actually run the whole assembly without pretending to have infinite hands.

### Chapter Compression

Siteswap notation becomes a lawful pod algebra when throw height is interpreted as autonomy window, landing as checkpoint, channel as attention hand, collision as unread simultaneous demand, and pattern style as governance regime; odd pods naturally converge toward cascade-like cross-routing, even pods toward fountain-like subteam symmetry; multiplexes formalize broadcast, sideswap-like transitions formalize topology change, and poi geometry formalizes continuous monitoring; the existing workspace already provides the missing surrounding machinery in the form of route packets, witness bundles, replay capsules, control ticks, audit ledgers, metro addressing, and crystal-agent expansion, so the only missing layer was an embodied scheduler for one bounded orchestrator; siteswap fills that gap and yields a rigorous progression from `3` through `13` agents governed by a measurable drop-rate threshold rather than intuition alone.

CHAPTER 11 - SITESWAP COORDINATION: JUGGLING PATTERNS AS THE FORMAL LANGUAGE OF MULTI-AGENT POD ARCHITECTURE
