from __future__ import annotations

import json,sys,time
from .core import StaleTarget
from .git_backend import GitStaleHead
from .kc144 import station_manifest
from .validate import validate
from .protocol import PROTOCOL_VERSION,SERVER_INFO,TOOLS,PROMPTS
from .timebundle import TIME_PROVENANCE
from .orchestration import orchestration_law
from .orchestration_robustness import SUCCESSOR_FACTOR_COUNT
from .aor_development_surface import AOR_DEVELOPMENT_RESOURCES,AOR_DEVELOPMENT_RESOURCE_URIS
from .collective_science import CollectiveScienceRuntime
from .collective_discovery import CollectiveDiscoveryRuntime
from .collective_v6_protocol import CLAIM_NAMESPACE_LAW
from .unified_manifest import build_unified_manifest,maxdev_law

# Canonical introspection must not perturb the state it is observing. Operational
# tool usage remains metered; health/state/manifest reads use the causal event
# ledgers they inspect rather than creating a telemetry event about the read.
NON_SELF_METERING={
    'athena_omega_state','athena_schema_status','athena_schema_plan','athena_schema_verify',
    'athena_self_test','athena_startup_health','athena_surface_audit','athena_runtime_manifest','athena_maxdev_law',
    'athena_benchmark','athena_git_status','athena_reconstruction_get','athena_reconstruction_verify','athena_reconstruction_recent',
}


def _meter(server,name,started,status):
    if name in NON_SELF_METERING:return
    try:server.collective_learning.record_runtime_usage(name,time.perf_counter()-started,status)
    except Exception:pass


def _science(server):return CollectiveScienceRuntime(server.store,server.collective,server.collective_growth,server.collective_memory,server.collective_learning,server.collective_ecology)
def _discovery(server):return CollectiveDiscoveryRuntime(_science(server))


