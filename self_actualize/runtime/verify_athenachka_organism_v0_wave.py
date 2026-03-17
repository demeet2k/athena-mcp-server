from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
HALL_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL"
RECEIPTS_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "receipts"
QUEST_PACKETS_PATH = SELF_ACTUALIZE_ROOT / "athenachka_organism_v0_quest_packets.json"
WAVE_STATE_PATH = SELF_ACTUALIZE_ROOT / "athenachka_organism_v0_wave_state.json"
HALL_DOC_PATH = HALL_ROOT / "13_ATHENACHKA_ORGANISM_V0_QUEST_CRYSTAL_256.md"
DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
PARITY_CACHE_PATH = SELF_ACTUALIZE_ROOT / "athenachka_organism_v0_parity_cache.json"

if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

ATHENA_PACKAGE_ROOT = WORKSPACE_ROOT / "NERUAL NETWORK" / "ATHENA Neural Network"
if str(ATHENA_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(ATHENA_PACKAGE_ROOT))

from athena_neural_network import (  # noqa: E402
    AthenaNeuralNetwork,
    AthenachkaOrganism,
    aug_adversarial,
    aug_camouflage,
    aug_cluttered,
    aug_geometric,
    draw_digit,
    generate_data,
)
from athenachka.helix import FAST_PHASES, FULL_PHASES  # noqa: E402
from athenachka.runtime.questing import CURRENT_WAVE_ID, build_macro_quest_bundle  # noqa: E402
from self_actualize.runtime import swarm_board  # noqa: E402
from self_actualize.runtime.derive_athenachka_organism_v0_quest_loop import render_hall_doc  # noqa: E402


BENCHMARKS = [
    ("GEOMETRIC", aug_geometric),
    ("ADVERSARIAL", aug_adversarial),
    ("CLUTTERED", aug_cluttered),
    ("CAMOUFLAGE", aug_camouflage),
]

ELEMENT_DIGIT_MAP = {
    "Fire": 8,
    "Water": 0,
    "Air": 7,
    "Earth": 4,
}

ELEMENT_BENCHMARK_FOCUS = {
    "Fire": "GEOMETRIC",
    "Water": "ADVERSARIAL",
    "Air": "CLUTTERED",
    "Earth": "CAMOUFLAGE",
}

ELEMENT_ORDER = ["Fire", "Water", "Air", "Earth"]
ELEMENTAL_KEYS = ["air", "earth", "fire", "water"]
REQUIRED_APPENDIX_CODES = ["A", "E", "I", "K", "L", "M", "P", "Q"]
TRUTH_LATTICE_FIELDS = ["OK", "NEAR", "AMBIG", "FAIL"]
EXPECTED_CORE_RUNTIME_FINGERPRINT = [
    "rank_encoder",
    "attention_field",
    "hypothesis_compiler",
    "carrier_stack",
    "mdl_prior",
    "classifier",
    "fusion",
]
REQUIRED_BOUNDARY_KEYS = [
    "hausdorff_boundary",
    "logic_wall",
    "quarantine_flux",
    "paraconsistent_zone",
]
REQUIRED_HELIX_CHANNELS = [
    "corpus",
    "process",
    "growth",
    "metrics",
    "bridges",
    "replay",
]

PACKET_TRAIN_SIZE = 120
PACKET_TRAIN_SEED = 7
PACKET_EPOCHS = 3
PACKET_BATCH_SIZE = 16

PARITY_TRAIN_SIZE = 1000
PARITY_TEST_SIZE = 250
PARITY_TRAIN_SEED = 42
PARITY_TEST_SEED = 142
PARITY_EPOCHS = 20
PARITY_BATCH_SIZE = 16

