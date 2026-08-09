from __future__ import annotations

from typing import Any

V14_RESOURCE={
    'uri':'athena://collective/v14',
    'name':'Collective Joint Posterior Scientific-Control Runtime V14',
    'mimeType':'application/json',
}
V14_LAYER='COLLECTIVE_SYNTHESIS_V14'
V14_MANIFEST='ATHENA.RUNTIME.UNIFIED.10'
V14_PACKAGE_VERSION='3.3.0'
V14_COORDINATE='COLLECTIVE_SYNTHESIS=<JB,SE,JE,DR,RP,AZ,MR,L>'
V14_LAWS=[
    'FINITE_FACTOR_PRODUCT_BELIEF != FULL_JOINT_POSTERIOR',
    'BOOTSTRAP_GRAPH_FREQUENCY != CAUSAL_POSTERIOR',
    'JOINT_SCIENCE_EVI != OBSERVATION_OR_EVIDENCE',
    'SEQUENTIAL_DR_POLICY_VALUE != GENERAL_LONGITUDINAL_CAUSAL_VALUE_THEOREM',
    'FINITE_SCENARIO_ROBUST_POLICY != GENERAL_ROBUST_CONTROL',
    'QUERY_SET_DECISION_PRESERVATION != GLOBAL_APPROXIMATION_CERTIFICATE',
    'FINITE_TWO_STAGE_SCENARIO_RECOURSE != GENERAL_MULTISTAGE_STOCHASTIC_PROGRAM',
]


def _synthesis(server):
    # Construct the same lazy V5→V14 chain used by the mature dispatcher without
    # importing dispatch here (which would create a package-initialization cycle).
    from .collective_science import CollectiveScienceRuntime
    from .collective_discovery import CollectiveDiscoveryRuntime
    from .collective_dual_control import CollectiveDualControlRuntime
    from .collective_belief import CollectiveBeliefRuntime
    from .collective_inference import CollectiveInferenceRuntime
    from .collective_probabilistic import CollectiveProbabilisticRuntime
    from .collective_adaptive import CollectiveAdaptiveRuntime
    from .collective_joint import CollectiveJointRuntime
    from .collective_robust import CollectiveRobustRuntime
    from .collective_synthesis import CollectiveSynthesisRuntime

    science=CollectiveScienceRuntime(
        server.store,server.collective,server.collective_growth,
        server.collective_memory,server.collective_learning,server.collective_ecology,
    )
    discovery=CollectiveDiscoveryRuntime(science)
    dual=CollectiveDualControlRuntime(discovery)
    belief=CollectiveBeliefRuntime(dual)
    inference=CollectiveInferenceRuntime(belief)
    probabilistic=CollectiveProbabilisticRuntime(inference)
    adaptive=CollectiveAdaptiveRuntime(probabilistic)
    joint=CollectiveJointRuntime(adaptive)
    robust=CollectiveRobustRuntime(joint)
    return CollectiveSynthesisRuntime(robust)


