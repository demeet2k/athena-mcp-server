"""
ATHENA OS - HELLENIC COMPUTATION FRAMEWORK
==========================================

A complete computational architecture based on Greek philosophy,
built on the algebraic primitive of the Klein-4 group acting
on a 2-bit state space.

CORE THESIS:
    The Greek philosophical corpus constitutes a complete distributed
    operating system. Every major system—physical, logical, biological,
    ethical—reduces to the same minimal algebraic structure:
    
    V = Z₂ × Z₂
    K₄ = {I, R, S, C}

MODULES:

    1. FOUNDATION (foundation.py)
       - The 2-bit state space V = Z₂ × Z₂
       - The Klein-4 group K₄
       - The 4×4 Diagonal Latin Kernel
       - Universal Tetrad Encoding
    
    2. PYTHAGORAS (pythagoras.py)
       - The Tetractys {1, 2, 3, 4}
       - Harmonic Ratios
       - Limiter/Unlimited Binary
       - Dimensional Engine
    
    3. EUCLID (euclid.py)
       - The 31-bit Register
       - Hamming (31,26) Error Correction
       - Parity Matrix & Syndrome Decoding
       - Euclidean Propositions
    
    4. PLATO (plato.py)
       - The Four-Variable Compiler
       - Forms and Instances
       - The Receptacle (Coordinate System)
       - Platonic Solids as Atomic Types
       - The Good (Optimization Function)
    
    5. ARISTOTLE (aristotle.py)
       - The Ten Categories (Type System)
       - The Syllogism (Compilation Algorithm)
       - The Four Causes (Causal Vector)
       - Actuality/Potentiality
       - Knowledge Graph
    
    6. NEOPLATONISM (neoplatonism.py)
       - The Virtualization Stack (One → Nous → Soul → Matter)
       - The Triadic Loop (Μονή → Πρόοδος → Ἐπιστροφή)
       - Henadic Lookup Table
       - Procession and Reversion
    
    7. STOICISM (stoicism.py)
       - The Dichotomy of Control
       - The Prohairesis (Kernel Space)
       - The Pneumatic Field
       - Virtues and Passions
       - The Tranquility Metric (ἀταραξία)
    
    8. HIPPOCRATES (hippocrates.py)
       - The Four Humors
       - The Homeostasis Algorithm
       - Treatment Protocol (Contraria contrariis)
       - The Three Spirits

MATHEMATICAL FRAMEWORK:

    State Space:  V = Z₂ × Z₂ = {(0,0), (0,1), (1,0), (1,1)}
    
    Symmetry:     K₄ = {I, R, S, C}
                  - I: identity
                  - R: flip second bit
                  - S: flip first bit
                  - C: flip both bits
    
    Encoding:     Elements     → (Hot/Cold) × (Wet/Dry)
                  Humors       → (Hot/Cold) × (Wet/Dry)
                  Causes       → (Temporal) × (Structural)
                  Control      → (Internal) × (Preferred)

INTEGRATION:
    All modules share the V = Z₂ × Z₂ foundation and interoperate
    through the common state space and Klein-4 transformations.

SOURCES:
    - THE_HELLENIC_COMPUTATION_FRAMEWORK.docx
"""

__version__ = "1.0.0"
__author__ = "ATHENA OS"

# =============================================================================
# FOUNDATION - Algebraic Primitives
# =============================================================================

from .foundation import (
    # State Space
    BitState,
    StateVector,
    STATE_SPACE,
    V_00, V_01, V_10, V_11,
    
    # Elements
    Element,
    
    # Klein-4 Group
    Klein4Op,
    Klein4Group,
    
    # Latin Kernel
    LatinKernel,
    
    # Tetrad Mappings
    TetradMapping,
    ELEMENT_TETRAD,
    HUMOR_TETRAD,
    CAUSE_TETRAD,
    CONTROL_TETRAD,
)

# =============================================================================
# PYTHAGORAS - Dimensional Engine
# =============================================================================

