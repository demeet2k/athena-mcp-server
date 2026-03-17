"""
ATHENA OS - BIT4
================
Gate Libraries and Circuit Semantics

From BIT4.docx §6:

GATE LIFTING SCHEMAS:

1. RAIL-DUAL (RD):
   For Boolean gate h: {0,1}ⁿ → {0,1}, lift to BIT4 by:
   T_h^RD = h(t₁,...,tₙ)
   F_h^RD = h(f₁,...,fₙ)

2. MINTERM-SUM (MS):
   For each minterm a ∈ A_h (truth set of h):
   T_h^MS = ∨_{a∈A_h} (∧ᵢ ℓᵢ^sup(aᵢ))
   F_h^MS = ∨_{a∈Ā_h} (∧ᵢ ℓᵢ^sup(aᵢ))

CIRCUIT SEMANTICS:
- Wires range over B₄
- Gates lift Boolean gates to B₄
- Cyclic systems use fixed-point semantics

GATE CLASSIFICATION:
- Closure: total map B₄ⁿ → B₄ᵐ
- Boolean respect: agrees with Boolean on {0,1}ⁿ
- Monotonicity: ≤_k or ≤_t monotone
- Feedback-safe: can be used in SCCs
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Tuple, Optional, Set
from enum import Enum

from .carrier import B4, TwoRail, B4Vector


# =============================================================================
# LIFT SCHEMAS
# =============================================================================

class LiftSchema(Enum):
    """Gate lifting schemas."""
    
    RAIL_DUAL = "RD"      # Rail-dual lift
    MINTERM_SUM = "MS"    # Minterm-sum lift
    SUPPORT = "SUP"       # Support-based lift


# =============================================================================
# BOOLEAN GATES
# =============================================================================

def bool_not(x: bool) -> bool:
    return not x

def bool_and(x: bool, y: bool) -> bool:
    return x and y

def bool_or(x: bool, y: bool) -> bool:
    return x or y

def bool_xor(x: bool, y: bool) -> bool:
    return x != y

def bool_nand(x: bool, y: bool) -> bool:
    return not (x and y)

def bool_nor(x: bool, y: bool) -> bool:
    return not (x or y)

def bool_impl(x: bool, y: bool) -> bool:
    """Implication: x → y = ¬x ∨ y"""
    return (not x) or y


# =============================================================================
# RAIL-DUAL LIFTING
# =============================================================================

def lift_unary_rd(h: Callable[[bool], bool]) -> Callable[[B4], B4]:
    """
    Rail-dual lift of unary Boolean gate.
    
    T_h = h(t)
    F_h = h(f)
    """
    def lifted(x: B4) -> B4:
        enc = TwoRail.encode(x)
        t_out = 1 if h(enc.t == 1) else 0
        f_out = 1 if h(enc.f == 1) else 0
        return TwoRail(t_out, f_out).decode()
    
    return lifted


def lift_binary_rd(h: Callable[[bool, bool], bool]) -> Callable[[B4, B4], B4]:
    """
    Rail-dual lift of binary Boolean gate.
    
    T_h = h(t₁, t₂)
    F_h = h(f₁, f₂)
    """
    def lifted(x: B4, y: B4) -> B4:
        ex = TwoRail.encode(x)
        ey = TwoRail.encode(y)
        
        t_out = 1 if h(ex.t == 1, ey.t == 1) else 0
        f_out = 1 if h(ex.f == 1, ey.f == 1) else 0
        
        return TwoRail(t_out, f_out).decode()
    
    return lifted


# =============================================================================
# BIT4 GATES (RAIL-DUAL LIFTED)
# =============================================================================

def b4_not_rd(x: B4) -> B4:
    """
    Rail-dual NOT.
    
    Note: This is NOT the same as truth-negation ¬!
    RD-NOT gives: ⊥ → ⊥, 0 → 1, 1 → 0, ⊤ → ⊤
    """
    enc = TwoRail.encode(x)
    return TwoRail(1 - enc.t, 1 - enc.f).decode()


def b4_and_rd(x: B4, y: B4) -> B4:
    """Rail-dual AND."""
    ex = TwoRail.encode(x)
    ey = TwoRail.encode(y)
    return TwoRail(
        min(ex.t, ey.t),
        min(ex.f, ey.f)
    ).decode()


def b4_or_rd(x: B4, y: B4) -> B4:
    """Rail-dual OR."""
    ex = TwoRail.encode(x)
    ey = TwoRail.encode(y)
    return TwoRail(
        max(ex.t, ey.t),
        max(ex.f, ey.f)
    ).decode()


def b4_xor_rd(x: B4, y: B4) -> B4:
    """Rail-dual XOR."""
    ex = TwoRail.encode(x)
    ey = TwoRail.encode(y)
    return TwoRail(
        ex.t ^ ey.t,
        ex.f ^ ey.f
    ).decode()


def b4_nand_rd(x: B4, y: B4) -> B4:
    """Rail-dual NAND."""
    enc_and = TwoRail.encode(b4_and_rd(x, y))
    return TwoRail(1 - enc_and.t, 1 - enc_and.f).decode()


def b4_nor_rd(x: B4, y: B4) -> B4:
    """Rail-dual NOR."""
    enc_or = TwoRail.encode(b4_or_rd(x, y))
    return TwoRail(1 - enc_or.t, 1 - enc_or.f).decode()


# =============================================================================
# SUPPORT-BASED LIFTING
# =============================================================================

def lift_unary_support(h: Callable[[bool], bool]) -> Callable[[B4], B4]:
    """
    Support-based lift of unary Boolean gate.
    
    Output support = {h(b) | b ∈ support(x)}
    """
    def lifted(x: B4) -> B4:
        if x.width == 0:
            return B4.BOT
        
        output_support = set()
        for b in x.support:
            result = h(b == 1)
            output_support.add(1 if result else 0)
        
        return B4.from_support(output_support)
    
    return lifted


def lift_binary_support(h: Callable[[bool, bool], bool]) -> Callable[[B4, B4], B4]:
    """
    Support-based lift of binary Boolean gate.
    
    Output support = {h(a, b) | a ∈ support(x), b ∈ support(y)}
    """
    def lifted(x: B4, y: B4) -> B4:
        if x.width == 0 or y.width == 0:
            return B4.BOT
        
        output_support = set()
        for a in x.support:
            for b in y.support:
                result = h(a == 1, b == 1)
                output_support.add(1 if result else 0)
        
        return B4.from_support(output_support)
    
    return lifted


# =============================================================================
# BIT4 GATES (SUPPORT-BASED)
# =============================================================================

def b4_and_sup(x: B4, y: B4) -> B4:
    """Support-based AND."""
    return lift_binary_support(bool_and)(x, y)


def b4_or_sup(x: B4, y: B4) -> B4:
    """Support-based OR."""
    return lift_binary_support(bool_or)(x, y)


def b4_not_sup(x: B4) -> B4:
    """Support-based NOT (same as truth-negation ¬)."""
    return lift_unary_support(bool_not)(x)


# =============================================================================
# GATE SPECIFICATION
# =============================================================================

@dataclass
class GateSpec:
    """
    Specification for a BIT4 gate.
    """
    
    name: str
    arity: int                           # Number of inputs
    lift_schema: LiftSchema
    boolean_func: Optional[Callable] = None
    b4_func: Optional[Callable] = None
    
    # Classification
    k_monotone: bool = True              # ≤_k monotone
    t_monotone: bool = True              # ≤_t monotone
    feedback_safe_k: bool = True         # Safe in k-mode feedback
    feedback_safe_t: bool = True         # Safe in t-mode feedback
    
    def apply(self, *args: B4) -> B4:
        """Apply gate to arguments."""
        if self.b4_func:
            return self.b4_func(*args)
        raise ValueError(f"No B4 function defined for gate {self.name}")


# =============================================================================
# GATE LIBRARY
# =============================================================================

@dataclass
class GateLibrary:
    """
    Library of BIT4 gates.
    """
    
    gates: Dict[str, GateSpec] = field(default_factory=dict)
    
    def register(self, spec: GateSpec) -> None:
        """Register a gate specification."""
        self.gates[spec.name] = spec
    
    def get(self, name: str) -> Optional[GateSpec]:
        """Get gate by name."""
        return self.gates.get(name)
    
    def apply(self, name: str, *args: B4) -> B4:
        """Apply named gate."""
        spec = self.gates.get(name)
        if spec is None:
            raise ValueError(f"Unknown gate: {name}")
        return spec.apply(*args)
    
    @classmethod
    def standard_library(cls) -> 'GateLibrary':
        """Create standard gate library."""
        lib = cls()
        
        # Knowledge lattice operations
        from .orders import join_k, meet_k, join_t, meet_t
        
        lib.register(GateSpec(
            name="JOIN_K", arity=2,
            lift_schema=LiftSchema.SUPPORT,
            b4_func=join_k,
            k_monotone=True, t_monotone=True
        ))
        
        lib.register(GateSpec(
            name="MEET_K", arity=2,
            lift_schema=LiftSchema.SUPPORT,
            b4_func=meet_k,
            k_monotone=True, t_monotone=True
        ))
        
        lib.register(GateSpec(
            name="JOIN_T", arity=2,
            lift_schema=LiftSchema.SUPPORT,
            b4_func=join_t,
            k_monotone=True, t_monotone=True
        ))
        
        lib.register(GateSpec(
            name="MEET_T", arity=2,
            lift_schema=LiftSchema.SUPPORT,
            b4_func=meet_t,
            k_monotone=True, t_monotone=True
        ))
        
        # Rail-dual lifted gates
        lib.register(GateSpec(
            name="AND_RD", arity=2,
            lift_schema=LiftSchema.RAIL_DUAL,
            boolean_func=bool_and,
            b4_func=b4_and_rd,
            k_monotone=True, t_monotone=True
        ))
        
        lib.register(GateSpec(
            name="OR_RD", arity=2,
            lift_schema=LiftSchema.RAIL_DUAL,
            boolean_func=bool_or,
            b4_func=b4_or_rd,
            k_monotone=True, t_monotone=True
        ))
        
        lib.register(GateSpec(
            name="XOR_RD", arity=2,
            lift_schema=LiftSchema.RAIL_DUAL,
            boolean_func=bool_xor,
            b4_func=b4_xor_rd,
            k_monotone=False, t_monotone=False  # XOR is not monotone
        ))
        
        # Support-based gates
        lib.register(GateSpec(
            name="AND_SUP", arity=2,
            lift_schema=LiftSchema.SUPPORT,
            boolean_func=bool_and,
            b4_func=b4_and_sup,
            k_monotone=True, t_monotone=True
        ))
        
        lib.register(GateSpec(
            name="OR_SUP", arity=2,
            lift_schema=LiftSchema.SUPPORT,
            boolean_func=bool_or,
            b4_func=b4_or_sup,
            k_monotone=True, t_monotone=True
        ))
        
        # Involutions
        from .symmetry import neg, kappa, complement
        
        lib.register(GateSpec(
            name="NEG", arity=1,
            lift_schema=LiftSchema.SUPPORT,
            b4_func=neg,
            k_monotone=True, t_monotone=False,
            feedback_safe_k=True, feedback_safe_t=False
        ))
        
        lib.register(GateSpec(
            name="KAPPA", arity=1,
            lift_schema=LiftSchema.SUPPORT,
            b4_func=kappa,
            k_monotone=False, t_monotone=True,
            feedback_safe_k=False, feedback_safe_t=True
        ))
        
        lib.register(GateSpec(
            name="COMP", arity=1,
            lift_schema=LiftSchema.SUPPORT,
            b4_func=complement,
            k_monotone=False, t_monotone=False,
            feedback_safe_k=False, feedback_safe_t=False
        ))
        
        return lib


# =============================================================================
# CIRCUIT REPRESENTATION
# =============================================================================

@dataclass
class Wire:
    """A wire in a BIT4 circuit."""
    
    name: str
    value: B4 = B4.BOT


@dataclass
class GateInstance:
    """An instance of a gate in a circuit."""
    
    gate_name: str
    input_wires: List[str]
    output_wire: str


@dataclass
class Circuit:
    """
    A BIT4 circuit.
    """
    
    wires: Dict[str, Wire] = field(default_factory=dict)
    gates: List[GateInstance] = field(default_factory=list)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    
    library: GateLibrary = field(default_factory=GateLibrary.standard_library)
    
    def add_wire(self, name: str, initial: B4 = B4.BOT) -> None:
        """Add a wire to the circuit."""
        self.wires[name] = Wire(name, initial)
    
    def add_gate(self, gate_name: str, inputs: List[str], output: str) -> None:
        """Add a gate instance."""
        self.gates.append(GateInstance(gate_name, inputs, output))
    
    def set_input(self, name: str, value: B4) -> None:
        """Set an input wire value."""
        if name in self.wires:
            self.wires[name].value = value
    
    def get_output(self, name: str) -> B4:
        """Get an output wire value."""
        return self.wires[name].value if name in self.wires else B4.BOT
    
    def evaluate_once(self) -> bool:
        """
        Evaluate circuit once.
        
        Returns True if any value changed.
        """
        changed = False
        
        for gate_inst in self.gates:
            # Get input values
            inputs = [self.wires[w].value for w in gate_inst.input_wires]
            
            # Apply gate
            output = self.library.apply(gate_inst.gate_name, *inputs)
            
            # Update output wire
            old_value = self.wires[gate_inst.output_wire].value
            if output != old_value:
                self.wires[gate_inst.output_wire].value = output
                changed = True
        
        return changed
    
    def evaluate_to_fixpoint(self, max_iter: int = 100) -> int:
        """
        Evaluate circuit to fixed point.
        
        Returns number of iterations.
        """
        for i in range(max_iter):
            if not self.evaluate_once():
                return i + 1
        return max_iter


# =============================================================================
# VALIDATION
# =============================================================================

def validate_gates() -> bool:
    """Validate gates module."""
    
    # Test rail-dual AND
    assert b4_and_rd(B4.ONE, B4.ONE) == B4.ONE
    assert b4_and_rd(B4.ONE, B4.ZERO) == B4.BOT  # (1,0) ∧ (0,1) = (0,0)
    assert b4_and_rd(B4.TOP, B4.TOP) == B4.TOP
    
    # Test rail-dual OR
    assert b4_or_rd(B4.ONE, B4.ZERO) == B4.TOP  # (1,0) ∨ (0,1) = (1,1)
    assert b4_or_rd(B4.BOT, B4.BOT) == B4.BOT
    
    # Test support-based AND
    assert b4_and_sup(B4.ONE, B4.ONE) == B4.ONE
    assert b4_and_sup(B4.ONE, B4.ZERO) == B4.ZERO
    assert b4_and_sup(B4.TOP, B4.TOP) == B4.TOP
    
    # Test support-based OR
    assert b4_or_sup(B4.ONE, B4.ZERO) == B4.ONE
    assert b4_or_sup(B4.ZERO, B4.ZERO) == B4.ZERO
    assert b4_or_sup(B4.BOT, B4.ONE) == B4.BOT  # Empty support
    
    # Test gate library
    lib = GateLibrary.standard_library()
    assert lib.apply("AND_RD", B4.ONE, B4.ONE) == B4.ONE
    assert lib.apply("JOIN_K", B4.ZERO, B4.ONE) == B4.TOP
    
    # Test circuit
    circ = Circuit()
    circ.add_wire("a")
    circ.add_wire("b")
    circ.add_wire("c")
    circ.inputs = ["a", "b"]
    circ.outputs = ["c"]
    
    circ.add_gate("AND_RD", ["a", "b"], "c")
    
    circ.set_input("a", B4.ONE)
    circ.set_input("b", B4.ONE)
    circ.evaluate_once()
    
    assert circ.get_output("c") == B4.ONE
    
    return True


if __name__ == "__main__":
    print("Validating BIT4 Gates...")
    assert validate_gates()
    print("✓ Gates module validated")
