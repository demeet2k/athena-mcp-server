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
    """Project current accessible runtime state into one addressable Ω packet.

    This is an observation of connected/local runtime state only. UNKNOWN is
    preserved for unavailable components and the projection never claims unseen
    external systems were reconstructed.
    """
    dev=getattr(server,'aor_development',None)
    semantic_head=server.store.head('global')
    git=_safe(lambda:server.git.status(),'git status unavailable')
    topology=_safe(lambda:server.collective_memory.describe(),'collective memory/topology summary unavailable')
    branches=_safe(lambda:{'benchmark':server.branches.benchmark(),'review':server.branches.list(status='REVIEW',limit=100),'hibernated':server.branches.list(status='HIBERNATED',limit=100)},'branch lifecycle unavailable')
    authority=_safe(lambda:{'benchmark':server.authority.benchmark(),'challenged':server.authority.list(status='CHALLENGED',limit=100),'canonical_challenged':server.authority.list(status='CANONICAL_CHALLENGED',limit=100)},'authority state unavailable')
    aor=_safe(lambda:{'benchmark':server.orchestration.benchmark(),'recent':server.orchestration.recent(20)},'AOR runtime unavailable')
    development=_safe(lambda:dev.benchmark() if dev else {},'development surface unavailable')
    cycles=_safe(lambda:dev.cycle.recent(20) if dev and hasattr(dev,'cycle') else [],'cycle runtime unavailable')
    promotion=_safe(lambda:dev.integrity.promotion.recent(20) if dev and hasattr(dev,'integrity') else [],'promotion ledger unavailable')
    migrations=_safe(lambda:dev.state_foundation.schema.recent(20) if dev and hasattr(dev,'state_foundation') else [],'schema migration ledger unavailable')
    core=_safe(lambda:server.core.benchmark(),'core benchmark unavailable')
    crystal=_safe(lambda:server.crystal.benchmark_extension(),'crystal benchmark unavailable')
    collective=_safe(lambda:{'runtime':server.collective.describe(),'growth':server.collective_growth.describe(),'memory':server.collective_memory.describe()},'collective state unavailable')
    state={
        'version':OMEGA_VERSION,
        'semantic':{'global_head':semantic_head},
        'git':git,
        'core':core,
        'crystal':crystal,
        'collective':collective,
        'topology_memory':topology,
        'branches':branches,
        'authority':authority,
        'aor':aor,
        'development':development,
        'cycles':cycles,
        'promotion':promotion,
        'migrations':migrations,
        'pending_mutations':_safe(lambda:server.core.pending_mutations('ATHENA.OMEGA.1'),'pending mutation query unavailable'),
        'boundary':'Ω projection covers accessible runtime/ledger state only; absent external sources remain UNKNOWN and are not inferred',
    }
    digest_source={k:v for k,v in state.items() if k not in {'omega_id','state_digest'}}
    state_digest=_digest(digest_source)
    state['state_digest']=state_digest
    state['omega_id']='OMEGA.'+state_digest[:24]
    return state


def omega_diff(before:Mapping[str,Any],after:Mapping[str,Any])->Dict[str,Any]:
    before=dict(before);after=dict(after);changed=[]
    keys=sorted(set(before)|set(after))
    for key in keys:
        if key in {'state_digest','omega_id'}:continue
        if before.get(key)!=after.get(key):changed.append(key)
    return {
        'version':'ATHENA.OMEGA.DELTA.1',
        'before':before.get('omega_id'),'after':after.get('omega_id'),
        'before_digest':before.get('state_digest'),'after_digest':after.get('state_digest'),
        'changed_components':changed,
        'changed':bool(changed),
        'boundary':'component change is observational delta; it does not by itself establish causality for the change',
    }
