from __future__ import annotations

from typing import Any,Dict

from .composition_integrity import composition_certificate
from .github_promotion_verifier import GITHUB_PROMOTION_VERIFIER_VERSION,GithubPromotionVerifier
from .promotion import PromotionLedger
from .promotion_protocol import PROMOTION_RESOURCE,PROMOTION_TOOLS,PROMOTION_TOOL_NAMES
from .self_test import SelfTestRuntime
from .self_test_protocol import SELF_TEST_RESOURCE,SELF_TEST_TOOLS,SELF_TEST_TOOL_NAMES
from .startup_health import StartupHealth
from .startup_health_protocol import STARTUP_HEALTH_RESOURCE,STARTUP_HEALTH_TOOLS,STARTUP_HEALTH_TOOL_NAMES
from .state_foundation_protocol import STATE_FOUNDATION_RESOURCES,STATE_FOUNDATION_RESOURCE_URIS,STATE_FOUNDATION_TOOLS,STATE_FOUNDATION_TOOL_NAMES
from .state_foundation_surface import StateFoundationSurface
from .surface_contract import audit_surface,contract_manifest
from .surface_protocol import SURFACE_RESOURCE,SURFACE_TOOLS,SURFACE_TOOL_NAMES
from .unified_manifest import UNIFIED_MANIFEST_VERSION,build_unified_manifest,maxdev_law
from .unified_manifest_protocol import UNIFIED_MANIFEST_RESOURCES,UNIFIED_MANIFEST_RESOURCE_URIS,UNIFIED_MANIFEST_TOOLS,UNIFIED_MANIFEST_TOOL_NAMES

INTEGRITY_TOOLS=(
    list(SURFACE_TOOLS)+list(PROMOTION_TOOLS)+list(STATE_FOUNDATION_TOOLS)+
    list(SELF_TEST_TOOLS)+list(STARTUP_HEALTH_TOOLS)+list(UNIFIED_MANIFEST_TOOLS)
)
INTEGRITY_RESOURCES=(
    [SURFACE_RESOURCE,PROMOTION_RESOURCE]+list(STATE_FOUNDATION_RESOURCES)+
    [SELF_TEST_RESOURCE,STARTUP_HEALTH_RESOURCE]+list(UNIFIED_MANIFEST_RESOURCES)
)
INTEGRITY_TOOL_NAMES=(
    set(SURFACE_TOOL_NAMES)|set(PROMOTION_TOOL_NAMES)|set(STATE_FOUNDATION_TOOL_NAMES)|
    set(SELF_TEST_TOOL_NAMES)|set(STARTUP_HEALTH_TOOL_NAMES)|set(UNIFIED_MANIFEST_TOOL_NAMES)
)
INTEGRITY_RESOURCE_URIS={resource['uri'] for resource in INTEGRITY_RESOURCES}


