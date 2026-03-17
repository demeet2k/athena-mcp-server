"""
ATHENA OS - QUR'ANIC HOLOGRAPHIC LATTICE
========================================
Part V: Time Stasis (The Cave / Al-Kahf)

THE TIME STASIS APPLICATION:
    A warp-factor peak A(φ) > 0 that generates massive time dilation.
    
    The narrative: 7 Sleepers + Dog remained in a cave for 309 years
    while appearing to sleep only one day.
    
    Time dilation ratio: 309:1 (or 300:1)

THE WARP FACTOR PEAK:
    At certain φ coordinates, A(φ) reaches positive values where
    the metric factor e^(2A) >> 1, creating a time dilation chamber.
    
    Δτ_cave / Δτ_exterior = e^(-A)

BIOLOGICAL PRESERVATION:
    - Standard metabolic rate suppressed by 1/309
    - Decay algorithms suspended
    - "Turning" mechanism prevents tidal stress

SOURCES:
    - Qur'anic Holographic Lattice manuscript, Chapter 3
    - Surah Al-Kahf (18): Verses 18:9-26
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import numpy as np
from scipy.optimize import brentq

from .lattice import IntegerLattice
from .metric import WarpFactor, Metric6D


# =============================================================================
# CONSTANTS FROM THE NARRATIVE
# =============================================================================

# Number of sleepers
N_SLEEPERS = 7  # Matches flux quantum n₁

# Additional companion
N_DOG = 1       # The dog (Qitmīr)

# Total occupants
N_TOTAL = 8     # 7 + 1 = 8 (2³, power of 2)

# Duration in years
YEARS_EXTERIOR = 309  # Some say 300
YEARS_INTERIOR = 1    # One day experienced

# Time dilation ratio
DILATION_RATIO = 309  # exterior/interior


# =============================================================================
# THE STASIS CHAMBER
# =============================================================================

class StasisState(Enum):
    """States of the stasis field."""
    
    INACTIVE = "inactive"
    CHARGING = "charging"
    ACTIVE = "active"
    DISCHARGING = "discharging"
    EMERGENCY = "emergency"


@dataclass
class StasisParameters:
    """
    Parameters defining the stasis field.
    
    The warp factor A(φ) at the chamber location determines
    the time dilation ratio.
    """
    
    # Target dilation ratio
    target_ratio: float = 309.0
    
    # Required warp factor
    required_A: float = field(init=False)
    
    # Chamber location in φ coordinate
    phi_chamber: float = 0.0
    
    def __post_init__(self):
        # e^(-A) = 1/ratio => A = ln(ratio)
        self.required_A = np.log(self.target_ratio)
    
    @property
    def metric_factor(self) -> float:
        """e^(2A) at chamber."""
        return np.exp(2 * self.required_A)
    
    @property
    def proper_time_ratio(self) -> float:
        """dτ_interior / dτ_exterior."""
        return 1.0 / self.target_ratio


@dataclass
class StasisChamber:
    """
    The time stasis chamber (Cave).
    
    A region of spacetime where the warp factor creates
    extreme time dilation relative to exterior.
    """
    
    params: StasisParameters = field(default_factory=StasisParameters)
    state: StasisState = StasisState.INACTIVE
    
    # Occupants
    n_sleepers: int = N_SLEEPERS
    has_dog: bool = True
    
    # Chamber geometry
    radius_m: float = 5.0
    depth_m: float = 3.0
    
    def __post_init__(self):
        self.lattice = IntegerLattice()
        self.occupant_count = self.n_sleepers + (1 if self.has_dog else 0)
    
    @property
    def total_occupants(self) -> int:
        return self.occupant_count
    
    def activate(self) -> bool:
        """Activate stasis field."""
        if self.state == StasisState.INACTIVE:
            self.state = StasisState.CHARGING
            # Simulate charging
            self.state = StasisState.ACTIVE
            return True
        return False
    
    def deactivate(self) -> bool:
        """Deactivate stasis field."""
        if self.state == StasisState.ACTIVE:
            self.state = StasisState.DISCHARGING
            # Simulate discharge
            self.state = StasisState.INACTIVE
            return True
        return False
    
    def elapsed_time(self, exterior_years: float) -> Dict[str, float]:
        """
        Calculate elapsed time inside vs outside.
        
        Args:
            exterior_years: Years passed in exterior reference frame
            
        Returns:
            Interior elapsed time breakdown
        """
        ratio = self.params.target_ratio
        interior_years = exterior_years / ratio
        
        return {
            "exterior_years": exterior_years,
            "interior_years": interior_years,
            "interior_days": interior_years * 365.25,
            "interior_hours": interior_years * 365.25 * 24,
            "dilation_ratio": ratio,
        }
    
    def occupant_positions(self) -> List[Dict[str, Any]]:
        """
        Calculate occupant positions with turning mechanism.
        
        The text mentions "We turned them to right and left" (18:18)
        to prevent tidal stress from static positioning.
        """
        positions = []
        
        for i in range(self.n_sleepers):
            angle = 2 * np.pi * i / self.n_sleepers
            x = self.radius_m * 0.5 * np.cos(angle)
            y = self.radius_m * 0.5 * np.sin(angle)
            
            positions.append({
                "sleeper": i + 1,
                "position": (x, y),
                "current_side": "right" if i % 2 == 0 else "left",
            })
        
        if self.has_dog:
            positions.append({
                "sleeper": "dog",
                "position": (self.radius_m * 0.7, 0),
                "current_side": "entrance",
            })
        
        return positions


# =============================================================================
# THE TURNING MECHANISM
# =============================================================================

@dataclass
class TurningMechanism:
    """
    The "turning" mechanism for biological preservation.
    
    "We turned them to the right and left" (18:18)
    
    Prevents:
    - Blood pooling from gravitational anisotropy
    - Tidal stress from warp field gradient
    - Localized pressure necrosis
    """
    
    # Turning period
    period_hours: float = 12.0  # Interior time
    
    # Phase perturbation
    phi_amplitude: float = 0.1  # Small phase oscillation
    angular_frequency: float = field(init=False)
    
    def __post_init__(self):
        self.angular_frequency = 2 * np.pi / self.period_hours
    
    def position_offset(self, t_hours: float) -> Tuple[float, float]:
        """
        Calculate position offset from turning.
        
        Returns (δx, δy) displacement.
        """
        phase = self.angular_frequency * t_hours
        
        # Simple oscillation model
        dx = self.phi_amplitude * np.sin(phase)
        dy = self.phi_amplitude * np.cos(phase)
        
        return (dx, dy)
    
    def current_side(self, t_hours: float) -> str:
        """Determine current turning side."""
        phase = self.angular_frequency * t_hours
        normalized = (phase % (2 * np.pi)) / (2 * np.pi)
        
        if normalized < 0.25:
            return "right"
        elif normalized < 0.5:
            return "back"
        elif normalized < 0.75:
            return "left"
        else:
            return "front"
    
    def stress_mitigation_factor(self) -> float:
        """
        Factor by which turning reduces accumulated stress.
        
        Without turning: stress accumulates linearly
        With turning: stress averages out over positions
        """
        # Approximate: 4 positions reduce stress by factor of 4
        return 0.25


# =============================================================================
# BIOLOGICAL PRESERVATION
# =============================================================================

@dataclass
class BiologicalPreservation:
    """
    Biological preservation in stasis field.
    
    Standard metabolic processes suppressed proportional
    to time dilation ratio.
    """
    
    dilation_ratio: float = DILATION_RATIO
    
    # Normal rates (arbitrary units)
    normal_heart_rate: float = 70.0      # bpm
    normal_respiration: float = 15.0     # breaths/min
    normal_metabolism: float = 1.0       # relative
    
    @property
    def effective_heart_rate(self) -> float:
        """Heart rate in exterior frame."""
        return self.normal_heart_rate / self.dilation_ratio
    
    @property
    def effective_respiration(self) -> float:
        """Respiration in exterior frame."""
        return self.normal_respiration / self.dilation_ratio
    
    @property
    def effective_metabolism(self) -> float:
        """Metabolic rate in exterior frame."""
        return self.normal_metabolism / self.dilation_ratio
    
    def apparent_age_gain(self, exterior_years: float) -> float:
        """
        Calculate apparent aging during stasis.
        
        For 309 exterior years, only 1 year of biological aging.
        """
        return exterior_years / self.dilation_ratio
    
    def decay_suppression(self) -> Dict[str, float]:
        """
        Suppression factors for decay processes.
        
        All decay is slowed by dilation factor.
        """
        factor = 1.0 / self.dilation_ratio
        
        return {
            "cellular_decay": factor,
            "oxidation": factor,
            "bacterial_growth": factor,
            "entropy_accumulation": factor,
        }


# =============================================================================
# THE CAVE GEOMETRY
# =============================================================================

@dataclass
class CaveGeometry:
    """
    The physical geometry of the cave.
    
    "Their dog stretching out his forelegs at the entrance" (18:18)
    """
    
    # Dimensions
    entrance_width_m: float = 2.0
    main_chamber_radius_m: float = 5.0
    ceiling_height_m: float = 3.0
    
    # Orientation
    entrance_bearing_deg: float = 90.0  # East-facing
    
    def solar_exposure(self, hour: float, day_of_year: int) -> float:
        """
        Calculate solar exposure at entrance.
        
        "The sun, when it rose, incline away from their cave 
        to the right, and when it set, turn away from them 
        to the left" (18:17)
        """
        # Simplified: assume cave oriented to minimize direct sunlight
        # Returns fraction of entrance illuminated
        
        # Solar azimuth varies through day
        solar_azimuth = (hour - 12) * 15 + 180  # Rough approximation
        
        angle_diff = abs(solar_azimuth - self.entrance_bearing_deg)
        
        if angle_diff > 90:
            return 0.0  # No direct exposure
        else:
            return 1.0 - (angle_diff / 90.0)
    
    def warp_field_profile(self, r: float) -> float:
        """
        Radial profile of warp field strength.
        
        Maximum at center, decreasing toward entrance.
        """
        r_normalized = r / self.main_chamber_radius_m
        
        if r_normalized > 1.0:
            return 0.0  # Outside chamber
        
        # Gaussian profile
        return np.exp(-2 * r_normalized**2)


# =============================================================================
# STASIS FIELD EQUATIONS
# =============================================================================

@dataclass
class StasisFieldEquations:
    """
    Field equations for the stasis chamber.
    
    The warp factor must be maintained at A ≈ ln(309) ≈ 5.73
    to achieve the required time dilation.
    """
    
    target_A: float = np.log(309)  # ≈ 5.73
    
    def dilation_from_A(self, A: float) -> float:
        """Calculate time dilation from warp factor."""
        return np.exp(A)
    
    def A_from_dilation(self, ratio: float) -> float:
        """Calculate required A for target dilation."""
        return np.log(ratio)
    
    def field_energy_density(self, A: float) -> float:
        """
        Energy density required to maintain field.
        
        Proportional to curvature induced by warp factor.
        """
        # Simplified: T_00 ~ (dA/dx)² + potential terms
        return A**2  # Proportional to A²
    
    def stability_condition(self, A: float, dA_dphi: float) -> bool:
        """
        Check if field configuration is stable.
        
        Requires d²V/dA² > 0 at minimum.
        """
        # Simplified stability check
        return abs(dA_dphi) < 0.1 * abs(A)
    
    def find_stable_chamber(self, warp: WarpFactor) -> Optional[float]:
        """
        Find φ coordinate where stable stasis is possible.
        
        Looks for local maximum of A(φ) near target value.
        """
        phi_grid, A_solution = warp.solve()
        
        # Find peaks
        for i in range(1, len(A_solution) - 1):
            if A_solution[i-1] < A_solution[i] > A_solution[i+1]:
                if A_solution[i] > 0:  # Positive peak
                    return phi_grid[i]
        
        return None


# =============================================================================
# COMPLETE STASIS SYSTEM
# =============================================================================

@dataclass
class StasisSystem:
    """
    Complete time stasis system.
    
    Integrates chamber, turning mechanism, biological preservation,
    and field equations.
    """
    
    chamber: StasisChamber = field(default_factory=StasisChamber)
    turning: TurningMechanism = field(default_factory=TurningMechanism)
    preservation: BiologicalPreservation = field(default_factory=BiologicalPreservation)
    geometry: CaveGeometry = field(default_factory=CaveGeometry)
    equations: StasisFieldEquations = field(default_factory=StasisFieldEquations)
    
    def __post_init__(self):
        self.lattice = IntegerLattice()
    
    def simulate_period(self, exterior_years: float) -> Dict[str, Any]:
        """
        Simulate a period of stasis.
        
        Args:
            exterior_years: Duration in exterior reference frame
            
        Returns:
            Simulation results
        """
        elapsed = self.chamber.elapsed_time(exterior_years)
        aging = self.preservation.apparent_age_gain(exterior_years)
        decay = self.preservation.decay_suppression()
        
        return {
            "exterior_duration_years": exterior_years,
            "interior_duration_years": elapsed["interior_years"],
            "interior_duration_days": elapsed["interior_days"],
            "biological_aging_years": aging,
            "decay_factors": decay,
            "occupants": self.chamber.total_occupants,
            "turning_cycles": exterior_years * 365.25 * 24 / self.turning.period_hours / DILATION_RATIO,
        }
    
    def verify_narrative_match(self) -> Dict[str, bool]:
        """
        Verify match with Qur'anic narrative numbers.
        
        309 years exterior, ~1 year interior, 7 sleepers.
        """
        sim = self.simulate_period(309)
        
        return {
            "duration_309_years": True,  # Input
            "interior_approx_1_year": abs(sim["interior_duration_years"] - 1.0) < 0.01,
            "sleepers_7": self.chamber.n_sleepers == 7,
            "plus_dog": self.chamber.has_dog,
            "total_8": self.chamber.total_occupants == 8,
        }
    
    def lattice_connections(self) -> Dict[str, Any]:
        """
        Connections between stasis and integer lattice.
        
        - 7 sleepers → n₁ = 7
        - 309 ratio → related to flux integers
        """
        return {
            "n_sleepers": self.chamber.n_sleepers,
            "matches_n1": self.chamber.n_sleepers == self.lattice.PRIME_RING_A,
            "dilation_ratio": DILATION_RATIO,
            "ratio_factorization": f"309 = 3 × 103",  # Contains k₂!
            "k2_connection": 103 in [103, 309//3],  # 309 = 3 × 103
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_stasis() -> bool:
    """Validate the stasis module."""
    
    # Test StasisParameters
    params = StasisParameters()
    assert abs(params.target_ratio - 309) < 0.1
    assert params.required_A > 5.0  # ln(309) ≈ 5.73
    
    # Test StasisChamber
    chamber = StasisChamber()
    assert chamber.n_sleepers == 7
    assert chamber.total_occupants == 8
    
    elapsed = chamber.elapsed_time(309)
    assert abs(elapsed["interior_years"] - 1.0) < 0.01
    
    # Test TurningMechanism
    turning = TurningMechanism()
    dx, dy = turning.position_offset(0)
    assert isinstance(dx, float)
    
    # Test BiologicalPreservation
    preservation = BiologicalPreservation()
    aging = preservation.apparent_age_gain(309)
    assert abs(aging - 1.0) < 0.01
    
    # Test StasisFieldEquations
    equations = StasisFieldEquations()
    A = equations.A_from_dilation(309)
    ratio_back = equations.dilation_from_A(A)
    assert abs(ratio_back - 309) < 0.01
    
    # Test StasisSystem
    system = StasisSystem()
    verification = system.verify_narrative_match()
    assert verification["interior_approx_1_year"]
    assert verification["sleepers_7"]
    
    connections = system.lattice_connections()
    assert connections["matches_n1"]
    
    return True


if __name__ == "__main__":
    print("Validating Stasis Module...")
    assert validate_stasis()
    print("✓ Stasis module validated")
    
    # Demo
    print("\n--- Time Stasis (The Cave) Demo ---")
    
    print("\n1. Stasis Parameters:")
    params = StasisParameters()
    print(f"   Target ratio: {params.target_ratio}:1")
    print(f"   Required warp A: {params.required_A:.3f}")
    print(f"   Metric factor e^(2A): {params.metric_factor:.2e}")
    
    print("\n2. Chamber Configuration:")
    chamber = StasisChamber()
    print(f"   Sleepers: {chamber.n_sleepers}")
    print(f"   With dog: {chamber.has_dog}")
    print(f"   Total: {chamber.total_occupants}")
    
    print("\n3. Time Elapsed (309 exterior years):")
    elapsed = chamber.elapsed_time(309)
    print(f"   Exterior: {elapsed['exterior_years']} years")
    print(f"   Interior: {elapsed['interior_years']:.2f} years")
    print(f"   Interior: {elapsed['interior_days']:.1f} days")
    
    print("\n4. Biological Preservation:")
    preservation = BiologicalPreservation()
    print(f"   Effective heart rate: {preservation.effective_heart_rate:.3f} bpm")
    print(f"   Apparent aging: {preservation.apparent_age_gain(309):.2f} years")
    
    print("\n5. Lattice Connections:")
    system = StasisSystem()
    connections = system.lattice_connections()
    print(f"   Sleepers = n₁: {connections['matches_n1']}")
    print(f"   309 = 3 × 103: k₂ = {103}")
    
    print("\n6. Narrative Verification:")
    verification = system.verify_narrative_match()
    for key, val in verification.items():
        status = "✓" if val else "✗"
        print(f"   {key}: {status}")
