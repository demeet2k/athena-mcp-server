from __future__ import annotations

from typing import Any

V16_RESOURCE={
    'uri':'athena://collective/v16',
    'name':'Collective Generalized Scientific-Control Runtime V16',
    'mimeType':'application/json',
}
V16_LAYER='COLLECTIVE_GENERALIZED_V16'
V16_MANIFEST='ATHENA.RUNTIME.UNIFIED.12'
V16_PACKAGE_VERSION='3.5.0'
V16_COORDINATE='COLLECTIVE_GENERALIZED=<OG,MH,GM,EF,NR,L>'
V16_LAWS=[
    'ORDER_CONSTRAINED_DAG_POSTERIOR != GENERAL_CAUSAL_GRAPH_POSTERIOR',
    'BOUNDED_MULTISTAGE_CROSS_FITTED_DR != ARBITRARY_HORIZON_LONGITUDINAL_THEOREM',
    'FINITE_GAUSSIAN_MIXTURE != GENERAL_NON_GAUSSIAN_BAYES',
    'CV_RESIDUAL_QUANTILE != DISTRIBUTION_FREE_ERROR_CERTIFICATE',
    'FINITE_FIXED_MODEL_FAMILY_POLICY_EVALUATION != GENERAL_NONRECTANGULAR_DRO_OPTIMIZATION',
]


def _generalized(server):
    from .collective_v15_install import _calibrated
    from .collective_generalized import CollectiveGeneralizedRuntime
    return CollectiveGeneralizedRuntime(_calibrated(server))


