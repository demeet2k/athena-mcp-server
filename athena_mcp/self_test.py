from __future__ import annotations

from typing import Any,Callable,Dict

from .state_foundation_surface import CRITICAL_REQUIRED_COLUMNS,CRITICAL_REQUIRED_TABLES

SELF_TEST_VERSION='ATHENA.SELFTEST.1'


class SelfTestRuntime:
    """Read-only health synthesis across the unified organism."""

    def __init__(self,server,integrity):self.server=server;self.integrity=integrity
    def describe(self):return {'version':SELF_TEST_VERSION,'mode':'READ_ONLY','mutates':False}

    def _sample(self,label,rows,replay:Callable[[str],Dict[str,Any]],id_key,limit=10):
        rows=list(rows or [])[:limit]
        if not rows:return {'status':'N/A','checked':0,'matches':0,'failures':[],'reason':'no persisted runs available'}
        failures=[];matches=0
        for row in rows:
            run_id=row[id_key]
            try:
                result=replay(run_id);ok=bool(result.get('match'))
                if ok:matches+=1
                else:failures.append({'id':run_id,'result':result})
            except Exception as exc:failures.append({'id':run_id,'error':f'{type(exc).__name__}: {exc}'})
        return {'status':'PASS' if not failures else 'FAIL','checked':len(rows),'matches':matches,'failures':failures}

    def run(self,replay_limit=10,run_composition_probes=True):
        dev=self.integrity.development
        surface=self.integrity.surface_audit(run_composition_probes)
        schema=self.integrity.state_foundation.schema.verify(CRITICAL_REQUIRED_TABLES,CRITICAL_REQUIRED_COLUMNS)
        omega=self.integrity.state_foundation.call_tool('athena_omega_state',{})[1]
        samples={
            'aor':self._sample('aor',self.server.orchestration.recent(replay_limit),self.server.orchestration.replay,'run_id',replay_limit),
            'retrieval':self._sample('retrieval',dev.retrieval.recent(replay_limit),dev.retrieval.replay,'run_id',replay_limit),
            'gap':self._sample('gap',dev.gap.recent(replay_limit),dev.gap.replay,'run_id',replay_limit),
            'field':self._sample('field',dev.field.recent(replay_limit),dev.field.replay,'run_id',replay_limit),
            'transport':self._sample('transport',dev.transport.runtime.recent(replay_limit),dev.transport.runtime.replay,'run_id',replay_limit),
            'promotion':self._sample('promotion',self.integrity.promotion.recent(replay_limit),self.integrity.promotion.replay,'run_id',replay_limit),
            'cycle':self._sample('cycle',dev.cycle.recent(replay_limit),dev.cycle.replay,'cycle_id',replay_limit),
            'reconstruction':self._sample('reconstruction',self.integrity.state_foundation.reconstruction.recent(replay_limit),self.integrity.state_foundation.reconstruction.verify,'run_id',replay_limit),
        }
        replay_failures=[name for name,value in samples.items() if value['status']=='FAIL']
        gates={
            'surface':surface['status'],'composition':surface['composition']['status'],'schema':schema['status'],
            'omega':'PASS' if omega.get('state_digest') and omega.get('omega_id') else 'FAIL',
            'replay':'PASS' if not replay_failures else 'FAIL',
        }
        overall='PASS' if all(value=='PASS' for value in gates.values()) else 'DEGRADED'
        return {
            'version':SELF_TEST_VERSION,'status':overall,'gates':gates,'surface':surface,'schema':schema,
            'omega':{'omega_id':omega.get('omega_id'),'state_digest':omega.get('state_digest'),'boundary':omega.get('boundary')},
            'replay_samples':samples,'replay_failures':replay_failures,
            'promotion_eligibility':'LOCAL_GATES_READY_EXTERNAL_ATTESTATIONS_STILL_REQUIRED' if overall=='PASS' else 'BLOCKED_BY_LOCAL_HEALTH',
            'boundary':'SELFTEST is read-only health synthesis. PASS does not replace external CI/smoke attestations or prove semantic truth of unresolved algorithms such as QHUG.',
        }
