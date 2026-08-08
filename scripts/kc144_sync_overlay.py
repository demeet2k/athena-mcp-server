#!/usr/bin/env python3
"""Apply the semantic KC144 overlay after merging the frozen AOR/Collective base.

This bootstrap script is intentionally exact-string and fail-closed. It patches
only the known upstream V5/V6 composition omission and the hub test assertions
that became stale when PROMOTION.1 entered the live unified surface.
"""
from __future__ import annotations

import json
from pathlib import Path


def replace_exact(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected exactly one replacement target, observed {count}")
    path.write_text(text.replace(old, new))


def patch_server() -> None:
    path = Path("athena_mcp/server.py")

    replace_exact(
        path,
        "from .collective_learning import CollectiveLearningRuntime\n"
        "from .collective_ecology import CollectiveEcologyRuntime\n"
        "from .collective_v3_dispatch import call as call_collective_v3\n"
        "from .collective_v4_dispatch import call as call_collective_v4\n",
        "from .collective_learning import CollectiveLearningRuntime\n"
        "from .collective_ecology import CollectiveEcologyRuntime\n"
        "from .collective_science import CollectiveScienceRuntime\n"
        "from .collective_discovery import CollectiveDiscoveryRuntime\n"
        "from .collective_v3_dispatch import call as call_collective_v3\n"
        "from .collective_v4_dispatch import call as call_collective_v4\n"
        "from .collective_v5_dispatch import call as call_collective_v5\n"
        "from .collective_v6_dispatch import call as call_collective_v6\n",
    )

    replace_exact(
        path,
        "from .collective_v3_protocol import COLLECTIVE_V3_TOOLS\n"
        "from .collective_v4_protocol import COLLECTIVE_V4_TOOLS\n"
        "from .aor_protocol import AOR_TOOLS\n",
        "from .collective_v3_protocol import COLLECTIVE_V3_TOOLS\n"
        "from .collective_v4_protocol import COLLECTIVE_V4_TOOLS\n"
        "from .collective_v5_protocol import COLLECTIVE_V5_TOOLS\n"
        "from .collective_v6_protocol import COLLECTIVE_V6_TOOLS\n"
        "from .aor_protocol import AOR_TOOLS\n",
    )

    replace_exact(
        path,
        "_existing_tool_names={t['name'] for t in TOOLS}\n"
        "for tool in COLLECTIVE_TOOLS+COLLECTIVE_GROWTH_TOOLS+COLLECTIVE_V2_TOOLS+COLLECTIVE_V3_TOOLS+COLLECTIVE_V4_TOOLS+AOR_TOOLS+BRANCH_TOOLS+AUTHORITY_TOOLS+ROBUSTNESS_TOOLS+AOR_DEVELOPMENT_TOOLS:\n"
        "    if tool['name'] not in _existing_tool_names:\n"
        "        TOOLS.append(tool);_existing_tool_names.add(tool['name'])\n"
        "COLLECTIVE_V3_NAMES={tool['name'] for tool in COLLECTIVE_V3_TOOLS}\n"
        "COLLECTIVE_V4_NAMES={tool['name'] for tool in COLLECTIVE_V4_TOOLS}\n",
        "_existing_tool_names={t['name'] for t in TOOLS}\n"
        "for tool in COLLECTIVE_TOOLS+COLLECTIVE_GROWTH_TOOLS+COLLECTIVE_V2_TOOLS+COLLECTIVE_V3_TOOLS+COLLECTIVE_V4_TOOLS+COLLECTIVE_V5_TOOLS+COLLECTIVE_V6_TOOLS+AOR_TOOLS+BRANCH_TOOLS+AUTHORITY_TOOLS+ROBUSTNESS_TOOLS+AOR_DEVELOPMENT_TOOLS:\n"
        "    if tool['name'] not in _existing_tool_names:\n"
        "        TOOLS.append(tool);_existing_tool_names.add(tool['name'])\n"
        "COLLECTIVE_V3_NAMES={tool['name'] for tool in COLLECTIVE_V3_TOOLS}\n"
        "COLLECTIVE_V4_NAMES={tool['name'] for tool in COLLECTIVE_V4_TOOLS}\n"
        "COLLECTIVE_V5_NAMES={tool['name'] for tool in COLLECTIVE_V5_TOOLS}\n"
        "COLLECTIVE_V6_NAMES={tool['name'] for tool in COLLECTIVE_V6_TOOLS}\n",
    )

    replace_exact(
        path,
        "        self.collective_learning=CollectiveLearningRuntime(self.store,self.collective,self.collective_memory)\n"
        "        self.collective_ecology=CollectiveEcologyRuntime(self.store,self.collective,self.collective_growth,self.collective_memory,self.collective_learning)\n"
        "        self.branches=BranchLedger(self.core);self.authority=AuthorityLedger(self.core);self.orchestration=AuthorityOrchestrationRuntime(self.core,self.branches,self.authority)\n",
        "        self.collective_learning=CollectiveLearningRuntime(self.store,self.collective,self.collective_memory)\n"
        "        self.collective_ecology=CollectiveEcologyRuntime(self.store,self.collective,self.collective_growth,self.collective_memory,self.collective_learning)\n"
        "        self.collective_science=CollectiveScienceRuntime(self.store,self.collective,self.collective_growth,self.collective_memory,self.collective_learning,self.collective_ecology)\n"
        "        self.collective_discovery=CollectiveDiscoveryRuntime(self.collective_science)\n"
        "        self.branches=BranchLedger(self.core);self.authority=AuthorityLedger(self.core);self.orchestration=AuthorityOrchestrationRuntime(self.core,self.branches,self.authority)\n",
    )

    replace_exact(
        path,
        "        if name=='athena_topology_project_jspace':return self._project_topology_to_jspace(a)\n"
        "        if name in COLLECTIVE_V4_NAMES:return call_collective_v4(self.collective_ecology,name,a)\n"
        "        if name=='athena_benchmark':\n",
        "        if name=='athena_topology_project_jspace':return self._project_topology_to_jspace(a)\n"
        "        if name in COLLECTIVE_V4_NAMES:return call_collective_v4(self.collective_ecology,name,a)\n"
        "        if name in COLLECTIVE_V5_NAMES:return call_collective_v5(self.collective_science,c,name,a)\n"
        "        if name in COLLECTIVE_V6_NAMES:return call_collective_v6(self.collective_discovery,name,a)\n"
        "        if name=='athena_benchmark':\n",
    )

    replace_exact(
        path,
        "r['collective_memory']=self.collective_memory.describe();r['collective_learning']=self.collective_learning.describe();r['collective_ecology']=self.collective_ecology.describe();r['aor_law']=orchestration_law()['version'];return r",
        "r['collective_memory']=self.collective_memory.describe();r['collective_learning']=self.collective_learning.describe();r['collective_ecology']=self.collective_ecology.describe();r['collective_science']=self.collective_science.describe();r['collective_discovery']=self.collective_discovery.describe();r['aor_law']=orchestration_law()['version'];return r",
    )

    source = path.read_text()
    compile(source, str(path), "exec")
    for token in (
        "COLLECTIVE_V5_NAMES",
        "COLLECTIVE_V6_NAMES",
        "call_collective_v5(self.collective_science,c,name,a)",
        "call_collective_v6(self.collective_discovery,name,a)",
    ):
        if token not in source:
            raise RuntimeError(f"server composition token missing after patch: {token}")


def patch_hub_test() -> None:
    path = Path("tests/test_hub_server.py")
    replace_exact(
        path,
        '            self.assertNotIn("athena_promotion_evaluate", names)\n',
        '            self.assertIn("athena_promotion_evaluate", names)\n',
    )
    replace_exact(
        path,
        '            self.assertNotIn("athena://promotion", uris)\n',
        '            self.assertIn("athena://promotion", uris)\n',
    )
    replace_exact(
        path,
        '            self.assertFalse(overlay["ORGAN.PROMOTION1"]["surface_pass"])\n',
        '            self.assertTrue(overlay["ORGAN.PROMOTION1"]["surface_pass"])\n',
    )
    compile(path.read_text(), str(path), "exec")


def main() -> None:
    patch_server()
    patch_hub_test()
    print(json.dumps({
        "status": "PASS",
        "patch": "ATHENA.KC144.BASE.SYNC.OVERLAY.1",
        "server_routes": ["COLLECTIVE_V5", "COLLECTIVE_V6"],
        "hub_truth_update": "PROMOTION1_LIVE_COMPOSED",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
