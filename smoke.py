import json
import os
import subprocess
import sys
import tempfile

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)
os.unlink(path)
process = subprocess.Popen(
    [sys.executable, "-m", "athena_mcp", "--db", path],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True,
)


def rpc(method, params=None, request_id=1):
    message = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        message["params"] = params
    process.stdin.write(json.dumps(message) + "\n")
    process.stdin.flush()
    response = json.loads(process.stdout.readline())
    assert response.get("error") is None, response
    return response["result"]


def call(name, arguments, request_id):
    result = rpc(
        "tools/call", {"name": name, "arguments": arguments}, request_id
    )
    assert result.get("isError") is not True, result
    return result["structuredContent"]


def resource(uri, request_id):
    return json.loads(
        rpc("resources/read", {"uri": uri}, request_id)["contents"][0]["text"]
    )


try:
    init = rpc(
        "initialize",
        {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "smoke", "version": "8"},
        },
        1,
    )
    assert init["serverInfo"]["version"] == "3.1.0", init
    assert init["serverInfo"]["httpAdapter"] == "ATHENA.JSONRPC.HTTP.ADAPTER.1"
    process.stdin.write(
        json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"})
        + "\n"
    )
    process.stdin.flush()

    names = {item["name"] for item in rpc("tools/list", {}, 2)["tools"]}
    for name in (
        "athena_orchestrate",
        "athena_cycle_start",
        "athena_self_test",
        "athena_schema_migrate",
        "athena_gp_observe",
        "athena_gp_hyperfit",
        "athena_system_upgrade_plan",
        "athena_kc144_hub_validate",
        "athena_deployment_manifest",
        "athena_deployment_validate",
        "athena_deployment_activation_plan",
        "athena_deployment_assess_canary",
        "athena_finalize_output",
    ):
        assert name in names, name

    manifest = resource("athena://manifest", 3)
    assert manifest["artifact"] == "ATHENA.RUNTIME.UNIFIED.6", manifest
    for layer in (
        "COLLECTIVE_ADAPTIVE_V11",
        "KC144_TOPOLOGICAL_COMMAND_HUB",
        "SYSTEM_UPGRADE1_WITNESSED_CAS",
        "DEPLOYMENT1_DIGEST_PINNED_ACTIVATION",
    ):
        assert layer in manifest["layers"], layer
    deployment = resource("athena://deployment", 4)
    assert deployment["version"] == "ATHENA.DEPLOYMENT.1"
    assert deployment["persistence"]["mode"] == "SINGLE_WRITER"

    migration = call("athena_schema_migrate", {}, 5)
    assert migration["status"] in {"APPLIED", "UP_TO_DATE"}, migration
    health = call("athena_self_test", {"replay_limit": 5}, 6)
    assert health["status"] == "PASS", health
    hub = call("athena_kc144_hub_validate", {}, 7)
    assert hub["overall_status"] == "PASS", hub

    exact_image = "ghcr.io/demeet2k/athena-mcp-server@sha256:" + "a" * 64
    bundle = call(
        "athena_deployment_validate",
        {
            "bundle": {
                "schema": "ATHENA.DEPLOYMENT.BUNDLE.1",
                "image_ref": exact_image,
                "transport": "ATHENA.JSONRPC.HTTP.ADAPTER.1",
                "state_mode": "SINGLE_WRITER",
                "token_secret_ref": "secret://athena/token",
                "allow_insecure_http": False,
                "database_backup_witness": "backup://smoke",
            }
        },
        8,
    )
    assert bundle["status"] == "PASS", bundle
    plan = call(
        "athena_deployment_activation_plan",
        {
            "image_ref": exact_image,
            "state_snapshot_ref": "backup://smoke",
            "token_secret_ref": "secret://athena/token",
        },
        9,
    )
    assert plan["status"] == "PLAN_ONLY", plan
    canary = call(
        "athena_deployment_assess_canary",
        {
            "baseline": {"error_rate": 0.01, "p95_ms": 100, "restart_count": 0},
            "canary": {
                "error_rate": 0.01,
                "p95_ms": 105,
                "restart_count": 0,
                "ready": True,
                "schema_up_to_date": True,
                "replay_match": True,
            },
        },
        10,
    )
    assert canary["decision"] == "PROMOTE", canary

    call(
        "athena_gp_register",
        {
            "context_key": "SMOKE.GP",
            "features": ["x"],
            "length_scale": 0.7,
            "signal_variance": 1.0,
            "noise_variance": 0.02,
        },
        11,
    )
    for request_id, (x_value, target) in enumerate(
        ((-1.0, 1.0), (0.0, 0.0), (1.0, 1.0)), start=12
    ):
        evidence_ref = f"smoke://gp/{request_id}"
        observed = call(
            "athena_gp_observe",
            {
                "context_key": "SMOKE.GP",
                "features": {"x": x_value},
                "target": target,
                "evidence_ref": evidence_ref,
                "actor": "SMOKE",
            },
            request_id,
        )
        assert observed["status"] == "FIXED_KERNEL_GP_STATE", observed
        assert observed["observation_count"] == request_id - 11, observed
        assert observed["evidence_ref"] == evidence_ref, observed

    before = call("athena_gp_state", {"context_key": "SMOKE.GP"}, 15)
    assert before["observation_count"] == 3, before
    design = call(
        "athena_gp_hyperfit",
        {
            "context_key": "SMOKE.GP",
            "length_scales": [0.4, 0.7],
            "signal_variances": [1.0],
            "noise_variances": [0.02],
            "apply": False,
        },
        16,
    )
    assert design["status"] == "GP_HYPERPARAMETER_DESIGN_ONLY", design
    after = call("athena_gp_state", {"context_key": "SMOKE.GP"}, 17)
    assert before["observation_count"] == after["observation_count"]

    emission = call(
        "athena_finalize_output",
        {
            "semantic": {
                "kind": "ARTIFACT",
                "domain": "SMOKE",
                "verb": "TEST",
                "object_name": "DEPLOYMENT_OUTPUT",
                "method": "FINAL_EMISSION",
                "input_contract": {},
                "output_contract": {},
            },
            "text": "ATHENA deployment crystal smoke.",
            "native_locator": "memory://smoke/deployment",
            "agent": "SMOKE",
            "task": "ci",
            "seq": 1,
        },
        18,
    )
    assert emission["envelope_id"].startswith("ENV."), emission
    verified = call(
        "athena_verify_emission",
        {
            "envelope_id": emission["envelope_id"],
            "visible_text": emission["visible_text"],
        },
        19,
    )
    assert verified["verified"] is True
    print(
        "SMOKE PASS: V11 + KC144 + SYSTEM.UPGRADE.1 + DEPLOYMENT.1 + SECURE HTTP ADAPTER + FINAL EMISSION"
    )
finally:
    process.terminate()
    process.wait(timeout=10)
