from __future__ import annotations

import unittest

import athena_mcp
from athena_mcp.organism_room import ORGANISM_ROOM_TOOL_NAMES


class OrganismRoomRegistrationTests(unittest.TestCase):
    def test_tool_is_registered_once_in_protocol_and_prompt_surfaces(self):
        self.assertEqual(ORGANISM_ROOM_TOOL_NAMES, {"athena_organism_room"})
        self.assertIn("athena_organism_room", athena_mcp.PROMPT_RUNTIME_TOOL_NAMES)
        self.assertEqual(sum(tool["name"] == "athena_organism_room" for tool in athena_mcp._protocol.TOOLS), 1)


if __name__ == "__main__":
    unittest.main()
