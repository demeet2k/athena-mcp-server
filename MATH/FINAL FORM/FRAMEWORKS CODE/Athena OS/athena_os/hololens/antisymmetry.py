"""
ATHENA OS - Anti-Symmetry and Defect Framework
===============================================
Systematic treatment of crystal non-commutativity.

Anti-symmetry is the operator-valued residual when rotation paths disagree.
Where symmetry asserts "different paths yield the same object,"
anti-symmetry names the defect that appears when paths disagree.

For any diagram supposed to commute:
    X --f--> Y
    X --g--> Z --h--> Y
    
The anti-symmetry (defect) operator is:
    Δ := f - h∘g

Anti-symmetry is:
- COMPUTABLE: We can measure |Δx| for any input
- LOCALIZABLE: We can identify where defects concentrate
- PATCHABLE: We can design repair operators

Defect Types by Lens:
- Square: Kernel defects, quotient collapse, conditioning failure
- Flower: Spectral leakage, aliasing, phase discontinuity
- Cloud: Irreducible uncertainty, entropy inflation, mixing failure
- Fractal: Scale-dependent defects, fixed-point drift, holonomy
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable, Set
from datetime import datetime
import numpy as np
import math

from .crystal import Lens, Cell, CrystalCoordinate


# =============================================================================
# DEFECT TYPES
# =============================================================================

class DefectType(IntEnum):
    """
    Classification of anti-symmetry defects.
    
    Each defect type has characteristic signatures and repair strategies.
    """
    # Square defects (discrete/local)
    KERNEL = 0          # Blind spots - distinct states share same shadow
    QUOTIENT_COLLAPSE = 1  # Many-to-one mapping
    ILL_CONDITIONING = 2   # Sensitivity to perturbation
    RULE_MISMATCH = 3      # Local vs global rule inconsistency
    
    # Flower defects (spectral/phase)
    ALIASING = 4        # Frequency folding
    LEAKAGE = 5         # Energy escape from band
    PHASE_SLIP = 6      # Discontinuous phase
    MODE_MIXING = 7     # Eigenmode confusion
    
    # Cloud defects (stochastic/uncertainty)
    IRREDUCIBLE_NOISE = 8   # Fundamental uncertainty
    ENTROPY_INFLATION = 9   # Uncertainty growth
    MIXING_FAILURE = 10     # Non-ergodicity
    BIAS = 11               # Systematic offset
    
    # Fractal defects (multiscale/recursive)
    SCALE_DRIFT = 12        # Scale-dependent parameters
    FIXED_POINT_LOSS = 13   # RG fixed point instability
    HOLONOMY = 14           # Loop-dependent phase
    CORRIDOR_COLLAPSE = 15  # Convergence failure


@dataclass
class Defect:
    """
    A detected defect in the crystal lattice.
    
    Records the type, location, magnitude, and repair status.
    """
    defect_type: DefectType
    lens: Lens
    
    # Location
    location: Optional[CrystalCoordinate] = None
    spatial_position: Optional[np.ndarray] = None
    
    # Magnitude
    magnitude: float = 0.0
    threshold: float = 1e-6
    
    # Operators involved
    operator_a: str = ""
    operator_b: str = ""
    
    # Status
    detected_at: datetime = field(default_factory=datetime.now)
    repaired: bool = False
    repair_method: str = ""
    
    @property
    def is_significant(self) -> bool:
        """Check if defect exceeds threshold."""
        return self.magnitude > self.threshold
    
    @property
    def severity(self) -> str:
        """Classify defect severity."""
        if self.magnitude < self.threshold:
            return "negligible"
        elif self.magnitude < self.threshold * 10:
            return "minor"
        elif self.magnitude < self.threshold * 100:
            return "moderate"
        elif self.magnitude < self.threshold * 1000:
            return "severe"
        else:
            return "critical"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.defect_type.name,
            'lens': self.lens.name,
            'magnitude': self.magnitude,
            'threshold': self.threshold,
            'severity': self.severity,
            'repaired': self.repaired,
            'repair_method': self.repair_method
        }


# =============================================================================
# DEFECT DETECTOR
# =============================================================================

class DefectDetector:
    """
    Detects anti-symmetry defects by measuring commutator residuals.
    
    For operators A, B, the commutator is [A,B] = AB - BA.
    Non-zero commutator indicates non-commutativity (anti-symmetry).
    """
    
    def __init__(self, threshold: float = 1e-6):
        self.threshold = threshold
        self.detected_defects: List[Defect] = []
    
    def measure_commutator(self, A: np.ndarray, B: np.ndarray) -> float:
        """
        Measure commutator norm ||[A,B]||.
        
        Returns Frobenius norm of AB - BA.
        """
        commutator = A @ B - B @ A
        return np.linalg.norm(commutator, 'fro')
    
    def measure_path_defect(self, f: Callable, g: Callable, h: Callable,
                           x: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        Measure path defect: Δ = f - h∘g
        
        For diagram X --f--> Y and X --g--> Z --h--> Y,
        returns ||f(x) - h(g(x))||.
        """
        y_direct = f(x)
        z = g(x)
        y_indirect = h(z)
        
        delta = y_direct - y_indirect
        magnitude = np.linalg.norm(delta)
        
        return magnitude, delta
    
    def detect_kernel_defect(self, operator: np.ndarray, 
                            tolerance: float = 1e-10) -> Defect:
        """
        Detect kernel defects (blind spots).
        
        Non-trivial kernel means distinct inputs map to same output.
        """
        # Compute SVD to find null space
        U, s, Vh = np.linalg.svd(operator)
        
        # Count singular values below tolerance
        null_dim = np.sum(s < tolerance)
        
        defect = Defect(
            defect_type=DefectType.KERNEL,
            lens=Lens.SQUARE,
            magnitude=float(null_dim),
            threshold=0.5  # Any kernel dimension > 0 is a defect
        )
        
        if defect.is_significant:
            self.detected_defects.append(defect)
        
        return defect
    
    def detect_conditioning_defect(self, operator: np.ndarray) -> Defect:
        """
        Detect ill-conditioning defects.
        
        High condition number means sensitivity to perturbation.
        """
        try:
            cond = np.linalg.cond(operator)
        except:
            cond = float('inf')
        
        defect = Defect(
            defect_type=DefectType.ILL_CONDITIONING,
            lens=Lens.SQUARE,
            magnitude=cond,
            threshold=1e6  # Condition numbers above 10^6 are problematic
        )
        
        if defect.is_significant:
            self.detected_defects.append(defect)
        
        return defect
    
    def detect_aliasing(self, signal: np.ndarray, sample_rate: float,
                       max_freq: float) -> Defect:
        """
        Detect aliasing defects (Nyquist violation).
        
        Aliasing occurs when max_freq > sample_rate / 2.
        """
        nyquist = sample_rate / 2
        alias_ratio = max_freq / nyquist if nyquist > 0 else float('inf')
        
        defect = Defect(
            defect_type=DefectType.ALIASING,
            lens=Lens.FLOWER,
            magnitude=alias_ratio,
            threshold=1.0  # Ratio > 1 means aliasing
        )
        
        if defect.is_significant:
            self.detected_defects.append(defect)
        
        return defect
    
    def detect_spectral_leakage(self, spectrum: np.ndarray, 
                               band_low: int, band_high: int) -> Defect:
        """
        Detect spectral leakage outside declared band.
        
        Energy outside [band_low, band_high) is leakage.
        """
        total_energy = np.sum(np.abs(spectrum) ** 2)
        in_band = np.sum(np.abs(spectrum[band_low:band_high]) ** 2)
        
        if total_energy > 0:
            leakage_ratio = 1.0 - (in_band / total_energy)
        else:
            leakage_ratio = 0.0
        
        defect = Defect(
            defect_type=DefectType.LEAKAGE,
            lens=Lens.FLOWER,
            magnitude=leakage_ratio,
            threshold=0.01  # 1% leakage is threshold
        )
        
        if defect.is_significant:
            self.detected_defects.append(defect)
        
        return defect
    
    def detect_entropy_inflation(self, entropy_initial: float,
                                entropy_final: float) -> Defect:
        """
        Detect entropy inflation (uncertainty growth).
        """
        if entropy_initial > 0:
            inflation = entropy_final / entropy_initial
        else:
            inflation = entropy_final if entropy_final > 0 else 0.0
        
        defect = Defect(
            defect_type=DefectType.ENTROPY_INFLATION,
            lens=Lens.CLOUD,
            magnitude=inflation,
            threshold=1.1  # 10% inflation is threshold
        )
        
        if defect.is_significant:
            self.detected_defects.append(defect)
        
        return defect
    
    def detect_scale_drift(self, params_coarse: Dict[str, float],
                          params_fine: Dict[str, float]) -> Defect:
        """
        Detect scale drift (parameters change with resolution).
        """
        total_drift = 0.0
        for key in params_coarse:
            if key in params_fine and params_coarse[key] != 0:
                drift = abs(params_fine[key] - params_coarse[key]) / abs(params_coarse[key])
                total_drift += drift
        
        defect = Defect(
            defect_type=DefectType.SCALE_DRIFT,
            lens=Lens.FRACTAL,
            magnitude=total_drift,
            threshold=0.05  # 5% total drift is threshold
        )
        
        if defect.is_significant:
            self.detected_defects.append(defect)
        
        return defect
    
    def summary(self) -> Dict[str, Any]:
        """Get detection summary."""
        by_type = {}
        for defect in self.detected_defects:
            name = defect.defect_type.name
            if name not in by_type:
                by_type[name] = 0
            by_type[name] += 1
        
        return {
            'total_defects': len(self.detected_defects),
            'by_type': by_type,
            'severe_count': sum(1 for d in self.detected_defects 
                               if d.severity in ('severe', 'critical'))
        }


