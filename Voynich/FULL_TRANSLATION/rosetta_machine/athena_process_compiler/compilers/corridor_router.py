"""
corridor_router.py -- Crystal address routing, elemental corridor algebra,
and legality checking for the Athena Process Language Compiler.

The four elemental corridors partition the 16 operator family codes:
    EARTH : L, D, X, S
    WATER : W, T, C, M
    FIRE  : H, P, F, R
    AIR   : V, B, G, Q

Adjacent elements (those sharing an edge on the element square) may
transition freely.  Opposite elements (fire<->water, earth<->air) require
a gate operator to mediate the crossing.

Crystal addresses follow the format:  Book.Folio.Line.Position

Usage:
    >>> from athena_process_compiler.compilers.corridor_router import CorridorRouter
    >>> router = CorridorRouter()
    >>> routed = router.route(ir_nodes)
    >>> routed[0].crystal_address
    'I.f001r.01.0003'
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Sequence

from athena_process_compiler.schemas.ir import OperatorIR

# ---------------------------------------------------------------------------
# Elemental corridor definitions
# ---------------------------------------------------------------------------

CORRIDORS: dict[str, list[str]] = {
    "earth": ["L", "D", "X", "S"],
    "water": ["W", "T", "C", "M"],
    "fire":  ["H", "P", "F", "R"],
    "air":   ["V", "B", "G", "Q"],
}

#: Reverse map: family code -> element.
CODE_TO_ELEMENT: dict[str, str] = {}
for _elem, _codes in CORRIDORS.items():
    for _c in _codes:
        CODE_TO_ELEMENT[_c] = _elem

# ---------------------------------------------------------------------------
# Transition legality
# ---------------------------------------------------------------------------

#: Adjacent element pairs (share an edge on the alchemical square).
#: Transitions between adjacent elements are free.
ADJACENT_PAIRS: frozenset[frozenset[str]] = frozenset([
    frozenset({"earth", "water"}),
    frozenset({"water", "fire"}),
    frozenset({"fire", "air"}),
    frozenset({"air", "earth"}),
])

#: Opposite element pairs (require a gate to cross).
OPPOSITE_PAIRS: frozenset[frozenset[str]] = frozenset([
    frozenset({"earth", "fire"}),
    frozenset({"water", "air"}),
])

#: Alchemical transition names for adjacent pairs.
TRANSITION_NAMES: dict[tuple[str, str], str] = {
    ("earth", "water"): "dissolution",
    ("water", "earth"): "sedimentation",
    ("water", "fire"):  "evaporation",
    ("fire", "water"):  "quenching",
    ("fire", "air"):    "sublimation",
    ("air", "fire"):    "ignition",
    ("air", "earth"):   "condensation",
    ("earth", "air"):   "levitation",
    # Opposite (gated) transitions
    ("earth", "fire"):  "calcination",
    ("fire", "earth"):  "crystallisation",
    ("water", "air"):   "distillation",
    ("air", "water"):   "precipitation",
}

#: Gate family codes that can mediate opposite-element crossings.
GATE_CODES: frozenset[str] = frozenset({"G", "Q"})

#: Maximum corridor length before a gate is required.
MAX_UNGATED_RUN: int = 12


def is_adjacent(a: str, b: str) -> bool:
    """Return True if elements *a* and *b* are adjacent on the element square."""
    return frozenset({a, b}) in ADJACENT_PAIRS


def is_opposite(a: str, b: str) -> bool:
    """Return True if elements *a* and *b* are opposite on the element square."""
    return frozenset({a, b}) in OPPOSITE_PAIRS


def transition_type(src: str, dst: str) -> str:
    """Classify a transition between two elements.

    Returns:
        ``"same"``     -- no transition (same element).
        ``"adjacent"`` -- free transition.
        ``"opposite"`` -- requires a gate.
        ``"unknown"``  -- one or both elements are unrecognised.
    """
    if src == dst:
        return "same"
    if is_adjacent(src, dst):
        return "adjacent"
    if is_opposite(src, dst):
        return "opposite"
    return "unknown"


# ---------------------------------------------------------------------------
# Crystal address
# ---------------------------------------------------------------------------

@dataclass
class CrystalAddress:
    """A four-part address locating a token in the manuscript crystal.

    Format: Book.Folio.Line.Position
    """

    book: str
    folio: str
    line: str
    position: int

    def __str__(self) -> str:
        return f"{self.book}.{self.folio}.{self.line}.{self.position:04d}"

    @classmethod
    def parse(cls, address_str: str) -> CrystalAddress:
        """Parse a dotted address string back into a CrystalAddress.

        Args:
            address_str: A string in ``Book.Folio.Line.Position`` format.

        Returns:
            A CrystalAddress instance.

        Raises:
            ValueError: If the string does not have exactly four dot-separated parts.
        """
        parts = address_str.split(".")
        if len(parts) != 4:
            raise ValueError(
                f"Crystal address must have 4 parts (Book.Folio.Line.Position), "
                f"got {len(parts)}: {address_str!r}"
            )
        return cls(
            book=parts[0],
            folio=parts[1],
            line=parts[2],
            position=int(parts[3]),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation."""
        return {
            "book": self.book,
            "folio": self.folio,
            "line": self.line,
            "position": self.position,
            "canonical": str(self),
        }


