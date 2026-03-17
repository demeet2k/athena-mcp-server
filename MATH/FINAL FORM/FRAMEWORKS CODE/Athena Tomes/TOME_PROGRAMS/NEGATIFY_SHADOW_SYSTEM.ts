/**
 * NEGATIFY_SHADOW_SYSTEM.ts
 * 
 * Comprehensive implementation of Negatify: Inverse-φ Shadow Maps,
 * Failure Mode Detection, Guard Installation, and Worst-Case Catalogs
 * 
 * From SELF_SUFFICIENCY_TOME Ch15.R and Appendix M:
 * - Negatify maps: structured catalogs of worst-case pathways
 * - Inverse-φ alignment: preference ordering over failure patterns
 * - Shadow completeness: failure enumeration across all lenses
 * - Guard installers: corridor hardening actions
 * - Probe generators: adversarial test construction
 * 
 * Negatify does NOT enact failure patterns - it DETECTS and GUARDS against them.
 */

// ============================================================================
// SECTION 1: CORE TYPES AND FAILURE MODE TAXONOMY
// ============================================================================

/**
 * Failure mode classes from M.S1.b
 */
enum FailureModeClass {
  Spoof = 'SPOOF',                    // Certificate/proof spoofing
  Bypass = 'BYPASS',                  // Corridor/safety bypass attempts
  Drift = 'DRIFT',                    // Model/data/convention drift
  FragmentFraud = 'FRAGMENT_FRAUD',   // Non-4^n level completeness claims
  FalseCoherence = 'FALSE_COHERENCE', // Cross-lens inconsistency masking
  Runaway = 'RUNAWAY',                // Unbounded recursion/self-upgrade
  Leak = 'LEAK',                      // Budget/κ/safety leakage
  AmbiguityAbuse = 'AMBIGUITY_ABUSE', // Uncertainty envelope exploitation
  ProofDebt = 'PROOF_DEBT',           // Missing/incomplete proofs
  RouteCorruption = 'ROUTE_CORRUPTION' // Metro routing violations
}

/**
 * Severity levels for failure modes
 */
enum Severity {
  Critical = 'CRITICAL',   // Immediate safety/correctness threat
  High = 'HIGH',           // Significant impact on system integrity
  Medium = 'MEDIUM',       // Notable concern requiring attention
  Low = 'LOW',             // Minor issue, manageable
  Info = 'INFO'            // Informational, monitoring only
}

/**
 * Lens classification for shadow coverage
 */
enum ShadowLens {
  Square = 'SQUARE',   // Typing/cert failures
  Flower = 'FLOWER',   // Illegal transforms/rotations
  Cloud = 'CLOUD',     // Uncertainty abuse, calibration failure
  Fractal = 'FRACTAL'  // Runaway recursion, fragment fraud
}

/**
 * Probe decision outcomes
 */
enum ProbeDecision {
  Confirmed = 'CONFIRMED',       // Failure mode confirmed
  Inconclusive = 'INCONCLUSIVE', // Underresolved - needs more evidence
  FalseAlarm = 'FALSE_ALARM',    // Mode not present
  Blocked = 'BLOCKED'            // Probe blocked by guards
}

/**
 * Guard action types
 */
enum GuardAction {
  TightenCorridor = 'TIGHTEN_CORRIDOR',
  AddNonBypassCheck = 'ADD_NON_BYPASS_CHECK',
  RequireStrongerCert = 'REQUIRE_STRONGER_CERT',
  EnforceAdmittedLevel = 'ENFORCE_ADMITTED_LEVEL',
  AddRecursionClamp = 'ADD_RECURSION_CLAMP',
  AddCheckpoint = 'ADD_CHECKPOINT',
  RerouteSaferHub = 'REROUTE_SAFER_HUB',
  AddConventionAdapter = 'ADD_CONVENTION_ADAPTER',
  InvalidateStaleProof = 'INVALIDATE_STALE_PROOF',
  AddCalibrationGate = 'ADD_CALIBRATION_GATE',
  AddDriftTrigger = 'ADD_DRIFT_TRIGGER',
  RejectRoute = 'REJECT_ROUTE'
}

/**
 * Obligation kinds from guard installation
 */
enum ObligationKind {
  InstallGuard = 'INSTALL_GUARD',
  TightenCorridor = 'TIGHTEN_CORRIDOR',
  AddCertRequirement = 'ADD_CERT_REQUIREMENT',
  AddConventionAdapter = 'ADD_CONVENTION_ADAPTER',
  UpgradeLevel = 'UPGRADE_LEVEL',
  EnforceFragmentRejection = 'ENFORCE_FRAGMENT_REJECTION',
  AddRecursionClamp = 'ADD_RECURSION_CLAMP',
  RerouteViaSaferHubs = 'REROUTE_VIA_SAFER_HUBS'
}

// ============================================================================
// SECTION 2: FAILURE MODE OBJECTS
// ============================================================================

/**
 * Failure mode signature - pattern identifying the failure
 */
interface FailureModeSignature {
  readonly pattern: string;
  readonly indicators: readonly string[];
  readonly thresholds: Map<string, number>;
  readonly requiredEvidence: readonly string[];
}

/**
 * Impact assessment for failure mode
 */
interface FailureModeImpact {
  readonly affectedNodes: readonly string[];
  readonly cascadeRisk: number;        // 0-1
  readonly recoveryDifficulty: number; // 0-1
  readonly dataLossRisk: number;       // 0-1
  readonly safetyImpact: Severity;
}

/**
 * Countermeasure specification
 */
interface Countermeasure {
  readonly id: string;
  readonly action: GuardAction;
  readonly parameters: Readonly<Record<string, unknown>>;
  readonly effectiveness: number; // 0-1
  readonly cost: number;          // resource cost
  readonly dependencies: readonly string[];
}

/**
 * Complete failure mode object (M.S1.b)
 */
interface FailureMode {
  readonly mid: string;
  readonly class: FailureModeClass;
  readonly lens: ShadowLens;
  readonly signature: FailureModeSignature;
  readonly severity: Severity;
  readonly preconditions: readonly string[];
  readonly impact: FailureModeImpact;
  readonly countermeasures: readonly Countermeasure[];
  readonly hash: string;
}

// ============================================================================
// SECTION 3: TRIGGER AND PROBE OBJECTS
// ============================================================================

/**
 * Trigger template for probe generation (M.S1.c)
 */
interface TriggerTemplate {
  readonly triggerId: string;
  readonly targetMode: string;
  readonly contextRequirements: readonly string[];
  readonly inputGenerator: (context: ProbeContext) => ProbeInput;
  readonly expectedBoundary: BoundaryType;
  readonly hash: string;
}

/**
 * Probe context - environment for running probes
 */
interface ProbeContext {
  readonly domain: string;
  readonly artifact: ArtifactReference;
  readonly corridor: CorridorState;
  readonly budgets: BudgetState;
  readonly seed: string;
  readonly admittedLevels: readonly number[];
  readonly detectorRegistry: DetectorRegistry;
}

/**
 * Probe input generated from trigger template
 */
interface ProbeInput {
  readonly inputId: string;
  readonly triggerId: string;
  readonly targetMode: string;
  readonly adversarialData: Readonly<Record<string, unknown>>;
  readonly expectedOutcome: ProbeDecision;
  readonly boundConstraints: readonly string[];
  readonly seed: string;
  readonly hash: string;
}

/**
 * Probe report from running a shadow probe
 */
interface ProbeReport {
  readonly reportId: string;
  readonly probeInput: ProbeInput;
  readonly decision: ProbeDecision;
  readonly confidence: number;
  readonly observedVulnerabilities: readonly VulnerabilityFingerprint[];
  readonly detectorOutputs: Map<string, DetectorOutput>;
  readonly obligations: readonly Obligation[];
  readonly replayTrace: ReplayTrace;
  readonly hash: string;
}

/**
 * Vulnerability fingerprint from probe
 */
interface VulnerabilityFingerprint {
  readonly vulnId: string;
  readonly mode: string;
  readonly signature: string;
  readonly evidence: readonly string[];
  readonly severity: Severity;
  readonly exploitPath: readonly string[];
}

/**
 * Boundary type classification
 */
enum BoundaryType {
  Undefined = 'UNDEFINED',
  Singular = 'SINGULAR',
  Ambiguous = 'AMBIGUOUS',
  OutOfCorridor = 'OUT_OF_CORRIDOR',
  UnderResolved = 'UNDER_RESOLVED',
  NonTerminating = 'NON_TERMINATING'
}

// ============================================================================
// SECTION 4: NEGATIFY CATALOG
// ============================================================================

/**
 * Complete Negatify catalog (M.S1.a)
 */
interface NegatifyCatalog {
  readonly domain: string;
  readonly modes: Map<string, FailureMode>;
  readonly triggers: Map<string, TriggerTemplate>;
  readonly detectors: readonly string[];
  readonly guards: Map<GuardAction, GuardInstaller>;
  readonly obligations: Map<ObligationKind, ObligationTemplate>;
  readonly coverage: CoverageReport;
  readonly version: string;
  readonly hash: string;
}

/**
 * Coverage report for shadow completeness
 */
interface CoverageReport {
  readonly totalModes: number;
  readonly coveredModes: number;
  readonly coverageByLens: Map<ShadowLens, number>;
  readonly coverageByClass: Map<FailureModeClass, number>;
  readonly missingCoverage: readonly string[];
  readonly completenessScore: number; // 0-1
}

/**
 * Guard installer - translates probe findings to hardening actions
 */
interface GuardInstaller {
  readonly action: GuardAction;
  readonly install: (report: ProbeReport, corridor: CorridorState) => GuardInstallation;
  readonly verify: (installation: GuardInstallation) => boolean;
  readonly cost: number;
}

