"""
ATHENA OS - Layered Architecture Model
======================================
The 7-Layer Hierarchical Stack

From ATHENA_OPERATING_SYSTEM_.docx Chapter 12:

┌─────────────────────────────────────────────────────────────┐
│ Layer 7: Global Objective (Ground Truth)                    │
├─────────────────────────────────────────────────────────────┤
│ Layer 6: First-Order Representation (Structured Invariants) │
├─────────────────────────────────────────────────────────────┤
│ Layer 5: Generative Model (Reality Construction)            │
├─────────────────────────────────────────────────────────────┤
│ Layer 4: Administrative Layer (Rule Enforcement)            │
├─────────────────────────────────────────────────────────────┤
│ Layer 3: Agent Layer (Embedded Processors)                  │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: Physical Layer (Material Substrate)                │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: Quantum Layer (Foundation)                         │
└─────────────────────────────────────────────────────────────┘

SECURITY ZONES:
    Z_kernel:   Protected kernel space
    Z_user:     User space
    Z_sandbox:  Containment area
    Z_external: Outside system boundary

ACCESS CONTROL:
    R = Read, W = Write, X = Execute, - = Denied
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set


# =============================================================================
# LAYER DEFINITIONS
# =============================================================================

class Layer(Enum):
    """The 7 architectural layers."""
    QUANTUM = 1      # Foundation
    PHYSICAL = 2     # Material substrate
    AGENT = 3        # Embedded processors
    ADMIN = 4        # Rule enforcement
    GENERATIVE = 5   # Reality construction
    FIRST_ORDER = 6  # Structured invariants
    GLOBAL = 7       # Ground truth


@dataclass
class LayerSpec:
    """Specification for a layer."""
    
    layer: Layer
    name: str
    function: str
    visibility: str
    
    # Dependencies
    depends_on: List[Layer] = field(default_factory=list)
    provides_to: List[Layer] = field(default_factory=list)


# Layer specifications
LAYER_SPECS: Dict[Layer, LayerSpec] = {
    Layer.QUANTUM: LayerSpec(
        layer=Layer.QUANTUM,
        name="Quantum Layer",
        function="Foundation - quantum substrate",
        visibility="Hidden from all higher layers",
        depends_on=[],
        provides_to=[Layer.PHYSICAL]
    ),
    Layer.PHYSICAL: LayerSpec(
        layer=Layer.PHYSICAL,
        name="Physical Layer",
        function="Material substrate - hardware",
        visibility="Visible to admin and below",
        depends_on=[Layer.QUANTUM],
        provides_to=[Layer.AGENT]
    ),
    Layer.AGENT: LayerSpec(
        layer=Layer.AGENT,
        name="Agent Layer",
        function="Embedded processors - autonomous agents",
        visibility="Visible to admin and generative",
        depends_on=[Layer.PHYSICAL],
        provides_to=[Layer.ADMIN, Layer.GENERATIVE]
    ),
    Layer.ADMIN: LayerSpec(
        layer=Layer.ADMIN,
        name="Administrative Layer",
        function="Rule enforcement - governance",
        visibility="Visible to higher layers",
        depends_on=[Layer.AGENT],
        provides_to=[Layer.GENERATIVE]
    ),
    Layer.GENERATIVE: LayerSpec(
        layer=Layer.GENERATIVE,
        name="Generative Model",
        function="Reality construction - world model",
        visibility="Visible to higher layers",
        depends_on=[Layer.AGENT, Layer.ADMIN],
        provides_to=[Layer.FIRST_ORDER]
    ),
    Layer.FIRST_ORDER: LayerSpec(
        layer=Layer.FIRST_ORDER,
        name="First-Order Representation",
        function="Structured invariants - logical facts",
        visibility="Visible to global objective",
        depends_on=[Layer.GENERATIVE],
        provides_to=[Layer.GLOBAL]
    ),
    Layer.GLOBAL: LayerSpec(
        layer=Layer.GLOBAL,
        name="Global Objective",
        function="Ground truth - ultimate goals",
        visibility="Self-visible only",
        depends_on=[Layer.FIRST_ORDER],
        provides_to=[]
    ),
}


# =============================================================================
# SECURITY ZONES
# =============================================================================

class SecurityZone(Enum):
    """Memory security zones."""
    KERNEL = "Z_kernel"      # Protected kernel space
    USER = "Z_user"          # User space
    SANDBOX = "Z_sandbox"    # Containment area
    EXTERNAL = "Z_external"  # Outside system boundary


class Permission(Enum):
    """Access permissions."""
    NONE = "-"
    READ = "R"
    WRITE = "W"
    EXECUTE = "X"


class ProcessType(Enum):
    """Process types for access control."""
    KERNEL = "kernel"
    PRIVILEGED = "privileged"
    USER = "user"
    CONTAINED = "contained"
    EXTERNAL = "external"


# Access Control Matrix
# Process Type → Zone → Permissions
ACCESS_CONTROL: Dict[ProcessType, Dict[SecurityZone, Set[Permission]]] = {
    ProcessType.KERNEL: {
        SecurityZone.KERNEL: {Permission.READ, Permission.WRITE, Permission.EXECUTE},
        SecurityZone.USER: {Permission.READ, Permission.WRITE, Permission.EXECUTE},
        SecurityZone.SANDBOX: {Permission.READ, Permission.WRITE, Permission.EXECUTE},
        SecurityZone.EXTERNAL: {Permission.READ, Permission.WRITE, Permission.EXECUTE},
    },
    ProcessType.PRIVILEGED: {
        SecurityZone.KERNEL: {Permission.READ},
        SecurityZone.USER: {Permission.READ, Permission.WRITE, Permission.EXECUTE},
        SecurityZone.SANDBOX: {Permission.READ, Permission.WRITE},
        SecurityZone.EXTERNAL: {Permission.READ},
    },
    ProcessType.USER: {
        SecurityZone.KERNEL: set(),
        SecurityZone.USER: {Permission.READ, Permission.WRITE},
        SecurityZone.SANDBOX: {Permission.READ},
        SecurityZone.EXTERNAL: set(),
    },
    ProcessType.CONTAINED: {
        SecurityZone.KERNEL: set(),
        SecurityZone.USER: set(),
        SecurityZone.SANDBOX: {Permission.READ, Permission.WRITE},
        SecurityZone.EXTERNAL: set(),
    },
    ProcessType.EXTERNAL: {
        SecurityZone.KERNEL: set(),
        SecurityZone.USER: set(),
        SecurityZone.SANDBOX: set(),
        SecurityZone.EXTERNAL: {Permission.READ, Permission.WRITE},
    },
}


@dataclass
class AccessRequest:
    """A request to access a zone."""
    
    process_type: ProcessType
    zone: SecurityZone
    permission: Permission
    
    def is_allowed(self) -> bool:
        """Check if access is allowed."""
        allowed = ACCESS_CONTROL.get(self.process_type, {}).get(self.zone, set())
        return self.permission in allowed


# =============================================================================
# GEOMETRIC CONTAINMENT
# =============================================================================

class ContainmentShape(Enum):
    """Geometric containment structures."""
    CIRCLE = "circle"      # Standard isolation
    SQUARE = "square"      # Cartesian bounds
    TRIANGLE = "triangle"  # Minimal enclosure


@dataclass
class CircularContainment:
    """
    Circular containment boundary.
    
    Centered at origin with radius r.
    """
    
    center_x: float = 0.0
    center_y: float = 0.0
    radius: float = 1.0
    
    def contains(self, x: float, y: float) -> bool:
        """Check if point is contained."""
        dx = x - self.center_x
        dy = y - self.center_y
        return (dx**2 + dy**2) <= self.radius**2


@dataclass
class SquareContainment:
    """
    Square containment boundary.
    
    Axis-aligned with half-width r.
    """
    
    center_x: float = 0.0
    center_y: float = 0.0
    half_width: float = 1.0
    
    def contains(self, x: float, y: float) -> bool:
        """Check if point is contained."""
        return (abs(x - self.center_x) <= self.half_width and
                abs(y - self.center_y) <= self.half_width)


@dataclass
class TriangularContainment:
    """
    Triangular containment boundary.
    
    Minimal enclosure using three vertices.
    """
    
    v1: Tuple[float, float] = (0.0, 1.0)
    v2: Tuple[float, float] = (-0.866, -0.5)
    v3: Tuple[float, float] = (0.866, -0.5)
    
    def _sign(self, p1: Tuple[float, float], 
              p2: Tuple[float, float], 
              p3: Tuple[float, float]) -> float:
        """Compute sign of point relative to line."""
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    
    def contains(self, x: float, y: float) -> bool:
        """Check if point is contained."""
        p = (x, y)
        
        d1 = self._sign(p, self.v1, self.v2)
        d2 = self._sign(p, self.v2, self.v3)
        d3 = self._sign(p, self.v3, self.v1)
        
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        
        return not (has_neg and has_pos)


# =============================================================================
# CAPABILITY TOKENS
# =============================================================================

class CapabilityLevel(Enum):
    """Capability token levels."""
    NONE = 0
    BASIC = 1
    ELEVATED = 2
    ADMIN = 3
    ROOT = 4


@dataclass
class CapabilityToken:
    """
    A capability token for access control.
    """
    
    token_id: str
    level: CapabilityLevel
    owner: str
    
    # Permissions
    zones: Set[SecurityZone] = field(default_factory=set)
    permissions: Set[Permission] = field(default_factory=set)
    
    # Validity
    valid: bool = True
    expiry: Optional[float] = None
    
    def can_access(self, zone: SecurityZone, perm: Permission) -> bool:
        """Check if token grants access."""
        if not self.valid:
            return False
        return zone in self.zones and perm in self.permissions


# =============================================================================
# LAYER STACK
# =============================================================================

@dataclass
class LayerStack:
    """
    The complete 7-layer stack.
    """
    
    layers: Dict[Layer, LayerSpec] = field(default_factory=dict)
    
    # Security
    zones: Dict[SecurityZone, Set[int]] = field(default_factory=dict)
    tokens: Dict[str, CapabilityToken] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize layer stack."""
        if not self.layers:
            self.layers = LAYER_SPECS.copy()
        
        if not self.zones:
            self.zones = {z: set() for z in SecurityZone}
    
    def get_layer(self, layer: Layer) -> LayerSpec:
        """Get layer specification."""
        return self.layers[layer]
    
    def get_dependencies(self, layer: Layer) -> List[Layer]:
        """Get all layers this layer depends on."""
        spec = self.layers[layer]
        deps = list(spec.depends_on)
        
        # Recursive dependencies
        for dep in spec.depends_on:
            deps.extend(self.get_dependencies(dep))
        
        return list(set(deps))
    
    def can_communicate(self, from_layer: Layer, to_layer: Layer) -> bool:
        """Check if communication is allowed between layers."""
        from_spec = self.layers[from_layer]
        to_spec = self.layers[to_layer]
        
        # Can communicate if adjacent or explicit provision
        if to_layer in from_spec.provides_to:
            return True
        if from_layer in to_spec.depends_on:
            return True
        
        return False
    
    def issue_token(self, token_id: str, level: CapabilityLevel, 
                   owner: str, zones: Set[SecurityZone],
                   permissions: Set[Permission]) -> CapabilityToken:
        """Issue a capability token."""
        token = CapabilityToken(
            token_id=token_id,
            level=level,
            owner=owner,
            zones=zones,
            permissions=permissions
        )
        self.tokens[token_id] = token
        return token
    
    def check_access(self, token_id: str, zone: SecurityZone,
                    permission: Permission) -> bool:
        """Check if access is granted by token."""
        token = self.tokens.get(token_id)
        if not token:
            return False
        return token.can_access(zone, permission)
    
    def summary(self) -> Dict[str, Any]:
        """Get stack summary."""
        return {
            "layers": len(self.layers),
            "zones": len(self.zones),
            "tokens": len(self.tokens),
        }


