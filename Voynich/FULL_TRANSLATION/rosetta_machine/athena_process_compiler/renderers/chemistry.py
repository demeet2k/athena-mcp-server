"""
chemistry.py -- Alchemical / chemistry process renderer for VML operator chains.

Maps each VML operator to its laboratory-process equivalent and assembles
the chain into a bench-chemistry protocol narrative.
"""

from __future__ import annotations

from typing import Any

from athena_process_compiler.schemas.artifacts import NativeRender, Truth
from athena_process_compiler.schemas.ir import OperatorIR

# ---------------------------------------------------------------------------
# Operator -> chemistry-process mapping
# ---------------------------------------------------------------------------
_OP_MAP: dict[str, str] = {
    "W": "hydrate",
    "L": "load-ore",
    "H": "calcine",
    "T": "distill",
    "C": "collect",
    "S": "seal-vessel",
    "V": "assay",
    "B": "ligature",
    "P": "press",
    "F": "furnace",
    "R": "reflux",
    "D": "precipitate",
    "Q": "checkpoint",
    "X": "triple-fix",
    "G": "tap",
    "M": "amalgamate",
}

# Element -> classical alchemical symbol for decoration
_ELEMENT_GLYPH: dict[str, str] = {
    "fire": "\u0394",    # Delta -- triangle pointing up
    "water": "\u2207",   # Nabla -- triangle pointing down
    "air": "\u25B3",     # White up-pointing triangle
    "earth": "\u25BD",   # White down-pointing triangle
    "void": "\u2205",    # Empty set
}

_BACKEND_NAME = "chemistry"


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
    """Map an OperatorIR to its chemistry-process term."""
    key = node.operator_family.upper()
    if key in _OP_MAP:
        return _OP_MAP[key]
    first = key[0] if key else ""
    if first in _OP_MAP:
        return _OP_MAP[first]
    return f"process-{node.operator_family}"


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


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------

class ChemistryRenderer:
    """Render an OperatorIR chain as a bench-chemistry / alchemical protocol."""

    backend = _BACKEND_NAME

    # -- single node ---------------------------------------------------------

    def render_one(self, node: OperatorIR) -> NativeRender:
        """Render one node as a single lab instruction line."""
        proc = _resolve_op(node)
        carrier_label = node.carrier or "materia"
        glyph = _ELEMENT_GLYPH.get(node.element, "?")
        line = f"[{glyph}] {proc}({carrier_label})"

        return NativeRender(
            backend=_BACKEND_NAME,
            content=line,
            invariants=_build_invariants([node]),
            status=_assess_status([node]),
            notes=[f"element={node.element}"],
        )

    # -- full chain ----------------------------------------------------------

    def render_chain(self, chain: list[OperatorIR]) -> NativeRender:
        """Render the full chain as an alchemical protocol sheet.

        Format resembles a classical lab notebook:
          Stage 1  [Delta]  calcine(ite)          # fire phase
          Stage 2  [Nabla]  distill(spirit)       # water phase
          ...
        """
        if not chain:
            return NativeRender(
                backend=_BACKEND_NAME,
                content="(empty vessel -- no operations)",
                invariants=_build_invariants([]),
                status="FAIL",
                notes=["empty chain"],
            )

        lines: list[str] = [
            "=== Alchemical Protocol Sheet ===",
            "",
        ]

        for i, node in enumerate(chain, start=1):
            proc = _resolve_op(node)
            carrier_label = node.carrier or "materia"
            glyph = _ELEMENT_GLYPH.get(node.element, "?")
            closure_note = f"  -> closure: {node.closure}" if node.closure else ""
            line = f"  Stage {i:>2}  [{glyph}]  {proc}({carrier_label}){closure_note}"
            lines.append(line)

        # Summary
        element_counts: dict[str, int] = {}
        for node in chain:
            element_counts[node.element] = element_counts.get(node.element, 0) + 1

        lines.append("")
        lines.append("--- Elemental Balance ---")
        for elem, count in sorted(element_counts.items()):
            glyph = _ELEMENT_GLYPH.get(elem, "?")
            lines.append(f"  {glyph} {elem:<8} x{count}")

        final_closure = chain[-1].closure or "open-vessel"
        lines.append("")
        lines.append(f"Vessel seal : {final_closure}")
        lines.append(f"Total stages: {len(chain)}")

        content = "\n".join(lines)
        return NativeRender(
            backend=_BACKEND_NAME,
            content=content,
            invariants=_build_invariants(chain),
            status=_assess_status(chain),
            notes=[f"rendered {len(chain)} stages"],
        )
