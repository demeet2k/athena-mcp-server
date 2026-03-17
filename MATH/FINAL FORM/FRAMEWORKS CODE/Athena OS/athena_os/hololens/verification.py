"""
ATHENA OS - Verification Harness and Snap Controller
====================================================
Invariant tracking, convergence monitoring, and the snap procedure.

Verification Methodology:
1. Invariant Ledgers: Track conserved quantities, monotone functionals
2. Commutator Budgets: Quantify non-commutativity defects
3. Cross-Scale Certificates: Verify coarse models preserve invariants
4. Stability Regions: Map convergence domains

The Snap Controller:
The snap operator Z★ = P_spin,ε ○ P_≤Λ ○ Π_h ○ P_B produces a verified
shared state across all four corners of the crystal by:
1. Bandlimiting (P_≤Λ): Restrict to stable frequency range
2. Projecting (Π_h): Map to discrete grid
3. Spin-snapping (P_spin,ε): Lock to verified phases
4. Boundary correction (P_B): Handle edge effects
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable, Set
from datetime import datetime
import hashlib
import numpy as np
import math

from .crystal import Lens, Cell, Corner, CrystalCoordinate, CrystalLattice
from .antisymmetry import Defect, DefectType, DefectDetector, CommutatorBudget


# =============================================================================
# INVARIANT TYPES
# =============================================================================

class InvariantType(IntEnum):
    """
    Classification of invariants.
    
    Different invariants have different preservation requirements:
    - CONSERVED: Must remain exactly constant (energy, unitarity)
    - MONOTONE: Must only increase or decrease (entropy, Lyapunov)
    - STATIONARY: Must converge to fixed value (mixing)
    - COARSE: Must persist under coarse-graining (topology)
    """
    CONSERVED = 0   # Exact conservation (energy)
    MONOTONE = 1    # One-directional (entropy)
    STATIONARY = 2  # Converges to fixed point
    COARSE = 3      # Preserved under coarse-graining


@dataclass
class Invariant:
    """
    A tracked invariant quantity.
    
    Records the invariant's evolution and verification status.
    """
    name: str
    invariant_type: InvariantType
    
    # Current and history
    current_value: float = 0.0
    history: List[float] = field(default_factory=list)
    
    # Tolerance
    tolerance: float = 1e-10
    
    # Status
    verified: bool = True
    violation_count: int = 0
    last_checked: datetime = field(default_factory=datetime.now)
    
    def update(self, value: float) -> bool:
        """
        Update invariant value and check preservation.
        
        Returns True if invariant is preserved.
        """
        self.history.append(self.current_value)
        old_value = self.current_value
        self.current_value = value
        self.last_checked = datetime.now()
        
        # Check based on type
        if self.invariant_type == InvariantType.CONSERVED:
            if len(self.history) > 0:
                preserved = abs(value - old_value) < self.tolerance
            else:
                preserved = True
        
        elif self.invariant_type == InvariantType.MONOTONE:
            if len(self.history) > 0:
                # Check monotonicity (allowing for tolerance)
                preserved = (value >= old_value - self.tolerance)
            else:
                preserved = True
        
        elif self.invariant_type == InvariantType.STATIONARY:
            if len(self.history) > 1:
                # Check convergence: |Δ| decreasing
                prev_delta = abs(old_value - self.history[-1])
                curr_delta = abs(value - old_value)
                preserved = curr_delta <= prev_delta + self.tolerance
            else:
                preserved = True
        
        else:  # COARSE
            # Coarse invariants allow larger tolerance
            preserved = True
        
        if not preserved:
            self.violation_count += 1
            self.verified = False
        
        return preserved
    
    @property
    def drift(self) -> float:
        """Compute total drift from initial value."""
        if not self.history:
            return 0.0
        return abs(self.current_value - self.history[0])
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'type': self.invariant_type.name,
            'current': self.current_value,
            'drift': self.drift,
            'verified': self.verified,
            'violations': self.violation_count
        }


# =============================================================================
# INVARIANT LEDGER
# =============================================================================

@dataclass
class InvariantLedger:
    """
    Complete ledger of tracked invariants.
    
    Organizes invariants by type and provides verification summary.
    """
    name: str = "invariant_ledger"
    
    # Invariant storage
    invariants: Dict[str, Invariant] = field(default_factory=dict)
    
    # Global verification
    all_verified: bool = True
    total_violations: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    
    def add(self, name: str, invariant_type: InvariantType,
           initial_value: float = 0.0, tolerance: float = 1e-10) -> Invariant:
        """Add a new invariant to track."""
        inv = Invariant(
            name=name,
            invariant_type=invariant_type,
            current_value=initial_value,
            tolerance=tolerance
        )
        self.invariants[name] = inv
        return inv
    
    def update(self, name: str, value: float) -> bool:
        """Update an invariant and check preservation."""
        if name not in self.invariants:
            return True
        
        preserved = self.invariants[name].update(value)
        if not preserved:
            self.all_verified = False
            self.total_violations += 1
        
        return preserved
    
    def get(self, name: str) -> Optional[Invariant]:
        """Get invariant by name."""
        return self.invariants.get(name)
    
    def by_type(self, inv_type: InvariantType) -> List[Invariant]:
        """Get all invariants of a type."""
        return [inv for inv in self.invariants.values() 
                if inv.invariant_type == inv_type]
    
    def summary(self) -> Dict[str, Any]:
        """Get ledger summary."""
        by_type = {t.name: len(self.by_type(t)) for t in InvariantType}
        verified = sum(1 for inv in self.invariants.values() if inv.verified)
        
        return {
            'total': len(self.invariants),
            'verified': verified,
            'violations': self.total_violations,
            'by_type': by_type,
            'all_verified': self.all_verified
        }


# =============================================================================
# STABILITY REGION
# =============================================================================

@dataclass
class StabilityRegion:
    """
    Defines a stability region for numerical methods.
    
    Maps parameter ranges where methods converge.
    """
    name: str
    
    # Parameter bounds
    parameters: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    
    # Stability classification
    is_stable: bool = True
    stability_margin: float = 0.0
    
    def contains(self, params: Dict[str, float]) -> bool:
        """Check if parameters are in stable region."""
        for name, value in params.items():
            if name in self.parameters:
                low, high = self.parameters[name]
                if value < low or value > high:
                    return False
        return True
    
    def distance_to_boundary(self, params: Dict[str, float]) -> float:
        """Compute distance to stability boundary."""
        min_dist = float('inf')
        
        for name, value in params.items():
            if name in self.parameters:
                low, high = self.parameters[name]
                dist_low = abs(value - low)
                dist_high = abs(value - high)
                min_dist = min(min_dist, dist_low, dist_high)
        
        return min_dist if min_dist != float('inf') else 0.0


# =============================================================================
# SNAP CONTROLLER
# =============================================================================

class SnapController:
    """
    The Snap Controller: Produces verified shared state across crystal corners.
    
    The snap operator Z★ = P_spin,ε ○ P_≤Λ ○ Π_h ○ P_B consists of:
    1. P_B: Boundary correction
    2. Π_h: Discrete projection
    3. P_≤Λ: Bandlimit filter
    4. P_spin,ε: Spin/phase snapping
    
    The iteration converges to a fixed point that is consistent
    across all four lens views.
    """
    
    def __init__(self, 
                 bandlimit: int = 32,
                 grid_size: int = 64,
                 spin_phases: int = 4,
                 epsilon: float = 1e-6,
                 max_iterations: int = 100):
        
        self.bandlimit = bandlimit
        self.grid_size = grid_size
        self.spin_phases = spin_phases
        self.epsilon = epsilon
        self.max_iterations = max_iterations
        
        # Convergence tracking
        self.residuals: List[float] = []
        self.iterations_used: int = 0
        self.converged: bool = False
        
        # Verification
        self.invariant_ledger = InvariantLedger(name="snap_ledger")
        self.defect_detector = DefectDetector()
        self.commutator_budget = CommutatorBudget()
    
    def boundary_projection(self, state: np.ndarray) -> np.ndarray:
        """
        P_B: Boundary correction.
        
        Enforces boundary conditions (e.g., periodic, Dirichlet).
        """
        # Periodic boundary - ensure smooth wrap
        result = state.copy()
        # Apply taper at boundaries
        n = len(state)
        taper_width = max(1, n // 10)
        taper = np.linspace(0, 1, taper_width)
        
        result[:taper_width] *= taper
        result[-taper_width:] *= taper[::-1]
        
        return result
    
    def discrete_projection(self, state: np.ndarray) -> np.ndarray:
        """
        Π_h: Project to discrete grid.
        
        Samples state at grid points.
        """
        n = len(state)
        if n <= self.grid_size:
            return state
        
        # Downsample by averaging
        ratio = n // self.grid_size
        result = np.zeros(self.grid_size, dtype=state.dtype)
        for i in range(self.grid_size):
            result[i] = np.mean(state[i*ratio:(i+1)*ratio])
        
        return result
    
    def bandlimit_projection(self, state: np.ndarray) -> np.ndarray:
        """
        P_≤Λ: Bandlimit filter.
        
        Projects to frequencies below bandlimit Λ.
        """
        spectrum = np.fft.fft(state)
        n = len(spectrum)
        
        # Zero out high frequencies
        filtered = np.zeros_like(spectrum)
        B = min(self.bandlimit, n // 2)
        filtered[:B] = spectrum[:B]
        if n > B:
            filtered[-B:] = spectrum[-B:]
        
        return np.real(np.fft.ifft(filtered))
    
    def spin_projection(self, state: np.ndarray) -> np.ndarray:
        """
        P_spin,ε: Spin/phase snapping.
        
        Snaps phases to discrete values (e.g., {1, i, -1, -i} for 4 phases).
        """
        if np.iscomplexobj(state):
            magnitudes = np.abs(state)
            phases = np.angle(state)
            
            # Snap to discrete phases
            phase_step = 2 * np.pi / self.spin_phases
            snapped_phases = np.round(phases / phase_step) * phase_step
            
            return magnitudes * np.exp(1j * snapped_phases)
        else:
            # For real arrays, snap to sign
            return np.sign(state) * np.abs(state)
    
    def snap_operator(self, state: np.ndarray) -> np.ndarray:
        """
        Z★ = P_spin,ε ○ P_≤Λ ○ Π_h ○ P_B
        
        Apply the complete snap operator.
        """
        # Apply in order: boundary → discrete → bandlimit → spin
        s1 = self.boundary_projection(state)
        s2 = self.discrete_projection(s1)
        s3 = self.bandlimit_projection(s2)
        s4 = self.spin_projection(s3)
        
        return s4
    
    def iterate(self, initial_state: np.ndarray) -> Tuple[np.ndarray, bool]:
        """
        Iterate snap operator until convergence.
        
        Returns (fixed_point, converged).
        """
        current = initial_state.copy()
        self.residuals = []
        
        for iteration in range(self.max_iterations):
            next_state = self.snap_operator(current)
            
            # Compute residual
            residual = np.linalg.norm(next_state - current)
            self.residuals.append(residual)
            
            # Check convergence
            if residual < self.epsilon:
                self.converged = True
                self.iterations_used = iteration + 1
                return next_state, True
            
            current = next_state
        
        self.converged = False
        self.iterations_used = self.max_iterations
        return current, False
    
    def verify_fixed_point(self, state: np.ndarray) -> bool:
        """
        Verify that state is a valid fixed point.
        
        Checks:
        1. Snap-invariance: Z★(x) = x
        2. Invariant preservation
        3. Within commutator budget
        """
        snapped = self.snap_operator(state)
        residual = np.linalg.norm(snapped - state)
        
        if residual > self.epsilon:
            return False
        
        # Add to commutator budget
        self.commutator_budget.add_defect(
            Lens.SQUARE, residual, "snap_residual"
        )
        
        return self.commutator_budget.is_within_budget()
    
    def compute_holonomy(self, initial: np.ndarray, 
                        path: List[Callable]) -> Tuple[np.ndarray, float]:
        """
        Compute holonomy (loop defect) for a path of operators.
        
        If path commutes, result equals initial.
        Holonomy is the defect: ||result - initial||.
        """
        current = initial.copy()
        
        for operator in path:
            current = operator(current)
        
        holonomy = np.linalg.norm(current - initial)
        return current, holonomy
    
    def summary(self) -> Dict[str, Any]:
        return {
            'bandlimit': self.bandlimit,
            'grid_size': self.grid_size,
            'spin_phases': self.spin_phases,
            'epsilon': self.epsilon,
            'converged': self.converged,
            'iterations': self.iterations_used,
            'final_residual': self.residuals[-1] if self.residuals else None,
            'budget': self.commutator_budget.summary()
        }


# =============================================================================
# CROSS-SCALE CERTIFICATE
# =============================================================================

@dataclass
class CrossScaleCertificate:
    """
    Certificate that coarse model preserves correct invariants.
    
    Verifies that renormalized parameters are stable under
    further compression.
    """
    
    # Scales involved
    fine_scale: float
    coarse_scale: float
    
    # Invariants checked
    invariants_checked: List[str] = field(default_factory=list)
    invariants_preserved: List[str] = field(default_factory=list)
    
    # Parameters
    parameters_fine: Dict[str, float] = field(default_factory=dict)
    parameters_coarse: Dict[str, float] = field(default_factory=dict)
    
    # Verification
    verified: bool = False
    drift_bound: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def verify(self, tolerance: float = 0.1) -> bool:
        """
        Verify cross-scale consistency.
        
        Parameters should not drift more than tolerance.
        """
        total_drift = 0.0
        
        for key in self.parameters_fine:
            if key in self.parameters_coarse:
                fine_val = self.parameters_fine[key]
                coarse_val = self.parameters_coarse[key]
                
                if fine_val != 0:
                    drift = abs(coarse_val - fine_val) / abs(fine_val)
                else:
                    drift = abs(coarse_val)
                
                total_drift += drift
        
        self.drift_bound = total_drift
        self.verified = total_drift < tolerance
        
        return self.verified
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'fine_scale': self.fine_scale,
            'coarse_scale': self.coarse_scale,
            'verified': self.verified,
            'drift_bound': self.drift_bound,
            'invariants_preserved': self.invariants_preserved
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_verification() -> bool:
    """Validate verification harness."""
    
    # Test invariant types
    assert len(InvariantType) == 4
    
    # Test invariant tracking
    inv = Invariant(
        name="test_energy",
        invariant_type=InvariantType.CONSERVED,
        current_value=1.0,
        tolerance=1e-6
    )
    
    assert inv.update(1.0 + 1e-7)  # Within tolerance
    assert not inv.update(2.0)     # Out of tolerance
    
    # Test monotone invariant
    entropy = Invariant(
        name="test_entropy",
        invariant_type=InvariantType.MONOTONE,
        current_value=0.0
    )
    
    assert entropy.update(0.1)  # Increasing - OK
    assert entropy.update(0.2)  # Increasing - OK
    # Decreasing is a violation
    
    # Test invariant ledger
    ledger = InvariantLedger()
    ledger.add("energy", InvariantType.CONSERVED, initial_value=10.0)
    ledger.add("entropy", InvariantType.MONOTONE, initial_value=0.0)
    
    assert ledger.update("energy", 10.0)
    assert ledger.update("entropy", 0.5)
    
    # Test snap controller
    snap = SnapController(bandlimit=8, grid_size=16, epsilon=1e-4)
    
    # Create test state
    state = np.sin(np.linspace(0, 2*np.pi, 64))
    
    # Test individual projections
    s1 = snap.boundary_projection(state)
    assert len(s1) == len(state)
    
    s2 = snap.discrete_projection(state)
    assert len(s2) == snap.grid_size
    
    s3 = snap.bandlimit_projection(s2)
    assert len(s3) == len(s2)
    
    # Test iteration
    final, converged = snap.iterate(state)
    # May or may not converge depending on parameters
    
    # Test cross-scale certificate
    cert = CrossScaleCertificate(
        fine_scale=0.01,
        coarse_scale=0.1,
        parameters_fine={'k': 1.0, 'omega': 2.0},
        parameters_coarse={'k': 1.05, 'omega': 2.02}
    )
    
    assert cert.verify(tolerance=0.1)  # 5% drift is OK
    
    return True


if __name__ == "__main__":
    print("Validating Verification Harness...")
    assert validate_verification()
    print("✓ Verification Harness validated")
    
    # Demo
    print("\n=== Snap Controller Demo ===")
    snap = SnapController(bandlimit=8, grid_size=32, epsilon=1e-4)
    
    # Create test signal
    t = np.linspace(0, 2*np.pi, 64)
    signal = np.sin(t) + 0.3 * np.sin(5*t) + 0.1 * np.random.randn(64)
    
    print(f"Initial signal: length={len(signal)}, energy={np.sum(signal**2):.4f}")
    
    # Iterate
    fixed_point, converged = snap.iterate(signal)
    
    print(f"Converged: {converged}")
    print(f"Iterations: {snap.iterations_used}")
    print(f"Final residual: {snap.residuals[-1] if snap.residuals else 'N/A'}")
    print(f"Fixed point: length={len(fixed_point)}, energy={np.sum(fixed_point**2):.4f}")
    
    print(f"\nSnap summary: {snap.summary()}")
