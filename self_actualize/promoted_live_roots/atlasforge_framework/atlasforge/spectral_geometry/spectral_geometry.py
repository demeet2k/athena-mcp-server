"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                 SPECTRAL-GEOMETRIC DUALITY MODULE                            ║
║                                                                              ║
║  Platonic Shells, Nodal Surfaces, Laplacian Eigenstructure                  ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Geometry and spectrum are dual perspectives on the same object.          ║
║    The shape of a domain determines its eigenvalues, and vice versa.        ║
║                                                                              ║
║  "Can you hear the shape of a drum?" - Mark Kac (1966)                      ║
║                                                                              ║
║  Key Relationships:                                                          ║
║    - Weyl law: N(λ) ~ (Area/4π)λ as λ → ∞                                   ║
║    - Nodal domains: # ≤ n for n-th eigenfunction                            ║
║    - Spectral gap ↔ connectivity/expansion                                  ║
║    - Heat kernel ↔ geometric distance                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Callable, Any
from enum import Enum, auto
import numpy as np
from numpy.typing import NDArray
from scipy.special import sph_harm


# ═══════════════════════════════════════════════════════════════════════════════
# PLATONIC SOLIDS
# ═══════════════════════════════════════════════════════════════════════════════

class PlatonicSolid(Enum):
    """The five Platonic solids."""
    TETRAHEDRON = "tetrahedron"   # 4 faces, 4 vertices, 6 edges
    CUBE = "cube"                  # 6 faces, 8 vertices, 12 edges
    OCTAHEDRON = "octahedron"      # 8 faces, 6 vertices, 12 edges
    DODECAHEDRON = "dodecahedron"  # 12 faces, 20 vertices, 30 edges
    ICOSAHEDRON = "icosahedron"    # 20 faces, 12 vertices, 30 edges


