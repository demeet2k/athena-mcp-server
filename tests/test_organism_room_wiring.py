import pathlib
import unittest


class OrganismRoomWiringTests(unittest.TestCase):
    def test_server_registers_room_tool(self):
        root = pathlib.Path(__file__).parents[1]
        server = (root / "athena_mcp" / "server.py").read_text(encoding="utf-8")
        self.assertIn("ORGANISM_ROOM_TOOLS", server)
        self.assertIn("OrganismRoomRuntime(MessageBoardRuntime(self.git))", server)
        self.assertIn("if name in ORGANISM_ROOM_TOOL_NAMES", server)

    def test_spec_and_runtime_share_tool_identity(self):
        root = pathlib.Path(__file__).parents[1]
        runtime = (root / "athena_mcp" / "organism_room.py").read_text(encoding="utf-8")
        spec = (root / "spec" / "ORGANISM_ROOM_V1.json").read_text(encoding="utf-8")
        self.assertIn('TOOL_NAME = "athena_organism_room"', runtime)
        self.assertIn('"runtime_tool": "athena_organism_room"', spec)


if __name__ == "__main__":
    unittest.main()
