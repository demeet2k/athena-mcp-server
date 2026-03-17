"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ██████╗  █████╗ ███╗   ██╗██████╗                                 ║
║  ██╔════╝ ██╔══██╗██╔══██╗████╗  ██║██╔══██╗                                ║
║  ██║  ███╗██████╔╝███████║██╔██╗ ██║██║  ██║                                ║
║  ██║   ██║██╔══██╗██╔══██║██║╚██╗██║██║  ██║                                ║
║  ╚██████╔╝██║  ██║██║  ██║██║ ╚████║██████╔╝                                ║
║   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝                                 ║
║                                                                              ║
║  ██╗   ██╗███╗   ██╗██╗███████╗██╗███████╗██████╗                           ║
║  ██║   ██║████╗  ██║██║██╔════╝██║██╔════╝██╔══██╗                          ║
║  ██║   ██║██╔██╗ ██║██║█████╗  ██║█████╗  ██║  ██║                          ║
║  ██║   ██║██║╚██╗██║██║██╔══╝  ██║██╔══╝  ██║  ██║                          ║
║  ╚██████╔╝██║ ╚████║██║██║     ██║███████╗██████╔╝                          ║
║   ╚═════╝ ╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝╚══════╝╚═════╝                           ║
║                                                                              ║
║             THE GRAND UNIFIED MATHEMATICAL FRAMEWORK                         ║
║                                                                              ║
║                        ATLASFORGE v4.0.0-FINAL                               ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  "From the Gateway, four paths emerge—                                       ║
║   Hierarchical depths, Stochastic tides,                                     ║
║   Continuous flows, and Discrete bridges—                                    ║
║   All unified in the Latin Kernel's embrace."                                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

This module provides the MASTER SYNTHESIS of the AtlasForge framework,
connecting all mathematical domains through the four-pole structure:

                              ┌─────────┐
                              │ GATEWAY │
                              │ SL(2,ℝ) │
                              └────┬────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
           ▼                       ▼                       ▼
    ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
    │   Ψ-POLE     │       │   Σ-POLE     │       │   C-POLE     │
    │ Hierarchical │       │  Stochastic  │       │  Continuous  │
    │              │       │              │       │              │
    │ • Wavelets   │       │ • Markov     │       │ • Lie        │
    │ • p-adic     │       │ • Monte Carlo│       │ • Symplectic │
    │ • K-theory   │       │ • Quantum    │       │ • De Rham    │
    │ • Multigrid  │       │ • Entropy    │       │ • Modular    │
    └──────┬───────┘       └──────┬───────┘       └──────┬───────┘
           │                       │                       │
           └───────────────────────┼───────────────────────┘
                                   │
                              ┌────▼────┐
                              │ D-POLE  │
                              │ Discrete│
                              │         │
                              │• Automata│
                              │• Tropical│
                              │• Knot    │
                              │• Latin   │
                              └─────────┘
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable, Union, Set
from enum import Enum, auto
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# FUNDAMENTAL POLE STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════════