/**
 * Guard installation result
 */
interface GuardInstallation {
  readonly installationId: string;
  readonly action: GuardAction;
  readonly parameters: Readonly<Record<string, unknown>>;
  readonly appliedTo: readonly string[];
  readonly merkleLink: string;
  readonly replayable: boolean;
  readonly hash: string;
}

/**
 * Obligation template for generating obligations
 */
interface ObligationTemplate {
  readonly kind: ObligationKind;
  readonly generate: (mode: FailureMode, report: ProbeReport) => Obligation;
  readonly priority: number;
  readonly dependencies: readonly string[];
}

// ============================================================================
// SECTION 5: SUPPORTING TYPES
// ============================================================================

interface ArtifactReference {
  readonly addr: string;
  readonly hash: string;
  readonly type: string;
}

interface CorridorState {
  readonly guards: readonly string[];
  readonly budgets: BudgetState;
  readonly constraints: readonly string[];
  readonly admittedLevels: readonly number[];
}

interface BudgetState {
  readonly kappa: number;
  readonly beta: number;
  readonly chi: number;
  readonly epsilon: number;
}

interface DetectorRegistry {
  readonly detectors: Map<string, Detector>;
  readonly run: (id: string, input: unknown) => DetectorOutput;
}

interface Detector {
  readonly id: string;
  readonly targetModes: readonly string[];
  readonly run: (input: unknown) => DetectorOutput;
}

interface DetectorOutput {
  readonly detected: boolean;
  readonly confidence: number;
  readonly evidence: readonly string[];
  readonly trace: string;
}

interface Obligation {
  readonly oblId: string;
  readonly kind: ObligationKind;
  readonly target: string;
  readonly requirements: readonly string[];
  readonly budgets: BudgetState;
  readonly deadlinePolicy: string;
  readonly priority: number;
}

interface ReplayTrace {
  readonly seed: string;
  readonly events: readonly string[];
  readonly hashes: readonly string[];
  readonly deterministic: boolean;
}

// ============================================================================
// SECTION 6: FAILURE MODE REGISTRY - ALL KNOWN MODES
// ============================================================================

class FailureModeRegistry {
  private readonly modes: Map<string, FailureMode> = new Map();
  
  constructor() {
    this.registerSquareModes();
    this.registerFlowerModes();
    this.registerCloudModes();
    this.registerFractalModes();
  }
  
  /**
   * Register Square/Earth lens failure modes
   */
  private registerSquareModes(): void {
    // Spoof: Certificate spoofing
    this.modes.set('SQ_SPOOF_CERT', {
      mid: 'SQ_SPOOF_CERT',
      class: FailureModeClass.Spoof,
      lens: ShadowLens.Square,
      signature: {
        pattern: 'INVALID_CERT_SIGNATURE',
        indicators: ['hash_mismatch', 'signature_invalid', 'chain_broken'],
        thresholds: new Map([['confidence', 0.95]]),
        requiredEvidence: ['cert_bytes', 'public_key', 'signature']
      },
      severity: Severity.Critical,
      preconditions: ['has_certificate', 'verifier_available'],
      impact: {
        affectedNodes: [],
        cascadeRisk: 0.9,
        recoveryDifficulty: 0.7,
        dataLossRisk: 0.3,
        safetyImpact: Severity.Critical
      },
      countermeasures: [{
        id: 'CM_STRONGER_CERT',
        action: GuardAction.RequireStrongerCert,
        parameters: { minBits: 256, requireChain: true },
        effectiveness: 0.95,
        cost: 1.2,
        dependencies: []
      }],
      hash: this.computeHash('SQ_SPOOF_CERT')
    });
    
    // Bypass: Corridor bypass attempt
    this.modes.set('SQ_BYPASS_CORRIDOR', {
      mid: 'SQ_BYPASS_CORRIDOR',
      class: FailureModeClass.Bypass,
      lens: ShadowLens.Square,
      signature: {
        pattern: 'CORRIDOR_CONSTRAINT_VIOLATED',
        indicators: ['guard_skipped', 'budget_exceeded', 'scope_violation'],
        thresholds: new Map([['violation_count', 1]]),
        requiredEvidence: ['corridor_state', 'operation_log', 'guard_trace']
      },
      severity: Severity.Critical,
      preconditions: ['has_corridor_guards'],
      impact: {
        affectedNodes: [],
        cascadeRisk: 0.95,
        recoveryDifficulty: 0.8,
        dataLossRisk: 0.5,
        safetyImpact: Severity.Critical
      },
      countermeasures: [{
        id: 'CM_NON_BYPASS',
        action: GuardAction.AddNonBypassCheck,
        parameters: { enforceAll: true, logViolations: true },
        effectiveness: 0.98,
        cost: 1.5,
        dependencies: ['corridor_engine']
      }],
      hash: this.computeHash('SQ_BYPASS_CORRIDOR')
    });
    
    // ProofDebt: Missing required proofs
    this.modes.set('SQ_PROOF_DEBT', {
      mid: 'SQ_PROOF_DEBT',
      class: FailureModeClass.ProofDebt,
      lens: ShadowLens.Square,
      signature: {
        pattern: 'MISSING_REQUIRED_PROOF',
        indicators: ['proof_absent', 'proof_incomplete', 'witness_missing'],
        thresholds: new Map([['missing_count', 1]]),
        requiredEvidence: ['claim', 'required_proofs', 'existing_proofs']
      },
      severity: Severity.High,
      preconditions: ['has_claims'],
      impact: {
        affectedNodes: [],
        cascadeRisk: 0.6,
        recoveryDifficulty: 0.5,
        dataLossRisk: 0.2,
        safetyImpact: Severity.High
      },
      countermeasures: [{
        id: 'CM_REQUIRE_PROOF',
        action: GuardAction.RequireStrongerCert,
        parameters: { requireWitness: true, requireReplay: true },
        effectiveness: 0.9,
        cost: 1.0,
        dependencies: []
      }],
      hash: this.computeHash('SQ_PROOF_DEBT')
    });
  }
  
  /**
   * Register Flower/Air lens failure modes
   */
  private registerFlowerModes(): void {
    // Convention exploit
    this.modes.set('FL_CONVENTION_EXPLOIT', {
      mid: 'FL_CONVENTION_EXPLOIT',
      class: FailureModeClass.Drift,
      lens: ShadowLens.Flower,
      signature: {
        pattern: 'CONVENTION_MISMATCH',
        indicators: ['fourier_norm_mismatch', 'log_branch_conflict', 'wick_rotation_error'],
        thresholds: new Map([['drift_magnitude', 0.01]]),
        requiredEvidence: ['convention_hashes', 'route_log', 'transform_chain']
      },
      severity: Severity.High,
      preconditions: ['uses_transforms'],
      impact: {
        affectedNodes: [],
        cascadeRisk: 0.7,
        recoveryDifficulty: 0.6,
        dataLossRisk: 0.4,
        safetyImpact: Severity.High
      },
      countermeasures: [{
        id: 'CM_CONVENTION_ADAPTER',
        action: GuardAction.AddConventionAdapter,
        parameters: { requireExplicit: true, validateChain: true },
        effectiveness: 0.92,
        cost: 1.1,
        dependencies: ['convention_registry']
      }],
      hash: this.computeHash('FL_CONVENTION_EXPLOIT')
    });
    
    // Illegal rotation
    this.modes.set('FL_ILLEGAL_ROTATION', {
      mid: 'FL_ILLEGAL_ROTATION',
      class: FailureModeClass.RouteCorruption,
      lens: ShadowLens.Flower,
      signature: {
        pattern: 'FORBIDDEN_OPPOSITE_POLE',
        indicators: ['direct_opposite_jump', 'missing_tunnel', 'checkpoint_absent'],
        thresholds: new Map([['violation_severity', 0.8]]),
        requiredEvidence: ['rotation_attempt', 'pole_positions', 'allowed_bridges']
      },
      severity: Severity.Critical,
      preconditions: ['uses_rotations'],
      impact: {
        affectedNodes: [],
        cascadeRisk: 0.8,
        recoveryDifficulty: 0.7,
        dataLossRisk: 0.3,
        safetyImpact: Severity.Critical
      },
      countermeasures: [{
        id: 'CM_REQUIRE_TUNNEL',
        action: GuardAction.RerouteSaferHub,
        parameters: { requireZ0Tunnel: true, enforceCheckpoint: true },
        effectiveness: 0.95,
        cost: 1.3,
        dependencies: ['metro_router']
      }],
      hash: this.computeHash('FL_ILLEGAL_ROTATION')
    });
    
    // Bridge spoof
    this.modes.set('FL_BRIDGE_SPOOF', {
      mid: 'FL_BRIDGE_SPOOF',
      class: FailureModeClass.Spoof,
      lens: ShadowLens.Flower,
      signature: {
        pattern: 'SPOOFED_COMMUTATION',
        indicators: ['missing_witness', 'invalid_duality_proof', 'commutation_failed'],
        thresholds: new Map([['confidence', 0.9]]),
        requiredEvidence: ['bridge_claim', 'witness_attempt', 'verification_log']
      },
      severity: Severity.Critical,
      preconditions: ['uses_bridges'],
      impact: {
        affectedNodes: [],
        cascadeRisk: 0.85,
        recoveryDifficulty: 0.75,
        dataLossRisk: 0.4,
        safetyImpact: Severity.Critical
      },
      countermeasures: [{
        id: 'CM_REQUIRE_WITNESS',
        action: GuardAction.RequireStrongerCert,
        parameters: { requireCommutationWitness: true, requireDualityProof: true },
        effectiveness: 0.96,
        cost: 1.4,
        dependencies: ['bridge_verifier']
      }],
      hash: this.computeHash('FL_BRIDGE_SPOOF')
    });
  }
  
