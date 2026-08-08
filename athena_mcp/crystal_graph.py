from __future__ import annotations
import json,time
from collections import defaultdict
from .identity import digest
from .crystal import MATH_KINDS
from .transform_dsl import ALL_MODES, DERIVATIONAL_MODES, evaluate, validate_program, compare

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
    def register_transform(self,src_chart,dst_chart,operator_oid=None,operator_vid=None,status='FORMALIZED',loss_model=None,actor='agent',mode='LOOKUP',program=None,metric=None):
        sc=src_chart if src_chart.startswith('CHART.') else 'CHART.'+src_chart; dc=dst_chart if dst_chart.startswith('CHART.') else 'CHART.'+dst_chart; mode=str(mode).upper()
        if mode not in ALL_MODES:raise ValueError(f'unsupported transform mode {mode}')
        for c in (sc,dc):
            if not self.s.one("SELECT chart_id FROM coordinate_charts WHERE chart_id=?",(c,)):raise KeyError(f'unknown chart {c}')
        if mode!='LOOKUP':
            if program is None:raise ValueError('derivational transform requires program')
            validate_program(program)
        ep={'src_chart':sc,'dst_chart':dc,'operator_oid':operator_oid,'operator_vid':operator_vid,'status':status,'loss_model':loss_model or {},'mode':mode,'program':program,'metric':metric or {'type':'EXACT'}}; eid=self._event('REGISTER_TRANSFORM',actor,ep); tid='TRANSFORM.'+digest(ep,24)
        with self.s.db:
            self.s.db.execute("INSERT OR REPLACE INTO transforms VALUES(?,?,?,?,?,?,?,?,?)",(tid,sc,dc,operator_oid,operator_vid,status,json.dumps(loss_model or {},sort_keys=True),eid,time.time()))
            self.s.db.execute("INSERT OR REPLACE INTO transform_programs VALUES(?,?,?,?,?)",(tid,mode,json.dumps(program,sort_keys=True) if program is not None else None,json.dumps(metric or {'type':'EXACT'},sort_keys=True),time.time()))
        return {'transform_id':tid,**ep,'event':eid}
    def _transform(self,src_chart,dst_chart):
        sc=src_chart if src_chart.startswith('CHART.') else 'CHART.'+src_chart; dc=dst_chart if dst_chart.startswith('CHART.') else 'CHART.'+dst_chart
        return self.s.one("SELECT t.*,p.mode,p.program_json,p.metric_json FROM transforms t LEFT JOIN transform_programs p ON p.transform_id=t.transform_id WHERE t.src_chart=? AND t.dst_chart=? ORDER BY t.created_at DESC LIMIT 1",(sc,dc))
    def _execute_transform_value(self,t,subject_id,source_value=None):
        mode=t.get('mode') or 'LOOKUP'; target=self._coordinate(subject_id,t['dst_chart']) if subject_id else None; target_value=target.get('value') if target else None
        if mode=='LOOKUP':
            if target is None or target.get('status') not in ('RESOLVED','PARTIAL') or target_value is None:raise ValueError('LOOKUP target coordinate is not resolved')
            result=target_value
        else:
            if source_value is None:
                src=self._coordinate(subject_id,t['src_chart']) if subject_id else None
                if src is None or src.get('status') not in ('RESOLVED','PARTIAL') or src.get('value') is None:raise ValueError('source coordinate is not resolved')
                source_value=src['value']
            program=json.loads(t['program_json']) if t.get('program_json') else None
            result=evaluate(program,source_value)
        metric=json.loads(t['metric_json']) if t.get('metric_json') else {'type':'EXACT'}
        comparison=compare(result,target_value,metric) if target_value is not None else {'status':'NO_RESOLVED_TARGET','metric':None}
        return source_value,result,target_value,comparison
    def apply_transform(self,subject_id,src_chart,dst_chart,source_value=None,persist=False,actor='agent'):
        t=self._transform(src_chart,dst_chart)
        if not t:raise KeyError(f'no transform {src_chart}->{dst_chart}')
        source,result,target,comparison=self._execute_transform_value(t,subject_id,source_value)
        status='PASS' if comparison.get('metric') in (0,0.0) else ('DERIVED_NO_TARGET' if comparison.get('status')=='NO_RESOLVED_TARGET' else 'DEFECT')
        ep={'transform_id':t['transform_id'],'subject_id':subject_id,'src_chart':t['src_chart'],'dst_chart':t['dst_chart'],'mode':t.get('mode'),'source':source,'result':result,'target':target,'comparison':comparison,'status':status}; eid=self._event('APPLY_TRANSFORM',actor,ep); xid='TXEXEC.'+digest(ep,24)
        with self.s.db:self.s.db.execute("INSERT OR REPLACE INTO transform_executions VALUES(?,?,?,?,?,?,?,?,?,?)",(xid,t['transform_id'],subject_id,json.dumps(source,sort_keys=True,ensure_ascii=False) if source is not None else None,json.dumps(result,sort_keys=True,ensure_ascii=False),json.dumps(target,sort_keys=True,ensure_ascii=False) if target is not None else None,json.dumps(comparison,sort_keys=True,ensure_ascii=False),status,eid,time.time()))
        if persist and (target is None):
            coord_status='RESOLVED' if t['status'] in ('TESTED','CANONICAL') else 'PARTIAL'
            self._put_coordinate(subject_id,t['dst_chart'],{'status':coord_status,'value':result,'transform':t['transform_id'],'loss':comparison},eid)
        return {'execution_id':xid,'event':eid,**ep}
    def apply_transform_route(self,subject_id,route,source_value=None,actor='agent'):
        if len(route)<2:raise ValueError('route requires at least two charts')
        route=[c if c.startswith('CHART.') else 'CHART.'+c for c in route]
        if source_value is None:
            src=self._coordinate(subject_id,route[0])
            if not src or src.get('value') is None:raise ValueError('route source coordinate not resolved')
            source_value=src['value']
        value=source_value; steps=[]; all_derivational=True
        for a,b in zip(route,route[1:]):
            t=self._transform(a,b)
            if not t:raise KeyError(f'no transform {a}->{b}')
            mode=t.get('mode') or 'LOOKUP'; all_derivational=all_derivational and mode in DERIVATIONAL_MODES
            _,value,target,comparison=self._execute_transform_value(t,subject_id,value)
            steps.append({'transform_id':t['transform_id'],'src_chart':a,'dst_chart':b,'mode':mode,'result':value,'target':target,'comparison':comparison})
        out={'subject_id':subject_id,'route':route,'start':source_value,'returned':value,'steps':steps,'all_derivational':all_derivational}
        if route[0]==route[-1]:
            if all_derivational:
                cmp=compare(value,source_value,{'type':'EXACT'}); out['holonomy']=self.record_holonomy(subject_id,route,source_value,value,cmp.get('defect') or {'equal':True},cmp.get('metric'),actor=actor)
            else:out['holonomy']={'status':'N/A_LOOKUP_ROUTE','reason':'Holonomy is not promoted when any edge is a subject lookup rather than a derivation.'}
        return out
    def coordinate_matrix(self,subject_id=None):
        charts=self.s.rows("SELECT chart_id,name FROM coordinate_charts ORDER BY name"); transforms=self.s.rows("SELECT t.*,p.mode,p.program_json FROM transforms t LEFT JOIN transform_programs p ON p.transform_id=t.transform_id ORDER BY t.src_chart,t.dst_chart,t.created_at"); coords=self.s.rows("SELECT chart_id,status FROM coordinates WHERE subject_id=?",(subject_id,)) if subject_id else []
        status={r['chart_id']:r['status'] for r in coords}; resolved=[c['chart_id'] for c in charts if status.get(c['chart_id']) in ('RESOLVED','PARTIAL')]; latest={}
        for t in transforms:latest[(t['src_chart'],t['dst_chart'])]=t
        capacity=len(resolved)*(len(resolved)-1); registered=sum((a,b) in latest for a in resolved for b in resolved if a!=b); executable=sum(bool((a,b) in latest and (latest[(a,b)].get('mode')=='LOOKUP' or latest[(a,b)].get('program_json'))) for a in resolved for b in resolved if a!=b); deriv=sum(bool((a,b) in latest and latest[(a,b)].get('mode') in DERIVATIONAL_MODES and latest[(a,b)].get('program_json')) for a in resolved for b in resolved if a!=b)
        triangles=[]
        for a in resolved:
            for b in resolved:
                for c in resolved:
                    if len({a,b,c})==3 and min(a,b,c)==a and (a,b) in latest and (b,c) in latest and (c,a) in latest:triangles.append([a,b,c])
        missing=[{'src':a,'dst':b} for a in resolved for b in resolved if a!=b and (a,b) not in latest]
        return {'subject_id':subject_id,'resolved_charts':resolved,'directed_pair_capacity':capacity,'registered_pairs':registered,'executable_pairs':executable,'derivational_pairs':deriv,'navigation_coverage':registered/capacity if capacity else None,'executable_coverage':executable/capacity if capacity else None,'derivation_coverage':deriv/capacity if capacity else None,'missing_pairs':missing,'closed_triangles':triangles,'holonomy_observations':self.s.rows("SELECT * FROM holonomy_observations WHERE subject_id=? ORDER BY created_at",(subject_id,)) if subject_id else [],'recent_executions':self.s.rows("SELECT execution_id,transform_id,status,eid,created_at FROM transform_executions WHERE subject_id=? ORDER BY created_at DESC LIMIT 100",(subject_id,)) if subject_id else []}
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
