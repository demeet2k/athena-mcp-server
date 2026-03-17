"""
ATHENA OS - Defect Operators and Error Decomposition
====================================================
The "Anti" Toolbox - tools for analyzing failures and defects.

From HYBRID_HOLO_LENSE.docx Appendix O:
Defect Operators and Error Decomposition

DEFECT TYPES:
    ■ Square (Discrete):
        - Sampling kernel defects
        - Reconstruction nullspace
        - Rank deficiencies
        - Commutator path defects
    
    ❀ Flower (Spectral):
        - Aliasing operator
        - Leakage operator
        - Spectral truncation
        - Mode mixing
    
    ☁ Cloud (Stochastic):
        - Bias operator
        - Variance operator
        - Entropy inflation
        - Divergence maps
    
    ✶ Fractal (Multiscale):
        - Scale-dependent defects
        - Defect renormalization
        - Snap failure modes
        - Holonomy persistence

ANTI-AETHER PRINCIPLE:
    Anti-Aether represents impossible moves / ill-posed operations.
    Defect operators detect and characterize these boundaries.
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
import math


# =============================================================================
# DEFECT TYPES
# =============================================================================

class DefectDomain(Enum):
    """The four domains for defect analysis."""
    SQUARE = "square"      # Discrete/combinatorial
    FLOWER = "flower"      # Spectral/continuous
    CLOUD = "cloud"        # Stochastic/probabilistic
    FRACTAL = "fractal"    # Multiscale/recursive


class DefectSeverity(Enum):
    """Severity levels for defects."""
    INFO = 0       # Informational only
    WARNING = 1    # May cause issues
    ERROR = 2      # Will cause issues
    CRITICAL = 3   # System failure


# =============================================================================
# DEFECT ATOM
# =============================================================================

@dataclass
class DefectAtom:
    """
    A single defect or error atom.
    
    Atoms are the basic building blocks of defect analysis.
    """
    
    id: str
    domain: DefectDomain
    name: str
    description: str
    severity: DefectSeverity = DefectSeverity.WARNING
    
    # Quantification
    magnitude: float = 0.0
    threshold: float = float('inf')
    
    # Location
    location: str = ""
    
    # Remediation
    remediation: str = ""
    
    def is_above_threshold(self) -> bool:
        """Check if defect exceeds threshold."""
        return self.magnitude > self.threshold
    
    def severity_score(self) -> int:
        """Get numeric severity score."""
        return self.severity.value
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "domain": self.domain.value,
            "name": self.name,
            "severity": self.severity.name,
            "magnitude": self.magnitude,
            "threshold": self.threshold,
            "above_threshold": self.is_above_threshold(),
            "location": self.location,
        }


# =============================================================================
# SQUARE DEFECTS (DISCRETE)
# =============================================================================

@dataclass
class SamplingDefect(DefectAtom):
    """Sampling kernel defect - missing or corrupted samples."""
    
    missing_samples: int = 0
    total_samples: int = 0
    
    def __post_init__(self):
        self.domain = DefectDomain.SQUARE
        self.name = "Sampling Defect"
        if self.total_samples > 0:
            self.magnitude = self.missing_samples / self.total_samples


@dataclass
class RankDefect(DefectAtom):
    """Rank deficiency in a matrix or linear system."""
    
    expected_rank: int = 0
    actual_rank: int = 0
    
    def __post_init__(self):
        self.domain = DefectDomain.SQUARE
        self.name = "Rank Defect"
        if self.expected_rank > 0:
            self.magnitude = (self.expected_rank - self.actual_rank) / self.expected_rank


@dataclass
class CommutatorDefect(DefectAtom):
    """Commutator/path defect - operations don't commute as expected."""
    
    path_a_result: Any = None
    path_b_result: Any = None
    difference: float = 0.0
    
    def __post_init__(self):
        self.domain = DefectDomain.SQUARE
        self.name = "Commutator Defect"
        self.magnitude = self.difference


# =============================================================================
# FLOWER DEFECTS (SPECTRAL)
# =============================================================================

@dataclass
class AliasingDefect(DefectAtom):
    """Aliasing due to undersampling in frequency domain."""
    
    nyquist_frequency: float = 0.0
    max_signal_frequency: float = 0.0
    
    def __post_init__(self):
        self.domain = DefectDomain.FLOWER
        self.name = "Aliasing Defect"
        if self.nyquist_frequency > 0:
            ratio = self.max_signal_frequency / self.nyquist_frequency
            self.magnitude = max(0, ratio - 1)