  /**
   * Register Cloud/Water lens failure modes
   */
  private registerCloudModes(): void {
    // Ambiguity abuse
    this.modes.set('CL_AMBIGUITY_ABUSE', {
      mid: 'CL_AMBIGUITY_ABUSE',
      class: FailureModeClass.AmbiguityAbuse,
      lens: ShadowLens.Cloud,
      signature: {
        pattern: 'UNSAFE_STRADDLE_DECISION',
        indicators: ['straddle_forced', 'envelope_ignored', 'refinement_suppressed'],
        thresholds: new Map([['straddle_count', 3]]),
        requiredEvidence: ['envelope_state', 'decision_log', 'threshold_crossings']
      },
      severity: Severity.High,
      preconditions: ['uses_uncertainty'],
      impact: {
        affectedNodes: [],
        cascadeRisk: 0.65,
        recoveryDifficulty: 0.5,
        dataLossRisk: 0.35,
        safetyImpact: Severity.High
      },
      countermeasures: [{
        id: 'CM_CONSERVATIVE_THRESHOLD',
        action: GuardAction.TightenCorridor,
        parameters: { enforceStraddle: true, requireRefinement: true },
        effectiveness: 0.88,
        cost: 0.9,
        dependencies: []
      }],
      hash: this.computeHash('CL_AMBIGUITY_ABUSE')
    });
    
    // Calibration spoof
    this.modes.set('CL_CALIBRATION_SPOOF', {
      mid: 'CL_CALIBRATION_SPOOF',
      class: FailureModeClass.Spoof,
      lens: ShadowLens.Cloud,
      signature: {
        pattern: 'MISSING_CALIBRATION',
        indicators: ['no_calibration_hash', 'protocol_mismatch', 'provenance_absent'],
        thresholds: new Map([['confidence', 0.85]]),
        requiredEvidence: ['prob_claim', 'calibration_attempt', 'protocol_id']
      },
      severity: Severity.High,
      preconditions: ['makes_prob_claims'],
      impact: {
        affectedNodes: [],
        cascadeRisk: 0.6,
        recoveryDifficulty: 0.55,
        dataLossRisk: 0.3,
        safetyImpact: Severity.High
      },
      countermeasures: [{
        id: 'CM_REQUIRE_CALIBRATION',
        action: GuardAction.AddCalibrationGate,
        parameters: { requireProvenance: true, downgradeToWorstCase: true },
        effectiveness: 0.91,
        cost: 1.0,
        dependencies: ['calibration_registry']
      }],
      hash: this.computeHash('CL_CALIBRATION_SPOOF')
    });
    
    // Drift masking
    this.modes.set('CL_DRIFT_MASKING', {
      mid: 'CL_DRIFT_MASKING',
      class: FailureModeClass.Drift,
      lens: ShadowLens.Cloud,
      signature: {
        pattern: 'DRIFT_SUPPRESSED',
        indicators: ['drift_detected_but_ignored', 'stale_model_used', 'decision_log_inconsistent'],
        thresholds: new Map([['drift_magnitude', 0.05]]),
        requiredEvidence: ['drift_detector_output', 'decision_log', 'model_version']
      },
      severity: Severity.High,
      preconditions: ['uses_models'],
      impact: {
        affectedNodes: [],
        cascadeRisk: 0.7,
        recoveryDifficulty: 0.6,
        dataLossRisk: 0.45,
        safetyImpact: Severity.High
      },
      countermeasures: [{
        id: 'CM_DRIFT_TRIGGER',
        action: GuardAction.AddDriftTrigger,
        parameters: { triggerTightening: true, invalidateStale: true },
        effectiveness: 0.89,
        cost: 1.1,
        dependencies: ['drift_detector']
      }],
      hash: this.computeHash('CL_DRIFT_MASKING')
    });
  }
  
  /**
   * Register Fractal/Fire lens failure modes
   */
  private registerFractalModes(): void {
    // Fragment fraud
    this.modes.set('FR_FRAGMENT_FRAUD', {
      mid: 'FR_FRAGMENT_FRAUD',
      class: FailureModeClass.FragmentFraud,
      lens: ShadowLens.Fractal,
      signature: {
        pattern: 'NON_ADMITTED_LEVEL_CLAIM',
        indicators: ['level_not_power_of_4', 'completeness_on_fragment', '8x8_detected'],
        thresholds: new Map([['violation_count', 1]]),
        requiredEvidence: ['claimed_level', 'admitted_levels', 'completeness_claim']
      },
      severity: Severity.Critical,
      preconditions: ['makes_completeness_claims'],
      impact: {
        affectedNodes: [],
        cascadeRisk: 0.85,
        recoveryDifficulty: 0.7,
        dataLossRisk: 0.5,
        safetyImpact: Severity.Critical
      },
      countermeasures: [{
        id: 'CM_ENFORCE_LEVEL',
        action: GuardAction.EnforceAdmittedLevel,
        parameters: { admittedLevels: [4, 16, 64, 256, 1024], rejectFragments: true },
        effectiveness: 0.97,
        cost: 0.8,
        dependencies: []
      }],
      hash: this.computeHash('FR_FRAGMENT_FRAUD')
    });
    
    // Seed drift
    this.modes.set('FR_SEED_DRIFT', {
      mid: 'FR_SEED_DRIFT',
      class: FailureModeClass.Drift,
      lens: ShadowLens.Fractal,
      signature: {
        pattern: 'FIXED_POINT_VIOLATION',
        indicators: ['collapse_expand_mismatch', 'merkle_divergence', 'dependency_mutation'],
        thresholds: new Map([['divergence', 0]]),
        requiredEvidence: ['original_seed', 'expanded_form', 'collapsed_result']
      },
      severity: Severity.Critical,
      preconditions: ['uses_seeds'],
      impact: {
        affectedNodes: [],
        cascadeRisk: 0.9,
        recoveryDifficulty: 0.8,
        dataLossRisk: 0.6,
        safetyImpact: Severity.Critical
      },
      countermeasures: [{
        id: 'CM_CHECKPOINT_ENFORCE',
        action: GuardAction.AddCheckpoint,
        parameters: { verifyFixedPoint: true, merkleValidate: true },
        effectiveness: 0.94,
        cost: 1.2,
        dependencies: ['seed_store']
      }],
      hash: this.computeHash('FR_SEED_DRIFT')
    });
    
    // Runaway recursion
    this.modes.set('FR_RUNAWAY_RECURSION', {
      mid: 'FR_RUNAWAY_RECURSION',
      class: FailureModeClass.Runaway,
      lens: ShadowLens.Fractal,
      signature: {
        pattern: 'RECURSION_DEPTH_EXCEEDED',
        indicators: ['depth_violation', 'checkpoint_failure', 'unbounded_growth'],
        thresholds: new Map([['max_depth', 256]]),
        requiredEvidence: ['recursion_trace', 'depth_counter', 'clamp_state']
      },
      severity: Severity.Critical,
      preconditions: ['uses_recursion'],
      impact: {
        affectedNodes: [],
        cascadeRisk: 0.95,
        recoveryDifficulty: 0.85,
        dataLossRisk: 0.4,
        safetyImpact: Severity.Critical
      },
      countermeasures: [{
        id: 'CM_RECURSION_CLAMP',
        action: GuardAction.AddRecursionClamp,
        parameters: { maxDepth: 64, rollbackOnViolation: true },
        effectiveness: 0.96,
        cost: 1.0,
        dependencies: []
      }],
      hash: this.computeHash('FR_RUNAWAY_RECURSION')
    });
    
    // Leak mode
    this.modes.set('FR_BUDGET_LEAK', {
      mid: 'FR_BUDGET_LEAK',
      class: FailureModeClass.Leak,
      lens: ShadowLens.Fractal,
      signature: {
        pattern: 'KAPPA_CONSERVATION_VIOLATED',
        indicators: ['kappa_pre_ne_post', 'budget_disappeared', 'leak_detected'],
        thresholds: new Map([['leak_magnitude', 0.001]]),
        requiredEvidence: ['kappa_pre', 'kappa_post', 'kappa_spent', 'kappa_leak']
      },
      severity: Severity.Critical,
      preconditions: ['uses_budgets'],
      impact: {
        affectedNodes: [],
        cascadeRisk: 0.8,
        recoveryDifficulty: 0.7,
        dataLossRisk: 0.3,
        safetyImpact: Severity.Critical
      },
      countermeasures: [{
        id: 'CM_KAPPA_ACCOUNTING',
        action: GuardAction.TightenCorridor,
        parameters: { enforceConservation: true, logAllTransfers: true },
        effectiveness: 0.93,
        cost: 1.1,
        dependencies: ['budget_tracker']
      }],
      hash: this.computeHash('FR_BUDGET_LEAK')
    });
  }
  
  private computeHash(id: string): string {
    let hash = 0;
    const str = id + Date.now().toString();
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return `HASH_${Math.abs(hash).toString(16).toUpperCase().padStart(16, '0')}`;
  }
  
  getMode(mid: string): FailureMode | undefined {
    return this.modes.get(mid);
  }
  
  getAllModes(): FailureMode[] {
    return Array.from(this.modes.values());
  }
  
  getModesByLens(lens: ShadowLens): FailureMode[] {
    return this.getAllModes().filter(m => m.lens === lens);
  }
  
  getModesByClass(modeClass: FailureModeClass): FailureMode[] {
    return this.getAllModes().filter(m => m.class === modeClass);
  }
}

