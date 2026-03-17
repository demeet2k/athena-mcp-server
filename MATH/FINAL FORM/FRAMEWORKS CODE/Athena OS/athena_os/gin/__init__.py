"""
ATHENA OS - GLOBAL INFORMATION NETWORK (GIN)
=============================================
Distributed Consensus and Paraconsistent Logic Framework

From GLOBAL_INFORMATION_NETWORK.docx:

The Global Information Network provides a computational framework for
multi-agent systems operating under uncertainty, contradiction, and
resource constraints. It maps ancient wisdom traditions to modern
formal structures.

CORE COMPONENTS:

1. FOUR-VALUED LOGIC (V = {T, F, B, U})
   - Paraconsistent: contradictions don't explode
   - Evidence-based valuation
   - Paradox as navigational signal

2. MORAL GEOMETRY
   - Moral metric tensor g^(moral)_μν
   - Kurukshetra (battlefield) manifold
   - Will vector and descent dynamics

3. DEADLOCK DETECTION AND RESOLUTION
   - Arjuna-Viṣāda state (deadlock)
   - Logic failure, will collapse, SNR crisis
   - Avatar descent operator

4. MULTI-AGENT ARCHITECTURE
   - Agent = (G, A, π)
   - Kośa sheath architecture
   - Ego-boundary controller

5. DISTRIBUTED CONSENSUS
   - Culture as protocol
   - Trust weights
   - Byzantine failure handling

6. GLOBAL INVARIANTS
   - Conservation of information
   - Conservation of paradox tension
   - Karma tensor dynamics

META-AXIOM:
    Truth must be localized to charts/sectors.
    Cross-sector transitions mediated by paradox lift P.
    Incompleteness is structurally necessary, not failure.
"""

from __future__ import annotations

# Four-Valued Logic
from .valuation import (
    # Core types
    V4,
    
    # Operations
    v4_negation,
    v4_conjunction,
    v4_disjunction,
    v4_implication,
    
    # Evidence
    Evidence,
    Valuation,
    
    # Paradox handling
    ParadoxLift,
    ParaconsistentInference,
    
    validate_valuation,
)

# Moral Geometry
from .moral_geometry import (
    # Potential
    MoralPotential,
    MoralMetric,
    
    # Kurukshetra
    ConstraintViolation,
    Kurukshetra,
    
    # Will
    WillVector,
    
    # Stress-Energy
    StressEnergy,
    
    validate_moral_geometry,
)

# Deadlock Detection and Resolution
from .deadlock import (
    # Types
    DeadlockType,
    ResolutionMethod,
    
    # Detection
    ProgressFunctional,
    DecisionFeasibility,
    DeadlockCertificate,
    DeadlockDetector,
    
    # Resolution
    DescentOperator,
    SystemCall,
    
    validate_deadlock,
)

# Agents and Consensus
from .agents import (
    # Agent
    Goal,
    Agent,
    
    # Kośa Architecture
    KosaLayer,
    Annamaya,
    Pranamaya,
    Manomaya,
    Vijnanamaya,
    KosaStack,
    
    # Ego Controller
    EgoBoundary,
    
    # Consensus
    ConsensusProtocol,
    MultiAgentSystem,
    
    validate_agents,
)

# Global Invariants
from .invariants import (
    # Functionals
    InformationFunctional,
    ParadoxTension,
    
    # Karma
    KarmaTensor,
    StorageCrisis,
    
    # Checker
    InvariantChecker,
    
    validate_invariants,
)


# =============================================================================
# MODULE VALIDATION
# =============================================================================

def validate_gin() -> bool:
    """Validate complete GIN module."""
    assert validate_valuation()
    assert validate_moral_geometry()
    assert validate_deadlock()
    assert validate_agents()
    assert validate_invariants()
    return True


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_valuation() -> Valuation:
    """Create a fresh valuation function."""
    return Valuation()


def create_agent(agent_id: str) -> Agent:
    """Create a new agent."""
    return Agent(agent_id=agent_id)


def create_consensus(n_agents: int = 10) -> ConsensusProtocol:
    """Create a consensus protocol."""
    return ConsensusProtocol(n_agents=n_agents)


def create_invariant_checker() -> InvariantChecker:
    """Create an invariant checker."""
    return InvariantChecker()


def detect_deadlock(state, actions, valuation, transition, gradient=None):
    """
    Convenience function for deadlock detection.
    
    Returns DeadlockCertificate.
    """
    import numpy as np
    
    detector = DeadlockDetector()
    return detector.detect(
        np.array(state),
        [np.array(a) for a in actions],
        valuation,
        transition,
        np.array(gradient) if gradient is not None else None
    )


