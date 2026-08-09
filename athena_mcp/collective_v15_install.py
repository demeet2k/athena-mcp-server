from __future__ import annotations

from typing import Any

V15_RESOURCE={
    'uri':'athena://collective/v15',
    'name':'Collective Calibrated Continuous Scientific-Control Runtime V15',
    'mimeType':'application/json',
}
V15_LAYER='COLLECTIVE_CALIBRATED_V15'
V15_MANIFEST='ATHENA.RUNTIME.UNIFIED.11'
V15_PACKAGE_VERSION='3.4.0'
V15_COORDINATE='COLLECTIVE_CALIBRATED=<SR,XT,XD,CJ,AT,MD,L>'
V15_LAWS=[
    'OUT_OF_FOLD_ISOTONIC_RELIABILITY != CAUSAL_GRAPH_POSTERIOR',
    'CROSS_FITTED_TWO_TIMEPOINT_TMLE != GENERAL_LONGITUDINAL_TMLE_THEOREM',
    'CROSS_FITTED_SEQUENTIAL_DR != GENERAL_OFF_POLICY_CAUSAL_VALUE',
    'LINEAR_GAUSSIAN_UPDATE != GENERAL_CONTINUOUS_JOINT_BAYES',
    'GAUSSIAN_LINEAR_CONTROL != GENERAL_BELIEF_MDP',
    'DECLARED_LIPSCHITZ_ERROR_ENVELOPE != EMPIRICAL_GLOBAL_ERROR_TRUTH',
    'RECTANGULAR_TV_ROBUST_MDP != GENERAL_MULTISTAGE_DRO',
    'IDENTICAL_CALIBRATION_COORDINATE != MULTIPLE_FITTED_VALUES',
    'DECISION_TIME_HISTORY != FULL_ROW_STATE',
    'UNKNOWN_COEFFICIENT != ZERO_COEFFICIENT',
    'NONFINITE_NUMERIC_STATE != MODEL_COORDINATE',
    'GEOMETRIC_NEAREST_WITNESS != TIGHTEST_ERROR_ENVELOPE_WITNESS',
    'GLOBAL_ENVELOPE != RADIUS_ELIGIBLE_LOCAL_CERTIFICATE',
    'UNKNOWN_STATE_COORDINATE != UNUSED_METADATA',
    'NONFINITE_TRANSITION != PROBABILITY_MODEL',
    'STAGE2_PSEUDO_OUTCOME_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_INTERVENTION',
    'ZERO_TEST_SELECTION != PROOF',
]


def _calibrated(server):
    from .collective_v14_install import _synthesis
    from .collective_calibrated import CollectiveCalibratedRuntime
    return CollectiveCalibratedRuntime(_synthesis(server))


