from athena_mcp.mythic_computation_protocol import MCK_RESOURCE, MCK_TOOL_NAMES
from athena_mcp.mythic_computation_runtime import MythicComputationRuntime
from athena_mcp.mythic_computation_surface import MythicComputationSurface
from athena_mcp.aor_development_surface import AOR_DEVELOPMENT_TOOL_NAMES, AOR_DEVELOPMENT_RESOURCES


def test_symbolic_address_selects_only_from_supplied_space_and_preserves_source():
    r=MythicComputationRuntime()
    p=r.symbolic_address(
        "branch reconciliation topology",
        [
            {"id":"A","terms":["oracle","sample"],"source_ref":"source://a","standing":"SOURCE_REPORTED"},
            {"id":"B","terms":["branch","topology","reconciliation"],"source_ref":"source://b","standing":"SYMBOLIC_INFERENCE"},
        ],
    )
    assert p["status"]=="ADDRESS_SELECTED"
    assert p["selected"]["id"]=="B"
    assert p["provenance"]==["source://b"]
    assert p["authority"]=="SYMBOLIC_ADDRESS_SELECTION_ONLY"


def test_symbolic_address_holds_when_nothing_matches():
    p=MythicComputationRuntime().symbolic_address(
        "unrelated query",
        [{"id":"A","terms":["xylophone"],"standing":"UNKNOWN"}],
    )
    assert p["status"]=="HOLD_NO_ADDRESS_MATCH"
    assert p["authority"]=="NONE"


def test_correspondence_route_preserves_edge_standing_and_denies_causal_authority():
    p=MythicComputationRuntime().correspondence_route(
        "a","c",
        [
            {"src":"a","dst":"b","relation":"symbolic_correspondence","standing":"SOURCE_REPORTED","source_ref":"s1"},
            {"src":"b","dst":"c","relation":"analogy","standing":"SYMBOLIC_INFERENCE","source_ref":"s2"},
        ],
    )
    assert p["status"]=="ROUTE_FOUND"
    assert p["standing_trace"]==["SOURCE_REPORTED","SYMBOLIC_INFERENCE"]
    assert p["weakest_standing"]=="SYMBOLIC_INFERENCE"
    assert p["causal_authority"] is False


def test_oracle_decode_keeps_sampler_witness_decoder_and_update_separate():
    p=MythicComputationRuntime().oracle_decode(
        "creative reframing",
        [
            {"code":"00","interpretation":"contract","standing":"SYMBOLIC_INFERENCE","source_ref":"source://0"},
            {"code":"01","interpretation":"expand","standing":"TRADITION_INTERNAL","source_ref":"source://1"},
        ],
        sample=3,
        use_case="CREATIVE",
    )
    assert p["status"]=="SYMBOLIC_GENERATION_ONLY"
    assert p["R_sampler"]["index"]==1
    assert p["W_witness"]["code"]=="01"
    assert p["D_decoder"]["interpretation"]=="expand"
    assert p["U_update"]["decision_authority"]=="NONE"


def test_protocol_machine_requires_boundary_then_phase():
    r=MythicComputationRuntime()
    assert r.protocol_machine({"authorized":False},{"ready":True},["x"])["status"]=="HOLD_BOUNDARY"
    assert r.protocol_machine({"authorized":True},{"ready":False},["x"])["status"]=="HOLD_PHASE"
    p=r.protocol_machine({"authorized":True},{"ready":True},["x","y"],witness={"result":"observed"})
    assert p["status"]=="SIMULATED_PROTOCOL"
    assert p["B_Theta_Pi_separation"] is True
    assert p["state_trace"][-1]=="CLOSED"
    assert p["execution_authority"]=="NONE"


def test_model_bridge_preserves_unmapped_residue_and_nonidentity():
    p=MythicComputationRuntime().model_bridge(
        {"alpha":1,"beta":2,"gamma":3},
        {"existing":9},
        {"alpha":"a","beta":"b"},
        invariants=["keep lineage"],
        source_ref="model://left",
        target_ref="model://right",
    )
    assert p["status"]=="BRIDGE_COMPILED"
    assert p["target_output"]["a"]==1
    assert p["unmapped_residue"]=={"gamma":3}
    assert p["identity_equivalence"] is False
    assert p["transform_loss"]


def test_epistemic_split_allows_only_witnessed_observation_promotion():
    r=MythicComputationRuntime()
    bad=r.epistemic_split(
        [{"claim":"reported","status":"SOURCE_REPORTED","source_ref":"source://x"}],
        requested_promotion="OBSERVED",
    )
    assert bad["promotion"]["status"]=="REJECTED_UNSUPPORTED_PROMOTION"
    good=r.epistemic_split(
        [{"claim":"measurement","status":"OBSERVED","witness_ref":"test://measurement"}],
        requested_promotion="OBSERVED",
    )
    assert good["promotion"]["status"]=="ALLOWED_WITHIN_DECLARED_SCOPE"


def test_surface_exposes_six_tools_and_resource_through_aor_composition():
    s=MythicComputationSurface()
    assert len(MCK_TOOL_NAMES)==6
    for name in MCK_TOOL_NAMES:
        assert name in AOR_DEVELOPMENT_TOOL_NAMES
    assert MCK_RESOURCE in AOR_DEVELOPMENT_RESOURCES
    handled,value=s.call_tool(
        "athena_mck_symbolic_address",
        {"query":"alpha","address_space":[{"id":"a","terms":["alpha"],"standing":"UNKNOWN"}]},
    )
    assert handled and value["status"]=="ADDRESS_SELECTED"
    resource=s.read_resource(MCK_RESOURCE["uri"])
    assert resource["version"]=="MCK.RUNTIME.V1"
    assert resource["benchmark"]["protected_illegal_promotions"]==0