from .pythagoras import (
    # The Tetractys
    Tetractys,
    
    # Harmonics
    HarmonicInterval,
    HarmonicRatioSystem,
    
    # Limiter/Unlimited
    LimitType,
    LimiterUnlimited,
    
    # Engine
    DimensionalEngine,
    PythagoreanTuning,
)

# =============================================================================
# EUCLID - Error Correction
# =============================================================================

from .euclid import (
    # Hamming Code
    HammingParameters,
    ParityMatrix,
    GeneratorMatrix,
    HammingCode,
    EUCLID_PARAMS,
    
    # Euclidean System
    Proposition as EuclideanProposition,
    EuclideanRegister,
)

# =============================================================================
# PLATO - Type System
# =============================================================================

from .plato import (
    # Ontology
    OntologicalLevel,
    
    # Forms
    Form,
    Instance,
    
    # Space
    Receptacle,
    
    # Solids
    PlatonicSolid,
    
    # Demiurge
    Demiurge,
    TheGood,
    
    # Allegories
    DividedLine,
    Cave,
)

# =============================================================================
# ARISTOTLE - Logic Kernel
# =============================================================================

from .aristotle import (
    # Categories
    Category,
    Predicate,
    Substance,
    
    # Syllogism
    Quantifier,
    Proposition,
    Syllogism,
    SyllogisticEngine,
    VALID_SYLLOGISMS,
    SYLLOGISM_NAMES,
    
    # Causes
    CauseType,
    Cause,
    CausalVector,
    
    # Actuality/Potentiality
    ActualityState,
    PotentialActual,
    
    # Knowledge
    Demonstration,
    KnowledgeGraph,
)

# =============================================================================
# NEOPLATONISM - Hypervisor
# =============================================================================

from .neoplatonism import (
    # Hypostases
    Hypostasis,
    HypostasisLevel,
    
    # Triadic Loop
    TriadicPhase,
    TriadicLoop,
    
    # Henads
    Henad,
    HenadRegistry,
    
    # Procession
    ProcessionPath,
    Emanation,
    
    # Hypervisor
    NeoplatonicHypervisor,
)

# =============================================================================
# STOICISM - Control Kernel
# =============================================================================

from .stoicism import (
    # Control
    ControlDomain,
    Impression,
    
    # Prohairesis
    AssentState,
    Prohairesis,
    
    # Pneuma
    PneumaTension,
    PneumaField,
    
    # Ethics
    Passion,
    Eupathos,
    Virtue,
    
    # Kernel
    StoicKernel,
)

# =============================================================================
# HIPPOCRATES - Biological Driver
# =============================================================================

from .hippocrates import (
    # Humors
    Humor,
    Quality,
    QualityVector,
    HumoralState,
    
    # Diagnosis
    HealthState,
    Diagnosis,
    HomeostasisEngine,
    
    # Treatment
    Treatment,
    TREATMENTS,
    
    # Spirits
    Spirit,
    SpiritSystem,
    
    # Driver
    BiologicalDriver,
)


# =============================================================================
# INTEGRATED SYSTEM
# =============================================================================

