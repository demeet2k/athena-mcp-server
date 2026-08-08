
from __future__ import annotations
import hashlib, json, unittest
from athena_mcp.campaign_v3_sibling import (
    bind_sibling_disposition, compile_pulse_with_sibling_dispositions
)
from athena_mcp.campaign_v3_ledger import LEDGER_ARTIFACT

def _sha(value):
    raw=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()

def _source():
    actions=[]
    for step in range(1,11):
        horizon="I" if step<=4 else "M" if step<=7 else "L"
        actions.append({"step":step,"horizon":horizon,"text":f"historical {step}"})
    source={
      "artifact":LEDGER_ARTIFACT,"source_issue":177,"verification_issue":185,
      "pulses":[{"pulse_index":1,"step_start":1,"step_end":10,
                 "horizon_coverage":{"I":4,"M":3,"L":3},"actions":actions}]
    }
    source["ledger_digest"]=_sha(source)
    return source

def _coord(head="H"):
    return {"git_head":head,"shared_fresh":True}

def _delta(step=1,relation="SATISFIES",head="H"):
    return {
      "target_step":step,"relation":relation,
      "source_ref":"pr#x","source_head":"S",
      "recipient_head":head,"consumed":True,
      "recipient_readback_ref":"readback#1",
      "recipient_effect_observed":True,
      "recipient_effect_ref":"effect#1",
      "reason":"current recipient observed the effect",
      "evidence_refs":["evidence#1"],
      "expected_vid":"V1","current_vid":"V1",
    }

class Tests(unittest.TestCase):
    def test_satisfies_marks_current_pulse_without_erasing_history(self):
        result=compile_pulse_with_sibling_dispositions(
          ledger_source=_source(),pulse_index=1,current_coordinates=_coord(),
          sibling_deltas=[_delta(1,"SATISFIES")],
          operational_basis={"status":"PASS","basis_digest":"B"},
        )
        self.assertEqual(result["status"],"COMPILED")
        pulse=result["pulse"]
        self.assertEqual(pulse["actions"][0]["current_state"],"SATISFIED")
        self.assertEqual(pulse["actions"][0]["text"],"historical 1")
        self.assertTrue(pulse["actions"][0]["history_preserved"])
        self.assertEqual(pulse["historical_horizon_coverage"],{"I":4,"M":3,"L":3})
        self.assertFalse(pulse["execution_authorized"])

    def test_supersedes_preserves_historical_action_and_seals_receipt(self):
        action={"step":2,"horizon":"I","text":"old route"}
        r=bind_sibling_disposition(
          pulse_action=action,current_coordinates=_coord(),
          sibling_delta=_delta(2,"SUPERSEDES")
        )
        self.assertEqual(r["status"],"BOUND")
        self.assertEqual(r["current_state"],"SUPERSEDED")
        self.assertEqual(r["source_action"],action)
        self.assertTrue(r["receipt_digest"])

    def test_delivery_or_consumption_without_effect_observation_holds(self):
        d=_delta()
        d["recipient_effect_observed"]=False
        d["recipient_effect_ref"]=""
        r=bind_sibling_disposition(
          pulse_action={"step":1,"horizon":"I","text":"x"},
          current_coordinates=_coord(),sibling_delta=d
        )
        self.assertEqual(r["status"],"HOLD_INVALID_SIBLING_EVIDENCE")
        self.assertIn("RECIPIENT_EFFECT_OBSERVATION_REQUIRED",r["failures"])
        self.assertIn("RECIPIENT_EFFECT_REF_REQUIRED",r["failures"])

    def test_stale_recipient_head_holds_batch_and_returns_no_pulse(self):
        result=compile_pulse_with_sibling_dispositions(
          ledger_source=_source(),pulse_index=1,current_coordinates=_coord("NEW"),
          sibling_deltas=[_delta(1,head="OLD")],
          operational_basis={"status":"PASS","basis_digest":"B"},
        )
        self.assertEqual(result["status"],"HOLD_INVALID_SIBLING_EVIDENCE")
        self.assertIsNone(result["pulse"])
        self.assertTrue(any("STALE_RECIPIENT_HEAD" in x for x in result["failures"]))

    def test_unfresh_shared_state_holds(self):
        coord=_coord(); coord["shared_fresh"]=False
        r=bind_sibling_disposition(
          pulse_action={"step":1,"horizon":"I","text":"x"},
          current_coordinates=coord,sibling_delta=_delta()
        )
        self.assertIn("SHARED_FRESHNESS_REQUIRED",r["failures"])

    def test_vid_drift_and_missing_pair_hold(self):
        d=_delta(); d["current_vid"]="V2"
        r=bind_sibling_disposition(
          pulse_action={"step":1,"horizon":"I","text":"x"},
          current_coordinates=_coord(),sibling_delta=d
        )
        self.assertTrue(any(x.startswith("STALE_TARGET") for x in r["failures"]))
        d=_delta(); d.pop("current_vid")
        r=bind_sibling_disposition(
          pulse_action={"step":1,"horizon":"I","text":"x"},
          current_coordinates=_coord(),sibling_delta=d
        )
        self.assertIn("VID_PAIR_REQUIRED",r["failures"])

    def test_duplicate_target_step_holds_batch(self):
        result=compile_pulse_with_sibling_dispositions(
          ledger_source=_source(),pulse_index=1,current_coordinates=_coord(),
          sibling_deltas=[_delta(1),_delta(1)],
          operational_basis={"status":"PASS","basis_digest":"B"},
        )
        self.assertEqual(result["status"],"HOLD_INVALID_SIBLING_EVIDENCE")
        self.assertIn("DUPLICATE_TARGET_STEP:1",result["failures"])
        self.assertIsNone(result["pulse"])

    def test_target_outside_pulse_holds(self):
        result=compile_pulse_with_sibling_dispositions(
          ledger_source=_source(),pulse_index=1,current_coordinates=_coord(),
          sibling_deltas=[_delta(11)],
          operational_basis={"status":"PASS","basis_digest":"B"},
        )
        self.assertIn("TARGET_STEP_OUTSIDE_PULSE:11",result["failures"])

    def test_tampered_ledger_source_holds_before_disposition(self):
        src=_source(); src["pulses"][0]["actions"][0]["text"]="tampered"
        result=compile_pulse_with_sibling_dispositions(
          ledger_source=src,pulse_index=1,current_coordinates=_coord(),
          sibling_deltas=[_delta()],
          operational_basis={"status":"PASS","basis_digest":"B"},
        )
        self.assertEqual(result["status"],"HOLD_INVALID_LEDGER_OR_PULSE_SOURCE")
        self.assertEqual(result["dispositions"],[])

    def test_multiple_valid_deltas_apply_only_named_states(self):
        result=compile_pulse_with_sibling_dispositions(
          ledger_source=_source(),pulse_index=1,current_coordinates=_coord(),
          sibling_deltas=[_delta(1,"SATISFIES"),_delta(5,"SUPERSEDES")],
          operational_basis={"status":"PASS","basis_digest":"B"},
        )
        p=result["pulse"]
        self.assertEqual(p["actions"][0]["current_state"],"SATISFIED")
        self.assertEqual(p["actions"][4]["current_state"],"SUPERSEDED")
        self.assertEqual(p["actions"][1]["current_state"],"RESIDUAL")
        self.assertEqual(result["applied_states"],{"1":"SATISFIED","5":"SUPERSEDED"})

if __name__=="__main__":
    unittest.main()
