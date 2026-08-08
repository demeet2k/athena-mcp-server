from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from athena_mcp.git_backend import GitBackend, GitStaleHead
from athena_mcp.prompt_runtime import PromptRuntime, PROMPT_RUNTIME_TOOL_NAMES


def _run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    assert p.returncode == 0, p.stderr or p.stdout
    return p.stdout.strip()


def _write(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _brain(tmp_path: Path) -> PromptRuntime:
    root = tmp_path / "brain"
    root.mkdir()
    _run(root, "init")
    _run(root, "config", "user.name", "test")
    _run(root, "config", "user.email", "test@example.invalid")
    manifest = {
        "artifact": "ATHENA.PROMPT.RUNTIME.V1",
        "authority_ceiling": "below external authority",
        "active_state": "prompts/state/ACTIVE.json",
        "policy": "policies/PROMPT_RUNTIME.md",
        "default_profile": "MAXDEV",
        "profiles": {
            "MAXDEV": ["core", "git_organism", "crystal_navigation", "epistemic_learning", "self_engineering"],
            "BUILD": ["core", "git_organism", "epistemic_learning", "self_engineering"],
        },
        "modules": {
            "core": {"path": "prompts/ORCHESTRATION_CORE.md", "order": 0, "mandatory": True},
            "git_organism": {"path": "prompts/modules/GIT_ORGANISM.md", "order": 10, "mandatory": True},
            "crystal_navigation": {"path": "prompts/modules/CRYSTALLIZATION_NAVIGATION.md", "order": 20, "selectors": ["math", "graph"]},
            "epistemic_learning": {"path": "prompts/modules/EPISTEMIC_LEARNING.md", "order": 30, "mandatory": True},
            "self_engineering": {"path": "prompts/modules/SELF_ENGINEERING.md", "order": 40, "mandatory": True},
        },
    }
    active = {
        "artifact": "ATHENA.PROMPT.STATE.ACTIVE.V1",
        "status": "ACTIVE",
        "profile": "MAXDEV",
        "enabled_modules": list(manifest["modules"]),
        "active_scoped_overlays": [],
        "revision": 1,
    }
    _write(root, "prompts/PROMPT.manifest.json", json.dumps(manifest, indent=2))
    _write(root, "prompts/state/ACTIVE.json", json.dumps(active, indent=2))
    _write(root, "policies/PROMPT_RUNTIME.md", "POLICY\n")
    _write(root, "prompts/ORCHESTRATION_CORE.md", "CORE\n")
    _write(root, "prompts/modules/GIT_ORGANISM.md", "GIT\n")
    _write(root, "prompts/modules/CRYSTALLIZATION_NAVIGATION.md", "CRYSTAL\n")
    _write(root, "prompts/modules/EPISTEMIC_LEARNING.md", "EVIDENCE\n")
    _write(root, "prompts/modules/SELF_ENGINEERING.md", "SELF\n")
    _run(root, "add", ".")
    _run(root, "commit", "-m", "seed brain")
    return PromptRuntime(GitBackend(root))


def test_compile_is_deterministic_and_selector_expands_build(tmp_path, monkeypatch):
    monkeypatch.delenv("ATHENA_GIT_AUTOPUSH", raising=False)
    runtime = _brain(tmp_path)
    a = runtime.compile(task="implement service", profile="BUILD", include_text=True)
    b = runtime.compile(task="implement service", profile="BUILD", include_text=True)
    assert a["prompt_stack_digest"] == b["prompt_stack_digest"]
    assert a["compiled_text"] == b["compiled_text"]
    assert "crystal_navigation" not in a["selected_modules"]
    math = runtime.compile(task="deep math graph proof", profile="BUILD", include_text=False)
    assert "crystal_navigation" in math["selected_modules"]


def test_proposal_is_cas_guarded_and_does_not_auto_activate(tmp_path, monkeypatch):
    monkeypatch.delenv("ATHENA_GIT_AUTOPUSH", raising=False)
    runtime = _brain(tmp_path)
    head = runtime.git.head()
    result = runtime.propose(
        module_id="self_engineering",
        content="SELF V2\n",
        defect="repeated stale coordination",
        expected_effect="rehydrate before shared mutation",
        scope=["profile:BUILD"],
        tests=["deterministic compile"],
        falsifier="no reduction in stale actions",
        rollback="git revert candidate promotion",
        expected_git_head=head,
        actor="tester",
        profile="BUILD",
    )
    assert result["metadata"]["status"] == "CANDIDATE"
    compiled = runtime.compile(task="build", profile="BUILD", include_text=False)
    assert compiled["selected_overlays"] == []
    assert result["git"]["shared_remote"] is False


def test_stale_head_rejects_prompt_write(tmp_path, monkeypatch):
    monkeypatch.delenv("ATHENA_GIT_AUTOPUSH", raising=False)
    runtime = _brain(tmp_path)
    old = runtime.git.head()
    _write(runtime.git.root, "prompts/external.md", "new sibling state\n")
    _run(runtime.git.root, "add", ".")
    _run(runtime.git.root, "commit", "-m", "sibling change")
    with pytest.raises(GitStaleHead):
        runtime.propose(
            module_id="self_engineering",
            content="STALE\n",
            defect="x",
            expected_effect="y",
            scope=["profile:BUILD"],
            tests=["z"],
            falsifier="f",
            rollback="r",
            expected_git_head=old,
            actor="tester",
            profile="BUILD",
        )


def test_tested_candidate_can_activate_only_in_declared_scope(tmp_path, monkeypatch):
    monkeypatch.delenv("ATHENA_GIT_AUTOPUSH", raising=False)
    runtime = _brain(tmp_path)
    proposed = runtime.propose(
        module_id="self_engineering",
        content="SELF SCOPED V2\n",
        defect="build routing defect",
        expected_effect="improved build routing",
        scope=["profile:BUILD"],
        tests=["shadow build"],
        falsifier="build metric does not improve",
        rollback="remove overlay",
        expected_git_head=runtime.git.head(),
        actor="tester",
        profile="BUILD",
    )
    tested = runtime.record_experiment(
        proposed["candidate_ref"],
        runtime.git.head(),
        observed=True,
        verdict="PASS",
        observations={"verified_gain": 1.0, "baseline": 0.0},
        evidence_refs=["test://shadow-build"],
        actor="verifier",
    )
    assert tested["candidate_status"] == "TESTED"
    activated = runtime.activate(
        proposed["candidate_ref"],
        runtime.git.head(),
        scope=["profile:BUILD"],
        experiment_refs=[tested["experiment_ref"]],
        witness={"status": "PASS", "ref": "test://shadow-build"},
        actor="verifier",
    )
    build = runtime.compile(task="build service", profile="BUILD", include_text=True)
    assert activated["overlay"]["overlay_id"] in build["selected_overlays"]
    assert "SELF SCOPED V2" in build["compiled_text"]
    maxdev = runtime.compile(task="general", profile="MAXDEV", include_text=True)
    assert activated["overlay"]["overlay_id"] not in maxdev["selected_overlays"]


def test_unobserved_experiment_cannot_claim_pass(tmp_path):
    runtime = _brain(tmp_path)
    proposed = runtime.propose(
        module_id="self_engineering",
        content="SELF CANDIDATE\n",
        defect="d",
        expected_effect="e",
        scope=["profile:BUILD"],
        tests=["t"],
        falsifier="f",
        rollback="r",
        expected_git_head=runtime.git.head(),
        actor="tester",
        profile="BUILD",
    )
    with pytest.raises(ValueError, match="unobserved"):
        runtime.record_experiment(proposed["candidate_ref"], runtime.git.head(), False, "PASS", {}, [], "tester")


def test_tool_surface_contains_full_v1_mutation_membrane():
    assert {
        "athena_prompt_hydrate",
        "athena_prompt_compile",
        "athena_prompt_freshness",
        "athena_prompt_propose",
        "athena_prompt_experiment",
        "athena_prompt_activate",
        "athena_prompt_promote",
    }.issubset(PROMPT_RUNTIME_TOOL_NAMES)
