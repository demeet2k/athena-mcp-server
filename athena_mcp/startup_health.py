from __future__ import annotations

from typing import Any, Dict

STARTUP_HEALTH_VERSION='ATHENA.STARTUP.1'


class StartupHealth:
    """Read-only startup/readiness classifier.

    The runtime remains inspectable while degraded. This object does not itself
    block writes; it provides the typed state later mutation policies may gate
    against. That separation avoids silently changing legacy write semantics.
    """
    def __init__(self,server,integrity):self.server=server;self.integrity=integrity

    def evaluate(self,run_replay_samples=False)->Dict[str,Any]:
        surface=self.integrity.surface_audit(True)
        foundation=self.integrity.state_foundation
        schema=foundation.schema.verify(
            __import__('athena_mcp.state_foundation_surface',fromlist=['CRITICAL_REQUIRED_TABLES']).CRITICAL_REQUIRED_TABLES,
            __import__('athena_mcp.state_foundation_surface',fromlist=['CRITICAL_REQUIRED_COLUMNS']).CRITICAL_REQUIRED_COLUMNS,
        )
        gates={'surface':surface['surface_status'],'composition':surface['composition']['status'],'schema':schema['status']}
        selftest=None
        if run_replay_samples or all(v=='PASS' for v in gates.values()):
            selftest=self.integrity.self_test.run(10,True);gates['self_test']=selftest['status']
        if surface['surface_status']!='PASS':status='DEGRADED_SURFACE'
        elif surface['composition']['status']!='PASS':status='DEGRADED_COMPOSITION'
        elif schema['status']!='PASS':status='DEGRADED_SCHEMA'
        elif selftest is not None and selftest['status']!='PASS':status='DEGRADED_SELFTEST'
        else:status='READY_LOCAL'
        return {
            'version':STARTUP_HEALTH_VERSION,'status':status,'gates':gates,
            'read_policy':'READS_ALLOWED_WHILE_DEGRADED',
            'write_policy':'NOT_ENFORCED_BY_STARTUP1; mutation gating requires explicit per-tool policy and tests',
            'promotion_policy':'PROMOTION_REQUIRES_READY_LOCAL_PLUS_EXACT_HEAD_EXTERNAL_CI_SMOKE_ATTESTATIONS',
            'surface':{'status':surface['status'],'surface_status':surface['surface_status'],'composition_status':surface['composition']['status']},
            'schema':schema,'self_test':selftest,
            'boundary':'READY_LOCAL is local substrate health, not external CI/smoke qualification and not semantic proof of unresolved algorithms.',
        }
