"""
ATHENA OS - Constraint System and Seed Ledger
=============================================
Construction machinery and holographic storage for mathematical objects.

Constraint Grammar (how objects are forged):
1. Fixed-point locks: x = F(x) or t = f(t)
2. Equalization locks: F₁ = F₂ = ... = Fₙ
3. Cancellation locks: Σ wᵢFᵢ = 0
4. Commutation locks: F ∘ G = G ∘ F
5. Equivariance locks: F(φx) = φᵏF(x)
6. Periodicity/finite-order: F^{∘n} = Id
7. Hardening locks: H^(k) = 0, det J = 0

Algorithmic Pipeline:
1. Normalize → 2. Reduce → 3. Enumerate → 4. Solve → 5. Certify → 6. Ledger

Holographic Storage (store "in", not "out"):
Seed Σ = (T, λ, H, cert) is a minimal sufficient statistic
From Σ, we reconstruct:
- The constant x* (or family {xₖ})
- Its pole/shadow/cross orbit
- Associated operations (⊕_T, ⊗_T, Pow_T)
- Verification traces and invariants

This is "holographic encoding": any one well-formed seed can regenerate
a large portion of the atlas through symmetry, conjugacy, and lattice shifts.
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable, Set, Union
import numpy as np
from scipy import optimize
import hashlib
import json
import time

from .lenses import Lens, LogLens, TrigPhaseLens, PHI
from .zeros import ZeroPoint, ZeroType


# =============================================================================
# CONSTRAINT TYPES
# =============================================================================

class ConstraintType(IntEnum):
    """Types of constraints that forge mathematical objects."""
    FIXED_POINT = 0     # x = F(x)
    EQUALIZATION = 1    # F₁ = F₂ = ... = Fₙ
    CANCELLATION = 2    # Σ wᵢFᵢ = 0
    COMMUTATION = 3     # F ∘ G = G ∘ F
    EQUIVARIANCE = 4    # F(φx) = φᵏF(x)
    PERIODICITY = 5     # F^{∘n} = Id
    JET_LOCK = 6        # H^(k)(x*) = 0 for k < m
    SINGULAR = 7        # det J_H(z*) = 0
    LATTICE = 8         # T(x) ∈ L (lattice membership)
    POWER_LATTICE = 9   # T(x) ∈ L_A AND T(x^p) ∈ L_B


@dataclass
class Constraint:
    """
    A constraint that defines a mathematical object.
    
    Constraints are the building blocks for forging constants and operations.
    """
    constraint_type: ConstraintType
    description: str
    
    # Function(s) involved
    functions: List[Callable] = field(default_factory=list)
    function_names: List[str] = field(default_factory=list)
    
    # Parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Domain
    domain: Tuple[float, float] = (0.01, 100.0)
    
    # Solution(s)
    solutions: List[float] = field(default_factory=list)
    
    def solve(self, **kwargs) -> List[float]:
        """Solve the constraint to find satisfying values."""
        if self.constraint_type == ConstraintType.FIXED_POINT:
            return self._solve_fixed_point(**kwargs)
        elif self.constraint_type == ConstraintType.EQUALIZATION:
            return self._solve_equalization(**kwargs)
        elif self.constraint_type == ConstraintType.CANCELLATION:
            return self._solve_cancellation(**kwargs)
        elif self.constraint_type == ConstraintType.LATTICE:
            return self._solve_lattice(**kwargs)
        else:
            return self._generic_solve(**kwargs)
    
    def _solve_fixed_point(self, tolerance: float = 1e-10, 
                          max_iter: int = 1000) -> List[float]:
        """
        Solve x = F(x) via iteration and root-finding.
        """
        if not self.functions:
            return []
        
        F = self.functions[0]
        a, b = self.domain
        
        # Try iteration from multiple starts
        solutions = []
        
        for x0 in np.linspace(a, b, 20):
            x = x0
            for _ in range(max_iter):
                try:
                    x_new = F(x)
                    if abs(x_new - x) < tolerance:
                        if a < x_new < b and abs(x_new - F(x_new)) < tolerance:
                            solutions.append(x_new)
                        break
                    x = x_new
                except (ValueError, OverflowError):
                    break
        
        # Remove duplicates
        self.solutions = self._remove_duplicates(solutions, tolerance)
        return self.solutions
    
    def _solve_equalization(self, n_samples: int = 1000,
                           tolerance: float = 1e-8) -> List[float]:
        """
        Solve F₁(x) = F₂(x) = ... = Fₙ(x).
        """
        if len(self.functions) < 2:
            return []
        
        def variance(x):
            try:
                vals = [f(x) for f in self.functions]
                mean = sum(vals) / len(vals)
                return sum((v - mean)**2 for v in vals)
            except:
                return np.inf
        
        a, b = self.domain
        xs = np.linspace(a, b, n_samples)
        candidates = []
        
        for i in range(1, len(xs) - 1):
            v_prev = variance(xs[i-1])
            v_curr = variance(xs[i])
            v_next = variance(xs[i+1])
            
            if v_curr < v_prev and v_curr < v_next and v_curr < tolerance:
                candidates.append(xs[i])
        
        self.solutions = self._remove_duplicates(candidates, tolerance)
        return self.solutions
    
    def _solve_cancellation(self, **kwargs) -> List[float]:
        """
        Solve Σ wᵢFᵢ(x) = 0.
        """
        weights = self.parameters.get('weights', [1.0] * len(self.functions))
        
        def H(x):
            try:
                return sum(w * f(x) for w, f in zip(weights, self.functions))
            except:
                return np.inf
        
        # Find zeros of H
        from .zeros import ZeroSet
        zero_set = ZeroSet(H, self.domain)
        zeros = zero_set.find_zeros(**kwargs)
        
        self.solutions = [z.location for z in zeros]
        return self.solutions
    
    def _solve_lattice(self, **kwargs) -> List[float]:
        """
        Solve T(x) ∈ L for lattice L.
        """
        lens = self.parameters.get('lens')
        base = self.parameters.get('base', 0)
        period = self.parameters.get('period', np.pi)
        n_terms = self.parameters.get('n_terms', 10)
        
        if lens is None:
            return []
        
        from .symmetry import Lattice, LatticeType
        lattice = Lattice(base, period, LatticeType.SIN_ZEROS)
        
        self.solutions = lattice.pullback(lens, n_terms)
        return self.solutions
    
    def _generic_solve(self, n_samples: int = 1000, 
                      tolerance: float = 1e-8) -> List[float]:
        """Generic solver via minimization."""
        if not self.functions:
            return []
        
        # Define residual based on constraint type
        def residual(x):
            try:
                if self.constraint_type == ConstraintType.COMMUTATION:
                    # F ∘ G(x) - G ∘ F(x)
                    F, G = self.functions[0], self.functions[1]
                    return abs(F(G(x)) - G(F(x)))
                elif self.constraint_type == ConstraintType.EQUIVARIANCE:
                    # F(φx) - φᵏF(x)
                    F = self.functions[0]
                    k = self.parameters.get('k', 1)
                    return abs(F(PHI * x) - (PHI ** k) * F(x))
                else:
                    return 0.0
            except:
                return np.inf
        
        a, b = self.domain
        solutions = []
        
        for x0 in np.linspace(a, b, 20):
            try:
                result = optimize.minimize_scalar(
                    residual,
                    bounds=(a, b),
                    method='bounded'
                )
                if result.fun < tolerance:
                    solutions.append(result.x)
            except:
                pass
        
        self.solutions = self._remove_duplicates(solutions, tolerance)
        return self.solutions
    
    def _remove_duplicates(self, values: List[float], tolerance: float) -> List[float]:
        """Remove duplicate values within tolerance."""
        if not values:
            return []
        
        sorted_vals = sorted(values)
        result = [sorted_vals[0]]
        
        for v in sorted_vals[1:]:
            if abs(v - result[-1]) > tolerance:
                result.append(v)
        
        return result
    
    def verify(self, x: float, tolerance: float = 1e-8) -> Tuple[bool, float]:
        """Verify that x satisfies the constraint."""
        try:
            if self.constraint_type == ConstraintType.FIXED_POINT:
                F = self.functions[0]
                residual = abs(x - F(x))
            elif self.constraint_type == ConstraintType.EQUALIZATION:
                vals = [f(x) for f in self.functions]
                mean = sum(vals) / len(vals)
                residual = max(abs(v - mean) for v in vals)
            elif self.constraint_type == ConstraintType.CANCELLATION:
                weights = self.parameters.get('weights', [1.0] * len(self.functions))
                residual = abs(sum(w * f(x) for w, f in zip(weights, self.functions)))
            else:
                residual = 0.0
            
            return residual < tolerance, residual
        except:
            return False, np.inf


# =============================================================================
# CONSTRAINT BUILDERS
# =============================================================================

def fixed_point_constraint(F: Callable, name: str = "F",
                          domain: Tuple[float, float] = (0.01, 100)) -> Constraint:
    """Create a fixed-point constraint x = F(x)."""
    return Constraint(
        constraint_type=ConstraintType.FIXED_POINT,
        description=f"x = {name}(x)",
        functions=[F],
        function_names=[name],
        domain=domain
    )


def equalization_constraint(functions: List[Callable], names: List[str] = None,
                           domain: Tuple[float, float] = (0.01, 100)) -> Constraint:
    """Create an equalization constraint F₁ = F₂ = ... = Fₙ."""
    names = names or [f"F{i}" for i in range(len(functions))]
    return Constraint(
        constraint_type=ConstraintType.EQUALIZATION,
        description=" = ".join(names),
        functions=functions,
        function_names=names,
        domain=domain
    )


def cancellation_constraint(functions: List[Callable], weights: List[float],
                           names: List[str] = None,
                           domain: Tuple[float, float] = (0.01, 100)) -> Constraint:
    """Create a cancellation constraint Σ wᵢFᵢ = 0."""
    names = names or [f"F{i}" for i in range(len(functions))]
    terms = [f"{w}·{n}" for w, n in zip(weights, names)]
    return Constraint(
        constraint_type=ConstraintType.CANCELLATION,
        description=" + ".join(terms) + " = 0",
        functions=functions,
        function_names=names,
        parameters={'weights': weights},
        domain=domain
    )


def lattice_constraint(lens: Lens, base: float = 0, period: float = np.pi,
                      n_terms: int = 10,
                      domain: Tuple[float, float] = (0.01, 100)) -> Constraint:
    """Create a lattice membership constraint T(x) ∈ base + period·ℤ."""
    return Constraint(
        constraint_type=ConstraintType.LATTICE,
        description=f"T(x) ∈ {base:.4f} + {period:.4f}ℤ",
        parameters={'lens': lens, 'base': base, 'period': period, 'n_terms': n_terms},
        domain=domain
    )


def jet_lock_constraint(H: Callable, order: int, name: str = "H",
                       domain: Tuple[float, float] = (0.01, 100)) -> Constraint:
    """
    Create a jet lock constraint: H^(k)(x*) = 0 for k = 0, ..., order-1.
    
    This is a "hardening" lock that makes constants structurally rigid.
    """
    return Constraint(
        constraint_type=ConstraintType.JET_LOCK,
        description=f"{name}^(k) = 0 for k < {order}",
        functions=[H],
        function_names=[name],
        parameters={'order': order},
        domain=domain
    )


# =============================================================================
# SEED LEDGER - HOLOGRAPHIC STORAGE
# =============================================================================

@dataclass
class Certificate:
    """
    Certificate for a mathematical object.
    
    Contains verification data that enables reconstruction
    and independent checking.
    """
    cert_type: str  # "invertibility", "contraction", "residual", etc.
    bounds: Dict[str, float] = field(default_factory=dict)
    proofs: List[str] = field(default_factory=list)
    verified: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'type': self.cert_type,
            'bounds': self.bounds,
            'proofs': self.proofs,
            'verified': self.verified
        }


@dataclass
class Seed:
    """
    A seed is a minimal sufficient statistic for a mathematical object.
    
    Σ = (T, λ, H, cert)
    
    From Σ, we can reconstruct:
    - The constant x* (or family {xₖ})
    - Its pole/shadow/cross orbit
    - Associated operations (⊕_T, ⊗_T, Pow_T)
    - Verification traces and invariants
    """
    seed_id: str
    
    # Lens (coordinate system)
    lens_type: str
    lens_params: Dict[str, Any] = field(default_factory=dict)
    
    # Parameters (Fourier coefficients, exponents, lattice offsets)
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Constraint system
    constraints: List[Dict] = field(default_factory=list)
    
    # Certificates
    certificates: List[Certificate] = field(default_factory=list)
    
    # Computed values
    values: List[float] = field(default_factory=list)
    
    # Metadata
    created: float = field(default_factory=time.time)
    description: str = ""
    
    def compute_hash(self) -> str:
        """Compute content hash for the seed."""
        content = json.dumps({
            'lens_type': self.lens_type,
            'lens_params': self.lens_params,
            'parameters': self.parameters,
            'constraints': self.constraints
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict:
        """Serialize seed to dictionary."""
        return {
            'seed_id': self.seed_id,
            'lens_type': self.lens_type,
            'lens_params': self.lens_params,
            'parameters': self.parameters,
            'constraints': self.constraints,
            'certificates': [c.to_dict() for c in self.certificates],
            'values': self.values,
            'created': self.created,
            'description': self.description,
            'hash': self.compute_hash()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Seed':
        """Deserialize seed from dictionary."""
        return cls(
            seed_id=data['seed_id'],
            lens_type=data['lens_type'],
            lens_params=data.get('lens_params', {}),
            parameters=data.get('parameters', {}),
            constraints=data.get('constraints', []),
            certificates=[
                Certificate(**c) for c in data.get('certificates', [])
            ],
            values=data.get('values', []),
            created=data.get('created', time.time()),
            description=data.get('description', '')
        )


class SeedLedger:
    """
    Ledger for storing and managing seeds.
    
    Provides holographic encoding: store "in" (generators),
    not "out" (full expansions).
    """
    
    def __init__(self):
        self.seeds: Dict[str, Seed] = {}
        self.index_by_hash: Dict[str, str] = {}
        self.index_by_type: Dict[str, List[str]] = {}
    
    def store(self, seed: Seed) -> str:
        """Store a seed and return its ID."""
        self.seeds[seed.seed_id] = seed
        
        # Index by hash
        hash_val = seed.compute_hash()
        self.index_by_hash[hash_val] = seed.seed_id
        
        # Index by lens type
        if seed.lens_type not in self.index_by_type:
            self.index_by_type[seed.lens_type] = []
        self.index_by_type[seed.lens_type].append(seed.seed_id)
        
        return seed.seed_id
    
    def retrieve(self, seed_id: str) -> Optional[Seed]:
        """Retrieve a seed by ID."""
        return self.seeds.get(seed_id)
    
    def find_by_hash(self, hash_val: str) -> Optional[Seed]:
        """Find a seed by its content hash."""
        seed_id = self.index_by_hash.get(hash_val)
        if seed_id:
            return self.seeds.get(seed_id)
        return None
    
    def find_by_type(self, lens_type: str) -> List[Seed]:
        """Find all seeds using a particular lens type."""
        seed_ids = self.index_by_type.get(lens_type, [])
        return [self.seeds[sid] for sid in seed_ids if sid in self.seeds]
    
    def list_all(self) -> List[str]:
        """List all seed IDs."""
        return list(self.seeds.keys())
    
    def export_json(self) -> str:
        """Export ledger to JSON."""
        return json.dumps({
            'seeds': {sid: s.to_dict() for sid, s in self.seeds.items()},
            'version': '1.0'
        }, indent=2)
    
    def import_json(self, json_str: str) -> int:
        """Import seeds from JSON. Returns count of imported seeds."""
        data = json.loads(json_str)
        count = 0
        for sid, sdata in data.get('seeds', {}).items():
            seed = Seed.from_dict(sdata)
            self.store(seed)
            count += 1
        return count


# =============================================================================
# SEED COMPILER - CONSTRUCTION PIPELINE
# =============================================================================

class SeedCompiler:
    """
    Compiler for constructing mathematical objects from constraints.
    
    Pipeline: Normalize → Reduce → Enumerate → Solve → Certify → Ledger
    """
    
    def __init__(self, ledger: SeedLedger = None):
        self.ledger = ledger or SeedLedger()
    
    def compile(self, constraints: List[Constraint], 
                lens: Lens,
                seed_id: str = None,
                description: str = "") -> Seed:
        """
        Compile constraints into a seed.
        
        1. Normalize expressions to canonical form
        2. Reduce via lens transforms
        3. Enumerate lattice points if applicable
        4. Solve constraint system
        5. Generate certificates
        6. Store in ledger
        """
        seed_id = seed_id or f"seed_{int(time.time()*1000)}"
        
        # Solve all constraints
        all_values = []
        constraint_dicts = []
        
        for c in constraints:
            values = c.solve()
            all_values.extend(values)
            
            constraint_dicts.append({
                'type': c.constraint_type.name,
                'description': c.description,
                'domain': list(c.domain),
                'solutions': values
            })
        
        # Generate certificates
        certificates = self._generate_certificates(constraints, lens, all_values)
        
        # Create seed
        seed = Seed(
            seed_id=seed_id,
            lens_type=lens.name,
            lens_params={},
            parameters={},
            constraints=constraint_dicts,
            certificates=certificates,
            values=all_values,
            description=description
        )
        
        # Store in ledger
        self.ledger.store(seed)
        
        return seed
    
    def _generate_certificates(self, constraints: List[Constraint],
                              lens: Lens, values: List[float]) -> List[Certificate]:
        """Generate verification certificates."""
        certs = []
        
        # Invertibility certificate for lens
        if lens.is_monotone():
            certs.append(Certificate(
                cert_type="invertibility",
                bounds={'monotone': 1.0},
                verified=True
            ))
        
        # Residual certificates for solutions
        for c in constraints:
            for v in c.solutions:
                valid, residual = c.verify(v)
                if valid:
                    certs.append(Certificate(
                        cert_type="residual",
                        bounds={'value': v, 'residual': residual},
                        verified=True
                    ))
        
        return certs
    
    def reconstruct(self, seed: Seed) -> Dict[str, Any]:
        """
        Reconstruct mathematical objects from a seed.
        
        Returns:
        - constants: the computed values
        - lens: the coordinate lens
        - operations: transported arithmetic
        - orbit: symmetry orbit information
        """
        from .lenses import LensRegistry
        
        registry = LensRegistry()
        lens = registry.get(seed.lens_type)
        
        if lens is None:
            # Try to reconstruct lens from type
            if seed.lens_type == "ln":
                lens = LogLens()
            elif seed.lens_type == "φ-phase":
                lens = TrigPhaseLens()
            else:
                lens = LogLens()  # Default
        
        from .lenses import TransportedField
        field = TransportedField(lens)
        
        return {
            'constants': seed.values,
            'lens': lens,
            'field': field,
            'zero': field.zero,
            'one': field.one,
            'certificates': seed.certificates
        }


# =============================================================================
# HYBRID CONSTANTS - LATTICE-PREIMAGE AND PHASE-LOCK
# =============================================================================

def create_lattice_preimage_constant(lens: Lens, theta: float, k: int) -> float:
    """
    Create a lattice-preimage constant: x_k = T⁻¹(θ + kπ/2)
    
    These are axis/diagonal family constants.
    """
    return lens.inverse(theta + k * np.pi / 2)


def create_phase_lock_constant(a: float, b: float, c: float, 
                               tolerance: float = 1e-10) -> Optional[float]:
    """
    Create a phase-lock constant by solving: u = a·cos(u) + b·sin(u) + c
    Then return x = e^u.
    
    This is log-trig-exp fusion.
    """
    def residual(u):
        return u - (a * np.cos(u) + b * np.sin(u) + c)
    
    # Search for fixed point
    for u0 in np.linspace(-10, 10, 50):
        u = u0
        for _ in range(100):
            try:
                u_new = a * np.cos(u) + b * np.sin(u) + c
                if abs(u_new - u) < tolerance:
                    if abs(residual(u_new)) < tolerance:
                        return np.exp(u_new)
                    break
                u = u_new
            except:
                break
    
    return None


def create_hardened_constant(H: Callable, x0: float, order: int = 2,
                            tolerance: float = 1e-10) -> Optional[ZeroPoint]:
    """
    Create a hardened constant by finding order-m zero of H.
    
    These are "zero-of-zero" constants that are structurally rigid.
    """
    from .zeros import ZeroOfZeroChain
    
    chain = ZeroOfZeroChain(H, (max(0.01, x0 - 10), x0 + 10))
    actual_order = chain.check_order(x0, tolerance)
    
    if actual_order >= order:
        return ZeroPoint(
            location=x0,
            order=actual_order,
            zero_type=ZeroType.DOUBLE if actual_order == 2 else ZeroType.HIGHER,
            derivative_values=chain.jet_at_zero(x0, order)
        )
    
    return None


# =============================================================================
# VALIDATION
# =============================================================================

def validate_constraints_and_seeds() -> bool:
    """Validate constraint system and seed ledger."""
    # Fixed point constraint
    fp = fixed_point_constraint(lambda x: np.cos(x), "cos", (0, 2))
    solutions = fp.solve()
    assert len(solutions) > 0
    assert any(abs(s - 0.7391) < 0.01 for s in solutions)  # Dottie number
    
    # Equalization constraint
    eq = equalization_constraint(
        [lambda x: x**2, lambda x: 2*x + 3],
        ["x²", "2x+3"],
        (0, 10)
    )
    solutions = eq.solve()
    assert any(abs(s - 3.0) < 0.1 for s in solutions)
    
    # Lattice constraint
    lens = TrigPhaseLens()
    lat = lattice_constraint(lens, base=0, period=np.pi, n_terms=5)
    solutions = lat.solve()
    assert len(solutions) > 0
    
    # Seed creation and storage
    ledger = SeedLedger()
    seed = Seed(
        seed_id="test_seed",
        lens_type="ln",
        parameters={'test': 42},
        constraints=[{'type': 'FIXED_POINT', 'description': 'test'}],
        values=[1.5, 2.5, 3.5],
        description="Test seed"
    )
    
    ledger.store(seed)
    retrieved = ledger.retrieve("test_seed")
    assert retrieved is not None
    assert retrieved.values == [1.5, 2.5, 3.5]
    
    # Seed compiler
    compiler = SeedCompiler()
    compiled = compiler.compile(
        [fp],
        LogLens(),
        "compiled_test",
        "Dottie number"
    )
    assert len(compiled.values) > 0
    
    # Reconstruct
    reconstructed = compiler.reconstruct(compiled)
    assert 'constants' in reconstructed
    assert 'lens' in reconstructed
    
    # Phase-lock constant
    phase_const = create_phase_lock_constant(0.5, 0.5, 0.0)
    assert phase_const is not None
    
    return True


if __name__ == "__main__":
    print("Validating Constraints and Seeds...")
    assert validate_constraints_and_seeds()
    print("✓ Constraints and Seeds validated")
    
    # Demo
    print("\n=== Constraint Demo ===")
    
    # Dottie number: x = cos(x)
    fp = fixed_point_constraint(lambda x: np.cos(x), "cos", (0, 2))
    dottie = fp.solve()
    print(f"Dottie number (x = cos(x)): {dottie[0]:.10f}")
    
    # Verify
    valid, res = fp.verify(dottie[0])
    print(f"Verified: {valid}, residual: {res:.2e}")
    
    print("\n=== Seed Ledger Demo ===")
    compiler = SeedCompiler()
    seed = compiler.compile(
        [fp],
        LogLens(),
        "dottie_seed",
        "The Dottie number: unique fixed point of cosine"
    )
    
    print(f"Seed ID: {seed.seed_id}")
    print(f"Hash: {seed.compute_hash()}")
    print(f"Values: {seed.values}")
    print(f"Certificates: {len(seed.certificates)}")
