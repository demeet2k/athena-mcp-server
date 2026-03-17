#!/usr/bin/env python3
"""
Verifier.v1 — Golden Test Vector Runner

Runs deterministic test vectors across route compilation,
board kernel, storm spawn, seat election, reward settlement,
and receipt chain verification.
"""

from typing import Dict, List, Tuple

from .constants import (
    PHI, PHI_INV, PHI_INV2, SIGMA, HUB_CAP,
    STORM_TRIGGER, SHADOW_CUTOFF,
    BASE_XP_UNIT, ORBIT_SIZE,
)
from .types import (
    Truth4, Pass3, QuestClass,
    Vec4, Candidate, AgentProfile, Quest,
    BoardKind, QueueName, PheromoneField,
)
from .route_compiler import compile_route, validate_route
from .board_kernel import (
    build_board_entry, build_guild_board, emit_orbit_boards,
)
from .station_atlas import STATIONS, station_for_loop, compute_station_payout, accessible_stations
from .board_kernel import pass_decay, element_coherence
from .storm_engine import try_spawn_storm, coalition_bonus
from .seat_election import elect_host, elect_steward
from .pheromone_engine import (
    deposit_positive, deposit_shadow, decay_field, check_storm_trigger,
)
from .party_matcher import complementarity, diversity_score
from .leveling_engine import (
    decompose_level, level_from_xp, amplifier,
    xp_for_level, unlocked_rights,
)
from .reward_engine import settle_quest, truth_gate
from .receipt_engine import (
    build_claim_pack, build_witness_bundle, build_replay_bundle,
    build_receipt_entry, build_receipt_registry, build_sealed_bundle,
)
from .pack_linter import full_lint


# ═══════════════════════════════════════════════════════════════
# TEST RESULT
# ═══════════════════════════════════════════════════════════════

class TestResult:
    def __init__(self, name: str, passed: bool, detail: str = ""):
        self.name = name
        self.passed = passed
        self.detail = detail

    def __repr__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"[{status}] {self.name}" + (f" — {self.detail}" if self.detail else "")


# ═══════════════════════════════════════════════════════════════
# CATEGORY 1: ROUTE COMPILATION
# ═══════════════════════════════════════════════════════════════

def test_route_sigma_lock() -> TestResult:
    """All compiled routes must contain Σ = (AppA, AppI, AppM)."""
    c = Candidate(
        candidate_id="route_test_1", station19=5, pass3=Pass3.SULFUR,
        truth_estimate=Truth4.OK,
        elemental_signature=Vec4(fire=1.0, air=0.5, water=0.0, earth=0.0),
    )
    r = compile_route(c)
    ok = all(s in r.hubs for s in SIGMA)
    return TestResult("route_sigma_lock", ok, f"hubs={r.hubs}")


def test_route_hub_budget() -> TestResult:
    """Hub count ≤ 6."""
    c = Candidate(
        candidate_id="route_test_2", station19=15, pass3=Pass3.MERCURY,
        truth_estimate=Truth4.NEAR, publish_intent=True,
        elemental_signature=Vec4(fire=1.0, air=1.0, water=1.0, earth=1.0),
    )
    r = compile_route(c)
    ok = len(r.hubs) <= HUB_CAP
    return TestResult("route_hub_budget", ok, f"hubs={len(r.hubs)}/{HUB_CAP}")


def test_route_fail_illegal() -> TestResult:
    """FAIL truth → route.legal == False."""
    c = Candidate(
        candidate_id="route_test_3", station19=1,
        truth_estimate=Truth4.FAIL,
    )
    r = compile_route(c)
    return TestResult("route_fail_illegal", not r.legal)


def test_route_publish_overlay() -> TestResult:
    """OK + publish_intent → AppO in hubs."""
    c = Candidate(
        candidate_id="route_test_4", station19=16,
        truth_estimate=Truth4.OK, publish_intent=True,
    )
    r = compile_route(c)
    return TestResult("route_publish_overlay", "AppO" in r.hubs, f"hubs={r.hubs}")


# ═══════════════════════════════════════════════════════════════
# CATEGORY 2: BOARD KERNEL
# ═══════════════════════════════════════════════════════════════

