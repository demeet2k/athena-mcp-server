"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        OBLIGATION DAG MODULE                                 ║
║                                                                              ║
║  Proof Obligations, Discharge, and Certification System                      ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Every mathematical claim generates OBLIGATIONS that must be DISCHARGED   ║
║    before the claim can be CERTIFIED.                                        ║
║                                                                              ║
║  The Obligation DAG:                                                         ║
║    - Nodes: Mathematical statements requiring proof                          ║
║    - Edges: Dependencies (A depends on B if B must be proved first)         ║
║    - Discharge: Provide proof/certificate for an obligation                  ║
║    - Stop predicates: All obligations cleared + RT stamps                    ║
║                                                                              ║
║  Letter Assignments:                                                         ║
║    P: obligation DAG                                                         ║
║    Q: quality gates RT registry                                              ║
║    V: fixtures/verifiers                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Set, Callable
from enum import Enum
import hashlib


# ═══════════════════════════════════════════════════════════════════════════════
# OBLIGATION TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class ObligationStatus(Enum):
    """Status of an obligation."""
    PENDING = "pending"         # Not yet addressed
    IN_PROGRESS = "in_progress" # Being worked on
    DISCHARGED = "discharged"   # Proven/satisfied
    FAILED = "failed"           # Could not be discharged
    DEFERRED = "deferred"       # Postponed to later


class ObligationPriority(Enum):
    """Priority levels for obligations."""
    CRITICAL = 0    # Must be discharged before anything else
    HIGH = 1        # Should be discharged soon
    NORMAL = 2      # Standard priority
    LOW = 3         # Can be deferred
    OPTIONAL = 4    # Nice to have


class ObligationType(Enum):
    """Types of obligations."""
    EXISTENCE = "existence"     # Prove something exists
    UNIQUENESS = "uniqueness"   # Prove something is unique
    BOUND = "bound"             # Prove a bound holds
    CONVERGENCE = "convergence" # Prove convergence
    COMMUTATION = "commutation" # Prove operations commute
    DOMAIN = "domain"           # Prove domain conditions
    PRECONDITION = "precondition" # Verify preconditions
    POSTCONDITION = "postcondition" # Verify postconditions
    INVARIANT = "invariant"     # Prove invariant maintained


# ═══════════════════════════════════════════════════════════════════════════════
# OBLIGATION NODE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Obligation:
    """
    A single obligation node in the DAG.
    """
    id: str
    description: str
    obligation_type: ObligationType
    priority: ObligationPriority = ObligationPriority.NORMAL
    status: ObligationStatus = ObligationStatus.PENDING
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # IDs of prerequisites
    
    # Discharge information
    discharge_method: Optional[str] = None
    discharge_certificate: Optional[str] = None
    discharge_timestamp: Optional[str] = None
    
    # Context
    source: str = ""  # Where this obligation came from
    chart: str = "□"  # Which chart (□✿☁⟂)
    
    def is_ready(self, discharged_ids: Set[str]) -> bool:
        """Check if all dependencies are discharged."""
        return all(dep in discharged_ids for dep in self.depends_on)
    
    def discharge(self, method: str, certificate: str = ""):
        """Mark obligation as discharged."""
        self.status = ObligationStatus.DISCHARGED
        self.discharge_method = method
        self.discharge_certificate = certificate
    
    def fail(self, reason: str):
        """Mark obligation as failed."""
        self.status = ObligationStatus.FAILED
        self.discharge_method = reason
    
    @property
    def is_discharged(self) -> bool:
        return self.status == ObligationStatus.DISCHARGED


# ═══════════════════════════════════════════════════════════════════════════════
# DISCHARGE METHODS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DischargeMethod:
    """
    A method for discharging an obligation.
    """
    name: str
    applicable_types: List[ObligationType]
    verifier: Callable[..., bool]
    description: str = ""
    
    def can_discharge(self, obligation: Obligation) -> bool:
        """Check if this method can discharge given obligation."""
        return obligation.obligation_type in self.applicable_types
    
    def apply(self, obligation: Obligation, *args, **kwargs) -> bool:
        """Attempt to discharge obligation."""
        if not self.can_discharge(obligation):
            return False
        return self.verifier(*args, **kwargs)


