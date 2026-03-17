# LP-57Omega Quest Atlas v1.5 — Machine-Readable Policy Bundle

- Source layer: `LP57Omega-SelfPlayQuestAtlas`
- Kind: `policy-specification`
- Role tags: `policy, contracts, governance, machine-readable`
- Family: `LP-57Omega Self-Play Quest Atlas`

## Working focus

Defines the machine-readable policy bundle containing all system contracts: BoardKernelPolicy, RouteCompilerPolicy, QueuePrunePolicy, StormPolicy, SeatElectionPolicy, PromotionBoundaryPolicy, ExecutionContract, and the BundleManifest.v1 top-level container.

## BundleManifest.v1

The top-level container that references all policy files and establishes the policy version:

```json
{
  "bundle_ver": "BundleManifest.v1",
  "protocol_id": "LP-57OMEGA",
  "created": "2026-03-14T00:00:00Z",
  "checksum_algo": "sha256",
  "policies": [
    "BoardKernelPolicy.json",
    "RouteCompilerPolicy.json",
    "QueuePrunePolicy.json",
    "StormPolicy.json",
    "SeatElectionPolicy.json",
    "PromotionBoundaryPolicy.json",
    "ExecutionContract.json",
    "RewardPolicy_v1.json",
    "QuestPolicy_v1.json",
    "TemplePolicy_v1.json",
    "MigrationPolicy_v1.json",
    "UnlockPolicy_v1.json",
    "KernelConst_v1.json"
  ],
  "integrity": {
    "all_policies_required": true,
    "bundle_hash": "<sha256 of concatenated policy hashes>",
    "backward_compatible_from": "BundleManifest.v0"
  }
}
```

### Manifest Rules

```
1. All listed policies must be present for valid bundle
2. Bundle hash is computed from sorted policy hashes
3. Any policy modification requires new bundle version
4. Backward compatibility is declared, not inferred
5. Protocol ID is immutable within a bundle version
```

## Policy Definitions

### BoardKernelPolicy

Governs the deterministic board generation kernel.

```json
{
  "policy_id": "BoardKernelPolicy",
  "version": "1.0",
  "rules": {
    "determinism": {
      "required": true,
      "description": "Same input must produce same output",
      "verification": "golden_vector:board_determinism"
    },
    "scoring": {
      "guild": {
        "formula": "base * truth_weight * difficulty * pressure * community * guild_amp",
        "truth_weights": {"OK": 1.0, "NEAR": 0.618, "AMBIG": 0.382, "FAIL": 0.0}
      },
      "temple": {
        "formula": "base * truth_weight * depth * temple_amp"
      }
    },
    "capacity": {
      "guild_max": 16,
      "temple_max": 8,
      "overflow_policy": "excess_to_overflow_queue"
    },
    "channel_split": {
      "temple_classes": ["deep_focus", "meditation", "compression",
                         "recursion_dive", "void_approach", "certify",
                         "verify", "audit"],
      "default_channel": "GUILD"
    }
  }
}
```

### RouteCompilerPolicy

Governs route construction and hub management.

```json
{
  "policy_id": "RouteCompilerPolicy",
  "version": "1.0",
  "rules": {
    "sigma_path": {
      "required": true,
      "value": ["AppA", "AppI", "AppM"],
      "description": "Always present in every route"
    },
    "hub_budget": {
      "max_hubs": 6,
      "trim_priority": ["publish_hub", "lens_hub", "overlay"],
      "sigma_protected": true
    },
    "overlay_map": {
      "OK": null,
      "NEAR": "AppJ",
      "AMBIG": "AppL",
      "FAIL": "AppK"
    },
    "publish_conditions": {
      "hub": "AppO",
      "requires": ["publish_intent", "truth_state:OK"]
    },
    "tunnel_planning": {
      "max_tunnels_per_route": 4,
      "dependency_resolution": "topological_sort"
    }
  }
}
```

### QueuePrunePolicy

Governs queue maintenance and overflow handling.

