from __future__ import annotations
import json, time
from .identity import event_id, digest
from .polycoord import CHARTS

EXTENSION_SCHEMA='''
CREATE TABLE IF NOT EXISTS hyperedges(hyperedge_id TEXT PRIMARY KEY,relation TEXT NOT NULL,members_json TEXT NOT NULL,eid TEXT NOT NULL,attrs_json TEXT NOT NULL,created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS math_objects(math_id TEXT PRIMARY KEY,owner_id TEXT NOT NULL,kind TEXT NOT NULL,symbol TEXT,latex TEXT NOT NULL,assumptions_json TEXT NOT NULL,status TEXT NOT NULL,eid TEXT NOT NULL,created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS coordinate_charts(chart_id TEXT PRIMARY KEY,name TEXT UNIQUE NOT NULL,family TEXT NOT NULL,dimensionality TEXT,applicability TEXT NOT NULL,schema_json TEXT NOT NULL,status TEXT NOT NULL,created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS coordinates(subject_id TEXT NOT NULL,chart_id TEXT NOT NULL,status TEXT NOT NULL,value_json TEXT,source_eid TEXT,transform_id TEXT,loss_json TEXT,created_at REAL NOT NULL,PRIMARY KEY(subject_id,chart_id));
CREATE TABLE IF NOT EXISTS transforms(transform_id TEXT PRIMARY KEY,src_chart TEXT NOT NULL,dst_chart TEXT NOT NULL,operator_oid TEXT,operator_vid TEXT,status TEXT NOT NULL,loss_model_json TEXT NOT NULL,eid TEXT NOT NULL,created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS transform_programs(transform_id TEXT PRIMARY KEY,mode TEXT NOT NULL,program_json TEXT,metric_json TEXT NOT NULL,created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS transform_executions(execution_id TEXT PRIMARY KEY,transform_id TEXT NOT NULL,subject_id TEXT,src_json TEXT,dst_json TEXT,target_json TEXT,comparison_json TEXT,status TEXT NOT NULL,eid TEXT NOT NULL,created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS holonomy_observations(observation_id TEXT PRIMARY KEY,subject_id TEXT NOT NULL,route_json TEXT NOT NULL,start_json TEXT NOT NULL,returned_json TEXT NOT NULL,defect_json TEXT NOT NULL,metric REAL,status TEXT NOT NULL,eid TEXT NOT NULL,created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS crystals(crystal_id TEXT PRIMARY KEY,oid TEXT NOT NULL,vid TEXT NOT NULL,mid TEXT NOT NULL,manifest_json TEXT NOT NULL,header TEXT NOT NULL,created_at REAL NOT NULL);
CREATE INDEX IF NOT EXISTS idx_math_owner ON math_objects(owner_id);
CREATE INDEX IF NOT EXISTS idx_coordinates_subject ON coordinates(subject_id);
CREATE INDEX IF NOT EXISTS idx_transforms_pair ON transforms(src_chart,dst_chart,created_at);
CREATE INDEX IF NOT EXISTS idx_transform_exec_subject ON transform_executions(subject_id,created_at);
'''

class CrystalBase:
    def _install(self):
        with self.s.db: self.s.db.executescript(EXTENSION_SCHEMA)
        with self.s.db:
            for name,meta in CHARTS.items():
                self.s.db.execute("INSERT OR IGNORE INTO coordinate_charts VALUES(?,?,?,?,?,?,?,?)",(
                    'CHART.'+name,name,meta['family'],meta.get('dimensionality'),meta['applicability'],json.dumps({'open_world':True}),'ACTIVE',time.time()))
        seeds=[
          ('TOOL','OUTPUT','CRYSTALLIZE','VISIBLE_TEXT','POLYCOORDINATE_FIBER',{'semantic':'signature','text':'string','metadata':'object'},{'crystal':'manifest','header':'string'}),
          ('TOOL','NAVIGATION','RESOLVE','CRYSTAL','DENSE_POLYATLAS',{'identifier':'OID|CID|CRYS'},{'routes':'all coordinate/graph/lineage views'}),
          ('TOOL','COORDINATE','APPLY','TRANSFORM','SAFE_DECLARATIVE_DSL',{'subject':'id','src_chart':'chart','dst_chart':'chart'},{'result':'coordinate','defect':'comparison'}),
          ('TOOL','OUTPUT','FINALIZE','VISIBLE_TEXT','CRYSTAL_EMISSION_GATEWAY',{'semantic':'signature','text':'string','metadata':'object'},{'visible_text':'header+body','envelope':'ENV'})]
        for args in seeds:self.core.register(*args,actor='GENESIS.V2.2',status='CANONICAL')
    def _event(self,event_type,actor,payload):
        parent=self.s.head('global'); pe=parent['eid'] if parent else None
        eid=event_id(event_type,actor,pe,payload); ed=digest(payload,32)
        self.s.put_event(eid,event_type,actor,pe,payload,ed); self.s.set_head('global',None,None,eid,ed)
        return eid
    def _put_coordinate(self,subject_id,name,slot,source_eid):
        chart_id=name if name.startswith('CHART.') else 'CHART.'+name
        chart_name=chart_id[6:]
        if not self.s.one("SELECT chart_id FROM coordinate_charts WHERE chart_id=?",(chart_id,)):
            with self.s.db:self.s.db.execute("INSERT INTO coordinate_charts VALUES(?,?,?,?,?,?,?,?)",(chart_id,chart_name,slot.get('family','EXTENSION'),None,'CONDITIONAL',json.dumps({'open_world':True}),'ACTIVE',time.time()))
        val=json.dumps(slot.get('value'),sort_keys=True,ensure_ascii=False) if slot.get('value') is not None else None
        loss=json.dumps(slot.get('loss'),sort_keys=True,ensure_ascii=False) if slot.get('loss') is not None else None
        with self.s.db:self.s.db.execute("INSERT OR REPLACE INTO coordinates VALUES(?,?,?,?,?,?,?,?)",(subject_id,chart_id,slot['status'],val,source_eid,slot.get('transform'),loss,time.time()))
    def _coordinate(self,subject_id,chart):
        cid=chart if chart.startswith('CHART.') else 'CHART.'+chart
        r=self.s.one("SELECT * FROM coordinates WHERE subject_id=? AND chart_id=?",(subject_id,cid))
        if r and r.get('value_json') is not None:r['value']=json.loads(r['value_json'])
        return r
    def _lineage(self,oid,vid):
        chain=[]; cur=vid; seen=set()
        while cur and cur not in seen:
            seen.add(cur); row=self.s.one("SELECT vid,parent_vid,status,created_at FROM versions WHERE vid=?",(cur,))
            if not row:break
            chain.append(row); cur=row['parent_vid']
        return {'oid':oid,'vid':vid,'depth':max(0,len(chain)-1),'chain':chain,'parent_vid':chain[0]['parent_vid'] if chain else None}
