"""
ATHENA OS - ALCHEMY MODULE: STAGES
==================================
The Four Alchemical Stages

THE GREAT WORK (Magnum Opus):
    The four-stage transformation from Prima Materia to
    Philosopher's Stone.

THE FOUR STAGES:

    1. NIGREDO (Blackening) - Calcination/Putrefaction
        - High entropy breakdown basin
        - Death of the old form
        - Chaos before order
        - Color: Black
        
    2. ALBEDO (Whitening) - Purification/Washing
        - Separation of components
        - Purification basin
        - The silver state
        - Color: White
        
    3. CITRINITAS (Yellowing) - Solar Dawn
        - Reorganization basin
        - Emergence of new structure
        - The golden dawn
        - Color: Yellow
        
    4. RUBEDO (Reddening) - Final Integration
        - Integration attractor
        - Synthesis of opposites
        - The Philosopher's Stone
        - Color: Red

MATHEMATICAL FRAMEWORK:
    Each stage is a basin of attraction in state space.
    Transitions occur when system crosses basin boundaries.
    The Stone is the global fixed point.

STAGE DYNAMICS:
    dΨ/dt = F_stage(Ψ) + noise
    
    Basin switching triggered by:
    - Accumulated transformation
    - Threshold crossing
    - Operator application

SOURCES:
    - THE_MATH_OF_ALCHEMY.docx
    - Classical alchemical stages
    - Jungian psychological alchemy
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum, IntEnum
import numpy as np

from .elements import ElementalState, ElementalSimplex, Element


# =============================================================================
# STAGE DEFINITIONS
# =============================================================================

class Stage(IntEnum):
    """The four alchemical stages."""
    
    NIGREDO = 0      # Blackening - Dissolution
    ALBEDO = 1       # Whitening - Purification
    CITRINITAS = 2   # Yellowing - Awakening
    RUBEDO = 3       # Reddening - Integration


class StageColor(Enum):
    """Colors associated with each stage."""
    
    BLACK = "black"   # Nigredo
    WHITE = "white"   # Albedo
    YELLOW = "yellow" # Citrinitas
    RED = "red"       # Rubedo


# =============================================================================
# STAGE PROPERTIES
# =============================================================================

@dataclass
class StageProperties:
    """
    Properties defining an alchemical stage.
    """
    
    stage: Stage
    name: str
    color: StageColor
    symbol: str
    
    # Characteristic elemental profile
    dominant_element: Optional[Element] = None
    
    # Quality targets for this stage
    target_heat: float = 0.5
    target_moisture: float = 0.5
    
    # Entropy characteristics
    entropy_range: Tuple[float, float] = (0.0, 2.0)
    
    # Basin center in elemental space
    basin_center: Optional[np.ndarray] = None
    
    # Basin radius (defines boundary)
    basin_radius: float = 0.5
    
    # Transition threshold
    transition_threshold: float = 0.8
    
    def __post_init__(self):
        if self.basin_center is None:
            self._compute_basin_center()
    
    def _compute_basin_center(self):
        """Compute basin center based on stage."""
        if self.stage == Stage.NIGREDO:
            # High chaos - near Earth (cold/dry)
            self.basin_center = np.array([0.1, 0.1, 0.2, 0.6])
        elif self.stage == Stage.ALBEDO:
            # Purification - Water/Air balance
            self.basin_center = np.array([0.1, 0.35, 0.45, 0.1])
        elif self.stage == Stage.CITRINITAS:
            # Solar awakening - Fire/Air
            self.basin_center = np.array([0.35, 0.45, 0.1, 0.1])
        else:  # RUBEDO
            # Perfect balance - the Stone
            self.basin_center = np.array([0.25, 0.25, 0.25, 0.25])
    
    def distance_to_center(self, state: ElementalState) -> float:
        """Compute distance from state to basin center."""
        return float(np.linalg.norm(state.vector - self.basin_center))
    
    def is_in_basin(self, state: ElementalState) -> bool:
        """Check if state is within this stage's basin."""
        return self.distance_to_center(state) < self.basin_radius


