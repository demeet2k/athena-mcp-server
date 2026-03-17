"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        TENSOR NETWORK MODULE                                 ║
║                                                                              ║
║  Matrix Product States, PEPS, and Tensor Contraction                         ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Tensor networks encode multi-scale structure through bond dimensions.     ║
║    They provide efficient representations for states with limited            ║
║    entanglement, connecting to the Ψ-pole (hierarchical structure).         ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - MPS: Matrix Product State (1D, bond dimension χ)                       ║
║    - MPO: Matrix Product Operator                                           ║
║    - PEPS: Projected Entangled Pair State (2D)                              ║
║    - TTN: Tree Tensor Network                                               ║
║                                                                              ║
║  Contraction:                                                                ║
║    - 1D contraction: O(Nχ³d)                                                ║
║    - 2D contraction: #P-hard in general                                     ║
║    - Approximate methods: DMRG, TEBD, variational                           ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - Bond dimension ↔ entanglement capacity                                 ║
║    - MPS structure ↔ fold ladder hierarchy                                  ║
║    - Contraction paths ↔ shortcut algorithms                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# TENSOR CORE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Tensor:
    """
    A multi-dimensional array with named indices.
    """
    data: NDArray[np.complex128]
    indices: List[str]
    
    @property
    def rank(self) -> int:
        """Number of indices (tensor rank)."""
        return len(self.indices)
    
    @property
    def shape(self) -> Tuple[int, ...]:
        """Dimensions along each index."""
        return self.data.shape
    
    def dim(self, index: str) -> int:
        """Dimension of a specific index."""
        idx = self.indices.index(index)
        return self.data.shape[idx]
    
    def rename_index(self, old: str, new: str) -> 'Tensor':
        """Rename an index."""
        new_indices = [new if i == old else i for i in self.indices]
        return Tensor(self.data.copy(), new_indices)
    
    def permute(self, new_order: List[str]) -> 'Tensor':
        """Permute indices to new order."""
        perm = [self.indices.index(i) for i in new_order]
        return Tensor(np.transpose(self.data, perm), new_order)
    
    @classmethod
    def random(cls, shape: Dict[str, int], 
              rng: np.random.Generator = None) -> 'Tensor':
        """Create random tensor."""
        if rng is None:
            rng = np.random.default_rng()
        
        indices = list(shape.keys())
        dims = [shape[i] for i in indices]
        data = rng.standard_normal(dims) + 1j * rng.standard_normal(dims)
        return cls(data, indices)
    
    @classmethod
    def identity_matrix(cls, dim: int, left: str, right: str) -> 'Tensor':
        """Create identity matrix as tensor."""
        return cls(np.eye(dim, dtype=np.complex128), [left, right])


def contract(A: Tensor, B: Tensor, indices: List[str]) -> Tensor:
    """
    Contract two tensors over specified indices.
    
    Uses np.tensordot with appropriate axis specification.
    """
    # Find axes to contract
    axes_A = [A.indices.index(i) for i in indices]
    axes_B = [B.indices.index(i) for i in indices]
    
    # Contract
    result_data = np.tensordot(A.data, B.data, (axes_A, axes_B))
    
    # Remaining indices
    remaining_A = [i for i in A.indices if i not in indices]
    remaining_B = [i for i in B.indices if i not in indices]
    result_indices = remaining_A + remaining_B
    
    return Tensor(result_data, result_indices)


def trace_tensor(T: Tensor, idx1: str, idx2: str) -> Tensor:
    """Trace over two indices of same dimension."""
    ax1 = T.indices.index(idx1)
    ax2 = T.indices.index(idx2)
    
    result_data = np.trace(T.data, axis1=ax1, axis2=ax2)
    result_indices = [i for i in T.indices if i not in [idx1, idx2]]
    
    return Tensor(result_data, result_indices)


