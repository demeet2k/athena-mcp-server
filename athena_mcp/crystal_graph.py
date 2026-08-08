from __future__ import annotations
import json,time
from collections import defaultdict
from .identity import digest
from .crystal import MATH_KINDS

class CrystalGraphMixin:
    def add_hyperedge(self,relation,members,actor='agent',attrs=None):
        members=sorted(set(members)); attrs=attrs or {}
        if len(members)<2:raise ValueError('hyperedge requires at least 2 members')
        ep={'relation':relation,'members':members,'attrs':attrs}; eid=self._event('HYPEREDGE',actor,ep); hid='HYPER.'+digest(ep,20)
        with self.s.db:self.s.db.execute("INSERT OR IGNORE INTO hyperedges VALUES(?,?,?,?,?,?)",(hid,relation,json.dumps(members),eid,json.dumps(attrs,sort_keys=True),time.time()))
        return {'hyperedge_id':hid,'event':eid,'arity':len(members),'dimension':len(members)-1}
    def register_math(self,owner_id,items,source_eid):
        out=[]
        for item in items or []:
            kind=str(item.get('kind','EQUATION')).upper(); latex=item.get('latex') or item.get('expression')
            if kind not in MATH_KINDS:raise ValueError(f'unsupported math kind {kind}')
            if not latex:raise ValueError('math object requires latex/expression')
            p={'owner':owner_id,'kind':kind,'symbol':item.get('symbol'),'latex':latex,'assumptions':item.get('assumptions',[]),'status':item.get('status','FORMALIZED')}; mid='MATH.'+digest(p,24)
            with self.s.db:self.s.db.execute("INSERT OR REPLACE INTO math_objects VALUES(?,?,?,?,?,?,?,?,?)",(mid,owner_id,kind,p['symbol'],latex,json.dumps(p['assumptions']),p['status'],source_eid,time.time()))
            out.append({'math_id':mid,**p})
        return out
    def _jspace(self,oid):
        out=self.s.rows("SELECT edge_id,relation,dst,eid FROM edges WHERE src=? ORDER BY created_at",(oid,)); inc=self.s.rows("SELECT edge_id,relation,src,eid FROM edges WHERE dst=? ORDER BY created_at",(oid,)); hypers=[]
        for h in self.s.rows("SELECT * FROM hyperedges ORDER BY created_at"):
            members=json.loads(h['members_json'])
            if oid in members:hypers.append({'hyperedge_id':h['hyperedge_id'],'relation':h['relation'],'members':members,'eid':h['eid']})
        return {'node':oid,'in_degree':len(inc),'out_degree':len(out),'degree':len(inc)+len(out),'hyperedge_count':len(hypers),'incoming':inc,'outgoing':out,'hyperedges':hypers}
    def register_transform(self,src_chart,dst_chart,operator_oid=None,operator_vid=None,status='FORMALIZED',loss_model=None,actor='agent'):
        sc=src_chart if src_chart.startswith('CHART.') else 'CHART.'+src_chart; dc=dst_chart if dst_chart.startswith('CHART.') else 'CHART.'+dst_chart
        for c in (sc,dc):
            if not self.s.one("SELECT chart_id FROM coordinate_charts WHERE chart_id=?",(c,)):raise KeyError(f'unknown chart {c}')
        ep={'src_chart':sc,'dst_chart':dc,'operator_oid':operator_oid,'operator_vid':operator_vid,'status':status,'loss_model':loss_model or {}}; eid=self._event('REGISTER_TRANSFORM',actor,ep); tid='TRANSFORM.'+digest(ep,24)
        with self.s.db:self.s.db.execute("INSERT OR REPLACE INTO transforms VALUES(?,?,?,?,?,?,?,?,?)",(tid,sc,dc,operator_oid,operator_vid,status,json.dumps(loss_model or {},sort_keys=True),eid,time.time()))
        return {'transform_id':tid,**ep,'event':eid}
    def coordinate_matrix(self,subject_id=None):
        charts=self.s.rows("SELECT chart_id,name FROM coordinate_charts ORDER BY name"); transforms=self.s.rows("SELECT * FROM transforms ORDER BY src_chart,dst_chart"); coords=self.s.rows("SELECT chart_id,status FROM coordinates WHERE subject_id=?",(subject_id,)) if subject_id else []
        status={r['chart_id']:r['status'] for r in coords}; resolved=[c['chart_id'] for c in charts if status.get(c['chart_id']) in ('RESOLVED','PARTIAL')]; pair={(t['src_chart'],t['dst_chart']):t for t in transforms}; capacity=len(resolved)*(len(resolved)-1); covered=sum((a,b) in pair for a in resolved for b in resolved if a!=b)
        triangles=[]
        for a in resolved:
            for b in resolved:
                for c in resolved:
                    if len({a,b,c})==3 and min(a,b,c)==a and (a,b) in pair and (b,c) in pair and (c,a) in pair:triangles.append([a,b,c])
        return {'subject_id':subject_id,'resolved_charts':resolved,'directed_pair_capacity':capacity,'covered_pairs':covered,'transform_coverage':covered/capacity if capacity else None,'closed_triangles':triangles,'holonomy_observations':self.s.rows("SELECT * FROM holonomy_observations WHERE subject_id=? ORDER BY created_at",(subject_id,)) if subject_id else []}
    def record_holonomy(self,subject_id,route,start,returned,defect,metric=None,status='MEASURED',actor='agent'):
        if len(route)<3 or route[0]!=route[-1]:raise ValueError('holonomy route must be closed')
        ep={'subject_id':subject_id,'route':route,'start':start,'returned':returned,'defect':defect,'metric':metric,'status':status}; eid=self._event('HOLONOMY_OBSERVATION',actor,ep); oid='HOLO.'+digest(ep,24)
        with self.s.db:self.s.db.execute("INSERT OR REPLACE INTO holonomy_observations VALUES(?,?,?,?,?,?,?,?,?,?)",(oid,subject_id,json.dumps(route),json.dumps(start,sort_keys=True),json.dumps(returned,sort_keys=True),json.dumps(defect,sort_keys=True),metric,status,eid,time.time()))
        return {'observation_id':oid,'event':eid,**ep}
    def graph_path(self,src,dst,relations=None,max_depth=12):
        if src==dst:return {'found':True,'path':[src],'edges':[],'length':0}
        relset=set(relations or []); adj=defaultdict(list)
        for e in self.s.rows("SELECT edge_id,src,relation,dst,eid FROM edges"):
            if not relset or e['relation'] in relset:adj[e['src']].append(e)
        q=[(src,[src],[])]; seen={src}
        while q:
            node,nodes,eds=q.pop(0)
            if len(eds)>=max_depth:continue
            for e in adj.get(node,[]):
                nxt=e['dst']
                if nxt==dst:return {'found':True,'path':nodes+[nxt],'edges':eds+[e],'length':len(eds)+1}
                if nxt not in seen:seen.add(nxt);q.append((nxt,nodes+[nxt],eds+[e]))
        return {'found':False,'src':src,'dst':dst,'relations':sorted(relset),'max_depth':max_depth}