class HellenicComputationFramework:
    """
    The complete Hellenic Computation Framework.
    
    Integrates all modules into a unified system.
    """
    
    def __init__(self):
        # Foundation
        self.state_space = STATE_SPACE
        self.klein4 = Klein4Group
        self.latin_kernel = LatinKernel()
        
        # Dimensional
        self.dimensional_engine = DimensionalEngine()
        
        # Error Correction
        self.hamming = HammingCode(r=5)
        
        # Type System
        self.demiurge = Demiurge()
        
        # Logic
        self.syllogistic = SyllogisticEngine()
        
        # Hypervisor
        self.hypervisor = NeoplatonicHypervisor()
        
        # Control
        self.stoic_kernel = StoicKernel()
        
        # Biological
        self.biological_driver = BiologicalDriver()
    
    def validate_all(self) -> bool:
        """Validate all modules."""
        from .foundation import validate_foundation
        from .pythagoras import validate_pythagoras
        from .euclid import validate_euclid
        from .plato import validate_plato
        from .aristotle import validate_aristotle
        from .neoplatonism import validate_neoplatonism
        from .stoicism import validate_stoicism
        from .hippocrates import validate_hippocrates
        
        validations = [
            ("Foundation", validate_foundation),
            ("Pythagoras", validate_pythagoras),
            ("Euclid", validate_euclid),
            ("Plato", validate_plato),
            ("Aristotle", validate_aristotle),
            ("Neoplatonism", validate_neoplatonism),
            ("Stoicism", validate_stoicism),
            ("Hippocrates", validate_hippocrates),
        ]
        
        all_valid = True
        for name, validator in validations:
            try:
                result = validator()
                if not result:
                    print(f"✗ {name} validation failed")
                    all_valid = False
            except Exception as e:
                print(f"✗ {name} validation error: {e}")
                all_valid = False
        
        return all_valid
    
    def state_to_all_domains(self, state: StateVector) -> dict:
        """Map a state to all domain interpretations."""
        return {
            "element": Element.from_state(state).value,
            "humor": Humor.from_state(state).value[0],
            "control": ControlDomain.from_state(state).value[0],
            "cause": CauseType.MATERIAL if state == V_00 else (
                CauseType.FORMAL if state == V_01 else (
                    CauseType.EFFICIENT if state == V_10 else
                    CauseType.FINAL
                )
            ).value[0],
            "virtue": (
                Virtue.WISDOM if state == V_00 else (
                    Virtue.COURAGE if state == V_01 else (
                        Virtue.JUSTICE if state == V_10 else
                        Virtue.TEMPERANCE
                    )
                )
            ).value[0],
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_hellenic_compute() -> bool:
    """Validate the complete hellenic_compute module."""
    
    framework = HellenicComputationFramework()
    return framework.validate_all()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Version
    "__version__",
    
    # Foundation
    "BitState", "StateVector", "STATE_SPACE",
    "V_00", "V_01", "V_10", "V_11",
    "Element",
    "Klein4Op", "Klein4Group",
    "LatinKernel",
    "TetradMapping", "ELEMENT_TETRAD", "HUMOR_TETRAD", 
    "CAUSE_TETRAD", "CONTROL_TETRAD",
    
    # Pythagoras
    "Tetractys", "HarmonicInterval", "HarmonicRatioSystem",
    "LimitType", "LimiterUnlimited",
    "DimensionalEngine", "PythagoreanTuning",
    
    # Euclid
    "HammingParameters", "ParityMatrix", "GeneratorMatrix",
    "HammingCode", "EUCLID_PARAMS",
    "EuclideanProposition", "EuclideanRegister",
    
    # Plato
    "OntologicalLevel", "Form", "Instance",
    "Receptacle", "PlatonicSolid",
    "Demiurge", "TheGood",
    "DividedLine", "Cave",
    
    # Aristotle
    "Category", "Predicate", "Substance",
    "Quantifier", "Proposition", "Syllogism",
    "SyllogisticEngine", "VALID_SYLLOGISMS", "SYLLOGISM_NAMES",
    "CauseType", "Cause", "CausalVector",
    "ActualityState", "PotentialActual",
    "Demonstration", "KnowledgeGraph",
    
    # Neoplatonism
    "Hypostasis", "HypostasisLevel",
    "TriadicPhase", "TriadicLoop",
    "Henad", "HenadRegistry",
    "ProcessionPath", "Emanation",
    "NeoplatonicHypervisor",
    
    # Stoicism
    "ControlDomain", "Impression",
    "AssentState", "Prohairesis",
    "PneumaTension", "PneumaField",
    "Passion", "Eupathos", "Virtue",
    "StoicKernel",
    
    # Hippocrates
    "Humor", "Quality", "QualityVector", "HumoralState",
    "HealthState", "Diagnosis", "HomeostasisEngine",
    "Treatment", "TREATMENTS",
    "Spirit", "SpiritSystem",
    "BiologicalDriver",
    
    # Integration
    "HellenicComputationFramework",
    "validate_hellenic_compute",
]