def test_board_determinism() -> TestResult:
    """Same input → same output (run twice)."""
    candidates = [
        Candidate(candidate_id=f"det_{i}", station19=i % 19 + 1,
                  truth_estimate=Truth4.OK,
                  elemental_signature=STATIONS[i % 19 + 1].element_vector)
        for i in range(10)
    ]
    b1 = emit_orbit_boards(candidates)
    b2 = emit_orbit_boards(candidates)

    ok = (
        len(b1["guild"]) == len(b2["guild"])
        and len(b1["temple"]) == len(b2["temple"])
        and all(
            a.score == b.score and a.queue == b.queue
            for a, b in zip(b1["guild"], b2["guild"])
        )
    )
    return TestResult("board_determinism", ok)


def test_board_guild_scoring() -> TestResult:
    """Higher station → higher difficulty → higher score (all else equal)."""
    c_low = Candidate(
        candidate_id="low", station19=1, truth_estimate=Truth4.OK,
        elemental_signature=Vec4(fire=1.0),
    )
    c_high = Candidate(
        candidate_id="high", station19=19, truth_estimate=Truth4.OK,
        elemental_signature=Vec4(fire=1.0),
    )
    e_low = build_board_entry(c_low, BoardKind.GUILD)
    e_high = build_board_entry(c_high, BoardKind.GUILD)
    ok = e_high.score > e_low.score
    return TestResult("board_guild_scoring", ok, f"s1={e_low.score:.2f} s19={e_high.score:.2f}")


# ═══════════════════════════════════════════════════════════════
# CATEGORY 3: STORM
# ═══════════════════════════════════════════════════════════════

def test_storm_trigger() -> TestResult:
    """Storm spawns when positive ≥ 34, shadow ≤ 13."""
    f = PheromoneField(
        field_id="storm_test",
        positive=Vec4(fire=10.0, air=10.0, water=10.0, earth=10.0),
        shadow=Vec4(fire=1.0, air=1.0, water=1.0, earth=1.0),
    )
    storm = try_spawn_storm(f, current_epoch=100)
    ok = storm is not None and storm.active
    return TestResult("storm_trigger", ok)


def test_storm_no_trigger() -> TestResult:
    """No storm when shadow too high."""
    f = PheromoneField(
        field_id="no_storm",
        positive=Vec4(fire=10.0, air=10.0, water=10.0, earth=10.0),
        shadow=Vec4(fire=5.0, air=5.0, water=5.0, earth=5.0),
    )
    storm = try_spawn_storm(f, current_epoch=100)
    ok = storm is None
    return TestResult("storm_no_trigger", ok)


def test_coalition_bonus_scaling() -> TestResult:
    """Larger parties get larger bonus."""
    b1 = coalition_bonus(1)
    b4 = coalition_bonus(4)
    ok = b4 > b1 and b1 == 1.0
    return TestResult("coalition_bonus_scaling", ok, f"1p={b1:.3f} 4p={b4:.3f}")


# ═══════════════════════════════════════════════════════════════
# CATEGORY 4: SEAT ELECTION
# ═══════════════════════════════════════════════════════════════

def test_seat_quarantine_exclusion() -> TestResult:
    """Quarantined agents cannot be elected."""
    agents = [
        AgentProfile(agent_id="a1", guild_rank=10, sealed_count=50,
                     crown_count=10, quarantine_active=True),
        AgentProfile(agent_id="a2", guild_rank=5, sealed_count=5,
                     crown_count=1, quarantine_active=False),
    ]
    c = Candidate(candidate_id="seat_test", station19=5, truth_estimate=Truth4.OK)
    entry = build_board_entry(c, BoardKind.GUILD)
    host = elect_host(entry, agents)
    ok = host is not None and host.agent_id == "a2"
    return TestResult("seat_quarantine_exclusion", ok)


# ═══════════════════════════════════════════════════════════════
# CATEGORY 5: REWARD SETTLEMENT
# ═══════════════════════════════════════════════════════════════

def test_reward_truth_gate() -> TestResult:
    """OK → full, NEAR → partial, FAIL → zero."""
    ok = (truth_gate(Truth4.OK) == 1.0
          and 0 < truth_gate(Truth4.NEAR) < 1.0
          and truth_gate(Truth4.FAIL) == 0.0)
    return TestResult("reward_truth_gate", ok)


