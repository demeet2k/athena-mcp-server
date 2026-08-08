from __future__ import annotations

import json
import time
from typing import Any,Dict,Iterable,Mapping,Optional

from .identity import digest,event_id

SCHEMA_LEDGER_VERSION='ATHENA.SCHEMA.2'
CURRENT_DB_SCHEMA_VERSION=2

SCHEMA_LEDGER_SQL='''
CREATE TABLE IF NOT EXISTS runtime_schema_meta(key TEXT PRIMARY KEY,value_json TEXT NOT NULL,updated_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS schema_migrations(
 migration_id TEXT PRIMARY KEY,from_version INTEGER NOT NULL,to_version INTEGER NOT NULL,name TEXT NOT NULL,status TEXT NOT NULL,
 preflight_json TEXT NOT NULL,postflight_json TEXT NOT NULL,component_versions_json TEXT NOT NULL,migration_digest TEXT NOT NULL,eid TEXT NOT NULL,applied_at REAL NOT NULL);
CREATE UNIQUE INDEX IF NOT EXISTS idx_schema_migrations_to_version ON schema_migrations(to_version);
'''

DEFAULT_COMPONENT_VERSIONS={
 'base_runtime':'2.4+unified','collective_runtime':'V1','collective_growth':'V1','collective_memory':'V2',
 'aor':'AOR.3.1','authority':'Y.1','equivalence':'EQ.1','extraction':'SX.1','retrieval':'RAG.1','hug':'HUG.ABI.1',
 'gap':'GAP.1','field':'FIELD.1','transport':'AORCOLL.TRANSPORT.1','surface':'ATHENA.SURFACE.2','composition':'ATHENA.COMPOSITION.2',
 'promotion':'ATHENA.PROMOTION.1','cycle':'ATHENA.CYCLE.1','state':'ATHENA.OMEGA.1','reconstruction':'ATHENA.RECON.1',
 'self_test':'ATHENA.SELFTEST.1','startup':'ATHENA.STARTUP.1','manifest':'ATHENA.RUNTIME.UNIFIED.1',
}


