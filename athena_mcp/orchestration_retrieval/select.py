from __future__ import annotations

from itertools import combinations
from typing import Any, Dict, Iterable, Mapping

from .score import finite, score_candidate
from .specs import EXACT_SELECTION_LIMIT, RETRIEVAL_ROLES


def candidate_id(candidate: Mapping[str,Any], index: int):
    for key in ("id","oid","cid","ref","source_ref"):
        value=candidate.get(key)
        if value not in (None,""):
            return str(value)
    return f"retrieval:{index:04d}"


def _validate_roles(candidate):
    roles=sorted({str(x) for x in (candidate.get("roles") or []) if str(x)})
    unknown=[x for x in roles if x not in RETRIEVAL_ROLES]
    if unknown: raise ValueError(f"unknown retrieval roles {unknown}")
    return roles


def _scored_rows(candidates,query):
    rows=[];seen=set()
    for index,raw in enumerate(candidates):
        item=dict(raw);ident=candidate_id(item,index)
        if ident in seen: raise ValueError(f"duplicate retrieval candidate id {ident}")
        seen.add(ident);item["id"]=ident;item["roles"]=_validate_roles(item);item["facets"]=sorted({str(x) for x in (item.get("facets") or []) if str(x)})
        rows.append({"id":ident,"source":item,"score":score_candidate(item,query)})
    known=[row for row in rows if row["score"]["status"]=="KNOWN"]
    max_score=max((float(row["score"]["value"]) for row in known),default=0.0)
    for row in rows:
        row["normalized_score"]=(float(row["score"]["value"])/max_score) if row["score"]["status"]=="KNOWN" and max_score>0 else (1.0 if row["score"]["status"]=="KNOWN" and max_score==0 else None)
    return rows


def _equivalence_reduce(rows,eq_snapshot):
    if not eq_snapshot:
        return rows,{"mode":"NONE","groups":[],"suppressed":[]}
    by_id={row["id"]:row for row in rows};covered=set();kept=[];groups=[];suppressed=[]
    for group in eq_snapshot.get("groups") or []:
        members=[m for m in group.get("members") or [] if m in by_id]
        if not members: continue
        covered.update(members)
        if group.get("collapse_allowed") is True and len(members)>1:
            candidates=[by_id[m] for m in members]
            known=[r for r in candidates if r["score"]["status"]=="KNOWN"]
            if known:
                chosen=sorted(known,key=lambda r:(-float(r["score"]["value"]),float(r["score"]["cost"]),r["id"]))[0]
            else:
                chosen=sorted(candidates,key=lambda r:r["id"])[0]
            kept.append(chosen);suppressed.extend(m for m in members if m!=chosen["id"])
            groups.append({"eq_group_id":group.get("group_id"),"members":sorted(members),"retrieval_representative":chosen["id"],"collapse_applied":True})
        else:
            kept.extend(by_id[m] for m in members);groups.append({"eq_group_id":group.get("group_id"),"members":sorted(members),"retrieval_representative":None,"collapse_applied":False,"status":group.get("status")})
    kept.extend(row for row in rows if row["id"] not in covered)
    unique={row["id"]:row for row in kept}
    return [unique[k] for k in sorted(unique)],{"mode":"EQ.1_SNAPSHOT","groups":groups,"suppressed":sorted(set(suppressed)),"pair_conflicts":eq_snapshot.get("pair_conflicts") or [],"transitive_conflicts":eq_snapshot.get("transitive_conflicts") or []}


def _set_utility(selected,required_roles,required_facets,coverage_weight,role_weight):
    score=sum(float(row["normalized_score"] or 0.0) for row in selected)
    roles=set();facets=set()
    for row in selected:
        roles.update(row["source"].get("roles") or []);facets.update(row["source"].get("facets") or [])
    role_fraction=(len(roles & required_roles)/len(required_roles)) if required_roles else 0.0
    facet_fraction=(len(facets & required_facets)/len(required_facets)) if required_facets else 0.0
    return score+role_weight*role_fraction+coverage_weight*facet_fraction,roles,facets


def _better(candidate,incumbent):
    if incumbent is None:return True
    utility,cost,ids= candidate; iu,ic,iids=incumbent
    if abs(utility-iu)>1e-12:return utility>iu
    if abs(cost-ic)>1e-12:return cost<ic
    return ids<iids


