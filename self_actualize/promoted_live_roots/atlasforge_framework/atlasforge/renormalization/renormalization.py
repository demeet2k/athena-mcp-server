"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ATLAS FORGE - Renormalization Group (Ψ)                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

Ψ acts on LAWS, not just states.

Renormalization Group Flow:
    H_ℓ → H_{ℓ+1} = R(H_ℓ)
    
where H is an effective Hamiltonian/law at scale ℓ.

Key Concepts:
- Block averaging: aggregate microscopic degrees of freedom
- Decimation: keep every k-th degree of freedom
- Coarse-graining: map fine → coarse representations
- Fixed points: scale-invariant laws

RG Transformation Properties:
- Preserves universality class
- Reveals relevant/irrelevant operators
- Fixed points correspond to critical phenomena

Noise-to-Law Transition:
    micro-noise →[Σ]→ mixed ensembles →[Ψ]→ effective laws
    
This is the "holographic encoding" where coarse laws encode
astronomically large micro-trajectory spaces.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum
import math

import numpy as np
from numpy.typing import NDArray


class RGTransformType(Enum):
    """Types of RG transformations."""
    BLOCK_AVERAGE = "block_average"     # Average over blocks
    DECIMATION = "decimation"           # Keep every k-th
    MAJORITY_RULE = "majority_rule"     # Discrete block spin
    MOMENTUM_SHELL = "momentum_shell"   # Integrate out high-k modes
    VARIATIONAL = "variational"         # Variational RG


@dataclass
class EffectiveLaw:
    """
    Effective law (Hamiltonian) at a given scale.
    
    H(x; θ) where θ are coupling constants.
    """
    scale: int                          # Scale level ℓ
    couplings: NDArray[np.float64]      # Coupling constants θ
    energy_func: Optional[Callable] = None  # H(x; θ)
    dimension: int = 0                  # Effective dimension at this scale
    
    def energy(self, state: NDArray) -> float:
        """Compute energy H(x; θ)."""
        if self.energy_func:
            return self.energy_func(state, self.couplings)
        # Default: quadratic form
        return 0.5 * state @ np.diag(self.couplings[:len(state)]) @ state
    
    def gibbs_weight(self, state: NDArray, temperature: float = 1.0) -> float:
        """Compute Gibbs weight exp(-H/T)."""
        return np.exp(-self.energy(state) / temperature)


@dataclass
class RGFlow:
    """
    Record of RG flow through scale hierarchy.
    """
    scales: List[int] = field(default_factory=list)
    laws: List[EffectiveLaw] = field(default_factory=list)
    beta_functions: List[NDArray] = field(default_factory=list)
    
    def add_step(self, law: EffectiveLaw, beta: Optional[NDArray] = None):
        self.scales.append(law.scale)
        self.laws.append(law)
        if beta is not None:
            self.beta_functions.append(beta)
    
    @property
    def n_steps(self) -> int:
        return len(self.laws)
    
    def coupling_trajectory(self) -> NDArray:
        """Return couplings at each scale."""
        if not self.laws:
            return np.array([])
        return np.array([law.couplings for law in self.laws])
    
    def is_approaching_fixed_point(self, tol: float = 1e-6) -> bool:
        """Check if couplings are converging."""
        if len(self.laws) < 2:
            return False
        
        last = self.laws[-1].couplings
        prev = self.laws[-2].couplings
        
        if len(last) != len(prev):
            return False
        
        return np.linalg.norm(last - prev) < tol


class RGTransform(ABC):
    """Abstract base class for RG transformations."""
    
    @abstractmethod
    def transform_law(self, law: EffectiveLaw) -> EffectiveLaw:
        """Transform law to coarser scale."""
        pass
    
    @abstractmethod
    def transform_state(self, state: NDArray) -> NDArray:
        """Transform state to coarser representation."""
        pass
    
    def beta_function(self, law: EffectiveLaw) -> NDArray:
        """Compute beta function: dθ/d(log ℓ)."""
        coarse_law = self.transform_law(law)
        return coarse_law.couplings - law.couplings


class BlockAverageRG(RGTransform):
    """
    Block averaging RG transformation.
    
    Partition state into blocks, average within blocks.
    """
    
    def __init__(self, block_size: int = 2):
        self.block_size = block_size
    
    def transform_state(self, state: NDArray) -> NDArray:
        """Average blocks of size k."""
        n = len(state)
        n_blocks = n // self.block_size
        
        if n_blocks == 0:
            return state
        
        coarse = np.zeros(n_blocks)
        for i in range(n_blocks):
            block = state[i*self.block_size:(i+1)*self.block_size]
            coarse[i] = np.mean(block)
        
        return coarse
    
    def transform_law(self, law: EffectiveLaw) -> EffectiveLaw:
        """Transform couplings under block averaging."""
        # For nearest-neighbor models, couplings rescale
        # This is a simplified version
        n = len(law.couplings)
        n_coarse = n // self.block_size
        
        if n_coarse == 0:
            return law
        
        # Couplings at coarse scale (simplified)
        coarse_couplings = np.zeros(n_coarse)
        for i in range(n_coarse):
            block = law.couplings[i*self.block_size:(i+1)*self.block_size]
            # Effective coupling is average scaled by block size
            coarse_couplings[i] = np.mean(block) * self.block_size
        
        return EffectiveLaw(
            scale=law.scale + 1,
            couplings=coarse_couplings,
            energy_func=law.energy_func,
            dimension=n_coarse,
        )


