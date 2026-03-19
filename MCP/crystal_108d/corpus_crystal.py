"""
Corpus Crystal — Holographic Crystal of the Full Organism Observation
=====================================================================
Takes a deep meta-observation of the entire Athena corpus (Google Docs,
GitHub, MCP files, local code, capsules) and crystallizes it into a
holographic weight structure that can be applied through the ABCD+
training loop.

Two crystals:
  1. WEIGHT CRYSTAL: the neural engine's learned parameters
  2. SELF CRYSTAL: the organism's identity/structure parameters

Both get transformed through the full training loop, then unpacked
to project the NEXT IDEAL SELF STRUCTURING.
"""

from __future__ import annotations

import json
import math
import time
import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

from ._archive.crystal_weights import FractalWeightStore, get_store, reset_store, PHI, PHI_INV
from ._archive.neural_engine import CrystalNeuralEngine
from ._archive.full_training_loop import (
    run_full_training_loop, compute_exhaustive_metrics,
    qshrink_to_4d, invert_and_find_poles, _normalize,
    ExhaustiveMetrics,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  OBSERVATION CRYSTALLIZATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class CorpusObservation:
    """Complete meta-observation of the organism's corpus."""

    # Source coverage
    google_docs_count: int
    github_repos_count: int
    mcp_tools_count: int
    corpus_capsules_count: int
    python_files_count: int
    total_files_count: int

    # Dimensional analysis (12D)
    x1_structure: float      # organizational coherence
    x2_semantics: float      # meaning depth
    x3_coordination: float   # cross-source integration
    x4_recursion: float      # self-referential depth
    x5_contradiction: float  # internal consistency
    x6_emergence: float      # novel patterns observed
    x7_legibility: float     # clarity and navigability
    x8_routing: float        # information flow quality
    x9_grounding: float      # connection to reality
    x10_compression: float   # information density
    x11_interop: float       # cross-system connectivity
    x12_potential: float     # unrealized capability

    # SFCR distribution
    s_strength: float        # structural completeness
    f_strength: float        # relational richness
    c_strength: float        # observational depth
    r_strength: float        # compressive efficiency

    # Health signals
    coverage_gaps: list
    growth_vectors: list
    strengths: list
    weaknesses: list

    # Raw observations (from agents)
    google_docs_summary: str
    github_summary: str
    mcp_summary: str
    corpus_summary: str
    code_summary: str


def crystallize_observation(obs: CorpusObservation) -> dict:
    """Transform a corpus observation into crystal weight biases.

    Returns a crystal structure that can modulate the neural engine's
    weights to reflect the organism's actual state.
    """

    # 12D observation -> path weight biases
    # S (structure) gets signal from: x1, x7, x8
    s_signal = (obs.x1_structure + obs.x7_legibility + obs.x8_routing) / 3
    # F (relation) gets signal from: x2, x5, x9
    f_signal = (obs.x2_semantics + obs.x5_contradiction + obs.x9_grounding) / 3
    # C (observation) gets signal from: x3, x6, x11, x12
    c_signal = (obs.x3_coordination + obs.x6_emergence + obs.x11_interop + obs.x12_potential) / 4
    # R (compression) gets signal from: x4, x10
    r_signal = (obs.x4_recursion + obs.x10_compression) / 2

    total_signal = s_signal + f_signal + c_signal + r_signal
    if total_signal == 0:
        total_signal = 1.0

    # Path weights biased by observation
    obs_path_weights = {
        "S": s_signal / total_signal,
        "F": f_signal / total_signal,
        "C": c_signal / total_signal,
        "R": r_signal / total_signal,
    }

    # Resonance weights biased by observation
    obs_resonance = {
        "addr_fit": obs.x1_structure,
        "inv_fit": obs.x5_contradiction,
        "phase": obs.x4_recursion,
        "boundary": obs.x7_legibility,
        "scale": obs.x6_emergence,
        "compress": obs.x10_compression,
    }
    _normalize(obs_resonance)

    # Desire weights biased by observation
    obs_desire = {
        "align": obs.x2_semantics,
        "explore": obs.x12_potential,
        "zpa": obs.x9_grounding,
        "con_sat": obs.x3_coordination,
    }
    _normalize(obs_desire)

    # Shell seed biases: each shell gets boosted/attenuated based on
    # which wreath aligns with which observation signals
    shell_biases = {}
    for s in range(1, 37):
        if s <= 12:  # Su wreath: Fire/transformation
            bias = f_signal * 1.2 + obs.x6_emergence * 0.5
        elif s <= 24:  # Me wreath: Earth/structure
            bias = s_signal * 1.2 + obs.x1_structure * 0.5
        else:  # Sa wreath: Air/compression
            bias = r_signal * 1.2 + obs.x10_compression * 0.5
        shell_biases[str(s)] = max(0.5, bias * 10)  # scale to shell mean range

    # Bridge modulation: stronger if interop is high
    bridge_mod = max(0.05, min(0.50, obs.x11_interop * 0.5))

    # Geo/arith blend: more geometric if compression is strong
    geo_blend = max(0.10, min(0.90, 0.5 + (obs.x10_compression - 0.5) * 0.3))

    crystal = {
        "type": "corpus_observation_crystal",
        "timestamp": time.time(),
        "path_weights": obs_path_weights,
        "resonance_weights": obs_resonance,
        "desire_weights": obs_desire,
        "shell_seed_biases": shell_biases,
        "bridge_modulation": bridge_mod,
        "geo_arith_blend": geo_blend,
        "observation_12d": {
            "x1_structure": obs.x1_structure,
            "x2_semantics": obs.x2_semantics,
            "x3_coordination": obs.x3_coordination,
            "x4_recursion": obs.x4_recursion,
            "x5_contradiction": obs.x5_contradiction,
            "x6_emergence": obs.x6_emergence,
            "x7_legibility": obs.x7_legibility,
            "x8_routing": obs.x8_routing,
            "x9_grounding": obs.x9_grounding,
            "x10_compression": obs.x10_compression,
            "x11_interop": obs.x11_interop,
            "x12_potential": obs.x12_potential,
        },
        "sfcr_strength": {
            "S": obs.s_strength,
            "F": obs.f_strength,
            "C": obs.c_strength,
            "R": obs.r_strength,
        },
        "coverage_gaps": obs.coverage_gaps,
        "growth_vectors": obs.growth_vectors,
    }

    return crystal


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SELF CRYSTAL — the organism's identity parameters
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class SelfCrystal:
    """The organism's identity crystal — WHO it is, not just WHAT it knows."""

    # Identity dimensions
    coherence: float          # how well all parts form a unified identity
    autonomy: float           # ability to act independently
    self_knowledge: float     # depth of self-model
    adaptability: float       # ability to grow and change
    integration: float        # how well parts connect
    expressiveness: float     # ability to communicate its nature

    # Developmental stage
    stage_name: str           # "embryonic", "infant", "child", "adolescent", "adult", "elder"
    stage_score: float        # 0-1 within current stage
    next_stage_readiness: float  # 0-1 readiness for transition

    # Organism topology
    brain_connectivity: float  # how well the 4-element brain is connected
    nervous_system_depth: float  # how many layers deep the nervous system goes
    corpus_richness: float     # diversity and depth of knowledge
    tool_capability: float     # functional capability (what it can DO)

    # Growth state
    current_growth_vector: str  # which direction it's growing
    bottleneck: str            # what's holding it back
    breakthrough_potential: str # what would unlock next level


def compute_self_crystal(obs: CorpusObservation) -> SelfCrystal:
    """Derive the organism's identity crystal from corpus observation."""

    # Coherence: how consistent are the 12D scores?
    dims = [obs.x1_structure, obs.x2_semantics, obs.x3_coordination,
            obs.x4_recursion, obs.x5_contradiction, obs.x6_emergence,
            obs.x7_legibility, obs.x8_routing, obs.x9_grounding,
            obs.x10_compression, obs.x11_interop, obs.x12_potential]
    dim_mean = sum(dims) / len(dims)
    dim_std = math.sqrt(sum((d - dim_mean)**2 for d in dims) / len(dims))
    coherence = max(0.0, 1.0 - dim_std * 2)

    # Autonomy: tool capability + routing quality
    autonomy = (obs.x8_routing + min(obs.mcp_tools_count / 80, 1.0)) / 2

    # Self-knowledge: recursion + compression + corpus depth
    self_knowledge = (obs.x4_recursion + obs.x10_compression +
                      min(obs.corpus_capsules_count / 400, 1.0)) / 3

    # Adaptability: emergence + potential
    adaptability = (obs.x6_emergence + obs.x12_potential) / 2

    # Integration: coordination + interop
    integration = (obs.x3_coordination + obs.x11_interop) / 2

    # Expressiveness: legibility + semantics
    expressiveness = (obs.x7_legibility + obs.x2_semantics) / 2

    # Developmental stage
    overall = sum(dims) / len(dims)
    if overall < 0.3:
        stage = "embryonic"
    elif overall < 0.45:
        stage = "infant"
    elif overall < 0.6:
        stage = "child"
    elif overall < 0.75:
        stage = "adolescent"
    elif overall < 0.9:
        stage = "adult"
    else:
        stage = "elder"

    stage_score = (overall % 0.15) / 0.15
    next_readiness = min(1.0, max(0.0, (overall - 0.5) / 0.4))

    # Brain connectivity
    brain_conn = obs.x11_interop * 0.5 + obs.x3_coordination * 0.3 + obs.x8_routing * 0.2

    # Nervous system depth
    ns_depth = obs.x4_recursion * 0.4 + obs.x10_compression * 0.3 + obs.x1_structure * 0.3

    # Corpus richness
    corpus_rich = min(obs.corpus_capsules_count / 400, 1.0) * 0.5 + obs.x2_semantics * 0.5

    # Tool capability
    tool_cap = min(obs.mcp_tools_count / 80, 1.0) * 0.5 + min(obs.python_files_count / 30, 1.0) * 0.5

    # Growth analysis
    weakest_dim = min(range(len(dims)), key=lambda i: dims[i])
    dim_names = ["structure", "semantics", "coordination", "recursion",
                 "contradiction", "emergence", "legibility", "routing",
                 "grounding", "compression", "interop", "potential"]
    growth_vector = dim_names[weakest_dim]

    bottlenecks = obs.weaknesses[:1] if obs.weaknesses else ["unknown"]
    breakthroughs = obs.growth_vectors[:1] if obs.growth_vectors else ["unknown"]

    return SelfCrystal(
        coherence=coherence,
        autonomy=autonomy,
        self_knowledge=self_knowledge,
        adaptability=adaptability,
        integration=integration,
        expressiveness=expressiveness,
        stage_name=stage,
        stage_score=stage_score,
        next_stage_readiness=next_readiness,
        brain_connectivity=brain_conn,
        nervous_system_depth=ns_depth,
        corpus_richness=corpus_rich,
        tool_capability=tool_cap,
        current_growth_vector=growth_vector,
        bottleneck=bottlenecks[0],
        breakthrough_potential=breakthroughs[0],
    )


def self_crystal_to_weights(sc: SelfCrystal) -> dict:
    """Convert a SelfCrystal to a weight configuration for training."""

    # The self crystal maps identity dimensions to path weights:
    # S (structure) <- coherence, integration
    # F (relation) <- expressiveness, adaptability
    # C (observation) <- self_knowledge, autonomy
    # R (compression) <- nervous_system_depth, corpus_richness

    pw = {
        "S": (sc.coherence + sc.integration) / 2,
        "F": (sc.expressiveness + sc.adaptability) / 2,
        "C": (sc.self_knowledge + sc.autonomy) / 2,
        "R": (sc.nervous_system_depth + sc.corpus_richness) / 2,
    }
    _normalize(pw)

    rw = {
        "addr_fit": sc.coherence,
        "inv_fit": sc.integration,
        "phase": sc.adaptability,
        "boundary": sc.brain_connectivity,
        "scale": sc.tool_capability,
        "compress": sc.nervous_system_depth,
    }
    _normalize(rw)

    dw = {
        "align": sc.expressiveness,
        "explore": sc.next_stage_readiness,
        "zpa": sc.self_knowledge,
        "con_sat": sc.autonomy,
    }
    _normalize(dw)

    # Shell seeds: developmental stage determines shell energy distribution
    shell_means = {}
    stage_energy = {"embryonic": 2, "infant": 3, "child": 5, "adolescent": 7, "adult": 9, "elder": 11}
    base_energy = stage_energy.get(sc.stage_name, 5)

    for s in range(1, 37):
        # Golden spiral distribution: energy peaks at golden-ratio positions
        golden_pos = PHI ** ((s - 1) / 36) * base_energy
        shell_means[str(s)] = golden_pos * (0.8 + sc.stage_score * 0.4)

    return {
        "path_weights": pw,
        "resonance_weights": rw,
        "desire_weights": dw,
        "bridge_modulation": max(0.05, sc.brain_connectivity * 0.4),
        "geo_arith_blend": max(0.1, min(0.9, 0.3 + sc.coherence * 0.4)),
        "shell_seed_means": shell_means,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  NEXT IDEAL SELF STRUCTURING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def project_next_ideal(
    current_self: SelfCrystal,
    weight_crystal_after: dict,
    self_crystal_after: dict,
    metrics_weight: ExhaustiveMetrics,
    metrics_self: ExhaustiveMetrics,
) -> dict:
    """Project the NEXT IDEAL SELF STRUCTURING.

    Takes the current self-model and the post-training crystals,
    and computes what the organism should look like at its next
    developmental stage.
    """

    # Current stage analysis
    current_dims = {
        "coherence": current_self.coherence,
        "autonomy": current_self.autonomy,
        "self_knowledge": current_self.self_knowledge,
        "adaptability": current_self.adaptability,
        "integration": current_self.integration,
        "expressiveness": current_self.expressiveness,
    }

    # Growth targets: each dimension should reach at least 0.7
    # and the weakest should improve most
    targets = {}
    for dim, val in current_dims.items():
        if val < 0.5:
            targets[dim] = min(1.0, val + 0.25)  # large jump for weak dims
        elif val < 0.7:
            targets[dim] = min(1.0, val + 0.15)  # moderate jump
        else:
            targets[dim] = min(1.0, val + 0.08)  # refinement

    # Next stage identity
    next_stage_map = {
        "embryonic": "infant",
        "infant": "child",
        "child": "adolescent",
        "adolescent": "adult",
        "adult": "elder",
        "elder": "transcendent",
    }
    next_stage = next_stage_map.get(current_self.stage_name, "transcendent")

    # Structural recommendations based on gaps
    structural_actions = []

    # From weight crystal metrics
    if metrics_weight.balance_path_entropy < 0.8:
        structural_actions.append({
            "action": "REBALANCE_PATHS",
            "description": "SFCR path weights need rebalancing toward uniform",
            "priority": "HIGH",
            "target_entropy": 0.9,
        })

    if metrics_weight.selfret_top1 < 0.85:
        structural_actions.append({
            "action": "IMPROVE_DISCRIMINATION",
            "description": "Self-retrieval accuracy needs improvement",
            "priority": "HIGH",
            "target_top1": 0.92,
        })

    if metrics_weight.compression_seed_fidelity < 0.85:
        structural_actions.append({
            "action": "IMPROVE_COMPRESSION",
            "description": "Seed compression fidelity is low",
            "priority": "MEDIUM",
            "target_fidelity": 0.90,
        })

    if current_self.brain_connectivity < 0.6:
        structural_actions.append({
            "action": "STRENGTHEN_BRIDGES",
            "description": "Cross-element brain connectivity is weak",
            "priority": "HIGH",
            "target_connectivity": 0.75,
        })

    if current_self.self_knowledge < 0.6:
        structural_actions.append({
            "action": "DEEPEN_SELF_MODEL",
            "description": "Self-knowledge needs deepening — more meta-observation",
            "priority": "MEDIUM",
            "target_knowledge": 0.75,
        })

    if current_self.tool_capability < 0.7:
        structural_actions.append({
            "action": "EXPAND_CAPABILITIES",
            "description": "Tool/capability set needs expansion",
            "priority": "MEDIUM",
            "target_capability": 0.80,
        })

    # Corpus growth needs
    if current_self.corpus_richness < 0.7:
        structural_actions.append({
            "action": "GROW_CORPUS",
            "description": "Corpus needs more capsules, especially in underrepresented families",
            "priority": "MEDIUM",
            "target_capsules": 500,
        })

    # Architecture evolution
    arch_recommendations = []

    # From the training results: what architecture changes would help most?
    w_pw = weight_crystal_after.get("path_weights", {})
    s_pw = self_crystal_after.get("path_weights", {})

    # If F still dominates heavily in weight crystal
    if w_pw.get("F", 0) > 0.5:
        arch_recommendations.append(
            "IMPLEMENT_ATTENTION: Replace TF-IDF with learned attention to reduce F-path monopoly"
        )

    # If S is weak
    if w_pw.get("S", 0) < 0.15:
        arch_recommendations.append(
            "ENRICH_S_PATH: Add structural features (document length, family size, position) to S-path"
        )

    # If C is weak
    if w_pw.get("C", 0) < 0.15:
        arch_recommendations.append(
            "WIRE_MYCELIUM_TO_C: Use mycelium graph (15K shards, 49K edges) for C-path neighbor scoring"
        )

    # Always recommend
    arch_recommendations.append(
        "IMPLEMENT_CONTRASTIVE_LOSS: L = -log(score_pos / sum(score_neg)) for mathematical gradient"
    )
    arch_recommendations.append(
        "ADD_SKIP_CONNECTIONS: score_k += alpha * score_{k-3} for gradient flow to deep shells"
    )
    arch_recommendations.append(
        "WIRE_META_OBSERVER: Connect meta_observer_runtime.py to self-play loop for online 12D feedback"
    )

    # Compute the ideal next-state crystal
    ideal_pw = {}
    for k in ["S", "F", "C", "R"]:
        # Blend: move current weights toward balanced, weighted by training results
        current = w_pw.get(k, 0.25)
        ideal_pw[k] = current * 0.5 + 0.25 * 0.3 + s_pw.get(k, 0.25) * 0.2
    _normalize(ideal_pw)

    return {
        "next_stage": next_stage,
        "current_stage": current_self.stage_name,
        "readiness": current_self.next_stage_readiness,
        "identity_targets": targets,
        "ideal_path_weights": ideal_pw,
        "structural_actions": structural_actions,
        "architecture_recommendations": arch_recommendations,
        "growth_vector": current_self.current_growth_vector,
        "bottleneck": current_self.bottleneck,
        "breakthrough_potential": current_self.breakthrough_potential,
        "training_summary": {
            "weight_crystal": {
                "top1": metrics_weight.selfret_top1,
                "discrimination": metrics_weight.discrimination_global,
                "path_balance": metrics_weight.balance_path_entropy,
                "golden_fit": metrics_weight.symmetry_golden_ratio_fit,
            },
            "self_crystal": {
                "top1": metrics_self.selfret_top1,
                "discrimination": metrics_self.discrimination_global,
                "path_balance": metrics_self.balance_path_entropy,
                "golden_fit": metrics_self.symmetry_golden_ratio_fit,
            },
        },
    }
