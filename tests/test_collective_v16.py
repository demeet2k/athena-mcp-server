import math
import unittest

from athena_mcp.collective_generalized import (
    approx_error_field,
    coupled_model_robust_policy,
    gaussian_mixture_update,
    longitudinal_dr_multistage_crossfit,
    ordered_dag_posterior,
)


def _dag_rows(n=80):
    rows=[]
    for i in range(n):
        x=(i-40)/10.0
        y=1.75*x+((i%5)-2)*0.03
        rows.append({'X':x,'Y':y})
    return rows


def _longitudinal_rows(n=240):
    rows=[]
    for i in range(n):
        x=(i%11)/10.0
        a1=(i//3)%2
        l1=1 if (x+0.25*a1+((i%7)-3)*0.04) >= 0.55 else 0
        a2=(i//5)%2
        score=0.35*x+0.18*a1+0.22*l1+0.20*a2+((i%13)/13.0)*0.30
        y=1 if score >= 0.60 else 0
        rows.append({'X':x,'A1':a1,'L1':l1,'A2':a2,'Y':y})
    return rows


def _models_and_policies():
    states=['S0','S1']
    m1={
        'id':'optimistic','weight':0.5,
        'actions_by_state':{
            'S0':[
                {'id':'safe','reward':0.8,'transitions':{'S0':0.7,'S1':0.3}},
                {'id':'risk','reward':2.0,'transitions':{'S0':0.2,'S1':0.8}},
            ],
            'S1':[
                {'id':'safe','reward':0.6,'transitions':{'S0':0.4,'S1':0.6}},
                {'id':'risk','reward':1.8,'transitions':{'S0':0.1,'S1':0.9}},
            ],
        },
    }
    m2={
        'id':'adverse','weight':0.5,
        'actions_by_state':{
            'S0':[
                {'id':'safe','reward':0.7,'transitions':{'S0':0.8,'S1':0.2}},
                {'id':'risk','reward':-1.0,'transitions':{'S0':0.3,'S1':0.7}},
            ],
            'S1':[
                {'id':'safe','reward':0.5,'transitions':{'S0':0.5,'S1':0.5}},
                {'id':'risk','reward':-1.2,'transitions':{'S0':0.2,'S1':0.8}},
            ],
        },
    }
    safe={'id':'always-safe','action_by_stage':{'0':{'S0':'safe','S1':'safe'},'1':{'S0':'safe','S1':'safe'}}}
    risk={'id':'always-risk','action_by_stage':{'0':{'S0':'risk','S1':'risk'},'1':{'S0':'risk','S1':'risk'}}}
    return states,[m1,m2],[safe,risk]


class CollectiveV16ConstructiveTests(unittest.TestCase):
    def test_ordered_dag_posterior_is_normalized_and_deterministic_inside_declared_order(self):
        rows=_dag_rows()
        first=ordered_dag_posterior(rows,['X','Y'],prior_edge_probability=0.3,top_k=8)
        second=ordered_dag_posterior(rows,['X','Y'],prior_edge_probability=0.3,top_k=8)
        self.assertEqual(first,second)
        self.assertEqual(first['status'],'EXACT_ORDER_CONSTRAINED_LINEAR_GAUSSIAN_DAG_POSTERIOR')
        self.assertEqual(first['graph_count'],2)
        self.assertEqual(len(first['edges']),1)
        self.assertAlmostEqual(sum(row['posterior_weight'] for row in first['top_graphs']),1.0,places=10)
        self.assertGreaterEqual(first['edges'][0]['posterior_probability'],0.0)
        self.assertLessEqual(first['edges'][0]['posterior_probability'],1.0)
        self.assertIn('topological order',first['law'])
        self.assertIn('not general causal graph posterior',first['law'])

    def test_multistage_crossfit_is_bounded_deterministic_and_history_explicit(self):
        rows=_longitudinal_rows()
        stages=[
            {'treatment':'A1','history':['X']},
            {'treatment':'A2','history':['X','A1','L1']},
        ]
        policies=[
            {'id':'never','actions':[0,0]},
            {'id':'always','actions':[1,1]},
        ]
        first=longitudinal_dr_multistage_crossfit(rows,stages,'Y',policies,folds=3,seed=17)
        second=longitudinal_dr_multistage_crossfit(rows,stages,'Y',policies,folds=3,seed=17)
        self.assertEqual(first,second)
        self.assertEqual(first['status'],'BOUNDED_MULTISTAGE_CROSS_FITTED_SEQUENTIAL_DR')
        self.assertEqual(first['stages'],2)
        self.assertEqual(first['folds'],3)
        self.assertEqual(first['row_count'],len(rows))
        self.assertEqual(first['history_contract'][0]['available_features'],['X'])
        self.assertEqual(first['history_contract'][1]['available_features'],['X','A1','L1'])
        self.assertEqual({p['id'] for p in first['policies']},{'never','always'})
        for row in first['policies']:
            self.assertTrue(math.isfinite(row['estimated_value']))
            self.assertTrue(math.isfinite(row['standard_error']))
        self.assertIn('at most six binary treatment stages',first['law'])
        self.assertIn('not an arbitrary-horizon',first['law'])

    def test_gaussian_mixture_update_is_exact_for_supplied_finite_family(self):
        out=gaussian_mixture_update(
            ['X'],
            [
                {'id':'left','weight':0.5,'mean':[-1.0],'covariance':[[1.0]]},
                {'id':'right','weight':0.5,'mean':[1.0],'covariance':[[1.0]]},
            ],
            {'coefficients':{'X':1.0},'value':0.6,'noise_variance':0.25},
        )
        self.assertEqual(out['status'],'EXACT_FINITE_GAUSSIAN_MIXTURE_LINEAR_OBSERVATION_UPDATE')
        self.assertAlmostEqual(sum(c['posterior_weight'] for c in out['components']),1.0,places=10)
        self.assertEqual(len(out['mixture_mean']),1)
        self.assertEqual(len(out['mixture_covariance']),1)
        self.assertIn('bounded non-Gaussian family',out['law'])
        self.assertIn('not general non-Gaussian Bayes',out['law'])

    def test_error_field_uses_explicit_witnesses_and_preserves_support_geometry(self):
        witnesses=[]
        for i in range(40):
            x=i/10.0
            witnesses.append({'features':{'x':x},'absolute_error':0.1+0.02*x+0.01*((i%3)-1)})
        out=approx_error_field(
            ['x'],witnesses,
            [
                {'id':'near','features':{'x':1.25}},
                {'id':'far','features':{'x':20.0}},
            ],
            bandwidth=0.8,ridge=1e-3,folds=4,coverage=0.9,seed=3,max_support_distance=1.0,
        )
        self.assertEqual(out['status'],'CV_CALIBRATED_RBF_APPROXIMATION_ERROR_FIELD')
        self.assertEqual(out['witness_count'],40)
        by_id={row['id']:row for row in out['queries']}
        self.assertTrue(by_id['near']['within_support_radius'])
        self.assertFalse(by_id['far']['within_support_radius'])
        self.assertGreaterEqual(by_id['near']['cv_residual_upper'],by_id['near']['predicted_absolute_error'])
        self.assertIn('not a distribution-free conformal guarantee',out['law'])
        self.assertIn('unsupported/OOD geometry remains explicit',out['law'])

    def test_coupled_model_robust_policy_keeps_one_model_fixed_over_horizon(self):
        states,models,policies=_models_and_policies()
        out=coupled_model_robust_policy(states,'S0',models,policies,horizon=2,discount=1.0)
        self.assertEqual(out['status'],'EXACT_SUPPLIED_POLICY_SET_COUPLED_MODEL_FAMILY_ROBUST_EVALUATION')
        self.assertEqual(out['ambiguity'],'ONE_COMPLETE_MODEL_CHOSEN_FOR_WHOLE_HORIZON')
        self.assertEqual(out['model_count'],2)
        self.assertEqual(out['policy_count'],2)
        self.assertEqual(out['winner'],'always-safe')
        self.assertEqual({row['id'] for row in out['ranked']},{'always-safe','always-risk'})
        self.assertIn('supplied policy set',out['law'])
        self.assertIn('not general non-rectangular DRO optimization',out['law'])


if __name__=='__main__':
    unittest.main()
