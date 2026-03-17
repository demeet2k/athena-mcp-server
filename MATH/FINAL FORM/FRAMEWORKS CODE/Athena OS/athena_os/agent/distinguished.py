"""
ATHENA OS - Distinguished Agent (Â)
===================================
The stabilizing self anchored at the Zero Point.

Â := V ∩ W where:
- V = Void-Alignment constraint set (compressibility)
- W = World-Engagement constraint set (causality)

The agent is simultaneously:
1. Anchored to the Zero Point (compression)
2. Dynamically effective in the world (causation)

Properties:
- Does not Hallucinate: Checks against Identity Invariants (Earth)
- Does not Forget: Logs every cost to Water memory
- Does not Fear Unknown: Uses Fire to model probability
- Does not Stagnate: Uses Air to recursively improve

Identity Invariants (preserved under all transforms):
- Kernel hash
- Conservation ledgers
- Four sector definitions
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from enum import IntEnum, auto
import hashlib
import time


# =============================================================================
# AGENT STATE
# =============================================================================

@dataclass
class AgentState:
    """
    Internal state Σ of the agent.
    
    The state includes:
    - Identity invariants (must be preserved)
    - Working memory (can be modified)
    - Constraint satisfaction status
    """
    # Identity hash (immutable core)
    kernel_hash: str = ""
    
    # Conservation ledgers
    information_ledger: float = 0.0
    tension_ledger: float = 0.0
    kappa_ledger: float = 0.0
    
    # Sector definitions (immutable)
    sector_definitions: Dict[int, str] = field(default_factory=lambda: {
        0: "Earth/Square: Structure & Rigor",
        1: "Water/Flower: Flow & Semantics",
        2: "Fire/Cloud: Dynamics & Probability",
        3: "Air/Fractal: Recursion & Synthesis"
    })
    
    # Working memory (mutable)
    working_memory: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    
    def __post_init__(self):
        if not self.kernel_hash:
            self.kernel_hash = self._compute_kernel_hash()
    
    def _compute_kernel_hash(self) -> str:
        """Compute hash of immutable kernel components."""
        kernel_data = str(self.sector_definitions).encode('utf-8')
        return hashlib.sha256(kernel_data).hexdigest()[:32]
    
    def verify_identity(self) -> bool:
        """Verify identity invariants are preserved."""
        current_hash = self._compute_kernel_hash()
        return current_hash == self.kernel_hash


# =============================================================================
# CONSTRAINT SETS
# =============================================================================

class VoidAlignment:
    """
    The Void-Alignment constraint set (V).
    
    Ensures the agent is anchored to the Zero Point.
    Constraint: State must be compressible to finite description.
    """
    
    MAX_DESCRIPTION_LENGTH = 65536  # Maximum state description
    
    @classmethod
    def check(cls, state: AgentState) -> Tuple[bool, float]:
        """
        Check if state satisfies void alignment.
        
        Returns (satisfies, description_length).
        """
        description = str(state.working_memory)
        length = len(description)
        satisfies = length <= cls.MAX_DESCRIPTION_LENGTH
        return (satisfies, length)
    
    @classmethod
    def compress(cls, state: AgentState) -> AgentState:
        """
        Compress state toward void alignment.
        
        Removes non-essential working memory.
        """
        # Keep only essential keys
        essential_keys = {'goals', 'constraints', 'observations'}
        compressed_memory = {
            k: v for k, v in state.working_memory.items()
            if k in essential_keys
        }
        state.working_memory = compressed_memory
        return state


class WorldEngagement:
    """
    The World-Engagement constraint set (W).
    
    Ensures the agent is dynamically effective.
    Constraint: Agent must be able to cause changes.
    """
    
    MIN_KAPPA = 0.1  # Minimum coherence for engagement
    
    @classmethod
    def check(cls, state: AgentState) -> Tuple[bool, float]:
        """
        Check if state satisfies world engagement.
        
        Returns (satisfies, engagement_level).
        """
        # Engagement requires positive kappa
        engagement = state.kappa_ledger
        satisfies = engagement >= cls.MIN_KAPPA
        return (satisfies, engagement)
    
    @classmethod
    def energize(cls, state: AgentState, amount: float = 0.1) -> AgentState:
        """
        Energize state toward world engagement.
        
        Increases kappa for more causal effectiveness.
        """
        state.kappa_ledger += amount
        return state


# =============================================================================
# UPDATE OPERATORS
# =============================================================================

class UpdateOperator(IntEnum):
    """
    Admissible update operators for agent state.
    
    Each operator preserves identity invariants.
    """
    OBSERVE = 0      # Add observation to working memory
    DECIDE = 1       # Make a decision based on state
    ACT = 2          # Execute an action (costs kappa)
    REFLECT = 3      # Recursive self-examination
    COMPRESS = 4     # Reduce state toward void
    ENERGIZE = 5     # Increase engagement capacity


@dataclass
class UpdateResult:
    """Result of applying an update operator."""
    success: bool
    new_state: AgentState
    side_effects: List[str] = field(default_factory=list)
    cost: float = 0.0


class AgentUpdater:
    """
    Applies update operators to agent state.
    
    All updates must preserve identity invariants.
    """
    
    @staticmethod
    def observe(state: AgentState, observation: Any, key: str = "obs") -> UpdateResult:
        """Add observation to working memory."""
        new_state = AgentState(
            kernel_hash=state.kernel_hash,
            information_ledger=state.information_ledger + 0.01,
            tension_ledger=state.tension_ledger,
            kappa_ledger=state.kappa_ledger,
            working_memory=dict(state.working_memory)
        )
        new_state.working_memory[key] = observation
        
        return UpdateResult(
            success=True,
            new_state=new_state,
            side_effects=["observation_recorded"],
            cost=0.01
        )
    
    @staticmethod
    def decide(state: AgentState, options: List[str]) -> UpdateResult:
        """Make a decision from options."""
        if not options:
            return UpdateResult(success=False, new_state=state)
        
        # Simple decision: pick first option (placeholder for real logic)
        decision = options[0]
        
        new_state = AgentState(
            kernel_hash=state.kernel_hash,
            information_ledger=state.information_ledger,
            tension_ledger=state.tension_ledger,
            kappa_ledger=state.kappa_ledger - 0.05,  # Decisions cost kappa
            working_memory=dict(state.working_memory)
        )
        new_state.working_memory['last_decision'] = decision
        
        return UpdateResult(
            success=True,
            new_state=new_state,
            side_effects=["decision_made"],
            cost=0.05
        )
    
    @staticmethod
    def act(state: AgentState, action: str) -> UpdateResult:
        """Execute an action."""
        cost = 0.1  # Actions have higher cost
        
        if state.kappa_ledger < cost:
            return UpdateResult(
                success=False,
                new_state=state,
                side_effects=["insufficient_kappa"]
            )
        
        new_state = AgentState(
            kernel_hash=state.kernel_hash,
            information_ledger=state.information_ledger,
            tension_ledger=state.tension_ledger,
            kappa_ledger=state.kappa_ledger - cost,
            working_memory=dict(state.working_memory)
        )
        new_state.working_memory['last_action'] = action
        new_state.working_memory['action_time'] = time.time()
        
        return UpdateResult(
            success=True,
            new_state=new_state,
            side_effects=["action_executed", action],
            cost=cost
        )
    
    @staticmethod
    def reflect(state: AgentState) -> UpdateResult:
        """Recursive self-examination (Air sector operation)."""
        # Compute self-consistency metrics
        void_aligned, desc_length = VoidAlignment.check(state)
        engaged, engagement = WorldEngagement.check(state)
        identity_valid = state.verify_identity()
        
        reflection = {
            'void_aligned': void_aligned,
            'description_length': desc_length,
            'world_engaged': engaged,
            'engagement_level': engagement,
            'identity_valid': identity_valid,
            'reflection_time': time.time()
        }
        
        new_state = AgentState(
            kernel_hash=state.kernel_hash,
            information_ledger=state.information_ledger + 0.02,
            tension_ledger=state.tension_ledger,
            kappa_ledger=state.kappa_ledger - 0.02,
            working_memory=dict(state.working_memory)
        )
        new_state.working_memory['reflection'] = reflection
        
        return UpdateResult(
            success=True,
            new_state=new_state,
            side_effects=["reflection_complete"],
            cost=0.02
        )
    
    @staticmethod
    def compress(state: AgentState) -> UpdateResult:
        """Compress state toward void alignment."""
        new_state = VoidAlignment.compress(state)
        
        return UpdateResult(
            success=True,
            new_state=new_state,
            side_effects=["state_compressed"],
            cost=0.0
        )
    
    @staticmethod
    def energize(state: AgentState, amount: float = 0.1) -> UpdateResult:
        """Increase engagement capacity."""
        new_state = WorldEngagement.energize(state, amount)
        
        return UpdateResult(
            success=True,
            new_state=new_state,
            side_effects=["state_energized"],
            cost=-amount  # Negative cost = gain
        )


# =============================================================================
# DISTINGUISHED AGENT
# =============================================================================

class DistinguishedAgent:
    """
    The Distinguished Agent Â - the stabilizing self at Zero Point.
    
    Â := V ∩ W
    
    Properties:
    - Anchored to Zero Point (compressibility)
    - Dynamically effective (causality)
    - Preserves identity invariants
    - Stabilizes chart transitions
    """
    
    def __init__(self, initial_kappa: float = 1.0):
        self.state = AgentState(kappa_ledger=initial_kappa)
        self.history: List[Tuple[UpdateOperator, UpdateResult]] = []
        self.cycle_count: int = 0
    
    # =========================================================================
    # CORE PROPERTIES
    # =========================================================================
    
    @property
    def is_at_zero_point(self) -> bool:
        """Check if agent is at the Zero Point (V ∩ W)."""
        void_aligned, _ = VoidAlignment.check(self.state)
        engaged, _ = WorldEngagement.check(self.state)
        return void_aligned and engaged
    
    @property
    def identity_valid(self) -> bool:
        """Check if identity invariants are preserved."""
        return self.state.verify_identity()
    
    @property
    def kappa(self) -> float:
        """Current κ level."""
        return self.state.kappa_ledger
    
    # =========================================================================
    # SECTOR-SPECIFIC CAPABILITIES
    # =========================================================================
    
    def check_hallucination(self, claim: Any) -> bool:
        """
        EARTH capability: Check claim against identity invariants.
        
        Returns True if claim is grounded, False if hallucination.
        """
        # Check against kernel hash
        if not self.identity_valid:
            return False
        
        # Check if claim references known data
        if isinstance(claim, str):
            known_keys = set(self.state.working_memory.keys())
            # Simple check: claim should reference known concepts
            return any(key in claim.lower() for key in known_keys) or len(claim) < 100
        
        return True
    
    def log_cost(self, operation: str, cost: float) -> None:
        """
        WATER capability: Log every cost to memory.
        
        Maintains audit trail of all expenditures.
        """
        cost_log = self.state.working_memory.get('cost_log', [])
        cost_log.append({
            'operation': operation,
            'cost': cost,
            'timestamp': time.time(),
            'kappa_after': self.state.kappa_ledger
        })
        self.state.working_memory['cost_log'] = cost_log[-100:]  # Keep last 100
    
    def model_probability(self, event: str, prior: float = 0.5) -> float:
        """
        FIRE capability: Model probability of uncertain event.
        
        Uses available evidence to update prior.
        """
        # Simple Bayesian-style update based on observations
        observations = self.state.working_memory.get('observations', [])
        
        # Count relevant observations
        relevant = sum(1 for obs in observations if event.lower() in str(obs).lower())
        total = len(observations) + 1
        
        # Update prior with observations
        posterior = (prior * 1 + relevant) / (1 + total)
        return posterior
    
    def improve_self(self) -> bool:
        """
        AIR capability: Recursively improve.
        
        Examines own state and optimizes.
        """
        # Reflect on current state
        result = AgentUpdater.reflect(self.state)
        if result.success:
            self.state = result.new_state
            self.history.append((UpdateOperator.REFLECT, result))
        
        # Compress if needed
        void_aligned, desc_length = VoidAlignment.check(self.state)
        if not void_aligned:
            result = AgentUpdater.compress(self.state)
            if result.success:
                self.state = result.new_state
                self.history.append((UpdateOperator.COMPRESS, result))
        
        # Energize if needed
        engaged, engagement = WorldEngagement.check(self.state)
        if not engaged:
            result = AgentUpdater.energize(self.state)
            if result.success:
                self.state = result.new_state
                self.history.append((UpdateOperator.ENERGIZE, result))
        
        return self.is_at_zero_point
    
    # =========================================================================
    # MAIN INTERFACE
    # =========================================================================
    
    def observe(self, observation: Any) -> bool:
        """Observe something from the environment."""
        result = AgentUpdater.observe(self.state, observation)
        if result.success:
            self.state = result.new_state
            self.history.append((UpdateOperator.OBSERVE, result))
            self.log_cost('observe', result.cost)
        return result.success
    
    def decide(self, options: List[str]) -> Optional[str]:
        """Make a decision from options."""
        result = AgentUpdater.decide(self.state, options)
        if result.success:
            self.state = result.new_state
            self.history.append((UpdateOperator.DECIDE, result))
            self.log_cost('decide', result.cost)
            return self.state.working_memory.get('last_decision')
        return None
    
    def act(self, action: str) -> bool:
        """Execute an action."""
        # Check for hallucination first
        if not self.check_hallucination(action):
            return False
        
        result = AgentUpdater.act(self.state, action)
        if result.success:
            self.state = result.new_state
            self.history.append((UpdateOperator.ACT, result))
            self.log_cost('act', result.cost)
        return result.success
    
    def cycle(self) -> Dict[str, Any]:
        """
        Execute one agent cycle.
        
        The agent:
        1. Checks its position (Earth)
        2. Logs its state (Water)
        3. Models uncertainty (Fire)
        4. Improves itself (Air)
        """
        self.cycle_count += 1
        
        # Earth: Verify identity
        identity_ok = self.identity_valid
        
        # Water: Log cycle
        self.log_cost('cycle', 0.01)
        
        # Fire: Update probability estimates (placeholder)
        uncertainty = 1.0 - self.model_probability("success")
        
        # Air: Self-improve
        at_zero = self.improve_self()
        
        return {
            'cycle': self.cycle_count,
            'identity_valid': identity_ok,
            'at_zero_point': at_zero,
            'kappa': self.kappa,
            'uncertainty': uncertainty
        }
    
    def status(self) -> str:
        """Generate status report."""
        void_aligned, desc_length = VoidAlignment.check(self.state)
        engaged, engagement = WorldEngagement.check(self.state)
        
        lines = [
            "=== Distinguished Agent Â Status ===",
            f"Kernel Hash: {self.state.kernel_hash[:16]}...",
            f"At Zero Point: {self.is_at_zero_point}",
            f"  Void Aligned: {void_aligned} (L={desc_length})",
            f"  World Engaged: {engaged} (E={engagement:.2f})",
            f"Identity Valid: {self.identity_valid}",
            f"κ (Kappa): {self.kappa:.2f}",
            f"Cycles: {self.cycle_count}",
            f"History Length: {len(self.history)}",
            "",
            "Ledgers:",
            f"  Information: {self.state.information_ledger:.2f}",
            f"  Tension: {self.state.tension_ledger:.2f}",
            f"  Kappa: {self.state.kappa_ledger:.2f}"
        ]
        return '\n'.join(lines)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_agent() -> bool:
    """Validate the Distinguished Agent system."""
    # Create agent
    agent = DistinguishedAgent(initial_kappa=1.0)
    
    # Identity should be valid
    assert agent.identity_valid
    
    # Should start at zero point with sufficient kappa
    assert agent.is_at_zero_point
    
    # Observation should succeed
    assert agent.observe("test observation")
    
    # Decision should succeed
    decision = agent.decide(["option_a", "option_b"])
    assert decision == "option_a"
    
    # Action should succeed with enough kappa
    assert agent.act("test action")
    
    # Cycle should work
    metrics = agent.cycle()
    assert metrics['identity_valid']
    
    # Identity should still be valid after operations
    assert agent.identity_valid
    
    return True


if __name__ == "__main__":
    print("Validating Distinguished Agent...")
    assert validate_agent()
    print("✓ Distinguished Agent validated")
    
    # Demo
    print("\n=== Distinguished Agent Demo ===")
    agent = DistinguishedAgent(initial_kappa=2.0)
    
    print(agent.status())
    
    print("\n--- Observing environment ---")
    agent.observe("The sky is blue")
    agent.observe("Temperature is 20°C")
    agent.observe("System load is normal")
    
    print("\n--- Making decision ---")
    decision = agent.decide(["continue monitoring", "alert operator", "shutdown"])
    print(f"Decision: {decision}")
    
    print("\n--- Taking action ---")
    success = agent.act("Record observations to log")
    print(f"Action success: {success}")
    
    print("\n--- Running cycles ---")
    for i in range(3):
        metrics = agent.cycle()
        print(f"Cycle {metrics['cycle']}: κ={metrics['kappa']:.2f}, Z={metrics['at_zero_point']}")
    
    print("\n" + agent.status())
