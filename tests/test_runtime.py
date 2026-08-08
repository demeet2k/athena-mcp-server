import os, subprocess, tempfile, unittest
from pathlib import Path
from athena_mcp.store import Store
from athena_mcp.core import AthenaCore, StaleTarget
from athena_mcp.server import Server
from athena_mcp.orchestration import TRANSFORMS, compile_orchestration

BASE_METRICS={'readiness':1,'gain':2,'independence':1,'bridge':1,'cost':1,'delta_j':2,'information_gain':1,'option_value':1,'evidence':1,'connection':1,'replay':1,'navigation':1,'reconstruction':1,'implementation':1,'novelty':1,'duplicate':0,'fake':0,'bloat':0,'unsupported':0,'unhandled_contradiction':0,'coordinate_loss':0}
SUCCESSOR_CONTRACT={'basis_id':'AOR.TEST.V1','strict':True,'metrics':{'delta_j':{'scale':2,'unit':'normalized-delta'},'information_gain':{'scale':1},'bridge':{'scale':1},'option_value':{'scale':1},'cost':{'scale':1}}}

class RuntimeTests(unittest.TestCase):
 def test_registry_stale_text_simplex(self):
  with tempfile.NamedTemporaryFile(suffix='.db') as f:
   s=Store(f.name); c=AthenaCore(s); r=c.register('TOOL','TEST','MEASURE','STATE','EXACT',{},{}); self.assertEqual(c.register('TOOL','TEST','MEASURE','STATE','EXACT',{}, {})['action'],'REUSE'); oid=r['object']['oid']; vid=r['version']['vid']; c.commit_delta(oid,vid,{'x':1});
   with self.assertRaises(StaleTarget): c.commit_delta(oid,vid,{'x':2})
   r2=c.register('ARTIFACT','TEXT','INDEX','OUTPUT','LEXEME_COORDS',{},{}); x=c.ingest_text(r2['object']['oid'],r2['version']['vid'],'Hello, world. Again!','memory://demo'); self.assertIn('/C:',x['first_coordinate']); self.assertEqual(c.form_simplex(['a','b','c'],'t','x')['dimension'],2); s.close()
 def test_mcp_composition_preserves_transform_emission_and_aor(self):
  with tempfile.NamedTemporaryFile(suffix='.db') as f:
   srv=Server(f.name); self.assertGreaterEqual(srv.core.benchmark()['objects'],16); r=srv.handle({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25'}}); self.assertEqual(r['result']['protocolVersion'],'2025-11-25'); names=[x['name'] for x in srv.handle({'jsonrpc':'2.0','id':2,'method':'tools/list'})['result']['tools']]; self.assertEqual(names,sorted(names))
   for name in ['athena_crystallize_output','athena_dense_navigate','athena_apply_transform','athena_apply_transform_route','athena_finalize_output','athena_verify_emission','athena_orchestrate','athena_orchestration_get','athena_orchestration_replay']: self.assertIn(name,names)
   resources=srv.handle({'jsonrpc':'2.0','id':3,'method':'resources/list'})['result']['resources']; uris=[x['uri'] for x in resources];
   for uri in ['athena://orchestration/law','athena://orchestration/recent','athena://transforms','athena://emissions']: self.assertIn(uri,uris)
   srv.store.close()
 def test_aor_frontier_reward_and_hibernate(self):
  strong={'id':'strong',**BASE_METRICS}; duplicate={'id':'duplicate',**{**BASE_METRICS,'readiness':0,'gain':0,'delta_j':0,'evidence':0,'connection':0,'replay':0,'navigation':0,'reconstruction':0,'implementation':0,'novelty':0,'duplicate':1}}
  out=compile_orchestration('seed',[duplicate,strong],[{'id':'gap','severity':2,'leverage':3,'information_gain':4,'cost':2}],{'tokens':495}); self.assertEqual(len(out['extraction_plan']),len(TRANSFORMS)); self.assertEqual(out['next']['id'],'strong'); self.assertEqual(out['grow']['id'],'gap'); self.assertIn('braid',out['frontier'][0]['allocation']); dup=next(x for x in out['frontier'] if x['id']=='duplicate'); self.assertEqual(dup['allocation'],['hibernate']); self.assertFalse(out['law']['allocation']['hibernate_is_erase'])
 def test_unknown_is_not_zero_and_measurement_plan_is_explicit(self):
  incomplete={'id':'unknown',**BASE_METRICS}; incomplete.pop('option_value'); complete={'id':'known',**{**BASE_METRICS,'delta_j':0.1}}
  out=compile_orchestration('seed',[incomplete,complete]); self.assertEqual(out['next']['id'],'known'); unknown=next(x for x in out['measurement_frontier'] if x['id']=='unknown'); self.assertEqual(unknown['scores']['successor']['status'],'UNKNOWN'); self.assertIsNone(unknown['scores']['successor']['value']); self.assertIn('option_value',unknown['unknown_metrics']); self.assertFalse(unknown['rankable_successor']); req=next(x for x in out['measurement_plan'] if x['candidate']=='unknown'); self.assertIn('successor',req['blocked_formulas']); self.assertIn('option_value',req['missing_metrics'])
 def test_dependency_and_cycle_block_frontier(self):
  parent={'id':'parent',**BASE_METRICS,'resolved':False}; child={'id':'child',**BASE_METRICS,'requires':['parent']}; out=compile_orchestration('seed',[parent,child]); child_row=next(x for x in out['frontier'] if x['id']=='child'); self.assertFalse(child_row['dependency']['ready']); self.assertIn('unresolved_dependency',child_row['dependency']['blockers']); self.assertEqual(child_row['allocation'],['resolve_dependency']); self.assertEqual(out['next']['id'],'parent')
  cyc=compile_orchestration('seed',[{'id':'a',**BASE_METRICS,'requires':['b']},{'id':'b',**BASE_METRICS,'requires':['a']}]); self.assertTrue(cyc['dependency_graph']['cycles']); self.assertIsNone(cyc['next'])
 def test_witness_persistence_coordinate_and_evidence_gates(self):
  no_witness={'id':'nw',**BASE_METRICS,'test':{'claimed':True,'procedure':'p','observation':'o','result':'r'}}; no_receipt={'id':'nr',**BASE_METRICS,'transaction':{'persisted':True,'commit':'c','verify':'v'}}; coord={'id':'coord',**BASE_METRICS,'require_coordinates':True,'coordinates':{'kc144':1,'graph':1,'lineage':1,'semantic':1}}; unsupported={'id':'u',**BASE_METRICS,'unsupported':1}
  out=compile_orchestration('seed',[no_witness,no_receipt,coord,unsupported]); self.assertIsNone(out['next']); rows={x['id']:x for x in out['frontier']}; self.assertIn('test',rows['nw']['gate']['blocked_by']); self.assertIn('persistence',rows['nr']['gate']['blocked_by']); self.assertIn('coordinates',rows['coord']['gate']['blocked_by']); self.assertIn('evidence',rows['u']['gate']['blocked_by']); self.assertEqual(rows['nw']['allocation'],['branch','repair','retest'])
 def test_pareto_frontier_and_decision_explanation(self):
  a={'id':'a',**BASE_METRICS}; b={'id':'b',**{**BASE_METRICS,'delta_j':1,'information_gain':2}}; c={'id':'c',**{**BASE_METRICS,'delta_j':1,'information_gain':1,'cost':2}}
  out=compile_orchestration('seed',[a,b,c]); self.assertEqual(out['next']['id'],'a'); self.assertEqual(out['pareto_successor_frontier'],['a','b']); self.assertEqual(out['decision_explanation']['selected'],'a'); rejected={x['candidate']:x['reasons'] for x in out['decision_explanation']['rejected']}; self.assertIn('tie_broken_by_frontier_then_id',rejected['b']); self.assertIn('lower_successor_score',rejected['c'])
 def test_strict_metric_contract_blocks_uncalibrated_successor(self):
  contract={'basis_id':'STRICT.MISSING.OPTION','strict':True,'metrics':{'delta_j':{'scale':1},'information_gain':{'scale':1},'bridge':{'scale':1},'cost':{'scale':1}}}
  out=compile_orchestration('seed',[{'id':'x',**BASE_METRICS}],metric_contract=contract); self.assertIsNone(out['next']); row=out['frontier'][0]; self.assertEqual(row['metric_calibration']['successor']['status'],'BLOCKED'); self.assertFalse(row['rankable_successor']); req=next(x for x in out['calibration_plan'] if x['candidate']=='x' and x['formula']=='successor'); self.assertTrue(req['strict_block']); self.assertIn('option_value',req['metrics']); self.assertIn('metric_calibration_blocked',out['decision_explanation']['rejected'][0]['reasons'])
 def test_metric_contract_normalizes_successor_and_replay_basis(self):
  out=compile_orchestration('seed',[{'id':'x',**BASE_METRICS}],metric_contract=SUCCESSOR_CONTRACT); self.assertEqual(out['next']['id'],'x'); row=out['frontier'][0]; self.assertEqual(row['scoring_source']['delta_j'],1.0); self.assertEqual(row['metric_calibration']['successor']['status'],'CALIBRATED'); self.assertEqual(out['metric_contract']['basis_id'],'AOR.TEST.V1')
  with tempfile.NamedTemporaryFile(suffix='.db') as f:
   srv=Server(f.name); run=srv.call_tool('athena_orchestrate',{'seed':'s','candidates':[{'id':'x',**BASE_METRICS}],'metric_contract':SUCCESSOR_CONTRACT,'actor':'A1','task':'basis'}); replay=srv.call_tool('athena_orchestration_replay',{'run_id':run['run_id']}); self.assertTrue(replay['match']); self.assertEqual(replay['stored_metric_basis']['basis_id'],'AOR.TEST.V1'); self.assertEqual(replay['stored_metric_basis'],replay['recomputed_metric_basis']); srv.store.close()
 def test_aor_persist_get_replay_and_benchmark(self):
  with tempfile.NamedTemporaryFile(suffix='.db') as f:
   srv=Server(f.name); run=srv.call_tool('athena_orchestrate',{'seed':'s','candidates':[{'id':'x',**BASE_METRICS}],'actor':'A1','task':'route'}); self.assertTrue(run['persisted']); self.assertTrue(run['run_id'].startswith('AORRUN.')); stored=srv.call_tool('athena_orchestration_get',{'run_id':run['run_id']}); self.assertEqual(stored['decision_digest'],run['decision_digest']); replay=srv.call_tool('athena_orchestration_replay',{'run_id':run['run_id']}); self.assertTrue(replay['match']); self.assertEqual(replay['status'],'REPLAY_MATCH'); self.assertEqual(replay['stored_pareto'],replay['recomputed_pareto']); bench=srv.call_tool('athena_benchmark',{}); self.assertEqual(bench['orchestration_runs'],1); self.assertEqual(bench['replay_match_rate'],1.0); srv.store.close()
 def test_git_cas(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'brain'; root.mkdir(); subprocess.run(['git','init','-b','main',root],check=True,capture_output=True); (root/'README.md').write_text('x'); subprocess.run(['git','-C',root,'add','.'],check=True); env=os.environ|{'GIT_AUTHOR_NAME':'t','GIT_AUTHOR_EMAIL':'t@x','GIT_COMMITTER_NAME':'t','GIT_COMMITTER_EMAIL':'t@x'}; subprocess.run(['git','-C',root,'commit','-m','genesis'],check=True,capture_output=True,env=env); srv=Server(str(Path(td)/'a.db'),str(root)); head=srv.git.head(); ss=srv.core.session_start('A1','task',head); end=srv.core.session_end(ss['session_id'],{'delta':'ok'},head); out=srv.git.checkpoint(head,srv.core.event(end['end_eid']),srv.core.hydrate(),actor='A1'); self.assertEqual(out['status'],'COMMITTED');
   with self.assertRaises(Exception): srv.git.checkpoint(head,srv.core.event(end['end_eid']),srv.core.hydrate(),actor='A1')
   srv.store.close()
if __name__=='__main__': unittest.main()
