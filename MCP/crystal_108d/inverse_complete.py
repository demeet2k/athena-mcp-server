"""
Inverse Crystal Complete — Projection Stack + Weave Operators
==============================================================
The full round-trip projection stack from 3D seed to 108D A+ crown
and back, plus the three weave operators (W3/W5/W7), three control
shells, and the 20-step regeneration protocol.
"""

from ._cache import JsonCache

_COMPLETE = JsonCache("inverse_crystal_complete.json")


def query_projection_stack(direction: str = "all") -> str:
    """
    Query the full projection stack.

    Direction:
      - all    : Full round-trip (up + down)
      - up     : 3D -> 108D -> A+ (expansion)
      - down   : A+ -> 3D (compression)
      - regen  : 20-step regeneration protocol
      - terminal: Terminal statement (seed = stone = generator = crystal)
    """
    data = _COMPLETE.load()
    d = direction.strip().lower()

    if d == "all":
        return _format_stack_all(data)
    elif d == "up":
        return _format_stack_up(data)
    elif d == "down":
        return _format_stack_down(data)
    elif d == "regen":
        return _format_regen(data)
    elif d == "terminal":
        return _format_terminal(data)
    else:
        return (
            f"Unknown direction '{direction}'. Use: all, up, down, regen, terminal"
        )


def query_weave_operator(weave: str = "all") -> str:
    """
    Query weave operators and control shells.

    Weave:
      - all      : All 3 weave operators + master clock
      - W3       : Triadic wheel (Su/Me/Sa)
      - W5       : Pentadic wheel (Hold/Lift/Traverse/Twist/Compress)
      - W7       : Heptadic wheel (Seed/Ignite/Translate/Bridge/Weave/Seal/Return)
      - controls : 3 control shells (C7/C9/C11)
      - clock    : Master clock Z420
    """
    data = _COMPLETE.load()
    w = weave.strip().upper()

    if w == "ALL":
        return _format_weaves_all(data)
    elif w in ("W3", "W5", "W7"):
        return _format_one_weave(data, w)
    elif w == "CONTROLS":
        return _format_controls(data)
    elif w == "CLOCK":
        return _format_clock(data)
    else:
        return (
            f"Unknown weave '{weave}'. Use: all, W3, W5, W7, controls, clock"
        )


def inverse_complete_status() -> str:
    """Return a status summary for the resource endpoint."""
    data = _COMPLETE.load()
    stack = data["projection_stack"]
    return (
        "## Inverse Crystal Complete\n\n"
        f"**Projection Stack**: {len(stack['up'])} levels up, "
        f"{len(stack['down'])} levels down\n"
        f"**Round-Trip Law**: {stack['round_trip_law']}\n"
        f"**Weave Operators**: W3 (period 3), W5 (period 5), W7 (period 7)\n"
        f"**Master Clock**: Z420 = lcm(3,4,5,7)\n"
        f"**Regeneration**: {data['regeneration_protocol']['description'][:80]}...\n"
    )


# -- Stack formatters ------------------------------------------------------

def _format_stack_all(data: dict) -> str:
    stack = data["projection_stack"]
    lines = [
        "## Full Projection Stack (Round Trip)\n",
        f"**Law**: {stack['round_trip_law']}\n",
        "### Expansion (3D -> A+)\n",
    ]
    for level in stack["up"]:
        op = f" via {level['operation']}" if level["operation"] else ""
        lines.append(f"- **{level['level']}** ({level['dimension']}): {level['description']}{op}")
    lines.append("\n### Compression (A+ -> 3D)\n")
    for level in stack["down"]:
        op = f" via {level['operation']}" if level["operation"] else ""
        lines.append(f"- **{level['level']}** ({level['dimension']}): {level['description']}{op}")
    return "\n".join(lines)


def _format_stack_up(data: dict) -> str:
    lines = ["## Expansion: 3D -> 108D -> A+\n"]
    for level in data["projection_stack"]["up"]:
        op = f"\n  Operation: `{level['operation']}`" if level["operation"] else ""
        lines.append(f"### {level['level']} ({level['dimension']})")
        lines.append(f"{level['description']}{op}\n")
    return "\n".join(lines)