@dataclass
class LeakageDefect(DefectAtom):
    """Spectral leakage due to windowing/truncation."""
    
    main_lobe_energy: float = 0.0
    side_lobe_energy: float = 0.0
    
    def __post_init__(self):
        self.domain = DefectDomain.FLOWER
        self.name = "Leakage Defect"
        total = self.main_lobe_energy + self.side_lobe_energy
        if total > 0:
            self.magnitude = self.side_lobe_energy / total


@dataclass
class ModeMixingDefect(DefectAtom):
    """Mode mixing/confusion in spectral decomposition."""
    
    expected_modes: int = 0
    detected_modes: int = 0
    confusion_matrix: Optional[List[List[float]]] = None
    
    def __post_init__(self):
        self.domain = DefectDomain.FLOWER
        self.name = "Mode Mixing Defect"
        if self.expected_modes > 0:
            self.magnitude = abs(self.detected_modes - self.expected_modes) / self.expected_modes


# =============================================================================
# CLOUD DEFECTS (STOCHASTIC)
# =============================================================================

@dataclass
class BiasDefect(DefectAtom):
    """Systematic bias in estimation."""
    
    expected_value: float = 0.0
    estimated_value: float = 0.0
    
    def __post_init__(self):
        self.domain = DefectDomain.CLOUD
        self.name = "Bias Defect"
        self.magnitude = abs(self.estimated_value - self.expected_value)


@dataclass
class VarianceDefect(DefectAtom):
    """Excessive variance in estimation."""
    
    observed_variance: float = 0.0
    expected_variance: float = 0.0
    
    def __post_init__(self):
        self.domain = DefectDomain.CLOUD
        self.name = "Variance Defect"
        if self.expected_variance > 0:
            self.magnitude = self.observed_variance / self.expected_variance - 1
            self.magnitude = max(0, self.magnitude)


@dataclass
class EntropyDefect(DefectAtom):
    """Entropy inflation - loss of information."""
    
    initial_entropy: float = 0.0
    final_entropy: float = 0.0
    
    def __post_init__(self):
        self.domain = DefectDomain.CLOUD
        self.name = "Entropy Defect"
        if self.initial_entropy > 0:
            self.magnitude = (self.final_entropy - self.initial_entropy) / self.initial_entropy
            self.magnitude = max(0, self.magnitude)


@dataclass
class DivergenceDefect(DefectAtom):
    """Distribution divergence (KL, etc.)."""
    
    divergence_type: str = "KL"
    divergence_value: float = 0.0
    
    def __post_init__(self):
        self.domain = DefectDomain.CLOUD
        self.name = f"{self.divergence_type} Divergence Defect"
        self.magnitude = self.divergence_value


# =============================================================================
# FRACTAL DEFECTS (MULTISCALE)
# =============================================================================

@dataclass
class ScaleDefect(DefectAtom):
    """Scale-dependent defect that varies across levels."""
    
    scale_level: int = 0
    defects_by_scale: Dict[int, float] = field(default_factory=dict)
    
    def __post_init__(self):
        self.domain = DefectDomain.FRACTAL
        self.name = "Scale Defect"
        if self.defects_by_scale:
            self.magnitude = max(self.defects_by_scale.values())


@dataclass
class SnapFailureDefect(DefectAtom):
    """Failure of snap/convergence in iterative process."""
    
    iterations: int = 0
    max_iterations: int = 100
    final_residual: float = float('inf')
    target_residual: float = 1e-6
    
    def __post_init__(self):
        self.domain = DefectDomain.FRACTAL
        self.name = "Snap Failure Defect"
        if self.target_residual > 0:
            self.magnitude = self.final_residual / self.target_residual


@dataclass
class HolonomyDefect(DefectAtom):
    """Holonomy/path-dependence that persists across scales."""
    
    loop_integral: float = 0.0
    expected_value: float = 0.0
    
    def __post_init__(self):
        self.domain = DefectDomain.FRACTAL
        self.name = "Holonomy Defect"
        self.magnitude = abs(self.loop_integral - self.expected_value)


# =============================================================================
# DEFECT OPERATOR
# =============================================================================

@dataclass
class DefectOperator:
    """
    An operator that detects and quantifies defects.
    
    Defect operators are the tools for finding what's wrong.
    """
    
    name: str
    domain: DefectDomain
    description: str
    
    # Detection function
    detect_fn: Optional[Callable[[Any], List[DefectAtom]]] = None
    
    def detect(self, target: Any) -> List[DefectAtom]:
        """Run defect detection on target."""
        if self.detect_fn:
            return self.detect_fn(target)
        return []


# =============================================================================
# DEFECT ANALYZER
# =============================================================================

