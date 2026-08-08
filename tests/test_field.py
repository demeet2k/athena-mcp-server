import tempfile
import unittest

from athena_mcp.core import AthenaCore
from athena_mcp.store import Store
from athena_mcp.orchestration_field import FieldLedger, build_field

AOR_METRICS={'readiness','gain','independence','bridge','cost','delta_j','information_gain','option_value','evidence','connection','replay','navigation','reconstruction','implementation','novelty','duplicate','fake','bloat','unsupported','unhandled_contradiction','coordinate_loss','resource_cost'}

class FieldCompilerTests(unittest.TestCase):
    def modules(self):
        return {
            'extraction_frontier':[{'task_id':'EXTTASK.1','run_id':'EXTRUN.1','seed_ref':'seed://x','transform':'formalize','depth':0,'status':'PLANNED'}],
            'retrieval':{'run_id':'RAGRUN.1','measurement_plan':[{'candidate':'src-missing','defects':[{'metric':'cross_value'}]}],'coverage':{'missing_roles':['contradiction'],'missing_facets':['failure']}},
            'authority_plan':[{'candidate':'claim-work','route':'execute_witnessed_test','reason':'Y below !','minimum':'!','current':'+'}],
            'gap':{'run_id':'GAPRUN.1','measurement_plan':[{'target':'gap-u','node':'u','defects':[{'metric':'information_gain'}]}],'gap':[{'id':'gap-k','node':'k','residual_score':{'status':'KNOWN','value':4}}]},
            'hug_invocations':[{'invocation_id':'HUGINV.1','impl_id':'HUGIMPL.1','status':'PLANNED'},{'invocation_id':'HUGINV.2','impl_id':'HUGIMPL.1','status':'FAILED','failure':{'reason':'executor'}}],
            'branches':[{'branch_id':'BR.1','basis_id':'BASIS.1','state':'REVIEW','ewma':0.7,'last_trigger_ref':'gap:new'}],
            'aor':{'run_id':'AORRUN.1','measurement_plan':[{'candidate':'aor-u','defects':['readiness']}],'calibration_plan':[{'candidate':'aor-c','metrics':['gain']}]},
        }

    def test_module_residuals_become_typed_actions_not_fake_scores(self):
        out=build_field('seed://root',self.modules(),ecosystem={'K':'known','Z':'boundary'})
        kinds={(c['kind'],c['operation']) for c in out['candidates']}
        expected={
            ('EXECUTE','execute_extraction_transform'),('MEASURE','measure_retrieval_candidate'),('RETRIEVE','acquire_missing_retrieval_role'),('RETRIEVE','acquire_missing_retrieval_facet'),('TEST','execute_witnessed_test'),('MEASURE','measure_gap_residual'),('DEVELOP','address_gap_target'),('EXECUTE','execute_hug_invocation'),('REPAIR','repair_hug_failure'),('REVIEW','review_branch_reactivation'),('MEASURE','measure_aor_candidate'),('CALIBRATE','calibrate_aor_candidate')
        }
        self.assertTrue(expected.issubset(kinds));self.assertEqual(set(out['unmeasured_candidate_ids']),set(out['candidate_ids']))
        for candidate in out['candidates']:
            self.assertEqual(candidate['metric_state'],'UNMEASURED')
            self.assertTrue(AOR_METRICS.isdisjoint(candidate.keys()))
        self.assertEqual(out['ecosystem']['Z'],'boundary');self.assertEqual(out['handoff_to_aor'],out['candidates'])

    def test_provenance_edges_are_preserved(self):
        out=build_field('seed://root',self.modules())
        formalize=next(c for c in out['candidates'] if c['operation']=='execute_extraction_transform')
        self.assertIn('EXTTASK.1',formalize['source_refs']);self.assertIn('EXTRUN.1',formalize['source_refs'])
        source_edges=[e for e in out['field_edges'] if e['dst']==formalize['id'] and e['relation']=='proposes']
        self.assertEqual({e['src'] for e in source_edges},{'EXTTASK.1','EXTRUN.1'})

    def test_exact_action_signature_merges_provenance_not_semantic_similarity(self):
        explicit=[
            {'kind':'IMPLEMENT','operation':'build_tool','target_ref':'tool:X','payload':{'v':1},'source_refs':['proof:A'],'field_origin':['EXPLICIT']},
            {'kind':'IMPLEMENT','operation':'build_tool','target_ref':'tool:X','payload':{'v':1},'source_refs':['proof:B'],'field_origin':['EXPLICIT']},
            {'kind':'IMPLEMENT','operation':'build_tool','target_ref':'tool:X','payload':{'v':2},'source_refs':['proof:C'],'field_origin':['EXPLICIT']},
        ]
        out=build_field('seed://x',{},explicit)
        self.assertEqual(len(out['candidates']),2)
        merged=next(c for c in out['candidates'] if c['payload']=={'v':1});self.assertEqual(merged['source_refs'],['proof:A','proof:B']);self.assertEqual(len(out['exact_signature_merges']),1)

    def test_conflicting_explicit_aor_metrics_fail_closed_on_exact_merge(self):
        explicit=[
            {'kind':'IMPLEMENT','operation':'build_tool','target_ref':'tool:X','payload':{},'source_refs':['obs:A'],'readiness':0.9,'gain':0.8,'cost':1},
            {'kind':'IMPLEMENT','operation':'build_tool','target_ref':'tool:X','payload':{},'source_refs':['obs:B'],'readiness':0.2,'gain':0.8,'cost':1},
        ]
        out=build_field('seed://x',{},explicit);self.assertEqual(len(out['candidates']),1);candidate=out['candidates'][0]
        self.assertEqual(candidate['metric_state'],'CONFLICT');self.assertNotIn('readiness',candidate);self.assertNotIn('gain',candidate);self.assertNotIn('cost',candidate);self.assertTrue(candidate['metric_conflicts']);self.assertIn(candidate['id'],out['unmeasured_candidate_ids'])

    def test_identical_explicit_metrics_can_merge_without_conflict(self):
        explicit=[
            {'kind':'BRIDGE','operation':'connect','target_ref':'A->B','payload':{},'source_refs':['s1'],'readiness':1,'gain':2,'cost':1},
            {'kind':'BRIDGE','operation':'connect','target_ref':'A->B','payload':{},'source_refs':['s2'],'readiness':1,'gain':2,'cost':1},
        ]
        out=build_field('seed://x',{},explicit);c=out['candidates'][0];self.assertEqual(c['metric_state'],'EXPLICIT');self.assertEqual(c['readiness'],1);self.assertEqual(c['gain'],2);self.assertEqual(c['source_refs'],['s1','s2']);self.assertEqual(out['unmeasured_candidate_ids'],[])

class FieldLedgerTests(unittest.TestCase):
    def test_fieldrun_persist_and_replay(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as tmp:
            store=Store(tmp.name);core=AthenaCore(store);ledger=FieldLedger(core)
            run=ledger.compile('seed://ledger',{'gap':{'run_id':'GAPRUN.X','gap':[{'id':'g','node':'n','residual_score':{'status':'KNOWN','value':1}}]}},ecosystem={'K':'x'},actor='A1')
            self.assertTrue(run['persisted']);self.assertTrue(run['run_id'].startswith('FIELDRUN.'));self.assertEqual(len(run['candidate_ids']),1)
            replay=ledger.replay(run['run_id']);self.assertTrue(replay['match']);self.assertEqual(replay['stored_candidate_ids'],replay['recomputed_candidate_ids']);self.assertEqual(replay['stored_edges'],replay['recomputed_edges'])
            bench=ledger.benchmark();self.assertEqual(bench['field_runs'],1);self.assertEqual(bench['field_replay_match_rate'],1.0);store.close()

if __name__=='__main__':unittest.main()
