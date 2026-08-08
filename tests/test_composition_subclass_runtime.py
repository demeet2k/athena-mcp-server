import tempfile
import unittest

from athena_mcp.composition_integrity import composition_certificate
from athena_mcp.hub_server import HubServer
from athena_mcp.server import Server


class CompositionSubclassRuntimeTests(unittest.TestCase):
    def test_hub_server_subclass_is_one_canonical_runtime(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as handle:
            server=HubServer(handle.name)
            try:
                cert=composition_certificate(server,run_probes=True)
                self.assertEqual(cert['status'],'PASS',cert)
                runtime=cert['runtime_class']
                self.assertEqual(runtime['observed_mro'][:3],['HubServer','Server','object'])
                self.assertTrue(runtime['inherits_canonical_server'])
                self.assertEqual(runtime['canonical_server_mro_count'],1)
                self.assertEqual(runtime['competing_server_roots'],[])
                self.assertEqual(runtime['dispatch_ownership'],{'call_tool':True,'handle':True})
                self.assertTrue(runtime['single_composed_runtime'])
            finally:
                server.store.close()

    def test_nested_server_root_fails_closed(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as first, tempfile.NamedTemporaryFile(suffix='.db') as second:
            server=Server(first.name)
            competing=Server(second.name)
            server.competing_runtime=competing
            try:
                cert=composition_certificate(server,run_probes=False)
                self.assertEqual(cert['status'],'FAIL',cert)
                runtime=cert['runtime_class']
                self.assertFalse(runtime['single_composed_runtime'])
                self.assertEqual(runtime['competing_server_roots'],[
                    {'attribute':'competing_runtime','class':'Server'},
                ])
            finally:
                competing.store.close()
                server.store.close()


if __name__=='__main__':
    unittest.main()
