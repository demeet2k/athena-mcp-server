"""
ATHENA OS - THE MATH OF ALCHEMY
================================
Module V: Stone (אבן) - The Philosopher's Stone as Attractor

THE PHILOSOPHER'S STONE DEFINED:
    The Stone is the mathematical attractor of the alchemical dynamical system.
    
    Definition: A state s* such that:
    O_Magnum(s*) = λ·s*  where λ ≥ 1
    
    Properties:
    1. Eigenstate of the composite Great Work operator
    2. Stable attractor for controlled dynamics
    3. Nontrivial elemental/quality coordinates

THE THREE STAGES (STAGES OF THE WORK):
    1. Nigredo (Blackening) - Dissolution, chaos, prima materia
    2. Albedo (Whitening) - Purification, separation, lunar
    3. Rubedo (Reddening) - Coagulation, fixation, solar

STABILITY ANALYSIS:
    The Stone's stability is analyzed via:
    - Linearization around the fixed point
    - Eigenvalues of the Jacobian
    - Lyapunov functionals
    - Basin of attraction

SOURCES:
    THE MATH OF ALCHEMY
    Classical Alchemical Tradition
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto

from .elements import ElementalState, ElementalSystem, QualityState, QualityMapping
from .tria_prima import TriaPrimaSystem, SulfurOperator, MercuryOperator, SaltOperator
from .planetary import PlanetarySystem, Planet
from .zodiac import ZodiacSystem, MagnumOpus, ZodiacSign


# =============================================================================
# STAGES OF THE WORK
# =============================================================================

class WorkStage(Enum):
    """The Three (or Four) Stages of the Great Work."""
    
    NIGREDO = ("Nigredo", "Blackening", "Melanosis", "Dissolution to prima materia")
    ALBEDO = ("Albedo", "Whitening", "Leukosis", "Purification and separation")
    CITRINITAS = ("Citrinitas", "Yellowing", "Xanthosis", "Dawn of solar consciousness")
    RUBEDO = ("Rubedo", "Reddening", "Iosis", "Final coagulation and fixation")
    
    def __init__(self, name: str, english: str, greek: str, description: str):
        self._name = name
        self.english = english
        self.greek = greek
        self._description = description


# =============================================================================
# THE PHILOSOPHER'S STONE
# =============================================================================

@dataclass
class PhilosophersStone:
    """
    The Philosopher's Stone - The Distinguished Attractor.
    
    The Stone is the eigenstate/fixed point of the Great Work operator
    that represents the completed transformation.
    
    Properties:
    - Elemental balance (typically Fire-dominant but stable)
    - Quality equilibrium (moderate heat, neutral moisture)
    - Planetary harmony (all influences balanced)
    - Zodiacal completion (full cycle integrated)
    """
    
    # The Stone's elemental composition
    elemental_state: ElementalState = field(default_factory=lambda: ElementalState(
        fire=0.4, air=0.3, water=0.2, earth=0.1
    ))
    
    # The Stone's quality coordinates
    quality_state: QualityState = field(default_factory=lambda: QualityState(
        heat=0.5, moisture=0.2
    ))
    
    # Eigenvalue (scaling factor under Great Work)
    eigenvalue: float = 1.0
    
    @classmethod
    def theoretical_stone(cls) -> 'PhilosophersStone':
        """
        The theoretical/ideal Philosopher's Stone.
        
        Gold-like composition with perfect balance.
        """
        return cls(
            elemental_state=ElementalState(
                fire=0.5,  # Solar/Gold dominance
                air=0.25,  # Intellectual clarity
                water=0.15,  # Emotional depth
                earth=0.10,  # Minimal but stable form
            ),
            quality_state=QualityState(
                heat=0.7,  # Warm/active
                moisture=0.1,  # Slightly dry (fixed)
            ),
            eigenvalue=1.0,
        )
    
    @property
    def is_valid_stone(self) -> bool:
        """Check if this represents a valid Stone state."""
        # Must be Fire or Air dominant (active/solar)
        p = self.elemental_state.normalized.probabilities
        return (p[0] > 0.3 or p[1] > 0.3) and self.eigenvalue >= 1.0
    
    def stability_measure(self) -> float:
        """
        Measure the stability of this Stone.
        
        Based on entropy and balance.
        """
        from .elements import ElementalSimplex
        p = np.array(self.elemental_state.normalized.probabilities)
        entropy = ElementalSimplex.entropy(p)
        
        # Optimal entropy is moderate (not too uniform, not too concentrated)
        optimal_entropy = 1.0  # Approximately log(e)
        stability = 1.0 / (1.0 + abs(entropy - optimal_entropy))
        
        return stability
    
    def get_summary(self) -> Dict[str, Any]:
        """Get Stone summary."""
        s = self.elemental_state
        return {
            "composition": {
                "fire": float(s.fire.real),
                "air": float(s.air.real),
                "water": float(s.water.real),
                "earth": float(s.earth.real),
            },
            "quality": {
                "heat": self.quality_state.heat,
                "moisture": self.quality_state.moisture,
            },
            "eigenvalue": self.eigenvalue,
            "valid": self.is_valid_stone,
            "stability": self.stability_measure(),
        }


# =============================================================================
# STONE FINDER
# =============================================================================

@dataclass
class StoneFinder:
    """
    Algorithm for finding the Philosopher's Stone.
    
    Uses the combined alchemical dynamical system to search
    for stable attractors.
    """
    
    tria_prima: TriaPrimaSystem = field(default_factory=TriaPrimaSystem)
    planetary: PlanetarySystem = field(default_factory=PlanetarySystem)
    zodiac: ZodiacSystem = field(default_factory=ZodiacSystem)
    
    def combined_step(self, state: ElementalState, t: float,
                      dt: float = 0.1) -> ElementalState:
        """
        Execute one step of the combined dynamical system.
        
        Applies: Tria Prima + Planetary + Zodiacal (current sign)
        """
        # Tria Prima dynamics
        current = self.tria_prima.step(state, dt)
        
        # Planetary modulation
        current = self.planetary.apply_all(current, t, dt)
        
        # Determine current zodiac sign (based on time)
        sign_idx = int((t / 30.4375) % 12)  # ~30 days per sign
        sign = list(ZodiacSign)[sign_idx]
        current = self.zodiac.apply_sign(current, sign, dt)
        
        return current
    
    def evolve_to_stone(self, initial_state: ElementalState,
                        max_time: float = 3650.0,  # 10 years
                        dt: float = 1.0,
                        tolerance: float = 1e-4) -> Tuple[ElementalState, float, bool]:
        """
        Evolve the system toward a Stone state.
        
        Returns (final_state, time_taken, converged).
        """
        current = initial_state
        t = 0.0
        
        while t < max_time:
            next_state = self.combined_step(current, t, dt)
            
            # Check for convergence (fixed point)
            diff = np.linalg.norm(next_state.vector - current.vector)
            if diff < tolerance:
                return next_state, t, True
            
            current = next_state
            t += dt
        
        return current, t, False
    
    def search_multiple_paths(self, n_attempts: int = 10,
                              max_time: float = 365.0) -> List[Tuple[ElementalState, float, bool]]:
        """
        Search for Stones from multiple initial conditions.
        """
        results = []
        
        for i in range(n_attempts):
            # Random initial state
            coeffs = np.random.dirichlet([1, 1, 1, 1])
            initial = ElementalState(
                fire=coeffs[0],
                air=coeffs[1],
                water=coeffs[2],
                earth=coeffs[3]
            )
            
            final, time, converged = self.evolve_to_stone(initial, max_time)
            results.append((final, time, converged))
        
        return results
    
    def analyze_basin(self, stone_state: ElementalState,
                      n_samples: int = 100,
                      perturbation: float = 0.1,
                      max_time: float = 100.0) -> Dict[str, Any]:
        """
        Analyze the basin of attraction around a Stone state.
        """
        converged_count = 0
        distances = []
        
        for _ in range(n_samples):
            # Perturb the Stone state
            perturbed = ElementalState(
                fire=stone_state.fire + perturbation * np.random.randn(),
                air=stone_state.air + perturbation * np.random.randn(),
                water=stone_state.water + perturbation * np.random.randn(),
                earth=stone_state.earth + perturbation * np.random.randn(),
            )
            
            final, _, converged = self.evolve_to_stone(perturbed, max_time)
            
            if converged:
                converged_count += 1
                dist = np.linalg.norm(final.vector - stone_state.vector)
                distances.append(float(dist))
        
        return {
            "convergence_rate": converged_count / n_samples,
            "mean_final_distance": np.mean(distances) if distances else float('inf'),
            "std_final_distance": np.std(distances) if distances else float('inf'),
            "samples": n_samples,
            "perturbation": perturbation,
        }


# =============================================================================
# STABILITY ANALYZER
# =============================================================================

@dataclass
class StabilityAnalyzer:
    """
    Analyze the stability of Stone states.
    
    Uses linearization and eigenvalue analysis.
    """
    
    tria_prima: TriaPrimaSystem = field(default_factory=TriaPrimaSystem)
    
    def jacobian_numerical(self, state: ElementalState,
                           epsilon: float = 1e-6) -> np.ndarray:
        """
        Compute the Jacobian numerically at a state.
        
        J_ij = ∂F_i/∂Ψ_j
        """
        n = 4
        J = np.zeros((n, n))
        
        for j in range(n):
            # Perturb in direction j
            psi_plus = state.vector.copy()
            psi_minus = state.vector.copy()
            psi_plus[j] += epsilon
            psi_minus[j] -= epsilon
            
            state_plus = ElementalState.from_vector(psi_plus)
            state_minus = ElementalState.from_vector(psi_minus)
            
            # Compute derivative via central difference
            f_plus = self.tria_prima.step(state_plus, dt=1.0).vector
            f_minus = self.tria_prima.step(state_minus, dt=1.0).vector
            
            J[:, j] = (f_plus - f_minus).real / (2 * epsilon)
        
        return J
    
    def eigenvalue_stability(self, state: ElementalState) -> Dict[str, Any]:
        """
        Analyze stability via eigenvalues of the Jacobian.
        
        Stable if all eigenvalues have Re(λ) < 0 (continuous)
        or |λ| < 1 (discrete).
        """
        J = self.jacobian_numerical(state)
        eigenvalues = np.linalg.eigvals(J)
        
        # For discrete system, stability requires |λ| < 1
        stable = all(np.abs(eigenvalues) < 1.0)
        
        return {
            "eigenvalues": eigenvalues,
            "spectral_radius": np.max(np.abs(eigenvalues)),
            "stable": stable,
            "jacobian": J,
        }
    
    def lyapunov_candidate(self, state: ElementalState,
                           reference: ElementalState = None) -> float:
        """
        Compute a Lyapunov function candidate.
        
        V(Ψ) = ||Ψ - Ψ*||² + W(H,M)
        
        where Ψ* is the reference Stone state.
        """
        if reference is None:
            reference = PhilosophersStone.theoretical_stone().elemental_state
        
        # Distance term
        dist = np.linalg.norm(state.vector - reference.vector) ** 2
        
        # Quality deviation term
        q = QualityMapping.map_to_quality(state)
        q_ref = QualityMapping.map_to_quality(reference)
        quality_dev = (q.heat - q_ref.heat) ** 2 + (q.moisture - q_ref.moisture) ** 2
        
        return float(dist + 0.5 * quality_dev)


# =============================================================================
# ALCHEMICAL SYSTEM (UNIFIED)
# =============================================================================

@dataclass
class AlchemicalSystem:
    """
    The complete unified alchemical dynamical system.
    
    A = (S, O, D) where:
    - S = State space (elemental × quality × planetary × zodiacal)
    - O = Operator family (Tria Prima + Planetary + Zodiacal)
    - D = Dynamical law (evolution equations)
    """
    
    tria_prima: TriaPrimaSystem = field(default_factory=TriaPrimaSystem)
    planetary: PlanetarySystem = field(default_factory=PlanetarySystem)
    zodiac: ZodiacSystem = field(default_factory=ZodiacSystem)
    magnum_opus: MagnumOpus = field(default_factory=MagnumOpus)
    stone_finder: StoneFinder = field(default_factory=StoneFinder)
    stability: StabilityAnalyzer = field(default_factory=StabilityAnalyzer)
    
    def __post_init__(self):
        """Share systems between components."""
        self.stone_finder.tria_prima = self.tria_prima
        self.stone_finder.planetary = self.planetary
        self.stone_finder.zodiac = self.zodiac
        self.stability.tria_prima = self.tria_prima
    
    def evolve(self, initial: ElementalState, 
               duration: float = 365.0,
               dt: float = 1.0) -> List[Tuple[float, ElementalState]]:
        """Evolve the system over time."""
        trajectory = [(0.0, initial)]
        current = initial
        t = 0.0
        
        while t < duration:
            t += dt
            current = self.stone_finder.combined_step(current, t, dt)
            trajectory.append((t, current))
        
        return trajectory
    
    def find_stone(self, initial: ElementalState,
                   max_time: float = 1000.0) -> PhilosophersStone:
        """Find the Philosopher's Stone from initial state."""
        final, time, converged = self.stone_finder.evolve_to_stone(
            initial, max_time
        )
        
        quality = QualityMapping.map_to_quality(final)
        
        return PhilosophersStone(
            elemental_state=final,
            quality_state=quality,
            eigenvalue=1.0 if converged else 0.0
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get complete system summary."""
        return {
            "name": "Alchemical Dynamical System",
            "formula": "A = (S, O, D)",
            "state_space": {
                "elemental_dim": 4,
                "quality_dim": 2,
                "planetary_dim": 7,
                "zodiacal_dim": 12,
            },
            "operators": {
                "tria_prima": ["Sulfur", "Mercury", "Salt"],
                "planets": 7,
                "zodiac": 12,
            },
            "goal": "Find Philosopher's Stone (distinguished attractor)",
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_stone() -> bool:
    """Validate the Stone module."""
    
    # Test WorkStage
    assert WorkStage.NIGREDO.english == "Blackening"
    assert WorkStage.RUBEDO.english == "Reddening"
    
    # Test PhilosophersStone
    stone = PhilosophersStone.theoretical_stone()
    assert stone.is_valid_stone
    assert stone.stability_measure() > 0
    
    summary = stone.get_summary()
    assert "composition" in summary
    assert summary["valid"]
    
    # Test StoneFinder
    finder = StoneFinder()
    initial = ElementalState(fire=0.2, air=0.2, water=0.3, earth=0.3)
    
    # Quick evolution test
    final, time, converged = finder.evolve_to_stone(
        initial, max_time=100.0, dt=1.0
    )
    assert final.magnitude > 0
    
    # Test StabilityAnalyzer
    analyzer = StabilityAnalyzer()
    eigen_analysis = analyzer.eigenvalue_stability(initial)
    assert "eigenvalues" in eigen_analysis
    
    lyap = analyzer.lyapunov_candidate(initial)
    assert lyap >= 0
    
    # Test AlchemicalSystem
    system = AlchemicalSystem()
    summary = system.get_summary()
    assert "state_space" in summary
    
    # Test evolution
    trajectory = system.evolve(initial, duration=10.0, dt=1.0)
    assert len(trajectory) > 1
    
    return True


if __name__ == "__main__":
    print("Validating Stone Module...")
    assert validate_stone()
    print("✓ Stone module validated")
    
    # Demo
    print("\n--- Philosopher's Stone Demo ---")
    
    print("\nStages of the Great Work:")
    for stage in WorkStage:
        print(f"  {stage._name}: {stage.english} ({stage.greek})")
    
    # Theoretical Stone
    stone = PhilosophersStone.theoretical_stone()
    print("\nTheoretical Philosopher's Stone:")
    s = stone.elemental_state
    print(f"  Fire={s.fire.real:.3f}, Air={s.air.real:.3f}, "
          f"Water={s.water.real:.3f}, Earth={s.earth.real:.3f}")
    print(f"  Heat={stone.quality_state.heat:.3f}, "
          f"Moisture={stone.quality_state.moisture:.3f}")
    print(f"  Valid: {stone.is_valid_stone}")
    print(f"  Stability: {stone.stability_measure():.4f}")
    
    # Find Stone from Lead
    print("\n--- Searching for Stone from Lead ---")
    system = AlchemicalSystem()
    lead = ElementalState(fire=0.05, air=0.05, water=0.1, earth=0.8)
    
    found_stone = system.find_stone(lead, max_time=500.0)
    fs = found_stone.elemental_state
    print(f"Found Stone:")
    print(f"  Fire={fs.fire.real:.3f}, Air={fs.air.real:.3f}, "
          f"Water={fs.water.real:.3f}, Earth={fs.earth.real:.3f}")
    print(f"  Valid: {found_stone.is_valid_stone}")