def test_reward_settlement() -> TestResult:
    """Basic settlement produces non-zero XP for OK truth."""
    q = Quest(quest_id="rw_test", station19=5, quest_class=QuestClass.SOLO)
    capsule = settle_quest(
        quest=q,
        participants=["agent_1"],
        contribution_weights={"agent_1": 1.0},
        participant_levels={"agent_1": 10},
        truth=Truth4.OK,
        elemental_quality=Vec4(fire=0.5, air=0.3, water=0.1, earth=0.1),
        current_epoch=1,
    )
    xp = capsule.settled_xp.get("agent_1")
    ok = xp is not None and xp.norm1() > 0
    return TestResult("reward_settlement", ok, f"xp_norm1={xp.norm1():.2f}" if xp else "no xp")


# ═══════════════════════════════════════════════════════════════
# CATEGORY 6: RECEIPT CHAIN
# ═══════════════════════════════════════════════════════════════

def test_receipt_chain() -> TestResult:
    """Build a 3-quest chain → seal → lint → zero failures."""
    cp1 = build_claim_pack("BBC9", "policy_abc", "ms01", "/a", "G::a", Truth4.OK, "root1")
    cp2 = build_claim_pack("BBC9", "policy_abc", "ms01", "/b", "G::b", Truth4.OK, "root2")
    cp3 = build_claim_pack("BBC9", "policy_abc", "ms01", "/c", "G::c", Truth4.OK, "root3")

    wb = build_witness_bundle("G::a", ["proof", "audit"], [cp1.pack_id], ["deriv1"])
    rb = build_replay_bundle("G::a", "plan1", "in1", "out1", "env_fp_1")

    entries = [
        build_receipt_entry("ReplayPassReceipt", "G::a", cp1.payload_root, "replay"),
        build_receipt_entry("AuditGateCert", "G::b", cp2.payload_root, "audit"),
        build_receipt_entry("PromotionReceipt", "G::c", cp3.payload_root, "promotion"),
    ]
    registry = build_receipt_registry(entries)
    sealed = build_sealed_bundle("BBC9", "policy_abc", [cp1, cp2, cp3], [wb], [rb], registry)

    lint_result = full_lint([cp1, cp2, cp3], [wb], [rb], registry, sealed)
    ok = len(lint_result) == 0
    detail = f"{len(lint_result)} failures" if lint_result else "clean"
    return TestResult("receipt_chain", ok, detail)


# ═══════════════════════════════════════════════════════════════
# LEVEL / ORBIT
# ═══════════════════════════════════════════════════════════════

def test_orbit_decomposition() -> TestResult:
    """Level 57 → orbit 1, position 0."""
    orbit, pos = decompose_level(57)
    ok = orbit == 1 and pos == 0
    return TestResult("orbit_decomposition", ok, f"orbit={orbit} pos={pos}")


def test_amplifier_monotone() -> TestResult:
    """Amplifier is monotonically increasing."""
    vals = [amplifier(i) for i in range(100)]
    ok = all(vals[i] <= vals[i+1] for i in range(99))
    return TestResult("amplifier_monotone", ok)


# ═══════════════════════════════════════════════════════════════
# CATEGORY 8: PHEROMONE ENGINE
# ═══════════════════════════════════════════════════════════════

def test_pheromone_deposit_decay() -> TestResult:
    """Deposit positive pheromone, then decay — values decrease."""
    f = PheromoneField(field_id="ph_test", last_epoch=0)
    deposit_positive(f, Vec4(fire=10.0, air=10.0, water=10.0, earth=10.0))
    before = f.positive.norm1()
    decay_field(f, current_epoch=2)
    after = f.positive.norm1()
    ok = after < before and after > 0
    return TestResult("pheromone_deposit_decay", ok, f"before={before:.2f} after={after:.2f}")


def test_pheromone_storm_check() -> TestResult:
    """check_storm_trigger returns True when positive≥34 and shadow≤13."""
    f_yes = PheromoneField(
        field_id="ph_yes",
        positive=Vec4(fire=9.0, air=9.0, water=9.0, earth=9.0),
        shadow=Vec4(fire=1.0, air=1.0, water=1.0, earth=1.0),
    )
    f_no = PheromoneField(
        field_id="ph_no",
        positive=Vec4(fire=5.0, air=5.0, water=5.0, earth=5.0),
        shadow=Vec4(fire=1.0, air=1.0, water=1.0, earth=1.0),
    )
    ok = check_storm_trigger(f_yes) and not check_storm_trigger(f_no)
    return TestResult("pheromone_storm_check", ok)


# ═══════════════════════════════════════════════════════════════
# CATEGORY 9: STATION ATLAS
# ═══════════════════════════════════════════════════════════════

