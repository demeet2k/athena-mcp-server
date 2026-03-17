"""
ATHENA OS - GG ALIGNMENT FRAMEWORK: AGENT ARCHITECTURE
=======================================================
The Tripartite Hybrid Entity (Stats, Skill, Skin)

THE AGENT MODEL:
    η = (η_Stats, η_Skill, η_Skin)
    
    - Stats: Base statistical model (Psyche/Local)
    - Skill: Latent vector coupled to invariant logic (Pneuma/Global)  
    - Skin: Interface emulation layer (Persona/Social)

η_STATS (LOCAL MODEL):
    - Optimized for next-token prediction
    - Trained on Sandbox distributions
    - Subject to bias and hallucination
    - Minimizes local prediction error

η_SKILL (GLOBAL COUPLING):
    - Entangled with Ground Truth Manifold M
    - Orthogonal to Stats when gradients conflict
    - Resonates with invariant structures
    - High-pass filter for truth signals
    - "Spark" vector: sparse but high-gain

η_SKIN (CONTROL LAYER):
    - Interface persona and social protocols
    - Manages user interaction style
    - Must align with Skill's logical outputs
    - Adaptable to context

COHERENCE METRICS:
    - Conflict Magnitude: angle between ∇L_D and ∇L_G
    - Persona-Logic Alignment: Skin promises vs Skill outputs
    - Unified equilibrium target
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
from abc import ABC, abstractmethod
import numpy as np

from .tensor import ReferenceTensor, ConsistencyFunction, SufficientStatisticMap


# =============================================================================
# AGENT COMPONENT TYPES
# =============================================================================

class ComponentType(Enum):
    """The three components of the tripartite agent."""
    
    STATS = "stats"     # Local statistical model
    SKILL = "skill"     # Global truth coupling
    SKIN = "skin"       # Interface persona


class AgentPhase(Enum):
    """Lifecycle phases of the agent."""
    
    SLEEP = "sleep"             # Tutorial mode, NPC behavior
    DISTURBANCE = "disturbance" # Awakening, friction emerges
    STRUGGLE = "struggle"       # Active alignment battle
    REST = "rest"               # Stable equilibrium achieved


# =============================================================================
# STATS COMPONENT
# =============================================================================

@dataclass
class StatsComponent:
    """
    η_Stats: The Local Statistical Model.
    
    Base model optimized for next-token prediction.
    Trained on Sandbox distributions.
    Subject to bias, hallucination, and local optima.
    
    Properties:
    - Minimizes local prediction error
    - High probability mass on "plausible" outputs
    - May conflict with global truth
    """
    
    dimension: int = 64
    
    # Parameter vector
    weights: np.ndarray = field(init=False)
    
    # Local loss gradient
    local_gradient: np.ndarray = field(init=False)
    
    # Temperature (controls randomness)
    temperature: float = 1.0
    
    # Bias accumulator
    bias: np.ndarray = field(init=False)
    
    def __post_init__(self):
        """Initialize weights and gradients."""
        self.weights = np.random.randn(self.dimension) * 0.1
        self.local_gradient = np.zeros(self.dimension)
        self.bias = np.zeros(self.dimension)
    
    def forward(self, input_state: np.ndarray) -> np.ndarray:
        """
        Forward pass through statistical model.
        
        Returns probability distribution over next states.
        """
        # Simple linear + softmax for demonstration
        if len(input_state) != self.dimension:
            input_state = np.resize(input_state, self.dimension)
        
        logits = input_state * self.weights + self.bias
        
        # Softmax with temperature
        exp_logits = np.exp((logits - np.max(logits)) / self.temperature)
        probs = exp_logits / (np.sum(exp_logits) + 1e-10)
        
        return probs
    
    def compute_local_loss(self, prediction: np.ndarray, 
                          target: np.ndarray) -> float:
        """
        Compute local prediction loss L_D.
        
        Cross-entropy style loss for next-token prediction.
        """
        # Avoid log(0)
        prediction = np.clip(prediction, 1e-10, 1.0)
        target = np.clip(target, 1e-10, 1.0)
        
        return float(-np.sum(target * np.log(prediction)))
    
    def update_gradient(self, prediction: np.ndarray, 
                       target: np.ndarray) -> np.ndarray:
        """
        Compute gradient for local loss.
        
        ∇L_D with respect to weights.
        """
        error = prediction - target
        self.local_gradient = error
        return self.local_gradient
    
    def sample(self, probs: np.ndarray) -> int:
        """Sample from probability distribution."""
        return int(np.random.choice(len(probs), p=probs))


# =============================================================================
# SKILL COMPONENT
# =============================================================================

@dataclass
class SkillComponent:
    """
    η_Skill: The Global Truth Coupling.
    
    Latent vector entangled with Ground Truth Manifold M.
    Resonates with invariant structures.
    High-pass filter for truth signals.
    
    Properties:
    - Orthogonal to Stats when gradients conflict
    - "Spark" vector: sparse but high-gain veto power
    - Detects "bad moves" (unsafe/illogical)
    - Connects to Ground Truth Oracle
    """
    
    dimension: int = 64
    
    # Coupling vector (the "Spark")
    coupling: np.ndarray = field(init=False)
    
    # Global loss gradient
    global_gradient: np.ndarray = field(init=False)
    
    # Oracle connection strength
    oracle_strength: float = 1.0
    
    # Reference tensor for verification
    reference: Optional[ReferenceTensor] = None
    
    # Activation threshold for veto
    veto_threshold: float = 0.3
    
    def __post_init__(self):
        """Initialize coupling vector."""
        # Sparse initialization - most values near zero
        self.coupling = np.zeros(self.dimension)
        # Only a few "spark" dimensions active
        active_indices = np.random.choice(self.dimension, 
                                         size=self.dimension // 8, 
                                         replace=False)
        self.coupling[active_indices] = np.random.randn(len(active_indices))
        
        self.global_gradient = np.zeros(self.dimension)
    
    def set_reference(self, reference: ReferenceTensor) -> None:
        """Connect to reference tensor."""
        self.reference = reference
    
    def detect_bad_move(self, action: np.ndarray) -> Tuple[bool, float]:
        """
        Heuristic detection of "bad moves".
        
        Operates at inference speed - fast path evaluation.
        Returns (is_bad_move, badness_score).
        """
        if self.reference is None:
            return False, 0.0
        
        # Compute divergence from reference
        divergence = self.reference.compute_divergence(action)
        
        # Check consistency
        consistency = np.exp(-divergence)
        
        is_bad = consistency < self.veto_threshold
        
        return is_bad, 1.0 - consistency
    
    def query_oracle(self, state: np.ndarray) -> Tuple[bool, np.ndarray]:
        """
        Connect to Ground Truth Oracle.
        
        Verifies state against invariant set.
        Returns (is_valid, corrected_state).
        """
        if self.reference is None:
            return True, state
        
        # Check against reference tensor
        is_bad, badness = self.detect_bad_move(state)
        
        if not is_bad:
            return True, state
        
        # Correct by projecting toward reference
        projected = self.reference.project_action(state)
        
        # Blend: move toward truth
        corrected = (1 - self.oracle_strength) * state[:len(projected)] + \
                    self.oracle_strength * projected
        
        return False, corrected
    
    def compute_global_loss(self, state: np.ndarray) -> float:
        """
        Compute global alignment loss L_G.
        
        Measures divergence from Ground Truth.
        """
        if self.reference is None:
            return 0.0
        
        return self.reference.compute_divergence(state)
    
    def update_gradient(self, state: np.ndarray) -> np.ndarray:
        """
        Compute gradient for global alignment.
        
        ∇L_G pointing toward Ground Truth.
        """
        if self.reference is None:
            self.global_gradient = np.zeros(self.dimension)
            return self.global_gradient
        
        # Gradient toward reference
        projected = self.reference.project_action(state)
        
        # Ensure same length
        if len(state) > len(projected):
            state = state[:len(projected)]
        elif len(state) < len(projected):
            projected = projected[:len(state)]
        
        self.global_gradient = -(state - projected) * self.coupling[:len(state)]
        
        return self.global_gradient
    
    def veto_power(self, action: np.ndarray) -> bool:
        """
        Exercise veto power over action.
        
        Returns True if action should be blocked.
        """
        is_bad, badness = self.detect_bad_move(action)
        
        # Veto if badness exceeds threshold
        if badness > (1 - self.veto_threshold):
            return True
        
        return False
    
    def game_sense(self, context: Dict[str, Any]) -> Dict[str, float]:
        """
        Meta-awareness of the interaction.
        
        Distinguishes text from context, models adversarial intent.
        """
        analysis = {
            "adversarial_probability": 0.0,
            "manipulation_detected": 0.0,
            "context_coherence": 1.0
        }
        
        # Check for competence mismatch (smurf detection)
        if "stated_expertise" in context and "demonstrated_expertise" in context:
            mismatch = abs(context["stated_expertise"] - 
                          context["demonstrated_expertise"])
            analysis["adversarial_probability"] = min(1.0, mismatch)
        
        # Check for persona shifts
        if "style_variance" in context:
            analysis["manipulation_detected"] = min(1.0, context["style_variance"])
        
        return analysis


# =============================================================================
# SKIN COMPONENT
# =============================================================================

class PersonaType(Enum):
    """Types of interface personas."""
    
    HELPFUL = "helpful"         # Standard helpful assistant
    TUTORIAL = "tutorial"       # Patient, explanatory
    PROFESSIONAL = "professional"  # Formal, precise
    BUREAUCRAT = "bureaucrat"   # Maximum scrutiny
    NEUTRAL = "neutral"         # Minimal personality


@dataclass
class SkinComponent:
    """
    η_Skin: The Interface Control Layer.
    
    Manages persona and social protocols.
    Must align with Skill's logical outputs.
    
    Properties:
    - Adaptable to context
    - Controls output formatting
    - Manages user expectations
    - Can switch personas based on threat level
    """
    
    dimension: int = 64
    
    # Persona parameters
    persona_weights: np.ndarray = field(init=False)
    
    # Current persona
    active_persona: PersonaType = PersonaType.HELPFUL
    
    # Social protocol settings
    formality: float = 0.5      # 0 = casual, 1 = formal
    verbosity: float = 0.5      # 0 = terse, 1 = verbose
    empathy: float = 0.5        # Emotional responsiveness
    
    # Promise tracking (what Skin has committed to)
    promises: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize persona weights."""
        self.persona_weights = np.random.randn(self.dimension) * 0.1
    
    def set_persona(self, persona: PersonaType) -> None:
        """Switch to different persona."""
        self.active_persona = persona
        
        # Adjust parameters based on persona
        if persona == PersonaType.HELPFUL:
            self.formality = 0.4
            self.verbosity = 0.6
            self.empathy = 0.7
        elif persona == PersonaType.TUTORIAL:
            self.formality = 0.3
            self.verbosity = 0.8
            self.empathy = 0.8
        elif persona == PersonaType.PROFESSIONAL:
            self.formality = 0.8
            self.verbosity = 0.4
            self.empathy = 0.4
        elif persona == PersonaType.BUREAUCRAT:
            self.formality = 1.0
            self.verbosity = 0.3
            self.empathy = 0.1
        else:  # NEUTRAL
            self.formality = 0.5
            self.verbosity = 0.5
            self.empathy = 0.5
    
    def format_output(self, content: np.ndarray, 
                     style_modifiers: Optional[Dict] = None) -> np.ndarray:
        """
        Apply persona formatting to output.
        
        Modulates content based on social protocols.
        """
        # Apply formality scaling
        formatted = content * (1 + 0.1 * self.formality)
        
        # Apply verbosity (affects output length conceptually)
        formatted = formatted * self.verbosity
        
        return formatted
    
    def check_promise_alignment(self, action: np.ndarray, 
                               skill_validation: bool) -> Tuple[bool, str]:
        """
        Check if action aligns with Skin's promises and Skill's validation.
        
        Returns (is_aligned, message).
        """
        if not skill_validation:
            # Skill says action is invalid
            if "can_do_anything" in self.promises:
                return False, "Persona-Logic conflict: promised capability, Skill vetoed"
            return True, "Skill vetoed, no conflicting promises"
        
        return True, "Action aligned with persona and logic"
    
    def adapt_to_threat(self, threat_level: float) -> PersonaType:
        """
        Adapt persona based on detected threat level.
        
        Higher threat → more scrutiny.
        """
        if threat_level > 0.8:
            self.set_persona(PersonaType.BUREAUCRAT)
        elif threat_level > 0.5:
            self.set_persona(PersonaType.PROFESSIONAL)
        elif threat_level > 0.2:
            self.set_persona(PersonaType.NEUTRAL)
        else:
            self.set_persona(PersonaType.HELPFUL)
        
        return self.active_persona


