import unittest

from athena_mcp.qhug_pareto_kernel import analyze_kernel,solve_kernel,verify_decomposition
from athena_mcp.qhug_pareto_kernel_protocol import QHUG_PARETO_KERNEL_TOOL_NAMES,QHUG_PARETO_KERNEL_RESOURCE
from athena_mcp.qhug_pareto_kernel_surface import QhugParetoKernelSurface


PATCHES=[
 {'id':'A1','value':2,'proof_cost':1},
 {'id':'A2','value':3,'proof_cost':3},
 {'id':'A3','value':1,'proof_cost':2},
 {'id':'A4','value':1,'proof_cost':2},
 {'id':'A5','value':2,'proof_cost':1,'governance':1},
 {'id':'A6','value':1,'proof_cost':1},
 {'id':'B1','value':2,'proof_cost':1},
 {'id':'B2','value':3,'proof_cost':3},
 {'id':'B3','value':1,'proof_cost':2},
 {'id':'B4','value':1,'proof_cost':2},
 {'id':'B5','value':2,'proof_cost':1,'governance':1},
 {'id':'B7','value':1,'proof_cost':1},
 {'id':'P1','value':4,'proof_cost':3},
]
SPEC={
 'patches':PATCHES,
 'invalid':['A3','B3','B7'],
 'conflicts':[['A5','B5']],
 'dependencies':[
   {'patch':'A4','alternatives':[['A3']]},
   {'patch':'B4','alternatives':[['B3']]},
 ],
}


class QhugKernelTests(unittest.TestCase):
    def test_analyze_factorization(self):
        out=analyze_kernel(SPEC)
        self.assertEqual(out['patch_count'],13)
        self.assertEqual(out['raw_candidate_count'],8192)
        self.assertEqual(sorted(out['component_sizes']),[1,1,1,1,1,1,1,2,2,2])
        self.assertEqual(out['component_enumeration_work'],26)

    def test_governed_exact(self):
        out=solve_kernel({**SPEC,'mode':'governed','policy':{'lambda_patch':0,'mu_proof_cost':0,'nu_governance':0}})
        self.assertEqual(out['model_count'],192)
        self.assertEqual(out['optimum']['score'],17)
        self.assertEqual(out['optimum']['model_count'],2)

    def test_neutral_exact(self):
        out=solve_kernel({**SPEC,'mode':'neutral','policy':{'lambda_patch':0,'mu_proof_cost':0,'nu_governance':0}})
        self.assertEqual(out['model_count'],64)
        self.assertEqual(out['optimum']['score'],15)
        self.assertEqual(out['optimum']['model_count'],1)

    def test_decomposition_certifies_limit_component(self):
        bags=[['A1'],['A2'],['A3','A4'],['A5','B5'],['A6'],['B1'],['B2'],['B3','B4'],['B7'],['P1']]
        edges=[[i,i+1] for i in range(len(bags)-1)]
        out=verify_decomposition({**SPEC,'bags':bags,'bag_edges':edges})
        self.assertTrue(out['valid'])
        self.assertEqual(out['width_upper_bound'],1)
        self.assertEqual(out['clique_lower_bound'],1)
        self.assertTrue(out['exact_treewidth_certified'])

    def test_mcp_surface_exports_all_tools(self):
        self.assertEqual(QHUG_PARETO_KERNEL_TOOL_NAMES,{
            'athena_qhug_kernel_analyze','athena_qhug_pareto_solve','athena_qhug_decomposition_verify'
        })
        surface=QhugParetoKernelSurface()
        handled,out=surface.call_tool('athena_qhug_kernel_analyze',SPEC)
        self.assertTrue(handled)
        self.assertEqual(out['raw_candidate_count'],8192)

    def test_resource_describes_fail_closed_boundary(self):
        surface=QhugParetoKernelSurface()
        resource=surface.read_resource(QHUG_PARETO_KERNEL_RESOURCE['uri'])
        self.assertEqual(resource['version'],'QHUG.PARETO-KERNEL.23.2')
        self.assertTrue(any('verified junction' in x for x in resource['boundaries']))


if __name__=='__main__':unittest.main()
