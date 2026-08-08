from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

_legacy_path=Path(__file__).resolve().parent.parent / "ledger.py"
_spec=importlib.util.spec_from_file_location("athena_mcp.orchestration_gap._ledger_impl",_legacy_path)
_impl=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_impl)


def _carrier(output):
    return {
        "closure_kind":output.get("closure_kind"),
        "policy":output.get("policy"),
        "source_groups":output.get("source_groups"),
        "closure_nodes":output.get("closure_nodes"),
        "closure_paths":output.get("closure_paths"),
        "admissible_edge_ids":output.get("admissible_edge_ids"),
        "rejected_edges":output.get("rejected_edges"),
        "covered_target_ids":output.get("covered_target_ids"),
        "gap_target_ids":output.get("gap_target_ids"),
        "ranked_gap_ids":output.get("ranked_gap_ids"),
        "grow":(output.get("grow") or {}).get("id"),
        "measurement_plan":output.get("measurement_plan"),
    }


def decision_digest(output):
    raw=json.dumps(_carrier(output),sort_keys=True,ensure_ascii=False,separators=(",",":"));return hashlib.sha256(raw.encode()).hexdigest()


class GapLedger(_impl.GapLedger):
    """GAPRUN ledger whose decision digest includes navigation path witnesses."""
    def compile(self,task_ref,sources,edges,targets,policy,actor="agent",persist=True):
        # Reuse the legacy storage/event implementation, but recompute output and
        # persistence through the strengthened digest path rather than accepting
        # a reachable-set-only decision identity.
        import time
        from ..compiler import compile_gap
        from ...identity import digest,event_id
        task_ref=str(task_ref or "").strip()
        if not task_ref:raise ValueError("task_ref required")
        inputs={"sources":{str(k):list(v or []) for k,v in dict(sources or {}).items()},"edges":[dict(x) for x in edges or []],"targets":[dict(x) for x in targets or []],"policy":dict(policy or {})}
        output=compile_gap(**inputs);output["decision_digest"]=decision_digest(output)
        if not persist:return {**output,"persisted":False}
        parent=self.s.head("global");pe=parent["eid"] if parent else None
        ep={"operation":"GAP_COMPILE","task_ref":task_ref,"actor":actor,"closure_count":len(output["closure_nodes"]),"gap_ids":output["gap_target_ids"],"grow":(output.get("grow") or {}).get("id"),"decision_digest":output["decision_digest"]};eid=event_id("GAP_COMPILE",actor,pe,ep);ed=digest(ep,32);run_id="GAPRUN."+digest({"eid":eid,"decision":output["decision_digest"]},24)
        with self.s.db:self.s.db.execute("INSERT INTO gap_runs VALUES(?,?,?,?,?,?,?,?)",(run_id,task_ref,actor,json.dumps(inputs,sort_keys=True,ensure_ascii=False),json.dumps(output,sort_keys=True,ensure_ascii=False),output["decision_digest"],eid,time.time()))
        self.s.put_event(eid,"GAP_COMPILE",actor,pe,ep,ed);self.s.set_head("global",None,None,eid,ed)
        return {**output,"persisted":True,"run_id":run_id,"eid":eid}

    def replay(self,run_id):
        from ..compiler import compile_gap
        stored=self.get(run_id);recomputed=compile_gap(**stored["input"]);digest_now=decision_digest(recomputed);match=digest_now==stored["decision_digest"]
        return {"run_id":run_id,"status":"REPLAY_MATCH" if match else "REPLAY_DIVERGED","match":match,"stored_decision_digest":stored["decision_digest"],"recomputed_decision_digest":digest_now,"stored_gap":stored["output"].get("gap_target_ids"),"recomputed_gap":recomputed.get("gap_target_ids"),"stored_grow":(stored["output"].get("grow") or {}).get("id"),"recomputed_grow":(recomputed.get("grow") or {}).get("id"),"stored_closure_nodes":stored["output"].get("closure_nodes"),"recomputed_closure_nodes":recomputed.get("closure_nodes"),"stored_closure_paths":stored["output"].get("closure_paths"),"recomputed_closure_paths":recomputed.get("closure_paths")}

__all__=["GapLedger","decision_digest"]