def handle(server,m):
    mid=m.get('id');method=m.get('method');params=m.get('params') or {}
    if method=='initialize':
        pv=params.get('protocolVersion',PROTOCOL_VERSION)
        return server.result(mid,{'protocolVersion':PROTOCOL_VERSION if pv!=PROTOCOL_VERSION else pv,'capabilities':{'tools':{'listChanged':False},'resources':{'listChanged':False},'prompts':{'listChanged':False}},'serverInfo':SERVER_INFO})
    if method in ('notifications/initialized','notifications/cancelled'):return None
    if method=='ping':return server.result(mid,{})
    if method=='tools/list':return server.result(mid,{'tools':sorted(TOOLS,key=lambda x:x['name'])})
    if method=='tools/call':
        name=params.get('name');args=params.get('arguments') or {}
        if not server.rate.allow(name):return server.result(mid,{'content':[{'type':'text','text':'Rate limit exceeded; retry later.'}],'isError':True})
        started=time.perf_counter()
        try:
            td=next((t for t in TOOLS if t['name']==name),None)
            if td is None:raise KeyError(name)
            validate(td['inputSchema'],args);value=server.call_tool(name,args);_meter(server,name,started,'OK')
            return server.result(mid,{'content':[{'type':'text','text':json.dumps(value,ensure_ascii=False,sort_keys=True)}],'structuredContent':value,'isError':False})
        except StaleTarget as e:
            _meter(server,name,started,'STALE_TARGET');return server.result(mid,{'content':[{'type':'text','text':str(e)}],'structuredContent':{'status':'STALE_TARGET','detail':str(e)},'isError':True})
        except GitStaleHead as e:
            _meter(server,name,started,'STALE_GIT_HEAD');return server.result(mid,{'content':[{'type':'text','text':str(e)}],'structuredContent':{'status':'STALE_GIT_HEAD','detail':str(e)},'isError':True})
        except (ValueError,KeyError) as e:
            _meter(server,name,started,'REJECTED');return server.result(mid,{'content':[{'type':'text','text':str(e)}],'isError':True})
        except Exception as e:
            _meter(server,name,started,'ERROR');print(f'tool error {name}: {e}',file=sys.stderr);return server.error(mid,-32603,'Internal error')
    if method=='resources/list':
        rs=[
            {'uri':'athena://manifest','name':'ATHENA Live Unified Runtime Manifest','mimeType':'application/json'},
            {'uri':'athena://kc144/stations','name':'KC144 12x12 Station Registry','mimeType':'application/json'},
            {'uri':'athena://state/head','name':'Canonical State Head','mimeType':'application/json'},
            {'uri':'athena://registry','name':'Canonical Capability Registry','mimeType':'application/json'},
            {'uri':'athena://jspace','name':'JSPACE Graph/Hypergraph','mimeType':'application/json'},
            {'uri':'athena://scale','name':'SCALE Representation Ladder','mimeType':'application/json'},
            {'uri':'athena://coordinate/charts','name':'Open-world Polycoordinate Chart Registry','mimeType':'application/json'},
            {'uri':'athena://crystals','name':'Crystallized Output Registry','mimeType':'application/json'},
            {'uri':'athena://math','name':'Mathematical Object Registry','mimeType':'application/json'},
            {'uri':'athena://time/provenance','name':'Atomic/Civil Time Provenance','mimeType':'application/json'},
            {'uri':'athena://transforms','name':'Coordinate Transform Registry / Execution History','mimeType':'application/json'},
            {'uri':'athena://emissions','name':'Final Crystal Emission Registry','mimeType':'application/json'},
            {'uri':'athena://collective/runtime','name':'Collective Intelligence Runtime V1','mimeType':'application/json'},
            {'uri':'athena://collective/growth','name':'Collective Growth Runtime V1','mimeType':'application/json'},
            {'uri':'athena://collective/v2','name':'Collective Memory Runtime V2','mimeType':'application/json'},
            {'uri':'athena://collective/v3','name':'Collective Learning Runtime V3','mimeType':'application/json'},
            {'uri':'athena://collective/v4','name':'Collective Ecology Runtime V4','mimeType':'application/json'},
            {'uri':'athena://collective/v5','name':'Collective Science Runtime V5','mimeType':'application/json'},
            {'uri':'athena://collective/v6','name':'Collective Discovery Runtime V6','mimeType':'application/json'},
            {'uri':'athena://orchestration/law','name':'AOR Developmental Decision Cortex Law','mimeType':'application/json'},
            {'uri':'athena://orchestration/recent','name':'Recent Persisted AORRUN Receipts','mimeType':'application/json'},
            {'uri':'athena://orchestration/robustness','name':'AOR Successor Robustness Law','mimeType':'application/json'},
            {'uri':'athena://branches','name':'AOR Branch Lifecycle Ledger','mimeType':'application/json'},
            {'uri':'athena://authority','name':'Typed Canonical Claim Authority Registry Y1','mimeType':'application/json'},
        ]
        known={r['uri'] for r in rs};rs.extend(r for r in AOR_DEVELOPMENT_RESOURCES if r['uri'] not in known)
        return server.result(mid,{'resources':rs})
    if method=='resources/read':
        uri=params.get('uri');c=server.core
        if uri in AOR_DEVELOPMENT_RESOURCE_URIS:val=server.aor_development.read_resource(uri)
        elif uri=='athena://manifest':val=build_unified_manifest(server)
        elif uri=='athena://kc144/stations':val=json.loads(station_manifest())
        elif uri=='athena://state/head':val=c.s.head('global') or {}
        elif uri=='athena://registry':val=c.s.rows('SELECT * FROM objects ORDER BY canonical_name')
        elif uri=='athena://jspace':val={'edges':c.s.rows('SELECT * FROM edges ORDER BY created_at DESC LIMIT 1000'),'hyperedges':c.s.rows('SELECT * FROM hyperedges ORDER BY created_at DESC LIMIT 1000')}
        elif uri=='athena://scale':val={'levels':{'S0':'RAW_EVENT','S1':'STATE_DELTA','S2':'RELATION_DELTA','S3':'MOTIF','S4':'GENERATOR','S5':'ORGAN_NATIVE_LAW'}}
        elif uri=='athena://coordinate/charts':val=c.s.rows('SELECT * FROM coordinate_charts ORDER BY name')
        elif uri=='athena://crystals':val=c.s.rows('SELECT crystal_id,oid,vid,mid,header,created_at FROM crystals ORDER BY created_at DESC LIMIT 1000')
        elif uri=='athena://math':val=c.s.rows('SELECT * FROM math_objects ORDER BY created_at DESC LIMIT 1000')
        elif uri=='athena://time/provenance':val=TIME_PROVENANCE
        elif uri=='athena://transforms':val={'transforms':c.s.rows('SELECT t.*,p.mode,p.program_json,p.metric_json FROM transforms t LEFT JOIN transform_programs p ON p.transform_id=t.transform_id ORDER BY t.created_at DESC LIMIT 1000'),'executions':c.s.rows('SELECT * FROM transform_executions ORDER BY created_at DESC LIMIT 1000')}
        elif uri=='athena://emissions':val=c.s.rows('SELECT envelope_id,crystal_id,emission_mid,visible_digest,created_at FROM emissions ORDER BY created_at DESC LIMIT 1000')
        elif uri=='athena://collective/runtime':val=server.collective.describe()
        elif uri=='athena://collective/growth':val=server.collective_growth.describe()
        elif uri=='athena://collective/v2':val=server.collective_memory.describe()
        elif uri=='athena://collective/v3':val={'runtime':server.collective_learning.describe(),'policy':server.collective_learning.policy_state(),'budget':server.collective_learning.budget_summary(limit=100),'elders':server.collective_learning.elder_rank(limit=20),'boundary':'learning predictions/elders/policy are organizational state, not Y1 evidence or canonical authority'}
        elif uri=='athena://collective/v4':val={'runtime':server.collective_ecology.describe(),'diffusion':server.collective_ecology.diffusion_matrix(),'credit':server.collective_ecology.credit_summary(limit=100),'boundary':'bandit/credit/diffusion/projection state remains model/routing state unless separately witnessed into an authority/evidence surface'}
        elif uri=='athena://collective/v5':
            science=_science(server);val={'runtime':science.describe(),'delayed_credit':science.delayed_credit_summary(limit=100),'learned_regime_geometry':science.regime_geometry_resolve({},top_k=10),'boundary':'POSTERIOR != TRUTH; EIG != EVIDENCE; ROLLOUT != EXECUTION; interaction/delay require identification before causal claims'}
        elif uri=='athena://collective/v6':val={'runtime':_discovery(server).describe(),'claim_namespace':CLAIM_NAMESPACE_LAW,'boundary':'V6 discovery models/claims are science-shadow state; athena_discovery_claim_* never mutates Y1 athena_claim_* canonical authority'}
        elif uri=='athena://orchestration/law':val={**orchestration_law(),'authority_law':'Y in {?,+,!,#} is persistent, non-skippable and distinct from score/confidence/consensus/reward; linked candidates snapshot Y state into AORRUN','dedup_law':'UNKNOWN sameness preserves identity; only witnessed contradiction-free EQ1 components may collapse'}
        elif uri=='athena://orchestration/recent':val=server.orchestration.recent(50)
        elif uri=='athena://orchestration/robustness':val={'version':'AOR.3.2','successor_factor_count':SUCCESSOR_FACTOR_COUNT,'law':'q*((1-eps)/(1+eps))^5; eps*=(q^(1/5)-1)/(q^(1/5)+1)','boundary':'rank sensitivity, not truth probability or causal evidence'}
        elif uri=='athena://branches':val={'benchmark':server.branches.benchmark(),'recent':server.branches.list(limit=100),'law':'branch lifecycle is basis-specific witnessed EWMA state; hibernate != erase; resurrection requires new evidence/gap/bridge pressure plus policy thresholds'}
        elif uri=='athena://authority':val={'benchmark':server.authority.benchmark(),'claims':server.authority.list(limit=100),'law':'?->+ verified evidence; +->! witnessed execution; !-># explicit authorized canonicalization; challenges block automatic routing; authority != confidence != consensus != reward; V6 discovery shadow claims use athena_discovery_claim_* and cannot alias this registry'}
        else:return server.error(mid,-32002,'Resource not found',{'uri':uri})
        return server.result(mid,{'contents':[{'uri':uri,'mimeType':'application/json','text':json.dumps(val,ensure_ascii=False,sort_keys=True)}]})
    if method=='prompts/list':return server.result(mid,{'prompts':PROMPTS})
    if method=='prompts/get':
        if params.get('name')!='athena_maxdev':return server.error(mid,-32602,'Unknown prompt')
        a=params.get('arguments') or {};task=a.get('task','');agent=a.get('agent','ATHENA')
        text='ATHENA UNIFIED AOR×COLLECTIVE V6 MAXDEV\nAGENT='+str(agent)+'\nTASK='+str(task)+'\n'+maxdev_law()
        return server.result(mid,{'description':'Unified AOR decision cortex × Y1 authority × EQ/SX/RAG/HUG/GAP/FIELD × Collective V1–V6 execution/science/discovery cycle','messages':[{'role':'user','content':{'type':'text','text':text}}]})
    return server.error(mid,-32601,'Method not found')
