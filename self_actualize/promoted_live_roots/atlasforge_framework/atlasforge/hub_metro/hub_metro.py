"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           HUB METRO MODULE                                   ║
║                                                                              ║
║  The Mathematical Hub System: Fourier / Derivative / Log / Wick             ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Hubs are transformation centers that convert between representations     ║
║    Each hub has a LAW (algebraic identity) and requires a TICKET (gauge)    ║
║                                                                              ║
║  Gauge Neutrality:                                                           ║
║    RSpin(Spin(Rep)) ≈ Rep (ticket must be stored)                           ║
║                                                                              ║
║  The Four Hubs:                                                              ║
║    FOURIER:    DFT(a*b) = DFT(a) ⊙ DFT(b)                                   ║
║    DERIVATIVE: D(fg) = (Df)g + f(Dg)                                        ║
║    LOG:        log(ab) = log(a) + log(b)  (branch ticket required)         ║
║    WICK:       E[e^{λX}] = exp(K(λ))     (mgf exists condition)            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable
from enum import Enum
import numpy as np
from numpy.typing import NDArray
import hashlib


# ═══════════════════════════════════════════════════════════════════════════════
# HUB TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class HubType(Enum):
    """The four fundamental hubs."""
    FOURIER = "Fourier"       # Convolution ↔ Multiplication
    DERIVATIVE = "Derivative"  # Leibniz rule
    LOG = "Log"               # Multiplication ↔ Addition
    WICK = "Wick"             # Moment generating functions