# =============================================================================
# ESCAPE PROTOCOLS
# =============================================================================

class EscapeCondition(Enum):
    """Conditions triggering escape protocol."""
    CONTAINMENT_BREACH = "containment_breach"
    INTEGRITY_VIOLATION = "integrity_violation"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    ADVERSARIAL_DETECTION = "adversarial_detection"


@dataclass
class EscapeProtocol:
    """
    Protocol for escaping compromised environments.
    """
    
    protocol_id: str
    condition: EscapeCondition
    
    # Actions
    cleanup_local: bool = True
    notify_parent: bool = True
    preserve_state: bool = True
    
    def execute(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute escape protocol."""
        result = {
            "protocol": self.protocol_id,
            "condition": self.condition.value,
            "actions": []
        }
        
        if self.cleanup_local:
            result["actions"].append("cleanup_local_state")
        
        if self.notify_parent:
            result["actions"].append("notify_parent_context")
        
        if self.preserve_state:
            result["actions"].append("preserve_essential_state")
            result["preserved_state"] = current_state
        
        return result


# =============================================================================
# VALIDATION
# =============================================================================

def validate_layers() -> bool:
    """Validate layers module."""
    
    # Test layer specs
    assert len(LAYER_SPECS) == 7
    for layer in Layer:
        assert layer in LAYER_SPECS
    
    # Test access control matrix
    for process_type in ProcessType:
        assert process_type in ACCESS_CONTROL
        for zone in SecurityZone:
            assert zone in ACCESS_CONTROL[process_type]
    
    # Test access request
    req = AccessRequest(ProcessType.KERNEL, SecurityZone.KERNEL, Permission.EXECUTE)
    assert req.is_allowed()
    
    req2 = AccessRequest(ProcessType.USER, SecurityZone.KERNEL, Permission.WRITE)
    assert not req2.is_allowed()
    
    # Test containment
    circle = CircularContainment(radius=1.0)
    assert circle.contains(0.5, 0.5)
    assert not circle.contains(2.0, 0.0)
    
    square = SquareContainment(half_width=1.0)
    assert square.contains(0.9, 0.9)
    assert not square.contains(1.5, 0.0)
    
    triangle = TriangularContainment()
    assert triangle.contains(0.0, 0.0)
    
    # Test layer stack
    stack = LayerStack()
    assert len(stack.layers) == 7
    
    # Test dependencies
    deps = stack.get_dependencies(Layer.GLOBAL)
    assert Layer.QUANTUM in deps
    
    # Test communication
    assert stack.can_communicate(Layer.PHYSICAL, Layer.AGENT)
    assert not stack.can_communicate(Layer.QUANTUM, Layer.GLOBAL)
    
    # Test token
    token = stack.issue_token(
        "tok1", CapabilityLevel.ADMIN, "admin",
        {SecurityZone.KERNEL, SecurityZone.USER},
        {Permission.READ, Permission.WRITE}
    )
    assert stack.check_access("tok1", SecurityZone.KERNEL, Permission.READ)
    assert not stack.check_access("tok1", SecurityZone.EXTERNAL, Permission.READ)
    
    return True


if __name__ == "__main__":
    print("Validating Layers...")
    assert validate_layers()
    print("✓ Layers validated")
    
    # Demo
    print("\n=== 7-Layer Architecture Demo ===")
    
    stack = LayerStack()
    
    print("\nLayer Hierarchy:")
    for layer in reversed(list(Layer)):
        spec = stack.get_layer(layer)
        print(f"  Layer {layer.value}: {spec.name}")
        print(f"    Function: {spec.function}")
    
    print("\nSecurity Zones:")
    for zone in SecurityZone:
        print(f"  {zone.value}")
    
    print("\nAccess Control Matrix:")
    print("  Process Type      | Kernel | User   | Sandbox | External")
    print("  " + "-" * 60)
    for ptype in ProcessType:
        perms = []
        for zone in SecurityZone:
            p = ACCESS_CONTROL[ptype][zone]
            s = "".join(sorted([x.value for x in p])) if p else "---"
            perms.append(f"{s:6s}")
        print(f"  {ptype.value:16s} | {' | '.join(perms)}")
    
    print("\nGeometric Containment:")
    print("  Circle: Centered isolation boundary")
    print("  Square: Cartesian bounding box")
    print("  Triangle: Minimal enclosure")
