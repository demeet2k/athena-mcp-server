import math
import unittest

from athena_mcp.server import Server
from tests.db_fixture import TemporaryDatabasePath


class MeasuredBudgetAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.db=TemporaryDatabasePath()
        self.path=self.db.__enter__()
        self.server=Server(self.path.name)

    def tearDown(self):
        self.server.store.close()
        self.db.__exit__(None,None,None)

    def observe(self,resources,**extra):
        return self.server.call_tool('athena_worker_cost_observe',{'worker_id':'w','task_id':'t','resources':resources,**extra})

    def test_missing_constrained_measurement_does_not_mint_efficiency(self):
        result=self.observe({'cpu_time_s':10},budget={'tokens':100},useful_output=1)
        self.assertIsNone(result['budget_pressure'])
        self.assertIsNone(result['efficiency'])

    def test_each_resource_uses_only_its_observed_sample_count_after_restart(self):
        self.observe({'cpu_time_s':10})
        self.observe({'tokens':100})
        self.observe({'cpu_time_s':20})
        self.server.store.close()
        self.server=Server(self.path.name)
        p=self.server.collective_ecology._worker_profile({'id':'w'},'global')
        self.assertEqual(p['estimate'],{'cpu_time_s':15.0,'tokens':100.0})
        self.assertEqual(p['resource_observation_counts'],{'cpu_time_s':2,'tokens':1})

    def test_legacy_stored_free_pressure_does_not_pollute_profile(self):
        self.observe({'cpu_time_s':10},budget={'tokens':100},useful_output=1)
        with self.server.store.db:
            self.server.store.db.execute('UPDATE collective_worker_cost_observations SET pressure=0,efficiency=1')
            self.server.store.db.execute('UPDATE collective_worker_cost_stats SET efficiency_sum=1,efficiency_n=1')
        p=self.server.collective_ecology._worker_profile({'id':'w'},'global')
        self.assertEqual(p['efficiency'],0.5)

    def test_partial_explicit_estimates_keep_observed_other_dimensions(self):
        self.observe({'cpu_time_s':10,'tokens':100})
        p=self.server.collective_ecology._worker_profile({'id':'w','estimated_resources':{'tokens':20}},'global')
        self.assertEqual(p['estimate'],{'cpu_time_s':10.0,'tokens':20.0})
        self.assertEqual(p['cost_source'],'EXPLICIT_WITH_HISTORY')

    def test_zero_budget_is_observed_in_pressure(self):
        self.assertEqual(self.observe({'tokens':1},budget={'tokens':0})['budget_pressure'],1.0)
        self.assertEqual(self.observe({'tokens':0},budget={'tokens':0})['budget_pressure'],0.0)

    def schedule(self,name,worker,task=None,budget=None):
        args={'tasks':[task or {'id':'t','required_capabilities':['x','y']}],'workers':[worker]}
        args['remaining_budget' if name=='athena_budget_schedule' else 'budget']=budget if budget is not None else {'tokens':2}
        return self.server.call_tool(name,args)

    def test_all_scheduler_routes_reject_partial_capability_and_missing_cost(self):
        for name in ('athena_budget_schedule','athena_schedule_multiperiod','athena_schedule_certified'):
            for missing in ('capability','cost'):
                worker={'id':'w','capabilities':['x'] if missing=='capability' else ['x','y']}
                task={'id':'t','required_capabilities':['x','y']}
                if missing=='capability':
                    worker.update(estimated_resources={'tokens':1},expected_resources={'tokens':1})
                    task['resource_cost']={'tokens':1}
                out=self.schedule(name,worker,task)
                with self.subTest(name=name,missing=missing):
                    self.assertEqual(out.get('assignments',out.get('schedule')),[])

    def test_multiperiod_uses_real_history_and_preserves_budget(self):
        self.observe({'tokens':3})
        out=self.schedule('athena_schedule_multiperiod',{'id':'w','capabilities':['x','y']},budget={'tokens':4})
        self.assertEqual(out['schedule'][0]['resources'],{'tokens':3.0})
        self.assertEqual(out['schedule'][0]['cost_source'],'MEASURED_HISTORY')
        self.assertEqual(out['remaining_budget']['tokens'],1.0)

    def test_invalid_resource_numbers_and_unknown_dimensions_fail(self):
        for value in (True,-1,float('inf'),float('nan'),'5'):
            with self.subTest(value=value),self.assertRaises(ValueError): self.observe({'tokens':value})
        with self.assertRaises(ValueError): self.observe({'misspelled_tokens':1})
        with self.assertRaises(ValueError): self.schedule('athena_budget_schedule',{'id':'w'},budget={'tokens':None})

    def test_duplicate_task_or_worker_identity_cannot_collapse_capacity(self):
        for name in ('athena_budget_schedule','athena_schedule_multiperiod','athena_schedule_certified'):
            for collection in ('tasks','workers'):
                args={'tasks':[{'id':'t'}],'workers':[{'id':'w'}]}
                args[collection]*=2
                if name=='athena_budget_schedule': args['remaining_budget']={}
                with self.subTest(name=name,collection=collection),self.assertRaises(ValueError):
                    self.server.call_tool(name,args)


if __name__=='__main__': unittest.main()
