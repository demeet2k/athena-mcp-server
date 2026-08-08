import unittest

from athena_mcp import campaign_v3 as c

PULSE1 = """### Pulse 01 — Current HEAD / prompt hydration

0001 `[I]` Read the current shared Git HEAD before any material ATHENA action; record it as the pulse ancestry, never as world truth.
0002 `[I]` Hydrate `PROMPT.manifest.json`, ACTIVE state, policy, core, selected modules, current P0 issues, claims, sibling deltas, and target VID/OID.
0003 `[I]` Compare the hydrated frontier with the prior pulse; classify each changed coordinate and invalidate only the affected dependency cone.
0004 `[I]` Emit a compact boot receipt containing HEAD, prompt-stack identity, pressure/frontier identities, coverage, holds, and the exact next lawful action.
0005 `[M]` Engineer a deterministic hydration contract so cold agents reconstruct the same prompt ancestry without relying on prior chat memory.
0006 `[M]` Separate Git head, prompt digest, frontier digest, issue-pressure digest, target VID, and provider witness instead of hiding freshness in one hash.
0007 `[M]` Benchmark full rehydration against selective refresh; keep the cheaper route only if both yield the same decision-relevant state.
0008 `[L]` Measure how many downstream failures were caused by stale cognition rather than bad reasoning and add the result to the loop-science ledger.
0009 `[L]` Run S1 prompt self-play: baseline hydration wording versus freshness-explicit wording on the same stale-state fixtures; compare behavioral divergence.
0010 `[L]` Run the **Time-Travel Trap** game: deliberately present an attractive older state and reward the policy only if it detects and rejects the stale frontier.
"""

def contract():
    return {
        "source_issue": 177,
        "verification_issue": 185,
        "verification_comment_id": 5228358747,
        "ledger_verified": "PASS",
        "total_steps": 1000,
        "total_pulses": 100,
        "actions_per_pulse": 10,
        "horizon_totals_per_pulse": {"I":4,"M":3,"L":3},
        "ledger_digest": "ledger-digest",
        "verification_digest": "verification-digest",
    }

def boot(claim=False, status="BOOTSTRAPPED"):
    return {
        "artifact": "ATHENA.AGENT.BOOT.V1",
        "status": status,
        "prompt": {
            "git_head": "a"*40,
            "prompt_stack_digest": "p"*64,
        },
        "frontier": {
            "source_head": "b"*40,
            "frontier_digest": "f"*64,
        },
        "issue_pressure": {"digest": "i"*64},
        "contract_digest": "c"*64,
        "holds": [],
        "execution_surface": {
            "frontier_tools": ["athena_frontier_hydrate"],
            "claim_tool_exposed": claim,
            "standing": "OBSERVED_TOOL_SURFACE",
        },
    }