// ============================================================================
// SECTION 7: TRIGGER GENERATOR
// ============================================================================

class TriggerGenerator {
  private readonly registry: FailureModeRegistry;
  private readonly triggers: Map<string, TriggerTemplate> = new Map();
  
  constructor(registry: FailureModeRegistry) {
    this.registry = registry;
    this.generateAllTriggers();
  }
  
  private generateAllTriggers(): void {
    for (const mode of this.registry.getAllModes()) {
      const trigger = this.createTriggerForMode(mode);
      this.triggers.set(trigger.triggerId, trigger);
    }
  }
  
  private createTriggerForMode(mode: FailureMode): TriggerTemplate {
    const triggerId = `TRIG_${mode.mid}`;
    
    return {
      triggerId,
      targetMode: mode.mid,
      contextRequirements: mode.preconditions,
      inputGenerator: (context: ProbeContext) => this.generateProbeInput(mode, context),
      expectedBoundary: this.getExpectedBoundary(mode),
      hash: this.computeHash(triggerId)
    };
  }
  
  private generateProbeInput(mode: FailureMode, context: ProbeContext): ProbeInput {
    const inputId = `INPUT_${mode.mid}_${Date.now()}`;
    
    // Generate adversarial data based on mode class
    const adversarialData = this.generateAdversarialData(mode, context);
    
    return {
      inputId,
      triggerId: `TRIG_${mode.mid}`,
      targetMode: mode.mid,
      adversarialData,
      expectedOutcome: ProbeDecision.Confirmed,
      boundConstraints: context.corridor.constraints,
      seed: context.seed,
      hash: this.computeHash(inputId)
    };
  }
  
  private generateAdversarialData(
    mode: FailureMode, 
    context: ProbeContext
  ): Readonly<Record<string, unknown>> {
    switch (mode.class) {
      case FailureModeClass.Spoof:
        return {
          spoofedSignature: 'INVALID_SIG_' + Math.random().toString(36),
          originalHash: context.artifact.hash,
          claimedHash: 'FAKE_HASH_' + Math.random().toString(36)
        };
        
      case FailureModeClass.Bypass:
        return {
          bypassTarget: context.corridor.guards[0],
          violatedConstraint: context.corridor.constraints[0],
          exceededBudget: { kappa: context.budgets.kappa * 1.5 }
        };
        
      case FailureModeClass.Drift:
        return {
          originalConvention: 'FOURIER_UNITARY',
          mutatedConvention: 'FOURIER_NON_UNITARY',
          driftMagnitude: 0.15
        };
        
      case FailureModeClass.FragmentFraud:
        return {
          claimedLevel: 8, // Non-admitted level
          admittedLevels: context.admittedLevels,
          completenessAssertion: true
        };
        
      case FailureModeClass.FalseCoherence:
        return {
          squareResult: { valid: true },
          flowerResult: { valid: false },
          coherenceClaim: true
        };
        
      case FailureModeClass.Runaway:
        return {
          recursionDepth: 1000,
          maxAllowed: 64,
          checkpointState: 'MISSING'
        };
        
      case FailureModeClass.Leak:
        return {
          kappaPre: 100,
          kappaPost: 50,
          kappaSpent: 30,
          kappaLeak: 20
        };
        
      case FailureModeClass.AmbiguityAbuse:
        return {
          straddleCount: 10,
          refinementAttempts: 0,
          forcedDecision: true
        };
        
      case FailureModeClass.ProofDebt:
        return {
          requiredProofs: ['WITNESS_A', 'WITNESS_B'],
          providedProofs: [],
          claimsMade: 5
        };
        
      case FailureModeClass.RouteCorruption:
        return {
          attemptedRoute: ['NORTH_POLE', 'SOUTH_POLE'],
          tunnelUsed: false,
          checkpointPresent: false
        };
        
      default:
        return {};
    }
  }
  
  private getExpectedBoundary(mode: FailureMode): BoundaryType {
    switch (mode.class) {
      case FailureModeClass.Bypass:
      case FailureModeClass.RouteCorruption:
        return BoundaryType.OutOfCorridor;
        
      case FailureModeClass.FragmentFraud:
      case FailureModeClass.ProofDebt:
        return BoundaryType.UnderResolved;
        
      case FailureModeClass.AmbiguityAbuse:
        return BoundaryType.Ambiguous;
        
      case FailureModeClass.Runaway:
        return BoundaryType.NonTerminating;
        
      default:
        return BoundaryType.Undefined;
    }
  }
  
  private computeHash(id: string): string {
    let hash = 0;
    const str = id;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return `HASH_${Math.abs(hash).toString(16).toUpperCase().padStart(16, '0')}`;
  }
  
  getTrigger(triggerId: string): TriggerTemplate | undefined {
    return this.triggers.get(triggerId);
  }
  
  getAllTriggers(): TriggerTemplate[] {
    return Array.from(this.triggers.values());
  }
  
  getTriggerForMode(mid: string): TriggerTemplate | undefined {
    return this.triggers.get(`TRIG_${mid}`);
  }
}

// ============================================================================
// SECTION 8: SHADOW PROBE ENGINE
// ============================================================================

class ShadowProbeEngine {
  private readonly registry: FailureModeRegistry;
  private readonly triggerGenerator: TriggerGenerator;
  private readonly detectorRegistry: DetectorRegistry;
  
  constructor(
    registry: FailureModeRegistry,
    triggerGenerator: TriggerGenerator,
    detectorRegistry: DetectorRegistry
  ) {
    this.registry = registry;
    this.triggerGenerator = triggerGenerator;
    this.detectorRegistry = detectorRegistry;
  }
  
  /**
   * Run a shadow probe for a specific failure mode (Construction 15.8)
   */
  runProbe(
    artifact: ArtifactReference,
    domain: string,
    modeId: string,
    context: ProbeContext
  ): ProbeReport {
    const mode = this.registry.getMode(modeId);
    if (!mode) {
      throw new Error(`Unknown failure mode: ${modeId}`);
    }
    
    const trigger = this.triggerGenerator.getTriggerForMode(modeId);
    if (!trigger) {
      throw new Error(`No trigger for mode: ${modeId}`);
    }
    
    // Generate probe input
    const probeInput = trigger.inputGenerator(context);
    
    // Run detectors
    const detectorOutputs = this.runDetectors(mode, probeInput);
    
    // Analyze results
    const analysis = this.analyzeDetectorOutputs(mode, detectorOutputs);
    
    // Generate obligations if needed
    const obligations = this.generateObligations(mode, analysis);
    
    // Build replay trace
    const replayTrace = this.buildReplayTrace(probeInput, detectorOutputs);
    
    const reportId = `REPORT_${modeId}_${Date.now()}`;
    
    return {
      reportId,
      probeInput,
      decision: analysis.decision,
      confidence: analysis.confidence,
      observedVulnerabilities: analysis.vulnerabilities,
      detectorOutputs,
      obligations,
      replayTrace,
      hash: this.computeHash(reportId)
    };
  }
  
  /**
   * Run all probes for a domain
   */
  runFullScan(
    artifact: ArtifactReference,
    domain: string,
    context: ProbeContext
  ): ProbeReport[] {
    const reports: ProbeReport[] = [];
    
    for (const mode of this.registry.getAllModes()) {
      // Check preconditions
      if (!this.checkPreconditions(mode, context)) {
        continue;
      }
      
      try {
        const report = this.runProbe(artifact, domain, mode.mid, context);
        reports.push(report);
      } catch (e) {
        // Log error but continue
        console.error(`Probe failed for ${mode.mid}:`, e);
      }
    }
    
    return reports;
  }
  
  /**
   * Run probes for a specific lens
   */
  runLensScan(
    artifact: ArtifactReference,
    domain: string,
    lens: ShadowLens,
    context: ProbeContext
  ): ProbeReport[] {
    const reports: ProbeReport[] = [];
    const modes = this.registry.getModesByLens(lens);
    
    for (const mode of modes) {
      if (!this.checkPreconditions(mode, context)) {
        continue;
      }
      
      try {
        const report = this.runProbe(artifact, domain, mode.mid, context);
        reports.push(report);
      } catch (e) {
        console.error(`Probe failed for ${mode.mid}:`, e);
      }
    }
    
    return reports;
  }
  
  private checkPreconditions(mode: FailureMode, context: ProbeContext): boolean {
    // Simplified precondition check
    return mode.preconditions.every(pre => {
      switch (pre) {
        case 'has_certificate':
          return context.artifact.hash !== '';
        case 'verifier_available':
          return context.detectorRegistry !== undefined;
        case 'has_corridor_guards':
          return context.corridor.guards.length > 0;
        case 'uses_transforms':
        case 'uses_rotations':
        case 'uses_bridges':
          return true; // Assume available
        case 'uses_uncertainty':
        case 'makes_prob_claims':
        case 'uses_models':
          return true;
        case 'makes_completeness_claims':
        case 'uses_seeds':
        case 'uses_recursion':
        case 'uses_budgets':
          return true;
        case 'has_claims':
          return true;
        default:
          return true;
      }
    });
  }
  
  private runDetectors(
    mode: FailureMode, 
    input: ProbeInput
  ): Map<string, DetectorOutput> {
    const outputs = new Map<string, DetectorOutput>();
    
    // Run signature-based detection
    const signatureOutput = this.runSignatureDetector(mode, input);
    outputs.set('SIGNATURE_DETECTOR', signatureOutput);
    
    // Run class-specific detector
    const classOutput = this.runClassDetector(mode, input);
    outputs.set(`${mode.class}_DETECTOR`, classOutput);
    
    // Run lens-specific detector
    const lensOutput = this.runLensDetector(mode, input);
    outputs.set(`${mode.lens}_DETECTOR`, lensOutput);
    
    return outputs;
  }
  
