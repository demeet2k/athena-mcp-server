"""
Inverse Crystal Octave — 14-Stage Lift + A+ Crown Transform
=============================================================
The full 4D to 108D nested octave lift through weaves of 3/5/7/9,
plus the 6-step A+ crown transform.
"""

from ._cache import JsonCache

_OCTAVE = JsonCache("inverse_crystal_octave.json")


def query_octave_stage(stage: str = "all") -> str:
    """
    Query the octave lift stages.

    Stage:
      - all     : All 14 stages overview
      - S00-S13 : Specific stage by ID (e.g. 'S03' for triadic Mobius lift)
      - 6D, 8D, etc. : Find the stage that reaches this dimension
      - weaves  : Only stages with weave operators (S03/S05/S07/S09)
      - controls: Only odd control shells (S04/S06/S08)
    """
    data = _OCTAVE.load()
    s = stage.strip().upper()

    if s == "ALL":
        return _format_stages_all(data)
    elif s == "WEAVES":
        return _format_weave_stages(data)
    elif s == "CONTROLS":
        return _format_control_stages(data)
    elif s.startswith("S") and s[1:].isdigit():
        return _format_one_stage(data, s)
    else:
        # Try dimension match
        return _format_by_dimension(data, stage)


def query_crown_transform(step: str = "all") -> str:
    """
    Query the A+ crown transform.

    Step:
      - all         : Full 6-step crown transform
      - 1-6         : Specific step by number
      - ZeroTunnel, PhaseWeave, PillarBind, ReverseCanopy, AtlasBind, CrownLock
      - live        : The live crystal formula
      - traditions  : 36-shell tradition map
    """
    data = _OCTAVE.load()
    s = step.strip().lower()

    if s == "all":
        return _format_crown_all(data)
    elif s == "live":
        return _format_live(data)
    elif s == "traditions":
        return _format_traditions(data)
    elif s.isdigit():
        return _format_crown_step(data, int(s))
    else:
        # Try name match
        return _format_crown_by_name(data, s)


def inverse_octave_status() -> str:
    """Return a status summary for the resource endpoint."""
    data = _OCTAVE.load()
    m = data["meta"]
    return (
        "## Inverse Crystal Octave\n\n"
        f"**Stages**: {m['total_stages']} (S00-S13)\n"
        f"**Crown Steps**: {m['crown_steps']}\n"
        f"**Weaves**: 3/5/7/9 (closures Z12/Z20/Z28/Z36)\n"
        f"**Live Crystal**: `{data['live_crystal']['formula']}`\n"
        f"**Master Clock**: {data['live_crystal']['master_clock']}\n"
    )


# -- Stage formatters ------------------------------------------------------

def _format_stages_all(data: dict) -> str:
    lines = ["## 14-Stage Octave Lift (4D -> 108D)\n"]
    for stage in data["octave_stages"]:
        weave = f" [Weave {stage['weave']}]" if stage.get("weave") else ""
        closure = f" (closure {stage['local_closure']})" if stage.get("local_closure") else ""
        lines.append(
            f"- **{stage['id']}** {stage['from']} -> {stage['to']}: "
            f"{stage['name']}{weave}{closure}"
        )
    return "\n".join(lines)


def _format_one_stage(data: dict, stage_id: str) -> str:
    for stage in data["octave_stages"]:
        if stage["id"].upper() == stage_id:
            return _render_stage(stage)
    return f"Stage '{stage_id}' not found. Use S00-S13."


def _format_by_dimension(data: dict, dim: str) -> str:
    dim_upper = dim.strip().upper().replace(" ", "")
    for stage in data["octave_stages"]:
        to = stage["to"].upper().replace(" ", "").replace("_", "")
        if dim_upper in to or dim_upper == stage["from"].upper():
            return _render_stage(stage)
    ids = [s["id"] for s in data["octave_stages"]]
    return f"Dimension '{dim}' not found. Available stages: {', '.join(ids)}"


def _format_weave_stages(data: dict) -> str:
    lines = ["## Weave Stages\n"]
    for stage in data["octave_stages"]:
        if stage.get("weave"):
            lines.append(f"\n### {stage['id']}: {stage['name']} (Weave {stage['weave']})")
            lines.append(f"**{stage['from']} -> {stage['to']}**")
            lines.append(f"**Closure**: {stage.get('local_closure', 'N/A')}")
            lines.append(f"**Mechanism**: {stage['mechanism']}")
            if "detail" in stage:
                for key, val in stage["detail"].items():
                    if isinstance(val, list):
                        lines.append(f"**{key}**: {', '.join(str(v) for v in val)}")
                    elif isinstance(val, dict):
                        for k2, v2 in val.items():
                            lines.append(f"  - {k2}: {v2}")
                    else:
                        lines.append(f"**{key}**: {val}")
    return "\n".join(lines)


