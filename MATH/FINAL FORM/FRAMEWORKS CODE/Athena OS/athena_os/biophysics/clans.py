"""
ATHENA OS - Biological Clans (16 Parent Archetypes)
===================================================
The 4→16 expansion for biology.

Each pillar expands into four archetypes via Primary[Influence]:
- Fire Clan: Energy-dominant biology
- Water Clan: Replication-dominant biology
- Air Clan: Information-dominant biology
- Earth Clan: Constraint-dominant biology

These are NOT metaphors - they are the dominant operators.

Fire[Fire] = Autotrophic Metabolism (photosynthesis, chemosynthesis)
Fire[Water] = Catabolic Flux (respiration, fermentation)
Fire[Air] = Metabolic Regulation (hormones, enzyme feedback)
Fire[Earth] = Energy Storage (fat, starch, glycogen)

Water[Fire] = Growth Bursts (rapid division, blooms)
Water[Water] = Reproduction (mitosis, meiosis)
Water[Air] = Developmental Programs (embryogenesis, morphogens)
Water[Earth] = Heredity (DNA/RNA as persistent replicators)

Air[Fire] = Neural Activation (action potentials)
Air[Water] = Learning/Plasticity (synaptic change, epigenetics)
Air[Air] = Cognition/Control (decision-making, homeostasis)
Air[Earth] = Memory Encoding (DNA memory, neural memory, immune memory)

Earth[Fire] = Cellular Machinery (ribosomes, mitochondria)
Earth[Water] = Boundaries (membranes, tissues)
Earth[Air] = Genetic Code (codons, regulatory networks)
Earth[Earth] = Morphology (body plans, skeletons)
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from .aether import BioPillar, BioState


# =============================================================================
# BIOLOGICAL ARCHETYPE ADDRESS
# =============================================================================

@dataclass
class BioAddress:
    """
    A biological address in the 256-atlas.
    
    T[i,j,k,ℓ] where:
    - (i,j) = Primary[Influence] (16 parents)
    - k = Flavor (4)
    - ℓ = Refinement (4)
    
    Total: 4 × 4 × 4 × 4 = 256 addresses
    """
    primary: BioPillar
    influence: BioPillar
    flavor: Optional[BioPillar] = None
    refinement: Optional[BioPillar] = None
    
    @property
    def parent_index(self) -> int:
        """Get index in 16-parent space."""
        return self.primary.value * 4 + self.influence.value
    
    @property
    def full_index(self) -> int:
        """Get index in 256-space."""
        flavor = self.flavor.value if self.flavor else 0
        refinement = self.refinement.value if self.refinement else 0
        return (self.primary.value * 64 + 
                self.influence.value * 16 + 
                flavor * 4 + 
                refinement)
    
    def __str__(self) -> str:
        parts = [f"{self.primary.name}[{self.influence.name}]"]
        if self.flavor:
            parts.append(f"+{self.flavor.name}")
        if self.refinement:
            parts.append(f"+{self.refinement.name}")
        return "".join(parts)
    
    @classmethod
    def from_index(cls, index: int) -> 'BioAddress':
        """Create address from 256-index."""
        primary = BioPillar(index // 64)
        remainder = index % 64
        influence = BioPillar(remainder // 16)
        remainder = remainder % 16
        flavor = BioPillar(remainder // 4)
        refinement = BioPillar(remainder % 4)
        return cls(primary, influence, flavor, refinement)


# =============================================================================
# 16 PARENT ARCHETYPES
# =============================================================================

@dataclass
class BioArchetype:
    """
    A biological archetype (one of 16 parents).
    
    Contains the operator definition and biological meaning.
    """
    address: BioAddress
    name: str
    description: str
    examples: List[str]
    
    # Operator properties
    dominant_hub: str = ""  # Primary BH hub
    law_template: str = ""  # Governing equation template
    
    def apply(self, state: BioState) -> BioState:
        """Apply this archetype's operator to a state."""
        # Default: modify state based on primary pillar
        new_state = BioState(
            population=state.population,
            dominant_pillar=self.address.primary,
            replication_rate=state.replication_rate,
            energy_flux=state.energy_flux,
            information=state.information,
            has_boundary=state.has_boundary,
            ledger=state.ledger.copy()
        )
        new_state.append_ledger(f"ARCHETYPE:{self.name}")
        return new_state


