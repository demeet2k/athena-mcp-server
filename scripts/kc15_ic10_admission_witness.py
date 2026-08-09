from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

from athena_mcp.bootstrap import bootstrap
from athena_mcp.core import AthenaCore
from athena_mcp.crystal_runtime import CrystalRuntime
from athena_mcp.h6_root import H6RootRuntime
from athena_mcp.ic10_runtime import GATE_ORDER, IC10Compiler
from athena_mcp.inner_constitution import ACTIVE_EPOCH, seat
from athena_mcp.store import Store

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "spec" / "KC15_IC10_ADMISSION_V1.json"
OUTPUT = Path("kc15_ic10_admission_observed_v1.json")


def git_head() -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()


def blob_sha(path: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", f"HEAD:{path}"], text=True).strip()


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def replay_digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def independent_rows() -> list[dict]:
    poles=["11","10","00","01"]
    rows=[]
    for n in range(1,16):
        bits=[1 if n & (1<<i) else 0 for i in range(4)]
        support=[pole for pole,bit in zip(poles,bits) if bit]
        rows.append({"gid":90+n,"mask":"".join(str(x) for x in bits),"support":support,"rank":len(support)})
    return rows


def current_runtime_kc15_refs() -> list[dict]:
    p=subprocess.run(["git","-C",str(ROOT),"grep","-n","-I","KC15","--","athena_mcp/*.py"],text=True,capture_output=True)
    if p.returncode not in (0,1): raise RuntimeError(p.stderr.strip() or "git grep failed")
    rows=[]
    for line in p.stdout.splitlines():
        path,lineno,text=line.split(":",2)
        rows.append({"path":path,"line":int(lineno),"text":text})
    return rows


def main(argv=None) -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--population",required=True)
    parser.add_argument("--structural",required=True)
    parser.add_argument("--interpretation",required=True)
    parser.add_argument("--output",default=str(OUTPUT))
    args=parser.parse_args(argv)

    contract=json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    population=json.loads(Path(args.population).read_text(encoding="utf-8"))
    structural=json.loads(Path(args.structural).read_text(encoding="utf-8"))
    interpretation=json.loads(Path(args.interpretation).read_text(encoding="utf-8"))
    head=git_head()
    constitution_blob=blob_sha("athena_mcp/inner_constitution.py")
    kc144_blob=blob_sha("athena_mcp/kc144.py")

    rows=independent_rows()
    active=[]
    mismatches=[]
    for row in rows:
        descriptor=seat(row["gid"])
        expected_coord="{"+",".join(row["support"])+"}"
        active_row={"gid":row["gid"],"mask":descriptor["code"],"support":descriptor["coordinate"],"role":descriptor["role"]}
        active.append(active_row)
        if descriptor["block"]!="KC15" or descriptor["code"]!=row["mask"] or descriptor["coordinate"]!=expected_coord or descriptor["role"]!="FOUR_POLE_SUPPORT_MASK":
            mismatches.append({"expected":row,"actual":active_row})

    rank_counts=Counter(row["rank"] for row in rows)
    structural_rows=structural.get("rows") or []
    structural_normalized=[{k:r.get(k) for k in ("gid","mask","support","rank")} for r in structural_rows]
    current_refs=current_runtime_kc15_refs()
    safe_runtime_paths={"athena_mcp/inner_constitution.py","athena_mcp/kc144.py"}
    unexpected_runtime_refs=[r for r in current_refs if r["path"] not in safe_runtime_paths]

    population_checks = population.get("checks") or {}
    structural_checks = structural.get("checks") or {}
    interpretation_checks = interpretation.get("checks") or {}
    population_source_receipts = population.get("source_receipts") or {}
    kc15_population_receipts=[population_source_receipts.get(str(g)) or {} for g in range(91,106)]
    population_constitution_refs=[
        ref
        for receipt in kc15_population_receipts
        for ref in receipt.get("evidence_refs",[])
        if ref.startswith("GIT_BLOB:athena_mcp/inner_constitution.py:")
    ]
    structural_constitution_refs=[
        ref for ref in structural.get("source_refs",[])
        if ref.startswith("GIT_BLOB:athena_mcp/inner_constitution.py:")
    ]

    compatibility={
        "active_epoch": ACTIVE_EPOCH == "EPOCH-B-EIGHT-BLOCK",
        "constitution_blob_matches_contract": constitution_blob == contract["constitution_source_blob"],
        "population_pass": population.get("status") == "KC144_SOURCE_POPULATION_144_MATCH" and population.get("population_complete") is True,
        "population_144_closed": (population.get("dimension_counts") or {}).get("population_status",{}).get("CLOSED") == 144,
        "population_kc15_receipts_present": all(bool(x) for x in kc15_population_receipts),
        "population_constitution_refs_match": len(population_constitution_refs) == 15 and all(ref.endswith(constitution_blob) or f":{constitution_blob}#" in ref for ref in population_constitution_refs),
        "structural_pass": structural.get("status") == "KC15_INDEPENDENT_STRUCTURAL_WITNESS_PASS" and all(structural_checks.values()),
        "structural_rows_match_recomputed": structural_normalized == rows,
        "structural_constitution_ref_matches": any(constitution_blob in ref for ref in structural_constitution_refs),
        "interpretation_pass": interpretation.get("status") == "KC15_INTERPRETATION_REVIEW_PASS" and all(interpretation_checks.values()),
        "interpretation_no_unreviewed_consumers": not interpretation.get("unreviewed_executable_runtime_consumers"),
        "current_runtime_no_new_consumers": not unexpected_runtime_refs,
        "current_structure_matches": not mismatches,
        "rank_distribution_matches": dict(rank_counts) == {1:4,2:6,3:4,4:1},
    }

    claim_body={
        "artifact":"ATHENA.KC15.BOUNDED.STRUCTURAL.CLAIM.V1",
        "claim":contract["claim"],
        "epoch":ACTIVE_EPOCH,
        "constitution_blob":constitution_blob,
        "kc144_blob":kc144_blob,
        "rows":rows,
        "provider_evidence":contract["evidence_sources"],
        "compatibility":compatibility,
    }
    claim_text=json.dumps(claim_body,sort_keys=True,indent=2)

    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        store=Store(tmp.name)
        try:
            core=AthenaCore(store); bootstrap(core)
            crystal=CrystalRuntime(core); h6=H6RootRuntime(core,crystal); ic10=IC10Compiler()
            target=crystal.crystallize_output(
                {
                    "kind":"FINITE_STRUCTURAL_CLAIM","domain":"KC15","verb":"ADMIT","object_name":"EPOCH_B_15_MASK_SUPPORT_LATTICE","method":"PROVIDER_WITNESSED_COMBINATORIAL_AND_RUNTIME_REVIEW",
                    "input_contract":{"constitution":"exact blob","provider_receipts":"population+structural+interpretation"},
                    "output_contract":{"claim_scope":"STRUCTURAL_ONLY","admission":"IC10"},
                },
                claim_text,
                f"git+provider://KC15/STRUCTURAL_CLAIM@{head}",
                "KC15.IC10.ADMISSION","kc15-admission",1,carrier="application/json",
            )
            oid=target["manifest"]["identity"]["OID"]; vid=target["manifest"]["identity"]["VID"]
            identity=h6.identity_decide(oid,candidate_oids=[oid])

            forward=crystal.register_transform("KC144","JSPACE",status="TESTED",mode="ISOMORPHISM",program={"op":"identity"},metric={"type":"EXACT"})
            reverse=crystal.register_transform("JSPACE","KC144",status="TESTED",mode="ISOMORPHISM",program={"op":"identity"},metric={"type":"EXACT"})
            bridge=h6.bridge_decide(forward["transform_id"],{
                "preserved_invariants":["KC15_MASK_SET","EPOCH_B_GID_MAPPING","SUPPORT_ONLY_SEMANTICS"],
                "lost_invariants":[],
                "validity_corridor":{"epoch":ACTIVE_EPOCH,"claim_scope":"STRUCTURAL_ONLY","constitution_blob":constitution_blob},
                "evidence_refs":[
                    f"ACTIONS_ARTIFACT:{contract['evidence_sources']['independent_structural']['artifact_id']}:{contract['evidence_sources']['independent_structural']['digest']}",
                    f"ACTIONS_ARTIFACT:{contract['evidence_sources']['interpretation_review']['artifact_id']}:{contract['evidence_sources']['interpretation_review']['digest']}",
                ],
                "required_authority":["READ_ONLY_KC15_STRUCTURAL_ADMISSION"],
                "reverse_transform_id":reverse["transform_id"],
                "counterexamples":["EMPTY_SUBSET_AS_SIXTEENTH_SEAT","SUPPORT_CAST_TO_TRUTH","HISTORICAL_GID_AS_CURRENT_AUTHORITY"],
            })
            evidence=h6.evidence_decide(
                {"claim_id":contract["claim"]["claim_id"],"evidence_floor":{"minimum_independent":2}},
                [
                    {"evidence_id":"KC15.STRUCTURAL.PROVIDER","source_id":f"ACTIONS.RUN.{contract['evidence_sources']['independent_structural']['run_id']}","source_revision":contract['evidence_sources']['independent_structural']['digest'],"independence_group":contract['evidence_sources']['independent_structural']['independence_group'],"support_direction":"SUPPORT","freshness":"CURRENT"},
                    {"evidence_id":"KC15.INTERPRETATION.PROVIDER","source_id":f"ACTIONS.RUN.{contract['evidence_sources']['interpretation_review']['run_id']}","source_revision":contract['evidence_sources']['interpretation_review']['digest'],"independence_group":contract['evidence_sources']['interpretation_review']['independence_group'],"support_direction":"SUPPORT","freshness":"CURRENT"},
                ],
            )

            query_args={
                "request":"Admit bounded Epoch-B KC15 structural support-lattice claim",
                "goal":"IC10-qualify only the finite structural claim with support-only semantics",
                "identity_targets":[oid],"semantic_vids":[vid],"git_head":head,"topology_version":ACTIVE_EPOCH,"prompt_digest":constitution_blob,
                "evidence_floor":{"minimum_independent":2},"authority_envelope":{"mode":"READ_ONLY_KC15_STRUCTURAL_ADMISSION"},
                "completion_predicate":{"I01_I09":"PASS"},"stop_predicate":{"I10":"UNBOUND_EXTERNAL_PROMOTION"},"return_target":"IC10:I10_EXISTING_PROMOTION_QUALIFICATION",
            }
            qa=h6.compile_query(**query_args); qb=h6.compile_query(**query_args); replay_match=canonical(qa)==canonical(qb)
            replay_hash=replay_digest(qa)

            syntax={"observed":True,"status":"PASS" if all(compatibility.values()) else "HOLD","ref":f"GIT_BLOB:athena_mcp/inner_constitution.py:{constitution_blob}","normalized":True,"dependencies_explicit":all(compatibility.values()),"trust_class":"PROVIDER_REPOSITORY_AND_ARTIFACT_OBSERVED"}
            type_carrier={"observed":True,"status":"PASS","ref":f"GIT_BLOB:athena_mcp/inner_constitution.py:{constitution_blob}","type":"FINITE_NONEMPTY_SUBSET_LATTICE","carrier":"PYTHON_CONSTITUTION_PLUS_PROVIDER_JSON_RECEIPTS","units_status":"NOT_APPLICABLE","trust_class":"PROVIDER_OBSERVED"}
            scope={"observed":True,"status":"PASS" if bridge.get('decision')=='ADMITTED' and evidence.get('status')=='EVIDENCE_SUFFICIENT' else "HOLD","ref":contract['claim']['claim_id'],"scope":contract['claim']['scope'],"validity_corridor":bridge.get('validity_corridor'),"evidence_alignment":"PASS" if evidence.get('status')=='EVIDENCE_SUFFICIENT' else "HOLD","trust_class":"PROVIDER_OBSERVED"}
            violations=[]
            if mismatches: violations.append("ACTIVE_MAPPING_MISMATCH")
            if dict(rank_counts)!={1:4,2:6,3:4,4:1}: violations.append("RANK_DISTRIBUTION_MISMATCH")
            if unexpected_runtime_refs: violations.append("UNREVIEWED_RUNTIME_CONSUMER")
            invariant={"observed":True,"status":"PASS" if not violations else "HOLD","ref":contract['claim']['claim_id'],"declared_invariants":["15_NONEMPTY_UNIQUE_MASKS","RANK_4_6_4_1","EPOCH_B_GID_MAPPING","SUPPORT_ONLY_SEMANTICS"],"violations":violations,"trust_class":"PROVIDER_OBSERVED"}
            dependency={"observed":True,"status":"PASS" if all(compatibility.values()) and replay_match else "HOLD","ref":f"H6REPLAY:{replay_hash}","dependencies_closed":all(compatibility.values()),"replay_prerequisites":replay_match,"exact_versions":True,"trust_class":"PROVIDER_OBSERVED"}
            audit={"observed":True,"status":"PASS" if replay_match else "HOLD","ref":f"H6REPLAY:{replay_hash}","audit_complete":True,"replay_complete":replay_match,"replay_digest":replay_hash,"trust_class":"PROVIDER_OBSERVED"}
            promotion_unbound={"status":"UNBOUND_EXTERNAL_PROMOTION","promotion_allowed":False,"git_head":head,"run_id":None,"gates":{"external_verification":{"status":"HOLD","trusted":False,"reason":"CLAIM_WITNESS_CANNOT_SELF_MINT_I10"}}}
            candidate={"candidate_ref":"KC15.EPOCH_B.STRUCTURAL_SUPPORT_LATTICE","git_head":head,"identity_decision":identity,"provenance_refs":[f"GIT_BLOB:athena_mcp/inner_constitution.py:{constitution_blob}",f"ACTIONS_ARTIFACT:{contract['evidence_sources']['population']['artifact_id']}:{contract['evidence_sources']['population']['digest']}",f"ACTIONS_ARTIFACT:{contract['evidence_sources']['independent_structural']['artifact_id']}:{contract['evidence_sources']['independent_structural']['digest']}",f"ACTIONS_ARTIFACT:{contract['evidence_sources']['interpretation_review']['artifact_id']}:{contract['evidence_sources']['interpretation_review']['digest']}"],"syntax_witness":syntax,"type_carrier_witness":type_carrier,"scope_witness":scope,"invariant_witness":invariant,"evidence_decision":evidence,"dependency_replay_witness":dependency,"bridge_decision":bridge,"audit_replay_witness":audit,"promotion_certificate":promotion_unbound}
            before=store.one("SELECT COUNT(*) n FROM events")["n"]; ra=ic10.evaluate(candidate); rb=ic10.evaluate(candidate); after=store.one("SELECT COUNT(*) n FROM events")["n"]
        finally:
            store.close()

    gate_status={g['gate']:g['status'] for g in ra['gates']}
    checks={
        "all_artifact_compatibility_checks":all(compatibility.values()),
        "identity_resolved":identity.get('decision')=='RESOLVED_EXISTING',
        "bridge_admitted":bridge.get('decision')=='ADMITTED' and not bridge.get('defects') and not bridge.get('missing_obligations'),
        "evidence_sufficient_two_independent_groups":evidence.get('status')=='EVIDENCE_SUFFICIENT' and evidence.get('promotion_authority') is False,
        "query_replay_match":replay_match,
        "replay_digest_nonempty":bool(replay_hash),
        "i01_i09_pass":all(gate_status.get(name)=='PASS' for name in GATE_ORDER[:9]),
        "i10_hold":gate_status.get(GATE_ORDER[9])=='HOLD',
        "first_hold_i10":ra.get('first_hold')==GATE_ORDER[9],
        "decision_hold_until_i10":ra.get('decision')=='IC10_HOLD',
        "no_ic10_event_mutation":before==after,
        "decision_deterministic":ra.get('decision_digest')==rb.get('decision_digest'),
        "truth_nonclaim_preserved":all('truth' not in x.lower() or x.lower().startswith('kc15 support is true') for x in contract['claim']['explicit_nonclaims']),
    }
    ok=all(checks.values())
    receipt={"artifact":"ATHENA.KC15.IC10.OBSERVED.ADMISSION.V1","status":"I01_I09_OBSERVED_I10_UNBOUND_MATCH" if ok else "KC15_IC10_OBSERVED_ADMISSION_HOLD","checkout_head":head,"claim":contract['claim'],"compatibility":compatibility,"checks":checks,"gate_status":gate_status,"first_hold":ra.get('first_hold'),"decision":ra.get('decision'),"decision_digest":ra.get('decision_digest'),"event_count_before_ic10":before,"event_count_after_ic10":after,"candidate_packet":candidate,"bounded_standing":{"population":"CLOSED","execution":"PARTIAL","evidence":"HOLD_UNTIL_TRUSTED_I10","return":"PARTIAL","truth_claim":"NOT_ESTABLISHED","promotion_authority":False},"evidence_ceiling":contract['firewalls']}
    Path(args.output).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in receipt.items() if k!='candidate_packet'},indent=2,sort_keys=True))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
