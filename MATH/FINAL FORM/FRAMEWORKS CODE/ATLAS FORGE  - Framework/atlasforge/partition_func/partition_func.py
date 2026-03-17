"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PARTITION FUNCTIONS MODULE                                ║
║                                                                              ║
║  Integer Partitions, Generating Functions, and Combinatorics                 ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Partition functions encode deep combinatorial structure.                  ║
║    The partition function p(n) counts ways to write n as sum of              ║
║    positive integers, connecting to modular forms via η(τ).                 ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - p(n): number of partitions of n                                        ║
║    - Generating function: Σ p(n)q^n = Π(1 - q^k)^{-1}                       ║
║    - Ferrers diagrams: visual representation                                 ║
║    - Hook length formula: |SYT(λ)| = n! / Π h(i,j)                          ║
║    - Ramanujan congruences: p(5n+4) ≡ 0 (mod 5), etc.                       ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - D-pole (discrete) ↔ partition enumeration                              ║
║    - Modular forms ↔ partition generating function                          ║
║    - Latin squares ↔ restricted partitions                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Iterator, Set
from functools import lru_cache
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# PARTITION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Partition:
    """
    An integer partition λ = (λ_1, λ_2, ..., λ_k) with λ_1 ≥ λ_2 ≥ ... ≥ λ_k > 0.
    """
    parts: Tuple[int, ...]
    
    def __post_init__(self):
        # Ensure sorted and no zeros
        self.parts = tuple(sorted([p for p in self.parts if p > 0], reverse=True))
    
    @property
    def size(self) -> int:
        """Sum of all parts: n = Σλ_i."""
        return sum(self.parts)
    
    @property
    def length(self) -> int:
        """Number of parts: ℓ(λ)."""
        return len(self.parts)
    
    @property
    def largest_part(self) -> int:
        """Largest part: λ_1."""
        return self.parts[0] if self.parts else 0
    
    def conjugate(self) -> 'Partition':
        """
        Conjugate partition λ'.
        
        Transpose the Ferrers diagram.
        """
        if not self.parts:
            return Partition(())
        
        # λ'_i = |{j : λ_j ≥ i}|
        conj_parts = []
        for i in range(1, self.parts[0] + 1):
            count = sum(1 for p in self.parts if p >= i)
            if count > 0:
                conj_parts.append(count)
        
        return Partition(tuple(conj_parts))
    
    def ferrers_diagram(self) -> List[str]:
        """Visual Ferrers diagram using asterisks."""
        return ['*' * p for p in self.parts]
    
    def hook_lengths(self) -> List[List[int]]:
        """
        Hook lengths h(i,j) for each cell.
        
        h(i,j) = λ_i - j + λ'_j - i + 1
        """
        if not self.parts:
            return []
        
        conj = self.conjugate()
        hooks = []
        
        for i, part in enumerate(self.parts):
            row = []
            for j in range(part):
                # Arm: cells to the right = λ_i - j - 1
                arm = part - j - 1
                # Leg: cells below = λ'_j - i - 1
                leg = (conj.parts[j] if j < len(conj.parts) else 0) - i - 1
                h = arm + leg + 1
                row.append(h)
            hooks.append(row)
        
        return hooks
    
    def hook_length_product(self) -> int:
        """Product of all hook lengths."""
        product = 1
        for row in self.hook_lengths():
            for h in row:
                product *= h
        return product
    
    def num_standard_tableaux(self) -> int:
        """
        Number of standard Young tableaux of shape λ.
        
        |SYT(λ)| = n! / Π h(i,j)
        """
        n = self.size
        if n == 0:
            return 1
        
        from math import factorial
        hook_prod = self.hook_length_product()
        return factorial(n) // hook_prod
    
    def dominates(self, other: 'Partition') -> bool:
        """
        Check if self dominates other in dominance order.
        
        λ ⊵ μ iff Σ_{i≤k} λ_i ≥ Σ_{i≤k} μ_i for all k.
        """
        if self.size != other.size:
            return False
        
        sum_self = 0
        sum_other = 0
        
        max_len = max(len(self.parts), len(other.parts))
        
        for k in range(max_len):
            sum_self += self.parts[k] if k < len(self.parts) else 0
            sum_other += other.parts[k] if k < len(other.parts) else 0
            
            if sum_self < sum_other:
                return False
        
        return True
    
    def __repr__(self) -> str:
        return f"({', '.join(map(str, self.parts))})"
    
    def __hash__(self) -> int:
        return hash(self.parts)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Partition):
            return False
        return self.parts == other.parts


# ═══════════════════════════════════════════════════════════════════════════════
# PARTITION ENUMERATION
# ═══════════════════════════════════════════════════════════════════════════════