def install_release_v15(namespace: dict[str, Any]) -> None:
    if namespace.get('_ATHENA_COLLECTIVE_V15_INSTALLED'):
        return

    protocol=namespace['_protocol']
    namespace['__version__']=V15_PACKAGE_VERSION
    server_info={
        'name':'athena-canonical-mcp',
        'version':V15_PACKAGE_VERSION,
        'description':'Canonical KC144/JSPACE/SCALE developmental control with calibrated structural reliability, history-safe cross-fitted longitudinal causal estimation, strict continuous Gaussian joint belief, approximation-error transport, and bounded multistage robust control',
    }
    namespace['SERVER_INFO']=server_info
    protocol.SERVER_INFO=dict(server_info)

    # DEPLOYMENT.2 imports dispatch after V14 and before this installer. dispatch
    # binds SERVER_INFO by value at import time, so advancing protocol.SERVER_INFO
    # alone leaves initialize/HTTP on the V14 identity. Advance the live dispatch
    # chart explicitly; this is release identity synchronization, not a second ABI.
    from . import dispatch as dispatch_module
    dispatch_module.SERVER_INFO=dict(server_info)

    from . import unified_manifest_protocol as ump
    if V15_RESOURCE['uri'] not in {r['uri'] for r in ump.UNIFIED_MANIFEST_RESOURCES}:
        ump.UNIFIED_MANIFEST_RESOURCES.append(dict(V15_RESOURCE))
        ump.UNIFIED_MANIFEST_RESOURCE_URIS.add(V15_RESOURCE['uri'])

    from . import unified_manifest as um
    if not getattr(um,'_athena_collective_v15_installed',False):
        original_build=um.build_unified_manifest
        original_maxdev=um.maxdev_law
        um.UNIFIED_MANIFEST_VERSION=V15_MANIFEST

        def build_unified_manifest_v15(server):
            payload=original_build(server)
            payload['artifact']=V15_MANIFEST
            compat=list(payload.get('artifact_compat') or [])
            if 'ATHENA.RUNTIME.UNIFIED.10' not in compat:
                compat.append('ATHENA.RUNTIME.UNIFIED.10')
            payload['artifact_compat']=compat
            layers=list(payload.get('layers') or [])
            if V15_LAYER not in layers:
                insert_at=layers.index('GITHUB_PROMOTION_VERIFIER.1') if 'GITHUB_PROMOTION_VERIFIER.1' in layers else len(layers)
                layers.insert(insert_at,V15_LAYER)
            payload['layers']=layers
            organs=dict(payload.get('organs') or {})
            organ=_calibrated(server).describe()
            organ['audit_laws']=[law for law in V15_LAWS if law not in organ.get('laws',[])]
            organ['history_membrane']={
                'a1':'baseline only',
                'a2':'baseline + A1 + L1 only',
                'forbidden_future':['A2','Y'],
            }
            organ['numerical_membrane']='unknown coordinates and non-finite numeric state fail closed'
            organs['collective_v15']=organ
            payload['organs']=organs
            cycle=str(payload.get('cycle','')).replace('COLLECTIVE(V1-V14)','COLLECTIVE(V1-V15)').replace('Collective(V1-V14)','Collective(V1-V15)')
            payload['cycle']=cycle
            navigation=str(payload.get('navigation',''))
            navigation=navigation.replace('COLLECTIVE_SYNTHESIS_V14 <-> PROMOTION_TRUST_V2','COLLECTIVE_SYNTHESIS_V14 <-> COLLECTIVE_CALIBRATED_V15 <-> PROMOTION_TRUST_V2')
            navigation=navigation.replace('COLLECTIVE_SYNTHESIS_V14 <-> Git/MCP','COLLECTIVE_SYNTHESIS_V14 <-> COLLECTIVE_CALIBRATED_V15 <-> Git/MCP')
            navigation=navigation.replace('Collective(V1-V14) <-> COLLECTIVE_SYNTHESIS_V14 <-> Git/MCP','Collective(V1-V15) <-> COLLECTIVE_SYNTHESIS_V14 <-> COLLECTIVE_CALIBRATED_V15 <-> Git/MCP')
            navigation=navigation.replace('Collective(V1-V14)','Collective(V1-V15)')
            if V15_LAYER not in navigation:
                navigation=f'{navigation} <-> {V15_LAYER}' if navigation else V15_LAYER
            payload['navigation']=navigation
            invariants=list(payload.get('invariants') or [])
            for law in V15_LAWS:
                if law not in invariants:invariants.append(law)
            payload['invariants']=invariants
            payload['collective_calibrated']={
                'version':'COLLECTIVE_RUNTIME_V15',
                'coordinate':V15_COORDINATE,
                'authority':'CALIBRATION_SCIENCE_TWIN_AND_PLAN_ONLY',
                'laws':list(V15_LAWS),
                'decision_time_history':{'A1':'baseline','A2':'baseline+A1+L1'},
                'error_transport_coordinates':['geometric_nearest','global_envelope','radius_eligible_local_certificate'],
                'numeric_policy':'reject unknown or non-finite model coordinates',
            }
            for unresolved in payload.get('unresolved') or []:
                uid=unresolved.get('id')
                if uid=='GENERAL_BELIEF_CONTROL':unresolved['v15_boundary']='exact finite-dimensional linear-Gaussian belief update plus linear-Gaussian action control with strict declared-coordinate validation; non-Gaussian/general continuous belief-MDP remains unresolved'
                elif uid=='FORMAL_CAUSAL_DISCOVERY':unresolved['v15_boundary']='weighted out-of-fold isotonic reliability calibration from externally labelled structural examples with duplicate-support pooling; calibrated causal graph posterior/full FCI-RFCI remains unresolved'
                elif uid=='LONGITUDINAL_CAUSAL_POLICY':unresolved['v15_boundary']='history-safe cross-fitted bounded two-timepoint sequential logistic TMLE and sequential AIPW dynamic-policy value; arbitrary-horizon/general longitudinal theory remains unresolved'
                elif uid=='STOCHASTIC_RESOURCE_CONTROL':unresolved['v15_boundary']='finite-horizon rectangular total-variation robust dynamic program with strict finite state/action/transition coordinates; non-rectangular/general multistage stochastic-DRO control remains unresolved'
            payload['braid_law']=str(payload.get('braid_law','')).replace('V1-V14','V1-V15')
            return payload

        def maxdev_law_v15():
            base=original_maxdev().replace('COLLECTIVE(V1-V14)','COLLECTIVE(V1-V15)').replace('Collective(V1-V14)','Collective(V1-V15)')
            return base + '''\n\nV15 CALIBRATION LAW:\n- pool identical structural-support coordinates before weighted PAV; one semantic calibration coordinate cannot carry order-dependent duplicate fitted values;\n- calibrate structural bootstrap support only against externally labelled correctness with out-of-fold reliability; calibrated reliability != causal graph posterior;\n- cross-fit two-timepoint sequential TMLE/AIPW nuisance and evaluation folds while preserving explicit causal assumptions and observed history ordering; stage-1 policies may use baseline only and stage-2 policies may use baseline+A1+L1 only;\n- reject unknown Gaussian/state/action coordinates and non-finite model numbers instead of silently mapping them to zero or valid state;\n- use exact multivariate-Gaussian conditioning only for declared linear-Gaussian observation models; Gaussian joint belief != general continuous Bayes;\n- rank linear actions under Gaussian moments/CVaR as PLAN_ONLY; action value != execution authority;\n- keep geometric nearest witness, tightest global error envelope, and radius-eligible local transport certificate distinct;\n- transport approximation error only through a declared Lipschitz envelope that is consistent with supplied witnesses; transport certificate remains assumption/domain scoped;\n- solve finite-horizon robust dynamic programs exactly only under supplied state-action rectangular total-variation ambiguity with finite complete coordinate validation; rectangular TV-DRO != general multistage DRO;\n- zero selected tests are not proof even when a test command exits successfully;\n- never promote calibration curves, cross-fitted estimates, Gaussian posterior state, transported error bounds, or robust policies into observation/Y1/JSPACE/execution/trust state without a separately witnessed transition.\n'''
        um.build_unified_manifest=build_unified_manifest_v15
        um.maxdev_law=maxdev_law_v15
        um._athena_collective_v15_installed=True

    # dispatch imported these callables by value before the V15 overlay existed.
    # Synchronize both manifest entry points so athena://manifest, the runtime
    # manifest tool/resource, and the fallback MAXDEV prompt share one chart.
    dispatch_module.build_unified_manifest=um.build_unified_manifest
    dispatch_module.maxdev_law=um.maxdev_law

    from . import surface_contract as sc
    from .collective_v15_protocol import COLLECTIVE_V15_TOOLS
    v15_names={tool['name'] for tool in COLLECTIVE_V15_TOOLS}
    if 'collective_v14' in sc.REQUIRED_TOOLS:sc.REQUIRED_TOOLS['collective_v14']=set(sc.REQUIRED_TOOLS['collective_v14'])-v15_names
    sc.REQUIRED_TOOLS['collective_v15']=set(v15_names)
    sc.REQUIRED_RESOURCES['collective_v15']={V15_RESOURCE['uri']}
    if not getattr(sc,'_athena_collective_v15_installed',False):
        original_contract=sc.contract_manifest
        def contract_manifest_v15():
            payload=original_contract();payload['law']=str(payload.get('law','')).replace('Collective V1-V14','Collective V1-V15');return payload
        sc.contract_manifest=contract_manifest_v15
        sc._athena_collective_v15_installed=True

    from . import runtime_integrity_surface as ris
    ris.UNIFIED_MANIFEST_VERSION=V15_MANIFEST
    ris.build_unified_manifest=um.build_unified_manifest
    ris.maxdev_law=um.maxdev_law
    # RuntimeIntegritySurface snapshots UNIFIED_MANIFEST_RESOURCES at module import,
    # so advancing the protocol list alone is insufficient. Advance the live
    # composed resource registry as the same versioned chart transition.
    if V15_RESOURCE['uri'] not in ris.INTEGRITY_RESOURCE_URIS:
        ris.INTEGRITY_RESOURCES.append(dict(V15_RESOURCE))
        ris.INTEGRITY_RESOURCE_URIS.add(V15_RESOURCE['uri'])

    # AorDevelopmentSurface snapshots INTEGRITY_RESOURCES a second time while
    # dispatch is imported by DEPLOYMENT.2. Synchronize that second-order chart
    # as well; resources/list and resources/read depend on these exact objects.
    from . import aor_development_surface as ads
    if V15_RESOURCE['uri'] not in ads.AOR_DEVELOPMENT_RESOURCE_URIS:
        ads.AOR_DEVELOPMENT_RESOURCES.append(dict(V15_RESOURCE))
        ads.AOR_DEVELOPMENT_RESOURCE_URIS.add(V15_RESOURCE['uri'])

    if not getattr(ris.RuntimeIntegritySurface,'_athena_collective_v15_installed',False):
        original_read=ris.RuntimeIntegritySurface.read_resource
        def read_resource_v15(self,uri):
            if uri==V15_RESOURCE['uri']:
                from .collective_v6_protocol import CLAIM_NAMESPACE_LAW
                runtime=_calibrated(self.server).describe()
                runtime['audit_laws']=[law for law in V15_LAWS if law not in runtime.get('laws',[])]
                return {
                    'runtime':runtime,
                    'claim_namespace':CLAIM_NAMESPACE_LAW,
                    'decision_time_history':{'A1':'baseline only','A2':'baseline + A1 + L1 only'},
                    'error_transport_coordinates':['geometric_nearest','global_envelope','radius_eligible_local_certificate'],
                    'numeric_policy':'unknown coordinates and non-finite model numbers fail closed',
                    'boundary':'V15 reliability calibration, history-safe cross-fitted longitudinal estimates, strict Gaussian joint beliefs/actions, approximation-error transport and rectangular-TV robust plans are calibration/model/science/control state. They do not mutate Y1 authority, canonical JSPACE, empirical observations, execution history, or trusted promotion state by adjacency.'
                }
            return original_read(self,uri)
        ris.RuntimeIntegritySurface.read_resource=read_resource_v15
        ris.RuntimeIntegritySurface._athena_collective_v15_installed=True

    namespace['_ATHENA_COLLECTIVE_V15_INSTALLED']=True
