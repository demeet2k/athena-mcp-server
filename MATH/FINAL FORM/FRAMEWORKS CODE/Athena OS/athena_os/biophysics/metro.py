"""
ATHENA OS - Bio Metro Map (Hubs + Routes + Addressing)
======================================================
The 8 biological hubs and routing system.

The Bio Metro replaces EM hubs (H1-H8) with biology-native invariants.
Same metro idea, but hubs become biological "transfer stations."

BH1 Energy: ATP budget, redox, gradients, fuel (Fire supply line)
BH2 Replication: DNA/RNA copying, cell cycle (Water propagation)
BH3 Regulation: Signaling networks, hormones (Air control plane)
BH4 Boundary: Membranes, compartments, tissues (Earth surfaces)
BH5 Code: Genotype, transcription/translation (Earth ledger)
BH6 Error Control: Proofreading, repair, checkpoints (Earth clamp)
BH7 Selection: Fitness, competition, ecology (Earth filter)
BH8 Transport: Diffusion, circulation, gradients (Water plumbing)

Lines connect hubs for specific phenomena:
- L_Immune: BH6 → BH3 → BH2 (surveillance → response → proliferation)
- L_Metabolic: BH1 → BH3 → BH8 (energy → regulation → distribution)
- L_Development: BH3 → BH8 → BH4 (control → transport → boundaries)
- L_Cancer: BH2 → BH6 → BH7 (replication → failed clamps → selection)
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from .aether import BioPillar, BioState
from .clans import BioAddress, BioArchetype, ARCHETYPES, get_archetype


# =============================================================================
# BIO HUBS
# =============================================================================

class BioHub(IntEnum):
    """
    The 8 biological transfer hubs.
    
    These are biology's equivalent of the physics metro hubs.
    """
    BH1_ENERGY = 1      # Fire supply line
    BH2_REPLICATION = 2  # Water propagation
    BH3_REGULATION = 3   # Air control plane
    BH4_BOUNDARY = 4     # Earth surfaces
    BH5_CODE = 5         # Earth ledger
    BH6_ERROR = 6        # Earth clamp
    BH7_SELECTION = 7    # Earth filter
    BH8_TRANSPORT = 8    # Water plumbing
    
    @property
    def pillar(self) -> BioPillar:
        """Get dominant pillar for this hub."""
        pillars = {
            BioHub.BH1_ENERGY: BioPillar.FIRE,
            BioHub.BH2_REPLICATION: BioPillar.WATER,
            BioHub.BH3_REGULATION: BioPillar.AIR,
            BioHub.BH4_BOUNDARY: BioPillar.EARTH,
            BioHub.BH5_CODE: BioPillar.EARTH,
            BioHub.BH6_ERROR: BioPillar.EARTH,
            BioHub.BH7_SELECTION: BioPillar.EARTH,
            BioHub.BH8_TRANSPORT: BioPillar.WATER,
        }
        return pillars[self]
    
    @property
    def description(self) -> str:
        """Get hub description."""
        descriptions = {
            BioHub.BH1_ENERGY: "ATP budget, redox, gradients, fuel",
            BioHub.BH2_REPLICATION: "DNA/RNA copying, cell cycle, reproduction",
            BioHub.BH3_REGULATION: "Signaling networks, gene regulation, hormones",
            BioHub.BH4_BOUNDARY: "Membranes, compartments, tissue interfaces",
            BioHub.BH5_CODE: "Genotype, transcription/translation, epigenetics",
            BioHub.BH6_ERROR: "Proofreading, repair, checkpoints, apoptosis",
            BioHub.BH7_SELECTION: "Fitness, competition, ecology, bottlenecks",
            BioHub.BH8_TRANSPORT: "Diffusion, circulation, cytoskeleton",
        }
        return descriptions[self]


# =============================================================================
# BIO METRO LINES
# =============================================================================

@dataclass
class BioMetroLine:
    """
    A metro line connecting biological hubs.
    
    Each line serves specific biological phenomena.
    """
    name: str
    hubs: List[BioHub]
    description: str
    phenomena: List[str]  # What phenomena use this line
    
    def __str__(self) -> str:
        hub_str = " → ".join(h.name.split('_')[0] for h in self.hubs)
        return f"{self.name}: {hub_str}"
    
    def contains_hub(self, hub: BioHub) -> bool:
        return hub in self.hubs


# Standard metro lines
LINE_IMMUNE = BioMetroLine(
    name="L_Immune",
    hubs=[BioHub.BH6_ERROR, BioHub.BH3_REGULATION, BioHub.BH2_REPLICATION],
    description="Immune surveillance → response → proliferation",
    phenomena=["Immune memory", "Inflammation", "Antibody production"]
)

LINE_METABOLIC = BioMetroLine(
    name="L_Metabolic",
    hubs=[BioHub.BH1_ENERGY, BioHub.BH3_REGULATION, BioHub.BH8_TRANSPORT],
    description="Energy acquisition → regulation → distribution",
    phenomena=["Fatigue", "Obesity", "Diabetes", "Thermoregulation"]
)

LINE_DEVELOPMENT = BioMetroLine(
    name="L_Development",
    hubs=[BioHub.BH3_REGULATION, BioHub.BH8_TRANSPORT, BioHub.BH4_BOUNDARY],
    description="Developmental control → morphogen transport → boundaries",
    phenomena=["Embryogenesis", "Wound healing", "Regeneration"]
)

LINE_CANCER = BioMetroLine(
    name="L_Cancer",
    hubs=[BioHub.BH2_REPLICATION, BioHub.BH6_ERROR, BioHub.BH7_SELECTION],
    description="Replication runaway + failed clamps + selection",
    phenomena=["Tumor growth", "Metastasis", "Drug resistance"]
)

LINE_GENETIC = BioMetroLine(
    name="L_Genetic",
    hubs=[BioHub.BH5_CODE, BioHub.BH3_REGULATION, BioHub.BH2_REPLICATION],
    description="Genetic code → regulatory network → expression",
    phenomena=["Gene expression", "Mutations", "Epigenetics"]
)

LINE_STRUCTURAL = BioMetroLine(
    name="L_Structural",
    hubs=[BioHub.BH4_BOUNDARY, BioHub.BH5_CODE, BioHub.BH1_ENERGY],
    description="Structure ← code ← energy for construction",
    phenomena=["Cell wall synthesis", "Protein folding", "Cytoskeleton"]
)

LINE_EVOLUTIONARY = BioMetroLine(
    name="L_Evolutionary",
    hubs=[BioHub.BH2_REPLICATION, BioHub.BH5_CODE, BioHub.BH7_SELECTION],
    description="Replication + mutation + selection",
    phenomena=["Adaptation", "Speciation", "Natural selection"]
)

LINE_LIFE_CYCLE = BioMetroLine(
    name="L_LifeCycle",
    hubs=[BioHub.BH1_ENERGY, BioHub.BH3_REGULATION, BioHub.BH2_REPLICATION, 
          BioHub.BH6_ERROR, BioHub.BH7_SELECTION],
    description="The fundamental life loop",
    phenomena=["Life", "Death", "Reproduction", "Evolution"]
)

# All lines
METRO_LINES: List[BioMetroLine] = [
    LINE_IMMUNE, LINE_METABOLIC, LINE_DEVELOPMENT, LINE_CANCER,
    LINE_GENETIC, LINE_STRUCTURAL, LINE_EVOLUTIONARY, LINE_LIFE_CYCLE
]


# =============================================================================
# BIO METRO MAP
# =============================================================================

@dataclass
class BioMetroMap:
    """
    The complete biological metro map.
    
    Routes any biological phenomenon to:
    - Address T[i,j,k,ℓ]
    - Hub route [BH...]
    - Law line (governing equation)
    """
    
    # Hub adjacency (which hubs connect directly)
    adjacency: Dict[BioHub, List[BioHub]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Build adjacency from lines."""
        self._build_adjacency()
    
    def _build_adjacency(self) -> None:
        """Build hub adjacency graph from metro lines."""
        self.adjacency = {hub: [] for hub in BioHub}
        
        for line in METRO_LINES:
            for i in range(len(line.hubs) - 1):
                h1, h2 = line.hubs[i], line.hubs[i + 1]
                if h2 not in self.adjacency[h1]:
                    self.adjacency[h1].append(h2)
                if h1 not in self.adjacency[h2]:
                    self.adjacency[h2].append(h1)
    
    def find_route(self, start: BioHub, end: BioHub) -> List[BioHub]:
        """Find shortest route between hubs (BFS)."""
        if start == end:
            return [start]
        
        visited = {start}
        queue = [(start, [start])]
        
        while queue:
            current, path = queue.pop(0)
            
            for neighbor in self.adjacency[current]:
                if neighbor == end:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []  # No route found
    
    def get_lines_through_hub(self, hub: BioHub) -> List[BioMetroLine]:
        """Get all lines passing through a hub."""
        return [line for line in METRO_LINES if line.contains_hub(hub)]


