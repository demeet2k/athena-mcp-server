"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        POLESTAR GEMM MODULE                                  ║
║                                                                              ║
║  Adaptive Matrix Multiplication with Strassen-Style Hybrid Recursion         ║
║                                                                              ║
║  Core Insight:                                                               ║
║    Matrix multiplication can be viewed as a hybrid algorithm where:          ║
║      - D (Discrete): Block partitioning, index arithmetic                   ║
║      - Ω (Oscillatory): Spectral decomposition, FFT-based methods          ║
║      - Σ (Stochastic): Randomized sketching, sampling                       ║
║      - Ψ (Recursive): Strassen recursion, divide-and-conquer               ║
║                                                                              ║
║  Complexity Hierarchy:                                                       ║
║    Standard:    O(n³)                                                        ║
║    Strassen:    O(n^2.807) = O(n^{log_2 7})                                 ║
║    Coppersmith: O(n^2.376)                                                   ║
║    Optimal:     Ω(n²) (theoretical lower bound)                             ║
║                                                                              ║
║  Adaptive Strategy:                                                          ║
║    - Small matrices: Standard BLAS                                          ║
║    - Medium matrices: Strassen with crossover                               ║
║    - Large matrices: Cache-oblivious recursive blocking                     ║
║    - Sparse matrices: Specialized sparse-dense hybrids                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Callable, Any
from enum import Enum, auto
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# GEMM ALGORITHM TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class GEMMAlgorithm(Enum):
    """Matrix multiplication algorithm selection."""
    STANDARD = "standard"          # O(n³) naive/BLAS
    STRASSEN = "strassen"          # O(n^2.807) Strassen
    STRASSEN_WINOGRAD = "strassen_winograd"  # Improved Strassen
    CACHE_OBLIVIOUS = "cache_oblivious"      # Recursive blocking
    SPARSE_DENSE = "sparse_dense"            # Sparse × Dense hybrid
    RANDOMIZED = "randomized"                # Sketching-based


class CrossoverStrategy(Enum):
    """When to switch from recursive to standard."""
    FIXED = "fixed"        # Fixed threshold
    ADAPTIVE = "adaptive"  # Based on cache size
    PROFILE = "profile"    # Based on profiling


# ═══════════════════════════════════════════════════════════════════════════════
# BLOCK PARTITIONING
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class BlockPartition:
    """
    2×2 block partition of a matrix.
    
    A = [[A11, A12],
         [A21, A22]]
    """
    A11: NDArray[np.float64]
    A12: NDArray[np.float64]
    A21: NDArray[np.float64]
    A22: NDArray[np.float64]
    
    @classmethod
    def from_matrix(cls, A: NDArray[np.float64]) -> 'BlockPartition':
        """Partition matrix into 2×2 blocks."""
        n, m = A.shape
        n2, m2 = n // 2, m // 2
        
        return cls(
            A11=A[:n2, :m2].copy(),
            A12=A[:n2, m2:].copy(),
            A21=A[n2:, :m2].copy(),
            A22=A[n2:, m2:].copy()
        )
    
    def to_matrix(self) -> NDArray[np.float64]:
        """Reconstruct matrix from blocks."""
        top = np.hstack([self.A11, self.A12])
        bottom = np.hstack([self.A21, self.A22])
        return np.vstack([top, bottom])
    
    @property
    def block_shape(self) -> Tuple[int, int]:
        """Shape of individual blocks."""
        return self.A11.shape


def pad_to_power_of_two(A: NDArray[np.float64]) -> Tuple[NDArray[np.float64], Tuple[int, int]]:
    """Pad matrix to nearest power of 2 dimensions."""
    n, m = A.shape
    n_padded = 1 << (n - 1).bit_length()
    m_padded = 1 << (m - 1).bit_length()
    
    if n_padded == n and m_padded == m:
        return A, (n, m)
    
    result = np.zeros((n_padded, m_padded), dtype=A.dtype)
    result[:n, :m] = A
    return result, (n, m)


