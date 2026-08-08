from __future__ import annotations

from typing import Any,Dict

from .reconstruction import RECON_VERSION,ReconstructionLedger
from .runtime_schema import CURRENT_DB_SCHEMA_VERSION,SCHEMA_LEDGER_VERSION,SchemaManager
from .state_foundation_protocol import STATE_FOUNDATION_RESOURCES,STATE_FOUNDATION_RESOURCE_URIS,STATE_FOUNDATION_TOOLS,STATE_FOUNDATION_TOOL_NAMES
from .state_projection import OMEGA_VERSION,project_omega

CRITICAL_REQUIRED_TABLES={
    'runtime_schema_meta','schema_migrations','reconstruction_runs',
    'orchestration_runs','retrieval_runs','gap_runs','field_runs','transport_runs',
    'promotion_runs','cycle_runs','cycle_events',
    'hug_implementations','hug_invocations','extraction_runs','extraction_tasks','extraction_results',
}
CRITICAL_REQUIRED_COLUMNS={
    'reconstruction_runs':{'run_id','source_refs_json','expected_refs_json','omega_json','defects_json','reconstruction_digest'},
    'cycle_runs':{'cycle_id','phase','status','state_json','state_digest','last_eid'},
    'orchestration_runs':{'run_id','input_json','output_json','decision_digest','eid'},
    'promotion_runs':{'run_id','git_head','status','input_json','certificate_json','decision_digest','eid'},
    'field_runs':{'run_id','input_json','output_json','field_digest','eid'},
    'transport_runs':{'run_id','transport_kind','source_json','output_json','transport_digest','eid'},
}


class StateFoundationSurface:
    """Schema-version, OMEGA-state and RECONRUN substrate."""

    def __init__(self,server,development):
        self.server=server;self.development=development
        self.CRITICAL_REQUIRED_TABLES=CRITICAL_REQUIRED_TABLES
        self.CRITICAL_REQUIRED_COLUMNS=CRITICAL_REQUIRED_COLUMNS
        self.schema=SchemaManager(server.core)
        self.reconstruction=ReconstructionLedger(server)

    def call_tool(self,name:str,args:Dict[str,Any]):
        if name=='athena_schema_status':return True,self.schema.status()
        if name=='athena_schema_plan':return True,self.schema.plan()
        if name=='athena_schema_migrate':return True,self.schema.migrate(args.get('actor','agent'),CRITICAL_REQUIRED_TABLES,CRITICAL_REQUIRED_COLUMNS)
        if name=='athena_schema_verify':return True,self.schema.verify(CRITICAL_REQUIRED_TABLES,CRITICAL_REQUIRED_COLUMNS)
        if name=='athena_omega_state':return True,project_omega(self.server)
        if name=='athena_reconstruct_state':return True,self.reconstruction.compile(args['task_ref'],args['source_refs'],args.get('expected_refs'),args.get('actor','agent'),args.get('persist',True))
        if name=='athena_reconstruction_get':return True,self.reconstruction.get(args['run_id'])
        if name=='athena_reconstruction_verify':return True,self.reconstruction.verify(args['run_id'])
        if name=='athena_reconstruction_recent':return True,self.reconstruction.recent(args.get('limit',50))
        return False,None

    def read_resource(self,uri:str):
        if uri=='athena://schema':
            return {
                'version':SCHEMA_LEDGER_VERSION,'target_db_schema_version':CURRENT_DB_SCHEMA_VERSION,
                'critical_required_tables':sorted(CRITICAL_REQUIRED_TABLES),
                'critical_required_columns':{k:sorted(v) for k,v in CRITICAL_REQUIRED_COLUMNS.items()},
                'status':self.schema.status(),'plan':self.schema.plan(),
                'verification':self.schema.verify(CRITICAL_REQUIRED_TABLES,CRITICAL_REQUIRED_COLUMNS),
                'law':'migrations are explicit and versioned; v1 inventories existing additive state, v2 repairs the RECONRUN expected-ref column contract; future schema versions block silent downgrade and required-column absence is a hard failure',
            }
        if uri=='athena://state/omega':
            return {'version':OMEGA_VERSION,'projection':project_omega(self.server),'law':'OMEGA is one current accessible runtime-state projection; unavailable external components remain UNKNOWN and the digest covers the observed packet, not unseen world state'}
        if uri=='athena://reconstruction':
            return {'version':RECON_VERSION,'benchmark':self.reconstruction.benchmark(),'recent':self.reconstruction.recent(50),'law':'RECONRUN freezes current OMEGA plus exact consulted and expected source refs; missing expected refs become explicit defects and unlisted sources are never implied searched'}
        raise KeyError(uri)

    def benchmark(self):
        return {'db_schema_version':self.schema.current_version(),'schema_target_version':CURRENT_DB_SCHEMA_VERSION,**self.reconstruction.benchmark()}
