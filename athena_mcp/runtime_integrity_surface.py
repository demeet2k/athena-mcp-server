from __future__ import annotations

from pathlib import Path
from typing import Any,Dict

from .architecture_drift import MATURE_ORGANS,audit_architecture,inventory_manifest
from .architecture_drift_protocol import ARCHITECTURE_DRIFT_RESOURCES,ARCHITECTURE_DRIFT_TOOLS,ARCHITECTURE_DRIFT_TOOL_NAMES
from .composition_integrity import composition_certificate
from .coordination_manifest import EFFECTIVE_UNIFIED_MANIFEST_VERSION,build_effective_manifest,effective_layers,effective_maxdev_law
from .github_promotion_verifier import GITHUB_PROMOTION_VERIFIER_VERSION,GithubPromotionVerifier
from .promotion import PromotionLedger
from .promotion_protocol import PROMOTION_RESOURCE,PROMOTION_TOOLS,PROMOTION_TOOL_NAMES
from .self_test import SelfTestRuntime
from .self_test_protocol import SELF_TEST_RESOURCE,SELF_TEST_TOOLS,SELF_TEST_TOOL_NAMES
from .startup_health import StartupHealth
from .startup_health_protocol import STARTUP_HEALTH_RESOURCE,STARTUP_HEALTH_TOOLS,STARTUP_HEALTH_TOOL_NAMES
from .state_foundation_protocol import STATE_FOUNDATION_RESOURCES,STATE_FOUNDATION_RESOURCE_URIS,STATE_FOUNDATION_TOOLS,STATE_FOUNDATION_TOOL_NAMES
from .state_foundation_surface import StateFoundationSurface
from .state_projection import OMEGA_COMPONENTS
from .surface_contract import audit_surface,contract_manifest
from .surface_protocol import SURFACE_RESOURCE,SURFACE_TOOLS,SURFACE_TOOL_NAMES
from .unified_manifest_protocol import UNIFIED_MANIFEST_RESOURCES,UNIFIED_MANIFEST_TOOLS,UNIFIED_MANIFEST_TOOL_NAMES

INTEGRITY_TOOLS=(
    list(SURFACE_TOOLS)+list(PROMOTION_TOOLS)+list(STATE_FOUNDATION_TOOLS)+
    list(SELF_TEST_TOOLS)+list(STARTUP_HEALTH_TOOLS)+list(UNIFIED_MANIFEST_TOOLS)+list(ARCHITECTURE_DRIFT_TOOLS)
)
INTEGRITY_RESOURCES=(
    [SURFACE_RESOURCE,PROMOTION_RESOURCE]+list(STATE_FOUNDATION_RESOURCES)+
    [SELF_TEST_RESOURCE,STARTUP_HEALTH_RESOURCE]+list(UNIFIED_MANIFEST_RESOURCES)+list(ARCHITECTURE_DRIFT_RESOURCES)
)
INTEGRITY_TOOL_NAMES=(
    set(SURFACE_TOOL_NAMES)|set(PROMOTION_TOOL_NAMES)|set(STATE_FOUNDATION_TOOL_NAMES)|
    set(SELF_TEST_TOOL_NAMES)|set(STARTUP_HEALTH_TOOL_NAMES)|set(UNIFIED_MANIFEST_TOOL_NAMES)|set(ARCHITECTURE_DRIFT_TOOL_NAMES)
)
INTEGRITY_RESOURCE_URIS={resource['uri'] for resource in INTEGRITY_RESOURCES}


def _flatten_dict_values(groups):
    out=set()
    for values in groups.values():out.update(values)
    return out


