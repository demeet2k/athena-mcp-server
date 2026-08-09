from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from athena_mcp.bootstrap import bootstrap
from athena_mcp.core import AthenaCore
from athena_mcp.crystal_runtime import CrystalRuntime
from athena_mcp.h6_root import H6RootRuntime
from athena_mcp.ic10_runtime import GATE_ORDER, IC10Compiler
from athena_mcp.store import Store

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "spec" / "IC10_OBSERVED_WITNESS_V1.json"
COMPILER_SPEC_PATH = ROOT / "spec" / "IC10_COMPILER_V1.json"
RUNTIME_PATH = ROOT / "athena_mcp" / "ic10_runtime.py"
H6_PATH = ROOT / "athena_mcp" / "h6_root.py"
OUTPUT = Path("ic10_observed_witness_v1.json")


def blob_sha(path: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", f"HEAD:{path}"], text=True
    ).strip()


def checkout_head() -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
    ).strip()


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    compiler_spec_text = COMPILER_SPEC_PATH.read_text(encoding="utf-8")
    compiler_spec = json.loads(compiler_spec_text)
    runtime_text = RUNTIME_PATH.read_text(encoding="utf-8")
    h6_text = H6_PATH.read_text(encoding="utf-8")
    ast.parse(runtime_text)
    ast.parse(h6_text)

    head = checkout_head()
    spec_blob = blob_sha("spec/IC10_COMPILER_V1.json")
    runtime_blob = blob_sha("athena_mcp/ic10_runtime.py")
    h6_blob = blob_sha("athena_mcp/h6_root.py")
    source_refs = [
        f"GIT_BLOB:spec/IC10_COMPILER_V1.json:{spec_blob}",
        f"GIT_BLOB:athena_mcp/ic10_runtime.py:{runtime_blob}",
        f"GIT_BLOB:athena_mcp/h6_root.py:{h6_blob}",
    ]

    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        store = Store(tmp.name)
        try:
            core = AthenaCore(store)
            bootstrap(core)
            crystal = CrystalRuntime(core)
            h6 = H6RootRuntime(core, crystal)
            ic10 = IC10Compiler()

            target = crystal.crystallize_output(
                {
                    "kind": "RUNTIME_CONSTITUTIONAL_COMPILER",
                    "domain": "IC10",
                    "verb": "QUALIFY",
                    "object_name": "IC10_COMPILER_V1",
                    "method": "EXACT_REPOSITORY_SOURCE",
                    "input_contract": {"candidate": "typed gate inputs"},
                    "output_contract": {"decision": "IC10_CHAIN_SATISFIED|IC10_HOLD"},
                },
                compiler_spec_text,
                f"git://spec/IC10_COMPILER_V1.json@{head}",
                "IC10.OBSERVED.WITNESS",
                "ic10-observed",
                1,
                carrier="application/json",
            )
            oid = target["manifest"]["identity"]["OID"]
            vid = target["manifest"]["identity"]["VID"]

            identity = h6.identity_decide(oid, candidate_oids=[oid])

            forward = crystal.register_transform(
                "KC144", "JSPACE", status="TESTED", mode="ISOMORPHISM",
                program={"op": "identity"}, metric={"type": "EXACT"},
            )
            reverse = crystal.register_transform(
                "JSPACE", "KC144", status="TESTED", mode="ISOMORPHISM",
                program={"op": "identity"}, metric={"type": "EXACT"},
            )
            bridge = h6.bridge_decide(
                forward["transform_id"],
                {
                    "preserved_invariants": ["IDENTITY", "TYPE"],
                    "lost_invariants": [],
                    "validity_corridor": {
                        "type": "EXACT_REPOSITORY_MECHANISM_WITNESS",
                        "git_head": head,
                    },
                    "evidence_refs": source_refs,
                    "required_authority": ["READ_ONLY_PROVIDER_WITNESS"],
                    "reverse_transform_id": reverse["transform_id"],
                    "counterexamples": ["OUTSIDE_EXACT_REPOSITORY_WITNESS_SCOPE"],
                },
            )

            evidence = h6.evidence_decide(
                {
                    "claim_id": "CLAIM.IC10.I01_I09.MECHANISM",
                    "evidence_floor": {"minimum_independent": 1},
                },
                [
                    {
                        "evidence_id": "IC10.SOURCE.1",
                        "source_id": "GIT.IC10.COMPILER.SPEC",
                        "source_revision": spec_blob,
                        "independence_group": "IC10.REPOSITORY.MECHANISM",
                        "support_direction": "SUPPORT",
                        "freshness": "CURRENT",
                    },
                ],
            )

            prompt_digest = sha256_text(compiler_spec_text)
            query_args = {
                "request": "Observe IC10 I01-I09 constitutional gate prerequisites",
                "goal": "Produce a deterministic read-only observed witness with I10 deliberately unbound",
                "identity_targets": [oid],
                "semantic_vids": [vid],
                "git_head": head,
                "topology_version": "EPOCH-B-EIGHT-BLOCK",
                "prompt_digest": prompt_digest,
                "evidence_floor": {"minimum_independent": 1},
                "authority_envelope": {"mode": "READ_ONLY_PROVIDER_WITNESS"},
                "completion_predicate": {"I01_I09": "PASS"},
                "stop_predicate": {"I10": "UNBOUND_EXTERNAL_PROMOTION"},
                "return_target": "IC10:I10_EXISTING_PROMOTION_QUALIFICATION",
            }
            query_a = h6.compile_query(**query_args)
            query_b = h6.compile_query(**query_args)
            query_replay_match = canonical(query_a) == canonical(query_b)
            query_replay_digest = sha256_text(canonical(query_a))

            dependencies_explicit = (
                compiler_spec.get("gate_order") == list(GATE_ORDER)
                and all(path.is_file() for path in (COMPILER_SPEC_PATH, RUNTIME_PATH, H6_PATH))
                and all(source_refs)
            )
            syntax_witness = {
                "observed": True,
                "status": "PASS" if dependencies_explicit else "HOLD",
                "ref": source_refs[0],
                "normalized": canonical(json.loads(compiler_spec_text)) == canonical(compiler_spec),
                "dependencies_explicit": dependencies_explicit,
                "trust_class": "PROVIDER_REPOSITORY_OBSERVED",
            }
            type_carrier_witness = {
                "observed": True,
                "status": "PASS",
                "ref": source_refs[1],
                "type": "PYTHON_MODULE",
                "carrier": "text/x-python",
                "units_status": "NOT_APPLICABLE",
                "trust_class": "PROVIDER_REPOSITORY_OBSERVED",
            }
            scope_witness = {
                "observed": True,
                "status": "PASS" if bridge.get("decision") == "ADMITTED" and evidence.get("status") == "EVIDENCE_SUFFICIENT" else "HOLD",
                "ref": source_refs[0],
                "scope": "IC10_COMPILER_MECHANISM_I01_I09",
                "validity_corridor": bridge.get("validity_corridor"),
                "evidence_alignment": "PASS" if evidence.get("status") == "EVIDENCE_SUFFICIENT" else "HOLD",
                "trust_class": "PROVIDER_RUNTIME_OBSERVED",
            }
            invariant_witness = {
                "observed": True,
                "status": "PASS" if bridge.get("decision") == "ADMITTED" and not bridge.get("defects") else "HOLD",
                "ref": source_refs[2],
                "declared_invariants": list(bridge.get("preserved_invariants") or []),
                "violations": list(bridge.get("defects") or []),
                "trust_class": "PROVIDER_RUNTIME_OBSERVED",
            }
            dependency_replay_witness = {
                "observed": True,
                "status": "PASS" if dependencies_explicit and query_replay_match else "HOLD",
                "ref": f"H6QUERY:{query_a.get('query_id')}",
                "dependencies_closed": dependencies_explicit,
                "replay_prerequisites": query_replay_match,
                "exact_versions": bool(head and spec_blob and runtime_blob and h6_blob),
                "trust_class": "PROVIDER_RUNTIME_OBSERVED",
            }
            audit_replay_witness = {
                "observed": True,
                "status": "PASS" if query_replay_match else "HOLD",
                "ref": f"H6QUERY:{query_a.get('query_id')}",
                "audit_complete": True,
                "replay_complete": query_replay_match,
                "replay_digest": query_replay_digest,
                "trust_class": "PROVIDER_RUNTIME_OBSERVED",
            }

            promotion_unbound = {
                "status": "UNBOUND_EXTERNAL_PROMOTION",
                "promotion_allowed": False,
                "git_head": head,
                "run_id": None,
                "gates": {
                    "external_verification": {
                        "status": "HOLD",
                        "trusted": False,
                        "reason": "OBSERVED_WITNESS_CARTRIDGE_CANNOT_MINT_OR_SELF_SUPPLY_TRUSTED_PROMOTION",
                    }
                },
            }
            candidate = {
                "candidate_ref": "IC10.OBSERVED.I01_I09",
                "git_head": head,
                "identity_decision": identity,
                "provenance_refs": source_refs,
                "syntax_witness": syntax_witness,
                "type_carrier_witness": type_carrier_witness,
                "scope_witness": scope_witness,
                "invariant_witness": invariant_witness,
                "evidence_decision": evidence,
                "dependency_replay_witness": dependency_replay_witness,
                "bridge_decision": bridge,
                "audit_replay_witness": audit_replay_witness,
                "promotion_certificate": promotion_unbound,
            }

            before_events = store.one("SELECT COUNT(*) n FROM events")["n"]
            result_a = ic10.evaluate(candidate)
            result_b = ic10.evaluate(candidate)
            after_events = store.one("SELECT COUNT(*) n FROM events")["n"]
        finally:
            store.close()

    gate_status = {gate["gate"]: gate["status"] for gate in result_a["gates"]}
    checks = {
        "identity_resolved": identity.get("decision") == "RESOLVED_EXISTING" and bool(identity.get("selected_oid")),
        "bridge_admitted": bridge.get("decision") == "ADMITTED" and not bridge.get("missing_obligations") and not bridge.get("defects"),
        "evidence_sufficient_nonpromoting": evidence.get("status") == "EVIDENCE_SUFFICIENT" and evidence.get("promotion_authority") is False,
        "querybundle_replay_match": query_replay_match,
        "i01_i09_all_pass": all(gate_status[name] == "PASS" for name in GATE_ORDER[:9]),
        "i10_hold": gate_status[GATE_ORDER[9]] == "HOLD",
        "first_hold_exactly_i10": result_a.get("first_hold") == GATE_ORDER[9],
        "decision_hold_until_external_promotion": result_a.get("decision") == "IC10_HOLD",
        "promotion_authority_false": result_a.get("promotion_authority") is False,
        "ic10_evaluation_no_event_mutation": before_events == after_events,
        "decision_digest_deterministic": result_a.get("decision_digest") == result_b.get("decision_digest"),
        "source_refs_exact": all(ref.startswith("GIT_BLOB:") for ref in source_refs),
    }
    ok = all(checks.values())
    receipt = {
        "artifact": contract["artifact"],
        "status": "I01_I09_OBSERVED_I10_UNBOUND_MATCH" if ok else "IC10_OBSERVED_WITNESS_HOLD",
        "checkout_head": head,
        "source_refs": source_refs,
        "checks": checks,
        "query_replay": {
            "query_id": query_a.get("query_id"),
            "digest": query_replay_digest,
            "match": query_replay_match,
        },
        "identity_decision": identity,
        "bridge_decision": bridge,
        "evidence_decision": evidence,
        "gate_status": gate_status,
        "first_hold": result_a.get("first_hold"),
        "decision": result_a.get("decision"),
        "decision_digest": result_a.get("decision_digest"),
        "event_count_before_ic10": before_events,
        "event_count_after_ic10": after_events,
        "authority_ceiling": "I01_I09_PROVIDER_OBSERVED_I10_EXTERNAL_PROMOTION_UNBOUND",
        "evidence_ceiling": [
            "OBSERVED_I01_I09 != FULL_IC10_PROMOTION",
            "PROVIDER_EXECUTED_CARTRIDGE != TRUSTED_PROMOTION_VERIFIER",
            "I10_MUST_CONSUME_EXISTING_PROMOTION_AUTHORITY_ONLY",
            "REPOSITORY_SOURCE_REF != INDEPENDENT_EMPIRICAL_EVIDENCE",
            "H6_QUERY_REPLAY_MATCH != EXTERNAL_REVERIFICATION",
            "IC10_OBSERVED_WITNESS != CANONICAL_EMISSION_AUTHORITY",
        ],
    }
    OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