# =============================================================================
# FIRE CLAN (Energy-dominant)
# =============================================================================

FIRE_FIRE = BioArchetype(
    address=BioAddress(BioPillar.FIRE, BioPillar.FIRE),
    name="Autotrophic Metabolism",
    description="Energy capture from environment",
    examples=["Photosynthesis", "Chemosynthesis", "Thermotrophy"],
    dominant_hub="BH1",
    law_template="Φ_in = hν·σ·I (light) or ΔG_redox (chemical)"
)

FIRE_WATER = BioArchetype(
    address=BioAddress(BioPillar.FIRE, BioPillar.WATER),
    name="Catabolic Flux",
    description="Energy extraction from substrates",
    examples=["Respiration", "Fermentation", "Beta-oxidation"],
    dominant_hub="BH1",
    law_template="C6H12O6 + 6O2 → 6CO2 + 6H2O + ATP"
)

FIRE_AIR = BioArchetype(
    address=BioAddress(BioPillar.FIRE, BioPillar.AIR),
    name="Metabolic Regulation",
    description="Control of energy pathways",
    examples=["Hormonal control", "Enzyme feedback", "Allosteric regulation"],
    dominant_hub="BH3",
    law_template="v = Vmax·[S]/(Km + [S]) with regulation"
)

FIRE_EARTH = BioArchetype(
    address=BioAddress(BioPillar.FIRE, BioPillar.EARTH),
    name="Energy Storage",
    description="Buffering and storage of energy",
    examples=["Fat deposition", "Starch synthesis", "Glycogen storage"],
    dominant_hub="BH1",
    law_template="d[storage]/dt = Φ_in - Φ_out - Φ_maint"
)


# =============================================================================
# WATER CLAN (Replication-dominant)
# =============================================================================

WATER_FIRE = BioArchetype(
    address=BioAddress(BioPillar.WATER, BioPillar.FIRE),
    name="Growth Bursts",
    description="Rapid cell division driven by resources",
    examples=["Algal blooms", "Tumor growth", "Exponential phase"],
    dominant_hub="BH2",
    law_template="dN/dt = rN (exponential growth)"
)

WATER_WATER = BioArchetype(
    address=BioAddress(BioPillar.WATER, BioPillar.WATER),
    name="Reproduction",
    description="Core replication machinery",
    examples=["Mitosis", "Meiosis", "Binary fission"],
    dominant_hub="BH2",
    law_template="R' = copy(R) + noise"
)

WATER_AIR = BioArchetype(
    address=BioAddress(BioPillar.WATER, BioPillar.AIR),
    name="Developmental Programs",
    description="Programmed replication patterns",
    examples=["Embryogenesis", "Morphogen gradients", "Cell fate decisions"],
    dominant_hub="BH3",
    law_template="∂c/∂t = D∇²c + R(c) (reaction-diffusion)"
)

WATER_EARTH = BioArchetype(
    address=BioAddress(BioPillar.WATER, BioPillar.EARTH),
    name="Heredity",
    description="Persistent information transmission",
    examples=["DNA replication", "RNA heredity", "Epigenetic inheritance"],
    dominant_hub="BH5",
    law_template="I(R_{t+1}; R_t) > 0 (information preservation)"
)


# =============================================================================
# AIR CLAN (Information-dominant)
# =============================================================================

AIR_FIRE = BioArchetype(
    address=BioAddress(BioPillar.AIR, BioPillar.FIRE),
    name="Neural Activation",
    description="Rapid information processing",
    examples=["Action potentials", "Excitation", "Neurotransmitter release"],
    dominant_hub="BH3",
    law_template="C(dV/dt) = I_ion + I_syn"
)

AIR_WATER = BioArchetype(
    address=BioAddress(BioPillar.AIR, BioPillar.WATER),
    name="Learning/Plasticity",
    description="Adaptive information modification",
    examples=["Synaptic plasticity", "Epigenetics", "Operant conditioning"],
    dominant_hub="BH3",
    law_template="Δw ∝ pre·post (Hebbian)"
)

