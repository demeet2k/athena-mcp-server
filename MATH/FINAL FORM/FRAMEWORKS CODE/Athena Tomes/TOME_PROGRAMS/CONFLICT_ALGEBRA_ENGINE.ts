/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * CONFLICT ALGEBRA ENGINE - Minimal Witness Sets, Quarantine Capsules, Refutation
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * From TRUTH-COLLAPSE_COMPILER Ch19:
 * 
 * Core Components:
 *   - Conflict receipt schema
 *   - Minimal witness minimization
 *   - Refutation routing
 *   - Permanence criteria under admissible refinement
 * 
 * Obstruction contributions:
 *   - Failure artifacts must be replayable
 *   - Minimizer caps → NEAR-minFAIL
 * 
 * @module CONFLICT_ALGEBRA_ENGINE
 * @version 2.0.0
 */

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: CONFLICT TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Conflict kind
 */
export enum ConflictKind {
  Contradiction = "Contradiction",
  TypeMismatch = "TypeMismatch",
  CorridorViolation = "CorridorViolation",
  ReplayDrift = "ReplayDrift",
  ObstructionPersistent = "ObstructionPersistent",
  DependencyMissing = "DependencyMissing",
  CycleDetected = "CycleDetected",
  BudgetExceeded = "BudgetExceeded",
  Incoherent = "Incoherent"
}

/**
 * Conflict severity
 */
export enum ConflictSeverity {
  Fatal = "Fatal",      // Immediate FAIL
  Critical = "Critical", // FAIL unless repaired
  Warning = "Warning",   // NEAR with obligations
  Info = "Info"          // Logged but not blocking
}

/**
 * Conflict receipt (Ch19 schema)
 */
export interface ConflictReceipt {
  id: string;
  kind: ConflictKind;
  severity: ConflictSeverity;
  source: string;
  target: string;
  description: string;
  witnesses: WitnessRef[];
  minimalWitnessSet: string[];
  refutationRoute?: RefutationRoute;
  timestamp: number;
  permanent: boolean;
  hash: string;
}

export interface WitnessRef {
  type: "positive" | "negative" | "diagnostic";
  address: string;
  content: string;
  hash: string;
}

/**
 * Refutation route
 */
export interface RefutationRoute {
  steps: RefutationStep[];
  cost: number;
  confidence: number;
}

export interface RefutationStep {
  from: string;
  to: string;
  operation: "derive" | "contradict" | "reduce" | "witness";
  justification: string;
}

/**
 * Quarantine capsule
 */
export interface QuarantineCapsule {
  id: string;
  target: string;
  conflictReceipts: ConflictReceipt[];
  minimalWitnessSet: MinimalWitnessSet;
  refutationRoute: RefutationRoute;
  isolationScope: string[];
  created: number;
  permanent: boolean;
  repairPlan?: RepairPlan;
  hash: string;
}

export interface RepairPlan {
  steps: RepairStep[];
  estimatedCost: number;
  confidence: number;
}

export interface RepairStep {
  action: string;
  target: string;
  params: Record<string, unknown>;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: MINIMAL WITNESS SET
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Minimal witness set
 */
export interface MinimalWitnessSet {
  id: string;
  witnesses: WitnessRef[];
  claim: string;
  isMinimal: boolean;
  minimizationTrace: MinimizationStep[];
  hash: string;
}

export interface MinimizationStep {
  step: number;
  action: "remove" | "merge" | "simplify";
  removed?: string;
  merged?: [string, string];
  simplified?: string;
  remainingCount: number;
}

/**
 * Witness minimizer
 */
export class WitnessMinimizer {
  private maxIterations = 100;
  
