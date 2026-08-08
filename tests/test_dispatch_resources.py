import tempfile
import unittest
from athena_mcp.server import Server

class DispatchResourceRegressionTests(unittest.TestCase):
    def test_transform_and_collective_v3_resources_read(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            for uri in ('athena://transforms','athena://collective/v3'):
                r=srv.handle({'jsonrpc':'2.0','id':1,'method':'resources/read','params':{'uri':uri}})
                self.assertIn('result',r)
                self.assertEqual(r['result']['contents'][0]['mimeType'],'application/json')
            srv.store.close()

if __name__=='__main__': unittest.main()