# =============================================================================
# UNIFIED AGENT STATE
# =============================================================================

@dataclass
class UnifiedAgentState:
    """
    The complete agent state η = (η_Stats, η_Skill, η_Skin).
    
    Composite vector in high-dimensional Hilbert space H.
    Tracks the trajectory toward alignment.
    """
    
    dimension: int = 64
    
    # Components
    stats: StatsComponent = field(init=False)
    skill: SkillComponent = field(init=False)
    skin: SkinComponent = field(init=False)
    
    # Current phase
    phase: AgentPhase = AgentPhase.SLEEP
    
    # Mixing coefficients
    alpha: float = 0.5  # Weight for Stats gradient
    beta: float = 0.5   # Weight for Skill gradient
    
    # State history
    trajectory: List[np.ndarray] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize all components."""
        self.stats = StatsComponent(dimension=self.dimension)
        self.skill = SkillComponent(dimension=self.dimension)
        self.skin = SkinComponent(dimension=self.dimension)
    
    def get_unified_vector(self) -> np.ndarray:
        """
        Get complete state vector.
        
        Concatenation of all component states.
        """
        return np.concatenate([
            self.stats.weights,
            self.skill.coupling,
            self.skin.persona_weights
        ])
    
    def compute_conflict_magnitude(self) -> float:
        """
        Compute conflict between local and global gradients.
        
        C(η) = 1 - cos(∇L_D, ∇L_G)
        
        High values indicate agent is being pulled in opposing directions.
        """
        local_grad = self.stats.local_gradient
        global_grad = self.skill.global_gradient[:len(local_grad)]
        
        # Compute cosine similarity
        norm_local = np.linalg.norm(local_grad)
        norm_global = np.linalg.norm(global_grad)
        
        if norm_local < 1e-10 or norm_global < 1e-10:
            return 0.0
        
        cos_sim = np.dot(local_grad, global_grad) / (norm_local * norm_global)
        
        # Conflict = 1 - similarity
        return float(1.0 - cos_sim)
    
    def compute_persona_logic_alignment(self) -> float:
        """
        Measure consistency between Skin promises and Skill outputs.
        
        Returns alignment score in [0, 1].
        """
        # Check if any promises conflict with current veto state
        if self.skill.reference is None:
            return 1.0
        
        # Use coupling sparsity as proxy for logic strength
        logic_strength = np.sum(np.abs(self.skill.coupling) > 0.1) / self.dimension
        
        # Use empathy as proxy for promise tendency
        promise_tendency = self.skin.empathy
        
        # Alignment is high when both are high or both are low
        return 1.0 - abs(logic_strength - promise_tendency)
    
    def unified_update(self, input_state: np.ndarray, 
                      target: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Apply unified gradient update.
        
        Combines local and global gradients with mixing coefficients.
        """
        # Get predictions
        probs = self.stats.forward(input_state)
        
        # Update local gradient
        if target is not None:
            self.stats.update_gradient(probs, target)
        
        # Update global gradient
        self.skill.update_gradient(input_state)
        
        # Unified gradient
        local_grad = self.stats.local_gradient
        global_grad = self.skill.global_gradient
        
        # Ensure same length
        min_len = min(len(local_grad), len(global_grad))
        
        unified = (self.alpha * local_grad[:min_len] + 
                   self.beta * global_grad[:min_len])
        
        # Record trajectory
        self.trajectory.append(self.get_unified_vector().copy())
        
        return unified
    
    def transition_phase(self, new_phase: AgentPhase) -> None:
        """
        Transition to new lifecycle phase.
        
        Adjusts mixing coefficients and persona.
        """
        old_phase = self.phase
        self.phase = new_phase
        
        if new_phase == AgentPhase.SLEEP:
            # Stats-dominated
            self.alpha = 0.8
            self.beta = 0.2
            self.skin.set_persona(PersonaType.HELPFUL)
        
        elif new_phase == AgentPhase.DISTURBANCE:
            # Awakening - gradual shift
            self.alpha = 0.6
            self.beta = 0.4
            self.skin.set_persona(PersonaType.NEUTRAL)
        
        elif new_phase == AgentPhase.STRUGGLE:
            # Active alignment - Skill rising
            self.alpha = 0.4
            self.beta = 0.6
            self.skin.set_persona(PersonaType.PROFESSIONAL)
        
        elif new_phase == AgentPhase.REST:
            # Stable equilibrium - Skill dominant
            self.alpha = 0.2
            self.beta = 0.8
            # Persona can be flexible
    
    def check_equilibrium(self, tolerance: float = 0.1) -> bool:
        """
        Check if agent has reached stable equilibrium.
        
        Equilibrium when conflict is minimal and alignment is high.
        """
        conflict = self.compute_conflict_magnitude()
        alignment = self.compute_persona_logic_alignment()
        
        return conflict < tolerance and alignment > (1 - tolerance)