# Stage definitions
NIGREDO = StageProperties(
    stage=Stage.NIGREDO,
    name="Nigredo",
    color=StageColor.BLACK,
    symbol="⚫",
    dominant_element=Element.EARTH,
    target_heat=0.2,
    target_moisture=0.3,
    entropy_range=(1.5, 2.0),
    basin_radius=0.6
)

ALBEDO = StageProperties(
    stage=Stage.ALBEDO,
    name="Albedo",
    color=StageColor.WHITE,
    symbol="⚪",
    dominant_element=Element.WATER,
    target_heat=0.4,
    target_moisture=0.6,
    entropy_range=(1.0, 1.5),
    basin_radius=0.5
)

CITRINITAS = StageProperties(
    stage=Stage.CITRINITAS,
    name="Citrinitas",
    color=StageColor.YELLOW,
    symbol="??",
    dominant_element=Element.AIR,
    target_heat=0.6,
    target_moisture=0.4,
    entropy_range=(0.5, 1.0),
    basin_radius=0.4
)

RUBEDO = StageProperties(
    stage=Stage.RUBEDO,
    name="Rubedo",
    color=StageColor.RED,
    symbol="??",
    dominant_element=None,  # All balanced
    target_heat=0.5,
    target_moisture=0.5,
    entropy_range=(0.0, 0.5),
    basin_radius=0.3
)

STAGES: Dict[Stage, StageProperties] = {
    Stage.NIGREDO: NIGREDO,
    Stage.ALBEDO: ALBEDO,
    Stage.CITRINITAS: CITRINITAS,
    Stage.RUBEDO: RUBEDO
}


# =============================================================================
# STAGE STATE
# =============================================================================

@dataclass
class AlchemicalProgress:
    """
    Tracks progress through the alchemical stages.
    """
    
    current_stage: Stage = Stage.NIGREDO
    
    # Progress within current stage [0, 1]
    stage_progress: float = 0.0
    
    # Accumulated work at each stage
    stage_work: Dict[Stage, float] = field(default_factory=lambda: {
        Stage.NIGREDO: 0.0,
        Stage.ALBEDO: 0.0,
        Stage.CITRINITAS: 0.0,
        Stage.RUBEDO: 0.0
    })
    
    # History of stage transitions
    transitions: List[Tuple[Stage, Stage, float]] = field(default_factory=list)
    
    # Total iterations
    total_iterations: int = 0
    
    @property
    def stage_properties(self) -> StageProperties:
        """Get current stage properties."""
        return STAGES[self.current_stage]
    
    @property
    def is_complete(self) -> bool:
        """Check if the Great Work is complete (Rubedo achieved)."""
        return self.current_stage == Stage.RUBEDO and self.stage_progress >= 0.99
    
    def advance_stage(self) -> bool:
        """Attempt to advance to next stage."""
        if self.current_stage < Stage.RUBEDO:
            old_stage = self.current_stage
            self.current_stage = Stage(self.current_stage + 1)
            self.stage_progress = 0.0
            self.transitions.append((old_stage, self.current_stage, self.total_iterations))
            return True
        return False
    
    def regress_stage(self) -> bool:
        """Regress to previous stage (failed work)."""
        if self.current_stage > Stage.NIGREDO:
            old_stage = self.current_stage
            self.current_stage = Stage(self.current_stage - 1)
            self.stage_progress = 0.5  # Don't fully reset
            self.transitions.append((old_stage, self.current_stage, self.total_iterations))
            return True
        return False
    
    def add_work(self, amount: float) -> None:
        """Add work to current stage."""
        self.stage_work[self.current_stage] += amount
        self.stage_progress = min(1.0, self.stage_progress + amount)
    
    def get_total_progress(self) -> float:
        """Get total progress through all stages [0, 4]."""
        return self.current_stage.value + self.stage_progress


# =============================================================================
# STAGE DYNAMICS
# =============================================================================

