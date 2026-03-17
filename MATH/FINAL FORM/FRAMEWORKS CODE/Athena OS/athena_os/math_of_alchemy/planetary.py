"""
ATHENA OS - THE MATH OF ALCHEMY
================================
Module III: Planetary (כוכבים) - The Seven Planetary Operators

THE SEVEN CLASSICAL PLANETS:
    Each planet is a linear operator L_P on the elemental state space,
    modulated by periodic time functions.
    
    ☉ Sun     → Gold    → Fire Stabilization
    ☾ Moon    → Silver  → Water Amplification
    ☿ Mercury → Quicksilver → Air/Mixing/Volatility
    ♀ Venus   → Copper  → Cohesion/Harmony
    ♂ Mars    → Iron    → Combustion/Severing
    ♃ Jupiter → Tin     → Expansion/Growth
    ♄ Saturn  → Lead    → Contraction/Crystallization

PLANETARY FORCING:
    dΨ/dt|planets = Σ_P γ_P · Re(e^{iω_P t}) · L_P · Ψ(t)
    
    where:
    - γ_P = coupling strength
    - ω_P = synodic angular frequency
    - L_P = 4×4 planetary matrix

METALLIC EIGENSTATES:
    Each metal is a distinguished eigenstate of its planetary operator:
    L_P · Ψ^(P) = λ_P · Ψ^(P)

SOURCES:
    THE MATH OF ALCHEMY
    Classical Astrological Tradition
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto

from .elements import ElementalState, Element


# =============================================================================
# PLANETARY TYPES
# =============================================================================

class Planet(Enum):
    """The Seven Classical Planets."""
    
    SUN = ("☉", "Sun", "Sol", "Gold", "Au", 365.25)
    MOON = ("☾", "Moon", "Luna", "Silver", "Ag", 29.53)
    MERCURY = ("☿", "Mercury", "Mercurius", "Quicksilver", "Hg", 115.88)
    VENUS = ("♀", "Venus", "Venus", "Copper", "Cu", 583.92)
    MARS = ("♂", "Mars", "Mars", "Iron", "Fe", 779.94)
    JUPITER = ("♃", "Jupiter", "Iuppiter", "Tin", "Sn", 398.88)
    SATURN = ("♄", "Saturn", "Saturnus", "Lead", "Pb", 378.09)
    
    def __init__(self, symbol: str, name: str, latin: str, 
                 metal: str, element_symbol: str, synodic_period: float):
        self.symbol = symbol
        self._name = name
        self.latin = latin
        self.metal = metal
        self.element_symbol = element_symbol
        self.synodic_period = synodic_period  # days
    
    @property
    def synodic_frequency(self) -> float:
        """Angular frequency ω = 2π/T (radians per day)."""
        return 2 * np.pi / self.synodic_period
    
    @property
    def quality_influence(self) -> Dict[str, int]:
        """Hot/Cold and Moist/Dry influence."""
        influences = {
            Planet.SUN: {"heat": +1, "moisture": 0},
            Planet.MOON: {"heat": -1, "moisture": +1},
            Planet.MERCURY: {"heat": 0, "moisture": 0},  # Neutral
            Planet.VENUS: {"heat": 0, "moisture": +1},
            Planet.MARS: {"heat": +1, "moisture": -1},
            Planet.JUPITER: {"heat": +1, "moisture": +1},
            Planet.SATURN: {"heat": -1, "moisture": -1},
        }
        return influences[self]


# =============================================================================
# PLANETARY MATRICES
# =============================================================================

class PlanetaryMatrices:
    """
    The 4×4 matrices encoding each planet's action on elemental space.
    
    L_P: V_elem → V_elem
    
    Matrix entries encode how the planet stretches, contracts,
    transfers, or weights elemental intensities.
    """
    
    @staticmethod
    def sun() -> np.ndarray:
        """☉ Sun: Strengthens Fire, harmonizes Earth, clarifies Air/Water."""
        return np.array([
            [+1.0, +0.3, 0.0, +0.3],  # Fire row
            [+0.3, 0.0, 0.0, 0.0],    # Air row
            [0.0, 0.0, 0.0, 0.0],     # Water row
            [+0.3, 0.0, 0.0, +0.5],   # Earth row
        ])
    
    @staticmethod
    def moon() -> np.ndarray:
        """☾ Moon: Enhances Water, modulates Air-Water diffusion."""
        return np.array([
            [0.0, 0.0, 0.0, 0.0],      # Fire row
            [0.0, 0.0, +0.3, 0.0],     # Air row
            [+0.2, +0.3, +1.0, 0.0],   # Water row
            [0.0, 0.0, 0.0, 0.0],      # Earth row
        ])
    
    @staticmethod
    def mercury_planet() -> np.ndarray:
        """☿ Mercury: Enhances Air, rotates distribution, increases flux."""
        return np.array([
            [0.0, +0.4, 0.0, 0.0],     # Fire row
            [+0.4, 0.0, +0.4, +0.3],   # Air row
            [0.0, +0.3, 0.0, 0.0],     # Water row
            [0.0, +0.3, 0.0, 0.0],     # Earth row
        ])
    
    @staticmethod
    def venus() -> np.ndarray:
        """♀ Venus: Strengthens Water/Air, smooths ratios, cohesion."""
        return np.array([
            [0.0, +0.2, +0.2, 0.0],    # Fire row
            [+0.2, +0.5, +0.3, 0.0],   # Air row
            [+0.2, +0.3, +0.5, 0.0],   # Water row
            [0.0, 0.0, 0.0, 0.0],      # Earth row
        ])
    
    @staticmethod
    def mars() -> np.ndarray:
        """♂ Mars: Accelerates Fire, suppresses Water, cuts cohesion."""
        return np.array([
            [+1.0, +0.3, -0.5, 0.0],   # Fire row
            [0.0, 0.0, 0.0, 0.0],      # Air row
            [-0.3, 0.0, 0.0, 0.0],     # Water row
            [0.0, 0.0, 0.0, 0.0],      # Earth row
        ])
    
    @staticmethod
    def jupiter() -> np.ndarray:
        """♃ Jupiter: Amplifies scale, expands Fire-Air axis."""
        return np.array([
            [+0.7, +0.3, 0.0, 0.0],    # Fire row
            [+0.3, +0.7, 0.0, 0.0],    # Air row
            [0.0, 0.0, 0.0, 0.0],      # Water row
            [0.0, 0.0, 0.0, +0.3],     # Earth row
        ])
    
    @staticmethod
    def saturn() -> np.ndarray:
        """♄ Saturn: Strengthens Earth, suppresses volatility, structure."""
        return np.array([
            [-0.5, 0.0, 0.0, +0.2],    # Fire row
            [0.0, -0.3, 0.0, 0.0],     # Air row
            [0.0, 0.0, -0.3, 0.0],     # Water row
            [+0.3, 0.0, 0.0, +1.0],    # Earth row
        ])
    
    @classmethod
    def get_matrix(cls, planet: Planet) -> np.ndarray:
        """Get the planetary matrix for a given planet."""
        matrices = {
            Planet.SUN: cls.sun,
            Planet.MOON: cls.moon,
            Planet.MERCURY: cls.mercury_planet,
            Planet.VENUS: cls.venus,
            Planet.MARS: cls.mars,
            Planet.JUPITER: cls.jupiter,
            Planet.SATURN: cls.saturn,
        }
        return matrices[planet]()


# =============================================================================
# PLANETARY OPERATOR
# =============================================================================

@dataclass
class PlanetaryOperator:
    """
    A single planetary operator with time modulation.
    
    Ψ(t+Δt) = Ψ(t) + γ · Re(e^{iωt}) · L_P · Ψ(t)
    """
    
    planet: Planet
    coupling: float = 0.1  # γ_P
    
    @property
    def matrix(self) -> np.ndarray:
        """Get the planetary matrix."""
        return PlanetaryMatrices.get_matrix(self.planet)
    
    @property
    def frequency(self) -> float:
        """Get the synodic frequency."""
        return self.planet.synodic_frequency
    
    def modulation(self, t: float) -> float:
        """
        Time modulation factor: Re(e^{iωt}) = cos(ωt)
        """
        return np.cos(self.frequency * t)
    
    def apply(self, state: ElementalState, t: float, 
              dt: float = 0.1) -> ElementalState:
        """
        Apply the planetary operator at time t.
        
        Ψ_new = Ψ + γ · cos(ωt) · L_P · Ψ · dt
        """
        psi = state.vector.real
        mod = self.modulation(t)
        dpsi = self.coupling * mod * (self.matrix @ psi)
        new_psi = psi + dpsi * dt
        return ElementalState.from_vector(new_psi.astype(complex))
    
    def eigenanalysis(self) -> Dict[str, Any]:
        """Analyze eigenvalues and eigenvectors of the planetary matrix."""
        eigenvalues, eigenvectors = np.linalg.eig(self.matrix)
        return {
            "eigenvalues": eigenvalues,
            "eigenvectors": eigenvectors,
            "dominant_eigenvalue": eigenvalues[np.argmax(np.abs(eigenvalues))],
        }
    
    def metallic_eigenstate(self) -> np.ndarray:
        """
        Get the metallic eigenstate (dominant eigenvector).
        
        This represents the elemental composition of the associated metal.
        """
        _, eigenvectors = np.linalg.eig(self.matrix)
        eigenvalues = np.linalg.eigvals(self.matrix)
        dominant_idx = np.argmax(np.abs(eigenvalues))
        return np.abs(eigenvectors[:, dominant_idx])
    
    def get_summary(self) -> Dict[str, Any]:
        """Get operator summary."""
        return {
            "planet": self.planet._name,
            "symbol": self.planet.symbol,
            "metal": self.planet.metal,
            "coupling": self.coupling,
            "synodic_period_days": self.planet.synodic_period,
            "frequency": self.frequency,
        }


# =============================================================================
# PLANETARY SYSTEM
# =============================================================================

@dataclass
class PlanetarySystem:
    """
    The combined system of all seven planetary operators.
    
    dΨ/dt|planets = Σ_P γ_P · cos(ω_P t) · L_P · Ψ
    """
    
    operators: Dict[Planet, PlanetaryOperator] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize all planetary operators if not provided."""
        if not self.operators:
            for planet in Planet:
                self.operators[planet] = PlanetaryOperator(planet=planet)
    
    def set_coupling(self, planet: Planet, coupling: float):
        """Set the coupling strength for a planet."""
        if planet in self.operators:
            self.operators[planet].coupling = coupling
    
    def apply_all(self, state: ElementalState, t: float,
                  dt: float = 0.1) -> ElementalState:
        """
        Apply all planetary operators at time t.
        """
        current = state
        for planet, op in self.operators.items():
            current = op.apply(current, t, dt)
        return current
    
    def apply_single(self, state: ElementalState, planet: Planet,
                     t: float, dt: float = 0.1) -> ElementalState:
        """Apply a single planetary operator."""
        return self.operators[planet].apply(state, t, dt)
    
    def evolve(self, initial_state: ElementalState,
               n_steps: int = 100,
               dt: float = 1.0) -> List[Tuple[float, ElementalState]]:
        """
        Evolve the state under planetary influence.
        
        Returns list of (time, state) pairs.
        """
        trajectory = [(0.0, initial_state)]
        current = initial_state
        t = 0.0
        
        for _ in range(n_steps):
            t += dt
            current = self.apply_all(current, t, dt)
            trajectory.append((t, current))
        
        return trajectory
    
    def beat_period(self, planet1: Planet, planet2: Planet) -> float:
        """
        Calculate the beat period between two planets.
        
        T_beat = 1 / |1/T_1 - 1/T_2|
        """
        T1 = planet1.synodic_period
        T2 = planet2.synodic_period
        return 1.0 / abs(1.0/T1 - 1.0/T2)
    
    def resonance_analysis(self) -> Dict[str, float]:
        """Analyze beat periods between planetary pairs."""
        beats = {}
        planets = list(Planet)
        for i, p1 in enumerate(planets):
            for p2 in planets[i+1:]:
                key = f"{p1._name}-{p2._name}"
                beats[key] = self.beat_period(p1, p2)
        return beats
    
    def get_summary(self) -> Dict[str, Any]:
        """Get system summary."""
        return {
            "planets": len(self.operators),
            "operators": {p._name: op.get_summary() 
                         for p, op in self.operators.items()},
        }