# Global metro map instance
BIO_METRO = BioMetroMap()


# =============================================================================
# PHENOMENON ROUTER
# =============================================================================

@dataclass
class PhenomenonRoute:
    """
    A routed biological phenomenon.
    
    Contains:
    - Address (Parent, Flavor, Refinement)
    - Hub route
    - Law line (governing equation)
    - Shadow pole (inner code vs outer saturation)
    """
    phenomenon: str
    address: BioAddress
    hub_route: List[BioHub]
    law_line: str
    shadow_pole: str  # "inner" (code) or "outer" (saturation)
    
    def __str__(self) -> str:
        route_str = " → ".join(h.name.split('_')[0] for h in self.hub_route)
        return f"{self.phenomenon}: T[{self.address}] via {route_str}"


class BioRouter:
    """
    Routes biological phenomena to crystal addresses.
    
    Usage:
    1. Name the phenomenon
    2. Answer: What dominates? What shapes it?
    3. Get address + route + law
    """
    
    def __init__(self):
        self.metro = BIO_METRO
        self.known_routes: Dict[str, PhenomenonRoute] = {}
        self._init_known_routes()
    
    def _init_known_routes(self) -> None:
        """Initialize known phenomenon routes."""
        # Cancer
        self.known_routes["cancer"] = PhenomenonRoute(
            phenomenon="Cancer",
            address=BioAddress(BioPillar.WATER, BioPillar.EARTH, 
                              BioPillar.FIRE, BioPillar.EARTH),
            hub_route=[BioHub.BH2_REPLICATION, BioHub.BH6_ERROR, BioHub.BH7_SELECTION],
            law_line="dN/dt = rN (uncontrolled) + checkpoint_failure",
            shadow_pole="outer"  # Saturation horizon (error catastrophe)
        )
        
        # Immune memory
        self.known_routes["immune_memory"] = PhenomenonRoute(
            phenomenon="Immune Memory",
            address=BioAddress(BioPillar.AIR, BioPillar.EARTH, 
                              BioPillar.WATER, BioPillar.AIR),
            hub_route=[BioHub.BH3_REGULATION, BioHub.BH6_ERROR, BioHub.BH5_CODE],
            law_line="u = π_θ(·) with ledgered memory state",
            shadow_pole="inner"  # Code depth
        )
        
        # Embryogenesis
        self.known_routes["embryogenesis"] = PhenomenonRoute(
            phenomenon="Embryogenesis",
            address=BioAddress(BioPillar.WATER, BioPillar.AIR, 
                              BioPillar.WATER, BioPillar.EARTH),
            hub_route=[BioHub.BH3_REGULATION, BioHub.BH8_TRANSPORT, 
                      BioHub.BH4_BOUNDARY, BioHub.BH2_REPLICATION],
            law_line="∂c/∂t = D∇²c + R(c) + fate_lock",
            shadow_pole="inner"  # Code depth (developmental program)
        )
        
        # Aging
        self.known_routes["aging"] = PhenomenonRoute(
            phenomenon="Aging",
            address=BioAddress(BioPillar.EARTH, BioPillar.FIRE, 
                              BioPillar.EARTH, BioPillar.WATER),
            hub_route=[BioHub.BH6_ERROR, BioHub.BH1_ENERGY, BioHub.BH4_BOUNDARY],
            law_line="d[damage]/dt = production - repair",
            shadow_pole="outer"  # Saturation (repair ceiling)
        )
        
        # Photosynthesis
        self.known_routes["photosynthesis"] = PhenomenonRoute(
            phenomenon="Photosynthesis",
            address=BioAddress(BioPillar.FIRE, BioPillar.FIRE, 
                              BioPillar.WATER, BioPillar.EARTH),
            hub_route=[BioHub.BH1_ENERGY, BioHub.BH3_REGULATION],
            law_line="6CO2 + 6H2O + hν → C6H12O6 + 6O2",
            shadow_pole="inner"  # Code (chloroplast machinery)
        )
        
        # Neural plasticity
        self.known_routes["learning"] = PhenomenonRoute(
            phenomenon="Learning/Plasticity",
            address=BioAddress(BioPillar.AIR, BioPillar.WATER, 
                              BioPillar.AIR, BioPillar.EARTH),
            hub_route=[BioHub.BH3_REGULATION, BioHub.BH5_CODE],
            law_line="Δw ∝ pre·post (Hebbian)",
            shadow_pole="inner"  # Code (synaptic weights)
        )
        
        # Infection
        self.known_routes["infection"] = PhenomenonRoute(
            phenomenon="Infection",
            address=BioAddress(BioPillar.WATER, BioPillar.FIRE, 
                              BioPillar.AIR, BioPillar.FIRE),
            hub_route=[BioHub.BH2_REPLICATION, BioHub.BH6_ERROR, 
                      BioHub.BH3_REGULATION, BioHub.BH1_ENERGY],
            law_line="dP/dt = rP - immune_response(P)",
            shadow_pole="outer"  # Saturation (carrying capacity)
        )
    
    def route(self, phenomenon: str) -> Optional[PhenomenonRoute]:
        """Get route for known phenomenon."""
        key = phenomenon.lower().replace(" ", "_")
        return self.known_routes.get(key)
    
    def quick_route(self, dominant: BioPillar, influence: BioPillar,
                   primary_hub: BioHub) -> PhenomenonRoute:
        """
        Quick routing for new phenomena.
        
        Just specify dominant pillar, influence, and primary hub.
        """
        # Get archetype
        archetype = get_archetype(dominant, influence)
        
        # Build minimal hub route
        hub_route = [primary_hub]
        
        # Add connected hubs based on archetype
        if dominant == BioPillar.FIRE:
            hub_route.append(BioHub.BH1_ENERGY)
        elif dominant == BioPillar.WATER:
            hub_route.append(BioHub.BH2_REPLICATION)
        elif dominant == BioPillar.AIR:
            hub_route.append(BioHub.BH3_REGULATION)
        else:
            hub_route.append(BioHub.BH4_BOUNDARY)
        
        return PhenomenonRoute(
            phenomenon=f"Custom({dominant.name}[{influence.name}])",
            address=BioAddress(dominant, influence),
            hub_route=hub_route,
            law_line=archetype.law_template,
            shadow_pole="inner" if influence in (BioPillar.EARTH, BioPillar.AIR) else "outer"
        )
    
    def list_phenomena(self) -> List[str]:
        """List all known phenomena."""
        return list(self.known_routes.keys())


