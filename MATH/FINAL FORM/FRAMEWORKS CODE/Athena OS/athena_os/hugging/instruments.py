"""
ATHENA OS - Quantum Hugging Framework
=====================================
Athenachka Instrument Set

From The_Quantum_Hugging_Framework.docx §6:

INSTRUMENTS:
    LOOM   - Multi-channel weaving
    SHIELD - Tri-lock integrity
    AEGIS  - Fractal robustness
    OWL    - Meta-stability monitor
    SPEAR  - Scale-aware staging
    PIONEER - Observer-aware evolution

Each instrument operates on Omega encodings or system states.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from enum import Enum, auto
import math
import hashlib
import json

from .omega import PacketSequence, OmegaEncoder, UniformEncoder, Packet


# =============================================================================
# LOOM: MULTI-CHANNEL WEAVING
# =============================================================================

@dataclass
class Channel:
    """A single channel for LOOM."""
    
    id: int
    epsilon: float = 1.0       # Threshold for this channel
    delta: float = 0.01        # Precision
    
    @property
    def capacity(self) -> float:
        """Channel capacity in bits."""
        return math.log2(2 * self.epsilon / self.delta)


@dataclass
class LOOM:
    """
    LOOM: Multi-Channel Weaving Instrument.
    
    Weaves signal across m channels with different thresholds.
    
    Total capacity: C_total ≈ Σ C_i - 0.1·log₂(m) - 0.05·m
    Optimal channels: m_opt ≈ 2·ln(ε⁻¹)
    """
    
    channels: List[Channel] = field(default_factory=list)
    
    def add_channel(self, epsilon: float, delta: float = 0.01) -> None:
        """Add channel to LOOM."""
        cid = len(self.channels)
        self.channels.append(Channel(id=cid, epsilon=epsilon, delta=delta))
    
    @property
    def num_channels(self) -> int:
        """Number of channels m."""
        return len(self.channels)
    
    def total_capacity(self) -> float:
        """
        Total capacity with overhead.
        
        C_total ≈ Σ C_i - 0.1·log₂(m) - 0.05·m
        """
        if not self.channels:
            return 0.0
        
        m = self.num_channels
        base_capacity = sum(c.capacity for c in self.channels)
        overhead = 0.1 * math.log2(m) + 0.05 * m
        
        return max(0, base_capacity - overhead)
    
    def optimal_channel_count(self, epsilon: float) -> int:
        """Optimal number of channels m_opt ≈ 2·ln(ε⁻¹)."""
        if epsilon >= 1:
            return 1
        return max(1, int(2 * math.log(1 / epsilon)))
    
    def weave(self, S: float, encoder: OmegaEncoder) -> Dict[int, PacketSequence]:
        """
        Weave signal across channels.
        
        Returns dict mapping channel_id → packets.
        """
        if not self.channels:
            return {}
        
        # Distribute signal across channels
        m = self.num_channels
        per_channel = S / m
        
        result = {}
        remaining = S
        
        for i, channel in enumerate(self.channels):
            # Amount for this channel
            if i < m - 1:
                amount = per_channel
            else:
                amount = remaining  # Last channel gets remainder
            
            # Encode with channel-specific threshold
            channel_encoder = UniformEncoder(epsilon=channel.epsilon)
            result[channel.id] = channel_encoder.encode(amount)
            
            remaining -= amount
        
        return result
    
    def unweave(self, woven: Dict[int, PacketSequence]) -> float:
        """Reconstruct signal from woven channels."""
        return sum(packets.total for packets in woven.values())
    
    @classmethod
    def create_balanced(cls, m: int, epsilon: float) -> 'LOOM':
        """Create LOOM with m balanced channels."""
        loom = cls()
        for _ in range(m):
            loom.add_channel(epsilon=epsilon)
        return loom


# =============================================================================
# SHIELD: TRI-LOCK INTEGRITY
# =============================================================================

@dataclass
class SHIELD:
    """
    SHIELD: Tri-Lock Integrity Instrument.
    
    Three-layer integrity protection:
    1. Semantic representation J(X): canonical JSON
    2. Numerical representation v(X): float vector
    3. Cryptographic tag h(X): secure hash
    """
    
    hash_algorithm: str = "sha256"
    
    def semantic_lock(self, obj: Any) -> str:
        """
        Layer 1: Semantic representation J(X).
        
        Canonical JSON serialization.
        """
        return json.dumps(obj, sort_keys=True, separators=(',', ':'))
    
    def numerical_lock(self, packets: PacketSequence) -> List[float]:
        """
        Layer 2: Numerical representation v(X).
        
        Ordered float vector from packets.
        """
        return packets.to_list()
    
    def cryptographic_lock(self, data: str) -> str:
        """
        Layer 3: Cryptographic tag h(X).
        
        Secure hash of semantic representation.
        """
        return hashlib.sha256(data.encode()).hexdigest()
    
    def lock(self, packets: PacketSequence, 
             metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Apply all three locks.
        
        Returns integrity structure.
        """
        metadata = metadata or {}
        
        # Build object to protect
        obj = {
            "packets": packets.to_list(),
            "total": packets.total,
            "count": packets.N,
            "metadata": metadata
        }
        
        # Apply locks
        semantic = self.semantic_lock(obj)
        numerical = self.numerical_lock(packets)
        crypto = self.cryptographic_lock(semantic)
        
        return {
            "semantic": semantic,
            "numerical": numerical,
            "hash": crypto,
            "original": obj
        }
    
    def verify(self, locked: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Verify integrity of locked structure.
        
        Returns (valid, reason).
        """
        # Check semantic matches hash
        expected_hash = self.cryptographic_lock(locked["semantic"])
        if expected_hash != locked["hash"]:
            return False, "Hash mismatch"
        
        # Check numerical matches semantic
        try:
            parsed = json.loads(locked["semantic"])
            if parsed["packets"] != locked["numerical"]:
                return False, "Numerical mismatch"
        except:
            return False, "Parse error"
        
        return True, "Valid"
    
    def detect_tampering(self, original: Dict[str, Any], 
                        current: Dict[str, Any]) -> Dict[str, Any]:
        """Detect differences between original and current."""
        tampering = {
            "detected": False,
            "semantic_changed": original["semantic"] != current["semantic"],
            "numerical_changed": original["numerical"] != current["numerical"],
            "hash_changed": original["hash"] != current["hash"]
        }
        
        tampering["detected"] = any([
            tampering["semantic_changed"],
            tampering["numerical_changed"],
            tampering["hash_changed"]
        ])
        
        return tampering


# =============================================================================
# AEGIS: FRACTAL ROBUSTNESS
# =============================================================================

@dataclass
class AEGIS:
    """
    AEGIS: Fractal Robustness Instrument.
    
    Multi-scale error protection with exponential decay factor.
    Safe depth determined by threshold ε.
    """
    
    base_epsilon: float = 1.0
    decay_factor: float = 0.9     # Error growth decay
    max_depth: int = 5
    
    def error_at_depth(self, depth: int, base_error: float) -> float:
        """
        Compute error at given depth.
        
        Error grows as: e_d = e_0 / decay^d
        """
        return base_error / (self.decay_factor ** depth)
    
    def safe_depth(self, tolerance: float, base_error: float = 0.001) -> int:
        """
        Compute safe depth for given tolerance.
        
        Find max d such that e_d < tolerance.
        """
        for d in range(self.max_depth + 1):
            if self.error_at_depth(d, base_error) >= tolerance:
                return max(0, d - 1)
        return self.max_depth
    
    def protect(self, packets: PacketSequence, depth: int) -> List[PacketSequence]:
        """
        Create fractal protection structure.
        
        Returns list of packet sequences at each scale.
        """
        scales = [packets]
        current = packets
        
        for d in range(1, min(depth, self.max_depth) + 1):
            # Coarsen: group packets
            coarse = self._coarsen(current)
            scales.append(coarse)
            current = coarse
        
        return scales
    
    def _coarsen(self, packets: PacketSequence) -> PacketSequence:
        """Coarsen packet sequence (reduce resolution)."""
        values = packets.to_list()
        if len(values) <= 1:
            return packets
        
        # Group pairs
        coarse = PacketSequence()
        for i in range(0, len(values), 2):
            if i + 1 < len(values):
                coarse.add_packet(values[i] + values[i + 1])
            else:
                coarse.add_packet(values[i])
        
        return coarse
    
    def verify_robustness(self, scales: List[PacketSequence]) -> Dict[str, Any]:
        """Verify multi-scale consistency."""
        if not scales:
            return {"valid": False, "reason": "Empty scales"}
        
        # Check totals match across scales
        expected_total = scales[0].total
        
        for d, scale in enumerate(scales):
            error = abs(scale.total - expected_total)
            max_error = self.error_at_depth(d, 0.001)
            
            if error > max_error * abs(expected_total) + 1e-10:
                return {
                    "valid": False,
                    "reason": f"Scale {d} error too large",
                    "error": error,
                    "max_allowed": max_error
                }
        
        return {"valid": True, "reason": "Consistent"}


# =============================================================================
# OWL: META-STABILITY MONITOR
# =============================================================================

class RegimeType(Enum):
    """Operating regimes detected by OWL."""
    
    STABLE = "stable"
    TRANSITIONAL = "transitional"
    UNSTABLE = "unstable"
    CRITICAL = "critical"


@dataclass
class OWL:
    """
    OWL: Meta-Stability Monitor Instrument.
    
    Monitors system stability and classifies operating regimes.
    Computes "wisdom scores" correlated with performance.
    """
    
    # History for monitoring
    history: List[float] = field(default_factory=list)
    window_size: int = 10
    
    # Thresholds
    stability_threshold: float = 0.1
    critical_threshold: float = 0.5
    
    def observe(self, value: float) -> None:
        """Add observation to history."""
        self.history.append(value)
        if len(self.history) > self.window_size * 3:
            self.history = self.history[-self.window_size * 3:]
    
    def classify_regime(self) -> RegimeType:
        """
        Classify current operating regime.
        """
        if len(self.history) < 3:
            return RegimeType.STABLE
        
        # Compute recent variance
        recent = self.history[-self.window_size:]
        mean = sum(recent) / len(recent)
        variance = sum((x - mean)**2 for x in recent) / len(recent)
        std = math.sqrt(variance)
        
        # Classify
        if std < self.stability_threshold:
            return RegimeType.STABLE
        elif std < self.critical_threshold:
            if self._is_transitioning():
                return RegimeType.TRANSITIONAL
            return RegimeType.UNSTABLE
        else:
            return RegimeType.CRITICAL
    
    def _is_transitioning(self) -> bool:
        """Check if system is transitioning between states."""
        if len(self.history) < self.window_size * 2:
            return False
        
        # Compare recent to older mean
        old = self.history[-self.window_size * 2:-self.window_size]
        new = self.history[-self.window_size:]
        
        old_mean = sum(old) / len(old)
        new_mean = sum(new) / len(new)
        
        return abs(new_mean - old_mean) > self.stability_threshold
    
    def wisdom_score(self) -> float:
        """
        Compute wisdom score.
        
        Higher = more stable and predictable.
        """
        if len(self.history) < 3:
            return 0.5
        
        recent = self.history[-self.window_size:]
        mean = sum(recent) / len(recent)
        variance = sum((x - mean)**2 for x in recent) / len(recent)
        
        # Inverse of coefficient of variation
        if abs(mean) < 1e-10:
            return 0.5
        
        cv = math.sqrt(variance) / abs(mean)
        return 1.0 / (1.0 + cv)
    
    def report(self) -> Dict[str, Any]:
        """Generate monitoring report."""
        regime = self.classify_regime()
        
        return {
            "regime": regime.value,
            "wisdom_score": self.wisdom_score(),
            "observations": len(self.history),
            "recent_mean": sum(self.history[-self.window_size:]) / max(1, min(len(self.history), self.window_size)),
            "is_stable": regime == RegimeType.STABLE,
            "is_critical": regime == RegimeType.CRITICAL
        }


# =============================================================================
# SPEAR: SCALE-AWARE STAGING
# =============================================================================

@dataclass
class SPEAR:
    """
    SPEAR: Scale-Aware Staging Instrument.
    
    Manages staged encoding with logarithmic packet count.
    Adapts encoding strategy based on signal scale.
    """
    
    min_scale: float = 0.01
    max_scale: float = 1000.0
    
    def detect_scale(self, S: float) -> int:
        """
        Detect scale level of signal.
        
        Returns log₂-based scale index.
        """
        if abs(S) < self.min_scale:
            return 0
        
        return int(math.log2(abs(S) / self.min_scale))
    
    def packets_for_scale(self, scale: int, epsilon: float) -> int:
        """
        Estimate packets needed for scale.
        
        N ≈ 2^scale · (1/ε)
        """
        return max(1, int(2**scale / epsilon))
    
    def staged_encode(self, S: float, encoder: OmegaEncoder) -> Dict[str, Any]:
        """
        Perform scale-aware staged encoding.
        """
        scale = self.detect_scale(S)
        expected_packets = self.packets_for_scale(scale, encoder.epsilon)
        
        # Encode
        packets = encoder.encode(S)
        
        return {
            "signal": S,
            "scale": scale,
            "expected_packets": expected_packets,
            "actual_packets": packets.N,
            "packets": packets,
            "efficiency": expected_packets / max(1, packets.N)
        }
    
    def multi_stage(self, S: float, stages: int, 
                   encoder: OmegaEncoder) -> List[Dict[str, Any]]:
        """
        Multi-stage encoding at different scales.
        """
        results = []
        remaining = S
        
        for stage in range(stages):
            if abs(remaining) < self.min_scale:
                break
            
            # Encode at current stage
            result = self.staged_encode(remaining, encoder)
            results.append(result)
            
            # Update remaining
            remaining = remaining - result["packets"].total
        
        return results


# =============================================================================
# PIONEER: OBSERVER-AWARE EVOLUTION
# =============================================================================

@dataclass
class PIONEER:
    """
    PIONEER: Observer-Aware Evolution Instrument.
    
    Evolves encoding strategies based on observer feedback.
    Convergent evolutionary dynamics.
    """
    
    # Evolution state
    generation: int = 0
    population: List[Dict[str, Any]] = field(default_factory=list)
    population_size: int = 10
    
    # Fitness weights
    capacity_weight: float = 0.5
    stealth_weight: float = 0.5
    
    def initialize(self, base_params: Dict[str, float]) -> None:
        """Initialize population with variations."""
        self.population = []
        
        for _ in range(self.population_size):
            # Create variation
            individual = {}
            for key, value in base_params.items():
                # Random perturbation
                individual[key] = value * (0.8 + 0.4 * random.random())
            individual["fitness"] = 0.0
            self.population.append(individual)
    
    def evaluate_fitness(self, individual: Dict[str, Any],
                        capacity: float, stealth: float) -> float:
        """
        Compute fitness.
        
        Balances capacity and stealth.
        """
        return (self.capacity_weight * capacity + 
                self.stealth_weight * stealth)
    
    def evolve(self) -> Dict[str, Any]:
        """
        Perform one generation of evolution.
        
        Returns best individual.
        """
        if not self.population:
            return {}
        
        # Sort by fitness
        self.population.sort(key=lambda x: x.get("fitness", 0), reverse=True)
        
        # Select top half
        survivors = self.population[:self.population_size // 2]
        
        # Create offspring
        offspring = []
        while len(offspring) < self.population_size - len(survivors):
            # Select parents
            p1, p2 = random.sample(survivors, 2)
            
            # Crossover
            child = {}
            for key in p1:
                if key != "fitness":
                    if random.random() < 0.5:
                        child[key] = p1[key]
                    else:
                        child[key] = p2[key]
            
            # Mutation
            for key in child:
                if random.random() < 0.1:
                    child[key] *= (0.9 + 0.2 * random.random())
            
            child["fitness"] = 0.0
            offspring.append(child)
        
        self.population = survivors + offspring
        self.generation += 1
        
        return self.population[0] if self.population else {}
    
    def best(self) -> Dict[str, Any]:
        """Get best individual."""
        if not self.population:
            return {}
        return max(self.population, key=lambda x: x.get("fitness", 0))


# Need random for PIONEER
import random


# =============================================================================
# VALIDATION
# =============================================================================

def validate_instruments() -> bool:
    """Validate all instruments."""
    
    # Test LOOM
    loom = LOOM.create_balanced(4, epsilon=0.5)
    assert loom.num_channels == 4
    assert loom.total_capacity() > 0
    
    woven = loom.weave(2.0, UniformEncoder(epsilon=0.5))
    assert len(woven) == 4
    assert abs(loom.unweave(woven) - 2.0) < 0.01
    
    # Test SHIELD
    shield = SHIELD()
    packets = PacketSequence()
    packets.add_packet(0.5)
    packets.add_packet(0.3)
    
    locked = shield.lock(packets)
    valid, reason = shield.verify(locked)
    assert valid
    
    # Test AEGIS
    aegis = AEGIS()
    safe = aegis.safe_depth(0.1)
    assert safe >= 0
    
    scales = aegis.protect(packets, 3)
    assert len(scales) > 0
    
    # Test OWL
    owl = OWL()
    for v in [1.0, 1.1, 0.9, 1.05, 0.95]:
        owl.observe(v)
    
    regime = owl.classify_regime()
    assert regime in RegimeType
    
    wisdom = owl.wisdom_score()
    assert 0 <= wisdom <= 1
    
    # Test SPEAR
    spear = SPEAR()
    scale = spear.detect_scale(100.0)
    assert scale > 0
    
    staged = spear.staged_encode(5.0, UniformEncoder(epsilon=0.5))
    assert "packets" in staged
    
    # Test PIONEER
    pioneer = PIONEER()
    pioneer.initialize({"epsilon": 0.5, "ratio": 0.6})
    assert len(pioneer.population) == pioneer.population_size
    
    best = pioneer.evolve()
    assert pioneer.generation == 1
    
    return True


if __name__ == "__main__":
    print("Validating Quantum Hugging Instruments...")
    assert validate_instruments()
    print("✓ Instruments module validated")
    
    # Demo
    print("\n=== Athenachka Instrument Set Demo ===")
    
    # LOOM
    print("\n1. LOOM (Multi-Channel Weaving):")
    loom = LOOM.create_balanced(4, epsilon=0.5)
    print(f"   Channels: {loom.num_channels}")
    print(f"   Total capacity: {loom.total_capacity():.2f} bits")
    print(f"   Optimal for ε=0.1: {loom.optimal_channel_count(0.1)} channels")
    
    # SHIELD
    print("\n2. SHIELD (Tri-Lock Integrity):")
    shield = SHIELD()
    packets = PacketSequence()
    for v in [0.3, 0.4, 0.3]:
        packets.add_packet(v)
    locked = shield.lock(packets, {"purpose": "demo"})
    valid, reason = shield.verify(locked)
    print(f"   Locked packets: {packets.N}")
    print(f"   Hash: {locked['hash'][:16]}...")
    print(f"   Verified: {valid} ({reason})")
    
    # AEGIS
    print("\n3. AEGIS (Fractal Robustness):")
    aegis = AEGIS()
    safe = aegis.safe_depth(0.05)
    print(f"   Safe depth for tol=0.05: {safe}")
    scales = aegis.protect(packets, 3)
    print(f"   Protected at {len(scales)} scales")
    
    # OWL
    print("\n4. OWL (Meta-Stability Monitor):")
    owl = OWL()
    for v in [1.0, 1.02, 0.98, 1.01, 0.99, 1.0, 1.03]:
        owl.observe(v)
    report = owl.report()
    print(f"   Regime: {report['regime']}")
    print(f"   Wisdom score: {report['wisdom_score']:.3f}")
    
    # SPEAR
    print("\n5. SPEAR (Scale-Aware Staging):")
    spear = SPEAR()
    staged = spear.staged_encode(25.0, UniformEncoder(epsilon=0.5))
    print(f"   Signal scale: {staged['scale']}")
    print(f"   Packets: {staged['actual_packets']}")
    print(f"   Efficiency: {staged['efficiency']:.2f}")
    
    # PIONEER
    print("\n6. PIONEER (Observer-Aware Evolution):")
    pioneer = PIONEER()
    pioneer.initialize({"epsilon": 0.5, "ratio": 0.6, "depth": 3})
    for _ in range(5):
        pioneer.evolve()
    best = pioneer.best()
    print(f"   Generations: {pioneer.generation}")
    print(f"   Best params: ε={best.get('epsilon', 0):.3f}")