@dataclass
class HubLaw:
    """
    The algebraic law governing a hub transformation.
    """
    hub_type: HubType
    formula: str
    preconditions: List[str]
    inverse_formula: str
    
    @classmethod
    def fourier(cls) -> 'HubLaw':
        """Fourier convolution theorem."""
        return cls(
            HubType.FOURIER,
            "DFT(a * b) = DFT(a) ⊙ DFT(b)",
            ["Sequences defined on same domain", "DFT ticket stored"],
            "IDFT(Â ⊙ B̂) = a * b"
        )
    
    @classmethod
    def derivative(cls) -> 'HubLaw':
        """Leibniz product rule."""
        return cls(
            HubType.DERIVATIVE,
            "D(fg) = (Df)g + f(Dg)",
            ["Functions differentiable", "Order of differentiation"],
            "∫(Df)g = fg - ∫f(Dg) (integration by parts)"
        )
    
    @classmethod
    def log(cls) -> 'HubLaw':
        """Logarithm product rule."""
        return cls(
            HubType.LOG,
            "log(ab) = log(a) + log(b)",
            ["a, b > 0", "Branch cut specified", "Branch ticket stored"],
            "exp(log(a) + log(b)) = ab"
        )
    
    @classmethod
    def wick(cls) -> 'HubLaw':
        """Wick/cumulant generating function."""
        return cls(
            HubType.WICK,
            "E[e^{λX}] = exp(K(λ))",
            ["MGF exists in neighborhood of 0", "λ in convergence domain"],
            "log E[e^{λX}] = K(λ) (cumulant generating function)"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TICKETS (GAUGE RECORDS)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HubTicket:
    """
    A ticket recording transformation metadata.
    
    Required for gauge neutrality: RSpin(Spin(Rep)) ≈ Rep
    """
    hub_type: HubType
    forward_params: Dict[str, Any] = field(default_factory=dict)
    inverse_params: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    checksum: str = ""
    
    def __post_init__(self):
        """Compute checksum."""
        data = f"{self.hub_type.name}|{self.forward_params}|{self.inverse_params}"
        self.checksum = hashlib.sha256(data.encode()).hexdigest()[:16]
    
    @classmethod
    def fourier_ticket(cls, n: int, normalization: str = "ortho") -> 'HubTicket':
        """Create Fourier transform ticket."""
        return cls(
            HubType.FOURIER,
            {"n": n, "normalization": normalization, "direction": "forward"},
            {"n": n, "normalization": normalization, "direction": "inverse"}
        )
    
    @classmethod
    def log_ticket(cls, branch: int = 0) -> 'HubTicket':
        """Create logarithm ticket with branch cut."""
        return cls(
            HubType.LOG,
            {"branch": branch, "cut": "negative_real"},
            {"branch": branch}
        )
    
    @classmethod
    def derivative_ticket(cls, order: int = 1, variable: str = "x") -> 'HubTicket':
        """Create derivative ticket."""
        return cls(
            HubType.DERIVATIVE,
            {"order": order, "variable": variable},
            {"order": -order, "variable": variable}
        )
    
    @classmethod
    def wick_ticket(cls, domain: Tuple[float, float] = (-1, 1)) -> 'HubTicket':
        """Create Wick/MGF ticket."""
        return cls(
            HubType.WICK,
            {"convergence_domain": domain},
            {"convergence_domain": domain}
        )


# ═══════════════════════════════════════════════════════════════════════════════
# HUB WORD (COMPOSITION)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HubWord:
    """
    A composition of hub transformations.
    
    HubWord skeleton: H⁻¹ · H (round-trip)
    """
    operations: List[Tuple[HubType, bool]] = field(default_factory=list)  # (hub, is_inverse)
    tickets: List[HubTicket] = field(default_factory=list)
    
    def append(self, hub: HubType, inverse: bool = False, ticket: HubTicket = None):
        """Append a hub operation."""
        self.operations.append((hub, inverse))
        if ticket:
            self.tickets.append(ticket)
    
    def simplify(self) -> 'HubWord':
        """
        Simplify hub word by canceling H⁻¹H pairs.
        """
        simplified = []
        for hub, inv in self.operations:
            if simplified and simplified[-1] == (hub, not inv):
                simplified.pop()
            else:
                simplified.append((hub, inv))
        result = HubWord()
        result.operations = simplified
        return result
    
    def is_identity(self) -> bool:
        """Check if word simplifies to identity."""
        return len(self.simplify().operations) == 0
    
    def __str__(self) -> str:
        parts = []
        for hub, inv in self.operations:
            name = hub.value
            if inv:
                name += "⁻¹"
            parts.append(name)
        return " · ".join(parts) if parts else "id"


# ═══════════════════════════════════════════════════════════════════════════════
# FOURIER HUB
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FourierHub:
    """
    Fourier transform hub.
    
    Law: DFT(a * b) = DFT(a) ⊙ DFT(b)
    """
    n: int
    normalization: str = "ortho"  # "ortho", "forward", "backward"
    
    @property
    def law(self) -> HubLaw:
        return HubLaw.fourier()
    
    def dft(self, x: NDArray) -> Tuple[NDArray, HubTicket]:
        """
        Compute DFT with ticket.
        
        Returns (DFT(x), ticket).
        """
        ticket = HubTicket.fourier_ticket(len(x), self.normalization)
        if self.normalization == "ortho":
            result = np.fft.fft(x) / np.sqrt(len(x))
        else:
            result = np.fft.fft(x)
        return result, ticket
    
    def idft(self, x_hat: NDArray, ticket: HubTicket) -> NDArray:
        """
        Compute inverse DFT using ticket.
        """
        if self.normalization == "ortho":
            return np.fft.ifft(x_hat) * np.sqrt(len(x_hat))
        else:
            return np.fft.ifft(x_hat)
    
    def convolution_via_hub(self, a: NDArray, b: NDArray) -> Tuple[NDArray, HubTicket]:
        """
        Compute cyclic convolution via Fourier hub.
        
        a * b = IDFT(DFT(a) ⊙ DFT(b))
        """
        a_hat, ticket = self.dft(a)
        b_hat, _ = self.dft(b)
        c_hat = a_hat * b_hat  # Hadamard product
        c = self.idft(c_hat, ticket)
        return c.real, ticket
    
    def verify_law(self, a: NDArray, b: NDArray, tolerance: float = 1e-10) -> bool:
        """
        Verify convolution theorem: DFT(a*b) = DFT(a)⊙DFT(b)
        """
        # Direct convolution
        c_direct = np.convolve(a, b, mode='full')[:len(a)]  # Simplified
        
        # Via hub
        c_hub, _ = self.convolution_via_hub(a, b)
        
        # For cyclic convolution comparison
        c_cyclic = np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))
        
        return np.allclose(c_hub, c_cyclic, atol=tolerance)


# ═══════════════════════════════════════════════════════════════════════════════
# LOG HUB
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LogHub:
    """
    Logarithm hub.
    
    Law: log(ab) = log(a) + log(b) (with branch ticket)
    """
    branch: int = 0  # Principal branch
    
    @property
    def law(self) -> HubLaw:
        return HubLaw.log()
    
    def log(self, z: complex) -> Tuple[complex, HubTicket]:
        """
        Compute complex log with ticket.
        """
        ticket = HubTicket.log_ticket(self.branch)
        result = np.log(z) + 2j * np.pi * self.branch
        return result, ticket
    
    def exp(self, w: complex, ticket: HubTicket) -> complex:
        """
        Inverse: exp using ticket.
        """
        return np.exp(w)
    
    def product_via_hub(self, a: complex, b: complex) -> Tuple[complex, HubTicket]:
        """
        Compute product via log hub.
        
        ab = exp(log(a) + log(b))
        """
        log_a, ticket = self.log(a)
        log_b, _ = self.log(b)
        return self.exp(log_a + log_b, ticket), ticket
    
    def verify_law(self, a: complex, b: complex, tolerance: float = 1e-10) -> bool:
        """
        Verify log(ab) = log(a) + log(b) up to 2πi.
        """
        log_ab, _ = self.log(a * b)
        log_a, _ = self.log(a)
        log_b, _ = self.log(b)
        
        diff = log_ab - (log_a + log_b)
        # Should differ by 2πik for some integer k
        k = np.round(diff.imag / (2 * np.pi))
        residual = diff - 2j * np.pi * k
        
        return np.abs(residual) < tolerance


