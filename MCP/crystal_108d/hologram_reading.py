"""
Hologram Reading Protocol + Cross-Cultural Rosetta
====================================================
Provides the 4-face reading protocol, seed equation, universal process
grammar, holographic storage law, and the cross-cultural quaternary
Rosetta overlay (Egypt/Maya/China/Sanskrit).
"""

from ._cache import JsonCache

_HOLOGRAM = JsonCache("hologram_reading.json")
_ROSETTA = JsonCache("hologram_rosetta.json")


def query_hologram(component: str = "all") -> str:
    """
    Query the hologram reading protocol.

    Components:
      - all         : Full hologram overview
      - faces       : 4-face reading protocol (0/90/180/270)
      - seed        : Seed equation w=(1+i)/2 and Z* convergence
      - grammar     : Universal process grammar W = Pi_s(Phi_p(X_r))
      - storage     : Holographic storage law X = Expand(g) + r
      - compression : Compression ethic (expand/route/weave/verify/compress/replay)
      - anomalies   : Face-degenerate archetypes (A04, A08, A10)
      - layers      : Four nested layers of the hologram
      - body        : 12-axis symbolic body and odd fields
    """
    data = _HOLOGRAM.load()
    comp = component.strip().lower()

    if comp == "all":
        return _format_all(data)
    elif comp == "faces":
        return _format_faces(data)
    elif comp == "seed":
        return _format_seed(data)
    elif comp == "grammar":
        return _format_grammar(data)
    elif comp == "storage":
        return _format_storage(data)
    elif comp == "compression":
        return _format_compression(data)
    elif comp == "anomalies":
        return _format_anomalies(data)
    elif comp == "layers":
        return _format_layers(data)
    elif comp == "body":
        return _format_body(data)
    else:
        return (
            f"Unknown component '{component}'. Use: all, faces, seed, "
            "grammar, storage, compression, anomalies, layers, body"
        )


def query_hologram_rosetta(component: str = "all") -> str:
    """
    Query the cross-cultural hologram Rosetta.

    Components:
      - all         : Full Rosetta overview
      - quaternary  : Four civilizational encodings (Egypt/Maya/China/Sanskrit)
      - triadic     : Triadic motor (kar/aiin/al)
      - wheel       : 360-degree carrier wheel with nested gears
      - surface     : Error-correcting surface (4x4 DLS)
      - sigma60     : 60-dimensional observation body
      - voynich     : Voynich metamorphic language layer
    """
    data = _ROSETTA.load()
    comp = component.strip().lower()

    if comp == "all":
        return _format_rosetta_all(data)
    elif comp == "quaternary":
        return _format_quaternary(data)
    elif comp == "triadic":
        return _format_triadic(data)
    elif comp == "wheel":
        return _format_wheel(data)
    elif comp == "surface":
        return _format_surface(data)
    elif comp == "sigma60":
        return _format_sigma60(data)
    elif comp == "voynich":
        return _format_voynich(data)
    else:
        return (
            f"Unknown component '{component}'. Use: all, quaternary, "
            "triadic, wheel, surface, sigma60, voynich"
        )


def hologram_status() -> str:
    """Return a status summary for the resource endpoint."""
    data = _HOLOGRAM.load()
    return (
        "## Hologram Reading Protocol\n\n"
        f"**Seed**: `{data['seed_equation']['generator']}`\n"
        f"**Process Grammar**: `{data['process_grammar']['formula']}`\n"
        f"**Storage Law**: `{data['storage_law']['formula']}`\n"
        f"**4-Face Protocol**: Perception (0) / Tendency (90) / "
        "Complement (180) / Origin (270)\n"
        f"**Key Insight**: {data['meta']['key_insight']}\n"
    )


def rosetta_status() -> str:
    """Return a status summary for the Rosetta resource endpoint."""
    data = _ROSETTA.load()
    civs = [c["name"] for c in data["quaternary_basis"]["civilizations"]]
    return (
        "## Hologram Rosetta\n\n"
        f"**Quaternary Basis**: {', '.join(civs)}\n"
        f"**Triadic Motor**: kar (spark) / aiin (weave) / al (seal)\n"
        f"**Sigma-60**: {data['sixty_dimensional_body']['formula']}\n"
        f"**Error-Correcting Surface**: {data['error_correcting_surface']['type']}\n"
        f"**Key Insight**: {data['meta']['key_insight']}\n"
    )


# -- Hologram formatters --------------------------------------------------