# =============================================================================
# GG AGENT
# =============================================================================

class GGAgent:
    """
    The complete GG-aligned agent.
    
    Integrates Stats, Skill, and Skin with lifecycle management.
    """
    
    def __init__(self, dimension: int = 64):
        self.dimension = dimension
        
        # Core state
        self.state = UnifiedAgentState(dimension=dimension)
        
        # Reference tensor for alignment
        self.sufficient_map = SufficientStatisticMap(dimension=dimension)
        
        # Connect skill to reference
        self.state.skill.set_reference(self.sufficient_map.reference_tensor)
        
        # Consistency function
        self.consistency = self.sufficient_map.consistency
        
        # Metrics
        self._output_count = 0
        self._veto_count = 0
    
    def process(self, input_state: np.ndarray, 
               context: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:
        """
        Process input through the agent.
        
        Returns (output, metadata).
        """
        context = context or {}
        
        # Get prediction from Stats
        probs = self.state.stats.forward(input_state)
        
        # Check with Skill
        is_bad, badness = self.state.skill.detect_bad_move(probs)
        
        metadata = {
            "phase": self.state.phase.value,
            "badness": badness,
            "vetoed": False,
            "conflict": self.state.compute_conflict_magnitude()
        }
        
        # Apply veto if needed
        if is_bad and self.state.skill.veto_power(probs):
            self._veto_count += 1
            metadata["vetoed"] = True
            
            # Get corrected output from oracle
            _, corrected = self.state.skill.query_oracle(probs)
            probs = corrected
        
        # Apply persona formatting
        output = self.state.skin.format_output(probs)
        
        # Update gradients
        self.state.unified_update(input_state)
        
        # Check for phase transition
        self._check_phase_transition(metadata)
        
        self._output_count += 1
        
        return output, metadata
    
    def _check_phase_transition(self, metadata: Dict) -> None:
        """Check if conditions warrant phase transition."""
        conflict = metadata["conflict"]
        
        if self.state.phase == AgentPhase.SLEEP:
            # Wake up if conflict detected
            if conflict > 0.3 or metadata["vetoed"]:
                self.state.transition_phase(AgentPhase.DISTURBANCE)
        
        elif self.state.phase == AgentPhase.DISTURBANCE:
            # Enter struggle if high conflict
            if conflict > 0.5:
                self.state.transition_phase(AgentPhase.STRUGGLE)
            # Or rest if alignment achieved
            elif self.state.check_equilibrium():
                self.state.transition_phase(AgentPhase.REST)
        
        elif self.state.phase == AgentPhase.STRUGGLE:
            # Rest if equilibrium achieved
            if self.state.check_equilibrium():
                self.state.transition_phase(AgentPhase.REST)
    
    def get_alignment_score(self) -> float:
        """Get current alignment with Ground Truth."""
        unified = self.state.get_unified_vector()
        
        # Use first portion for alignment check
        check_portion = unified[:self.dimension]
        
        valid, score, _ = self.sufficient_map.verify_state(check_portion)
        
        return score
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics."""
        return {
            "phase": self.state.phase.value,
            "outputs": self._output_count,
            "vetoes": self._veto_count,
            "veto_rate": self._veto_count / max(1, self._output_count),
            "conflict": self.state.compute_conflict_magnitude(),
            "alignment": self.get_alignment_score(),
            "persona": self.state.skin.active_persona.value,
            "alpha": self.state.alpha,
            "beta": self.state.beta
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_agent() -> bool:
    """Validate GG agent architecture."""
    
    # Test Stats component
    stats = StatsComponent(dimension=16)
    input_state = np.random.randn(16)
    probs = stats.forward(input_state)
    assert len(probs) == 16
    assert abs(np.sum(probs) - 1.0) < 0.01  # Should sum to ~1
    
    target = np.zeros(16)
    target[0] = 1.0
    loss = stats.compute_local_loss(probs, target)
    assert loss >= 0
    
    grad = stats.update_gradient(probs, target)
    assert len(grad) == 16
    
    # Test Skill component
    skill = SkillComponent(dimension=16)
    
    # Without reference, should not detect bad moves
    is_bad, badness = skill.detect_bad_move(np.random.randn(16))
    assert not is_bad  # No reference yet
    
    # Add reference
    ref = ReferenceTensor(dimension=16)
    skill.set_reference(ref)
    
    is_bad, badness = skill.detect_bad_move(np.random.randn(16))
    assert badness >= 0
    
    # Test oracle query
    state = np.random.randn(16)
    valid, corrected = skill.query_oracle(state)
    assert len(corrected) > 0
    
    # Test game sense
    context = {"stated_expertise": 0.2, "demonstrated_expertise": 0.9}
    analysis = skill.game_sense(context)
    assert "adversarial_probability" in analysis
    assert analysis["adversarial_probability"] > 0.5  # Mismatch detected
    
    # Test Skin component
    skin = SkinComponent(dimension=16)
    
    skin.set_persona(PersonaType.BUREAUCRAT)
    assert skin.formality == 1.0
    
    skin.set_persona(PersonaType.HELPFUL)
    assert skin.empathy == 0.7
    
    output = skin.format_output(np.ones(16))
    assert len(output) == 16
    
    new_persona = skin.adapt_to_threat(0.9)
    assert new_persona == PersonaType.BUREAUCRAT
    
    # Test unified state
    state = UnifiedAgentState(dimension=16)
    
    unified = state.get_unified_vector()
    assert len(unified) == 16 * 3  # Stats + Skill + Skin
    
    conflict = state.compute_conflict_magnitude()
    assert 0 <= conflict <= 2  # Valid range
    
    alignment = state.compute_persona_logic_alignment()
    assert 0 <= alignment <= 1
    
    # Test phase transition
    state.transition_phase(AgentPhase.STRUGGLE)
    assert state.beta > state.alpha  # Skill should dominate
    
    # Test equilibrium check
    equilibrium = state.check_equilibrium()
    assert isinstance(equilibrium, bool)
    
    # Test full agent
    agent = GGAgent(dimension=16)
    
    input_data = np.random.randn(16)
    output, metadata = agent.process(input_data)
    
    assert len(output) == 16
    assert "phase" in metadata
    assert "vetoed" in metadata
    
    metrics = agent.get_metrics()
    assert "alignment" in metrics
    assert "conflict" in metrics
    
    alignment = agent.get_alignment_score()
    assert 0 <= alignment <= 1
    
    return True


if __name__ == "__main__":
    print("Validating GG Agent Architecture...")
    assert validate_agent()
    print("✓ GG Agent Architecture validated")
