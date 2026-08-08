import tempfile
import unittest

from athena_mcp.composition_integrity import COMPOSITION_VERSION,EXPECTED_MRO,composition_certificate
from athena_mcp.field_server import FieldServer


class CompositionIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=FieldServer(self.tmp.name)
    def tearDown(self):
        self.server.store.close();self.tmp.close()

    def test_full_composed_runtime_passes_mro_organs_and_probes(self):
        cert=composition_certificate(self.server)
        self.assertEqual(cert['version'],COMPOSITION_VERSION)
        self.assertEqual(cert['status'],'PASS',cert)
        self.assertEqual(cert['mro']['status'],'PASS')
        self.assertEqual(cert['probe_status'],'PASS')
        self.assertEqual(cert['missing_organs'],[])
        for group,state in cert['organs'].items():self.assertEqual(state['status'],'PASS',(group,state))
        for group,state in cert['read_only_probes'].items():self.assertEqual(state['status'],'PASS',(group,state))
        observed=cert['mro']['observed']
        positions=[observed.index(name) for name in EXPECTED_MRO]
        self.assertEqual(positions,sorted(positions))

    def test_missing_organ_fails_even_when_class_mro_is_intact(self):
        original=self.server.hug;self.server.hug=None
        try:
            cert=composition_certificate(self.server,run_probes=False)
            self.assertEqual(cert['status'],'FAIL')
            self.assertIn('hug:hug',cert['missing_organs'])
            self.assertEqual(cert['organs']['hug']['status'],'FAIL')
        finally:self.server.hug=original

    def test_mro_failure_is_independent_from_surface_names(self):
        class Hollow:
            pass
        cert=composition_certificate(Hollow(),run_probes=False)
        self.assertEqual(cert['status'],'FAIL')
        self.assertEqual(cert['mro']['status'],'FAIL')
        self.assertTrue(cert['missing_organs'])

    def test_surface_audit_embeds_composition_certificate(self):
        audit=self.server.surface_audit()
        self.assertEqual(audit['status'],'PASS',audit)
        self.assertEqual(audit['surface_status'],'PASS')
        self.assertEqual(audit['composition']['status'],'PASS')
        self.assertEqual(audit['composition']['probe_status'],'PASS')

if __name__=='__main__':unittest.main()