class RuntimeIntegritySurface:
    """State foundation, local health, architectural self-certification and promotion trust boundary."""

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

    def architecture_drift_audit(self,include_repository_witnesses=False):
        tool_names,resource_uris=self._observed_surface();surface=contract_manifest()
        req_tools=_flatten_dict_values(surface['required_tools']);req_resources=_flatten_dict_values(surface['required_resources'])
        ci_text='';available_paths=None
        if include_repository_witnesses:
            root=Path(__file__).resolve().parents[1];ci_path=root/'.github/workflows/ci.yml'
            if ci_path.exists():ci_text=ci_path.read_text(encoding='utf-8',errors='replace')
            expected=set()
            for organ in MATURE_ORGANS:
                expected.update(str(path) for path in organ.get('source_refs') or [])
                expected.update(str(path) for path in organ.get('spec_refs') or [])
            available_paths={path for path in expected if (root/path).exists()}
        return audit_architecture(
            observed_tools=tool_names,observed_resources=resource_uris,manifest_layers=effective_layers(),
            surface_required_tools=req_tools,surface_required_resources=req_resources,omega_components=OMEGA_COMPONENTS,
            ci_text=ci_text,available_paths=available_paths,
            classified_tool_baseline=req_tools,classified_resource_baseline=req_resources,
        )

    def surface_audit(self,run_probes=True):
        tool_names,resource_uris=self._observed_surface();raw=audit_surface(tool_names,resource_uris)
        composition=composition_certificate(self.server,run_probes=run_probes);drift=self.architecture_drift_audit(False)
        raw['surface_status']=raw['status'];raw['composition']=composition;raw['architecture_drift']=drift
        raw['status']='PASS' if raw['surface_status']=='PASS' and composition['status']=='PASS' and drift['status']=='PASS' else 'FAIL'
        raw['promotion_ready_locally']=raw['status']=='PASS'
        return raw

    def call_tool(self,name:str,args:Dict[str,Any]):
        if name=='athena_runtime_manifest':return True,build_effective_manifest(self.server)
        if name=='athena_maxdev_law':return True,{'text':effective_maxdev_law()}
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
            qualified=self.promotion.evaluate('Server',head,surface,verification['ci_witness'],verification['smoke_witness'],local_git,args.get('actor','GITHUB.PROMOTION.VERIFIER'),args.get('persist',True),verification['trusted_external_verification'])
            return True,{**qualified,'github_verification':verification}
        if name=='athena_promotion_get':return True,self.promotion.get(args['run_id'])
        if name=='athena_promotion_replay':return True,self.promotion.replay(args['run_id'])
        if name=='athena_promotion_recent':return True,self.promotion.recent(args.get('limit',20))
        return False,None

    def read_resource(self,uri:str):
        if uri=='athena://runtime/unified-manifest':return build_effective_manifest(self.server)
        if uri=='athena://runtime/maxdev':return {'mimeType':'text/plain','text':effective_maxdev_law()}
        if uri=='athena://architecture/inventory':return inventory_manifest()
        if uri=='athena://architecture/drift':return {'inventory':inventory_manifest(),'latest':self.architecture_drift_audit(False),'law':'declared mature organs must agree across runtime discovery, SURFACE, effective manifest and OMEGA; repository CI/source witnesses are available through the explicit audit option'}
        if uri==STARTUP_HEALTH_RESOURCE['uri']:
            return {'version':'ATHENA.STARTUP.1','latest':self.startup.evaluate(False),'law':'local startup readiness is typed separately from external promotion; reads remain available while degraded and write blocking requires explicit per-tool policy'}
        if uri==SELF_TEST_RESOURCE['uri']:
            return {'version':'ATHENA.SELFTEST.1','description':self.self_test.describe(),'latest':self.self_test.run(10,True),'law':'local readiness requires surface+composition+architecture-drift+schema+OMEGA+sampled replay health; trusted external qualification remains a separate promotion trust plane'}
        if uri in STATE_FOUNDATION_RESOURCE_URIS:return self.state_foundation.read_resource(uri)
        if uri==SURFACE_RESOURCE['uri']:
            return {'contract':contract_manifest(),'audit':self.surface_audit(True),'law':'SURFACE.2 discovery PASS is necessary but not sufficient; declared mature organs must also pass architecture-drift and COMPOSITION gates before PROMOTION.2 readiness'}
        if uri==PROMOTION_RESOURCE['uri']:
            return {'version':'ATHENA.PROMOTION.2','compat':['ATHENA.PROMOTION.1'],'benchmark':self.promotion.benchmark(),'recent':self.promotion.recent(50),'github_verifier':self.github_promotion_verifier.describe(),'architecture_drift':self.architecture_drift_audit(False),'law':'ATTESTED_READY iff unified Server + SURFACE.2 + COMPOSITION.2 + ARCHITECTURE.DRIFT.1 + configured local Git gate + caller-bound CI/smoke packets all PASS on the same exact head; QUALIFIED additionally requires an internal trusted verifier receipt.','boundary':'unclassified live surfaces are exposed as expansion pressure but do not become mature or authoritative by adjacency; failed declared-organ integration blocks local promotion readiness.'}
        raise KeyError(uri)

    def benchmark(self):
        result={};result.update(self.promotion.benchmark());result.update(self.state_foundation.benchmark());drift=self.architecture_drift_audit(False)
        result['self_test_version']='ATHENA.SELFTEST.1';result['startup_health_version']='ATHENA.STARTUP.1';result['unified_manifest_version']=EFFECTIVE_UNIFIED_MANIFEST_VERSION;result['promotion_version']='ATHENA.PROMOTION.2'
        result['github_promotion_verifier_version']=GITHUB_PROMOTION_VERIFIER_VERSION;result['github_promotion_verifier_configured']=self.github_promotion_verifier.describe()['configured']
        result['organ_inventory_version']=drift['organ_inventory_version'];result['architecture_drift_version']=drift['version'];result['architecture_drift_status']=drift['status'];result['architecture_drift_count']=drift['drift_count'];result['unclassified_surface_count']=drift['unclassified_surface']['count']
        return result
