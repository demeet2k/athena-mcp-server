from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from athena_mcp.aor_collective_transport_surface import AOR_COLLECTIVE_TRANSPORT_TOOL_NAMES
from athena_mcp.cohesion_dependency_cone import augment_dependency_cone_resource, dependency_cone
from athena_mcp.cohesion_dependency_cone_protocol import DEPENDENCY_CONE_TOOL_NAMES
from athena_mcp.cohesion_evidence_guard import CohesionEvidenceGuardRuntime
from athena_mcp.git_backend import GitBackend
from athena_mcp.message_board import MessageBoardRuntime
from athena_mcp.party_coordination_v3 import PartyCoordinationRuntimeV3


def _run(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    return proc.stdout.strip()


def _clone(remote: Path, destination: Path) -> None:
    proc = subprocess.run(["git", "clone", str(remote), str(destination)], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    _run(destination, "config", "user.name", "dependency-cone-test")
    _run(destination, "config", "user.email", "dependency-cone-test@example.invalid")


def _fixture(base: Path):
    remote = base / "origin.git"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    seed = base / "seed"; seed.mkdir(); _run(seed, "init", "-b", "master")
    _run(seed, "config", "user.name", "seed"); _run(seed, "config", "user.email", "seed@example.invalid")
    (seed / "README.md").write_text("seed\n", encoding="utf-8")
    _run(seed, "add", "."); _run(seed, "commit", "-m", "seed"); _run(seed, "remote", "add", "origin", str(remote)); _run(seed, "push", "-u", "origin", "master")
    subprocess.run(["git", "--git-dir", str(remote), "symbolic-ref", "HEAD", "refs/heads/master"], check=True, capture_output=True)
    local = base / "local"; _clone(remote, local); return remote, local


def _board_digest(root: Path) -> str:
    board = root / "runtime" / "message_board" / "v1"
    if not board.exists(): return "ABSENT"
    rows=[]
    for path in sorted(p for p in board.rglob("*") if p.is_file()): rows.append((str(path.relative_to(root)), path.read_text(encoding="utf-8")))
    return json.dumps(rows, sort_keys=True, separators=(",", ":"))


class CohesionDependencyConeTests(unittest.TestCase):
    def setUp(self):
        self._td=tempfile.TemporaryDirectory(); self.addCleanup(self._td.cleanup)
        _,self.root=_fixture(Path(self._td.name)); self.git=GitBackend(self.root); self.server=SimpleNamespace(git=self.git)
        self.board=MessageBoardRuntime(self.git); self.cohesion=CohesionEvidenceGuardRuntime(self.server); self.party=PartyCoordinationRuntimeV3(self.server)

    def cone(self,change,**kwargs):
        return dependency_cone(self.cohesion,self.party,change=change,shared_remote_mode=kwargs.pop("shared_remote_mode","REQUIRED"),**kwargs)

    def present(self,agent_id,task,work_key=None,targets=None):
        result=self.board.present(agent_id=agent_id,task=task,work_key=work_key,targets=targets); self.assertTrue(result.get("durable_return"),result); return result

    def need(self,request_id,agent_id,dependency,goal_ref="goal:consumer"):
        result=self.cohesion.request_offer(request_id,agent_id,"NEED",["capability:consumer"],goal_ref,"consumer",None,None,[dependency],None,1,1,["scope:declared"],["acceptance:done"],None,None,None,None,False,None,"origin"); self.assertTrue(result.get("durable_return"),result); return result

    def offer(self,request_id,agent_id,provided,goal_ref="goal:provider"):
        result=self.cohesion.request_offer(request_id,agent_id,"OFFER",["capability:provider"],goal_ref,"provider",None,None,None,[provided],1,1,["scope:declared"],["acceptance:done"],None,None,None,None,False,None,"origin"); self.assertTrue(result.get("durable_return"),result); return result

    @staticmethod
    def affected_ids(result):
        return {str(row["agent_id"]) for row in (result.get("directly_affected") or [])+(result.get("transitively_affected") or [])}

    def test_required_shared_freshness_failure_holds_without_mutation(self):
        _run(self.root,"remote","set-url","origin",str(self.root.parent/"missing.git")); result=self.cone({"kind":"WORK_KEY","work_key":"WK:X"})
        self.assertEqual(result["classification"],"SHARED_FRONTIER_HOLD"); self.assertFalse(result["shared_frontier_verified"]); self.assertFalse(result["mutation_performed"])

    def test_work_key_targets_only_matching_lane_and_exposes_unaffected_lane(self):
        self.present("agent-a","build parser",work_key="WK:PARSER"); self.present("agent-b","build renderer",work_key="WK:RENDERER")
        result=self.cone({"kind":"WORK_KEY","work_key":"WK:PARSER"}); self.assertEqual(self.affected_ids(result),{"agent-a"},result)
        self.assertEqual({row["agent_id"] for row in result["unaffected_observed_lanes"]},{"agent-b"}); row=result["directly_affected"][0]
        self.assertIn("EXACT_WORK_KEY",row["reason_codes"]); self.assertIn("RECHECK_CLAIM",row["required_actions"])

    def test_exact_target_affects_only_exact_claimant(self):
        self.present("agent-a","build parser",targets=["src/shared.py"]); self.present("agent-b","build renderer",targets=["src/other.py"])
        result=self.cone({"kind":"TARGET","targets":["src/shared.py"]}); self.assertEqual(self.affected_ids(result),{"agent-a"}); self.assertTrue(any("TARGET_PATH:src/shared.py" in row["reason_codes"] for row in result["directly_affected"]))

    def test_claim_id_reaches_root_claimant_and_explicit_join_descendant(self):
        leader=self.present("leader","build parser",work_key="WK:PARSER"); joined=self.board.join(agent_id="collab",join_agent_id="leader"); self.assertTrue(joined.get("durable_return"),joined)
        result=self.cone({"kind":"CLAIM","claim_id":leader["presence"]["claim_id"]}); self.assertEqual(self.affected_ids(result),{"leader","collab"},result)
        collab=next(row for row in result["directly_affected"] if row["agent_id"]=="collab"); self.assertIn("JOIN_RELATION",collab["reason_codes"])

    def test_dependency_ref_reaches_need_owner_transitively(self):
        self.present("consumer","consume artifact",work_key="WK:CONSUMER"); self.need("need-1","consumer","dep:artifact")
        result=self.cone({"kind":"DEPENDENCY","dependency_refs":["dep:artifact"]}); self.assertEqual({row["agent_id"] for row in result["transitively_affected"]},{"consumer"},result)
        row=result["transitively_affected"][0]; self.assertIn("DEPENDENCY_REF:dep:artifact",row["reason_codes"]); self.assertIn("RECHECK_DEPENDENCY",row["required_actions"])

    def test_provider_change_propagates_only_through_explicit_provides_consumes_edge(self):
        provider=self.present("provider","provide artifact",work_key="WK:PROVIDER"); self.present("consumer","consume artifact",work_key="WK:CONSUMER"); self.present("unrelated","other work",work_key="WK:OTHER")
        self.offer("offer-1","provider","dep:artifact"); self.need("need-1","consumer","dep:artifact")
        result=self.cone({"kind":"CLAIM","claim_id":provider["presence"]["claim_id"],"agent_id":"provider"})
        self.assertEqual(self.affected_ids(result),{"provider","consumer"},result); consumer=next(row for row in result["transitively_affected"] if row["agent_id"]=="consumer")
        flattened=[rel for path in consumer["propagation_paths"] for rel in path["relations"]]; self.assertIn("PROVIDES_REF",flattened); self.assertIn("DEPENDENCY_REF",flattened)
        self.assertIn("unrelated",{row["agent_id"] for row in result["unaffected_observed_lanes"]})

    def _form_party(self):
        leader=self.present("leader","lead work",work_key="WK:LEAD"); self.present("member","member work",work_key="WK:MEMBER")
        formed=self.party.form("party-1","leader",[{"goal_id":"goal:lead","required_capabilities":[]},{"goal_id":"goal:member","required_capabilities":[]}],["goal:lead"],purpose="test party"); self.assertTrue(formed.get("durable_return"),formed)
        joined=self.party.join("party-1","member",["goal:member"],"INDEPENDENT"); self.assertTrue(joined.get("durable_return"),joined)
        return leader

    def test_party_membership_alone_does_not_fan_out_but_explicit_goal_does(self):
        leader=self._form_party(); claim_change=self.cone({"kind":"CLAIM","claim_id":leader["presence"]["claim_id"],"agent_id":"leader"}); self.assertEqual(self.affected_ids(claim_change),{"leader"},claim_change)
        self.assertFalse(claim_change["parties"][0]["other_members_auto_invalidated"])
        goal_change=self.cone({"kind":"COHESION_ENTRY","goal_ref":"goal:member"}); self.assertEqual(self.affected_ids(goal_change),{"member"},goal_change)
        member=goal_change["directly_affected"][0]; self.assertIn("PARTY_GOAL_REF",member["reason_codes"]); self.assertIn("RECHECK_PARTY",member["required_actions"])

    def test_party_message_targets_explicit_recipient_and_ack_requirement_only(self):
        self._form_party(); posted=self.party.message("party-1","leader",["member"],["goal:member"],"dependency changed"); self.assertTrue(posted.get("durable_return"),posted)
        message_id=posted["message_event"]["event_id"]; result=self.cone({"kind":"MESSAGE","event_id":message_id}); self.assertEqual(self.affected_ids(result),{"member"},result)
        member=result["directly_affected"][0]; self.assertIn("READ_MESSAGE",member["required_actions"]); self.assertIn("ACK_MESSAGE",member["required_actions"])
        acked=self.board.ack(agent_id="member",message_id=message_id); self.assertTrue(acked.get("durable_return"),acked); after=self.cone({"kind":"MESSAGE","event_id":message_id}); self.assertNotIn("ACK_MESSAGE",after["directly_affected"][0]["required_actions"])

    def test_valid_git_range_computes_changed_paths_and_hits_exact_target(self):
        self.present("agent-a","owns shared file",targets=["src/shared.py"]); base=_run(self.root,"rev-parse","HEAD")
        target=self.root/"src"/"shared.py"; target.parent.mkdir(parents=True,exist_ok=True); target.write_text("v1\n",encoding="utf-8")
        _run(self.root,"add","src/shared.py"); _run(self.root,"commit","-m","change shared file"); _run(self.root,"push","origin","master"); head=_run(self.root,"rev-parse","HEAD")
        result=self.cone({"kind":"GIT_RANGE","base_ref":base,"head_ref":head}); self.assertEqual(result["change"]["changed_paths"],["src/shared.py"]); self.assertEqual(self.affected_ids(result),{"agent-a"},result)
        self.assertIn("RECHECK_GIT_HEAD",result["directly_affected"][0]["required_actions"])

    def test_git_disjoint_path_is_not_semantic_independence_proof(self):
        self.present("agent-a","owns different file",targets=["src/a.py"]); base=_run(self.root,"rev-parse","HEAD")
        path=self.root/"src"/"other.py"; path.parent.mkdir(parents=True,exist_ok=True); path.write_text("x\n",encoding="utf-8")
        _run(self.root,"add","src/other.py"); _run(self.root,"commit","-m","other file"); _run(self.root,"push","origin","master"); head=_run(self.root,"rev-parse","HEAD")
        result=self.cone({"kind":"GIT_RANGE","base_ref":base,"head_ref":head}); self.assertEqual(result["classification"],"NO_OBSERVED_LANE_HIT_WITH_UNKNOWN_SEMANTIC_RESIDUE")
        self.assertTrue(any(row["code"]=="UNOBSERVED_SEMANTIC_DEPENDENCY_POSSIBLE" for row in result["unresolved"]))

    def test_invalid_git_ref_returns_typed_hold_not_empty_diff(self):
        result=self.cone({"kind":"GIT_RANGE","base_ref":"missing-ref","head_ref":"HEAD"}); self.assertEqual(result["classification"],"GIT_REF_HOLD",result); self.assertTrue(any(row["code"]=="GIT_REF_UNAVAILABLE" for row in result["unresolved"]))

    def test_caller_supplied_edge_remains_labeled_and_can_target_lane(self):
        self.present("agent-a","explicit caller dependency"); result=self.cone({"kind":"TARGET","targets":["external:surface"]},caller_edges=[{"src":"target:external:surface","relation":"declared affects","dst":"agent:agent-a","evidence_refs":["caller://edge/1"]}])
        self.assertEqual(self.affected_ids(result),{"agent-a"},result); path=result["directly_affected"][0]["propagation_paths"][0]; self.assertIn("CALLER_SUPPLIED_EDGE",path["relations"]); self.assertIn("CALLER_SUPPLIED",path["standing"])

    def test_max_depth_truncation_preserves_unknown_residue(self):
        self.present("consumer","consume artifact"); self.need("need-1","consumer","dep:deep"); result=self.cone({"kind":"DEPENDENCY","dependency_refs":["dep:deep"]},max_depth=1)
        self.assertTrue(result["truncated"],result); self.assertTrue(any(row["code"]=="MAX_DEPTH_OR_PATH_LIMIT_REACHED" for row in result["unresolved"]))

    def test_already_fresh_call_is_read_only_and_digest_is_deterministic(self):
        self.present("agent-a","build parser",work_key="WK:PARSER"); head=_run(self.root,"rev-parse","HEAD"); before=_board_digest(self.root)
        first=self.cone({"kind":"WORK_KEY","work_key":"WK:PARSER"}); second=self.cone({"kind":"WORK_KEY","work_key":"WK:PARSER"})
        self.assertEqual(first["decision_digest"],second["decision_digest"]); self.assertEqual(_run(self.root,"rev-parse","HEAD"),head); self.assertEqual(_board_digest(self.root),before); self.assertFalse(first["mutation_performed"])

    def test_mata_absence_and_registration_resource_projection(self):
        result=self.cone({"kind":"WORK_KEY","work_key":"WK:UNKNOWN"}); self.assertFalse(result["mata"]["runtime_available"]); self.assertEqual(result["mata"]["dependency_relation"],"UNAVAILABLE_NOT_IN_RUNTIME")
        self.assertEqual(DEPENDENCY_CONE_TOOL_NAMES,{"athena_cohesion_dependency_cone"}); self.assertIn("athena_cohesion_dependency_cone",AOR_COLLECTIVE_TRANSPORT_TOOL_NAMES)
        resource=augment_dependency_cone_resource(self.cohesion.resource()); self.assertIn("athena_cohesion_dependency_cone",resource["tools"]); self.assertIn("remaining C3 steering tools 13-15",resource["residual"]); self.assertFalse(resource["targeted_invalidation"]["global_reset"])


if __name__=="__main__": unittest.main()