# ═══════════════════════════════════════════════════════════════════════════════
# MATRIX PRODUCT STATE (MPS)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MPS:
    """
    Matrix Product State for 1D quantum systems.
    
    |ψ⟩ = Σ_{s_1,...,s_N} Tr[A^{s_1}...A^{s_N}] |s_1...s_N⟩
    
    Each tensor A^s_i has shape (χ_{i-1}, d_i, χ_i)
    where χ are bond dimensions and d is physical dimension.
    """
    tensors: List[NDArray[np.complex128]]  # List of rank-3 tensors
    
    @property
    def length(self) -> int:
        """Number of sites."""
        return len(self.tensors)
    
    @property
    def bond_dimensions(self) -> List[int]:
        """List of bond dimensions [χ_0, χ_1, ..., χ_N]."""
        dims = [self.tensors[0].shape[0]]
        for T in self.tensors:
            dims.append(T.shape[2])
        return dims
    
    @property
    def physical_dimensions(self) -> List[int]:
        """Physical dimension at each site."""
        return [T.shape[1] for T in self.tensors]
    
    @property
    def max_bond_dim(self) -> int:
        """Maximum bond dimension."""
        return max(self.bond_dimensions)
    
    def coefficient(self, config: List[int]) -> complex:
        """
        Get coefficient ⟨config|ψ⟩.
        
        config: list of physical indices [s_1, s_2, ..., s_N]
        """
        if len(config) != self.length:
            raise ValueError("Config length must match MPS length")
        
        # Contract left to right
        result = self.tensors[0][:, config[0], :]
        
        for i in range(1, self.length):
            mat = self.tensors[i][:, config[i], :]
            result = result @ mat
        
        # Trace (for periodic) or just the scalar
        if result.shape == (1, 1):
            return result[0, 0]
        return np.trace(result)
    
    def norm_squared(self) -> float:
        """Compute ⟨ψ|ψ⟩ via transfer matrix contraction."""
        # Simple method: contract from left to right
        if self.length == 0:
            return 0.0
        
        # Start with first tensor contracted with its conjugate
        # A: (χ_L, d, χ_R)
        A = self.tensors[0]
        # ⟨A|A⟩ over physical index
        E = np.einsum('ijk,ljk->il', np.conj(A), A)  # (χ_L, χ_L)
        
        for T in self.tensors[1:]:
            # E: (χ, χ), T: (χ, d, χ')
            # Contract: E @ T @ T†
            E_T = np.einsum('ij,jkl->ikl', E, T)  # (χ, d, χ')
            E = np.einsum('ijk,ljk->il', np.conj(T), E_T)  # (χ', χ')
        
        return np.real(np.trace(E))
    
    def normalize(self) -> 'MPS':
        """Return normalized MPS."""
        norm = np.sqrt(self.norm_squared())
        if norm < 1e-15:
            return self
        
        # Distribute normalization factor
        factor = norm ** (1 / self.length)
        new_tensors = [T / factor for T in self.tensors]
        return MPS(new_tensors)
    
    @classmethod
    def product_state(cls, states: List[NDArray]) -> 'MPS':
        """
        Create product state MPS from local states.
        
        states: list of d-dimensional vectors
        """
        tensors = []
        for state in states:
            # Reshape to (1, d, 1)
            T = state.reshape(1, -1, 1).astype(np.complex128)
            tensors.append(T)
        return cls(tensors)
    
    @classmethod
    def random(cls, length: int, physical_dim: int, bond_dim: int,
              rng: np.random.Generator = None) -> 'MPS':
        """Create random MPS."""
        if rng is None:
            rng = np.random.default_rng()
        
        tensors = []
        chi_left = 1
        
        for i in range(length):
            chi_right = bond_dim if i < length - 1 else 1
            if i == 0:
                chi_left = 1
            
            shape = (chi_left, physical_dim, chi_right)
            T = rng.standard_normal(shape) + 1j * rng.standard_normal(shape)
            tensors.append(T)
            chi_left = chi_right
        
        mps = cls(tensors)
        return mps.normalize()