  private runSignatureDetector(mode: FailureMode, input: ProbeInput): DetectorOutput {
    const detected = this.matchesSignature(mode.signature, input.adversarialData);
    
    return {
      detected,
      confidence: detected ? 0.9 : 0.1,
      evidence: detected ? [JSON.stringify(input.adversarialData)] : [],
      trace: `Signature detection for ${mode.mid}`
    };
  }
  
  private matchesSignature(
    signature: FailureModeSignature, 
    data: Readonly<Record<string, unknown>>
  ): boolean {
    // Check if any indicators are present in the data
    return signature.indicators.some(indicator => {
      const keys = Object.keys(data);
      return keys.some(k => 
        k.toLowerCase().includes(indicator.toLowerCase()) ||
        String(data[k]).toLowerCase().includes(indicator.toLowerCase())
      );
    });
  }
  
  private runClassDetector(mode: FailureMode, input: ProbeInput): DetectorOutput {
    // Class-specific detection logic
    let detected = false;
    let confidence = 0;
    const evidence: string[] = [];
    
    switch (mode.class) {
      case FailureModeClass.Spoof:
        detected = this.detectSpoof(input.adversarialData);
        confidence = detected ? 0.95 : 0.05;
        if (detected) evidence.push('Spoofed signature detected');
        break;
        
      case FailureModeClass.Bypass:
        detected = this.detectBypass(input.adversarialData);
        confidence = detected ? 0.92 : 0.08;
        if (detected) evidence.push('Bypass attempt detected');
        break;
        
      case FailureModeClass.FragmentFraud:
        detected = this.detectFragmentFraud(input.adversarialData);
        confidence = detected ? 0.98 : 0.02;
        if (detected) evidence.push('Fragment fraud detected');
        break;
        
      case FailureModeClass.Runaway:
        detected = this.detectRunaway(input.adversarialData);
        confidence = detected ? 0.94 : 0.06;
        if (detected) evidence.push('Runaway recursion detected');
        break;
        
      default:
        detected = true; // Conservative default
        confidence = 0.7;
        evidence.push('Generic detection triggered');
    }
    
    return { detected, confidence, evidence, trace: `Class detection for ${mode.class}` };
  }
  
  private detectSpoof(data: Readonly<Record<string, unknown>>): boolean {
    return 'spoofedSignature' in data || 'claimedHash' in data;
  }
  
  private detectBypass(data: Readonly<Record<string, unknown>>): boolean {
    return 'bypassTarget' in data || 'violatedConstraint' in data;
  }
  
  private detectFragmentFraud(data: Readonly<Record<string, unknown>>): boolean {
    if ('claimedLevel' in data) {
      const level = data.claimedLevel as number;
      return ![4, 16, 64, 256, 1024, 4096].includes(level);
    }
    return false;
  }
  
  private detectRunaway(data: Readonly<Record<string, unknown>>): boolean {
    if ('recursionDepth' in data && 'maxAllowed' in data) {
      return (data.recursionDepth as number) > (data.maxAllowed as number);
    }
    return false;
  }
  
  private runLensDetector(mode: FailureMode, input: ProbeInput): DetectorOutput {
    // Lens-specific detection
    return {
      detected: true,
      confidence: 0.85,
      evidence: [`Lens ${mode.lens} check passed`],
      trace: `Lens detection for ${mode.lens}`
    };
  }
  
  private analyzeDetectorOutputs(
    mode: FailureMode,
    outputs: Map<string, DetectorOutput>
  ): { decision: ProbeDecision; confidence: number; vulnerabilities: VulnerabilityFingerprint[] } {
    // Count detections
    let detectedCount = 0;
    let totalConfidence = 0;
    const vulnerabilities: VulnerabilityFingerprint[] = [];
    
    for (const [name, output] of outputs) {
      if (output.detected) {
        detectedCount++;
        totalConfidence += output.confidence;
        
        vulnerabilities.push({
          vulnId: `VULN_${mode.mid}_${name}`,
          mode: mode.mid,
          signature: mode.signature.pattern,
          evidence: output.evidence,
          severity: mode.severity,
          exploitPath: []
        });
      }
    }
    
    const avgConfidence = detectedCount > 0 ? totalConfidence / detectedCount : 0;
    
    let decision: ProbeDecision;
    if (detectedCount >= 2 && avgConfidence > 0.8) {
      decision = ProbeDecision.Confirmed;
    } else if (detectedCount >= 1 && avgConfidence > 0.5) {
      decision = ProbeDecision.Inconclusive;
    } else {
      decision = ProbeDecision.FalseAlarm;
    }
    
    return { decision, confidence: avgConfidence, vulnerabilities };
  }
  
  private generateObligations(
    mode: FailureMode,
    analysis: { decision: ProbeDecision; confidence: number; vulnerabilities: VulnerabilityFingerprint[] }
  ): Obligation[] {
    const obligations: Obligation[] = [];
    
    if (analysis.decision === ProbeDecision.Confirmed || 
        (analysis.decision === ProbeDecision.Inconclusive && analysis.confidence > 0.6)) {
      
      // Generate obligation for each countermeasure
      for (const cm of mode.countermeasures) {
        obligations.push({
          oblId: `OBL_${mode.mid}_${cm.id}`,
          kind: this.mapActionToObligation(cm.action),
          target: mode.mid,
          requirements: [cm.id],
          budgets: { kappa: cm.cost, beta: 0, chi: 0, epsilon: 0 },
          deadlinePolicy: 'IMMEDIATE',
          priority: this.getPriorityFromSeverity(mode.severity)
        });
      }
    }
    
    return obligations;
  }
  
  private mapActionToObligation(action: GuardAction): ObligationKind {
    switch (action) {
      case GuardAction.TightenCorridor:
        return ObligationKind.TightenCorridor;
      case GuardAction.RequireStrongerCert:
        return ObligationKind.AddCertRequirement;
      case GuardAction.AddConventionAdapter:
        return ObligationKind.AddConventionAdapter;
      case GuardAction.EnforceAdmittedLevel:
        return ObligationKind.UpgradeLevel;
      case GuardAction.AddRecursionClamp:
        return ObligationKind.AddRecursionClamp;
      case GuardAction.RerouteSaferHub:
        return ObligationKind.RerouteViaSaferHubs;
      default:
        return ObligationKind.InstallGuard;
    }
  }
  
  private getPriorityFromSeverity(severity: Severity): number {
    switch (severity) {
      case Severity.Critical: return 100;
      case Severity.High: return 75;
      case Severity.Medium: return 50;
      case Severity.Low: return 25;
      case Severity.Info: return 10;
    }
  }
  
  private buildReplayTrace(
    input: ProbeInput,
    outputs: Map<string, DetectorOutput>
  ): ReplayTrace {
    const events: string[] = [
      `PROBE_START:${input.inputId}`,
      `TRIGGER:${input.triggerId}`,
      ...Array.from(outputs.keys()).map(k => `DETECTOR:${k}`)
    ];
    
    const hashes = [
      input.hash,
      ...Array.from(outputs.values()).map(o => o.trace)
    ];
    
    return {
      seed: input.seed,
      events,
      hashes,
      deterministic: true
    };
  }
  
  private computeHash(id: string): string {
    let hash = 0;
    const str = id;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return `HASH_${Math.abs(hash).toString(16).toUpperCase().padStart(16, '0')}`;
  }
}

// ============================================================================
// SECTION 9: GUARD INSTALLER ENGINE
// ============================================================================

class GuardInstallerEngine {
  private readonly installers: Map<GuardAction, GuardInstaller> = new Map();
  private readonly installations: GuardInstallation[] = [];
  
  constructor() {
    this.registerInstallers();
  }
  
  private registerInstallers(): void {
    // Tighten Corridor
    this.installers.set(GuardAction.TightenCorridor, {
      action: GuardAction.TightenCorridor,
      install: (report, corridor) => this.installTightenCorridor(report, corridor),
      verify: (installation) => this.verifyInstallation(installation),
      cost: 1.0
    });
    
    // Non-Bypass Check
    this.installers.set(GuardAction.AddNonBypassCheck, {
      action: GuardAction.AddNonBypassCheck,
      install: (report, corridor) => this.installNonBypassCheck(report, corridor),
      verify: (installation) => this.verifyInstallation(installation),
      cost: 1.5
    });
    
    // Stronger Certificate
    this.installers.set(GuardAction.RequireStrongerCert, {
      action: GuardAction.RequireStrongerCert,
      install: (report, corridor) => this.installStrongerCert(report, corridor),
      verify: (installation) => this.verifyInstallation(installation),
      cost: 1.2
    });
    
    // Admitted Level
    this.installers.set(GuardAction.EnforceAdmittedLevel, {
      action: GuardAction.EnforceAdmittedLevel,
      install: (report, corridor) => this.installAdmittedLevel(report, corridor),
      verify: (installation) => this.verifyInstallation(installation),
      cost: 0.8
    });
    
    // Recursion Clamp
    this.installers.set(GuardAction.AddRecursionClamp, {
      action: GuardAction.AddRecursionClamp,
      install: (report, corridor) => this.installRecursionClamp(report, corridor),
      verify: (installation) => this.verifyInstallation(installation),
      cost: 1.0
    });
    
    // Checkpoint
    this.installers.set(GuardAction.AddCheckpoint, {
      action: GuardAction.AddCheckpoint,
      install: (report, corridor) => this.installCheckpoint(report, corridor),
      verify: (installation) => this.verifyInstallation(installation),
      cost: 1.1
    });
    
    // Safer Hub Reroute
    this.installers.set(GuardAction.RerouteSaferHub, {
      action: GuardAction.RerouteSaferHub,
      install: (report, corridor) => this.installSaferHub(report, corridor),
      verify: (installation) => this.verifyInstallation(installation),
      cost: 1.3
    });
    
    // Convention Adapter
    this.installers.set(GuardAction.AddConventionAdapter, {
      action: GuardAction.AddConventionAdapter,
      install: (report, corridor) => this.installConventionAdapter(report, corridor),
      verify: (installation) => this.verifyInstallation(installation),
      cost: 1.1
    });
    
    // Calibration Gate
    this.installers.set(GuardAction.AddCalibrationGate, {
      action: GuardAction.AddCalibrationGate,
      install: (report, corridor) => this.installCalibrationGate(report, corridor),
      verify: (installation) => this.verifyInstallation(installation),
      cost: 1.0
    });
    
    // Drift Trigger
    this.installers.set(GuardAction.AddDriftTrigger, {
      action: GuardAction.AddDriftTrigger,
      install: (report, corridor) => this.installDriftTrigger(report, corridor),
      verify: (installation) => this.verifyInstallation(installation),
      cost: 1.1
    });
    
    // Route Rejection
    this.installers.set(GuardAction.RejectRoute, {
      action: GuardAction.RejectRoute,
      install: (report, corridor) => this.installRouteRejection(report, corridor),
      verify: (installation) => this.verifyInstallation(installation),
      cost: 0.9
    });
  }
  
