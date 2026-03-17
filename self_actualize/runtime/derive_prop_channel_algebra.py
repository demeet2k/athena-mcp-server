from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
TEMPLE_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "ATHENA TEMPLE"
RECEIPTS_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "receipts"

OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "prop_channel_algebra.json"
OUTPUT_MARKDOWN_PATH = TEMPLE_ROOT / "CRYSTALS" / "02_PROP_CHANNEL_ALGEBRA.md"
OUTPUT_RECEIPT_PATH = RECEIPTS_ROOT / "2026-03-09_prop_channel_algebra.md"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_prop_channel_algebra"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CountProfile:
    count: str
    physical_pattern: str
    channel_mode: str
    use_case: str


@dataclass
class PropChannelSpec:
    prop: str
    channel_type: str
    state_model: str
    bandwidth: float
    error_mode: str
    error_impact: str
    recovery_cost: str
    definition_fields: list[str] = field(default_factory=list)
    physical_read: str = ""
    communication_read: str = ""
    use_cases: list[str] = field(default_factory=list)
    count_profiles: list[CountProfile] = field(default_factory=list)
    formulas: list[str] = field(default_factory=list)


@dataclass
class VTGModeSpec:
    name: str
    trace: str
    protocol: str
    use_when: str
    parameter: str


@dataclass
class PropChannelAlgebra:
    generated_at: str
    derivation_command: str
    chapter_name: str
    station: str
    chapter_address: str
    prerequisites: list[str]
    deliverables: list[str]
    forward_references: list[str]
    bandwidth_progression: dict[str, float]
    props: list[PropChannelSpec]
    vtg_modes: list[VTGModeSpec]
    selection_function: str
    heuristics: list[str]


def build_props() -> list[PropChannelSpec]:
    return [
        PropChannelSpec(
            prop="ball",
            channel_type="stateless_data_packet",
            state_model="stateless",
            bandwidth=1.0,
            error_mode="drop",
            error_impact="local",
            recovery_cost="1-2 beats",
            definition_fields=["payload", "position", "timing", "weight"],
            physical_read="caught by position and timing alone",
            communication_read="self-contained message requiring no sender-state knowledge",
            use_cases=[
                "factual query",
                "lookup request",
                "formatted data transfer",
                "routine one-shot packet",
            ],
            count_profiles=[
                CountProfile("1", "single toss-and-catch", "one-to-one query", "quick factual question"),
                CountProfile("2", "paired exchange", "comparison lane", "A/B testing or cross-validation"),
                CountProfile("3", "cascade / fountain / shower", "full three-pod circulation", "standard multi-agent round-robin"),
                CountProfile("4+", "scaled pattern", "full pod-scale data routing", "high-volume stateless coordination"),
            ],
            formulas=[
                "B = (payload, position, timing, weight)",
                "Accuracy(B) = A_height * A_lateral * A_temporal",
            ],
        ),
        PropChannelSpec(
            prop="club",
            channel_type="stateful_packet",
            state_model="stateful_spin_orientation_grip",
            bandwidth=1.618,
            error_mode="knob_catch",
            error_impact="propagating",
            recovery_cost="3-5 beats",
            definition_fields=["payload", "state", "spin", "orientation", "grip"],
            physical_read="clean catch depends on spin count, handle direction, and grip alignment",
            communication_read="work-in-progress or context-bearing handoff that requires state alignment",
            use_cases=[
                "analysis handoff",
                "work-in-progress transfer",
                "partial D/Q/I bundle",
                "verification pipeline stage transfer",
            ],
            count_profiles=[
                CountProfile("1", "single club manipulation", "one stateful handoff", "passing one analysis between two agents"),
                CountProfile("2", "double club passing", "dual stateful streams", "bidirectional handoff"),
                CountProfile("3", "club cascade / fountain", "full three-pod stateful loop", "round-robin WIP coordination"),
                CountProfile("4+", "multi-club patterns", "full pod-scale state routing", "large stateful coordination"),
            ],
            formulas=[
                "C = (payload, state, spin, orientation, grip)",
                "spin(A->B) + spin(B->C) <= 3",
            ],
        ),
        PropChannelSpec(
            prop="ring",
            channel_type="framing_constraint",
            state_model="aperture_plane_diameter",
            bandwidth=0.618,
            error_mode="snag",
            error_impact="blocking",
            recovery_cost="2-3 beats",
            definition_fields=["aperture", "plane", "diameter", "rigidity"],
            physical_read="defines a boundary or aperture rather than carrying mass-state",
            communication_read="schema, template, or verification frame that content must pass through",
            use_cases=[
                "seed format",
                "verification contract",
                "schema or template",
                "multi-constraint framing",
            ],
            count_profiles=[
                CountProfile("1", "single hoop", "one framing constraint", "single schema or template"),
                CountProfile("2", "double hoop", "dual constraint stack", "must satisfy two independent schemas"),
                CountProfile("3", "triple hoop", "triple constraint stack", "high-rigor output gate"),
                CountProfile("4+", "over-constrained stack", "usually counterproductive", "decompose instead of stacking"),
            ],
            formulas=[
                "R = (aperture, plane, diameter, rigidity)",
            ],
        ),
        PropChannelSpec(
            prop="poi",
            channel_type="continuous_monitoring_channel",
            state_model="orbit_plane_trace",
            bandwidth=0.618,
            error_mode="tangle",
            error_impact="narrowing",
            recovery_cost="3-4 beats",
            definition_fields=["orbit_radius", "plane", "frequency", "trace_pattern"],
            physical_read="continuous tethered orbit tracing geometry through space",
            communication_read="always-on background monitoring with adjustable monitoring geometry",
            use_cases=[
                "long-running task monitoring",
                "convergence tracking",
                "invariance testing",
                "dual-agent correlated monitoring",
            ],
            count_profiles=[
                CountProfile("1", "single poi", "one monitoring channel", "minimum background awareness"),
                CountProfile("2", "double poi", "dual monitoring channel", "standard dual monitoring"),
                CountProfile("3", "triple poi", "three monitoring channels", "pod-scale background monitoring"),
                CountProfile("4", "quad poi", "monitoring-only mode", "all limbs dedicated to monitoring"),
            ],
            formulas=[
                "P = (orbit_radius, plane, frequency, trace_pattern)",
            ],
        ),
        PropChannelSpec(
            prop="staff",
            channel_type="broadcast_override_channel",
            state_model="full_pod_broadcast",
            bandwidth=2.618,
            error_mode="collision",
            error_impact="global",
            recovery_cost="5+ beats",
            definition_fields=["payload", "scope", "priority", "lever_arm"],
            physical_read="sweeps through the entire workspace and forces all other motion to clear",
            communication_read="broadcast or governance directive reaching all agents at once",
            use_cases=[
                "global seed update",
                "priority override",
                "session start or stop",
                "whole-pod governance directive",
            ],
            count_profiles=[
                CountProfile("1", "single staff", "one broadcast channel", "one whole-pod directive"),
                CountProfile("2", "double staff", "dual broadcast channel", "seed plus constraint or parallel broadcast"),
                CountProfile("3+", "triple or more staves", "message flooding", "avoid except in exceptional governance cases"),
            ],
            formulas=[
                "S = (payload, scope=ALL, priority=OVERRIDE, lever_arm)",
            ],
        ),
    ]


