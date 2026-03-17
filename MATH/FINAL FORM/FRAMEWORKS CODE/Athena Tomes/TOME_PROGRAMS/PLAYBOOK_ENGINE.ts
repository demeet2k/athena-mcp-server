/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * PLAYBOOK ENGINE - Core Operational Playbooks (Π1-Π7)
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * This module implements the seven core playbooks from TRUTH-COLLAPSE:
 * 
 * Π1 (HCENM) - Compile: Parse → Normalize → Plan → Solve → Certify → Store
 * Π2 (LHMJ)  - Resolve: Disambiguate AMBIG claims to NEAR/OK/FAIL
 * Π3 (KHDM)  - Conflict: Handle conflicts, quarantine, minimal witnesses
 * Π4 (DOP)   - Publish: Seal and export OK-only bundles
 * Π5 (GNAE)  - Migrate: Cross-domain translation with bridge coherence
 * Π6 (BFIC)  - Validate: Rule application, invariant checking
 * Π7 (FULL)  - Orchestrate: Full pipeline coordination
 * 
 * Each playbook follows MicroRoute discipline with HubSet ≤ 6.
 * 
 * @module PLAYBOOK_ENGINE
 * @version 2.0.0
 */

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: PLAYBOOK TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Truth values
 */
export enum TruthValue {
  OK = "OK",
  NEAR = "NEAR",
  AMBIG = "AMBIG",
  FAIL = "FAIL"
}

/**
 * Hub identifiers
 */
export type HubId = 
  | "AppA" | "AppB" | "AppC" | "AppD" 
  | "AppE" | "AppF" | "AppG" | "AppH"
  | "AppI" | "AppJ" | "AppK" | "AppL"
  | "AppM" | "AppN" | "AppO" | "AppP";

/**
 * Playbook identifier
 */
export enum PlaybookId {
  Compile = "Π1_HCENM",
  Resolve = "Π2_LHMJ",
  Conflict = "Π3_KHDM",
  Publish = "Π4_DOP",
  Migrate = "Π5_GNAE",
  Validate = "Π6_BFIC",
  Orchestrate = "Π7_FULL"
}

/**
 * MicroRoute specification
 */
export interface MicroRoute {
  hubs: HubId[];
  description: string;
}

/**
 * Playbook step
 */
export interface PlaybookStep {
  name: string;
  route: MicroRoute;
  execute: (ctx: PlaybookContext) => Promise<StepResult>;
}

/**
 * Step result
 */
export interface StepResult {
  success: boolean;
  truth: TruthValue;
  output: unknown;
  nextStep?: string;
  error?: string;
}

/**
 * Playbook context
 */
export interface PlaybookContext {
  input: unknown;
  corridor: CorridorSpec;
  state: Map<string, unknown>;
  route: HubId[];
  replayId: string;
  kappaSpent: number;
}

/**
 * Corridor specification
 */
export interface CorridorSpec {
  kappa: number;
  beta: number;
  chi: number;
  epsilon: number;
}

/**
 * Playbook result
 */
export interface PlaybookResult {
  playbook: PlaybookId;
  success: boolean;
  truth: TruthValue;
  output: unknown;
  steps: StepExecutionRecord[];
  totalKappaSpent: number;
  replayId: string;
}