class UnifiedPole(Enum):
    """The four fundamental poles of mathematical reality."""
    
    PSI = "Ψ"       # Hierarchical / Recursive / Self-similar
    SIGMA = "Σ"     # Stochastic / Random / Probabilistic
    C = "C"         # Continuous / Smooth / Differential
    D = "D"         # Discrete / Combinatorial / Logical
    
    @property
    def description(self) -> str:
        descriptions = {
            UnifiedPole.PSI: "Hierarchical pole: recursive scaling, wavelets, p-adic, multigrid",
            UnifiedPole.SIGMA: "Stochastic pole: randomness, Monte Carlo, quantum, entropy",
            UnifiedPole.C: "Continuous pole: symmetry, Lie groups, differential geometry, flows",
            UnifiedPole.D: "Discrete pole: logic, automata, tropical, combinatorics"
        }
        return descriptions[self]
    
    @property
    def associated_domains(self) -> List[str]:
        """Mathematical domains primarily associated with this pole."""
        domains = {
            UnifiedPole.PSI: [
                "Wavelet Analysis", "p-adic Numbers", "Algebraic K-Theory",
                "Multigrid Methods", "Renormalization", "Hierarchical Models"
            ],
            UnifiedPole.SIGMA: [
                "Stochastic Processes", "Quantum Information", "Statistical Mechanics",
                "Monte Carlo Methods", "Entropy Theory", "Probabilistic Methods"
            ],
            UnifiedPole.C: [
                "Lie Algebras", "Symplectic Geometry", "De Rham Cohomology",
                "Modular Forms", "Hyperbolic Geometry", "Differential Equations"
            ],
            UnifiedPole.D: [
                "Automata Theory", "Tropical Geometry", "Knot Theory",
                "Latin Squares", "Constraint Satisfaction", "Combinatorics"
            ]
        }
        return domains[self]


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED MATHEMATICAL STATE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class UnifiedPoleWeights:
    """Weights for each pole in the unified state."""
    psi: float = 0.25
    sigma: float = 0.25
    c: float = 0.25
    d: float = 0.25
    
    def __post_init__(self):
        """Normalize weights to sum to 1."""
        total = self.psi + self.sigma + self.c + self.d
        if total > 0:
            self.psi /= total
            self.sigma /= total
            self.c /= total
            self.d /= total
    
    def as_vector(self) -> NDArray[np.float64]:
        """Return as numpy vector."""
        return np.array([self.psi, self.sigma, self.c, self.d])
    
    def dominant(self) -> UnifiedPole:
        """Return the dominant pole."""
        weights = [self.psi, self.sigma, self.c, self.d]
        poles = [UnifiedPole.PSI, UnifiedPole.SIGMA, UnifiedPole.C, UnifiedPole.D]
        return poles[np.argmax(weights)]
    
    def entropy(self) -> float:
        """Shannon entropy of pole distribution."""
        w = self.as_vector()
        w = w[w > 0]  # Remove zeros
        return -np.sum(w * np.log(w))
    
    @classmethod
    def pure(cls, pole: UnifiedPole) -> 'UnifiedPoleWeights':
        """Create pure state for single pole."""
        if pole == UnifiedPole.PSI:
            return cls(1.0, 0.0, 0.0, 0.0)
        elif pole == UnifiedPole.SIGMA:
            return cls(0.0, 1.0, 0.0, 0.0)
        elif pole == UnifiedPole.C:
            return cls(0.0, 0.0, 1.0, 0.0)
        else:
            return cls(0.0, 0.0, 0.0, 1.0)
    
    @classmethod
    def uniform(cls) -> 'UnifiedPoleWeights':
        """Uniform distribution over poles."""
        return cls(0.25, 0.25, 0.25, 0.25)