class DecimationRG(RGTransform):
    """
    Decimation RG: keep every k-th degree of freedom.
    
    Used for exact RG in 1D Ising model.
    """
    
    def __init__(self, decimation_factor: int = 2):
        self.factor = decimation_factor
    
    def transform_state(self, state: NDArray) -> NDArray:
        """Keep every k-th component."""
        return state[::self.factor].copy()
    
    def transform_law(self, law: EffectiveLaw) -> EffectiveLaw:
        """Decimation RG for couplings."""
        # Keep every k-th coupling
        coarse_couplings = law.couplings[::self.factor].copy()
        
        return EffectiveLaw(
            scale=law.scale + 1,
            couplings=coarse_couplings,
            energy_func=law.energy_func,
            dimension=len(coarse_couplings),
        )


class MajorityRuleRG(RGTransform):
    """
    Majority rule RG for discrete (spin) systems.
    
    Block spin takes majority vote of its constituents.
    """
    
    def __init__(self, block_size: int = 3):
        self.block_size = block_size
    
    def transform_state(self, state: NDArray) -> NDArray:
        """Apply majority rule to blocks."""
        n = len(state)
        n_blocks = n // self.block_size
        
        if n_blocks == 0:
            return state
        
        coarse = np.zeros(n_blocks)
        for i in range(n_blocks):
            block = state[i*self.block_size:(i+1)*self.block_size]
            # Majority vote: sign of sum
            coarse[i] = np.sign(np.sum(block))
            if coarse[i] == 0:
                coarse[i] = 1  # Tie-breaker
        
        return coarse
    
    def transform_law(self, law: EffectiveLaw) -> EffectiveLaw:
        """Transform couplings under majority rule."""
        # Simplified: couplings scale with block size
        n_coarse = len(law.couplings) // self.block_size
        
        if n_coarse == 0:
            return law
        
        coarse_couplings = np.zeros(n_coarse)
        for i in range(n_coarse):
            block = law.couplings[i*self.block_size:(i+1)*self.block_size]
            coarse_couplings[i] = np.sum(block)
        
        return EffectiveLaw(
            scale=law.scale + 1,
            couplings=coarse_couplings,
            energy_func=law.energy_func,
            dimension=n_coarse,
        )


@dataclass
class FixedPoint:
    """
    RG fixed point: self-similar law under RG transformation.
    
    At fixed point: R(H*) = H*
    """
    couplings: NDArray[np.float64]
    stability: str  # "stable", "unstable", "marginal"
    critical_exponents: Dict[str, float] = field(default_factory=dict)
    universality_class: str = "unknown"
    
    def is_stable(self) -> bool:
        return self.stability == "stable"
    
    def is_unstable(self) -> bool:
        return self.stability == "unstable"


class RGFlowAnalyzer:
    """
    Analyze RG flow and find fixed points.
    """
    
    def __init__(self, transform: RGTransform):
        self.transform = transform
    
    def flow(
        self,
        initial_law: EffectiveLaw,
        n_steps: int = 10,
    ) -> RGFlow:
        """Run RG flow for n steps."""
        flow = RGFlow()
        flow.add_step(initial_law)
        
        current = initial_law
        for _ in range(n_steps):
            if len(current.couplings) < 2:
                break
            
            beta = self.transform.beta_function(current)
            coarse = self.transform.transform_law(current)
            flow.add_step(coarse, beta)
            current = coarse
        
        return flow
    
    def find_fixed_point(
        self,
        initial_law: EffectiveLaw,
        max_iterations: int = 100,
        tol: float = 1e-8,
    ) -> Optional[FixedPoint]:
        """Find fixed point by iteration."""
        current = initial_law
        
        for _ in range(max_iterations):
            if len(current.couplings) < 2:
                break
            
            coarse = self.transform.transform_law(current)
            
            # Check for fixed point
            if len(coarse.couplings) == len(current.couplings):
                diff = np.linalg.norm(coarse.couplings - current.couplings)
                if diff < tol:
                    return FixedPoint(
                        couplings=current.couplings,
                        stability="unknown",
                    )
            
            current = coarse
        
        return None
    
    def linearize_at_fixed_point(
        self,
        fixed_point: FixedPoint,
        eps: float = 1e-6,
    ) -> NDArray:
        """
        Compute linearized RG transformation at fixed point.
        
        Returns eigenvalues that determine stability.
        """
        n = len(fixed_point.couplings)
        jacobian = np.zeros((n, n))
        
        law0 = EffectiveLaw(
            scale=0,
            couplings=fixed_point.couplings.copy(),
            dimension=n,
        )
        
        for i in range(n):
            # Perturb coupling i
            perturbed = fixed_point.couplings.copy()
            perturbed[i] += eps
            
            law_plus = EffectiveLaw(scale=0, couplings=perturbed, dimension=n)
            
            beta_plus = self.transform.beta_function(law_plus)
            beta_0 = self.transform.beta_function(law0)
            
            if len(beta_plus) == n and len(beta_0) == n:
                jacobian[:, i] = (beta_plus - beta_0) / eps
        
        return np.linalg.eigvals(jacobian)