# =============================================================================
# REPAIR OPERATORS
# =============================================================================

class RepairOperator:
    """
    Base class for defect repair operators.
    
    Each repair operator targets specific defect types
    and applies corrective transformations.
    """
    
    def __init__(self, name: str, target_defects: List[DefectType]):
        self.name = name
        self.target_defects = target_defects
    
    def can_repair(self, defect: Defect) -> bool:
        """Check if this operator can repair the defect."""
        return defect.defect_type in self.target_defects
    
    def repair(self, defect: Defect, data: Any) -> Tuple[Any, bool]:
        """
        Attempt to repair defect.
        
        Returns (repaired_data, success).
        """
        raise NotImplementedError


class TikhonovRegularizer(RepairOperator):
    """
    Tikhonov regularization for ill-conditioning.
    
    Replaces A^(-1) with (A^T A + λI)^(-1) A^T.
    """
    
    def __init__(self, lambda_reg: float = 1e-6):
        super().__init__("Tikhonov", [DefectType.ILL_CONDITIONING, DefectType.KERNEL])
        self.lambda_reg = lambda_reg
    
    def repair(self, defect: Defect, operator: np.ndarray) -> Tuple[np.ndarray, bool]:
        """Apply Tikhonov regularization."""
        n = operator.shape[0]
        regularized = operator.T @ operator + self.lambda_reg * np.eye(n)
        
        try:
            inv = np.linalg.inv(regularized) @ operator.T
            return inv, True
        except:
            return operator, False


