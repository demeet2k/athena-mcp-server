/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * APPENDIX HUB SYSTEM - Complete AppA-AppP Hub Definitions
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * This module implements the complete 16-appendix outer crystal routing system:
 * 
 * AppA - Contract nucleus: addressing, LinkEdge ABI, router v2, truth lattice
 * AppB - Lawbook: rules, rewrite/confluence, clamp rules, obligation templates
 * AppC - Square base: CF/NF, invariants, type registry, canonical equality
 * AppD - Schemas: ClaimPack/TruthRecord/DAG/CandSet/Quarantine ABI
 * AppE - Flower base: operators, hub gates, solve engines, defects
 * AppF - Translation: typed candidate bridges, non-coercion, bridge coherence
 * AppG - Corridor: scope algebra, admissibility predicates, zoom ladders
 * AppH - Constructions: derived objects, discriminators, discharge constructors
 * AppI - Truth kernel: promotion/refutation, evidence discipline, CollapsePack
 * AppJ - NEAR overlay: Δ ledger, tightening ladders, monotone residual
 * AppK - FAIL overlay: quarantine, minimal witness sets, refutation routes
 * AppL - AMBIG overlay: candidate sets, evidence plans, discriminator ranking
 * AppM - Fractal base: canonical serialization, digest discipline, replay/seal
 * AppN - Boundaries: domain capsules, MIGRATE templates, interface checks
 * AppO - Publishing: OK-sealed bundles only, proof-preserving export
 * AppP - Toolchain: deterministic runners, replay CLI, integration tests
 * 
 * @module APPENDIX_HUB_SYSTEM
 * @version 2.0.0
 */

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: HUB TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Hub identifier
 */
export type HubId = 
  | "AppA" | "AppB" | "AppC" | "AppD" 
  | "AppE" | "AppF" | "AppG" | "AppH"
  | "AppI" | "AppJ" | "AppK" | "AppL"
  | "AppM" | "AppN" | "AppO" | "AppP";

/**
 * Hub category
 */
export enum HubCategory {
  Core = "Core",           // AppA, AppI, AppM (mandatory signature Σ)
  LensBase = "LensBase",   // AppC (S), AppE (F), AppI (C), AppM (R)
  FacetBase = "FacetBase", // AppA (1), AppB (2), AppH (3), AppM (4)
  TruthOverlay = "TruthOverlay", // AppJ (NEAR), AppK (FAIL), AppL (AMBIG), AppO (OK pub)
  Functional = "Functional" // AppB, AppD, AppF, AppG, AppN, AppP
}

/**
 * Hub contract
 */
export interface HubContract {
  id: HubId;
  name: string;
  category: HubCategory;
  description: string;
  capabilities: string[];
  dependencies: HubId[];
  provides: ProviderSpec[];
  requires: RequirementSpec[];
}

export interface ProviderSpec {
  name: string;
  type: string;
  description: string;
}

