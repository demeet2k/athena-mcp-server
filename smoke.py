import json
import os
import subprocess
import sys
import tempfile

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)
os.unlink(path)
p = subprocess.Popen(
    [sys.executable, "-m", "athena_mcp", "--db", path],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True,
)


def rpc(method, params=None, request_id=1):
    msg = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        msg["params"] = params
    p.stdin.write(json.dumps(msg) + "\n")
    p.stdin.flush()
    response = json.loads(p.stdout.readline())
    assert response.get("error") is None, response
    return response["result"]


def call(name, args, request_id):
    result = rpc(
        "tools/call",
        {"name": name, "arguments": args},
        request_id,
    )
    assert result.get("isError") is not True, result
    return result["structuredContent"]


def resource(uri, request_id):
    return json.loads(
        rpc(
            "resources/read", {"uri": uri}, request_id
        )["contents"][0]["text"]
    )


init = rpc(
    "initialize",
    {
        "protocolVersion": "2025-11-25",
        "capabilities": {},
        "clientInfo": {"name": "smoke", "version": "4"},
    },
    1,
)
assert init["serverInfo"]["version"] == "2.5.0", init
assert init["serverInfo"]["systemUpgrade"]["version"] == "ATHENA.SYSTEM.UPGRADE.1"
p.stdin.write(
    json.dumps(
        {"jsonrpc": "2.0", "method": "notifications/initialized"}
    )
    + "\n"
)
p.stdin.flush()

tools = rpc("tools/list", {}, 2)["tools"]
names = {item["name"] for item in tools}
for name in (
    "athena_orchestrate",
    "athena_cycle_start",
    "athena_self_test",
    "athena_schema_migrate",
    "athena_bayes_predict",
    "athena_experiment_design",
    "athena_ood_score",
    "athena_experiment_generate",
    "athena_causal_identify",
    "athena_dual_control_plan",
    "athena_replication_independence",
    "athena_discovery_claim_register",
    "athena_claim_register",
    "athena_finalize_output",
    "athena_system_upgrade_plan",
    "athena_system_upgrade_observe",
    "athena_system_upgrade_replay",
    "athena_system_release_certificate",
    "athena_system_release_replay",
):
    assert name in names, name

manifest = resource("athena://manifest", 3)
assert manifest["artifact"] == "ATHENA.RUNTIME.UNIFIED.3", manifest
assert "COLLECTIVE_DISCOVERY_V6" in manifest["layers"]
assert "COLLECTIVE_DUAL_CONTROL_V7" in manifest["layers"]
assert "AOR_DECISION_CORTEX" in manifest["layers"]
assert "SYSTEM_UPGRADE1_WITNESSED_CAS" in manifest["layers"]
assert "SYSTEM_RELEASE1_EXACT_HEAD_CERTIFICATE" in manifest["layers"]

upgrade_resource = resource("athena://system/upgrade", 4)
assert (
    upgrade_resource["manifest"]["version"]
    == "ATHENA.SYSTEM.UPGRADE.1"
), upgrade_resource

v5 = resource("athena://collective/v5", 5)
assert v5["runtime"]["version"] == "COLLECTIVE_RUNTIME_V5", v5
v6 = resource("athena://collective/v6", 6)
assert v6["runtime"]["version"] == "COLLECTIVE_RUNTIME_V6", v6
assert (
    v6["claim_namespace"]["discovery_shadow_prefix"]
    == "athena_discovery_claim_"
)
v7 = resource("athena://collective/v7", 7)
assert v7["runtime"]["version"] == "COLLECTIVE_RUNTIME_V7", v7
assert "plans/simulations are not execution" in v7["boundary"]

migration = call("athena_schema_migrate", {}, 8)
assert migration["status"] in {"APPLIED", "UP_TO_DATE"}, migration
health = call("athena_self_test", {"replay_limit": 5}, 9)
assert health["status"] == "PASS", health

head = "smoke-exact-head-001"
upgrade = call(
    "athena_system_upgrade_plan",
    {
        "objective": "subprocess complete-system smoke",
        "target_version": "2.6.0",
        "expected_git_head": head,
    },
    10,
)
assert upgrade["run_id"].startswith("UPGRUN."), upgrade
assert upgrade["athena_ready_local"] is True, upgrade
assert all(
    status == "PASS" for status in upgrade["gate_states"].values()
), upgrade

task_id = upgrade["frontier"]["frontier"][0]["task_id"]
observed = call(
    "athena_system_upgrade_observe",
    {
        "run_id": upgrade["run_id"],
        "task_id": task_id,
        "expected_state_digest": upgrade["state_digest"],
        "refresh_local": False,
        "witness": {
            "observed": True,
            "ref": "smoke://task-000",
            "procedure": {
                "runner": "subprocess-mcp",
                "command": "observe first ready task",
            },
            "observation": {
                "returncode": 0,
                "stdout": "PASS",
            },
            "result": "PASS",
            "independence_key": "smoke:system-upgrade",
        },
    },
    11,
)
assert observed["source_completion"]["completed"] == 1, observed
upgrade_replay = call(
    "athena_system_upgrade_replay",
    {"run_id": upgrade["run_id"]},
    12,
)
assert upgrade_replay["match"] is True, upgrade_replay