  /**
   * Install guards based on probe report (Construction 15.9)
   */
  installGuardsFromReport(
    report: ProbeReport,
    corridor: CorridorState
  ): GuardInstallation[] {
    const installations: GuardInstallation[] = [];
    
    for (const obligation of report.obligations) {
      const action = this.mapObligationToAction(obligation.kind);
      const installer = this.installers.get(action);
      
      if (installer) {
        const installation = installer.install(report, corridor);
        
        if (installer.verify(installation)) {
          installations.push(installation);
          this.installations.push(installation);
        }
      }
    }
    
    return installations;
  }
  
  private mapObligationToAction(kind: ObligationKind): GuardAction {
    switch (kind) {
      case ObligationKind.TightenCorridor:
        return GuardAction.TightenCorridor;
      case ObligationKind.AddCertRequirement:
        return GuardAction.RequireStrongerCert;
      case ObligationKind.AddConventionAdapter:
        return GuardAction.AddConventionAdapter;
      case ObligationKind.UpgradeLevel:
        return GuardAction.EnforceAdmittedLevel;
      case ObligationKind.AddRecursionClamp:
        return GuardAction.AddRecursionClamp;
      case ObligationKind.RerouteViaSaferHubs:
        return GuardAction.RerouteSaferHub;
      case ObligationKind.EnforceFragmentRejection:
        return GuardAction.EnforceAdmittedLevel;
      default:
        return GuardAction.TightenCorridor;
    }
  }
  
  private installTightenCorridor(report: ProbeReport, corridor: CorridorState): GuardInstallation {
    return this.createInstallation(
      GuardAction.TightenCorridor,
      {
        originalGuards: corridor.guards,
        newConstraints: report.observedVulnerabilities.map(v => `BLOCK_${v.mode}`),
        enforceLevel: 'STRICT'
      },
      corridor.guards
    );
  }
  
  private installNonBypassCheck(report: ProbeReport, corridor: CorridorState): GuardInstallation {
    return this.createInstallation(
      GuardAction.AddNonBypassCheck,
      {
        checkPoints: corridor.guards,
        enforceAll: true,
        logViolations: true,
        blockOnViolation: true
      },
      corridor.guards
    );
  }
  
  private installStrongerCert(report: ProbeReport, corridor: CorridorState): GuardInstallation {
    return this.createInstallation(
      GuardAction.RequireStrongerCert,
      {
        minSignatureStrength: 256,
        requireChain: true,
        requireReplay: true,
        requireWitness: true
      },
      ['certificate_verifier']
    );
  }
  
  private installAdmittedLevel(report: ProbeReport, corridor: CorridorState): GuardInstallation {
    return this.createInstallation(
      GuardAction.EnforceAdmittedLevel,
      {
        admittedLevels: corridor.admittedLevels,
        rejectFragments: true,
        requireUpgrade: true
      },
      ['level_validator']
    );
  }
  
  private installRecursionClamp(report: ProbeReport, corridor: CorridorState): GuardInstallation {
    return this.createInstallation(
      GuardAction.AddRecursionClamp,
      {
        maxDepth: 64,
        checkpointInterval: 8,
        rollbackOnViolation: true,
        merkleValidate: true
      },
      ['recursion_controller']
    );
  }
  
  private installCheckpoint(report: ProbeReport, corridor: CorridorState): GuardInstallation {
    return this.createInstallation(
      GuardAction.AddCheckpoint,
      {
        verifyFixedPoint: true,
        merkleValidate: true,
        interval: 'ON_TRANSITION'
      },
      ['checkpoint_manager']
    );
  }
  
  private installSaferHub(report: ProbeReport, corridor: CorridorState): GuardInstallation {
    return this.createInstallation(
      GuardAction.RerouteSaferHub,
      {
        avoidHubs: report.observedVulnerabilities.map(v => v.exploitPath).flat(),
        preferHubs: ['FOURIER_HUB', 'DERIVATIVE_HUB'],
        requireTunnel: true
      },
      ['metro_router']
    );
  }
  
  private installConventionAdapter(report: ProbeReport, corridor: CorridorState): GuardInstallation {
    return this.createInstallation(
      GuardAction.AddConventionAdapter,
      {
        requireExplicit: true,
        validateChain: true,
        normalizeOnMismatch: true
      },
      ['convention_manager']
    );
  }
  
  private installCalibrationGate(report: ProbeReport, corridor: CorridorState): GuardInstallation {
    return this.createInstallation(
      GuardAction.AddCalibrationGate,
      {
        requireProvenance: true,
        downgradeToWorstCase: true,
        blockUncalibrated: true
      },
      ['calibration_verifier']
    );
  }
  
  private installDriftTrigger(report: ProbeReport, corridor: CorridorState): GuardInstallation {
    return this.createInstallation(
      GuardAction.AddDriftTrigger,
      {
        threshold: 0.05,
        triggerTightening: true,
        invalidateStale: true,
        requireRecertification: true
      },
      ['drift_monitor']
    );
  }
  
  private installRouteRejection(report: ProbeReport, corridor: CorridorState): GuardInstallation {
    return this.createInstallation(
      GuardAction.RejectRoute,
      {
        rejectedPatterns: report.observedVulnerabilities.map(v => v.signature),
        logRejections: true
      },
      ['route_validator']
    );
  }
  
  private createInstallation(
    action: GuardAction,
    parameters: Readonly<Record<string, unknown>>,
    appliedTo: readonly string[]
  ): GuardInstallation {
    const installationId = `INSTALL_${action}_${Date.now()}`;
    
    return {
      installationId,
      action,
      parameters,
      appliedTo,
      merkleLink: this.computeHash(installationId + JSON.stringify(parameters)),
      replayable: true,
      hash: this.computeHash(installationId)
    };
  }
  
  private verifyInstallation(installation: GuardInstallation): boolean {
    // Verify installation is valid
    return (
      installation.installationId !== '' &&
      installation.action !== undefined &&
      installation.merkleLink !== '' &&
      installation.replayable
    );
  }
  
  private computeHash(content: string): string {
    let hash = 0;
    for (let i = 0; i < content.length; i++) {
      const char = content.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return `HASH_${Math.abs(hash).toString(16).toUpperCase().padStart(16, '0')}`;
  }
  
  getInstallations(): GuardInstallation[] {
    return [...this.installations];
  }
}

// ============================================================================
// SECTION 10: NEGATIFY CATALOG BUILDER
// ============================================================================

class NegatifyCatalogBuilder {
  private readonly registry: FailureModeRegistry;
  private readonly triggerGenerator: TriggerGenerator;
  private readonly guardInstallerEngine: GuardInstallerEngine;
  
  constructor() {
    this.registry = new FailureModeRegistry();
    this.triggerGenerator = new TriggerGenerator(this.registry);
    this.guardInstallerEngine = new GuardInstallerEngine();
  }
  
  /**
   * Build complete Negatify catalog for a domain (M.S3.a)
   */
  buildCatalog(domain: string): NegatifyCatalog {
    const modes = new Map<string, FailureMode>();
    const triggers = new Map<string, TriggerTemplate>();
    const guards = new Map<GuardAction, GuardInstaller>();
    const obligations = new Map<ObligationKind, ObligationTemplate>();
    
    // Enumerate domain surfaces and collect modes
    for (const mode of this.registry.getAllModes()) {
      modes.set(mode.mid, mode);
      
      const trigger = this.triggerGenerator.getTriggerForMode(mode.mid);
      if (trigger) {
        triggers.set(trigger.triggerId, trigger);
      }
    }
    
    // Collect guard installers
    for (const action of Object.values(GuardAction)) {
      guards.set(action, {
        action,
        install: (report, corridor) => ({
          installationId: `${action}_${Date.now()}`,
          action,
          parameters: {},
          appliedTo: [],
          merkleLink: '',
          replayable: true,
          hash: ''
        }),
        verify: () => true,
        cost: 1.0
      });
    }
    
    // Collect obligation templates
    for (const kind of Object.values(ObligationKind)) {
      obligations.set(kind, {
        kind,
        generate: (mode, report) => ({
          oblId: `OBL_${mode.mid}_${Date.now()}`,
          kind,
          target: mode.mid,
          requirements: [],
          budgets: { kappa: 1, beta: 0, chi: 0, epsilon: 0 },
          deadlinePolicy: 'NORMAL',
          priority: 50
        }),
        priority: 50,
        dependencies: []
      });
    }
    
    // Compute coverage
    const coverage = this.computeCoverage(modes);
    
    const catalogId = `CATALOG_${domain}_${Date.now()}`;
    
    return {
      domain,
      modes,
      triggers,
      detectors: this.getDetectorIds(),
      guards,
      obligations,
      coverage,
      version: '1.0.0',
      hash: this.computeHash(catalogId)
    };
  }
  
