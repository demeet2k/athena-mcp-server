import json
import tempfile
import unittest

from athena_mcp.server import Server


class AorCollectiveBraidTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):
        self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args):
        response=self.rpc('tools/call',{'name':name,'arguments':args});result=response['result'];self.assertFalse(result.get('isError'),response);return result['structuredContent']
    @staticmethod
    def candidate(ident,scale=1.0,branch_id=None):
        row={'id':ident,'readiness':1.0,'gain':2.0*scale,'independence':1.0,'bridge':1.0,'cost':1.0,'resource_cost':1.0,'delta_j':2.0*scale,'information_gain':1.0,'option_value':1.0,'evidence':1.0,'connection':1.0,'replay':1.0,'navigation':1.0,'reconstruction':1.0,'implementation':1.0,'novelty':1.0,'duplicate':0,'fake':0,'bloat':0,'unsupported':0,'unhandled_contradiction':0,'coordinate_loss':0}
        if branch_id:row['branch_id']=branch_id
        return row

    def test_tool_and_resource_union_preserves_collective_and_aor(self):
        names={row['name'] for row in self.rpc('tools/list')['result']['tools']}
        for name in ['athena_collective_plan','athena_pheromone_reinforce','athena_topology_apply','athena_orchestrate','athena_branch_observe','athena_orchestration_robustness']:
            self.assertIn(name,names)
        resources={row['uri'] for row in self.rpc('resources/list')['result']['resources']}
        for uri in ['athena://collective/runtime','athena://collective/v2','athena://orchestration/law','athena://branches']:
            self.assertIn(uri,resources)

    def test_collective_runtime_still_executes_after_aor_integration(self):
        plan=self.tool('athena_collective_plan',{'signals':{},'max_workers':8})
        self.assertIn(plan['form'],{'HIVE','SWARM','PACK','FLOCK','HERD','POD'})
        self.assertGreaterEqual(plan['active_workers'],1)
        self.assertIn('collective_coordinate',plan)

    def test_aorrun_selects_replays_and_exposes_robustness(self):
        run=self.tool('athena_orchestrate',{'seed':'S','candidates':[self.candidate('weak',0.5),self.candidate('strong',1.0)],'task':'braid-test'})
        self.assertTrue(run['persisted']);self.assertEqual(run['next']['id'],'strong');self.assertTrue(run['run_id'].startswith('AORRUN.'))
        replay=self.tool('athena_orchestration_replay',{'run_id':run['run_id']});self.assertTrue(replay['match'],replay)
        robustness=self.tool('athena_orchestration_robustness',{'run_id':run['run_id'],'relative_perturbation':0.01})
        self.assertEqual(robustness['winner'],'strong');self.assertEqual(robustness['decision_digest'],run['decision_digest'])

    def test_hibernated_branch_is_not_selected_even_with_high_score(self):
        observation=self.tool('athena_branch_observe',{'branch_id':'B1','basis_id':'RAW.UNDECLARED','reward':-1,'witness':{'verified':True,'ref':'test://negative'},'policy':{'alpha':1,'min_observations':1,'hibernate_below':0,'resurrect_above':0.5}})
        self.assertEqual(observation['status'],'HIBERNATED')
        run=self.tool('athena_orchestrate',{'seed':'S','candidates':[self.candidate('hibernated',5,'B1'),self.candidate('live',1)]})
        self.assertEqual(run['next']['id'],'live')
        blocked=next(row for row in run['frontier'] if row['id']=='hibernated')
        self.assertEqual(blocked['gate']['gates']['lifecycle']['status'],'HIBERNATED')
        self.assertFalse(blocked['rankable_successor'])

    def test_pheromone_priority_never_becomes_aor_evidence_implicitly(self):
        self.tool('athena_pheromone_reinforce',{'route_key':'candidate:X','observations':{'quality':1,'reuse':1,'evidence':1}})
        candidate=self.candidate('X');candidate.pop('evidence')
        run=self.tool('athena_orchestrate',{'seed':'S','candidates':[candidate],'persist':False})
        row=run['frontier'][0]
        self.assertNotIn('evidence',row['source'])
        self.assertIn('evidence',row['unknown_metrics'])
        self.assertEqual(row['scores']['reward']['status'],'UNKNOWN')
        pheromone=self.tool('athena_pheromone_field',{'route_key':'candidate:X'})
        self.assertTrue(pheromone)

    def test_benchmark_reports_both_metabolisms(self):
        bench=self.tool('athena_benchmark',{})
        self.assertIn('collective_runtime',bench);self.assertIn('collective_memory',bench);self.assertIn('orchestration_runs',bench);self.assertIn('branches',bench);self.assertEqual(bench['aor_law'],'AOR.3.1')

    def test_unified_manifest_states_authority_boundary(self):
        payload=json.loads(self.rpc('resources/read',{'uri':'athena://manifest'})['result']['contents'][0]['text'])
        self.assertIn('AOR_DECISION_CORTEX',payload['layers']);self.assertIn('COLLECTIVE_MEMORY_V2',payload['layers']);self.assertIn('pheromone/consensus never become evidence',payload['braid_law'])


if __name__=='__main__':unittest.main()
