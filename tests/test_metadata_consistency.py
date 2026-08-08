import tempfile
import tomllib
import unittest
from pathlib import Path

from athena_mcp.protocol import SERVER_INFO
from athena_mcp.server import Server


class MetadataConsistencyTests(unittest.TestCase):
    def test_package_and_server_versions_match(self):
        root=Path(__file__).resolve().parents[1]
        project=tomllib.loads((root/'pyproject.toml').read_text())['project']
        self.assertEqual(project['version'],SERVER_INFO['version'])
        self.assertEqual(project['name'],SERVER_INFO['name'])
        self.assertEqual(project['version'],'2.3.0')

    def test_v4_is_exposed_by_mcp(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            init=srv.handle({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25'}})['result']
            self.assertEqual(init['serverInfo']['version'],'2.3.0')
            names={x['name'] for x in srv.handle({'jsonrpc':'2.0','id':2,'method':'tools/list'})['result']['tools']}
            self.assertIn('athena_bandit_select',names)
            self.assertIn('athena_topology_project_jspace',names)
            uris={x['uri'] for x in srv.handle({'jsonrpc':'2.0','id':3,'method':'resources/list'})['result']['resources']}
            self.assertIn('athena://collective/v4',uris)
            srv.store.close()


if __name__=='__main__': unittest.main()
