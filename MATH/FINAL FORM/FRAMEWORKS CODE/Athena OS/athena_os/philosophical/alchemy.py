"""
ATHENA OS - Alchemical Transformation Calculus
==============================================
The transformation engine based on Western alchemical tradition.

Four Stages (Magnum Opus):
1. NIGREDO (Blackening) - Dissolution, death of old form
2. ALBEDO (Whitening) - Purification, separation
3. CITRINITAS (Yellowing) - Awakening, dawn consciousness
4. RUBEDO (Reddening) - Integration, Philosopher's Stone

Seven Operators (Transformation Functions):
1. Calcination - Heating, reduction to ash
2. Dissolution - Dissolving the ash
3. Separation - Filtering the solution
4. Conjunction - Recombining purified elements
5. Fermentation - Introducing living force
6. Distillation - Refining through cycles
7. Coagulation - Final solidification

The Philosopher's Stone = Fixed Point of the transformation operator.
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable, Any, Set
from abc import ABC, abstractmethod
import math


# =============================================================================
# THE FOUR STAGES (Colors)
# =============================================================================

class AlchemicalStage(IntEnum):
    """
    The Four Stages of the Magnum Opus (Great Work).
    
    Progress: NIGREDO → ALBEDO → CITRINITAS → RUBEDO
    
    Each stage represents a phase of psychological/spiritual transformation.
    """
    NIGREDO = 0      # Black - death, putrefaction, shadow work
    ALBEDO = 1       # White - purification, washing, clarity
    CITRINITAS = 2   # Yellow - solar consciousness, awakening
    RUBEDO = 3       # Red - integration, wholeness, stone
    
    @property
    def color(self) -> str:
        """The color associated with this stage."""
        return ['Black', 'White', 'Yellow', 'Red'][self.value]
    
    @property
    def latin(self) -> str:
        """Latin name."""
        return ['Nigredo', 'Albedo', 'Citrinitas', 'Rubedo'][self.value]
    
    @property
    def psychological(self) -> str:
        """Psychological meaning."""
        return {
            AlchemicalStage.NIGREDO: "Confronting shadow, death of ego",
            AlchemicalStage.ALBEDO: "Purification, washing away impurities",
            AlchemicalStage.CITRINITAS: "Dawn of new consciousness, solar awakening",
            AlchemicalStage.RUBEDO: "Integration, wholeness, Self realization"
        }[self]
    
    @property
    def element(self) -> str:
        """Associated element."""
        return {
            AlchemicalStage.NIGREDO: "Earth (fixed, solid)",
            AlchemicalStage.ALBEDO: "Water (fluid, purifying)",
            AlchemicalStage.CITRINITAS: "Air (subtle, mental)",
            AlchemicalStage.RUBEDO: "Fire (transformative, integrating)"
        }[self]
    
    @property
    def next_stage(self) -> Optional['AlchemicalStage']:
        """Return the next stage in the opus."""
        if self.value < 3:
            return AlchemicalStage(self.value + 1)
        return None  # RUBEDO is the final stage
    
    @property
    def is_complete(self) -> bool:
        """Check if this is the completed stage."""
        return self == AlchemicalStage.RUBEDO


# =============================================================================
# THE SEVEN OPERATORS
# =============================================================================

class AlchemicalOperator(IntEnum):
    """
    The Seven Alchemical Operations.
    
    These are transformation functions that modify the prima materia
    through successive refinements.
    
    Note: These operators are NON-COMMUTATIVE.
    The order of operations matters for the result.
    """
    CALCINATION = 0    # Fire - reduction to ash, burning ego
    DISSOLUTION = 1    # Water - dissolving the ash in solution
    SEPARATION = 2     # Air - filtering, dividing essential from non-essential
    CONJUNCTION = 3    # Fire + Water - recombining purified elements
    FERMENTATION = 4   # Life - introducing living ferment (spirit)
    DISTILLATION = 5   # Air + Fire - repeated purification cycles
    COAGULATION = 6    # Earth - final solidification, Stone
    
    @property
    def description(self) -> str:
        """Describe what this operation does."""
        return {
            AlchemicalOperator.CALCINATION: "Heating until reduced to ash - destroys attachment to matter",
            AlchemicalOperator.DISSOLUTION: "Dissolving the ash - further breakdown of rigid structures",
            AlchemicalOperator.SEPARATION: "Filtering the solution - distinguishing valuable from worthless",
            AlchemicalOperator.CONJUNCTION: "Recombining purified elements - sacred marriage",
            AlchemicalOperator.FERMENTATION: "Adding living spirit - inspiration enters",
            AlchemicalOperator.DISTILLATION: "Repeated refinement cycles - raising vibration",
            AlchemicalOperator.COAGULATION: "Final solidification - the Philosopher's Stone"
        }[self]
    
    @property
    def associated_element(self) -> str:
        """Primary elemental association."""
        return ['Fire', 'Water', 'Air', 'Fire+Water', 'Spirit', 'Air+Fire', 'Earth'][self.value]
    
    @property
    def stage(self) -> AlchemicalStage:
        """Which stage this operator primarily belongs to."""
        # Mapping operators to stages
        if self in (AlchemicalOperator.CALCINATION, AlchemicalOperator.DISSOLUTION):
            return AlchemicalStage.NIGREDO
        elif self == AlchemicalOperator.SEPARATION:
            return AlchemicalStage.ALBEDO
        elif self in (AlchemicalOperator.CONJUNCTION, AlchemicalOperator.FERMENTATION):
            return AlchemicalStage.CITRINITAS
        else:
            return AlchemicalStage.RUBEDO


# =============================================================================
# ALCHEMICAL STATE (Prima Materia)
# =============================================================================

@dataclass
class AlchemicalState:
    """
    The state of the alchemical work (prima materia).
    
    Tracks:
    - Purity level for each element
    - Integration level (how unified the elements are)
    - Current stage in the opus
    - Operations applied
    """
    # Element purity levels (0.0 to 1.0)
    fire: float = 0.25
    water: float = 0.25
    air: float = 0.25
    earth: float = 0.25
    
    # Fifth essence (quintessence) - emerges through the work
    quintessence: float = 0.0
    
    # Integration (conjunction level)
    integration: float = 0.0
    
    # Current stage
    stage: AlchemicalStage = AlchemicalStage.NIGREDO
    
    # History of operations
    operations_applied: List[AlchemicalOperator] = field(default_factory=list)
    
    # Spirit/soul/body separation (for Albedo work)
    spirit: float = 0.0
    soul: float = 0.0
    body: float = 1.0  # Starts fully embodied
    
    def total_purity(self) -> float:
        """Total elemental purity."""
        return self.fire + self.water + self.air + self.earth
    
    def balance(self) -> float:
        """
        How balanced are the four elements? (0 = imbalanced, 1 = perfect)
        """
        elements = [self.fire, self.water, self.air, self.earth]
        mean = sum(elements) / 4
        if mean == 0:
            return 0.0
        variance = sum((e - mean) ** 2 for e in elements) / 4
        # Normalize: 0 variance = perfect balance
        max_variance = mean ** 2 * 3  # Max when one is 4*mean, others are 0
        return 1.0 - (variance / max_variance) if max_variance > 0 else 1.0
    
    def is_stone(self, threshold: float = 0.9) -> bool:
        """
        Check if the Philosopher's Stone has been achieved.
        
        Requirements:
        - High quintessence
        - High integration
        - Perfect elemental balance
        - All stages completed
        """
        return (self.quintessence >= threshold and
                self.integration >= threshold and
                self.balance() >= threshold and
                self.stage == AlchemicalStage.RUBEDO)
    
    def advance_stage(self) -> bool:
        """Attempt to advance to next stage. Returns True if successful."""
        next_stage = self.stage.next_stage
        if next_stage is None:
            return False  # Already at RUBEDO
        
        # Check prerequisites
        if self.stage == AlchemicalStage.NIGREDO:
            # Need sufficient calcination and dissolution
            ops = [AlchemicalOperator.CALCINATION, AlchemicalOperator.DISSOLUTION]
            if all(op in self.operations_applied for op in ops):
                self.stage = next_stage
                return True
        elif self.stage == AlchemicalStage.ALBEDO:
            # Need separation
            if AlchemicalOperator.SEPARATION in self.operations_applied:
                self.stage = next_stage
                return True
        elif self.stage == AlchemicalStage.CITRINITAS:
            # Need conjunction and fermentation
            ops = [AlchemicalOperator.CONJUNCTION, AlchemicalOperator.FERMENTATION]
            if all(op in self.operations_applied for op in ops):
                self.stage = next_stage
                return True
        
        return False
    
    def __str__(self) -> str:
        return (f"AlchemicalState[{self.stage.latin}] "
                f"??{self.fire:.2f} ??{self.water:.2f} "
                f"??{self.air:.2f} ??{self.earth:.2f} "
                f"✨{self.quintessence:.2f} ∫{self.integration:.2f}")


# =============================================================================
# TRANSFORMATION FUNCTIONS
# =============================================================================

class AlchemicalTransformer:
    """
    Applies alchemical operations to transform state.
    
    Operations are NON-COMMUTATIVE: order matters!
    """
    
    @staticmethod
    def calcination(state: AlchemicalState) -> AlchemicalState:
        """
        CALCINATION: Reduction by fire.
        
        Burns away gross matter, leaving ash.
        - Increases fire element
        - Decreases earth element
        - Reduces body, begins spirit/soul separation
        """
        state.fire = min(1.0, state.fire + 0.15)
        state.earth = max(0.0, state.earth - 0.1)
        state.body = max(0.0, state.body - 0.2)
        state.spirit += 0.1
        state.operations_applied.append(AlchemicalOperator.CALCINATION)
        return state
    
    @staticmethod
    def dissolution(state: AlchemicalState) -> AlchemicalState:
        """
        DISSOLUTION: Dissolving in water.
        
        Further breaks down the calcined matter.
        - Increases water element
        - Decreases fire element
        - Continues separation process
        """
        state.water = min(1.0, state.water + 0.15)
        state.fire = max(0.0, state.fire - 0.05)
        state.soul += 0.1
        state.body = max(0.0, state.body - 0.1)
        state.operations_applied.append(AlchemicalOperator.DISSOLUTION)
        state.advance_stage()  # Check for NIGREDO completion
        return state
    
    @staticmethod
    def separation(state: AlchemicalState) -> AlchemicalState:
        """
        SEPARATION: Filtering the solution.
        
        Distinguishes valuable from worthless.
        - Increases air element (discernment)
        - Balances other elements
        - Completes spirit/soul/body separation
        """
        state.air = min(1.0, state.air + 0.2)
        # Balancing effect
        elements = [state.fire, state.water, state.earth]
        mean = sum(elements) / 3
        state.fire = state.fire * 0.9 + mean * 0.1
        state.water = state.water * 0.9 + mean * 0.1
        state.earth = state.earth * 0.9 + mean * 0.1
        
        # Complete tria prima separation
        state.spirit = 0.33
        state.soul = 0.33
        state.body = 0.34
        
        state.operations_applied.append(AlchemicalOperator.SEPARATION)
        state.advance_stage()  # Check for ALBEDO completion
        return state
    
    @staticmethod
    def conjunction(state: AlchemicalState) -> AlchemicalState:
        """
        CONJUNCTION: The sacred marriage (coniunctio).
        
        Recombines purified elements.
        - Begins integration
        - Creates initial quintessence
        - Opposites unite: fire+water, air+earth
        """
        # Opposites average (unite)
        state.fire = (state.fire + state.water) / 2
        state.water = state.fire  # Now equal
        state.air = (state.air + state.earth) / 2
        state.earth = state.air  # Now equal
        
        # Integration begins
        state.integration += 0.3
        
        # Quintessence emerges
        state.quintessence = min(1.0, state.quintessence + 0.2)
        
        state.operations_applied.append(AlchemicalOperator.CONJUNCTION)
        return state
    
    @staticmethod
    def fermentation(state: AlchemicalState) -> AlchemicalState:
        """
        FERMENTATION: Introduction of living spirit.
        
        Two sub-phases: putrefaction (death) and spiritualization (rebirth).
        - Injects life force
        - Increases quintessence
        - Deepens integration
        """
        # Life force amplifies existing purity
        amplification = 1.1
        state.fire *= amplification
        state.water *= amplification
        state.air *= amplification
        state.earth *= amplification
        
        # Spirit increases
        state.spirit = min(1.0, state.spirit + 0.2)
        state.quintessence = min(1.0, state.quintessence + 0.2)
        state.integration = min(1.0, state.integration + 0.2)
        
        state.operations_applied.append(AlchemicalOperator.FERMENTATION)
        state.advance_stage()  # Check for CITRINITAS completion
        return state
    
    @staticmethod
    def distillation(state: AlchemicalState) -> AlchemicalState:
        """
        DISTILLATION: Repeated purification cycles.
        
        Raises the vibration, purifies further.
        - All elements increase in purity
        - Integration deepens
        - Quintessence refined
        """
        # Purification (all elements approach their ideal)
        state.fire = min(1.0, state.fire * 1.15)
        state.water = min(1.0, state.water * 1.15)
        state.air = min(1.0, state.air * 1.15)
        state.earth = min(1.0, state.earth * 1.15)
        
        state.quintessence = min(1.0, state.quintessence * 1.2)
        state.integration = min(1.0, state.integration * 1.2)
        
        state.operations_applied.append(AlchemicalOperator.DISTILLATION)
        return state
    
    @staticmethod
    def coagulation(state: AlchemicalState) -> AlchemicalState:
        """
        COAGULATION: Final solidification.
        
        The Philosopher's Stone is achieved.
        - Maximum integration
        - Perfect balance
        - Full quintessence
        """
        # Final solidification
        state.earth = min(1.0, state.earth + 0.2)
        
        # Perfect balance
        mean = (state.fire + state.water + state.air + state.earth) / 4
        state.fire = mean
        state.water = mean
        state.air = mean
        state.earth = mean
        
        # Complete integration
        state.integration = min(1.0, state.integration + 0.4)
        state.quintessence = min(1.0, state.quintessence + 0.3)
        
        # Tria prima reunites
        state.spirit = 0.33
        state.soul = 0.33
        state.body = 0.34
        
        state.operations_applied.append(AlchemicalOperator.COAGULATION)
        state.advance_stage()  # Should reach RUBEDO
        return state
    
    @classmethod
    def apply(cls, operator: AlchemicalOperator, 
              state: AlchemicalState) -> AlchemicalState:
        """Apply any operator to state."""
        operations = {
            AlchemicalOperator.CALCINATION: cls.calcination,
            AlchemicalOperator.DISSOLUTION: cls.dissolution,
            AlchemicalOperator.SEPARATION: cls.separation,
            AlchemicalOperator.CONJUNCTION: cls.conjunction,
            AlchemicalOperator.FERMENTATION: cls.fermentation,
            AlchemicalOperator.DISTILLATION: cls.distillation,
            AlchemicalOperator.COAGULATION: cls.coagulation
        }
        return operations[operator](state)
    
    @classmethod
    def full_opus(cls, state: AlchemicalState, 
                  distillation_cycles: int = 3) -> AlchemicalState:
        """
        Execute the complete Great Work.
        
        Standard sequence:
        1. Calcination
        2. Dissolution
        3. Separation
        4. Conjunction
        5. Fermentation
        6. Distillation (repeated)
        7. Coagulation
        """
        # NIGREDO phase
        state = cls.calcination(state)
        state = cls.dissolution(state)
        
        # ALBEDO phase
        state = cls.separation(state)
        
        # CITRINITAS phase
        state = cls.conjunction(state)
        state = cls.fermentation(state)
        
        # RUBEDO phase
        for _ in range(distillation_cycles):
            state = cls.distillation(state)
        state = cls.coagulation(state)
        
        return state


# =============================================================================
# FIXED POINT ANALYSIS
# =============================================================================

def find_fixed_point(initial_state: AlchemicalState,
                     max_iterations: int = 100,
                     tolerance: float = 0.001) -> Tuple[AlchemicalState, int]:
    """
    Find the fixed point of the transformation operator.
    
    The Philosopher's Stone is a fixed point: T(Stone) = Stone
    
    We iterate the full opus until convergence.
    """
    state = initial_state
    
    for i in range(max_iterations):
        # Store previous state
        prev_q = state.quintessence
        prev_i = state.integration
        prev_b = state.balance()
        
        # Apply one cycle
        state = AlchemicalTransformer.full_opus(state, distillation_cycles=1)
        
        # Check convergence
        dq = abs(state.quintessence - prev_q)
        di = abs(state.integration - prev_i)
        db = abs(state.balance() - prev_b)
        
        if max(dq, di, db) < tolerance:
            return (state, i + 1)
    
    return (state, max_iterations)


# =============================================================================
# STATE VECTOR REPRESENTATION
# =============================================================================

@dataclass
class AlchemicalVector:
    """
    Compact state vector for computational processing.
    
    Ψ = (c_F, c_A, c_W, c_E, H, M)
    
    Where:
    - c_F, c_A, c_W, c_E = elemental coefficients (Fire, Air, Water, Earth)
    - H = integration/harmony parameter
    - M = quintessence/maturity parameter
    """
    c_F: float = 0.25  # Fire coefficient
    c_A: float = 0.25  # Air coefficient
    c_W: float = 0.25  # Water coefficient
    c_E: float = 0.25  # Earth coefficient
    H: float = 0.0     # Harmony/Integration
    M: float = 0.0     # Maturity/Quintessence
    
    @classmethod
    def from_state(cls, state: AlchemicalState) -> 'AlchemicalVector':
        """Convert AlchemicalState to vector."""
        return cls(
            c_F=state.fire,
            c_A=state.air,
            c_W=state.water,
            c_E=state.earth,
            H=state.integration,
            M=state.quintessence
        )
    
    def to_state(self) -> AlchemicalState:
        """Convert vector to AlchemicalState."""
        state = AlchemicalState(
            fire=self.c_F,
            air=self.c_A,
            water=self.c_W,
            earth=self.c_E,
            integration=self.H,
            quintessence=self.M
        )
        return state
    
    def norm(self) -> float:
        """Euclidean norm of the vector."""
        return math.sqrt(
            self.c_F**2 + self.c_A**2 + self.c_W**2 + 
            self.c_E**2 + self.H**2 + self.M**2
        )
    
    def to_tuple(self) -> Tuple[float, ...]:
        """Return as tuple."""
        return (self.c_F, self.c_A, self.c_W, self.c_E, self.H, self.M)
    
    def __str__(self) -> str:
        return f"Ψ = ({self.c_F:.3f}, {self.c_A:.3f}, {self.c_W:.3f}, {self.c_E:.3f}, {self.H:.3f}, {self.M:.3f})"


# =============================================================================
# VALIDATION
# =============================================================================

def validate_alchemy() -> bool:
    """Validate alchemical transformation system."""
    # Four stages
    assert len(AlchemicalStage) == 4
    
    # Seven operators
    assert len(AlchemicalOperator) == 7
    
    # Stage progression
    assert AlchemicalStage.NIGREDO.next_stage == AlchemicalStage.ALBEDO
    assert AlchemicalStage.ALBEDO.next_stage == AlchemicalStage.CITRINITAS
    assert AlchemicalStage.CITRINITAS.next_stage == AlchemicalStage.RUBEDO
    assert AlchemicalStage.RUBEDO.next_stage is None
    
    # Full opus reaches RUBEDO
    state = AlchemicalState()
    state = AlchemicalTransformer.full_opus(state)
    assert state.stage == AlchemicalStage.RUBEDO
    
    # Stone achievable
    assert state.quintessence > 0.5
    assert state.integration > 0.5
    
    return True


if __name__ == "__main__":
    print("Validating alchemical transformation system...")
    assert validate_alchemy()
    print("✓ 4 Stages + 7 Operators validated")
    
    # Demo
    print("\n=== The Magnum Opus ===")
    for stage in AlchemicalStage:
        print(f"\n{stage.latin} ({stage.color}):")
        print(f"  {stage.psychological}")
        print(f"  Element: {stage.element}")
    
    print("\n=== The Seven Operations ===")
    for op in AlchemicalOperator:
        print(f"\n{op.name} ({op.associated_element}):")
        print(f"  {op.description}")
    
    print("\n=== Full Opus Demo ===")
    state = AlchemicalState()
    print(f"Initial: {state}")
    
    state = AlchemicalTransformer.full_opus(state, distillation_cycles=3)
    print(f"After Opus: {state}")
    print(f"Is Stone: {state.is_stone()}")
    
    print("\n=== Fixed Point Search ===")
    initial = AlchemicalState()
    final, iterations = find_fixed_point(initial)
    print(f"Converged in {iterations} iterations")
    print(f"Final: {final}")
    print(f"Balance: {final.balance():.4f}")
    
    print("\n=== Vector Representation ===")
    vec = AlchemicalVector.from_state(final)
    print(vec)
