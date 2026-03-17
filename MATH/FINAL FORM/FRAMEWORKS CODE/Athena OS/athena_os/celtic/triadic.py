"""
ATHENA OS - CELTIC OGHAM KERNEL: TRIADIC MODULE
================================================
Ternary Logic Gates and Synthesis Resolution

TRIADIC LOGIC:
    While Zoroastrianism provides Binary Logic (1 vs -1), the Celtic
    system introduces Ternary Logic (Trinary), optimizing for balance
    and synthesis.
    
THE TRIAD GATE:
    Wisdom encoded in structure: "Three things that..."
    
    A Logic Gate that resolves dualistic deadlocks.
    
    Let A be Thesis and B be Antithesis.
    The Gate outputs C such that:
    - C balances A and B
    - Creates stable triad
    
TERNARY VALUES:
    -1: Negative / Opposition / Dissolution
     0: Neutral / Balance / Synthesis  
    +1: Positive / Affirmation / Creation
    
TRIADIC RESOLUTION:
    Given opposing vectors A and B:
    Find C such that A + B + C = 0 (Static Equilibrium)
    or creates stable rotation (Dynamic Equilibrium)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
import numpy as np


# =============================================================================
# TERNARY VALUES
# =============================================================================

class TernaryValue(Enum):
    """Ternary logic values."""
    
    NEGATIVE = -1      # Opposition / Dissolution
    NEUTRAL = 0        # Balance / Synthesis
    POSITIVE = 1       # Affirmation / Creation
    
    @classmethod
    def from_int(cls, value: int) -> 'TernaryValue':
        """Create from integer (-1, 0, 1)."""
        if value < 0:
            return cls.NEGATIVE
        elif value > 0:
            return cls.POSITIVE
        return cls.NEUTRAL
    
    @classmethod
    def from_bool_pair(cls, a: bool, b: bool) -> 'TernaryValue':
        """Create from two boolean values."""
        if a and b:
            return cls.POSITIVE
        elif not a and not b:
            return cls.NEGATIVE
        return cls.NEUTRAL


# =============================================================================
# TRIAD STRUCTURE
# =============================================================================

@dataclass
class Triad:
    """
    A Celtic Triad - Three related concepts forming wisdom.
    
    "Three things that..."
    
    Structure: (Thesis, Antithesis, Synthesis)
    """
    
    first: str                      # First element
    second: str                     # Second element
    third: str                      # Third element (synthesizing)
    
    category: str = "general"       # Category of triad
    wisdom: str = ""                # The teaching
    
    def get_vector(self) -> np.ndarray:
        """Get as 3D vector (simple hash-based)."""
        import hashlib
        
        values = []
        for item in [self.first, self.second, self.third]:
            h = int(hashlib.md5(item.encode()).hexdigest()[:8], 16)
            values.append((h % 100) / 100.0)  # Normalize
        
        return np.array(values)
    
    def is_balanced(self) -> bool:
        """Check if triad is balanced (has synthesizing third)."""
        return len(self.third) > 0


# Celtic Wisdom Triads
CELTIC_TRIADS = [
    Triad("Strength", "Wisdom", "Compassion",
          category="virtue",
          wisdom="Three things required for sovereignty"),
    
    Triad("Earth", "Sea", "Sky",
          category="cosmos",
          wisdom="Three realms of existence"),
    
    Triad("Past", "Present", "Future",
          category="time",
          wisdom="Three aspects of the eternal now"),
    
    Triad("Birth", "Life", "Death",
          category="cycle",
          wisdom="Three gates all must pass"),
    
    Triad("Chaos", "Order", "Flow",
          category="state",
          wisdom="Three states of the universe"),
    
    Triad("Body", "Mind", "Spirit",
          category="being",
          wisdom="Three components of the self"),
    
    Triad("Truth", "Honor", "Justice",
          category="law",
          wisdom="Three pillars of the Brehon"),
    
    Triad("Art", "Science", "Magic",
          category="knowledge",
          wisdom="Three paths to understanding"),
]


# =============================================================================
# TERNARY LOGIC GATES
# =============================================================================

class TernaryGate:
    """
    Base class for ternary logic gates.
    
    Operates on values from {-1, 0, +1}.
    """
    
    def __init__(self, name: str = "gate"):
        self.name = name
    
    def evaluate(self, *inputs: TernaryValue) -> TernaryValue:
        """Evaluate gate with inputs."""
        raise NotImplementedError


class TernaryNOT(TernaryGate):
    """
    Ternary NOT gate.
    
    -1 → +1
     0 →  0
    +1 → -1
    """
    
    def __init__(self):
        super().__init__("NOT")
    
    def evaluate(self, a: TernaryValue) -> TernaryValue:
        return TernaryValue.from_int(-a.value)


class TernaryAND(TernaryGate):
    """
    Ternary AND gate (MIN operation).
    
    Returns minimum of inputs.
    """
    
    def __init__(self):
        super().__init__("AND")
    
    def evaluate(self, a: TernaryValue, b: TernaryValue) -> TernaryValue:
        return TernaryValue.from_int(min(a.value, b.value))


class TernaryOR(TernaryGate):
    """
    Ternary OR gate (MAX operation).
    
    Returns maximum of inputs.
    """
    
    def __init__(self):
        super().__init__("OR")
    
    def evaluate(self, a: TernaryValue, b: TernaryValue) -> TernaryValue:
        return TernaryValue.from_int(max(a.value, b.value))


class TernarySUM(TernaryGate):
    """
    Ternary SUM gate.
    
    Adds values with clamping to [-1, 0, +1].
    """
    
    def __init__(self):
        super().__init__("SUM")
    
    def evaluate(self, a: TernaryValue, b: TernaryValue) -> TernaryValue:
        result = a.value + b.value
        return TernaryValue.from_int(max(-1, min(1, result)))


class TriadGate(TernaryGate):
    """
    The Celtic Triad Gate.
    
    Given Thesis (A) and Antithesis (B), resolves deadlock
    by generating Synthesis (C).
    
    C balances A and B:
    - Static Equilibrium: A + B + C = 0
    - Dynamic Equilibrium: Creates stable rotation
    """
    
    def __init__(self):
        super().__init__("TRIAD")
    
    def evaluate(self, a: TernaryValue, b: TernaryValue) -> TernaryValue:
        """
        Generate synthesizing third value.
        
        If A and B oppose, find balancing C.
        """
        sum_ab = a.value + b.value
        
        # For equilibrium: A + B + C = 0
        # Therefore: C = -(A + B)
        c_value = -sum_ab
        
        return TernaryValue.from_int(max(-1, min(1, c_value)))
    
    def resolve_triad(self, a: TernaryValue, b: TernaryValue) -> Tuple[TernaryValue, TernaryValue, TernaryValue]:
        """Return complete balanced triad."""
        c = self.evaluate(a, b)
        return (a, b, c)
    
    def verify_equilibrium(self, a: TernaryValue, b: TernaryValue, c: TernaryValue) -> bool:
        """Verify triad is in equilibrium."""
        total = a.value + b.value + c.value
        return abs(total) <= 1  # Allow slight imbalance


# =============================================================================
# TRIADIC RESOLVER
# =============================================================================

class TriadicResolver:
    """
    Resolves conflicts between binary positions using triadic logic.
    
    System Call: triadic_resolve(Node_A, Node_B)
    
    Logic:
    1. Analyze Vectors of A and B
    2. Calculate Equilibrium: Find C such that A + B + C = 0
    3. Instantiate C (The Mediator / The Bard / The Judge)
    """
    
    def __init__(self):
        self.triad_gate = TriadGate()
        self.resolutions: int = 0
        self.deadlocks_broken: int = 0
    
    def analyze_vectors(self, 
                        vec_a: np.ndarray, 
                        vec_b: np.ndarray) -> Dict[str, Any]:
        """Analyze the opposition between two vectors."""
        # Calculate angle between vectors
        dot = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        
        if norm_a == 0 or norm_b == 0:
            cos_theta = 0
        else:
            cos_theta = dot / (norm_a * norm_b)
        
        # Determine relationship
        if cos_theta > 0.7:
            relationship = "aligned"
        elif cos_theta < -0.7:
            relationship = "opposed"
        else:
            relationship = "orthogonal"
        
        return {
            "cos_theta": cos_theta,
            "relationship": relationship,
            "magnitude_a": norm_a,
            "magnitude_b": norm_b,
            "is_deadlock": abs(cos_theta) > 0.9 and cos_theta < 0
        }
    
    def calculate_equilibrium_vector(self, 
                                      vec_a: np.ndarray,
                                      vec_b: np.ndarray) -> np.ndarray:
        """
        Calculate equilibrium vector C such that A + B + C = 0.
        
        C = -(A + B)
        """
        return -(vec_a + vec_b)
    
    def resolve(self, 
                node_a: Dict[str, Any],
                node_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve conflict between two nodes using triadic logic.
        
        Returns the synthesizing third node.
        """
        self.resolutions += 1
        
        # Get or create vectors
        vec_a = np.array(node_a.get("vector", [1, 0, 0]))
        vec_b = np.array(node_b.get("vector", [-1, 0, 0]))
        
        # Analyze opposition
        analysis = self.analyze_vectors(vec_a, vec_b)
        
        # Check for deadlock
        if analysis["is_deadlock"]:
            self.deadlocks_broken += 1
        
        # Calculate equilibrium
        vec_c = self.calculate_equilibrium_vector(vec_a, vec_b)
        
        # Create synthesizing node
        node_c = {
            "type": "synthesis",
            "vector": vec_c.tolist(),
            "role": "mediator",
            "derived_from": [node_a.get("name", "A"), node_b.get("name", "B")],
            "analysis": analysis
        }
        
        return node_c
    
    def triadic_resolve(self, 
                        thesis: Any,
                        antithesis: Any) -> Tuple[Any, Any, Any]:
        """
        Full triadic resolution.
        
        Returns (Thesis, Antithesis, Synthesis).
        """
        # Convert to nodes if needed
        if not isinstance(thesis, dict):
            thesis = {"name": str(thesis), "vector": [1, 0, 0]}
        if not isinstance(antithesis, dict):
            antithesis = {"name": str(antithesis), "vector": [-1, 0, 0]}
        
        synthesis = self.resolve(thesis, antithesis)
        
        return (thesis, antithesis, synthesis)