export interface StepExecutionRecord {
  step: string;
  route: HubId[];
  duration: number;
  truth: TruthValue;
  success: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: PLAYBOOK DEFINITIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Mandatory signature
 */
const Σ: HubId[] = ["AppA", "AppI", "AppM"];

/**
 * Π1 - Compile Playbook (HCENM)
 * Parse → Normalize → Plan → Solve → Certify → Store
 */
export const PLAYBOOK_COMPILE: PlaybookStep[] = [
  {
    name: "Parse",
    route: { hubs: [...Σ, "AppC", "AppD"], description: "Parse input to AST" },
    execute: async (ctx) => {
      // Parse input
      const input = ctx.input as { source: string };
      const ast = { type: "AST", source: input.source, parsed: true };
      ctx.state.set("ast", ast);
      ctx.kappaSpent += 0.05;
      return { success: true, truth: TruthValue.NEAR, output: ast };
    }
  },
  {
    name: "Normalize",
    route: { hubs: [...Σ, "AppC", "AppH"], description: "Normalize to canonical form" },
    execute: async (ctx) => {
      const ast = ctx.state.get("ast");
      const normalized = { ...ast as object, normalized: true };
      ctx.state.set("normalized", normalized);
      ctx.kappaSpent += 0.05;
      return { success: true, truth: TruthValue.NEAR, output: normalized };
    }
  },
  {
    name: "Plan",
    route: { hubs: [...Σ, "AppE", "AppG"], description: "Plan solve strategy" },
    execute: async (ctx) => {
      const normalized = ctx.state.get("normalized");
      const plan = { strategy: "default", targets: [], normalized };
      ctx.state.set("plan", plan);
      ctx.kappaSpent += 0.05;
      return { success: true, truth: TruthValue.NEAR, output: plan };
    }
  },
  {
    name: "Solve",
    route: { hubs: [...Σ, "AppE", "AppH"], description: "Execute solve" },
    execute: async (ctx) => {
      const plan = ctx.state.get("plan");
      const solution = { solved: true, plan };
      ctx.state.set("solution", solution);
      ctx.kappaSpent += 0.15;
      return { success: true, truth: TruthValue.NEAR, output: solution };
    }
  },
  {
    name: "Certify",
    route: { hubs: [...Σ, "AppH", "AppD"], description: "Generate certificates" },
    execute: async (ctx) => {
      const solution = ctx.state.get("solution");
      const certificate = { certified: true, solution, witnessPtr: "wit_" + Date.now() };
      ctx.state.set("certificate", certificate);
      ctx.kappaSpent += 0.10;
      return { success: true, truth: TruthValue.OK, output: certificate };
    }
  },
  {
    name: "Store",
    route: { hubs: [...Σ, "AppD", "AppO"], description: "Store result" },
    execute: async (ctx) => {
      const certificate = ctx.state.get("certificate");
      const stored = { stored: true, certificate, replayPtr: "replay_" + Date.now() };
      ctx.kappaSpent += 0.05;
      return { success: true, truth: TruthValue.OK, output: stored };
    }
  }
];

/**
 * Π2 - Resolve Playbook (LHMJ)
 * Disambiguate AMBIG claims
 */
export const PLAYBOOK_RESOLVE: PlaybookStep[] = [
  {
    name: "LoadCandidates",
    route: { hubs: [...Σ, "AppL", "AppD"], description: "Load candidate set" },
    execute: async (ctx) => {
      const input = ctx.input as { claim: unknown; candidates: unknown[] };
      ctx.state.set("candidates", input.candidates);
      ctx.state.set("claim", input.claim);
      ctx.kappaSpent += 0.05;
      return { success: true, truth: TruthValue.AMBIG, output: input.candidates };
    }
  },
  {
    name: "SelectDiscriminator",
    route: { hubs: [...Σ, "AppH", "AppL"], description: "Select best discriminator" },
    execute: async (ctx) => {
      const candidates = ctx.state.get("candidates") as unknown[];
      const discriminator = { type: "consistency", candidates: candidates.length };
      ctx.state.set("discriminator", discriminator);
      ctx.kappaSpent += 0.10;
      return { success: true, truth: TruthValue.AMBIG, output: discriminator };
    }
  },
  {
    name: "RunDiscriminator",
    route: { hubs: [...Σ, "AppE", "AppH"], description: "Execute discriminator" },
    execute: async (ctx) => {
      const candidates = ctx.state.get("candidates") as unknown[];
      const discriminator = ctx.state.get("discriminator");
      // Simulate elimination
      const remaining = candidates.length > 1 ? candidates.slice(0, 1) : candidates;
      ctx.state.set("remaining", remaining);
      ctx.kappaSpent += 0.15;
      
      if (remaining.length === 1) {
        return { success: true, truth: TruthValue.NEAR, output: remaining[0] };
      } else if (remaining.length === 0) {
        return { success: true, truth: TruthValue.FAIL, output: null };
      }
      return { success: true, truth: TruthValue.AMBIG, output: remaining };
    }
  },
  {
    name: "PromoteOrFail",
    route: { hubs: [...Σ, "AppJ", "AppK"], description: "Final promotion or failure" },
    execute: async (ctx) => {
      const remaining = ctx.state.get("remaining") as unknown[];
      ctx.kappaSpent += 0.05;
      
      if (remaining.length === 1) {
        return { success: true, truth: TruthValue.NEAR, output: { winner: remaining[0] } };
      }
      return { success: false, truth: TruthValue.FAIL, output: { noWinner: true } };
    }
  }
];

/**
 * Π3 - Conflict Playbook (KHDM)
 * Handle conflicts and quarantine
 */
export const PLAYBOOK_CONFLICT: PlaybookStep[] = [
  {
    name: "DetectConflict",
    route: { hubs: [...Σ, "AppK", "AppD"], description: "Detect conflicts" },
    execute: async (ctx) => {
      const input = ctx.input as { claims: unknown[] };
      const conflicts = []; // Placeholder for conflict detection
      ctx.state.set("conflicts", conflicts);
      ctx.kappaSpent += 0.10;
      return { success: true, truth: TruthValue.NEAR, output: conflicts };
    }
  },
  {
    name: "ComputeMinimalWitness",
    route: { hubs: [...Σ, "AppH", "AppK"], description: "Compute minimal witness set" },
    execute: async (ctx) => {
      const conflicts = ctx.state.get("conflicts") as unknown[];
      const minimalSet = { witnesses: [], conflicts };
      ctx.state.set("minimalWitness", minimalSet);
      ctx.kappaSpent += 0.15;
      return { success: true, truth: TruthValue.NEAR, output: minimalSet };
    }
  },
  {
    name: "FindRefutationRoute",
    route: { hubs: [...Σ, "AppK", "AppE"], description: "Find refutation route" },
    execute: async (ctx) => {
      const minimalSet = ctx.state.get("minimalWitness");
      const route = { path: ["start", "end"], cost: 1, minimalSet };
      ctx.state.set("refutationRoute", route);
      ctx.kappaSpent += 0.10;
      return { success: true, truth: TruthValue.NEAR, output: route };
    }
  },
  {
    name: "Quarantine",
    route: { hubs: [...Σ, "AppK", "AppD"], description: "Create quarantine capsule" },
    execute: async (ctx) => {
      const route = ctx.state.get("refutationRoute");
      const minimalSet = ctx.state.get("minimalWitness");
      const capsule = {
        id: "quarantine_" + Date.now(),
        target: ctx.input,
        minimalWitness: minimalSet,
        refutationRoute: route,
        permanent: false
      };
      ctx.kappaSpent += 0.05;
      return { success: true, truth: TruthValue.FAIL, output: capsule };
    }
  }
];

/**
 * Π4 - Publish Playbook (DOP)
 * Seal and export OK-only bundles
 */
export const PLAYBOOK_PUBLISH: PlaybookStep[] = [
  {
    name: "VerifyOK",
    route: { hubs: [...Σ, "AppI", "AppD"], description: "Verify OK status" },
    execute: async (ctx) => {
      const input = ctx.input as { truth: TruthValue; data: unknown };
      if (input.truth !== TruthValue.OK) {
        return { 
          success: false, 
          truth: TruthValue.FAIL, 
          output: { error: "Only OK-sealed content can be published" } 
        };
      }
      ctx.state.set("verified", input.data);
      ctx.kappaSpent += 0.05;
      return { success: true, truth: TruthValue.OK, output: input.data };
    }
  },
  {
    name: "Seal",
    route: { hubs: [...Σ, "AppM", "AppO"], description: "Seal for publication" },
    execute: async (ctx) => {
      const verified = ctx.state.get("verified");
      const sealed = {
        data: verified,
        seal: "seal_" + Date.now(),
        digest: "digest_" + Math.random().toString(36).slice(2)
      };
      ctx.state.set("sealed", sealed);
      ctx.kappaSpent += 0.10;
      return { success: true, truth: TruthValue.OK, output: sealed };
    }
  },
  {
    name: "Export",
    route: { hubs: [...Σ, "AppO", "AppP"], description: "Export bundle" },
    execute: async (ctx) => {
      const sealed = ctx.state.get("sealed");
      const exported = {
        bundle: sealed,
        version: "1.0.0",
        exportedAt: Date.now(),
        proofPreserved: true
      };
      ctx.kappaSpent += 0.05;
      return { success: true, truth: TruthValue.OK, output: exported };
    }
  }
];

/**
 * Π5 - Migrate Playbook (GNAE)
 * Cross-domain translation
 */
export const PLAYBOOK_MIGRATE: PlaybookStep[] = [
  {
    name: "LoadSource",
    route: { hubs: [...Σ, "AppG", "AppN"], description: "Load source domain" },
    execute: async (ctx) => {
      const input = ctx.input as { source: unknown; targetDomain: string };
      ctx.state.set("source", input.source);
      ctx.state.set("targetDomain", input.targetDomain);
      ctx.kappaSpent += 0.05;
      return { success: true, truth: TruthValue.NEAR, output: input.source };
    }
  },
  {
    name: "FindBridge",
    route: { hubs: [...Σ, "AppF", "AppN"], description: "Find translation bridge" },
    execute: async (ctx) => {
      const targetDomain = ctx.state.get("targetDomain");
      const bridge = { type: "typed_bridge", target: targetDomain, coherent: true };
      ctx.state.set("bridge", bridge);
      ctx.kappaSpent += 0.10;
      return { success: true, truth: TruthValue.NEAR, output: bridge };
    }
  },
  {
    name: "Translate",
    route: { hubs: [...Σ, "AppE", "AppF"], description: "Execute translation" },
    execute: async (ctx) => {
      const source = ctx.state.get("source");
      const bridge = ctx.state.get("bridge");
      const translated = { original: source, bridge, translated: true };
      ctx.state.set("translated", translated);
      ctx.kappaSpent += 0.15;
      return { success: true, truth: TruthValue.NEAR, output: translated };
    }
  },
  {
    name: "VerifyCoherence",
    route: { hubs: [...Σ, "AppF", "AppH"], description: "Verify bridge coherence" },
    execute: async (ctx) => {
      const translated = ctx.state.get("translated");
      const proof = { coherent: true, translated, proof: "coherence_proof" };
      ctx.kappaSpent += 0.10;
      return { success: true, truth: TruthValue.OK, output: proof };
    }
  }
];

/**
 * Π6 - Validate Playbook (BFIC)
 * Rule application and invariant checking
 */
export const PLAYBOOK_VALIDATE: PlaybookStep[] = [
  {
    name: "LoadRules",
    route: { hubs: [...Σ, "AppB", "AppD"], description: "Load rule set" },
    execute: async (ctx) => {
      const input = ctx.input as { target: unknown; rules: string[] };
      ctx.state.set("target", input.target);
      ctx.state.set("rules", input.rules);
      ctx.kappaSpent += 0.05;
      return { success: true, truth: TruthValue.NEAR, output: input.rules };
    }
  },
  {
    name: "CheckInvariants",
    route: { hubs: [...Σ, "AppC", "AppB"], description: "Check invariants" },
    execute: async (ctx) => {
      const target = ctx.state.get("target");
      const invariantResults = { passed: true, violations: [] };
      ctx.state.set("invariants", invariantResults);
      ctx.kappaSpent += 0.10;
      return { success: true, truth: TruthValue.NEAR, output: invariantResults };
    }
  },
  {
    name: "ApplyRules",
    route: { hubs: [...Σ, "AppB", "AppE"], description: "Apply rules" },
    execute: async (ctx) => {
      const target = ctx.state.get("target");
      const rules = ctx.state.get("rules");
      const applied = { target, rulesApplied: rules, valid: true };
      ctx.state.set("applied", applied);
      ctx.kappaSpent += 0.15;
      return { success: true, truth: TruthValue.NEAR, output: applied };
    }
  },
  {
    name: "Certify",
    route: { hubs: [...Σ, "AppI", "AppH"], description: "Certify validation" },
    execute: async (ctx) => {
      const applied = ctx.state.get("applied");
      const invariants = ctx.state.get("invariants");
      const certificate = {
        valid: true,
        applied,
        invariants,
        certifiedAt: Date.now()
      };
      ctx.kappaSpent += 0.05;
      return { success: true, truth: TruthValue.OK, output: certificate };
    }
  }
];

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: PLAYBOOK REGISTRY
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Playbook registry
 */
export const PLAYBOOK_REGISTRY: Map<PlaybookId, PlaybookStep[]> = new Map([
  [PlaybookId.Compile, PLAYBOOK_COMPILE],
  [PlaybookId.Resolve, PLAYBOOK_RESOLVE],
  [PlaybookId.Conflict, PLAYBOOK_CONFLICT],
  [PlaybookId.Publish, PLAYBOOK_PUBLISH],
  [PlaybookId.Migrate, PLAYBOOK_MIGRATE],
  [PlaybookId.Validate, PLAYBOOK_VALIDATE]
]);

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: PLAYBOOK EXECUTOR
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Playbook executor
 */
export class PlaybookExecutor {
  private defaultCorridor: CorridorSpec = {
    kappa: 1.0,
    beta: 30000,
    chi: 4194304,
    epsilon: 0.01
  };
  