# ═══════════════════════════════════════════════════════════════════════════════
# MATRIX PRODUCT OPERATOR (MPO)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MPO:
    """
    Matrix Product Operator for 1D systems.
    
    O = Σ Tr[W^{s_1,s'_1}...W^{s_N,s'_N}] |s⟩⟨s'|
    
    Each tensor W has shape (χ_{i-1}, d, d, χ_i)
    """
    tensors: List[NDArray[np.complex128]]  # Rank-4 tensors
    
    @property
    def length(self) -> int:
        return len(self.tensors)
    
    def apply_to_mps(self, mps: MPS) -> MPS:
        """
        Apply MPO to MPS: |ψ'⟩ = O|ψ⟩.
        
        Bond dimension grows: χ' = χ_O × χ_ψ
        """
        if len(self.tensors) != mps.length:
            raise ValueError("MPO and MPS must have same length")
        
        new_tensors = []
        
        for W, A in zip(self.tensors, mps.tensors):
            # W: (χ_W_L, d', d, χ_W_R)
            # A: (χ_A_L, d, χ_A_R)
            # Result: (χ_W_L × χ_A_L, d', χ_W_R × χ_A_R)
            
            # Contract over physical index d
            B = np.einsum('abcd,edf->aebcf', W, A)
            
            # Reshape to combine bond indices
            shape = B.shape
            new_shape = (shape[0] * shape[1], shape[2], shape[3] * shape[4])
            new_tensors.append(B.reshape(new_shape))
        
        return MPS(new_tensors)
    
    @classmethod
    def identity(cls, length: int, physical_dim: int) -> 'MPO':
        """Identity operator as MPO."""
        tensors = []
        for _ in range(length):
            W = np.eye(physical_dim).reshape(1, physical_dim, physical_dim, 1)
            tensors.append(W.astype(np.complex128))
        return cls(tensors)


# ═══════════════════════════════════════════════════════════════════════════════
# TREE TENSOR NETWORK (TTN)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TreeTensorNetwork:
    """
    Tree Tensor Network for hierarchical systems.
    
    Binary tree structure with branching ratio 2.
    Each internal node has 3 indices: 2 children + 1 parent.
    """
    leaves: List[NDArray]  # Physical tensors at leaves
    internal: List[NDArray]  # Internal tensors
    
    @classmethod
    def binary_from_mps(cls, mps: MPS) -> 'TreeTensorNetwork':
        """
        Convert MPS to binary TTN via hierarchical grouping.
        
        Groups pairs of sites and builds tree bottom-up.
        """
        # Start with MPS tensors as leaves
        current_level = list(mps.tensors)
        internal = []
        
        while len(current_level) > 1:
            next_level = []
            
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    # Pair two tensors
                    A, B = current_level[i], current_level[i + 1]
                    
                    # Contract and SVD to create new tensor
                    # Simple version: just stack
                    combined = np.tensordot(A, B, axes=([2], [0]))
                    
                    # SVD to reduce bond dimension
                    shape = combined.shape
                    matrix = combined.reshape(shape[0] * shape[1], -1)
                    U, S, Vh = np.linalg.svd(matrix, full_matrices=False)
                    
                    # Truncate
                    chi = min(len(S), shape[0])
                    U = U[:, :chi]
                    S = S[:chi]
                    Vh = Vh[:chi, :]
                    
                    internal.append((U, S, Vh))
                    next_level.append(U @ np.diag(S))
                else:
                    next_level.append(current_level[i])
            
            current_level = next_level
        
        return cls(list(mps.tensors), internal)


# ═══════════════════════════════════════════════════════════════════════════════
# ENTANGLEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class EntanglementAnalyzer:
    """
    Analyze entanglement in tensor network states.
    """
    
    @staticmethod
    def bipartite_entropy_mps(mps: MPS, cut: int) -> float:
        """
        Von Neumann entanglement entropy for bipartition at site `cut`.
        
        S = -Tr(ρ_L log ρ_L)
        """
        if cut <= 0 or cut >= mps.length:
            return 0.0
        
        # Build reduced density matrix via Schmidt decomposition
        # Contract left part
        left = mps.tensors[0]
        for i in range(1, cut):
            # (χ_l, d, χ_r) contracted with next
            left = np.tensordot(left, mps.tensors[i], axes=([2], [0]))
            # Reshape to (χ_0, d_1 × ... × d_i, χ_i)
            shape = left.shape
            left = left.reshape(shape[0], -1, shape[-1])
        
        # SVD gives Schmidt coefficients
        shape = left.shape
        matrix = left.reshape(-1, shape[-1])
        _, S, _ = np.linalg.svd(matrix, full_matrices=False)
        
        # Normalize
        S = S / np.linalg.norm(S)
        
        # Entanglement entropy
        S_sq = S ** 2
        S_sq = S_sq[S_sq > 1e-15]  # Remove zeros
        return -np.sum(S_sq * np.log(S_sq))
    
    @staticmethod
    def entanglement_spectrum(mps: MPS, cut: int) -> NDArray[np.float64]:
        """
        Entanglement spectrum (Schmidt values) at bipartition.
        """
        if cut <= 0 or cut >= mps.length:
            return np.array([1.0])
        
        # Contract left part
        left = mps.tensors[0]
        for i in range(1, cut):
            left = np.tensordot(left, mps.tensors[i], axes=([2], [0]))
            shape = left.shape
            left = left.reshape(shape[0], -1, shape[-1])
        
        shape = left.shape
        matrix = left.reshape(-1, shape[-1])
        _, S, _ = np.linalg.svd(matrix, full_matrices=False)
        
        return S / np.linalg.norm(S)