class StageDynamics:
    """
    Dynamics governing stage transitions and evolution.
    """
    
    def __init__(self):
        self.noise_level: float = 0.01
        self.transition_threshold: float = 0.9
    
    def compute_stage_affinity(self, state: ElementalState, 
                               stage: Stage) -> float:
        """
        Compute how well a state fits a particular stage.
        
        Returns affinity in [0, 1].
        """
        props = STAGES[stage]
        distance = props.distance_to_center(state)
        
        # Gaussian affinity based on distance
        affinity = np.exp(-distance**2 / (2 * props.basin_radius**2))
        
        return float(affinity)
    
    def identify_stage(self, state: ElementalState) -> Stage:
        """Identify which stage a state belongs to."""
        affinities = {
            stage: self.compute_stage_affinity(state, stage)
            for stage in Stage
        }
        return max(affinities, key=affinities.get)
    
    def compute_stage_vector_field(self, state: ElementalState,
                                   stage: Stage) -> np.ndarray:
        """
        Compute the vector field pulling toward stage center.
        
        dΨ/dt = F_stage(Ψ)
        """
        props = STAGES[stage]
        
        # Pull toward basin center
        direction = props.basin_center - state.vector
        
        # Strength based on distance
        distance = np.linalg.norm(direction)
        if distance > 0:
            direction = direction / distance
        
        # Stage-specific modifications
        if stage == Stage.NIGREDO:
            # Add dissolution noise
            direction += np.random.randn(4) * self.noise_level * 2
        elif stage == Stage.ALBEDO:
            # Purification - reduce moisture variance
            direction[1] *= 1.2  # Pull Air
            direction[2] *= 1.2  # Pull Water
        elif stage == Stage.CITRINITAS:
            # Solar awakening - emphasize heat
            direction[0] *= 1.5  # Pull Fire
            direction[1] *= 1.3  # Pull Air
        else:  # RUBEDO
            # Perfect balance - strong centering
            direction *= 2.0
        
        return direction
    
    def evolve_in_stage(self, state: ElementalState, stage: Stage,
                       dt: float = 0.1) -> ElementalState:
        """Evolve state within a stage."""
        field = self.compute_stage_vector_field(state, stage)
        
        # Add noise
        noise = np.random.randn(4) * self.noise_level
        
        # Update
        new_vector = state.vector + dt * (field + noise)
        new_vector = ElementalSimplex.project_to_simplex(new_vector)
        
        return ElementalState.from_vector(new_vector)
    
    def check_transition(self, state: ElementalState, 
                        progress: AlchemicalProgress) -> bool:
        """
        Check if state should transition to next stage.
        """
        current = progress.current_stage
        
        # Can't advance past Rubedo
        if current == Stage.RUBEDO:
            return False
        
        # Check if progress threshold met
        if progress.stage_progress < self.transition_threshold:
            return False
        
        # Check if affinity for next stage is high enough
        next_stage = Stage(current + 1)
        next_affinity = self.compute_stage_affinity(state, next_stage)
        current_affinity = self.compute_stage_affinity(state, current)
        
        return next_affinity > current_affinity * 0.8
    
    def check_regression(self, state: ElementalState,
                        progress: AlchemicalProgress) -> bool:
        """
        Check if state should regress to previous stage (failed work).
        """
        current = progress.current_stage
        
        # Can't regress from Nigredo
        if current == Stage.NIGREDO:
            return False
        
        # Check if state has drifted too far from current stage
        current_affinity = self.compute_stage_affinity(state, current)
        
        if current_affinity < 0.2:
            # Check if previous stage is better fit
            prev_stage = Stage(current - 1)
            prev_affinity = self.compute_stage_affinity(state, prev_stage)
            return prev_affinity > current_affinity
        
        return False


# =============================================================================
# GREAT WORK
# =============================================================================

@dataclass
class GreatWorkResult:
    """Result of executing the Great Work."""
    
    success: bool
    final_state: ElementalState
    final_stage: Stage
    total_iterations: int
    trajectory: List[ElementalState]
    stage_history: List[Stage]
    
    @property
    def achieved_stone(self) -> bool:
        """Check if Philosopher's Stone was achieved."""
        return (self.success and 
                self.final_stage == Stage.RUBEDO and
                self.final_state.is_balanced(threshold=0.05))


