"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      ATLAS FORGE - Crystal Combat System                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

Crystal Combat: Algorithmic Fighting for Mathematical Solutions.

Components:
- CrystalCard: Individual operation cards
- CrystalDeck: Collection of cards
- ZStarLock: Fixed point detection
- PivotRule: Card selection strategy
- Rotor: Coordinate transformation
- CrystalSolver: Main solver
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from enum import Enum, auto
import math
import random
import json

from atlasforge.core.types import Interval
from atlasforge.core.base import ContentAddressed
from atlasforge.core.enums import Pole
from atlasforge.lenses.chart import Chart


class CardType(Enum):
    ATTACK = auto()
    DEFEND = auto()
    TRANSFORM = auto()
    PIVOT = auto()
    PROBE = auto()
    LOCK = auto()
    UNLOCK = auto()


class CardRarity(Enum):
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    LEGENDARY = 5


@dataclass
class CrystalCard(ContentAddressed):
    """A Crystal Card represents a single operation/move."""
    
    name: str = ""
    card_type: CardType = CardType.ATTACK
    rarity: CardRarity = CardRarity.COMMON
    operation: Callable[[Any], Any] = field(default=lambda x: x)
    precondition: Callable[[Any], bool] = field(default=lambda x: True)
    cost: float = 1.0
    cooldown: int = 0
    current_cooldown: int = 0
    description: str = ""
    pole: Optional[Pole] = None
    
    def canonical_repr(self) -> str:
        return json.dumps({'name': self.name, 'type': self.card_type.value}, sort_keys=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'card_type': self.card_type.value,
            'rarity': self.rarity.value,
            'cost': self.cost,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CrystalCard':
        return cls(
            name=data.get('name', ''),
            card_type=CardType(data.get('card_type', 1)),
            rarity=CardRarity(data.get('rarity', 1)),
            cost=data.get('cost', 1.0))
    
    def can_play(self, state: Any) -> bool:
        return self.current_cooldown == 0 and self.precondition(state)
    
    def play(self, state: Any) -> Any:
        if not self.can_play(state):
            raise ValueError(f"Cannot play {self.name}")
        result = self.operation(state)
        self.current_cooldown = self.cooldown
        return result
    
    def tick(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
    
    def reset(self):
        self.current_cooldown = 0


@dataclass
class CrystalDeck:
    """A deck of Crystal Cards."""
    
    cards: List[CrystalCard] = field(default_factory=list)
    max_energy: float = 100.0
    current_energy: float = 100.0
    energy_regen: float = 10.0
    
    def add_card(self, card: CrystalCard):
        self.cards.append(card)
    
    def get_playable(self, state: Any) -> List[CrystalCard]:
        return [c for c in self.cards if c.can_play(state) and c.cost <= self.current_energy]
    
    def play_card(self, card: CrystalCard, state: Any) -> Any:
        if card.cost > self.current_energy:
            raise ValueError("Not enough energy")
        result = card.play(state)
        self.current_energy -= card.cost
        return result
    
    def tick(self):
        for card in self.cards:
            card.tick()
        self.current_energy = min(self.max_energy, self.current_energy + self.energy_regen)
    
    def reset(self):
        for card in self.cards:
            card.reset()
        self.current_energy = self.max_energy


class StandardCards:
    """Factory for standard Crystal Cards."""
    
    @staticmethod
    def newton_step(H: Callable, dH: Callable = None) -> CrystalCard:
        eps = 1e-8
        if dH is None:
            dH = lambda x: (H(x + eps) - H(x - eps)) / (2 * eps)
        
        def operation(x):
            fx, dfx = H(x), dH(x)
            return x if abs(dfx) < 1e-15 else x - fx / dfx
        
        return CrystalCard(name="Newton Step", card_type=CardType.ATTACK, 
                          operation=operation, cost=2.0, pole=Pole.D)
    
    @staticmethod
    def bisect_step(H: Callable, bracket: List[float]) -> CrystalCard:
        def operation(x):
            a, b = bracket
            c = (a + b) / 2
            if H(a) * H(c) < 0:
                bracket[1] = c
            else:
                bracket[0] = c
            return c
        
        return CrystalCard(name="Bisect Step", card_type=CardType.ATTACK,
                          operation=operation, cost=1.0, pole=Pole.PSI,
                          precondition=lambda x: H(bracket[0]) * H(bracket[1]) < 0)
    
    @staticmethod
    def project_to_interval(interval: Interval) -> CrystalCard:
        return CrystalCard(name="Project", card_type=CardType.DEFEND,
                          operation=lambda x: max(interval.lo, min(interval.hi, x)),
                          cost=0.5, pole=Pole.PSI)
    
    @staticmethod
    def random_perturbation(scale: float = 0.1) -> CrystalCard:
        return CrystalCard(name="Perturb", card_type=CardType.ATTACK,
                          operation=lambda x: x + random.gauss(0, scale),
                          cost=1.5, cooldown=2, pole=Pole.SIGMA)


@dataclass
class ZStarLock:
    """Z* Lock: Fixed point detection and locking."""
    
    tolerance: float = 1e-12
    patience: int = 5
    locked: bool = False
    locked_value: Optional[float] = None
    history: List[float] = field(default_factory=list)
    stable_count: int = 0
    last_value: Optional[float] = None
    
    def update(self, value: float) -> bool:
        if self.locked:
            return True
        
        self.history.append(value)
        if len(self.history) > 20:
            self.history.pop(0)
        
        if self.last_value is not None:
            if abs(value - self.last_value) < self.tolerance:
                self.stable_count += 1
            else:
                self.stable_count = 0
        
        self.last_value = value
        
        if self.stable_count >= self.patience or self._detect_cycle():
            self.lock(value)
            return True
        return False
    
    def lock(self, value: float):
        self.locked = True
        self.locked_value = value
    
    def unlock(self):
        self.locked = False
        self.locked_value = None
        self.stable_count = 0
    
    def _detect_cycle(self) -> bool:
        if len(self.history) < 4:
            return False
        if abs(self.history[-1] - self.history[-3]) < self.tolerance:
            if abs(self.history[-2] - self.history[-4]) < self.tolerance:
                return True
        return False
    
    def reset(self):
        self.locked = False
        self.locked_value = None
        self.history.clear()
        self.stable_count = 0
        self.last_value = None


class PivotRule(ABC):
    """Abstract base for pivot rules."""
    
    @abstractmethod
    def select(self, playable: List[CrystalCard], state: Any, residual: float) -> CrystalCard:
        pass


class GreedyPivot(PivotRule):
    def select(self, playable: List[CrystalCard], state: Any, residual: float) -> CrystalCard:
        return min(playable, key=lambda c: c.cost)


class AggressivePivot(PivotRule):
    def select(self, playable: List[CrystalCard], state: Any, residual: float) -> CrystalCard:
        attacks = [c for c in playable if c.card_type == CardType.ATTACK]
        return attacks[0] if attacks else playable[0]


class AdaptivePivot(PivotRule):
    def __init__(self, high_threshold: float = 1.0, low_threshold: float = 0.01):
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold
    
    def select(self, playable: List[CrystalCard], state: Any, residual: float) -> CrystalCard:
        if residual > self.high_threshold:
            attacks = [c for c in playable if c.card_type == CardType.ATTACK]
            if attacks:
                return max(attacks, key=lambda c: c.rarity.value)
        attacks = [c for c in playable if c.card_type == CardType.ATTACK]
        return min(attacks, key=lambda c: c.cost) if attacks else min(playable, key=lambda c: c.cost)


class PolePivot(PivotRule):
    def __init__(self):
        self.current_pole = Pole.D
        self.pole_order = [Pole.D, Pole.OMEGA, Pole.SIGMA, Pole.PSI]
    
    def select(self, playable: List[CrystalCard], state: Any, residual: float) -> CrystalCard:
        pole_cards = [c for c in playable if c.pole == self.current_pole]
        card = pole_cards[0] if pole_cards else playable[0]
        self.current_pole = self.pole_order[(self.pole_order.index(self.current_pole) + 1) % 4]
        return card


@dataclass
class Rotor:
    """Rotor provides coordinate transformations for 'dodging'."""
    
    charts: List[Chart] = field(default_factory=list)
    current_index: int = 0
    
    @property
    def current(self) -> Optional[Chart]:
        return self.charts[self.current_index] if self.charts else None
    
    def rotate(self, steps: int = 1):
        if self.charts:
            self.current_index = (self.current_index + steps) % len(self.charts)
    
    def transform(self, x: float) -> float:
        return self.current.forward(x) if self.current else x
    
    def inverse_transform(self, y: float) -> float:
        return self.current.inverse(y) if self.current else y


@dataclass
class CrystalSolverResult:
    """Result from Crystal Solver."""
    solution: Optional[float] = None
    residual: float = float('inf')
    converged: bool = False
    turns: int = 0
    cards_played: int = 0
    total_cost: float = 0.0
    card_history: List[str] = field(default_factory=list)
    value_history: List[float] = field(default_factory=list)
    locked: bool = False
    lock_reason: str = ""


class CrystalSolver:
    """The Crystal Combat solver."""
    
    def __init__(self, deck: CrystalDeck = None, pivot_rule: PivotRule = None,
                 rotor: Rotor = None, tolerance: float = 1e-12, max_turns: int = 1000):
        self.deck = deck or CrystalDeck()
        self.pivot_rule = pivot_rule or AdaptivePivot()
        self.rotor = rotor or Rotor()
        self.tolerance = tolerance
        self.max_turns = max_turns
        self.z_lock = ZStarLock(tolerance=tolerance)
    
    def solve(self, H: Callable[[float], float], x0: float = 0.0,
              domain: Interval = None) -> CrystalSolverResult:
        result = CrystalSolverResult()
        
        if not self.deck.cards:
            self._build_standard_deck(H, domain)
        
        self.deck.reset()
        self.z_lock.reset()
        x = x0
        
        for turn in range(self.max_turns):
            residual = abs(H(x))
            result.value_history.append(x)
            
            if residual < self.tolerance:
                result.solution, result.residual = x, residual
                result.converged, result.turns = True, turn
                return result
            
            if self.z_lock.update(x):
                result.solution = self.z_lock.locked_value
                result.residual = abs(H(self.z_lock.locked_value))
                result.converged = result.residual < self.tolerance
                result.locked, result.turns = True, turn
                return result
            
            playable = self.deck.get_playable(x)
            if not playable:
                self.deck.tick()
                continue
            
            try:
                card = self.pivot_rule.select(playable, x, residual)
                x = self.deck.play_card(card, x)
                result.cards_played += 1
                result.total_cost += card.cost
                result.card_history.append(card.name)
            except Exception:
                pass
            
            self.deck.tick()
        
        result.solution, result.residual = x, abs(H(x))
        result.turns = self.max_turns
        return result
    
    def _build_standard_deck(self, H: Callable, domain: Interval):
        self.deck.add_card(StandardCards.newton_step(H))
        if domain and domain.is_bounded:
            bracket = [domain.lo, domain.hi]
            self.deck.add_card(StandardCards.bisect_step(H, bracket))
            self.deck.add_card(StandardCards.project_to_interval(domain))
        self.deck.add_card(StandardCards.random_perturbation(0.1))


class CrystalCombatArena:
    """Arena for Crystal Combat matches."""
    
    def __init__(self):
        self.matches = []
        self.statistics = {'total': 0, 'wins': 0, 'turns': 0, 'cards': 0}
    
    def fight(self, solver: CrystalSolver, H: Callable, x0: float = 0.0,
              domain: Interval = None) -> CrystalSolverResult:
        result = solver.solve(H, x0, domain)
        self.statistics['total'] += 1
        if result.converged:
            self.statistics['wins'] += 1
        self.statistics['turns'] += result.turns
        self.statistics['cards'] += result.cards_played
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        s = self.statistics.copy()
        if s['total'] > 0:
            s['win_rate'] = s['wins'] / s['total']
            s['avg_turns'] = s['turns'] / s['total']
        return s
