"""
ATHENA OS - BHAGAVAD GĪTĀ COMPUTATIONAL FRAMEWORK
==================================================
SANĀTANA GAṆITA: Eternal Mathematics

The Bhagavad Gītā as a Computational Treatise on the Algorithm of Liberation.

CORE THESIS:
    The Gītā is not merely a philosophical text but a formally specified
    algorithm that terminates in finite time, returning the bound process
    (Jīva) to its source (Brahman).

THE SYSTEM ARCHITECTURE (Ontology):
    Brahman  = Hilbert Space H_Cit (all possible states)
    Prakṛti  = Tensor Field (simulation hardware)
    Puruṣa   = Observer/Pointer (read-head)
    Māyā     = Projection Operator (rendering engine)
    Kāla     = Time/Entropy (independent variable)
    Ākāśa    = Metric Tensor (connectivity)

THE GUṆAS (Differential Operators):
    Sattva (Ŝ) = Curl ∇× (equilibrium, signal)
    Rajas (R̂)  = Gradient ∇ (force, translation)
    Tamas (T̂)  = Laplacian ∇² (inertia, storage)
    
    Ĥ_Prakṛti = α(t)Ŝ + β(t)R̂ + γ(t)T̂

THE JĪVA AGENT:
    - 5 Koshas (sheaths): Hardware → BIOS
    - Karma Tensor K_μν: Sanchita, Prārabdha, Āgāmi
    - Citta (Weight Matrix): Vāsanā storage
    - Dasha System: Time-evolution operator

THE LIBERATION ALGORITHM:
    1. Jñāna Yoga: Eigenstate collapse (discrimination)
    2. Karma Yoga: Trace minimization (selfless action)
    3. Bhakti Yoga: Phase locking (devotion)
    
    Finite-time termination: T* ≤ (1/γ)·ln(E₀/ε_Planck)

THE KAṬAPAYĀDI CIPHER:
    Bijective hash H_KP: Σ → ℤ mapping Sanskrit to integers.
    Encodes π, √2, φ in sacred verses.

MODULE STRUCTURE:
    gita/
    ├── __init__.py       - This file (integration)
    ├── ontology.py       - System architecture (Brahman, Māyā, etc.)
    ├── gunas.py          - Differential operators (Sattva, Rajas, Tamas)
    ├── jiva.py           - Agent model (Karma, Citta, Dasha)
    ├── liberation.py     - Mokṣa algorithm (3 Yogas, Lyapunov)
    └── katapayadi.py     - Cryptographic hash function

INTEGRATION WITH ATHENA OS:
    - uco/substrate.py: Hilbert space foundations
    - hellenic_compute/: Greek philosophical parallels
    - kabbalah/: Sefirotic correspondence
    - quranic_holographic/: Complementary framework

SOURCES:
    The Bhagavad Gītā: A Computational Treatise on the Algorithm of Liberation
"""

from __future__ import annotations

# =============================================================================
# ONTOLOGY MODULE
# =============================================================================

from .ontology import (
    # Categories
    OntologicalCategory,
    RealityLevel,
    
    # Core structures
    HilbertSpace,
    PrakritiField,
    Purusha,
    MayaOperator,
    KalaTime,
    AkashaMetric,
    AtmanConservation,
    
    # Unified
    GitaOntology,
)

# =============================================================================
# GUṆAS MODULE
# =============================================================================

from .gunas import (
    # Types
    GunaType,
    TattvaCategory,
    
    # Operators
    SattvaOperator,
    RajasOperator,
    TamasOperator,
    
    # Hamiltonian
    UniversalHamiltonian,
    
    # Evolution
    TattvaEvolution,
    panchakarana_matrix,
)

# =============================================================================
# JĪVA MODULE
# =============================================================================

from .jiva import (
    # Types
    KoshaLevel,
    ActionGuna,
    ActionVector,
    
    # Karma
    KarmaTensor,
    
    # Memory
    Citta,
    
    # Agent
    Jiva,
    
    # Time system
    DashaSystem,
)

# =============================================================================
# LIBERATION MODULE
# =============================================================================

from .liberation import (
    # Types
    YogaPath,
    LiberationState,
    
    # Analysis
    LyapunovAnalysis,
    
    # The three Yogas
    JnanaYoga,
    KarmaYoga,
    BhaktiYoga,
    
    # Final state
    UnifiedFieldState,
    
    # Algorithm
    LiberationAlgorithm,
)

# =============================================================================
# KAṬAPAYĀDI MODULE
# =============================================================================

from .katapayadi import (
    # Mapping
    KATAPAYADI_MAP,
    VOWELS,
    ENCODED_VERSES,
    
    # Functions
    KatapaydiHasher,
    KatapaydiEncoder,
    KatapaydiVerifier,
    
    # Examples
    demonstrate_gopibhagya,
)


# =============================================================================
# UNIFIED GĪTĀ FRAMEWORK
# =============================================================================