class RuntimeIntegritySurface:
    """State foundation, local health, self-certification and promotion trust boundary."""

    def __init__(self,server,development):
        self.server=server;self.development=development
        self.promotion=PromotionLedger(server.core)
        self.github_promotion_verifier=GithubPromotionVerifier()
        self.state_foundation=StateFoundationSurface(server,development)
        self.self_test=SelfTestRuntime(server,self)
        self.startup=StartupHealth(server,self)

    def _observed_surface(self):
        tools_response=self.server.handle({'jsonrpc':'2.0','id':'surface:tools','method':'tools/list'})
        resources_response=self.server.handle({'jsonrpc':'2.0','id':'surface:resources','method':'resources/list'})
        tools=tools_response['result']['tools'];resources=resources_response['result']['resources']
        return [tool['name'] for tool in tools],[resource['uri'] for resource in resources]

    def surface_audit(self,run_probes=True):
        tool_names,resource_uris=self._observed_surface()
        raw=audit_surface(tool_names,resource_uris)
        composition=composition_certificate(self.server,run_probes=run_probes)
        raw['surface_status']=raw['status'];raw['composition']=composition
        raw['status']='PASS' if raw['surface_status']=='PASS' and composition['status']=='PASS' else 'FAIL'
        raw['promotion_ready_locally']=raw['status']=='PASS'
        return raw

    def call_tool(self,name:str,args:Dict[str,Any]):
        if name=='athena_runtime_manifest':return True,build_unified_manifest(self.server)
        if name=='athena_maxdev_law':return True,{'text':maxdev_law()}
        if name=='athena_startup_health':return True,self.startup.evaluate(args.get('run_replay_samples',False))
        if name=='athena_self_test':return True,self.self_test.run(args.get('replay_limit',10),args.get('run_composition_probes',True))

        handled,value=self.state_foundation.call_tool(name,args)
        if handled:return True,value

        if name=='athena_surface_audit':return True,self.surface_audit(args.get('run_probes',True))
        if name=='athena_promotion_evaluate':
            surface=self.surface_audit(True);local_git=self.server.git.status()
            return True,self.promotion.evaluate('Server',args['git_head'],surface,args['ci_witness'],args['smoke_witness'],local_git,args.get('actor','agent'),args.get('persist',True))
        if name=='athena_promotion_verify_github':
            head=str(args['git_head']);verification=self.github_promotion_verifier.verify(head,args.get('timeout_s',12.0))
            if verification.get('verified') is not True:
                return True,{**verification,'promotion_allowed':False,'persisted':False,'law':'failed or unavailable independent GitHub verification creates no PROMRUN and cannot be converted into caller-attested readiness'}
            surface=self.surface_audit(True);local_git=self.server.git.status()
            qualified=self.promotion.evaluate(
                'Server',head,surface,verification['ci_witness'],verification['smoke_witness'],local_git,
                args.get('actor','GITHUB.PROMOTION.VERIFIER'),args.get('persist',True),verification['trusted_external_verification'],
            )
            return True,{**qualified,'github_verification':verification}
        if name=='athena_promotion_get':return True,self.promotion.get(args['run_id'])
        if name=='athena_promotion_replay':return True,self.promotion.replay(args['run_id'])
        if name=='athena_promotion_recent':return True,self.promotion.recent(args.get('limit',20))
        return False,None

    def read_resource(self,uri:str):
        if uri=='athena://runtime/unified-manifest':return build_unified_manifest(self.server)
        if uri=='athena://runtime/maxdev':return {'mimeType':'text/plain','text':maxdev_law()}
        if uri==STARTUP_HEALTH_RESOURCE['uri']:
            return {'version':'ATHENA.STARTUP.1','latest':self.startup.evaluate(False),'law':'local startup readiness is typed separately from external promotion; reads remain available while degraded and write blocking requires explicit per-tool policy'}
        if uri==SELF_TEST_RESOURCE['uri']:
            return {'version':'ATHENA.SELFTEST.1','description':self.self_test.describe(),'latest':self.self_test.run(10,True),'law':'local readiness requires surface+composition+schema+OMEGA+sampled replay health; trusted external qualification remains a separate promotion trust plane'}
        if uri in STATE_FOUNDATION_RESOURCE_URIS:return self.state_foundation.read_resource(uri)
        if uri==SURFACE_RESOURCE['uri']:
            return {'contract':contract_manifest(),'audit':self.surface_audit(True),'law':'SURFACE.2 discovery PASS is necessary but not sufficient; PROMOTION.2 ATTESTED_READY may use caller packets, while QUALIFIED requires an independent trusted verifier receipt'}
        if uri==PROMOTION_RESOURCE['uri']:
            return {
                'version':'ATHENA.PROMOTION.2','compat':['ATHENA.PROMOTION.1'],'benchmark':self.promotion.benchmark(),'recent':self.promotion.recent(50),
                'github_verifier':self.github_promotion_verifier.describe(),
                'law':'ATTESTED_READY iff unified Server + SURFACE.2 + COMPOSITION.2 + configured local Git gate + caller-bound CI/smoke packets all PASS on the same exact head; QUALIFIED additionally requires an internal trusted verifier receipt. GITHUB_PROMOTION_VERIFIER.1 can independently derive that receipt from one coherent host-bound GitHub Actions run/check-suite.',
                'boundary':'MCP caller witness packets never mint PROMOTION.2 QUALIFIED. athena_promotion_verify_github accepts only the target head; trusted repository/API/run identity and required checks come from host configuration, and failed GitHub verification creates no PROMRUN.',
            }
        raise KeyError(uri)

    def benchmark(self):
        result={};result.update(self.promotion.benchmark());result.update(self.state_foundation.benchmark())
        result['self_test_version']='ATHENA.SELFTEST.1';result['startup_health_version']='ATHENA.STARTUP.1';result['unified_manifest_version']=UNIFIED_MANIFEST_VERSION;result['promotion_version']='ATHENA.PROMOTION.2'
        result['github_promotion_verifier_version']=GITHUB_PROMOTION_VERIFIER_VERSION;result['github_promotion_verifier_configured']=self.github_promotion_verifier.describe()['configured']
        return result