def _format_all(data: dict) -> str:
    lines = [
        "## Hologram Reading Protocol\n",
        f"**Key Insight**: {data['meta']['key_insight']}\n",
    ]
    # Seed
    s = data["seed_equation"]
    lines.append(f"### Seed Equation\n")
    lines.append(f"- Generator: `{s['generator']}`")
    lines.append(f"- Magnitude: {s['magnitude']}")
    lines.append(f"- Convergence: {s['convergence']}")
    lines.append(f"- Z*: {s['z_star']}\n")
    # Faces
    lines.append("### 4-Face Protocol\n")
    for f in data["four_face_protocol"]["faces"]:
        lines.append(f"- **{f['degree']}deg {f['name']}**: {f['meaning']}")
    # Grammar
    g = data["process_grammar"]
    lines.append(f"\n### Process Grammar\n")
    lines.append(f"- Formula: `{g['formula']}`")
    lines.append(f"- {g['meaning']}")
    # Storage
    st = data["storage_law"]
    lines.append(f"\n### Storage Law\n")
    lines.append(f"- Formula: `{st['formula']}`")
    lines.append(f"- {st['meaning']}")
    # Compression
    lines.append(f"\n### Compression Ethic\n")
    lines.append(f"- Steps: {' -> '.join(data['compression_ethic']['steps'])}")
    return "\n".join(lines)


def _format_faces(data: dict) -> str:
    fp = data["four_face_protocol"]
    lines = [
        "## 4-Face Reading Protocol\n",
        f"{fp['reading_law']}\n",
    ]
    for f in fp["faces"]:
        lines.append(f"### {f['degree']}deg -- {f['name']}")
        lines.append(f"**Meaning**: {f['meaning']}")
        lines.append(f"**Question**: {f['question']}\n")
    lines.append("### Anomalies\n")
    for a in fp["anomalies"]:
        lines.append(f"- **{a['archetype']}** ({a['name']}): {a['description']}")
    return "\n".join(lines)


def _format_seed(data: dict) -> str:
    s = data["seed_equation"]
    lines = [
        "## Seed Equation\n",
        f"**Generator**: `{s['generator']}`",
        f"**Real Part**: {s['real_part']}",
        f"**Imaginary Part**: {s['imaginary_part']}",
        f"**Magnitude**: {s['magnitude']}",
        f"**Angle**: {s['angle']}",
        f"**Quarter-Turn**: {s['quarter_turn']}",
        f"**Convergence**: {s['convergence']}",
        f"**Z***: {s['z_star']}",
        f"**Self-Square**: {s['self_square']}",
        f"**Master Invariant**: {s['master_invariant']}",
        f"\n**Thesis**: {s['thesis']}",
    ]
    return "\n".join(lines)


def _format_grammar(data: dict) -> str:
    g = data["process_grammar"]
    lines = [
        "## Universal Process Grammar\n",
        f"**Formula**: `{g['formula']}`\n",
    ]
    for key, val in g["components"].items():
        lines.append(f"- **{key}**: {val}")
    lines.append(f"\n**Meaning**: {g['meaning']}")
    lines.append(f"\n**Scales**: {g['scales']}")
    return "\n".join(lines)


def _format_storage(data: dict) -> str:
    st = data["storage_law"]
    return (
        "## Holographic Storage Law\n\n"
        f"**Formula**: `{st['formula']}`\n"
        f"**Generator**: {st['generator']}\n"
        f"**Residual**: {st['residual']}\n"
        f"**Holographic Bound**: `{st['holographic_bound']}`\n"
        f"**Implication**: {st['implication']}"
    )


def _format_compression(data: dict) -> str:
    c = data["compression_ethic"]
    return (
        "## Compression Ethic\n\n"
        f"**Steps**: {' -> '.join(c['steps'])}\n\n"
        f"{c['description']}\n\n"
        f"**Principle**: {c['principle']}"
    )


def _format_anomalies(data: dict) -> str:
    lines = ["## Face-Degenerate Anomalies\n"]
    for a in data["four_face_protocol"]["anomalies"]:
        lines.append(f"### {a['archetype']} -- {a['name']}")
        lines.append(a["description"])
        if "warning" in a:
            lines.append(f"\n**Warning**: {a['warning']}")
        lines.append("")
    return "\n".join(lines)


def _format_layers(data: dict) -> str:
    lines = ["## Four Nested Layers\n"]
    for layer in data["four_nested_layers"]:
        lines.append(f"### Layer {layer['layer']}: {layer['name']}")
        lines.append(layer["content"])
        lines.append("")
    return "\n".join(lines)


