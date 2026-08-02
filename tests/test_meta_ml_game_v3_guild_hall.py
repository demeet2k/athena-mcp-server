from __future__ import annotations

import json
from pathlib import Path

import pytest

from MCP.crystal_108d.meta_ml_game_v2 import FrozenMetaMLGameV2
from MCP.crystal_108d.meta_ml_game_v3 import (
    CANARY_ROLES,
    GuildHallMMLG3,
    MMLG3Error,
    SOURCE_ADAPTERS,
    register_meta_ml_game_v3,
)


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "MCP" / "data" / "meta_ml_game_v2_goal_index.json"


def digest(char: str) -> str:
    return "sha256:" + char * 64


def runtime(tmp_path: Path) -> GuildHallMMLG3:
    snapshot = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    game = FrozenMetaMLGameV2(
        snapshot,
        ledger_path=tmp_path / "mmlg2.jsonl",
    )
    return GuildHallMMLG3(
        game,
        ledger_path=tmp_path / "mmlg3.jsonl",
    )


def github_metadata() -> dict:
    return {
        "repository": "demeet2k/athena-mcp-server",
        "commit_sha": "a" * 40,
        "path": "MCP/crystal_108d/meta_ml_game_v3.py",
        "object_digest": digest("1"),
    }


def drive_metadata() -> dict:
    return {
        "file_id": "drive-file-1",
        "revision_id": "rev-7",
        "mime_type": "application/vnd.google-apps.document",
        "content_digest": digest("2"),
        "consent_basis": "user_connected_source",
    }


def mcp_metadata() -> dict:
    return {
        "endpoint_class": "local-stdio",
        "tool_or_resource": "mmlg_status",
        "receipt_hash": digest("3"),
        "output_digest": digest("4"),
    }


def website_metadata() -> dict:
    return {
        "site_id": "athenachka-web",
        "letter": "m",
        "traversal_stage": "LETTER",
        "page_digest": digest("5"),
    }


def claim(game: GuildHallMMLG3, quest: str = "MLG-G027") -> None:
    game.claim(quest, "agent-alpha", 3600, "claim-1")


def observe(
    game: GuildHallMMLG3,
    adapter: str,
    metadata: dict,
    index: int,
    quest: str = "MLG-G027",
):
    return game.ingest_observation(
        quest,
        adapter,
        f"locator://{adapter}/{index}",
        f"version-{index}",
        digest(str(index % 10)),
        "INTERNAL_DIGEST",
        metadata,
        f"observation-{index}",
    )


def votes() -> list[dict]:
    roles = sorted(CANARY_ROLES)
    return [
        {
            "role": role,
            "witness_id": f"witness-{index}",
            "authority_domain": f"authority-{index % 2}",
            "implementation_id": f"implementation-{index % 2}",
            "passed": True,
            "evidence_digest": digest(str(index + 6)),
        }
        for index, role in enumerate(roles, start=1)
    ]


def prepare_canary(game: GuildHallMMLG3):
    claim(game)
    observe(game, "github", github_metadata(), 1)
    observe(game, "mcp", mcp_metadata(), 2)
    return game.compile_canary(
        "MLG-G027",
        "episode-027",
        digest("a"),
        digest("b"),
        votes(),
        "canary-1",
    )


def test_projection_is_exact_12_by_12_and_content_addressed(tmp_path):
    game = runtime(tmp_path)
    projection = game.projection()
    assert projection["quest_count"] == 144
    assert projection["domain_count"] == 12
    assert len(projection["quests"]) == 144
    assert projection["quests"][0]["quest_id"] == "MMLG3-Q001"
    assert projection["quests"][-1]["quest_id"] == "MMLG3-Q144"
    assert projection["projection_digest"].startswith("sha256:")


