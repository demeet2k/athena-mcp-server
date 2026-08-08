import importlib.util
from pathlib import Path
import unittest

import athena_mcp
from athena_mcp.server import Server
from athena_mcp.authority_server import AuthorityServer


class EntrypointTests(unittest.TestCase):
    def test_default_module_entrypoint_uses_authority_server(self):
        root = Path(athena_mcp.__file__).parent
        text = (root / '__main__.py').read_text()
        self.assertIn('from .authority_server import main', text)
        self.assertNotIn('from .server import main', text)

    def test_base_server_remains_available_as_compatibility_substrate(self):
        self.assertTrue(issubclass(AuthorityServer, Server))
        self.assertIsNot(AuthorityServer, Server)

    def test_authority_server_module_is_importable_without_running_stdio_loop(self):
        spec = importlib.util.find_spec('athena_mcp.authority_server')
        self.assertIsNotNone(spec)


if __name__ == '__main__':
    unittest.main()