  /**
   * Minimize witness set
   */
  minimize(witnesses: WitnessRef[], claim: string): MinimalWitnessSet {
    const trace: MinimizationStep[] = [];
    let current = [...witnesses];
    let step = 0;
    
    // Greedy minimization: try removing each witness
    while (step < this.maxIterations && current.length > 1) {
      let removed = false;
      
      for (let i = 0; i < current.length; i++) {
        const subset = current.filter((_, j) => j !== i);
        
        if (this.stillProvesClaim(subset, claim)) {
          trace.push({
            step: step++,
            action: "remove",
            removed: current[i].address,
            remainingCount: subset.length
          });
          current = subset;
          removed = true;
          break;
        }
      }
      
      if (!removed) break;
    }
    
    // Try merging similar witnesses
    for (let i = 0; i < current.length - 1; i++) {
      for (let j = i + 1; j < current.length; j++) {
        if (this.canMerge(current[i], current[j])) {
          const merged = this.mergeWitnesses(current[i], current[j]);
          const newSet = [...current.slice(0, i), ...current.slice(i + 1, j), ...current.slice(j + 1), merged];
          
          if (this.stillProvesClaim(newSet, claim)) {
            trace.push({
              step: step++,
              action: "merge",
              merged: [current[i].address, current[j].address],
              remainingCount: newSet.length
            });
            current = newSet;
          }
        }
      }
    }
    
    return {
      id: `mws_${Date.now()}`,
      witnesses: current,
      claim,
      isMinimal: true,
      minimizationTrace: trace,
      hash: hashString(JSON.stringify(current.map(w => w.hash)))
    };
  }
  
  /**
   * Check if subset still proves claim
   */
  private stillProvesClaim(witnesses: WitnessRef[], claim: string): boolean {
    // Check if we have at least one negative witness (for contradiction)
    // or sufficient positive witnesses
    const hasNegative = witnesses.some(w => w.type === "negative");
    const positiveCount = witnesses.filter(w => w.type === "positive").length;
    
    return hasNegative || positiveCount >= 1;
  }
  
  /**
   * Check if two witnesses can be merged
   */
  private canMerge(w1: WitnessRef, w2: WitnessRef): boolean {
    return w1.type === w2.type && 
           w1.content.length > 0 && 
           w2.content.length > 0;
  }
  
