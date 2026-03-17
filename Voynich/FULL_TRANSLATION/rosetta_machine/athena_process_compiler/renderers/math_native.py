"""
math_native.py -- Category-theoretic mathematics renderer for VML operator chains.

Maps each VML operator to its categorical counterpart (functors, natural
transformations, limits, colimits, etc.) and assembles the chain into a
mathematical composition diagram expressed in plain-text notation.
"""

from __future__ import annotations

from typing import Any

from athena_process_compiler.schemas.artifacts import NativeRender, Truth
from athena_process_compiler.schemas.ir import OperatorIR

# ---------------------------------------------------------------------------
# Operator -> category-theory mapping
# ---------------------------------------------------------------------------
_OP_MAP: dict[str, str] = {
    "W": "unit",
    "L": "initial",
    "H": "functor",
    "T": "nat-transform",
    "C": "limit",
    "S": "terminal",
    "V": "equalizer",
    "B": "pullback",
    "P": "tensor",
    "F": "colimit",
    "R": "endofunctor",
    "D": "fixed-point",
    "Q": "commute-check",
    "X": "triple-equalizer",
    "G": "counit",
    "M": "coproduct",
}

# Unicode arrows / symbols for the composition diagram
_ARROW = "\u2192"       # ->
_DOUBLE_ARROW = "\u21D2"  # =>
_COMPOSE = "\u2218"     # ring operator

_BACKEND_NAME = "math"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _build_invariants(chain: list[OperatorIR]) -> dict[str, Any]:
    """Domain-agnostic invariants preserved across every backend."""
    return {
        "operators": [node.operator_family for node in chain],
        "carriers": [node.carrier for node in chain],
        "elements": [node.element for node in chain],
        "closure": chain[-1].closure if chain else None,
        "chain_len": len(chain),
    }


def _resolve_op(node: OperatorIR) -> str:
    """Map an OperatorIR to its categorical term."""
    key = node.operator_family.upper()
    if key in _OP_MAP:
        return _OP_MAP[key]
    first = key[0] if key else ""
    if first in _OP_MAP:
        return _OP_MAP[first]
    return f"morphism({node.operator_family})"


def _assess_status(chain: list[OperatorIR]) -> Truth:
    """Conservative aggregate truth from node burdens."""
    burdens = {node.burden for node in chain}
    if not burdens:
        return "FAIL"
    if "FAIL" in burdens:
        return "FAIL"
    if "AMBIG" in burdens:
        return "AMBIG"
    if "NEAR" in burdens:
        return "NEAR"
    return "OK"


def _object_label(node: OperatorIR) -> str:
    """Build a category-object label from the carrier and element."""
    carrier = node.carrier or "Ob"
    elem_initial = node.element[0].upper() if node.element else "V"
    return f"{carrier}_{elem_initial}"


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------

class MathNativeRenderer:
    """Render an OperatorIR chain as a categorical composition diagram."""

    backend = _BACKEND_NAME

    # -- single node ---------------------------------------------------------

    def render_one(self, node: OperatorIR) -> NativeRender:
        """Render one node as a morphism declaration."""
        cat_op = _resolve_op(node)
        obj = _object_label(node)
        line = f"{cat_op} : {obj} {_ARROW} {obj}'"

        return NativeRender(
            backend=_BACKEND_NAME,
            content=line,
            invariants=_build_invariants([node]),
            status=_assess_status([node]),
            notes=[f"categorical_type={cat_op}"],
        )

    # -- full chain ----------------------------------------------------------

    def render_chain(self, chain: list[OperatorIR]) -> NativeRender:
        """Render the full chain as a categorical composition.

        Produces:
          1. Individual morphism declarations
          2. A composition expression  f_n . ... . f_2 . f_1
          3. Commutative-diagram summary
        """
        if not chain:
            return NativeRender(
                backend=_BACKEND_NAME,
                content="(initial object -- empty diagram)",
                invariants=_build_invariants([]),
                status="FAIL",
                notes=["empty chain"],
            )

        lines: list[str] = [
            "=== Categorical Composition Diagram ===",
            "",
            "-- Morphism declarations --",
        ]

        morphism_names: list[str] = []
        for i, node in enumerate(chain, start=1):
            cat_op = _resolve_op(node)
            obj = _object_label(node)
            closure_tag = f"  [{node.closure}]" if node.closure else ""
            fname = f"f_{i}"
            morphism_names.append(fname)
            line = f"  {fname} := {cat_op}({obj}){closure_tag}"
            lines.append(line)

        # Composition expression (right-to-left by convention)
        lines.append("")
        lines.append("-- Composition --")
        comp_expr = f" {_COMPOSE} ".join(reversed(morphism_names))
        lines.append(f"  {comp_expr}")

        # Diagram summary
        lines.append("")
        lines.append("-- Diagram properties --")
        # Count limit/colimit nodes as a rough measure of diagram complexity
        structural_ops = {"limit", "colimit", "pullback", "terminal", "initial"}
        used_ops = {_resolve_op(n) for n in chain}
        structural_count = len(used_ops & structural_ops)
        lines.append(f"  Structural nodes : {structural_count}")
        lines.append(f"  Total morphisms  : {len(chain)}")

        has_equalizer = any(_resolve_op(n) in {"equalizer", "triple-equalizer"} for n in chain)
        has_commute = any(_resolve_op(n) == "commute-check" for n in chain)
        lines.append(f"  Equalizer present: {has_equalizer}")
        lines.append(f"  Commute verified : {has_commute}")

        final_closure = chain[-1].closure or "open"
        lines.append(f"  Terminal closure  : {final_closure}")

        content = "\n".join(lines)
        return NativeRender(
            backend=_BACKEND_NAME,
            content=content,
            invariants=_build_invariants(chain),
            status=_assess_status(chain),
            notes=[f"rendered {len(chain)} morphisms"],
        )
