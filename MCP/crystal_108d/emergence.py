"""
Dimensional Emergence Path
===========================
Formalizes the 3D -> 4D -> ... -> 12D -> A+ emergence sequence.
Each phase describes HOW a lower-dimensional body weaves into its
successor, WHAT lens upgrades occur, and WHICH transport layers unlock.
"""

from ._cache import JsonCache

_EMERGENCE = JsonCache("dimensional_emergence.json")


def query_emergence(component: str = "all") -> str:
    """
    Query the dimensional emergence path.

    Components:
      - all         : Full emergence overview
      - phases      : All 7 emergence phases
      - phase:N     : Specific phase by index (1-7) or name (e.g. phase:4D->6D)
      - kernel      : Kernel embedding law and chain
      - lenses      : Cross-lens upgrade sequence by stage
      - lens:STAGE  : Lens state at a specific stage (e.g. lens:6D)
      - bodies      : Body directory mapping
    """
    data = _EMERGENCE.load()
    comp = component.strip().lower()

    if comp == "all":
        return _format_all(data)
    elif comp == "phases":
        return _format_phases(data)
    elif comp.startswith("phase:"):
        return _format_one_phase(data, comp.split(":", 1)[1])
    elif comp == "kernel":
        return _format_kernel(data)
    elif comp == "lenses":
        return _format_lenses(data)
    elif comp.startswith("lens:"):
        return _format_lens_at(data, comp.split(":", 1)[1])
    elif comp == "bodies":
        return _format_bodies(data)
    else:
        return (
            f"Unknown component '{component}'. Use: all, phases, "
            "phase:<N or name>, kernel, lenses, lens:<stage>, bodies"
        )


def emergence_status() -> str:
    """Return a status summary for the resource endpoint."""
    data = _EMERGENCE.load()
    m = data["meta"]
    return (
        "## Dimensional Emergence Path\n\n"
        f"**Path**: `{m['path']}`\n"
        f"**Governing Law**: {m['governing_law']}\n"
        f"**Kernel Embedding**: {m['kernel_embedding_law']}\n"
        f"**Phases**: {m['total_phases']}\n"
        f"**Source**: {m['source']}\n"
    )


# ── Formatters ──────────────────────────────────────────────────────

def _format_all(data: dict) -> str:
    m = data["meta"]
    lines = [
        "## Dimensional Emergence Path\n",
        f"**Path**: `{m['path']}`",
        f"**Governing Law**: {m['governing_law']}",
        f"**Kernel Embedding**: {m['kernel_embedding_law']}\n",
        "### Emergence Phases\n",
    ]
    for phase in data["emergence_phases"]:
        lines.append(
            f"  {phase['index']}. **{phase['from']} -> {phase['to']}** "
            f"({phase['name']}): {phase['mechanism']}"
        )

    lines.append("\n### Kernel Embedding Chain\n")
    for step in data["kernel_embedding"]["chain"]:
        lines.append(f"  - {step['dimension']}D: {step['embedding']}")

    lines.append(f"\n**Expansion**: {data['kernel_embedding']['expansion_factor']}")
    return "\n".join(lines)


def _format_phases(data: dict) -> str:
    lines = ["## Emergence Phases\n"]
    for phase in data["emergence_phases"]:
        lines.append(f"\n### Phase {phase['index']}: {phase['name']}")
        lines.append(f"**{phase['from']} -> {phase['to']}**\n")
        lines.append(f"- **Mechanism**: {phase['mechanism']}")
        lines.append(f"- **Lens State**: {phase['lens_state']}")
        lines.append(f"- **Body Gained**: {phase['body_gained']}")
        lines.append(f"- **Transport**: {', '.join(phase['transport_gained'])}")
        lines.append(f"- **Key Object**: {phase['key_object']}")
        if phase.get("directory"):
            lines.append(f"- **Directory**: {phase['directory']}")
        lines.append(f"\n{phase['description']}")
    return "\n".join(lines)


def _format_one_phase(data: dict, query: str) -> str:
    phases = data["emergence_phases"]
    # Try index
    try:
        idx = int(query)
        for p in phases:
            if p["index"] == idx:
                return _render_phase(p)
        return f"Phase index {idx} not found. Use 1-{len(phases)}."
    except ValueError:
        pass

    # Try name/dimension match
    q = query.upper().replace(" ", "")
    for p in phases:
        key = f"{p['from']}->{p['to']}".replace(" ", "")
        if q in key or q in p["name"].upper().replace(" ", ""):
            return _render_phase(p)

    return f"Phase '{query}' not found. Use index 1-7 or dimension pair like '4D->6D'."


def _render_phase(phase: dict) -> str:
    lines = [
        f"## Phase {phase['index']}: {phase['name']}",
        f"**{phase['from']} -> {phase['to']}**\n",
        f"**Mechanism**: {phase['mechanism']}",
        f"**Lens State**: {phase['lens_state']}",
        f"**Body Gained**: {phase['body_gained']}",
        f"**Transport Gained**: {', '.join(phase['transport_gained'])}",
        f"**Key Object**: {phase['key_object']}",
    ]
    if phase.get("directory"):
        lines.append(f"**Directory**: {phase['directory']}")
    lines.append(f"\n{phase['description']}")
    return "\n".join(lines)


def _format_kernel(data: dict) -> str:
    ke = data["kernel_embedding"]
    lines = [
        "## Kernel Embedding Law\n",
        f"**Law**: {ke['law']}",
        f"**Expansion Factor**: {ke['expansion_factor']}\n",
        "### Embedding Chain\n",
    ]
    for step in ke["chain"]:
        lines.append(f"  - **{step['dimension']}D**: {step['embedding']}")
    return "\n".join(lines)


def _format_lenses(data: dict) -> str:
    lines = ["## Cross-Lens Upgrade Sequence\n"]
    lines.append("| Stage | Square | Flower | Cloud | Fractal | Combined |")
    lines.append("|-------|--------|--------|-------|---------|----------|")
    for row in data["cross_lens_upgrade_sequence"]:
        lines.append(
            f"| {row['stage']} | {row['square']} | {row['flower']} | "
            f"{row['cloud']} | {row['fractal']} | {row['combined']} |"
        )
    return "\n".join(lines)


def _format_lens_at(data: dict, stage: str) -> str:
    stage_upper = stage.upper()
    for row in data["cross_lens_upgrade_sequence"]:
        if row["stage"].upper() == stage_upper:
            return (
                f"## Lens State at {row['stage']}\n\n"
                f"- **Square**: {row['square']}\n"
                f"- **Flower**: {row['flower']}\n"
                f"- **Cloud**: {row['cloud']}\n"
                f"- **Fractal**: {row['fractal']}\n"
                f"- **Combined**: {row['combined']}"
            )
    stages = [r["stage"] for r in data["cross_lens_upgrade_sequence"]]
    return f"Stage '{stage}' not found. Available: {', '.join(stages)}"


def _format_bodies(data: dict) -> str:
    m = data["meta"]
    lines = [
        "## Body Directories\n",
        "Local nervous system directories containing dimensional body documents:\n",
    ]
    for dim, dirname in m["body_directories"].items():
        lines.append(f"- **{dim}**: `ACTIVE_NERVOUS_SYSTEM/{dirname}/`")
    lines.append(
        "\nUse `read_dimensional_body(dimension, document)` to explore these."
    )
    return "\n".join(lines)