  /**
   * Merge two witnesses
   */
  private mergeWitnesses(w1: WitnessRef, w2: WitnessRef): WitnessRef {
    return {
      type: w1.type,
      address: `merged_${w1.address}_${w2.address}`,
      content: `${w1.content}∧${w2.content}`,
      hash: hashString(`${w1.hash}:${w2.hash}`)
    };
  }
}

function hashString(s: string): string {
  let hash = 0;
  for (let i = 0; i < s.length; i++) {
    hash = ((hash << 5) - hash) + s.charCodeAt(i);
    hash = hash & hash;
  }
  return Math.abs(hash).toString(16).padStart(8, '0');
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: CONFLICT DETECTOR
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Conflict detection result
 */
export interface ConflictDetectionResult {
  hasConflict: boolean;
  conflicts: ConflictReceipt[];
  severity: ConflictSeverity;
}

/**
 * Conflict detector
 */
export class ConflictDetector {
  private detectors: ConflictDetectorFn[] = [];
  
  constructor() {
    this.initializeDefaultDetectors();
  }
  
  private initializeDefaultDetectors(): void {
    // Contradiction detector
    this.detectors.push({
      name: "ContradictionDetector",
      kinds: [ConflictKind.Contradiction],
      detect: (context) => {
        const conflicts: ConflictReceipt[] = [];
        
        // Check for φ and ¬φ both claimed
        for (const [claim1, evidence1] of context.claims) {
          const negatedClaim = `¬${claim1}`;
          if (context.claims.has(negatedClaim)) {
            conflicts.push(this.createReceipt(
              ConflictKind.Contradiction,
              ConflictSeverity.Fatal,
              claim1,
              negatedClaim,
              `Direct contradiction: ${claim1} and ${negatedClaim}`,
              [
                { type: "positive", address: claim1, content: evidence1, hash: hashString(evidence1) },
                { type: "negative", address: negatedClaim, content: context.claims.get(negatedClaim)!, hash: hashString(context.claims.get(negatedClaim)!) }
              ]
            ));
          }
        }
        
        return conflicts;
      }
    });
    
    // Type mismatch detector
    this.detectors.push({
      name: "TypeMismatchDetector",
      kinds: [ConflictKind.TypeMismatch],
      detect: (context) => {
        const conflicts: ConflictReceipt[] = [];
        
        for (const [source, expectedType] of context.typeExpectations) {
          const actualType = context.actualTypes.get(source);
          if (actualType && actualType !== expectedType) {
            conflicts.push(this.createReceipt(
              ConflictKind.TypeMismatch,
              ConflictSeverity.Critical,
              source,
              expectedType,
              `Type mismatch: expected ${expectedType}, got ${actualType}`,
              [
                { type: "diagnostic", address: source, content: `${expectedType} vs ${actualType}`, hash: hashString(`${expectedType}:${actualType}`) }
              ]
            ));
          }
        }
        
        return conflicts;
      }
    });
    
    // Corridor violation detector
    this.detectors.push({
      name: "CorridorViolationDetector",
      kinds: [ConflictKind.CorridorViolation],
      detect: (context) => {
        const conflicts: ConflictReceipt[] = [];
        
        for (const [operation, budgets] of context.operations) {
          if (budgets.time > context.corridor.maxTime) {
            conflicts.push(this.createReceipt(
              ConflictKind.CorridorViolation,
              ConflictSeverity.Critical,
              operation,
              "time_budget",
              `Time budget exceeded: ${budgets.time} > ${context.corridor.maxTime}`,
              []
            ));
          }
          if (budgets.memory > context.corridor.maxMemory) {
            conflicts.push(this.createReceipt(
              ConflictKind.CorridorViolation,
              ConflictSeverity.Critical,
              operation,
              "memory_budget",
              `Memory budget exceeded: ${budgets.memory} > ${context.corridor.maxMemory}`,
              []
            ));
          }
        }
        
        return conflicts;
      }
    });
    
    // Replay drift detector
    this.detectors.push({
      name: "ReplayDriftDetector",
      kinds: [ConflictKind.ReplayDrift],
      detect: (context) => {
        const conflicts: ConflictReceipt[] = [];
        
        for (const [replayId, expectedHash] of context.replayExpectations) {
          const actualHash = context.replayResults.get(replayId);
          if (actualHash && actualHash !== expectedHash) {
            conflicts.push(this.createReceipt(
              ConflictKind.ReplayDrift,
              ConflictSeverity.Fatal,
              replayId,
              expectedHash,
              `Replay drift detected: hash mismatch`,
              [
                { type: "negative", address: replayId, content: `${expectedHash} vs ${actualHash}`, hash: hashString(`${expectedHash}:${actualHash}`) }
              ]
            ));
          }
        }
        
        return conflicts;
      }
    });
  }
  
  /**
   * Detect conflicts in context
   */
  detect(context: ConflictDetectionContext): ConflictDetectionResult {
    const allConflicts: ConflictReceipt[] = [];
    
    for (const detector of this.detectors) {
      const conflicts = detector.detect(context);
      allConflicts.push(...conflicts);
    }
    
    // Determine overall severity
    let severity = ConflictSeverity.Info;
    for (const conflict of allConflicts) {
      if (conflict.severity === ConflictSeverity.Fatal) {
        severity = ConflictSeverity.Fatal;
        break;
      }
      if (conflict.severity === ConflictSeverity.Critical && severity !== ConflictSeverity.Fatal) {
        severity = ConflictSeverity.Critical;
      }
      if (conflict.severity === ConflictSeverity.Warning && severity === ConflictSeverity.Info) {
        severity = ConflictSeverity.Warning;
      }
    }
    
    return {
      hasConflict: allConflicts.length > 0,
      conflicts: allConflicts,
      severity
    };
  }
  
  /**
   * Add custom detector
   */
  addDetector(detector: ConflictDetectorFn): void {
    this.detectors.push(detector);
  }
  
  private createReceipt(
    kind: ConflictKind,
    severity: ConflictSeverity,
    source: string,
    target: string,
    description: string,
    witnesses: WitnessRef[]
  ): ConflictReceipt {
    return {
      id: `conflict_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      kind,
      severity,
      source,
      target,
      description,
      witnesses,
      minimalWitnessSet: witnesses.map(w => w.address),
      timestamp: Date.now(),
      permanent: severity === ConflictSeverity.Fatal,
      hash: hashString(JSON.stringify({ kind, source, target, description }))
    };
  }
}

export interface ConflictDetectionContext {
  claims: Map<string, string>;
  typeExpectations: Map<string, string>;
  actualTypes: Map<string, string>;
  operations: Map<string, { time: number; memory: number }>;
  corridor: { maxTime: number; maxMemory: number };
  replayExpectations: Map<string, string>;
  replayResults: Map<string, string>;
}

export interface ConflictDetectorFn {
  name: string;
  kinds: ConflictKind[];
  detect: (context: ConflictDetectionContext) => ConflictReceipt[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: REFUTATION ROUTER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Refutation routing result
 */
export interface RefutationRoutingResult {
  found: boolean;
  route?: RefutationRoute;
  alternatives: RefutationRoute[];
}

/**
 * Refutation router
 */
export class RefutationRouter {
  /**
   * Find refutation route from source to FAIL
   */
  findRoute(
    source: string,
    conflict: ConflictReceipt,
    availableSteps: RefutationStepTemplate[]
  ): RefutationRoutingResult {
    const routes: RefutationRoute[] = [];
    
    // BFS to find all possible routes
    const queue: { current: string; path: RefutationStep[]; cost: number }[] = [
      { current: source, path: [], cost: 0 }
    ];
    const visited = new Set<string>();
    
    while (queue.length > 0) {
      const { current, path, cost } = queue.shift()!;
      
      if (visited.has(current)) continue;
      visited.add(current);
      
      // Check if we've reached a refutation
      if (this.isRefutation(current, conflict)) {
        routes.push({
          steps: path,
          cost,
          confidence: this.computeConfidence(path)
        });
        continue;
      }
      
      // Explore available steps
      for (const template of availableSteps) {
        if (template.applicableFrom(current)) {
          const step: RefutationStep = {
            from: current,
            to: template.target(current),
            operation: template.operation,
            justification: template.justification
          };
          
          queue.push({
            current: step.to,
            path: [...path, step],
            cost: cost + template.cost
          });
        }
      }
    }
    
    // Sort by cost
    routes.sort((a, b) => a.cost - b.cost);
    
    return {
      found: routes.length > 0,
      route: routes[0],
      alternatives: routes.slice(1, 4)  // Return top 3 alternatives
    };
  }
  
  /**
   * Validate refutation route
   */
  validateRoute(route: RefutationRoute, conflict: ConflictReceipt): RouteValidationResult {
    const errors: string[] = [];
    
    // Check step connectivity
    for (let i = 0; i < route.steps.length - 1; i++) {
      if (route.steps[i].to !== route.steps[i + 1].from) {
        errors.push(`Disconnected steps at ${i}: ${route.steps[i].to} ≠ ${route.steps[i + 1].from}`);
      }
    }
    
    // Check justifications
    for (const step of route.steps) {
      if (!step.justification || step.justification.length === 0) {
        errors.push(`Missing justification for step ${step.from} → ${step.to}`);
      }
    }
    
    // Check final step leads to refutation
    if (route.steps.length > 0) {
      const finalStep = route.steps[route.steps.length - 1];
      if (!this.isRefutation(finalStep.to, conflict)) {
        errors.push("Route does not terminate in refutation");
      }
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }
  
  private isRefutation(state: string, conflict: ConflictReceipt): boolean {
    // State is a refutation if it matches the conflict target
    return state === conflict.target || 
           state === "FAIL" || 
           state.startsWith("refuted_");
  }
  
  private computeConfidence(path: RefutationStep[]): number {
    if (path.length === 0) return 1.0;
    
    // Confidence decreases with path length
    return Math.pow(0.95, path.length);
  }
}

export interface RefutationStepTemplate {
  operation: RefutationStep["operation"];
  justification: string;
  cost: number;
  applicableFrom: (state: string) => boolean;
  target: (state: string) => string;
}

export interface RouteValidationResult {
  valid: boolean;
  errors: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: QUARANTINE MANAGER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Quarantine manager
 */
export class QuarantineManager {
  private capsules: Map<string, QuarantineCapsule> = new Map();
  private witnessMinimizer: WitnessMinimizer;
  private refutationRouter: RefutationRouter;
  
  constructor() {
    this.witnessMinimizer = new WitnessMinimizer();
    this.refutationRouter = new RefutationRouter();
  }
  
  /**
   * Create quarantine capsule from conflict
   */
  createCapsule(
    target: string,
    conflicts: ConflictReceipt[],
    availableSteps: RefutationStepTemplate[]
  ): QuarantineCapsule {
    // Collect all witnesses
    const allWitnesses: WitnessRef[] = [];
    for (const conflict of conflicts) {
      allWitnesses.push(...conflict.witnesses);
    }
    
    // Minimize witness set
    const minimalSet = this.witnessMinimizer.minimize(
      allWitnesses,
      conflicts.map(c => c.description).join("; ")
    );
    
    // Find refutation route
    const mainConflict = conflicts.find(c => c.severity === ConflictSeverity.Fatal) ?? conflicts[0];
    const routingResult = this.refutationRouter.findRoute(target, mainConflict, availableSteps);
    
    const capsule: QuarantineCapsule = {
      id: `quarantine_${target}_${Date.now()}`,
      target,
      conflictReceipts: conflicts,
      minimalWitnessSet: minimalSet,
      refutationRoute: routingResult.route ?? {
        steps: [],
        cost: Infinity,
        confidence: 0
      },
      isolationScope: this.computeIsolationScope(target, conflicts),
      created: Date.now(),
      permanent: conflicts.some(c => c.permanent),
      hash: ""
    };
    
    capsule.hash = hashString(JSON.stringify({
      target: capsule.target,
      conflictCount: capsule.conflictReceipts.length,
      permanent: capsule.permanent
    }));
    
    this.capsules.set(capsule.id, capsule);
    return capsule;
  }
  
  /**
   * Get quarantine capsule
   */
  getCapsule(id: string): QuarantineCapsule | undefined {
    return this.capsules.get(id);
  }
  
  /**
   * Check if target is quarantined
   */
  isQuarantined(target: string): boolean {
    for (const capsule of this.capsules.values()) {
      if (capsule.target === target || capsule.isolationScope.includes(target)) {
        return true;
      }
    }
    return false;
  }
  
  /**
   * Attempt repair
   */
  attemptRepair(capsuleId: string, repairPlan: RepairPlan): RepairResult {
    const capsule = this.capsules.get(capsuleId);
    if (!capsule) {
      return { success: false, reason: "Capsule not found" };
    }
    
    if (capsule.permanent) {
      return { success: false, reason: "Permanent quarantine cannot be repaired" };
    }
    
    // Execute repair plan
    let success = true;
    const completedSteps: string[] = [];
    
    for (const step of repairPlan.steps) {
      try {
        this.executeRepairStep(step);
        completedSteps.push(step.action);
      } catch (e) {
        success = false;
        break;
      }
    }
    
    if (success) {
      capsule.repairPlan = repairPlan;
      // Remove from quarantine
      this.capsules.delete(capsuleId);
    }
    
    return {
      success,
      completedSteps,
      reason: success ? undefined : "Repair step failed"
    };
  }
  
  /**
   * Get all quarantined targets
   */
  getQuarantinedTargets(): string[] {
    const targets = new Set<string>();
    for (const capsule of this.capsules.values()) {
      targets.add(capsule.target);
      capsule.isolationScope.forEach(t => targets.add(t));
    }
    return Array.from(targets);
  }
  
  private computeIsolationScope(target: string, conflicts: ConflictReceipt[]): string[] {
    const scope = new Set<string>();
    scope.add(target);
    
    for (const conflict of conflicts) {
      scope.add(conflict.source);
      scope.add(conflict.target);
    }
    
    return Array.from(scope);
  }
  
  private executeRepairStep(step: RepairStep): void {
    // Simplified - would execute actual repair
    if (step.action === "invalid") {
      throw new Error("Invalid repair step");
    }
  }
}

export interface RepairResult {
  success: boolean;
  completedSteps?: string[];
  reason?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: PERMANENCE CHECKER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Permanence criteria
 */
export interface PermanenceCriteria {
  kind: ConflictKind;
  minWitnessCount: number;
  requiresRefutationRoute: boolean;
  canBeOverridden: boolean;
}

/**
 * Permanence check result
 */
export interface PermanenceCheckResult {
  permanent: boolean;
  criteria: PermanenceCriteria[];
  overridable: boolean;
  confidence: number;
}

/**
 * Permanence checker
 */
export class PermanenceChecker {
  private criteria: Map<ConflictKind, PermanenceCriteria> = new Map();
  
  constructor() {
    this.initializeDefaultCriteria();
  }
  
  private initializeDefaultCriteria(): void {
    // Contradiction is always permanent
    this.criteria.set(ConflictKind.Contradiction, {
      kind: ConflictKind.Contradiction,
      minWitnessCount: 2,
      requiresRefutationRoute: true,
      canBeOverridden: false
    });
    
    // Replay drift is permanent
    this.criteria.set(ConflictKind.ReplayDrift, {
      kind: ConflictKind.ReplayDrift,
      minWitnessCount: 1,
      requiresRefutationRoute: false,
      canBeOverridden: false
    });
    
    // Type mismatch may be repairable
    this.criteria.set(ConflictKind.TypeMismatch, {
      kind: ConflictKind.TypeMismatch,
      minWitnessCount: 1,
      requiresRefutationRoute: false,
      canBeOverridden: true
    });
    
    // Corridor violation may be repairable
    this.criteria.set(ConflictKind.CorridorViolation, {
      kind: ConflictKind.CorridorViolation,
      minWitnessCount: 1,
      requiresRefutationRoute: false,
      canBeOverridden: true
    });
    
    // Persistent obstruction is permanent
    this.criteria.set(ConflictKind.ObstructionPersistent, {
      kind: ConflictKind.ObstructionPersistent,
      minWitnessCount: 3,
      requiresRefutationRoute: true,
      canBeOverridden: false
    });
  }
  
  /**
   * Check permanence of conflict
   */
  check(conflict: ConflictReceipt, refutationRoute?: RefutationRoute): PermanenceCheckResult {
    const crit = this.criteria.get(conflict.kind);
    if (!crit) {
      return {
        permanent: false,
        criteria: [],
        overridable: true,
        confidence: 0.5
      };
    }
    
    const metCriteria: PermanenceCriteria[] = [];
    let permanent = true;
    
    // Check witness count
    if (conflict.witnesses.length < crit.minWitnessCount) {
      permanent = false;
    } else {
      metCriteria.push(crit);
    }
    
    // Check refutation route requirement
    if (crit.requiresRefutationRoute && !refutationRoute) {
      permanent = false;
    }
    
    // Compute confidence
    const confidence = this.computeConfidence(conflict, crit, refutationRoute);
    
    return {
      permanent: permanent && !crit.canBeOverridden,
      criteria: metCriteria,
      overridable: crit.canBeOverridden,
      confidence
    };
  }
  
  /**
   * Add custom criteria
   */
  addCriteria(criteria: PermanenceCriteria): void {
    this.criteria.set(criteria.kind, criteria);
  }
  
  private computeConfidence(
    conflict: ConflictReceipt,
    criteria: PermanenceCriteria,
    route?: RefutationRoute
  ): number {
    let confidence = 0.5;
    
    // More witnesses = higher confidence
    const witnessBonus = Math.min(conflict.witnesses.length / 5, 0.3);
    confidence += witnessBonus;
    
    // Refutation route adds confidence
    if (route) {
      confidence += route.confidence * 0.2;
    }
    
    // Severity affects confidence
    if (conflict.severity === ConflictSeverity.Fatal) {
      confidence += 0.2;
    }
    
    return Math.min(confidence, 1.0);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: COMPLETE ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete Conflict Algebra Engine
 */
export class ConflictAlgebraEngine {
  private conflictDetector: ConflictDetector;
  private witnessMinimizer: WitnessMinimizer;
  private refutationRouter: RefutationRouter;
  private quarantineManager: QuarantineManager;
  private permanenceChecker: PermanenceChecker;
  
  private conflictHistory: ConflictReceipt[] = [];
  
  constructor() {
    this.conflictDetector = new ConflictDetector();
    this.witnessMinimizer = new WitnessMinimizer();
    this.refutationRouter = new RefutationRouter();
    this.quarantineManager = new QuarantineManager();
    this.permanenceChecker = new PermanenceChecker();
  }
  
  /**
   * Detect conflicts in context
   */
  detectConflicts(context: ConflictDetectionContext): ConflictDetectionResult {
    const result = this.conflictDetector.detect(context);
    
    // Add to history
    this.conflictHistory.push(...result.conflicts);
    
    return result;
  }
  
  /**
   * Minimize witness set
   */
  minimizeWitnesses(witnesses: WitnessRef[], claim: string): MinimalWitnessSet {
    return this.witnessMinimizer.minimize(witnesses, claim);
  }
  
  /**
   * Find refutation route
   */
  findRefutationRoute(
    source: string,
    conflict: ConflictReceipt,
    availableSteps: RefutationStepTemplate[]
  ): RefutationRoutingResult {
    return this.refutationRouter.findRoute(source, conflict, availableSteps);
  }
  
  /**
   * Create quarantine capsule
   */
  createQuarantine(
    target: string,
    conflicts: ConflictReceipt[],
    availableSteps: RefutationStepTemplate[]
  ): QuarantineCapsule {
    return this.quarantineManager.createCapsule(target, conflicts, availableSteps);
  }
  
  /**
   * Check if target is quarantined
   */
  isQuarantined(target: string): boolean {
    return this.quarantineManager.isQuarantined(target);
  }
  
  /**
   * Attempt repair
   */
  attemptRepair(capsuleId: string, repairPlan: RepairPlan): RepairResult {
    return this.quarantineManager.attemptRepair(capsuleId, repairPlan);
  }
  
  /**
   * Check permanence
   */
  checkPermanence(conflict: ConflictReceipt, route?: RefutationRoute): PermanenceCheckResult {
    return this.permanenceChecker.check(conflict, route);
  }
  
  /**
   * Full conflict analysis: detect → minimize → route → quarantine → check permanence
   */
  fullAnalysis(
    target: string,
    context: ConflictDetectionContext,
    availableSteps: RefutationStepTemplate[]
  ): FullConflictAnalysisResult {
    // Detect conflicts
    const detection = this.detectConflicts(context);
    
    if (!detection.hasConflict) {
      return {
        type: "NoConflict",
        target
      };
    }
    
    // Create quarantine
    const capsule = this.createQuarantine(target, detection.conflicts, availableSteps);
    
    // Check permanence for each conflict
    const permanenceResults: Map<string, PermanenceCheckResult> = new Map();
    for (const conflict of detection.conflicts) {
      const perm = this.checkPermanence(conflict, capsule.refutationRoute);
      permanenceResults.set(conflict.id, perm);
    }
    
    // Determine overall status
    const hasPermanent = Array.from(permanenceResults.values()).some(p => p.permanent);
    
    return {
      type: "Conflict",
      target,
      detection,
      capsule,
      permanenceResults,
      permanent: hasPermanent,
      repairPossible: !hasPermanent && detection.severity !== ConflictSeverity.Fatal
    };
  }
  
  /**
   * Get conflict history
   */
  getHistory(): ConflictReceipt[] {
    return [...this.conflictHistory];
  }
  
  /**
   * Get quarantined targets
   */
  getQuarantinedTargets(): string[] {
    return this.quarantineManager.getQuarantinedTargets();
  }
  
  /**
   * Get statistics
   */
  getStats(): ConflictAlgebraStats {
    return {
      totalConflicts: this.conflictHistory.length,
      quarantinedTargets: this.quarantineManager.getQuarantinedTargets().length,
      fatalConflicts: this.conflictHistory.filter(c => c.severity === ConflictSeverity.Fatal).length,
      permanentConflicts: this.conflictHistory.filter(c => c.permanent).length
    };
  }
}

export type FullConflictAnalysisResult =
  | { type: "NoConflict"; target: string }
  | {
      type: "Conflict";
      target: string;
      detection: ConflictDetectionResult;
      capsule: QuarantineCapsule;
      permanenceResults: Map<string, PermanenceCheckResult>;
      permanent: boolean;
      repairPossible: boolean;
    };

export interface ConflictAlgebraStats {
  totalConflicts: number;
  quarantinedTargets: number;
  fatalConflicts: number;
  permanentConflicts: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Enums
  ConflictKind,
  ConflictSeverity,
  
  // Classes
  WitnessMinimizer,
  ConflictDetector,
  RefutationRouter,
  QuarantineManager,
  PermanenceChecker,
  ConflictAlgebraEngine
};