# ═══════════════════════════════════════════════════════════════════════════════
# CONTRACTION OPTIMIZER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ContractionPath:
    """
    Optimal contraction path for tensor network.
    """
    operations: List[Tuple[int, int]]  # Pairs of tensors to contract
    cost: float  # Total computational cost
    
    @classmethod
    def greedy(cls, tensors: List[Tensor], 
              target_indices: List[str]) -> 'ContractionPath':
        """
        Find greedy contraction order.
        
        At each step, contract the pair with smallest intermediate size.
        """
        remaining = list(range(len(tensors)))
        tensor_info = [(set(T.indices), T.shape) for T in tensors]
        
        operations = []
        total_cost = 0
        
        while len(remaining) > 1:
            best_pair = None
            best_cost = float('inf')
            
            for i in range(len(remaining)):
                for j in range(i + 1, len(remaining)):
                    ti, tj = remaining[i], remaining[j]
                    indices_i, shape_i = tensor_info[ti]
                    indices_j, shape_j = tensor_info[tj]
                    
                    # Shared indices
                    shared = indices_i & indices_j
                    if not shared:
                        continue
                    
                    # Estimate cost
                    cost = np.prod(shape_i) * np.prod(shape_j)
                    
                    if cost < best_cost:
                        best_cost = cost
                        best_pair = (ti, tj)
            
            if best_pair is None:
                break
            
            operations.append(best_pair)
            total_cost += best_cost
            
            # Update remaining
            ti, tj = best_pair
            remaining.remove(ti)
            remaining.remove(tj)
            
            # Add merged tensor
            new_idx = len(tensor_info)
            merged_indices = (tensor_info[ti][0] | tensor_info[tj][0]) - \
                           (tensor_info[ti][0] & tensor_info[tj][0])
            tensor_info.append((merged_indices, (1,)))  # Simplified
            remaining.append(new_idx)
        
        return cls(operations, total_cost)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_mps(length: int, physical_dim: int = 2, 
              bond_dim: int = 4) -> MPS:
    """Create random MPS."""
    return MPS.random(length, physical_dim, bond_dim)


def mps_overlap(mps1: MPS, mps2: MPS) -> complex:
    """Compute ⟨ψ_1|ψ_2⟩."""
    if mps1.length != mps2.length:
        raise ValueError("MPS must have same length")
    
    if mps1.length == 0:
        return 0.0
    
    # Contract from left to right
    A1, A2 = mps1.tensors[0], mps2.tensors[0]
    E = np.einsum('ijk,ljk->il', np.conj(A1), A2)
    
    for T1, T2 in zip(mps1.tensors[1:], mps2.tensors[1:]):
        E_T = np.einsum('ij,jkl->ikl', E, T2)
        E = np.einsum('ijk,ljk->il', np.conj(T1), E_T)
    
    return np.trace(E)


def entanglement_entropy(mps: MPS, cut: int) -> float:
    """Entanglement entropy at bipartition."""
    return EntanglementAnalyzer.bipartite_entropy_mps(mps, cut)


def contract_tensors(A: Tensor, B: Tensor, indices: List[str]) -> Tensor:
    """Contract two tensors."""
    return contract(A, B, indices)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Core
    'Tensor',
    'contract',
    'trace_tensor',
    
    # MPS/MPO
    'MPS',
    'MPO',
    
    # TTN
    'TreeTensorNetwork',
    
    # Entanglement
    'EntanglementAnalyzer',
    
    # Contraction
    'ContractionPath',
    
    # Functions
    'create_mps',
    'mps_overlap',
    'entanglement_entropy',
    'contract_tensors',
]
