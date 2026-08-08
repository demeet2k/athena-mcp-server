from __future__ import annotations

from typing import Any,Dict

from .reconstruction import RECON_VERSION,ReconstructionLedger
from .runtime_schema import CURRENT_DB_SCHEMA_VERSION,SCHEMA_LEDGER_VERSION,SchemaManager
from .state_foundation_protocol import STATE_FOUNDATION_RESOURCES,STATE_FOUNDATION_RESOURCE_URIS,STATE_FOUNDATION_TOOLS,STATE_FOUNDATION_TOOL_NAMES
from .state_projection import OMEGA_VERSION,project_omega

# Critical tables required for the unified runtime to claim that all currently
# promoted metabolisms have durable state. This is intentionally a minimum
# integrity set, not an assertion that every table in SQLite is enumerated here.
CRITICAL_REQUIRED_TABLES={
    'runtime_schema_meta','schema_migrations','reconstruction_runs',
    'orchestration_runs','retrieval_runs','gap_runs','field_runs','transport_runs',
    'promotion_runs','cycle_runs','cycle_events',
    'hug_implementations','hug_invocations','extraction_runs','extraction_tasks','extraction_results',
}

class StateFoundationSurface:
    """Schema-version, Ω-state and RECONRUN substrate.

    Migration and reconstruction are deliberately separate: schema migration
    changes/records storage compatibility, while RECONRUN freezes an observation
    of current state and source coverage. Neither operation implies semantic
    proof or external-source completeness.
    """
    def __init__(self,server,development):
        self.server=server;self.development=development
        self.schema=SchemaManager(server.core)
        self.reconstruction=ReconstructionLedger(server)

    def call_tool(self,name:str,args:Dict[str,Any]):
        if name=='athena_schema_status':return True,self.schema.status()
        if name=='athena_schema_plan':return True,self.schema.plan()
        if name=='athena_schema_migrate':return True,self.schema.migrate(args.get('actor','agent'),CRITICAL_REQUIRED_TABLES)
        if name=='athena_schema_verify':return True,self.schema.verify(CRITICAL_REQUIRED_TABLES)
        if name=='athena_omega_state':return True,project_omega(self.server)
        if name=='athena_reconstruct_state':return True,self.reconstruction.compile(args['task_ref'],args['source_refs'],args.get('expected_refs'),args.get('actor','agent'),args.get('persist',True))
        if name=='athena_reconstruction_get':return True,self.reconstruction.get(args['run_id'])
        if name=='athena_reconstruction_verify':return True,self.reconstruction.verify(args['run_id'])
        if name=='athena_reconstruction_recent':return True,self.reconstruction.recent(args.get('limit',50))
        return False,None

    def read_resource(self,uri:str):
        if uri=='athena://schema':
            return {
                'version':SCHEMA_LEDGER_VERSION,
                'target_db_schema_version':CURRENT_DB_SCHEMA_VERSION,
                'critical_required_tables':sorted(CRITICAL_REQUIRED_TABLES),
                'status':self.schema.status(),
                'plan':self.schema.plan(),
                'verification':self.schema.verify(CRITICAL_REQUIRED_TABLES),
                'law':'migration steps are explicit and versioned; v1 inventories the already-created additive organism instead of destructively rewriting organ tables; future schema versions block silent downgrade',
            }
        if uri=='athena://state/omega':
            return {
                'version':OMEGA_VERSION,
                'projection':project_omega(self.server),
                'law':'Ω is one current accessible runtime-state projection; unavailable external components remain UNKNOWN and the digest covers the observed packet, not unseen world state',
            }
        if uri=='athena://reconstruction':
            return {
                'version':RECON_VERSION,
                'benchmark':self.reconstruction.benchmark(),
                'recent':self.reconstruction.recent(50),
                'law':'RECONRUN freezes current Ω plus exact consulted and expected source refs; missing expected refs become explicit defects and unlisted sources are never implied searched',
            }
        raise KeyError(uri)

    def benchmark(self):
        return {
            'db_schema_version':self.schema.current_version(),
            'schema_target_version':CURRENT_DB_SCHEMA_VERSION,
            **self.reconstruction.benchmark(),
        }
