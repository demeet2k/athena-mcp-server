from __future__ import annotations

from typing import Any,Dict

from .composition_integrity import composition_certificate
from .promotion import PromotionLedger
from .promotion_protocol import PROMOTION_RESOURCE,PROMOTION_TOOLS,PROMOTION_TOOL_NAMES
from .surface_contract import audit_surface,contract_manifest
from .surface_protocol import SURFACE_RESOURCE,SURFACE_TOOLS,SURFACE_TOOL_NAMES

INTEGRITY_TOOLS=list(SURFACE_TOOLS)+list(PROMOTION_TOOLS)
INTEGRITY_RESOURCES=[SURFACE_RESOURCE,PROMOTION_RESOURCE]
INTEGRITY_TOOL_NAMES=set(SURFACE_TOOL_NAMES)|set(PROMOTION_TOOL_NAMES)
INTEGRITY_RESOURCE_URIS={resource['uri'] for resource in INTEGRITY_RESOURCES}


class RuntimeIntegritySurface:
    """Self-certification and exact-head promotion boundary for the unified runtime.

    SURFACE.2 checks discovery. COMPOSITION.2 checks the actual single-Server
    organ graph and representative read-only dispatch paths. PROMOTION.1 binds
    those local certificates to caller-supplied external CI/smoke attestations
    naming the exact same Git head. An external attestation is preserved as an
    attestation; this layer never relabels it as independently fetched evidence.
    """

    def __init__(self,server):
        self.server=server
        self.promotion=PromotionLedger(server.core)

    def _observed_surface(self):
        tools_response=self.server.handle({'jsonrpc':'2.0','id':'surface:tools','method':'tools/list'})
        resources_response=self.server.handle({'jsonrpc':'2.0','id':'surface:resources','method':'resources/list'})
        tools=tools_response['result']['tools'];resources=resources_response['result']['resources']
        return [tool['name'] for tool in tools],[resource['uri'] for resource in resources]

    def surface_audit(self,run_probes=True):
        tool_names,resource_uris=self._observed_surface()
        raw=audit_surface(tool_names,resource_uris)
        composition=composition_certificate(self.server,run_probes=run_probes)
        raw['surface_status']=raw['status']
        raw['composition']=composition
        raw['status']='PASS' if raw['surface_status']=='PASS' and composition['status']=='PASS' else 'FAIL'
        raw['promotion_ready_locally']=raw['status']=='PASS'
        return raw

    def call_tool(self,name:str,args:Dict[str,Any]):
        if name=='athena_surface_audit':
            return True,self.surface_audit(args.get('run_probes',True))
        if name=='athena_promotion_evaluate':
            surface=self.surface_audit(True)
            local_git=self.server.git.status()
            return True,self.promotion.evaluate(
                'Server',args['git_head'],surface,args['ci_witness'],args['smoke_witness'],local_git,
                args.get('actor','agent'),args.get('persist',True),
            )
        if name=='athena_promotion_get':return True,self.promotion.get(args['run_id'])
        if name=='athena_promotion_replay':return True,self.promotion.replay(args['run_id'])
        if name=='athena_promotion_recent':return True,self.promotion.recent(args.get('limit',20))
        return False,None

    def read_resource(self,uri:str):
        if uri==SURFACE_RESOURCE['uri']:
            return {
                'contract':contract_manifest(),
                'audit':self.surface_audit(True),
                'law':'SURFACE.2 discovery PASS is necessary but not sufficient; unified promotion additionally requires COMPOSITION.2 PASS and exact-head CI/smoke witnesses',
            }
        if uri==PROMOTION_RESOURCE['uri']:
            return {
                'version':'ATHENA.PROMOTION.1',
                'benchmark':self.promotion.benchmark(),
                'recent':self.promotion.recent(50),
                'law':'QUALIFIED iff unified Server + SURFACE.2 + COMPOSITION.2 + local Git match when configured + external CI and smoke attestations all PASS on the same exact head',
                'boundary':'CI/smoke witness packets are external attestations supplied by the caller; PROMRUN preserves their exact refs/head/conclusion but does not independently query GitHub',
            }
        raise KeyError(uri)

    def benchmark(self):
        return self.promotion.benchmark()