def test_projection_preserves_goal_coordinates_and_methods(tmp_path):
    game = runtime(tmp_path)
    quest = game.quest("MLG-G073")
    assert quest["quest_id"] == "MMLG3-Q073"
    assert quest["coordinate"] == "D07.01"
    assert quest["learning_method"] == "contextual_bandit"
    assert quest["learnable_layer"] == "routing_priority"
    assert quest["state"] == "OPEN"


def test_list_filters_domain_state_and_adapter(tmp_path):
    game = runtime(tmp_path)
    result = game.list_quests(
        domain_id="D11",
        state="OPEN",
        source_adapter="website_letter_search",
    )
    assert result["count"] == 12
    assert {quest["domain_id"] for quest in result["quests"]} == {"D11"}


def test_claim_is_local_hash_chained_and_idempotent(tmp_path):
    game = runtime(tmp_path)
    created = game.claim("MMLG3-Q027", "agent-alpha", 3600, "claim-key")
    assert created["state"] == "CLAIMED"
    assert created["source_board_written"] is False
    assert game.verify_ledger()["events"] == 1
    with pytest.raises(MMLG3Error, match="duplicate idempotency"):
        game.claim("MLG-G028", "agent-beta", 3600, "claim-key")


def test_observation_requires_claim(tmp_path):
    game = runtime(tmp_path)
    with pytest.raises(MMLG3Error, match="state OPEN"):
        observe(game, "github", github_metadata(), 1)


@pytest.mark.parametrize(
    ("adapter", "metadata"),
    [
        ("github", github_metadata()),
        ("google_drive", drive_metadata()),
        ("mcp", mcp_metadata()),
        ("website_letter_search", website_metadata()),
    ],
)
def test_all_four_digest_only_source_adapters(adapter, metadata, tmp_path):
    game = runtime(tmp_path)
    claim(game)
    result = observe(game, adapter, metadata, 1)
    assert result["adapter"] == adapter
    assert result["raw_content_stored"] is False
    assert result["source_contact_performed"] is False
    assert result["state"] == "RUNNING"


def test_raw_or_secret_bearing_observation_metadata_is_rejected(tmp_path):
    game = runtime(tmp_path)
    claim(game)
    damaged = github_metadata()
    damaged["raw_content"] = "private document body"
    with pytest.raises(MMLG3Error, match="raw or secret"):
        observe(game, "github", damaged, 1)


def test_letter_search_plan_maps_retrieval_and_public_interface_goals(tmp_path):
    game = runtime(tmp_path)
    plan = game.letter_search_plan("m", "athenachka-web")
    assert plan["letter"] == "M"
    assert plan["goal_ids"][0] == "MLG-G027"
    assert plan["goal_ids"][1:] == [
        f"MLG-G{index:03d}" for index in range(121, 133)
    ]
    assert plan["execution_performed"] is False
    assert plan["endpoint_contacted"] is False


def test_canary_requires_two_observations_from_two_adapters(tmp_path):
    game = runtime(tmp_path)
    claim(game)
    observe(game, "github", github_metadata(), 1)
    with pytest.raises(MMLG3Error, match="two observations from two adapters"):
        game.compile_canary(
            "MLG-G027",
            "episode-027",
            digest("a"),
            digest("b"),
            votes(),
            "canary-1",
        )


def test_canary_requires_exact_independent_three_role_council(tmp_path):
    game = runtime(tmp_path)
    claim(game)
    observe(game, "github", github_metadata(), 1)
    observe(game, "mcp", mcp_metadata(), 2)
    damaged = votes()
    damaged[0]["witness_id"] = "athena-learner"
    with pytest.raises(MMLG3Error, match="independence"):
        game.compile_canary(
            "MLG-G027",
            "episode-027",
            digest("a"),
            digest("b"),
            damaged,
            "canary-1",
        )


def test_valid_canary_is_local_witness_not_external_promotion(tmp_path):
    game = runtime(tmp_path)
    canary = prepare_canary(game)
    assert canary["state"] == "WITNESSED"
    assert canary["external_promotion"] is False
    assert canary["dispatch_performed"] is False
    assert set(canary["roles"]) == CANARY_ROLES
    assert len(canary["adapter_diversity"]) == 2