# =============================================================================
# TERNARY PROCESSOR
# =============================================================================

class TernaryProcessor:
    """
    Complete ternary logic processor.
    
    Provides alternative to binary dualism through
    balanced three-state logic.
    """
    
    def __init__(self):
        # Gates
        self.NOT = TernaryNOT()
        self.AND = TernaryAND()
        self.OR = TernaryOR()
        self.SUM = TernarySUM()
        self.TRIAD = TriadGate()
        
        # Resolver
        self.resolver = TriadicResolver()
        
        # State
        self.registers: Dict[str, TernaryValue] = {}
    
    def set_register(self, name: str, value: int) -> None:
        """Set a register to ternary value."""
        self.registers[name] = TernaryValue.from_int(value)
    
    def get_register(self, name: str) -> Optional[TernaryValue]:
        """Get register value."""
        return self.registers.get(name)
    
    def execute(self, operation: str, 
                operands: List[str]) -> TernaryValue:
        """
        Execute ternary operation.
        
        Operations: NOT, AND, OR, SUM, TRIAD
        """
        # Get operand values
        values = []
        for op in operands:
            if op in self.registers:
                values.append(self.registers[op])
            else:
                values.append(TernaryValue.from_int(int(op)))
        
        # Execute operation
        if operation == "NOT" and len(values) >= 1:
            return self.NOT.evaluate(values[0])
        elif operation == "AND" and len(values) >= 2:
            return self.AND.evaluate(values[0], values[1])
        elif operation == "OR" and len(values) >= 2:
            return self.OR.evaluate(values[0], values[1])
        elif operation == "SUM" and len(values) >= 2:
            return self.SUM.evaluate(values[0], values[1])
        elif operation == "TRIAD" and len(values) >= 2:
            return self.TRIAD.evaluate(values[0], values[1])
        
        return TernaryValue.NEUTRAL
    
    def balance_check(self, values: List[TernaryValue]) -> bool:
        """Check if values are balanced (sum to ~0)."""
        total = sum(v.value for v in values)
        return abs(total) <= 1
    
    def find_balance(self, values: List[TernaryValue]) -> TernaryValue:
        """Find value that would balance the set."""
        total = sum(v.value for v in values)
        return TernaryValue.from_int(-total)


