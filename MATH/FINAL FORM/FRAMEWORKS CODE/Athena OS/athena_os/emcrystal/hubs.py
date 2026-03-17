"""
ATHENA OS - Hub Routing System
==============================
The 9 hubs (H0-H8) that route EM phenomena.

HUB DEFINITIONS:
    H0 = Curvature (F = dA, field strength)
    H1 = Sources (J_e, J_m - charges and currents)
    H2 = Gate (τ, M(τ), duality transformations)
    H3 = Propagation (□, Green functions, wave evolution)
    H4 = Boundary (BCs, interface conditions)
    H5 = Quantization (Dirac, SZ lattice)
    H6 = Holonomy (Wilson loops, Aharonov-Bohm)
    H7 = Topology (CS, characteristic classes)
    H8 = Medium (ε, μ, σ, constitutive relations)

PARENT ROUTING:
    Fire clan → H0, H1 primary
    Water clan → H3, H4 primary
    Air clan → H2, H5, H6 primary
    Earth clan → H4, H5, H7, H8 primary

TWO-STEP LOOKUP:
    1. Pick Parent by asking: which hub is unavoidable?
    2. Pick Flavor by asking: what is being turned on?
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set

from .atlas import Element, AtlasAddress, Archetype, ARCHETYPE_CATALOG


# =============================================================================
# HUB DEFINITIONS
# =============================================================================

class Hub(Enum):
    """The 9 routing hubs."""
    H0 = 0   # Curvature
    H1 = 1   # Sources
    H2 = 2   # Gate (τ, duality)
    H3 = 3   # Propagation
    H4 = 4   # Boundary
    H5 = 5   # Quantization
    H6 = 6   # Holonomy
    H7 = 7   # Topology
    H8 = 8   # Medium
    
    @property
    def name_full(self) -> str:
        """Full descriptive name."""
        names = {
            Hub.H0: "Curvature",
            Hub.H1: "Sources",
            Hub.H2: "Gate",
            Hub.H3: "Propagation",
            Hub.H4: "Boundary",
            Hub.H5: "Quantization",
            Hub.H6: "Holonomy",
            Hub.H7: "Topology",
            Hub.H8: "Medium",
        }
        return names[self]
    
    @property
    def description(self) -> str:
        """Detailed description."""
        descs = {
            Hub.H0: "F = dA, field strength curvature",
            Hub.H1: "J_e, J_m - electric and magnetic sources",
            Hub.H2: "τ, M(τ), SL(2,Z) duality transformations",
            Hub.H3: "□, G_ret - wave equation and propagators",
            Hub.H4: "Boundary conditions, interface matching",
            Hub.H5: "Dirac/SZ quantization, charge lattice",
            Hub.H6: "Wilson loops, Aharonov-Bohm phases",
            Hub.H7: "Chern-Simons, characteristic classes",
            Hub.H8: "ε, μ, σ - medium constitutive relations",
        }
        return descs[self]
    
    @property
    def primary_element(self) -> Element:
        """Which element primarily uses this hub."""
        mapping = {
            Hub.H0: Element.FIRE,    # Curvature → Fire (field creation)
            Hub.H1: Element.FIRE,    # Sources → Fire (charges)
            Hub.H2: Element.AIR,     # Gate → Air (duality)
            Hub.H3: Element.WATER,   # Propagation → Water (flow)
            Hub.H4: Element.EARTH,   # Boundary → Earth (constraint)
            Hub.H5: Element.EARTH,   # Quantization → Earth (lattice)
            Hub.H6: Element.AIR,     # Holonomy → Air (connection)
            Hub.H7: Element.EARTH,   # Topology → Earth (invariant)
            Hub.H8: Element.EARTH,   # Medium → Earth (material)
        }
        return mapping[self]


# =============================================================================
# HUB ROUTES
# =============================================================================

@dataclass
class HubRoute:
    """
    A route through the hub network.
    
    Specifies the primary hub and secondary hubs for a phenomenon.
    """
    
    primary: Hub
    secondary: List[Hub] = field(default_factory=list)
    
    def all_hubs(self) -> List[Hub]:
        """Get all hubs in route."""
        return [self.primary] + self.secondary
    
    def contains(self, hub: Hub) -> bool:
        """Check if route contains hub."""
        return hub in self.all_hubs()
    
    def as_string(self) -> str:
        """Format as string like 'H0 → H3 → H5'."""
        hubs = self.all_hubs()
        return " → ".join(h.name for h in hubs)


# Default routes for each clan (16 archetypes)
ARCHETYPE_ROUTES: Dict[Tuple[Element, Element], HubRoute] = {
    # Fire clan
    (Element.FIRE, Element.FIRE): HubRoute(Hub.H0, [Hub.H1]),
    (Element.FIRE, Element.WATER): HubRoute(Hub.H0, [Hub.H3]),
    (Element.FIRE, Element.AIR): HubRoute(Hub.H0, [Hub.H2]),
    (Element.FIRE, Element.EARTH): HubRoute(Hub.H0, [Hub.H8]),
    
    # Water clan
    (Element.WATER, Element.FIRE): HubRoute(Hub.H3, [Hub.H0]),
    (Element.WATER, Element.WATER): HubRoute(Hub.H3, []),
    (Element.WATER, Element.AIR): HubRoute(Hub.H3, [Hub.H2]),
    (Element.WATER, Element.EARTH): HubRoute(Hub.H3, [Hub.H5]),
    
    # Air clan
    (Element.AIR, Element.FIRE): HubRoute(Hub.H2, [Hub.H0]),
    (Element.AIR, Element.WATER): HubRoute(Hub.H2, [Hub.H3]),
    (Element.AIR, Element.AIR): HubRoute(Hub.H2, [Hub.H5]),
    (Element.AIR, Element.EARTH): HubRoute(Hub.H2, [Hub.H5, Hub.H4]),
    
    # Earth clan
    (Element.EARTH, Element.FIRE): HubRoute(Hub.H8, [Hub.H0]),
    (Element.EARTH, Element.WATER): HubRoute(Hub.H4, [Hub.H8]),
    (Element.EARTH, Element.AIR): HubRoute(Hub.H6, [Hub.H0]),
    (Element.EARTH, Element.EARTH): HubRoute(Hub.H5, [Hub.H6, Hub.H7]),
}


def get_route(addr: AtlasAddress) -> HubRoute:
    """Get hub route for an atlas address."""
    key = addr.parent_address()
    return ARCHETYPE_ROUTES.get(key, HubRoute(Hub.H0))


# =============================================================================
# HUB NETWORK
# =============================================================================

@dataclass
class HubNetwork:
    """
    The complete hub routing network.
    
    Manages connections and routing decisions.
    """
    
    # Active hubs
    active_hubs: Set[Hub] = field(default_factory=lambda: set(Hub))
    
    # Custom routes
    custom_routes: Dict[str, HubRoute] = field(default_factory=dict)
    
    def activate(self, hub: Hub) -> None:
        """Activate a hub."""
        self.active_hubs.add(hub)
    
    def deactivate(self, hub: Hub) -> None:
        """Deactivate a hub."""
        self.active_hubs.discard(hub)
    
    def is_active(self, hub: Hub) -> bool:
        """Check if hub is active."""
        return hub in self.active_hubs
    
    def route(self, addr: AtlasAddress) -> HubRoute:
        """Get route for address (custom or default)."""
        key = addr.short_string()
        if key in self.custom_routes:
            return self.custom_routes[key]
        return get_route(addr)
    
    def add_custom_route(self, addr: AtlasAddress, route: HubRoute) -> None:
        """Add a custom route."""
        self.custom_routes[addr.short_string()] = route
    
    def hubs_for_element(self, element: Element) -> List[Hub]:
        """Get primary hubs for an element."""
        return [h for h in Hub if h.primary_element == element]


# =============================================================================
# DECISION TREE
# =============================================================================

@dataclass
class PhenomenonQuery:
    """
    A query for routing a physical phenomenon.
    
    Answer yes/no questions to determine (Parent, Flavor, HubRoute).
    """
    
    # Is source central?
    sources_central: bool = False
    
    # Is propagation central?
    propagation_central: bool = False
    
    # Is duality/theta central?
    duality_central: bool = False
    
    # Is constraint/boundary central?
    constraint_central: bool = False
    
    # Secondary features
    has_sources: bool = False
    has_wave: bool = False
    has_mixing: bool = False
    has_boundary: bool = False
    
    def determine_parent(self) -> Element:
        """Determine parent element."""
        if self.sources_central:
            return Element.FIRE
        if self.propagation_central:
            return Element.WATER
        if self.duality_central:
            return Element.AIR
        if self.constraint_central:
            return Element.EARTH
        # Default
        return Element.FIRE
    
    def determine_flavor(self) -> Element:
        """Determine flavor element."""
        if self.has_sources:
            return Element.FIRE
        if self.has_wave:
            return Element.WATER
        if self.has_mixing:
            return Element.AIR
        if self.has_boundary:
            return Element.EARTH
        return Element.FIRE
    
    def determine_address(self) -> AtlasAddress:
        """Determine full address (16-level)."""
        parent = self.determine_parent()
        flavor = self.determine_flavor()
        return AtlasAddress(
            primary=parent,
            influence=flavor,
            flavor=Element.FIRE,  # Default
            refinement=Element.FIRE  # Default
        )
    
    def determine_route(self) -> HubRoute:
        """Determine hub route."""
        addr = self.determine_address()
        return get_route(addr)


class DecisionTree:
    """
    The compact decision tree for phenomenon routing.
    
    Maps phenomenon descriptions to (Parent, Flavor, HubRoute).
    """
    
    @staticmethod
    def route_phenomenon(description: str) -> Tuple[Element, Element, HubRoute]:
        """
        Route a phenomenon based on description keywords.
        
        Returns (parent, flavor, route).
        """
        desc_lower = description.lower()
        
        query = PhenomenonQuery()
        
        # Check for sources
        if any(k in desc_lower for k in ['source', 'charge', 'current', 'monopole']):
            query.sources_central = True
            query.has_sources = True
        
        # Check for propagation
        if any(k in desc_lower for k in ['wave', 'propagat', 'green', 'retard']):
            query.propagation_central = True
            query.has_wave = True
        
        # Check for duality
        if any(k in desc_lower for k in ['duality', 'theta', 'axion', 'topolog']):
            query.duality_central = True
            query.has_mixing = True
        
        # Check for constraints
        if any(k in desc_lower for k in ['boundary', 'quantiz', 'lattice', 'medium']):
            query.constraint_central = True
            query.has_boundary = True
        
        parent = query.determine_parent()
        flavor = query.determine_flavor()
        route = query.determine_route()
        
        return (parent, flavor, route)
    
    @staticmethod
    def lookup(addr: AtlasAddress) -> Dict[str, Any]:
        """
        Full lookup for an address.
        
        Returns archetype info and route.
        """
        parent = addr.primary
        influence = addr.influence
        
        route = get_route(addr)
        archetype = None
        for arch in ARCHETYPE_CATALOG:
            if arch.primary == parent and arch.influence == influence:
                archetype = arch
                break
        
        return {
            'address': addr.short_string(),
            'parent': parent.name,
            'influence': influence.name,
            'archetype': archetype.name if archetype else "Unknown",
            'description': archetype.description if archetype else "",
            'route': route.as_string(),
            'primary_hub': route.primary.name_full,
        }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_hubs() -> bool:
    """Validate hubs module."""
    
    # Test Hub enum
    assert len(Hub) == 9
    assert Hub.H0.name_full == "Curvature"
    assert Hub.H3.primary_element == Element.WATER
    
    # Test HubRoute
    route = HubRoute(Hub.H0, [Hub.H3, Hub.H5])
    assert route.contains(Hub.H0)
    assert route.contains(Hub.H3)
    assert not route.contains(Hub.H2)
    assert route.as_string() == "H0 → H3 → H5"
    
    # Test archetype routes
    assert len(ARCHETYPE_ROUTES) == 16
    
    addr = AtlasAddress(
        primary=Element.FIRE,
        influence=Element.WATER,
        flavor=Element.AIR,
        refinement=Element.EARTH
    )
    route = get_route(addr)
    assert route.primary == Hub.H0
    
    # Test HubNetwork
    network = HubNetwork()
    assert network.is_active(Hub.H0)
    
    network.deactivate(Hub.H0)
    assert not network.is_active(Hub.H0)
    
    # Test PhenomenonQuery
    query = PhenomenonQuery(sources_central=True, has_wave=True)
    assert query.determine_parent() == Element.FIRE
    assert query.determine_flavor() == Element.WATER
    
    # Test DecisionTree
    parent, flavor, route = DecisionTree.route_phenomenon(
        "electric charge source in vacuum"
    )
    assert parent == Element.FIRE
    
    parent, flavor, route = DecisionTree.route_phenomenon(
        "wave propagation through medium"
    )
    assert parent == Element.WATER
    
    return True


if __name__ == "__main__":
    print("Validating Hubs Module...")
    assert validate_hubs()
    print("✓ Hubs Module validated")
    
    # Demo
    print("\n=== Hub Routing Demo ===")
    
    print("\n9 Hubs:")
    for hub in Hub:
        print(f"  {hub.name}: {hub.name_full} - {hub.description}")
    
    print("\n16 Archetype Routes:")
    for (p, i), route in ARCHETYPE_ROUTES.items():
        arch = None
        for a in ARCHETYPE_CATALOG:
            if a.primary == p and a.influence == i:
                arch = a
                break
        name = arch.name if arch else "?"
        print(f"  {p.short}{i.short} ({name:10s}): {route.as_string()}")
    
    print("\nDecision Tree Examples:")
    for desc in [
        "electric charge source",
        "wave propagation in plasma",
        "axion-photon conversion",
        "boundary conditions at interface"
    ]:
        parent, flavor, route = DecisionTree.route_phenomenon(desc)
        print(f"  '{desc}'")
        print(f"    → Parent={parent.name}, Flavor={flavor.name}")
        print(f"    → Route: {route.as_string()}")