class CampaignV3Tests(unittest.TestCase):
    def test_parse_exact_pulse_1_grammar(self):
        rows = c.pulse_actions_from_comment(PULSE1, 1)
        self.assertEqual([x["step"] for x in rows], [f"{i:04d}" for i in range(1,11)])
        self.assertEqual([x["horizon"] for x in rows], list(c.HORIZON_PATTERN))

    def test_read_only_residual_routes_without_claim(self):
        packet = c.compile_pulse_from_comment(
            pulse_index=1,
            comment_body=PULSE1,
            ledger_contract=contract(),
            boot_packet=boot(False),
            action_effects={"0001":"READ_ONLY"},
        )
        self.assertEqual(packet["status"], "ROUTABLE_NONMUTATING")
        self.assertEqual(packet["next_action"]["step"], "0001")
        self.assertFalse(packet["execution_surface"]["claim_exposed"])

    def test_material_residual_holds_without_claim(self):
        packet = c.compile_pulse_from_comment(
            pulse_index=1,
            comment_body=PULSE1,
            ledger_contract=contract(),
            boot_packet=boot(False),
            action_effects={"0001":"MATERIAL_WRITE"},
        )
        self.assertEqual(packet["status"], "HOLD_EXECUTION_AUTHORITY")
        self.assertIn("CLAIM_EXECUTION_NOT_EXPOSED", packet["holds"])

    def test_material_residual_can_bind_only_when_observed_claim_surface(self):
        packet = c.compile_pulse_from_comment(
            pulse_index=1,
            comment_body=PULSE1,
            ledger_contract=contract(),
            boot_packet=boot(True),
            action_effects={"0001":"MATERIAL_WRITE"},
        )
        self.assertEqual(packet["status"], "READY_TO_BIND")

    def test_selective_satisfaction_preserves_historical_rows(self):
        packet = c.compile_pulse_from_comment(
            pulse_index=1,
            comment_body=PULSE1,
            ledger_contract=contract(),
            boot_packet=boot(False),
            satisfied_steps=["0001","0002"],
            superseded_steps=["0003"],
            action_effects={"0004":"READ_ONLY"},
        )
        self.assertEqual(len(packet["steps"]), 10)
        self.assertEqual(packet["steps"][0]["disposition"], "SATISFIED")
        self.assertEqual(packet["steps"][2]["disposition"], "SUPERSEDED")
        self.assertEqual(packet["next_action"]["step"], "0004")
        self.assertEqual(packet["horizon_coverage"]["I"], {
            "total":4,"satisfied":2,"superseded":1,"residual":1
        })

    def test_issue_text_never_mints_claim_authority(self):
        fake_basis = {
            "basis_digest":"x",
            "descriptors": [{
                "operation":"athena_frontier_claim",
                "capability_class":"CLAIM_EXECUTION",
                "current_exposure": False,
                "effect":"CLAIM",
            }]
        }
        packet = c.compile_pulse_from_comment(
            pulse_index=1,
            comment_body=PULSE1,
            ledger_contract=contract(),
            boot_packet=boot(False),
            action_effects={"0001":"CLAIM"},
            operational_basis=fake_basis,
        )
        self.assertEqual(packet["status"], "HOLD_EXECUTION_AUTHORITY")
        self.assertFalse(packet["execution_surface"]["claim_exposed"])

    def test_unclassified_write_surface_holds(self):
        basis = {
            "basis_digest":"x",
            "descriptors":[],
            "unclassified":[{"operation":"mystery_write","current_exposure":True,"effect":"WRITE"}],
        }
        packet = c.compile_pulse_from_comment(
            pulse_index=1, comment_body=PULSE1, ledger_contract=contract(),
            boot_packet=boot(False), action_effects={"0001":"READ_ONLY"},
            operational_basis=basis,
        )
        self.assertEqual(packet["status"], "HOLD_UNCLASSIFIED_CAPABILITY")

    def test_compile_is_deterministic_for_cold_resume_identity(self):
        kwargs = dict(
            pulse_index=1, comment_body=PULSE1, ledger_contract=contract(),
            boot_packet=boot(False), satisfied_steps=["0001"],
            action_effects={"0002":"READ_ONLY"},
            active_loop_binding={"loop_id":"RHL-X","state_digest":"s","checkpoint_head":"h"},
        )
        a = c.compile_pulse_from_comment(**kwargs)
        b = c.compile_pulse_from_comment(**kwargs)
        self.assertEqual(a["chain_digest"], b["chain_digest"])
        self.assertEqual(a["current_address"]["address_digest"], b["current_address"]["address_digest"])

    def test_liminal_coordinate_identity_stable_and_movement_exact(self):
        a = c.liminal_coordinate(
            agent_id="SOL", quest_issue=189, pulse_index=1, stage="HYDRATED",
            boot_packet=boot(False), implementation_head="m"*40,
        )
        changed_boot = boot(False)
        changed_boot["issue_pressure"]["digest"] = "j"*64
        b = c.liminal_coordinate(
            agent_id="SOL", quest_issue=189, pulse_index=1, stage="LEDGER_BOUND",
            boot_packet=changed_boot, implementation_head="n"*40,
        )
        self.assertEqual(a["coordinate_id"], b["coordinate_id"])
        self.assertEqual(a["coordinate_name"], "SOL.C189.P001")
        move = c.liminal_movement(a, b)
        self.assertEqual(move["movement"], "STATE_TRANSITION")
        self.assertEqual(
            set(move["changed_axes"]),
            {"implementation_head", "issue_pressure_digest", "stage"},
        )
        self.assertIn("athena_git_head", move["stable_axes"])

    def test_liminal_movement_rejects_different_agent_coordinate(self):
        a = c.liminal_coordinate(
            agent_id="SOL", quest_issue=189, pulse_index=1, stage="A",
            boot_packet=boot(False),
        )
        b = c.liminal_coordinate(
            agent_id="OTHER", quest_issue=189, pulse_index=1, stage="B",
            boot_packet=boot(False),
        )
        with self.assertRaisesRegex(ValueError, "same coordinate identity"):
            c.liminal_movement(a, b)

    def test_unverified_source_contract_rejected(self):
        bad = contract()
        bad["ledger_verified"] = "HOLD"
        with self.assertRaisesRegex(ValueError, "not PASS"):
            c.compile_pulse_from_comment(
                pulse_index=1, comment_body=PULSE1, ledger_contract=bad,
                boot_packet=boot(False),
            )

    def test_gap_or_wrong_horizon_rejected(self):
        bad = PULSE1.replace("0002 `[I]`", "0012 `[I]`")
        with self.assertRaises(ValueError):
            c.pulse_actions_from_comment(bad, 1)
        bad2 = PULSE1.replace("0005 `[M]`", "0005 `[L]`")
        with self.assertRaisesRegex(ValueError, "horizon grammar"):
            c.pulse_actions_from_comment(bad2, 1)

    def test_step_1000_reseeds_instead_of_completing_campaign(self):
        lines=[]
        start,end=c.expected_step_range(100)
        for offset, step in enumerate(range(start,end+1)):
            horizon=c.HORIZON_PATTERN[offset]
            lines.append(f"{step:04d} `[{horizon}]` action {step}")
        body="\n".join(lines)
        packet = c.compile_pulse_from_comment(
            pulse_index=100, comment_body=body, ledger_contract=contract(),
            boot_packet=boot(False), satisfied_steps=[f"{i:04d}" for i in range(start,end+1)],
        )
        self.assertEqual(packet["status"], "RESEED_REQUIRED")
        self.assertEqual(packet["successor"]["mode"], "REHYDRATE_RESEED")
        self.assertTrue(packet["successor"]["from_current_git"])
        self.assertNotEqual(packet["status"], "COMPLETE")

if __name__ == "__main__":
    unittest.main()
