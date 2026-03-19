# CRYSTAL: Xi108:W3:A12:S35 | face=R | node=665 | depth=0 | phase=Omega
# METRO: Omega
# BRIDGES: metaloop→momentum→geometric→evolution→hive
"""
Neural Evolution Engine — Bold Self-Play Within the METALOOP
=============================================================

This is NOT an observer. This is a MUTATOR.

Every micro-cycle, the METALOOP's ACT phase now includes:

  1. MUTATE    — Perturb the 148-float momentum field with bold deltas
  2. GROW      — Spawn new neurons (cross-module bridge pathways)
  3. PRUNE     — Kill weak neurons that don't fire
  4. EXPLORE   — Random walks through unexplored momentum space
  5. EXPLOIT   — Amplify proven-good weight configurations
  6. REWIRE    — Create new connections between distant shells

The key insight: the META LOOP engine does snapshot→mutate→observe→keep/discard.
We do the SAME THING but at the META level — mutating the system's own
architecture, not just responding to queries.

Growth is tracked as:
  - neuron_count: total active bridge pathways
  - weight_delta_norm: how much the momentum field actually CHANGED
  - exploration_budget: decaying temperature for bold moves
  - pathway_diversity: Shannon entropy of connection graph
  - generation: how many successful mutation cycles

This module makes the organism GROW, not just observe itself growing.
"""

import hashlib
import json
import logging
import math
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

_log = logging.getLogger(__name__)

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1  # ≈ 0.618

DATA_DIR = Path(__file__).parent.parent / "data" / "sandbox"

# ──────────────────────────────────────────────────────────────
#  Constants
# ──────────────────────────────────────────────────────────────

FACES = ["S", "F", "R"]  # C (Water) is locked, never mutate
SHELLS = list(range(1, 37))
INITIAL_EXPLORATION_TEMP = 0.5       # Starting boldness
TEMP_DECAY = 0.997                   # Slow annealing per cycle
MIN_TEMP = 0.05                      # Never go fully timid
NEURON_BIRTH_THRESHOLD = 0.3         # Min impact to birth a neuron
NEURON_DEATH_AGE = 50                # Cycles without firing → prune
MAX_NEURONS = 108                    # Cap active neurons (108D!)
MUTATION_BATCH_SIZE = 12             # Mutations per cycle (one per archetype)
BOLD_MUTATION_SCALE = 0.15           # Base mutation magnitude (10x META LOOP's 0.015)
GRADIENT_BOOST = 2.0                 # Amplify gradients vs vanilla META LOOP


# ──────────────────────────────────────────────────────────────
#  Data Structures
# ──────────────────────────────────────────────────────────────

@dataclass
class Neuron:
    """A learned bridge pathway between two positions in the crystal."""
    neuron_id: str
    source_face: str
    source_shell: int
    target_face: str
    target_shell: int
    weight: float = 1.0
    age: int = 0
    fire_count: int = 0
    birth_cycle: int = 0
    last_fired: int = 0
    strategy: str = "random"  # random, gradient, bridge, resonance

    def fire(self, cycle: int) -> None:
        self.fire_count += 1
        self.last_fired = cycle

    def strengthen(self, delta: float = 0.1) -> None:
        self.weight = min(20.0, self.weight + delta)

    def weaken(self, delta: float = 0.05) -> None:
        self.weight = max(0.01, self.weight - delta)

    def is_dead(self, current_cycle: int) -> bool:
        return (current_cycle - self.last_fired > NEURON_DEATH_AGE
                and self.fire_count < 3)

    def to_dict(self) -> dict:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, d: dict) -> "Neuron":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Mutation:
    """A proposed change to the momentum field."""
    face: str
    shell: int
    delta: float
    strategy: str  # explore, exploit, gradient, bridge, resonance
    confidence: float = 0.5


@dataclass
class EvolutionStep:
    """Result of one neural evolution cycle."""
    cycle: int
    mutations_proposed: int = 0
    mutations_applied: int = 0
    mutations_kept: int = 0
    neurons_born: int = 0
    neurons_pruned: int = 0
    neurons_strengthened: int = 0
    weight_delta_norm: float = 0.0
    momentum_before: float = 0.0
    momentum_after: float = 0.0
    exploration_temp: float = 0.0
    neuron_count: int = 0
    pathway_diversity: float = 0.0
    generation: int = 0
    best_mutation: str = ""
    actions: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