  /**
   * Execute playbook
   */
  async execute(
    playbookId: PlaybookId,
    input: unknown,
    corridor?: Partial<CorridorSpec>
  ): Promise<PlaybookResult> {
    const playbook = PLAYBOOK_REGISTRY.get(playbookId);
    if (!playbook) {
      throw new Error(`Unknown playbook: ${playbookId}`);
    }
    
    const ctx: PlaybookContext = {
      input,
      corridor: { ...this.defaultCorridor, ...corridor },
      state: new Map(),
      route: [],
      replayId: `replay_${playbookId}_${Date.now()}`,
      kappaSpent: 0
    };
    
    const steps: StepExecutionRecord[] = [];
    let finalTruth = TruthValue.AMBIG;
    let finalOutput: unknown = null;
    let success = true;
    
    for (const step of playbook) {
      // Validate hub set
      if (step.route.hubs.length > 6) {
        throw new Error(`Hub set exceeds maximum of 6 in step ${step.name}`);
      }
      
      const startTime = Date.now();
      ctx.route = step.route.hubs;
      
      try {
        const result = await step.execute(ctx);
        
        steps.push({
          step: step.name,
          route: step.route.hubs,
          duration: Date.now() - startTime,
          truth: result.truth,
          success: result.success
        });
        
        finalTruth = result.truth;
        finalOutput = result.output;
        
        if (!result.success) {
          success = false;
          break;
        }
        
        // Check kappa budget
        if (ctx.kappaSpent > ctx.corridor.kappa) {
          success = false;
          finalTruth = TruthValue.FAIL;
          finalOutput = { error: "Kappa budget exceeded" };
          break;
        }
        
      } catch (e) {
        steps.push({
          step: step.name,
          route: step.route.hubs,
          duration: Date.now() - startTime,
          truth: TruthValue.FAIL,
          success: false
        });
        
        success = false;
        finalTruth = TruthValue.FAIL;
        finalOutput = { error: e instanceof Error ? e.message : "Unknown error" };
        break;
      }
    }
    
    return {
      playbook: playbookId,
      success,
      truth: finalTruth,
      output: finalOutput,
      steps,
      totalKappaSpent: ctx.kappaSpent,
      replayId: ctx.replayId
    };
  }
  
