"""
ATHENA OS - QUMRAN KERNEL: DUALISM MODULE
==========================================
Two Spirits Doctrine and Binary Path Algebra

THE TWO SPIRITS (from Community Rule 1QS III-IV):
    God created two spirits to govern humanity:
    
    - Spirit of Truth (Ruach Emet): Prince of Light
    - Spirit of Falsehood (Ruach Avel): Angel of Darkness
    
    Every person walks in both spirits in varying proportions
    until the appointed End when Truth will be victorious.

BINARY PATH ALGEBRA:
    State space partitioned into two macro-states:
    - Way of Light (Γ_L): Path of righteousness
    - Way of Darkness (Γ_D): Path of wickedness
    
    Every action is a transition rule:
    - Virtue: e ∈ Virtues → e: Γ_L → Γ_L
    - Vice: e ∈ Vices → e: Γ_D → Γ_D
    
    No neutral moves - every action assigned to one path.

SONS OF LIGHT VS SONS OF DARKNESS:
    Global partition of humanity into two equivalence classes
    under the Light/Darkness operators.
    
    War Scroll (1QM): Final eschatological battle between
    the two camps.

RAZ NIHYEH (Mystery of Existence):
    Hidden Hamiltonian governing the system evolution.
    The "secret" that determines ultimate outcomes.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import numpy as np


# =============================================================================
# SPIRIT TYPES
# =============================================================================

class Spirit(Enum):
    """The two ruling spirits."""
    
    TRUTH = "truth"              # Ruach Emet - Spirit of Truth
    FALSEHOOD = "falsehood"      # Ruach Avel - Spirit of Falsehood


class PathType(Enum):
    """The two ways/paths."""
    
    LIGHT = "light"              # Way of Light/Life
    DARKNESS = "darkness"        # Way of Darkness/Death


class AllegianceType(Enum):
    """Cosmic allegiance."""
    
    SON_OF_LIGHT = "son_of_light"
    SON_OF_DARKNESS = "son_of_darkness"
    UNDECIDED = "undecided"      # In process of choice


# =============================================================================
# SPIRIT CHARACTERISTICS
# =============================================================================

@dataclass
class SpiritCharacteristics:
    """
    Characteristics of each spirit from Community Rule.
    
    Each spirit produces distinct fruits/outcomes.
    """
    
    spirit: Spirit
    
    # Ruler
    ruler: str
    
    # Domain
    realm: str
    light_level: float           # 0-1 (darkness to light)
    
    # Outcomes (fruits)
    virtues: List[str] = field(default_factory=list)
    vices: List[str] = field(default_factory=list)
    
    # Effects on followers
    reward: str = ""
    punishment: str = ""


SPIRIT_OF_TRUTH = SpiritCharacteristics(
    spirit=Spirit.TRUTH,
    ruler="Prince of Light (Michael)",
    realm="Eternal Light",
    light_level=1.0,
    virtues=[
        "humility",
        "patience",
        "compassion",
        "goodness",
        "understanding",
        "wisdom",
        "zeal_for_righteous_laws",
        "holy_intention",
        "steadfast_love",
        "modesty",
        "slowness_to_anger",
        "abundant_mercy",
        "eternal_goodness"
    ],
    vices=[],
    reward="healing_and_peace_and_length_of_days",
    punishment=""
)

SPIRIT_OF_FALSEHOOD = SpiritCharacteristics(
    spirit=Spirit.FALSEHOOD,
    ruler="Angel of Darkness (Belial)",
    realm="Eternal Darkness",
    light_level=0.0,
    virtues=[],
    vices=[
        "greed",
        "slackness_in_righteousness",
        "wickedness",
        "falsehood",
        "pride",
        "haughtiness",
        "deception",
        "cruelty",
        "great_impatience",
        "folly",
        "zeal_for_lust",
        "abominable_deeds",
        "spirit_of_fornication",
        "defilement",
        "blasphemy",
        "blindness_of_eyes",
        "dullness_of_ears",
        "stiffness_of_neck",
        "hardness_of_heart"
    ],
    reward="",
    punishment="eternal_torment_and_endless_reproach"
)


# =============================================================================
# LOT DISTRIBUTION
# =============================================================================

@dataclass
class LotDistribution:
    """
    Distribution of lots between the two spirits.
    
    Every person has portions in both spirits,
    determining their nature and actions.
    """
    
    light_portion: float         # 0-1 portion in light
    darkness_portion: float      # 0-1 portion in darkness
    
    def __post_init__(self):
        # Normalize to sum to 1
        total = self.light_portion + self.darkness_portion
        if total > 0:
            self.light_portion /= total
            self.darkness_portion /= total
    
    @classmethod
    def create(cls, light_ratio: float) -> LotDistribution:
        """Create distribution from light ratio (0-1)."""
        light = max(0, min(1, light_ratio))
        return cls(light_portion=light, darkness_portion=1 - light)
    
    def dominant_spirit(self) -> Spirit:
        """Get the dominant spirit."""
        if self.light_portion > self.darkness_portion:
            return Spirit.TRUTH
        elif self.darkness_portion > self.light_portion:
            return Spirit.FALSEHOOD
        else:
            return Spirit.TRUTH  # Tie goes to light
    
    def get_allegiance(self) -> AllegianceType:
        """Determine allegiance based on lot."""
        if self.light_portion > 0.5:
            return AllegianceType.SON_OF_LIGHT
        elif self.darkness_portion > 0.5:
            return AllegianceType.SON_OF_DARKNESS
        else:
            return AllegianceType.UNDECIDED


# =============================================================================
# BINARY PATH AUTOMATON
# =============================================================================

class PathState(Enum):
    """States in the two-way path automaton."""
    
    WAY_OF_LIGHT = "way_of_light"
    WAY_OF_DARKNESS = "way_of_darkness"
    BOUNDARY = "boundary"        # Between paths


@dataclass
class PathAction:
    """
    An action that moves along a path.
    
    Virtuous actions → stay/move toward Light
    Wicked actions → stay/move toward Darkness
    """
    
    name: str
    path_type: PathType
    weight: float = 1.0          # Strength of action
    
    def is_virtue(self) -> bool:
        return self.path_type == PathType.LIGHT
    
    def is_vice(self) -> bool:
        return self.path_type == PathType.DARKNESS


# Predefined actions
VIRTUOUS_ACTIONS = [
    PathAction("prayer", PathType.LIGHT, 1.0),
    PathAction("study_torah", PathType.LIGHT, 1.2),
    PathAction("charity", PathType.LIGHT, 1.0),
    PathAction("truthfulness", PathType.LIGHT, 1.1),
    PathAction("sabbath_keeping", PathType.LIGHT, 1.5),
    PathAction("purity_ritual", PathType.LIGHT, 0.8),
    PathAction("community_service", PathType.LIGHT, 1.0),
    PathAction("humility", PathType.LIGHT, 0.9),
    PathAction("patience", PathType.LIGHT, 0.8),
    PathAction("mercy", PathType.LIGHT, 1.0),
]

WICKED_ACTIONS = [
    PathAction("lying", PathType.DARKNESS, 1.0),
    PathAction("theft", PathType.DARKNESS, 1.2),
    PathAction("sabbath_violation", PathType.DARKNESS, 1.5),
    PathAction("idolatry", PathType.DARKNESS, 2.0),
    PathAction("murder", PathType.DARKNESS, 3.0),
    PathAction("adultery", PathType.DARKNESS, 1.8),
    PathAction("greed", PathType.DARKNESS, 0.8),
    PathAction("pride", PathType.DARKNESS, 0.7),
    PathAction("cruelty", PathType.DARKNESS, 1.3),
    PathAction("blasphemy", PathType.DARKNESS, 2.0),
]


class BinaryPathAutomaton:
    """
    Finite-state automaton with two macro-states.
    
    - Way of Life (Light)
    - Way of Death (Darkness)
    
    Each action is a transition rule that keeps or moves
    the agent along the paths.
    """
    
    def __init__(self, initial_state: PathState = PathState.BOUNDARY):
        self.state = initial_state
        self.history: List[PathAction] = []
        
        # Cumulative scores
        self.light_score: float = 0.0
        self.darkness_score: float = 0.0
    
    def perform_action(self, action: PathAction) -> Dict[str, Any]:
        """
        Perform an action and update state.
        
        Returns the effect of the action.
        """
        self.history.append(action)
        
        old_state = self.state
        
        if action.path_type == PathType.LIGHT:
            self.light_score += action.weight
        else:
            self.darkness_score += action.weight
        
        # Determine new state
        if self.light_score > self.darkness_score + 2:
            self.state = PathState.WAY_OF_LIGHT
        elif self.darkness_score > self.light_score + 2:
            self.state = PathState.WAY_OF_DARKNESS
        else:
            self.state = PathState.BOUNDARY
        
        return {
            "action": action.name,
            "type": action.path_type.value,
            "old_state": old_state.value,
            "new_state": self.state.value,
            "light_score": self.light_score,
            "darkness_score": self.darkness_score
        }
    
    def get_dominant_path(self) -> PathType:
        """Get the currently dominant path."""
        if self.light_score > self.darkness_score:
            return PathType.LIGHT
        else:
            return PathType.DARKNESS
    
    def get_trajectory(self) -> Dict[str, Any]:
        """Get overall trajectory analysis."""
        total = self.light_score + self.darkness_score
        
        if total == 0:
            light_ratio = 0.5
        else:
            light_ratio = self.light_score / total
        
        return {
            "total_actions": len(self.history),
            "light_score": self.light_score,
            "darkness_score": self.darkness_score,
            "light_ratio": light_ratio,
            "current_state": self.state.value,
            "dominant_path": self.get_dominant_path().value,
            "basin_of_attraction": "life" if light_ratio > 0.5 else "death"
        }


# =============================================================================
# WAR OF SONS
# =============================================================================

class WarPhase(Enum):
    """Phases of the eschatological war."""
    
    GATHERING = "gathering"      # Armies assemble
    FIRST_BATTLE = "first_battle"
    SECOND_BATTLE = "second_battle"
    THIRD_BATTLE = "third_battle"
    DECISIVE = "decisive"        # Final engagement
    VICTORY = "victory"          # Light triumphs


@dataclass
class Army:
    """An army in the war of Sons of Light vs Sons of Darkness."""
    
    allegiance: AllegianceType
    size: int
    strength: float              # Combat effectiveness
    morale: float                # Will to fight
    
    # Divine backing
    angelic_support: bool = False
    
    def combat_power(self) -> float:
        """Calculate total combat power."""
        base = self.size * self.strength * self.morale
        if self.angelic_support:
            base *= 1.5
        return base


class WarOfSons:
    """
    The eschatological war between Sons of Light and Sons of Darkness.
    
    From War Scroll (1QM):
    - 40-year war
    - Series of battles with alternating victories
    - Final victory for Sons of Light guaranteed
    """
    
    WAR_DURATION = 40  # Years
    
    def __init__(self):
        self.phase = WarPhase.GATHERING
        self.year = 0
        
        # Armies
        self.sons_of_light = Army(
            AllegianceType.SON_OF_LIGHT,
            size=12000,
            strength=1.0,
            morale=1.0,
            angelic_support=True
        )
        
        self.sons_of_darkness = Army(
            AllegianceType.SON_OF_DARKNESS,
            size=12000,
            strength=1.0,
            morale=1.0,
            angelic_support=False
        )
        
        # Battle history
        self.battles: List[Dict[str, Any]] = []
    
    def conduct_battle(self) -> Dict[str, Any]:
        """Conduct one battle."""
        light_power = self.sons_of_light.combat_power()
        dark_power = self.sons_of_darkness.combat_power()
        
        # Early battles alternate (as per War Scroll)
        if len(self.battles) < 6:
            # First three go each way
            if len(self.battles) % 2 == 0:
                winner = "light"
            else:
                winner = "darkness"
        else:
            # Later battles favor light due to divine intervention
            if light_power > dark_power * 0.9:
                winner = "light"
            else:
                winner = "darkness"
        
        # Apply casualties
        if winner == "light":
            self.sons_of_darkness.size = int(self.sons_of_darkness.size * 0.85)
            self.sons_of_darkness.morale *= 0.95
            self.sons_of_light.morale = min(1.0, self.sons_of_light.morale * 1.05)
        else:
            self.sons_of_light.size = int(self.sons_of_light.size * 0.9)
            self.sons_of_light.morale *= 0.98
        
        result = {
            "battle_number": len(self.battles) + 1,
            "winner": winner,
            "light_remaining": self.sons_of_light.size,
            "darkness_remaining": self.sons_of_darkness.size
        }
        
        self.battles.append(result)
        self._update_phase()
        
        return result
    
    def _update_phase(self) -> None:
        """Update war phase based on battles."""
        n = len(self.battles)
        
        if n == 0:
            self.phase = WarPhase.GATHERING
        elif n <= 2:
            self.phase = WarPhase.FIRST_BATTLE
        elif n <= 4:
            self.phase = WarPhase.SECOND_BATTLE
        elif n <= 6:
            self.phase = WarPhase.THIRD_BATTLE
        elif self.sons_of_darkness.size < 1000:
            self.phase = WarPhase.VICTORY
        else:
            self.phase = WarPhase.DECISIVE
    
    def run_war(self) -> Dict[str, Any]:
        """Run the complete war to conclusion."""
        while self.phase != WarPhase.VICTORY and len(self.battles) < 20:
            self.conduct_battle()
        
        return {
            "total_battles": len(self.battles),
            "final_phase": self.phase.value,
            "light_survivors": self.sons_of_light.size,
            "darkness_survivors": self.sons_of_darkness.size,
            "victory": self.phase == WarPhase.VICTORY
        }


# =============================================================================
# RAZ NIHYEH (Mystery of Existence)
# =============================================================================

class RazNihyeh:
    """
    Raz Nihyeh - The Mystery of Existence.
    
    The hidden Hamiltonian governing system evolution.
    Contains the "secrets" that determine outcomes.
    
    From 4QInstruction and Book of Mysteries.
    """
    
    def __init__(self):
        # Hidden parameters
        self._mystery_key: np.ndarray = np.random.randn(7)
        self._fate_matrix: np.ndarray = np.eye(7)
        
        # Revealed portion
        self.revealed_wisdom: List[str] = []
    
    def inquire(self, question: str) -> Dict[str, Any]:
        """
        Inquire into the mystery.
        
        Returns cryptic wisdom.
        """
        # Hash question to get index
        hash_val = hash(question) % len(self._wisdom_sayings())
        
        saying = self._wisdom_sayings()[hash_val]
        self.revealed_wisdom.append(saying)
        
        return {
            "question": question,
            "wisdom": saying,
            "mystery_depth": len(self.revealed_wisdom)
        }
    
    def _wisdom_sayings(self) -> List[str]:
        """Hidden wisdom sayings."""
        return [
            "Study the mystery of existence and know the paths of everything living",
            "Consider the years of generation to generation",
            "Walk in the way of truth according to the lot of your portion",
            "The mystery of existence reveals to the understanding ones",
            "Truth and righteousness are eternal foundations",
            "The end of darkness is determined, the end of deceit is fixed",
            "In the secrets of God's wisdom lies the appointed times"
        ]
    
    def calculate_fate(self, lot_distribution: LotDistribution) -> Dict[str, Any]:
        """
        Calculate fate based on lot distribution.
        
        Uses hidden Hamiltonian.
        """
        # Create state vector
        state = np.array([
            lot_distribution.light_portion,
            lot_distribution.darkness_portion,
            0.5,  # uncertainty
            0, 0, 0, 0  # padding
        ])
        
        # Apply mystery transformation
        fate_vector = self._fate_matrix @ (state + 0.1 * self._mystery_key)
        fate_value = np.sum(fate_vector[:2])
        
        if fate_value > 1:
            outcome = "inheritance_of_light"
        else:
            outcome = "inheritance_of_darkness"
        
        return {
            "lot_light": lot_distribution.light_portion,
            "lot_darkness": lot_distribution.darkness_portion,
            "fate_value": fate_value,
            "outcome": outcome
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_dualism() -> bool:
    """Validate dualism module."""
    
    # Test spirit characteristics
    assert SPIRIT_OF_TRUTH.light_level == 1.0
    assert SPIRIT_OF_FALSEHOOD.light_level == 0.0
    assert len(SPIRIT_OF_TRUTH.virtues) > 0
    assert len(SPIRIT_OF_FALSEHOOD.vices) > 0
    
    # Test lot distribution
    lot = LotDistribution.create(0.7)
    assert lot.light_portion == 0.7
    assert lot.darkness_portion == 0.3
    assert lot.dominant_spirit() == Spirit.TRUTH
    assert lot.get_allegiance() == AllegianceType.SON_OF_LIGHT
    
    # Test binary path automaton
    automaton = BinaryPathAutomaton()
    
    for action in VIRTUOUS_ACTIONS[:3]:
        automaton.perform_action(action)
    
    assert automaton.light_score > 0
    trajectory = automaton.get_trajectory()
    assert trajectory["dominant_path"] == "light"
    
    # Test war
    war = WarOfSons()
    result = war.run_war()
    assert result["victory"]  # Light always wins
    
    # Test Raz Nihyeh
    raz = RazNihyeh()
    wisdom = raz.inquire("What is the mystery?")
    assert "wisdom" in wisdom
    
    fate = raz.calculate_fate(lot)
    assert "outcome" in fate
    
    return True


if __name__ == "__main__":
    print("Validating Dualism Module...")
    assert validate_dualism()
    print("✓ Dualism Module validated")
    
    # Demo
    print("\n--- Two Spirits Demo ---")
    print("Spirit of Truth:")
    print(f"  Ruler: {SPIRIT_OF_TRUTH.ruler}")
    print(f"  Virtues: {SPIRIT_OF_TRUTH.virtues[:5]}...")
    
    print("\nSpirit of Falsehood:")
    print(f"  Ruler: {SPIRIT_OF_FALSEHOOD.ruler}")
    print(f"  Vices: {SPIRIT_OF_FALSEHOOD.vices[:5]}...")
    
    print("\n--- Binary Path Demo ---")
    automaton = BinaryPathAutomaton()
    
    actions = [
        VIRTUOUS_ACTIONS[0],
        VIRTUOUS_ACTIONS[1],
        WICKED_ACTIONS[0],
        VIRTUOUS_ACTIONS[2],
        VIRTUOUS_ACTIONS[3]
    ]
    
    for action in actions:
        result = automaton.perform_action(action)
        print(f"  {action.name}: {result['new_state']}")
    
    trajectory = automaton.get_trajectory()
    print(f"\nFinal basin: {trajectory['basin_of_attraction']}")
    
    print("\n--- War of Sons Demo ---")
    war = WarOfSons()
    result = war.run_war()
    print(f"  Battles: {result['total_battles']}")
    print(f"  Light survivors: {result['light_survivors']}")
    print(f"  Victory: {result['victory']}")
