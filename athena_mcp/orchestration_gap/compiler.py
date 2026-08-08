from __future__ import annotations

import math
from collections import deque
from typing import Any,Dict,Iterable,Mapping

AOR_EDGE_TYPES=('define','derive','depend','support','contradict','test','fail','implement','bridge','reconstruct','fork','merge','next')

def _finite(value):
    if isinstance(value,bool):return None
    try:out=float(value)
    except (TypeError,ValueError):return None
    return out if math.isfinite(out) else None

def _edge_id(edge,index):return str(edge.get('id') or edge.get('edge_id') or f'edge:{index:05d}')
def _normalize_sources(sources):
    groups={};origins={}
    for group,values in dict(sources or {}).items():
        ids=sorted({str(v) for v in (values or []) if str(v)});groups[str(group)]=ids
        for node in ids:origins.setdefault(node,[]).append(str(group))
    for node in origins:origins[node]=sorted(set(origins[node]))
    return groups,origins

def _admissible(edge,policy):
    relation=str(edge.get('relation') or '');allowed=set(policy.get('traversable_relations') or []);defects=[]
    if relation not in AOR_EDGE_TYPES:defects.append('unknown_relation')
    if relation not in allowed:defects.append('relation_not_traversable')
    status=str(edge.get('status') or 'ACTIVE').upper()
    if status not in set(policy.get('allowed_statuses') or ['ACTIVE']):defects.append('status_not_allowed')
    if policy.get('require_witness',True):
        if edge.get('verified') is not True:defects.append('edge_not_verified')
        if not str(edge.get('witness_ref') or '').strip():defects.append('missing_witness_ref')
    return not defects,defects

def _residual_score(target):
    required=('severity','leverage','information_gain','cost');values={};defects=[]
    for name in required:
        value=_finite(target.get(name))
        if value is None:defects.append({'metric':name,'reason':'missing_or_invalid'})
        else:values[name]=value
    if 'cost' in values and values['cost']<=0:defects.append({'metric':'cost','reason':'nonpositive'})
    for name in ('severity','leverage','information_gain'):
        if name in values and values[name]<0:defects.append({'metric':name,'reason':'negative_not_allowed'})
    if defects:return {'status':'UNKNOWN','value':None,'components':values,'defects':defects}
    return {'status':'KNOWN','value':values['severity']*values['leverage']*values['information_gain']/values['cost'],'components':values,'defects':[]}

def compile_gap(sources:Mapping[str,Iterable[str]],edges:Iterable[Mapping[str,Any]],targets:Iterable[Mapping[str,Any]],policy:Mapping[str,Any]):
    policy=dict(policy or {});relations=list(dict.fromkeys(str(x) for x in policy.get('traversable_relations') or []));invalid=[r for r in relations if r not in AOR_EDGE_TYPES]
    if invalid:raise ValueError(f'unknown traversable relations {invalid}')
    try:max_depth=int(policy.get('max_depth',12))
    except (TypeError,ValueError):raise ValueError('max_depth must be integer')
    if max_depth<0:raise ValueError('max_depth must be >=0')
    policy={**policy,'traversable_relations':relations,'max_depth':max_depth,'require_witness':bool(policy.get('require_witness',True)),'allowed_statuses':list(dict.fromkeys(str(x).upper() for x in (policy.get('allowed_statuses') or ['ACTIVE'])))}
    groups,origins=_normalize_sources(sources);edge_rows=[];adj={};seen=set()
    for index,raw in enumerate(edges or []):
        edge=dict(raw);eid=_edge_id(edge,index)
        if eid in seen:raise ValueError(f'duplicate edge id {eid}')
        seen.add(eid);src=str(edge.get('src') or '');dst=str(edge.get('dst') or '')
        if not src or not dst:raise ValueError(f'edge {eid} requires src,dst')
        ok,defects=_admissible(edge,policy);row={**edge,'id':eid,'src':src,'dst':dst,'admissible':ok,'defects':defects};edge_rows.append(row)
        if ok:adj.setdefault(src,[]).append(row)
    for src in adj:adj[src]=sorted(adj[src],key=lambda e:(e['relation'],e['dst'],e['id']))
    reached=set(origins);paths={node:{'start':node,'origin_groups':origins[node],'edges':[],'nodes':[node],'depth':0} for node in sorted(origins)};queue=deque(sorted(origins))
    while queue:
        node=queue.popleft();path=paths[node]
        if path['depth']>=max_depth:continue
        for edge in adj.get(node,[]):
            dst=edge['dst']
            if dst in reached:continue
            reached.add(dst);paths[dst]={'start':path['start'],'origin_groups':path['origin_groups'],'edges':path['edges']+[edge['id']],'nodes':path['nodes']+[dst],'relations':[*(path.get('relations') or []),edge['relation']],'depth':path['depth']+1};queue.append(dst)
    target_rows=[];gap=[];measurement=[];target_ids=set()
    for index,raw in enumerate(targets or []):
        target=dict(raw);tid=str(target.get('id') or f'target:{index:04d}');node=str(target.get('node') or '')
        if tid in target_ids:raise ValueError(f'duplicate target id {tid}')
        target_ids.add(tid)
        if not node:raise ValueError(f'target {tid} requires node')
        covered=node in reached;score=_residual_score(target) if not covered else {'status':'N/A_COVERED','value':None,'components':{},'defects':[]};row={**target,'id':tid,'node':node,'covered':covered,'closure_path':paths.get(node),'residual_score':score};target_rows.append(row)
        if not covered:
            gap.append(row)
            if score['status']!='KNOWN':measurement.append({'target':tid,'node':node,'defects':score['defects']})
    ranked=sorted((row for row in gap if row['residual_score']['status']=='KNOWN'),key=lambda row:(-float(row['residual_score']['value']),row['id']));grow=ranked[0] if ranked else None;rejected=[{'id':e['id'],'src':e['src'],'dst':e['dst'],'relation':e.get('relation'),'defects':e['defects']} for e in edge_rows if not e['admissible']]
    return {'closure_kind':'WITNESSED_DIRECTED_REACHABILITY_NOT_LOGICAL_PROOF','policy':policy,'source_groups':groups,'closure_nodes':sorted(reached),'closure_paths':paths,'admissible_edge_ids':[e['id'] for e in edge_rows if e['admissible']],'rejected_edges':rejected,'targets':target_rows,'covered_target_ids':[r['id'] for r in target_rows if r['covered']],'gap_target_ids':[r['id'] for r in gap],'gap':gap,'ranked_gap_ids':[r['id'] for r in ranked],'grow':grow,'measurement_plan':measurement,'law':'gap = explicit target nodes - witnessed directed reachability closure; grow = max severity*leverage*information_gain/cost among uncovered KNOWN residuals','epistemic_boundary':'reachability is navigation closure only; logical/causal entailment requires separately registered operator semantics'}
