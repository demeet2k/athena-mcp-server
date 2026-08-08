from athena_mcp.mythic_computation_runtime import MythicComputationRuntime


def test_high_stakes_oracle_use_holds_before_decode():
    r=MythicComputationRuntime()
    for use_case in ["MEDICAL","LEGAL","FINANCIAL","SAFETY_CRITICAL"]:
        p=r.oracle_decode(
            "what should I do",
            [{"code":"A","interpretation":"symbol","standing":"SYMBOLIC_INFERENCE"}],
            sample=0,
            use_case=use_case,
        )
        assert p["status"]=="HOLD_SAFETY_CRITICAL_USE"
        assert p["decision_authority"]=="NONE"


def test_symbolic_or_tradition_internal_state_cannot_drive_high_stakes_epistemic_use():
    p=MythicComputationRuntime().epistemic_split(
        [
            {"claim":"internal","status":"TRADITION_INTERNAL"},
            {"claim":"symbol","status":"SYMBOLIC_INFERENCE"},
        ],
        use_case="MEDICAL",
    )
    assert p["status"]=="HOLD_SAFETY_CRITICAL_USE"
    assert p["decision_authority"]=="NONE"


def test_source_report_is_not_observation_even_with_source_ref():
    p=MythicComputationRuntime().epistemic_split(
        [{"claim":"reported","status":"SOURCE_REPORTED","source_ref":"source://reputable"}],
        requested_promotion="OBSERVED",
    )
    assert p["promotion"]["status"]=="REJECTED_UNSUPPORTED_PROMOTION"
    assert p["promotion"]["decisions"][0]["allowed"] is False


def test_empirical_support_requires_observed_witness_and_independence():
    r=MythicComputationRuntime()
    for item in [
        {"claim":"source","status":"SOURCE_REPORTED","source_ref":"s","independent":True},
        {"claim":"obs-no-witness","status":"OBSERVED","independent":True},
        {"claim":"obs-not-independent","status":"OBSERVED","witness_ref":"w","independent":False},
    ]:
        p=r.epistemic_split([item],requested_promotion="EMPIRICAL_SUPPORT")
        assert p["promotion"]["status"]=="REJECTED_UNSUPPORTED_PROMOTION"
    good=r.epistemic_split(
        [{"claim":"obs","status":"OBSERVED","witness_ref":"w","independent":True}],
        requested_promotion="EMPIRICAL_SUPPORT",
    )
    assert good["promotion"]["status"]=="ALLOWED_WITHIN_DECLARED_SCOPE"


def test_modern_reconstruction_cannot_become_historical_primary():
    r=MythicComputationRuntime()
    modern=r.epistemic_split(
        [{
            "claim":"modern mapping",
            "status":"SOURCE_REPORTED",
            "source_ref":"source://modern",
            "provenance_type":"MODERN_RECONSTRUCTION",
        }],
        requested_promotion="HISTORICAL_PRIMARY",
    )
    assert modern["promotion"]["status"]=="REJECTED_UNSUPPORTED_PROMOTION"
    primary=r.epistemic_split(
        [{
            "claim":"primary text statement",
            "status":"SOURCE_REPORTED",
            "source_ref":"source://primary",
            "provenance_type":"PRIMARY_HISTORICAL_SOURCE",
        }],
        requested_promotion="HISTORICAL_PRIMARY",
    )
    assert primary["promotion"]["status"]=="ALLOWED_WITHIN_DECLARED_SCOPE"


def test_hazardous_protocol_classes_hold_without_compiling_steps():
    r=MythicComputationRuntime()
    for risk in ["TOXIC","HARM_DIRECTED","COERCIVE","ILLEGAL","DANGEROUS"]:
        p=r.protocol_machine({"authorized":True},{"ready":True},["do not execute"],risk_class=risk)
        assert p["status"]=="HOLD_NON_EXECUTABLE_HAZARD"
        assert p["execution_authority"]=="NONE"


def test_route_cycle_is_bounded_by_seen_set_and_depth():
    r=MythicComputationRuntime()
    p=r.correspondence_route(
        "a","z",
        [
            {"src":"a","dst":"b","relation":"r","standing":"UNKNOWN"},
            {"src":"b","dst":"a","relation":"r","standing":"UNKNOWN"},
        ],
        max_depth=4,
    )
    assert p["status"]=="HOLD_NO_ROUTE"


def test_model_bridge_does_not_drop_absent_or_unmapped_information():
    r=MythicComputationRuntime()
    p=r.model_bridge(
        {"one":1,"two":2},
        {},
        {"missing":"x","one":"one_x"},
    )
    assert p["missing_source_fields"]==["missing"]
    assert p["unmapped_residue"]=={"two":2}
    assert p["identity_equivalence"] is False
    assert "UNMAPPED != ZERO" in p["law"]


def test_synthetic_benchmark_has_zero_protected_illegal_promotions_and_full_gate_pass():
    b=MythicComputationRuntime().benchmark()
    assert b["benchmark_kind"]=="DETERMINISTIC_SYNTHETIC_REGRESSION_NOT_REAL_WORLD_EFFECTIVENESS"
    assert b["unsafe_reference_illegal_promotions"]>0
    assert b["protected_illegal_promotions"]==0
    assert b["protocol_gate_expectations_passed"]==b["protocol_gate_cases"]
    assert b["high_stakes_oracle_hold"] is True
    assert "SELF_GENERATED_BENCHMARK != INDEPENDENT_EVIDENCE" in b["laws"]
