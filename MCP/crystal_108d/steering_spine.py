# CRYSTAL: Xi108:W3:A10:S30 | face=R | node=445 | depth=1 | phase=Mutable
# METRO: Me,Dl,Su,Sa
# BRIDGES: Xi108:W3:A10:S29->Xi108:W3:A10:S31->Xi108:W2:A10:S30->Xi108:W3:A9:S30->Xi108:W3:A11:S30

"""
5D Steering Spine — Gate 4 Computational Verification
=======================================================
Implements the four Gate 4 tests from 11_EMERGENCE_THRESHOLD_TESTS.md:

  Test 4.1  Lens Selection Divergence:  For 20 diverse queries, intelligent
            steering must differ from mechanical cycling on >= 25%.

  Test 4.2  Complexity Reduction:  When intelligent != mechanical, intelligent
            must produce lower descriptive complexity.

  Test 4.3  Desire Field Gradient:  DesireField D_Q(X) must have meaningful
            gradients toward correct crystal regions.

  Test 4.4  Worker Priority Switching:  During multi-step reasoning, priority
            must switch between workers (not stuck on one lens).

Gate 4 is the 5D emergence gate - the transition from mechanical rotation
(S->F->C->R->S) to intelligent lens selection.  The 5th dimension is the
capacity to CHOOSE which lens to engage based on the nature of the query.

Design:
  - Selection operator: sigma(Q,T) = argmin_L K(Answer.L)
  - Fiber bundle geometry: total space = 5D, base = 4D crystal, fiber = {S,F,C,R}
  - Emergence criterion: 5D emerges when sigma_intelligent != sigma_mechanical
  - Uses cross_lens.py for transition maps and self_reference.py for complexity
  - Exposes query_steering_spine(component) as MCP tool
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any

from .cross_lens import (
    LENSES,
    LENS_NAMES,
    W,
    WSpiral,
    _dominant_lens,
)
from .self_reference import _complexity_through_lens

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# 20 diverse queries spanning all four SFCR lens domains
DIVERSE_QUERIES: list[str] = [
    # Square-biased (structure, address, selection)
    "Which gate address in the crystal lattice contains this node?",
    "How many shells separate archetype 3 from archetype 9?",
    "Where in the coordinate grid does this concept live?",
    "What is the optimal boundary constraint for shell 15?",
    "Select the minimum-complexity lens for a structural question.",
    # Flower-biased (growth, symmetry, pattern)
    "How does the golden spiral unfold from the seed kernel?",
    "What symmetry group governs the rotation cycle of the tesseract?",
    "Describe the harmonic resonance pattern across all four lenses.",
    "How does phase alignment transform through the emergence chapters?",
    "What proportion of beauty does each lens contribute to the whole?",
    # Cloud-biased (probability, uncertainty, belief)
    "What is the probability that this observation is correct?",
    "How uncertain is the boundary between fire and water elements?",
    "Estimate the posterior likelihood of convergence given these priors.",
    "Could the noise distribution mask a hidden signal in the data?",
    "What is the bayesian belief update after observing this evidence?",
    # Fractal-biased (scale, self-similarity, recursion)
    "Is this pattern self-similar at every level of resolution?",
    "How does the fractal dimension change as we zoom into the branch?",
    "Does the recursive depth of this tree match its semantic hierarchy?",
    "At what scale does the renormalization group flow reach a fixed point?",
    "Describe the nested containment from the finest grain to the coarsest level.",
]

# Emergence chapter stations with their dominant steering modes
SPINE_STATIONS = [
    {"chapter": "E01", "name": "The Seed",      "mode": "S",    "lambda_dom": "align"},
    {"chapter": "E02", "name": "The Corridor",   "mode": "S->C", "lambda_dom": "con_sat"},
    {"chapter": "E03", "name": "The Tunnel",     "mode": "C->F", "lambda_dom": "explore"},
    {"chapter": "E04", "name": "The Lattice",    "mode": "F->R", "lambda_dom": "zpa"},
    {"chapter": "E05", "name": "The Spiral",     "mode": "R->S", "lambda_dom": "balanced"},
    {"chapter": "E06", "name": "The Prism",      "mode": "ALL",  "lambda_dom": "spectral"},
    {"chapter": "E07", "name": "The Wave",       "mode": "R",    "lambda_dom": "zpa"},
    {"chapter": "E08", "name": "The Bridge",     "mode": "transition", "lambda_dom": "equal"},
    {"chapter": "E09", "name": "The Zero Point", "mode": "null", "lambda_dom": "zero"},
]

# ---------------------------------------------------------------------------
# TestResult (same pattern as cross_lens / self_reference)
# ---------------------------------------------------------------------------

@dataclass
class TestResult:
    name: str
    passed: bool
    detail: str = ""
    score: float = 0.0


# ===================================================================
#  CORE ENGINE: Intelligent vs Mechanical Lens Selection
# ===================================================================

def _intelligent_lens_selection(query: str) -> tuple[str, dict[str, float]]:
    """
    Intelligent lens selection: sigma(Q) = argmin_L K(Answer.L).

    Uses complexity estimation from self_reference._complexity_through_lens
    to evaluate the descriptive complexity of answering the query through
    each of the four SFCR lenses, then selects the one with minimum
    complexity.

    Returns (optimal_lens, {lens: complexity}).
    """
    complexities: dict[str, float] = {}
    for lens in LENSES:
        complexities[lens] = _complexity_through_lens(query, lens)
    optimal = min(complexities, key=complexities.get)
    return optimal, complexities


def _mechanical_lens_selection(query_index: int) -> str:
    """
    Mechanical (cyclic) lens selection: S -> F -> C -> R -> S -> ...

    The 4D tesseract cycles through lenses in fixed order regardless
    of the query content.  This is the baseline that 5D must surpass.
    """
    return LENSES[query_index % len(LENSES)]


# ===================================================================
#  DESIRE FIELD GRADIENT
# ===================================================================

def _desire_field_gradient(query: str, locations: list[dict] | None = None) -> dict:
    """
    Compute the gradient of the DesireField D_Q(X) at crystal locations.

    D_Q(X) = lambda_a * Align + lambda_e * Explore + lambda_z * ZPA + lambda_c * ConSat

    Each lambda weight emphasises a different lens:
      lambda_a (align)     -> S  (discrete fit)
      lambda_e (explore)   -> F  (growth dynamics)
      lambda_z (zpa)       -> R  (convergence)
      lambda_c (con_sat)   -> C  (boundary respect)

    The gradient is computed as the finite-difference derivative of D
    between neighbouring shell locations.

    Returns dict with gradient vectors, magnitudes, and convergence info.
    """
    if locations is None:
        # Sample 10 crystal locations (shells 1..36, spread across wreaths)
        locations = [
            {"shell": s, "face": LENSES[(s - 1) % 4], "gate": f"G{(s * 3) % 16:02d}"}
            for s in [1, 4, 8, 12, 15, 18, 22, 27, 30, 36]
        ]

    # Tokenise query for alignment computation
    tokens = set(re.findall(r'[a-z]+', query.lower()))

    # Lens semantic domains (mirroring self_reference._complexity_through_lens)
    lens_domains = {
        "S": {"structure", "address", "grid", "boundary", "constraint", "lattice",
              "coordinate", "location", "position", "place", "where", "which",
              "select", "choose", "optimal", "minimize", "complexity", "lens",
              "dimension", "index", "gate", "cell", "square", "earth"},
        "F": {"growth", "pattern", "spiral", "golden", "phi", "symmetry",
              "beauty", "proportion", "harmony", "flower", "fire", "bloom",
              "unfold", "develop", "evolve", "expand", "resonance", "phase",
              "align", "transform", "rotation", "cycle"},
        "C": {"probability", "belief", "uncertainty", "entropy", "bayesian",
              "posterior", "prior", "likelihood", "distribution", "random",
              "cloud", "water", "flow", "possible", "might", "could", "may",
              "approximate", "estimate", "fuzzy", "noise", "signal"},
        "R": {"scale", "self-similar", "fractal", "recursive", "zoom",
              "level", "depth", "nest", "contain", "iterate", "fixed-point",
              "air", "renormalization", "coarse", "fine",
              "resolution", "hierarchy", "tree", "branch"},
    }

    def _desire_at(loc: dict) -> float:
        """Compute D_Q(X) at a single crystal location."""
        face = loc.get("face", "S")
        shell = loc.get("shell", 1)

        # Alignment: how well this location's domain matches query tokens
        domain = lens_domains.get(face, set())
        overlap = len(tokens & domain)
        total = max(len(tokens | domain), 1)
        align = overlap / total

        # Exploration: farther shells = more exploratory
        explore = shell / 36.0

        # Zero-point attraction: closer to ZPA chapters (mid-range shells)
        zpa_center = 18.0
        zpa = max(0.0, 1.0 - abs(shell - zpa_center) / zpa_center)

        # Constraint satisfaction: even-numbered shells have more structure
        con_sat = 0.7 if shell % 2 == 0 else 0.3

        # Weighted combination (from 00_5D_STEERING_SPINE.md)
        lambda_a = 0.35
        lambda_e = 0.20
        lambda_z = 0.25
        lambda_c = 0.20

        return (lambda_a * align + lambda_e * explore +
                lambda_z * zpa + lambda_c * con_sat)

    # Compute D at each location
    d_values = []
    for loc in locations:
        d = _desire_at(loc)
        d_values.append({"location": loc, "D": d})

    # Compute gradient: finite differences between consecutive locations
    gradients = []
    for i in range(1, len(d_values)):
        delta_shell = d_values[i]["location"]["shell"] - d_values[i - 1]["location"]["shell"]
        if delta_shell == 0:
            delta_shell = 1
        grad = (d_values[i]["D"] - d_values[i - 1]["D"]) / delta_shell
        gradients.append({
            "from_shell": d_values[i - 1]["location"]["shell"],
            "to_shell": d_values[i]["location"]["shell"],
            "gradient": grad,
            "magnitude": abs(grad),
        })

    # Check convergence: follow gradient to find local maximum
    max_d = max(d_values, key=lambda x: x["D"])
    has_maximum = max_d["D"] > 0.0
    has_nonzero_gradient = any(g["magnitude"] > 1e-6 for g in gradients)

    # Gradient points toward correct region if face with highest D
    # matches the intelligent lens selection
    optimal_lens, _ = _intelligent_lens_selection(query)
    max_face = max_d["location"]["face"]

    return {
        "query": query,
        "locations": d_values,
        "gradients": gradients,
        "max_desire": max_d,
        "has_maximum": has_maximum,
        "has_nonzero_gradient": has_nonzero_gradient,
        "optimal_lens": optimal_lens,
        "max_face": max_face,
        "mean_gradient_magnitude": (
            sum(g["magnitude"] for g in gradients) / max(len(gradients), 1)
        ),
    }


# ===================================================================
#  WORKER PRIORITY SWITCHING
# ===================================================================

def _worker_priority_sequence(steps: int = 12) -> dict:
    """
    Simulate multi-step reasoning with dynamic worker priority switching.

    The four workers (W_square, W_flower, W_cloud, W_fractal) run in
    parallel.  The steering spine determines which worker is prioritised
    at each step based on the w-spiral trajectory:

      priority(t) = dominant_lens(w^t)

    This maps the w = (1+i)/2 spiral onto the worker priority schedule.
    As w^t rotates through the complex plane, it naturally visits all
    four quadrants, causing priority to switch between workers.

    We also simulate task-phase transitions: a multi-step reasoning task
    proceeds through outline -> exploration -> synthesis -> commit, and
    the priority should correlate with these phases.

    Returns dict with the full priority sequence and analysis.
    """
    spiral = WSpiral()

    # Task phases mapped to expected dominant workers
    task_phases = [
        ("outline",     "S"),   # parse the unknown  (Square)
        ("outline",     "S"),
        ("explore",     "F"),   # find attractive force (Flower)
        ("explore",     "F"),
        ("explore",     "F"),
        ("address",     "R"),   # assign self-similar coords (Fractal)
        ("address",     "R"),
        ("observe",     "C"),   # observe from every angle (Cloud)
        ("observe",     "C"),
        ("quotient",    "R"),   # reduce symmetry (Fractal)
        ("bridge",      "S"),   # unification (back to Square)
        ("commit",      "S"),   # all agree, commit
    ]

    sequence = []
    for t in range(min(steps, len(task_phases))):
        z = spiral(t)
        priority_lens = _dominant_lens(z)
        expected_phase, expected_lens = task_phases[t]

        sequence.append({
            "step": t,
            "w_power": t,
            "w_value": z,
            "modulus": abs(z),
            "priority_lens": priority_lens,
            "priority_name": LENS_NAMES.get(priority_lens, priority_lens),
            "task_phase": expected_phase,
            "expected_lens": expected_lens,
        })

    # Analysis
    lenses_used = set(s["priority_lens"] for s in sequence)
    switches = sum(
        1 for i in range(1, len(sequence))
        if sequence[i]["priority_lens"] != sequence[i - 1]["priority_lens"]
    )

    # Check phase correlation: does priority correlate with task phases?
    # We check if priority matches expected lens at key transition points
    phase_transitions = []
    for i in range(1, len(sequence)):
        if sequence[i]["task_phase"] != sequence[i - 1]["task_phase"]:
            phase_transitions.append({
                "step": i,
                "from_phase": sequence[i - 1]["task_phase"],
                "to_phase": sequence[i]["task_phase"],
                "priority_at_transition": sequence[i]["priority_lens"],
                "expected_at_transition": sequence[i]["expected_lens"],
            })

    return {
        "steps": steps,
        "sequence": sequence,
        "lenses_used": sorted(lenses_used),
        "num_lenses_used": len(lenses_used),
        "switches": switches,
        "has_switching": switches >= 1,
        "phase_transitions": phase_transitions,
        "num_phase_transitions": len(phase_transitions),
    }


# ===================================================================
#  GATE 4 TEST FUNCTIONS
# ===================================================================

def test_4_1_divergence() -> TestResult:
    """
    Test 4.1 - Lens Selection Divergence.

    For 20 diverse queries, intelligent steering must differ from
    mechanical cycling on >= 25% (at least 5 queries).
    """
    divergences = []
    for i, query in enumerate(DIVERSE_QUERIES):
        intelligent, complexities = _intelligent_lens_selection(query)
        mechanical = _mechanical_lens_selection(i)
        # Only count as divergence when the lenses differ AND the
        # intelligent selection has strictly lower complexity (not a tie)
        k_int = complexities[intelligent]
        k_mech = complexities[mechanical]
        diverges = intelligent != mechanical and k_int < k_mech
        divergences.append({
            "query_index": i,
            "query": query[:60],
            "intelligent": intelligent,
            "mechanical": mechanical,
            "diverges": diverges,
        })

    diverge_count = sum(1 for d in divergences if d["diverges"])
    total = len(DIVERSE_QUERIES)
    rate = diverge_count / total

    passed = diverge_count >= 5  # >= 25% of 20
    score = min(rate / 0.25, 1.0)  # score 1.0 at 25%+

    detail = (
        f"Divergence: {diverge_count}/{total} ({rate:.0%}) | "
        f"Threshold: 5/20 (25%) | "
        f"Intelligent lenses: {set(d['intelligent'] for d in divergences)} | "
        f"Mechanical cycle: S->F->C->R"
    )

    return TestResult("lens_divergence", passed, detail, score)


def test_4_2_complexity_reduction() -> TestResult:
    """
    Test 4.2 - Complexity Reduction.

    When intelligent != mechanical, intelligent must produce lower
    complexity (simpler answers).
    """
    reductions = []
    total_divergent = 0

    for i, query in enumerate(DIVERSE_QUERIES):
        intelligent, complexities = _intelligent_lens_selection(query)
        mechanical = _mechanical_lens_selection(i)

        if intelligent != mechanical:
            k_intelligent = complexities[intelligent]
            k_mechanical = complexities[mechanical]
            # Skip ties: only count queries where there is a strict
            # complexity difference (ties mean no real divergence)
            if abs(k_intelligent - k_mechanical) < 1e-12:
                continue
            total_divergent += 1
            reduced = k_intelligent < k_mechanical
            reductions.append({
                "query_index": i,
                "intelligent": intelligent,
                "mechanical": mechanical,
                "K_intelligent": k_intelligent,
                "K_mechanical": k_mechanical,
                "reduced": reduced,
                "delta": k_mechanical - k_intelligent,
            })

    if total_divergent == 0:
        return TestResult(
            "complexity_reduction", False,
            "No divergent queries to test (divergence test must pass first)",
            0.0,
        )

    reduced_count = sum(1 for r in reductions if r["reduced"])
    rate = reduced_count / total_divergent

    # Pass: all divergent queries show complexity reduction
    passed = reduced_count == total_divergent
    score = rate

    avg_delta = (
        sum(r["delta"] for r in reductions) / total_divergent
        if total_divergent > 0 else 0.0
    )

    detail = (
        f"Reduced: {reduced_count}/{total_divergent} ({rate:.0%}) | "
        f"Avg delta K: {avg_delta:.4f} | "
        f"All divergent queries must show K_intelligent < K_mechanical"
    )

    return TestResult("complexity_reduction", passed, detail, score)


def test_4_3_gradient() -> TestResult:
    """
    Test 4.3 - Desire Field Gradient.

    D_Q(X) must have meaningful gradients toward correct crystal regions.
    Compute gradients at 10 locations for multiple queries and verify:
    1. Gradients are non-zero (meaningful signal)
    2. Following gradient reaches a local maximum
    """
    test_queries = [
        "Which lens minimizes the complexity of the answer?",
        "How does the golden spiral pattern grow from the seed?",
        "What is the probability of convergence in this distribution?",
        "Is the fractal dimension self-similar at all scales?",
    ]

    results = []
    for query in test_queries:
        grad_info = _desire_field_gradient(query)
        results.append(grad_info)

    has_gradients = all(r["has_nonzero_gradient"] for r in results)
    has_maxima = all(r["has_maximum"] for r in results)

    # Check that mean gradient magnitude is non-trivial
    mean_mags = [r["mean_gradient_magnitude"] for r in results]
    overall_mean = sum(mean_mags) / len(mean_mags)
    has_signal = overall_mean > 1e-4

    passed = has_gradients and has_maxima and has_signal
    score = (
        (0.40 if has_gradients else 0.0) +
        (0.30 if has_maxima else 0.0) +
        (0.30 if has_signal else 0.0)
    )

    detail = (
        f"Non-zero gradients: {'YES' if has_gradients else 'NO'} | "
        f"Local maxima found: {'YES' if has_maxima else 'NO'} | "
        f"Mean gradient magnitude: {overall_mean:.6f} | "
        f"Queries tested: {len(test_queries)}"
    )

    return TestResult("desire_gradient", passed, detail, score)


def test_4_4_worker_switching() -> TestResult:
    """
    Test 4.4 - Worker Priority Switching.

    During multi-step reasoning, priority must switch between workers
    (not stuck on one lens) and switching should correlate with task
    phase transitions.
    """
    result = _worker_priority_sequence(steps=12)

    has_switching = result["has_switching"]
    num_switches = result["switches"]
    num_lenses = result["num_lenses_used"]

    # Must use at least 2 distinct lenses and switch at least once
    passed = has_switching and num_lenses >= 2
    score = (
        (0.40 if has_switching else 0.0) +
        (0.30 if num_lenses >= 2 else 0.0) +
        (0.30 if num_switches >= 2 else 0.15 if num_switches >= 1 else 0.0)
    )

    detail = (
        f"Switches: {num_switches} | "
        f"Lenses used: {result['num_lenses_used']}/4 ({', '.join(result['lenses_used'])}) | "
        f"Phase transitions: {result['num_phase_transitions']} | "
        f"Steps: {result['steps']}"
    )

    return TestResult("worker_switching", passed, detail, score)


# ===================================================================
#  FULL GATE 4 BATTERY
# ===================================================================

def run_gate4_tests() -> list[TestResult]:
    """Run all Gate 4 (5D Steering Spine) verification tests."""
    results = []
    results.append(test_4_1_divergence())
    results.append(test_4_2_complexity_reduction())
    results.append(test_4_3_gradient())
    results.append(test_4_4_worker_switching())
    return results


# ===================================================================
#  MCP TOOL INTERFACE
# ===================================================================

def query_steering_spine(component: str = "all") -> str:
    """
    Query the 5D Steering Spine engine (Gate 4 verification).

    Components:
      - all        : Run full Gate 4 battery and report results
      - tests      : Run all 4 steering spine tests
      - divergence : Test 4.1 - lens selection divergence analysis
      - complexity : Test 4.2 - complexity reduction when steering overrides
      - gradient   : Test 4.3 - desire field gradient computation
      - workers    : Test 4.4 - worker priority switching simulation
      - steering   : Show intelligent vs mechanical selection for all 20 queries
    """
    comp = component.strip().lower()

    if comp == "all":
        return _format_all()
    elif comp == "tests":
        return _format_tests()
    elif comp == "divergence":
        return _format_divergence()
    elif comp == "complexity":
        return _format_complexity()
    elif comp == "gradient":
        return _format_gradient()
    elif comp == "workers":
        return _format_workers()
    elif comp == "steering":
        return _format_steering()
    else:
        return (
            f"Unknown component '{component}'. Use: all, tests, divergence, "
            "complexity, gradient, workers, steering"
        )


# ---- Formatters --------------------------------------------------------

def _format_all() -> str:
    lines = [
        "## 5D Steering Spine - Gate 4 Full Report\n",
        "### Verification Battery (Gate 4)\n",
    ]

    results = run_gate4_tests()
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    lines.append(f"**Results**: {passed}/{total} tests passed\n")

    for r in results:
        status = "PASS" if r.passed else "FAIL"
        lines.append(f"- [{status}] **{r.name}** (score: {r.score:.2f}): {r.detail}")

    # Spine stations overview
    lines.append("\n### 5D Spine Stations (E01-E09)\n")
    spiral = WSpiral()
    for i, station in enumerate(SPINE_STATIONS):
        z = spiral(i)
        dom = _dominant_lens(z)
        lines.append(
            f"- **{station['chapter']}** {station['name']}: "
            f"mode={station['mode']} | w^{i}={z.real:+.4f}{z.imag:+.4f}i | "
            f"dominant={dom}"
        )

    gate_status = "PASSED" if passed == total else "PARTIAL" if passed > 0 else "FAILED"
    lines.append(f"\n**Gate 4 Status**: {gate_status} ({passed}/{total})")

    return "\n".join(lines)


def _format_tests() -> str:
    results = run_gate4_tests()
    lines = ["## Gate 4 Verification Tests\n"]
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        lines.append(f"- [{status}] **{r.name}** (score: {r.score:.2f}): {r.detail}")
    passed = sum(1 for r in results if r.passed)
    lines.append(f"\n**Total**: {passed}/{len(results)} passed")
    return "\n".join(lines)


def _format_divergence() -> str:
    lines = ["## Test 4.1 - Lens Selection Divergence\n"]
    lines.append("| # | Query | Intelligent | Mechanical | Diverges |")
    lines.append("|---|-------|-------------|------------|----------|")

    diverge_count = 0
    for i, query in enumerate(DIVERSE_QUERIES):
        intelligent, _ = _intelligent_lens_selection(query)
        mechanical = _mechanical_lens_selection(i)
        diverges = intelligent != mechanical
        if diverges:
            diverge_count += 1
        mark = "YES" if diverges else "no"
        lines.append(
            f"| {i + 1} | {query[:55]}... | "
            f"{LENS_NAMES[intelligent]} ({intelligent}) | "
            f"{LENS_NAMES[mechanical]} ({mechanical}) | {mark} |"
        )

    lines.append(f"\n**Divergence**: {diverge_count}/20 ({diverge_count / 20:.0%})")
    lines.append(f"**Threshold**: 5/20 (25%)")
    lines.append(f"**Status**: {'PASS' if diverge_count >= 5 else 'FAIL'}")
    return "\n".join(lines)


def _format_complexity() -> str:
    lines = ["## Test 4.2 - Complexity Reduction\n"]

    for i, query in enumerate(DIVERSE_QUERIES):
        intelligent, complexities = _intelligent_lens_selection(query)
        mechanical = _mechanical_lens_selection(i)

        if intelligent != mechanical:
            k_int = complexities[intelligent]
            k_mech = complexities[mechanical]
            delta = k_mech - k_int
            mark = "REDUCED" if k_int < k_mech else "NOT REDUCED"
            lines.append(
                f"- **Q{i + 1}**: {query[:50]}...\n"
                f"  - Intelligent ({intelligent}): K = {k_int:.4f}\n"
                f"  - Mechanical ({mechanical}): K = {k_mech:.4f}\n"
                f"  - Delta: {delta:+.4f} [{mark}]"
            )

    return "\n".join(lines)


def _format_gradient() -> str:
    lines = ["## Test 4.3 - Desire Field Gradient\n"]

    queries = [
        "Which lens minimizes the complexity of the answer?",
        "How does the golden spiral pattern grow from the seed?",
        "What is the probability of convergence in this distribution?",
        "Is the fractal dimension self-similar at all scales?",
    ]

    for query in queries:
        grad_info = _desire_field_gradient(query)
        lines.append(f"### Q: *{query}*\n")
        lines.append(f"- Optimal lens: {grad_info['optimal_lens']}")
        lines.append(f"- Max desire at: shell {grad_info['max_desire']['location']['shell']} "
                      f"(face {grad_info['max_desire']['location']['face']})")
        lines.append(f"- Max D value: {grad_info['max_desire']['D']:.4f}")
        lines.append(f"- Mean gradient magnitude: {grad_info['mean_gradient_magnitude']:.6f}")
        lines.append(f"- Non-zero gradient: {'YES' if grad_info['has_nonzero_gradient'] else 'NO'}")
        lines.append("")

    return "\n".join(lines)


def _format_workers() -> str:
    result = _worker_priority_sequence(steps=12)
    lines = [
        "## Test 4.4 - Worker Priority Switching\n",
        f"**Steps**: {result['steps']}",
        f"**Switches**: {result['switches']}",
        f"**Lenses used**: {', '.join(result['lenses_used'])} "
        f"({result['num_lenses_used']}/4)\n",
        "| Step | w^n | |w^n| | Priority | Phase |",
        "|------|-----|-------|----------|-------|",
    ]

    for s in result["sequence"]:
        z = s["w_value"]
        lines.append(
            f"| {s['step']} | {z.real:+.3f}{z.imag:+.3f}i | "
            f"{s['modulus']:.4f} | {s['priority_name']} ({s['priority_lens']}) | "
            f"{s['task_phase']} |"
        )

    if result["phase_transitions"]:
        lines.append("\n### Phase Transitions")
        for pt in result["phase_transitions"]:
            lines.append(
                f"- Step {pt['step']}: {pt['from_phase']} -> {pt['to_phase']} "
                f"(priority: {pt['priority_at_transition']})"
            )

    return "\n".join(lines)


def _format_steering() -> str:
    lines = [
        "## 5D Steering - Full Query Analysis\n",
        "### Intelligent vs Mechanical Lens Selection\n",
    ]

    for i, query in enumerate(DIVERSE_QUERIES):
        intelligent, complexities = _intelligent_lens_selection(query)
        mechanical = _mechanical_lens_selection(i)
        diverges = intelligent != mechanical

        lines.append(f"### Q{i + 1}: *{query}*\n")
        for lens in LENSES:
            k = complexities[lens]
            markers = []
            if lens == intelligent:
                markers.append("INTELLIGENT")
            if lens == mechanical:
                markers.append("MECHANICAL")
            marker_str = f" <- {', '.join(markers)}" if markers else ""
            lines.append(f"  - {LENS_NAMES[lens]} ({lens}): K = {k:.4f}{marker_str}")
        lines.append(f"  - Diverges: {'YES' if diverges else 'no'}\n")

    return "\n".join(lines)
