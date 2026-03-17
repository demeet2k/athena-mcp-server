"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       ATLAS FORGE - Constraint System                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Mathematical constraints: root finding, fixed points, generators.
"""

from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Type
import json
import math

from atlasforge.core.types import Interval
from atlasforge.core.base import ContentAddressed
from atlasforge.core.enums import ConstraintType, NormalFormType, ObligationType, CertificateLevel
from atlasforge.lenses.chart import Chart


@dataclass
class Constraint(ContentAddressed):
    """Base class for mathematical constraints."""
    
    name: str = ""
    description: str = ""
    domain: Optional[Interval] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    @abstractmethod
    def constraint_type(self) -> ConstraintType:
        pass
    
    @abstractmethod
    def evaluate(self, x: float) -> float:
        pass
    
    @abstractmethod
    def is_satisfied(self, x: float, tol: float = 1e-10) -> bool:
        pass
    
    def canonical_repr(self) -> str:
        return json.dumps({
            'type': self.constraint_type.value,
            'name': self.name,
            'domain': [self.domain.lo, self.domain.hi] if self.domain else None,
        }, sort_keys=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.constraint_type.value,
            'name': self.name,
            'domain': [self.domain.lo, self.domain.hi] if self.domain else None,
        }


@dataclass
class RootConstraint(Constraint):
    """Root constraint: H(x) = 0"""
    
    H: Callable[[float], float] = field(default=lambda x: x)
    dH: Optional[Callable[[float], float]] = None
    
    @property
    def constraint_type(self) -> ConstraintType:
        return ConstraintType.ROOT
    
    def evaluate(self, x: float) -> float:
        return self.H(x)
    
    def is_satisfied(self, x: float, tol: float = 1e-10) -> bool:
        return abs(self.H(x)) < tol
    
    def derivative(self, x: float, eps: float = 1e-8) -> float:
        if self.dH is not None:
            return self.dH(x)
        return (self.H(x + eps) - self.H(x - eps)) / (2 * eps)
    
    def to_normal_form(self) -> 'NormalForm':
        return NormalForm(
            form_type=NormalFormType.SCALAR_ROOT,
            functions={'H': self.H, 'dH': self.dH or self.derivative},
            domain=self.domain or Interval.all_reals(),
            source_constraint=self.content_hash()[:12],
        )
    
    def transport_through(self, chart: Chart) -> 'RootConstraint':
        def H_T(y):
            return self.H(chart.inverse(y))
        def dH_T(y):
            return self.derivative(chart.inverse(y)) * chart.inverse_jacobian(y)
        return RootConstraint(
            name=f"{self.name}_via_{chart.name}",
            domain=chart.domain, H=H_T, dH=dH_T)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RootConstraint':
        domain = None
        if data.get('domain'):
            domain = Interval.closed(data['domain'][0], data['domain'][1])
        return cls(name=data.get('name', ''), domain=domain)


@dataclass
class FixedPointConstraint(Constraint):
    """Fixed point constraint: x = F(x)"""
    
    F: Callable[[float], float] = field(default=lambda x: x)
    dF: Optional[Callable[[float], float]] = None
    
    @property
    def constraint_type(self) -> ConstraintType:
        return ConstraintType.FIXED_POINT
    
    def evaluate(self, x: float) -> float:
        return self.F(x) - x
    
    def is_satisfied(self, x: float, tol: float = 1e-10) -> bool:
        return abs(self.F(x) - x) < tol
    
    def derivative(self, x: float, eps: float = 1e-8) -> float:
        if self.dF is not None:
            return self.dF(x)
        return (self.F(x + eps) - self.F(x - eps)) / (2 * eps)
    
    def to_root_constraint(self) -> RootConstraint:
        return RootConstraint(
            name=f"{self.name}_as_root", domain=self.domain,
            H=lambda x: self.F(x) - x,
            dH=lambda x: self.derivative(x) - 1)
    
    def to_normal_form(self) -> 'NormalForm':
        return NormalForm(
            form_type=NormalFormType.FIXED_POINT,
            functions={'F': self.F, 'dF': self.dF or self.derivative},
            domain=self.domain or Interval.all_reals(),
            source_constraint=self.content_hash()[:12])
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FixedPointConstraint':
        domain = None
        if data.get('domain'):
            domain = Interval.closed(data['domain'][0], data['domain'][1])
        return cls(name=data.get('name', ''), domain=domain)


@dataclass
class GeneratorConstraint(Constraint):
    """Generator constraint: find x where generator flow equilibrates."""
    
    generator: Any = None
    target_value: float = 0.0
    
    @property
    def constraint_type(self) -> ConstraintType:
        return ConstraintType.GENERATOR
    
    def evaluate(self, x: float) -> float:
        if self.generator is None:
            return x - self.target_value
        import numpy as np
        return float(np.linalg.norm(self.generator(np.array([x]))))
    
    def is_satisfied(self, x: float, tol: float = 1e-10) -> bool:
        return abs(self.evaluate(x)) < tol
    
    def to_normal_form(self) -> 'NormalForm':
        return NormalForm(
            form_type=NormalFormType.GENERATOR_EQUILIBRIUM,
            functions={'G': self.generator},
            domain=self.domain or Interval.all_reals(),
            source_constraint=self.content_hash()[:12])
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeneratorConstraint':
        return cls(name=data.get('name', ''), target_value=data.get('target_value', 0.0))


@dataclass
class EqualityConstraint(Constraint):
    """Equality constraint: f(x) = g(x)"""
    
    f: Callable[[float], float] = field(default=lambda x: x)
    g: Callable[[float], float] = field(default=lambda x: 0)
    
    @property
    def constraint_type(self) -> ConstraintType:
        return ConstraintType.EQUALITY
    
    def evaluate(self, x: float) -> float:
        return self.f(x) - self.g(x)
    
    def is_satisfied(self, x: float, tol: float = 1e-10) -> bool:
        return abs(self.f(x) - self.g(x)) < tol
    
    def to_root_constraint(self) -> RootConstraint:
        return RootConstraint(
            name=f"{self.name}_as_root", domain=self.domain,
            H=lambda x: self.f(x) - self.g(x))
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EqualityConstraint':
        return cls(name=data.get('name', ''))


@dataclass
class VectorRootConstraint(Constraint):
    """Vector root constraint: H(x) = 0 for x ∈ ℝⁿ"""
    
    H: Callable[[List[float]], List[float]] = field(default=lambda x: x)
    J: Optional[Callable[[List[float]], List[List[float]]]] = None
    dimension: int = 1
    
    @property
    def constraint_type(self) -> ConstraintType:
        return ConstraintType.VECTOR_ROOT
    
    def evaluate(self, x: float) -> float:
        result = self.H([x])
        import math
        return math.sqrt(sum(r*r for r in result))
    
    def evaluate_vector(self, x: List[float]) -> List[float]:
        return self.H(x)
    
    def is_satisfied(self, x: float, tol: float = 1e-10) -> bool:
        return self.evaluate(x) < tol
    
    def is_satisfied_vector(self, x: List[float], tol: float = 1e-10) -> bool:
        residual = self.H(x)
        import math
        return math.sqrt(sum(r*r for r in residual)) < tol
    
    def jacobian(self, x: List[float], eps: float = 1e-8) -> List[List[float]]:
        if self.J is not None:
            return self.J(x)
        n = len(x)
        fx = self.H(x)
        m = len(fx)
        J = [[0.0] * n for _ in range(m)]
        for j in range(n):
            x_plus = x.copy()
            x_minus = x.copy()
            x_plus[j] += eps
            x_minus[j] -= eps
            f_plus = self.H(x_plus)
            f_minus = self.H(x_minus)
            for i in range(m):
                J[i][j] = (f_plus[i] - f_minus[i]) / (2 * eps)
        return J
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VectorRootConstraint':
        return cls(name=data.get('name', ''), dimension=data.get('dimension', 1))


@dataclass
class NormalForm(ContentAddressed):
    """Normalized constraint form for solvers."""
    
    form_type: NormalFormType = NormalFormType.SCALAR_ROOT
    functions: Dict[str, Callable] = field(default_factory=dict)
    domain: Interval = field(default_factory=lambda: Interval.all_reals())
    parameters: Dict[str, Any] = field(default_factory=dict)
    source_constraint: str = ""
    
    def canonical_repr(self) -> str:
        return json.dumps({
            'type': self.form_type.value,
            'source': self.source_constraint,
        }, sort_keys=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {'type': self.form_type.value, 'source': self.source_constraint}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NormalForm':
        return cls(form_type=NormalFormType(data.get('type', 'scalar_root')))
    
    def get_function(self, name: str) -> Optional[Callable]:
        return self.functions.get(name)
    
    @property
    def H(self) -> Optional[Callable]:
        return self.functions.get('H')
    
    @property
    def dH(self) -> Optional[Callable]:
        return self.functions.get('dH')


@dataclass
class ProofObligation(ContentAddressed):
    """A proof obligation that must be discharged."""
    
    obligation_type: ObligationType = ObligationType.ENCLOSURE
    description: str = ""
    required_level: CertificateLevel = CertificateLevel.L1_EMPIRICAL
    discharged: bool = False
    discharging_certificate: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    
    def canonical_repr(self) -> str:
        return json.dumps({
            'type': self.obligation_type.value,
            'level': self.required_level.value,
        }, sort_keys=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.obligation_type.value,
            'discharged': self.discharged,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProofObligation':
        return cls(
            obligation_type=ObligationType(data.get('type', 'enclosure')),
            discharged=data.get('discharged', False))
    
    def discharge(self, certificate_hash: str):
        self.discharged = True
        self.discharging_certificate = certificate_hash


@dataclass
class ConstraintIR(ContentAddressed):
    """Intermediate representation for constraints."""
    
    constraint_type: ConstraintType = ConstraintType.ROOT
    normal_form: Optional[NormalForm] = None
    domain: Interval = field(default_factory=lambda: Interval.all_reals())
    obligations: List[ProofObligation] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_hash: str = ""
    
    def canonical_repr(self) -> str:
        return json.dumps({
            'type': self.constraint_type.value,
            'source': self.source_hash,
        }, sort_keys=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {'type': self.constraint_type.value, 'source': self.source_hash}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConstraintIR':
        return cls(constraint_type=ConstraintType(data.get('type', 'root')))
    
    @classmethod
    def from_constraint(cls, constraint: Constraint) -> 'ConstraintIR':
        normal_form = None
        if hasattr(constraint, 'to_normal_form'):
            normal_form = constraint.to_normal_form()
        obligations = [
            ProofObligation(ObligationType.ENCLOSURE, "Solution must be enclosed"),
            ProofObligation(ObligationType.REPLAY, "Must be replayable"),
        ]
        return cls(
            constraint_type=constraint.constraint_type,
            normal_form=normal_form,
            domain=constraint.domain or Interval.all_reals(),
            obligations=obligations,
            source_hash=constraint.content_hash()[:12])
    
    def add_obligation(self, obl: ProofObligation):
        self.obligations.append(obl)
    
    def all_obligations_discharged(self) -> bool:
        return all(o.discharged for o in self.obligations)
