/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * TRUTH COLLAPSE ENGINE - Complete Implementation
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Collapse NEAR/AMBIG states to OK/FAIL through discriminator application.
 * 
 * Features:
 * - Claim representation with candidate sets
 * - Discriminator types (boolean, threshold, witness, composite)
 * - Collapse strategies (eager, lazy, scheduled)
 * - Obstruction analysis
 * - Evidence plan generation
 * - Collapse certification
 * 
 * @module TRUTH_COLLAPSE_ENGINE
 * @version 1.0.0
 */

import {
  TruthValue,
  TruthLattice,
  WitnessPtr,
  Witnesses,
  ReplayCapsule,
  ReplayCapsules,
  Corridors,
  ValidationResult
} from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: CLAIM REPRESENTATION
// ═══════════════════════════════════════════════════════════════════════════════

export interface Claim {
  id: string;
  statement: string;
  domain: string;
  truth: TruthValue;
  candidates?: Candidate[];
  evidence: Evidence[];
  metadata: ClaimMetadata;
}

export interface Candidate {
  id: string;
  value: unknown;
  probability: number;
  supportingEvidence: string[];  // Evidence IDs
  refutingEvidence: string[];
}

export interface Evidence {
  id: string;
  type: EvidenceType;
  content: unknown;
  source: string;
  strength: number;  // 0 to 1
  timestamp: number;
}

export type EvidenceType = 
  | "direct"       // Direct observation
  | "derived"      // Derived from other evidence
  | "testimonial"  // From external source
  | "computational"; // Computed result

export interface ClaimMetadata {
  createdAt: number;
  lastEvaluated: number;
  evaluationCount: number;
  collapseAttempts: number;
  corridor: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: DISCRIMINATORS
// ═══════════════════════════════════════════════════════════════════════════════

export interface Discriminator {
  id: string;
  name: string;
  type: DiscriminatorType;
  apply: (claim: Claim, context: CollapseContext) => DiscriminatorResult;
  cost: number;  // Computational cost
  reliability: number;  // 0 to 1
}

export type DiscriminatorType = 
  | "boolean"     // Yes/no decision
  | "threshold"   // Numeric threshold
  | "witness"     // Witness-based
  | "composite"   // Combination of discriminators
  | "probabilistic"; // Probability-based

export interface DiscriminatorResult {
  applied: boolean;
  eliminated: string[];  // Candidate IDs eliminated
  promoted: string[];    // Candidate IDs promoted
  newTruth?: TruthValue;
  confidence: number;
  witness?: WitnessPtr;
  reason: string;
}

export interface CollapseContext {
  corridor: Corridors.Corridor;
  maxIterations: number;
  targetTruth?: TruthValue;
  allowedDiscriminators?: string[];
  evidenceThreshold: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: DISCRIMINATOR IMPLEMENTATIONS
// ═══════════════════════════════════════════════════════════════════════════════

export namespace Discriminators {
  
  // Boolean discriminator: eliminates candidates that fail a predicate
  export function createBoolean(
    id: string,
    name: string,
    predicate: (candidate: Candidate) => boolean,
    cost: number = 1
  ): Discriminator {
    return {
      id,
      name,
      type: "boolean",
      cost,
      reliability: 1.0,
      apply: (claim: Claim, context: CollapseContext) => {
        if (!claim.candidates || claim.candidates.length === 0) {
          return {
            applied: false,
            eliminated: [],
            promoted: [],
            confidence: 0,
            reason: "No candidates to discriminate"
          };
        }
        
        const eliminated: string[] = [];
        const remaining: Candidate[] = [];
        
        for (const candidate of claim.candidates) {
          if (predicate(candidate)) {
            remaining.push(candidate);
          } else {
            eliminated.push(candidate.id);
          }
        }
        
        // Determine new truth
        let newTruth: TruthValue | undefined;
        if (remaining.length === 0) {
          newTruth = TruthValue.FAIL;
        } else if (remaining.length === 1 && remaining[0].probability > context.evidenceThreshold) {
          newTruth = TruthValue.OK;
        } else if (remaining.length < (claim.candidates?.length ?? 0)) {
          newTruth = TruthValue.NEAR;
        }
        
        return {
          applied: eliminated.length > 0,
          eliminated,
          promoted: remaining.length === 1 ? [remaining[0].id] : [],
          newTruth,
          confidence: eliminated.length > 0 ? 0.9 : 0,
          reason: `Eliminated ${eliminated.length} candidates via ${name}`
        };
      }
    };
  }
  