class AntiAliasFilter(RepairOperator):
    """
    Anti-alias filter for Nyquist violations.
    
    Applies lowpass filter before sampling.
    """
    
    def __init__(self, cutoff_ratio: float = 0.9):
        super().__init__("AntiAlias", [DefectType.ALIASING])
        self.cutoff_ratio = cutoff_ratio
    
    def repair(self, defect: Defect, spectrum: np.ndarray) -> Tuple[np.ndarray, bool]:
        """Apply anti-alias filter."""
        n = len(spectrum)
        cutoff = int(n * self.cutoff_ratio / 2)
        
        filtered = np.zeros_like(spectrum)
        filtered[:cutoff] = spectrum[:cutoff]
        filtered[-cutoff:] = spectrum[-cutoff:]
        
        return filtered, True


class WindowTaper(RepairOperator):
    """
    Window taper for spectral leakage.
    
    Applies smooth window function to reduce boundary effects.
    """
    
    def __init__(self, window_type: str = "hann"):
        super().__init__("WindowTaper", [DefectType.LEAKAGE])
        self.window_type = window_type
    
    def repair(self, defect: Defect, signal: np.ndarray) -> Tuple[np.ndarray, bool]:
        """Apply window taper."""
        n = len(signal)
        
        if self.window_type == "hann":
            window = 0.5 * (1 - np.cos(2 * np.pi * np.arange(n) / n))
        elif self.window_type == "hamming":
            window = 0.54 - 0.46 * np.cos(2 * np.pi * np.arange(n) / n)
        else:
            window = np.ones(n)
        
        return signal * window, True


class MultiscaleSmoother(RepairOperator):
    """
    Multiscale smoother for scale drift.
    
    Applies consistent smoothing across scales.
    """
    
    def __init__(self, smoothing_width: int = 3):
        super().__init__("MultiscaleSmoother", [DefectType.SCALE_DRIFT])
        self.smoothing_width = smoothing_width
    
    def repair(self, defect: Defect, hierarchy: List[np.ndarray]) -> Tuple[List[np.ndarray], bool]:
        """Apply multiscale smoothing."""
        smoothed = []
        for level in hierarchy:
            kernel = np.ones(min(self.smoothing_width, len(level))) / self.smoothing_width
            smoothed_level = np.convolve(level, kernel, mode='same')
            smoothed.append(smoothed_level)
        
        return smoothed, True


# =============================================================================
# COMMUTATOR BUDGET
# =============================================================================

