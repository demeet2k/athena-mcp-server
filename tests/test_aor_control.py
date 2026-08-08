import unittest

from athena_mcp.orchestration import compile_orchestration
from athena_mcp.orchestration_reward import reallocation_plan, reward_delta
from athena_mcp.orchestration_successor import continuation_gate, successor_packet
from athena_mcp.orchestration_test import validate_persistence_claim, validate_test_claim, validation_bundle

BASE={
    'readiness':1,'gain':2,'independence':1,'bridge':1,'cost':1,
    'delta_j':2,'information_gain':1,'option_value':1,'evidence':1,
    'connection':1,'replay':1,'navigation':1,'reconstruction':1,
    'implementation':1,'novelty':1,'duplicate':0,'fake':0,'bloat':0,
    'unsupported':0,'unhandled_contradiction':0,'coordinate_loss':0,
}

class AORControlTests(unittest.TestCase):
    def test_test_claim_is_fail_closed(self):
        missing=validate_test_claim({'procedure':'p','observation':'o','result':'r'})
        self.assertEqual(missing['status'],'BLOCKED')
        self.assertEqual(missing['missing'],['witness'])
        good=validate_test_claim({'procedure':'p','observation':'o','result':'r','witness':['W1']})
        self.assertEqual(good['status'],'PASS')
        self.assertEqual(good['witness_count'],1)

    def test_persistence_requires_commit_receipt_verify(self):
        bad=validate_persistence_claim({'persisted':True,'commit':'C','verify':'V'})
        self.assertEqual(bad['status'],'BLOCKED')
        self.assertIn('receipt',bad['missing'])
        good=validate_persistence_claim({'persisted':True,'commit':'C','receipt':'R','verify':'V','rollback':'RB'})
        self.assertEqual(good['status'],'PASS')
        self.assertTrue(good['rollback_available'])

    def test_validation_bundle_exposes_adversarial_pressure(self):
        out=validation_bundle({'unsupported':1,'unhandled_contradiction':1})
        self.assertEqual(out['status'],'PASS')
        self.assertTrue(out['adversarial']['required'])
        self.assertEqual(out['adversarial']['branches'],['main','counter','edge','fail'])
        self.assertIn('contradiction',out['adversarial']['pressure'])

    def test_compiler_rejects_higher_score_with_invalid_test(self):
        invalid={'id':'invalid-high',**{**BASE,'delta_j':20},'test':{'procedure':'p','observation':'o','result':'r'}}
        valid={'id':'valid-lower',**BASE,'test':{'procedure':'p','observation':'o','result':'r','witness':['W']}}
        out=compile_orchestration('seed',[invalid,valid])
        self.assertEqual(out['kernel'],'AOR.3.1')
        self.assertEqual(out['next']['id'],'valid-lower')
        rows={row['id']:row for row in out['frontier']}
        self.assertEqual(rows['invalid-high']['validation']['status'],'BLOCKED')
        self.assertFalse(rows['invalid-high']['rankable_successor'])
        self.assertIn('invalid-high',[row['id'] for row in out['validation_frontier']])

    def test_reallocation_keeps_hibernation_recoverable(self):
        rows=[
            {'id':'grow','allocation':['deepen','replicate','braid'],'scores':{'reward':{'status':'KNOWN','value':4}}},
            {'id':'sleep','allocation':['hibernate'],'scores':{'reward':{'status':'KNOWN','value':-2}}},
            {'id':'unknown','allocation':['measure'],'scores':{'reward':{'status':'UNKNOWN','value':None}}},
        ]
        plan=reallocation_plan(rows)
        self.assertEqual(plan['dormant'],['sleep'])
        self.assertIn('grow',plan['active'])
        self.assertIn('unknown',plan['blocked'])
        self.assertFalse(plan['laws']['hibernate_is_erase'])

    def test_reward_delta_does_not_fake_causality(self):
        d=reward_delta({'capability':1,'evidence':2},{'capability':3,'evidence':4})
        self.assertFalse(d['causal_claim'])
        self.assertEqual(d['delta']['capability'],2)
        self.assertEqual(d['status'],'PARTIAL')

    def test_successor_packet_routes_measurement_before_false_stop(self):
        p=successor_packet(None,[],[],[{'candidate':'x','missing_metrics':['option_value']}],[],[],'KC144:GID001')
        self.assertEqual(p['status'],'CONTINUE_MEASURE')
        self.assertTrue(p['continue'])
        self.assertEqual(p['counter_route']['type'],'measure')
        self.assertEqual(p['return_coordinate'],'KC144:GID001')
        self.assertFalse(continuation_gate(p,requested_complete=True)['stop_allowed'])

    def test_compiler_emits_reallocation_and_successor(self):
        strong={'id':'strong',**BASE}
        duplicate={'id':'duplicate',**{**BASE,'delta_j':0,'evidence':0,'connection':0,'replay':0,'navigation':0,'reconstruction':0,'implementation':0,'novelty':0,'duplicate':1}}
        out=compile_orchestration('seed',[strong,duplicate],[{'id':'gap','severity':2,'leverage':2,'information_gain':2,'cost':1}],{'return_coordinate':'KC144:GID009'})
        self.assertEqual(out['successor']['primary'],'strong')
        self.assertEqual(out['successor']['return_coordinate'],'KC144:GID009')
        self.assertIn('strong',out['reward_reallocation']['active'])
        self.assertIn('duplicate',out['reward_reallocation']['dormant'])
        self.assertEqual(out['successor']['status'],'CONTINUE_EXECUTE')

if __name__=='__main__':
    unittest.main()