@dataclass
class DefectAnalyzer:
    """
    Comprehensive defect analysis system.
    
    Coordinates multiple defect operators across domains.
    """
    
    operators: Dict[str, DefectOperator] = field(default_factory=dict)
    detected_defects: List[DefectAtom] = field(default_factory=list)
    
    def add_operator(self, operator: DefectOperator) -> None:
        """Add a defect operator."""
        self.operators[operator.name] = operator
    
    def analyze(self, target: Any, 
               domains: Optional[List[DefectDomain]] = None) -> List[DefectAtom]:
        """
        Run defect analysis on target.
        
        Args:
            target: Object to analyze
            domains: Specific domains to check (all if None)
        """
        self.detected_defects = []
        
        for name, op in self.operators.items():
            if domains is None or op.domain in domains:
                defects = op.detect(target)
                self.detected_defects.extend(defects)
        
        return self.detected_defects
    
    def get_defects_by_domain(self, domain: DefectDomain) -> List[DefectAtom]:
        """Get defects for a specific domain."""
        return [d for d in self.detected_defects if d.domain == domain]
    
    def get_critical_defects(self) -> List[DefectAtom]:
        """Get critical severity defects."""
        return [d for d in self.detected_defects 
                if d.severity == DefectSeverity.CRITICAL]
    
    def get_defects_above_threshold(self) -> List[DefectAtom]:
        """Get defects above their thresholds."""
        return [d for d in self.detected_defects if d.is_above_threshold()]
    
    def max_severity(self) -> DefectSeverity:
        """Get maximum severity among detected defects."""
        if not self.detected_defects:
            return DefectSeverity.INFO
        return max(d.severity for d in self.detected_defects)
    
    def summary(self) -> Dict[str, Any]:
        """Get analysis summary."""
        domain_counts = {d.value: 0 for d in DefectDomain}
        severity_counts = {s.name: 0 for s in DefectSeverity}
        
        for defect in self.detected_defects:
            domain_counts[defect.domain.value] += 1
            severity_counts[defect.severity.name] += 1
        
        return {
            "total_defects": len(self.detected_defects),
            "by_domain": domain_counts,
            "by_severity": severity_counts,
            "critical_count": len(self.get_critical_defects()),
            "above_threshold": len(self.get_defects_above_threshold()),
            "max_severity": self.max_severity().name,
        }


# =============================================================================
# ERROR DECOMPOSITION
# =============================================================================

@dataclass
class ErrorComponent:
    """A component of total error."""
    
    name: str
    magnitude: float
    source: str
    reducible: bool = True
    
    def contribution(self, total: float) -> float:
        """Get fractional contribution to total error."""
        if total > 0:
            return self.magnitude / total
        return 0.0


@dataclass
class ErrorDecomposition:
    """
    Decomposition of total error into components.
    
    Error = Bias² + Variance + Noise + Structural
    """
    
    components: List[ErrorComponent] = field(default_factory=list)
    
    def add_component(self, name: str, magnitude: float, 
                     source: str, reducible: bool = True) -> None:
        """Add an error component."""
        self.components.append(ErrorComponent(
            name=name,
            magnitude=magnitude,
            source=source,
            reducible=reducible
        ))
    
    def total_error(self) -> float:
        """Get total error (sum of components)."""
        return sum(c.magnitude for c in self.components)
    
    def reducible_error(self) -> float:
        """Get reducible error component."""
        return sum(c.magnitude for c in self.components if c.reducible)
    
    def irreducible_error(self) -> float:
        """Get irreducible error component."""
        return sum(c.magnitude for c in self.components if not c.reducible)
    
    def dominant_component(self) -> Optional[ErrorComponent]:
        """Get the largest error component."""
        if not self.components:
            return None
        return max(self.components, key=lambda c: c.magnitude)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        total = self.total_error()
        return {
            "total_error": total,
            "reducible_error": self.reducible_error(),
            "irreducible_error": self.irreducible_error(),
            "components": [
                {
                    "name": c.name,
                    "magnitude": c.magnitude,
                    "contribution": c.contribution(total),
                    "source": c.source,
                    "reducible": c.reducible,
                }
                for c in self.components
            ],
            "dominant": self.dominant_component().name if self.dominant_component() else None,
        }


# =============================================================================
# STANDARD DEFECT OPERATORS
# =============================================================================