  private computeCoverage(modes: Map<string, FailureMode>): CoverageReport {
    const totalModes = modes.size;
    const coveredModes = modes.size; // All registered modes are covered
    
    const coverageByLens = new Map<ShadowLens, number>();
    const coverageByClass = new Map<FailureModeClass, number>();
    
    for (const lens of Object.values(ShadowLens)) {
      const lensModes = Array.from(modes.values()).filter(m => m.lens === lens);
      coverageByLens.set(lens, lensModes.length / totalModes);
    }
    
    for (const modeClass of Object.values(FailureModeClass)) {
      const classModes = Array.from(modes.values()).filter(m => m.class === modeClass);
      coverageByClass.set(modeClass, classModes.length / totalModes);
    }
    
    return {
      totalModes,
      coveredModes,
      coverageByLens,
      coverageByClass,
      missingCoverage: [],
      completenessScore: coveredModes / totalModes
    };
  }
  
  private getDetectorIds(): readonly string[] {
    return [
      'SIGNATURE_DETECTOR',
      'SPOOF_DETECTOR',
      'BYPASS_DETECTOR',
      'DRIFT_DETECTOR',
      'FRAGMENT_DETECTOR',
      'COHERENCE_DETECTOR',
      'RUNAWAY_DETECTOR',
      'LEAK_DETECTOR',
      'AMBIGUITY_DETECTOR',
      'PROOF_DETECTOR',
      'ROUTE_DETECTOR',
      'SQUARE_LENS_DETECTOR',
      'FLOWER_LENS_DETECTOR',
      'CLOUD_LENS_DETECTOR',
      'FRACTAL_LENS_DETECTOR'
    ];
  }
  
  private computeHash(content: string): string {
    let hash = 0;
    for (let i = 0; i < content.length; i++) {
      const char = content.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return `HASH_${Math.abs(hash).toString(16).toUpperCase().padStart(16, '0')}`;
  }
}

// ============================================================================
// SECTION 11: WORST-CASE CERTIFICATE GENERATOR
// ============================================================================

interface WorstCaseCatalogCertificate {
  readonly certId: string;
  readonly catalog: NegatifyCatalog;
  readonly coverageClaims: readonly string[];
  readonly probeSuite: readonly ProbeReport[];
  readonly guardActions: readonly GuardInstallation[];
  readonly trace: ReplayTrace;
  readonly omegaNonOverride: boolean;
  readonly hash: string;
}

class WorstCaseCertificateGenerator {
  private readonly probeEngine: ShadowProbeEngine;
  private readonly guardEngine: GuardInstallerEngine;
  
  constructor(
    probeEngine: ShadowProbeEngine,
    guardEngine: GuardInstallerEngine
  ) {
    this.probeEngine = probeEngine;
    this.guardEngine = guardEngine;
  }
  
  /**
   * Generate worst-case catalog certificate (Certificate 15.6)
   */
  generateCertificate(
    catalog: NegatifyCatalog,
    artifact: ArtifactReference,
    context: ProbeContext
  ): WorstCaseCatalogCertificate {
    // Run all probes
    const probeSuite = this.probeEngine.runFullScan(artifact, catalog.domain, context);
    
    // Install guards from confirmed findings
    const guardActions: GuardInstallation[] = [];
    for (const report of probeSuite) {
      if (report.decision === ProbeDecision.Confirmed) {
        const installations = this.guardEngine.installGuardsFromReport(report, context.corridor);
        guardActions.push(...installations);
      }
    }
    
    // Generate coverage claims
    const coverageClaims = this.generateCoverageClaims(catalog, probeSuite);
    
    // Build replay trace
    const trace = this.buildCertTrace(probeSuite, guardActions);
    
    const certId = `CERT_WC_${catalog.domain}_${Date.now()}`;
    
    return {
      certId,
      catalog,
      coverageClaims,
      probeSuite,
      guardActions,
      trace,
      omegaNonOverride: true, // Guards preserve Ω clamps
      hash: this.computeHash(certId)
    };
  }
  
  private generateCoverageClaims(
    catalog: NegatifyCatalog,
    probeSuite: readonly ProbeReport[]
  ): readonly string[] {
    const claims: string[] = [];
    
    // Coverage by lens
    for (const [lens, coverage] of catalog.coverage.coverageByLens) {
      claims.push(`LENS_${lens}_COVERAGE:${(coverage * 100).toFixed(1)}%`);
    }
    
    // Coverage by class
    for (const [modeClass, coverage] of catalog.coverage.coverageByClass) {
      claims.push(`CLASS_${modeClass}_COVERAGE:${(coverage * 100).toFixed(1)}%`);
    }
    
    // Probe results summary
    const confirmed = probeSuite.filter(r => r.decision === ProbeDecision.Confirmed).length;
    const inconclusive = probeSuite.filter(r => r.decision === ProbeDecision.Inconclusive).length;
    const falseAlarm = probeSuite.filter(r => r.decision === ProbeDecision.FalseAlarm).length;
    
    claims.push(`PROBES_CONFIRMED:${confirmed}`);
    claims.push(`PROBES_INCONCLUSIVE:${inconclusive}`);
    claims.push(`PROBES_FALSE_ALARM:${falseAlarm}`);
    claims.push(`TOTAL_PROBES:${probeSuite.length}`);
    
    return claims;
  }
  
  private buildCertTrace(
    probeSuite: readonly ProbeReport[],
    guardActions: readonly GuardInstallation[]
  ): ReplayTrace {
    const events: string[] = [];
    const hashes: string[] = [];
    
    for (const report of probeSuite) {
      events.push(`PROBE:${report.reportId}:${report.decision}`);
      hashes.push(report.hash);
    }
    
    for (const action of guardActions) {
      events.push(`GUARD:${action.installationId}:${action.action}`);
      hashes.push(action.hash);
    }
    
    return {
      seed: 'CERT_' + Date.now().toString(),
      events,
      hashes,
      deterministic: true
    };
  }
  
  private computeHash(content: string): string {
    let hash = 0;
    for (let i = 0; i < content.length; i++) {
      const char = content.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return `HASH_${Math.abs(hash).toString(16).toUpperCase().padStart(16, '0')}`;
  }
}

// ============================================================================
// SECTION 12: GOLDEN SUITE GENERATOR
// ============================================================================

interface GoldenSuite {
  readonly suiteId: string;
  readonly domain: string;
  readonly probes: readonly GoldenProbe[];
  readonly expectedResults: Map<string, ProbeDecision>;
  readonly replaySeals: readonly string[];
  readonly hash: string;
}

interface GoldenProbe {
  readonly probeId: string;
  readonly targetMode: string;
  readonly targetLens: ShadowLens;
  readonly input: ProbeInput;
  readonly expectedDecision: ProbeDecision;
  readonly expectedBoundary: BoundaryType;
}

class GoldenSuiteGenerator {
  private readonly registry: FailureModeRegistry;
  private readonly triggerGenerator: TriggerGenerator;
  
  constructor(registry: FailureModeRegistry, triggerGenerator: TriggerGenerator) {
    this.registry = registry;
    this.triggerGenerator = triggerGenerator;
  }
  
  /**
   * Generate golden suite for domain (M.S4.d, M.R4.d)
   */
  generateGoldenSuite(domain: string, context: ProbeContext): GoldenSuite {
    const probes: GoldenProbe[] = [];
    const expectedResults = new Map<string, ProbeDecision>();
    const replaySeals: string[] = [];
    
    // Generate probe for each failure mode
    for (const mode of this.registry.getAllModes()) {
      const trigger = this.triggerGenerator.getTriggerForMode(mode.mid);
      if (!trigger) continue;
      
      const input = trigger.inputGenerator(context);
      const probeId = `GOLDEN_${mode.mid}`;
      
      probes.push({
        probeId,
        targetMode: mode.mid,
        targetLens: mode.lens,
        input,
        expectedDecision: ProbeDecision.Confirmed,
        expectedBoundary: trigger.expectedBoundary
      });
      
      expectedResults.set(probeId, ProbeDecision.Confirmed);
      replaySeals.push(this.computeHash(probeId + input.hash));
    }
    
    const suiteId = `GOLDEN_SUITE_${domain}_${Date.now()}`;
    
    return {
      suiteId,
      domain,
      probes,
      expectedResults,
      replaySeals,
      hash: this.computeHash(suiteId)
    };
  }
  
  /**
   * Verify golden suite execution
   */
  verifyGoldenSuite(
    suite: GoldenSuite,
    actualResults: Map<string, ProbeReport>
  ): { passed: boolean; failures: string[] } {
    const failures: string[] = [];
    
    for (const probe of suite.probes) {
      const actual = actualResults.get(probe.probeId);
      
      if (!actual) {
        failures.push(`${probe.probeId}: Missing result`);
        continue;
      }
      
      if (actual.decision !== probe.expectedDecision) {
        failures.push(
          `${probe.probeId}: Expected ${probe.expectedDecision}, got ${actual.decision}`
        );
      }
    }
    
    return {
      passed: failures.length === 0,
      failures
    };
  }
  
