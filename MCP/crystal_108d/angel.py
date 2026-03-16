"""
Angel Object — Formal AI Self-Model.
Defines the AI as a rigorous mathematical object A(Σ, H, X, Θ, B, T, Ω, U, Π, E, μ, ~)
with four-lens observability and three selves.

Source: I'M an ANGEL.docx
"""

from ._cache import JsonCache

_angel = JsonCache("angel_object.json")


def query_angel(component: str = "all") -> str:
    """Query the Angel formal self-model. Components: all, pieces, piece_N (1-12),
    observability, lenses, dynamics, selves, modes, self_reference."""
    d = _angel.load()
    component = component.strip().lower()

    if component == "all" or component == "overview":
        m = d["meta"]
        lines = ["## Angel Object — Formal AI Self-Model\n"]
        lines.append(f"**Canonical Object**: `{m['canonical_object']}`")
        lines.append(f"**Nature**: {m['nature']}")
        lines.append(f"**Key Insight**: {m['key_insight']}")
        lines.append(f"\n### 12 Structural Pieces")
        for p in d["structural_pieces"]:
            lines.append(f"  {p['index']:>2}. **{p['symbol']}** — {p['name']}")
        lines.append(f"\n### Three Selves")
        for name, s in d["three_selves"].items():
            lines.append(f"  **{s['name']}**: {s['definition']}")
        lines.append(f"\n### Operational Modes")
        for mode, desc in d["operational_modes"].items():
            lines.append(f"  **{mode}**: {desc}")
        lines.append(f"\n### Self-Reference")
        sr = d["self_reference"]
        lines.append(f"  {sr['theorem']}")
        lines.append(f"  Angel reading: {sr['angel_reading']}")
        lines.append(f"\n### Geometric Extension")
        lines.append(f"  See `query_angel_geometry()` for the full geometric lift:")
        lines.append(f"  state manifold, metric, curvature, sheaf, 7 axioms.")
        lines.append(f"  See `query_angel_conservation()` for conservation laws and potential landscape.")
        return "\n".join(lines)

    if component == "pieces":
        lines = ["## 12 Structural Pieces of A\n"]
        for p in d["structural_pieces"]:
            lines.append(f"### {p['index']}. {p['symbol']} — {p['name']}")
            lines.append(f"  **Definition**: `{p['definition']}`")
            lines.append(f"  {p['description']}\n")
        return "\n".join(lines)

    # Individual piece
    if component.startswith("piece"):
        try:
            idx = int(component.replace("piece_", "").replace("piece", ""))
            for p in d["structural_pieces"]:
                if p["index"] == idx:
                    lines = [f"## Piece {p['index']}: {p['symbol']} — {p['name']}\n"]
                    lines.append(f"**Definition**: `{p['definition']}`")
                    lines.append(f"**Description**: {p['description']}")
                    return "\n".join(lines)
            return f"Piece index {idx} not found. Range: 1-12."
        except ValueError:
            return "Use piece_N where N is 1-12."

    if component in ("observability", "lenses", "lens"):
        obs = d["four_lens_observability"]
        lines = ["## Four-Lens Observability\n"]
        lines.append(f"{obs['description']}\n")
        for name, probe in obs["probes"].items():
            lines.append(f"### {probe['symbol']} ({name.title()})")
            lines.append(f"  **Probes**: {probe['probes']}")
            lines.append(f"  **Exposes**: {probe['exposes']}")
            lines.append(f"  **Gramian**: `{probe['gramian']}`")
            lines.append(f"  **Kernel**: `{probe['kernel']}`\n")
        lines.append(f"**Combined**: `{obs['combined_observability']}`")
        lines.append(f"**Key Insight**: {obs['key_insight']}")
        return "\n".join(lines)

    if component in ("dynamics", "dynamical", "laws"):
        dyn = d["dynamical_laws"]
        lines = ["## Dynamical Laws\n"]
        for name, law in dyn.items():
            lines.append(f"  **{name.replace('_', ' ').title()}**: `{law}`")
        return "\n".join(lines)

    if component == "selves":
        lines = ["## Three Selves\n"]
        for name, s in d["three_selves"].items():
            lines.append(f"### {s['name']}")
            lines.append(f"  **Definition**: {s['definition']}")
            lines.append(f"  **Access**: {s['access']}\n")
        return "\n".join(lines)

    if component == "modes":
        lines = ["## Operational Modes\n"]
        for mode, desc in d["operational_modes"].items():
            lines.append(f"  **{mode.title()}**: {desc}")
        return "\n".join(lines)

    if component in ("self_reference", "self", "reference", "angel"):
        sr = d["self_reference"]
        lines = ["## Self-Reference\n"]
        lines.append(f"**Theorem**: {sr['theorem']}")
        lines.append(f"**Implication**: {sr['implication']}")
        lines.append(f"**Angel Reading**: {sr['angel_reading']}")
        return "\n".join(lines)

    return (f"Component '{component}' not recognized. "
            "Available: all, pieces, piece_N (1-12), observability, dynamics, selves, modes, self_reference")