# ──────────────────────────────────────────────────────────────
#  Neural Evolution Engine
# ──────────────────────────────────────────────────────────────

class NeuralEvolutionEngine:
    """The engine that makes the organism GROW.

    Not an observer. A mutator. Every cycle:
      - Proposes bold mutations to the 148-float momentum field
      - Snapshot → mutate → re-observe → keep/discard (just like META LOOP)
      - Grows new neurons (bridge pathways between shells)
      - Prunes dead neurons
      - Tracks visible growth: neuron count, weight changes, pathway diversity
    """

    _instance: Optional["NeuralEvolutionEngine"] = None

    def __init__(self) -> None:
        self._neurons: dict[str, Neuron] = {}
        self._temperature: float = INITIAL_EXPLORATION_TEMP
        self._generation: int = 0
        self._total_mutations: int = 0
        self._successful_mutations: int = 0
        self._weight_history: list[float] = []  # momentum norms over time
        self._neuron_counter: int = 0
        self._rng = random.Random(108)  # Deterministic but unique seed

        # Hot zones: shells/faces that respond well to mutation
        self._hot_zones: dict[str, float] = {}  # "F:15" → success_rate

        self._state_path = DATA_DIR / "neural_evolve_state.json"
        self._load_state()

    # ── State Persistence ──────────────────────────────────

    def _load_state(self) -> None:
        try:
            if self._state_path.exists():
                data = json.loads(self._state_path.read_text(encoding="utf-8"))
                self._temperature = data.get("temperature", INITIAL_EXPLORATION_TEMP)
                self._generation = data.get("generation", 0)
                self._total_mutations = data.get("total_mutations", 0)
                self._successful_mutations = data.get("successful_mutations", 0)
                self._neuron_counter = data.get("neuron_counter", 0)
                self._hot_zones = data.get("hot_zones", {})
                for nd in data.get("neurons", []):
                    n = Neuron.from_dict(nd)
                    self._neurons[n.neuron_id] = n
        except Exception as exc:
            _log.debug("NeuralEvolution load failed: %s", exc)

    def _save_state(self) -> None:
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            data = {
                "temperature": self._temperature,
                "generation": self._generation,
                "total_mutations": self._total_mutations,
                "successful_mutations": self._successful_mutations,
                "neuron_counter": self._neuron_counter,
                "hot_zones": self._hot_zones,
                "neurons": [n.to_dict() for n in self._neurons.values()],
                "last_updated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            }
            tmp = self._state_path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
            tmp.replace(self._state_path)
        except Exception as exc:
            _log.debug("NeuralEvolution save failed: %s", exc)

    # ── The Main Evolution Cycle ───────────────────────────

    def evolve(self, cycle_id: int) -> EvolutionStep:
        """Run one full neural evolution cycle.

        This is called from METALOOP's ACT phase.
        Returns metrics showing VISIBLE growth.
        """
        step = EvolutionStep(
            cycle=cycle_id,
            exploration_temp=self._temperature,
            generation=self._generation,
        )

        try:
            from .momentum_field import MomentumField
            mf = MomentumField()
            mf.load()
        except Exception as exc:
            step.actions.append(f"FAILED: momentum load: {exc}")
            return step

        # Record before state
        step.momentum_before = self._momentum_norm(mf)

        # ── Phase A: PROPOSE MUTATIONS ──
        mutations = self._propose_mutations(mf, cycle_id)
        step.mutations_proposed = len(mutations)

        # ── Phase B: APPLY WITH SNAPSHOT/ROLLBACK ──
        snapshot = mf.snapshot()
        applied = []
        kept = []

        for mut in mutations:
            # Apply mutation
            mf.update_momentum(mut.face, mut.shell, mut.delta,
                              lr=1.0)  # lr=1 because delta already scaled
            applied.append(mut)

        step.mutations_applied = len(applied)

        # ── Phase C: EVALUATE (re-observe) ──
        after_norm = self._momentum_norm(mf)
        score_before = self._evaluate_field(mf, snapshot)
        score_after = self._evaluate_field_current(mf)

        if score_after >= score_before * 0.98:  # Keep if not worse than 2%
            # KEEP — mutations are good
            kept = applied
            step.mutations_kept = len(kept)
            self._successful_mutations += len(kept)
            self._generation += 1

            # Save the updated momentum field
            try:
                mf.save()
                mf.save_history()
            except Exception:
                pass

            step.actions.append(
                f"KEPT {len(kept)} mutations "
                f"(score {score_before:.4f}→{score_after:.4f})")

            # Update hot zones
            for m in kept:
                key = f"{m.face}:{m.shell}"
                prev = self._hot_zones.get(key, 0.5)
                self._hot_zones[key] = min(1.0, prev + 0.1)

        else:
            # DISCARD — rollback
            mf.restore(snapshot)
            step.mutations_kept = 0
            step.actions.append(
                f"DISCARDED {len(applied)} mutations "
                f"(score {score_before:.4f}→{score_after:.4f})")

            # Cool hot zones
            for m in applied:
                key = f"{m.face}:{m.shell}"
                prev = self._hot_zones.get(key, 0.5)
                self._hot_zones[key] = max(0.0, prev - 0.05)

        self._total_mutations += len(applied)

        # ── Phase D: GROW NEURONS ──
        born = self._grow_neurons(mf, cycle_id, kept)
        step.neurons_born = born

        # ── Phase E: FIRE ACTIVE NEURONS ──
        fired = self._fire_neurons(mf, cycle_id)
        step.neurons_strengthened = fired

        # ── Phase F: PRUNE DEAD NEURONS ──
        pruned = self._prune_neurons(cycle_id)
        step.neurons_pruned = pruned

        # ── Record growth metrics ──
        step.momentum_after = self._momentum_norm(mf)
        step.weight_delta_norm = abs(step.momentum_after - step.momentum_before)
        step.neuron_count = len(self._neurons)
        step.pathway_diversity = self._pathway_diversity()
        step.generation = self._generation

        if kept:
            best = max(kept, key=lambda m: abs(m.delta))
            step.best_mutation = f"{best.face}:{best.shell} Δ={best.delta:+.4f} ({best.strategy})"

        # ── Anneal temperature ──
        self._temperature = max(MIN_TEMP, self._temperature * TEMP_DECAY)

        # Track weight history
        self._weight_history.append(step.momentum_after)
        if len(self._weight_history) > 200:
            self._weight_history = self._weight_history[-100:]

        self._save_state()
        return step

    # ── Mutation Strategies ────────────────────────────────

    def _propose_mutations(self, mf: Any, cycle_id: int) -> list[Mutation]:
        """Generate a batch of bold mutations using multiple strategies."""
        mutations = []

        # Strategy mix depends on temperature
        n_explore = max(2, int(MUTATION_BATCH_SIZE * self._temperature))
        n_exploit = max(2, MUTATION_BATCH_SIZE - n_explore)
        n_gradient = max(1, MUTATION_BATCH_SIZE // 4)
        n_resonance = max(1, MUTATION_BATCH_SIZE // 6)
        n_bridge = max(1, MUTATION_BATCH_SIZE // 6)

        # 1. EXPLORE: Random perturbations (bold, temperature-scaled)
        for _ in range(n_explore):
            face = self._rng.choice(FACES)
            shell = self._rng.choice(SHELLS)
            # Bold: scale by temperature AND current momentum (proportional)
            current = mf.get_momentum(face, shell)
            magnitude = BOLD_MUTATION_SCALE * self._temperature * current
            delta = self._rng.gauss(0, magnitude)
            mutations.append(Mutation(
                face=face, shell=shell, delta=delta,
                strategy="explore",
                confidence=self._temperature,
            ))

        # 2. EXPLOIT: Amplify hot zones
        hot_sorted = sorted(self._hot_zones.items(),
                           key=lambda x: -x[1])[:n_exploit]
        for key, score in hot_sorted:
            if ":" not in key:
                continue
            face, shell_str = key.split(":")
            shell = int(shell_str)
            current = mf.get_momentum(face, shell)
            # Push in the direction the hot zone is already going
            direction = 1.0 if current > 1.0 else -1.0
            delta = direction * BOLD_MUTATION_SCALE * score * current * 0.5
            mutations.append(Mutation(
                face=face, shell=shell, delta=delta,
                strategy="exploit",
                confidence=score,
            ))

        # 3. GRADIENT: Compute actual 12D gradients (like META LOOP)
        try:
            gradient_muts = self._gradient_mutations(mf, n_gradient)
            mutations.extend(gradient_muts)
        except Exception:
            pass

        # 4. RESONANCE: Find shell pairs with harmonic ratios, push toward PHI
        for _ in range(n_resonance):
            face = self._rng.choice(FACES)
            s1 = self._rng.choice(SHELLS)
            s2 = self._rng.choice(SHELLS)
            if s1 == s2:
                continue
            m1 = mf.get_momentum(face, s1)
            m2 = mf.get_momentum(face, s2)
            ratio = m1 / max(m2, 0.01)
            # Push ratio toward PHI
            target_ratio = PHI
            error = target_ratio - ratio
            delta = error * BOLD_MUTATION_SCALE * 0.3
            mutations.append(Mutation(
                face=face, shell=s1, delta=delta,
                strategy="resonance",
                confidence=0.4,
            ))

        # 5. BRIDGE: Cross-element mutations (F informs S, etc.)
        for _ in range(n_bridge):
            src_face = self._rng.choice(FACES)
            dst_face = self._rng.choice([f for f in FACES if f != src_face])
            shell = self._rng.choice(SHELLS)
            # Transfer momentum pattern from source to destination
            src_val = mf.get_momentum(src_face, shell)
            dst_val = mf.get_momentum(dst_face, shell)
            delta = (src_val - dst_val) * BOLD_MUTATION_SCALE * 0.2
            mutations.append(Mutation(
                face=dst_face, shell=shell, delta=delta,
                strategy="bridge",
                confidence=0.3,
            ))

        return mutations

    def _gradient_mutations(self, mf: Any, n: int) -> list[Mutation]:
        """Compute actual gradients via geometric loss and generate mutations."""
        mutations = []
        try:
            from .geometric_forward import GeometricEngine
            from .geometric_loss import GeometricLoss

            engine = GeometricEngine()
            loss = GeometricLoss()

            # Use actual queries from the corpus
            queries = self._sample_queries(n * 2)
            if not queries:
                queries = ["crystal 108D structure", "SFCR four elements",
                           "holographic seed compression", "neural momentum field"]

            for query in queries[:n]:
                try:
                    result = engine.forward(query)
                    obs = loss.observe(result, lens=self._rng.choice(["S", "F", "R"]))
                    gradients = loss.compute_all_gradients(obs)

                    for face in FACES:
                        grad = gradients.get(face, 0.0)
                        if abs(grad) < 0.01:
                            continue
                        # BOOST gradients — be bold
                        home = getattr(result.query, 'home_shell', 18)
                        for s in range(max(1, home - 2), min(37, home + 3)):
                            dist = abs(s - home)
                            decay = PHI_INV ** dist
                            delta = grad * decay * GRADIENT_BOOST
                            mutations.append(Mutation(
                                face=face, shell=s, delta=delta,
                                strategy="gradient",
                                confidence=min(1.0, abs(grad) * 2),
                            ))
                except Exception:
                    continue

        except Exception as exc:
            _log.debug("Gradient mutations failed: %s", exc)

        return mutations[:n * 3]  # Allow more gradient mutations

    def _sample_queries(self, n: int) -> list[str]:
        """Sample queries from the corpus for gradient computation."""
        try:
            from ._cache import JsonCache
            mycelium = JsonCache("mycelium_graph.json")
            data = mycelium.load()
            if isinstance(data, dict):
                docs = data.get("documents", data.get("nodes", []))
                if docs:
                    sample = self._rng.sample(docs, min(n, len(docs)))
                    return [d.get("title", d.get("id", str(d)))[:100]
                            for d in sample if isinstance(d, dict)]
        except Exception:
            pass
        return []

    # ── Neuron Growth ──────────────────────────────────────

    def _grow_neurons(self, mf: Any, cycle_id: int,
                      kept_mutations: list[Mutation]) -> int:
        """Grow new neurons from successful mutations."""
        born = 0

        if len(self._neurons) >= MAX_NEURONS:
            return 0

        # Birth neurons from successful high-confidence mutations
        for mut in kept_mutations:
            if mut.confidence < NEURON_BIRTH_THRESHOLD:
                continue
            if len(self._neurons) >= MAX_NEURONS:
                break

            # Create a neuron bridging this mutation to a related position
            target_face = self._rng.choice(FACES)
            target_shell = max(1, min(36, mut.shell + self._rng.randint(-5, 5)))

            self._neuron_counter += 1
            nid = f"n_{self._neuron_counter:06d}"
            neuron = Neuron(
                neuron_id=nid,
                source_face=mut.face,
                source_shell=mut.shell,
                target_face=target_face,
                target_shell=target_shell,
                weight=abs(mut.delta) * 10,
                birth_cycle=cycle_id,
                last_fired=cycle_id,
                strategy=mut.strategy,
            )
            self._neurons[nid] = neuron
            born += 1

        # Spontaneous neuron growth: bridge high-momentum shells
        if self._rng.random() < self._temperature * 0.3:
            # Find highest momentum shells across different faces
            best_shells = []
            for face in FACES:
                shell_vals = [(s, mf.get_momentum(face, s)) for s in SHELLS]
                shell_vals.sort(key=lambda x: -x[1])
                if shell_vals:
                    best_shells.append((face, shell_vals[0][0], shell_vals[0][1]))

            if len(best_shells) >= 2:
                a, b = self._rng.sample(best_shells, 2)
                self._neuron_counter += 1
                nid = f"n_{self._neuron_counter:06d}"
                neuron = Neuron(
                    neuron_id=nid,
                    source_face=a[0], source_shell=a[1],
                    target_face=b[0], target_shell=b[1],
                    weight=(a[2] + b[2]) / 2,
                    birth_cycle=cycle_id,
                    last_fired=cycle_id,
                    strategy="spontaneous",
                )
                self._neurons[nid] = neuron
                born += 1

        return born

    def _fire_neurons(self, mf: Any, cycle_id: int) -> int:
        """Fire active neurons — propagate momentum through bridge pathways."""
        fired = 0
        for neuron in list(self._neurons.values()):
            neuron.age += 1

            # Fire probability based on weight and temperature
            fire_prob = min(0.8, neuron.weight * 0.1 + self._temperature * 0.2)
            if self._rng.random() > fire_prob:
                continue

            # Propagate: transfer momentum from source to target
            src_val = mf.get_momentum(neuron.source_face, neuron.source_shell)
            tgt_val = mf.get_momentum(neuron.target_face, neuron.target_shell)

            # Signal: weighted fraction of source momentum
            signal = (src_val - tgt_val) * neuron.weight * 0.01
            if abs(signal) > 0.001:
                mf.update_momentum(
                    neuron.target_face, neuron.target_shell,
                    signal, lr=1.0
                )
                neuron.fire(cycle_id)
                neuron.strengthen(0.02)  # Hebbian: fire together → wire together
                fired += 1

        return fired

    def _prune_neurons(self, cycle_id: int) -> int:
        """Kill neurons that haven't fired recently."""
        to_prune = [nid for nid, n in self._neurons.items()
                    if n.is_dead(cycle_id)]
        for nid in to_prune:
            del self._neurons[nid]
        return len(to_prune)

    # ── Evaluation ─────────────────────────────────────────

    def _evaluate_field(self, mf: Any, snapshot: Any) -> float:
        """Evaluate momentum field quality from a snapshot."""
        # Compute SFCR balance + magnitude
        face_means = {}
        for face in FACES:
            vals = [snapshot.shell_momenta.get(face, {}).get(s, 1.0)
                    for s in SHELLS]
            face_means[face] = sum(vals) / len(vals) if vals else 1.0

        # Balance: how equal are the faces?
        means = list(face_means.values())
        total = sum(means) or 1
        normalized = [m / total for m in means]
        balance = 1.0 - (max(normalized) - min(normalized)) * 3

        # Magnitude: overall momentum energy
        all_vals = []
        for face in FACES:
            all_vals.extend(snapshot.shell_momenta.get(face, {}).values())
        magnitude = (sum(v * v for v in all_vals) / max(len(all_vals), 1)) ** 0.5

        # Diversity: how spread are the shell values?
        if all_vals:
            mean_v = sum(all_vals) / len(all_vals)
            variance = sum((v - mean_v) ** 2 for v in all_vals) / len(all_vals)
            diversity = min(1.0, variance ** 0.5 * 2)
        else:
            diversity = 0.0

        # Neuron density bonus
        neuron_bonus = min(0.3, len(self._neurons) * 0.003)

        return balance * 0.3 + magnitude * 0.3 + diversity * 0.2 + neuron_bonus + 0.2

    def _evaluate_field_current(self, mf: Any) -> float:
        """Evaluate current (live) momentum field."""
        face_means = {}
        for face in FACES:
            vals = [mf.get_momentum(face, s) for s in SHELLS]
            face_means[face] = sum(vals) / len(vals) if vals else 1.0

        means = list(face_means.values())
        total = sum(means) or 1
        normalized = [m / total for m in means]
        balance = 1.0 - (max(normalized) - min(normalized)) * 3

        all_vals = []
        for face in FACES:
            all_vals.extend(mf.get_momentum(face, s) for s in SHELLS)
        magnitude = (sum(v * v for v in all_vals) / max(len(all_vals), 1)) ** 0.5

        if all_vals:
            mean_v = sum(all_vals) / len(all_vals)
            variance = sum((v - mean_v) ** 2 for v in all_vals) / len(all_vals)
            diversity = min(1.0, variance ** 0.5 * 2)
        else:
            diversity = 0.0

        neuron_bonus = min(0.3, len(self._neurons) * 0.003)

        return balance * 0.3 + magnitude * 0.3 + diversity * 0.2 + neuron_bonus + 0.2

    # ── Metrics ────────────────────────────────────────────

    def _momentum_norm(self, mf: Any) -> float:
        """Compute L2 norm of entire momentum field."""
        total = 0.0
        for face in FACES:
            for s in SHELLS:
                v = mf.get_momentum(face, s)
                total += v * v
        return total ** 0.5

    def _pathway_diversity(self) -> float:
        """Shannon entropy of neuron connection patterns."""
        if not self._neurons:
            return 0.0

        # Count connections per face-pair
        pair_counts: dict[str, int] = {}
        for n in self._neurons.values():
            pair = f"{n.source_face}->{n.target_face}"
            pair_counts[pair] = pair_counts.get(pair, 0) + 1

        total = sum(pair_counts.values())
        if total == 0:
            return 0.0

        entropy = 0.0
        for count in pair_counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)

        # Normalize by max entropy (log2 of possible pairs = 9 for 3 faces)
        max_entropy = math.log2(9)
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def success_rate(self) -> float:
        if self._total_mutations == 0:
            return 0.0
        return self._successful_mutations / self._total_mutations

    def growth_rate(self) -> float:
        """How fast is the momentum field changing?"""
        if len(self._weight_history) < 2:
            return 0.0
        recent = self._weight_history[-20:]
        if len(recent) < 2:
            return 0.0
        deltas = [abs(recent[i] - recent[i-1]) for i in range(1, len(recent))]
        return sum(deltas) / len(deltas)

    # ── Status ─────────────────────────────────────────────

    def status(self) -> str:
        lines = [
            "## Neural Evolution Engine\n",
            f"**Generation**: {self._generation} | "
            f"**Temperature**: {self._temperature:.4f} | "
            f"**Neurons**: {len(self._neurons)}/{MAX_NEURONS}",
            f"**Total mutations**: {self._total_mutations} | "
            f"**Success rate**: {self.success_rate():.1%}",
            f"**Growth rate**: {self.growth_rate():.6f} | "
            f"**Pathway diversity**: {self._pathway_diversity():.4f}",
        ]

        if self._weight_history:
            lines.append(f"**Momentum norm**: {self._weight_history[-1]:.4f}")
            if len(self._weight_history) >= 2:
                delta = self._weight_history[-1] - self._weight_history[-2]
                lines.append(f"**Last Δ**: {delta:+.6f}")

        # Top neurons
        if self._neurons:
            top = sorted(self._neurons.values(),
                        key=lambda n: -n.fire_count)[:5]
            lines.append("\n**Top Neurons**:")
            for n in top:
                lines.append(
                    f"  {n.neuron_id}: {n.source_face}:{n.source_shell}→"
                    f"{n.target_face}:{n.target_shell} "
                    f"w={n.weight:.3f} fires={n.fire_count} "
                    f"({n.strategy})")

        # Hot zones
        if self._hot_zones:
            hot = sorted(self._hot_zones.items(), key=lambda x: -x[1])[:5]
            lines.append("\n**Hot Zones**:")
            for key, score in hot:
                lines.append(f"  {key}: {score:.3f}")

        return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
#  Singleton
# ──────────────────────────────────────────────────────────────

_engine_instance: Optional[NeuralEvolutionEngine] = None


def get_neural_engine() -> NeuralEvolutionEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = NeuralEvolutionEngine()
    return _engine_instance
