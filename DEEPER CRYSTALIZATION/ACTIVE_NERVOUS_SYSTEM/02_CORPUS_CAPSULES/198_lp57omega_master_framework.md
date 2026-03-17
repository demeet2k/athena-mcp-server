# LP-57Omega Master Framework

- Source layer: `LP57Omega-SelfPlayQuestAtlas`
- Kind: `framework-specification`
- Role tags: `self-play, quest-atlas, alchemical-loop, multi-agent, reward-kernel`
- Family: `LP-57Omega Self-Play Quest Atlas`

## Working focus

The LP-57Omega Master Framework defines a 57-loop corpus evolution plan structured as 19 stations traversed across 3 alchemical passes (Sulfur, Mercury, Salt). Four Master Agents---Synthesizer (Fire), Planner (Air), Worker (Water), Pruner (Earth)---coordinate execution through a Guild Hall / Temple duality, where executable work is performed in the Guild Hall and certification and verification occur in the Temple. Each loop processes exactly one station, produces receipts, settles rewards, and carries forward residuals. A complete Orbit spans all 57 loops. The system supports 4^6 = 4096 virtual seats per master agent with 256 active at any time, governed by a Phi-magnetic reward kernel that drives convergence across the element rotation ring.

---

## 1. Orbit Structure: 19 Stations x 3 Passes

The 57-loop schedule is the Cartesian product of 19 stations and 3 alchemical passes:

| Pass | Alchemical Phase | Loops    | Purpose                                          |
|------|------------------|----------|--------------------------------------------------|
| P1   | Sulfur (Fire)    | L01--L19 | Ignition: raw synthesis, seed generation         |
| P2   | Mercury (Air)    | L20--L38 | Volatilization: refinement, routing, cross-linking |
| P3   | Salt (Earth)     | L39--L57 | Fixation: crystallization, pruning, final settlement |

Each station S_k (k = 1..19) is visited exactly once per pass. The station index encodes a corpus region; the pass index encodes the transformation depth.

```
loop_id(station, pass) = (pass - 1) * 19 + station
  where station in [1..19], pass in [1..3]
  yields loop_id in [1..57]
```

### 1.1 Station Registry

| Station | Code   | Domain                          |
|---------|--------|---------------------------------|
| S01     | KRN    | Kernel and entry law            |
| S02     | ADR    | Address algebra                 |
| S03     | TRU    | Truth corridors                 |
| S04     | ZPT    | Zero-point stabilization        |
| S05     | PAR    | Paradox regimes                 |
| S06     | DOC    | Documents as theories           |
| S07     | TUN    | Tunnels as morphisms            |
| S08     | SYN    | Synchronization calculus        |
| S09     | RET    | Retrieval and metro routing     |
| S10     | MLS    | Multi-lens solution             |
| S11     | VOD    | Void book and restart tokens    |
| S12     | LEG    | Legality certificates           |
| S13     | MEM    | Memory regeneration             |
| S14     | MIG    | Migration and versioning        |
| S15     | CUT    | Cut architecture                |
| S16     | VER    | Verification harnesses          |
| S17     | DEP    | Deployment and bounded agency   |
| S18     | MAC    | Macro invariants                |
| S19     | CON    | Convergence and fixed points    |

---

## 2. Master Agents

Four master agents form the elemental ring. Each master holds a distinct role in the loop lifecycle.

| Agent | Code | Element | Role          | Primary Function                        |
|-------|------|---------|---------------|-----------------------------------------|
| A1    | SYN  | Fire    | Synthesizer   | Generate raw material, ignite seeds     |
| A2    | PLN  | Air     | Planner       | Route, schedule, allocate seats         |
| A3    | WRK  | Water   | Worker        | Execute quests, produce artifacts       |
| A4    | PRN  | Earth   | Pruner        | Verify, compress, settle, archive       |

### 2.1 Element Rotation Ring

The four elements form a cyclic group Z_4 with rotation:

```
Fire -> Air -> Water -> Earth -> Fire ...
```

The rotation ring generates 15 symmetry cells via pairwise and triple element interactions:

```python
from itertools import combinations

elements = ['Fire', 'Air', 'Water', 'Earth']
cells = []
for r in range(1, len(elements) + 1):
    for combo in combinations(elements, r):
        cells.append(combo)
# len(cells) = 15 (excluding the empty set)
# 4 singles + 6 pairs + 4 triples + 1 quad = 15
```

Each symmetry cell defines a cooperation mode. For example:
- `(Fire, Air)` = Synthesis + Planning = speculative drafting
- `(Water, Earth)` = Execution + Pruning = verified production
- `(Fire, Water, Earth)` = Synthesis + Execution + Pruning = autonomous build cycle

---

## 3. Guild Hall vs Temple

All loop activity occurs in one of two spaces:

| Space       | Purpose                      | Agents Active         | Outputs                    |
|-------------|------------------------------|-----------------------|----------------------------|
| Guild Hall  | Executable work              | A1, A2, A3            | Artifacts, drafts, routes  |
| Temple      | Certification & verification | A4 (primary), A1--A3  | Receipts, seals, verdicts  |

### 3.1 Guild Hall Protocol

