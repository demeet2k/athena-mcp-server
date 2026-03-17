"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      LM DYNAMICS MODULE                                      ║
║                                                                              ║
║  Liminal Mathematics - TOME II Implementation                                ║
║                                                                              ║
║  Core Concepts:                                                              ║
║    - Hybrid dynamics: continuous flows + discrete typed events               ║
║    - Boundary operator ∂ as distinction constructor                          ║
║    - Liminal residents: fixed points of edge-local dynamics                  ║
║    - Boundary ecology: typed species with population dynamics                ║
║    - Organizational jets: (Ω,I,C,F) coordinates for near-critical            ║
║                                                                              ║
║  Central Thesis:                                                             ║
║    Emergence dynamics is typed routing, not narrative.                       ║
║    Every transition yields boundary distribution over typed species.         ║
║    Residents are certified dynamical objects with stability witnesses.       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any, Callable, Set
from enum import Enum
import numpy as np
from numpy.typing import NDArray
import hashlib


# ═══════════════════════════════════════════════════════════════════════════════
# DYNAMICAL STATE OBJECTS
# ═══════════════════════════════════════════════════════════════════════════════

class TimeModel(Enum):
    """Time model for dynamics."""
    DISCRETE = "discrete"       # Tick index n ∈ ℕ
    CONTINUOUS = "continuous"   # t ∈ ℝ₊
    HYBRID = "hybrid"           # Flow + jump events


@dataclass
class EnvelopeLedger:
    """
    Accumulated uncertainty budget and bound ledger.
    """
    entries: List[Dict[str, float]] = field(default_factory=list)
    total_error: float = 0.0
    
    def add_entry(self, source: str, error: float):
        """Add error entry to ledger."""
        self.entries.append({"source": source, "error": error})
        self.total_error += error
    
    def reset(self):
        """Reset ledger."""
        self.entries = []
        self.total_error = 0.0


@dataclass
class DynamicState:
    """
    Tome II dynamic state.
    
    DynState_n := (RegimeRef, ρ_n, EnvelopeLedger_n, Meta_n)
    """
    regime_ref: str
    state: NDArray
    envelope_ledger: EnvelopeLedger
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Time index
    time_index: int = 0
    time_value: float = 0.0
    
    @property
    def mass(self) -> float:
        """Total probability mass."""
        return np.real(np.trace(self.state)) if self.state is not None else 0.0
    
    def advance(self, new_state: NDArray, dt: float = 1.0) -> 'DynamicState':
        """Advance to next time step."""
        new_ledger = EnvelopeLedger(
            entries=self.envelope_ledger.entries.copy(),
            total_error=self.envelope_ledger.total_error
        )
        return DynamicState(
            regime_ref=self.regime_ref,
            state=new_state,
            envelope_ledger=new_ledger,
            metadata=self.metadata.copy(),
            time_index=self.time_index + 1,
            time_value=self.time_value + dt
        )


# ═══════════════════════════════════════════════════════════════════════════════
# BOUNDARY TYPE TAXONOMY
# ═══════════════════════════════════════════════════════════════════════════════

class BoundarySpecies(Enum):
    """
    Universal grammar of dynamical boundary species.
    """
    PROTO = "proto"             # Nascent, not yet differentiated
    BRANCH = "branch"           # Multi-branch with sheet index
    RESIDENT = "resident"       # Stable fixed point
    CHEATER = "cheater"         # Exploitative pathology
    AUTOIMMUNE = "autoimmune"   # Self-destructive pathology
    LOCK_IN = "lock_in"         # Stuck state
    FRAGMENT = "fragment"       # Broken piece
    DISSOLVE = "dissolve"       # Dissipating
    AMBIG = "ambig"             # Ambiguous, needs escalation
    FAIL = "fail"               # Certified failure