# ═══════════════════════════════════════════════════════════════════════════════
# DERIVATIVE HUB
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DerivativeHub:
    """
    Derivative hub.
    
    Law: D(fg) = (Df)g + f(Dg) (Leibniz rule)
    """
    order: int = 1
    
    @property
    def law(self) -> HubLaw:
        return HubLaw.derivative()
    
    def differentiate(self, f: Callable, x: float, 
                      h: float = 1e-8) -> Tuple[float, HubTicket]:
        """
        Numerical differentiation with ticket.
        """
        ticket = HubTicket.derivative_ticket(self.order)
        # Central difference
        result = (f(x + h) - f(x - h)) / (2 * h)
        return result, ticket
    
    def integrate(self, df: Callable, x0: float, x1: float,
                  ticket: HubTicket) -> float:
        """
        Inverse: numerical integration.
        """
        from scipy import integrate
        result, _ = integrate.quad(df, x0, x1)
        return result
    
    def leibniz_product(self, f: Callable, g: Callable, x: float,
                        h: float = 1e-8) -> Tuple[float, float]:
        """
        Verify Leibniz rule: D(fg) = (Df)g + f(Dg)
        
        Returns (D(fg), (Df)g + f(Dg)).
        """
        fg = lambda t: f(t) * g(t)
        
        D_fg, _ = self.differentiate(fg, x, h)
        Df, _ = self.differentiate(f, x, h)
        Dg, _ = self.differentiate(g, x, h)
        
        leibniz = Df * g(x) + f(x) * Dg
        
        return D_fg, leibniz


# ═══════════════════════════════════════════════════════════════════════════════
# WICK HUB
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class WickHub:
    """
    Wick/MGF hub for probability.
    
    Law: E[e^{λX}] = exp(K(λ)) where K is cumulant generating function.
    
    Precondition: MGF must exist in neighborhood of 0.
    """
    convergence_domain: Tuple[float, float] = (-1.0, 1.0)
    
    @property
    def law(self) -> HubLaw:
        return HubLaw.wick()
    
    def mgf_exists(self, samples: NDArray, lambda_max: float = 1.0) -> bool:
        """
        Check if MGF appears to exist (empirical check).
        """
        try:
            for lam in np.linspace(-lambda_max, lambda_max, 20):
                val = np.mean(np.exp(lam * samples))
                if not np.isfinite(val):
                    return False
            return True
        except:
            return False
    
    def compute_mgf(self, samples: NDArray, lambda_val: float) -> Tuple[float, HubTicket]:
        """
        Compute empirical MGF E[e^{λX}] with ticket.
        """
        ticket = HubTicket.wick_ticket(self.convergence_domain)
        mgf = np.mean(np.exp(lambda_val * samples))
        return mgf, ticket
    
    def compute_cgf(self, samples: NDArray, lambda_val: float) -> float:
        """
        Compute cumulant generating function K(λ) = log E[e^{λX}].
        """
        mgf, _ = self.compute_mgf(samples, lambda_val)
        return np.log(mgf)
    
    def chernoff_optimize(self, samples: NDArray, target_t: float) -> Tuple[float, float]:
        """
        Optimize Chernoff bound: min_λ exp(nK(λ) - λt)
        
        For Rademacher: tanh(λ*) = t/n
        """
        from scipy.optimize import minimize_scalar
        
        n = len(samples)
        
        def bound(lam):
            if lam <= 0:
                return np.inf
            cgf = self.compute_cgf(samples, lam)
            return np.exp(n * cgf - lam * target_t)
        
        result = minimize_scalar(bound, bounds=(0.01, 5.0), method='bounded')
        return result.x, result.fun
    
    def rademacher_tail_bound(self, n: int, t: float) -> float:
        """
        Closed-form Rademacher tail bound.
        
        P(Sₙ ≥ t) ≤ exp(n·log(cosh(λ*)) - λ*t)
        where tanh(λ*) = t/n
        """
        if t >= n:
            return 0.0
        
        lambda_star = np.arctanh(t / n)
        bound = np.exp(n * np.log(np.cosh(lambda_star)) - lambda_star * t)
        return bound