def build_vtg_modes() -> list[VTGModeSpec]:
    return [
        VTGModeSpec(
            name="extension",
            trace="expanding or contracting circles",
            protocol="gradual scope adjustment",
            use_when="widening or narrowing research scope",
            parameter="radius_delta_per_cycle",
        ),
        VTGModeSpec(
            name="flower",
            trace="inscribed n-petal pattern",
            protocol="cyclic sub-topic exploration",
            use_when="agent should revisit n aspects repeatedly",
            parameter="petal_count",
        ),
        VTGModeSpec(
            name="isolation",
            trace="fixed-point hover",
            protocol="invariance testing",
            use_when="checking whether a claim survives context change",
            parameter="fixed_point_address",
        ),
        VTGModeSpec(
            name="cap",
            trace="dual synchronized orbits",
            protocol="correlated dual-agent monitoring",
            use_when="tracking complementary or anti-correlated outputs",
            parameter="correlation_target",
        ),
        VTGModeSpec(
            name="antispin",
            trace="inward-pointing petals",
            protocol="convergence tracking",
            use_when="monitoring D/Q/I collapse toward zero point",
            parameter="convergence_threshold",
        ),
    ]


def build_algebra() -> PropChannelAlgebra:
    props = build_props()
    if len(props) != 5:
        raise ValueError("Prop channel algebra requires exactly five prop families.")
    return PropChannelAlgebra(
        generated_at=utc_now(),
        derivation_command=DERIVATION_COMMAND,
        chapter_name="Chapter 17: Prop Types - The Physics Of Communication Channels",
        station="<0100>",
        chapter_address="Arc 5 / Su Rail / Seed",
        prerequisites=["Ch11", "Ch12", "Ch13", "Ch14", "Ch15", "Ch16"],
        deliverables=[
            "typed channel-physics algebra for five prop families",
            "prop x count bandwidth matrix",
            "state-complexity hierarchy",
            "single-to-quad scaling",
            "VTG trace library as monitoring protocol",
            "club-spin session-handoff algebra",
        ],
        forward_references=["Ch18", "Ch19", "Ch20"],
        bandwidth_progression={
            "ring": 0.618,
            "poi": 0.618,
            "ball": 1.0,
            "club": 1.618,
            "staff": 2.618,
        },
        props=props,
        vtg_modes=build_vtg_modes(),
        selection_function="Channel* = argmax[(BW(C) * Match(C, message)) / (Risk(C) * (1 + DR_C))]",
        heuristics=[
            "default to balls for routine stateless queries",
            "upgrade to clubs when the handoff carries sender-state or work-in-progress context",
            "use rings when setting schemas, seeds, or verification frames",
            "use poi for background monitoring, convergence tracking, or correlated observation",
            "use staff sparingly for governance broadcasts that every agent must hear simultaneously",
        ],
    )