```json
{
  "policy_id": "QueuePrunePolicy",
  "version": "1.0",
  "rules": {
    "guild_queues": {
      "names": ["featured", "ladder", "repair", "storm", "recruit", "overflow"],
      "prune_after_loops": 19,
      "stale_threshold": "3 passes without progress"
    },
    "temple_queues": {
      "names": ["certification", "near_closure", "ambiguities",
                "compression", "sovereign", "overflow"],
      "prune_after_loops": 38,
      "stale_threshold": "2 orbits without progress"
    },
    "overflow_rules": {
      "max_overflow_entries": 32,
      "eviction_policy": "lowest_score_first",
      "evicted_entries": "logged_to_droplog"
    },
    "requeue_policy": {
      "failed_quests": "requeue_with_priority_decay",
      "decay_factor": 0.618
    }
  }
}
```

### StormPolicy

Governs PhiStorm triggering, duration, and effects.

```json
{
  "policy_id": "StormPolicy",
  "version": "1.0",
  "rules": {
    "trigger": {
      "positive_threshold": 34,
      "shadow_ceiling": 13,
      "station": "S13",
      "description": "Both conditions must be met simultaneously"
    },
    "duration": {
      "base_loops": 5,
      "max_loops": 19,
      "dissipation": "natural_phi_decay"
    },
    "effects": {
      "speed_multiplier": 2.0,
      "mint_multiplier": 1.618,
      "xp_multiplier": 2.618,
      "shuffle_rate": "storm_intensity * 0.3",
      "min_cross_bridges": 2
    },
    "termination": {
      "positive_floor": 21,
      "shadow_ceiling_alt": 21,
      "condition": "positive < floor OR shadow > ceiling_alt"
    },
    "pool": {
      "base": 21,
      "scale": 13,
      "coalition_bonus": 0.236
    }
  }
}
```

### SeatElectionPolicy

Governs subagent seat activation and quarantine.

```json
{
  "policy_id": "SeatElectionPolicy",
  "version": "1.0",
  "rules": {
    "election": {
      "max_active_per_master": 256,
      "affinity_scoring": "dot_product(seat.signature, quest.element_vector)",
      "demand_driven": true,
      "bottom_up_propagation": true
    },
    "quarantine": {
      "exclusion": "quarantined seats cannot be elected",
      "triggers": {
        "truth_violation": {"threshold": 0.3, "scope": "single_seat"},
        "repeated_failure": {"count": 3, "scope": "seat_and_siblings"},
        "risk_escalation": {"threshold": 0.8, "scope": "subtree"},
        "contradiction_cascade": {"count": 2, "scope": "full_lineage"},
        "resource_exhaustion": {"threshold": 0.95, "scope": "level_wide"}
      },
      "recovery": {
        "cooldown_required": true,
        "parent_approval": true,
        "verification_harness": true
      }
    },
    "host_steward_scoring": {
      "host_score": "capacity * affinity * availability",
      "steward_score": "experience * trust * element_match"
    }
  }
}
```

### PromotionBoundaryPolicy

Governs truth state transitions and promotion requirements.

```json
{
  "policy_id": "PromotionBoundaryPolicy",
  "version": "1.0",
  "rules": {
    "truth_promotions": {
      "FAIL_to_AMBIG": {
        "requires": ["root_cause_identified", "remediation_plan"],
        "minimum_evidence": 1
      },
      "AMBIG_to_NEAR": {
        "requires": ["evidence_submitted", "single_witness"],
        "minimum_evidence": 2
      },
      "NEAR_to_OK": {
        "requires": ["upgrade_plan", "witness_signature", "verification_pass"],
        "minimum_evidence": 3,
        "lock_ratio": 0.382
      }
    },
    "truth_demotions": {
      "OK_to_NEAR": {
        "triggers": ["contradiction_found", "evidence_invalidated"],
        "grace_period_loops": 3
      },
      "automatic_to_FAIL": {
        "triggers": ["quarantine_triggered", "integrity_violation"]
      }
    },
    "vesting": {
      "NEAR_lock_ratio": 0.382,
      "description": "38.2% of NEAR rewards are locked until promotion to OK"
    }
  }
}
```