@dataclass
class HierarchicalLaw:
    """
    Multi-scale hierarchical law.
    
    Maintains effective laws at all scales simultaneously.
    """
    laws: Dict[int, EffectiveLaw] = field(default_factory=dict)
    
    def set_law(self, scale: int, law: EffectiveLaw):
        self.laws[scale] = law
    
    def get_law(self, scale: int) -> Optional[EffectiveLaw]:
        return self.laws.get(scale)
    
    @property
    def finest_scale(self) -> int:
        return min(self.laws.keys()) if self.laws else 0
    
    @property
    def coarsest_scale(self) -> int:
        return max(self.laws.keys()) if self.laws else 0
    
    def n_scales(self) -> int:
        return len(self.laws)


class VerticalHybridFlow:
    """
    Vertical hybrid flow: Σ + Ψ.
    
    Combines stochastic exploration (Σ) with hierarchical compression (Ψ).
    
    Pattern:
    1. Σ generates samples/trajectories at fine scale
    2. Ψ compresses into coarse statistics/laws
    3. Iterate: stochastic expansion + recursive compression
    """
    
    def __init__(
        self,
        sigma_strength: float = 1.0,
        psi_transform: RGTransform = None,
    ):
        self.sigma = sigma_strength
        self.psi = psi_transform or BlockAverageRG(block_size=2)
        self._rng = np.random.default_rng()
    
    def sample_and_compress(
        self,
        initial_state: NDArray,
        n_samples: int = 100,
        n_rg_steps: int = 3,
    ) -> Tuple[List[NDArray], HierarchicalLaw]:
        """
        Generate samples via Σ, compress via Ψ.
        
        Returns samples and hierarchical effective law.
        """
        d = len(initial_state)
        
        # Σ: Generate stochastic samples
        samples = []
        for _ in range(n_samples):
            noise = self._rng.standard_normal(d)
            sample = initial_state + self.sigma * noise
            samples.append(sample)
        
        # Build hierarchical law from samples
        hier_law = HierarchicalLaw()
        
        # Fine scale: empirical covariance as "couplings"
        samples_array = np.array(samples)
        cov = np.cov(samples_array.T)
        
        fine_law = EffectiveLaw(
            scale=0,
            couplings=np.diag(cov),
            dimension=d,
        )
        hier_law.set_law(0, fine_law)
        
        # Ψ: Compress to coarser scales
        current_law = fine_law
        for step in range(1, n_rg_steps + 1):
            if len(current_law.couplings) < 2:
                break
            
            coarse_law = self.psi.transform_law(current_law)
            hier_law.set_law(step, coarse_law)
            current_law = coarse_law
        
        return samples, hier_law


# Noise-to-law transition helper
def noise_to_law_transition(
    noise_samples: NDArray,
    rg_transform: RGTransform,
    n_steps: int = 3,
) -> HierarchicalLaw:
    """
    Transition from micro-noise to effective macro-laws.
    
    micro-noise →[Σ]→ mixed ensembles →[Ψ]→ effective laws
    """
    n_samples, d = noise_samples.shape
    hier_law = HierarchicalLaw()
    
    # Fine scale: compute statistics from samples
    mean = np.mean(noise_samples, axis=0)
    cov = np.cov(noise_samples.T)
    
    # Use eigenvalues of covariance as effective couplings
    if d > 1:
        eigenvalues = np.linalg.eigvalsh(cov)
    else:
        eigenvalues = np.array([cov.item()])
    
    fine_law = EffectiveLaw(
        scale=0,
        couplings=eigenvalues,
        dimension=d,
    )
    hier_law.set_law(0, fine_law)
    
    # Compress through scales
    current_law = fine_law
    for step in range(1, n_steps + 1):
        if len(current_law.couplings) < 2:
            break
        coarse_law = rg_transform.transform_law(current_law)
        hier_law.set_law(step, coarse_law)
        current_law = coarse_law
    
    return hier_law


# 1D Ising model RG (exact decimation)
class Ising1DRG(RGTransform):
    """
    Exact RG for 1D Ising model via decimation.
    
    H = -J Σ_i s_i s_{i+1}
    
    After decimating every other spin:
    J' = (1/2) ln(cosh(2J))
    """
    
    def transform_state(self, state: NDArray) -> NDArray:
        """Keep every other spin."""
        return state[::2].copy()
    
    def transform_law(self, law: EffectiveLaw) -> EffectiveLaw:
        """Apply exact RG recursion for coupling."""
        J = law.couplings[0] if len(law.couplings) > 0 else 1.0
        
        # Exact recursion: J' = (1/2) ln(cosh(2J))
        J_prime = 0.5 * np.log(np.cosh(2 * J))
        
        return EffectiveLaw(
            scale=law.scale + 1,
            couplings=np.array([J_prime]),
            dimension=1,
        )