def compute_crystal_address(
    book: str, folio: str, line: str, position: int
) -> CrystalAddress:
    """Build a crystal address from its component parts.

    Args:
        book:     Book identifier (e.g. ``"I"``).
        folio:    Folio identifier (e.g. ``"f001r"``).
        line:     Line label within the folio.
        position: Zero-based token position within the line.

    Returns:
        A CrystalAddress instance.
    """
    return CrystalAddress(book=book, folio=folio, line=line, position=position)


# ---------------------------------------------------------------------------
# Metro edge
# ---------------------------------------------------------------------------

@dataclass
class MetroEdge:
    """An edge in the metro routing graph connecting two crystal addresses.

    Attributes:
        source:          Crystal address of the source token.
        target:          Crystal address of the target token.
        edge_type:       One of ``"sequential"``, ``"adjacent_transition"``,
                         ``"gated_transition"``, ``"corridor_boundary"``.
        transition_name: Alchemical name of the transition (e.g. ``"sublimation"``).
        legal:           Whether this edge is legal under the corridor algebra.
    """

    source: str
    target: str
    edge_type: str
    transition_name: str
    legal: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation."""
        return asdict(self)


# ---------------------------------------------------------------------------
# Routed token
# ---------------------------------------------------------------------------

@dataclass
class RoutedToken:
    """An OperatorIR node enriched with crystal coordinates and metro edges.

    Attributes:
        ir:              The original OperatorIR node.
        crystal_address: Computed crystal address.
        element:         Resolved elemental corridor.
        corridor_id:     Identifier of the corridor this token belongs to.
        metro_edges:     Edges connecting this token to its neighbours.
        legal:           Whether all incoming edges are legal.
        violations:      List of legality violations, if any.
    """

    ir: OperatorIR
    crystal_address: CrystalAddress
    element: str
    corridor_id: str
    metro_edges: list[MetroEdge] = field(default_factory=list)
    legal: bool = True
    violations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation."""
        return {
            "token_id": self.ir.token_id,
            "crystal_address": self.crystal_address.to_dict(),
            "element": self.element,
            "corridor_id": self.corridor_id,
            "metro_edges": [e.to_dict() for e in self.metro_edges],
            "legal": self.legal,
            "violations": self.violations,
            "ir": self.ir.to_dict(),
        }

    def to_json(self, **kwargs: Any) -> str:
        """Serialise to a JSON string."""
        return json.dumps(self.to_dict(), **kwargs)


# ---------------------------------------------------------------------------
# Corridor container
# ---------------------------------------------------------------------------

@dataclass
class Corridor:
    """A contiguous run of tokens sharing routing context.

    Attributes:
        corridor_id: Unique identifier (Greek-letter or numeric).
        tokens:      Ordered list of RoutedTokens in the corridor.
        dominant:    The dominant element of this corridor.
        legal:       Whether the corridor passes all legality checks.
        violations:  Human-readable violation descriptions.
    """

    corridor_id: str
    tokens: list[RoutedToken] = field(default_factory=list)
    dominant: str = "void"
    legal: bool = True
    violations: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Legality checker for operator chains
# ---------------------------------------------------------------------------

