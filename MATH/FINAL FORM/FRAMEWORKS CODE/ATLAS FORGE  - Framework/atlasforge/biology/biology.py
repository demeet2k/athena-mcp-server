"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    BIOLOGY AND PHYSICS MODULE                                ║
║                                                                              ║
║  Morphogen Gradients, Turing Patterns, Neural Signaling, Homeostasis         ║
║                                                                              ║
║  Core Principle:                                                             ║
║    The same tetradic kernel (Klein-4, 4-state homeostasis) governs          ║
║    constraint satisfaction at every biological scale:                        ║
║      - Molecular: 4 nucleotides, 4-state ion channels                       ║
║      - Cellular: 4 phases of cell cycle, 4 tissue types                     ║
║      - Organ: Tetradic control loops (hot/cold, wet/dry)                    ║
║      - Organism: Greek humoral tetrads (Fire/Air/Water/Earth)               ║
║                                                                              ║
║  Reaction-Diffusion Systems:                                                 ║
║    ∂u/∂t = D_u∇²u + f(u,v)                                                  ║
║    ∂v/∂t = D_v∇²v + g(u,v)                                                  ║
║                                                                              ║
║  Turing Instability: D_v >> D_u leads to spontaneous pattern formation      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Callable, Any
from enum import Enum, auto
import numpy as np
from numpy.typing import NDArray
from scipy.ndimage import laplace
from scipy.integrate import solve_ivp


# ═══════════════════════════════════════════════════════════════════════════════
# TETRADIC STATE SYSTEMS - THE UNIVERSAL 4-STATE KERNEL
# ═══════════════════════════════════════════════════════════════════════════════

