"""Built-in seed entries for a fresh AtlasForge memory bank.

AtlasForge is meant to be your *external* memory for math.

When a memory directory is empty, it can be useful to start with a few
high-signal "seed" entries that describe the backbone of the framework and the
central mathematical objects you've been working with.

The seeds here are intentionally compact and operational. They are not a
replacement for your own derivations — they are anchors you can search for and
build upon.
"""

from __future__ import annotations

from typing import List

from atlasforge.memory.entry import MemoryEntry


def builtin_seed_entries() -> List[MemoryEntry]:
    """Return a small set of built-in seed entries.

    Notes
    -----
    We keep this list short on purpose. The idea is to provide stable anchors
    and let your own work become the majority of the memory bank.
    """

    seeds: List[MemoryEntry] = []

    # ------------------------------------------------------------------
    # QCM / interference / boxplus
    # ------------------------------------------------------------------
    seeds.append(
        MemoryEntry(
            title="Interference law (QCM backbone)",
            content=(
                "The core measurement identity used throughout QCM is:\n\n"
                "  |ψ₁ + ψ₂|² = a² + b² + 2ab·cos(Δθ)\n\n"
                "where a=|ψ₁|, b=|ψ₂| and Δθ is the phase difference.\n\n"
                "Special slices:\n"
                "- Δθ = 0   → (a+b)²  (constructive / aligned)\n"
                "- Δθ = π/2 → a²+b²  (orthogonal; interference term cancels)\n"
                "- Δθ = π   → (a-b)² (destructive / anti-aligned)\n\n"
                "This identity is the bridge between amplitude geometry (Θ) and\n"
                "discrete phase structure (Λ).\n"
            ),
            tags=["seed", "qcm", "interference", "theta", "lambda", "kind:identity"],
            extra={
                "kind": "identity",
                "crystal_hint": "Σ·✿ (phase/interference)",
            },
        )
    )

    seeds.append(
        MemoryEntry(
            title="Quadrature / boxplus operator (⊞)",
            content=(
                "Define the orthogonal (Δθ=π/2) slice of interference as an operator:\n\n"
                "  a ⊞ b := √(a² + b²)\n\n"
                "Equivalently, ⊞ is the Euclidean norm of the 2-vector (a,b).\n\n"
                "Useful properties:\n"
                "- Commutative: a ⊞ b = b ⊞ a\n"
                "- Monotone in |a|,|b|\n"
                "- N-ary form: ⊞(a₁,…,aₙ) = √(Σ aᵢ²)\n"
                "- Interpretable as composition of independent orthogonal components\n"
                "  (energy-like aggregation).\n"
            ),
            tags=["seed", "operator", "boxplus", "quadrature", "qcm", "kind:operator"],
            extra={
                "kind": "operator",
                "symbol": "⊞",
                "crystal_hint": "Σ·✿ (orthogonal composition)",
            },
        )
    )

    # ------------------------------------------------------------------
    # Pivot equation
    # ------------------------------------------------------------------
    seeds.append(
        MemoryEntry(
            title="Pivot equation (order-of-operations defect)",
            content=(
                "A recurring identity in the framework is the idea that an\n"
                "expand-then-compress pipeline does not always commute with a\n"
                "compress-then-expand pipeline. The symbolic shorthand is:\n\n"
                "  ∂∫ − ∫∂ = Ω\n\n"
                "Read as: the non-commutativity between expansion (∂) and\n"
                "compression (∫) manifests as recursion/renormalization (Ω).\n\n"
                "Operationally, this is a reminder to *choose a representation*\n"
                "before you optimize/verify, and to record that choice as part\n"
                "of the artifact (Replay + Proof).\n"
            ),
            tags=["seed", "pivot", "recursion", "renormalization", "kind:identity"],
            extra={
                "kind": "identity",
                "crystal_hint": "Ψ·❋ (recursion / RG)",
            },
        )
    )

    # ------------------------------------------------------------------
    # Kernel spine
    # ------------------------------------------------------------------
    seeds.append(
        MemoryEntry(
            title="Invariant spine (Ledger · Corridor · Proof · Replay)",
            content=(
                "AtlasForge computations are designed to travel along a stable spine:\n\n"
                "1) Ledger   — content-addressed storage and provenance\n"
                "2) Corridor — explicit domains/bounds where claims are valid\n"
                "3) Proof    — certificates / enclosures / obligations\n"
                "4) Replay   — deterministic reproduction of the result\n\n"
                "A Recipe is the unit that ties these together: it records HOW the\n"
                "result was produced and stores the proof-carrying payload needed\n"
                "for verification.\n"
            ),
            tags=["seed", "kernel", "proof", "replay", "registry", "kind:note"],
            extra={
                "kind": "note",
                "crystal_hint": "Ψ·□ (structural invariants)",
            },
        )
    )

    # ------------------------------------------------------------------
    # Master equation
    # ------------------------------------------------------------------
    seeds.append(
        MemoryEntry(
            title="Master equation (system decomposition)",
            content=(
                "The documentation summarizes the whole architecture as a\n"
                "decomposition of interacting subsystems:\n\n"
                "  S = (T,Ψ,Σ,C,D;Ω) + AQM[...] + LM[...] + QCM[...] + PROOF[...]\n\n"
                "Interpretation:\n"
                "- (T,Ψ,Σ,C,D;Ω): the universal backbone (time, poles, constraints,\n"
                "  discrete/continuous coupling)\n"
                "- AQM: axiomatic quantum mathematics (extended arithmetic + channels)\n"
                "- LM: liminal mathematics (hybrid dynamics, closure, RG tower)\n"
                "- QCM: quadrature/cyclotomic manifold (Θ↔Λ interference geometry)\n"
                "- PROOF: certificates + verifier kernel + replay\n\n"
                "This is less a single equation than a map of where objects live\n"
                "and how they translate.\n"
            ),
            tags=["seed", "master-equation", "architecture", "kind:note"],
            extra={
                "kind": "note",
                "crystal_hint": "Ψ·□ (global structure)",
            },
        )
    )

    # ------------------------------------------------------------------
    # Crystal merge protocol
    # ------------------------------------------------------------------
    seeds.append(
        MemoryEntry(
            title="Crystal Merge Protocol (CM0 → CM6)",
            content=(
                "CM0: Lock — identify object + degeneracies\n"
                "CM1: Four-lens scan — □ ✿ ☁ ❋ parallel analysis\n"
                "CM2: Pivot — controlled representation change\n"
                "CM3: Collapse — reduce to a master equation / normal form\n"
                "CM4: Meta-duality — discover higher-level symmetry/structure\n"
                "CM5: Proof pack — bundle witnesses + verifiers\n"
                "CM6: Publication gate — final verification + stable artifact\n\n"
                "In the codebase today, CM1/CM3/CM5 map most directly to:\n"
                "- Lens transports (charts)\n"
                "- Normal forms (constraint IR)\n"
                "- CertificateBundle / ProofPack\n"
            ),
            tags=["seed", "cm", "protocol", "lenses", "certificates", "kind:note"],
            extra={
                "kind": "note",
                "crystal_hint": "Ψ·❋ (procedure/recursion)",
            },
        )
    )

    # ------------------------------------------------------------------
    # OICF / closure potential
    # ------------------------------------------------------------------
    seeds.append(
        MemoryEntry(
            title="OICF coordinates (Ω, I, C, F)",
            content=(
                "A recurrent coordinate system used across the LM/AQM layer is:\n\n"
                "  Ω — viability margin (distance to failure)\n"
                "  I — integration / coupling strength\n"
                "  C — coherence (cross-scale consistency)\n"
                "  F — function / goal-directedness\n\n"
                "A common aggregate is an emergence / closure potential:\n"
                "  P = Ω · I · C · F\n\n"
                "Operationally: treat these as measurable scalars that can be\n"
                "attached to artifacts (recipes, seeds, entries) as metadata.\n"
            ),
            tags=["seed", "oicf", "emergence", "lm", "kind:definition"],
            extra={
                "kind": "definition",
                "crystal_hint": "Ψ·☁ (metrics/uncertainty)",
            },
        )
    )

    # ------------------------------------------------------------------
    # Master equation
    # ------------------------------------------------------------------
    
    return seeds