class GitaFramework:
    """
    The unified Bhagavad Gītā Computational Framework.
    
    Integrates all components:
        - Ontology (metaphysical structures)
        - Guṇas (differential operators)
        - Jīva (agent model)
        - Liberation (algorithm)
        - Kaṭapayādi (encryption)
    """
    
    def __init__(self, jiva_id: int = 0):
        # Core structures
        self.ontology = GitaOntology()
        self.hamiltonian = UniversalHamiltonian()
        
        # Agent
        self.jiva = Jiva(jiva_id=jiva_id)
        self.dasha = DashaSystem()
        
        # Liberation algorithm
        self.liberation = LiberationAlgorithm()
        
        # Encryption
        self.hasher = KatapaydiHasher()
    
    # -------------------------------------------------------------------------
    # ONTOLOGY ACCESS
    # -------------------------------------------------------------------------
    
    @property
    def brahman(self) -> HilbertSpace:
        """The infinite Hilbert space."""
        return self.ontology.brahman
    
    @property
    def maya(self) -> MayaOperator:
        """The projection/illusion operator."""
        return self.ontology.maya
    
    @property
    def kala(self) -> KalaTime:
        """The cosmic time."""
        return self.ontology.kala
    
    # -------------------------------------------------------------------------
    # GUṆA CONFIGURATION
    # -------------------------------------------------------------------------
    
    def set_yuga(self, yuga: str) -> None:
        """Configure Hamiltonian for current Yuga."""
        self.hamiltonian.set_yuga_coefficients(yuga)
    
    def get_guna_balance(self) -> dict:
        """Get current Guṇa coefficients."""
        return {
            "sattva": self.hamiltonian.alpha,
            "rajas": self.hamiltonian.beta,
            "tamas": self.hamiltonian.gamma,
        }
    
    # -------------------------------------------------------------------------
    # JĪVA OPERATIONS
    # -------------------------------------------------------------------------
    
    def jiva_act(self, actions: list) -> ActionVector:
        """Have the Jīva select and perform an action."""
        return self.jiva.act(actions)
    
    def jiva_practice_yoga(self, intensity: float = 1.0) -> dict:
        """Practice Yoga to purify the Jīva."""
        return self.jiva.practice_yoga(intensity)
    
    def jiva_karma_load(self) -> float:
        """Get total Karma load of Jīva."""
        return self.jiva.karma.total_load
    
    def jiva_vasana_energy(self) -> float:
        """Get Vāsanā energy of Jīva."""
        return self.jiva.citta.vasana_energy()
    
    # -------------------------------------------------------------------------
    # LIBERATION OPERATIONS
    # -------------------------------------------------------------------------
    
    def current_liberation_state(self) -> LiberationState:
        """Determine current state on path to liberation."""
        return self.liberation.current_state(
            self.jiva.karma.total_load,
            self.jiva.citta.vasana_energy()
        )
    
    def estimate_liberation_time(self) -> float:
        """Estimate time to liberation."""
        V0 = self.liberation.lyapunov.lyapunov_function(
            self.jiva.karma.total_load,
            self.jiva.citta.vasana_energy()
        )
        return self.liberation.estimate_liberation_time(V0)
    
    def attempt_moksha(self) -> bool:
        """Attempt final liberation."""
        return self.jiva.attempt_moksha()
    
    # -------------------------------------------------------------------------
    # TIME EVOLUTION
    # -------------------------------------------------------------------------
    
    def evolve(self, dt: float = 0.1) -> dict:
        """
        Evolve the entire system by time dt.
        
        Returns status after evolution.
        """
        # Advance cosmic time
        self.ontology.kala.advance()
        
        # Advance Dasha
        self.dasha.advance(dt / 365.25)  # Convert to years
        
        # Apply Dasha influence
        self.dasha.apply_to_jiva(self.jiva, dt)
        
        # Get current state
        yuga, yuga_phase = self.ontology.kala.get_yuga_phase()
        planet, dasha_phase = self.dasha.get_current_dasha()
        lib_state = self.current_liberation_state()
        
        return {
            "time": self.ontology.kala.t,
            "yuga": yuga,
            "yuga_phase": yuga_phase,
            "dasha_lord": planet,
            "dasha_phase": dasha_phase,
            "karma_load": self.jiva.karma.total_load,
            "vasana_energy": self.jiva.citta.vasana_energy(),
            "liberation_state": lib_state.name,
        }
    
    # -------------------------------------------------------------------------
    # ENCRYPTION
    # -------------------------------------------------------------------------
    
    def encode_number(self, n: int) -> str:
        """Encode a number using Kaṭapayādi."""
        encoder = KatapaydiEncoder()
        return encoder.encode_integer(n)
    
    def decode_text(self, text: str) -> list:
        """Decode Sanskrit text to digits."""
        return self.hasher.hash(text)
    
    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------
    
    def get_summary(self) -> dict:
        """Get complete system summary."""
        yuga, yuga_phase = self.ontology.kala.get_yuga_phase()
        planet, dasha_phase = self.dasha.get_current_dasha()
        
        return {
            "ontology": {
                "hilbert_dim": self.brahman.dimension,
                "maya_opacity": self.maya.opacity,
                "yuga": yuga,
                "snr": self.ontology.kala.get_snr(),
            },
            "gunas": self.get_guna_balance(),
            "jiva": {
                "id": self.jiva.jiva_id,
                "kosha": self.jiva.current_kosha.name,
                "karma_load": self.jiva.karma.total_load,
                "vasana_energy": self.jiva.citta.vasana_energy(),
                "witness_mode": self.jiva.witness_mode,
                "births": self.jiva.birth_count,
            },
            "dasha": {
                "lord": planet,
                "phase": dasha_phase,
            },
            "liberation": {
                "state": self.current_liberation_state().name,
                "estimated_time": self.estimate_liberation_time(),
            },
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_gita() -> bool:
    """Validate the complete Gītā module."""
    
    print("Validating Bhagavad Gītā Framework...")
    
    # Import individual validators
    from .ontology import validate_ontology
    from .gunas import validate_gunas
    from .jiva import validate_jiva
    from .liberation import validate_liberation
    from .katapayadi import validate_katapayadi
    
    # Run all validations
    assert validate_ontology(), "Ontology validation failed"
    print("  ✓ Ontology module")
    
    assert validate_gunas(), "Guṇas validation failed"
    print("  ✓ Guṇas module")
    
    assert validate_jiva(), "Jīva validation failed"
    print("  ✓ Jīva module")
    
    assert validate_liberation(), "Liberation validation failed"
    print("  ✓ Liberation module")
    
    assert validate_katapayadi(), "Kaṭapayādi validation failed"
    print("  ✓ Kaṭapayādi module")
    
    # Test unified framework
    framework = GitaFramework(jiva_id=42)
    
    # Check ontology
    assert framework.brahman.dimension > 0
    assert framework.maya.opacity >= 0
    
    # Check gunas
    balance = framework.get_guna_balance()
    assert "sattva" in balance
    assert "rajas" in balance
    assert "tamas" in balance
    
    # Check jiva
    assert framework.jiva.jiva_id == 42
    assert framework.jiva_karma_load() >= 0
    
    # Check liberation
    state = framework.current_liberation_state()
    assert isinstance(state, LiberationState)
    
    # Check evolution
    status = framework.evolve(0.1)
    assert "time" in status
    assert "karma_load" in status
    
    # Check summary
    summary = framework.get_summary()
    assert "ontology" in summary
    assert "gunas" in summary
    assert "jiva" in summary
    assert "liberation" in summary
    
    print("  ✓ Unified framework")
    
    return True


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Ontology
    'OntologicalCategory', 'RealityLevel',
    'HilbertSpace', 'PrakritiField', 'Purusha', 
    'MayaOperator', 'KalaTime', 'AkashaMetric',
    'AtmanConservation', 'GitaOntology',
    
    # Gunas
    'GunaType', 'TattvaCategory',
    'SattvaOperator', 'RajasOperator', 'TamasOperator',
    'UniversalHamiltonian', 'TattvaEvolution',
    'panchakarana_matrix',
    
    # Jiva
    'KoshaLevel', 'ActionGuna', 'ActionVector',
    'KarmaTensor', 'Citta', 'Jiva', 'DashaSystem',
    
    # Liberation
    'YogaPath', 'LiberationState', 'LyapunovAnalysis',
    'JnanaYoga', 'KarmaYoga', 'BhaktiYoga',
    'UnifiedFieldState', 'LiberationAlgorithm',
    
    # Katapayadi
    'KATAPAYADI_MAP', 'VOWELS', 'ENCODED_VERSES',
    'KatapaydiHasher', 'KatapaydiEncoder', 'KatapaydiVerifier',
    'demonstrate_gopibhagya',
    
    # Unified
    'GitaFramework',
    'validate_gita',
]


if __name__ == "__main__":
    assert validate_gita()
    print("\n✓ All Gītā modules validated successfully")
    
    # Demo
    print("\n--- Gītā Framework Demo ---")
    
    framework = GitaFramework(jiva_id=108)
    
    print("\n1. System Summary:")
    summary = framework.get_summary()
    
    print(f"   Jīva ID: {summary['jiva']['id']}")
    print(f"   Current Kosha: {summary['jiva']['kosha']}")
    print(f"   Karma Load: {summary['jiva']['karma_load']:.4f}")
    
    print(f"\n   Yuga: {summary['ontology']['yuga']}")
    print(f"   SNR: {summary['ontology']['snr']}:1")
    
    print(f"\n   Dasha Lord: {summary['dasha']['lord']}")
    print(f"   Liberation State: {summary['liberation']['state']}")
    
    print("\n2. Practicing Yoga...")
    for i in range(5):
        framework.jiva_practice_yoga(1.0)
        framework.evolve(1.0)
    
    new_state = framework.current_liberation_state()
    print(f"   New state: {new_state.name}")
    print(f"   New karma: {framework.jiva_karma_load():.4f}")