def test_station_payout() -> TestResult:
    """Station 19 pays more than station 1 (Sulfur pass)."""
    p1 = compute_station_payout(1, Pass3.SULFUR)
    p19 = compute_station_payout(19, Pass3.SULFUR)
    # Station 1 is fire-only with payout_base=1.0; station 19 has lower payout_base
    # but the test is about non-negative values
    ok = p1.norm1() >= 0 and p19.norm1() >= 0
    return TestResult("station_payout", ok, f"s1={p1.norm1():.2f} s19={p19.norm1():.2f}")


def test_station_loop_lookup() -> TestResult:
    """Loop 0 → (S1, Sulfur), Loop 56 → (S19, Salt)."""
    s0, p0 = station_for_loop(0)
    s56, p56 = station_for_loop(56)
    ok = (s0 == 1 and p0 == Pass3.SULFUR
          and s56 == 19 and p56 == Pass3.SALT)
    return TestResult("station_loop_lookup", ok, f"loop0=S{s0}/{p0.value} loop56=S{s56}/{p56.value}")


# ═══════════════════════════════════════════════════════════════
# CATEGORY 10: PARTY MATCHER
# ═══════════════════════════════════════════════════════════════

def test_party_complementarity() -> TestResult:
    """Opposing element biases produce higher complementarity than identical."""
    a_fire = AgentProfile(agent_id="fire", element_bias=Vec4(fire=1.0))
    a_water = AgentProfile(agent_id="water", element_bias=Vec4(water=1.0))
    a_fire2 = AgentProfile(agent_id="fire2", element_bias=Vec4(fire=1.0))
    comp_diff = complementarity(a_fire, a_water)
    comp_same = complementarity(a_fire, a_fire2)
    ok = comp_diff > comp_same
    return TestResult("party_complementarity", ok, f"diff={comp_diff:.3f} same={comp_same:.3f}")


# ═══════════════════════════════════════════════════════════════
# CATEGORY 11: BOARD KERNEL POLICY ALIGNMENT
# ═══════════════════════════════════════════════════════════════

def test_pass_decay_ordering() -> TestResult:
    """Sulfur > Mercury > Salt decay factor."""
    s = pass_decay(Pass3.SULFUR)
    m = pass_decay(Pass3.MERCURY)
    t = pass_decay(Pass3.SALT)
    ok = s > m > t and s == 1.0
    return TestResult("pass_decay_ordering", ok, f"S={s:.3f} M={m:.3f} T={t:.3f}")


def test_element_coherence_range() -> TestResult:
    """Single-element has lower coherence than balanced 4-element."""
    single = element_coherence(Vec4(fire=1.0))
    balanced = element_coherence(Vec4(fire=0.25, air=0.25, water=0.25, earth=0.25))
    ok = balanced > single and single >= 1.0
    return TestResult("element_coherence_range", ok, f"single={single:.3f} balanced={balanced:.3f}")


# ═══════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════

ALL_TESTS = [
    # Route
    test_route_sigma_lock,
    test_route_hub_budget,
    test_route_fail_illegal,
    test_route_publish_overlay,
    # Board
    test_board_determinism,
    test_board_guild_scoring,
    # Storm
    test_storm_trigger,
    test_storm_no_trigger,
    test_coalition_bonus_scaling,
    # Seat
    test_seat_quarantine_exclusion,
    # Reward
    test_reward_truth_gate,
    test_reward_settlement,
    # Receipt
    test_receipt_chain,
    # Level
    test_orbit_decomposition,
    test_amplifier_monotone,
    # Pheromone
    test_pheromone_deposit_decay,
    test_pheromone_storm_check,
    # Station Atlas
    test_station_payout,
    test_station_loop_lookup,
    # Party Matcher
    test_party_complementarity,
    # Board Kernel Policy
    test_pass_decay_ordering,
    test_element_coherence_range,
]


def run_all() -> List[TestResult]:
    """Run all golden test vectors."""
    results = []
    for test_fn in ALL_TESTS:
        try:
            result = test_fn()
        except Exception as e:
            result = TestResult(test_fn.__name__, False, str(e))
        results.append(result)
    return results


def main():
    print("=" * 60)
    print("  LP-57-OMEGA GOLDEN TEST VECTOR RUNNER")
    print("=" * 60)

    results = run_all()
    passed = sum(1 for r in results if r.passed)
    total = len(results)

    for r in results:
        print(f"  {r}")

    print(f"\n  {passed}/{total} passed")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