### ExecutionContract

Governs the runtime execution guarantees.

```json
{
  "policy_id": "ExecutionContract",
  "version": "1.0",
  "rules": {
    "loop_execution": {
      "max_duration_per_loop": "configurable",
      "timeout_action": "force_close_with_partial_receipt",
      "retry_policy": "once_then_overflow"
    },
    "receipt_requirements": {
      "every_action_produces_receipt": true,
      "receipts_form_hash_chain": true,
      "chain_must_be_unbroken": true
    },
    "ledger_requirements": {
      "append_only": true,
      "no_modification": true,
      "no_deletion": true
    },
    "determinism": {
      "kernel_functions_pure": true,
      "no_external_state_reads": true,
      "no_side_effects": true
    },
    "orbit_boundary": {
      "carry_forward_required": true,
      "pheromone_decay": 0.618,
      "level_persistence": true,
      "xp_persistence": true
    }
  }
}
```

## Supporting Policy Files

### RewardPolicy_v1

```
- Truth gates: OK=1.0, NEAR=0.382 (locked portion)
- Base XP: 64
- Clamps: capsule=16x base, epoch=64x base
- Resonance ratio: 0.618
- Mint rates by quest class
```

### QuestPolicy_v1

```
- Lifecycle: Draft -> Active -> Blocked -> Sealed -> Published -> Archived
- State transitions are one-directional (no backward movement)
- Blocked quests timeout after configurable loops
```

### TemplePolicy_v1

```
- Certification requires invariant_set validation
- Ethics watchlist checked on every certification
- Grace and resonance weights apply to temple scoring
```

### MigrationPolicy_v1

```
- Freeze window: 3 loops before orbit boundary
- Backward replay: allowed for verification
- Rollback: only within current orbit
```

### UnlockPolicy_v1

```
- Fibonacci unlock ladder (L1, L3, L5, L8, L13, L21, L34, L55, L89)
- NEAR vesting: lock_ratio = 0.382 until truth promotion
- Tier permanence: unlocks never revoked
```

### KernelConst_v1

```json
{
  "BASE_XP": 64,
  "ORBIT_SIZE": 57,
  "STATION_COUNT": 19,
  "PASS_COUNT": 3,
  "PHI": 1.618033988749895,
  "PHI_INV": 0.618033988749895,
  "PHI_INV_SQ": 0.381966011250105,
  "GUILD_CAPACITY": 16,
  "TEMPLE_CAPACITY": 8,
  "MAX_HUBS": 6,
  "MAX_ACTIVE_SEATS": 256,
  "STORM_POSITIVE_THRESHOLD": 34,
  "STORM_SHADOW_CEILING": 13,
  "KAPPA": 0.381966011250105,
  "SUBAGENT_DEPTH": 6,
  "SEATS_PER_MASTER": 4096
}
```

## Bundle Verification

```
VERIFY_BUNDLE(manifest):
  1. Check all policy files present
  2. Verify individual policy checksums
  3. Compute bundle hash from sorted policy hashes
  4. Compare against manifest.integrity.bundle_hash
  5. Validate cross-policy consistency:
     - StormPolicy thresholds match KernelConst
     - SeatElectionPolicy limits match KernelConst
     - All phi-derived values are consistent
  6. Run golden test vectors (v1.6)
  7. If all pass: CERTIFIED
  8. If any fail: REJECTED with failure report
```

## Invariants

1. All policies are versioned and checksummed
2. Bundle is invalid if any policy is missing
3. Policy modifications require new bundle version
4. KernelConst values are the single source of truth for constants
5. Cross-policy consistency is verified at bundle validation
6. The bundle hash is deterministic

## Suggested chapter anchors

- `Ch01` — Kernel and entry law
- `Ch12` — Legality certificates and closure
- `Ch16` — Verification harnesses and replay kernels
- `Ch17` — Deployment and bounded agency