@dataclass
class BoundaryDistribution:
    """
    Distribution over boundary species at a transition.
    """
    masses: Dict[BoundarySpecies, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize all species to 0."""
        for species in BoundarySpecies:
            if species not in self.masses:
                self.masses[species] = 0.0
    
    @property
    def total_mass(self) -> float:
        """Total probability mass."""
        return sum(self.masses.values())
    
    def dominant_species(self) -> BoundarySpecies:
        """Return species with highest mass."""
        return max(self.masses.keys(), key=lambda k: self.masses[k])
    
    def normalize(self) -> 'BoundaryDistribution':
        """Normalize to probability distribution."""
        total = self.total_mass
        if total > 0:
            return BoundaryDistribution({k: v/total for k, v in self.masses.items()})
        return self


# ═══════════════════════════════════════════════════════════════════════════════
# HYBRID DYNAMICS OPERATORS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CPTPChannel:
    """
    Completely Positive Trace-Preserving channel.
    
    Continuous evolution step: ρ_{t+Δt} = T_Δt(ρ_t)
    """
    name: str
    kraus_operators: List[NDArray] = field(default_factory=list)
    
    def apply(self, state: NDArray) -> NDArray:
        """Apply channel to state."""
        if not self.kraus_operators:
            return state
        
        result = np.zeros_like(state)
        for K in self.kraus_operators:
            result += K @ state @ K.conj().T
        return result
    
    def verify_cptp(self) -> Tuple[bool, float]:
        """Verify channel is CPTP."""
        if not self.kraus_operators:
            return True, 0.0
        
        # Check sum K_i† K_i = I
        dim = self.kraus_operators[0].shape[0]
        total = np.zeros((dim, dim), dtype=complex)
        for K in self.kraus_operators:
            total += K.conj().T @ K
        
        error = np.linalg.norm(total - np.eye(dim))
        return error < 1e-10, error


@dataclass
class InstrumentBranch:
    """
    Single branch of a quantum instrument.
    """
    name: str
    channel: CPTPChannel
    boundary_type: BoundarySpecies = BoundarySpecies.PROTO


@dataclass 
class TypedInstrument:
    """
    Typed quantum instrument: {Φ_α} with sum CPTP.
    
    Event: ρ⁺ = Φ(ρ⁻) = Σ_α Φ_α(ρ⁻)
    
    Branches map to boundary types: stay/lift/liminal/fail
    """
    name: str
    branches: List[InstrumentBranch] = field(default_factory=list)
    
    def apply(self, state: NDArray) -> Tuple[NDArray, BoundaryDistribution]:
        """
        Apply instrument to state.
        
        Returns (total_output, boundary_distribution).
        """
        total_output = np.zeros_like(state)
        distribution = BoundaryDistribution()
        
        for branch in self.branches:
            branch_output = branch.channel.apply(state)
            branch_mass = np.real(np.trace(branch_output))
            
            total_output += branch_output
            distribution.masses[branch.boundary_type] = branch_mass
        
        return total_output, distribution
    
    def verify_cptp(self) -> Tuple[bool, float]:
        """Verify total instrument is CPTP."""
        total_error = 0.0
        for branch in self.branches:
            valid, error = branch.channel.verify_cptp()
            total_error += error
        return total_error < 1e-10 * len(self.branches), total_error


@dataclass
class HybridEvolution:
    """
    Hybrid evolution: alternating flows and events.
    """
    flow_channel: CPTPChannel
    event_instrument: TypedInstrument
    event_trigger: Callable[[DynamicState], bool]
    
    def step(self, state: DynamicState, dt: float = 1.0) -> Tuple[DynamicState, Optional[BoundaryDistribution]]:
        """
        Execute one hybrid step.
        
        Returns (new_state, event_distribution_if_triggered).
        """
        # Flow step
        new_rho = self.flow_channel.apply(state.state)
        new_state = state.advance(new_rho, dt)
        
        # Check event trigger
        if self.event_trigger(new_state):
            event_output, distribution = self.event_instrument.apply(new_state.state)
            new_state = DynamicState(
                regime_ref=state.regime_ref,
                state=event_output,
                envelope_ledger=state.envelope_ledger,
                metadata={**state.metadata, "event": True},
                time_index=new_state.time_index,
                time_value=new_state.time_value
            )
            return new_state, distribution
        
        return new_state, None


# ═══════════════════════════════════════════════════════════════════════════════
# ORGANIZATIONAL COORDINATES (Ω, I, C, F)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class OrganizationalCoordinates:
    """
    LM-dynamical order parameters: φ(ρ) = (Ω, I, C, F)
    
    - Ω (viability): margin-to-corridor-boundary, stability radius
    - I (identifiability): decisive label emission ability
    - C (coherence): observable-limited coherence
    - F (closure): bounded recurrence, repairability
    """
    omega: float  # Viability
    iota: float   # Identifiability  
    chi: float    # Coherence
    phi: float    # Closure
    
    @classmethod
    def compute(cls, state: NDArray, 
                corridor_margin: float = 1.0,
                stability_radius: float = 0.5) -> 'OrganizationalCoordinates':
        """
        Compute organizational coordinates from state.
        """
        # Ω: viability = margin / max_margin
        omega = min(1.0, corridor_margin)
        
        # I: identifiability = purity (simplified)
        trace_sq = np.real(np.trace(state @ state))
        trace = np.real(np.trace(state))
        iota = trace_sq / (trace ** 2) if trace > 0 else 0.0
        
        # C: coherence = off-diagonal magnitude
        dim = state.shape[0]
        off_diag = np.sum(np.abs(state)) - np.sum(np.abs(np.diag(state)))
        chi = off_diag / (dim * (dim - 1)) if dim > 1 else 0.0
        
        # F: closure = spectral radius of state
        eigenvalues = np.linalg.eigvals(state)
        phi = np.max(np.abs(eigenvalues))
        
        return cls(omega, iota, chi, phi)
    
    @property
    def emergence_potential(self) -> float:
        """Compute emergence potential Ω·I·C·F."""
        return self.omega * self.iota * self.chi * self.phi
    
    def is_viable(self, threshold: float = 0.1) -> bool:
        """Check if state is viable."""
        return self.omega >= threshold
    
    def is_identifiable(self, threshold: float = 0.5) -> bool:
        """Check if state is identifiable."""
        return self.iota >= threshold


# ═══════════════════════════════════════════════════════════════════════════════
# ORGANIZATIONAL JET LADDER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class OrganizationalJet:
    """
    Organizational jet for near-critical resolution.
    
    Ambig_m: choose control coordinate x, define certified response curves M(x),
    extract jets J^{(m)}_{x_0} with remainder bounds, resolve only with strict slack.
    """
    control_coordinate: str
    center: float
    order: int
    coefficients: List[float] = field(default_factory=list)
    remainder_bound: float = 0.0
    
    def evaluate(self, x: float) -> float:
        """Evaluate jet at x."""
        dx = x - self.center
        result = 0.0
        for i, c in enumerate(self.coefficients):
            result += c * (dx ** i)
        return result
    
    def can_resolve(self, threshold: float, slack: float) -> bool:
        """
        Check if jet can resolve decision at threshold with required slack.
        """
        value = self.evaluate(self.center)
        margin = abs(value - threshold)
        return margin > self.remainder_bound + slack


@dataclass
class EscalationPlan:
    """
    Plan for escalating ambiguity resolution.
    """
    current_order: int
    target_order: int
    method: str  # "increase_order", "refine_grid", "switch_estimator", etc.
    budget: int  # Maximum escalation steps
    
    def escalate(self, jet: OrganizationalJet) -> OrganizationalJet:
        """Escalate jet to higher order."""
        new_coeffs = jet.coefficients + [0.0] * (self.target_order - jet.order)
        return OrganizationalJet(
            control_coordinate=jet.control_coordinate,
            center=jet.center,
            order=self.target_order,
            coefficients=new_coeffs,
            remainder_bound=jet.remainder_bound / 2  # Assume tighter bound
        )


# ═══════════════════════════════════════════════════════════════════════════════
# LIMINAL RESIDENTS
# ═══════════════════════════════════════════════════════════════════════════════

class StabilityType(Enum):
    """Type of stability witness."""
    LYAPUNOV = "lyapunov"       # Lyapunov function decrease
    SPECTRAL_GAP = "spectral"   # Spectral gap
    CONTRACTION = "contraction" # Contraction mapping


@dataclass
class StabilityWitness:
    """
    Witness for resident stability.
    """
    stability_type: StabilityType
    margin: float  # Stability margin
    radius: float  # Stability radius
    
    def is_certified(self, slack: float = 0.01) -> bool:
        """Check if stability is certified with slack."""
        return self.margin >= slack


@dataclass
class LiminalResident:
    """
    Liminal resident: fixed point of edge-local dynamics.
    
    Equipped with:
    - Detection algorithm
    - Stability certificate
    - Residence/escape times
    - Lineage across cycles
    """
    name: str
    fixed_point: NDArray
    edge_ref: str  # Reference to liminal edge
    
    # Stability
    stability_witness: Optional[StabilityWitness] = None
    residual_bound: float = 0.0
    
    # Timing
    dwell_time_mean: float = float('inf')
    escape_time_mean: float = float('inf')
    
    # Lineage
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
    
    def verify_fixed_point(self, dynamics: CPTPChannel, 
                           tolerance: float = 1e-10) -> bool:
        """Verify this is a fixed point."""
        evolved = dynamics.apply(self.fixed_point)
        residual = np.linalg.norm(evolved - self.fixed_point)
        return residual < tolerance
    
    def is_metastable(self, min_dwell: float = 10.0) -> bool:
        """Check if resident is metastable."""
        return self.dwell_time_mean >= min_dwell


# ═══════════════════════════════════════════════════════════════════════════════
# BOUNDARY ECOLOGY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SpeciesPopulation:
    """
    Population of boundary species across cycles.
    """
    species: BoundarySpecies
    mass_history: List[float] = field(default_factory=list)
    
    @property
    def current_mass(self) -> float:
        """Current population mass."""
        return self.mass_history[-1] if self.mass_history else 0.0
    
    @property
    def growth_rate(self) -> float:
        """Estimated growth rate."""
        if len(self.mass_history) < 2:
            return 0.0
        return self.mass_history[-1] / self.mass_history[-2] if self.mass_history[-2] > 0 else 0.0


@dataclass
class ContainmentLaw:
    """
    Law governing containment of pathological species.
    """
    target_species: BoundarySpecies
    max_mass: float
    suppression_rate: float
    
    def check_violation(self, population: SpeciesPopulation) -> bool:
        """Check if containment is violated."""
        return population.current_mass > self.max_mass
    
    def apply_suppression(self, mass: float) -> float:
        """Apply suppression to reduce mass."""
        return mass * (1 - self.suppression_rate)


@dataclass
class LiminalEcology:
    """
    Boundary ecology: species population dynamics.
    """
    populations: Dict[BoundarySpecies, SpeciesPopulation] = field(default_factory=dict)
    containment_laws: List[ContainmentLaw] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize populations for all species."""
        for species in BoundarySpecies:
            if species not in self.populations:
                self.populations[species] = SpeciesPopulation(species)
    
    def update(self, distribution: BoundaryDistribution):
        """Update populations from boundary distribution."""
        for species, mass in distribution.masses.items():
            self.populations[species].mass_history.append(mass)
    
    def apply_containment(self) -> Dict[BoundarySpecies, float]:
        """Apply containment laws and return suppressed masses."""
        suppressed = {}
        for law in self.containment_laws:
            pop = self.populations[law.target_species]
            if law.check_violation(pop):
                old_mass = pop.current_mass
                new_mass = law.apply_suppression(old_mass)
                suppressed[law.target_species] = old_mass - new_mass
                if pop.mass_history:
                    pop.mass_history[-1] = new_mass
        return suppressed
    
    def pathology_check(self) -> Dict[str, bool]:
        """Check for ecological pathologies."""
        return {
            "cheater_outbreak": self.populations[BoundarySpecies.CHEATER].current_mass > 0.1,
            "autoimmune_risk": self.populations[BoundarySpecies.AUTOIMMUNE].current_mass > 0.05,
            "lock_in": self.populations[BoundarySpecies.LOCK_IN].current_mass > 0.3,
            "fragmentation": self.populations[BoundarySpecies.FRAGMENT].current_mass > 0.2,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# TRAJECTORY AND LOGS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TrajectoryPoint:
    """Single point in a trajectory."""
    time: float
    state: NDArray
    coordinates: OrganizationalCoordinates
    boundary_dist: Optional[BoundaryDistribution] = None


@dataclass
class Trajectory:
    """
    Proof-carrying trajectory log.
    """
    points: List[TrajectoryPoint] = field(default_factory=list)
    regime_ref: str = ""
    merkle_root: Optional[str] = None
    
    def add_point(self, point: TrajectoryPoint):
        """Add point to trajectory."""
        self.points.append(point)
        self._update_merkle()
    
    def _update_merkle(self):
        """Update Merkle root."""
        if not self.points:
            self.merkle_root = None
            return
        
        hashes = []
        for p in self.points:
            data = f"{p.time}:{p.coordinates.emergence_potential}"
            hashes.append(hashlib.sha256(data.encode()).hexdigest())
        
        while len(hashes) > 1:
            new_hashes = []
            for i in range(0, len(hashes), 2):
                if i + 1 < len(hashes):
                    combined = hashes[i] + hashes[i+1]
                else:
                    combined = hashes[i]
                new_hashes.append(hashlib.sha256(combined.encode()).hexdigest())
            hashes = new_hashes
        
        self.merkle_root = hashes[0] if hashes else None
    
    @property
    def duration(self) -> float:
        """Total trajectory duration."""
        if len(self.points) < 2:
            return 0.0
        return self.points[-1].time - self.points[0].time


# ═══════════════════════════════════════════════════════════════════════════════
# POLE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LMDynamicsPoleBridge:
    """
    Bridge between LM Dynamics and four-pole framework.
    """
    
    @staticmethod
    def integration() -> str:
        return """
        LM DYNAMICS (TOME II) ↔ FRAMEWORK
        
        ═══════════════════════════════════════════════════════════════
        HYBRID DYNAMICS
        ═══════════════════════════════════════════════════════════════
        
        Time models: DISCRETE | CONTINUOUS | HYBRID
        
        Continuous: ρ_{t+Δt} = T_Δt(ρ_t)  [CPTP channel]
        Discrete: ρ⁺ = Φ(ρ⁻) = Σ_α Φ_α(ρ⁻)  [Typed instrument]
        
        Every evolution step is:
          - Total (typed outcome, never undefined)
          - Proof-carrying (certificates + replay)
          - Auditable (Merkleized trajectory logs)
          
        ═══════════════════════════════════════════════════════════════
        BOUNDARY SPECIES TAXONOMY
        ═══════════════════════════════════════════════════════════════
        
        Universal grammar:
          PROTO | BRANCH | RESIDENT | CHEATER | AUTOIMMUNE |
          LOCK_IN | FRAGMENT | DISSOLVE | AMBIG | FAIL
          
        Every transition → boundary distribution over species
        Classification requires certified slack
        
        ═══════════════════════════════════════════════════════════════
        ORGANIZATIONAL COORDINATES
        ═══════════════════════════════════════════════════════════════
        
        φ(ρ) = (Ω, I, C, F)
          Ω: viability (corridor margin, stability radius)
          I: identifiability (decisive label emission)
          C: coherence (observable-limited)
          F: closure (bounded recurrence)
          
        Emergence potential = Ω · I · C · F
        
        ═══════════════════════════════════════════════════════════════
        ORGANIZATIONAL JETS
        ═══════════════════════════════════════════════════════════════
        
        Near-critical resolution:
          1. Choose control coordinate x
          2. Define response curves M(x)
          3. Extract jet J^{(m)}_{x₀}
          4. Resolve only with strict slack
          5. Escalate m → m' if insufficient
          
        ═══════════════════════════════════════════════════════════════
        LIMINAL RESIDENTS
        ═══════════════════════════════════════════════════════════════
        
        Fixed points of edge-local dynamics with:
          - Detection algorithm
          - Stability witness (Lyapunov/spectral/contraction)
          - Dwell/escape times
          - Lineage (parent/children across cycles)
          
        ═══════════════════════════════════════════════════════════════
        BOUNDARY ECOLOGY
        ═══════════════════════════════════════════════════════════════
        
        Species populations with:
          - Mass dynamics across cycles
          - Containment laws (suppress cheaters, prevent autoimmune)
          - Pathology detection (outbreak, lock-in, fragmentation)
          
        ═══════════════════════════════════════════════════════════════
        POLE CORRESPONDENCE
        ═══════════════════════════════════════════════════════════════
        
        D: Discrete events, typed instruments
        Ω: Continuous flows, CPTP channels
        Σ: Boundary distributions, ecological populations
        Ψ: Organizational jets, resident lineages
        """


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def dynamic_state(regime: str, state: NDArray) -> DynamicState:
    """Create dynamic state."""
    return DynamicState(
        regime_ref=regime,
        state=state,
        envelope_ledger=EnvelopeLedger()
    )


def cptp_channel(name: str, kraus: List[NDArray] = None) -> CPTPChannel:
    """Create CPTP channel."""
    return CPTPChannel(name, kraus or [])


def typed_instrument(name: str, branches: List[InstrumentBranch] = None) -> TypedInstrument:
    """Create typed instrument."""
    return TypedInstrument(name, branches or [])


def organizational_coordinates(state: NDArray) -> OrganizationalCoordinates:
    """Compute organizational coordinates."""
    return OrganizationalCoordinates.compute(state)


def liminal_resident(name: str, fixed_point: NDArray, edge: str) -> LiminalResident:
    """Create liminal resident."""
    return LiminalResident(name, fixed_point, edge)


def liminal_ecology() -> LiminalEcology:
    """Create liminal ecology."""
    return LiminalEcology()


def trajectory() -> Trajectory:
    """Create trajectory."""
    return Trajectory()


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Time
    'TimeModel',
    
    # State
    'EnvelopeLedger',
    'DynamicState',
    
    # Boundary
    'BoundarySpecies',
    'BoundaryDistribution',
    
    # Dynamics
    'CPTPChannel',
    'InstrumentBranch',
    'TypedInstrument',
    'HybridEvolution',
    
    # Coordinates
    'OrganizationalCoordinates',
    'OrganizationalJet',
    'EscalationPlan',
    
    # Residents
    'StabilityType',
    'StabilityWitness',
    'LiminalResident',
    
    # Ecology
    'SpeciesPopulation',
    'ContainmentLaw',
    'LiminalEcology',
    
    # Trajectory
    'TrajectoryPoint',
    'Trajectory',
    
    # Bridge
    'LMDynamicsPoleBridge',
    
    # Functions
    'dynamic_state',
    'cptp_channel',
    'typed_instrument',
    'organizational_coordinates',
    'liminal_resident',
    'liminal_ecology',
    'trajectory',
]
