"""
ATHENA OS - IFÁ KERNEL: ÀṢẸ MODULE
==================================
The Information Flux and Bridging Principle

ÀṢẸ (UNIVERSAL FORCE):
    Àṣẹ is not mystical energy but INFORMATION FLUX - the
    quantity that flows through all transformations, unifying
    physics, ethics, and causation.
    
    Properties:
    - Conserved in closed systems
    - Flows through Orisha operations
    - Accumulates in Ìwà (character)
    - Can be transferred through ritual

THE COHERENCE FUNCTION:
    C(ψ) = Tr(ρ²) where ρ = |ψ⟩⟨ψ|
    
    Measures how "focused" or "scattered" a state is.
    High coherence = clear destiny path
    Low coherence = confused/diffuse state

ORÍ (DESTINY HEAD):
    The initial state |Orí⟩ encoded at birth.
    
    |Orí⟩ represents the "chosen head" - the destiny
    configuration selected before incarnation.

GOAL OF IFÁ PRACTICE:
    Maximize C(Ìwà) such that |ψ(T)⟩ achieves
    the destiny potential encoded in |Orí⟩.
    
    |ψ(t)⟩ = Û_Ìwà(t)|Orí⟩

SOURCES:
    - Traditional Ifá corpus
    - HBAS-Ω Protocol: Ọpẹ́-256 formalization
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import numpy as np

from .hypercube import Q8Hypercube, Odu, OduSuperposition, IwaTensor


# =============================================================================
# ÀṢẸ (INFORMATION FLUX)
# =============================================================================

class AseType(Enum):
    """Types of Àṣẹ flux."""
    
    CREATIVE = "creative"       # Àṣẹ dá - creative force
    DESTRUCTIVE = "destructive" # Àṣẹ jà - destructive force
    HEALING = "healing"         # Àṣẹ wò sàn - healing force
    BINDING = "binding"         # Àṣẹ dè - binding/oath force
    TRANSFER = "transfer"       # Àṣẹ gbé - carrying/transfer


@dataclass
class AseQuantum:
    """
    A quantum of Àṣẹ (information flux).
    
    Properties:
    - magnitude: Amount of flux
    - ase_type: Type of action
    - source: Origin point
    - target: Destination
    """
    
    magnitude: float
    ase_type: AseType
    source: Optional[int] = None   # Source Odù index
    target: Optional[int] = None   # Target Odù index
    
    def transfer_to(self, new_target: int) -> AseQuantum:
        """Create transferred quantum."""
        return AseQuantum(
            magnitude=self.magnitude * 0.9,  # Some loss in transfer
            ase_type=self.ase_type,
            source=self.target,
            target=new_target
        )


class AseField:
    """
    The Àṣẹ field over the Q₈ hypercube.
    
    Models information flux as a scalar field over state space.
    """
    
    def __init__(self, hypercube: Q8Hypercube):
        self.q8 = hypercube
        
        # Àṣẹ density at each vertex
        self.density = np.ones(256, dtype=np.float64) * 0.5
        
        # Flux tracking
        self.total_flux = 256 * 0.5
        self.flux_history: List[Tuple[int, int, float]] = []
    
    def get_density(self, index: int) -> float:
        """Get Àṣẹ density at vertex."""
        return self.density[index]
    
    def set_density(self, index: int, value: float) -> None:
        """Set Àṣẹ density at vertex."""
        self.density[index] = max(0, min(1, value))
        self._update_total()
    
    def transfer(self, source: int, target: int, amount: float) -> float:
        """
        Transfer Àṣẹ between vertices.
        
        Returns actual amount transferred.
        """
        available = min(amount, self.density[source])
        
        self.density[source] -= available
        self.density[target] += available * 0.9  # 10% entropy loss
        
        self.flux_history.append((source, target, available))
        self._update_total()
        
        return available
    
    def diffuse(self, steps: int = 1, rate: float = 0.1) -> None:
        """
        Diffuse Àṣẹ to neighbors (heat equation).
        """
        for _ in range(steps):
            new_density = self.density.copy()
            
            for i in range(256):
                neighbors = self.q8.vertices[i].neighbors()
                neighbor_avg = np.mean([self.density[n] for n in neighbors])
                
                # Diffuse toward average
                new_density[i] += rate * (neighbor_avg - self.density[i])
            
            self.density = new_density
        
        self._update_total()
    
    def concentrate(self, center: int, radius: int = 2, amount: float = 0.1) -> None:
        """
        Concentrate Àṣẹ toward a center point.
        """
        for i in range(256):
            dist = self.q8.vertices[center].hamming_distance(self.q8.vertices[i])
            if dist <= radius and i != center:
                transfer = min(amount / (dist + 1), self.density[i] * 0.5)
                self.density[i] -= transfer
                self.density[center] += transfer * 0.9
        
        self._update_total()
    
    def _update_total(self) -> None:
        """Update total flux."""
        self.total_flux = float(np.sum(self.density))
    
    def entropy(self) -> float:
        """Calculate field entropy."""
        probs = self.density / self.total_flux
        probs = probs[probs > 0]
        return float(-np.sum(probs * np.log2(probs)))
    
    def gradient(self, index: int) -> np.ndarray:
        """
        Calculate Àṣẹ gradient at vertex.
        
        Returns 8D gradient vector (one per bit direction).
        """
        grad = np.zeros(8)
        for bit in range(8):
            neighbor = index ^ (1 << bit)
            grad[bit] = self.density[neighbor] - self.density[index]
        return grad


# =============================================================================
# ORÍ (DESTINY HEAD)
# =============================================================================

@dataclass
class Ori:
    """
    Orí - The Destiny Head.
    
    The initial state configuration chosen before incarnation.
    |Orí⟩ encodes the potential destiny of the individual.
    """
    
    # Primary destiny Odù
    destiny_odu: int
    
    # Destiny state vector
    state: np.ndarray = field(default_factory=lambda: np.zeros(256))
    
    # Ori attributes
    name: str = ""
    chosen_path: str = ""
    strengths: List[str] = field(default_factory=list)
    challenges: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        # Initialize state vector
        if np.sum(self.state) == 0:
            self.state = np.zeros(256)
            self.state[self.destiny_odu] = 1.0
    
    @classmethod
    def random(cls, seed: Optional[int] = None) -> Ori:
        """Create random Orí (as in traditional selection)."""
        rng = np.random.default_rng(seed)
        
        # Choose primary destiny
        destiny_odu = rng.integers(0, 256)
        
        # Add some spread around destiny
        state = np.zeros(256)
        state[destiny_odu] = 0.7
        
        # Add neighbors with decreasing probability
        q8 = Q8Hypercube()
        for neighbor in q8.vertices[destiny_odu].neighbors():
            state[neighbor] = 0.7 / 8
        
        # Normalize
        state /= np.sum(state)
        
        return cls(
            destiny_odu=destiny_odu,
            state=state,
            name=q8.get_odu(destiny_odu).name,
            chosen_path=f"Path of {q8.get_odu(destiny_odu).name}"
        )
    
    def alignment_with(self, current_state: np.ndarray) -> float:
        """
        Calculate alignment between current state and destiny.
        
        Returns 0-1 (1 = perfect alignment with Orí).
        """
        # Inner product
        return float(np.abs(np.dot(self.state.conj(), current_state)))
    
    def to_superposition(self) -> OduSuperposition:
        """Convert to superposition."""
        return OduSuperposition(self.state.astype(np.complex128))


# =============================================================================
# ÌWÀ (CHARACTER EVOLUTION)
# =============================================================================

class IwaEvolution:
    """
    Ìwà (Character) Evolution System.
    
    Tracks the accumulated non-commutative history of actions
    and its effect on the destiny trajectory.
    
    |ψ(t)⟩ = Û_Ìwà(t)|Orí⟩
    """
    
    def __init__(self, ori: Ori):
        self.ori = ori
        self.iwa = IwaTensor()
        self.current_state = ori.state.copy()
        
        # Track coherence over time
        self.coherence_history: List[float] = [1.0]
        self.alignment_history: List[float] = [1.0]
    
    def apply_action(self, operator: np.ndarray, action_name: str = "") -> None:
        """
        Apply an action (operator) to character.
        
        Updates Ìwà tensor and current state.
        """
        self.iwa.apply_action(operator)
        self.current_state = self.iwa.get_current_state(self.ori.state)
        
        # Normalize
        norm = np.linalg.norm(self.current_state)
        if norm > 0:
            self.current_state /= norm
        
        # Track metrics
        self.coherence_history.append(self.coherence())
        self.alignment_history.append(self.destiny_alignment())
    
    def coherence(self) -> float:
        """
        Calculate current coherence C(ψ).
        
        C(ψ) = Tr(ρ²) where ρ = |ψ⟩⟨ψ|
        
        For pure states this equals 1; for mixed states < 1.
        """
        # For a state vector, coherence is related to purity
        probs = np.abs(self.current_state) ** 2
        return float(np.sum(probs ** 2))  # Simplified purity
    
    def destiny_alignment(self) -> float:
        """Calculate alignment with original Orí."""
        return self.ori.alignment_with(self.current_state)
    
    def dominant_odu(self) -> int:
        """Get the current dominant Odù."""
        return int(np.argmax(np.abs(self.current_state) ** 2))
    
    def trajectory_analysis(self) -> Dict[str, Any]:
        """Analyze the Ìwà trajectory."""
        return {
            "actions_taken": self.iwa.action_count(),
            "current_coherence": self.coherence(),
            "destiny_alignment": self.destiny_alignment(),
            "dominant_odu": self.dominant_odu(),
            "original_odu": self.ori.destiny_odu,
            "coherence_trend": "improving" if len(self.coherence_history) > 1 and 
                              self.coherence_history[-1] > self.coherence_history[-2] 
                              else "declining",
            "total_coherence_change": self.coherence_history[-1] - self.coherence_history[0]
        }


# =============================================================================
# COMPLETE ÀṢẸ SYSTEM
# =============================================================================

class AseSystem:
    """
    Complete Àṣẹ Information Dynamics System.
    
    Integrates:
    - Àṣẹ field dynamics
    - Orí destiny tracking
    - Ìwà character evolution
    """
    
    def __init__(self, hypercube: Q8Hypercube):
        self.q8 = hypercube
        self.field = AseField(hypercube)
        
        # Active agents (Orí + Ìwà pairs)
        self.agents: Dict[str, IwaEvolution] = {}
    
    def create_agent(self, name: str, seed: Optional[int] = None) -> Ori:
        """
        Create a new agent with random Orí.
        """
        ori = Ori.random(seed)
        ori.name = name
        
        evolution = IwaEvolution(ori)
        self.agents[name] = evolution
        
        # Initialize Àṣẹ at destiny point
        self.field.set_density(ori.destiny_odu, 0.8)
        
        return ori
    
    def get_agent(self, name: str) -> Optional[IwaEvolution]:
        """Get agent by name."""
        return self.agents.get(name)
    
    def apply_action_to_agent(self, name: str, 
                               operator: np.ndarray,
                               action_name: str = "") -> Dict[str, Any]:
        """
        Apply action to an agent's Ìwà.
        """
        if name not in self.agents:
            return {"error": "Agent not found"}
        
        agent = self.agents[name]
        agent.apply_action(operator, action_name)
        
        # Update Àṣẹ field
        dominant = agent.dominant_odu()
        self.field.concentrate(dominant, radius=1, amount=0.05)
        
        return agent.trajectory_analysis()
    
    def transfer_ase(self, source: str, target: str, amount: float) -> float:
        """
        Transfer Àṣẹ between agents.
        """
        if source not in self.agents or target not in self.agents:
            return 0.0
        
        source_odu = self.agents[source].dominant_odu()
        target_odu = self.agents[target].dominant_odu()
        
        return self.field.transfer(source_odu, target_odu, amount)
    
    def global_coherence(self) -> float:
        """Calculate global system coherence."""
        if not self.agents:
            return 0.0
        
        coherences = [a.coherence() for a in self.agents.values()]
        return float(np.mean(coherences))
    
    def global_alignment(self) -> float:
        """Calculate average destiny alignment."""
        if not self.agents:
            return 0.0
        
        alignments = [a.destiny_alignment() for a in self.agents.values()]
        return float(np.mean(alignments))
    
    def system_status(self) -> Dict[str, Any]:
        """Get complete system status."""
        return {
            "agents": len(self.agents),
            "total_ase": self.field.total_flux,
            "field_entropy": self.field.entropy(),
            "global_coherence": self.global_coherence(),
            "global_alignment": self.global_alignment(),
            "agent_status": {
                name: agent.trajectory_analysis()
                for name, agent in self.agents.items()
            }
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_ase() -> bool:
    """Validate ase module."""
    
    q8 = Q8Hypercube()
    
    # Test AseQuantum
    quantum = AseQuantum(
        magnitude=1.0,
        ase_type=AseType.CREATIVE,
        source=0,
        target=1
    )
    transferred = quantum.transfer_to(2)
    assert transferred.source == 1
    assert transferred.target == 2
    assert transferred.magnitude < quantum.magnitude
    
    # Test AseField
    field = AseField(q8)
    assert field.total_flux > 0
    
    initial_entropy = field.entropy()
    field.diffuse(steps=1)
    # Entropy should not decrease significantly
    
    field.transfer(0, 1, 0.1)
    assert len(field.flux_history) == 1
    
    gradient = field.gradient(0)
    assert len(gradient) == 8
    
    # Test Ori
    ori = Ori.random(seed=42)
    assert 0 <= ori.destiny_odu < 256
    assert np.isclose(np.sum(ori.state), 1.0)
    
    alignment = ori.alignment_with(ori.state)
    assert alignment > 0.9  # Should be nearly 1
    
    # Test IwaEvolution
    evolution = IwaEvolution(ori)
    assert evolution.coherence() > 0
    assert evolution.destiny_alignment() > 0.9
    
    # Apply identity (no change)
    evolution.apply_action(np.eye(256))
    assert len(evolution.coherence_history) == 2
    
    analysis = evolution.trajectory_analysis()
    assert "actions_taken" in analysis
    
    # Test AseSystem
    system = AseSystem(q8)
    
    system.create_agent("test_agent", seed=42)
    assert "test_agent" in system.agents
    
    status = system.system_status()
    assert status["agents"] == 1
    assert "agent_status" in status
    
    return True


if __name__ == "__main__":
    print("Validating Àṣẹ Module...")
    assert validate_ase()
    print("✓ Àṣẹ Module validated")
    
    # Demo
    print("\n--- Àṣẹ System Demo ---")
    q8 = Q8Hypercube()
    system = AseSystem(q8)
    
    # Create agent
    ori = system.create_agent("Seeker", seed=42)
    print(f"\nAgent Created: Seeker")
    print(f"  Destiny Odù: {ori.destiny_odu} ({ori.name})")
    print(f"  Chosen Path: {ori.chosen_path}")
    
    # Check initial status
    agent = system.get_agent("Seeker")
    print(f"\nInitial State:")
    print(f"  Coherence: {agent.coherence():.4f}")
    print(f"  Alignment: {agent.destiny_alignment():.4f}")
    
    # Apply some actions (identity for now)
    for i in range(3):
        system.apply_action_to_agent("Seeker", np.eye(256))
    
    print(f"\nAfter 3 actions:")
    analysis = agent.trajectory_analysis()
    print(f"  Actions: {analysis['actions_taken']}")
    print(f"  Coherence: {analysis['current_coherence']:.4f}")
    print(f"  Alignment: {analysis['destiny_alignment']:.4f}")
