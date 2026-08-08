from __future__ import annotations
import hashlib,json,time
from .identity import manifestation_id
from .kc144 import coordinate_text
from .timebundle import bundle as make_time_bundle
from .polycoord import atlas as build_atlas
from .crystal import scale_state,crystal_id,render_header
from .core import StaleTarget

class CrystalCompileMixin:
    def crystallize_output(self,semantic,text,native_locator,agent,task,seq,expected_vid=None,carrier='text/plain',edges=None,hyperedges=None,math_objects=None,coordinates=None,cut_lm=None,evidence=None,scale_promotions=None,session_id=None,ephemeris=None,status='CRYSTALLIZED'):
        req=['kind','domain','verb','object_name','method','input_contract','output_contract']; miss=[k for k in req if k not in semantic]
        if miss:raise ValueError(f'semantic missing {miss}')
        reg=self.core.register(semantic['kind'],semantic['domain'],semantic['verb'],semantic['object_name'],semantic['method'],semantic['input_contract'],semantic['output_contract'],semantic.get('constraints'),semantic.get('payload'),actor=agent,status='CANONICAL' if semantic.get('canonical') else 'CANDIDATE')
        obj=reg['object'];oid=obj['oid'];head=self.s.head(f'object:{oid}');current=head['vid'] if head else None
        if expected_vid is not None and current!=expected_vid:raise StaleTarget(json.dumps({'status':'STALE_TARGET','expected':expected_vid,'current':current,'oid':oid}))
        before=current; ing=self.core.ingest_text(oid,current,text,native_locator,carrier,actor=agent);vid=ing['version']['vid'];mid=ing['mid'];source_eid=ing['event']
        er=[]
        for e in edges or []:
            if not e.get('dst') or not e.get('relation'):raise ValueError('edge requires relation and dst')
            er.append(self.core.add_edge(e.get('src',oid),e['relation'],e['dst'],agent,e.get('attrs')))
        hr=[]
        for h in hyperedges or []:
            members=list(h.get('members',[]))
            if oid not in members and h.get('include_self',True):members=[oid,*members]
            hr.append(self.add_hyperedge(h.get('relation','CO-PARTICIPATES'),members,agent,h.get('attrs')))
        maths=self.register_math(mid,math_objects,source_eid); j=self._jspace(oid); lineage=self._lineage(oid,vid)
        liminal={'agent':agent,'task':task,'seq':int(seq),'session_id':session_id,'address':f'LIMINAL/{agent}/{task}/SEQ:{int(seq):06d}'}
        logical=self.s.one("SELECT COUNT(*) n FROM events")['n'];tb=make_time_bundle(logical_clock=logical,liminal=liminal,ephemeris=ephemeris)
        scale=scale_state(has_text=bool(text),edge_count=len(er),hyperedge_count=len(hr),declared=scale_promotions)
        atlas=build_atlas(canonical_name=obj['canonical_name'],oid=oid,vid=vid,mid=mid,jspace=j,scale=scale,lineage=lineage,time_bundle=tb,liminal=liminal,cut_lm=cut_lm,evidence=evidence,supplied=coordinates)
        for name,slot in atlas.items():self._put_coordinate(oid,name,slot,source_eid);self._put_coordinate(mid,name,slot,source_eid)
        manifest={'schema':'ATHENA.CRYSTAL.OUTPUT.v1','identity':{'CID':obj['cid'],'OID':oid,'VID':vid,'MID':mid,'parent_VID':before,'canonical_name':obj['canonical_name']},'semantic':{'kind':obj['kind'],'domain':obj['domain'],'verb':obj['verb'],'object':obj.get('object_name',obj.get('object')),'method':obj['method']},'native':{'carrier':carrier,'locator':native_locator,'content_digest':ing['content_digest']},'coordinates':atlas,'text_coordinates':{'count':ing['token_count'],'first':ing['first_coordinate'],'last':ing['last_coordinate']},'graph_delta':{'edges':er,'hyperedges':hr,'jspace_after':j},'mathematics':maths,'lineage':lineage,'evidence':evidence or {'status':'UNKNOWN'},'CUT_LM':cut_lm or {'status':'UNKNOWN'},'status':status,'RETURN':native_locator}
        manifest['crystal_id']=crystal_id(manifest);header=render_header(manifest);header_locator=native_locator+'#ATHENA-CRYSTAL-HEADER';hd=hashlib.sha256(header.encode()).hexdigest();hmid=manifestation_id(vid,'application/vnd.athena.crystal-header+text',header_locator,hd)
        self.s.put_manifestation(hmid,vid,'application/vnd.athena.crystal-header+text',header_locator,hd,header);ht=coordinate_text(header,oid,vid,hmid,obj['canonical_name']);self.s.put_tokens(hmid,ht)
        manifest['envelope']={'header_mid':hmid,'header_locator':header_locator,'header_content_digest':hd,'header_token_count':len(ht),'header_first_coordinate':ht[0]['coordinate'] if ht else None,'header_last_coordinate':ht[-1]['coordinate'] if ht else None};manifest['token_polyfiber_law']='Pi(token)=ExactTokenKC144Address ⊕ CoordinateAtlas(OID,VID,MID)'
        with self.s.db:self.s.db.execute("INSERT OR REPLACE INTO crystals VALUES(?,?,?,?,?,?,?)",(manifest['crystal_id'],oid,vid,mid,json.dumps(manifest,sort_keys=True,ensure_ascii=False),header,time.time()))
        ceid=self._event('CRYSTALLIZE_OUTPUT',agent,{'crystal_id':manifest['crystal_id'],'oid':oid,'vid':vid,'mid':mid,'source_eid':source_eid,'edge_count':len(er),'hyperedge_count':len(hr),'math_count':len(maths)});manifest['crystallize_eid']=ceid
        with self.s.db:self.s.db.execute("UPDATE crystals SET manifest_json=? WHERE crystal_id=?",(json.dumps(manifest,sort_keys=True,ensure_ascii=False),manifest['crystal_id']))
        return {'crystal_id':manifest['crystal_id'],'header':header,'manifest':manifest,'event':ceid}
    def dense_navigate(self,identifier):
        cry=self.s.one("SELECT * FROM crystals WHERE crystal_id=?",(identifier,))
        if cry:return {'found':True,'type':'CRYSTAL','crystal':json.loads(cry['manifest_json']),'header':cry['header']}
        nav=self.core.navigate(identifier)
        if not nav.get('found'):return nav
        oid=nav['object']['oid'];head=nav['head'];vid=head['vid'] if head else None
        mans=self.s.rows("SELECT mid,vid,carrier,native_locator,content_digest,created_at FROM manifestations WHERE vid IN (SELECT vid FROM versions WHERE oid=?) ORDER BY created_at",(oid,));coords=self.s.rows("SELECT * FROM coordinates WHERE subject_id=? ORDER BY chart_id",(oid,));maths=self.s.rows("SELECT * FROM math_objects WHERE owner_id=? OR owner_id IN (SELECT mid FROM manifestations WHERE vid IN (SELECT vid FROM versions WHERE oid=?)) ORDER BY created_at",(oid,oid));crystals=self.s.rows("SELECT crystal_id,vid,mid,created_at FROM crystals WHERE oid=? ORDER BY created_at",(oid,))
        return {**nav,'type':'OBJECT','lineage':self._lineage(oid,vid) if vid else None,'jspace':self._jspace(oid),'manifestations':mans,'coordinates':coords,'math_objects':maths,'crystals':crystals,'coordinate_matrix':self.coordinate_matrix(oid),'routes':{'RETURN':[m['native_locator'] for m in mans[-10:]],'PARENTS':[v['parent_vid'] for v in nav['versions'] if v['parent_vid']],'OUT':[e['dst'] for e in nav['outgoing']],'IN':[e['src'] for e in nav['incoming']]}}
