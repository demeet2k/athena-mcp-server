from __future__ import annotations
import dataclasses,json,pathlib,tempfile,unittest
from kc144_v7_runtime import *
from kc144_v7_navigation import register_kc144_v7
BASE=pathlib.Path(__file__).resolve().parents[2]; BAML=BASE/'baml_src'; RECS=BASE/'recordings'
class FakeMCP:
 def __init__(self):self.tools={}
 def tool(self):
  def d(fn):self.tools[fn.__name__]=fn;return fn
  return d
class Tests(unittest.TestCase):
 def test_revision(self):j=RevisionJournal();self.assertTrue(j.scan(BAML));self.assertTrue(j.verify());self.assertEqual(j.scan(BAML),())
 def test_tamper(self):j=RevisionJournal();j.scan(BAML);j.events[0]=dataclasses.replace(j.events[0],new_digest='x');self.assertFalse(j.verify())
 def test_recording(self):f=FixtureStore(RECS).load('compile_query_contract.rec.json');self.assertFalse(f.external_witness)
 def test_bad_secret(self):
  with tempfile.TemporaryDirectory() as t:
   raw=json.loads((RECS/'compile_query_contract.rec.json').read_text());raw['headers']['authorization']='secret';pathlib.Path(t,'x.json').write_text(json.dumps(raw));self.assertRaises(ValueError,FixtureStore(t).load,'x.json')
 def valid(self):return {'query_id':'Q','literal':'x','intents':[],'exact_addresses':[],'requires_sources':False,'requires_execution':False,'requires_audit':False,'route_budget':1,'claim_ceiling':'RESEARCH_ONLY','authority_effect':'NONE'}
 def test_fallback(self):
  ps=(ModelProfile('a','rec',0,1,1,('typed',)),ModelProfile('b','api',.01,10,.5,('typed',)));r=FallbackRouter(ps);r.bind('a',lambda f,a:self.valid());x,_=r.route('CompileQueryContract',{},('typed',));self.assertEqual(x.selected_model_id,'a')
 def test_validation_fallback(self):
  ps=(ModelProfile('a','rec',0,1,1,('typed',)),ModelProfile('b','api',.01,10,.5,('typed',)));r=FallbackRouter(ps);r.bind('a',lambda f,a:{'authority_effect':'NONE'});r.bind('b',lambda f,a:self.valid());x,_=r.route('CompileQueryContract',{},('typed',));self.assertEqual(x.selected_model_id,'b')
 def test_coalition(self):
  ps=(OrganProposal('S',1,3,frozenset(),frozenset(),frozenset({'s'}),False),OrganProposal('R',1,2,frozenset(),frozenset({'S'}),frozenset({'s','r'}),True));fs=({'s':1,'generated_manifestation':True,'authority_effect':'NONE','final':False},{'s':1,'r':1,'generated_manifestation':True,'authority_effect':'NONE','final':True});x=CoalitionScheduler().schedule(ps,fs);self.assertEqual(x.state,CoalitionState.DISSOLVED)
 def test_validate(self):self.assertEqual(V7Runtime(BAML,RECS).validate()['revision_journal'],'PASS')
 def test_mcp(self):f=FakeMCP();register_kc144_v7(f);self.assertEqual(set(f.tools),{'kc144_v7_validate','kc144_v7_revisions','kc144_v7_recordings'})
if __name__=='__main__':unittest.main()
