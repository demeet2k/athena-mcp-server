from __future__ import annotations

from typing import Any,Dict

COMPOSITION_VERSION='ATHENA.COMPOSITION.2'
DIRECT_ORGANS=(
    'core','crystal','git','collective','collective_growth','collective_memory','collective_learning','collective_ecology',
    'branches','authority','orchestration','aor_development',
)
DEVELOPMENT_ORGANS=('equivalence','extraction','retrieval','hug','gap','field','transport','integrity','cycle','project_atlas')
GOVERNANCE_ORGANS=('promotion','state_foundation','self_test','startup')


def composition_certificate(server,run_probes=True)->Dict[str,Any]:
    mro=[cls.__name__ for cls in type(server).mro()]
    class_ok=type(server).__name__=='Server' and mro[:2]==['Server','object']
    missing_direct=[name for name in DIRECT_ORGANS if not hasattr(server,name) or getattr(server,name) is None]
    dev=getattr(server,'aor_development',None)
    missing_development=[name for name in DEVELOPMENT_ORGANS if dev is None or not hasattr(dev,name) or getattr(dev,name) is None]
    integrity=getattr(dev,'integrity',None) if dev is not None else None
    governance={name:getattr(integrity,name,None) if integrity is not None else None for name in GOVERNANCE_ORGANS}
    missing_governance=[name for name,value in governance.items() if value is None]
    probes={}
    if run_probes and not missing_direct and not missing_development:
        checks={
            'core':lambda:server.core.benchmark(),'crystal':lambda:server.crystal.benchmark_extension(),
            'collective':lambda:server.collective.describe(),'collective_growth':lambda:server.collective_growth.describe(),'collective_memory':lambda:server.collective_memory.describe(),
            'collective_learning':lambda:server.collective_learning.describe(),'collective_ecology':lambda:server.collective_ecology.describe(),
            'branch':lambda:server.branches.list(limit=1),'authority':lambda:server.authority.list(limit=1),
            'equivalence':lambda:dev.equivalence.benchmark(),'extraction':lambda:dev.extraction.benchmark(),'retrieval':lambda:dev.retrieval.recent(1),
            'hug':lambda:dev.hug.list(limit=1),'gap':lambda:dev.gap.recent(1),'field':lambda:dev.field.recent(1),'transport':lambda:dev.transport.runtime.recent(1),
            'cycle':lambda:dev.cycle.recent(1),'project_atlas':lambda:dev.project_atlas.benchmark(),
            'promotion':(lambda:integrity.promotion.recent(1)) if integrity and integrity.promotion else None,
            'schema':(lambda:integrity.state_foundation.schema.status()) if integrity and integrity.state_foundation else None,
            'reconstruction':(lambda:integrity.state_foundation.reconstruction.recent(1)) if integrity and integrity.state_foundation else None,
            'self_test':(lambda:integrity.self_test.describe()) if integrity and integrity.self_test else None,
            'startup':(lambda:{'version':'ATHENA.STARTUP.1'}) if integrity and integrity.startup else None,
        }
        for name,fn in checks.items():
            if fn is None:probes[name]={'status':'FAIL','error':'organ missing'};continue
            try:fn();probes[name]={'status':'PASS'}
            except Exception as exc:probes[name]={'status':'FAIL','error':f'{type(exc).__name__}: {exc}'}
    probe_status='PASS' if (not run_probes or probes and all(p['status']=='PASS' for p in probes.values())) else ('SKIPPED' if not run_probes else 'FAIL')
    ok=class_ok and not missing_direct and not missing_development and not missing_governance and (not run_probes or probe_status=='PASS')
    return {
        'version':COMPOSITION_VERSION,'status':'PASS' if ok else 'FAIL',
        'runtime_class':{'status':'PASS' if class_ok else 'FAIL','expected':'Server -> object','observed_mro':mro,'single_composed_runtime':class_ok},
        'direct_organs':{'status':'PASS' if not missing_direct else 'FAIL','required':list(DIRECT_ORGANS),'missing':missing_direct},
        'development_organs':{'status':'PASS' if not missing_development else 'FAIL','required':list(DEVELOPMENT_ORGANS),'missing':missing_development},
        'governance_organs':{'status':'PASS' if not missing_governance else 'FAIL','required':list(GOVERNANCE_ORGANS),'missing':missing_governance},
        'read_only_probes':probes,'probe_status':probe_status,
        'law':'composition integrity requires one Server with resident Collective V1-V4 + AOR/FIELD/transport/CYCLE/state-foundation/startup/self-test/promotion + read-only Project Atlas query organs; V5-V13 science/inference/control/adaptation/joint/robust surfaces are lazily constructed but their advertised surfaces are required by SURFACE.2',
        'boundary':'certifies runtime wiring/dispatch reachability and organ presence; Project Atlas navigation is read-only and not semantic equivalence; model validity, migration currency, trusted external promotion verification, external CI/smoke and semantic truth are separate gates',
    }