def install_release_v14(namespace: dict[str, Any]) -> None:
    """Install V14 ABI metadata/resource surfaces without rewriting v3.2 registrations.

    Package initialization already uses additive installers for frontier,
    rehydration, Message Board and related organs. V14 follows the same pattern:
    the historical v3.2 registration body remains replayable, while this installer
    advances only current release identity and the lazy Collective frontier.
    """
    if namespace.get('_ATHENA_COLLECTIVE_V14_INSTALLED'):
        return

    protocol=namespace['_protocol']
    namespace['__version__']=V14_PACKAGE_VERSION
    server_info={
        'name':'athena-canonical-mcp',
        'version':V14_PACKAGE_VERSION,
        'description':'Canonical KC144/JSPACE/SCALE developmental control with joint posterior scientific control, sequential doubly robust policy value, decision-relative model resolution, and finite two-stage recourse',
    }
    namespace['SERVER_INFO']=server_info
    protocol.SERVER_INFO=dict(server_info)

    from . import unified_manifest_protocol as ump
    if V14_RESOURCE['uri'] not in {r['uri'] for r in ump.UNIFIED_MANIFEST_RESOURCES}:
        ump.UNIFIED_MANIFEST_RESOURCES.append(dict(V14_RESOURCE))
        ump.UNIFIED_MANIFEST_RESOURCE_URIS.add(V14_RESOURCE['uri'])

    from . import unified_manifest as um
    if not getattr(um,'_athena_collective_v14_installed',False):
        original_build=um.build_unified_manifest
        original_maxdev=um.maxdev_law
        um.UNIFIED_MANIFEST_VERSION=V14_MANIFEST

        def build_unified_manifest_v14(server):
            payload=original_build(server)
            payload['artifact']=V14_MANIFEST
            compat=list(payload.get('artifact_compat') or [])
            if 'ATHENA.RUNTIME.UNIFIED.9' not in compat:
                compat.append('ATHENA.RUNTIME.UNIFIED.9')
            payload['artifact_compat']=compat
            layers=list(payload.get('layers') or [])
            if V14_LAYER not in layers:
                insert_at=layers.index('GITHUB_PROMOTION_VERIFIER.1') if 'GITHUB_PROMOTION_VERIFIER.1' in layers else len(layers)
                layers.insert(insert_at,V14_LAYER)
            payload['layers']=layers
            organs=dict(payload.get('organs') or {})
            organs['collective_v14']=_synthesis(server).describe()
            payload['organs']=organs

            cycle=str(payload.get('cycle',''))
            cycle=cycle.replace('COLLECTIVE(V1-V13)','COLLECTIVE(V1-V14)')
            cycle=cycle.replace('Collective(V1-V13)','Collective(V1-V14)')
            payload['cycle']=cycle

            navigation=str(payload.get('navigation',''))
            navigation=navigation.replace(
                'COLLECTIVE_ROBUST_V13 <-> PROMOTION_TRUST_V2',
                'COLLECTIVE_ROBUST_V13 <-> COLLECTIVE_SYNTHESIS_V14 <-> PROMOTION_TRUST_V2',
            )
            navigation=navigation.replace(
                'COLLECTIVE_ROBUST_V13 <-> Git/MCP',
                'COLLECTIVE_ROBUST_V13 <-> COLLECTIVE_SYNTHESIS_V14 <-> Git/MCP',
            )
            # UNIFIED.9 uses a compact aggregate chart rather than the older
            # explicit successor ladder. Advance that chart as a distinct
            # coordinate transform instead of assuming the older string form.
            navigation=navigation.replace(
                'Collective(V1-V13) <-> Git/MCP',
                'Collective(V1-V14) <-> COLLECTIVE_SYNTHESIS_V14 <-> Git/MCP',
            )
            navigation=navigation.replace('Collective(V1-V13)','Collective(V1-V14)')
            if V14_LAYER not in navigation:
                navigation=f'{navigation} <-> {V14_LAYER}' if navigation else V14_LAYER
            payload['navigation']=navigation

            invariants=list(payload.get('invariants') or [])
            for law in V14_LAWS:
                if law not in invariants:
                    invariants.append(law)
            payload['invariants']=invariants
            payload['collective_synthesis']={
                'version':'COLLECTIVE_RUNTIME_V14',
                'coordinate':V14_COORDINATE,
                'authority':'SCIENCE_TWIN_AND_PLAN_ONLY',
                'laws':list(V14_LAWS),
            }
            for unresolved in payload.get('unresolved') or []:
                uid=unresolved.get('id')
                if uid=='GENERAL_BELIEF_CONTROL':
                    unresolved['v14_boundary']='bounded finite joint factor belief + finite-scenario robust policy; general continuous joint belief/control remains unresolved'
                elif uid=='FORMAL_CAUSAL_DISCOVERY':
                    unresolved['v14_boundary']='bootstrap FCI-lite procedural stability; calibrated causal graph posterior/full FCI-RFCI remains unresolved'
                elif uid=='LONGITUDINAL_CAUSAL_POLICY':
                    unresolved['v14_boundary']='two-timepoint sequential AIPW deterministic-policy value without cross-fitting; arbitrary-horizon/general off-policy theory remains unresolved'
                elif uid=='STOCHASTIC_RESOURCE_CONTROL':
                    unresolved['v14_boundary']='finite two-stage scenario recourse with exact small enumeration; general multistage stochastic/DRO control remains unresolved'
            payload['braid_law']=str(payload.get('braid_law','')).replace('V1-V13','V1-V14')
            return payload

        def maxdev_law_v14():
            base=original_maxdev().replace('COLLECTIVE(V1-V13)','COLLECTIVE(V1-V14)').replace('Collective(V1-V13)','Collective(V1-V14)')
            return base + '''\n\nV14 SYNTHESIS LAW:\n- build bounded finite joint science-twin states only from explicit factor axes/compatibility/likelihoods; factor product != universal posterior;\n- bootstrap FCI-lite graphs measure procedural stability, not causal edge probability;\n- value experiments jointly by finite-state decision EVI and entropy reduction while preserving DESIGN_ONLY;\n- two-timepoint sequential AIPW policy value preserves observed A1/L1 histories, declares cross_fitted=false, and remains assumption scoped;\n- robust policy comparison preserves expected utility, lower-tail CVaR, worst case, regret and Pareto alternatives before hidden scalarization;\n- route GP resolution only when FITC preserves the exact current decision on the witnessed action/query set within the declared margin-error rule;\n- finite two-stage resource recourse may be exactly enumerated only below its declared first-stage threshold; larger greedy plans are uncertified;\n- never feed joint beliefs, bootstrap graph frequencies, EVI branches, policy values, approximation routes or recourse plans back as observations, JSPACE edges, Y1 authority or execution history without a separate witnessed transition.\n'''

        um.build_unified_manifest=build_unified_manifest_v14
        um.maxdev_law=maxdev_law_v14
        um._athena_collective_v14_installed=True

    from . import surface_contract as sc
    from .collective_v14_protocol import COLLECTIVE_V14_TOOLS
    v14_names={tool['name'] for tool in COLLECTIVE_V14_TOOLS}
    if 'collective_v13' in sc.REQUIRED_TOOLS:
        sc.REQUIRED_TOOLS['collective_v13']=set(sc.REQUIRED_TOOLS['collective_v13'])-v14_names
    sc.REQUIRED_TOOLS['collective_v14']=set(v14_names)
    sc.REQUIRED_RESOURCES['collective_v14']={V14_RESOURCE['uri']}
    if not getattr(sc,'_athena_collective_v14_installed',False):
        original_contract=sc.contract_manifest
        def contract_manifest_v14():
            payload=original_contract()
            payload['law']=str(payload.get('law','')).replace('Collective V1-V13','Collective V1-V14')
            return payload
        sc.contract_manifest=contract_manifest_v14
        sc._athena_collective_v14_installed=True

    from . import runtime_integrity_surface as ris
    ris.UNIFIED_MANIFEST_VERSION=V14_MANIFEST
    ris.build_unified_manifest=um.build_unified_manifest
    ris.maxdev_law=um.maxdev_law
    if not getattr(ris.RuntimeIntegritySurface,'_athena_collective_v14_installed',False):
        original_read=ris.RuntimeIntegritySurface.read_resource
        def read_resource_v14(self,uri):
            if uri==V14_RESOURCE['uri']:
                from .collective_v6_protocol import CLAIM_NAMESPACE_LAW
                return {
                    'runtime':_synthesis(self.server).describe(),
                    'claim_namespace':CLAIM_NAMESPACE_LAW,
                    'boundary':'V14 joint beliefs, bootstrap structural ensembles, joint EVI, sequential DR policy values, finite-scenario robust policies, approximation routes and two-stage recourse plans are model/science-twin/control state. They do not mutate Y1 authority, canonical JSPACE, GP observations, execution history, or trusted promotion verification by adjacency.',
                }
            return original_read(self,uri)
        ris.RuntimeIntegritySurface.read_resource=read_resource_v14
        ris.RuntimeIntegritySurface._athena_collective_v14_installed=True

    namespace['_ATHENA_COLLECTIVE_V14_INSTALLED']=True