aor = call(
    "athena_orchestrate", {"seed": "SMOKE", "candidates": []}, 13
)
assert aor["run_id"].startswith("AORRUN."), aor
assert aor["next"] is None
cycle = call(
    "athena_cycle_start",
    {
        "task_ref": "task://smoke",
        "seed": "SMOKE",
        "config": {"require_hug": True},
    },
    14,
)
assert cycle["cycle_id"].startswith("CYCLE."), cycle
waiting = call(
    "athena_cycle_advance",
    {"cycle_id": cycle["cycle_id"], "max_steps": 16},
    15,
)
assert waiting["status"] == "WAITING_HUG_IMPLEMENTATION", waiting
assert waiting["phase"] == "HUG", waiting

design = call(
    "athena_experiment_design",
    {
        "hypotheses": [
            {"id": "H1", "prior": 0.5},
            {"id": "H2", "prior": 0.5},
        ],
        "experiments": [
            {
                "id": "E1",
                "positive_probability": {"H1": 0.9, "H2": 0.1},
                "ethical": True,
                "cost": 0.1,
                "risk": 0.1,
            }
        ],
        "sample_size": 10,
    },
    16,
)
assert design["decision"] == "DESIGN_ONLY"
assert design["winner"] == "E1"

causal = call(
    "athena_causal_identify",
    {
        "treatment": "T",
        "outcome": "Y",
        "edges": [
            {"src": "Z", "dst": "T"},
            {"src": "Z", "dst": "Y"},
            {"src": "T", "dst": "Y"},
        ],
        "observed_nodes": ["T", "Y", "Z"],
    },
    17,
)
assert causal["status"] == "IDENTIFIED_BACKDOOR"
assert ["Z"] in causal["minimal_adjustment_sets"]

transition = call(
    "athena_state_transition_model",
    {"action_id": "A", "context": {"x": 0.0}},
    18,
)
assert transition["status"] == "UNSEEN_ACTION", transition
dual = call(
    "athena_dual_control_plan",
    {
        "initial_context": {"x": 0.0},
        "actions": [
            {"id": "A", "base_reward": 0.4},
            {"id": "B", "base_reward": 0.6},
        ],
        "horizon": 2,
    },
    19,
)
assert dual["decision"] == "DUAL_CONTROL_PROXY_PLAN_ONLY", dual
assert dual["first_action"] in {"A", "B"}
assert "observe reality, and replan" in dual["law"]
transition_after = call(
    "athena_state_transition_model",
    {"action_id": "A", "context": {"x": 0.0}},
    20,
)
assert transition_after["status"] == "UNSEEN_ACTION", transition_after

semantic = {
    "kind": "ARTIFACT",
    "domain": "SMOKE",
    "verb": "TEST",
    "object_name": "OUTPUT",
    "method": "FINAL_EMISSION",
    "input_contract": {},
    "output_contract": {},
}
emission = call(
    "athena_finalize_output",
    {
        "semantic": semantic,
        "text": "Smoke crystal T: x maps to y.",
        "native_locator": "memory://smoke",
        "agent": "SMOKE",
        "task": "ci",
        "seq": 1,
        "math_objects": [
            {
                "kind": "OPERATOR",
                "symbol": "T",
                "latex": "T:x\\mapsto y",
            }
        ],
        "coordinates": {
            "BR21": {
                "status": "RESOLVED",
                "value": {"operator": "T"},
            }
        },
    },
    21,
)
assert emission["envelope_id"].startswith("ENV.")
assert emission["emission_mid"].startswith("MID.")
assert emission["visible_text"].startswith("⟦ATHENA::CRYSTAL::CRYS.")
assert emission["manifest"]["coordinates"]["BR21"]["status"] == "RESOLVED"
verified = call(
    "athena_verify_emission",
    {
        "envelope_id": emission["envelope_id"],
        "visible_text": emission["visible_text"],
    },
    22,
)
assert verified["verified"] is True

external = lambda kind: {
    "observed": True,
    "ref": f"{kind}://subprocess-smoke",
    "head_sha": head,
    "conclusion": "success",
}
release = call(
    "athena_system_release_certificate",
    {
        "run_id": upgrade["run_id"],
        "git_head": head,
        "ci_witness": external("ci"),
        "smoke_witness": external("smoke"),
        "require_source_completion": False,
    },
    23,
)
assert release["status"] == "QUALIFIED", release
assert release["certificate_id"].startswith("RELCERT.")
release_replay = call(
    "athena_system_release_replay",
    {"certificate_id": release["certificate_id"]},
    24,
)
assert release_replay["match"] is True, release_replay

p.terminate()
print(
    "SMOKE PASS: SYSTEM.UPGRADE.1 + RELCERT + V5 SCIENCE + V6 DISCOVERY + "
    "V7 DUAL-CONTROL + SCHEMA/SELFTEST + AOR + FAIL-CLOSED CYCLE + FINAL EMISSION"
)