# =============================================================================
# AWEN TRIPLE CHANNEL
# =============================================================================

@dataclass
class AwenChannel:
    """
    Single channel of the Awen (Three Rays).
    
    Each ray carries one aspect of creative broadcast.
    """
    
    name: str
    value: float = 0.0
    frequency: float = 1.0
    phase: float = 0.0


class AwenTripleWave:
    """
    The Awen (Three Rays) - Triple-Carrier Wave.
    
    Three orthogonal channels:
    - Nature (Physical reality)
    - Knowledge (Information)
    - Truth (Alignment)
    
    Together provide raw data stream for Bardic synthesis.
    """
    
    def __init__(self):
        self.channels = {
            "nature": AwenChannel("nature", frequency=1.0, phase=0),
            "knowledge": AwenChannel("knowledge", frequency=1.0, phase=2*np.pi/3),
            "truth": AwenChannel("truth", frequency=1.0, phase=4*np.pi/3),
        }
        self.time: float = 0.0
    
    def sample(self, t: float = None) -> Dict[str, float]:
        """Sample all three channels at time t."""
        if t is None:
            t = self.time
        
        samples = {}
        for name, channel in self.channels.items():
            # Sinusoidal wave
            value = np.sin(2 * np.pi * channel.frequency * t + channel.phase)
            samples[name] = value
        
        return samples
    
    def get_composite(self, t: float = None) -> np.ndarray:
        """Get composite 3D vector of all channels."""
        samples = self.sample(t)
        return np.array([
            samples["nature"],
            samples["knowledge"],
            samples["truth"]
        ])
    
    def advance(self, dt: float = 0.1) -> None:
        """Advance time."""
        self.time += dt
    
    def get_inspiration(self) -> str:
        """
        Get inspirational output from current Awen state.
        
        Used by Bards for synthesis.
        """
        samples = self.sample()
        
        # Determine dominant channel
        dominant = max(samples.items(), key=lambda x: abs(x[1]))
        
        inspirations = {
            "nature": "Draw from the natural world",
            "knowledge": "Draw from accumulated wisdom",
            "truth": "Draw from eternal principles"
        }
        
        return inspirations.get(dominant[0], "Balance all three rays")