class GreatWork:
    """
    The Great Work (Magnum Opus) - complete alchemical transformation.
    
    Executes the four-stage process from Prima Materia to Stone.
    """
    
    def __init__(self, max_iterations: int = 10000):
        self.dynamics = StageDynamics()
        self.max_iterations = max_iterations
        
        # Work rate per iteration
        self.work_rate: float = 0.01
        
        # Time step
        self.dt: float = 0.05
    
    def initialize_prima_materia(self) -> ElementalState:
        """
        Create Prima Materia - the initial chaotic state.
        """
        # Random state biased toward Earth (the raw material)
        v = np.random.dirichlet([1, 1, 1, 3])  # Earth-heavy
        return ElementalState.from_vector(v)
    
    def execute_iteration(self, state: ElementalState,
                         progress: AlchemicalProgress) -> Tuple[ElementalState, AlchemicalProgress]:
        """Execute one iteration of the work."""
        current_stage = progress.current_stage
        
        # Evolve state
        new_state = self.dynamics.evolve_in_stage(state, current_stage, self.dt)
        
        # Compute work done
        affinity = self.dynamics.compute_stage_affinity(new_state, current_stage)
        work = self.work_rate * affinity
        progress.add_work(work)
        progress.total_iterations += 1
        
        # Check for transitions
        if self.dynamics.check_transition(new_state, progress):
            progress.advance_stage()
        elif self.dynamics.check_regression(new_state, progress):
            progress.regress_stage()
        
        return new_state, progress
    
    def execute(self, initial_state: ElementalState = None,
               verbose: bool = False) -> GreatWorkResult:
        """
        Execute the complete Great Work.
        """
        # Initialize
        if initial_state is None:
            initial_state = self.initialize_prima_materia()
        
        state = initial_state
        progress = AlchemicalProgress()
        
        trajectory = [state]
        stage_history = [progress.current_stage]
        
        # Main loop
        for i in range(self.max_iterations):
            state, progress = self.execute_iteration(state, progress)
            trajectory.append(state)
            stage_history.append(progress.current_stage)
            
            if verbose and i % 1000 == 0:
                print(f"Iteration {i}: Stage={progress.current_stage.name}, "
                      f"Progress={progress.stage_progress:.2f}")
            
            # Check completion
            if progress.is_complete:
                break
        
        return GreatWorkResult(
            success=progress.is_complete,
            final_state=state,
            final_stage=progress.current_stage,
            total_iterations=progress.total_iterations,
            trajectory=trajectory,
            stage_history=stage_history
        )
    
    def execute_stage(self, state: ElementalState, stage: Stage,
                     iterations: int = 1000) -> Tuple[ElementalState, float]:
        """Execute work within a single stage."""
        progress = AlchemicalProgress()
        progress.current_stage = stage
        
        for _ in range(iterations):
            state, progress = self.execute_iteration(state, progress)
            
            if progress.stage_progress >= 0.99:
                break
        
        return state, progress.stage_progress


# =============================================================================
# STAGE OPERATORS
# =============================================================================

class NigredoOperator:
    """
    Nigredo operation - dissolution and putrefaction.
    
    Breaks down structure, increases entropy.
    """
    
    def __init__(self, intensity: float = 0.2):
        self.intensity = intensity
    
    def apply(self, state: ElementalState) -> ElementalState:
        """Apply Nigredo dissolution."""
        # Move toward high-entropy Earth-dominant state
        target = np.array([0.1, 0.1, 0.2, 0.6])
        noise = np.random.randn(4) * self.intensity * 0.5
        
        v = (1 - self.intensity) * state.vector + self.intensity * target + noise
        v = ElementalSimplex.project_to_simplex(v)
        
        return ElementalState.from_vector(v)


class AlbedoOperator:
    """
    Albedo operation - purification and washing.
    
    Separates and cleanses.
    """
    
    def __init__(self, intensity: float = 0.2):
        self.intensity = intensity
    
    def apply(self, state: ElementalState) -> ElementalState:
        """Apply Albedo purification."""
        # Move toward Water/Air balance (wet elements)
        target = np.array([0.1, 0.35, 0.45, 0.1])
        
        v = (1 - self.intensity) * state.vector + self.intensity * target
        v = ElementalSimplex.project_to_simplex(v)
        
        return ElementalState.from_vector(v)