def install_release_v16(namespace: dict[str, Any]) -> None:
    if namespace.get('_ATHENA_COLLECTIVE_V16_INSTALLED'):
        return

    protocol=namespace['_protocol']
    from .collective_v16_protocol import COLLECTIVE_V16_TOOLS,COLLECTIVE_V16_TOOL_NAMES
    for tool in COLLECTIVE_V16_TOOLS:
        if not any(existing['name']==tool['name'] for existing in protocol.TOOLS):
            protocol.TOOLS.append(tool)

    namespace['__version__']=V16_PACKAGE_VERSION
    server_info={
        'name':'athena-canonical-mcp',
        'version':V16_PACKAGE_VERSION,
        'description':'Canonical KC144/JSPACE/SCALE developmental control with order-constrained structural posterior inference, bounded multistage longitudinal DR, finite Gaussian-mixture belief, learned error fields, and coupled model-family robust policy evaluation',
    }
    namespace['SERVER_INFO']=server_info
    protocol.SERVER_INFO=dict(server_info)

    from . import dispatch as dispatch_module
    dispatch_module.SERVER_INFO=dict(server_info)

    # Intercept only V16 tool names at the Server boundary. All inherited tool
    # routing remains on its already-qualified V1-V15 path.
    Server=namespace['Server']
    if not getattr(Server,'_athena_collective_v16_installed',False):
        previous_call=Server.call_tool
        from . import collective_v16_dispatch
        def call_tool_v16(self,name,args):
            if name in COLLECTIVE_V16_TOOL_NAMES:
                return collective_v16_dispatch.call(_generalized(self),name,args)
            return previous_call(self,name,args)
        Server.call_tool=call_tool_v16
        Server._athena_collective_v16_installed=True

    from . import unified_manifest_protocol as ump
    if V16_RESOURCE['uri'] not in ump.UNIFIED_MANIFEST_RESOURCE_URIS:
        ump.UNIFIED_MANIFEST_RESOURCES.append(dict(V16_RESOURCE))
        ump.UNIFIED_MANIFEST_RESOURCE_URIS.add(V16_RESOURCE['uri'])

    from . import unified_manifest as um
    if not getattr(um,'_athena_collective_v16_installed',False):
        original_build=um.build_unified_manifest
        original_maxdev=um.maxdev_law
        um.UNIFIED_MANIFEST_VERSION=V16_MANIFEST

        def build_unified_manifest_v16(server):
            payload=original_build(server)
            payload['artifact']=V16_MANIFEST
            compat=list(payload.get('artifact_compat') or [])
            if 'ATHENA.RUNTIME.UNIFIED.11' not in compat:compat.append('ATHENA.RUNTIME.UNIFIED.11')
            payload['artifact_compat']=compat
            layers=list(payload.get('layers') or [])
            if V16_LAYER not in layers:
                insert_at=layers.index('GITHUB_PROMOTION_VERIFIER.1') if 'GITHUB_PROMOTION_VERIFIER.1' in layers else len(layers)
                layers.insert(insert_at,V16_LAYER)
            payload['layers']=layers
            organs=dict(payload.get('organs') or {});organs['collective_v16']=_generalized(server).describe();payload['organs']=organs
            cycle=str(payload.get('cycle','')).replace('COLLECTIVE(V1-V15)','COLLECTIVE(V1-V16)').replace('Collective(V1-V15)','Collective(V1-V16)');payload['cycle']=cycle
            navigation=str(payload.get('navigation',''))
            navigation=navigation.replace('COLLECTIVE_CALIBRATED_V15 <-> PROMOTION_TRUST_V2','COLLECTIVE_CALIBRATED_V15 <-> COLLECTIVE_GENERALIZED_V16 <-> PROMOTION_TRUST_V2')
            navigation=navigation.replace('COLLECTIVE_CALIBRATED_V15 <-> Git/MCP','COLLECTIVE_CALIBRATED_V15 <-> COLLECTIVE_GENERALIZED_V16 <-> Git/MCP')
            navigation=navigation.replace('Collective(V1-V15)','Collective(V1-V16)')
            if V16_LAYER not in navigation:navigation=f'{navigation} <-> {V16_LAYER}' if navigation else V16_LAYER
            payload['navigation']=navigation
            invariants=list(payload.get('invariants') or [])
            for law in V16_LAWS:
                if law not in invariants:invariants.append(law)
            payload['invariants']=invariants
            payload['collective_generalized']={
                'version':'COLLECTIVE_RUNTIME_V16','coordinate':V16_COORDINATE,'authority':'MODEL_SCIENCE_TWIN_AND_PLAN_ONLY','laws':list(V16_LAWS),
                'scope':{
                    'ordered_dag_max_variables':5,'multistage_dr_max_treatments':6,'gaussian_mixture_max_components':16,
                    'error_field_max_witnesses':96,'coupled_model_max_models':8,'coupled_policy_max_horizon':6,
                },
            }
            for unresolved in payload.get('unresolved') or []:
                uid=unresolved.get('id')
                if uid=='FORMAL_CAUSAL_DISCOVERY':unresolved['v16_boundary']='exact posterior only inside a topological-order-constrained linear-Gaussian DAG family; unrestricted graph order, latent confounding and general causal graph posterior remain unresolved'
                elif uid=='LONGITUDINAL_CAUSAL_POLICY':unresolved['v16_boundary']='cross-fitted sequential DR across caller-declared histories for <=6 binary treatment stages; arbitrary horizon/general longitudinal DML-TMLE remains unresolved'
                elif uid=='GENERAL_BELIEF_CONTROL':unresolved['v16_boundary']='exact finite Gaussian-mixture update under shared linear-Gaussian observation; general non-Gaussian continuous belief/control remains unresolved'
                elif uid=='STOCHASTIC_RESOURCE_CONTROL':unresolved['v16_boundary']='exact evaluation of supplied policies against a finite family of globally coupled complete models; general non-rectangular DRO policy optimization remains unresolved'
            payload['braid_law']=str(payload.get('braid_law','')).replace('V1-V15','V1-V16')
            return payload

        def maxdev_law_v16():
            base=original_maxdev().replace('COLLECTIVE(V1-V15)','COLLECTIVE(V1-V16)').replace('Collective(V1-V15)','Collective(V1-V16)')
            return base+'''\n\nV16 GENERALIZED LAW:\n- ordered DAG posterior is exact only within the caller-declared topological order and implemented linear-Gaussian BIC/edge-prior family; optional external reliability calibration never turns it into causal truth;\n- multistage longitudinal DR supports at most six binary treatment stages with explicit caller-declared decision-time histories; cross-fitting cannot verify chronology or identification assumptions;\n- finite Gaussian-mixture update is exact only for the supplied mixture and shared linear-Gaussian observation model; finite mixture != general non-Gaussian Bayes;\n- learned approximation-error fields train only from explicit error witnesses; CV residual quantiles are not distribution-free coverage certificates;\n- coupled model-family robust policy evaluates supplied policies when one complete model is fixed across the whole horizon; this non-rectangular finite ambiguity surface != general non-rectangular DRO optimization;\n- every V16 operator remains model/science/control state and cannot mutate Y1, canonical JSPACE, empirical observation, execution, deployment, release or trust state by adjacency.\n'''
        um.build_unified_manifest=build_unified_manifest_v16
        um.maxdev_law=maxdev_law_v16
        um._athena_collective_v16_installed=True

    dispatch_module.build_unified_manifest=um.build_unified_manifest
    dispatch_module.maxdev_law=um.maxdev_law

    from . import surface_contract as sc
    sc.REQUIRED_TOOLS['collective_v16']=set(COLLECTIVE_V16_TOOL_NAMES)
    sc.REQUIRED_RESOURCES['collective_v16']={V16_RESOURCE['uri']}
    if not getattr(sc,'_athena_collective_v16_installed',False):
        previous_contract=sc.contract_manifest
        def contract_manifest_v16():
            payload=previous_contract();payload['law']=str(payload.get('law','')).replace('Collective V1-V15','Collective V1-V16');return payload
        sc.contract_manifest=contract_manifest_v16
        sc._athena_collective_v16_installed=True

    from . import runtime_integrity_surface as ris
    ris.UNIFIED_MANIFEST_VERSION=V16_MANIFEST
    ris.build_unified_manifest=um.build_unified_manifest
    ris.maxdev_law=um.maxdev_law
    if V16_RESOURCE['uri'] not in ris.INTEGRITY_RESOURCE_URIS:
        ris.INTEGRITY_RESOURCES.append(dict(V16_RESOURCE));ris.INTEGRITY_RESOURCE_URIS.add(V16_RESOURCE['uri'])

    from . import aor_development_surface as ads
    if V16_RESOURCE['uri'] not in ads.AOR_DEVELOPMENT_RESOURCE_URIS:
        ads.AOR_DEVELOPMENT_RESOURCES.append(dict(V16_RESOURCE));ads.AOR_DEVELOPMENT_RESOURCE_URIS.add(V16_RESOURCE['uri'])

    if not getattr(ris.RuntimeIntegritySurface,'_athena_collective_v16_installed',False):
        previous_read=ris.RuntimeIntegritySurface.read_resource
        def read_resource_v16(self,uri):
            if uri==V16_RESOURCE['uri']:
                from .collective_v6_protocol import CLAIM_NAMESPACE_LAW
                return {
                    'runtime':_generalized(self.server).describe(),'claim_namespace':CLAIM_NAMESPACE_LAW,
                    'boundary':'V16 ordered-DAG posterior, multistage DR, Gaussian-mixture belief, learned error field and coupled model-family robust policy outputs remain bounded model/science/control state. They do not mutate Y1 authority, canonical JSPACE, empirical observations, execution, deployment, release-publication or trusted promotion state by adjacency.',
                }
            return previous_read(self,uri)
        ris.RuntimeIntegritySurface.read_resource=read_resource_v16
        ris.RuntimeIntegritySurface._athena_collective_v16_installed=True

    namespace['_ATHENA_COLLECTIVE_V16_INSTALLED']=True
