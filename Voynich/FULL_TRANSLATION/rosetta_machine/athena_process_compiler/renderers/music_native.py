"""
music_native.py -- Western music-theory renderer for VML operator chains.

Maps each VML operator to a music-structural concept (tonic, cadence,
fermata, da capo, etc.) and assembles the chain into a score-annotation
narrative -- the kind of description a conductor or analyst would write
in the margins of a score.
"""

from __future__ import annotations

from typing import Any

from athena_process_compiler.schemas.artifacts import NativeRender, Truth
from athena_process_compiler.schemas.ir import OperatorIR

# ---------------------------------------------------------------------------
# Operator -> music-theory mapping
# ---------------------------------------------------------------------------
_OP_MAP: dict[str, str] = {
    "W": "anacrusis",
    "L": "tonic",
    "H": "accent",
    "T": "passing-tone",
    "C": "cadence-capture",
    "S": "fermata",
    "V": "repeat-sign",
    "B": "tie",
    "P": "crescendo",
    "F": "fortissimo",
    "R": "da-capo",
    "D": "resolution",
    "Q": "barline",
    "X": "triple-forte",
    "G": "coda",
    "M": "chord",
}

# Unicode music symbols for decoration
_MUSIC_GLYPH: dict[str, str] = {
    "anacrusis": "\U0001D100",      # MUSICAL SYMBOL SINGLE BARLINE (approx.)
    "tonic": "\U0001D15E",          # MUSICAL SYMBOL HALF NOTE
    "accent": ">",
    "passing-tone": "\u266A",       # EIGHTH NOTE
    "cadence-capture": "\u2016",    # DOUBLE VERTICAL LINE
    "fermata": "\U0001D110",        # MUSICAL SYMBOL FERMATA
    "repeat-sign": "\U0001D106",    # MUSICAL SYMBOL LEFT REPEAT SIGN
    "tie": "\u2040",                # CHARACTER TIE
    "crescendo": "<",
    "fortissimo": "ff",
    "da-capo": "D.C.",
    "resolution": "\u266D",         # MUSIC FLAT SIGN (resolution often "flattens")
    "barline": "|",
    "triple-forte": "fff",
    "coda": "\U0001D10C",           # MUSICAL SYMBOL CODA
    "chord": "\u266F",              # MUSIC SHARP SIGN
}

_BACKEND_NAME = "music"


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
    """Map an OperatorIR to its music-theory term."""
    key = node.operator_family.upper()
    if key in _OP_MAP:
        return _OP_MAP[key]
    first = key[0] if key else ""
    if first in _OP_MAP:
        return _OP_MAP[first]
    return f"motif({node.operator_family})"


def _glyph_for(term: str) -> str:
    """Return a Unicode music symbol for the given term, or empty string."""
    return _MUSIC_GLYPH.get(term, "")


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

class MusicNativeRenderer:
    """Render an OperatorIR chain as a music-analytic score annotation."""

    backend = _BACKEND_NAME

    # -- single node ---------------------------------------------------------

    def render_one(self, node: OperatorIR) -> NativeRender:
        """Render one node as a single score annotation."""
        term = _resolve_op(node)
        glyph = _glyph_for(term)
        carrier_label = node.carrier or "voice"
        prefix = f"{glyph} " if glyph else ""
        line = f"{prefix}{term}({carrier_label})"

        return NativeRender(
            backend=_BACKEND_NAME,
            content=line,
            invariants=_build_invariants([node]),
            status=_assess_status([node]),
            notes=[f"music_term={term}"],
        )

    # -- full chain ----------------------------------------------------------

    def render_chain(self, chain: list[OperatorIR]) -> NativeRender:
        """Render the full chain as a score-margin analytical narrative.

        Produces a bar-by-bar annotation list plus a structural summary
        that identifies form (intro, body, coda) based on operator types.
        """
        if not chain:
            return NativeRender(
                backend=_BACKEND_NAME,
                content="(tacet -- no score)",
                invariants=_build_invariants([]),
                status="FAIL",
                notes=["empty chain"],
            )

        lines: list[str] = [
            "=== Score Analysis -- Music Rendering ===",
            "",
        ]

        # Track structural regions for the summary.
        has_anacrusis = False
        has_coda = False
        has_da_capo = False
        barline_count = 0

        for i, node in enumerate(chain, start=1):
            term = _resolve_op(node)
            glyph = _glyph_for(term)
            carrier_label = node.carrier or "voice"
            closure_tag = f"  [attacca: {node.closure}]" if node.closure else ""
            prefix = f"{glyph} " if glyph else ""
            line = f"  m.{i:>3}  {prefix}{term}({carrier_label}){closure_tag}"
            lines.append(line)

            # Track form indicators
            if term == "anacrusis":
                has_anacrusis = True
            elif term == "coda":
                has_coda = True
            elif term == "da-capo":
                has_da_capo = True
            elif term == "barline":
                barline_count += 1

        # Structural summary
        lines.append("")
        lines.append("--- Form Analysis ---")

        # Determine implied form
        form_parts: list[str] = []
        if has_anacrusis:
            form_parts.append("Introduction (anacrusis)")
        form_parts.append("Body")
        if has_da_capo:
            form_parts.append("Recapitulation (da capo)")
        if has_coda:
            form_parts.append("Coda")
        lines.append(f"  Implied form : {' -> '.join(form_parts)}")

        lines.append(f"  Barlines     : {barline_count}")
        lines.append(f"  Total events : {len(chain)}")

        # Dynamic profile
        dynamic_terms = {"crescendo", "fortissimo", "triple-forte", "accent"}
        dynamic_count = sum(1 for n in chain if _resolve_op(n) in dynamic_terms)
        lines.append(f"  Dynamic marks: {dynamic_count}")

        final_closure = chain[-1].closure or "open (attacca)"
        lines.append(f"  Final closure: {final_closure}")

        content = "\n".join(lines)
        return NativeRender(
            backend=_BACKEND_NAME,
            content=content,
            invariants=_build_invariants(chain),
            status=_assess_status(chain),
            notes=[f"rendered {len(chain)} events"],
        )