def _format_control_stages(data: dict) -> str:
    lines = ["## Odd Control Shells\n"]
    for stage in data["octave_stages"]:
        if stage.get("control"):
            lines.append(f"\n### {stage['id']}: {stage['name']}")
            lines.append(f"**{stage['from']} -> {stage['to']}**")
            lines.append(f"**Control**: {stage['control']}")
            lines.append(f"**Mechanism**: {stage['mechanism']}")
    return "\n".join(lines)


def _render_stage(stage: dict) -> str:
    lines = [
        f"## {stage['id']}: {stage['name']}",
        f"**{stage['from']} -> {stage['to']}**\n",
        f"**Mechanism**: {stage['mechanism']}",
    ]
    if stage.get("weave"):
        lines.append(f"**Weave**: {stage['weave']}")
    if stage.get("local_closure"):
        lines.append(f"**Local Closure**: {stage['local_closure']}")
    if stage.get("control"):
        lines.append(f"**Control**: {stage['control']}")
    if stage.get("note"):
        lines.append(f"**Note**: {stage['note']}")
    if stage.get("content"):
        lines.append(f"\n**Content**: {stage['content']}")
    if "detail" in stage:
        lines.append("\n### Detail\n")
        for key, val in stage["detail"].items():
            if isinstance(val, list):
                if val and isinstance(val[0], dict):
                    for item in val:
                        name = item.get("name", "")
                        maps_to = item.get("maps_to", "")
                        lines.append(f"  - {name} -> {maps_to}")
                elif val and isinstance(val[0], list):
                    for row in val:
                        lines.append(f"  {' | '.join(str(c) for c in row)}")
                else:
                    lines.append(f"**{key}**: {', '.join(str(v) for v in val)}")
            else:
                lines.append(f"**{key}**: {val}")
    return "\n".join(lines)


# -- Crown formatters ------------------------------------------------------

def _format_crown_all(data: dict) -> str:
    ct = data["crown_transform"]
    lines = [
        f"## {ct['name']}\n",
        f"**Formula**: `{ct['formula']}`\n",
    ]
    for step in ct["steps"]:
        lines.append(f"### Step {step['step']}: {step['name']} ({step['symbol']})")
        lines.append(f"{step['effect']}")
        if "examples" in step:
            for ex in step["examples"]:
                lines.append(f"  - {ex}")
        lines.append("")
    return "\n".join(lines)


def _format_crown_step(data: dict, num: int) -> str:
    for step in data["crown_transform"]["steps"]:
        if step["step"] == num:
            lines = [
                f"## Step {step['step']}: {step['name']}",
                f"**Symbol**: `{step['symbol']}`\n",
                f"{step['effect']}",
            ]
            if "examples" in step:
                lines.append("\n### Examples\n")
                for ex in step["examples"]:
                    lines.append(f"- {ex}")
            return "\n".join(lines)
    return f"Step {num} not found. Use 1-6."


def _format_crown_by_name(data: dict, name: str) -> str:
    name_lower = name.lower()
    for step in data["crown_transform"]["steps"]:
        if name_lower in step["name"].lower():
            return _format_crown_step(data, step["step"])
    names = [s["name"] for s in data["crown_transform"]["steps"]]
    return f"Step '{name}' not found. Available: {', '.join(names)}"


def _format_live(data: dict) -> str:
    lc = data["live_crystal"]
    lines = [
        "## Live Crystal\n",
        f"**Formula**: `{lc['formula']}`",
        f"**Master Clock**: {lc['master_clock']}",
        f"**Convergence**: {lc['convergence']}\n",
        f"### Even Stack (Body)\n",
        lc["even_stack"],
        "\n### Odd Wheels (Steering)\n",
    ]
    for key, wheel in lc["odd_wheels"].items():
        elems = ", ".join(wheel["elements"])
        lines.append(f"- **{key}** [{elems}]: {wheel['function']}")
    return "\n".join(lines)


def _format_traditions(data: dict) -> str:
    tm = data["tradition_map"]
    lines = ["## 36-Shell Tradition Map\n"]
    for phase_key in ["su_shells", "me_shells", "sa_shells"]:
        phase = tm[phase_key]
        lines.append(f"### Shells {phase['range']} ({phase['type']})")
        for t in phase["traditions"]:
            lines.append(f"  - {t}")
        lines.append("")
    return "\n".join(lines)