  // Threshold discriminator: eliminates candidates below probability threshold
  export function createThreshold(
    id: string,
    name: string,
    threshold: number,
    cost: number = 1
  ): Discriminator {
    return {
      id,
      name,
      type: "threshold",
      cost,
      reliability: 0.95,
      apply: (claim: Claim, context: CollapseContext) => {
        if (!claim.candidates || claim.candidates.length === 0) {
          return {
            applied: false,
            eliminated: [],
            promoted: [],
            confidence: 0,
            reason: "No candidates to discriminate"
          };
        }
        
        const eliminated: string[] = [];
        const remaining: Candidate[] = [];
        
        for (const candidate of claim.candidates) {
          if (candidate.probability >= threshold) {
            remaining.push(candidate);
          } else {
            eliminated.push(candidate.id);
          }
        }
        
        // Renormalize probabilities
        const totalProb = remaining.reduce((sum, c) => sum + c.probability, 0);
        for (const c of remaining) {
          c.probability = c.probability / totalProb;
        }
        
        let newTruth: TruthValue | undefined;
        if (remaining.length === 0) {
          newTruth = TruthValue.FAIL;
        } else if (remaining.length === 1 && remaining[0].probability > context.evidenceThreshold) {
          newTruth = TruthValue.OK;
        }
        
        return {
          applied: eliminated.length > 0,
          eliminated,
          promoted: remaining.length === 1 ? [remaining[0].id] : [],
          newTruth,
          confidence: eliminated.length > 0 ? 0.85 : 0,
          reason: `Eliminated ${eliminated.length} candidates below threshold ${threshold}`
        };
      }
    };
  }
  
  // Witness discriminator: requires witness for promotion
  export function createWitness(
    id: string,
    name: string,
    witnessRequirement: (candidate: Candidate, evidence: Evidence[]) => boolean,
    cost: number = 5
  ): Discriminator {
    return {
      id,
      name,
      type: "witness",
      cost,
      reliability: 0.99,
      apply: (claim: Claim, context: CollapseContext) => {
        if (!claim.candidates || claim.candidates.length === 0) {
          return {
            applied: false,
            eliminated: [],
            promoted: [],
            confidence: 0,
            reason: "No candidates to discriminate"
          };
        }
        
        const promoted: string[] = [];
        
        for (const candidate of claim.candidates) {
          const relevantEvidence = claim.evidence.filter(
            e => candidate.supportingEvidence.includes(e.id)
          );
          
          if (witnessRequirement(candidate, relevantEvidence)) {
            promoted.push(candidate.id);
          }
        }
        
        let newTruth: TruthValue | undefined;
        let witness: WitnessPtr | undefined;
        
        if (promoted.length === 1) {
          newTruth = TruthValue.OK;
          witness = Witnesses.createDirect(
            promoted,
            { discriminator: id, claim: claim.id }
          );
        }
        
        return {
          applied: promoted.length > 0,
          eliminated: [],
          promoted,
          newTruth,
          confidence: promoted.length > 0 ? 0.95 : 0,
          witness,
          reason: `Witnessed ${promoted.length} candidates via ${name}`
        };
      }
    };
  }
  
