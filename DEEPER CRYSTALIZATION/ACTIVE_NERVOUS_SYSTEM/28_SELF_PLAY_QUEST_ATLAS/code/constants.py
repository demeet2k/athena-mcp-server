#!/usr/bin/env python3
"""
KernelConst.v1 — LP-57Ω Canonical Constants

All numeric constants used by the quest atlas, reward kernel,
pheromone engine, leveling system, and board kernel.
"""

import math


# ═══════════════════════════════════════════════════════════════
# PHI FAMILY
# ═══════════════════════════════════════════════════════════════

PHI = (1 + math.sqrt(5)) / 2          # 1.61803398875
PHI_INV = PHI - 1                      # 0.61803398875 = 1/φ
PHI_INV2 = PHI_INV ** 2                # 0.38196601125 = φ^-2
PHI_INV3 = PHI_INV ** 3                # 0.23606797750
PHI_INV4 = PHI_INV ** 4                # 0.14589803375
PHI_INV5 = PHI_INV ** 5                # 0.09016994375
LN_PHI = math.log(PHI)                 # ~0.48121


# ═══════════════════════════════════════════════════════════════
# ORBIT / LOOP STRUCTURE
# ═══════════════════════════════════════════════════════════════

ORBIT_SIZE = 57          # total loops per orbit
STATION_COUNT = 19       # macro-levels per orbit
PASS_COUNT = 3           # alchemical passes per station
MASTER_AGENT_COUNT = 4   # A1 Synthesizer, A2 Planner, A3 Worker, A4 Pruner
SUBAGENT_BASE = 4
SUBAGENT_DIGITS = 6
SUBAGENT_CAPACITY = SUBAGENT_BASE ** SUBAGENT_DIGITS  # 4096 per master


# ═══════════════════════════════════════════════════════════════
# CRYSTAL / TILE
# ═══════════════════════════════════════════════════════════════

TILE_SIZE = 64           # base crystal tile
SYMMETRY_CELLS = 15      # |P({F,A,W,E}) \ ∅|


# ═══════════════════════════════════════════════════════════════
# ROUTE LAW
# ═══════════════════════════════════════════════════════════════

SIGMA = ("AppA", "AppI", "AppM")       # mandatory route signature
HUB_CAP = 6                            # max hubs per route

OVERLAY_MAP = {
    "OK":    None,
    "NEAR":  "AppJ",
    "AMBIG": "AppL",
    "FAIL":  "AppK",
}

PUBLISH_HUB = "AppO"                   # OK-only publish overlay

LENS_BASE = {
    "S": "AppC",   # Square
    "F": "AppE",   # Flower
    "C": "AppI",   # Cloud
    "R": "AppM",   # Fractal
}

FACET_BASE = {
    1: "AppA",
    2: "AppB",
    3: "AppH",
    4: "AppM",
}

ARC_HUB = {
    0: "AppA",
    1: "AppC",
    2: "AppE",
    3: "AppF",
    4: "AppG",
    5: "AppN",
    6: "AppP",
}


# ═══════════════════════════════════════════════════════════════
# REWARD / ECONOMY
# ═══════════════════════════════════════════════════════════════

BASE_XP_UNIT = 64
BASE_EPOCH_REWARD = 64

# Truth/ethics gate values
GAMMA_OK = 1.0
GAMMA_NEAR = PHI_INV2               # ~0.382
GAMMA_ZERO = 0.0                    # AMBIG / FAIL / ethics-fail

# Amplifier coefficients
GUILD_LAMBDA = 0.10
TEMPLE_LAMBDA = 0.15

# Difficulty coefficient
DIFFICULTY_DELTA = 0.25

# Community multiplier
COMMUNITY_BETA = 0.25

# Throughput clamp multipliers
CAPSULE_CLAMP = 16
EPOCH_CLAMP = 64

# Resonance ratio
RESONANCE_RATIO = PHI_INV           # ~0.618

# Higher phi powers (ascending scale per RewardPolicy_v1.json)
PHI2 = PHI ** 2                       # ~2.618
PHI3 = PHI ** 3                       # ~4.236
PHI4 = PHI ** 4                       # ~6.854
PHI5 = PHI ** 5                       # ~11.090

