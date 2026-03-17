"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     SPECTRAL GRAPH THEORY MODULE                             ║
║                                                                              ║
║  Graph Laplacians, Spectral Clustering, and Cheeger Inequality               ║
║                                                                              ║
║  Core Principle:                                                             ║
║    L = D - A (Laplacian), spectrum encodes graph structure                  ║
║    λ₂ (Fiedler value) ↔ connectivity, clustering                            ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - Ψ-pole ↔ Spectral hierarchy (eigenvector decomposition)                ║
║    - C-pole ↔ Continuous relaxation (spectral embedding)                    ║
║    - D-pole ↔ Discrete graph structure (cuts, partitions)                   ║
║    - Gateway ↔ Cheeger inequality (discrete ↔ continuous)                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Set
from enum import Enum
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# GRAPH REPRESENTATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Graph:
    """
    Graph G = (V, E) with n vertices.
    """
    n_vertices: int
    adjacency: NDArray  # A[i,j] = weight of edge (i,j)
    is_directed: bool = False
    vertex_labels: Optional[List[str]] = None
    
    @property
    def n_edges(self) -> int:
        """Number of edges."""
        if self.is_directed:
            return int(np.sum(self.adjacency > 0))
        return int(np.sum(self.adjacency > 0) // 2)
    
    @property
    def degree_matrix(self) -> NDArray:
        """D[i,i] = deg(i)."""
        degrees = np.sum(self.adjacency, axis=1)
        return np.diag(degrees)
    
    @property
    def degrees(self) -> NDArray:
        """Degree sequence."""
        return np.sum(self.adjacency, axis=1)
    
    def is_connected(self) -> bool:
        """Check if graph is connected via Fiedler value."""
        L = self.laplacian
        eigenvalues = np.linalg.eigvalsh(L)
        eigenvalues.sort()
        return eigenvalues[1] > 1e-10
    
    @property
    def laplacian(self) -> NDArray:
        """Unnormalized Laplacian L = D - A."""
        return self.degree_matrix - self.adjacency
    
    @property
    def normalized_laplacian(self) -> NDArray:
        """
        Normalized Laplacian L_norm = D^{-1/2} L D^{-1/2}.
        
        Eigenvalues in [0, 2].
        """
        D = self.degree_matrix
        D_inv_sqrt = np.diag(1.0 / np.sqrt(np.diag(D) + 1e-10))
        L = self.laplacian
        return D_inv_sqrt @ L @ D_inv_sqrt
    
    @property
    def random_walk_laplacian(self) -> NDArray:
        """
        Random walk Laplacian L_rw = D^{-1} L = I - D^{-1} A.
        """
        D_inv = np.diag(1.0 / (np.diag(self.degree_matrix) + 1e-10))
        return D_inv @ self.laplacian
    
    @classmethod
    def complete(cls, n: int) -> 'Graph':
        """Complete graph K_n."""
        A = np.ones((n, n)) - np.eye(n)
        return cls(n, A)
    
    @classmethod
    def cycle(cls, n: int) -> 'Graph':
        """Cycle graph C_n."""
        A = np.zeros((n, n))
        for i in range(n):
            A[i, (i+1) % n] = 1
            A[(i+1) % n, i] = 1
        return cls(n, A)
    
    @classmethod
    def path(cls, n: int) -> 'Graph':
        """Path graph P_n."""
        A = np.zeros((n, n))
        for i in range(n-1):
            A[i, i+1] = 1
            A[i+1, i] = 1
        return cls(n, A)
    
    @classmethod
    def random_regular(cls, n: int, d: int, seed: int = None) -> 'Graph':
        """Random d-regular graph (approximate)."""
        if seed is not None:
            np.random.seed(seed)
        A = np.zeros((n, n))
        for i in range(n):
            # Connect to d random neighbors
            available = [j for j in range(n) if j != i and A[i,j] == 0]
            if len(available) >= d - int(np.sum(A[i,:])):
                neighbors = np.random.choice(
                    available, 
                    size=min(d - int(np.sum(A[i,:])), len(available)),
                    replace=False
                )
                for j in neighbors:
                    A[i,j] = A[j,i] = 1
        return cls(n, A)


# ═══════════════════════════════════════════════════════════════════════════════
# SPECTRUM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GraphSpectrum:
    """
    Spectrum of graph Laplacian.
    
    0 = λ₁ ≤ λ₂ ≤ ... ≤ λₙ
    """
    eigenvalues: NDArray
    eigenvectors: NDArray
    laplacian_type: str = "unnormalized"  # or "normalized", "random_walk"
    
    @property
    def fiedler_value(self) -> float:
        """
        λ₂ = algebraic connectivity.
        
        λ₂ > 0 iff graph is connected.
        """
        sorted_eigs = np.sort(self.eigenvalues)
        return float(sorted_eigs[1])
    
    @property
    def fiedler_vector(self) -> NDArray:
        """
        v₂ = Fiedler vector.
        
        Sign determines bipartition.
        """
        idx = np.argsort(self.eigenvalues)
        return self.eigenvectors[:, idx[1]]
    
    @property
    def spectral_gap(self) -> float:
        """λ₂ - λ₁ = λ₂ (since λ₁ = 0)."""
        return self.fiedler_value
    
    @property
    def spectral_radius(self) -> float:
        """λₙ = largest eigenvalue."""
        return float(np.max(self.eigenvalues))
    
    def k_smallest_eigenpairs(self, k: int) -> Tuple[NDArray, NDArray]:
        """Get k smallest eigenvalue/eigenvector pairs."""
        idx = np.argsort(self.eigenvalues)[:k]
        return self.eigenvalues[idx], self.eigenvectors[:, idx]
    
    @classmethod
    def compute(cls, graph: Graph, 
                laplacian_type: str = "unnormalized") -> 'GraphSpectrum':
        """Compute spectrum of graph."""
        if laplacian_type == "unnormalized":
            L = graph.laplacian
        elif laplacian_type == "normalized":
            L = graph.normalized_laplacian
        else:
            L = graph.random_walk_laplacian
        
        eigenvalues, eigenvectors = np.linalg.eigh(L)
        return cls(eigenvalues, eigenvectors, laplacian_type)


# ═══════════════════════════════════════════════════════════════════════════════
# CHEEGER INEQUALITY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CheegerInequality:
    """
    Cheeger inequality: relates spectral gap to isoperimetric ratio.
    
    λ₂/2 ≤ h(G) ≤ √(2λ₂)
    
    where h(G) = min_S |∂S| / min(|S|, |V\S|) is Cheeger constant.
    """
    lambda_2: float
    cheeger_constant: Optional[float] = None
    
    @property
    def lower_bound(self) -> float:
        """λ₂/2 ≤ h(G)."""
        return self.lambda_2 / 2
    
    @property
    def upper_bound(self) -> float:
        """h(G) ≤ √(2λ₂)."""
        return np.sqrt(2 * self.lambda_2)
    
    def is_expander(self, threshold: float = 0.1) -> bool:
        """Check if graph is an expander (large Cheeger constant)."""
        return self.lower_bound > threshold
    
    @staticmethod
    def discrete_continuous_bridge() -> str:
        """The Cheeger inequality bridges discrete and continuous."""
        return """
        Cheeger Inequality: λ₂/2 ≤ h(G) ≤ √(2λ₂)
        
        This bridges:
        - Discrete: h(G) = combinatorial edge expansion
        - Continuous: λ₂ = spectral gap (analytic)
        
        This is the GATEWAY between D-pole and C-pole
        in spectral graph theory.
        """


# ═══════════════════════════════════════════════════════════════════════════════
# SPECTRAL CLUSTERING
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SpectralClustering:
    """
    Spectral clustering algorithm.
    
    1. Compute k smallest eigenvectors of L
    2. Embed vertices in ℝᵏ
    3. Run k-means on embedding
    """
    graph: Graph
    n_clusters: int
    
    def compute_embedding(self) -> NDArray:
        """
        Compute spectral embedding.
        
        Each vertex mapped to (v₂[i], v₃[i], ..., vₖ[i]).
        """
        spectrum = GraphSpectrum.compute(self.graph, "normalized")
        _, eigenvectors = spectrum.k_smallest_eigenpairs(self.n_clusters)
        # Normalize rows
        norms = np.linalg.norm(eigenvectors, axis=1, keepdims=True)
        return eigenvectors / (norms + 1e-10)
    
    def cluster(self, max_iter: int = 100) -> NDArray:
        """
        Perform spectral clustering.
        
        Returns cluster assignments.
        """
        embedding = self.compute_embedding()
        n = self.graph.n_vertices
        k = self.n_clusters
        
        # Simple k-means
        np.random.seed(42)
        centers = embedding[np.random.choice(n, k, replace=False)]
        
        for _ in range(max_iter):
            # Assign to nearest center
            dists = np.sum((embedding[:, None, :] - centers[None, :, :]) ** 2, axis=2)
            labels = np.argmin(dists, axis=1)
            
            # Update centers
            new_centers = np.zeros_like(centers)
            for i in range(k):
                mask = labels == i
                if np.any(mask):
                    new_centers[i] = embedding[mask].mean(axis=0)
                else:
                    new_centers[i] = centers[i]
            
            if np.allclose(centers, new_centers):
                break
            centers = new_centers
        
        return labels
    
    def fiedler_bipartition(self) -> Tuple[NDArray, NDArray]:
        """
        Bipartition using Fiedler vector.
        
        S = {i : v₂[i] ≥ 0}, S̄ = {i : v₂[i] < 0}
        """
        spectrum = GraphSpectrum.compute(self.graph)
        fiedler = spectrum.fiedler_vector
        S = np.where(fiedler >= 0)[0]
        S_bar = np.where(fiedler < 0)[0]
        return S, S_bar


# ═══════════════════════════════════════════════════════════════════════════════
# GRAPH CUTS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GraphCut:
    """
    Graph cut and partition quality.
    """
    S: NDArray  # vertex indices in S
    S_bar: NDArray  # vertex indices in S̄
    graph: Graph
    
    @property
    def cut_size(self) -> float:
        """
        cut(S, S̄) = Σ_{i∈S, j∈S̄} A[i,j]
        """
        return float(np.sum(self.graph.adjacency[np.ix_(self.S, self.S_bar)]))
    
    @property
    def volume_S(self) -> float:
        """vol(S) = Σ_{i∈S} deg(i)."""
        return float(np.sum(self.graph.degrees[self.S]))
    
    @property
    def volume_S_bar(self) -> float:
        """vol(S̄) = Σ_{i∈S̄} deg(i)."""
        return float(np.sum(self.graph.degrees[self.S_bar]))
    
    @property
    def ratio_cut(self) -> float:
        """
        RatioCut(S, S̄) = cut(S, S̄) · (1/|S| + 1/|S̄|)
        """
        return self.cut_size * (1.0 / len(self.S) + 1.0 / len(self.S_bar))
    
    @property
    def normalized_cut(self) -> float:
        """
        NCut(S, S̄) = cut(S, S̄) · (1/vol(S) + 1/vol(S̄))
        """
        return self.cut_size * (1.0 / self.volume_S + 1.0 / self.volume_S_bar)
    
    @property
    def cheeger_ratio(self) -> float:
        """
        h(S) = cut(S, S̄) / min(|S|, |S̄|)
        """
        return self.cut_size / min(len(self.S), len(self.S_bar))


# ═══════════════════════════════════════════════════════════════════════════════
# EXPANDER GRAPHS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ExpanderGraph:
    """
    Expander graph properties.
    
    Family of graphs with uniformly bounded spectral gap.
    """
    graph: Graph
    
    @property
    def expansion_ratio(self) -> float:
        """Estimate expansion from spectral gap."""
        spectrum = GraphSpectrum.compute(self.graph, "normalized")
        lambda_2 = spectrum.fiedler_value
        return lambda_2 / 2  # Lower bound on Cheeger constant
    
    def is_expander(self, epsilon: float = 0.1) -> bool:
        """
        Check if graph is an ε-expander.
        
        λ₂ ≥ 2ε (equivalently h(G) ≥ ε).
        """
        spectrum = GraphSpectrum.compute(self.graph, "normalized")
        return spectrum.fiedler_value >= 2 * epsilon
    
    @staticmethod
    def ramanujan_bound(d: int) -> float:
        """
        Ramanujan bound for d-regular graphs.
        
        For Ramanujan graphs: λ₂ ≤ 2√(d-1)/d (normalized)
        """
        return 2 * np.sqrt(d - 1) / d


# ═══════════════════════════════════════════════════════════════════════════════
# HEAT KERNEL
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GraphHeatKernel:
    """
    Heat kernel H_t = e^{-tL} on graph.
    
    Diffusion of heat on graph vertices.
    """
    graph: Graph
    
    def kernel(self, t: float) -> NDArray:
        """
        H_t = e^{-tL} = V e^{-tΛ} V^T
        
        where L = VΛV^T is eigendecomposition.
        """
        spectrum = GraphSpectrum.compute(self.graph)
        exp_eigenvalues = np.exp(-t * spectrum.eigenvalues)
        return spectrum.eigenvectors @ np.diag(exp_eigenvalues) @ spectrum.eigenvectors.T
    
    def diffuse(self, initial: NDArray, t: float) -> NDArray:
        """
        Diffuse initial distribution for time t.
        
        f(t) = H_t f(0)
        """
        H_t = self.kernel(t)
        return H_t @ initial
    
    def trace(self, t: float) -> float:
        """
        Trace of heat kernel = Σ e^{-tλᵢ}
        
        Related to partition function.
        """
        spectrum = GraphSpectrum.compute(self.graph)
        return float(np.sum(np.exp(-t * spectrum.eigenvalues)))


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SpectralGraphPoleBridge:
    """
    Bridge between spectral graph theory and pole structure.
    """
    
    @staticmethod
    def psi_pole_as_spectral() -> str:
        """
        Ψ-pole corresponds to spectral decomposition.
        Hierarchical structure from eigenvectors.
        """
        return "Ψ ↔ Spectrum: L = VΛV^T hierarchical decomposition"
    
    @staticmethod
    def c_pole_as_embedding() -> str:
        """
        C-pole corresponds to continuous embedding.
        Spectral embedding in ℝᵏ.
        """
        return "C ↔ Embedding: vertices → ℝᵏ via eigenvectors"
    
    @staticmethod
    def d_pole_as_cuts() -> str:
        """
        D-pole corresponds to discrete cuts.
        Partitions, clusters, combinatorial structure.
        """
        return "D ↔ Cuts: S, S̄ discrete partitions"
    
    @staticmethod
    def gateway_as_cheeger() -> str:
        """
        Gateway corresponds to Cheeger inequality.
        Bridge between discrete cuts and continuous spectrum.
        """
        return "Gateway ↔ Cheeger: λ₂/2 ≤ h(G) ≤ √(2λ₂)"


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def graph(n: int, adjacency: NDArray = None) -> Graph:
    """Create graph."""
    if adjacency is None:
        adjacency = np.zeros((n, n))
    return Graph(n, adjacency)


def graph_spectrum(g: Graph, laplacian_type: str = "unnormalized") -> GraphSpectrum:
    """Compute graph spectrum."""
    return GraphSpectrum.compute(g, laplacian_type)


def spectral_clustering(g: Graph, k: int) -> NDArray:
    """Perform spectral clustering."""
    return SpectralClustering(g, k).cluster()


def fiedler_bipartition(g: Graph) -> Tuple[NDArray, NDArray]:
    """Bipartition using Fiedler vector."""
    return SpectralClustering(g, 2).fiedler_bipartition()


def cheeger_bounds(lambda_2: float) -> Tuple[float, float]:
    """Get Cheeger inequality bounds."""
    cheeger = CheegerInequality(lambda_2)
    return cheeger.lower_bound, cheeger.upper_bound


def heat_kernel(g: Graph, t: float) -> NDArray:
    """Compute heat kernel at time t."""
    return GraphHeatKernel(g).kernel(t)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Graph
    'Graph',
    
    # Spectrum
    'GraphSpectrum',
    
    # Cheeger
    'CheegerInequality',
    
    # Clustering
    'SpectralClustering',
    
    # Cuts
    'GraphCut',
    
    # Expanders
    'ExpanderGraph',
    
    # Heat Kernel
    'GraphHeatKernel',
    
    # Bridge
    'SpectralGraphPoleBridge',
    
    # Functions
    'graph',
    'graph_spectrum',
    'spectral_clustering',
    'fiedler_bipartition',
    'cheeger_bounds',
    'heat_kernel',
]
