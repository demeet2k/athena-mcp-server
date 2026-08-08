import unittest

from athena_mcp.orchestration_gap.ledger import decision_digest


class GapDigestTests(unittest.TestCase):
    def base(self):
        return {
            'closure_kind':'WITNESSED_DIRECTED_REACHABILITY_NOT_LOGICAL_PROOF',
            'policy':{'traversable_relations':['derive'],'max_depth':3,'require_witness':True,'allowed_statuses':['ACTIVE']},
            'source_groups':{'S':['a']},
            'closure_nodes':['a','b'],
            'closure_paths':{
                'a':{'start':'a','origin_groups':['S'],'edges':[],'nodes':['a'],'depth':0},
                'b':{'start':'a','origin_groups':['S'],'edges':['e1'],'nodes':['a','b'],'relations':['derive'],'depth':1},
            },
            'admissible_edge_ids':['e1'],
            'rejected_edges':[],
            'covered_target_ids':['tb'],
            'gap_target_ids':[],
            'ranked_gap_ids':[],
            'grow':None,
            'measurement_plan':[],
        }

    def test_path_witness_change_changes_decision_digest_even_when_reachable_set_is_same(self):
        a=self.base();b=self.base();b['closure_paths']['b']={'start':'a','origin_groups':['S'],'edges':['e2'],'nodes':['a','b'],'relations':['bridge'],'depth':1}
        self.assertEqual(a['closure_nodes'],b['closure_nodes'])
        self.assertNotEqual(decision_digest(a),decision_digest(b))

    def test_source_group_provenance_change_changes_digest(self):
        a=self.base();b=self.base();b['source_groups']={'H':['a']};b['closure_paths']['a']['origin_groups']=['H'];b['closure_paths']['b']['origin_groups']=['H']
        self.assertNotEqual(decision_digest(a),decision_digest(b))

    def test_identical_navigation_carrier_is_stable(self):
        a=self.base();b=self.base();self.assertEqual(decision_digest(a),decision_digest(b))


if __name__=='__main__':unittest.main()