# Global router instance
BIO_ROUTER = BioRouter()


# =============================================================================
# VALIDATION
# =============================================================================

def validate_metro() -> bool:
    """Validate bio metro map."""
    
    # Test hubs
    assert len(BioHub) == 8
    assert BioHub.BH1_ENERGY.pillar == BioPillar.FIRE
    assert BioHub.BH3_REGULATION.pillar == BioPillar.AIR
    
    # Test lines
    assert len(METRO_LINES) >= 4
    assert LINE_CANCER.contains_hub(BioHub.BH2_REPLICATION)
    
    # Test metro map
    metro = BioMetroMap()
    route = metro.find_route(BioHub.BH1_ENERGY, BioHub.BH2_REPLICATION)
    assert len(route) > 0
    
    # Test router
    router = BioRouter()
    
    cancer_route = router.route("cancer")
    assert cancer_route is not None
    assert cancer_route.address.primary == BioPillar.WATER
    
    immune_route = router.route("immune_memory")
    assert immune_route is not None
    
    # Test quick route
    quick = router.quick_route(BioPillar.FIRE, BioPillar.WATER, BioHub.BH1_ENERGY)
    assert quick.address.primary == BioPillar.FIRE
    
    return True


if __name__ == "__main__":
    print("Validating Bio Metro Map...")
    assert validate_metro()
    print("✓ Bio Metro Map validated")
    
    # Demo
    print("\n=== Bio Metro Hubs ===")
    for hub in BioHub:
        print(f"  {hub.name}: {hub.description}")
    
    print("\n=== Metro Lines ===")
    for line in METRO_LINES[:4]:
        print(f"  {line}")
    
    print("\n=== Known Phenomenon Routes ===")
    router = BioRouter()
    for name in router.list_phenomena():
        route = router.route(name)
        print(f"\n{route.phenomenon}:")
        print(f"  Address: T[{route.address}]")
        hub_str = " → ".join(h.name.split('_')[0] for h in route.hub_route)
        print(f"  Route: {hub_str}")
        print(f"  Law: {route.law_line}")
        print(f"  Shadow: {route.shadow_pole}")
