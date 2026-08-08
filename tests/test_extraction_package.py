from pathlib import Path
import tempfile
import unittest

import athena_mcp.orchestration_extract as extraction
from athena_mcp.core import AthenaCore
from athena_mcp.store import Store


class ExtractionPackageTests(unittest.TestCase):
    def test_public_import_resolves_to_package(self):
        path = Path(extraction.__file__)
        self.assertEqual(path.name, '__init__.py')
        self.assertEqual(path.parent.name, 'orchestration_extract')
        self.assertTrue(hasattr(extraction, 'ExtractionLedger'))
        self.assertEqual(len(extraction.TRANSFORM_ORDER), 16)

    def test_corrected_result_insert_accepts_eight_column_row(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as tmp:
            store = Store(tmp.name)
            core = AthenaCore(store)
            ledger = extraction.ExtractionLedger(core)
            task = ledger.plan('seed://sql', {'x': 1}, transforms=['formalize'])['tasks'][0]
            done = ledger.complete(
                task['task_id'],
                [{'symbols': ['x'], 'equations': ['x=1']}],
                {'verified': True, 'ref': 'sql:witness'},
            )
            self.assertEqual(done['status'], 'COMPLETED')
            self.assertEqual(len(done['result_refs']), 1)
            result = ledger.result(done['result_refs'][0])
            self.assertEqual(result['payload']['equations'], ['x=1'])
            store.close()


if __name__ == '__main__':
    unittest.main()
