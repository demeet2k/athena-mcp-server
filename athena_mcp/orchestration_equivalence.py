from __future__ import annotations

import json
import time
from typing import Any, Dict, Iterable, Mapping, Optional

from .identity import digest, event_id

RELATIONS = {"EQUIVALENT", "DISTINCT"}
REQUIRED_SAMENESS = (
    "semantic_object",
    "functional_role",
    "proof_route",
    "carrier",
    "lineage",
    "boundary",
    "failure_role",
)

EQUIVALENCE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS equivalence_heads(
 context_id TEXT NOT NULL,
 left_id TEXT NOT NULL,
 right_id TEXT NOT NULL,
 relation TEXT NOT NULL,
 status TEXT NOT NULL,
 witness_ref TEXT NOT NULL,
 dimensions_json TEXT NOT NULL,
 conflict_json TEXT NOT NULL,
 last_eid TEXT NOT NULL,
 updated_at REAL NOT NULL,
 PRIMARY KEY(context_id,left_id,right_id)
);
CREATE TABLE IF NOT EXISTS equivalence_events(
 equivalence_event_id TEXT PRIMARY KEY,
 context_id TEXT NOT NULL,
 left_id TEXT NOT NULL,
 right_id TEXT NOT NULL,
 operation TEXT NOT NULL,
 relation TEXT,
 payload_json TEXT NOT NULL,
 eid TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_equivalence_context ON equivalence_heads(context_id,status,relation);
CREATE INDEX IF NOT EXISTS idx_equivalence_events_pair ON equivalence_events(context_id,left_id,right_id,created_at);
'''


def _pair(left_id: str, right_id: str):
    left = str(left_id).strip(); right = str(right_id).strip()
    if not left or not right: raise ValueError("equivalence ids must be nonempty")
    if left == right: raise ValueError("equivalence pair must contain two distinct ids")
    return tuple(sorted((left, right)))


def _verified_ref(witness: Mapping[str, Any], label: str = "witness") -> str:
    witness = dict(witness or {})
    if witness.get("verified") is not True: raise ValueError(f"{label} requires verified=true")
    ref = str(witness.get("ref") or "").strip()
    if not ref: raise ValueError(f"{label} requires ref")
    return ref


def _authorized_ref(authority: Mapping[str, Any]) -> str:
    authority = dict(authority or {})
    if authority.get("authorized") is not True: raise ValueError("conflict resolution requires authorized=true")
    ref = str(authority.get("ref") or "").strip()
    if not ref: raise ValueError("conflict resolution requires authority ref")
    return ref


def _equivalent_dimensions(same: Mapping[str, Any]) -> Dict[str, bool]:
    same = dict(same or {})
    missing = [name for name in REQUIRED_SAMENESS if same.get(name) is not True]
    if missing:
        raise ValueError(
            "EQUIVALENT requires witnessed sameness across preservation dimensions; "
            f"not proven same: {missing}. Record DISTINCT or leave UNKNOWN instead."
        )
    return {name: True for name in REQUIRED_SAMENESS}


class EquivalenceLedger:
    def __init__(self, core):
        self.core = core; self.s = core.s
        with self.s.db: self.s.db.executescript(EQUIVALENCE_SCHEMA)
        self.core.register(
            "TOOL", "DEVELOPMENT", "CLASSIFY", "EQUIVALENCE_GEOMETRY", "WITNESSED_CONSERVATIVE_DEDUP",
            {"pair": "stable ids", "context": "dedup context", "relation": "EQUIVALENT|DISTINCT", "witness": "verified"},
            {"head": "ACTIVE|CONFLICT", "groups": "collapse-safe components", "conflicts": "preserve-all components"},
            actor="GENESIS.AOR.3", status="CANONICAL"
        )

    def _event(self, context_id, left, right, operation, relation, payload, actor):
        parent = self.s.head("global"); pe = parent["eid"] if parent else None
        ep = {"context_id":context_id,"left_id":left,"right_id":right,"operation":operation,"relation":relation,**dict(payload)}
        eid = event_id(f"EQUIVALENCE_{operation}", actor, pe, ep); ed = digest(ep, 32)
        eeid = "EQEV." + digest({"eid":eid,"context":context_id,"pair":[left,right],"op":operation},24)
        self.s.put_event(eid, f"EQUIVALENCE_{operation}", actor, pe, ep, ed); self.s.set_head("global",None,None,eid,ed)
        with self.s.db:
            self.s.db.execute("INSERT INTO equivalence_events VALUES(?,?,?,?,?,?,?,?,?)",(eeid,context_id,left,right,operation,relation,json.dumps(ep,sort_keys=True),eid,time.time()))
        return eeid,eid

    def observe(self, context_id: str, left_id: str, right_id: str, relation: str, witness: Mapping[str,Any], same: Optional[Mapping[str,Any]]=None, different: Optional[Iterable[str]]=None, actor: str="agent"):
        context_id = str(context_id).strip()
        if not context_id: raise ValueError("context_id required")
        left,right = _pair(left_id,right_id); relation = str(relation).upper()
        if relation not in RELATIONS: raise ValueError("relation must be EQUIVALENT or DISTINCT")
        witness_ref = _verified_ref(witness)
        if relation == "EQUIVALENT":
            dimensions = _equivalent_dimensions(same or {})
        else:
            diff = sorted({str(x) for x in (different or []) if str(x)})
            if not diff: raise ValueError("DISTINCT requires at least one explicit differing dimension/reason")
            dimensions = {"different":diff}

        prior = self.s.one("SELECT * FROM equivalence_heads WHERE context_id=? AND left_id=? AND right_id=?",(context_id,left,right))
        conflict = []
        status = "ACTIVE"
        operation = "OBSERVE"
        if prior and prior["status"] == "ACTIVE" and prior["relation"] != relation:
            status = "CONFLICT"
            operation = "CONFLICT"
            conflict = [
                {"relation":prior["relation"],"witness_ref":prior["witness_ref"],"dimensions":json.loads(prior["dimensions_json"])},
                {"relation":relation,"witness_ref":witness_ref,"dimensions":dimensions},
            ]
            active_relation = prior["relation"]
            active_dimensions = json.loads(prior["dimensions_json"])
            active_witness = prior["witness_ref"]
        elif prior and prior["status"] == "CONFLICT":
            raise ValueError("pair is already CONFLICT; resolve conflict before new observation")
        else:
            active_relation = relation; active_dimensions = dimensions; active_witness = witness_ref

        eeid,eid = self._event(context_id,left,right,operation,relation,{"witness_ref":witness_ref,"dimensions":dimensions,"status":status,"conflict":conflict},actor)
        with self.s.db:
            self.s.db.execute("INSERT OR REPLACE INTO equivalence_heads VALUES(?,?,?,?,?,?,?,?,?,?)",(context_id,left,right,active_relation,status,active_witness,json.dumps(active_dimensions,sort_keys=True),json.dumps(conflict,sort_keys=True),eid,time.time()))
        return {"equivalence_event_id":eeid,"context_id":context_id,"left_id":left,"right_id":right,"relation":active_relation,"status":status,"witness_ref":active_witness,"conflict":conflict,"eid":eid}

    def resolve_conflict(self, context_id: str, left_id: str, right_id: str, relation: str, authority: Mapping[str,Any], actor: str="agent"):
        left,right = _pair(left_id,right_id); relation = str(relation).upper()
        if relation not in RELATIONS: raise ValueError("relation must be EQUIVALENT or DISTINCT")
        row = self.s.one("SELECT * FROM equivalence_heads WHERE context_id=? AND left_id=? AND right_id=?",(context_id,left,right))
        if not row or row["status"] != "CONFLICT": raise ValueError("pair is not in CONFLICT")
        authority_ref = _authorized_ref(authority)
        candidates = json.loads(row["conflict_json"])
        selected = next((item for item in candidates if item["relation"] == relation), None)
        if selected is None: raise ValueError("resolution relation must select one witnessed side of conflict")
        eeid,eid = self._event(context_id,left,right,"RESOLVE_CONFLICT",relation,{"authority_ref":authority_ref,"selected":selected},actor)
        with self.s.db:
            self.s.db.execute("UPDATE equivalence_heads SET relation=?,status='ACTIVE',witness_ref=?,dimensions_json=?,conflict_json='[]',last_eid=?,updated_at=? WHERE context_id=? AND left_id=? AND right_id=?",(relation,selected["witness_ref"],json.dumps(selected["dimensions"],sort_keys=True),eid,time.time(),context_id,left,right))
        return {"equivalence_event_id":eeid,"context_id":context_id,"left_id":left,"right_id":right,"relation":relation,"status":"ACTIVE","authority_ref":authority_ref,"eid":eid}

    def state(self, context_id: str, left_id: str, right_id: str):
        left,right = _pair(left_id,right_id)
        row = self.s.one("SELECT * FROM equivalence_heads WHERE context_id=? AND left_id=? AND right_id=?",(context_id,left,right))
        if not row: return None
        out = dict(row); out["dimensions"] = json.loads(out.pop("dimensions_json")); out["conflict"] = json.loads(out.pop("conflict_json")); return out

    def snapshot(self, context_id: str, candidates: Iterable[Mapping[str,Any]]):
        rows = [dict(x) for x in candidates]
        ids = []
        by_id = {}
        for index,item in enumerate(rows):
            ident = str(item.get("dedup_id") or item.get("id") or f"candidate:{index:04d}")
            if ident in by_id: raise ValueError(f"duplicate dedup identity {ident}")
            ids.append(ident); by_id[ident] = item
        allowed = set(ids)
        heads = self.s.rows("SELECT * FROM equivalence_heads WHERE context_id=?",(context_id,))
        relevant = [row for row in heads if row["left_id"] in allowed and row["right_id"] in allowed]

        parent = {ident:ident for ident in ids}
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]; x = parent[x]
            return x
        def union(a,b):
            ra,rb = find(a),find(b)
            if ra != rb: parent[max(ra,rb)] = min(ra,rb)

        equivalence_edges=[]; distinct_edges=[]; pair_conflicts=[]
        for row in relevant:
            edge={"left_id":row["left_id"],"right_id":row["right_id"],"relation":row["relation"],"status":row["status"],"witness_ref":row["witness_ref"],"last_eid":row["last_eid"]}
            if row["status"] == "CONFLICT": pair_conflicts.append(edge); continue
            if row["relation"] == "EQUIVALENT": equivalence_edges.append(edge); union(row["left_id"],row["right_id"])
            elif row["relation"] == "DISTINCT": distinct_edges.append(edge)

        components={}
        for ident in ids: components.setdefault(find(ident),[]).append(ident)
        transitive_conflicts=[]
        for edge in distinct_edges:
            if find(edge["left_id"]) == find(edge["right_id"]): transitive_conflicts.append(edge)

        conflicted_members=set()
        for edge in pair_conflicts + transitive_conflicts:
            conflicted_members.update(components.get(find(edge["left_id"]),[edge["left_id"]]))
            conflicted_members.update(components.get(find(edge["right_id"]),[edge["right_id"]]))

        groups=[]
        for root,members in sorted(components.items()):
            members=sorted(members)
            if any(member in conflicted_members for member in members):
                for member in members:
                    groups.append({"group_id":"EQG."+digest({"context":context_id,"members":[member]},20),"members":[member],"representative":member,"collapse_allowed":False,"status":"PRESERVE_ALL_CONFLICT"})
            else:
                groups.append({"group_id":"EQG."+digest({"context":context_id,"members":members},20),"members":members,"representative":members[0],"collapse_allowed":len(members)>1,"status":"EQUIVALENT" if len(members)>1 else "SINGLETON"})

        suppressed=[]
        for group in groups:
            if group["collapse_allowed"]:
                suppressed.extend(member for member in group["members"] if member != group["representative"])
        return {"context_id":context_id,"candidate_ids":ids,"groups":groups,"suppressed":sorted(suppressed),"equivalence_edges":equivalence_edges,"distinct_edges":distinct_edges,"pair_conflicts":pair_conflicts,"transitive_conflicts":transitive_conflicts,"law":"collapse only witnessed contradiction-free equivalence components; conflict/unknown => preserve"}

    def benchmark(self):
        q=lambda where,args=():self.s.one(f"SELECT COUNT(*) n FROM equivalence_heads{where}",args)["n"]
        return {"equivalence_pairs":q(""),"equivalence_active":q(" WHERE status='ACTIVE'"),"equivalence_conflicts":q(" WHERE status='CONFLICT'"),"equivalence_events":self.s.one("SELECT COUNT(*) n FROM equivalence_events")["n"]}