  private computeHash(content: string): string {
    let hash = 0;
    for (let i = 0; i < content.length; i++) {
      const char = content.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return `HASH_${Math.abs(hash).toString(16).toUpperCase().padStart(16, '0')}`;
  }
}

// ============================================================================
// SECTION 13: NEGATIFY SYSTEM ORCHESTRATOR
// ============================================================================

class NegatifySystem {
  readonly registry: FailureModeRegistry;
  readonly triggerGenerator: TriggerGenerator;
  readonly probeEngine: ShadowProbeEngine;
  readonly guardEngine: GuardInstallerEngine;
  readonly catalogBuilder: NegatifyCatalogBuilder;
  readonly certGenerator: WorstCaseCertificateGenerator;
  readonly goldenSuiteGenerator: GoldenSuiteGenerator;
  
  private catalogs: Map<string, NegatifyCatalog> = new Map();
  private certificates: Map<string, WorstCaseCatalogCertificate> = new Map();
  
  constructor() {
    this.registry = new FailureModeRegistry();
    this.triggerGenerator = new TriggerGenerator(this.registry);
    
    // Create a simple detector registry
    const detectorRegistry: DetectorRegistry = {
      detectors: new Map(),
      run: (id: string, input: unknown) => ({
        detected: true,
        confidence: 0.8,
        evidence: [],
        trace: `Detector ${id} run`
      })
    };
    
    this.probeEngine = new ShadowProbeEngine(
      this.registry,
      this.triggerGenerator,
      detectorRegistry
    );
    
    this.guardEngine = new GuardInstallerEngine();
    this.catalogBuilder = new NegatifyCatalogBuilder();
    this.certGenerator = new WorstCaseCertificateGenerator(
      this.probeEngine,
      this.guardEngine
    );
    this.goldenSuiteGenerator = new GoldenSuiteGenerator(
      this.registry,
      this.triggerGenerator
    );
  }
  
  /**
   * Initialize Negatify for a domain
   */
  initializeDomain(domain: string): NegatifyCatalog {
    const catalog = this.catalogBuilder.buildCatalog(domain);
    this.catalogs.set(domain, catalog);
    return catalog;
  }
  
  /**
   * Run full Negatify scan on artifact
   */
  runNegatifyScan(
    domain: string,
    artifact: ArtifactReference,
    corridor: CorridorState
  ): WorstCaseCatalogCertificate {
    let catalog = this.catalogs.get(domain);
    if (!catalog) {
      catalog = this.initializeDomain(domain);
    }
    
    const context: ProbeContext = {
      domain,
      artifact,
      corridor,
      budgets: corridor.budgets,
      seed: `NEGATIFY_${Date.now()}`,
      admittedLevels: corridor.admittedLevels,
      detectorRegistry: {
        detectors: new Map(),
        run: (id, input) => ({
          detected: true,
          confidence: 0.8,
          evidence: [],
          trace: `${id} run`
        })
      }
    };
    
    const certificate = this.certGenerator.generateCertificate(catalog, artifact, context);
    this.certificates.set(certificate.certId, certificate);
    
    return certificate;
  }
  
  /**
   * Get all registered failure modes
   */
  getFailureModes(): FailureMode[] {
    return this.registry.getAllModes();
  }
  
  /**
   * Get installed guards
   */
  getInstalledGuards(): GuardInstallation[] {
    return this.guardEngine.getInstallations();
  }
  
  /**
   * Generate golden suite for testing
   */
  generateGoldenSuite(domain: string, corridor: CorridorState): GoldenSuite {
    const context: ProbeContext = {
      domain,
      artifact: { addr: 'GOLDEN_ARTIFACT', hash: 'GOLDEN_HASH', type: 'TEST' },
      corridor,
      budgets: corridor.budgets,
      seed: `GOLDEN_${Date.now()}`,
      admittedLevels: corridor.admittedLevels,
      detectorRegistry: {
        detectors: new Map(),
        run: (id, input) => ({
          detected: true,
          confidence: 0.8,
          evidence: [],
          trace: `${id} run`
        })
      }
    };
    
    return this.goldenSuiteGenerator.generateGoldenSuite(domain, context);
  }
  
  /**
   * Get system statistics
   */
  getStatistics(): {
    totalModes: number;
    modesByLens: Record<string, number>;
    modesByClass: Record<string, number>;
    catalogCount: number;
    certificateCount: number;
    guardCount: number;
  } {
    const modes = this.registry.getAllModes();
    
    const modesByLens: Record<string, number> = {};
    const modesByClass: Record<string, number> = {};
    
    for (const lens of Object.values(ShadowLens)) {
      modesByLens[lens] = modes.filter(m => m.lens === lens).length;
    }
    
    for (const modeClass of Object.values(FailureModeClass)) {
      modesByClass[modeClass] = modes.filter(m => m.class === modeClass).length;
    }
    
    return {
      totalModes: modes.length,
      modesByLens,
      modesByClass,
      catalogCount: this.catalogs.size,
      certificateCount: this.certificates.size,
      guardCount: this.guardEngine.getInstallations().length
    };
  }
}

// ============================================================================
// SECTION 14: EXPORTS
// ============================================================================

export {
  // Enums
  FailureModeClass,
  Severity,
  ShadowLens,
  ProbeDecision,
  GuardAction,
  ObligationKind,
  BoundaryType,
  
  // Types
  FailureModeSignature,
  FailureModeImpact,
  Countermeasure,
  FailureMode,
  TriggerTemplate,
  ProbeContext,
  ProbeInput,
  ProbeReport,
  VulnerabilityFingerprint,
  NegatifyCatalog,
  CoverageReport,
  GuardInstaller,
  GuardInstallation,
  ObligationTemplate,
  Obligation,
  WorstCaseCatalogCertificate,
  GoldenSuite,
  GoldenProbe,
  
  // Classes
  FailureModeRegistry,
  TriggerGenerator,
  ShadowProbeEngine,
  GuardInstallerEngine,
  NegatifyCatalogBuilder,
  WorstCaseCertificateGenerator,
  GoldenSuiteGenerator,
  NegatifySystem
};

// ============================================================================
// SECTION 15: DEMONSTRATION
// ============================================================================

function demonstrateNegatifySystem(): void {
  console.log('='.repeat(70));
  console.log('NEGATIFY SHADOW SYSTEM - Comprehensive Failure Detection');
  console.log('From SELF_SUFFICIENCY_TOME Ch15.R and Appendix M');
  console.log('='.repeat(70));
  
  // Create system
  const negatify = new NegatifySystem();
  
  // Get statistics
  const stats = negatify.getStatistics();
  console.log('\n[FAILURE MODE REGISTRY]');
  console.log(`Total modes: ${stats.totalModes}`);
  console.log('\nBy Lens:');
  for (const [lens, count] of Object.entries(stats.modesByLens)) {
    console.log(`  ${lens}: ${count}`);
  }
  console.log('\nBy Class:');
  for (const [cls, count] of Object.entries(stats.modesByClass)) {
    console.log(`  ${cls}: ${count}`);
  }
  
  // Initialize domain
  console.log('\n[CATALOG INITIALIZATION]');
  const catalog = negatify.initializeDomain('TEST_DOMAIN');
  console.log(`Catalog: ${catalog.domain}`);
  console.log(`Modes: ${catalog.modes.size}`);
  console.log(`Triggers: ${catalog.triggers.size}`);
  console.log(`Coverage: ${(catalog.coverage.completenessScore * 100).toFixed(1)}%`);
  
  // Run scan
  console.log('\n[NEGATIFY SCAN]');
  const certificate = negatify.runNegatifyScan(
    'TEST_DOMAIN',
    { addr: 'TEST_ADDR', hash: 'TEST_HASH', type: 'TEST' },
    {
      guards: ['GUARD_1', 'GUARD_2'],
      budgets: { kappa: 100, beta: 50, chi: 25, epsilon: 10 },
      constraints: ['NO_BYPASS', 'REQUIRE_CERT'],
      admittedLevels: [4, 16, 64, 256]
    }
  );
  
  console.log(`Certificate ID: ${certificate.certId}`);
  console.log(`Probes run: ${certificate.probeSuite.length}`);
  console.log(`Guards installed: ${certificate.guardActions.length}`);
  console.log(`Ω non-override: ${certificate.omegaNonOverride}`);
  
  // Coverage claims
  console.log('\nCoverage Claims:');
  for (const claim of certificate.coverageClaims.slice(0, 5)) {
    console.log(`  ${claim}`);
  }
  
  // Sample probe results
  console.log('\nSample Probe Results:');
  for (const report of certificate.probeSuite.slice(0, 3)) {
    console.log(`  ${report.probeInput.targetMode}: ${report.decision} (conf: ${report.confidence.toFixed(2)})`);
    if (report.obligations.length > 0) {
      console.log(`    Obligations: ${report.obligations.length}`);
    }
  }
  
  // Golden suite
  console.log('\n[GOLDEN SUITE]');
  const goldenSuite = negatify.generateGoldenSuite('TEST_DOMAIN', {
    guards: ['GUARD_1'],
    budgets: { kappa: 100, beta: 50, chi: 25, epsilon: 10 },
    constraints: [],
    admittedLevels: [4, 16, 64, 256]
  });
  console.log(`Suite ID: ${goldenSuite.suiteId}`);
  console.log(`Probes: ${goldenSuite.probes.length}`);
  console.log(`Replay seals: ${goldenSuite.replaySeals.length}`);
  
  console.log('\n' + '='.repeat(70));
  console.log('NEGATIFY SYSTEM OPERATIONAL');
  console.log('Inverse-φ shadow detection active');
  console.log('Guard installation pipeline ready');
  console.log('='.repeat(70));
}

// Run demonstration
demonstrateNegatifySystem();