@dataclass
class CommutatorBudget:
    """
    Tracks commutator defects across the crystal.
    
    Organizes error by BCH hierarchies and separates:
    - Physical effects (genuine non-commutativity)
    - Numerical artifacts (discretization errors)
    """
    
    # Budget allocation per lens
    square_budget: float = 1e-6
    flower_budget: float = 1e-8
    cloud_budget: float = 1e-4
    fractal_budget: float = 1e-5
    
    # Accumulated defects
    square_used: float = 0.0
    flower_used: float = 0.0
    cloud_used: float = 0.0
    fractal_used: float = 0.0
    
    # Defect log
    defect_log: List[Tuple[Lens, float, str]] = field(default_factory=list)
    
    def add_defect(self, lens: Lens, magnitude: float, source: str = "") -> bool:
        """
        Add defect to budget.
        
        Returns True if within budget, False if exceeded.
        """
        self.defect_log.append((lens, magnitude, source))
        
        if lens == Lens.SQUARE:
            self.square_used += magnitude
            return self.square_used <= self.square_budget
        elif lens == Lens.FLOWER:
            self.flower_used += magnitude
            return self.flower_used <= self.flower_budget
        elif lens == Lens.CLOUD:
            self.cloud_used += magnitude
            return self.cloud_used <= self.cloud_budget
        elif lens == Lens.FRACTAL:
            self.fractal_used += magnitude
            return self.fractal_used <= self.fractal_budget
        
        return True
    
    def remaining(self, lens: Lens) -> float:
        """Get remaining budget for lens."""
        if lens == Lens.SQUARE:
            return max(0, self.square_budget - self.square_used)
        elif lens == Lens.FLOWER:
            return max(0, self.flower_budget - self.flower_used)
        elif lens == Lens.CLOUD:
            return max(0, self.cloud_budget - self.cloud_used)
        elif lens == Lens.FRACTAL:
            return max(0, self.fractal_budget - self.fractal_used)
        return 0.0
    
    def is_within_budget(self) -> bool:
        """Check if all lenses are within budget."""
        return (self.square_used <= self.square_budget and
                self.flower_used <= self.flower_budget and
                self.cloud_used <= self.cloud_budget and
                self.fractal_used <= self.fractal_budget)
    
    def summary(self) -> Dict[str, Any]:
        return {
            'square': {'used': self.square_used, 'budget': self.square_budget},
            'flower': {'used': self.flower_used, 'budget': self.flower_budget},
            'cloud': {'used': self.cloud_used, 'budget': self.cloud_budget},
            'fractal': {'used': self.fractal_used, 'budget': self.fractal_budget},
            'within_budget': self.is_within_budget(),
            'total_defects': len(self.defect_log)
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_antisymmetry() -> bool:
    """Validate anti-symmetry framework."""
    
    # Test defect types
    assert len(DefectType) == 16
    
    # Test defect detection
    detector = DefectDetector()
    
    # Test commutator measurement
    A = np.array([[1, 2], [3, 4]], dtype=float)
    B = np.array([[0, 1], [1, 0]], dtype=float)
    comm = detector.measure_commutator(A, B)
    assert comm > 0  # Non-zero commutator
    
    # Test kernel detection
    singular = np.array([[1, 2], [2, 4]], dtype=float)  # Rank 1
    defect = detector.detect_kernel_defect(singular)
    assert defect.magnitude == 1  # One-dimensional kernel
    
    # Test conditioning detection
    ill_cond = np.array([[1, 1e-10], [1, 1]], dtype=float)
    defect = detector.detect_conditioning_defect(ill_cond)
    assert defect.magnitude > 1e6  # High condition number
    
    # Test aliasing detection
    signal = np.random.randn(100)
    defect = detector.detect_aliasing(signal, sample_rate=100, max_freq=60)
    assert defect.is_significant  # 60 > 50 (Nyquist)
    
    # Test repair operators
    regularizer = TikhonovRegularizer()
    assert regularizer.can_repair(Defect(DefectType.ILL_CONDITIONING, Lens.SQUARE))
    
    # Test commutator budget
    budget = CommutatorBudget()
    assert budget.is_within_budget()
    budget.add_defect(Lens.SQUARE, 1e-7, "test")
    assert budget.is_within_budget()
    budget.add_defect(Lens.SQUARE, 1.0, "overflow")
    assert not budget.is_within_budget()
    
    return True


if __name__ == "__main__":
    print("Validating Anti-Symmetry Framework...")
    assert validate_antisymmetry()
    print("✓ Anti-Symmetry Framework validated")
    
    # Demo
    print("\n=== Defect Detection Demo ===")
    detector = DefectDetector()
    
    # Create a singular matrix
    singular = np.array([[1, 2, 3], [2, 4, 6], [1, 2, 3]], dtype=float)
    kernel_defect = detector.detect_kernel_defect(singular)
    print(f"Kernel defect: magnitude={kernel_defect.magnitude}, severity={kernel_defect.severity}")
    
    # Create aliasing scenario
    alias_defect = detector.detect_aliasing(np.zeros(100), sample_rate=100, max_freq=80)
    print(f"Aliasing defect: magnitude={alias_defect.magnitude:.2f}, severity={alias_defect.severity}")
    
    print(f"\nDetector summary: {detector.summary()}")