@dataclass
class GrandUnifiedState:
    """
    The Grand Unified State of the AtlasForge framework.
    
    S = (T, α, A, weights, components)
    
    where:
    - T ∈ (-1, 1): Gateway parameter
    - α = arctanh(T): Rapidity
    - A = 1/(1-T²): Discriminant
    - weights: Pole weights
    - components: Domain-specific data
    """
    T: float  # Gateway parameter
    weights: UnifiedPoleWeights = field(default_factory=UnifiedPoleWeights)
    psi_data: Optional[Any] = None
    sigma_data: Optional[Any] = None
    c_data: Optional[Any] = None
    d_data: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if abs(self.T) >= 1.0:
            raise ValueError("|T| must be strictly less than 1")
    
    # ─────────────────────────────────────────────────────────────────────────
    # Gateway Properties
    # ─────────────────────────────────────────────────────────────────────────
    
    @property
    def rapidity(self) -> float:
        """α = arctanh(T)."""
        return np.arctanh(self.T)
    
    @property
    def discriminant(self) -> float:
        """A = 1/(1-T²)."""
        return 1.0 / (1.0 - self.T**2)
    
    @property
    def gateway_matrix(self) -> NDArray[np.float64]:
        """Gateway matrix M = [[1,T],[T,1]] / √(1-T²)."""
        scale = 1.0 / np.sqrt(1.0 - self.T**2)
        return scale * np.array([[1, self.T], [self.T, 1]])
    
    # ─────────────────────────────────────────────────────────────────────────
    # Pole Access
    # ─────────────────────────────────────────────────────────────────────────
    
    def pole_weight(self, pole: UnifiedPole) -> float:
        """Get weight for specific pole."""
        if pole == UnifiedPole.PSI:
            return self.weights.psi
        elif pole == UnifiedPole.SIGMA:
            return self.weights.sigma
        elif pole == UnifiedPole.C:
            return self.weights.c
        else:
            return self.weights.d
    
    def pole_data(self, pole: UnifiedPole) -> Any:
        """Get data for specific pole."""
        if pole == UnifiedPole.PSI:
            return self.psi_data
        elif pole == UnifiedPole.SIGMA:
            return self.sigma_data
        elif pole == UnifiedPole.C:
            return self.c_data
        else:
            return self.d_data
    
    # ─────────────────────────────────────────────────────────────────────────
    # Transformations
    # ─────────────────────────────────────────────────────────────────────────
    
    def evolve(self, delta_alpha: float) -> 'GrandUnifiedState':
        """Evolve state by rapidity increment."""
        new_alpha = self.rapidity + delta_alpha
        new_T = np.tanh(new_alpha)
        return GrandUnifiedState(new_T, self.weights, self.psi_data,
                                 self.sigma_data, self.c_data, self.d_data,
                                 self.metadata.copy())
    
    def reflect(self) -> 'GrandUnifiedState':
        """Gateway reflection T → -T."""
        return GrandUnifiedState(-self.T, self.weights, self.psi_data,
                                 self.sigma_data, self.c_data, self.d_data,
                                 self.metadata.copy())
    
    def reweight(self, new_weights: UnifiedPoleWeights) -> 'GrandUnifiedState':
        """Change pole weights."""
        return GrandUnifiedState(self.T, new_weights, self.psi_data,
                                 self.sigma_data, self.c_data, self.d_data,
                                 self.metadata.copy())
    
    # ─────────────────────────────────────────────────────────────────────────
    # Factory Methods
    # ─────────────────────────────────────────────────────────────────────────
    
    @classmethod
    def identity(cls) -> 'GrandUnifiedState':
        """Identity state at T=0."""
        return cls(0.0)
    
    @classmethod
    def golden(cls) -> 'GrandUnifiedState':
        """State at golden ratio T = 1/φ."""
        phi = (1 + np.sqrt(5)) / 2
        return cls(1.0 / phi)
    
    @classmethod
    def from_rapidity(cls, alpha: float, **kwargs) -> 'GrandUnifiedState':
        """Create from rapidity."""
        return cls(np.tanh(alpha), **kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# MATHEMATICAL DOMAIN REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

class MathDomainType(Enum):
    """Classification of mathematical domains."""
    
    # Gateway/Core
    GATEWAY = "Gateway Algebra"
    METALLIC = "Metallic Sequences"
    LATIN = "Latin Kernels"
    
    # Number Theory
    MODULAR = "Modular Forms"
    ELLIPTIC = "Elliptic Curves"
    CONTINUED_FRAC = "Continued Fractions"
    QUADRATIC = "Quadratic Fields"
    ZETA = "L-functions & Zeta"
    
    # Algebra
    LIE = "Lie Algebras"
    K_THEORY = "Algebraic K-Theory"
    GALOIS = "Galois Theory"
    REPRESENTATION = "Representation Theory"
    
    # Geometry
    HYPERBOLIC = "Hyperbolic Geometry"
    TROPICAL = "Tropical Geometry"
    SPECTRAL_GEOM = "Spectral Geometry"
    SYMPLECTIC = "Symplectic Geometry"
    
    # Topology
    KNOT = "Knot Theory"
    HOMOLOGY = "Homological Algebra"
    SHEAF = "Sheaf Cohomology"
    DERIVED = "Derived Categories"
    
    # Analysis
    WAVELET = "Wavelet Analysis"
    PADIC = "p-adic Analysis"
    DYNAMICS = "Dynamical Systems"
    
    # Probability/Physics
    STOCHASTIC = "Stochastic Processes"
    QUANTUM = "Quantum Information"
    TENSOR = "Tensor Networks"
    ENTROPY = "Entropy Theory"
    
    # Computation
    AUTOMATA = "Automata Theory"
    CONSTRAINT = "Constraint Satisfaction"


@dataclass
class DomainPoleMapping:
    """Mapping between domains and poles."""
    
    @staticmethod
    def primary_pole(domain: MathDomainType) -> UnifiedPole:
        """Get primary pole for domain."""
        psi_domains = {
            MathDomainType.WAVELET, MathDomainType.PADIC,
            MathDomainType.K_THEORY, MathDomainType.DERIVED
        }
        sigma_domains = {
            MathDomainType.STOCHASTIC, MathDomainType.QUANTUM,
            MathDomainType.ENTROPY, MathDomainType.TENSOR
        }
        c_domains = {
            MathDomainType.LIE, MathDomainType.SYMPLECTIC,
            MathDomainType.MODULAR, MathDomainType.HYPERBOLIC,
            MathDomainType.DYNAMICS, MathDomainType.SHEAF
        }
        d_domains = {
            MathDomainType.AUTOMATA, MathDomainType.TROPICAL,
            MathDomainType.KNOT, MathDomainType.LATIN,
            MathDomainType.CONSTRAINT
        }
        
        if domain in psi_domains:
            return UnifiedPole.PSI
        elif domain in sigma_domains:
            return UnifiedPole.SIGMA
        elif domain in c_domains:
            return UnifiedPole.C
        elif domain in d_domains:
            return UnifiedPole.D
        else:
            return UnifiedPole.C  # Default


# ═══════════════════════════════════════════════════════════════════════════════
# MATHEMATICAL BRIDGE NETWORK
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MathBridge:
    """Bridge between two mathematical domains."""
    source: MathDomainType
    target: MathDomainType
    name: str
    description: str
    bidirectional: bool = True
    
    def __hash__(self):
        return hash((self.source, self.target, self.name))


@dataclass
class BridgeNetwork:
    """
    Network of mathematical bridges connecting domains.
    """
    bridges: List[MathBridge] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize with fundamental bridges."""
        self._add_fundamental_bridges()
    
    def _add_fundamental_bridges(self):
        """Add the core mathematical bridges."""
        fundamental = [
            # Gateway connections
            MathBridge(MathDomainType.GATEWAY, MathDomainType.HYPERBOLIC,
                      "Poincaré", "SL(2,ℝ) acts on hyperbolic plane"),
            MathBridge(MathDomainType.GATEWAY, MathDomainType.MODULAR,
                      "Modular", "SL(2,ℤ) action on modular forms"),
            MathBridge(MathDomainType.GATEWAY, MathDomainType.CONTINUED_FRAC,
                      "CF", "Continued fractions via matrix products"),
            
            # Number theory
            MathBridge(MathDomainType.MODULAR, MathDomainType.ELLIPTIC,
                      "Modularity", "Modular forms ↔ Elliptic curves"),
            MathBridge(MathDomainType.ELLIPTIC, MathDomainType.ZETA,
                      "L-function", "Hasse-Weil L-function"),
            MathBridge(MathDomainType.QUADRATIC, MathDomainType.CONTINUED_FRAC,
                      "Pell", "Pell equation via CF"),
            
            # Algebra
            MathBridge(MathDomainType.LIE, MathDomainType.REPRESENTATION,
                      "Rep", "Lie algebra representations"),
            MathBridge(MathDomainType.K_THEORY, MathDomainType.DERIVED,
                      "Grothendieck", "K-theory from derived categories"),
            
            # Geometry
            MathBridge(MathDomainType.SYMPLECTIC, MathDomainType.DYNAMICS,
                      "Hamiltonian", "Hamiltonian mechanics"),
            MathBridge(MathDomainType.SHEAF, MathDomainType.DERIVED,
                      "Derived", "Derived category of sheaves"),
            
            # Topology
            MathBridge(MathDomainType.KNOT, MathDomainType.QUANTUM,
                      "Jones", "Quantum invariants of knots"),
            MathBridge(MathDomainType.HOMOLOGY, MathDomainType.DERIVED,
                      "Derived", "Derived functors"),
            
            # Analysis
            MathBridge(MathDomainType.WAVELET, MathDomainType.SPECTRAL_GEOM,
                      "Spectral", "Multiresolution spectral analysis"),
            MathBridge(MathDomainType.PADIC, MathDomainType.ZETA,
                      "p-adic L", "p-adic L-functions"),
            
            # Probability
            MathBridge(MathDomainType.STOCHASTIC, MathDomainType.QUANTUM,
                      "Quantum Prob", "Quantum probability"),
            MathBridge(MathDomainType.ENTROPY, MathDomainType.QUANTUM,
                      "von Neumann", "von Neumann entropy"),
            
            # Computation
            MathBridge(MathDomainType.AUTOMATA, MathDomainType.TROPICAL,
                      "Min-plus", "Automata ↔ Tropical semiring"),
        ]
        self.bridges.extend(fundamental)
    
    def connected_domains(self, domain: MathDomainType) -> Set[MathDomainType]:
        """Get domains directly connected to given domain."""
        connected = set()
        for bridge in self.bridges:
            if bridge.source == domain:
                connected.add(bridge.target)
            if bridge.bidirectional and bridge.target == domain:
                connected.add(bridge.source)
        return connected
    
    def find_path(self, source: MathDomainType, 
                  target: MathDomainType) -> List[MathBridge]:
        """Find bridge path between domains (BFS)."""
        if source == target:
            return []
        
        from collections import deque
        visited = {source}
        queue = deque([(source, [])])
        
        while queue:
            current, path = queue.popleft()
            
            for bridge in self.bridges:
                next_domain = None
                if bridge.source == current:
                    next_domain = bridge.target
                elif bridge.bidirectional and bridge.target == current:
                    next_domain = bridge.source
                
                if next_domain and next_domain not in visited:
                    new_path = path + [bridge]
                    if next_domain == target:
                        return new_path
                    visited.add(next_domain)
                    queue.append((next_domain, new_path))
        
        return []  # No path found


# ═══════════════════════════════════════════════════════════════════════════════
# GRAND UNIFIED SOLVER
# ═══════════════════════════════════════════════════════════════════════════════

class SolutionStrategy(Enum):
    """Solution strategy based on pole dominance."""
    HIERARCHICAL = auto()  # Ψ: Recursive decomposition
    STOCHASTIC = auto()    # Σ: Monte Carlo, MCMC
    GRADIENT = auto()      # C: Continuous optimization
    CONSTRAINT = auto()    # D: SAT, Integer programming
    HYBRID = auto()        # Adaptive pole switching


@dataclass
class GrandUnifiedSolver:
    """
    The Grand Unified Solver for all mathematical problems.
    
    Routes problems to appropriate algorithms based on pole analysis.
    """
    default_strategy: SolutionStrategy = SolutionStrategy.HYBRID
    bridge_network: BridgeNetwork = field(default_factory=BridgeNetwork)
    
    def analyze_state(self, state: GrandUnifiedState) -> SolutionStrategy:
        """Determine optimal strategy from state."""
        dominant = state.weights.dominant()
        
        strategy_map = {
            UnifiedPole.PSI: SolutionStrategy.HIERARCHICAL,
            UnifiedPole.SIGMA: SolutionStrategy.STOCHASTIC,
            UnifiedPole.C: SolutionStrategy.GRADIENT,
            UnifiedPole.D: SolutionStrategy.CONSTRAINT
        }
        
        return strategy_map.get(dominant, self.default_strategy)
    
    def recommend_domain(self, state: GrandUnifiedState) -> List[MathDomainType]:
        """Recommend mathematical domains for given state."""
        dominant = state.weights.dominant()
        T = abs(state.T)
        
        recommendations = []
        
        # Based on T value
        if T > 0.9:
            recommendations.append(MathDomainType.HYPERBOLIC)
        if T < 0.1:
            recommendations.append(MathDomainType.MODULAR)
        
        # Based on dominant pole
        if dominant == UnifiedPole.PSI:
            recommendations.extend([
                MathDomainType.WAVELET,
                MathDomainType.PADIC,
                MathDomainType.K_THEORY
            ])
        elif dominant == UnifiedPole.SIGMA:
            recommendations.extend([
                MathDomainType.STOCHASTIC,
                MathDomainType.QUANTUM,
                MathDomainType.ENTROPY
            ])
        elif dominant == UnifiedPole.C:
            recommendations.extend([
                MathDomainType.LIE,
                MathDomainType.SYMPLECTIC,
                MathDomainType.MODULAR
            ])
        else:  # D
            recommendations.extend([
                MathDomainType.AUTOMATA,
                MathDomainType.TROPICAL,
                MathDomainType.LATIN
            ])
        
        return list(set(recommendations))
    
    def solve(self, problem: Any, state: GrandUnifiedState) -> Dict[str, Any]:
        """Unified problem-solving interface."""
        strategy = self.analyze_state(state)
        domains = self.recommend_domain(state)
        
        return {
            "strategy": strategy.name,
            "recommended_domains": [d.value for d in domains],
            "state_T": state.T,
            "state_rapidity": state.rapidity,
            "dominant_pole": state.weights.dominant().value,
            "pole_weights": state.weights.as_vector().tolist()
        }


# ═══════════════════════════════════════════════════════════════════════════════
# FRAMEWORK SYNTHESIS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FrameworkSynthesis:
    """
    Complete synthesis of the AtlasForge framework.
    """
    version: str = "4.0.0-final"
    codename: str = "Universal Harmonic Framework"
    
    @property
    def poles(self) -> List[UnifiedPole]:
        """The four fundamental poles."""
        return list(UnifiedPole)
    
    @property
    def domains(self) -> List[MathDomainType]:
        """All mathematical domains."""
        return list(MathDomainType)
    
    def describe_pole(self, pole: UnifiedPole) -> str:
        """Get full description of a pole."""
        return pole.description
    
    def pole_domains(self, pole: UnifiedPole) -> List[str]:
        """Get domains associated with pole."""
        return pole.associated_domains
    
    def summary(self) -> str:
        """Framework summary."""
        return f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     AtlasForge {self.version}                                  ║
║                 "{self.codename}"                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  THE FOUR POLES:                                                             ║
║  ──────────────                                                              ║
║  Ψ (PSI)   - Hierarchical: wavelets, p-adic, K-theory, multigrid            ║
║  Σ (SIGMA) - Stochastic: Markov, Monte Carlo, quantum, entropy              ║
║  C         - Continuous: Lie groups, symplectic, de Rham, modular           ║
║  D         - Discrete: automata, tropical, knot theory, Latin               ║
║                                                                              ║
║  CORE FOUNDATION:                                                            ║
║  ────────────────                                                            ║
║  • Gateway Algebra: SL(2,ℝ) hyperbolic action, T ∈ (-1,1)                   ║
║  • Latin Kernel: Orthogonality invariants, constraint encoding              ║
║  • Metallic Sequences: φ, δ_n continued fraction limits                     ║
║                                                                              ║
║  MATHEMATICAL BRIDGES:                                                       ║
║  ─────────────────────                                                       ║
║  Gateway ←→ Hyperbolic ←→ Modular ←→ Elliptic ←→ Zeta                      ║
║  Lie ←→ Representation ←→ K-Theory ←→ Derived ←→ Sheaf                     ║
║  Stochastic ←→ Quantum ←→ Entropy ←→ Tensor Networks                       ║
║  Automata ←→ Tropical ←→ Knot ←→ Constraint                                ║
║                                                                              ║
║  UNIFIED STATE:                                                              ║
║  ──────────────                                                              ║
║  S = (T, Ψ, Σ, C, D, weights)                                               ║
║  where T ∈ (-1,1), α = arctanh(T), A = 1/(1-T²)                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def grand_state(T: float, **kwargs) -> GrandUnifiedState:
    """Create grand unified state."""
    return GrandUnifiedState(T, **kwargs)


def pole_weights(psi: float = 0.25, sigma: float = 0.25,
                c: float = 0.25, d: float = 0.25) -> UnifiedPoleWeights:
    """Create pole weights."""
    return UnifiedPoleWeights(psi, sigma, c, d)


def pure_pole_state(pole: UnifiedPole, T: float = 0.0) -> GrandUnifiedState:
    """Create state dominated by single pole."""
    return GrandUnifiedState(T, UnifiedPoleWeights.pure(pole))


def bridge_network() -> BridgeNetwork:
    """Get the mathematical bridge network."""
    return BridgeNetwork()


def framework_synthesis() -> FrameworkSynthesis:
    """Get framework synthesis."""
    return FrameworkSynthesis()


def grand_solve(problem: Any, T: float = 0.0,
               weights: Optional[UnifiedPoleWeights] = None) -> Dict[str, Any]:
    """Unified solve interface."""
    if weights is None:
        weights = UnifiedPoleWeights()
    state = GrandUnifiedState(T, weights)
    solver = GrandUnifiedSolver()
    return solver.solve(problem, state)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Poles
    'UnifiedPole',
    'UnifiedPoleWeights',
    
    # State
    'GrandUnifiedState',
    
    # Domains
    'MathDomainType',
    'DomainPoleMapping',
    
    # Bridges
    'MathBridge',
    'BridgeNetwork',
    
    # Solver
    'SolutionStrategy',
    'GrandUnifiedSolver',
    
    # Synthesis
    'FrameworkSynthesis',
    
    # Functions
    'grand_state',
    'pole_weights',
    'pure_pole_state',
    'bridge_network',
    'framework_synthesis',
    'grand_solve',
]