class PartitionEnumerator:
    """
    Enumerate partitions of n with various constraints.
    """
    
    @staticmethod
    @lru_cache(maxsize=10000)
    def count(n: int) -> int:
        """
        Count partitions of n: p(n).
        
        Uses dynamic programming.
        """
        if n < 0:
            return 0
        if n == 0:
            return 1
        
        # p(n, k) = partitions of n with largest part ≤ k
        dp = [[0] * (n + 1) for _ in range(n + 1)]
        
        for k in range(n + 1):
            dp[0][k] = 1
        
        for i in range(1, n + 1):
            for k in range(1, n + 1):
                # Don't use k: dp[i][k-1]
                # Use k: dp[i-k][k] if i >= k
                dp[i][k] = dp[i][k-1]
                if i >= k:
                    dp[i][k] += dp[i-k][k]
        
        return dp[n][n]
    
    @staticmethod
    def generate(n: int) -> Iterator[Partition]:
        """Generate all partitions of n."""
        if n == 0:
            yield Partition(())
            return
        
        def _gen(remaining: int, max_part: int, current: List[int]):
            if remaining == 0:
                yield Partition(tuple(current))
                return
            
            for part in range(min(remaining, max_part), 0, -1):
                yield from _gen(remaining - part, part, current + [part])
        
        yield from _gen(n, n, [])
    
    @staticmethod
    def count_distinct_parts(n: int) -> int:
        """Count partitions with distinct parts: q(n)."""
        if n < 0:
            return 0
        if n == 0:
            return 1
        
        # DP: q(n, k) = partitions of n with distinct parts ≤ k
        dp = [[0] * (n + 2) for _ in range(n + 1)]
        dp[0][0] = 1
        
        for k in range(1, n + 1):
            for i in range(n + 1):
                dp[i][k] = dp[i][k-1]
                if i >= k:
                    dp[i][k] += dp[i-k][k-1]
        
        return dp[n][n]
    
    @staticmethod
    def generate_distinct_parts(n: int) -> Iterator[Partition]:
        """Generate partitions with distinct parts."""
        def _gen(remaining: int, max_part: int, current: List[int]):
            if remaining == 0:
                yield Partition(tuple(current))
                return
            
            for part in range(min(remaining, max_part), 0, -1):
                yield from _gen(remaining - part, part - 1, current + [part])
        
        yield from _gen(n, n, [])
    
    @staticmethod
    def count_odd_parts(n: int) -> int:
        """Count partitions with all odd parts."""
        if n < 0:
            return 0
        if n == 0:
            return 1
        
        dp = [0] * (n + 1)
        dp[0] = 1
        
        for k in range(1, n + 1, 2):  # Odd parts only
            for i in range(k, n + 1):
                dp[i] += dp[i - k]
        
        return dp[n]


# ═══════════════════════════════════════════════════════════════════════════════
# GENERATING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PartitionGeneratingFunction:
    """
    Generating function for partition sequences.
    
    Σ p(n) q^n = Π_{k≥1} 1/(1 - q^k)
    """
    max_n: int = 100
    
    def partition_series(self) -> NDArray[np.float64]:
        """Compute p(0), p(1), ..., p(max_n)."""
        return np.array([PartitionEnumerator.count(n) 
                        for n in range(self.max_n + 1)])
    
    def evaluate(self, q: complex) -> complex:
        """
        Evaluate generating function at q.
        
        Converges for |q| < 1.
        """
        if abs(q) >= 1:
            return float('inf')
        
        result = 1.0
        for k in range(1, self.max_n + 1):
            result /= (1 - q ** k)
        
        return result
    
    def eta_relation(self, q: complex) -> complex:
        """
        Relation to Dedekind eta: Σ p(n)q^n = q^{1/24}/η(τ)
        
        where q = e^{2πiτ}.
        """
        # η(τ) = q^{1/24} Π(1 - q^k)
        eta = q ** (1/24)
        for k in range(1, self.max_n + 1):
            eta *= (1 - q ** k)
        
        return 1 / eta if abs(eta) > 1e-15 else float('inf')
    
    def asymptotic_estimate(self, n: int) -> float:
        """
        Hardy-Ramanujan asymptotic formula.
        
        p(n) ~ exp(π√(2n/3)) / (4n√3) as n → ∞
        """
        if n <= 0:
            return 1.0
        
        from math import pi, sqrt, exp
        return exp(pi * sqrt(2 * n / 3)) / (4 * n * sqrt(3))