AIR_AIR = BioArchetype(
    address=BioAddress(BioPillar.AIR, BioPillar.AIR),
    name="Cognition/Control",
    description="Pure information processing",
    examples=["Decision-making", "Homeostasis", "Inference"],
    dominant_hub="BH3",
    law_template="u = π_θ(sense(x)) (policy)"
)

AIR_EARTH = BioArchetype(
    address=BioAddress(BioPillar.AIR, BioPillar.EARTH),
    name="Memory Encoding",
    description="Stable information storage",
    examples=["DNA memory", "Neural memory", "Immune memory"],
    dominant_hub="BH5",
    law_template="store(pattern) → retrieve(pattern)"
)


# =============================================================================
# EARTH CLAN (Constraint-dominant)
# =============================================================================

EARTH_FIRE = BioArchetype(
    address=BioAddress(BioPillar.EARTH, BioPillar.FIRE),
    name="Cellular Machinery",
    description="Structure-function coupling",
    examples=["Ribosomes", "Mitochondria", "Chloroplasts"],
    dominant_hub="BH4",
    law_template="F = structure·function"
)

EARTH_WATER = BioArchetype(
    address=BioAddress(BioPillar.EARTH, BioPillar.WATER),
    name="Boundaries",
    description="Compartmentalization and flow",
    examples=["Cell membranes", "Tissues", "Organ boundaries"],
    dominant_hub="BH4",
    law_template="J = -D∇c + v·c (flux with barrier)"
)

EARTH_AIR = BioArchetype(
    address=BioAddress(BioPillar.EARTH, BioPillar.AIR),
    name="Genetic Code",
    description="Information-structure mapping",
    examples=["Codon table", "Regulatory networks", "Transcription factors"],
    dominant_hub="BH5",
    law_template="DNA → RNA → Protein"
)

EARTH_EARTH = BioArchetype(
    address=BioAddress(BioPillar.EARTH, BioPillar.EARTH),
    name="Morphology",
    description="Stable structural patterns",
    examples=["Body plans", "Skeletons", "Cell walls"],
    dominant_hub="BH4",
    law_template="form = ∫ constraints dt"
)


# =============================================================================
# ARCHETYPE CATALOG
# =============================================================================

# All 16 parent archetypes
ARCHETYPES: Dict[Tuple[BioPillar, BioPillar], BioArchetype] = {
    # Fire clan
    (BioPillar.FIRE, BioPillar.FIRE): FIRE_FIRE,
    (BioPillar.FIRE, BioPillar.WATER): FIRE_WATER,
    (BioPillar.FIRE, BioPillar.AIR): FIRE_AIR,
    (BioPillar.FIRE, BioPillar.EARTH): FIRE_EARTH,
    # Water clan
    (BioPillar.WATER, BioPillar.FIRE): WATER_FIRE,
    (BioPillar.WATER, BioPillar.WATER): WATER_WATER,
    (BioPillar.WATER, BioPillar.AIR): WATER_AIR,
    (BioPillar.WATER, BioPillar.EARTH): WATER_EARTH,
    # Air clan
    (BioPillar.AIR, BioPillar.FIRE): AIR_FIRE,
    (BioPillar.AIR, BioPillar.WATER): AIR_WATER,
    (BioPillar.AIR, BioPillar.AIR): AIR_AIR,
    (BioPillar.AIR, BioPillar.EARTH): AIR_EARTH,
    # Earth clan
    (BioPillar.EARTH, BioPillar.FIRE): EARTH_FIRE,
    (BioPillar.EARTH, BioPillar.WATER): EARTH_WATER,
    (BioPillar.EARTH, BioPillar.AIR): EARTH_AIR,
    (BioPillar.EARTH, BioPillar.EARTH): EARTH_EARTH,
}


def get_archetype(primary: BioPillar, influence: BioPillar) -> BioArchetype:
    """Get archetype by primary and influence."""
    return ARCHETYPES[(primary, influence)]


