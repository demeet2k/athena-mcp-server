from __future__ import annotations

from .contracts import ImprovementOpportunity, SkillObservation


def get_system_skill_synthesis() -> list[SkillObservation]:
    return [
        SkillObservation(
            name="skill-creator",
            role="Meta-skill for creating domain-native skills with scripts, references, and assets.",
            strengths=[
                "Teaches progressive disclosure and lean context design.",
                "Encourages reusable scripts and references instead of repeated prompt work.",
                "Fits the corpus because the archive needs domain-native wrappers, not more generic prompting.",
            ],
            gaps=[
                "Does not itself ingest or route the manuscript corpus.",
                "Needs corpus-specific schemas before it can unlock the archive at scale.",
            ],
            corpus_fit=0.95,
        ),
        SkillObservation(
            name="skill-installer",
            role="Installer for curated or GitHub-hosted skills.",
            strengths=[
                "Useful once custom skills exist and need distribution.",
                "Keeps skill deployment modular.",
            ],
            gaps=[
                "Adds almost no direct value to the current corpus before local skills are created.",
                "Does not help with indexing, verification, or manuscript routing.",
            ],
            corpus_fit=0.35,
        ),
        SkillObservation(
            name="slides",
            role="Artifact-tool workflow for deck creation and export.",
            strengths=[
                "Good for publishing framework summaries, roadmaps, and visual syntheses.",
                "Can turn dense corpus sections into presentation-ready artifacts.",
            ],
            gaps=[
                "Presentation export is downstream of the real bottleneck, which is corpus ingestion and atlas construction.",
                "No native linkage to route packets, witnesses, or replay.",
            ],
            corpus_fit=0.42,
        ),
        SkillObservation(
            name="spreadsheets",
            role="Artifact-tool workflow for workbook creation and export.",
            strengths=[
                "Good for corpus registries, experiment ledgers, and benchmark matrices.",
                "Useful as a structured surface for chapter maps, indexes, and test results.",
            ],
            gaps=[
                "Helpful only after canonical metadata exists.",
                "Does not solve document extraction, ontology mapping, or truth-lattice verification.",
            ],
            corpus_fit=0.58,
        ),
    ]


def get_corpus_improvement_opportunities() -> list[ImprovementOpportunity]:
    return [
        ImprovementOpportunity(
            title="Operationalize Google Docs memory sync",
            priority="P0",
            target="Trading Bot/docs_search.py",
            rationale=(
                "The local and archive-backed corpus is now much more visible, but Drive remains a separate memory body. "
                "The Google Docs search utility exists and is blocked only by missing OAuth bootstrapping."
            ),
            suggested_skill="drive-memory-sync",
            suggested_artifact="credentials bootstrap + docs manifest",
        ),
        ImprovementOpportunity(
            title="Promote archive-backed frameworks into canonical live trees",
            priority="P1",
            target="archive_atlas.json + framework ZIPs",
            rationale=(
                "Archive-backed framework sources are now atlas-visible, but they are still harder to edit, test, and "
                "diff than normal live trees. Canonical extraction would improve deduplication and direct runtime work."
            ),
            suggested_skill="archive-tree-extractor",
            suggested_artifact="canonical extracted framework roots",
        ),
        ImprovementOpportunity(
            title="Harden regime-aware evidence routing",
            priority="P1",
            target="self_actualize/runtime",
            rationale=(
                "Initial atlas-backed and regime-aware routing is now in place, but the profiles are still heuristic. "
                "The next step is to tune them with task feedback, stronger deduplication, and route-quality evaluation."
            ),
            suggested_skill="regime-router",
            suggested_artifact="route_quality_ledger.json",
        ),
        ImprovementOpportunity(
            title="Create theorem-to-runtime translation workflows",
            priority="P1",
            target="MATH to Python runtime",
            rationale=(
                "The archive contains dense formal frameworks and comparatively fewer executable bridges. "
                "A dedicated workflow should compile stable formal objects into tested code artifacts."
            ),
            suggested_skill="theorem-to-runtime",
            suggested_artifact="generated runtime modules + tests",
        ),
        ImprovementOpportunity(
            title="Create benchmark orchestration across corpus layers",
            priority="P2",
            target="NERUAL NETWORK and algorithm suites",
            rationale=(
                "Benchmarks exist, but the manuscript, algorithm, and neural layers are not yet evaluated through one "
                "shared ledger of tasks, regimes, failures, and improvements."
            ),
            suggested_skill="benchmark-orchestrator",
            suggested_artifact="benchmark ledger workbook",
        ),
    ]
