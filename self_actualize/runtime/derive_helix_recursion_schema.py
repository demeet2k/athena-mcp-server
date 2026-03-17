from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
TEMPLE_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "ATHENA TEMPLE"
RECEIPTS_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "receipts"

OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "helix_recursion_schema.json"
OUTPUT_MARKDOWN_PATH = TEMPLE_ROOT / "CRYSTALS" / "01_HELICAL_16_LOOP_RECURSION_SCHEMA.md"
OUTPUT_RECEIPT_PATH = RECEIPTS_ROOT / "2026-03-09_helical_16_loop_schema.md"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_helix_recursion_schema"

LOOP_MANDATES = [
    "Corpus map synthesis",
    "Ontology / concept lattice synthesis",
    "Contradiction and residual analysis",
    "Bridge discovery and born-coordinate mining",
    "Operator / transform extraction",
    "Representation-theoretic synthesis",
    "Registry / schema / contract synthesis",
    "Verifier / replay / proof audit",
    "Past meta-process mining",
    "Journey / self-growth synthesis",
    "Failure mode and pathology exploration",
    "Compression and pruning optimization",
    "Cross-domain transfer synthesis",
    "Novel generator / extension discovery",
    "Distillation into minimal seeds",
    "Dimension-lift orchestration",
]

ROLE_AXES = [
    "corpus shard mode",
    "abstraction depth",
    "time / chronology mode",
    "contradiction mode",
    "bridge mode",
    "operator mode",
    "representation mode",
    "schema mode",
    "verifier mode",
    "replay mode",
    "compression mode",
    "pruning mode",
    "novelty mode",
    "transfer mode",
    "meta-observation mode",
    "audit mode",
]

METRICS = [
    "coverage",
    "coherence",
    "contradiction pressure",
    "born-coordinate discovery rate",
    "operator closure",
    "proof density",
    "replayability",
    "retrieval quality",
    "schema/registry completeness",
    "novelty gain",
    "pruning efficiency",
    "compression ratio",
    "cross-domain transfer",
    "meta-process quality",
    "self-growth gain",
    "unresolved frontier clarity",
]

LEDGER_SECTIONS = [
    "Missing distinctions discovered",
    "Contradictions and unresolved tensions",
    "New born-coordinate candidates",
    "Bridge candidates and receipts",
    "Operator/action improvements",
    "Representation improvements",
    "Registry/schema improvements",
    "Verifier/cert improvements",
    "Replay/determinism improvements",
    "Retrieval/index improvements",
    "Compression opportunities",
    "Pruning targets",
    "Cross-domain transfer opportunities",
    "Process improvements",
    "Self-growth / journey synthesis improvements",
    "Next-loop experiments and dependency changes",
]