def get_archetype_by_index(index: int) -> BioArchetype:
    """Get archetype by 0-15 index."""
    primary = BioPillar(index // 4)
    influence = BioPillar(index % 4)
    return ARCHETYPES[(primary, influence)]


def get_clan(pillar: BioPillar) -> List[BioArchetype]:
    """Get all archetypes in a clan."""
    return [arch for (p, i), arch in ARCHETYPES.items() if p == pillar]


# =============================================================================
# 64 EXPANSION (Parent + Flavor)
# =============================================================================

def expand_to_64(archetype: BioArchetype, flavor: BioPillar) -> BioAddress:
    """
    Expand parent to 64-space by adding flavor.
    
    Flavor meanings:
    - Fire: add stress/drive/resource pulse
    - Water: add time evolution/lineage dynamics
    - Air: add regulatory rewiring/signaling mode
    - Earth: add constraint/repair/compartment lock
    """
    return BioAddress(
        primary=archetype.address.primary,
        influence=archetype.address.influence,
        flavor=flavor
    )


# =============================================================================
# 256 EXPANSION (Parent + Flavor + Refinement)
# =============================================================================

def expand_to_256(archetype: BioArchetype, flavor: BioPillar, 
                  refinement: BioPillar) -> BioAddress:
    """
    Expand parent to 256-space by adding flavor and refinement.
    
    Refinement meanings:
    - Fire: threshold event (oncogenic, immune trigger, starvation)
    - Water: dynamic regime (oscillation, wave, cascade, attractor)
    - Air: channel selection (pathway, receptor, gene circuit mode)
    - Earth: lock state (differentiation, speciation, dormancy, senescence)
    """
    return BioAddress(
        primary=archetype.address.primary,
        influence=archetype.address.influence,
        flavor=flavor,
        refinement=refinement
    )


# =============================================================================
# VALIDATION
# =============================================================================

def validate_clans() -> bool:
    """Validate biological clans."""
    
    # Test address
    addr = BioAddress(BioPillar.FIRE, BioPillar.WATER)
    assert addr.parent_index == 1  # Fire=0, Water=1 → 0*4+1=1
    
    addr_full = BioAddress(BioPillar.FIRE, BioPillar.WATER, 
                          BioPillar.AIR, BioPillar.EARTH)
    assert addr_full.full_index == 0*64 + 1*16 + 2*4 + 3  # 27
    
    # Test round-trip
    addr2 = BioAddress.from_index(27)
    assert addr2.primary == BioPillar.FIRE
    assert addr2.influence == BioPillar.WATER
    assert addr2.flavor == BioPillar.AIR
    assert addr2.refinement == BioPillar.EARTH
    
    # Test archetypes
    assert len(ARCHETYPES) == 16
    
    fire_clan = get_clan(BioPillar.FIRE)
    assert len(fire_clan) == 4
    
    # Test specific archetype
    ff = get_archetype(BioPillar.FIRE, BioPillar.FIRE)
    assert ff.name == "Autotrophic Metabolism"
    
    ww = get_archetype(BioPillar.WATER, BioPillar.WATER)
    assert ww.name == "Reproduction"
    
    # Test expansion
    addr64 = expand_to_64(ff, BioPillar.WATER)
    assert addr64.flavor == BioPillar.WATER
    
    addr256 = expand_to_256(ff, BioPillar.WATER, BioPillar.EARTH)
    assert addr256.refinement == BioPillar.EARTH
    
    return True


if __name__ == "__main__":
    print("Validating Biological Clans...")
    assert validate_clans()
    print("✓ Biological Clans validated")
    
    # Demo
    print("\n=== Biological Clans Demo ===")
    for pillar in BioPillar:
        print(f"\n{pillar.symbol} {pillar.name} CLAN:")
        clan = get_clan(pillar)
        for arch in clan:
            print(f"  {arch.address}: {arch.name}")
            print(f"    Examples: {', '.join(arch.examples[:2])}")
    
    print("\n=== 256 Expansion Example ===")
    ww = get_archetype(BioPillar.WATER, BioPillar.WATER)
    print(f"Parent: {ww.name} ({ww.address})")
    
    for flavor in BioPillar:
        for refinement in BioPillar:
            addr = expand_to_256(ww, flavor, refinement)
            print(f"  T[{addr}] index={addr.full_index}")