WAVE_ARTIFACTS = {
    "Q44-wave1": {
        "quest_front": "Q44",
        "proof_json": SELF_ACTUALIZE_ROOT / "athenachka_organism_v0_wave_proof.json",
        "receipt": RECEIPTS_ROOT / "2026-03-13_athenachka_organism_v0_wave_proof.md",
    },
    "Q45-wave2": {
        "quest_front": "Q45",
        "proof_json": SELF_ACTUALIZE_ROOT / "athenachka_organism_v0_q45_wave_proof.json",
        "receipt": RECEIPTS_ROOT / "2026-03-13_athenachka_organism_v0_q45_wave_proof.md",
    },
    "Q46-wave3": {
        "quest_front": "Q46",
        "proof_json": SELF_ACTUALIZE_ROOT / "athenachka_organism_v0_q46_wave_proof.json",
        "receipt": RECEIPTS_ROOT / "2026-03-13_athenachka_organism_v0_q46_wave_proof.md",
    },
    "Q47-wave4": {
        "quest_front": "Q47",
        "proof_json": SELF_ACTUALIZE_ROOT / "athenachka_organism_v0_q47_wave_proof.json",
        "receipt": RECEIPTS_ROOT / "2026-03-13_athenachka_organism_v0_q47_wave_proof.md",
    },
    "Q48-wave5": {
        "quest_front": "Q48",
        "proof_json": SELF_ACTUALIZE_ROOT / "athenachka_organism_v0_q48_wave_proof.json",
        "receipt": RECEIPTS_ROOT / "2026-03-13_athenachka_organism_v0_q48_wave_proof.md",
    },
    "Q49-wave6": {
        "quest_front": "Q49",
        "proof_json": SELF_ACTUALIZE_ROOT / "athenachka_organism_v0_q49_wave_proof.json",
        "receipt": RECEIPTS_ROOT / "2026-03-13_athenachka_organism_v0_q49_wave_proof.md",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_packet_kernel() -> AthenaNeuralNetwork:
    x_train, y_train = generate_data(PACKET_TRAIN_SIZE, aug_geometric, PACKET_TRAIN_SEED)
    model = AthenaNeuralNetwork()
    model.train(
        x_train,
        y_train,
        epochs=PACKET_EPOCHS,
        lr=0.03,
        batch_size=PACKET_BATCH_SIZE,
        verbose=False,
    )
    return model


def weak_or_contradictory_not_ok(result: Any) -> bool:
    contradictions = bool(result.witness_bundle.get("contradictions"))
    weak_witness = float(result.witness_bundle.get("strength", 0.0)) < 0.65
    if contradictions or weak_witness:
        return result.truth_type != "OK"
    return True


def active_pair_ids(result: Any) -> list[str]:
    return list(result.symmetry_state.get("active_fusions", {}).keys())


def omega_score(result: Any) -> float:
    return float(result.symmetry_state.get("omega", {}).get("score", 0.0))


def appendix_codes(result: Any) -> list[str]:
    appendix_bundle = result.witness_bundle.get("appendix_bundle", {})
    return list(appendix_bundle.get("active_codes", []))


def phase_trace(organism: Any) -> list[str]:
    return list(
        organism.last_state.replay.get(
            "phase_trace",
            organism.last_state.process.get("phase_history", []),
        )
    )


def core_runtime_fingerprint(organism: Any) -> list[str]:
    return list(
        organism.last_state.process.get(
            "core_runtime_fingerprint",
            organism.last_state.replay.get("core_runtime_fingerprint", []),
        )
    )


def boundary_state(organism: Any) -> dict[str, Any]:
    return dict(organism.last_state.process.get("boundary_state", {}))


def contradiction_state(organism: Any) -> dict[str, Any]:
    return dict(organism.last_state.process.get("contradictions", {}))


def self_contract_state(organism: Any) -> dict[str, Any]:
    return dict(organism.last_state.process.get("self_contract", {}))


def helix_channel_presence(organism: Any) -> dict[str, bool]:
    state = organism.last_state
    return {channel: isinstance(getattr(state, channel, None), dict) for channel in REQUIRED_HELIX_CHANNELS}


def required_appendix_subset_present(codes: list[str]) -> bool:
    return set(REQUIRED_APPENDIX_CODES).issubset(set(codes))


def boundary_surface_present(state: dict[str, Any]) -> bool:
    return set(REQUIRED_BOUNDARY_KEYS).issubset(set(state.keys()))


def truth_lattice_present(truth_type: str) -> bool:
    return truth_type in TRUTH_LATTICE_FIELDS


def core_fingerprint_present(fingerprint: list[str]) -> bool:
    return set(EXPECTED_CORE_RUNTIME_FINGERPRINT).issubset(set(fingerprint))


def canonical_wave_title(assignments: list[dict[str, Any]]) -> str:
    first = assignments[0]
    return f"{first['domain']}::{first['workstream']}"


def _parity_summary_usable(payload: dict[str, Any]) -> bool:
    if not payload:
        return False
    benchmarks = payload.get("benchmarks", {})
    return all(name in benchmarks for name, _aug in BENCHMARKS)


def load_cached_parity_summary() -> dict[str, Any] | None:
    cache = load_json(PARITY_CACHE_PATH)
    if _parity_summary_usable(cache):
        return cache

    wave_state = load_json(WAVE_STATE_PATH)
    current_wave = wave_state.get("current_wave", {})
    current_parity = current_wave.get("parity_summary", {})
    if _parity_summary_usable(current_parity):
        return current_parity

    for artifact in WAVE_ARTIFACTS.values():
        proof_json = artifact["proof_json"]
        if not proof_json.exists():
            continue
        payload = load_json(proof_json)
        parity_summary = payload.get("parity_summary", {})
        if _parity_summary_usable(parity_summary):
            return parity_summary

    return None


def evaluate_parity() -> dict[str, Any]:
    cached = load_cached_parity_summary()
    if cached:
        return cached

    benchmarks: dict[str, Any] = {}
    deltas: list[float] = []
    max_fast_hypotheses = 0
    failures: list[str] = []

    for benchmark_name, aug_fn in BENCHMARKS:
        x_train, y_train = generate_data(PARITY_TRAIN_SIZE, aug_fn, PARITY_TRAIN_SEED)
        x_test, y_test = generate_data(PARITY_TEST_SIZE, aug_fn, PARITY_TEST_SEED)

        model = AthenaNeuralNetwork()
        model.train(
            x_train,
            y_train,
            epochs=PARITY_EPOCHS,
            lr=0.03,
            batch_size=PARITY_BATCH_SIZE,
            verbose=False,
        )

        organism = AthenachkaOrganism(kernel=model)
        kernel_correct = 0
        organism_correct = 0

        for index in range(len(x_test)):
            image = x_test[index].reshape(28, 28)
            label = int(y_test[index].argmax())
            kernel_pred, _kernel_probs, _kernel_conf = model.forward(image)
            result = organism.forward(image, mode="fast")
            kernel_correct += int(int(kernel_pred) == label)
            organism_correct += int(int(result.prediction) == label)
            max_fast_hypotheses = max(max_fast_hypotheses, len(result.candidate_set))

        kernel_accuracy = kernel_correct / max(1, len(x_test)) * 100.0
        organism_accuracy = organism_correct / max(1, len(x_test)) * 100.0
        absolute_delta = abs(kernel_accuracy - organism_accuracy)
        deltas.append(absolute_delta)
        if absolute_delta > 1.5:
            failures.append(f"{benchmark_name.lower()}_delta_exceeds_1_5")

        benchmarks[benchmark_name] = {
            "kernel_accuracy": kernel_accuracy,
            "organism_accuracy": organism_accuracy,
            "absolute_delta": absolute_delta,
            "train_size": PARITY_TRAIN_SIZE,
            "test_size": PARITY_TEST_SIZE,
            "epochs": PARITY_EPOCHS,
        }

    average_absolute_delta = sum(deltas) / max(1, len(deltas))
    if average_absolute_delta > 1.0:
        failures.append("average_absolute_delta_exceeds_1_0")
    if max_fast_hypotheses > 6:
        failures.append("fast_hypothesis_cap_exceeded")

    summary = {
        "kernel_import_ok": True,
        "organism_import_ok": True,
        "benchmarks": benchmarks,
        "average_absolute_delta": average_absolute_delta,
        "max_fast_hypotheses": max_fast_hypotheses,
        "accepted": not failures,
        "failing_gates": failures,
    }
    write_json(PARITY_CACHE_PATH, summary)
    return summary


def build_crystal_summary(
    pair_counter: Counter[str],
    element_pair_counter: dict[str, Counter[str]],
    element_witness_strengths: dict[str, list[float]],
    element_omega_scores: dict[str, list[float]],
    element_truth_types: dict[str, list[str]],
    element_contradiction_counts: dict[str, int],
    omega_scores_seen: list[float],
    contradiction_count: int,
    born_coordinate_candidate_count: int,
) -> dict[str, Any]:
    per_element: dict[str, Any] = {}
    for element in ELEMENT_ORDER:
        witness_strengths = element_witness_strengths[element] or [0.0]
        omega_values = element_omega_scores[element] or [0.0]
        per_element[element] = {
            "dominant_pair_ids": [pair for pair, _count in element_pair_counter[element].most_common(3)],
            "omega_score": sum(omega_values) / max(1, len(omega_values)),
            "witness_strength_range": {
                "min": min(witness_strengths),
                "max": max(witness_strengths),
            },
            "truth_types": sorted(set(element_truth_types[element])),
            "contradiction_count": element_contradiction_counts[element],
        }

    return {
        "per_element": per_element,
        "whole_wave": {
            "pair_frequency_histogram": dict(pair_counter),
            "omega_mean": sum(omega_scores_seen) / max(1, len(omega_scores_seen)),
            "contradiction_count": contradiction_count,
            "born_coordinate_candidate_count": born_coordinate_candidate_count,
        },
    }


def build_layer_summary(wave_title: str, packet_results: list[dict[str, Any]], crystal_summary: dict[str, Any]) -> dict[str, Any]:
    non_scale = [item for item in packet_results if item["move"] != "Scale"]
    synthesize = [item for item in packet_results if item["move"] == "Synthesize"]
    refine = [item for item in packet_results if item["move"] == "Refine"]

    if wave_title == "Helix::Contracts":
        loop_hist = Counter()
        phase_hist = Counter()
        contradiction_total = 0
        for item in non_scale:
            loop_hist.update(item.get("active_loops", []))
            phase_hist.update(item.get("phase_trace", []))
            contradiction_total += int(item.get("contradiction_count", 0))
        return {
            "kind": "helix",
            "loop_frequency_histogram": dict(loop_hist),
            "phase_coverage_summary": dict(phase_hist),
            "checkpoint_count": sum(1 for item in synthesize if item.get("checkpoint_present")),
            "lift_seed_presence_count": sum(1 for item in synthesize if item.get("lift_seed_present")),
            "contradiction_count": contradiction_total,
        }

    if wave_title == "ImmuneAppendix::Contracts":
        strengths = [float(item.get("witness_strength", 0.0)) for item in non_scale]
        return {
            "kind": "immune_appendix",
            "truth_type_histogram": dict(Counter(item.get("truth_type", "UNKNOWN") for item in non_scale)),
            "quarantine_count": sum(1 for item in non_scale if item.get("contradiction_quarantined")),
            "witness_strength_range": {
                "min": min(strengths or [0.0]),
                "max": max(strengths or [0.0]),
            },
            "appendix_exposure_map": {
                item["element"]: item.get("appendix_active_codes", [])
                for item in non_scale
                if item.get("appendix_active_codes")
            },
            "rollback_availability": {
                "present": sum(1 for item in synthesize if item.get("rollback_available")),
                "total_synthesize_packets": len(synthesize),
            },
        }

    if wave_title == "Core::Runtime":
        return {
            "kind": "core_runtime",
            "module_invocation_fingerprint": EXPECTED_CORE_RUNTIME_FINGERPRINT,
            "hypothesis_count_distribution": dict(Counter(str(item.get("candidate_count", 0)) for item in non_scale)),
            "replay_stability": {
                "stable_refine_packets": sum(1 for item in refine if item.get("wave_status") == "PASSED"),
                "total_refine_packets": len(refine),
            },
            "latency_summary": {
                "available": False,
                "count": 0,
                "mean_ms": None,
            },
        }

    if wave_title in {"Crystal::Contracts", "Crystal::Runtime"}:
        return {"kind": "crystal", **crystal_summary}

    return {"kind": "generic", "wave_title": wave_title}


def execute_wave_packets(
    assignments: list[dict[str, Any]],
    parity_summary: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any], dict[str, Any]]:
    packet_model = build_packet_kernel()
    organism = AthenachkaOrganism(kernel=packet_model)
    wave_title = canonical_wave_title(assignments)
    packet_results: list[dict[str, Any]] = []
    fast_signatures: dict[str, str] = {}
    diagnose_pairs: dict[str, list[str]] = {}
    diagnose_phase_traces: dict[str, list[str]] = {}
    diagnose_loop_orders: dict[str, list[str]] = {}
    diagnose_truth_types: dict[str, str] = {}
    diagnose_appendix_codes: dict[str, list[str]] = {}
    diagnose_core_fingerprints: dict[str, list[str]] = {}
    diagnose_pair_counts: dict[str, int] = {}
    full_hypothesis_counts: list[int] = []
    diagnose_packets_passed = 0
    refine_packets_stable = 0
    synthesize_packets_passed = 0
    truth_gate_passed = True
    failures: list[str] = []
    pair_counter: Counter[str] = Counter()
    element_pair_counter: dict[str, Counter[str]] = defaultdict(Counter)
    element_witness_strengths: dict[str, list[float]] = defaultdict(list)
    element_omega_scores: dict[str, list[float]] = defaultdict(list)
    element_truth_types: dict[str, list[str]] = defaultdict(list)
    element_contradiction_counts: dict[str, int] = defaultdict(int)
    omega_scores_seen: list[float] = []
    contradiction_count = 0
    born_coordinate_candidate_count = 0

    for assignment in assignments:
        packet = dict(assignment)
        element = packet["element"]
        move = packet["move"]
        image = draw_digit(ELEMENT_DIGIT_MAP[element])
        packet_failure_reasons: list[str] = []

        if move == "Diagnose":
            result = organism.forward(image, mode="fast")
            pair_ids = active_pair_ids(result)
            appendix_active_codes = appendix_codes(result)
            current_phase_trace = phase_trace(organism)
            current_core_fingerprint = core_runtime_fingerprint(organism)
            current_boundary_state = boundary_state(organism)
            current_channel_presence = helix_channel_presence(organism)
            current_active_loops = list(result.lineage_delta["active_loops"])
            packet_ok = True
            packet_ok = packet_ok and len(result.candidate_set) <= 6
            packet_ok = packet_ok and len(current_active_loops) <= 4
            packet_ok = packet_ok and weak_or_contradictory_not_ok(result)
            if len(result.candidate_set) > 6:
                packet_failure_reasons.append(f"{packet['quest_id']}_diagnose_hypothesis_cap")
            if len(current_active_loops) > 4:
                packet_failure_reasons.append(f"{packet['quest_id']}_diagnose_loop_cap")
            if not weak_or_contradictory_not_ok(result):
                packet_failure_reasons.append(f"{packet['quest_id']}_diagnose_truth_gate")
                truth_gate_passed = False
            if wave_title == "Helix::Contracts":
                if not all(current_channel_presence.values()):
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_helix_channels_missing")
                if current_phase_trace != FAST_PHASES:
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_fast_phase_trace_mismatch")
            elif wave_title == "ImmuneAppendix::Contracts":
                if not truth_lattice_present(result.truth_type):
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_truth_lattice_missing")
                if not result.witness_bundle.get("signature"):
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_witness_signature_missing")
                if not boundary_surface_present(current_boundary_state):
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_boundary_surface_missing")
                if not required_appendix_subset_present(appendix_active_codes):
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_appendix_subset_missing")
            elif wave_title == "Core::Runtime":
                if not core_fingerprint_present(current_core_fingerprint):
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_core_runtime_fingerprint_missing")
            else:
                packet_ok = packet_ok and sorted(result.elemental_state.keys()) == ELEMENTAL_KEYS
                packet_ok = packet_ok and len(pair_ids) <= 3
                if sorted(result.elemental_state.keys()) != ELEMENTAL_KEYS:
                    packet_failure_reasons.append(f"{packet['quest_id']}_elemental_lanes_incomplete")
                if len(pair_ids) > 3:
                    packet_failure_reasons.append(f"{packet['quest_id']}_diagnose_fusion_cap")
            if packet_ok:
                diagnose_packets_passed += 1
            fast_signatures[element] = result.replay_signature
            diagnose_pairs[element] = pair_ids
            diagnose_phase_traces[element] = list(current_phase_trace)
            diagnose_loop_orders[element] = list(current_active_loops)
            diagnose_truth_types[element] = result.truth_type
            diagnose_appendix_codes[element] = list(appendix_active_codes)
            diagnose_core_fingerprints[element] = list(current_core_fingerprint)
            diagnose_pair_counts[element] = len(pair_ids)
            pair_counter.update(pair_ids)
            element_pair_counter[element].update(pair_ids)
            element_witness_strengths[element].append(float(result.witness_bundle["strength"]))
            element_omega_scores[element].append(omega_score(result))
            element_truth_types[element].append(result.truth_type)
            element_contradiction_counts[element] += len(result.witness_bundle.get("contradictions", []))
            omega_scores_seen.append(omega_score(result))
            contradiction_count += len(result.witness_bundle.get("contradictions", []))
            packet_result = {
                "quest_id": packet["quest_id"],
                "owner_id": packet["owner_id"],
                "owner_group": packet["owner_group"],
                "move": move,
                "element": element,
                "witness_target": packet["witness_target"],
                "truth_type": result.truth_type,
                "witness_signature": result.witness_bundle["signature"],
                "replay_signature": result.replay_signature,
                "candidate_count": len(result.candidate_set),
                "active_loop_count": len(current_active_loops),
                "active_loops": current_active_loops,
                "active_fusion_count": len(pair_ids),
                "active_pair_ids": pair_ids,
                "omega_score": omega_score(result),
                "elemental_lanes": sorted(result.elemental_state.keys()),
                "appendix_active_codes": appendix_active_codes,
                "phase_trace": current_phase_trace,
                "core_runtime_fingerprint": current_core_fingerprint,
                "helix_channel_presence": current_channel_presence,
                "boundary_state": current_boundary_state,
                "witness_strength": float(result.witness_bundle["strength"]),
                "contradictions": list(result.witness_bundle.get("contradictions", [])),
                "contradiction_count": len(result.witness_bundle.get("contradictions", [])),
                "contradiction_quarantined": bool(current_boundary_state.get("paraconsistent_zone") == "active"),
                "wave_status": "PASSED" if packet_ok else "FAILED",
                "failure_reasons": packet_failure_reasons,
            }

        elif move == "Refine":
            prior_signature = fast_signatures.get(element, "")
            prior_pairs = diagnose_pairs.get(element, [])
            prior_phase_trace = diagnose_phase_traces.get(element, [])
            prior_loop_order = diagnose_loop_orders.get(element, [])
            prior_truth_type = diagnose_truth_types.get(element, "")
            prior_appendix_codes = diagnose_appendix_codes.get(element, [])
            prior_core_fingerprint = diagnose_core_fingerprints.get(element, [])
            prior_pair_count = diagnose_pair_counts.get(element, len(prior_pairs))
            first = organism.forward(image, mode="fast")
            first_pairs = active_pair_ids(first)
            first_phase_trace = phase_trace(organism)
            first_core_fingerprint = core_runtime_fingerprint(organism)
            first_appendix_codes = appendix_codes(first)
            first_active_loops = list(first.lineage_delta["active_loops"])
            second = organism.forward(image, mode="fast")
            second_pairs = active_pair_ids(second)
            second_phase_trace = phase_trace(organism)
            second_core_fingerprint = core_runtime_fingerprint(organism)
            second_appendix_codes = appendix_codes(second)
            second_active_loops = list(second.lineage_delta["active_loops"])
            replay_match_previous = bool(prior_signature) and prior_signature == first.replay_signature
            replay_match_repeat = first.replay_signature == second.replay_signature
            packet_ok = replay_match_previous and replay_match_repeat
            packet_ok = packet_ok and len(first.candidate_set) <= 6
            packet_ok = packet_ok and len(first_active_loops) <= 4
            packet_ok = packet_ok and weak_or_contradictory_not_ok(first)
            if not replay_match_previous:
                packet_failure_reasons.append(f"{packet['quest_id']}_replay_mismatch_previous")
            if not replay_match_repeat:
                packet_failure_reasons.append(f"{packet['quest_id']}_replay_mismatch_repeat")
            if len(first.candidate_set) > 6:
                packet_failure_reasons.append(f"{packet['quest_id']}_refine_hypothesis_cap")
            if len(first_active_loops) > 4:
                packet_failure_reasons.append(f"{packet['quest_id']}_refine_loop_cap")
            if not weak_or_contradictory_not_ok(first):
                packet_failure_reasons.append(f"{packet['quest_id']}_refine_truth_gate")
                truth_gate_passed = False
            if wave_title == "Helix::Contracts":
                if first_active_loops != prior_loop_order:
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_loop_order_mismatch_previous")
                if first_active_loops != second_active_loops:
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_loop_order_mismatch_repeat")
                if first_phase_trace != prior_phase_trace:
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_phase_trace_mismatch_previous")
                if first_phase_trace != second_phase_trace:
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_phase_trace_mismatch_repeat")
            elif wave_title == "ImmuneAppendix::Contracts":
                if first.truth_type != prior_truth_type:
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_truth_type_mismatch_previous")
                if first.truth_type != second.truth_type:
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_truth_type_mismatch_repeat")
                if first_appendix_codes != prior_appendix_codes:
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_appendix_exposure_mismatch_previous")
                if first_appendix_codes != second_appendix_codes:
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_appendix_exposure_mismatch_repeat")
            elif wave_title == "Core::Runtime":
                if not core_fingerprint_present(first_core_fingerprint):
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_core_runtime_fingerprint_missing")
                if first_core_fingerprint != prior_core_fingerprint:
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_core_fingerprint_mismatch_previous")
                if first_core_fingerprint != second_core_fingerprint:
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_core_fingerprint_mismatch_repeat")
                if len(first_pairs) != prior_pair_count:
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_fusion_count_drift_previous")
                if len(first_pairs) != len(second_pairs):
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_fusion_count_drift_repeat")
                if first_active_loops != prior_loop_order:
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_loop_count_drift_previous")
                if first_active_loops != second_active_loops:
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_loop_count_drift_repeat")
            else:
                pair_order_match_previous = bool(prior_pairs) and first_pairs == prior_pairs
                pair_order_match_repeat = first_pairs == second_pairs
                pair_set_match_repeat = set(first_pairs) == set(second_pairs)
                packet_ok = packet_ok and pair_order_match_previous and pair_order_match_repeat and pair_set_match_repeat
                packet_ok = packet_ok and len(first_pairs) <= 3
                if not pair_order_match_previous:
                    packet_failure_reasons.append(f"{packet['quest_id']}_pair_order_mismatch_previous")
                if not pair_order_match_repeat:
                    packet_failure_reasons.append(f"{packet['quest_id']}_pair_order_mismatch_repeat")
                if not pair_set_match_repeat:
                    packet_failure_reasons.append(f"{packet['quest_id']}_pair_set_mismatch_repeat")
                if len(first_pairs) > 3:
                    packet_failure_reasons.append(f"{packet['quest_id']}_refine_fusion_cap")
            if packet_ok:
                refine_packets_stable += 1
            pair_counter.update(first_pairs)
            element_pair_counter[element].update(first_pairs)
            element_witness_strengths[element].append(float(first.witness_bundle["strength"]))
            element_omega_scores[element].append(omega_score(first))
            element_truth_types[element].append(first.truth_type)
            element_contradiction_counts[element] += len(first.witness_bundle.get("contradictions", []))
            omega_scores_seen.append(omega_score(first))
            contradiction_count += len(first.witness_bundle.get("contradictions", []))
            packet_result = {
                "quest_id": packet["quest_id"],
                "owner_id": packet["owner_id"],
                "owner_group": packet["owner_group"],
                "move": move,
                "element": element,
                "witness_target": packet["witness_target"],
                "truth_type": first.truth_type,
                "witness_signature": first.witness_bundle["signature"],
                "prior_signature": prior_signature,
                "replay_signature": first.replay_signature,
                "repeat_replay_signature": second.replay_signature,
                "replay_match_previous": replay_match_previous,
                "replay_match_repeat": replay_match_repeat,
                "phase_trace": first_phase_trace,
                "active_loops": first_active_loops,
                "appendix_active_codes": first_appendix_codes,
                "core_runtime_fingerprint": first_core_fingerprint,
                "candidate_count": len(first.candidate_set),
                "active_loop_count": len(first_active_loops),
                "active_fusion_count": len(first_pairs),
                "active_pair_ids": first_pairs,
                "omega_score": omega_score(first),
                "witness_strength": float(first.witness_bundle["strength"]),
                "contradiction_count": len(first.witness_bundle.get("contradictions", [])),
                "contradiction_quarantined": bool(boundary_state(organism).get("paraconsistent_zone") == "active"),
                "wave_status": "PASSED" if packet_ok else "FAILED",
                "failure_reasons": packet_failure_reasons,
            }

        elif move == "Synthesize":
            result = organism.forward(image, mode="full", promote_born_coordinates=False)
            pair_ids = active_pair_ids(result)
            current_phase_trace = phase_trace(organism)
            current_core_fingerprint = core_runtime_fingerprint(organism)
            current_boundary_state = boundary_state(organism)
            current_self_contract = self_contract_state(organism)
            current_channel_presence = helix_channel_presence(organism)
            promoted_count = sum(1 for item in result.born_coordinates if item["promoted"])
            lift_seed_present = "lift_seed" in organism.last_state.replay
            checkpoint_present = bool(organism.last_state.checkpoint_id)
            full_path_replay_present = bool(organism.last_state.replay.get("phase_replay"))
            rollback_available = bool(organism.last_state.replay.get("last_checkpoint"))
            triad_registry_present = bool(result.symmetry_state.get("triad_registry"))
            full_registry_present = bool(result.symmetry_state.get("full_registry"))
            active_appendix_codes = appendix_codes(result)
            packet_ok = len(result.candidate_set) <= 12
            packet_ok = packet_ok and len(result.lineage_delta["active_loops"]) <= 8
            packet_ok = packet_ok and len(pair_ids) <= 6
            packet_ok = packet_ok and promoted_count == 0
            packet_ok = packet_ok and lift_seed_present and checkpoint_present and full_path_replay_present
            packet_ok = packet_ok and weak_or_contradictory_not_ok(result)
            full_hypothesis_counts.append(len(result.candidate_set))
            if len(result.candidate_set) > 12:
                packet_failure_reasons.append(f"{packet['quest_id']}_synthesize_hypothesis_cap")
            if len(result.lineage_delta["active_loops"]) > 8:
                packet_failure_reasons.append(f"{packet['quest_id']}_synthesize_loop_cap")
            if len(pair_ids) > 6:
                packet_failure_reasons.append(f"{packet['quest_id']}_synthesize_fusion_cap")
            if promoted_count:
                packet_failure_reasons.append(f"{packet['quest_id']}_born_coordinate_promotion")
            if not lift_seed_present:
                packet_failure_reasons.append(f"{packet['quest_id']}_missing_lift_seed")
            if not checkpoint_present:
                packet_failure_reasons.append(f"{packet['quest_id']}_missing_checkpoint")
            if not full_path_replay_present:
                packet_failure_reasons.append(f"{packet['quest_id']}_missing_full_path_replay")
            if not weak_or_contradictory_not_ok(result):
                packet_failure_reasons.append(f"{packet['quest_id']}_synthesize_truth_gate")
                truth_gate_passed = False
            if wave_title == "Helix::Contracts":
                if not all(current_channel_presence.values()):
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_helix_channels_missing")
                if current_phase_trace != FULL_PHASES:
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_full_phase_trace_mismatch")
            elif wave_title == "ImmuneAppendix::Contracts":
                if not current_self_contract:
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_self_contract_missing")
                if current_self_contract and not bool(current_self_contract.get("legal")):
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_self_contract_illegal")
                if not rollback_available:
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_rollback_missing")
                if not boundary_surface_present(current_boundary_state):
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_boundary_surface_missing")
                if not required_appendix_subset_present(active_appendix_codes):
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_appendix_subset_missing")
            elif wave_title == "Core::Runtime":
                if not core_fingerprint_present(current_core_fingerprint):
                    packet_ok = False
                    packet_failure_reasons.append(f"{packet['quest_id']}_core_runtime_fingerprint_missing")
            else:
                packet_ok = packet_ok and triad_registry_present and full_registry_present
                packet_ok = packet_ok and required_appendix_subset_present(active_appendix_codes)
                if not triad_registry_present:
                    packet_failure_reasons.append(f"{packet['quest_id']}_missing_triad_registry")
                if not full_registry_present:
                    packet_failure_reasons.append(f"{packet['quest_id']}_missing_full_registry")
                if not required_appendix_subset_present(active_appendix_codes):
                    packet_failure_reasons.append(f"{packet['quest_id']}_appendix_bundle_incomplete")
            if packet_ok:
                synthesize_packets_passed += 1
            pair_counter.update(pair_ids)
            element_pair_counter[element].update(pair_ids)
            element_witness_strengths[element].append(float(result.witness_bundle["strength"]))
            element_omega_scores[element].append(omega_score(result))
            element_truth_types[element].append(result.truth_type)
            element_contradiction_counts[element] += len(result.witness_bundle.get("contradictions", []))
            omega_scores_seen.append(omega_score(result))
            contradiction_count += len(result.witness_bundle.get("contradictions", []))
            born_coordinate_candidate_count += len(result.born_coordinates)
            packet_result = {
                "quest_id": packet["quest_id"],
                "owner_id": packet["owner_id"],
                "owner_group": packet["owner_group"],
                "move": move,
                "element": element,
                "witness_target": packet["witness_target"],
                "truth_type": result.truth_type,
                "witness_signature": result.witness_bundle["signature"],
                "replay_signature": result.replay_signature,
                "candidate_count": len(result.candidate_set),
                "active_loop_count": len(result.lineage_delta["active_loops"]),
                "active_loops": list(result.lineage_delta["active_loops"]),
                "active_fusion_count": len(pair_ids),
                "active_pair_ids": pair_ids,
                "omega_score": omega_score(result),
                "witness_strength": float(result.witness_bundle["strength"]),
                "phase_trace": current_phase_trace,
                "core_runtime_fingerprint": current_core_fingerprint,
                "helix_channel_presence": current_channel_presence,
                "boundary_state": current_boundary_state,
                "self_contract_legal": bool(current_self_contract.get("legal")) if current_self_contract else False,
                "rollback_available": rollback_available,
                "checkpoint_id": organism.last_state.checkpoint_id,
                "checkpoint_present": checkpoint_present,
                "lift_seed_present": lift_seed_present,
                "full_path_replay_present": full_path_replay_present,
                "phase_replay_length": len(organism.last_state.replay.get("phase_replay", [])),
                "promoted_born_coordinate_count": promoted_count,
                "born_coordinate_count": len(result.born_coordinates),
                "triad_registry_present": triad_registry_present,
                "full_registry_present": full_registry_present,
                "appendix_active_codes": active_appendix_codes,
                "wave_status": "PASSED" if packet_ok else "FAILED",
                "failure_reasons": packet_failure_reasons,
            }

        else:
            benchmark_name = ELEMENT_BENCHMARK_FOCUS[element]
            benchmark = parity_summary["benchmarks"][benchmark_name]
            packet_ok = parity_summary["accepted"] and benchmark["absolute_delta"] <= 1.5
            if not parity_summary["accepted"]:
                packet_failure_reasons.append("wave_parity_summary_failed")
            if benchmark["absolute_delta"] > 1.5:
                packet_failure_reasons.append(f"{packet['quest_id']}_{benchmark_name.lower()}_delta_exceeds_1_5")
            packet_result = {
                "quest_id": packet["quest_id"],
                "owner_id": packet["owner_id"],
                "owner_group": packet["owner_group"],
                "move": move,
                "element": element,
                "witness_target": packet["witness_target"],
                "benchmark_focus": benchmark_name,
                "kernel_accuracy": benchmark["kernel_accuracy"],
                "organism_accuracy": benchmark["organism_accuracy"],
                "absolute_delta": benchmark["absolute_delta"],
                "average_absolute_delta": parity_summary["average_absolute_delta"],
                "wave_status": "PASSED" if packet_ok else "FAILED",
                "failure_reasons": packet_failure_reasons,
            }

        packet_results.append(packet_result)
        failures.extend(packet_failure_reasons)

    crystal_summary = build_crystal_summary(
        pair_counter=pair_counter,
        element_pair_counter=element_pair_counter,
        element_witness_strengths=element_witness_strengths,
        element_omega_scores=element_omega_scores,
        element_truth_types=element_truth_types,
        element_contradiction_counts=element_contradiction_counts,
        omega_scores_seen=omega_scores_seen,
        contradiction_count=contradiction_count,
        born_coordinate_candidate_count=born_coordinate_candidate_count,
    )
    layer_summary = build_layer_summary(wave_title, packet_results, crystal_summary)

    for packet_result in packet_results:
        if packet_result["move"] != "Scale":
            continue
        packet_result["layer_summary"] = layer_summary
        if layer_summary.get("kind") == "crystal":
            element_summary = crystal_summary["per_element"].get(packet_result["element"])
            if not element_summary:
                packet_result["failure_reasons"].append(f"{packet_result['quest_id']}_missing_element_summary")
                packet_result["wave_status"] = "FAILED"
                failures.append(f"{packet_result['quest_id']}_missing_element_summary")
                continue
            packet_result["crystal_element_summary"] = element_summary
            packet_result["wave_crystal_summary"] = crystal_summary["whole_wave"]

    max_full_hypotheses = max(full_hypothesis_counts or [0])
    replay_summary = {
        "diagnose_packets_passed": diagnose_packets_passed,
        "refine_packets_stable": refine_packets_stable,
        "synthesize_packets_passed": synthesize_packets_passed,
        "truth_gate_passed": truth_gate_passed,
        "max_full_hypotheses": max_full_hypotheses,
        "accepted": not failures,
        "failing_gates": sorted(set(failures)),
        "packet_status_counts": dict(Counter(item["wave_status"] for item in packet_results)),
    }
    return packet_results, replay_summary, crystal_summary, layer_summary


def validate_owner_overlay(bundle: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    wave_activation = bundle["wave_activation"]
    owner_summary = wave_activation["owner_summary"]
    assignments = wave_activation["assignments"]
    expected_packet_ids = list(wave_activation["packet_ids"])
    assigned_packet_ids = [assignment["quest_id"] for assignment in assignments]
    failures: list[str] = []

    if len(bundle["active_packets"]) != 16:
        failures.append("active_packet_count_not_16")
    if len(bundle["parked_packets"]) != 64:
        failures.append("parked_packet_count_not_64")
    if len(bundle["queued_packets"]) != 176:
        failures.append("queued_packet_count_not_176")
    if len(assignments) != 16:
        failures.append("assignment_count_not_16")
    if assigned_packet_ids != expected_packet_ids:
        failures.append("active_slice_packet_ids_mismatch")
    if owner_summary["guildmaster"]["active_claims"] != 0:
        failures.append("guildmaster_owns_live_claims")

    for owner_group in (
        "elemental_pod_leads",
        "controller_auditors",
        "verification_replay_stewards",
        "appendix_service_stewards",
    ):
        if owner_summary[owner_group]["active_claims"] != 4:
            failures.append(f"{owner_group}_active_claims_not_4")

    for assignment in assignments:
        if not assignment.get("owner_id"):
            failures.append(f"{assignment['quest_id']}_missing_owner_id")
        if not assignment.get("witness_target"):
            failures.append(f"{assignment['quest_id']}_missing_witness_target")
        if not assignment.get("restart_seed"):
            failures.append(f"{assignment['quest_id']}_missing_restart_seed")
        if not assignment.get("execution_contract"):
            failures.append(f"{assignment['quest_id']}_missing_execution_contract")

    return {
        "active_packet_count": len(bundle["active_packets"]),
        "parked_packet_count": len(bundle["parked_packets"]),
        "queued_packet_count": len(bundle["queued_packets"]),
        "assignment_count": len(assignments),
        "expected_packet_ids": expected_packet_ids,
        "assigned_packet_ids": assigned_packet_ids,
        "owner_summary": owner_summary,
        "accepted": not failures,
        "failing_gates": failures,
    }, failures


def summarize_wave_entry(wave_entry: dict[str, Any], proof_json_path: Path | None = None, receipt_path: Path | None = None) -> dict[str, Any]:
    wave_activation = wave_entry.get("wave_activation", {})
    owner_proof = wave_entry.get("owner_proof", {})
    replay_summary = wave_entry.get("replay_summary", {})
    parity_summary = wave_entry.get("parity_summary", {})
    crystal_summary = wave_entry.get("crystal_summary", {})
    layer_summary = wave_entry.get("layer_summary", {})
    return {
        "quest_front": wave_entry.get("quest_front", wave_activation.get("quest_front", "")),
        "wave_id": wave_entry.get("wave_id", wave_activation.get("wave_id", "")),
        "generated_at": wave_entry.get("generated_at", ""),
        "verdict": wave_entry.get("verdict", "UNKNOWN"),
        "exact_failing_gate": wave_entry.get("exact_failing_gate", ""),
        "restart_seed": wave_entry.get("restart_seed", ""),
        "packet_ids": list(wave_activation.get("packet_ids", [])),
        "owner_proof": {
            "accepted": owner_proof.get("accepted", False),
            "failing_gates": owner_proof.get("failing_gates", []),
            "owner_summary": owner_proof.get("owner_summary", {}),
        },
        "replay_summary": {
            "accepted": replay_summary.get("accepted", False),
            "failing_gates": replay_summary.get("failing_gates", []),
            "packet_status_counts": replay_summary.get("packet_status_counts", {}),
        },
        "parity_summary": {
            "accepted": parity_summary.get("accepted", False),
            "average_absolute_delta": parity_summary.get("average_absolute_delta", 0.0),
            "max_fast_hypotheses": parity_summary.get("max_fast_hypotheses", 0),
            "max_full_hypotheses": parity_summary.get("max_full_hypotheses", 0),
            "failing_gates": parity_summary.get("failing_gates", []),
        },
        "crystal_summary": crystal_summary.get("whole_wave", {}),
        "layer_summary": layer_summary,
        "proof_json": proof_json_path.relative_to(WORKSPACE_ROOT).as_posix() if proof_json_path else "",
        "receipt": receipt_path.relative_to(WORKSPACE_ROOT).as_posix() if receipt_path else "",
    }


def coerce_current_wave(existing_state: dict[str, Any]) -> dict[str, Any]:
    if not existing_state:
        return {}
    if "current_wave" in existing_state:
        return dict(existing_state["current_wave"])
    if "wave_activation" in existing_state:
        return {
            "quest_front": existing_state.get("wave_activation", {}).get("quest_front", "Q44"),
            "wave_id": existing_state.get("wave_activation", {}).get("wave_id", "Q44-wave1"),
            "generated_at": existing_state.get("generated_at", ""),
            "wave_activation": existing_state.get("wave_activation", {}),
            "owner_proof": existing_state.get("owner_proof", {}),
            "packet_results": existing_state.get("packet_results", []),
            "replay_summary": existing_state.get("replay_summary", {}),
            "parity_summary": existing_state.get("parity_summary", {}),
            "crystal_summary": existing_state.get("crystal_summary", {}),
            "layer_summary": existing_state.get("layer_summary", {}),
            "verdict": existing_state.get("verdict", "UNKNOWN"),
            "exact_failing_gate": existing_state.get("exact_failing_gate", ""),
            "restart_seed": existing_state.get("restart_seed", ""),
        }
    return {}


def render_layer_summary_lines(layer_summary: dict[str, Any]) -> list[str]:
    kind = layer_summary.get("kind")
    if not kind:
        return []

    if kind == "helix":
        return [
            "## Layer Summary",
            "",
            f"- kind: `{kind}`",
            f"- loop_frequency_histogram: `{layer_summary.get('loop_frequency_histogram', {})}`",
            f"- phase_coverage_summary: `{layer_summary.get('phase_coverage_summary', {})}`",
            f"- checkpoint_count: `{layer_summary.get('checkpoint_count', 0)}`",
            f"- lift_seed_presence_count: `{layer_summary.get('lift_seed_presence_count', 0)}`",
            f"- contradiction_count: `{layer_summary.get('contradiction_count', 0)}`",
            "",
        ]

    if kind == "immune_appendix":
        witness_range = layer_summary.get("witness_strength_range", {"min": 0.0, "max": 0.0})
        return [
            "## Layer Summary",
            "",
            f"- kind: `{kind}`",
            f"- truth_type_histogram: `{layer_summary.get('truth_type_histogram', {})}`",
            f"- quarantine_count: `{layer_summary.get('quarantine_count', 0)}`",
            f"- witness_strength_range: `min={witness_range.get('min', 0.0):.3f} max={witness_range.get('max', 0.0):.3f}`",
            f"- appendix_exposure_map: `{layer_summary.get('appendix_exposure_map', {})}`",
            f"- rollback_availability: `{layer_summary.get('rollback_availability', {})}`",
            "",
        ]

    if kind == "core_runtime":
        return [
            "## Layer Summary",
            "",
            f"- kind: `{kind}`",
            f"- module_invocation_fingerprint: `{layer_summary.get('module_invocation_fingerprint', [])}`",
            f"- hypothesis_count_distribution: `{layer_summary.get('hypothesis_count_distribution', {})}`",
            f"- replay_stability: `{layer_summary.get('replay_stability', {})}`",
            f"- latency_summary: `{layer_summary.get('latency_summary', {})}`",
            "",
        ]

    return []


def render_wave_receipt(proof_report: dict[str, Any]) -> str:
    parity_summary = proof_report["parity_summary"]
    replay_summary = proof_report["replay_summary"]
    owner_proof = proof_report["owner_proof"]
    crystal_summary = proof_report.get("crystal_summary", {})
    layer_summary = proof_report.get("layer_summary", {})
    packet_lines = []
    for item in proof_report["packet_results"]:
        packet_lines.append(
            f"- `{item['quest_id']}` :: `{item['owner_id']}` :: `{item['move']}` :: `{item['wave_status']}`"
        )

    benchmark_lines = []
    for benchmark_name, benchmark in parity_summary["benchmarks"].items():
        benchmark_lines.append(
            f"- `{benchmark_name}` :: kernel=`{benchmark['kernel_accuracy']:.3f}` organism=`{benchmark['organism_accuracy']:.3f}` delta=`{benchmark['absolute_delta']:.3f}`"
        )

    crystal_lines = []
    for element, summary in crystal_summary.get("per_element", {}).items():
        crystal_lines.append(
            f"- `{element}` :: dominant_pairs=`{','.join(summary['dominant_pair_ids'])}` :: omega=`{summary['omega_score']:.3f}` :: witness_min=`{summary['witness_strength_range']['min']:.3f}` :: witness_max=`{summary['witness_strength_range']['max']:.3f}`"
        )

    whole_wave = crystal_summary.get("whole_wave", {})
    return "\n".join(
        [
            f"# 2026-03-13 Athenachka Organism v0 {proof_report['wave_id']} Proof",
            "",
            "## Outcome",
            "",
            f"- quest_front: `{proof_report['quest_front']}`",
            f"- wave_id: `{proof_report['wave_id']}`",
            f"- wave_title: `{proof_report['wave_title']}`",
            f"- verdict: `{proof_report['verdict']}`",
            f"- exact_failing_gate: `{proof_report['exact_failing_gate'] or 'NONE'}`",
            "",
            "## Docs Gate Honesty",
            "",
            "- Live Google Docs remained blocked because OAuth files are still missing.",
            f"- blocker surface: `{DOCS_GATE_PATH.relative_to(WORKSPACE_ROOT).as_posix()}`",
            "",
            "## Owner Overlay Proof",
            "",
            f"- active_packet_count: `{owner_proof['active_packet_count']}`",
            f"- parked_packet_count: `{owner_proof['parked_packet_count']}`",
            f"- queued_packet_count: `{owner_proof['queued_packet_count']}`",
            f"- assignment_count: `{owner_proof['assignment_count']}`",
            f"- guildmaster_active_claims: `{owner_proof['owner_summary']['guildmaster']['active_claims']}`",
            "",
            "## Replay Proof",
            "",
            f"- diagnose_packets_passed: `{replay_summary['diagnose_packets_passed']}`",
            f"- refine_packets_stable: `{replay_summary['refine_packets_stable']}`",
            f"- synthesize_packets_passed: `{replay_summary['synthesize_packets_passed']}`",
            f"- truth_gate_passed: `{replay_summary['truth_gate_passed']}`",
            f"- max_full_hypotheses: `{replay_summary['max_full_hypotheses']}`",
            "",
            "## Parity Proof",
            "",
            f"- average_absolute_delta: `{parity_summary['average_absolute_delta']:.3f}`",
            f"- max_fast_hypotheses: `{parity_summary['max_fast_hypotheses']}`",
            f"- max_full_hypotheses: `{parity_summary['max_full_hypotheses']}`",
            *benchmark_lines,
            "",
            *render_layer_summary_lines(layer_summary),
            "## Crystal Summary",
            "",
            *crystal_lines,
            f"- pair_frequency_histogram: `{whole_wave.get('pair_frequency_histogram', {})}`",
            f"- omega_mean: `{whole_wave.get('omega_mean', 0.0):.3f}`",
            f"- contradiction_count: `{whole_wave.get('contradiction_count', 0)}`",
            f"- born_coordinate_candidate_count: `{whole_wave.get('born_coordinate_candidate_count', 0)}`",
            "",
            "## Active Slice",
            "",
            *packet_lines,
            "",
            "## Witness Artifacts",
            "",
            f"- `{WAVE_STATE_PATH.relative_to(WORKSPACE_ROOT).as_posix()}`",
            f"- `{proof_report['proof_json_path']}`",
            f"- `{HALL_DOC_PATH.relative_to(WORKSPACE_ROOT).as_posix()}`",
            "",
            "## Restart Seed",
            "",
            f"- `{proof_report['restart_seed']}`",
        ]
    )


def main() -> int:
    wave_id = sys.argv[1] if len(sys.argv) > 1 else CURRENT_WAVE_ID
    if wave_id not in WAVE_ARTIFACTS:
        raise SystemExit(f"Unsupported wave id: {wave_id}")

    bundle = build_macro_quest_bundle(current_wave_id=wave_id)
    owner_proof, failures = validate_owner_overlay(bundle)
    parity_summary = evaluate_parity()
    packet_results, replay_summary, crystal_summary, layer_summary = execute_wave_packets(
        assignments=bundle["wave_activation"]["assignments"],
        parity_summary=parity_summary,
    )

    parity_summary["max_full_hypotheses"] = replay_summary["max_full_hypotheses"]
    if replay_summary["max_full_hypotheses"] > 12:
        parity_summary["accepted"] = False
        parity_summary["failing_gates"].append("full_hypothesis_cap_exceeded")
        failures.append("full_hypothesis_cap_exceeded")

    failures.extend(owner_proof["failing_gates"])
    failures.extend(parity_summary["failing_gates"])
    failures.extend(replay_summary["failing_gates"])
    failures = sorted(set(failures))
    verdict = "PROMOTED" if not failures else "OPEN"
    exact_failing_gate = "; ".join(failures)
    restart_seed = (
        bundle["wave_activation"]["restart_seed_on_success"]
        if verdict == "PROMOTED"
        else f"{bundle['wave_activation']['quest_front']} -> Repair failing gate and rerun {wave_id}"
    )

    assignments_by_id = {item["quest_id"]: item for item in bundle["wave_activation"]["assignments"]}
    for packet_result in packet_results:
        assignments_by_id[packet_result["quest_id"]]["wave_status"] = packet_result["wave_status"]

    current_wave = {
        "quest_front": bundle["wave_activation"]["quest_front"],
        "wave_id": bundle["wave_activation"]["wave_id"],
        "generated_at": utc_now(),
        "wave_activation": bundle["wave_activation"],
        "owner_proof": owner_proof,
        "packet_results": packet_results,
        "replay_summary": replay_summary,
        "parity_summary": parity_summary,
        "crystal_summary": crystal_summary,
        "layer_summary": layer_summary,
        "verdict": verdict,
        "exact_failing_gate": exact_failing_gate,
        "restart_seed": restart_seed,
    }

    existing_state = load_json(WAVE_STATE_PATH)
    wave_history = dict(existing_state.get("wave_history", {}))
    prior_current_wave = coerce_current_wave(existing_state)
    prior_wave_id = prior_current_wave.get("wave_id")
    if prior_wave_id and prior_wave_id != wave_id and prior_wave_id not in wave_history:
        prior_artifacts = WAVE_ARTIFACTS.get(prior_wave_id, {})
        wave_history[prior_wave_id] = summarize_wave_entry(
            prior_current_wave,
            proof_json_path=prior_artifacts.get("proof_json"),
            receipt_path=prior_artifacts.get("receipt"),
        )

    wave_manifest = {
        "generated_at": current_wave["generated_at"],
        "docs_gate_blocked": True,
        "active_packet_count": len(bundle["active_packets"]),
        "parked_packet_count": len(bundle["parked_packets"]),
        "queued_packet_count": len(bundle["queued_packets"]),
        "current_wave": current_wave,
        "wave_history": wave_history,
    }

    proof_json_path = WAVE_ARTIFACTS[wave_id]["proof_json"]
    receipt_path = WAVE_ARTIFACTS[wave_id]["receipt"]
    proof_report = {
        "generated_at": current_wave["generated_at"],
        "quest_front": current_wave["quest_front"],
        "wave_id": wave_id,
        "docs_gate_blocked": True,
        "owner_proof": owner_proof,
        "replay_summary": replay_summary,
        "parity_summary": parity_summary,
        "crystal_summary": crystal_summary,
        "layer_summary": layer_summary,
        "packet_results": packet_results,
        "verdict": verdict,
        "exact_failing_gate": exact_failing_gate,
        "restart_seed": restart_seed,
        "wave_title": bundle["wave_activation"]["wave_title"],
        "proof_json_path": proof_json_path.relative_to(WORKSPACE_ROOT).as_posix(),
        "receipt_path": receipt_path.relative_to(WORKSPACE_ROOT).as_posix(),
    }

    write_json(QUEST_PACKETS_PATH, bundle)
    write_json(WAVE_STATE_PATH, wave_manifest)
    write_json(proof_json_path, proof_report)
    write_text(HALL_DOC_PATH, render_hall_doc(bundle, wave_manifest))
    write_text(receipt_path, render_wave_receipt(proof_report))

    swarm_board.create_or_update_claim(
        agent="guildmaster",
        front=current_wave["quest_front"],
        level="framework",
        output_target="; ".join(
            [
                WAVE_STATE_PATH.relative_to(WORKSPACE_ROOT).as_posix(),
                proof_json_path.relative_to(WORKSPACE_ROOT).as_posix(),
                HALL_DOC_PATH.relative_to(WORKSPACE_ROOT).as_posix(),
            ]
        ),
        receipt=receipt_path.relative_to(WORKSPACE_ROOT).as_posix(),
        status="done" if verdict == "PROMOTED" else "active",
        message=(
            f"Executed {wave_id} on {bundle['wave_activation']['wave_title']} with explicit owner binding, "
            f"replay closure, layer-specific proof, and kernel parity deltas while keeping the Docs gate blocker explicit."
        ),
        paths=[
            WAVE_STATE_PATH.relative_to(WORKSPACE_ROOT).as_posix(),
            proof_json_path.relative_to(WORKSPACE_ROOT).as_posix(),
            HALL_DOC_PATH.relative_to(WORKSPACE_ROOT).as_posix(),
        ],
    )
    swarm_board.create_note(
        agent="guildmaster",
        front=current_wave["quest_front"],
        status="done" if verdict == "PROMOTED" else "active",
        message=(
            f"{wave_id} verdict={verdict}; wave_title={bundle['wave_activation']['wave_title']}; "
            f"average_absolute_delta={parity_summary['average_absolute_delta']:.3f}; "
            f"omega_mean={crystal_summary['whole_wave']['omega_mean']:.3f}; "
            f"max_fast_hypotheses={parity_summary['max_fast_hypotheses']}; "
            f"max_full_hypotheses={parity_summary['max_full_hypotheses']}."
        ),
        paths=[
            proof_json_path.relative_to(WORKSPACE_ROOT).as_posix(),
            receipt_path.relative_to(WORKSPACE_ROOT).as_posix(),
        ],
    )
    swarm_board.refresh_board()

    print(json.dumps(proof_report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