def render_markdown(algebra: PropChannelAlgebra) -> str:
    prop_lines = []
    for prop in algebra.props:
        count_lines = "\n".join(
            f"  - `{profile.count}`: {profile.channel_mode} - {profile.use_case}"
            for profile in prop.count_profiles
        )
        formula_lines = "\n".join(f"  - `{formula}`" for formula in prop.formulas)
        use_lines = "\n".join(f"  - {item}" for item in prop.use_cases)
        prop_lines.append(
            f"### {prop.prop.title()}\n\n"
            f"- channel type: `{prop.channel_type}`\n"
            f"- state model: `{prop.state_model}`\n"
            f"- bandwidth: `{prop.bandwidth}`\n"
            f"- error mode: `{prop.error_mode}`\n"
            f"- impact: `{prop.error_impact}`\n"
            f"- recovery: `{prop.recovery_cost}`\n"
            f"- physical read: {prop.physical_read}\n"
            f"- communication read: {prop.communication_read}\n"
            f"- definition fields: `{', '.join(prop.definition_fields)}`\n\n"
            f"Use cases:\n{use_lines}\n\n"
            f"Count profiles:\n{count_lines}\n\n"
            f"Key formulas:\n{formula_lines}"
        )

    vtg_lines = "\n".join(
        f"- `{mode.name}`: {mode.protocol} - {mode.use_when} (`{mode.parameter}`)"
        for mode in algebra.vtg_modes
    )
    heuristic_lines = "\n".join(f"- {item}" for item in algebra.heuristics)
    bandwidth_lines = "\n".join(
        f"- `{name}`: `{value}`" for name, value in algebra.bandwidth_progression.items()
    )

    return f"""# Prop Channel Algebra

Generated: `{algebra.generated_at}`
Command: `{algebra.derivation_command}`
Station: `{algebra.station}`
Verdict: `OK`

This crystal formalizes Chapter 17 as typed communication-channel algebra rather than pure metaphor.

## Scope

- chapter: `{algebra.chapter_name}`
- address: `{algebra.chapter_address}`
- prerequisites: `{", ".join(algebra.prerequisites)}`
- forward references: `{", ".join(algebra.forward_references)}`

## Deliverables

{chr(10).join(f"- {item}" for item in algebra.deliverables)}

## Bandwidth Progression

{bandwidth_lines}

## Prop Families

{chr(10).join(prop_lines)}

## VTG Monitoring Modes

{vtg_lines}

## Selection Function

- `{algebra.selection_function}`

## Practical Heuristics

{heuristic_lines}
"""


def render_receipt(algebra: PropChannelAlgebra) -> str:
    return f"""# Prop Channel Algebra Receipt

- Generated: `{algebra.generated_at}`
- Command: `{algebra.derivation_command}`
- Verdict: `OK`

## Proved Structure

- prop families: `{len(algebra.props)}`
- VTG monitoring modes: `{len(algebra.vtg_modes)}`
- station: `{algebra.station}`
- selection law: `{algebra.selection_function}`

## Bandwidth Ladder

{chr(10).join(f"- `{name}`: `{value}`" for name, value in algebra.bandwidth_progression.items())}

## Why This Matters

- the chapter now exists as a typed schema the local runtime can cite
- prop metaphors are converted into explicit channel classes with risk, bandwidth, and recovery profiles
- the next implementation frontier is to bind actual agent handoffs and board coordination surfaces to these channel types
"""


def main() -> int:
    algebra = build_algebra()
    OUTPUT_JSON_PATH.write_text(json.dumps(asdict(algebra), indent=2), encoding="utf-8")
    OUTPUT_MARKDOWN_PATH.write_text(render_markdown(algebra), encoding="utf-8")
    OUTPUT_RECEIPT_PATH.write_text(render_receipt(algebra), encoding="utf-8")
    print(f"Wrote prop channel algebra json: {OUTPUT_JSON_PATH}")
    print(f"Wrote prop channel algebra markdown: {OUTPUT_MARKDOWN_PATH}")
    print(f"Wrote prop channel algebra receipt: {OUTPUT_RECEIPT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