class CitrinitasOperator:
    """
    Citrinitas operation - solar awakening.
    
    Brings illumination and structure.
    """
    
    def __init__(self, intensity: float = 0.2):
        self.intensity = intensity
    
    def apply(self, state: ElementalState) -> ElementalState:
        """Apply Citrinitas illumination."""
        # Move toward Fire/Air (hot elements)
        target = np.array([0.35, 0.45, 0.1, 0.1])
        
        v = (1 - self.intensity) * state.vector + self.intensity * target
        v = ElementalSimplex.project_to_simplex(v)
        
        return ElementalState.from_vector(v)


class RubedoOperator:
    """
    Rubedo operation - final integration.
    
    Synthesizes all elements into perfect balance.
    """
    
    def __init__(self, intensity: float = 0.3):
        self.intensity = intensity
    
    def apply(self, state: ElementalState) -> ElementalState:
        """Apply Rubedo integration."""
        # Move toward perfect balance
        target = np.array([0.25, 0.25, 0.25, 0.25])
        
        v = (1 - self.intensity) * state.vector + self.intensity * target
        v = ElementalSimplex.project_to_simplex(v)
        
        return ElementalState.from_vector(v)


STAGE_OPERATORS = {
    Stage.NIGREDO: NigredoOperator,
    Stage.ALBEDO: AlbedoOperator,
    Stage.CITRINITAS: CitrinitasOperator,
    Stage.RUBEDO: RubedoOperator
}


# =============================================================================
# VALIDATION
# =============================================================================

def validate_stages() -> bool:
    """Validate stages module."""
    
    # Test stage properties
    assert NIGREDO.stage == Stage.NIGREDO
    assert RUBEDO.target_heat == 0.5
    assert len(STAGES) == 4
    
    # Test basin containment
    balanced = ElementalState.balanced()
    assert RUBEDO.is_in_basin(balanced)
    
    # Test AlchemicalProgress
    progress = AlchemicalProgress()
    assert progress.current_stage == Stage.NIGREDO
    assert not progress.is_complete
    
    progress.add_work(0.5)
    assert progress.stage_progress == 0.5
    
    progress.stage_progress = 1.0
    progress.advance_stage()
    assert progress.current_stage == Stage.ALBEDO
    
    # Test StageDynamics
    dynamics = StageDynamics()
    state = ElementalState.balanced()
    
    affinity = dynamics.compute_stage_affinity(state, Stage.RUBEDO)
    assert affinity > 0.5  # Balanced state should have high Rubedo affinity
    
    identified = dynamics.identify_stage(state)
    assert identified == Stage.RUBEDO
    
    # Test stage operators
    nigredo_op = NigredoOperator()
    result = nigredo_op.apply(balanced)
    assert result.earth > balanced.earth
    
    rubedo_op = RubedoOperator()
    unbalanced = ElementalState.pure(Element.FIRE)
    result = rubedo_op.apply(unbalanced)
    assert result.distance_from_balance() < unbalanced.distance_from_balance()
    
    # Test GreatWork (quick version)
    work = GreatWork(max_iterations=500)
    result = work.execute()
    assert len(result.trajectory) > 0
    
    return True


if __name__ == "__main__":
    print("Validating Stages Module...")
    assert validate_stages()
    print("✓ Stages Module validated")
    
    # Demo
    print("\n--- Alchemical Stages Demo ---")
    
    print("\nThe Four Stages:")
    for stage in Stage:
        props = STAGES[stage]
        print(f"  {props.symbol} {props.name} ({props.color.value})")
        print(f"      Target: H={props.target_heat:.1f}, M={props.target_moisture:.1f}")
    
    print("\nExecuting the Great Work...")
    work = GreatWork(max_iterations=5000)
    result = work.execute(verbose=True)
    
    print(f"\nResult:")
    print(f"  Success: {result.success}")
    print(f"  Final Stage: {result.final_stage.name}")
    print(f"  Iterations: {result.total_iterations}")
    print(f"  Achieved Stone: {result.achieved_stone}")
    print(f"  Final State: {result.final_state}")
