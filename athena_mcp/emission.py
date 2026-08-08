from __future__ import annotations
import hashlib,json,time
from .identity import digest,manifestation_id
from .kc144 import coordinate_text

EMISSION_SCHEMA='''
CREATE TABLE IF NOT EXISTS emissions(
 envelope_id TEXT PRIMARY KEY,crystal_id TEXT NOT NULL,emission_mid TEXT NOT NULL,visible_digest TEXT NOT NULL,
 body_digest TEXT NOT NULL,header_digest TEXT NOT NULL,visible_text TEXT NOT NULL,created_at REAL NOT NULL);
CREATE INDEX IF NOT EXISTS idx_emissions_crystal ON emissions(crystal_id);
'''

class EmissionMixin:
    def _install_emission(self):
        with self.s.db:self.s.db.executescript(EMISSION_SCHEMA)
    def finalize_output(self,**kwargs):
        text=kwargs['text']; native_locator=kwargs['native_locator']
        compiled=self.crystallize_output(**kwargs); manifest=compiled['manifest']; header=compiled['header']; visible=header+'\n\n'+text
        vd=hashlib.sha256(visible.encode()).hexdigest(); hd=hashlib.sha256(header.encode()).hexdigest(); bd=manifest['native']['content_digest']
        emission_locator=native_locator+'#ATHENA-FINAL-EMISSION'; emid=manifestation_id(manifest['identity']['VID'],'application/vnd.athena.emission+text',emission_locator,vd)
        self.s.put_manifestation(emid,manifest['identity']['VID'],'application/vnd.athena.emission+text',emission_locator,vd,visible)
        toks=coordinate_text(visible,manifest['identity']['OID'],manifest['identity']['VID'],emid,manifest['identity']['canonical_name']);self.s.put_tokens(emid,toks)
        envelope_id='ENV.'+digest({'crystal':compiled['crystal_id'],'emission_mid':emid,'visible_digest':vd},24)
        with self.s.db:self.s.db.execute("INSERT OR REPLACE INTO emissions VALUES(?,?,?,?,?,?,?,?)",(envelope_id,compiled['crystal_id'],emid,vd,bd,hd,visible,time.time()))
        eid=self._event('FINALIZE_OUTPUT',kwargs.get('agent','agent'),{'envelope_id':envelope_id,'crystal_id':compiled['crystal_id'],'emission_mid':emid,'visible_digest':vd})
        return {'envelope_id':envelope_id,'crystal_id':compiled['crystal_id'],'emission_mid':emid,'event':eid,'visible_digest':vd,'visible_text':visible,'first_coordinate':toks[0]['coordinate'] if toks else None,'last_coordinate':toks[-1]['coordinate'] if toks else None,'token_count':len(toks),'manifest':manifest}
    def verify_emission(self,envelope_id,visible_text=None):
        row=self.s.one("SELECT * FROM emissions WHERE envelope_id=?",(envelope_id,))
        if not row:return {'verified':False,'status':'NOT_FOUND','envelope_id':envelope_id}
        visible=row['visible_text'] if visible_text is None else visible_text; actual=hashlib.sha256(visible.encode()).hexdigest();ok=actual==row['visible_digest']
        return {'verified':ok,'status':'PASS' if ok else 'DIGEST_MISMATCH','envelope_id':envelope_id,'expected_digest':row['visible_digest'],'actual_digest':actual,'emission_mid':row['emission_mid'],'crystal_id':row['crystal_id']}