def _format_stack_down(data: dict) -> str:
    lines = ["## Compression: A+ -> 3D\n"]
    for level in data["projection_stack"]["down"]:
        op = f"\n  Operation: `{level['operation']}`" if level["operation"] else ""
        lines.append(f"### {level['level']} ({level['dimension']})")
        lines.append(f"{level['description']}{op}\n")
    lines.append(data["projection_stack"]["round_trip_law"])
    return "\n".join(lines)


def _format_regen(data: dict) -> str:
    rp = data["regeneration_protocol"]
    lines = [
        "## 20-Step Regeneration Protocol\n",
        f"{rp['description']}\n",
    ]
    for i, step in enumerate(rp["steps"], 1):
        lines.append(f"{i:>2}. {step}")
    return "\n".join(lines)


def _format_terminal(data: dict) -> str:
    ts = data["terminal_statement"]
    return (
        "## Terminal Statement\n\n"
        f"**Seed = Stone**: {ts['seed_is_stone']}\n\n"
        f"**Self-Reference**: {ts['self_reference']}\n\n"
        f"**In 14 symbols**: `{ts['in_fourteen_symbols']}`\n\n"
        f"**In 1 symbol**: `{ts['in_one_symbol']}`\n\n"
        f"**In 0 symbols**: {ts['in_zero_symbols']}"
    )


# -- Weave formatters ------------------------------------------------------

def _format_weaves_all(data: dict) -> str:
    lines = ["## Weave Operators\n"]
    for key in ("W3", "W5", "W7"):
        w = data["weave_operators"][key]
        elems = ", ".join(e["name"] for e in w["elements"])
        lines.append(f"### {w['name']} (period {w['period']})")
        lines.append(f"**Elements**: {elems}")
        lines.append(f"**Function**: {w['function']}")
        lines.append(f"**Local Closure**: {w['local_closure']}")
        lines.append(f"**Clock Period**: {w['clock_period']}\n")
    mc = data["weave_operators"]["master_clock"]
    lines.append(f"### Master Clock")
    lines.append(f"**Period**: {mc['period']} ({mc['formula']})")
    lines.append(f"**Meaning**: {mc['meaning']}")
    lines.append(f"**Supercycle**: {mc['supercycle']}")
    return "\n".join(lines)


def _format_one_weave(data: dict, key: str) -> str:
    w = data["weave_operators"][key]
    lines = [
        f"## {w['name']} (period {w['period']})\n",
        f"**Function**: {w['function']}",
        f"**Local Closure**: {w['local_closure']}",
        f"**Clock Period**: {w['clock_period']}\n",
        "### Elements\n",
    ]
    for e in w["elements"]:
        lines.append(f"- **{e['name']}**: {e['function']}")
    return "\n".join(lines)


def _format_controls(data: dict) -> str:
    lines = ["## Control Shells\n"]
    for key, shell in data["control_shells"].items():
        prime = " (PRIME)" if shell.get("prime") else ""
        lines.append(f"### {key} ({shell['dimension']}D){prime}")
        lines.append(f"**Governs**: {shell['governs']}")
        lines.append(f"**Period**: {shell['period']}")
        if "note" in shell:
            lines.append(f"**Note**: {shell['note']}")
        lines.append(f"**Installs At**: {shell['installs_at']}\n")
    return "\n".join(lines)


def _format_clock(data: dict) -> str:
    mc = data["weave_operators"]["master_clock"]
    lines = [
        "## Master Clock\n",
        f"**Period**: {mc['period']}",
        f"**Formula**: {mc['formula']}",
        f"**Meaning**: {mc['meaning']}",
        f"**Supercycle**: {mc['supercycle']}",
    ]
    # Add individual wheel periods
    for key in ("W3", "W5", "W7"):
        w = data["weave_operators"][key]
        lines.append(f"\n- **{key}**: period {w['period']}, clock period {w['clock_period']}")
    return "\n".join(lines)