# ═══════════════════════════════════════════════════════════════════════════════
# RAMANUJAN CONGRUENCES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RamanujanCongruences:
    """
    Famous congruences for partition function.
    
    p(5n + 4) ≡ 0 (mod 5)
    p(7n + 5) ≡ 0 (mod 7)
    p(11n + 6) ≡ 0 (mod 11)
    """
    
    @staticmethod
    def verify_mod5(max_n: int = 100) -> bool:
        """Verify p(5n + 4) ≡ 0 (mod 5)."""
        for n in range(max_n):
            k = 5 * n + 4
            if PartitionEnumerator.count(k) % 5 != 0:
                return False
        return True
    
    @staticmethod
    def verify_mod7(max_n: int = 50) -> bool:
        """Verify p(7n + 5) ≡ 0 (mod 7)."""
        for n in range(max_n):
            k = 7 * n + 5
            if PartitionEnumerator.count(k) % 7 != 0:
                return False
        return True
    
    @staticmethod
    def verify_mod11(max_n: int = 30) -> bool:
        """Verify p(11n + 6) ≡ 0 (mod 11)."""
        for n in range(max_n):
            k = 11 * n + 6
            if PartitionEnumerator.count(k) % 11 != 0:
                return False
        return True
    
    @staticmethod
    def congruence_residues(n: int, modulus: int) -> Dict[int, List[int]]:
        """
        Analyze p(n) mod m for 0 ≤ n < max.
        
        Returns dict: residue → list of n with that residue.
        """
        residues = {r: [] for r in range(modulus)}
        
        for k in range(n):
            p_k = PartitionEnumerator.count(k)
            residues[p_k % modulus].append(k)
        
        return residues


# ═══════════════════════════════════════════════════════════════════════════════
# YOUNG TABLEAUX
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class YoungTableau:
    """
    Standard Young tableau: filling of partition shape with 1,...,n.
    """
    shape: Partition
    entries: List[List[int]]
    
    def is_standard(self) -> bool:
        """
        Check if tableau is standard:
        - Rows increase left to right
        - Columns increase top to bottom
        - Contains 1, 2, ..., n exactly once
        """
        n = self.shape.size
        seen = set()
        
        for i, row in enumerate(self.entries):
            for j, val in enumerate(row):
                if val < 1 or val > n:
                    return False
                if val in seen:
                    return False
                seen.add(val)
                
                # Row increasing
                if j > 0 and row[j-1] >= val:
                    return False
                
                # Column increasing
                if i > 0 and j < len(self.entries[i-1]):
                    if self.entries[i-1][j] >= val:
                        return False
        
        return len(seen) == n
    
    def descent_set(self) -> Set[int]:
        """
        Descent set: {i : i+1 appears in row below i}.
        """
        n = self.shape.size
        descents = set()
        
        # Find position of each number
        positions = {}
        for i, row in enumerate(self.entries):
            for j, val in enumerate(row):
                positions[val] = (i, j)
        
        for i in range(1, n):
            if i in positions and i + 1 in positions:
                if positions[i][0] < positions[i + 1][0]:
                    descents.add(i)
        
        return descents
    
    @classmethod
    def enumerate_standard(cls, shape: Partition) -> Iterator['YoungTableau']:
        """Generate all standard Young tableaux of given shape."""
        n = shape.size
        if n == 0:
            yield cls(shape, [])
            return
        
        # Backtracking algorithm
        template = [[0] * p for p in shape.parts]
        
        def _fill(val: int, positions: List[Tuple[int, int]]):
            if val > n:
                yield cls(shape, [row[:] for row in template])
                return
            
            for i, j in positions:
                # Can place val at (i, j)?
                if template[i][j] != 0:
                    continue
                
                # Row constraint: left must be filled and smaller
                if j > 0 and (template[i][j-1] == 0 or template[i][j-1] >= val):
                    continue
                
                # Column constraint: above must be filled and smaller
                if i > 0 and j < len(template[i-1]):
                    if template[i-1][j] == 0 or template[i-1][j] >= val:
                        continue
                
                # This is a valid position - actually need corners only
                template[i][j] = val
                yield from _fill(val + 1, positions)
                template[i][j] = 0
        
        # Find all cell positions
        positions = [(i, j) for i, row in enumerate(template) 
                    for j in range(len(row))]
        
        yield from _fill(1, positions)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def partition(*parts: int) -> Partition:
    """Create partition from parts."""
    return Partition(tuple(parts))


def partition_count(n: int) -> int:
    """Count partitions of n."""
    return PartitionEnumerator.count(n)


def partitions(n: int) -> List[Partition]:
    """List all partitions of n."""
    return list(PartitionEnumerator.generate(n))


def partition_generating_function(q: complex, max_terms: int = 100) -> complex:
    """Evaluate partition generating function."""
    return PartitionGeneratingFunction(max_terms).evaluate(q)


def hook_length_formula(shape: Partition) -> int:
    """Number of standard Young tableaux."""
    return shape.num_standard_tableaux()


def verify_ramanujan() -> bool:
    """Verify Ramanujan congruences."""
    return (RamanujanCongruences.verify_mod5() and
            RamanujanCongruences.verify_mod7() and
            RamanujanCongruences.verify_mod11())


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Core
    'Partition',
    
    # Enumeration
    'PartitionEnumerator',
    
    # Generating functions
    'PartitionGeneratingFunction',
    
    # Congruences
    'RamanujanCongruences',
    
    # Tableaux
    'YoungTableau',
    
    # Functions
    'partition',
    'partition_count',
    'partitions',
    'partition_generating_function',
    'hook_length_formula',
    'verify_ramanujan',
]