def test_cross_plane_return_preserves_custody_and_never_dispatches(tmp_path):
    game = runtime(tmp_path)
    canary = prepare_canary(game)
    result = game.compile_return(
        "MLG-G027",
        "episode-027",
        canary["receipt"]["receipt_hash"],
        "return-1",
    )
    packet = result["return_packet"]
    assert result["state"] == "RETURNED"
    assert packet["dispatch_performed"] is False
    assert packet["external_promotion_authority"] is False
    assert packet["target_plane"]["repository"] == "demeet2k/Athena"
    assert packet["canary_council_receipt"] == canary["receipt"]["receipt_hash"]
    assert len(packet["observation_receipts"]) == 2


def test_return_rejects_wrong_canary_custody(tmp_path):
    game = runtime(tmp_path)
    prepare_canary(game)
    with pytest.raises(MMLG3Error, match="latest council"):
        game.compile_return(
            "MLG-G027",
            "episode-027",
            digest("f"),
            "return-1",
        )


def test_local_rollback_is_terminal_and_source_preserving(tmp_path):
    game = runtime(tmp_path)
    claim(game)
    result = game.rollback(
        "MLG-G027",
        "source revision changed",
        digest("c"),
        "rollback-1",
    )
    assert result["state"] == "ROLLED_BACK"
    assert result["guild_hall_source_mutated"] is False
    with pytest.raises(MMLG3Error, match="ROLLED_BACK"):
        game.rollback(
            "MLG-G027",
            "again",
            digest("d"),
            "rollback-2",
        )


def test_ledger_tampering_is_detected(tmp_path):
    game = runtime(tmp_path)
    claim(game)
    body = game.ledger_path.read_text(encoding="utf-8")
    game.ledger_path.write_text(
        body.replace("agent-alpha", "forged-agent"),
        encoding="utf-8",
    )
    with pytest.raises(MMLG3Error, match="hash mismatch"):
        game.verify_ledger()


def test_status_and_board_make_no_external_effect_claim(tmp_path):
    game = runtime(tmp_path)
    status = game.status()
    board = game.board_markdown()
    assert status["quests"] == 144
    assert status["guild_hall_source_board_written"] is False
    assert status["persistent_endpoint"] is False
    assert "PROJECTED_LOCAL_NOT_WRITTEN_TO_GUILD_HALL" in board
    assert board.count("MMLG3-Q") == 144


class FakeMCP:
    def __init__(self):
        self.tools = []
        self.resources = []

    def tool(self):
        def decorator(function):
            self.tools.append(function.__name__)
            return function

        return decorator

    def resource(self, uri):
        def decorator(function):
            self.resources.append((uri, function.__name__))
            return function

        return decorator


def test_registration_mounts_exactly_eleven_tools_and_four_resources(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(
        GuildHallMMLG3,
        "load",
        classmethod(lambda cls: runtime(tmp_path)),
    )
    mcp = FakeMCP()
    register_meta_ml_game_v3(mcp)
    assert mcp.tools == [
        "mmlg3_status",
        "mmlg3_quests_list",
        "mmlg3_quest_get",
        "mmlg3_quest_claim",
        "mmlg3_observation_ingest",
        "mmlg3_observations_list",
        "mmlg3_letter_search_plan",
        "mmlg3_canary_compile",
        "mmlg3_return_compile",
        "mmlg3_quest_rollback",
        "mmlg3_receipts_verify",
    ]
    assert [uri for uri, _ in mcp.resources] == [
        "athena://meta-ml-game/v3/guild-hall/projection",
        "athena://meta-ml-game/v3/guild-hall/quest-board",
        "athena://meta-ml-game/v3/source-adapters",
        "athena://meta-ml-game/v3/status",
    ]
    assert set(SOURCE_ADAPTERS) == {
        "github",
        "google_drive",
        "mcp",
        "website_letter_search",
    }