export interface RequirementSpec {
  name: string;
  from: HubId;
  required: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: HUB CONTRACTS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * AppA - Contract Nucleus
 */
export const HUB_APP_A: HubContract = {
  id: "AppA",
  name: "Contract Nucleus",
  category: HubCategory.Core,
  description: "Addressing, LinkEdge ABI, router v2, truth lattice interface",
  capabilities: [
    "GlobalAddr resolution",
    "LinkEdge creation and validation",
    "Router v2 hub computation",
    "Truth lattice operations"
  ],
  dependencies: [],
  provides: [
    { name: "resolveAddress", type: "(LocalAddr) => GlobalAddr", description: "Resolve local to global address" },
    { name: "createLinkEdge", type: "(EdgeSpec) => LinkEdge", description: "Create validated link edge" },
    { name: "computeHubSet", type: "(Route) => HubId[]", description: "Compute router v2 hub set" },
    { name: "truthMeet", type: "(TruthValue, TruthValue) => TruthValue", description: "Truth lattice meet" },
    { name: "truthJoin", type: "(TruthValue, TruthValue) => TruthValue", description: "Truth lattice join" }
  ],
  requires: []
};

/**
 * AppB - Lawbook
 */
export const HUB_APP_B: HubContract = {
  id: "AppB",
  name: "Lawbook",
  category: HubCategory.FacetBase,
  description: "Rules, rewrite/confluence, clamp rules, conflict laws, obligation templates",
  capabilities: [
    "Rule definition and validation",
    "Confluence checking",
    "Clamp rule application",
    "Conflict detection",
    "Obligation template instantiation"
  ],
  dependencies: ["AppA"],
  provides: [
    { name: "defineRule", type: "(RuleSpec) => Rule", description: "Define validated rule" },
    { name: "checkConfluence", type: "(Rule[]) => boolean", description: "Check rule confluence" },
    { name: "applyClamp", type: "(Value, Bounds) => Value", description: "Apply clamp rule" },
    { name: "detectConflict", type: "(Claim, Claim) => Conflict?", description: "Detect conflicts" },
    { name: "instantiateObligation", type: "(Template, Args) => Obligation", description: "Create obligation" }
  ],
  requires: [
    { name: "addressResolution", from: "AppA", required: true }
  ]
};

/**
 * AppC - Square Base
 */
export const HUB_APP_C: HubContract = {
  id: "AppC",
  name: "Square Base",
  category: HubCategory.LensBase,
  description: "CF/NF, invariants, type registry hooks, canonical equality",
  capabilities: [
    "Canonical form computation",
    "Normal form reduction",
    "Invariant checking",
    "Type registration",
    "Canonical equality"
  ],
  dependencies: ["AppA"],
  provides: [
    { name: "toCanonicalForm", type: "(Value) => CF", description: "Convert to canonical form" },
    { name: "toNormalForm", type: "(Value) => NF", description: "Reduce to normal form" },
    { name: "checkInvariant", type: "(Invariant, Value) => boolean", description: "Check invariant" },
    { name: "registerType", type: "(TypeSpec) => TypeId", description: "Register type" },
    { name: "canonicalEquals", type: "(Value, Value) => boolean", description: "Canonical equality" }
  ],
  requires: [
    { name: "addressResolution", from: "AppA", required: true }
  ]
};

/**
 * AppD - Schemas
 */
export const HUB_APP_D: HubContract = {
  id: "AppD",
  name: "Schemas",
  category: HubCategory.Functional,
  description: "ClaimPack/TruthRecord/DAG/CandSet/Quarantine ABI and validators",
  capabilities: [
    "ClaimPack serialization",
    "TruthRecord management",
    "DAG construction",
    "Candidate set operations",
    "Quarantine capsule creation"
  ],
  dependencies: ["AppA", "AppC"],
  provides: [
    { name: "createClaimPack", type: "(Claim, Evidence) => ClaimPack", description: "Create claim pack" },
    { name: "updateTruthRecord", type: "(TruthRecord, Update) => TruthRecord", description: "Update truth record" },
    { name: "buildDAG", type: "(Node[]) => DAG", description: "Build DAG structure" },
    { name: "createCandidateSet", type: "(Candidate[]) => CandSet", description: "Create candidate set" },
    { name: "createQuarantine", type: "(Target, Conflicts) => Quarantine", description: "Create quarantine" }
  ],
  requires: [
    { name: "addressResolution", from: "AppA", required: true },
    { name: "canonicalForm", from: "AppC", required: true }
  ]
};

/**
 * AppE - Flower Base
 */
export const HUB_APP_E: HubContract = {
  id: "AppE",
  name: "Flower Base",
  category: HubCategory.LensBase,
  description: "Operators, hub gates, solve engines, defects, feasibility/infeasibility",
  capabilities: [
    "Operator application",
    "Hub gate management",
    "Solve engine dispatch",
    "Defect detection",
    "Feasibility checking"
  ],
  dependencies: ["AppA", "AppB"],
  provides: [
    { name: "applyOperator", type: "(Operator, Input) => Output", description: "Apply operator" },
    { name: "openGate", type: "(HubId, Corridor) => Gate", description: "Open hub gate" },
    { name: "dispatchSolve", type: "(Problem) => Solution", description: "Dispatch to solve engine" },
    { name: "detectDefect", type: "(Structure) => Defect?", description: "Detect structural defect" },
    { name: "checkFeasibility", type: "(Constraints) => boolean", description: "Check feasibility" }
  ],
  requires: [
    { name: "addressResolution", from: "AppA", required: true },
    { name: "ruleApplication", from: "AppB", required: true }
  ]
};

/**
 * AppF - Translation
 */
export const HUB_APP_F: HubContract = {
  id: "AppF",
  name: "Translation",
  category: HubCategory.Functional,
  description: "Typed candidate bridges, non-coercion, bridge coherence proofs",
  capabilities: [
    "Candidate bridging",
    "Type translation",
    "Non-coercion verification",
    "Bridge coherence proofs"
  ],
  dependencies: ["AppC", "AppE"],
  provides: [
    { name: "createBridge", type: "(Source, Target) => Bridge", description: "Create type bridge" },
    { name: "translateCandidate", type: "(Candidate, Bridge) => Candidate", description: "Translate candidate" },
    { name: "verifyNonCoercion", type: "(Bridge) => boolean", description: "Verify non-coercion" },
    { name: "proveBridgeCoherence", type: "(Bridge[]) => Proof", description: "Prove bridge coherence" }
  ],
  requires: [
    { name: "canonicalForm", from: "AppC", required: true },
    { name: "operatorApplication", from: "AppE", required: true }
  ]
};

/**
 * AppG - Corridor
 */
export const HUB_APP_G: HubContract = {
  id: "AppG",
  name: "Corridor",
  category: HubCategory.Functional,
  description: "Scope algebra, admissibility predicates, zoom ladders, stability/persistence",
  capabilities: [
    "Scope composition",
    "Admissibility checking",
    "Zoom ladder operations",
    "Stability verification",
    "Persistence tracking"
  ],
  dependencies: ["AppA"],
  provides: [
    { name: "composeScope", type: "(Scope, Scope) => Scope", description: "Compose scopes" },
    { name: "checkAdmissibility", type: "(Value, Scope) => boolean", description: "Check admissibility" },
    { name: "zoomIn", type: "(Level) => Level", description: "Zoom to finer level" },
    { name: "zoomOut", type: "(Level) => Level", description: "Zoom to coarser level" },
    { name: "verifyStability", type: "(Value) => boolean", description: "Verify stability" }
  ],
  requires: [
    { name: "addressResolution", from: "AppA", required: true }
  ]
};

/**
 * AppH - Constructions
 */
export const HUB_APP_H: HubContract = {
  id: "AppH",
  name: "Constructions",
  category: HubCategory.FacetBase,
  description: "Derived objects, discriminators, horn/Čech builders, discharge constructors",
  capabilities: [
    "Derived object construction",
    "Discriminator creation",
    "Horn filler construction",
    "Čech nerve building",
    "Discharge construction"
  ],
  dependencies: ["AppB", "AppE"],
  provides: [
    { name: "constructDerived", type: "(Base, Spec) => Derived", description: "Construct derived object" },
    { name: "createDiscriminator", type: "(CandSet) => Discriminator", description: "Create discriminator" },
    { name: "buildHornFiller", type: "(Horn) => Filler", description: "Build horn filler" },
    { name: "buildCechNerve", type: "(Cover) => Nerve", description: "Build Čech nerve" },
    { name: "constructDischarge", type: "(Obligation) => Discharge", description: "Construct discharge" }
  ],
  requires: [
    { name: "ruleApplication", from: "AppB", required: true },
    { name: "operatorApplication", from: "AppE", required: true }
  ]
};

/**
 * AppI - Truth Kernel
 */
export const HUB_APP_I: HubContract = {
  id: "AppI",
  name: "Truth Kernel",
  category: HubCategory.Core,
  description: "Promotion/refutation, evidence discipline, TruthTrace updates, CollapsePack compile",
  capabilities: [
    "Truth promotion",
    "Truth refutation",
    "Evidence validation",
    "TruthTrace management",
    "CollapsePack compilation"
  ],
  dependencies: ["AppA", "AppD"],
  provides: [
    { name: "promote", type: "(TruthValue, Evidence) => TruthValue", description: "Promote truth value" },
    { name: "refute", type: "(TruthValue, Counterwitness) => FAIL", description: "Refute to FAIL" },
    { name: "validateEvidence", type: "(Evidence) => boolean", description: "Validate evidence" },
    { name: "updateTruthTrace", type: "(TruthTrace, Event) => TruthTrace", description: "Update truth trace" },
    { name: "compileCollapsePack", type: "(Claim, Resolution) => CollapsePack", description: "Compile collapse pack" }
  ],
  requires: [
    { name: "addressResolution", from: "AppA", required: true },
    { name: "truthRecordManagement", from: "AppD", required: true }
  ]
};

/**
 * AppJ - NEAR Overlay
 */
export const HUB_APP_J: HubContract = {
  id: "AppJ",
  name: "NEAR Overlay",
  category: HubCategory.TruthOverlay,
  description: "Δ ledger, tightening ladders, monotone residual shrink",
  capabilities: [
    "Residual ledger management",
    "Tightening operations",
    "Monotone shrinking",
    "Upgrade planning"
  ],
  dependencies: ["AppI"],
  provides: [
    { name: "createResidualLedger", type: "(Residuals) => ΔLedger", description: "Create residual ledger" },
    { name: "tighten", type: "(NEAR, Evidence) => NEAR | OK", description: "Tighten NEAR value" },
    { name: "shrinkResidual", type: "(Δ, Reduction) => Δ", description: "Shrink residual" },
    { name: "planUpgrade", type: "(NEAR) => UpgradePlan", description: "Plan upgrade to OK" }
  ],
  requires: [
    { name: "truthKernel", from: "AppI", required: true }
  ]
};

/**
 * AppK - FAIL Overlay
 */
export const HUB_APP_K: HubContract = {
  id: "AppK",
  name: "FAIL Overlay",
  category: HubCategory.TruthOverlay,
  description: "Quarantine, minimal witness sets, refutation routes, permanence enforcement",
  capabilities: [
    "Quarantine management",
    "Minimal witness computation",
    "Refutation routing",
    "Permanence checking"
  ],
  dependencies: ["AppI", "AppD"],
  provides: [
    { name: "quarantine", type: "(Target, Conflicts) => QuarantineCapsule", description: "Quarantine target" },
    { name: "computeMinimalWitness", type: "(Witnesses) => MinimalSet", description: "Compute minimal witnesses" },
    { name: "findRefutationRoute", type: "(Claim) => Route", description: "Find refutation route" },
    { name: "enforcePermanence", type: "(FAIL) => void", description: "Enforce permanence" }
  ],
  requires: [
    { name: "truthKernel", from: "AppI", required: true },
    { name: "quarantineABI", from: "AppD", required: true }
  ]
};

/**
 * AppL - AMBIG Overlay
 */
export const HUB_APP_L: HubContract = {
  id: "AppL",
  name: "AMBIG Overlay",
  category: HubCategory.TruthOverlay,
  description: "Candidate sets, evidence plans, discriminator ranking, stop reasons",
  capabilities: [
    "Candidate set management",
    "Evidence planning",
    "Discriminator ranking",
    "Stop reason tracking"
  ],
  dependencies: ["AppI", "AppH"],
  provides: [
    { name: "manageCandidateSet", type: "(CandSet) => CandSet", description: "Manage candidate set" },
    { name: "planEvidence", type: "(AMBIG) => EvidencePlan", description: "Plan evidence gathering" },
    { name: "rankDiscriminators", type: "(Discriminator[]) => Discriminator[]", description: "Rank discriminators" },
    { name: "recordStopReason", type: "(Reason) => void", description: "Record stop reason" }
  ],
  requires: [
    { name: "truthKernel", from: "AppI", required: true },
    { name: "discriminatorConstruction", from: "AppH", required: true }
  ]
};

/**
 * AppM - Fractal Base
 */
export const HUB_APP_M: HubContract = {
  id: "AppM",
  name: "Fractal Base",
  category: HubCategory.Core,
  description: "Canonical serialization, digest discipline, replay/seal authority, zoom fixed-point",
  capabilities: [
    "Canonical serialization",
    "Digest computation",
    "Replay execution",
    "Seal authority",
    "Zoom fixed-point computation"
  ],
  dependencies: ["AppA", "AppC"],
  provides: [
    { name: "canonSerialize", type: "(Value) => Bytes", description: "Canonical serialization" },
    { name: "computeDigest", type: "(Bytes) => Hash", description: "Compute digest" },
    { name: "executeReplay", type: "(ReplayCapsule) => Result", description: "Execute replay" },
    { name: "seal", type: "(Value, TruthValue) => Sealed", description: "Seal with truth" },
    { name: "computeZoomFixedPoint", type: "(Sequence) => FixedPoint", description: "Compute zoom fixed-point" }
  ],
  requires: [
    { name: "addressResolution", from: "AppA", required: true },
    { name: "canonicalForm", from: "AppC", required: true }
  ]
};

/**
 * AppN - Boundaries
 */
export const HUB_APP_N: HubContract = {
  id: "AppN",
  name: "Boundaries",
  category: HubCategory.Functional,
  description: "Domain capsules, MIGRATE templates/contracts, interface checks, bridge defect tokens",
  capabilities: [
    "Domain capsule creation",
    "Migration template management",
    "Interface validation",
    "Bridge defect tracking"
  ],
  dependencies: ["AppF", "AppG"],
  provides: [
    { name: "createDomainCapsule", type: "(Domain) => Capsule", description: "Create domain capsule" },
    { name: "instantiateMigrate", type: "(Template, Args) => Migration", description: "Instantiate migration" },
    { name: "checkInterface", type: "(Interface) => boolean", description: "Check interface" },
    { name: "trackBridgeDefect", type: "(Bridge, Defect) => Token", description: "Track bridge defect" }
  ],
  requires: [
    { name: "translationBridge", from: "AppF", required: true },
    { name: "corridorScope", from: "AppG", required: true }
  ]
};

/**
 * AppO - Publishing
 */
export const HUB_APP_O: HubContract = {
  id: "AppO",
  name: "Publishing",
  category: HubCategory.TruthOverlay,
  description: "OK-sealed bundles only, proof-preserving export, version pinning",
  capabilities: [
    "OK-only publishing",
    "Proof-preserving export",
    "Version management",
    "Bundle creation"
  ],
  dependencies: ["AppI", "AppM"],
  provides: [
    { name: "publish", type: "(OKSealed) => Publication", description: "Publish OK-sealed bundle" },
    { name: "exportWithProofs", type: "(Publication) => ExportBundle", description: "Export with proofs" },
    { name: "pinVersion", type: "(Publication, Version) => Pin", description: "Pin to version" },
    { name: "createBundle", type: "(OKSealed[]) => Bundle", description: "Create publication bundle" }
  ],
  requires: [
    { name: "truthKernel", from: "AppI", required: true },
    { name: "sealAuthority", from: "AppM", required: true }
  ]
};

/**
 * AppP - Toolchain
 */
export const HUB_APP_P: HubContract = {
  id: "AppP",
  name: "Toolchain",
  category: HubCategory.Functional,
  description: "Deterministic runners, import/export execution, replay CLI semantics, integration tests",
  capabilities: [
    "Deterministic execution",
    "Import/export management",
    "Replay CLI",
    "Integration testing"
  ],
  dependencies: ["AppM", "AppO"],
  provides: [
    { name: "runDeterministic", type: "(Program) => Result", description: "Run deterministically" },
    { name: "importBundle", type: "(ExportBundle) => ImportResult", description: "Import bundle" },
    { name: "exportBundle", type: "(Bundle) => ExportBundle", description: "Export bundle" },
    { name: "replayCLI", type: "(Command) => Output", description: "Replay CLI command" },
    { name: "runIntegrationTest", type: "(Test) => TestResult", description: "Run integration test" }
  ],
  requires: [
    { name: "sealAuthority", from: "AppM", required: true },
    { name: "publishingAuthority", from: "AppO", required: true }
  ]
};

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: HUB REGISTRY
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete hub registry
 */
export const HUB_REGISTRY: Map<HubId, HubContract> = new Map([
  ["AppA", HUB_APP_A],
  ["AppB", HUB_APP_B],
  ["AppC", HUB_APP_C],
  ["AppD", HUB_APP_D],
  ["AppE", HUB_APP_E],
  ["AppF", HUB_APP_F],
  ["AppG", HUB_APP_G],
  ["AppH", HUB_APP_H],
  ["AppI", HUB_APP_I],
  ["AppJ", HUB_APP_J],
  ["AppK", HUB_APP_K],
  ["AppL", HUB_APP_L],
  ["AppM", HUB_APP_M],
  ["AppN", HUB_APP_N],
  ["AppO", HUB_APP_O],
  ["AppP", HUB_APP_P]
]);

/**
 * Mandatory signature (always included in hub set)
 */
export const MANDATORY_SIGNATURE: HubId[] = ["AppA", "AppI", "AppM"];

/**
 * Lens base mapping
 */
export const LENS_BASE_MAP: Record<string, HubId> = {
  S: "AppC",  // Square → AppC
  F: "AppE",  // Flower → AppE
  C: "AppI",  // Cloud → AppI (overlaps with signature)
  R: "AppM"   // Fractal → AppM (overlaps with signature)
};

/**
 * Facet base mapping
 */
export const FACET_BASE_MAP: Record<number, HubId> = {
  1: "AppA",  // Objects → AppA (overlaps with signature)
  2: "AppB",  // Laws → AppB
  3: "AppH",  // Constructions → AppH
  4: "AppM"   // Certificates → AppM (overlaps with signature)
};

/**
 * Truth overlay mapping
 */
export const TRUTH_OVERLAY_MAP: Record<string, HubId> = {
  OK: "AppO",    // Publishing only
  NEAR: "AppJ",  // NEAR overlay
  AMBIG: "AppL", // AMBIG overlay
  FAIL: "AppK"   // FAIL overlay
};

/**
 * Arc hub mapping (α → Hub)
 */
export const ARC_HUB_MAP: Record<number, HubId> = {
  0: "AppA",
  1: "AppC",
  2: "AppE",
  3: "AppF",
  4: "AppG",
  5: "AppN",
  6: "AppP"
};

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: HUB SET COMPUTATION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Hub set computation parameters
 */
export interface HubSetParams {
  lens: string;
  facet: number;
  chapter: number;
  truth?: string;
}

/**
 * Compute hub set for given parameters
 */
export function computeHubSet(params: HubSetParams): HubId[] {
  const hubSet = new Set<HubId>(MANDATORY_SIGNATURE);
  
  // Add lens base
  const lensBase = LENS_BASE_MAP[params.lens];
  if (lensBase) hubSet.add(lensBase);
  
  // Add facet base
  const facetBase = FACET_BASE_MAP[params.facet];
  if (facetBase) hubSet.add(facetBase);
  
  // Add arc hub
  const omega = params.chapter - 1;
  const alpha = Math.floor(omega / 3);
  const arcHub = ARC_HUB_MAP[alpha];
  if (arcHub) hubSet.add(arcHub);
  
  // Add truth overlay (non-droppable)
  if (params.truth) {
    const overlay = TRUTH_OVERLAY_MAP[params.truth];
    if (overlay) hubSet.add(overlay);
  }
  
  // Convert to array and enforce max 6
  let result = Array.from(hubSet);
  
  if (result.length > 6) {
    // Priority: Signature > Overlay > ArcHub > LensBase > FacetBase
    const signature = result.filter(h => MANDATORY_SIGNATURE.includes(h));
    const overlay = result.find(h => Object.values(TRUTH_OVERLAY_MAP).includes(h));
    const arcHubInSet = result.find(h => Object.values(ARC_HUB_MAP).includes(h) && !MANDATORY_SIGNATURE.includes(h));
    const lensInSet = result.find(h => Object.values(LENS_BASE_MAP).includes(h) && !MANDATORY_SIGNATURE.includes(h));
    
    result = [...signature];
    if (overlay && result.length < 6) result.push(overlay);
    if (arcHubInSet && result.length < 6 && !result.includes(arcHubInSet)) result.push(arcHubInSet);
    if (lensInSet && result.length < 6 && !result.includes(lensInSet)) result.push(lensInSet);
  }
  
  return result;
}

/**
 * Validate hub set
 */
export function validateHubSet(hubSet: HubId[]): { valid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  // Check max 6
  if (hubSet.length > 6) {
    errors.push(`Hub set exceeds maximum of 6 (got ${hubSet.length})`);
  }
  
  // Check mandatory signature
  for (const hub of MANDATORY_SIGNATURE) {
    if (!hubSet.includes(hub)) {
      errors.push(`Missing mandatory hub: ${hub}`);
    }
  }
  
  // Check all hubs exist
  for (const hub of hubSet) {
    if (!HUB_REGISTRY.has(hub)) {
      errors.push(`Unknown hub: ${hub}`);
    }
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: HUB INSTANCE MANAGER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Hub instance
 */
export interface HubInstance {
  contract: HubContract;
  status: "ready" | "initializing" | "error";
  providers: Map<string, Function>;
}

/**
 * Hub manager
 */
export class HubManager {
  private instances: Map<HubId, HubInstance> = new Map();
  
  /**
   * Initialize hub
   */
  async initializeHub(id: HubId): Promise<HubInstance> {
    const contract = HUB_REGISTRY.get(id);
    if (!contract) {
      throw new Error(`Unknown hub: ${id}`);
    }
    
    // Check dependencies
    for (const dep of contract.dependencies) {
      if (!this.instances.has(dep)) {
        await this.initializeHub(dep);
      }
    }
    
    // Create instance
    const instance: HubInstance = {
      contract,
      status: "initializing",
      providers: new Map()
    };
    
    // Initialize providers (placeholder)
    for (const provider of contract.provides) {
      instance.providers.set(provider.name, () => {
        throw new Error(`Provider ${provider.name} not implemented`);
      });
    }
    
    instance.status = "ready";
    this.instances.set(id, instance);
    
    return instance;
  }
  
  /**
   * Get hub instance
   */
  getInstance(id: HubId): HubInstance | undefined {
    return this.instances.get(id);
  }
  
  /**
   * Initialize all hubs
   */
  async initializeAll(): Promise<void> {
    for (const id of HUB_REGISTRY.keys()) {
      if (!this.instances.has(id)) {
        await this.initializeHub(id);
      }
    }
  }
  
  /**
   * Get statistics
   */
  getStats(): {
    total: number;
    initialized: number;
    ready: number;
    errors: number;
  } {
    const all = Array.from(this.instances.values());
    return {
      total: HUB_REGISTRY.size,
      initialized: all.length,
      ready: all.filter(i => i.status === "ready").length,
      errors: all.filter(i => i.status === "error").length
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Contracts
  HUB_APP_A,
  HUB_APP_B,
  HUB_APP_C,
  HUB_APP_D,
  HUB_APP_E,
  HUB_APP_F,
  HUB_APP_G,
  HUB_APP_H,
  HUB_APP_I,
  HUB_APP_J,
  HUB_APP_K,
  HUB_APP_L,
  HUB_APP_M,
  HUB_APP_N,
  HUB_APP_O,
  HUB_APP_P,
  
  // Registry
  HUB_REGISTRY,
  
  // Constants
  MANDATORY_SIGNATURE,
  LENS_BASE_MAP,
  FACET_BASE_MAP,
  TRUTH_OVERLAY_MAP,
  ARC_HUB_MAP,
  
  // Enums
  HubCategory,
  
  // Functions
  computeHubSet,
  validateHubSet,
  
  // Classes
  HubManager
};
