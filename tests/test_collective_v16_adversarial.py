import unittest

from athena_mcp.collective_generalized import (
    approx_error_field,
    coupled_model_robust_policy,
    gaussian_mixture_update,
    longitudinal_dr_multistage_crossfit,
    ordered_dag_posterior,
)
from athena_mcp.collective_v16_dispatch import call


def _rows(n=120):
    return [
        {'X':(i%9)/8.0,'A1':(i//2)%2,'L1':(i//3)%2,'A2':(i//5)%2,'Y':(i//7)%2}
        for i in range(n)
    ]


class CollectiveV16AdversarialTests(unittest.TestCase):
    def test_ordered_dag_rejects_unbounded_variable_count_and_underpowered_calibration(self):
        samples=[{f'X{j}':float(i+j) for j in range(6)} for i in range(40)]
        with self.assertRaisesRegex(ValueError,'2..5 unique variables'):
            ordered_dag_posterior(samples,[f'X{j}' for j in range(6)])
        two=[{'X':float(i),'Y':float(2*i)} for i in range(40)]
        with self.assertRaisesRegex(ValueError,'at least forty externally labelled examples'):
            ordered_dag_posterior(two,['X','Y'],calibration_examples=[{'x':0.1,'y':1.0}] * 39)

    def test_multistage_rejects_future_information_and_too_many_stages(self):
        rows=_rows()
        with self.assertRaisesRegex(ValueError,'current/future treatment or outcome'):
            longitudinal_dr_multistage_crossfit(
                rows,
                [
                    {'treatment':'A1','history':['X','A2']},
                    {'treatment':'A2','history':['X','A1','L1']},
                ],
                'Y',[{'id':'p','actions':[0,0]}],
            )
        too_many=[]
        sample=[]
        for i in range(120):
            row={'X':float(i%3),'Y':i%2}
            for t in range(7):
                row[f'A{t}']=(i//(t+2))%2
            sample.append(row)
        for t in range(7):
            too_many.append({'treatment':f'A{t}','history':['X']+[f'A{j}' for j in range(t)]})
        with self.assertRaisesRegex(ValueError,'1..6 treatment stages'):
            longitudinal_dr_multistage_crossfit(sample,too_many,'Y',[{'id':'p','actions':[0]*7}])

    def test_gaussian_mixture_rejects_unknown_coefficients_non_psd_and_nonfinite(self):
        components=[
            {'id':'a','weight':0.5,'mean':[0.0,0.0],'covariance':[[1.0,0.0],[0.0,1.0]]},
            {'id':'b','weight':0.5,'mean':[1.0,1.0],'covariance':[[1.0,0.0],[0.0,1.0]]},
        ]
        with self.assertRaisesRegex(ValueError,'unknown observation coefficients'):
            gaussian_mixture_update(['X','Y'],components,{'coefficients':{'Z':1.0},'value':0.0,'noise_variance':1.0})
        bad=[
            {'id':'a','weight':0.5,'mean':[0.0,0.0],'covariance':[[1.0,2.0],[2.0,1.0]]},
            {'id':'b','weight':0.5,'mean':[1.0,1.0],'covariance':[[1.0,0.0],[0.0,1.0]]},
        ]
        with self.assertRaisesRegex(ValueError,'positive semidefinite'):
            gaussian_mixture_update(['X','Y'],bad,{'coefficients':{'X':1.0},'value':0.0,'noise_variance':1.0})
        with self.assertRaisesRegex(ValueError,'finite'):
            gaussian_mixture_update(['X','Y'],components,{'coefficients':{'X':float('nan')},'value':0.0,'noise_variance':1.0})

    def test_error_field_rejects_missing_negative_and_nonfinite_witnesses(self):
        good=[{'features':{'x':float(i)},'absolute_error':0.1} for i in range(30)]
        bad_missing=list(good);bad_missing[0]={'features':{},'absolute_error':0.1}
        with self.assertRaisesRegex(ValueError,'requires all features'):
            approx_error_field(['x'],bad_missing,[{'features':{'x':0.0}}])
        bad_negative=list(good);bad_negative[0]={'features':{'x':0.0},'absolute_error':-0.1}
        with self.assertRaisesRegex(ValueError,'nonnegative'):
            approx_error_field(['x'],bad_negative,[{'features':{'x':0.0}}])
        bad_nan=list(good);bad_nan[0]={'features':{'x':float('nan')},'absolute_error':0.1}
        with self.assertRaisesRegex(ValueError,'finite'):
            approx_error_field(['x'],bad_nan,[{'features':{'x':0.0}}])

    def test_coupled_model_policy_rejects_incomplete_transition_and_policy_surfaces(self):
        model={
            'id':'m1','weight':1.0,
            'actions_by_state':{
                'S0':[{'id':'a','reward':0.0,'transitions':{'S0':1.0}}],
                'S1':[{'id':'a','reward':0.0,'transitions':{'S0':0.5,'S1':0.5}}],
            },
        }
        model2={
            'id':'m2','weight':1.0,
            'actions_by_state':{
                'S0':[{'id':'a','reward':0.0,'transitions':{'S0':0.5,'S1':0.5}}],
                'S1':[{'id':'a','reward':0.0,'transitions':{'S0':0.5,'S1':0.5}}],
            },
        }
        policy={'id':'p','action_by_stage':{'0':{'S0':'a','S1':'a'}}}
        with self.assertRaisesRegex(ValueError,'transitions must define exactly every state'):
            coupled_model_robust_policy(['S0','S1'],'S0',[model,model2],[policy],horizon=1)
        complete={
            'id':'m1','weight':1.0,
            'actions_by_state':{
                'S0':[{'id':'a','reward':0.0,'transitions':{'S0':0.5,'S1':0.5}}],
                'S1':[{'id':'a','reward':0.0,'transitions':{'S0':0.5,'S1':0.5}}],
            },
        }
        bad_policy={'id':'p','action_by_stage':{'0':{'S0':'a'}}}
        with self.assertRaisesRegex(ValueError,'define exactly every state'):
            coupled_model_robust_policy(['S0','S1'],'S0',[complete,model2],[bad_policy],horizon=1)

    def test_dispatch_rejects_unknown_tool_instead_of_falling_through(self):
        with self.assertRaises(KeyError):
            call(None,'athena_v16_not_a_tool',{})


if __name__=='__main__':
    unittest.main()