# =============================================================================
# METALLIC TRANSFORMATIONS
# =============================================================================

@dataclass
class MetallicTransformation:
    """
    Transformations between metallic states (transmutation).
    
    The Great Work's metallic transformations are modeled as flows
    between planetary eigenstates.
    """
    
    @staticmethod
    def lead_to_gold_path() -> List[Planet]:
        """
        Traditional alchemical path: Lead → ... → Gold
        
        Saturn → Jupiter → Mars → Sun
        """
        return [Planet.SATURN, Planet.JUPITER, Planet.MARS, Planet.SUN]
    
    @staticmethod
    def get_metallic_composition(planet: Planet) -> ElementalState:
        """Get the idealized elemental composition of a metal."""
        compositions = {
            Planet.SUN: ElementalState(fire=0.6, air=0.3, water=0.05, earth=0.05),
            Planet.MOON: ElementalState(fire=0.1, air=0.2, water=0.6, earth=0.1),
            Planet.MERCURY: ElementalState(fire=0.2, air=0.5, water=0.2, earth=0.1),
            Planet.VENUS: ElementalState(fire=0.2, air=0.3, water=0.4, earth=0.1),
            Planet.MARS: ElementalState(fire=0.7, air=0.1, water=0.05, earth=0.15),
            Planet.JUPITER: ElementalState(fire=0.4, air=0.4, water=0.1, earth=0.1),
            Planet.SATURN: ElementalState(fire=0.05, air=0.05, water=0.1, earth=0.8),
        }
        return compositions[planet]
    
    @staticmethod
    def transmutation_distance(from_metal: Planet, to_metal: Planet) -> float:
        """
        Calculate the transformation distance between two metals.
        
        Based on elemental composition difference.
        """
        from_state = MetallicTransformation.get_metallic_composition(from_metal)
        to_state = MetallicTransformation.get_metallic_composition(to_metal)
        return float(np.linalg.norm(from_state.vector - to_state.vector))