@dataclass
class PlatonicShell:
    """
    Platonic solid as a shell/surface for spectral analysis.
    
    Properties:
        - Highly symmetric discrete geometry
        - Finite-dimensional Laplacian
        - Rich symmetry group action on eigenfunctions
    """
    solid: PlatonicSolid
    radius: float = 1.0
    
    _vertices: NDArray[np.float64] = field(default=None, repr=False)
    _faces: List[List[int]] = field(default=None, repr=False)
    _edges: List[Tuple[int, int]] = field(default=None, repr=False)
    
    def __post_init__(self):
        self._build_geometry()
    
    def _build_geometry(self):
        """Construct vertices, faces, edges for the solid."""
        if self.solid == PlatonicSolid.TETRAHEDRON:
            self._build_tetrahedron()
        elif self.solid == PlatonicSolid.CUBE:
            self._build_cube()
        elif self.solid == PlatonicSolid.OCTAHEDRON:
            self._build_octahedron()
        elif self.solid == PlatonicSolid.DODECAHEDRON:
            self._build_dodecahedron()
        elif self.solid == PlatonicSolid.ICOSAHEDRON:
            self._build_icosahedron()
        
        # Normalize to unit sphere and scale
        norms = np.linalg.norm(self._vertices, axis=1, keepdims=True)
        self._vertices = self._vertices / norms * self.radius
    
    def _build_tetrahedron(self):
        """Regular tetrahedron."""
        self._vertices = np.array([
            [1, 1, 1],
            [1, -1, -1],
            [-1, 1, -1],
            [-1, -1, 1]
        ], dtype=np.float64)
        self._faces = [[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]]
        self._edges = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
    
    def _build_cube(self):
        """Regular cube."""
        self._vertices = np.array([
            [1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
            [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1]
        ], dtype=np.float64)
        self._faces = [
            [0, 1, 3, 2], [4, 5, 7, 6],  # Front, back
            [0, 1, 5, 4], [2, 3, 7, 6],  # Top, bottom
            [0, 2, 6, 4], [1, 3, 7, 5]   # Left, right
        ]
        self._edges = [
            (0,1), (1,3), (3,2), (2,0),
            (4,5), (5,7), (7,6), (6,4),
            (0,4), (1,5), (2,6), (3,7)
        ]
    
    def _build_octahedron(self):
        """Regular octahedron (dual of cube)."""
        self._vertices = np.array([
            [1, 0, 0], [-1, 0, 0],
            [0, 1, 0], [0, -1, 0],
            [0, 0, 1], [0, 0, -1]
        ], dtype=np.float64)
        self._faces = [
            [0, 2, 4], [0, 4, 3], [0, 3, 5], [0, 5, 2],
            [1, 2, 4], [1, 4, 3], [1, 3, 5], [1, 5, 2]
        ]
        self._edges = [
            (0,2), (0,3), (0,4), (0,5),
            (1,2), (1,3), (1,4), (1,5),
            (2,4), (4,3), (3,5), (5,2)
        ]
    
    def _build_icosahedron(self):
        """Regular icosahedron."""
        phi = (1 + np.sqrt(5)) / 2  # Golden ratio
        self._vertices = np.array([
            [0, 1, phi], [0, -1, phi], [0, 1, -phi], [0, -1, -phi],
            [1, phi, 0], [-1, phi, 0], [1, -phi, 0], [-1, -phi, 0],
            [phi, 0, 1], [-phi, 0, 1], [phi, 0, -1], [-phi, 0, -1]
        ], dtype=np.float64)
        # Faces and edges for icosahedron
        self._faces = [
            [0, 1, 8], [0, 8, 4], [0, 4, 5], [0, 5, 9], [0, 9, 1],
            [1, 6, 8], [8, 6, 10], [8, 10, 4], [4, 10, 2], [4, 2, 5],
            [5, 2, 11], [5, 11, 9], [9, 11, 7], [9, 7, 1], [1, 7, 6],
            [3, 6, 7], [3, 7, 11], [3, 11, 2], [3, 2, 10], [3, 10, 6]
        ]
        self._edges = list(set(
            tuple(sorted([f[i], f[(i+1)%3]])) for f in self._faces for i in range(3)
        ))
    
    def _build_dodecahedron(self):
        """Regular dodecahedron (dual of icosahedron)."""
        phi = (1 + np.sqrt(5)) / 2
        a, b = 1/phi, phi
        self._vertices = np.array([
            # Cube vertices
            [1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
            [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1],
            # Rectangle vertices in xy plane
            [0, a, b], [0, -a, b], [0, a, -b], [0, -a, -b],
            # Rectangle vertices in yz plane
            [a, b, 0], [-a, b, 0], [a, -b, 0], [-a, -b, 0],
            # Rectangle vertices in xz plane
            [b, 0, a], [-b, 0, a], [b, 0, -a], [-b, 0, -a]
        ], dtype=np.float64)
        # Simplified faces list
        self._faces = [[0, 8, 9, 2, 16], [0, 16, 18, 1, 12]]  # Partial
        self._edges = [(i, j) for i in range(20) for j in range(i+1, 20)
                      if np.linalg.norm(self._vertices[i] - self._vertices[j]) < 1.3]
    
    @property
    def n_vertices(self) -> int:
        return len(self._vertices)
    
    @property
    def n_edges(self) -> int:
        return len(self._edges)
    
    @property
    def n_faces(self) -> int:
        return len(self._faces)
    
    @property
    def euler_characteristic(self) -> int:
        """V - E + F = 2 for convex polyhedra."""
        return self.n_vertices - self.n_edges + self.n_faces
    
    @property
    def vertices(self) -> NDArray[np.float64]:
        return self._vertices.copy()
    
    def graph_laplacian(self) -> NDArray[np.float64]:
        """
        Discrete Laplacian on the vertex graph.
        
        L = D - A where D = degree matrix, A = adjacency matrix.
        """
        n = self.n_vertices
        A = np.zeros((n, n))
        
        for i, j in self._edges:
            A[i, j] = 1
            A[j, i] = 1
        
        D = np.diag(A.sum(axis=1))
        return D - A
    
    def spectrum(self) -> NDArray[np.float64]:
        """Eigenvalues of the graph Laplacian."""
        L = self.graph_laplacian()
        eigvals = np.linalg.eigvalsh(L)
        return np.sort(eigvals)
    
    def eigenpairs(self) -> Tuple[NDArray, NDArray]:
        """Eigenvalues and eigenvectors of graph Laplacian."""
        L = self.graph_laplacian()
        eigvals, eigvecs = np.linalg.eigh(L)
        order = np.argsort(eigvals)
        return eigvals[order], eigvecs[:, order]
    
    @property
    def spectral_gap(self) -> float:
        """λ₂ - λ₁ = λ₂ (since λ₁ = 0)."""
        spec = self.spectrum()
        return spec[1] if len(spec) > 1 else 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# SPHERICAL HARMONICS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SphericalHarmonic:
    """
    Spherical harmonic Y_ℓ^m(θ, φ).
    
    Properties:
        - Eigenfunction of Laplacian on S²
        - Eigenvalue: ℓ(ℓ+1)
        - Degeneracy: 2ℓ+1
        - Orthonormal basis for L²(S²)
    """
    ell: int  # Degree (ℓ ≥ 0)
    m: int    # Order (-ℓ ≤ m ≤ ℓ)
    
    def __post_init__(self):
        if self.ell < 0:
            raise ValueError(f"ℓ must be non-negative, got {self.ell}")
        if abs(self.m) > self.ell:
            raise ValueError(f"|m| must be ≤ ℓ, got m={self.m}, ℓ={self.ell}")
    
    @property
    def eigenvalue(self) -> float:
        """Laplacian eigenvalue: -ℓ(ℓ+1)."""
        return -self.ell * (self.ell + 1)
    
    def __call__(self, theta: NDArray, phi: NDArray) -> NDArray[np.complex128]:
        """
        Evaluate Y_ℓ^m(θ, φ).
        
        Args:
            theta: Colatitude (0 to π)
            phi: Azimuth (0 to 2π)
        """
        return sph_harm(self.m, self.ell, phi, theta)
    
    def evaluate_cartesian(self, x: NDArray, y: NDArray, z: NDArray) -> NDArray[np.complex128]:
        """Evaluate at Cartesian coordinates on unit sphere."""
        r = np.sqrt(x**2 + y**2 + z**2)
        theta = np.arccos(z / r)
        phi = np.arctan2(y, x)
        return self(theta, phi)
    
    @property
    def nodal_count(self) -> int:
        """Number of nodal great circles."""
        return self.ell


@dataclass
class SphericalHarmonicExpansion:
    """
    Expansion in spherical harmonics up to degree ℓ_max.
    
    f(θ, φ) = Σ_{ℓ=0}^{ℓ_max} Σ_{m=-ℓ}^{ℓ} c_{ℓm} Y_ℓ^m(θ, φ)
    """
    ell_max: int
    coefficients: Dict[Tuple[int, int], complex] = field(default_factory=dict)
    
    @property
    def n_coefficients(self) -> int:
        """Total number of coefficients: (ℓ_max + 1)²."""
        return (self.ell_max + 1) ** 2
    
    def set_coefficient(self, ell: int, m: int, value: complex):
        """Set coefficient c_{ℓm}."""
        if ell > self.ell_max:
            raise ValueError(f"ℓ={ell} exceeds ℓ_max={self.ell_max}")
        self.coefficients[(ell, m)] = value
    
    def get_coefficient(self, ell: int, m: int) -> complex:
        """Get coefficient c_{ℓm}."""
        return self.coefficients.get((ell, m), 0.0)
    
    def __call__(self, theta: NDArray, phi: NDArray) -> NDArray[np.complex128]:
        """Evaluate expansion at (θ, φ)."""
        result = np.zeros_like(theta, dtype=np.complex128)
        
        for (ell, m), c in self.coefficients.items():
            Y = SphericalHarmonic(ell, m)
            result += c * Y(theta, phi)
        
        return result
    
    def power_spectrum(self) -> NDArray[np.float64]:
        """
        Angular power spectrum C_ℓ = Σ_m |c_{ℓm}|².
        """
        spectrum = np.zeros(self.ell_max + 1)
        for (ell, m), c in self.coefficients.items():
            spectrum[ell] += abs(c) ** 2
        return spectrum


# ═══════════════════════════════════════════════════════════════════════════════
# NODAL DOMAINS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class NodalDomain:
    """
    A nodal domain is a connected component of the sign set of an eigenfunction.
    
    For f: Ω → ℝ, nodal set = {x : f(x) = 0}
    Nodal domains = connected components of Ω \ (nodal set)
    
    Courant nodal domain theorem:
        The n-th eigenfunction has at most n nodal domains.
    """
    eigenfunction_index: int
    domain_values: NDArray[np.float64]  # Sign pattern on domain
    
    def count_nodal_domains(self, adjacency: NDArray) -> int:
        """
        Count nodal domains using connected components.
        
        Args:
            adjacency: Adjacency matrix of discretized domain
        """
        n = len(self.domain_values)
        signs = np.sign(self.domain_values)
        
        # Find connected components of each sign
        visited = np.zeros(n, dtype=bool)
        count = 0
        
        for start in range(n):
            if visited[start] or signs[start] == 0:
                continue
            
            # BFS from this node
            sign = signs[start]
            queue = [start]
            visited[start] = True
            
            while queue:
                node = queue.pop(0)
                for neighbor in range(n):
                    if adjacency[node, neighbor] and not visited[neighbor]:
                        if signs[neighbor] == sign:
                            visited[neighbor] = True
                            queue.append(neighbor)
            
            count += 1
        
        return count
    
    def courant_bound(self) -> int:
        """Upper bound from Courant theorem."""
        return self.eigenfunction_index


@dataclass
class NodalAnalysis:
    """
    Analyze nodal structure of eigenfunctions on a domain.
    """
    eigenvectors: NDArray[np.float64]  # n × n_modes
    adjacency: NDArray[np.float64]     # n × n adjacency
    
    def nodal_count(self, mode_index: int) -> int:
        """Count nodal domains for given mode."""
        domain = NodalDomain(
            eigenfunction_index=mode_index + 1,
            domain_values=self.eigenvectors[:, mode_index]
        )
        return domain.count_nodal_domains(self.adjacency)
    
    def nodal_statistics(self, max_modes: int = None) -> Dict[str, Any]:
        """Statistics of nodal domain counts."""
        n_modes = self.eigenvectors.shape[1]
        if max_modes:
            n_modes = min(n_modes, max_modes)
        
        counts = [self.nodal_count(i) for i in range(n_modes)]
        bounds = list(range(1, n_modes + 1))
        
        return {
            'counts': counts,
            'courant_bounds': bounds,
            'violations': sum(c > b for c, b in zip(counts, bounds)),
            'saturation_fraction': np.mean([c/b for c, b in zip(counts, bounds)])
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SPECTRAL GEOMETRY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SpectralGeometry:
    """
    Spectral invariants of a geometric domain.
    
    From spectrum → geometry:
        - Weyl law: Area from eigenvalue asymptotics
        - Heat invariants: Volume, surface area, curvature
        - Spectral gap: Connectivity/diameter bounds
    
    From geometry → spectrum:
        - Laplacian eigenvalues from mesh
        - Cheeger constant from geometry
    """
    laplacian: NDArray[np.float64]
    
    _eigenvalues: NDArray[np.float64] = field(default=None, repr=False)
    _eigenvectors: NDArray[np.float64] = field(default=None, repr=False)
    
    def __post_init__(self):
        self._compute_spectrum()
    
    def _compute_spectrum(self):
        """Compute eigendecomposition."""
        eigvals, eigvecs = np.linalg.eigh(self.laplacian)
        order = np.argsort(eigvals)
        self._eigenvalues = eigvals[order]
        self._eigenvectors = eigvecs[:, order]
    
    @property
    def spectrum(self) -> NDArray[np.float64]:
        return self._eigenvalues
    
    @property
    def eigenvectors(self) -> NDArray[np.float64]:
        return self._eigenvectors
    
    @property
    def spectral_gap(self) -> float:
        """λ₂ - λ₁ (first nonzero eigenvalue for graph Laplacian)."""
        return self._eigenvalues[1] - self._eigenvalues[0]
    
    def counting_function(self, lambda_max: float) -> int:
        """N(λ) = #{eigenvalues ≤ λ}."""
        return np.sum(self._eigenvalues <= lambda_max)
    
    def heat_trace(self, t: float) -> float:
        """
        Heat kernel trace Z(t) = Σ exp(-λ_n t).
        
        Encodes geometric information via small-t asymptotics.
        """
        return np.sum(np.exp(-self._eigenvalues * t))
    
    def heat_kernel_diagonal(self, t: float) -> NDArray[np.float64]:
        """
        Diagonal of heat kernel K(x, x, t).
        
        K(x, x, t) = Σ_n exp(-λ_n t) |φ_n(x)|²
        """
        exp_factors = np.exp(-self._eigenvalues * t)
        return np.sum(exp_factors * self._eigenvectors**2, axis=1)
    
    def spectral_distance(self, i: int, j: int, n_modes: int = 10) -> float:
        """
        Spectral embedding distance between vertices i and j.
        
        Uses first n_modes eigenvectors as coordinates.
        """
        coords_i = self._eigenvectors[i, 1:n_modes+1]  # Skip constant mode
        coords_j = self._eigenvectors[j, 1:n_modes+1]
        return np.linalg.norm(coords_i - coords_j)
    
    def weyl_estimate_2d(self) -> float:
        """
        Estimate area from eigenvalue asymptotics (2D Weyl law).
        
        N(λ) ~ (Area/4π)λ as λ → ∞
        """
        # Fit to large eigenvalues
        large_indices = np.arange(len(self._eigenvalues) // 2, len(self._eigenvalues))
        lambdas = self._eigenvalues[large_indices]
        counts = large_indices + 1
        
        # Linear fit: N = (Area/4π) λ
        slope, _ = np.polyfit(lambdas, counts, 1)
        area_estimate = slope * 4 * np.pi
        
        return area_estimate


# ═══════════════════════════════════════════════════════════════════════════════
# SPECTRAL-GEOMETRIC TRANSLATOR
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SpectralGeometricTranslator:
    """
    Translate between spectral and geometric representations.
    
    This is the core duality engine connecting:
        - SQUARE (discrete vertices) ↔ FLOWER (eigenfunctions)
        - Local geometry ↔ Global spectrum
    """
    
    def geometry_to_spectrum(self, vertices: NDArray, edges: List[Tuple[int, int]]) -> SpectralGeometry:
        """
        Build spectral geometry from vertex/edge data.
        """
        n = len(vertices)
        A = np.zeros((n, n))
        
        for i, j in edges:
            A[i, j] = 1
            A[j, i] = 1
        
        D = np.diag(A.sum(axis=1))
        L = D - A
        
        return SpectralGeometry(laplacian=L)
    
    def spectrum_to_embedding(self, spec_geom: SpectralGeometry, dim: int = 3) -> NDArray[np.float64]:
        """
        Spectral embedding: use eigenvectors as coordinates.
        
        Maps abstract graph to Euclidean space.
        """
        n = spec_geom.laplacian.shape[0]
        
        # Use eigenvectors 1 through dim (skip constant)
        coords = spec_geom.eigenvectors[:, 1:dim+1].copy()
        
        # Scale by inverse sqrt of eigenvalue
        for i in range(dim):
            if spec_geom.spectrum[i+1] > 1e-10:
                coords[:, i] /= np.sqrt(spec_geom.spectrum[i+1])
        
        return coords
    
    def diffusion_distance(self, spec_geom: SpectralGeometry, t: float) -> NDArray[np.float64]:
        """
        Diffusion distance matrix D_t(i,j).
        
        D_t²(i,j) = Σ_k exp(-2λ_k t) (φ_k(i) - φ_k(j))²
        """
        n = spec_geom.laplacian.shape[0]
        eigvals = spec_geom.spectrum
        eigvecs = spec_geom.eigenvectors
        
        weights = np.exp(-2 * eigvals * t)
        
        D = np.zeros((n, n))
        for i in range(n):
            for j in range(i+1, n):
                diff = eigvecs[i, :] - eigvecs[j, :]
                D[i, j] = np.sqrt(np.sum(weights * diff**2))
                D[j, i] = D[i, j]
        
        return D


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def platonic_spectrum(solid: str) -> NDArray[np.float64]:
    """Get spectrum of Platonic solid graph."""
    solid_map = {
        'tetrahedron': PlatonicSolid.TETRAHEDRON,
        'cube': PlatonicSolid.CUBE,
        'octahedron': PlatonicSolid.OCTAHEDRON,
        'dodecahedron': PlatonicSolid.DODECAHEDRON,
        'icosahedron': PlatonicSolid.ICOSAHEDRON
    }
    shell = PlatonicShell(solid_map[solid.lower()])
    return shell.spectrum()


def spherical_harmonic(ell: int, m: int, theta: NDArray, phi: NDArray) -> NDArray:
    """Evaluate spherical harmonic Y_ℓ^m."""
    Y = SphericalHarmonic(ell, m)
    return Y(theta, phi)


def spectral_embedding(laplacian: NDArray, dim: int = 3) -> NDArray:
    """Spectral embedding of graph from Laplacian."""
    sg = SpectralGeometry(laplacian)
    translator = SpectralGeometricTranslator()
    return translator.spectrum_to_embedding(sg, dim)


def heat_kernel_trace(laplacian: NDArray, t: float) -> float:
    """Compute heat kernel trace Z(t)."""
    sg = SpectralGeometry(laplacian)
    return sg.heat_trace(t)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Platonic solids
    'PlatonicSolid',
    'PlatonicShell',
    
    # Spherical harmonics
    'SphericalHarmonic',
    'SphericalHarmonicExpansion',
    
    # Nodal analysis
    'NodalDomain',
    'NodalAnalysis',
    
    # Spectral geometry
    'SpectralGeometry',
    'SpectralGeometricTranslator',
    
    # Functions
    'platonic_spectrum',
    'spherical_harmonic',
    'spectral_embedding',
    'heat_kernel_trace',
]