class TetradicState(Enum):
    """
    Four fundamental states in biological/physical systems.
    
    Mapped to Klein-4 group {00, 01, 10, 11} ≅ ℤ₂ × ℤ₂.
    
    Classical correspondences:
        - Greek elements: Fire, Air, Water, Earth
        - Qualities: Hot/Cold, Wet/Dry
        - Humors: Yellow bile, Blood, Phlegm, Black bile
        - Cell phases: G1, S, G2, M
    """
    STATE_00 = (0, 0)  # Fire / Hot-Dry
    STATE_01 = (0, 1)  # Air / Hot-Wet
    STATE_10 = (1, 0)  # Earth / Cold-Dry
    STATE_11 = (1, 1)  # Water / Cold-Wet
    
    @property
    def bits(self) -> Tuple[int, int]:
        return self.value
    
    @property
    def as_int(self) -> int:
        """Convert to integer 0-3."""
        return self.bits[0] * 2 + self.bits[1]
    
    @classmethod
    def from_int(cls, n: int) -> 'TetradicState':
        """Create from integer 0-3."""
        n = n % 4
        bits = (n // 2, n % 2)
        for state in cls:
            if state.bits == bits:
                return state
        raise ValueError(f"Invalid state index: {n}")
    
    def flip_bit0(self) -> 'TetradicState':
        """Klein-4 R action: flip first bit."""
        new_bits = (1 - self.bits[0], self.bits[1])
        return TetradicState(new_bits)
    
    def flip_bit1(self) -> 'TetradicState':
        """Klein-4 S action: flip second bit."""
        new_bits = (self.bits[0], 1 - self.bits[1])
        return TetradicState(new_bits)
    
    def complement(self) -> 'TetradicState':
        """Klein-4 C action: flip both bits."""
        new_bits = (1 - self.bits[0], 1 - self.bits[1])
        return TetradicState(new_bits)


# Classical element names
FIRE = TetradicState.STATE_00
AIR = TetradicState.STATE_01
EARTH = TetradicState.STATE_10
WATER = TetradicState.STATE_11


@dataclass
class TetradicController:
    """
    4-state homeostatic controller.
    
    Maintains system in one of four equilibrium states,
    with transitions governed by environmental signals.
    
    Properties:
        - State transitions via Klein-4 bit flips
        - Stable attractors at each state
        - Hysteresis prevents rapid oscillation
    """
    current_state: TetradicState = FIRE
    hysteresis_threshold: float = 0.1
    transition_rates: Dict[Tuple[int, int], float] = field(default_factory=dict)
    
    def __post_init__(self):
        # Default equal transition rates
        if not self.transition_rates:
            for i in range(4):
                for j in range(4):
                    if i != j:
                        self.transition_rates[(i, j)] = 1.0
    
    def signal_response(self, signal_0: float, signal_1: float) -> TetradicState:
        """
        Determine target state based on two-channel signal.
        
        signal_0: controls bit 0 (negative → 0, positive → 1)
        signal_1: controls bit 1 (negative → 0, positive → 1)
        """
        # Apply hysteresis
        bit0 = self.current_state.bits[0]
        bit1 = self.current_state.bits[1]
        
        if signal_0 > self.hysteresis_threshold:
            bit0 = 1
        elif signal_0 < -self.hysteresis_threshold:
            bit0 = 0
        
        if signal_1 > self.hysteresis_threshold:
            bit1 = 1
        elif signal_1 < -self.hysteresis_threshold:
            bit1 = 0
        
        return TetradicState((bit0, bit1))
    
    def update(self, signal_0: float, signal_1: float) -> bool:
        """
        Update state based on signals.
        Returns True if state changed.
        """
        target = self.signal_response(signal_0, signal_1)
        if target != self.current_state:
            self.current_state = target
            return True
        return False
    
    def transition_matrix(self) -> NDArray[np.float64]:
        """4×4 transition rate matrix."""
        Q = np.zeros((4, 4))
        for (i, j), rate in self.transition_rates.items():
            Q[i, j] = rate
        # Set diagonal for row sum = 0
        for i in range(4):
            Q[i, i] = -np.sum(Q[i, :])
        return Q


# ═══════════════════════════════════════════════════════════════════════════════
# REACTION-DIFFUSION SYSTEMS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ReactionDiffusionSystem:
    """
    General two-species reaction-diffusion system.
    
    ∂u/∂t = D_u∇²u + f(u,v)
    ∂v/∂t = D_v∇²v + g(u,v)
    
    The ratio D_v/D_u determines pattern formation behavior.
    """
    D_u: float = 0.1      # Activator diffusion
    D_v: float = 1.0      # Inhibitor diffusion
    grid_size: Tuple[int, int] = (64, 64)
    dx: float = 1.0       # Spatial step
    dt: float = 0.01      # Time step
    
    # Reaction functions (to be set)
    f: Callable[[NDArray, NDArray], NDArray] = None  # f(u,v)
    g: Callable[[NDArray, NDArray], NDArray] = None  # g(u,v)
    
    def __post_init__(self):
        nx, ny = self.grid_size
        self.u = np.random.rand(nx, ny) * 0.1
        self.v = np.random.rand(nx, ny) * 0.1
    
    def laplacian(self, field: NDArray) -> NDArray:
        """Compute discrete Laplacian with periodic boundaries."""
        return laplace(field, mode='wrap') / (self.dx ** 2)
    
    def step(self):
        """Advance one time step."""
        if self.f is None or self.g is None:
            raise ValueError("Reaction functions f and g must be set")
        
        # Compute Laplacians
        lap_u = self.laplacian(self.u)
        lap_v = self.laplacian(self.v)
        
        # Compute reactions
        fu = self.f(self.u, self.v)
        gv = self.g(self.u, self.v)
        
        # Update
        self.u += self.dt * (self.D_u * lap_u + fu)
        self.v += self.dt * (self.D_v * lap_v + gv)
    
    def run(self, n_steps: int, record_interval: int = 100) -> List[Tuple[NDArray, NDArray]]:
        """Run simulation and record snapshots."""
        snapshots = [(self.u.copy(), self.v.copy())]
        for i in range(n_steps):
            self.step()
            if (i + 1) % record_interval == 0:
                snapshots.append((self.u.copy(), self.v.copy()))
        return snapshots
    
    @property
    def diffusion_ratio(self) -> float:
        """D_v / D_u - determines pattern scale."""
        return self.D_v / self.D_u


# ═══════════════════════════════════════════════════════════════════════════════
# TURING PATTERNS - CLASSICAL SYSTEMS
# ═══════════════════════════════════════════════════════════════════════════════

class TuringPatternType(Enum):
    """Types of Turing patterns."""
    SPOTS = "spots"
    STRIPES = "stripes"
    LABYRINTH = "labyrinth"
    MIXED = "mixed"


@dataclass
class GiererMeinhardtSystem(ReactionDiffusionSystem):
    """
    Gierer-Meinhardt activator-inhibitor system.
    
    f(u,v) = ρ_u(u²/v - μ_u u) + σ_u
    g(u,v) = ρ_v(u² - μ_v v)
    
    Classic Turing pattern generator.
    """
    rho_u: float = 0.1
    rho_v: float = 0.1
    mu_u: float = 0.1
    mu_v: float = 0.1
    sigma_u: float = 0.01
    
    def __post_init__(self):
        super().__post_init__()
        
        def f(u, v):
            return self.rho_u * (u**2 / (v + 0.001) - self.mu_u * u) + self.sigma_u
        
        def g(u, v):
            return self.rho_v * (u**2 - self.mu_v * v)
        
        self.f = f
        self.g = g
    
    def initialize_random(self, amplitude: float = 0.1):
        """Initialize with small random perturbations."""
        nx, ny = self.grid_size
        self.u = 1.0 + amplitude * (np.random.rand(nx, ny) - 0.5)
        self.v = 1.0 + amplitude * (np.random.rand(nx, ny) - 0.5)


@dataclass
class GrayScottSystem(ReactionDiffusionSystem):
    """
    Gray-Scott reaction-diffusion system.
    
    f(u,v) = -u·v² + F(1-u)
    g(u,v) = u·v² - (F+k)v
    
    Parameters F (feed rate) and k (kill rate) control pattern type.
    """
    F: float = 0.04   # Feed rate
    k: float = 0.06   # Kill rate
    
    def __post_init__(self):
        super().__post_init__()
        
        def f(u, v):
            return -u * v**2 + self.F * (1 - u)
        
        def g(u, v):
            return u * v**2 - (self.F + self.k) * v
        
        self.f = f
        self.g = g
    
    def initialize_with_seed(self, seed_size: int = 10):
        """Initialize with central seed region."""
        nx, ny = self.grid_size
        self.u = np.ones((nx, ny))
        self.v = np.zeros((nx, ny))
        
        # Add seed in center
        cx, cy = nx // 2, ny // 2
        r = seed_size // 2
        self.u[cx-r:cx+r, cy-r:cy+r] = 0.5
        self.v[cx-r:cx+r, cy-r:cy+r] = 0.25
    
    @classmethod
    def spots_parameters(cls, **kwargs) -> 'GrayScottSystem':
        """Parameters for spot patterns."""
        return cls(F=0.035, k=0.065, **kwargs)
    
    @classmethod
    def stripes_parameters(cls, **kwargs) -> 'GrayScottSystem':
        """Parameters for stripe patterns."""
        return cls(F=0.04, k=0.06, **kwargs)
    
    @classmethod
    def mitosis_parameters(cls, **kwargs) -> 'GrayScottSystem':
        """Parameters for mitosis-like behavior."""
        return cls(F=0.0367, k=0.0649, **kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# MORPHOGEN GRADIENTS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MorphogenGradient:
    """
    Morphogen concentration gradient with source and decay.
    
    ∂c/∂t = D∇²c - λc + S(x)
    
    where:
        D: diffusion coefficient
        λ: decay rate
        S(x): source term (localized production)
    
    Steady state: exponential decay from source.
    """
    D: float = 1.0        # Diffusion coefficient
    decay: float = 0.1    # Decay rate λ
    grid_size: int = 100
    dx: float = 1.0
    
    concentration: NDArray[np.float64] = None
    source_positions: List[int] = field(default_factory=list)
    source_strength: float = 1.0
    
    def __post_init__(self):
        if self.concentration is None:
            self.concentration = np.zeros(self.grid_size)
    
    def set_source(self, position: int, strength: float = None):
        """Set morphogen source at position."""
        self.source_positions.append(position)
        if strength is not None:
            self.source_strength = strength
    
    def source_term(self) -> NDArray[np.float64]:
        """Compute source term S(x)."""
        S = np.zeros(self.grid_size)
        for pos in self.source_positions:
            if 0 <= pos < self.grid_size:
                S[pos] = self.source_strength
        return S
    
    def laplacian_1d(self) -> NDArray[np.float64]:
        """1D Laplacian with Neumann boundaries."""
        c = self.concentration
        lap = np.zeros_like(c)
        lap[1:-1] = (c[2:] - 2*c[1:-1] + c[:-2]) / self.dx**2
        lap[0] = (c[1] - c[0]) / self.dx**2
        lap[-1] = (c[-2] - c[-1]) / self.dx**2
        return lap
    
    def steady_state(self) -> NDArray[np.float64]:
        """
        Compute analytical steady state.
        For single source at x=0: c(x) = A·exp(-x/ξ)
        where ξ = √(D/λ) is the decay length.
        """
        decay_length = np.sqrt(self.D / self.decay)
        x = np.arange(self.grid_size) * self.dx
        
        if len(self.source_positions) == 1:
            x0 = self.source_positions[0] * self.dx
            A = self.source_strength / (2 * np.sqrt(self.D * self.decay))
            return A * np.exp(-np.abs(x - x0) / decay_length)
        else:
            # Superposition for multiple sources
            result = np.zeros(self.grid_size)
            for pos in self.source_positions:
                x0 = pos * self.dx
                A = self.source_strength / (2 * np.sqrt(self.D * self.decay))
                result += A * np.exp(-np.abs(x - x0) / decay_length)
            return result
    
    @property
    def decay_length(self) -> float:
        """Characteristic decay length ξ = √(D/λ)."""
        return np.sqrt(self.D / self.decay)
    
    def threshold_position(self, threshold: float) -> Optional[float]:
        """
        Find position where concentration crosses threshold.
        Used for determining cell fate boundaries.
        """
        ss = self.steady_state()
        for i in range(len(ss) - 1):
            if (ss[i] >= threshold and ss[i+1] < threshold) or \
               (ss[i] <= threshold and ss[i+1] > threshold):
                # Linear interpolation
                t = (threshold - ss[i]) / (ss[i+1] - ss[i])
                return (i + t) * self.dx
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# NEURAL SIGNALING - DISCRETE-CONTINUOUS COUPLING
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class NeuralPulse:
    """
    Single neural pulse / action potential.
    
    Modeled as discrete event with continuous refractory dynamics.
    """
    time: float
    amplitude: float = 1.0
    duration: float = 0.001  # 1ms typical
    
    def waveform(self, t: NDArray[np.float64]) -> NDArray[np.float64]:
        """Action potential waveform."""
        # Simplified triangular pulse
        dt = t - self.time
        result = np.zeros_like(t)
        mask = (dt >= 0) & (dt < self.duration)
        # Rising phase
        rise_mask = mask & (dt < self.duration / 2)
        result[rise_mask] = 2 * self.amplitude * dt[rise_mask] / self.duration
        # Falling phase
        fall_mask = mask & (dt >= self.duration / 2)
        result[fall_mask] = 2 * self.amplitude * (1 - dt[fall_mask] / self.duration)
        return result


@dataclass
class IntegrateAndFireNeuron:
    """
    Leaky integrate-and-fire neuron model.
    
    τ dV/dt = -(V - V_rest) + R·I(t)
    
    Fire when V > V_threshold, then reset to V_reset.
    """
    tau: float = 0.02      # Membrane time constant (20ms)
    V_rest: float = -70.0  # Resting potential (mV)
    V_threshold: float = -55.0  # Firing threshold
    V_reset: float = -75.0     # Reset potential
    R: float = 10.0        # Membrane resistance
    
    V: float = -70.0       # Current membrane potential
    refractory_time: float = 0.002  # Refractory period
    last_spike: float = -np.inf
    spike_times: List[float] = field(default_factory=list)
    
    def step(self, current: float, dt: float, t: float) -> bool:
        """
        Integrate for one time step.
        Returns True if spike occurred.
        """
        # Check refractory period
        if t - self.last_spike < self.refractory_time:
            self.V = self.V_reset
            return False
        
        # Integrate
        dV = (-(self.V - self.V_rest) + self.R * current) / self.tau
        self.V += dV * dt
        
        # Check threshold
        if self.V >= self.V_threshold:
            self.V = self.V_reset
            self.last_spike = t
            self.spike_times.append(t)
            return True
        
        return False
    
    def simulate(self, current_func: Callable[[float], float], 
                duration: float, dt: float = 0.0001) -> Tuple[NDArray, NDArray, List[float]]:
        """
        Simulate neuron with given input current.
        
        Returns:
            (time_array, voltage_array, spike_times)
        """
        n_steps = int(duration / dt)
        times = np.linspace(0, duration, n_steps)
        voltages = np.zeros(n_steps)
        
        self.V = self.V_rest
        self.spike_times = []
        
        for i, t in enumerate(times):
            I = current_func(t)
            self.step(I, dt, t)
            voltages[i] = self.V
        
        return times, voltages, self.spike_times
    
    @property
    def firing_rate(self) -> float:
        """Compute firing rate from spike times."""
        if len(self.spike_times) < 2:
            return 0.0
        duration = self.spike_times[-1] - self.spike_times[0]
        if duration <= 0:
            return 0.0
        return (len(self.spike_times) - 1) / duration


# ═══════════════════════════════════════════════════════════════════════════════
# DEFECT HYPERPLANES - STRESS LOCI
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DefectHyperplane:
    """
    Defect hyperplane in multi-scale biological system.
    
    Defects are stress loci where local constraints are maximally violated:
        - Metabolic thresholds
        - Developmental boundaries
        - Phase transition fronts
        - Normoxia/hypoxia interfaces
    
    In lattice model: carry hyperplane H_{d,t} where digit d at level t = 3.
    """
    dimension: int      # d - which axis
    level: int          # t - which scale level
    position: float     # Location in that dimension
    width: float = 1.0  # Transition width
    
    def indicator(self, x: NDArray[np.float64], axis: int) -> NDArray[np.float64]:
        """
        Smooth indicator function for defect zone.
        Returns 1 in defect zone, 0 outside.
        """
        if axis != self.dimension:
            return np.ones_like(x)
        
        # Smooth step function
        z = (x - self.position) / self.width
        return 1 / (1 + np.exp(-z * 4)) * (1 - 1 / (1 + np.exp((z - 1) * 4)))
    
    def stress_field(self, x: NDArray[np.float64]) -> NDArray[np.float64]:
        """
        Stress field: high near defect, low away.
        """
        distance = np.abs(x - self.position)
        return np.exp(-distance / self.width)


@dataclass
class DefectNetwork:
    """
    Network of defect hyperplanes at multiple scales.
    
    Defects organize into hierarchical patterns:
        - Fine-scale defects nested in coarse-scale ones
        - Percolation transition when defect density exceeds threshold
    """
    hyperplanes: List[DefectHyperplane] = field(default_factory=list)
    
    def add_defect(self, dimension: int, level: int, position: float, width: float = 1.0):
        """Add defect hyperplane."""
        self.hyperplanes.append(DefectHyperplane(dimension, level, position, width))
    
    def total_stress(self, x: NDArray[np.float64]) -> NDArray[np.float64]:
        """Combined stress from all defects."""
        stress = np.zeros_like(x)
        for hp in self.hyperplanes:
            stress += hp.stress_field(x)
        return stress
    
    def defect_density(self, x_range: Tuple[float, float], 
                      n_samples: int = 1000) -> float:
        """Compute defect density in region."""
        x = np.linspace(x_range[0], x_range[1], n_samples)
        stress = self.total_stress(x)
        # Count points above threshold
        threshold = 0.5
        return np.mean(stress > threshold)
    
    def by_level(self, level: int) -> List[DefectHyperplane]:
        """Get defects at specific scale level."""
        return [hp for hp in self.hyperplanes if hp.level == level]


# ═══════════════════════════════════════════════════════════════════════════════
# MULTI-SCALE HOMEOSTASIS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MultiScaleHomeostasis:
    """
    Hierarchical homeostatic control across biological scales.
    
    Same tetradic kernel governs:
        Level 0 (point): Single 4-state controller
        Level 1 (line): Signaling cascades with kernel transitions
        Level 2 (surface): Tissue sheets with 4×4 governance patches
        Level 3 (volume): Organs/ecosystems via radix-4 projector
    
    Each level inherits structure from level below via Kronecker lift.
    """
    n_levels: int = 3
    controllers: Dict[Tuple, TetradicController] = field(default_factory=dict)
    
    def _key(self, level: int, index: Tuple[int, ...]) -> Tuple:
        """Create hierarchical key."""
        return (level,) + index
    
    def get_controller(self, level: int, index: Tuple[int, ...]) -> TetradicController:
        """Get or create controller at position."""
        key = self._key(level, index)
        if key not in self.controllers:
            self.controllers[key] = TetradicController()
        return self.controllers[key]
    
    def set_state(self, level: int, index: Tuple[int, ...], state: TetradicState):
        """Set state at position."""
        self.get_controller(level, index).current_state = state
    
    def get_state(self, level: int, index: Tuple[int, ...]) -> TetradicState:
        """Get state at position."""
        return self.get_controller(level, index).current_state
    
    def coarse_grain(self, level: int, index: Tuple[int, ...]) -> TetradicState:
        """
        Compute coarse-grained state from fine level.
        Uses majority vote among 4 children.
        """
        if level == 0:
            return self.get_state(0, index)
        
        # Get 4 children (2×2 block for 2D)
        child_states = []
        for di in range(2):
            for dj in range(2):
                child_index = (index[0]*2 + di, index[1]*2 + dj) if len(index) >= 2 else (index[0]*2 + di,)
                child_states.append(self.get_state(level-1, child_index))
        
        # Majority vote by bit
        bit0_sum = sum(s.bits[0] for s in child_states)
        bit1_sum = sum(s.bits[1] for s in child_states)
        
        majority_bit0 = 1 if bit0_sum >= 2 else 0
        majority_bit1 = 1 if bit1_sum >= 2 else 0
        
        return TetradicState((majority_bit0, majority_bit1))
    
    def propagate_signal(self, signal_0: float, signal_1: float, level: int = None):
        """
        Propagate homeostatic signal across all controllers at level.
        If level is None, propagate to all levels.
        """
        if level is not None:
            levels = [level]
        else:
            levels = range(self.n_levels)
        
        for lvl in levels:
            for key, ctrl in self.controllers.items():
                if key[0] == lvl:
                    ctrl.update(signal_0, signal_1)
    
    def state_distribution(self, level: int) -> Dict[TetradicState, int]:
        """Count states at given level."""
        dist = {s: 0 for s in TetradicState}
        for key, ctrl in self.controllers.items():
            if key[0] == level:
                dist[ctrl.current_state] += 1
        return dist


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_pattern(field: NDArray[np.float64]) -> Dict[str, Any]:
    """
    Analyze spatial pattern in concentration field.
    
    Returns:
        - Fourier spectrum
        - Dominant wavelength
        - Pattern type classification
        - Contrast ratio
    """
    # 2D FFT
    fft = np.fft.fft2(field)
    power = np.abs(fft) ** 2
    
    # Radial average
    ny, nx = field.shape
    y, x = np.ogrid[-ny//2:ny//2, -nx//2:nx//2]
    r = np.sqrt(x**2 + y**2)
    r_int = r.astype(int)
    
    radial_profile = np.bincount(r_int.ravel(), weights=np.fft.fftshift(power).ravel())
    radial_counts = np.bincount(r_int.ravel())
    radial_profile = radial_profile / (radial_counts + 1e-10)
    
    # Find dominant wavelength (skip DC component)
    if len(radial_profile) > 1:
        peak_k = np.argmax(radial_profile[1:]) + 1
        dominant_wavelength = max(nx, ny) / peak_k if peak_k > 0 else float('inf')
    else:
        dominant_wavelength = float('inf')
    
    # Pattern type classification
    contrast = (field.max() - field.min()) / (field.max() + field.min() + 1e-10)
    
    # Simple heuristic for pattern type
    if contrast < 0.1:
        pattern_type = TuringPatternType.MIXED
    elif dominant_wavelength < min(nx, ny) / 4:
        pattern_type = TuringPatternType.SPOTS
    elif dominant_wavelength > min(nx, ny) / 2:
        pattern_type = TuringPatternType.LABYRINTH
    else:
        pattern_type = TuringPatternType.STRIPES
    
    return {
        'dominant_wavelength': dominant_wavelength,
        'contrast': contrast,
        'pattern_type': pattern_type,
        'radial_profile': radial_profile,
        'mean': field.mean(),
        'std': field.std()
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_turing_system(pattern_type: str = 'stripes', 
                        grid_size: Tuple[int, int] = (64, 64)) -> GrayScottSystem:
    """Create Gray-Scott system with parameters for desired pattern."""
    if pattern_type == 'spots':
        return GrayScottSystem.spots_parameters(grid_size=grid_size)
    elif pattern_type == 'stripes':
        return GrayScottSystem.stripes_parameters(grid_size=grid_size)
    elif pattern_type == 'mitosis':
        return GrayScottSystem.mitosis_parameters(grid_size=grid_size)
    else:
        return GrayScottSystem(grid_size=grid_size)


def morphogen_gradient_1d(source_pos: int, 
                         D: float = 1.0, 
                         decay: float = 0.1,
                         grid_size: int = 100) -> MorphogenGradient:
    """Create 1D morphogen gradient with single source."""
    grad = MorphogenGradient(D=D, decay=decay, grid_size=grid_size)
    grad.set_source(source_pos)
    return grad


def simulate_neuron(current_amplitude: float = 2.0,
                   duration: float = 0.5,
                   frequency: float = 10.0) -> Dict[str, Any]:
    """Simulate IF neuron with sinusoidal input."""
    neuron = IntegrateAndFireNeuron()
    
    def current(t):
        return current_amplitude * (1 + 0.5 * np.sin(2 * np.pi * frequency * t))
    
    times, voltages, spikes = neuron.simulate(current, duration)
    
    return {
        'times': times,
        'voltages': voltages,
        'spike_times': spikes,
        'firing_rate': neuron.firing_rate
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Tetradic states
    'TetradicState',
    'TetradicController',
    'FIRE', 'AIR', 'EARTH', 'WATER',
    
    # Reaction-diffusion
    'ReactionDiffusionSystem',
    'GiererMeinhardtSystem',
    'GrayScottSystem',
    'TuringPatternType',
    
    # Morphogens
    'MorphogenGradient',
    
    # Neural
    'NeuralPulse',
    'IntegrateAndFireNeuron',
    
    # Defects
    'DefectHyperplane',
    'DefectNetwork',
    
    # Multi-scale
    'MultiScaleHomeostasis',
    
    # Analysis
    'analyze_pattern',
    
    # Functions
    'create_turing_system',
    'morphogen_gradient_1d',
    'simulate_neuron',
]