# =============================================================================
# VALIDATION
# =============================================================================

def validate_planetary() -> bool:
    """Validate the Planetary module."""
    
    # Test Planet enum
    assert Planet.SUN.metal == "Gold"
    assert Planet.SATURN.metal == "Lead"
    assert Planet.SUN.synodic_period == 365.25
    
    # Test synodic frequency
    assert Planet.SUN.synodic_frequency > 0
    
    # Test PlanetaryMatrices
    sun_matrix = PlanetaryMatrices.sun()
    assert sun_matrix.shape == (4, 4)
    assert sun_matrix[0, 0] > 0  # Sun strengthens Fire
    
    saturn_matrix = PlanetaryMatrices.saturn()
    assert saturn_matrix[3, 3] > 0  # Saturn strengthens Earth
    
    # Test PlanetaryOperator
    sun_op = PlanetaryOperator(planet=Planet.SUN, coupling=0.2)
    assert sun_op.frequency == Planet.SUN.synodic_frequency
    
    state = ElementalState(fire=0.5, air=0.3, water=0.1, earth=0.1)
    new_state = sun_op.apply(state, t=0.0, dt=0.1)
    assert new_state.fire.real != state.fire.real
    
    # Test eigenanalysis
    eigen = sun_op.eigenanalysis()
    assert "eigenvalues" in eigen
    
    # Test metallic eigenstate
    metal_state = sun_op.metallic_eigenstate()
    assert len(metal_state) == 4
    
    # Test PlanetarySystem
    system = PlanetarySystem()
    assert len(system.operators) == 7
    
    # Test apply_all
    evolved = system.apply_all(state, t=10.0, dt=0.1)
    assert evolved.magnitude > 0
    
    # Test beat period
    beat = system.beat_period(Planet.MARS, Planet.VENUS)
    assert beat > 0
    
    # Test MetallicTransformation
    path = MetallicTransformation.lead_to_gold_path()
    assert path[0] == Planet.SATURN
    assert path[-1] == Planet.SUN
    
    dist = MetallicTransformation.transmutation_distance(Planet.SATURN, Planet.SUN)
    assert dist > 0
    
    return True