  // Composite discriminator: applies multiple discriminators in sequence
  export function createComposite(
    id: string,
    name: string,
    discriminators: Discriminator[],
    mode: "all" | "any" = "all"
  ): Discriminator {
    return {
      id,
      name,
      type: "composite",
      cost: discriminators.reduce((sum, d) => sum + d.cost, 0),
      reliability: mode === "all" 
        ? discriminators.reduce((prod, d) => prod * d.reliability, 1)
        : 1 - discriminators.reduce((prod, d) => prod * (1 - d.reliability), 1),
      apply: (claim: Claim, context: CollapseContext) => {
        let currentClaim = { ...claim };
        const allEliminated: string[] = [];
        const allPromoted: string[] = [];
        let finalTruth: TruthValue | undefined;
        let maxConfidence = 0;
        const reasons: string[] = [];
        
        for (const disc of discriminators) {
          const result = disc.apply(currentClaim, context);
          
          if (result.applied) {
            allEliminated.push(...result.eliminated);
            allPromoted.push(...result.promoted);
            
            // Update candidates
            if (currentClaim.candidates) {
              currentClaim = {
                ...currentClaim,
                candidates: currentClaim.candidates.filter(
                  c => !result.eliminated.includes(c.id)
                )
              };
            }
            
            if (result.newTruth !== undefined) {
              finalTruth = result.newTruth;
            }
            
            maxConfidence = Math.max(maxConfidence, result.confidence);
            reasons.push(result.reason);
            
            // Early exit conditions
            if (finalTruth === TruthValue.OK || finalTruth === TruthValue.FAIL) {
              break;
            }
          }
        }
        
        return {
          applied: allEliminated.length > 0 || allPromoted.length > 0,
          eliminated: [...new Set(allEliminated)],
          promoted: [...new Set(allPromoted)],
          newTruth: finalTruth,
          confidence: maxConfidence,
          reason: reasons.join("; ")
        };
      }
    };
  }
  