# =============================================================================
# VALIDATION
# =============================================================================

def validate_triadic() -> bool:
    """Validate triadic module."""
    
    # Test Ternary Values
    neg = TernaryValue.NEGATIVE
    neu = TernaryValue.NEUTRAL
    pos = TernaryValue.POSITIVE
    
    assert neg.value == -1
    assert neu.value == 0
    assert pos.value == 1
    
    # Test NOT gate
    not_gate = TernaryNOT()
    assert not_gate.evaluate(pos) == neg
    assert not_gate.evaluate(neg) == pos
    assert not_gate.evaluate(neu) == neu
    
    # Test AND gate (MIN)
    and_gate = TernaryAND()
    assert and_gate.evaluate(pos, neg) == neg
    assert and_gate.evaluate(pos, pos) == pos
    
    # Test OR gate (MAX)
    or_gate = TernaryOR()
    assert or_gate.evaluate(pos, neg) == pos
    assert or_gate.evaluate(neg, neg) == neg
    
    # Test Triad Gate
    triad = TriadGate()
    result = triad.evaluate(pos, neg)
    assert result == neu  # +1 + -1 needs 0 for balance
    
    # Test Triadic Resolver
    resolver = TriadicResolver()
    node_a = {"name": "Thesis", "vector": [1, 0, 0]}
    node_b = {"name": "Antithesis", "vector": [-1, 0, 0]}
    synthesis = resolver.resolve(node_a, node_b)
    assert synthesis["type"] == "synthesis"
    
    # Test Ternary Processor
    processor = TernaryProcessor()
    processor.set_register("A", 1)
    processor.set_register("B", -1)
    result = processor.execute("TRIAD", ["A", "B"])
    assert result == TernaryValue.NEUTRAL
    
    # Test Awen
    awen = AwenTripleWave()
    samples = awen.sample(0)
    assert "nature" in samples
    assert "knowledge" in samples
    assert "truth" in samples
    
    # Test Triads
    assert len(CELTIC_TRIADS) > 0
    for t in CELTIC_TRIADS:
        assert t.is_balanced()
    
    return True


if __name__ == "__main__":
    print("Validating Triadic Module...")
    assert validate_triadic()
    print("✓ Triadic Module validated")
    
    # Demo
    print("\n--- Ternary Logic Demo ---")
    processor = TernaryProcessor()
    
    print("\nTernary Gates:")
    pos = TernaryValue.POSITIVE
    neg = TernaryValue.NEGATIVE
    
    not_gate = TernaryNOT()
    print(f"  NOT(+1) = {not_gate.evaluate(pos).value}")
    
    and_gate = TernaryAND()
    print(f"  AND(+1, -1) = {and_gate.evaluate(pos, neg).value}")
    
    triad = TriadGate()
    print(f"  TRIAD(+1, -1) = {triad.evaluate(pos, neg).value}")
    
    print("\n--- Triadic Resolution ---")
    resolver = TriadicResolver()
    thesis, antithesis, synthesis = resolver.triadic_resolve(
        "Creation", "Destruction"
    )
    print(f"  Thesis: {thesis['name']}")
    print(f"  Antithesis: {antithesis['name']}")
    print(f"  Synthesis: {synthesis['role']}")
    
    print("\n--- Celtic Triads ---")
    for t in CELTIC_TRIADS[:3]:
        print(f"  {t.first} + {t.second} + {t.third}")
        print(f"    → {t.wisdom}")
