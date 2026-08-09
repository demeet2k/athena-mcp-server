from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from athena_mcp.ic10_runtime import GATE_ORDER, IC10Compiler

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "spec" / "IC10_I10_BINDING_V1.json"


def git_head(root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Bind observed IC10 I01-I09 packet to an existing exact-head trusted PROMOTION.2 receipt.")
    parser.add_argument("--observed", default="ic10_observed_witness_v1.json")
    parser.add_argument("--promotion", default="promotion-receipt.json")
    parser.add_argument("--output", default="ic10_i10_binding_receipt_v1.json")
    args = parser.parse_args(argv)

    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    observed = json.loads(Path(args.observed).read_text(encoding="utf-8"))
    promotion_receipt = json.loads(Path(args.promotion).read_text(encoding="utf-8"))
    promotion = dict(promotion_receipt.get("promotion") or {})
    replay = dict(promotion_receipt.get("replay") or {})
    head = git_head(ROOT)

    observed_candidate = dict(observed.get("candidate_packet") or {})
    observed_gate_status = dict(observed.get("gate_status") or {})
    external = dict((promotion.get("gates") or {}).get("external_verification") or {})

    prechecks = {
        "observed_status_match": observed.get("status") == "I01_I09_OBSERVED_I10_UNBOUND_MATCH",
        "observed_exact_head_match": observed.get("checkout_head") == head and observed_candidate.get("git_head") == head,
        "observed_i01_i09_pass": all(observed_gate_status.get(name) == "PASS" for name in GATE_ORDER[:9]),
        "observed_i10_hold": observed_gate_status.get(GATE_ORDER[9]) == "HOLD",
        "observed_first_hold_i10": observed.get("first_hold") == GATE_ORDER[9],
        "observed_nonmutating": observed.get("event_count_before_ic10") == observed.get("event_count_after_ic10"),
        "promotion_receipt_head_match": promotion_receipt.get("git_head") == head,
        "promotion_exact_head_match": promotion.get("git_head") == head,
        "promotion_qualified": promotion.get("status") == "QUALIFIED" and promotion.get("promotion_allowed") is True,
        "promotion_external_verification_trusted": external.get("status") == "PASS" and external.get("trusted") is True,
        "promotion_replay_match": replay.get("match") is True,
        "promotion_replay_qualified": replay.get("stored_status") == "QUALIFIED" and replay.get("recomputed_status") == "QUALIFIED",
        "promotion_run_id_consistent": bool(promotion.get("run_id")) and promotion_receipt.get("promotion", {}).get("run_id") == promotion.get("run_id"),
    }

    candidate = dict(observed_candidate)
    candidate["promotion_certificate"] = promotion
    result_a = IC10Compiler().evaluate(candidate)
    result_b = IC10Compiler().evaluate(candidate)
    gate_status = {gate["gate"]: gate["status"] for gate in result_a["gates"]}

    postchecks = {
        "all_i01_i10_pass": all(gate_status.get(name) == "PASS" for name in GATE_ORDER),
        "chain_satisfied": result_a.get("decision") == "IC10_CHAIN_SATISFIED",
        "no_first_hold": result_a.get("first_hold") is None,
        "ic10_promotion_authority_false": result_a.get("promotion_authority") is False,
        "canonical_emission_authority_preserved": result_a.get("canonical_emission_authority") == "EXISTING_PROMOTION_LEDGER_ONLY",
        "decision_digest_deterministic": result_a.get("decision_digest") == result_b.get("decision_digest"),
        "bound_promotion_run_id_preserved": result_a.get("promotion_run_id") == promotion.get("run_id"),
    }
    checks = {**prechecks, **postchecks}
    ok = all(checks.values())

    receipt = {
        "artifact": contract["artifact"],
        "status": "IC10_I10_BOUND_CHAIN_SATISFIED" if ok else "IC10_I10_BINDING_HOLD",
        "checkout_head": head,
        "observed_artifact": observed.get("artifact"),
        "observed_decision_digest": observed.get("decision_digest"),
        "promotion_receipt_artifact": promotion_receipt.get("artifact"),
        "promotion_run_id": promotion.get("run_id"),
        "promotion_verification_ref": promotion_receipt.get("verification_ref"),
        "checks": checks,
        "gate_status": gate_status,
        "decision": result_a.get("decision"),
        "first_hold": result_a.get("first_hold"),
        "decision_digest": result_a.get("decision_digest"),
        "promotion_authority": result_a.get("promotion_authority"),
        "canonical_emission_authority": result_a.get("canonical_emission_authority"),
        "authority_ceiling": "READ_ONLY_IC10_BINDING_CONSUMES_EXISTING_PROMOTION2_AUTHORITY",
        "evidence_ceiling": [
            "IC10_CHAIN_SATISFIED != CLAIM_TRUTH",
            "IC10_CHAIN_SATISFIED != MERGE_AUTHORITY",
            "IC10_CHAIN_SATISFIED != CANONICAL_INSTALLATION",
            "PROMOTION2_QUALIFIED != WHOLE_CRYSTAL_CERTIFIED",
            "BINDING_JOB_CONSUMES_BUT_DOES_NOT_MINT_PROMOTION_AUTHORITY",
        ],
    }
    Path(args.output).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