if __name__ == "__main__":
    print("Validating Planetary Module...")
    assert validate_planetary()
    print("✓ Planetary module validated")
    
    # Demo
    print("\n--- Planetary Demo ---")
    
    print("\nThe Seven Planets:")
    for planet in Planet:
        print(f"  {planet.symbol} {planet._name}: {planet.metal} ({planet.element_symbol})")
        print(f"      Synodic period: {planet.synodic_period:.2f} days")
    
    # Create system
    system = PlanetarySystem()
    
    # Set stronger Sun influence
    system.set_coupling(Planet.SUN, 0.3)
    
    # Initial state: Lead-like (Earth dominant)
    initial = ElementalState(fire=0.05, air=0.05, water=0.1, earth=0.8)
    
    print(f"\nInitial State (Lead-like):")
    print(f"  Fire={initial.fire.real:.3f}, Air={initial.air.real:.3f}, "
          f"Water={initial.water.real:.3f}, Earth={initial.earth.real:.3f}")
    
    # Evolve under planetary influence
    trajectory = system.evolve(initial, n_steps=365, dt=1.0)
    t_final, final = trajectory[-1]
    
    print(f"\nFinal State (after 365 days):")
    print(f"  Fire={final.fire.real:.3f}, Air={final.air.real:.3f}, "
          f"Water={final.water.real:.3f}, Earth={final.earth.real:.3f}")
    
    # Beat periods
    print("\nBeat Periods (days):")
    beats = system.resonance_analysis()
    for pair, period in list(beats.items())[:3]:
        print(f"  {pair}: {period:.1f}")
    
    # Transmutation distance
    dist = MetallicTransformation.transmutation_distance(Planet.SATURN, Planet.SUN)
    print(f"\nLead→Gold transmutation distance: {dist:.4f}")