def check_chain_legality(
    elements: Sequence[str],
    family_codes: Sequence[str],
) -> tuple[bool, list[str]]:
    """Check whether an operator chain is legal under the corridor algebra.

    Rules:
        1. Adjacent element transitions are always legal.
        2. Opposite element transitions require the destination operator to be
           a gate (G or Q) OR the source operator to be a gate.
        3. Runs of more than MAX_UNGATED_RUN tokens without a gate are illegal.

    Args:
        elements:     Sequence of element names for each operator.
        family_codes: Sequence of single-letter family codes for each operator.

    Returns:
        ``(legal, violations)`` where *legal* is True if the chain passes
        all checks.
    """
    if len(elements) != len(family_codes):
        return False, ["elements and family_codes length mismatch"]

    violations: list[str] = []
    run_since_gate = 0

    for i in range(len(elements)):
        code = family_codes[i]
        is_gate = code in GATE_CODES
        if is_gate:
            run_since_gate = 0
        else:
            run_since_gate += 1

        if run_since_gate > MAX_UNGATED_RUN:
            violations.append(
                f"ungated_overrun at position {i}: "
                f"run={run_since_gate} > max={MAX_UNGATED_RUN}"
            )

        if i == 0:
            continue

        src_elem = elements[i - 1]
        dst_elem = elements[i]
        src_code = family_codes[i - 1]

        if src_elem == dst_elem:
            continue

        if is_opposite(src_elem, dst_elem):
            if not (is_gate or src_code in GATE_CODES):
                violations.append(
                    f"ungated_opposite at position {i}: "
                    f"{src_elem}->{dst_elem} requires gate "
                    f"(src_code={src_code!r}, dst_code={code!r})"
                )

    return len(violations) == 0, violations


# ---------------------------------------------------------------------------
# Corridor Router
# ---------------------------------------------------------------------------

_CORRIDOR_NAMES = [
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta",
    "eta", "theta", "iota", "kappa", "lambda", "mu",
    "nu", "xi", "omicron", "pi", "rho", "sigma",
    "tau", "upsilon", "phi", "chi", "psi", "omega",
]


def _corridor_name(index: int) -> str:
    """Generate a corridor identifier from a zero-based index."""
    if index < len(_CORRIDOR_NAMES):
        return _CORRIDOR_NAMES[index]
    return f"corridor_{index}"


def _extract_family_code(operator_family: str) -> str:
    """Extract the single-letter family code from an operator_family string.

    The OperatorIR stores operator_family as ``"CODE:name"`` (e.g. ``"W:weave"``).
    This returns the part before the colon, or the first character if no colon.
    """
    if ":" in operator_family:
        return operator_family.split(":")[0]
    return operator_family[0] if operator_family else "?"


