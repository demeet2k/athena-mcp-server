import importlib.util
from pathlib import Path
import unittest

import athena_mcp
from athena_mcp.server import Server
from athena_mcp.authority_server import AuthorityServer
from athena_mcp.field_server import FieldServer
from athena_mcp.stack_server import StackServer


class EntrypointTests(unittest.TestCase):
    def test_default_module_entrypoint_uses_fully_composed_field_server(self):
        root = Path(athena_mcp.__file__).parent
        text = (root / '__main__.py').read_text()
        self.assertIn('from .field_server import main', text)
        self.assertNotIn('from .authority_server import main', text)
        self.assertNotIn('from .server import main', text)

    def test_composition_lineage_preserves_compatibility_substrates(self):
        self.assertTrue(issubclass(AuthorityServer, Server))
        self.assertTrue(issubclass(FieldServer, StackServer))
        self.assertTrue(issubclass(FieldServer, AuthorityServer))
        self.assertIsNot(FieldServer, Server)

    def test_composed_server_modules_are_importable_without_running_stdio_loop(self):
        self.assertIsNotNone(importlib.util.find_spec('athena_mcp.authority_server'))
        self.assertIsNotNone(importlib.util.find_spec('athena_mcp.stack_server'))
        self.assertIsNotNone(importlib.util.find_spec('athena_mcp.field_server'))


if __name__ == '__main__':
    unittest.main()