# Mint rates by quest class (ascending φ-power scale)
MINT_RATES = {
    "Solo":          1.0,             # base rate
    "Guild":         PHI,             # φ   ~1.618
    "Community":     PHI2,            # φ²  ~2.618
    "Repair":        1.0,             # base rate (same as Solo)
    "TempleRite":    PHI_INV,         # φ⁻¹ ~0.618 (resonance-weighted)
    "Storm":         PHI3,            # φ³  ~4.236
    "Crown":         PHI4,            # φ⁴  ~6.854
    "Certification": PHI_INV,         # φ⁻¹ ~0.618 (temple-adjacent)
    "Resonance":     PHI2,            # φ²  ~2.618
    "Publish":       PHI2,            # φ²  ~2.618
    "Seeding":       PHI3,            # φ³  ~4.236 (storm-adjacent)
    "Governance":    PHI4,            # φ⁴  ~6.854
    "Policy":        PHI4,            # φ⁴  ~6.854
    "Migration":     PHI5,            # φ⁵  ~11.090
    "Event":         PHI2,            # φ²  ~2.618
    "Convergence":   PHI3,            # φ³  ~4.236
}


# ═══════════════════════════════════════════════════════════════
# STORM THRESHOLDS
# ═══════════════════════════════════════════════════════════════

STORM_SEED = 21
STORM_TRIGGER = 34                   # positive pheromone threshold
SHADOW_CUTOFF = 13                   # max shadow for storm spawn
STORM_BASE_DURATION = 5              # epochs
STORM_POOL_BASE = 21
STORM_POOL_SCALE = 13
STORM_COALITION_BONUS = PHI_INV3     # ~0.236


# ═══════════════════════════════════════════════════════════════
# PHEROMONE PARAMETERS
# ═══════════════════════════════════════════════════════════════

PHEROMONE_DECAY = PHI_INV            # golden-memory decay
PHEROMONE_KAPPA = 1.0                # amplifier coupling

# Magnetic routing weights
MAGNET_PROFILE_WEIGHT = 0.618
MAGNET_POSITIVE_WEIGHT = 0.382
MAGNET_SHADOW_WEIGHT = 0.618
MAGNET_UNFINISHED_WEIGHT = 0.236
MAGNET_PULSE_WEIGHT = 0.146


# ═══════════════════════════════════════════════════════════════
# UNLOCK LADDER (Fibonacci-numbered)
# ═══════════════════════════════════════════════════════════════

UNLOCK_LADDER = {
    1:  "Solo quests",
    3:  "Guild Hall board access",
    5:  "Community quests",
    8:  "Temple rites",
    13: "PhiStorm participation",
    21: "Publish-candidate quests",
    34: "Storm seeding rights",
    55: "Policy proposal rights",
    89: "Migration review council",
}


# ═══════════════════════════════════════════════════════════════
# VESTING
# ═══════════════════════════════════════════════════════════════

NEAR_VEST_RATIO = PHI_INV2           # ~0.382


# ═══════════════════════════════════════════════════════════════
# PASS TRANSFORMS
# ═══════════════════════════════════════════════════════════════

PASS_TRANSFORMS = {
    "Sulfur": {
        "chi":  1.000,
        "r":    PHI_INV,             # 0.618
        "m":    1.000,
        "d":    (PHI, 1.0, PHI_INV, PHI_INV2),   # (F, A, W, E)
    },
    "Mercury": {
        "chi":  0.809,
        "r":    0.809,
        "m":    PHI_INV,             # 0.618
        "d":    (PHI_INV, PHI, 1.0, PHI_INV),
    },
    "Salt": {
        "chi":  PHI_INV,             # 0.618
        "r":    1.000,
        "m":    PHI_INV2,            # 0.382
        "d":    (PHI_INV2, PHI_INV, 1.0, PHI),
    },
}


# ═══════════════════════════════════════════════════════════════
# TRUTH LATTICE
# ═══════════════════════════════════════════════════════════════

TRUTH_STATES = ("OK", "NEAR", "AMBIG", "FAIL")

RECEIPT_PHASES = ("replay", "audit", "promotion", "publish", "chain")

RECEIPT_TYPES = (
    "ReplayPassReceipt",
    "ReplayIndexReceipt",
    "ScopeReplayClosureReceipt",
    "AuditGateCert",
    "LedgerReceipt",
    "UpgradePlanReceipt",
    "PromotionReceipt",
    "ReleaseSealCert",
    "ExportCert",
    "PublishLockCert",
    "PublicationReceipt",
    "ReceiptChainCert",
)