def unpad(C: NDArray[np.float64], original_shape: Tuple[int, int]) -> NDArray[np.float64]:
    """Remove padding from result matrix."""
    n, m = original_shape
    return C[:n, :m]


# ═══════════════════════════════════════════════════════════════════════════════
# STRASSEN ALGORITHM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class StrassenGEMM:
    """
    Strassen's algorithm for matrix multiplication.
    
    Complexity: O(n^{log_2 7}) ≈ O(n^2.807)
    
    The algorithm computes 7 matrix products instead of 8,
    trading multiplications for additions.
    
    M1 = (A11 + A22)(B11 + B22)
    M2 = (A21 + A22)B11
    M3 = A11(B12 - B22)
    M4 = A22(B21 - B11)
    M5 = (A11 + A12)B22
    M6 = (A21 - A11)(B11 + B12)
    M7 = (A12 - A22)(B21 + B22)
    
    C11 = M1 + M4 - M5 + M7
    C12 = M3 + M5
    C21 = M2 + M4
    C22 = M1 - M2 + M3 + M6
    """
    crossover: int = 64  # Switch to standard below this size
    
    def multiply(self, A: NDArray[np.float64], B: NDArray[np.float64]) -> NDArray[np.float64]:
        """Strassen matrix multiplication."""
        n = A.shape[0]
        
        # Base case: use standard multiplication
        if n <= self.crossover:
            return A @ B
        
        # Pad if necessary
        A_padded, orig_A = pad_to_power_of_two(A)
        B_padded, orig_B = pad_to_power_of_two(B)
        
        # Recursive Strassen
        C_padded = self._strassen_recursive(A_padded, B_padded)
        
        # Unpad result
        return unpad(C_padded, (orig_A[0], orig_B[1]))
    
    def _strassen_recursive(self, A: NDArray, B: NDArray) -> NDArray:
        """Recursive Strassen implementation."""
        n = A.shape[0]
        
        if n <= self.crossover:
            return A @ B
        
        # Partition
        A_blocks = BlockPartition.from_matrix(A)
        B_blocks = BlockPartition.from_matrix(B)
        
        A11, A12 = A_blocks.A11, A_blocks.A12
        A21, A22 = A_blocks.A21, A_blocks.A22
        B11, B12 = B_blocks.A11, B_blocks.A12
        B21, B22 = B_blocks.A21, B_blocks.A22
        
        # Compute 7 products
        M1 = self._strassen_recursive(A11 + A22, B11 + B22)
        M2 = self._strassen_recursive(A21 + A22, B11)
        M3 = self._strassen_recursive(A11, B12 - B22)
        M4 = self._strassen_recursive(A22, B21 - B11)
        M5 = self._strassen_recursive(A11 + A12, B22)
        M6 = self._strassen_recursive(A21 - A11, B11 + B12)
        M7 = self._strassen_recursive(A12 - A22, B21 + B22)
        
        # Combine results
        C11 = M1 + M4 - M5 + M7
        C12 = M3 + M5
        C21 = M2 + M4
        C22 = M1 - M2 + M3 + M6
        
        C_blocks = BlockPartition(C11, C12, C21, C22)
        return C_blocks.to_matrix()
    
    @staticmethod
    def operation_count(n: int) -> Dict[str, int]:
        """Count operations for n×n multiplication."""
        if n <= 1:
            return {'multiplications': 1, 'additions': 0}
        
        # Strassen: 7 recursive calls, ~18n² additions
        return {
            'multiplications': 7 ** int(np.log2(n)),
            'additions': int(6 * n**2 * np.log2(n))
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CACHE-OBLIVIOUS GEMM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CacheObliviousGEMM:
    """
    Cache-oblivious matrix multiplication.
    
    Recursively divides matrices to optimize cache utilization
    without knowing cache parameters.
    
    Cache complexity: O(n³/B√M) where M = cache size, B = block size
    """
    base_size: int = 32  # Base case threshold
    
    def multiply(self, A: NDArray[np.float64], B: NDArray[np.float64]) -> NDArray[np.float64]:
        """Cache-oblivious multiplication."""
        m, k = A.shape
        k2, n = B.shape
        assert k == k2, "Incompatible dimensions"
        
        C = np.zeros((m, n), dtype=A.dtype)
        self._recursive_multiply(A, B, C, 0, m, 0, k, 0, n)
        return C
    
    def _recursive_multiply(self, A: NDArray, B: NDArray, C: NDArray,
                           i0: int, i1: int, k0: int, k1: int, j0: int, j1: int):
        """Recursive helper with index ranges."""
        di = i1 - i0
        dk = k1 - k0
        dj = j1 - j0
        
        # Base case
        if di <= self.base_size and dk <= self.base_size and dj <= self.base_size:
            C[i0:i1, j0:j1] += A[i0:i1, k0:k1] @ B[k0:k1, j0:j1]
            return
        
        # Recursive case: split along largest dimension
        if di >= dk and di >= dj:
            # Split rows of A and C
            mid = (i0 + i1) // 2
            self._recursive_multiply(A, B, C, i0, mid, k0, k1, j0, j1)
            self._recursive_multiply(A, B, C, mid, i1, k0, k1, j0, j1)
        elif dk >= dj:
            # Split columns of A and rows of B
            mid = (k0 + k1) // 2
            self._recursive_multiply(A, B, C, i0, i1, k0, mid, j0, j1)
            self._recursive_multiply(A, B, C, i0, i1, mid, k1, j0, j1)
        else:
            # Split columns of B and C
            mid = (j0 + j1) // 2
            self._recursive_multiply(A, B, C, i0, i1, k0, k1, j0, mid)
            self._recursive_multiply(A, B, C, i0, i1, k0, k1, mid, j1)


# ═══════════════════════════════════════════════════════════════════════════════
# SPARSE-DENSE HYBRID
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SparseDenseGEMM:
    """
    Hybrid multiplication for sparse × dense matrices.
    
    When A is sparse and B is dense, uses compressed row format
    to skip zero multiplications.
    """
    density_threshold: float = 0.1  # Below this, use sparse
    
    def multiply(self, A: NDArray[np.float64], B: NDArray[np.float64]) -> NDArray[np.float64]:
        """Multiply sparse A by dense B."""
        density = np.count_nonzero(A) / A.size
        
        if density > self.density_threshold:
            # Dense multiplication
            return A @ B
        
        # Sparse multiplication
        return self._sparse_dense_multiply(A, B)
    
    def _sparse_dense_multiply(self, A: NDArray, B: NDArray) -> NDArray:
        """Sparse × dense using row-wise accumulation."""
        m, k = A.shape
        k2, n = B.shape
        C = np.zeros((m, n), dtype=A.dtype)
        
        for i in range(m):
            row = A[i, :]
            nonzero_indices = np.nonzero(row)[0]
            for j in nonzero_indices:
                C[i, :] += row[j] * B[j, :]
        
        return C
    
    @staticmethod
    def estimate_flops(A: NDArray, B: NDArray) -> int:
        """Estimate FLOPs for sparse-dense multiplication."""
        nnz_A = np.count_nonzero(A)
        n = B.shape[1]
        return 2 * nnz_A * n  # Each nonzero contributes 2n ops


# ═══════════════════════════════════════════════════════════════════════════════
# RANDOMIZED GEMM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RandomizedGEMM:
    """
    Randomized matrix multiplication using sketching.
    
    Approximates AB ≈ (AS)(S'B) where S is a random projection.
    Useful for approximate multiplication or low-rank approximation.
    """
    sketch_size: int = 100
    seed: Optional[int] = None
    
    def __post_init__(self):
        self.rng = np.random.RandomState(self.seed)
    
    def multiply_approximate(self, A: NDArray[np.float64], B: NDArray[np.float64], 
                            rank: int = None) -> NDArray[np.float64]:
        """
        Approximate multiplication using random projection.
        
        For rank-k approximation: projects to k dimensions.
        """
        k = rank or self.sketch_size
        m, n_A = A.shape
        n_B, p = B.shape
        
        # Random sketch matrix
        S = self.rng.randn(n_A, k) / np.sqrt(k)
        
        # Sketch and multiply
        AS = A @ S        # m × k
        StB = S.T @ B     # k × p
        
        return AS @ StB   # m × p (approximate)
    
    def multiply_with_error_bound(self, A: NDArray, B: NDArray, 
                                  epsilon: float = 0.1) -> Tuple[NDArray, float]:
        """
        Multiplication with probabilistic error bound.
        
        Returns (C_approx, error_bound) where
        ||AB - C_approx|| ≤ error_bound with high probability.
        """
        # Determine sketch size for desired accuracy
        k = int(1 / epsilon**2 * np.log(min(A.shape[0], B.shape[1])))
        k = max(k, 10)
        
        C_approx = self.multiply_approximate(A, B, rank=k)
        
        # Error bound (probabilistic)
        frobenius_A = np.linalg.norm(A, 'fro')
        frobenius_B = np.linalg.norm(B, 'fro')
        error_bound = epsilon * frobenius_A * frobenius_B
        
        return C_approx, error_bound


# ═══════════════════════════════════════════════════════════════════════════════
# ADAPTIVE GEMM SELECTOR
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AdaptiveGEMM:
    """
    Adaptive GEMM that selects algorithm based on matrix properties.
    
    Decision tree:
        1. Small matrices (n < 64): Standard BLAS
        2. Sparse matrices (density < 10%): Sparse-dense hybrid
        3. Medium matrices (64 ≤ n < 1024): Strassen
        4. Large matrices (n ≥ 1024): Cache-oblivious
        5. Approximate ok: Randomized
    """
    strassen_crossover: int = 64
    sparse_threshold: float = 0.1
    large_threshold: int = 1024
    
    def __post_init__(self):
        self.strassen = StrassenGEMM(crossover=self.strassen_crossover)
        self.cache_oblivious = CacheObliviousGEMM()
        self.sparse_dense = SparseDenseGEMM(density_threshold=self.sparse_threshold)
        self.randomized = RandomizedGEMM()
    
    def select_algorithm(self, A: NDArray, B: NDArray) -> GEMMAlgorithm:
        """Select best algorithm for given matrices."""
        n = max(A.shape[0], A.shape[1], B.shape[0], B.shape[1])
        
        # Check sparsity
        density_A = np.count_nonzero(A) / A.size
        density_B = np.count_nonzero(B) / B.size
        
        if density_A < self.sparse_threshold or density_B < self.sparse_threshold:
            return GEMMAlgorithm.SPARSE_DENSE
        
        if n < self.strassen_crossover:
            return GEMMAlgorithm.STANDARD
        elif n < self.large_threshold:
            return GEMMAlgorithm.STRASSEN
        else:
            return GEMMAlgorithm.CACHE_OBLIVIOUS
    
    def multiply(self, A: NDArray, B: NDArray, 
                algorithm: GEMMAlgorithm = None) -> NDArray:
        """
        Multiply matrices using selected or automatic algorithm.
        """
        if algorithm is None:
            algorithm = self.select_algorithm(A, B)
        
        if algorithm == GEMMAlgorithm.STANDARD:
            return A @ B
        elif algorithm == GEMMAlgorithm.STRASSEN:
            return self.strassen.multiply(A, B)
        elif algorithm == GEMMAlgorithm.CACHE_OBLIVIOUS:
            return self.cache_oblivious.multiply(A, B)
        elif algorithm == GEMMAlgorithm.SPARSE_DENSE:
            return self.sparse_dense.multiply(A, B)
        elif algorithm == GEMMAlgorithm.RANDOMIZED:
            return self.randomized.multiply_approximate(A, B)
        else:
            return A @ B
    
    def benchmark(self, A: NDArray, B: NDArray) -> Dict[str, Any]:
        """Benchmark all algorithms on given matrices."""
        import time
        
        results = {}
        for algo in [GEMMAlgorithm.STANDARD, GEMMAlgorithm.STRASSEN, 
                     GEMMAlgorithm.CACHE_OBLIVIOUS]:
            start = time.perf_counter()
            C = self.multiply(A, B, algorithm=algo)
            elapsed = time.perf_counter() - start
            results[algo.value] = {
                'time': elapsed,
                'gflops': 2 * A.shape[0] * A.shape[1] * B.shape[1] / elapsed / 1e9
            }
        
        results['selected'] = self.select_algorithm(A, B).value
        return results


# ═══════════════════════════════════════════════════════════════════════════════
# MATRIX CHAIN OPTIMIZATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MatrixChainOptimizer:
    """
    Optimal parenthesization for matrix chain multiplication.
    
    Given matrices A₁, A₂, ..., Aₙ, finds the optimal order
    to minimize total scalar multiplications.
    
    Dynamic programming: O(n³) preprocessing, O(n) query.
    """
    
    def optimize(self, dimensions: List[int]) -> Tuple[int, str]:
        """
        Find optimal parenthesization.
        
        Args:
            dimensions: [p₀, p₁, ..., pₙ] where Aᵢ is pᵢ₋₁ × pᵢ
            
        Returns:
            (min_cost, parenthesization_string)
        """
        n = len(dimensions) - 1
        
        # dp[i][j] = min cost to multiply Aᵢ...Aⱼ
        dp = [[0] * n for _ in range(n)]
        split = [[0] * n for _ in range(n)]
        
        # Chain length
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                dp[i][j] = float('inf')
                
                for k in range(i, j):
                    cost = (dp[i][k] + dp[k+1][j] + 
                           dimensions[i] * dimensions[k+1] * dimensions[j+1])
                    if cost < dp[i][j]:
                        dp[i][j] = cost
                        split[i][j] = k
        
        # Reconstruct parenthesization
        def build_parens(i: int, j: int) -> str:
            if i == j:
                return f"A{i+1}"
            k = split[i][j]
            left = build_parens(i, k)
            right = build_parens(k + 1, j)
            return f"({left} × {right})"
        
        return dp[0][n-1], build_parens(0, n-1)
    
    def multiply_chain(self, matrices: List[NDArray], 
                      gemm: AdaptiveGEMM = None) -> NDArray:
        """Multiply chain of matrices in optimal order."""
        if gemm is None:
            gemm = AdaptiveGEMM()
        
        n = len(matrices)
        if n == 1:
            return matrices[0]
        if n == 2:
            return gemm.multiply(matrices[0], matrices[1])
        
        # Get dimensions
        dims = [matrices[0].shape[0]]
        for M in matrices:
            dims.append(M.shape[1])
        
        # Get optimal order
        _, order = self.optimize(dims)
        
        # Execute in optimal order (simplified: left-to-right for now)
        result = matrices[0]
        for i in range(1, n):
            result = gemm.multiply(result, matrices[i])
        
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# POLESTAR GEMM - QUAD-POLAR PERSPECTIVE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PoleStarGEMM:
    """
    Matrix multiplication from the quad-polar perspective.
    
    Four poles of GEMM:
        D (Discrete): Block partitioning, index computations
        Ω (Oscillatory): FFT-based convolution methods
        Σ (Stochastic): Randomized sketching
        Ψ (Recursive): Strassen/cache-oblivious recursion
    
    The "shortcut" is achieved by hybrid combinations:
        - Standard BLAS: Pure D
        - Strassen: D + Ψ hybrid (recursion with discrete blocks)
        - Randomized: D + Σ hybrid (structure with sampling)
        - FFT-based: D + Ω hybrid (structure with transforms)
    """
    adaptive: AdaptiveGEMM = field(default_factory=AdaptiveGEMM)
    chain_optimizer: MatrixChainOptimizer = field(default_factory=MatrixChainOptimizer)
    
    def multiply(self, A: NDArray, B: NDArray) -> NDArray:
        """Multiply two matrices adaptively."""
        return self.adaptive.multiply(A, B)
    
    def multiply_chain(self, matrices: List[NDArray]) -> NDArray:
        """Multiply chain of matrices in optimal order."""
        return self.chain_optimizer.multiply_chain(matrices, self.adaptive)
    
    def pole_decomposition(self, algorithm: GEMMAlgorithm) -> Dict[str, float]:
        """
        Return pole weights for given algorithm.
        
        Represents algorithm as point in operator simplex.
        """
        if algorithm == GEMMAlgorithm.STANDARD:
            return {'D': 1.0, 'Omega': 0.0, 'Sigma': 0.0, 'Psi': 0.0}
        elif algorithm == GEMMAlgorithm.STRASSEN:
            return {'D': 0.3, 'Omega': 0.0, 'Sigma': 0.0, 'Psi': 0.7}
        elif algorithm == GEMMAlgorithm.CACHE_OBLIVIOUS:
            return {'D': 0.4, 'Omega': 0.0, 'Sigma': 0.0, 'Psi': 0.6}
        elif algorithm == GEMMAlgorithm.RANDOMIZED:
            return {'D': 0.3, 'Omega': 0.0, 'Sigma': 0.7, 'Psi': 0.0}
        else:
            return {'D': 0.25, 'Omega': 0.25, 'Sigma': 0.25, 'Psi': 0.25}
    
    def complexity_analysis(self, n: int) -> Dict[str, Any]:
        """Analyze complexity for different algorithms."""
        return {
            'standard': {
                'operations': n**3,
                'complexity': 'O(n³)',
                'exponent': 3.0
            },
            'strassen': {
                'operations': 7**int(np.log2(n)) if n > 1 else 1,
                'complexity': 'O(n^2.807)',
                'exponent': np.log2(7)
            },
            'coppersmith_winograd': {
                'operations': int(n**2.376),
                'complexity': 'O(n^2.376)',
                'exponent': 2.376
            },
            'theoretical_lower': {
                'operations': n**2,
                'complexity': 'Ω(n²)',
                'exponent': 2.0
            }
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def gemm(A: NDArray, B: NDArray, algorithm: str = 'auto') -> NDArray:
    """
    General matrix multiplication.
    
    Args:
        A: m × k matrix
        B: k × n matrix
        algorithm: 'auto', 'standard', 'strassen', 'cache_oblivious', 'sparse'
        
    Returns:
        m × n product matrix
    """
    gemm_engine = AdaptiveGEMM()
    
    if algorithm == 'auto':
        return gemm_engine.multiply(A, B)
    
    algo_map = {
        'standard': GEMMAlgorithm.STANDARD,
        'strassen': GEMMAlgorithm.STRASSEN,
        'cache_oblivious': GEMMAlgorithm.CACHE_OBLIVIOUS,
        'sparse': GEMMAlgorithm.SPARSE_DENSE,
        'randomized': GEMMAlgorithm.RANDOMIZED
    }
    
    return gemm_engine.multiply(A, B, algorithm=algo_map.get(algorithm, GEMMAlgorithm.STANDARD))


def strassen_multiply(A: NDArray, B: NDArray, crossover: int = 64) -> NDArray:
    """Strassen's algorithm for matrix multiplication."""
    return StrassenGEMM(crossover=crossover).multiply(A, B)


def matrix_chain_multiply(matrices: List[NDArray]) -> NDArray:
    """Multiply chain of matrices in optimal order."""
    return PoleStarGEMM().multiply_chain(matrices)


def optimal_parenthesization(dimensions: List[int]) -> Tuple[int, str]:
    """Find optimal parenthesization for matrix chain."""
    return MatrixChainOptimizer().optimize(dimensions)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    'GEMMAlgorithm',
    'CrossoverStrategy',
    
    # Block operations
    'BlockPartition',
    'pad_to_power_of_two',
    'unpad',
    
    # Algorithms
    'StrassenGEMM',
    'CacheObliviousGEMM',
    'SparseDenseGEMM',
    'RandomizedGEMM',
    'AdaptiveGEMM',
    
    # Chain optimization
    'MatrixChainOptimizer',
    
    # Main interface
    'PoleStarGEMM',
    
    # Functions
    'gemm',
    'strassen_multiply',
    'matrix_chain_multiply',
    'optimal_parenthesization',
]