def create_standard_operators() -> Dict[str, DefectOperator]:
    """Create standard set of defect operators."""
    
    operators = {}
    
    # Square operators
    operators["sampling"] = DefectOperator(
        name="sampling",
        domain=DefectDomain.SQUARE,
        description="Detect sampling defects"
    )
    
    operators["rank"] = DefectOperator(
        name="rank",
        domain=DefectDomain.SQUARE,
        description="Detect rank deficiencies"
    )
    
    # Flower operators
    operators["aliasing"] = DefectOperator(
        name="aliasing",
        domain=DefectDomain.FLOWER,
        description="Detect aliasing defects"
    )
    
    operators["leakage"] = DefectOperator(
        name="leakage",
        domain=DefectDomain.FLOWER,
        description="Detect spectral leakage"
    )
    
    # Cloud operators
    operators["bias"] = DefectOperator(
        name="bias",
        domain=DefectDomain.CLOUD,
        description="Detect systematic bias"
    )
    
    operators["variance"] = DefectOperator(
        name="variance",
        domain=DefectDomain.CLOUD,
        description="Detect excessive variance"
    )
    
    # Fractal operators
    operators["scale"] = DefectOperator(
        name="scale",
        domain=DefectDomain.FRACTAL,
        description="Detect scale-dependent defects"
    )
    
    operators["snap"] = DefectOperator(
        name="snap",
        domain=DefectDomain.FRACTAL,
        description="Detect snap/convergence failures"
    )
    
    return operators


# =============================================================================
# VALIDATION
# =============================================================================

def validate_defects() -> bool:
    """Validate defects module."""
    
    # Test DefectAtom
    defect = DefectAtom(
        id="d1",
        domain=DefectDomain.SQUARE,
        name="Test Defect",
        description="Test",
        severity=DefectSeverity.WARNING,
        magnitude=0.5,
        threshold=0.3
    )
    assert defect.is_above_threshold()
    assert defect.severity_score() == 1
    
    # Test specific defects
    sampling = SamplingDefect(
        id="s1",
        description="Missing samples",
        missing_samples=5,
        total_samples=100
    )
    assert sampling.magnitude == 0.05
    
    bias = BiasDefect(
        id="b1",
        description="Systematic bias",
        expected_value=10.0,
        estimated_value=12.0
    )
    assert bias.magnitude == 2.0
    
    # Test DefectAnalyzer
    analyzer = DefectAnalyzer()
    for name, op in create_standard_operators().items():
        analyzer.add_operator(op)
    
    assert len(analyzer.operators) == 8
    
    # Add some test defects
    analyzer.detected_defects = [
        DefectAtom("d1", DefectDomain.SQUARE, "Test1", "", 
                  DefectSeverity.WARNING, 0.1),
        DefectAtom("d2", DefectDomain.FLOWER, "Test2", "",
                  DefectSeverity.ERROR, 0.5),
        DefectAtom("d3", DefectDomain.CLOUD, "Test3", "",
                  DefectSeverity.CRITICAL, 0.9),
    ]
    
    assert len(analyzer.get_critical_defects()) == 1
    assert analyzer.max_severity() == DefectSeverity.CRITICAL
    
    # Test ErrorDecomposition
    decomp = ErrorDecomposition()
    decomp.add_component("bias", 0.1, "model", True)
    decomp.add_component("variance", 0.2, "data", True)
    decomp.add_component("noise", 0.05, "measurement", False)
    
    assert abs(decomp.total_error() - 0.35) < 1e-10
    assert abs(decomp.reducible_error() - 0.30) < 1e-10
    assert abs(decomp.irreducible_error() - 0.05) < 1e-10
    assert decomp.dominant_component().name == "variance"
    
    return True


if __name__ == "__main__":
    print("Validating Defects Module...")
    assert validate_defects()
    print("✓ Defects Module validated")
    
    # Demo
    print("\n=== Defect Analysis Demo ===")
    
    print("\nDefect Types by Domain:")
    for domain in DefectDomain:
        print(f"  {domain.value}: ", end="")
        if domain == DefectDomain.SQUARE:
            print("Sampling, Rank, Commutator")
        elif domain == DefectDomain.FLOWER:
            print("Aliasing, Leakage, Mode Mixing")
        elif domain == DefectDomain.CLOUD:
            print("Bias, Variance, Entropy, Divergence")
        elif domain == DefectDomain.FRACTAL:
            print("Scale, Snap Failure, Holonomy")
    
    print("\nError Decomposition Example:")
    decomp = ErrorDecomposition()
    decomp.add_component("bias_squared", 0.04, "model misspecification", True)
    decomp.add_component("variance", 0.15, "limited data", True)
    decomp.add_component("approximation", 0.08, "discretization", True)
    decomp.add_component("noise", 0.03, "measurement", False)
    
    print(f"  Total error: {decomp.total_error():.2f}")
    print(f"  Reducible: {decomp.reducible_error():.2f}")
    print(f"  Irreducible: {decomp.irreducible_error():.2f}")
    print(f"  Dominant: {decomp.dominant_component().name}")
    
    print("\nContributions:")
    total = decomp.total_error()
    for comp in decomp.components:
        pct = comp.contribution(total) * 100
        print(f"    {comp.name}: {pct:.1f}%")