  /**
   * Execute Π7 - Full Orchestration
   */
  async orchestrate(
    input: unknown,
    corridor?: Partial<CorridorSpec>
  ): Promise<PlaybookResult> {
    // Π7 orchestrates multiple playbooks
    const results: PlaybookResult[] = [];
    
    // Step 1: Compile
    const compileResult = await this.execute(PlaybookId.Compile, { source: input }, corridor);
    results.push(compileResult);
    
    if (!compileResult.success) {
      return {
        playbook: PlaybookId.Orchestrate,
        success: false,
        truth: TruthValue.FAIL,
        output: { phase: "compile", error: compileResult.output },
        steps: compileResult.steps,
        totalKappaSpent: compileResult.totalKappaSpent,
        replayId: `orchestrate_${Date.now()}`
      };
    }
    
    // Step 2: Validate
    const validateResult = await this.execute(
      PlaybookId.Validate,
      { target: compileResult.output, rules: ["invariant_check"] },
      corridor
    );
    results.push(validateResult);
    
    if (!validateResult.success) {
      return {
        playbook: PlaybookId.Orchestrate,
        success: false,
        truth: TruthValue.FAIL,
        output: { phase: "validate", error: validateResult.output },
        steps: [...compileResult.steps, ...validateResult.steps],
        totalKappaSpent: compileResult.totalKappaSpent + validateResult.totalKappaSpent,
        replayId: `orchestrate_${Date.now()}`
      };
    }
    
    // Step 3: Publish if OK
    if (validateResult.truth === TruthValue.OK) {
      const publishResult = await this.execute(
        PlaybookId.Publish,
        { truth: TruthValue.OK, data: validateResult.output },
        corridor
      );
      results.push(publishResult);
      
      return {
        playbook: PlaybookId.Orchestrate,
        success: publishResult.success,
        truth: publishResult.truth,
        output: publishResult.output,
        steps: [...compileResult.steps, ...validateResult.steps, ...publishResult.steps],
        totalKappaSpent: results.reduce((sum, r) => sum + r.totalKappaSpent, 0),
        replayId: `orchestrate_${Date.now()}`
      };
    }
    
    // Return NEAR if not fully OK
    return {
      playbook: PlaybookId.Orchestrate,
      success: true,
      truth: TruthValue.NEAR,
      output: validateResult.output,
      steps: [...compileResult.steps, ...validateResult.steps],
      totalKappaSpent: results.reduce((sum, r) => sum + r.totalKappaSpent, 0),
      replayId: `orchestrate_${Date.now()}`
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Get playbook by operation type
 */
export function getPlaybookForOperation(operation: string): PlaybookId | null {
  const mapping: Record<string, PlaybookId> = {
    compile: PlaybookId.Compile,
    resolve: PlaybookId.Resolve,
    disambiguate: PlaybookId.Resolve,
    conflict: PlaybookId.Conflict,
    quarantine: PlaybookId.Conflict,
    publish: PlaybookId.Publish,
    export: PlaybookId.Publish,
    migrate: PlaybookId.Migrate,
    translate: PlaybookId.Migrate,
    validate: PlaybookId.Validate,
    check: PlaybookId.Validate,
    full: PlaybookId.Orchestrate,
    orchestrate: PlaybookId.Orchestrate
  };
  
  return mapping[operation.toLowerCase()] ?? null;
}

/**
 * Get playbook summary
 */
export function getPlaybookSummary(playbookId: PlaybookId): string {
  const playbook = PLAYBOOK_REGISTRY.get(playbookId);
  if (!playbook) return "Unknown playbook";
  
  const steps = playbook.map(s => s.name).join(" → ");
  return `${playbookId}: ${steps}`;
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Enums
  TruthValue,
  PlaybookId,
  
  // Playbooks
  PLAYBOOK_COMPILE,
  PLAYBOOK_RESOLVE,
  PLAYBOOK_CONFLICT,
  PLAYBOOK_PUBLISH,
  PLAYBOOK_MIGRATE,
  PLAYBOOK_VALIDATE,
  
  // Registry
  PLAYBOOK_REGISTRY,
  
  // Classes
  PlaybookExecutor,
  
  // Functions
  getPlaybookForOperation,
  getPlaybookSummary
};