def _canonical(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'))
def _table_names(store):return [str(r['name']) for r in store.rows("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
def _index_names(store):return [str(r['name']) for r in store.rows("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
def _quote_ident(name):return '"'+str(name).replace('"','""')+'"'
def _columns(store,table):
    try:return [str(r['name']) for r in store.rows(f'PRAGMA table_info({_quote_ident(table)})')]
    except Exception:return []

def _schema_fingerprint(store):
    tables=_table_names(store);indexes=_index_names(store)
    definitions=store.rows("SELECT type,name,tbl_name,sql FROM sqlite_master WHERE type IN ('table','index') AND name NOT LIKE 'sqlite_%' ORDER BY type,name")
    normalized=[{'type':r['type'],'name':r['name'],'table':r['tbl_name'],'sql':r['sql']} for r in definitions]
    columns={table:_columns(store,table) for table in tables}
    return {'tables':tables,'indexes':indexes,'columns':columns,'definition_digest':digest({'definitions':normalized,'columns':columns},64),'table_count':len(tables),'index_count':len(indexes)}


class SchemaManager:
    """Explicit additive migration ledger with table and column verification."""

    def __init__(self,core,component_versions:Optional[Mapping[str,str]]=None):
        self.core=core;self.s=core.s;self.component_versions={**DEFAULT_COMPONENT_VERSIONS,**dict(component_versions or {})}
        with self.s.db:self.s.db.executescript(SCHEMA_LEDGER_SQL)

    def current_version(self):
        row=self.s.one("SELECT value_json FROM runtime_schema_meta WHERE key='db_schema_version'")
        if row:
            try:return int(json.loads(row['value_json']))
            except Exception:pass
        latest=self.s.one('SELECT MAX(to_version) v FROM schema_migrations')
        return int(latest['v'] or 0) if latest else 0

    def status(self):
        current=self.current_version();latest=self.s.one('SELECT * FROM schema_migrations ORDER BY to_version DESC LIMIT 1')
        return {'version':SCHEMA_LEDGER_VERSION,'current_db_schema_version':current,'target_db_schema_version':CURRENT_DB_SCHEMA_VERSION,'up_to_date':current==CURRENT_DB_SCHEMA_VERSION,'latest_migration':dict(latest) if latest else None,'component_versions':dict(self.component_versions),'schema_fingerprint':_schema_fingerprint(self.s)}

    def plan(self):
        current=self.current_version()
        if current>CURRENT_DB_SCHEMA_VERSION:return {'status':'FUTURE_SCHEMA_BLOCKED','current':current,'target':CURRENT_DB_SCHEMA_VERSION,'steps':[],'boundary':'runtime refuses to silently downgrade a database created by a newer schema version'}
        steps=[]
        if current<1:steps.append({'from_version':current,'to_version':1,'name':'inventory_existing_modular_schema','mode':'ADDITIVE_INVENTORY_NO_DESTRUCTIVE_REWRITE'})
        if current<2:steps.append({'from_version':max(current,1),'to_version':2,'name':'freeze_reconstruction_expected_refs','mode':'ADDITIVE_COLUMN_MIGRATION'})
        return {'status':'MIGRATION_REQUIRED' if steps else 'UP_TO_DATE','current':current,'target':CURRENT_DB_SCHEMA_VERSION,'steps':steps}

    def _event(self,payload,actor):
        parent=self.s.head('global');pe=parent['eid'] if parent else None;eid=event_id('SCHEMA_MIGRATION',actor,pe,dict(payload));ed=digest(dict(payload),32)
        self.s.put_event(eid,'SCHEMA_MIGRATION',actor,pe,dict(payload),ed);self.s.set_head('global',None,None,eid,ed);return eid

    def _apply_step_schema(self,step):
        if step['to_version']==1:return {'changed':False,'actions':[]}
        if step['to_version']==2:
            if 'reconstruction_runs' not in _table_names(self.s):raise ValueError('reconstruction_runs table missing before v2 migration')
            cols=set(_columns(self.s,'reconstruction_runs'));actions=[]
            if 'expected_refs_json' not in cols:
                with self.s.db:self.s.db.execute("ALTER TABLE reconstruction_runs ADD COLUMN expected_refs_json TEXT NOT NULL DEFAULT '[]'")
                actions.append('ADD reconstruction_runs.expected_refs_json')
            return {'changed':bool(actions),'actions':actions}
        raise ValueError(f"unsupported migration target {step['to_version']}")

    def migrate(self,actor='agent',required_tables:Optional[Iterable[str]]=None,required_columns:Optional[Mapping[str,Iterable[str]]]=None):
        plan=self.plan()
        if plan['status']=='FUTURE_SCHEMA_BLOCKED':return {**plan,'applied':False}
        if not plan['steps']:return {'status':'UP_TO_DATE','applied':False,'schema':self.status(),'applied_migrations':[]}
        required=sorted({str(x) for x in (required_tables or []) if str(x)});pre_all=_schema_fingerprint(self.s);missing_before=sorted(set(required)-set(pre_all['tables']))
        if missing_before:return {'status':'PREFLIGHT_FAILED','applied':False,'missing_required_tables':missing_before,'preflight':pre_all,'applied_migrations':[]}
        applied=[]
        for step in plan['steps']:
            existing=self.s.one('SELECT * FROM schema_migrations WHERE to_version=?',(step['to_version'],))
            if existing:
                now=time.time()
                with self.s.db:self.s.db.execute('INSERT OR REPLACE INTO runtime_schema_meta VALUES(?,?,?)',('db_schema_version',_canonical(step['to_version']),now))
                applied.append({'status':'RECOVERED_EXISTING_RECEIPT','migration_id':existing['migration_id'],'to_version':step['to_version'],'actions':[]});continue
            pre=_schema_fingerprint(self.s);schema_change=self._apply_step_schema(step);post=_schema_fingerprint(self.s)
            payload={'operation':'APPLY_SCHEMA_MIGRATION','from_version':step['from_version'],'to_version':step['to_version'],'name':step['name'],'mode':step['mode'],'schema_actions':schema_change['actions'],'preflight':pre,'postflight':post,'component_versions':self.component_versions}
            md=digest(payload,64);mid='MIGRUN.'+digest({'migration':md,'to':step['to_version']},24);eid=self._event({**payload,'migration_id':mid,'migration_digest':md},actor);now=time.time()
            with self.s.db:
                self.s.db.execute('INSERT INTO schema_migrations VALUES(?,?,?,?,?,?,?,?,?,?,?)',(mid,step['from_version'],step['to_version'],step['name'],'APPLIED',_canonical(pre),_canonical(post),_canonical(self.component_versions),md,eid,now))
                self.s.db.execute('INSERT OR REPLACE INTO runtime_schema_meta VALUES(?,?,?)',('db_schema_version',_canonical(step['to_version']),now))
                self.s.db.execute('INSERT OR REPLACE INTO runtime_schema_meta VALUES(?,?,?)',('component_versions',_canonical(self.component_versions),now))
            applied.append({'status':'APPLIED','migration_id':mid,'migration_digest':md,'from_version':step['from_version'],'to_version':step['to_version'],'actions':schema_change['actions'],'eid':eid})
        verification=self.verify(required,required_columns)
        return {'status':'APPLIED' if verification['status']=='PASS' else 'APPLIED_WITH_VERIFICATION_FAILURE','applied':True,'from_version':plan['current'],'to_version':self.current_version(),'applied_migrations':applied,'verification':verification,'schema':self.status()}

    def verify(self,required_tables:Optional[Iterable[str]]=None,required_columns:Optional[Mapping[str,Iterable[str]]]=None):
        status=self.status();actual=status['schema_fingerprint'];required=sorted({str(x) for x in (required_tables or []) if str(x)});missing_tables=sorted(set(required)-set(actual['tables']));column_defects=[]
        for table,names in dict(required_columns or {}).items():
            have=set(actual['columns'].get(str(table),[]))
            for name in names:
                if str(name) not in have:column_defects.append({'table':str(table),'column':str(name)})
        latest=status['latest_migration'];recorded=json.loads(latest['postflight_json']) if latest else None
        return {'version':SCHEMA_LEDGER_VERSION,'status':'PASS' if status['up_to_date'] and not missing_tables and not column_defects else 'FAIL','up_to_date':status['up_to_date'],'missing_required_tables':missing_tables,'missing_required_columns':column_defects,'actual':actual,'recorded_postflight':recorded,'definition_changed_since_latest_migration':bool(recorded and recorded.get('definition_digest')!=actual.get('definition_digest')),'boundary':'schema fingerprint drift is observable; additive organ tables created after a receipt may cause benign drift, while required table/column absence is a hard failure'}

    def recent(self,limit=50):
        limit=max(1,min(int(limit),500));return self.s.rows('SELECT migration_id,from_version,to_version,name,status,migration_digest,eid,applied_at FROM schema_migrations ORDER BY applied_at DESC LIMIT ?',(limit,))