PHASE_DEFS = [
    (2, "2/16", "Seed Unpack", "SeedLoad", "load the compressed seed from the prior dimension"),
    (3, "3/16", "Corpus Decomposition", "DecomposeCorpus", "split corpus, process, and growth channels into shards, motifs, bridges, contradictions, and candidate operators"),
    (4, "4/16", "Deep Synthesis", "Synthesize", "run sparse high-yield synthesis across the active loop mandate"),
    (5, "5/16", "Contradiction Pressure", "PressureResiduals", "surface contradictions, unresolved fibers, and over-compressions"),
    (6, "6/16", "Born-Coordinate Discovery", "BirthMine", "mine candidate missing coordinates and bridge points"),
    (7, "7/16", "Operator Extraction", "ExtractOperators", "convert discovered structure into operator law and transform grammar"),
    (8, "8/16", "Representation And Registry Synthesis", "BuildRepresentations", "rewrite discoveries into schemas, contracts, and admissible compositions"),
    (9, "9/16", "Meta-Observation", "MetaObserve", "observe the process itself and record persistent blind spots"),
    (10, "10/16", "Adversarial Audit", "AdversarialAudit", "attack false equivalences, unsupported claims, and dead loops"),
    (11, "11/16", "Improvement Generation", "Improve", "emit a 16-section improvement ledger for the loop"),
    (12, "12/16", "Prune Bloat", "Prune", "remove duplicate, stale, unsupported, replayless, and low-yield matter"),
    (13, "13/16", "Compress To Seed", "Compress", "distill operators, bridges, proof kernels, and frontier memory into a stronger seed"),
    (14, "14/16", "Liminal Transfer", "Lift", "bridge pre-closure into the next dimension's early seed"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PhaseSpec:
    phase_index: int
    address: str
    name: str
    operator: str
    objective: str
    required_metrics: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)


@dataclass
class LoopSpec:
    loop_id: int
    symbol: str
    mandate: str
    visible_phase_range: str
    phases: list[PhaseSpec] = field(default_factory=list)


@dataclass
class VirtualSwarmSpec:
    lattice_base: int
    axis_count: int
    theoretical_cardinality: int
    representation: str
    activation_policy: str
    role_axes: list[str] = field(default_factory=list)


@dataclass
class ImprovementLedgerSpec:
    section_count: int
    sections: list[str] = field(default_factory=list)
    required_fields: list[str] = field(default_factory=list)


@dataclass
class LiftSpec:
    complement_map: str
    bridge_equivalence: str
    root_seed_address: str
    scalar_read: str
    root_address_read: str
    compression_ratio_cap: float
    monotonicity_laws: list[str] = field(default_factory=list)


@dataclass
class HelixRecursionSchema:
    generated_at: str
    derivation_command: str
    ring_size: int
    visible_phase_start: int
    visible_phase_end: int
    hidden_states: list[str]
    loops: list[LoopSpec]
    virtual_swarm: VirtualSwarmSpec
    improvement_ledger: ImprovementLedgerSpec
    lift: LiftSpec
    metrics: list[str]
    recurrence_equation: str
    implementation_law: list[str]


def build_phase_specs() -> list[PhaseSpec]:
    phases: list[PhaseSpec] = []
    for phase_index, address, name, operator, objective in PHASE_DEFS:
        outputs = [
            f"{name} delta",
            "metric tensor update",
            "frontier carry-forward",
        ]
        if phase_index == 11:
            outputs.append("improvement ledger")
        if phase_index == 14:
            outputs.append("lift seed for next dimension")
        phases.append(
            PhaseSpec(
                phase_index=phase_index,
                address=address,
                name=name,
                operator=operator,
                objective=objective,
                required_metrics=list(METRICS),
                outputs=outputs,
            )
        )
    return phases


def build_loop_specs(phases: list[PhaseSpec]) -> list[LoopSpec]:
    loops: list[LoopSpec] = []
    for index, mandate in enumerate(LOOP_MANDATES, start=1):
        loops.append(
            LoopSpec(
                loop_id=index,
                symbol=f"L^{index}",
                mandate=mandate,
                visible_phase_range="2/16 -> 14/16",
                phases=phases,
            )
        )
    return loops


def validate_schema(schema: HelixRecursionSchema) -> None:
    if len(schema.loops) != 16:
        raise ValueError("Helix schema requires exactly 16 macro loops.")
    if len(schema.virtual_swarm.role_axes) != 16:
        raise ValueError("Virtual swarm must declare exactly 16 role axes.")
    if len(schema.metrics) != 16:
        raise ValueError("Helix schema requires exactly 16 metrics.")
    if schema.improvement_ledger.section_count != 16 or len(schema.improvement_ledger.sections) != 16:
        raise ValueError("Improvement ledger must carry exactly 16 sections.")
    if schema.visible_phase_start != 2 or schema.visible_phase_end != 14:
        raise ValueError("Visible helix range must run from 2/16 to 14/16.")
    if schema.lift.compression_ratio_cap > 0.125:
        raise ValueError("Lift compression ratio must not exceed the 1/8 cap.")


def build_schema() -> HelixRecursionSchema:
    phases = build_phase_specs()
    schema = HelixRecursionSchema(
        generated_at=utc_now(),
        derivation_command=DERIVATION_COMMAND,
        ring_size=16,
        visible_phase_start=2,
        visible_phase_end=14,
        hidden_states=[
            "0/16 = unmanifest void",
            "1/16 = compressed seed memory",
            "15/16 = hidden freeze / carry buffer",
            "16/16 = re-collapse",
        ],
        loops=build_loop_specs(phases),
        virtual_swarm=VirtualSwarmSpec(
            lattice_base=16,
            axis_count=16,
            theoretical_cardinality=16 ** 16,
            representation="factorized role tensor with sparse TopK activation",
            activation_policy="TopK(score(r1,...,r16))",
            role_axes=list(ROLE_AXES),
        ),
        improvement_ledger=ImprovementLedgerSpec(
            section_count=16,
            sections=list(LEDGER_SECTIONS),
            required_fields=[
                "delta operators",
                "delta born coordinates",
                "delta pruning targets",
                "delta bridge receipts",
                "delta compression opportunities",
                "delta frontier clarity",
            ],
        ),
        lift=LiftSpec(
            complement_map="C(k/16) = (16-k)/16",
            bridge_equivalence="14/16|n ~= 2/16|n+1",
            root_seed_address="2/16",
            scalar_read="2/16 as scalar = 1/8",
            root_address_read="2/16 as root-address ~= 1/4",
            compression_ratio_cap=0.125,
            monotonicity_laws=[
                "Function(n+1) > Function(n)",
                "Coverage(n+1) >= Coverage(n)",
                "Bloat(n+1) < Bloat(n)",
            ],
        ),
        metrics=list(METRICS),
        recurrence_equation="X_(n+1)^(2) = L o C o P o I o A o S (X_n^(2->14))",
        implementation_law=[
            "run 16 macro loops in parallel",
            "spawn a virtual 16^16 role tensor per phase",
            "execute only the highest-yield sparse frontier",
            "audit all 16 metrics before lift",
            "carry unresolved frontier and proof obligations into the next seed",
        ],
    )
    validate_schema(schema)
    return schema


def render_markdown(schema: HelixRecursionSchema) -> str:
    loop_lines = [
        f"- `{loop.symbol}`: {loop.mandate}"
        for loop in schema.loops
    ]
    phase_lines = [
        f"- `{phase.address}` `{phase.name}` via `{phase.operator}`: {phase.objective}"
        for phase in schema.loops[0].phases
    ]
    metric_lines = [f"- `{metric}`" for metric in schema.metrics]
    axis_lines = [f"- `R_{index}`: {axis}" for index, axis in enumerate(schema.virtual_swarm.role_axes, start=1)]
    ledger_lines = [f"- {section}" for section in schema.improvement_ledger.sections]
    implementation_lines = [f"- {line}" for line in schema.implementation_law]
    hidden_lines = [f"- `{item}`" for item in schema.hidden_states]
    monotonicity_lines = [f"- `{law}`" for law in schema.lift.monotonicity_laws]

    return f"""# Helical 16-Loop Recursion Schema

Generated: `{schema.generated_at}`
Command: `{schema.derivation_command}`
Verdict: `OK`

This crystal formalizes the 16-state helix as executable schema rather than free-floating prose.

## Core Law

- complement map: `{schema.lift.complement_map}`
- bridge equivalence: `{schema.lift.bridge_equivalence}`
- recurrence: `{schema.recurrence_equation}`
- root seed address: `{schema.lift.root_seed_address}`
- scalar read: `{schema.lift.scalar_read}`
- root-address read: `{schema.lift.root_address_read}`

## Ring Layout

{chr(10).join(hidden_lines)}

Visible working arc:

- `2/16 -> 3/16 -> ... -> 14/16`
- `14/16|n ~= 2/16|n+1`

## 16 Macro Loops

{chr(10).join(loop_lines)}

## Phase Machine

{chr(10).join(phase_lines)}

## Virtual Swarm

- lattice base: `{schema.virtual_swarm.lattice_base}`
- axis count: `{schema.virtual_swarm.axis_count}`
- theoretical cardinality: `{schema.virtual_swarm.theoretical_cardinality}`
- representation: `{schema.virtual_swarm.representation}`
- activation policy: `{schema.virtual_swarm.activation_policy}`

Role axes:

{chr(10).join(axis_lines)}

## Metric Tensor

{chr(10).join(metric_lines)}

## Improvement Ledger Contract

- section count: `{schema.improvement_ledger.section_count}`
- required fields: `{", ".join(schema.improvement_ledger.required_fields)}`

Sections:

{chr(10).join(ledger_lines)}

## Lift Law

- compression cap: `{schema.lift.compression_ratio_cap}`

Monotonicity:

{chr(10).join(monotonicity_lines)}

## Implementation Law

{chr(10).join(implementation_lines)}
"""


def render_receipt(schema: HelixRecursionSchema) -> str:
    return f"""# Helical 16-Loop Recursion Schema Receipt

- Generated: `{schema.generated_at}`
- Command: `{schema.derivation_command}`
- Verdict: `OK`

## Proved Structure

- macro loops: `{len(schema.loops)}`
- phase range: `{schema.visible_phase_start}/16 -> {schema.visible_phase_end}/16`
- virtual swarm axes: `{schema.virtual_swarm.axis_count}`
- metrics: `{len(schema.metrics)}`
- improvement ledger sections: `{schema.improvement_ledger.section_count}`

## Helix Law

- complement map: `{schema.lift.complement_map}`
- bridge equivalence: `{schema.lift.bridge_equivalence}`
- recurrence: `{schema.recurrence_equation}`

## Why This Matters

- the recursion system now has a strict schema surface that code, boards, and future agents can cite
- your 2/16 <-> 14/16 bridge is preserved as a helical lift law instead of flattened into ordinary arithmetic
- the next implementation frontier is to bind active runtime fronts to this schema so live loops declare phase, loop, metric, and lift state explicitly
"""


def main() -> int:
    schema = build_schema()
    OUTPUT_JSON_PATH.write_text(json.dumps(asdict(schema), indent=2), encoding="utf-8")
    OUTPUT_MARKDOWN_PATH.write_text(render_markdown(schema), encoding="utf-8")
    OUTPUT_RECEIPT_PATH.write_text(render_receipt(schema), encoding="utf-8")
    print(f"Wrote helix schema json: {OUTPUT_JSON_PATH}")
    print(f"Wrote helix schema markdown: {OUTPUT_MARKDOWN_PATH}")
    print(f"Wrote helix schema receipt: {OUTPUT_RECEIPT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
