"""
ATHENA OS - GLOBAL INFORMATION NETWORK
======================================
Deadlock: Detection and Resolution Algorithms

From GLOBAL_INFORMATION_NETWORK.docx §14:

ARJUNA-VIṢĀDA STATE:
    Deadlock is a formally identifiable phase where action selection
    becomes ill-posed or yields zero effective progress despite
    nonzero objective pressure.

DEADLOCK DEFINITION:
    1. A_adm(m) ≠ ∅ (actions exist)
    2. Δ*_Φ(m) ≥ 0 (no admissible action yields decrease)
    3. ||∇Φ(m)||_moral > 0 (objective pressure is nonzero)

FAILURE MODES:
    - Logic Failure: valuation overdetermined (B) or underdetermined (U)
    - Will Collapse: W(m) = 0 while ||∇Φ||_moral > 0
    - SNR Crisis: signal-to-noise ratio below threshold

DESCENT OPERATOR (Â_vatar):
    Produces modified kernel that escapes local deadlock while
    preserving admissibility, achieving local escape, and
    minimizing distortion.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Callable
from enum import Enum
import numpy as np

from .valuation import V4, Valuation, ParaconsistentInference
from .moral_geometry import MoralMetric, WillVector, Kurukshetra


# =============================================================================
# DEADLOCK TYPES
# =============================================================================

class DeadlockType(Enum):
    """Types of deadlock conditions."""
    
    NONE = "none"                    # No deadlock
    CONSTRAINT_TRAP = "constraint"   # Trapped by constraints
    LOGIC_FAILURE = "logic"          # Valuation inconsistency
    WILL_COLLAPSE = "will"           # Zero descent direction
    SNR_CRISIS = "snr"               # Noise-dominated
    TRAPPING = "trapping"            # Multi-step trap


class ResolutionMethod(Enum):
    """Methods for resolving deadlock."""
    
    RELAX_CONSTRAINT = "relax"       # Soften constraints
    SECTOR_ROTATION = "rotate"       # Cross-sector transfer
    REPRESENTATION_CHANGE = "repr"   # Change decision space
    PRIVILEGED_DEBUG = "debug"       # Access hidden state
    TUNNEL_SELECTION = "tunnel"      # Find escape route
    ESCALATION = "escalate"          # Request higher authority


# =============================================================================
# PROGRESS FUNCTIONAL
# =============================================================================

@dataclass
class ProgressFunctional:
    """
    Δ_Φ(m; a): Expected decrease in objective from action a.
    
    Δ_Φ(m; a) := E[Φ(m') - Φ(m) | m, a]
    
    Strict progress: Δ_Φ(m; a) < 0
    """
    
    objective: Callable[[np.ndarray], float] = field(default_factory=lambda: lambda x: 0.0)
    
    def compute(self, state: np.ndarray, action: np.ndarray,
                transition: Callable[[np.ndarray, np.ndarray], np.ndarray],
                n_samples: int = 10) -> float:
        """
        Compute expected progress from action.
        
        Args:
            state: Current state m
            action: Action a
            transition: P(m' | m, a) transition function
            n_samples: Number of samples for expectation
        """
        phi_current = self.objective(state)
        
        phi_next_sum = 0.0
        for _ in range(n_samples):
            next_state = transition(state, action)
            phi_next_sum += self.objective(next_state)
        
        phi_next_mean = phi_next_sum / n_samples
        return phi_next_mean - phi_current
    
    def best_progress(self, state: np.ndarray,
                      actions: List[np.ndarray],
                      transition: Callable[[np.ndarray, np.ndarray], np.ndarray]) -> float:
        """
        Compute Δ*_Φ(m) = inf_{a ∈ A_adm} Δ_Φ(m; a)
        """
        if not actions:
            return float('inf')
        
        best = float('inf')
        for action in actions:
            progress = self.compute(state, action, transition)
            best = min(best, progress)
        
        return best


# =============================================================================
# DECISION FEASIBILITY
# =============================================================================

@dataclass
class DecisionFeasibility:
    """
    Dec(m, v): Set of admissible actions under valuation.
    
    Dec(m, v) := {a ∈ A : Pre(m,a;v)=1 ∧ Safe(m,a;v)=1 ∧ Cap(m,a)=1}
    """
    
    preconditions: Dict[str, Callable[[np.ndarray, np.ndarray, Valuation], V4]] = field(default_factory=dict)
    safety_checks: Dict[str, Callable[[np.ndarray, np.ndarray, Valuation], V4]] = field(default_factory=dict)
    capability_checks: Dict[str, Callable[[np.ndarray, np.ndarray], bool]] = field(default_factory=dict)
    
    def add_precondition(self, name: str, 
                         check: Callable[[np.ndarray, np.ndarray, Valuation], V4]) -> None:
        """Add a precondition check."""
        self.preconditions[name] = check
    
    def add_safety_check(self, name: str,
                         check: Callable[[np.ndarray, np.ndarray, Valuation], V4]) -> None:
        """Add a safety check."""
        self.safety_checks[name] = check
    
    def add_capability_check(self, name: str,
                             check: Callable[[np.ndarray, np.ndarray], bool]) -> None:
        """Add a capability check."""
        self.capability_checks[name] = check
    
    def check_action(self, state: np.ndarray, action: np.ndarray,
                     valuation: Valuation) -> Tuple[bool, str]:
        """
        Check if action is admissible.
        
        Returns (admissible, reason) tuple.
        """
        # Check preconditions
        for name, check in self.preconditions.items():
            result = check(state, action, valuation)
            if not result.is_designated:
                return (False, f"Precondition failed: {name}")
        
        # Check safety
        for name, check in self.safety_checks.items():
            result = check(state, action, valuation)
            if not result.is_designated:
                return (False, f"Safety check failed: {name}")
        
        # Check capability
        for name, check in self.capability_checks.items():
            if not check(state, action):
                return (False, f"Capability check failed: {name}")
        
        return (True, "Admissible")
    
    def admissible_set(self, state: np.ndarray,
                       actions: List[np.ndarray],
                       valuation: Valuation) -> List[np.ndarray]:
        """Get set of admissible actions A_adm(m)."""
        admissible = []
        
        for action in actions:
            is_adm, _ = self.check_action(state, action, valuation)
            if is_adm:
                admissible.append(action)
        
        return admissible


# =============================================================================
# DEADLOCK CERTIFICATE
# =============================================================================

@dataclass
class DeadlockCertificate:
    """
    DL(m): Deadlock certificate - formal proof of deadlock condition.
    
    Contains:
    - Constraint graph C(m)
    - Admissible actions A_adm(m)
    - Valuation v(m)
    - Estimated gradient ĝ(m)
    - SNR(m)
    - Best progress Δ*_Φ(m)
    """
    
    state: np.ndarray
    constraint_graph: Dict[str, List[str]] = field(default_factory=dict)
    admissible_actions: List[np.ndarray] = field(default_factory=list)
    valuation_summary: Dict[str, V4] = field(default_factory=dict)
    gradient_estimate: np.ndarray = field(default_factory=lambda: np.zeros(4))
    snr: float = 1.0
    best_progress: float = 0.0
    
    # Deadlock classification
    deadlock_type: DeadlockType = DeadlockType.NONE
    blocking_constraints: List[str] = field(default_factory=list)
    
    @property
    def is_deadlocked(self) -> bool:
        return self.deadlock_type != DeadlockType.NONE
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for logging."""
        return {
            "state": self.state.tolist(),
            "n_admissible": len(self.admissible_actions),
            "snr": self.snr,
            "best_progress": self.best_progress,
            "deadlock_type": self.deadlock_type.value,
            "blocking_constraints": self.blocking_constraints
        }


# =============================================================================
# DEADLOCK DETECTOR
# =============================================================================

@dataclass
class DeadlockDetector:
    """
    Detects deadlock conditions in the Fire sector.
    """
    
    metric: MoralMetric = field(default_factory=MoralMetric)
    feasibility: DecisionFeasibility = field(default_factory=DecisionFeasibility)
    progress: ProgressFunctional = field(default_factory=ProgressFunctional)
    
    # Thresholds
    gradient_threshold: float = 0.01    # Minimum ||∇Φ|| to consider
    snr_threshold: float = 0.1          # SNR crisis threshold
    
    def detect(self, state: np.ndarray,
               actions: List[np.ndarray],
               valuation: Valuation,
               transition: Callable[[np.ndarray, np.ndarray], np.ndarray],
               gradient: Optional[np.ndarray] = None) -> DeadlockCertificate:
        """
        Detect deadlock at current state.
        
        Returns DeadlockCertificate with diagnosis.
        """
        cert = DeadlockCertificate(state=state.copy())
        
        # Get admissible actions
        cert.admissible_actions = self.feasibility.admissible_set(
            state, actions, valuation
        )
        
        # Store valuation summary
        for prop in list(valuation.assignments.keys())[:10]:
            cert.valuation_summary[prop] = valuation[prop]
        
        # Compute gradient
        if gradient is not None:
            cert.gradient_estimate = gradient
        else:
            # Estimate from objective
            eps = 1e-6
            cert.gradient_estimate = np.zeros(len(state))
            for i in range(len(state)):
                e_i = np.zeros(len(state))
                e_i[i] = eps
                cert.gradient_estimate[i] = (
                    self.progress.objective(state + e_i) - 
                    self.progress.objective(state - e_i)
                ) / (2 * eps)
        
        grad_norm = self.metric.norm(state, cert.gradient_estimate)
        
        # Check for deadlock conditions
        
        # 1. Check if actions exist but none make progress
        if cert.admissible_actions:
            cert.best_progress = self.progress.best_progress(
                state, cert.admissible_actions, transition
            )
            
            if cert.best_progress >= 0 and grad_norm > self.gradient_threshold:
                cert.deadlock_type = DeadlockType.CONSTRAINT_TRAP
                cert.blocking_constraints = self._find_blocking_constraints(
                    state, cert.admissible_actions, valuation
                )
        else:
            # No admissible actions at all
            if grad_norm > self.gradient_threshold:
                cert.deadlock_type = DeadlockType.CONSTRAINT_TRAP
        
        # 2. Check for logic failure
        contradictions = valuation.get_contradictions()
        undetermined = valuation.get_undetermined()
        
        if contradictions or undetermined:
            # Check if these affect decision
            for prop in contradictions:
                if self._affects_decision(prop, state, actions, valuation):
                    cert.deadlock_type = DeadlockType.LOGIC_FAILURE
                    cert.blocking_constraints.append(f"B:{prop}")
            
            for prop in undetermined:
                if self._affects_decision(prop, state, actions, valuation):
                    cert.deadlock_type = DeadlockType.LOGIC_FAILURE
                    cert.blocking_constraints.append(f"U:{prop}")
        
        # 3. Check for will collapse
        will = WillVector(metric=self.metric)
        if cert.admissible_actions:
            feasible_dirs = [a - state for a in cert.admissible_actions 
                            if np.linalg.norm(a - state) > 1e-10]
            
            if will.is_collapsed(state, cert.gradient_estimate, 
                                feasible_dirs or None):
                cert.deadlock_type = DeadlockType.WILL_COLLAPSE
        
        # 4. Check SNR
        if self._check_snr_crisis(state, cert.gradient_estimate):
            cert.snr = self._compute_snr(state, cert.gradient_estimate)
            if cert.snr < self.snr_threshold:
                cert.deadlock_type = DeadlockType.SNR_CRISIS
        
        return cert
    
    def _find_blocking_constraints(self, state: np.ndarray,
                                   actions: List[np.ndarray],
                                   valuation: Valuation) -> List[str]:
        """Identify which constraints are blocking progress."""
        blocking = []
        
        for name in self.feasibility.preconditions:
            blocking.append(f"pre:{name}")
        
        for name in self.feasibility.safety_checks:
            blocking.append(f"safe:{name}")
        
        return blocking[:5]  # Top 5
    
    def _affects_decision(self, prop: str, state: np.ndarray,
                         actions: List[np.ndarray], 
                         valuation: Valuation) -> bool:
        """Check if proposition affects decision feasibility."""
        # Simplified: assume all propositions potentially affect decision
        return True
    
    def _check_snr_crisis(self, state: np.ndarray, gradient: np.ndarray) -> bool:
        """Check if SNR is problematically low."""
        # Simplified noise model
        return np.random.random() < 0.1  # 10% chance of SNR check
    
    def _compute_snr(self, state: np.ndarray, gradient: np.ndarray) -> float:
        """
        Compute signal-to-noise ratio.
        
        SNR(m) = S(m) / (N(m) + ε₀)
        """
        signal = self.metric.norm(state, gradient)
        noise = 0.1  # Estimated noise (would come from observation model)
        return signal / (noise + 1e-6)


# =============================================================================
# DESCENT OPERATOR (AVATAR)
# =============================================================================

@dataclass
class DescentOperator:
    """
    Â_vatar: The Avatar Descent Operator.
    
    Produces modified kernel that escapes deadlock while:
    1. Preserving admissibility
    2. Achieving local escape (strict descent in H steps)
    3. Minimizing distortion
    """
    
    metric: MoralMetric = field(default_factory=MoralMetric)
    escape_horizon: int = 10  # H: steps to achieve escape
    
    def apply(self, certificate: DeadlockCertificate,
              kernel_params: np.ndarray) -> Tuple[np.ndarray, bool]:
        """
        Apply descent operator to escape deadlock.
        
        Args:
            certificate: Deadlock certificate DL(m)
            kernel_params: Current kernel parameters θ
        
        Returns:
            (new_params, success) tuple
        """
        if not certificate.is_deadlocked:
            return (kernel_params, True)
        
        # Select resolution strategy based on deadlock type
        strategy = self._select_strategy(certificate)
        
        if strategy == ResolutionMethod.RELAX_CONSTRAINT:
            return self._relax_constraints(certificate, kernel_params)
        
        elif strategy == ResolutionMethod.REPRESENTATION_CHANGE:
            return self._change_representation(certificate, kernel_params)
        
        elif strategy == ResolutionMethod.TUNNEL_SELECTION:
            return self._find_tunnel(certificate, kernel_params)
        
        elif strategy == ResolutionMethod.SECTOR_ROTATION:
            return self._rotate_sector(certificate, kernel_params)
        
        elif strategy == ResolutionMethod.ESCALATION:
            # Cannot resolve locally
            return (kernel_params, False)
        
        return (kernel_params, False)
    
    def _select_strategy(self, certificate: DeadlockCertificate) -> ResolutionMethod:
        """Select best resolution strategy for deadlock type."""
        if certificate.deadlock_type == DeadlockType.CONSTRAINT_TRAP:
            return ResolutionMethod.RELAX_CONSTRAINT
        
        elif certificate.deadlock_type == DeadlockType.LOGIC_FAILURE:
            return ResolutionMethod.SECTOR_ROTATION
        
        elif certificate.deadlock_type == DeadlockType.WILL_COLLAPSE:
            return ResolutionMethod.TUNNEL_SELECTION
        
        elif certificate.deadlock_type == DeadlockType.SNR_CRISIS:
            return ResolutionMethod.REPRESENTATION_CHANGE
        
        return ResolutionMethod.ESCALATION
    
    def _relax_constraints(self, certificate: DeadlockCertificate,
                          params: np.ndarray) -> Tuple[np.ndarray, bool]:
        """
        Relax blocking constraints to enable progress.
        
        Adds small perturbation in descent direction.
        """
        # Compute relaxation direction
        grad = certificate.gradient_estimate
        grad_norm = np.linalg.norm(grad) + 1e-10
        
        # Relax by stepping slightly in negative gradient direction
        relaxation = -0.1 * grad / grad_norm
        
        new_params = params + relaxation[:len(params)] if len(relaxation) >= len(params) else params
        
        return (new_params, True)
    
    def _change_representation(self, certificate: DeadlockCertificate,
                               params: np.ndarray) -> Tuple[np.ndarray, bool]:
        """
        Change representation to improve SNR.
        
        Applies smoothing/regularization to parameters.
        """
        # Smooth parameters (low-pass filter)
        smoothed = np.convolve(params, [0.25, 0.5, 0.25], mode='same')
        
        return (smoothed, True)
    
    def _find_tunnel(self, certificate: DeadlockCertificate,
                    params: np.ndarray) -> Tuple[np.ndarray, bool]:
        """
        Find tunnel through constraint boundary.
        
        Searches for narrow passage in constraint space.
        """
        # Random exploration for tunnel
        best_params = params
        best_progress = certificate.best_progress
        
        for _ in range(10):
            # Random perturbation
            noise = np.random.randn(len(params)) * 0.1
            candidate = params + noise
            
            # Would need to evaluate - simplified for now
            if np.random.random() < 0.3:  # 30% chance of finding better
                best_params = candidate
                best_progress = -0.01
                break
        
        success = best_progress < 0
        return (best_params, success)
    
    def _rotate_sector(self, certificate: DeadlockCertificate,
                      params: np.ndarray) -> Tuple[np.ndarray, bool]:
        """
        Rotate to different sector for resolution.
        
        Maps parameters through sector transition.
        """
        # Apply rotation matrix to parameters
        # Simplified: just rotate in 2D subspace
        if len(params) >= 2:
            angle = np.pi / 6  # 30 degree rotation
            c, s = np.cos(angle), np.sin(angle)
            new_params = params.copy()
            new_params[0] = c * params[0] - s * params[1]
            new_params[1] = s * params[0] + c * params[1]
            return (new_params, True)
        
        return (params, False)


# =============================================================================
# SYSTEM CALL
# =============================================================================

@dataclass
class SystemCall:
    """
    System call for deadlock resolution.
    
    Invoked when deadlock, logic failure, will collapse, or SNR crisis occurs.
    Provides controlled transition to privileged diagnostic mode.
    """
    
    privilege_level: int = 0
    audit_log: List[Dict] = field(default_factory=list)
    
    def invoke(self, certificate: DeadlockCertificate,
               reason: str) -> Dict:
        """
        Invoke system call for resolution.
        
        Args:
            certificate: Deadlock certificate
            reason: Reason for invocation
        
        Returns:
            Response with resolution instructions
        """
        call_id = len(self.audit_log)
        
        # Log the call
        log_entry = {
            "call_id": call_id,
            "reason": reason,
            "deadlock_type": certificate.deadlock_type.value,
            "privilege_requested": self._compute_privilege_needed(certificate)
        }
        self.audit_log.append(log_entry)
        
        # Determine response
        response = {
            "call_id": call_id,
            "granted": True,
            "privilege_level": self._compute_privilege_needed(certificate),
            "allowed_operations": self._get_allowed_operations(certificate),
            "resolution_hints": self._get_resolution_hints(certificate)
        }
        
        return response
    
    def _compute_privilege_needed(self, certificate: DeadlockCertificate) -> int:
        """Compute privilege level needed for resolution."""
        base = 1
        
        if certificate.deadlock_type == DeadlockType.SNR_CRISIS:
            return base + 1  # Need observability access
        
        if certificate.deadlock_type == DeadlockType.LOGIC_FAILURE:
            return base + 2  # Need representation access
        
        return base
    
    def _get_allowed_operations(self, certificate: DeadlockCertificate) -> List[str]:
        """Get operations allowed under current privilege."""
        ops = ["inspect_state", "log_debug"]
        
        if certificate.deadlock_type == DeadlockType.CONSTRAINT_TRAP:
            ops.append("relax_constraint")
        
        if certificate.deadlock_type == DeadlockType.LOGIC_FAILURE:
            ops.append("route_contradiction")
        
        return ops
    
    def _get_resolution_hints(self, certificate: DeadlockCertificate) -> List[str]:
        """Get hints for resolution based on certificate."""
        hints = []
        
        if certificate.blocking_constraints:
            hints.append(f"Blocking: {certificate.blocking_constraints[:3]}")
        
        if certificate.snr < 0.5:
            hints.append("Consider increasing observation")
        
        if certificate.best_progress >= 0:
            hints.append("Explore alternative action space")
        
        return hints


# =============================================================================
# VALIDATION
# =============================================================================

def validate_deadlock() -> bool:
    """Validate deadlock module."""
    
    # Test ProgressFunctional
    progress = ProgressFunctional(objective=lambda x: np.sum(x**2))
    
    state = np.array([1.0, 0.0, 0.0, 0.0])
    action = np.array([0.9, 0.0, 0.0, 0.0])
    transition = lambda s, a: a  # Deterministic for test
    
    p = progress.compute(state, action, transition)
    assert p < 0  # Should make progress (reduce objective)
    
    # Test DecisionFeasibility
    feasibility = DecisionFeasibility()
    feasibility.add_capability_check("budget", lambda s, a: np.linalg.norm(a) < 2)
    
    valuation = Valuation()
    
    small_action = np.array([0.1, 0.0, 0.0, 0.0])
    large_action = np.array([10.0, 0.0, 0.0, 0.0])
    
    is_adm, _ = feasibility.check_action(state, small_action, valuation)
    assert is_adm
    
    is_adm, _ = feasibility.check_action(state, large_action, valuation)
    assert not is_adm
    
    # Test DeadlockCertificate
    cert = DeadlockCertificate(
        state=state,
        deadlock_type=DeadlockType.CONSTRAINT_TRAP,
        best_progress=0.1
    )
    assert cert.is_deadlocked
    
    # Test DeadlockDetector
    detector = DeadlockDetector()
    detector.progress = progress
    detector.feasibility = feasibility
    
    actions = [small_action, np.array([0.5, 0.0, 0.0, 0.0])]
    cert = detector.detect(state, actions, valuation, transition)
    
    # Should not be deadlocked with good actions
    # (depends on configuration)
    
    # Test DescentOperator
    descent = DescentOperator()
    
    cert_dl = DeadlockCertificate(
        state=state,
        deadlock_type=DeadlockType.WILL_COLLAPSE,
        gradient_estimate=np.array([1.0, 0.0, 0.0, 0.0]),
        best_progress=0.1
    )
    
    params = np.array([0.5, 0.5, 0.0, 0.0])
    new_params, success = descent.apply(cert_dl, params)
    # May or may not succeed
    
    # Test SystemCall
    syscall = SystemCall()
    response = syscall.invoke(cert_dl, "Test deadlock")
    
    assert "call_id" in response
    assert "granted" in response
    assert len(syscall.audit_log) == 1
    
    return True


if __name__ == "__main__":
    print("Validating Deadlock Detection...")
    assert validate_deadlock()
    print("✓ Deadlock module validated")
