import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveV15CalibrationGeometryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):self.server.store.close();self.tmp.close()
    def tool(self,name,args):
        self.seq+=1
        result=self.server.handle({'jsonrpc':'2.0','id':self.seq,'method':'tools/call','params':{'name':name,'arguments':args}})['result']
        self.assertFalse(result.get('isError'),result)
        return result['structuredContent']

    def test_right_continuous_step_carries_previous_knot_until_next_support(self):
        examples=[]
        examples.extend({'support':.2,'correct':0} for _ in range(20))
        examples.extend({'support':.8,'correct':1} for _ in range(20))
        out=self.tool('athena_structural_reliability_calibrate',{
            'calibration_examples':examples,
            'supports':[0,.2,.5,.799,.8,1],
            'folds':4,
            'seed':13,
        })
        values={row['support']:row['calibrated_reliability'] for row in out['calibrated_supports']}
        self.assertEqual(out['interpolation'],'RIGHT_CONTINUOUS_MONOTONE_STEP_WITH_ENDPOINT_EXTENSION')
        self.assertEqual(values[0],0)
        self.assertEqual(values[.2],0)
        self.assertEqual(values[.5],0)
        self.assertEqual(values[.799],0)
        self.assertEqual(values[.8],1)
        self.assertEqual(values[1],1)


if __name__=='__main__':unittest.main()