def _exact(rows,capacity,max_items,required_roles,required_facets,coverage_weight,role_weight):
    best=None;best_rows=[]
    for size in range(0,min(max_items,len(rows))+1):
        for combo in combinations(rows,size):
            cost=sum(float(r["score"]["cost"]) for r in combo)
            if cost>capacity+1e-12:continue
            utility,_,_=_set_utility(combo,required_roles,required_facets,coverage_weight,role_weight);ids=tuple(sorted(r["id"] for r in combo))
            candidate=(utility,cost,ids)
            if _better(candidate,best):best=candidate;best_rows=list(combo)
    return best_rows,best or (0.0,0.0,tuple())


def _greedy(rows,capacity,max_items,required_roles,required_facets,coverage_weight,role_weight):
    selected=[];remaining=list(rows);used=0.0;current_utility=0.0
    while remaining and len(selected)<max_items:
        best=None;best_row=None
        for row in remaining:
            cost=float(row["score"]["cost"])
            if used+cost>capacity+1e-12:continue
            utility,_,_=_set_utility(selected+[row],required_roles,required_facets,coverage_weight,role_weight)
            marginal=utility-current_utility;density=marginal/cost if cost>0 else float("inf")
            key=(density,marginal,-cost,row["id"])
            if best is None or key>best:best=key;best_row=row
        if best_row is None or best[1]<=0:break
        selected.append(best_row);remaining=[r for r in remaining if r["id"]!=best_row["id"]];used+=float(best_row["score"]["cost"]);current_utility,_r,_f=_set_utility(selected,required_roles,required_facets,coverage_weight,role_weight)
    return selected,(current_utility,used,tuple(sorted(r["id"] for r in selected)))


def compile_selection(query: Mapping[str,Any],candidates: Iterable[Mapping[str,Any]],eq_snapshot=None):
    query=dict(query or {});rows=_scored_rows(candidates,query);reduced,eq_report=_equivalence_reduce(rows,eq_snapshot)
    rankable=[row for row in reduced if row["score"]["status"]=="KNOWN"]
    measurement_plan=[{"candidate":row["id"],"defects":row["score"]["defects"]} for row in reduced if row["score"]["status"]!="KNOWN"]
    required_roles={str(x) for x in query.get("required_roles") or []};unknown_roles=required_roles-set(RETRIEVAL_ROLES)
    if unknown_roles:raise ValueError(f"unknown required retrieval roles {sorted(unknown_roles)}")
    required_facets={str(x) for x in query.get("required_facets") or [] if str(x)}
    capacity=finite(query.get("budget"));capacity=capacity if capacity is not None else sum(float(r["score"]["cost"]) for r in rankable)
    if capacity<0:raise ValueError("retrieval budget must be nonnegative")
    try:max_items=int(query.get("max_items",len(rankable)))
    except (TypeError,ValueError):raise ValueError("max_items must be integer")
    if max_items<0:raise ValueError("max_items must be nonnegative")
    coverage_weight=finite(query.get("facet_coverage_weight"));coverage_weight=1.0 if coverage_weight is None else coverage_weight
    role_weight=finite(query.get("role_coverage_weight"));role_weight=1.0 if role_weight is None else role_weight
    if coverage_weight<0 or role_weight<0:raise ValueError("coverage weights must be nonnegative")
    if len(rankable)<=EXACT_SELECTION_LIMIT:
        selected,summary=_exact(rankable,capacity,max_items,required_roles,required_facets,coverage_weight,role_weight);solver="EXACT_ENUMERATION";optimality="PROVEN_FOR_DECLARED_UTILITY"
    else:
        selected,summary=_greedy(rankable,capacity,max_items,required_roles,required_facets,coverage_weight,role_weight);solver="GREEDY_MARGINAL_UTILITY";optimality="HEURISTIC_NOT_PROVEN"
    utility,used,ids=summary;selected=sorted(selected,key=lambda r:(-float(r["normalized_score"] or 0),r["id"]))
    selected_roles=set();selected_facets=set()
    for row in selected:selected_roles.update(row["source"].get("roles") or []);selected_facets.update(row["source"].get("facets") or [])
    return {"rows":rows,"equivalence":eq_report,"rankable_ids":[r["id"] for r in rankable],"measurement_plan":measurement_plan,"selected":selected,"selected_ids":[r["id"] for r in selected],"solver":solver,"optimality":optimality,"utility":utility,"budget":capacity,"used":used,"remaining":max(0.0,capacity-used),"max_items":max_items,"coverage":{"required_roles":sorted(required_roles),"covered_roles":sorted(selected_roles&required_roles),"missing_roles":sorted(required_roles-selected_roles),"required_facets":sorted(required_facets),"covered_facets":sorted(selected_facets&required_facets),"missing_facets":sorted(required_facets-selected_facets)},"utility_law":"sum(normalized source score) + role_coverage_weight*role_fraction + facet_coverage_weight*facet_fraction"}