class CorridorRouter:
    """Routes OperatorIR nodes through the elemental corridor algebra.

    Assigns crystal addresses, checks transition legality, builds metro
    edges, and groups tokens into corridors.

    Attributes:
        book:       Book identifier for crystal addresses.
        corridors:  Corridors produced by the most recent ``route()`` call.
    """

    def __init__(self, *, book: str = "I") -> None:
        self.book = book
        self.corridors: list[Corridor] = []
        self._position_counters: dict[str, int] = {}

    def _next_position(self, folio: str, line: str) -> int:
        """Return and increment the position counter for a folio+line."""
        key = f"{folio}:{line}"
        pos = self._position_counters.get(key, 0)
        self._position_counters[key] = pos + 1
        return pos

    def _resolve_element(self, ir: OperatorIR) -> str:
        """Resolve the element for an IR node.

        Prefers the element already set on the IR.  Falls back to looking
        up the family code in CODE_TO_ELEMENT.
        """
        if ir.element and ir.element != "void":
            return ir.element
        code = _extract_family_code(ir.operator_family)
        return CODE_TO_ELEMENT.get(code, "void")

    def route(self, nodes: Sequence[OperatorIR]) -> list[RoutedToken]:
        """Route a sequence of OperatorIR nodes through the corridor algebra.

        This is the main entry point.  For each node it:
            1. Computes a crystal address.
            2. Resolves the elemental corridor.
            3. Builds metro edges to the previous token.
            4. Checks transition legality.
            5. Groups tokens into corridors at gate boundaries.
            6. Annotates the original IR corridor_tags.

        Args:
            nodes: Ordered OperatorIR sequence.

        Returns:
            List of RoutedToken instances with crystal coordinates and
            metro edges populated.
        """
        if not nodes:
            return []

        routed: list[RoutedToken] = []
        corridor_idx = 0
        current_corridor = Corridor(corridor_id=_corridor_name(corridor_idx))
        run_since_gate = 0

        for i, ir in enumerate(nodes):
            # Resolve element
            element = self._resolve_element(ir)
            family_code = _extract_family_code(ir.operator_family)
            is_gate = family_code in GATE_CODES

            # Build crystal address from the IR's context or folio data
            folio = ir.context.get("folio", ir.address.split(".")[1] if "." in ir.address else "f000")
            line = ir.address.split(".")[2] if ir.address.count(".") >= 2 else "00"
            position = self._next_position(folio, line)
            crystal_addr = CrystalAddress(
                book=self.book, folio=folio, line=line, position=position
            )

            # Start new corridor at gate boundaries or overlong runs
            if is_gate or run_since_gate >= MAX_UNGATED_RUN:
                if current_corridor.tokens:
                    self._finalise_corridor(current_corridor)
                    self.corridors.append(current_corridor)
                    corridor_idx += 1
                    current_corridor = Corridor(
                        corridor_id=_corridor_name(corridor_idx)
                    )
                run_since_gate = 0

            # Build metro edges
            metro_edges: list[MetroEdge] = []
            violations: list[str] = []
            token_legal = True

            if routed:
                prev = routed[-1]
                prev_elem = prev.element
                prev_addr = str(prev.crystal_address)
                curr_addr = str(crystal_addr)
                prev_code = _extract_family_code(prev.ir.operator_family)

                t_type = transition_type(prev_elem, element)
                t_name = TRANSITION_NAMES.get(
                    (prev_elem, element), "identity" if t_type == "same" else "unknown"
                )

                if t_type == "same":
                    edge_type = "sequential"
                    edge_legal = True
                elif t_type == "adjacent":
                    edge_type = "adjacent_transition"
                    edge_legal = True
                elif t_type == "opposite":
                    edge_type = "gated_transition"
                    edge_legal = is_gate or prev_code in GATE_CODES
                    if not edge_legal:
                        violations.append(
                            f"ungated_opposite: {prev_elem}->{element} "
                            f"at {curr_addr}"
                        )
                        token_legal = False
                else:
                    edge_type = "unknown"
                    edge_legal = True

                metro_edges.append(MetroEdge(
                    source=prev_addr,
                    target=curr_addr,
                    edge_type=edge_type,
                    transition_name=t_name,
                    legal=edge_legal,
                ))

            # Build RoutedToken
            rt = RoutedToken(
                ir=ir,
                crystal_address=crystal_addr,
                element=element,
                corridor_id=current_corridor.corridor_id,
                metro_edges=metro_edges,
                legal=token_legal,
                violations=violations,
            )
            routed.append(rt)
            current_corridor.tokens.append(rt)
            run_since_gate += 1

            # Annotate the original IR
            ir.corridor_tags.append(f"corridor:{current_corridor.corridor_id}:{len(current_corridor.tokens) - 1}")
            ir.corridor_tags.append(f"crystal:{crystal_addr}")
            ir.corridor_tags.append(f"{element}:self")
            if not token_legal:
                ir.burden = "FAIL"
                for v in violations:
                    ir.corridor_tags.append(f"violation:{v}")

        # Finalise last corridor
        if current_corridor.tokens:
            self._finalise_corridor(current_corridor)
            self.corridors.append(current_corridor)

        return routed

    def _finalise_corridor(self, corridor: Corridor) -> None:
        """Compute dominant element and aggregate legality for a corridor."""
        elem_counts: dict[str, int] = {}
        for rt in corridor.tokens:
            elem_counts[rt.element] = elem_counts.get(rt.element, 0) + 1

        if elem_counts:
            corridor.dominant = max(elem_counts, key=lambda e: elem_counts[e])

        corridor.legal = all(rt.legal for rt in corridor.tokens)
        corridor.violations = []
        for rt in corridor.tokens:
            corridor.violations.extend(rt.violations)

    def reset(self) -> None:
        """Reset internal state between routing passes."""
        self.corridors.clear()
        self._position_counters.clear()

    def summary(self) -> dict[str, Any]:
        """Return a diagnostic summary of the most recent routing pass."""
        return {
            "corridor_count": len(self.corridors),
            "total_tokens": sum(len(c.tokens) for c in self.corridors),
            "legal_corridors": sum(1 for c in self.corridors if c.legal),
            "illegal_corridors": sum(1 for c in self.corridors if not c.legal),
            "violations": [
                {"corridor": c.corridor_id, "violations": c.violations}
                for c in self.corridors if c.violations
            ],
            "corridors": [
                {
                    "id": c.corridor_id,
                    "length": len(c.tokens),
                    "dominant": c.dominant,
                    "legal": c.legal,
                }
                for c in self.corridors
            ],
        }


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------

def route(nodes: Sequence[OperatorIR], *, book: str = "I") -> list[RoutedToken]:
    """Route a node sequence with default settings.

    Args:
        nodes: Ordered OperatorIR sequence.
        book:  Book identifier for crystal addresses.

    Returns:
        List of RoutedToken instances.
    """
    router = CorridorRouter(book=book)
    return router.route(nodes)