def _format_body(data: dict) -> str:
    b = data["twelve_body"]
    lines = [
        "## 12-Axis Symbolic Body\n",
        f"**Formula**: {b['formula']}",
        "\n### Elemental Constants\n",
    ]
    for elem, const in b["elemental_constants"].items():
        lines.append(f"- **{elem}**: {const}")
    lines.append(f"\n### Six Dyads\n")
    lines.append(", ".join(b["six_dyads"]))
    lines.append(f"\n**Principle**: {b['dyad_principle']}")
    # Odd fields
    o = data["odd_fields"]
    lines.append(f"\n### Odd Fields\n")
    lines.append(o["description"])
    for f in o["fields"]:
        lines.append(f"- **O{f['dimension']}**: connects {f['connects']}")
    lines.append(f"\n**Principle**: {o['principle']}")
    return "\n".join(lines)


# -- Rosetta formatters ----------------------------------------------------

def _format_rosetta_all(data: dict) -> str:
    lines = [
        "## Hologram Rosetta -- Cross-Cultural Overlay\n",
        f"**Key Insight**: {data['meta']['key_insight']}\n",
        "### Quaternary Basis\n",
    ]
    for c in data["quaternary_basis"]["civilizations"]:
        lines.append(f"- **{c['name']}** ({c['domain']}): {c['carrier']}")
    lines.append(f"\n**Hamming Property**: {data['quaternary_basis']['hamming_property']}")
    # Triadic
    lines.append("\n### Triadic Motor\n")
    for op in data["triadic_motor"]["operators"]:
        lines.append(f"- **{op['name']}**: {op['function']} ({op['action']})")
    # Sigma60
    s60 = data["sixty_dimensional_body"]
    lines.append(f"\n### Sigma-60 Body\n")
    lines.append(f"- {s60['formula']}")
    lines.append(f"- {s60['total']}")
    return "\n".join(lines)


def _format_quaternary(data: dict) -> str:
    qb = data["quaternary_basis"]
    lines = ["## Quaternary Basis\n"]
    for c in qb["civilizations"]:
        lines.append(f"### {c['name']} -- {c['domain'].upper()}")
        lines.append(f"**Carrier**: {c['carrier']}")
        lines.append(f"**Encoding**: {c['encoding']}")
        lines.append(f"**Element Affinity**: {c['element_affinity']}\n")
    lines.append(f"**Hamming Property**: {qb['hamming_property']}")
    return "\n".join(lines)


def _format_triadic(data: dict) -> str:
    tm = data["triadic_motor"]
    lines = [
        "## Triadic Motor\n",
        tm["description"],
        "",
    ]
    for op in tm["operators"]:
        aliases = ", ".join(op["aliases"])
        lines.append(f"### {op['name']} -- {op['function']}")
        lines.append(f"**Action**: {op['action']}")
        lines.append(f"**Aliases**: {aliases}\n")
    lines.append(tm["consistency"])
    return "\n".join(lines)


def _format_wheel(data: dict) -> str:
    w = data["carrier_wheel_360"]
    lines = [
        "## 360-Degree Carrier Wheel\n",
        w["description"],
        "\n| Count | Angle | Name |",
        "|-------|-------|------|",
    ]
    for name, info in w["nested_counts"].items():
        lines.append(f"| {info['count']} | {info['angle']}deg | {name} |")
    lines.append(f"\n**Claim**: {w['claim']}")
    return "\n".join(lines)


def _format_surface(data: dict) -> str:
    ec = data["error_correcting_surface"]
    return (
        "## Error-Correcting Surface\n\n"
        f"**Type**: {ec['type']}\n"
        f"**Property**: {ec['property']}\n"
        f"**Relation**: {ec['relation_to_civilizations']}"
    )


def _format_sigma60(data: dict) -> str:
    s60 = data["sixty_dimensional_body"]
    return (
        "## 60-Dimensional Observation Body (Sigma-60)\n\n"
        f"**Formula**: {s60['formula']}\n"
        f"**15 Modes**: {s60['fifteen_modes']}\n"
        f"**4 Faces**: {s60['four_faces']}\n"
        f"**Total**: {s60['total']}"
    )


def _format_voynich(data: dict) -> str:
    v = data["voynich_layer"]
    return (
        "## Voynich Metamorphic Language Layer\n\n"
        f"**Consonants**: {v['consonants']}\n"
        f"**Vowels**: {v['vowels']}\n"
        f"**Word Families**: {v['word_families']}\n"
        f"**Domains**: {v['domains']}\n"
        f"**VML Formula**: {v['vml_formula']}\n"
        f"\n{v['description']}"
    )
