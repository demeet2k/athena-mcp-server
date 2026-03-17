"""
ATHENA OS - EPICS: STATE EXTRACTION
====================================
State Space Extraction from Epic Narratives

STATE SPACE EXTRACTION:
    Identify the key STATE VARIABLES that the epic tracks and evolves.

MACRO-DOMAIN IDENTIFICATION:
    - Individual agent under extreme stress (hero)
    - Polity/civilization under threat (city, kingdom, empire)
    - Cosmic order and its stability (gods, fate, apocalypse)

STATE DIMENSIONS:
    - Political: legitimacy, sovereignty, alliances
    - Social: cohesion, trust, honor/reputation
    - Resource: food, cattle, gold, land, artifacts
    - Moral: justice/injustice, dharma/adharma, hubris/modesty
    - Psychological: rage, despair, resolve, fear, loyalty
    - Environmental: war/peace, famine/plenty, plague, omens
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Callable, Any, Union
from enum import Enum, auto
import numpy as np

from .epic_registry import EpicEntry, SystemDomain


# =============================================================================
# STATE DIMENSIONS
# =============================================================================

class StateDimension(Enum):
    """Categories of state dimensions tracked in epics."""
    
    POLITICAL = "political"       # Legitimacy, sovereignty, alliances
    SOCIAL = "social"             # Cohesion, trust, honor, reputation
    RESOURCE = "resource"         # Wealth, land, artifacts
    MORAL = "moral"               # Justice, dharma, hubris
    PSYCHOLOGICAL = "psychological"  # Rage, fear, resolve
    ENVIRONMENTAL = "environmental"  # War, peace, omens
    COSMIC = "cosmic"             # Divine favor, fate, karma


class StateScale(Enum):
    """Scale levels for state variables."""
    
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    OVERFLOW = 5


# =============================================================================
# STATE VARIABLE
# =============================================================================

@dataclass
class StateVariable:
    """
    A state variable tracked in an epic.
    
    Epics track specific variables and their evolution.
    """
    
    name: str
    dimension: StateDimension
    
    # Description
    description: str = ""
    
    # Bounds
    min_value: float = 0.0
    max_value: float = 1.0
    
    # Dynamics
    is_conserved: bool = False      # Does it follow conservation law?
    is_zero_sum: bool = False       # Is it zero-sum across agents?
    is_viral: bool = False          # Can it spread between agents?
    
    # Current value
    value: float = 0.5
    
    def set(self, value: float) -> None:
        """Set the state variable value (clamped)."""
        self.value = max(self.min_value, min(self.max_value, value))
    
    def increment(self, delta: float) -> None:
        """Increment the state variable."""
        self.set(self.value + delta)
    
    def get_scale(self) -> StateScale:
        """Get qualitative scale of current value."""
        if self.value <= 0:
            return StateScale.NONE
        elif self.value < 0.25:
            return StateScale.LOW
        elif self.value < 0.5:
            return StateScale.MEDIUM
        elif self.value < 0.75:
            return StateScale.HIGH
        elif self.value < 1.0:
            return StateScale.CRITICAL
        else:
            return StateScale.OVERFLOW
    
    def is_at_threshold(self, threshold: float = 0.9) -> bool:
        """Check if variable is at critical threshold."""
        return self.value >= threshold


# =============================================================================
# COMMON STATE VARIABLES
# =============================================================================

def create_common_state_variables() -> Dict[str, StateVariable]:
    """Create commonly tracked state variables across epics."""
    
    return {
        # Political
        "legitimacy": StateVariable(
            name="legitimacy",
            dimension=StateDimension.POLITICAL,
            description="Authority to rule, recognized by subjects",
            is_conserved=False
        ),
        "sovereignty": StateVariable(
            name="sovereignty",
            dimension=StateDimension.POLITICAL,
            description="Control over territory and decisions"
        ),
        "alliances": StateVariable(
            name="alliances",
            dimension=StateDimension.POLITICAL,
            description="Strength of coalition bonds"
        ),
        
        # Social
        "kleos": StateVariable(
            name="kleos",
            dimension=StateDimension.SOCIAL,
            description="Glory/fame - the Greek honor ledger",
            is_zero_sum=True
        ),
        "time": StateVariable(
            name="time",
            dimension=StateDimension.SOCIAL,
            description="Honor/respect from others"
        ),
        "cohesion": StateVariable(
            name="cohesion",
            dimension=StateDimension.SOCIAL,
            description="Group unity and trust"
        ),
        
        # Resource
        "wealth": StateVariable(
            name="wealth",
            dimension=StateDimension.RESOURCE,
            description="Material resources (gold, cattle, land)"
        ),
        "artifacts": StateVariable(
            name="artifacts",
            dimension=StateDimension.RESOURCE,
            description="Possession of key tokens (scepters, relics)"
        ),
        
        # Moral
        "dharma": StateVariable(
            name="dharma",
            dimension=StateDimension.MORAL,
            description="Alignment with cosmic order/duty"
        ),
        "hubris": StateVariable(
            name="hubris",
            dimension=StateDimension.MORAL,
            description="Excessive pride inviting divine punishment"
        ),
        "pietas": StateVariable(
            name="pietas",
            dimension=StateDimension.MORAL,
            description="Duty to gods, family, state"
        ),
        
        # Psychological
        "menis": StateVariable(
            name="menis",
            dimension=StateDimension.PSYCHOLOGICAL,
            description="Divine wrath/rage (Achilles' rage)",
            is_viral=True
        ),
        "nostos": StateVariable(
            name="nostos",
            dimension=StateDimension.PSYCHOLOGICAL,
            description="Longing for home/return"
        ),
        "grief": StateVariable(
            name="grief",
            dimension=StateDimension.PSYCHOLOGICAL,
            description="Mourning for loss"
        ),
        "resolve": StateVariable(
            name="resolve",
            dimension=StateDimension.PSYCHOLOGICAL,
            description="Determination to complete task"
        ),
        
        # Environmental
        "war_state": StateVariable(
            name="war_state",
            dimension=StateDimension.ENVIRONMENTAL,
            description="0=peace, 1=total war"
        ),
        "omens": StateVariable(
            name="omens",
            dimension=StateDimension.ENVIRONMENTAL,
            description="Prophetic signs of future"
        ),
        
        # Cosmic
        "divine_favor": StateVariable(
            name="divine_favor",
            dimension=StateDimension.COSMIC,
            description="Gods' support for agent"
        ),
        "moira": StateVariable(
            name="moira",
            dimension=StateDimension.COSMIC,
            description="Fate/allotted portion"
        ),
        "karma": StateVariable(
            name="karma",
            dimension=StateDimension.COSMIC,
            description="Accumulated action consequences"
        ),
    }


COMMON_VARIABLES = create_common_state_variables()


# =============================================================================
# STATE VECTOR
# =============================================================================

class StateVector:
    """
    A state vector representing system state at a point in time.
    
    x(t) = (x_1(t), x_2(t), ..., x_n(t))
    """
    
    def __init__(self, variables: Optional[List[str]] = None):
        self._variables: Dict[str, StateVariable] = {}
        
        if variables:
            for name in variables:
                if name in COMMON_VARIABLES:
                    self._variables[name] = StateVariable(
                        name=COMMON_VARIABLES[name].name,
                        dimension=COMMON_VARIABLES[name].dimension,
                        description=COMMON_VARIABLES[name].description,
                        is_conserved=COMMON_VARIABLES[name].is_conserved,
                        is_zero_sum=COMMON_VARIABLES[name].is_zero_sum,
                        is_viral=COMMON_VARIABLES[name].is_viral
                    )
                else:
                    self._variables[name] = StateVariable(
                        name=name,
                        dimension=StateDimension.PSYCHOLOGICAL
                    )
    
    def add_variable(self, var: StateVariable) -> None:
        """Add a state variable."""
        self._variables[var.name] = var
    
    def get(self, name: str) -> Optional[StateVariable]:
        """Get a state variable by name."""
        return self._variables.get(name)
    
    def set(self, name: str, value: float) -> None:
        """Set a state variable value."""
        if name in self._variables:
            self._variables[name].set(value)
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([v.value for v in self._variables.values()])
    
    def from_array(self, arr: np.ndarray) -> None:
        """Set values from numpy array."""
        for i, v in enumerate(self._variables.values()):
            if i < len(arr):
                v.set(float(arr[i]))
    
    def get_critical_variables(self, threshold: float = 0.9) -> List[str]:
        """Get variables at critical threshold."""
        return [name for name, v in self._variables.items() 
                if v.is_at_threshold(threshold)]
    
    def get_by_dimension(self, dim: StateDimension) -> Dict[str, StateVariable]:
        """Get all variables of a specific dimension."""
        return {name: v for name, v in self._variables.items() 
                if v.dimension == dim}
    
    def compute_entropy(self) -> float:
        """Compute entropy of the state vector."""
        values = self.to_array()
        # Normalize
        total = np.sum(values)
        if total <= 0:
            return 0.0
        
        probs = values / total
        probs = probs[probs > 0]  # Remove zeros
        
        return float(-np.sum(probs * np.log(probs + 1e-10)))
    
    @property
    def dimension(self) -> int:
        return len(self._variables)
    
    @property
    def variables(self) -> Dict[str, StateVariable]:
        return self._variables


# =============================================================================
# STATE SPACE
# =============================================================================

class StateSpace:
    """
    The state space of an epic narrative.
    
    Contains the full description of possible system states.
    """
    
    def __init__(self, epic: EpicEntry):
        self.epic = epic
        self.domain = epic.domain
        
        # Build state vector from epic's state variables
        self.state = StateVector(epic.state_variables)
        
        # Add domain-specific variables
        self._add_domain_variables()
        
        # Track state history
        self._history: List[Tuple[int, np.ndarray]] = []
        self._time = 0
    
    def _add_domain_variables(self) -> None:
        """Add domain-specific state variables."""
        if self.domain == SystemDomain.CONFLICT:
            for name in ["menis", "kleos", "time", "war_state"]:
                if name not in self.state.variables and name in COMMON_VARIABLES:
                    self.state.add_variable(StateVariable(
                        name=name,
                        dimension=COMMON_VARIABLES[name].dimension
                    ))
        
        elif self.domain == SystemDomain.MIGRATION:
            for name in ["nostos", "pietas", "resolve"]:
                if name not in self.state.variables and name in COMMON_VARIABLES:
                    self.state.add_variable(StateVariable(
                        name=name,
                        dimension=COMMON_VARIABLES[name].dimension
                    ))
        
        elif self.domain == SystemDomain.COSMIC:
            for name in ["dharma", "karma", "moira"]:
                if name not in self.state.variables and name in COMMON_VARIABLES:
                    self.state.add_variable(StateVariable(
                        name=name,
                        dimension=COMMON_VARIABLES[name].dimension
                    ))
    
    def evolve(self, operator: np.ndarray) -> np.ndarray:
        """
        Evolve the state by applying an operator.
        
        x(t+1) = operator @ x(t)
        """
        current = self.state.to_array()
        
        if operator.shape[0] != len(current):
            raise ValueError(f"Operator dimension mismatch: {operator.shape} vs {len(current)}")
        
        new_state = operator @ current
        self.state.from_array(new_state)
        
        self._time += 1
        self._history.append((self._time, new_state.copy()))
        
        return new_state
    
    def inject_event(self, variable: str, delta: float) -> None:
        """
        Inject an event that modifies a state variable.
        
        Models external shocks to the system.
        """
        var = self.state.get(variable)
        if var:
            var.increment(delta)
            self._history.append((self._time, self.state.to_array()))
    
    def check_threshold_breach(self) -> Dict[str, bool]:
        """Check which variables have breached thresholds."""
        return {name: v.is_at_threshold() 
                for name, v in self.state.variables.items()}
    
    def get_trajectory(self) -> np.ndarray:
        """Get the full state trajectory."""
        if not self._history:
            return np.array([self.state.to_array()])
        return np.array([s for _, s in self._history])
    
    @property
    def time(self) -> int:
        return self._time


# =============================================================================
# STATE EXTRACTOR
# =============================================================================

class StateExtractor:
    """
    Extracts state spaces from epic entries.
    
    Converts narrative data into formal state models.
    """
    
    def __init__(self):
        self._extracted: Dict[str, StateSpace] = {}
    
    def extract(self, epic: EpicEntry) -> StateSpace:
        """Extract state space from an epic."""
        if epic.name in self._extracted:
            return self._extracted[epic.name]
        
        space = StateSpace(epic)
        self._extracted[epic.name] = space
        return space
    
    def get_common_variables(self, epics: List[EpicEntry]) -> Set[str]:
        """Get state variables common across multiple epics."""
        if not epics:
            return set()
        
        common = set(epics[0].state_variables)
        for epic in epics[1:]:
            common &= set(epic.state_variables)
        
        return common
    
    def compare_state_spaces(self, epic1: EpicEntry, 
                            epic2: EpicEntry) -> Dict:
        """Compare state spaces of two epics."""
        space1 = self.extract(epic1)
        space2 = self.extract(epic2)
        
        vars1 = set(space1.state.variables.keys())
        vars2 = set(space2.state.variables.keys())
        
        return {
            "epic1": epic1.name,
            "epic2": epic2.name,
            "shared_variables": list(vars1 & vars2),
            "unique_to_epic1": list(vars1 - vars2),
            "unique_to_epic2": list(vars2 - vars1),
            "dimension_epic1": space1.state.dimension,
            "dimension_epic2": space2.state.dimension
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_state_extraction() -> bool:
    """Validate state extraction module."""
    from .epic_registry import EPIC_REGISTRY
    
    # Test StateVariable
    var = StateVariable(
        name="test_var",
        dimension=StateDimension.PSYCHOLOGICAL,
        value=0.5
    )
    
    var.increment(0.3)
    assert var.value == 0.8
    
    assert var.get_scale() == StateScale.CRITICAL
    assert not var.is_at_threshold(0.9)
    
    var.set(0.95)
    assert var.is_at_threshold(0.9)
    
    # Test StateVector
    vector = StateVector(["menis", "kleos", "dharma"])
    
    assert vector.dimension == 3
    
    menis = vector.get("menis")
    assert menis is not None
    assert menis.dimension == StateDimension.PSYCHOLOGICAL
    
    vector.set("menis", 0.9)
    critical = vector.get_critical_variables(0.8)
    assert "menis" in critical
    
    arr = vector.to_array()
    assert len(arr) == 3
    
    entropy = vector.compute_entropy()
    assert entropy >= 0
    
    # Test StateSpace
    iliad = EPIC_REGISTRY.get("Iliad")
    assert iliad is not None
    
    space = StateSpace(iliad)
    assert space.domain == SystemDomain.CONFLICT
    
    # Inject event
    space.inject_event("menis", 0.5)
    
    # Check threshold
    breaches = space.check_threshold_breach()
    assert isinstance(breaches, dict)
    
    # Test StateExtractor
    extractor = StateExtractor()
    
    space1 = extractor.extract(iliad)
    assert space1 is not None
    
    odyssey = EPIC_REGISTRY.get("Odyssey")
    assert odyssey is not None
    
    comparison = extractor.compare_state_spaces(iliad, odyssey)
    assert "shared_variables" in comparison
    
    return True


if __name__ == "__main__":
    print("Validating State Extraction Module...")
    assert validate_state_extraction()
    print("✓ State Extraction Module validated")