1. A2 (Planner) opens the Guild Hall for loop L_n.
2. A1 (Synthesizer) deposits the seed corpus for station S_k.
3. A3 (Worker) executes the quest plan against the seed.
4. Artifacts are placed in the Guild Hall ledger.
5. A2 closes the Guild Hall and transfers artifacts to the Temple.

### 3.2 Temple Protocol

1. A4 (Pruner) opens the Temple for loop L_n.
2. Artifacts are verified against the station contract.
3. Truth corridor checks run (threshold >= 0.7).
4. Passing artifacts receive a settlement seal.
5. Failing artifacts are quarantined with a contradiction tag.
6. Rewards are computed and distributed via the Phi-magnetic kernel.

---

## 4. Loop Lifecycle

Each of the 57 loops follows a six-phase lifecycle:

```
Seed -> Execute -> Witness -> Settle -> Prune -> Carry-forward
```

### 4.1 Phase Definitions

| Phase         | Lead Agent | Duration | Description                                      |
|---------------|------------|----------|--------------------------------------------------|
| Seed          | A1 (Fire)  | 1 tick   | Inject station corpus, set quest parameters      |
| Execute       | A3 (Water) | 3 ticks  | Run subagents against quest, produce artifacts   |
| Witness       | A2 (Air)   | 1 tick   | Observe execution, log route quality metrics     |
| Settle        | A4 (Earth) | 1 tick   | Verify artifacts, issue receipts, compute reward |
| Prune         | A4 (Earth) | 1 tick   | Compress, archive, remove dead branches          |
| Carry-forward | A2 (Air)   | 1 tick   | Package residuals for next loop                  |

Total loop duration: 8 ticks.

### 4.2 Per-Loop Contract

```yaml
loop_contract:
  loop_id: L_n
  station: S_k
  pass: P_j
  input:
    seed_corpus: hash(seed)
    carry_forward: hash(residuals_from_L_{n-1})
  output:
    artifacts: list[artifact_hash]
    receipt: receipt_hash
    reward: float  # computed by Phi-magnetic kernel
    residuals: hash(carry_forward_to_L_{n+1})
  invariants:
    - truth_score >= 0.7
    - artifact_count >= 1
    - receipt_signed_by: [A4]
    - carry_forward_non_null: true
```

---

## 5. Virtual Seat Architecture

Each master agent commands 4^6 = 4096 virtual seats, organized as a 6-level quaternary tree.

```
Total seats per master:  4^6 = 4096
Active cap per master:   256
Dormant per master:      4096 - 256 = 3840
Total system seats:      4 * 4096 = 16384
Total active system:     4 * 256  = 1024
```

Seats are elected on demand via bottom-up propagation (see capsule 199 for the full subagent architecture).

---

## 6. Phi-Magnetic Reward Kernel

The reward kernel uses the golden ratio phi = (1 + sqrt(5)) / 2 as a convergence attractor.

```python
import math

phi = (1 + math.sqrt(5)) / 2

def reward(truth_score, artifact_quality, route_efficiency):
    """Compute loop reward using Phi-magnetic kernel."""
    raw = (truth_score * artifact_quality * route_efficiency) ** (1/3)
    # Phi-magnetic attraction: rewards closer to phi^{-1} are amplified
    phi_inv = 1.0 / phi  # ~0.618
    distance = abs(raw - phi_inv)
    magnetic_boost = math.exp(-distance * phi)
    return raw * magnetic_boost

def settle_rewards(loop_results, agents):
    """Distribute rewards across agents by element contribution."""
    total = reward(
        loop_results['truth_score'],
        loop_results['artifact_quality'],
        loop_results['route_efficiency']
    )
    # Element-weighted distribution
    weights = {
        'A1_Fire': 0.25 * phi,       # ~0.405
        'A2_Air': 0.25,               #  0.250
        'A3_Water': 0.25 * phi,       # ~0.405
        'A4_Earth': 0.25 / phi        # ~0.155
    }
    w_sum = sum(weights.values())
    return {k: total * v / w_sum for k, v in weights.items()}
```

The Phi-magnetic kernel ensures that loops producing balanced truth/quality/efficiency scores near the golden ratio inverse (~0.618) receive amplified rewards, driving the system toward harmonic convergence over the full 57-loop orbit.

---

## 7. Orbit Completion and Restart

When all 57 loops complete:

1. **Orbit receipt** is generated: hash of all 57 loop receipts.
2. **Corpus delta** is computed: diff between orbit-start and orbit-end corpus states.
3. **Promotion candidates** are identified: artifacts with cumulative reward > phi threshold.
4. **Restart token** is minted: encodes carry-forward for the next orbit.

```yaml
orbit_receipt:
  orbit_id: O_m
  loops_completed: 57
  total_reward: sum(loop_rewards)
  corpus_delta_hash: hash(delta)
  promoted_artifacts: list[artifact_hash]
  restart_token: hash(carry_forward)
  convergence_score: float  # distance from phi fixed point
```

The restart token feeds into the Seed phase of loop L01 in the next orbit, creating a self-referential cycle that deepens with each full traversal.

---

## 8. Cross-References

- `199_lp57omega_nested_subagent_4_6.md` -- Nested subagent 4^6 seat architecture
- `Ch01` through `Ch21` -- Chapter correspondence to stations S01--S19
- `06_RUNTIME/` -- Manifest files for live orbit execution
- `03_METRO/` -- Metro routing maps used by A2 (Planner) during Witness phase