class StandardDischargeMethods:
    """Collection of standard discharge methods."""
    
    @staticmethod
    def by_computation() -> DischargeMethod:
        """Discharge by direct computation."""
        return DischargeMethod(
            "computation",
            [ObligationType.EXISTENCE, ObligationType.BOUND, ObligationType.UNIQUENESS],
            lambda result, expected, tol=1e-10: abs(result - expected) < tol,
            "Direct numerical/symbolic computation"
        )
    
    @staticmethod
    def by_certificate() -> DischargeMethod:
        """Discharge by external certificate."""
        return DischargeMethod(
            "certificate",
            list(ObligationType),  # All types
            lambda cert: cert is not None and len(cert) > 0,
            "External proof certificate"
        )
    
    @staticmethod
    def by_assumption() -> DischargeMethod:
        """Discharge by assuming (creates new obligation if not justified)."""
        return DischargeMethod(
            "assumption",
            [ObligationType.PRECONDITION, ObligationType.DOMAIN],
            lambda: True,  # Always succeeds, but should track
            "Assumed true (audit trail created)"
        )
    
    @staticmethod
    def by_invariant() -> DischargeMethod:
        """Discharge by loop invariant."""
        return DischargeMethod(
            "invariant",
            [ObligationType.INVARIANT, ObligationType.CONVERGENCE],
            lambda init, step, term: init and step and term,
            "Loop invariant: init ∧ step ∧ termination"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# OBLIGATION DAG
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ObligationDAG:
    """
    Directed Acyclic Graph of obligations.
    
    The "P" letter in the AETHER alphabet.
    """
    obligations: Dict[str, Obligation] = field(default_factory=dict)
    
    def add_obligation(self, obligation: Obligation):
        """Add obligation to DAG."""
        self.obligations[obligation.id] = obligation
    
    def add_dependency(self, from_id: str, to_id: str):
        """Add dependency: from_id depends on to_id."""
        if from_id in self.obligations:
            if to_id not in self.obligations[from_id].depends_on:
                self.obligations[from_id].depends_on.append(to_id)
    
    @property
    def discharged_ids(self) -> Set[str]:
        """Get IDs of discharged obligations."""
        return {id for id, ob in self.obligations.items() if ob.is_discharged}
    
    @property
    def pending_ids(self) -> Set[str]:
        """Get IDs of pending obligations."""
        return {id for id, ob in self.obligations.items() 
                if ob.status == ObligationStatus.PENDING}
    
    def ready_to_discharge(self) -> List[Obligation]:
        """Get obligations ready for discharge (all deps satisfied)."""
        discharged = self.discharged_ids
        return [ob for ob in self.obligations.values()
                if ob.status == ObligationStatus.PENDING and ob.is_ready(discharged)]
    
    def discharge(self, id: str, method: str, certificate: str = "") -> bool:
        """Attempt to discharge an obligation."""
        if id not in self.obligations:
            return False
        ob = self.obligations[id]
        if not ob.is_ready(self.discharged_ids):
            return False
        ob.discharge(method, certificate)
        return True
    
    def topological_order(self) -> List[str]:
        """Get topological ordering of obligations."""
        # Kahn's algorithm
        in_degree = {id: 0 for id in self.obligations}
        for ob in self.obligations.values():
            for dep in ob.depends_on:
                if dep in in_degree:
                    in_degree[ob.id] += 1
        
        queue = [id for id, deg in in_degree.items() if deg == 0]
        result = []
        
        while queue:
            id = queue.pop(0)
            result.append(id)
            for ob in self.obligations.values():
                if id in ob.depends_on:
                    in_degree[ob.id] -= 1
                    if in_degree[ob.id] == 0:
                        queue.append(ob.id)
        
        return result
    
    def is_complete(self) -> bool:
        """Check if all obligations are discharged."""
        return all(ob.is_discharged for ob in self.obligations.values())
    
    def summary(self) -> str:
        """Generate summary report."""
        total = len(self.obligations)
        discharged = len(self.discharged_ids)
        pending = len(self.pending_ids)
        failed = len([ob for ob in self.obligations.values() 
                     if ob.status == ObligationStatus.FAILED])
        
        return f"""
Obligation DAG Summary:
  Total: {total}
  Discharged: {discharged} ({100*discharged/total:.1f}%)
  Pending: {pending}
  Failed: {failed}
  Complete: {self.is_complete()}
"""


# ═══════════════════════════════════════════════════════════════════════════════
# QUALITY GATES (RT REGISTRY)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class QualityGate:
    """
    A quality gate for round-trip verification.
    
    The "Q" letter in the AETHER alphabet.
    """
    name: str
    chart: str  # □✿☁⟂
    verifier: Callable[..., bool]
    passed: bool = False
    timestamp: str = ""
    
    def check(self, *args, **kwargs) -> bool:
        """Run verification."""
        self.passed = self.verifier(*args, **kwargs)
        return self.passed


@dataclass
class RTRegistry:
    """
    Registry of round-trip quality gates.
    """
    gates: Dict[str, QualityGate] = field(default_factory=dict)
    
    def register(self, gate: QualityGate):
        """Register a quality gate."""
        self.gates[f"{gate.chart}:{gate.name}"] = gate
    
    def check_all(self, chart: str = None) -> Dict[str, bool]:
        """Check all gates (optionally filtered by chart)."""
        results = {}
        for key, gate in self.gates.items():
            if chart is None or gate.chart == chart:
                results[key] = gate.passed
        return results
    
    def all_passed(self, chart: str = None) -> bool:
        """Check if all relevant gates passed."""
        results = self.check_all(chart)
        return all(results.values()) if results else False


# ═══════════════════════════════════════════════════════════════════════════════
# STOP PREDICATES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class StopPredicate:
    """
    Stop predicate for terminating computation.
    
    Stop = (O = ∅) ∧ RT_chart
    """
    chart: str
    obligations_empty: Callable[[], bool]
    rt_verified: Callable[[], bool]
    
    def is_satisfied(self) -> bool:
        """Check if stop condition is met."""
        return self.obligations_empty() and self.rt_verified()
    
    @classmethod
    def for_square(cls, dag: ObligationDAG, registry: RTRegistry) -> 'StopPredicate':
        """Stop predicate for □ chart."""
        return cls(
            "□",
            lambda: dag.is_complete(),
            lambda: registry.all_passed("□")
        )
    
    @classmethod
    def for_fractal(cls, dag: ObligationDAG, 
                    ledger_stable: Callable[[], bool]) -> 'StopPredicate':
        """Stop predicate for ⟂ chart."""
        return cls(
            "⟂",
            lambda: dag.is_complete(),
            lambda: ledger_stable()
        )


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES AND VERIFIERS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Fixture:
    """
    A test fixture for verification.
    
    The "V" letter in the AETHER alphabet.
    """
    name: str
    input_data: Any
    expected_output: Any
    verifier: Callable[[Any, Any], bool]
    tolerance: float = 1e-10
    
    def run(self, actual_output: Any) -> bool:
        """Run fixture verification."""
        return self.verifier(actual_output, self.expected_output)


@dataclass
class FixtureSuite:
    """
    Suite of fixtures for a component.
    """
    name: str
    fixtures: List[Fixture] = field(default_factory=list)
    
    def add(self, fixture: Fixture):
        """Add fixture to suite."""
        self.fixtures.append(fixture)
    
    def run_all(self, get_output: Callable[[Any], Any]) -> Dict[str, bool]:
        """Run all fixtures."""
        results = {}
        for fix in self.fixtures:
            output = get_output(fix.input_data)
            results[fix.name] = fix.run(output)
        return results
    
    def all_passed(self, get_output: Callable[[Any], Any]) -> bool:
        """Check if all fixtures pass."""
        return all(self.run_all(get_output).values())


# ═══════════════════════════════════════════════════════════════════════════════
# OBLIGATION COMPILER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ObligationCompiler:
    """
    Compiles mathematical operations into obligation DAGs.
    
    Exact ↔ Approx boundary handling.
    """
    dag: ObligationDAG = field(default_factory=ObligationDAG)
    
    def compile_hub_chain(self, hubs: List[str]) -> List[Obligation]:
        """
        Compile hub chain into obligation DAG.
        
        Each hub generates obligations for:
        - Preconditions (domain, existence)
        - Commutation with previous hubs
        - Postconditions
        """
        obligations = []
        prev_id = None
        
        for i, hub in enumerate(hubs):
            # Precondition obligation
            pre_ob = Obligation(
                f"hub_{i}_pre",
                f"Verify {hub} preconditions",
                ObligationType.PRECONDITION,
                source=hub,
                chart="✿"
            )
            if prev_id:
                pre_ob.depends_on.append(prev_id)
            obligations.append(pre_ob)
            self.dag.add_obligation(pre_ob)
            
            # Domain obligation
            dom_ob = Obligation(
                f"hub_{i}_domain",
                f"Verify {hub} domain conditions",
                ObligationType.DOMAIN,
                source=hub,
                chart="□"
            )
            dom_ob.depends_on.append(pre_ob.id)
            obligations.append(dom_ob)
            self.dag.add_obligation(dom_ob)
            
            prev_id = dom_ob.id
        
        return obligations
    
    def compile_bound(self, name: str, assumption_ids: List[str]) -> Obligation:
        """Compile bound computation into obligation."""
        ob = Obligation(
            f"bound_{name}",
            f"Verify bound {name} holds",
            ObligationType.BOUND,
            source=name,
            chart="☁"
        )
        ob.depends_on = assumption_ids
        self.dag.add_obligation(ob)
        return ob
    
    def compile_convergence(self, name: str, init_id: str, 
                           step_id: str) -> Obligation:
        """Compile convergence proof into obligation."""
        ob = Obligation(
            f"conv_{name}",
            f"Verify {name} converges",
            ObligationType.CONVERGENCE,
            source=name,
            chart="⟂"
        )
        ob.depends_on = [init_id, step_id]
        self.dag.add_obligation(ob)
        return ob


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ObligationPoleBridge:
    """
    Bridge between Obligation DAG and four-pole framework.
    """
    
    @staticmethod
    def aether_letters() -> str:
        return """
        AETHER Letters:
          P: Obligation DAG
          Q: Quality gates RT registry
          V: Fixtures/verifiers
        """
    
    @staticmethod
    def d_pole() -> str:
        return "D-pole ↔ Discrete obligation discharge, certification"
    
    @staticmethod
    def square_chart() -> str:
        return "□ chart: Exact proofs, obligation completion"
    
    @staticmethod
    def integration() -> str:
        return """
        OBLIGATION DAG ↔ FRAMEWORK
        
        Stop predicates:
          Stop_□ = (O_□ = ∅) ∧ RT_□
          Stop_⟂ = RT_⟂ ∧ LedgerStable
        
        Cloud stops can be top-k if stable.
        "Done" = reconstructible seed + explicit uncertainty
        """


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def obligation(id: str, desc: str, ob_type: ObligationType) -> Obligation:
    """Create obligation."""
    return Obligation(id, desc, ob_type)


def obligation_dag() -> ObligationDAG:
    """Create empty obligation DAG."""
    return ObligationDAG()


def quality_gate(name: str, chart: str, verifier: Callable) -> QualityGate:
    """Create quality gate."""
    return QualityGate(name, chart, verifier)


def rt_registry() -> RTRegistry:
    """Create RT registry."""
    return RTRegistry()


def fixture(name: str, input_data: Any, expected: Any, 
            verifier: Callable = None) -> Fixture:
    """Create fixture."""
    if verifier is None:
        verifier = lambda a, b: a == b
    return Fixture(name, input_data, expected, verifier)


def obligation_compiler() -> ObligationCompiler:
    """Create obligation compiler."""
    return ObligationCompiler()


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    'ObligationStatus',
    'ObligationPriority',
    'ObligationType',
    
    # Core
    'Obligation',
    'DischargeMethod',
    'StandardDischargeMethods',
    'ObligationDAG',
    
    # Quality
    'QualityGate',
    'RTRegistry',
    
    # Stop
    'StopPredicate',
    
    # Fixtures
    'Fixture',
    'FixtureSuite',
    
    # Compiler
    'ObligationCompiler',
    
    # Bridge
    'ObligationPoleBridge',
    
    # Functions
    'obligation',
    'obligation_dag',
    'quality_gate',
    'rt_registry',
    'fixture',
    'obligation_compiler',
]