  // Probabilistic discriminator: uses Bayesian updating
  export function createProbabilistic(
    id: string,
    name: string,
    likelihoodFn: (candidate: Candidate, evidence: Evidence) => number,
    cost: number = 3
  ): Discriminator {
    return {
      id,
      name,
      type: "probabilistic",
      cost,
      reliability: 0.9,
      apply: (claim: Claim, context: CollapseContext) => {
        if (!claim.candidates || claim.candidates.length === 0) {
          return {
            applied: false,
            eliminated: [],
            promoted: [],
            confidence: 0,
            reason: "No candidates to discriminate"
          };
        }
        
        // Bayesian update for each candidate
        const posteriors = new Map<string, number>();
        
        for (const candidate of claim.candidates) {
          let posterior = candidate.probability;
          
          for (const evidence of claim.evidence) {
            const likelihood = likelihoodFn(candidate, evidence);
            posterior *= likelihood;
          }
          
          posteriors.set(candidate.id, posterior);
        }
        
        // Normalize
        const total = Array.from(posteriors.values()).reduce((a, b) => a + b, 0);
        for (const [id, p] of posteriors) {
          posteriors.set(id, p / total);
        }
        
        // Find eliminated (below threshold) and promoted (above threshold)
        const eliminated: string[] = [];
        const promoted: string[] = [];
        
        for (const [id, p] of posteriors) {
          if (p < 0.01) {
            eliminated.push(id);
          } else if (p > context.evidenceThreshold) {
            promoted.push(id);
          }
        }
        
        let newTruth: TruthValue | undefined;
        if (promoted.length === 1) {
          newTruth = TruthValue.OK;
        } else if (eliminated.length === (claim.candidates?.length ?? 0)) {
          newTruth = TruthValue.FAIL;
        }
        
        return {
          applied: eliminated.length > 0 || promoted.length > 0,
          eliminated,
          promoted,
          newTruth,
          confidence: Math.max(...posteriors.values()),
          reason: `Bayesian update: ${eliminated.length} eliminated, ${promoted.length} promoted`
        };
      }
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: COLLAPSE ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

export interface CollapseResult {
  success: boolean;
  claim: Claim;
  finalTruth: TruthValue;
  iterations: number;
  discriminatorsApplied: string[];
  totalCost: number;
  certificate?: CollapseCertificate;
  obstruction?: Obstruction;
}

export interface CollapseCertificate {
  claimId: string;
  finalTruth: TruthValue;
  discriminatorChain: string[];
  witness?: WitnessPtr;
  replay?: ReplayCapsule;
  timestamp: number;
}

export interface Obstruction {
  type: ObstructionType;
  description: string;
  blockingCandidates: string[];
  requiredEvidence: string[];
  estimatedCost: number;
}

export type ObstructionType = 
  | "insufficient_evidence"
  | "conflicting_evidence"
  | "budget_exhausted"
  | "no_discriminator"
  | "cycle_detected";

export class CollapseEngine {
  private discriminators: Map<string, Discriminator> = new Map();
  private collapseHistory: Map<string, CollapseResult[]> = new Map();
  
  constructor() {
    // Register default discriminators
    this.registerDiscriminator(
      Discriminators.createThreshold("threshold_low", "Low Threshold", 0.01)
    );
    this.registerDiscriminator(
      Discriminators.createThreshold("threshold_mid", "Mid Threshold", 0.1)
    );
    this.registerDiscriminator(
      Discriminators.createThreshold("threshold_high", "High Threshold", 0.5)
    );
  }
  
  registerDiscriminator(disc: Discriminator): void {
    this.discriminators.set(disc.id, disc);
  }
  
  getDiscriminator(id: string): Discriminator | undefined {
    return this.discriminators.get(id);
  }
  
  // Main collapse function
  collapse(claim: Claim, context: CollapseContext): CollapseResult {
    let currentClaim = { ...claim };
    let iterations = 0;
    const appliedDiscriminators: string[] = [];
    let totalCost = 0;
    
    // Check if already collapsed
    if (currentClaim.truth === TruthValue.OK || currentClaim.truth === TruthValue.FAIL) {
      return {
        success: true,
        claim: currentClaim,
        finalTruth: currentClaim.truth,
        iterations: 0,
        discriminatorsApplied: [],
        totalCost: 0
      };
    }
    
    // Collapse loop
    while (iterations < context.maxIterations) {
      iterations++;
      
      // Check budget
      if (totalCost > context.corridor.budgets.kappa_compute) {
        return {
          success: false,
          claim: currentClaim,
          finalTruth: currentClaim.truth,
          iterations,
          discriminatorsApplied: appliedDiscriminators,
          totalCost,
          obstruction: {
            type: "budget_exhausted",
            description: "Compute budget exhausted",
            blockingCandidates: currentClaim.candidates?.map(c => c.id) ?? [],
            requiredEvidence: [],
            estimatedCost: 0
          }
        };
      }
      
      // Select best discriminator
      const disc = this.selectDiscriminator(currentClaim, context, appliedDiscriminators);
      
      if (!disc) {
        // No applicable discriminator
        const obstruction = this.analyzeObstruction(currentClaim, context);
        return {
          success: false,
          claim: currentClaim,
          finalTruth: currentClaim.truth,
          iterations,
          discriminatorsApplied: appliedDiscriminators,
          totalCost,
          obstruction
        };
      }
      
      // Apply discriminator
      const result = disc.apply(currentClaim, context);
      totalCost += disc.cost;
      
      if (result.applied) {
        appliedDiscriminators.push(disc.id);
        
        // Update claim
        if (currentClaim.candidates) {
          currentClaim = {
            ...currentClaim,
            candidates: currentClaim.candidates.filter(
              c => !result.eliminated.includes(c.id)
            ),
            metadata: {
              ...currentClaim.metadata,
              lastEvaluated: Date.now(),
              evaluationCount: currentClaim.metadata.evaluationCount + 1
            }
          };
        }
        
        if (result.newTruth !== undefined) {
          currentClaim.truth = result.newTruth;
        }
        
        // Check if collapsed
        if (currentClaim.truth === TruthValue.OK || currentClaim.truth === TruthValue.FAIL) {
          // Create certificate
          const certificate = this.createCertificate(
            currentClaim,
            appliedDiscriminators,
            result.witness
          );
          
          return {
            success: true,
            claim: currentClaim,
            finalTruth: currentClaim.truth,
            iterations,
            discriminatorsApplied: appliedDiscriminators,
            totalCost,
            certificate
          };
        }
      }
    }
    
    // Max iterations reached
    return {
      success: false,
      claim: currentClaim,
      finalTruth: currentClaim.truth,
      iterations,
      discriminatorsApplied: appliedDiscriminators,
      totalCost,
      obstruction: {
        type: "cycle_detected",
        description: "Max iterations reached without collapse",
        blockingCandidates: currentClaim.candidates?.map(c => c.id) ?? [],
        requiredEvidence: this.identifyRequiredEvidence(currentClaim),
        estimatedCost: 100
      }
    };
  }
  
  // Select best discriminator for current state
  private selectDiscriminator(
    claim: Claim,
    context: CollapseContext,
    alreadyApplied: string[]
  ): Discriminator | null {
    let bestDisc: Discriminator | null = null;
    let bestScore = -Infinity;
    
    for (const disc of this.discriminators.values()) {
      // Skip if already applied (avoid loops)
      if (alreadyApplied.includes(disc.id)) continue;
      
      // Skip if not in allowed list
      if (context.allowedDiscriminators && 
          !context.allowedDiscriminators.includes(disc.id)) continue;
      
      // Skip if too expensive
      if (disc.cost > context.corridor.budgets.kappa_compute) continue;
      
      // Score: reliability / cost
      const score = disc.reliability / disc.cost;
      
      if (score > bestScore) {
        bestScore = score;
        bestDisc = disc;
      }
    }
    
    return bestDisc;
  }
  
  // Analyze why collapse is blocked
  private analyzeObstruction(claim: Claim, context: CollapseContext): Obstruction {
    // Check for conflicting evidence
    if (claim.candidates && claim.candidates.length > 1) {
      const hasConflict = claim.candidates.some(c => 
        c.supportingEvidence.length > 0 && c.refutingEvidence.length > 0
      );
      
      if (hasConflict) {
        return {
          type: "conflicting_evidence",
          description: "Evidence supports multiple incompatible candidates",
          blockingCandidates: claim.candidates.map(c => c.id),
          requiredEvidence: ["decisive_evidence"],
          estimatedCost: 50
        };
      }
    }
    
    // Check for insufficient evidence
    const totalEvidence = claim.evidence.length;
    if (totalEvidence < 3) {
      return {
        type: "insufficient_evidence",
        description: `Only ${totalEvidence} pieces of evidence available`,
        blockingCandidates: claim.candidates?.map(c => c.id) ?? [],
        requiredEvidence: this.identifyRequiredEvidence(claim),
        estimatedCost: 20
      };
    }
    
    return {
      type: "no_discriminator",
      description: "No applicable discriminator found",
      blockingCandidates: claim.candidates?.map(c => c.id) ?? [],
      requiredEvidence: [],
      estimatedCost: 100
    };
  }
  
  // Identify what evidence would help
  private identifyRequiredEvidence(claim: Claim): string[] {
    const required: string[] = [];
    
    if (claim.candidates && claim.candidates.length > 1) {
      required.push("discriminating_observation");
    }
    
    if (claim.evidence.filter(e => e.type === "direct").length === 0) {
      required.push("direct_observation");
    }
    
    if (claim.evidence.filter(e => e.strength > 0.8).length === 0) {
      required.push("high_strength_evidence");
    }
    
    return required;
  }
  
  // Create collapse certificate
  private createCertificate(
    claim: Claim,
    discriminatorChain: string[],
    witness?: WitnessPtr
  ): CollapseCertificate {
    return {
      claimId: claim.id,
      finalTruth: claim.truth,
      discriminatorChain,
      witness,
      timestamp: Date.now()
    };
  }
  
  // Generate evidence plan for AMBIG claim
  generateEvidencePlan(claim: Claim): EvidencePlan {
    const steps: EvidencePlanStep[] = [];
    
    // Check what evidence is missing
    const hasDirectEvidence = claim.evidence.some(e => e.type === "direct");
    const hasHighStrength = claim.evidence.some(e => e.strength > 0.8);
    const candidateCount = claim.candidates?.length ?? 0;
    
    if (!hasDirectEvidence) {
      steps.push({
        action: "gather_direct_observation",
        description: "Obtain direct observational evidence",
        estimatedCost: 10,
        expectedImpact: 0.3
      });
    }
    
    if (!hasHighStrength) {
      steps.push({
        action: "strengthen_evidence",
        description: "Gather high-strength corroborating evidence",
        estimatedCost: 15,
        expectedImpact: 0.4
      });
    }
    
    if (candidateCount > 2) {
      steps.push({
        action: "discriminate_candidates",
        description: `Reduce ${candidateCount} candidates through targeted evidence`,
        estimatedCost: 20,
        expectedImpact: 0.5
      });
    }
    
    return {
      claimId: claim.id,
      currentTruth: claim.truth,
      targetTruth: TruthValue.OK,
      steps,
      totalEstimatedCost: steps.reduce((sum, s) => sum + s.estimatedCost, 0),
      probabilityOfSuccess: 1 - steps.reduce((prod, s) => prod * (1 - s.expectedImpact), 1)
    };
  }
}

export interface EvidencePlan {
  claimId: string;
  currentTruth: TruthValue;
  targetTruth: TruthValue;
  steps: EvidencePlanStep[];
  totalEstimatedCost: number;
  probabilityOfSuccess: number;
}

export interface EvidencePlanStep {
  action: string;
  description: string;
  estimatedCost: number;
  expectedImpact: number;  // Probability of contributing to collapse
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: BATCH COLLAPSE
// ═══════════════════════════════════════════════════════════════════════════════

export class BatchCollapser {
  private engine: CollapseEngine;
  
  constructor(engine?: CollapseEngine) {
    this.engine = engine ?? new CollapseEngine();
  }
  
  // Collapse multiple claims with shared budget
  collapseBatch(
    claims: Claim[],
    corridor: Corridors.Corridor,
    strategy: BatchStrategy = "priority"
  ): BatchCollapseResult {
    const results: CollapseResult[] = [];
    let remainingBudget = corridor.budgets.kappa_compute;
    
    // Sort claims by strategy
    const sortedClaims = this.sortByStrategy(claims, strategy);
    
    for (const claim of sortedClaims) {
      if (remainingBudget <= 0) break;
      
      const context: CollapseContext = {
        corridor: {
          ...corridor,
          budgets: { ...corridor.budgets, kappa_compute: remainingBudget }
        },
        maxIterations: 10,
        evidenceThreshold: 0.9
      };
      
      const result = this.engine.collapse(claim, context);
      results.push(result);
      remainingBudget -= result.totalCost;
    }
    
    // Compute summary statistics
    const collapsed = results.filter(r => 
      r.finalTruth === TruthValue.OK || r.finalTruth === TruthValue.FAIL
    ).length;
    
    return {
      results,
      totalClaims: claims.length,
      collapsedCount: collapsed,
      remainingAmbig: results.filter(r => r.finalTruth === TruthValue.AMBIG).length,
      remainingNear: results.filter(r => r.finalTruth === TruthValue.NEAR).length,
      totalCost: corridor.budgets.kappa_compute - remainingBudget,
      budgetRemaining: remainingBudget
    };
  }
  
  private sortByStrategy(claims: Claim[], strategy: BatchStrategy): Claim[] {
    switch (strategy) {
      case "priority":
        // Sort by evidence count (more evidence = easier to collapse)
        return [...claims].sort((a, b) => b.evidence.length - a.evidence.length);
      
      case "cheap_first":
        // Sort by candidate count (fewer = cheaper)
        return [...claims].sort((a, b) => 
          (a.candidates?.length ?? 0) - (b.candidates?.length ?? 0)
        );
      
      case "important_first":
        // Sort by evaluation count (more attempts = more important)
        return [...claims].sort((a, b) => 
          b.metadata.evaluationCount - a.metadata.evaluationCount
        );
      
      default:
        return claims;
    }
  }
}

export type BatchStrategy = "priority" | "cheap_first" | "important_first";

export interface BatchCollapseResult {
  results: CollapseResult[];
  totalClaims: number;
  collapsedCount: number;
  remainingAmbig: number;
  remainingNear: number;
  totalCost: number;
  budgetRemaining: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: SCHEDULED COLLAPSE
// ═══════════════════════════════════════════════════════════════════════════════

export interface CollapseSchedule {
  id: string;
  claims: string[];  // Claim IDs
  trigger: CollapseTrigger;
  context: CollapseContext;
  status: "pending" | "running" | "completed" | "failed";
  nextRun?: number;
  lastRun?: number;
  results?: BatchCollapseResult;
}

export type CollapseTrigger = 
  | { type: "immediate" }
  | { type: "scheduled"; runAt: number }
  | { type: "periodic"; intervalMs: number }
  | { type: "evidence"; minNewEvidence: number }
  | { type: "budget"; minBudget: number };

export class CollapseScheduler {
  private schedules: Map<string, CollapseSchedule> = new Map();
  private claimStore: Map<string, Claim> = new Map();
  private collapser: BatchCollapser;
  
  constructor() {
    this.collapser = new BatchCollapser();
  }
  
  registerClaim(claim: Claim): void {
    this.claimStore.set(claim.id, claim);
  }
  
  schedule(schedule: CollapseSchedule): void {
    this.schedules.set(schedule.id, schedule);
  }
  
  // Check and execute due schedules
  tick(currentTime: number = Date.now()): CollapseSchedule[] {
    const executed: CollapseSchedule[] = [];
    
    for (const schedule of this.schedules.values()) {
      if (schedule.status !== "pending") continue;
      
      if (this.shouldExecute(schedule, currentTime)) {
        this.executeSchedule(schedule);
        executed.push(schedule);
      }
    }
    
    return executed;
  }
  
  private shouldExecute(schedule: CollapseSchedule, currentTime: number): boolean {
    switch (schedule.trigger.type) {
      case "immediate":
        return true;
      
      case "scheduled":
        return currentTime >= schedule.trigger.runAt;
      
      case "periodic":
        if (!schedule.lastRun) return true;
        return currentTime >= schedule.lastRun + schedule.trigger.intervalMs;
      
      case "evidence":
        // Check if enough new evidence
        const claims = schedule.claims.map(id => this.claimStore.get(id)).filter(Boolean) as Claim[];
        const totalNewEvidence = claims.reduce(
          (sum, c) => sum + c.evidence.filter(e => e.timestamp > (schedule.lastRun ?? 0)).length,
          0
        );
        return totalNewEvidence >= schedule.trigger.minNewEvidence;
      
      case "budget":
        return schedule.context.corridor.budgets.kappa_compute >= schedule.trigger.minBudget;
    }
  }
  
  private executeSchedule(schedule: CollapseSchedule): void {
    schedule.status = "running";
    schedule.lastRun = Date.now();
    
    const claims = schedule.claims
      .map(id => this.claimStore.get(id))
      .filter(Boolean) as Claim[];
    
    try {
      schedule.results = this.collapser.collapseBatch(
        claims,
        schedule.context.corridor
      );
      
      schedule.status = "completed";
      
      // Update claims in store
      for (const result of schedule.results.results) {
        this.claimStore.set(result.claim.id, result.claim);
      }
      
      // Schedule next run for periodic triggers
      if (schedule.trigger.type === "periodic") {
        schedule.status = "pending";
        schedule.nextRun = Date.now() + schedule.trigger.intervalMs;
      }
    } catch (error) {
      schedule.status = "failed";
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  Discriminators,
  CollapseEngine,
  BatchCollapser,
  CollapseScheduler
};
