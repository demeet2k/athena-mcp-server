from __future__ import annotations

import hashlib
import json
from typing import Any,Dict,Mapping

OMEGA_VERSION='ATHENA.OMEGA.1'


def _digest(value:Any)->str:
    raw=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'))
    return hashlib.sha256(raw.encode()).hexdigest()

def _safe(call,unknown_label):
    try:return {'status':'KNOWN','value':call()}
    except Exception as exc:return {'status':'UNKNOWN','reason':unknown_label,'error':f'{type(exc).__name__}: {exc}'}


def project_omega(server)->Dict[str,Any]:
    """Project current accessible runtime state into one addressable OMEGA packet."""
    dev=getattr(server,'aor_development',None);integrity=getattr(dev,'integrity',None) if dev else None;foundation=getattr(integrity,'state_foundation',None) if integrity else None
    semantic_head=server.store.head('global')
    state={
        'version':OMEGA_VERSION,
        'semantic':{'global_head':semantic_head},
        'git':_safe(lambda:server.git.status(),'git status unavailable'),
        'core':_safe(lambda:server.core.benchmark(),'core benchmark unavailable'),
        'crystal':_safe(lambda:server.crystal.benchmark_extension(),'crystal benchmark unavailable'),
        'collective':_safe(lambda:{
            'runtime_v1':server.collective.describe(),
            'growth_v1':server.collective_growth.describe(),
            'memory_v2':server.collective_memory.describe(),
            'learning_v3':server.collective_learning.describe(),
            'ecology_v4':server.collective_ecology.describe(),
            'lazy_surfaces':{
                'science_v5':'constructed on V5 tool/resource access; posterior/design/rollout state remains model-conditional',
                'discovery_v6':'constructed on V6 tool/resource access; shadow claims use athena_discovery_claim_* and never alias Y1 authority',
                'dual_control_v7':'constructed on V7 tool/resource access; uncertainty decomposition, causal skeletons, scenario/dual-control plans and replication geometry remain model/science-shadow state',
            },
        },'collective state unavailable'),
        'branches':_safe(lambda:{'benchmark':server.branches.benchmark(),'review':server.branches.list(status='REVIEW',limit=100),'hibernated':server.branches.list(status='HIBERNATED',limit=100)},'branch lifecycle unavailable'),
        'authority':_safe(lambda:{'benchmark':server.authority.benchmark(),'challenged':server.authority.list(status='CHALLENGED',limit=100),'canonical_challenged':server.authority.list(status='CANONICAL_CHALLENGED',limit=100),'claim_namespace':'athena_claim_* canonical Y1; athena_discovery_claim_* V6/V7 science-shadow only'},'authority state unavailable'),
        'aor':_safe(lambda:{'benchmark':server.orchestration.benchmark(),'recent':server.orchestration.recent(20)},'AOR runtime unavailable'),
        'development':_safe(lambda:dev.benchmark() if dev else {},'development surface unavailable'),
        'cycles':_safe(lambda:dev.cycle.recent(20) if dev and hasattr(dev,'cycle') else [],'cycle runtime unavailable'),
        'promotion':_safe(lambda:integrity.promotion.recent(20) if integrity else [],'promotion ledger unavailable'),
        'migrations':_safe(lambda:foundation.schema.recent(20) if foundation else [],'schema migration ledger unavailable'),
        'schema_status':_safe(lambda:foundation.schema.status() if foundation else {},'schema status unavailable'),
        'reconstruction':_safe(lambda:foundation.reconstruction.recent(20) if foundation else [],'reconstruction ledger unavailable'),
        'pending_mutations':_safe(lambda:server.core.pending_mutations('ATHENA.OMEGA.1'),'pending mutation query unavailable'),
        'boundary':'OMEGA covers accessible runtime/ledger state only; V5/V6/V7 lazy model construction, absent external sources and unseen world state remain explicit rather than inferred',
    }
    digest_source={k:v for k,v in state.items() if k not in {'omega_id','state_digest'}};state_digest=_digest(digest_source);state['state_digest']=state_digest;state['omega_id']='OMEGA.'+state_digest[:24];return state


def omega_diff(before:Mapping[str,Any],after:Mapping[str,Any])->Dict[str,Any]:
    before=dict(before);after=dict(after);changed=[]
    for key in sorted(set(before)|set(after)):
        if key in {'state_digest','omega_id'}:continue
        if before.get(key)!=after.get(key):changed.append(key)
    return {'version':'ATHENA.OMEGA.DELTA.1','before':before.get('omega_id'),'after':after.get('omega_id'),'before_digest':before.get('state_digest'),'after_digest':after.get('state_digest'),'changed_components':changed,'changed':bool(changed),'boundary':'component change is observational delta; it does not by itself establish causality for the change'}
