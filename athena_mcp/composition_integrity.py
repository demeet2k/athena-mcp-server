from __future__ import annotations

from typing import Any,Dict

COMPOSITION_VERSION='ATHENA.COMPOSITION.2'

DIRECT_ORGANS=('core','crystal','git','collective','collective_growth','collective_memory','branches','authority','orchestration','aor_development')
DEVELOPMENT_ORGANS=('equivalence','extraction','retrieval','hug','gap','field','transport')


def composition_certificate(server,run_probes=True)->Dict[str,Any]:
    mro=[cls.__name__ for cls in type(server).mro()]
    class_ok=type(server).__name__=='Server' and mro[:2]==['Server','object']
    missing_direct=[name for name in DIRECT_ORGANS if not hasattr(server,name) or getattr(server,name) is None]
    dev=getattr(server,'aor_development',None)
    missing_development=[name for name in DEVELOPMENT_ORGANS if dev is None or not hasattr(dev,name) or getattr(dev,name) is None]
    integrity=getattr(dev,'integrity',None) if dev is not None else None
    promotion=getattr(integrity,'promotion',None) if integrity is not None else None
    missing_governance=[] if promotion is not None else ['promotion']
    probes={}
    if run_probes and not missing_direct and not missing_development:
        checks={
            'core':lambda:server.core.benchmark(),
            'crystal':lambda:server.crystal.benchmark_extension(),
            'collective':lambda:server.collective.describe(),
            'collective_growth':lambda:server.collective_growth.describe(),
            'collective_memory':lambda:server.collective_memory.describe(),
            'branch':lambda:server.branches.list(limit=1),
            'authority':lambda:server.authority.list(limit=1),
            'equivalence':lambda:dev.equivalence.benchmark(),
            'extraction':lambda:dev.extraction.benchmark(),
            'retrieval':lambda:dev.retrieval.recent(1),
            'hug':lambda:dev.hug.list(limit=1),
            'gap':lambda:dev.gap.recent(1),
            'field':lambda:dev.field.recent(1),
            'transport':lambda:dev.transport.runtime.recent(1),
            'promotion':(lambda:promotion.recent(1)) if promotion is not None else None,
        }
        for name,fn in checks.items():
            if fn is None:
                probes[name]={'status':'FAIL','error':'organ missing'};continue
            try:
                fn();probes[name]={'status':'PASS'}
            except Exception as exc:probes[name]={'status':'FAIL','error':f'{type(exc).__name__}: {exc}'}
    probe_status='PASS' if (not run_probes or probes and all(p['status']=='PASS' for p in probes.values())) else ('SKIPPED' if not run_probes else 'FAIL')
    ok=class_ok and not missing_direct and not missing_development and not missing_governance and (not run_probes or probe_status=='PASS')
    return {
        'version':COMPOSITION_VERSION,'status':'PASS' if ok else 'FAIL',
        'runtime_class':{'status':'PASS' if class_ok else 'FAIL','expected':'Server -> object','observed_mro':mro,'single_composed_runtime':class_ok},
        'direct_organs':{'status':'PASS' if not missing_direct else 'FAIL','required':list(DIRECT_ORGANS),'missing':missing_direct},
        'development_organs':{'status':'PASS' if not missing_development else 'FAIL','required':list(DEVELOPMENT_ORGANS),'missing':missing_development},
        'governance_organs':{'status':'PASS' if not missing_governance else 'FAIL','required':['promotion'],'missing':missing_governance},
        'read_only_probes':probes,'probe_status':probe_status,
        'law':'composition integrity requires one promoted Server, initialized mature base/Collective/AOR/transport/governance organs, and successful representative read-only execution paths',
        'boundary':'this certifies runtime wiring/dispatch reachability and organ presence, not semantic truth of every organ output',
    }
