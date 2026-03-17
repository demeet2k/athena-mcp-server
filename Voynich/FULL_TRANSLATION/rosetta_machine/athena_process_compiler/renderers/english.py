"""
english.py -- Natural-language (English) renderer for VML operator chains.

Translates each of the 16 canonical VML operators into plain English
process verbs, then assembles the chain into a readable procedural
narrative.
"""

from __future__ import annotations

from typing import Any

from athena_process_compiler.schemas.artifacts import NativeRender, Truth
from athena_process_compiler.schemas.ir import OperatorIR

# ---------------------------------------------------------------------------
# Operator -> English verb mapping
# ---------------------------------------------------------------------------
_OP_MAP: dict[str, str] = {
    "W": "moisten / prime / activate",
    "L": "load substrate / root matter",
    "H": "heat / drive / energize",
    "T": "transfer through conduit",
    "C": "capture / collect / retain",
    "S": "seal / contain / clamp",
    "V": "verify / check / validate",
    "B": "bind / connect / ligature",
    "P": "apply pressure / compress",
    "F": "fire-seal / furnace-lock",
    "R": "recirculate / rotate / return",
    "D": "fix / stabilize / lock",
    "Q": "checkpoint / certify cycle",
    "X": "triple-fix / terminal lock",
    "G": "gate / threshold test",
    "M": "merge / conjoin / amalgamate",
}

_BACKEND_NAME = "english"


# ---------------------------------------------------------------------------
# Invariant builder
# ---------------------------------------------------------------------------

def _build_invariants(chain: list[OperatorIR]) -> dict[str, Any]:
    """Extract the domain-agnostic invariants that must hold across backends.

    Canonical invariant keys:
        operators  -- ordered list of operator_family strings
        carriers   -- ordered list of carrier strings
        elements   -- ordered list of element strings
        closure    -- the closure annotation from the final node, or None
        chain_len  -- number of nodes in the chain
    """
    return {
        "operators": [node.operator_family for node in chain],
        "carriers": [node.carrier for node in chain],
        "elements": [node.element for node in chain],
        "closure": chain[-1].closure if chain else None,
        "chain_len": len(chain),
    }


def _resolve_op(node: OperatorIR) -> str:
    """Map an OperatorIR to its English verb phrase.

    Uses ``operator_family`` first (single-letter key), then falls back to a
    generic description so the renderer never crashes on unknown operators.
    """
    key = node.operator_family.upper()
    # Try exact single-letter match first.
    if key in _OP_MAP:
        return _OP_MAP[key]
    # Try first character (handles families like "transform" -> "T").
    first = key[0] if key else ""
    if first in _OP_MAP:
        return _OP_MAP[first]
    return f"process ({node.operator_family})"


def _assess_status(chain: list[OperatorIR]) -> Truth:
    """Derive an aggregate truth verdict from the chain burdens.

    Rules (conservative):
        - All OK   -> OK
        - Any FAIL -> FAIL
        - Any AMBIG (no FAIL) -> AMBIG
        - Any NEAR  (no FAIL/AMBIG) -> NEAR
    """
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
# Renderer class
# ---------------------------------------------------------------------------

class EnglishRenderer:
    """Render an OperatorIR chain as a plain-English procedural narrative."""

    backend = _BACKEND_NAME

    # -- single node ---------------------------------------------------------

    def render_one(self, node: OperatorIR) -> NativeRender:
        """Render a single OperatorIR node.

        Returns a NativeRender whose *content* is a one-line English sentence.
        """
        verb = _resolve_op(node)
        carrier_label = node.carrier or "substance"
        line = f"Step {node.address}: {verb} the {carrier_label} [{node.element}]"

        invariants = _build_invariants([node])
        status = _assess_status([node])

        return NativeRender(
            backend=_BACKEND_NAME,
            content=line,
            invariants=invariants,
            status=status,
            notes=[f"operator_family={node.operator_family}", f"lens={node.lens}"],
        )

    # -- full chain ----------------------------------------------------------

    def render_chain(self, chain: list[OperatorIR]) -> NativeRender:
        """Render a complete operator chain as a multi-line English narrative.

        The output reads like a numbered recipe / procedure.
        """
        if not chain:
            return NativeRender(
                backend=_BACKEND_NAME,
                content="(empty process -- no operators)",
                invariants=_build_invariants([]),
                status="FAIL",
                notes=["empty chain"],
            )

        lines: list[str] = ["=== Athena Process -- English Rendering ===", ""]

        for i, node in enumerate(chain, start=1):
            verb = _resolve_op(node)
            carrier_label = node.carrier or "substance"
            element_tag = f"[{node.element}]"
            closure_tag = f" (closure: {node.closure})" if node.closure else ""
            line = f"  {i}. {verb.capitalize()} the {carrier_label} {element_tag}{closure_tag}"
            lines.append(line)

        # Summary footer
        elements_seen = sorted({n.element for n in chain})
        lines.append("")
        lines.append(f"Elements engaged : {', '.join(elements_seen)}")
        lines.append(f"Total steps      : {len(chain)}")
        final_closure = chain[-1].closure or "open"
        lines.append(f"Final closure    : {final_closure}")

        content = "\n".join(lines)
        invariants = _build_invariants(chain)
        status = _assess_status(chain)

        return NativeRender(
            backend=_BACKEND_NAME,
            content=content,
            invariants=invariants,
            status=status,
            notes=[f"rendered {len(chain)} steps"],
        )