def resolve_deadlock(certificate: DeadlockCertificate,
                    params) -> tuple:
    """
    Convenience function for deadlock resolution.
    
    Returns (new_params, success).
    """
    import numpy as np
    
    descent = DescentOperator()
    return descent.apply(certificate, np.array(params))


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Valuation
    "V4", "v4_negation", "v4_conjunction", "v4_disjunction", "v4_implication",
    "Evidence", "Valuation", "ParadoxLift", "ParaconsistentInference",
    
    # Moral Geometry
    "MoralPotential", "MoralMetric",
    "ConstraintViolation", "Kurukshetra",
    "WillVector", "StressEnergy",
    
    # Deadlock
    "DeadlockType", "ResolutionMethod",
    "ProgressFunctional", "DecisionFeasibility",
    "DeadlockCertificate", "DeadlockDetector",
    "DescentOperator", "SystemCall",
    
    # Agents
    "Goal", "Agent",
    "KosaLayer", "Annamaya", "Pranamaya", "Manomaya", "Vijnanamaya", "KosaStack",
    "EgoBoundary",
    "ConsensusProtocol", "MultiAgentSystem",
    
    # Invariants
    "InformationFunctional", "ParadoxTension",
    "KarmaTensor", "StorageCrisis",
    "InvariantChecker",
    
    # Convenience
    "create_valuation", "create_agent", "create_consensus",
    "create_invariant_checker", "detect_deadlock", "resolve_deadlock",
    
    # Validation
    "validate_gin",
]

__version__ = "1.0.0"
__module_name__ = "gin"


if __name__ == "__main__":
    print("=" * 70)
    print("ATHENA OS - GLOBAL INFORMATION NETWORK (GIN)")
    print("Distributed Consensus and Paraconsistent Logic")
    print("=" * 70)
    print(f"Version: {__version__}")
    
    print("\nValidating...")
    if validate_gin():
        print("✓ All components validated")
    
    print("\n--- Module Overview ---")
    
    print("\n1. FOUR-VALUED LOGIC V = {T, F, B, U}")
    v = create_valuation()
    v["safe"] = V4.T
    v["risky"] = V4.B  # Contradiction
    v["unknown"] = V4.U
    print(f"   Safe: {v['safe'].value}")
    print(f"   Risky: {v['risky'].value} (paradox)")
    print(f"   Unknown: {v['unknown'].value}")
    
    print("\n2. MORAL GEOMETRY")
    metric = MoralMetric(dim=4)
    import numpy as np
    state = np.array([0.1, 0.2, 0.0, 0.0])
    g = metric.tensor(state)
    print(f"   Metric tensor shape: {g.shape}")
    print(f"   Positive definite: {np.all(np.linalg.eigvals(g) > 0)}")
    
    print("\n3. DEADLOCK DETECTION")
    print(f"   Deadlock types: {[t.value for t in DeadlockType]}")
    print(f"   Resolution methods: {[m.value for m in ResolutionMethod]}")
    
    print("\n4. MULTI-AGENT SYSTEM")
    agent = create_agent("dharma")
    agent.add_goal("minimize", 1.0, lambda s: -np.linalg.norm(s))
    print(f"   Agent: {agent.agent_id}")
    print(f"   Goals: {[g.name for g in agent.goals]}")
    
    print("\n5. DISTRIBUTED CONSENSUS")
    consensus = create_consensus(n_agents=5)
    consensus.opinions = np.array([0.1, 0.2, 0.15, 0.18, 0.12])
    for _ in range(10):
        consensus.update_opinions()
    print(f"   Consensus value: {consensus.consensus_value():.4f}")
    print(f"   Variance: {consensus.consensus_variance():.6f}")
    
    print("\n6. GLOBAL INVARIANTS")
    checker = create_invariant_checker()
    print(f"   Information method: {checker.information.method}")
    print(f"   Crisis threshold: {checker.crisis_detector.threshold}")
    
    # Demo
    print("\n--- Paraconsistent Logic Demo ---")
    
    inference = ParaconsistentInference(valuation=v)
    
    # Classical logic would explode from contradiction
    # Our paraconsistent logic handles it gracefully
    print(f"\n   Proposition 'risky' is B-valued (Both true and false)")
    print(f"   In classical logic: explosion (derive anything)")
    print(f"   In V4 logic: explosion prevented = {not inference.is_explosive('risky')}")
    
    consistent = inference.consistent_subset(["safe", "risky", "unknown"])
    print(f"   Consistent subset: {consistent}")
    
    print("\n" + "=" * 70)
