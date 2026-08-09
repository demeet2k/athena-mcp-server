from __future__ import annotations

import hashlib
import json
from typing import Any,Dict,Mapping

from .architecture_drift import inventory_manifest

OMEGA_VERSION='ATHENA.OMEGA.1'
OMEGA_COMPONENTS=(
    'semantic','git','core','crystal','collective','coordination','branches','authority','aor','development',
    'cycles','promotion','migrations','schema_status','reconstruction','pending_mutations'
)


def _digest(value:Any)->str:
    raw=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'))
    return hashlib.sha256(raw.encode()).hexdigest()

def _safe(call,unknown_label):
    try:return {'status':'KNOWN','value':call()}
    except Exception as exc:return {'status':'UNKNOWN','reason':unknown_label,'error':f'{type(exc).__name__}: {exc}'}


def project_omega(server)->Dict[str,Any]:
    dev=getattr(server,'aor_development',None);integrity=getattr(dev,'integrity',None) if dev else None;foundation=getattr(integrity,'state_foundation',None) if integrity else None
    semantic_head=server.store.head('global')
    coordination_inventory=inventory_manifest()
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
                'belief_v8':'constructed on V8 tool/resource access; finite beliefs, EVI/effect/bootstrap/policy and spectral evidence geometry remain model/science-shadow state',
                'inference_v9':'constructed on V9 tool/resource access; Gaussian beliefs, EVPI/EVSI, AIPW/robustness, partial graphs and dependence models remain model-conditional state',
                'probabilistic_v10':'constructed on V10 tool/resource access; fixed-kernel GP, bounded PC-stable, TMLE, E-value, finite-POMDP and learned-dependence surfaces remain model/assumption-scoped state',
                'adaptive_v11':'constructed on V11 tool/resource access; GP hyperfit/EVSI, supplied-DAG latent projection, ensemble TMLE, RR sensitivity, finite-model BAPOMDP and dependence intervals remain model/assumption-scoped state',
                'joint_v12':'constructed on V12 tool/resource access; finite-grid GP hyperposterior/BMA, subset-GP approximation, bounded PAG candidate, two-timepoint g-formula, BMA GP EVSI and chance-constrained planning remain model/assumption-scoped state',
                'robust_v13':'constructed on V13 tool/resource access; QMC continuous-domain GP hyperbelief, FITC inducing approximation, joint model-information design, bounded FCI-lite candidate, sequential two-timepoint TMLE, dynamic policy g-formula and correlated Gaussian/ellipsoidal robust resource plans remain model/assumption-scoped state',
            },
        },'collective state unavailable'),
        'coordination':{
            'status':'KNOWN',
            'inventory_version':coordination_inventory['version'],
            'organs':[{
                'id':organ['id'],'version':organ['version'],'integration_class':organ['integration_class'],
                'authority_plane':organ['authority_plane'],'manifest_layer':organ['manifest_layer'],
            } for organ in coordination_inventory['organs']],
            'boundary':'descriptor projection only; OMEGA does not fetch/sync Message Board, Cohesion or Party Git state while observing itself',
            'law':'Y1 semantic claim authority != Message Board coordination/presence authority; Cohesion and Party reward layers remain typed advisory/provenance surfaces',
        },
        'branches':_safe(lambda:{'benchmark':server.branches.benchmark(),'review':server.branches.list(status='REVIEW',limit=100),'hibernated':server.branches.list(status='HIBERNATED',limit=100)},'branch lifecycle unavailable'),
        'authority':_safe(lambda:{'benchmark':server.authority.benchmark(),'challenged':server.authority.list(status='CHALLENGED',limit=100),'canonical_challenged':server.authority.list(status='CANONICAL_CHALLENGED',limit=100),'claim_namespace':'athena_claim_* canonical Y1; athena_discovery_claim_* V6-V13 science-shadow/model evidence only; Message Board claims belong to the distinct coordination/presence plane'},'authority state unavailable'),
        'aor':_safe(lambda:{'benchmark':server.orchestration.benchmark(),'recent':server.orchestration.recent(20)},'AOR runtime unavailable'),
        'development':_safe(lambda:dev.benchmark() if dev else {},'development surface unavailable'),
        'cycles':_safe(lambda:dev.cycle.recent(20) if dev and hasattr(dev,'cycle') else [],'cycle runtime unavailable'),
        'promotion':_safe(lambda:integrity.promotion.recent(20) if integrity else [],'promotion ledger unavailable'),
        'migrations':_safe(lambda:foundation.schema.recent(20) if foundation else [],'schema migration ledger unavailable'),
        'schema_status':_safe(lambda:foundation.schema.status() if foundation else {},'schema status unavailable'),
        'reconstruction':_safe(lambda:foundation.reconstruction.recent(20) if foundation else [],'reconstruction ledger unavailable'),
        'pending_mutations':_safe(lambda:server.core.pending_mutations('ATHENA.OMEGA.1'),'pending mutation query unavailable'),
        'boundary':'OMEGA covers accessible runtime/ledger state and explicit coordination-organ descriptors only; V5-V13 lazy model construction, remote coordination state, absent external sources and unseen world state remain explicit rather than inferred',
    }
    digest_source={k:v for k,v in state.items() if k not in {'omega_id','state_digest'}};state_digest=_digest(digest_source);state['state_digest']=state_digest;state['omega_id']='OMEGA.'+state_digest[:24];return state


def omega_diff(before:Mapping[str,Any],after:Mapping[str,Any])->Dict[str,Any]:
    before=dict(before);after=dict(after);changed=[]
    for key in sorted(set(before)|set(after)):
        if key in {'state_digest','omega_id'}:continue
        if before.get(key)!=after.get(key):changed.append(key)
    return {'version':'ATHENA.OMEGA.DELTA.1','before':before.get('omega_id'),'after':after.get('omega_id'),'before_digest':before.get('state_digest'),'after_digest':after.get('state_digest'),'changed_components':changed,'changed':bool(changed),'boundary':'component change is observational delta; it does not by itself establish causality for the change'}
