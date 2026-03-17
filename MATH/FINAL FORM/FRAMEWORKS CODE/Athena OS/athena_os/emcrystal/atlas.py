"""
ATHENA OS - 256 Atlas Compression System
=========================================
The 256→64→16→4→Aether compression hierarchy.

ADDRESS STRUCTURE:
    T[i, j, k, ℓ] where each index ∈ {Fire, Water, Air, Earth}

HIERARCHY:
    4 pillars (primary element)
    16 archetypes (primary × influence = 4×4)
    64 families (primary × influence × flavor = 4×4×4)
    256 leaves (primary × influence × flavor × refinement = 4×4×4×4)

MARGINAL COMPUTATION:
    256 → 64: p_64(i,j,k) = Σ_ℓ p(i,j,k,ℓ)      (drop refinement)
    64 → 16:  p_16(i,j) = Σ_k p_64(i,j,k)        (drop flavor)
    16 → 4:   p_4(i) = Σ_j p_16(i,j)             (drop influence)

The 16 Archetypes (Parent[Influence]):
    Fire[Fire]   = Plasma / Pure Drive
    Fire[Water]  = Lightning / Guided Fire
    Fire[Air]    = Spark / Ignition Point
    Fire[Earth]  = Forge / Contained Fire
    Water[Fire]  = Steam / Excited Flow
    Water[Water] = Ocean / Pure Adaptation
    Water[Air]   = Mist / Diffuse Flow
    Water[Earth] = Ice / Crystallized Flow
    Air[Fire]    = Wind / Energized Structure
    Air[Water]   = Cloud / Flowing Structure
    Air[Air]     = Sky / Pure Relation
    Air[Earth]   = Crystal / Ordered Mind
    Earth[Fire]  = Volcano / Constrained Power
    Earth[Water] = Mud / Yielding Ground
    Earth[Air]   = Sand / Granular Structure
    Earth[Earth] = Mountain / Pure Constraint
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
import numpy as np
import math

from .aether import Face, Aether, ProjectorSet, GeneratorSet, Generator


# =============================================================================
# ELEMENT INDEX
# =============================================================================

class Element(Enum):
    """The four elements as indices."""
    FIRE = 0
    WATER = 1
    AIR = 2
    EARTH = 3
    
    @property
    def symbol(self) -> str:
        symbols = {
            Element.FIRE: "??",
            Element.WATER: "??",
            Element.AIR: "??",
            Element.EARTH: "??"
        }
        return symbols[self]
    
    @property
    def short(self) -> str:
        """Single letter abbreviation."""
        return self.name[0]
    
    @classmethod
    def from_int(cls, i: int) -> 'Element':
        """Get element from integer."""
        return list(cls)[i % 4]


# =============================================================================
# ATLAS ADDRESS
# =============================================================================

@dataclass(frozen=True)
class AtlasAddress:
    """
    A 4-tuple address T[i, j, k, ℓ] in the 256-atlas.
    
    - i: Primary element (parent)
    - j: Influence element
    - k: Flavor element
    - ℓ: Refinement element
    """
    
    primary: Element      # i
    influence: Element    # j
    flavor: Element       # k
    refinement: Element   # ℓ
    
    def as_tuple(self) -> Tuple[int, int, int, int]:
        """Return as integer tuple."""
        return (
            self.primary.value,
            self.influence.value,
            self.flavor.value,
            self.refinement.value
        )
    
    def to_int(self) -> int:
        """Convert to single integer 0-255."""
        i, j, k, l = self.as_tuple()
        return i * 64 + j * 16 + k * 4 + l
    
    @classmethod
    def from_int(cls, n: int) -> 'AtlasAddress':
        """Create from integer 0-255."""
        n = n % 256
        l = n % 4
        n //= 4
        k = n % 4
        n //= 4
        j = n % 4
        n //= 4
        i = n % 4
        return cls(
            primary=Element.from_int(i),
            influence=Element.from_int(j),
            flavor=Element.from_int(k),
            refinement=Element.from_int(l)
        )
    
    def parent_address(self) -> Tuple[Element, Element]:
        """Get 16-level address (i, j)."""
        return (self.primary, self.influence)
    
    def family_address(self) -> Tuple[Element, Element, Element]:
        """Get 64-level address (i, j, k)."""
        return (self.primary, self.influence, self.flavor)
    
    def short_string(self) -> str:
        """Short string like 'FWAE'."""
        return (
            self.primary.short +
            self.influence.short +
            self.flavor.short +
            self.refinement.short
        )
    
    def archetype_name(self) -> str:
        """Get the 16-archetype name."""
        names = {
            (Element.FIRE, Element.FIRE): "Plasma",
            (Element.FIRE, Element.WATER): "Lightning",
            (Element.FIRE, Element.AIR): "Spark",
            (Element.FIRE, Element.EARTH): "Forge",
            (Element.WATER, Element.FIRE): "Steam",
            (Element.WATER, Element.WATER): "Ocean",
            (Element.WATER, Element.AIR): "Mist",
            (Element.WATER, Element.EARTH): "Ice",
            (Element.AIR, Element.FIRE): "Wind",
            (Element.AIR, Element.WATER): "Cloud",
            (Element.AIR, Element.AIR): "Sky",
            (Element.AIR, Element.EARTH): "Crystal",
            (Element.EARTH, Element.FIRE): "Volcano",
            (Element.EARTH, Element.WATER): "Mud",
            (Element.EARTH, Element.AIR): "Sand",
            (Element.EARTH, Element.EARTH): "Mountain",
        }
        return names.get(self.parent_address(), "Unknown")


# =============================================================================
# ATLAS DISTRIBUTION
# =============================================================================

@dataclass
class AtlasDistribution:
    """
    A probability distribution over the 256-atlas.
    
    Can be a hard set or a weighted histogram.
    """
    
    # Weights for each address (256 values)
    weights: np.ndarray = field(default_factory=lambda: np.zeros(256))
    
    def __post_init__(self):
        """Ensure weights is numpy array."""
        if not isinstance(self.weights, np.ndarray):
            self.weights = np.array(self.weights)
        if len(self.weights) != 256:
            self.weights = np.zeros(256)
    
    def set_address(self, addr: AtlasAddress, weight: float = 1.0) -> None:
        """Set weight for an address."""
        self.weights[addr.to_int()] = weight
    
    def get_weight(self, addr: AtlasAddress) -> float:
        """Get weight for an address."""
        return self.weights[addr.to_int()]
    
    def normalize(self) -> None:
        """Normalize to sum to 1."""
        total = self.weights.sum()
        if total > 0:
            self.weights /= total
    
    def is_normalized(self) -> bool:
        """Check if normalized."""
        return abs(self.weights.sum() - 1.0) < 1e-10
    
    # =========================================================================
    # MARGINAL COMPUTATIONS
    # =========================================================================
    
    def marginal_64(self) -> np.ndarray:
        """
        Compute 64-marginal: p_64(i,j,k) = Σ_ℓ p(i,j,k,ℓ).
        
        Returns 64-element array indexed by 4i + j + 4k.
        Actually it's i*16 + j*4 + k (4³ = 64).
        """
        result = np.zeros(64)
        for n in range(256):
            addr = AtlasAddress.from_int(n)
            i, j, k, _ = addr.as_tuple()
            idx64 = i * 16 + j * 4 + k
            result[idx64] += self.weights[n]
        return result
    
    def marginal_16(self) -> np.ndarray:
        """
        Compute 16-marginal: p_16(i,j) = Σ_k p_64(i,j,k).
        
        Returns 16-element array indexed by 4i + j.
        """
        p64 = self.marginal_64()
        result = np.zeros(16)
        for idx64 in range(64):
            i = idx64 // 16
            j = (idx64 // 4) % 4
            idx16 = i * 4 + j
            result[idx16] += p64[idx64]
        return result
    
    def marginal_4(self) -> np.ndarray:
        """
        Compute 4-marginal: p_4(i) = Σ_j p_16(i,j).
        
        Returns 4-element array indexed by i.
        """
        p16 = self.marginal_16()
        result = np.zeros(4)
        for idx16 in range(16):
            i = idx16 // 4
            result[i] += p16[idx16]
        return result
    
    def primary_element(self, threshold: float = 0.5) -> Optional[Element]:
        """Get dominant primary element if above threshold."""
        p4 = self.marginal_4()
        max_idx = np.argmax(p4)
        if p4[max_idx] >= threshold:
            return Element.from_int(max_idx)
        return None
    
    def active_elements(self, threshold: float = 0.1) -> List[Element]:
        """Get elements with weight above threshold."""
        p4 = self.marginal_4()
        return [Element.from_int(i) for i in range(4) if p4[i] >= threshold]
    
    # =========================================================================
    # LENS MASK COMPUTATION
    # =========================================================================
    
    def compute_lens_mask(self, threshold: float = 0.1) -> int:
        """
        Compute 4-bit lens mask from distribution.
        
        lens(i) = 1 if p_4(i) >= threshold, else 0
        """
        p4 = self.marginal_4()
        mask = 0
        for i in range(4):
            if p4[i] >= threshold:
                mask |= (1 << i)
        return mask
    
    # =========================================================================
    # FACTORY METHODS
    # =========================================================================
    
    @classmethod
    def uniform(cls) -> 'AtlasDistribution':
        """Uniform distribution over all 256 addresses."""
        return cls(weights=np.ones(256) / 256)
    
    @classmethod
    def from_addresses(cls, addresses: List[AtlasAddress]) -> 'AtlasDistribution':
        """Create from list of addresses (uniform weight)."""
        dist = cls()
        for addr in addresses:
            dist.set_address(addr, 1.0)
        dist.normalize()
        return dist
    
    @classmethod
    def primary_only(cls, element: Element) -> 'AtlasDistribution':
        """Distribution concentrated on one primary element."""
        dist = cls()
        for n in range(256):
            addr = AtlasAddress.from_int(n)
            if addr.primary == element:
                dist.weights[n] = 1.0
        dist.normalize()
        return dist


# =============================================================================
# ATLAS ARCHETYPE CATALOG
# =============================================================================

@dataclass
class Archetype:
    """
    One of the 16 archetypes (Parent[Influence]).
    """
    
    primary: Element
    influence: Element
    name: str
    description: str
    default_hubs: List[str] = field(default_factory=list)
    
    def address_pattern(self) -> Tuple[Element, Element]:
        """Get (i, j) pattern."""
        return (self.primary, self.influence)
    
    def short_code(self) -> str:
        """Get 2-letter code like 'FW'."""
        return self.primary.short + self.influence.short


# Catalog of 16 archetypes
ARCHETYPE_CATALOG = [
    Archetype(Element.FIRE, Element.FIRE, "Plasma", 
              "Pure Drive - uncontained energy", ["H0", "H1"]),
    Archetype(Element.FIRE, Element.WATER, "Lightning",
              "Guided Fire - channeled impulse", ["H0", "H3"]),
    Archetype(Element.FIRE, Element.AIR, "Spark",
              "Ignition Point - activation trigger", ["H0", "H2"]),
    Archetype(Element.FIRE, Element.EARTH, "Forge",
              "Contained Fire - productive constraint", ["H0", "H8"]),
    
    Archetype(Element.WATER, Element.FIRE, "Steam",
              "Excited Flow - energized adaptation", ["H3", "H0"]),
    Archetype(Element.WATER, Element.WATER, "Ocean",
              "Pure Adaptation - deep flow", ["H3"]),
    Archetype(Element.WATER, Element.AIR, "Mist",
              "Diffuse Flow - dispersed presence", ["H3", "H2"]),
    Archetype(Element.WATER, Element.EARTH, "Ice",
              "Crystallized Flow - frozen state", ["H3", "H5"]),
    
    Archetype(Element.AIR, Element.FIRE, "Wind",
              "Energized Structure - dynamic pattern", ["H2", "H0"]),
    Archetype(Element.AIR, Element.WATER, "Cloud",
              "Flowing Structure - adaptive pattern", ["H2", "H3"]),
    Archetype(Element.AIR, Element.AIR, "Sky",
              "Pure Relation - abstract connection", ["H2"]),
    Archetype(Element.AIR, Element.EARTH, "Crystal",
              "Ordered Mind - precise structure", ["H2", "H5"]),
    
    Archetype(Element.EARTH, Element.FIRE, "Volcano",
              "Constrained Power - contained force", ["H5", "H0"]),
    Archetype(Element.EARTH, Element.WATER, "Mud",
              "Yielding Ground - adaptive constraint", ["H5", "H3"]),
    Archetype(Element.EARTH, Element.AIR, "Sand",
              "Granular Structure - discrete units", ["H5", "H2"]),
    Archetype(Element.EARTH, Element.EARTH, "Mountain",
              "Pure Constraint - absolute stability", ["H5"]),
]


def get_archetype(primary: Element, influence: Element) -> Optional[Archetype]:
    """Get archetype by elements."""
    for arch in ARCHETYPE_CATALOG:
        if arch.primary == primary and arch.influence == influence:
            return arch
    return None


# =============================================================================
# ATLAS COMPRESSION
# =============================================================================

@dataclass
class AtlasCompressor:
    """
    Compresses atlas distributions to Aether objects.
    
    Pipeline: 256 → 64 → 16 → 4 → Aether
    """
    
    threshold: float = 0.1  # Threshold for active elements
    
    def compress(self, dist: AtlasDistribution) -> Aether:
        """
        Compress distribution to Aether.
        
        Uses marginals to determine:
        - Lens mask (which faces are active)
        - Generator mask (which operators needed)
        - τ snapshot (from dominant Air content)
        """
        # Compute marginals
        p4 = dist.marginal_4()
        p16 = dist.marginal_16()
        
        # Compute lens mask
        lens_mask = dist.compute_lens_mask(self.threshold)
        projectors = ProjectorSet.from_lens_mask(lens_mask)
        
        # Set weights from marginals
        for i, elem in enumerate(Element):
            face = Face(i)
            projectors.get(face).weight = p4[i]
        
        # Compute generators based on which families are present
        generators = self._infer_generators(dist, p4)
        
        # Create Aether
        aether = Aether(
            projectors=projectors,
            generators=generators
        )
        
        return aether
    
    def _infer_generators(self, dist: AtlasDistribution, 
                         p4: np.ndarray) -> GeneratorSet:
        """Infer required generators from distribution."""
        gs = GeneratorSet(active={Generator.D, Generator.STAR})
        
        # If Water significant, add propagator
        if p4[Element.WATER.value] >= self.threshold:
            gs.add(Generator.BOX)
        
        # If Air significant, add duality gate
        if p4[Element.AIR.value] >= self.threshold:
            gs.add(Generator.M_TAU)
        
        # If Earth significant, add constraints
        if p4[Element.EARTH.value] >= self.threshold:
            gs.add(Generator.OMEGA)
            gs.add(Generator.BC)
        
        return gs
    
    def expand(self, aether: Aether) -> AtlasDistribution:
        """
        Expand Aether back to atlas distribution.
        
        Uses face weights to create distribution.
        """
        dist = AtlasDistribution()
        
        # Get face weights
        weights = {
            Element.FIRE: aether.projectors.fire.weight if aether.projectors.fire.active else 0,
            Element.WATER: aether.projectors.water.weight if aether.projectors.water.active else 0,
            Element.AIR: aether.projectors.air.weight if aether.projectors.air.active else 0,
            Element.EARTH: aether.projectors.earth.weight if aether.projectors.earth.active else 0,
        }
        
        # Distribute to addresses based on primary weight
        for n in range(256):
            addr = AtlasAddress.from_int(n)
            w = weights[addr.primary]
            if w > 0:
                # Spread evenly within primary
                dist.weights[n] = w / 64  # 64 addresses per primary
        
        return dist


# =============================================================================
# VALIDATION
# =============================================================================

def validate_atlas() -> bool:
    """Validate atlas module."""
    
    # Test AtlasAddress
    addr = AtlasAddress(
        primary=Element.FIRE,
        influence=Element.WATER,
        flavor=Element.AIR,
        refinement=Element.EARTH
    )
    assert addr.short_string() == "FWAE"
    assert addr.archetype_name() == "Lightning"
    
    n = addr.to_int()
    addr2 = AtlasAddress.from_int(n)
    assert addr == addr2
    
    # Test all 256 addresses round-trip
    for i in range(256):
        addr = AtlasAddress.from_int(i)
        assert addr.to_int() == i
    
    # Test AtlasDistribution
    dist = AtlasDistribution.uniform()
    assert dist.is_normalized()
    
    p4 = dist.marginal_4()
    assert len(p4) == 4
    assert abs(sum(p4) - 1.0) < 1e-10
    assert all(abs(p - 0.25) < 1e-10 for p in p4)  # Uniform
    
    p16 = dist.marginal_16()
    assert len(p16) == 16
    
    p64 = dist.marginal_64()
    assert len(p64) == 64
    
    # Test lens mask
    fire_dist = AtlasDistribution.primary_only(Element.FIRE)
    mask = fire_dist.compute_lens_mask(0.5)
    assert mask == 1  # Only Fire active
    
    # Test compression
    compressor = AtlasCompressor()
    aether = compressor.compress(dist)
    assert aether.projectors.lens_mask() == 15  # All active for uniform
    
    # Test archetype catalog
    assert len(ARCHETYPE_CATALOG) == 16
    arch = get_archetype(Element.FIRE, Element.WATER)
    assert arch is not None
    assert arch.name == "Lightning"
    
    return True


if __name__ == "__main__":
    print("Validating Atlas Module...")
    assert validate_atlas()
    print("✓ Atlas Module validated")
    
    # Demo
    print("\n=== 256-Atlas Demo ===")
    
    print("\nAtlas Address Example:")
    addr = AtlasAddress(
        primary=Element.FIRE,
        influence=Element.WATER,
        flavor=Element.AIR,
        refinement=Element.EARTH
    )
    print(f"  Address: {addr.short_string()}")
    print(f"  Integer: {addr.to_int()}")
    print(f"  Archetype: {addr.archetype_name()}")
    
    print("\n16 Archetypes:")
    for arch in ARCHETYPE_CATALOG:
        print(f"  {arch.short_code()} = {arch.name}: {arch.description}")
    
    print("\nUniform Distribution Marginals:")
    dist = AtlasDistribution.uniform()
    p4 = dist.marginal_4()
    for i, elem in enumerate(Element):
        print(f"  p({elem.name}) = {p4[i]:.4f}")
    
    print("\nFire-concentrated Distribution:")
    fire_dist = AtlasDistribution.primary_only(Element.FIRE)
    p4 = fire_dist.marginal_4()
    print(f"  Lens mask: {fire_dist.compute_lens_mask():04b}")
    print(f"  Active elements: {[e.name for e in fire_dist.active_elements()]}")
    
    print("\nCompression to Aether:")
    compressor = AtlasCompressor()
    aether = compressor.compress(dist)
    print(f"  {aether.superposition_form()}")