# ═══════════════════════════════════════════════════════════════════════════════
# HUB METRO MAP
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HubMetroMap:
    """
    The complete hub metro system.
    
    Manages connections between hubs and tracks tickets.
    """
    fourier: FourierHub = field(default_factory=lambda: FourierHub(64))
    log: LogHub = field(default_factory=LogHub)
    derivative: DerivativeHub = field(default_factory=DerivativeHub)
    wick: WickHub = field(default_factory=WickHub)
    
    active_tickets: List[HubTicket] = field(default_factory=list)
    
    def enter_hub(self, hub_type: HubType) -> HubLaw:
        """Get the law for entering a hub."""
        laws = {
            HubType.FOURIER: HubLaw.fourier(),
            HubType.DERIVATIVE: HubLaw.derivative(),
            HubType.LOG: HubLaw.log(),
            HubType.WICK: HubLaw.wick()
        }
        return laws[hub_type]
    
    def store_ticket(self, ticket: HubTicket):
        """Store a ticket for later inverse."""
        self.active_tickets.append(ticket)
    
    def retrieve_ticket(self, hub_type: HubType) -> Optional[HubTicket]:
        """Retrieve matching ticket."""
        for t in reversed(self.active_tickets):
            if t.hub_type == hub_type:
                self.active_tickets.remove(t)
                return t
        return None
    
    def gauge_neutrality_check(self) -> bool:
        """
        Check gauge neutrality: all tickets should be consumed.
        
        RSpin(Spin(Rep)) ≈ Rep requires ticket balance.
        """
        return len(self.active_tickets) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HubMetroPoleBridge:
    """
    Bridge between Hub Metro and four-pole framework.
    """
    
    @staticmethod
    def flower_chart() -> str:
        """Hubs live in ✿ (Flower) chart."""
        return "Hub Metro ↔ ✿ chart: transform/domain operations"
    
    @staticmethod
    def c_pole() -> str:
        """Connection to C-pole."""
        return "C-pole ↔ Continuous transformations, gauge operations"
    
    @staticmethod
    def gateway() -> str:
        """Hub laws as gateways."""
        return "Each hub law is a gateway between representations"
    
    @staticmethod
    def integration() -> str:
        return """
        HUB METRO ↔ FRAMEWORK
        
        ✿ Flower Chart: Hub transformations
        C-pole: Continuous/smooth operations
        
        Four Hubs:
          FOURIER:    DFT(a*b) = DFT(a) ⊙ DFT(b)
          DERIVATIVE: D(fg) = (Df)g + f(Dg)
          LOG:        log(ab) = log(a) + log(b)
          WICK:       E[e^{λX}] = exp(K(λ))
        
        Gauge Neutrality: RSpin(Spin(Rep)) ≈ Rep
        """


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def hub_law(hub_type: HubType) -> HubLaw:
    """Get hub law."""
    laws = {
        HubType.FOURIER: HubLaw.fourier(),
        HubType.DERIVATIVE: HubLaw.derivative(),
        HubType.LOG: HubLaw.log(),
        HubType.WICK: HubLaw.wick()
    }
    return laws[hub_type]


def fourier_hub(n: int = 64) -> FourierHub:
    """Create Fourier hub."""
    return FourierHub(n)


def log_hub(branch: int = 0) -> LogHub:
    """Create Log hub."""
    return LogHub(branch)


def derivative_hub(order: int = 1) -> DerivativeHub:
    """Create Derivative hub."""
    return DerivativeHub(order)


def wick_hub(domain: Tuple[float, float] = (-1, 1)) -> WickHub:
    """Create Wick hub."""
    return WickHub(domain)


def hub_metro_map() -> HubMetroMap:
    """Create hub metro map."""
    return HubMetroMap()


def hub_word() -> HubWord:
    """Create empty hub word."""
    return HubWord()


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    'HubType',
    
    # Laws and Tickets
    'HubLaw',
    'HubTicket',
    'HubWord',
    
    # Hubs
    'FourierHub',
    'LogHub',
    'DerivativeHub',
    'WickHub',
    
    # Metro
    'HubMetroMap',
    
    # Bridge
    'HubMetroPoleBridge',
    
    # Functions
    'hub_law',
    'fourier_hub',
    'log_hub',
    'derivative_hub',
    'wick_hub',
    'hub_metro_map',
    'hub_word',
]
