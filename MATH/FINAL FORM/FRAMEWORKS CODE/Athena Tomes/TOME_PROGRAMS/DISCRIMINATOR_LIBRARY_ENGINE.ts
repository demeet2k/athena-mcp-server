/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * DISCRIMINATOR LIBRARY ENGINE - Complete Discriminator System
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * From TRUTH-COLLAPSE_COMPILER Ch17:
 * 
 * Core Components:
 *   - Discriminator registration and lookup
 *   - Candidate elimination predicates
 *   - Information gain computation
 *   - Tie-break resolution
 *   - Decisive vs probabilistic discriminators
 *   - Budget-aware discriminator selection
 * 
 * Discriminator Types:
 *   - Refinement stability (Ch08/Ch15)
 *   - Conditioning gate (Ch08/Ch06)
 *   - Roundtrip defect (Ch03)
 *   - Horn filler/coherence (Ch11)
 *   - Information-gain tie-break (Ch17/Ch09)
 * 
 * @module DISCRIMINATOR_LIBRARY_ENGINE
 * @version 2.0.0
 */

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: DISCRIMINATOR TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Discriminator kind
 */
export enum DiscriminatorKind {
  Decisive = "Decisive",         // Deterministic elimination
  Probabilistic = "Probabilistic", // Score-based ranking
  Heuristic = "Heuristic",       // Rule of thumb
  Composite = "Composite"        // Combination of others
}

/**
 * Discriminator category
 */
export enum DiscriminatorCategory {
  RefinementStability = "RefinementStability",
  ConditioningGate = "ConditioningGate",
  RoundtripDefect = "RoundtripDefect",
  HornFiller = "HornFiller",
  InformationGain = "InformationGain",
  TypeConsistency = "TypeConsistency",
  ReplayDeterminism = "ReplayDeterminism",
  CorridorAdmissibility = "CorridorAdmissibility"
}

/**
 * Candidate for discrimination
 */
export interface Candidate<T = unknown> {
  id: string;
  value: T;
  score: number;
  evidence: EvidenceItem[];
  eliminated: boolean;
  eliminationReason?: string;
  metadata: CandidateMetadata;
}

export interface EvidenceItem {
  type: "positive" | "negative" | "neutral";
  source: string;
  content: string;
  strength: number;
}

export interface CandidateMetadata {
  created: number;
  lastScored: number;
  scoringRounds: number;
  discriminatorsApplied: string[];
}

/**
 * Discriminator definition
 */
export interface Discriminator<T = unknown> {
  id: string;
  name: string;
  kind: DiscriminatorKind;
  category: DiscriminatorCategory;
  cost: number;
  eliminationPower: number;
  description: string;
  apply: (candidates: Candidate<T>[], context: DiscriminatorContext) => DiscriminatorResult;
}

export interface DiscriminatorContext {
  budgets: DiscriminatorBudgets;
  history: DiscriminationHistory;
  configuration: DiscriminatorConfig;
}

export interface DiscriminatorBudgets {
  maxCost: number;
  maxTime: number;
  maxCandidates: number;
}

export interface DiscriminationHistory {
  rounds: DiscriminationRound[];
  totalCost: number;
  totalTime: number;
}

export interface DiscriminationRound {
  discriminatorId: string;
  eliminated: string[];
  costSpent: number;
  timeSpent: number;
}

export interface DiscriminatorConfig {
  requireWitness: boolean;
  stopOnFirst: boolean;
  tieBreakStrategy: TieBreakStrategy;
}

export type TieBreakStrategy = "first" | "random" | "maxEvidence" | "minCost";

/**
 * Discriminator result
 */
export interface DiscriminatorResult {
  discriminatorId: string;
  eliminated: string[];
  scores: Map<string, number>;
  remainingCount: number;
  decisive: boolean;
  reason: string;
  cost: number;
  time: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: BUILT-IN DISCRIMINATORS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Create refinement stability discriminator (Ch08/Ch15)
 */
function createRefinementStabilityDiscriminator(): Discriminator {
  return {
    id: "disc_refinement_stability",
    name: "RefinementStability",
    kind: DiscriminatorKind.Decisive,
    category: DiscriminatorCategory.RefinementStability,
    cost: 15,
    eliminationPower: 0.8,
    description: "Refine cover once; compare H¹ signature stability",
    apply: (candidates, context) => {
      const startTime = Date.now();
      const eliminated: string[] = [];
      const scores = new Map<string, number>();
      
      for (const candidate of candidates) {
        if (candidate.eliminated) continue;
        
        // Check for stability evidence
        const hasStability = candidate.evidence.some(e => 
          e.source.includes("stability") || e.source.includes("H1")
        );
        
        const positiveCount = candidate.evidence.filter(e => e.type === "positive").length;
        const stability = hasStability ? 1.0 : (positiveCount > 0 ? 0.5 : 0.0);
        
        scores.set(candidate.id, stability);
        
        if (stability < 0.3) {
          eliminated.push(candidate.id);
        }
      }
      
      return {
        discriminatorId: "disc_refinement_stability",
        eliminated,
        scores,
        remainingCount: candidates.length - eliminated.length,
        decisive: eliminated.length > 0,
        reason: "Refinement stability check",
        cost: 15,
        time: Date.now() - startTime
      };
    }
  };
}

/**
 * Create conditioning gate discriminator (Ch08/Ch06)
 */
function createConditioningGateDiscriminator(): Discriminator {
  return {
    id: "disc_conditioning_gate",
    name: "ConditioningGate",
    kind: DiscriminatorKind.Decisive,
    category: DiscriminatorCategory.ConditioningGate,
    cost: 20,
    eliminationPower: 0.7,
    description: "Compute cond(δ₁) margins; detect rank ambiguity",
    apply: (candidates, context) => {
      const startTime = Date.now();
      const eliminated: string[] = [];
      const scores = new Map<string, number>();
      
      for (const candidate of candidates) {
        if (candidate.eliminated) continue;
        
        // Simulate conditioning number check
        const conditionScore = computeConditionScore(candidate);
        scores.set(candidate.id, conditionScore);
        
        // Eliminate if poorly conditioned
        if (conditionScore < 0.2) {
          eliminated.push(candidate.id);
        }
      }
      
      return {
        discriminatorId: "disc_conditioning_gate",
        eliminated,
        scores,
        remainingCount: candidates.length - eliminated.length,
        decisive: eliminated.length > 0,
        reason: "Conditioning gate check",
        cost: 20,
        time: Date.now() - startTime
      };
    }
  };
}

function computeConditionScore(candidate: Candidate): number {
  // Simplified condition number heuristic
  const evidenceStrength = candidate.evidence.reduce((sum, e) => sum + e.strength, 0);
  const avgStrength = candidate.evidence.length > 0 
    ? evidenceStrength / candidate.evidence.length 
    : 0;
  return Math.min(avgStrength, 1.0);
}

/**
 * Create roundtrip defect discriminator (Ch03)
 */
function createRoundtripDefectDiscriminator(): Discriminator {
  return {
    id: "disc_roundtrip_defect",
    name: "RoundtripDefect",
    kind: DiscriminatorKind.Decisive,
    category: DiscriminatorCategory.RoundtripDefect,
    cost: 25,
    eliminationPower: 0.9,
    description: "Expand→collapse consistency of Čech complex digests",
    apply: (candidates, context) => {
      const startTime = Date.now();
      const eliminated: string[] = [];
      const scores = new Map<string, number>();
      
      for (const candidate of candidates) {
        if (candidate.eliminated) continue;
        
        // Check for roundtrip consistency
        const hasRoundtrip = checkRoundtripConsistency(candidate);
        scores.set(candidate.id, hasRoundtrip ? 1.0 : 0.0);
        
        if (!hasRoundtrip) {
          eliminated.push(candidate.id);
        }
      }
      
      return {
        discriminatorId: "disc_roundtrip_defect",
        eliminated,
        scores,
        remainingCount: candidates.length - eliminated.length,
        decisive: eliminated.length > 0,
        reason: "Roundtrip defect check",
        cost: 25,
        time: Date.now() - startTime
      };
    }
  };
}

function checkRoundtripConsistency(candidate: Candidate): boolean {
  // Simplified roundtrip check
  return candidate.evidence.some(e => 
    e.type === "positive" && e.strength > 0.5
  );
}

/**
 * Create horn filler discriminator (Ch11)
 */
function createHornFillerDiscriminator(): Discriminator {
  return {
    id: "disc_horn_filler",
    name: "HornFiller",
    kind: DiscriminatorKind.Decisive,
    category: DiscriminatorCategory.HornFiller,
    cost: 30,
    eliminationPower: 0.85,
    description: "Triple overlap restriction commutation",
    apply: (candidates, context) => {
      const startTime = Date.now();
      const eliminated: string[] = [];
      const scores = new Map<string, number>();
      
      for (const candidate of candidates) {
        if (candidate.eliminated) continue;
        
        // Check horn filling condition
        const fillable = checkHornFillable(candidate);
        scores.set(candidate.id, fillable ? 1.0 : 0.0);
        
        if (!fillable) {
          eliminated.push(candidate.id);
        }
      }
      
      return {
        discriminatorId: "disc_horn_filler",
        eliminated,
        scores,
        remainingCount: candidates.length - eliminated.length,
        decisive: eliminated.length > 0,
        reason: "Horn filler coherence check",
        cost: 30,
        time: Date.now() - startTime
      };
    }
  };
}

function checkHornFillable(candidate: Candidate): boolean {
  // Simplified horn filler check
  const positiveEvidence = candidate.evidence.filter(e => e.type === "positive");
  return positiveEvidence.length >= 2 || 
         (positiveEvidence.length === 1 && positiveEvidence[0].strength > 0.8);
}

/**
 * Create information gain discriminator (Ch17/Ch09)
 */
function createInformationGainDiscriminator(): Discriminator {
  return {
    id: "disc_information_gain",
    name: "InformationGain",
    kind: DiscriminatorKind.Probabilistic,
    category: DiscriminatorCategory.InformationGain,
    cost: 10,
    eliminationPower: 0.5,
    description: "Choose discriminator that reduces candidate entropy fastest",
    apply: (candidates, context) => {
      const startTime = Date.now();
      const eliminated: string[] = [];
      const scores = new Map<string, number>();
      
      // Compute entropy scores
      const totalEvidence = candidates.reduce(
        (sum, c) => sum + c.evidence.length, 0
      );
      
      for (const candidate of candidates) {
        if (candidate.eliminated) continue;
        
        // Information gain = evidence / total * log reduction
        const evidenceRatio = candidate.evidence.length / Math.max(totalEvidence, 1);
        const infoGain = evidenceRatio * candidate.score;
        scores.set(candidate.id, infoGain);
      }
      
      // Eliminate bottom 25% by information gain
      const sortedScores = Array.from(scores.entries())
        .sort(([, a], [, b]) => a - b);
      
      const cutoff = Math.floor(sortedScores.length * 0.25);
      for (let i = 0; i < cutoff; i++) {
        eliminated.push(sortedScores[i][0]);
      }
      
      return {
        discriminatorId: "disc_information_gain",
        eliminated,
        scores,
        remainingCount: candidates.length - eliminated.length,
        decisive: false,
        reason: "Information gain tie-break",
        cost: 10,
        time: Date.now() - startTime
      };
    }
  };
}

/**
 * Create type consistency discriminator
 */
function createTypeConsistencyDiscriminator(): Discriminator {
  return {
    id: "disc_type_consistency",
    name: "TypeConsistency",
    kind: DiscriminatorKind.Decisive,
    category: DiscriminatorCategory.TypeConsistency,
    cost: 12,
    eliminationPower: 0.75,
    description: "Check type constraints and harmony conditions",
    apply: (candidates, context) => {
      const startTime = Date.now();
      const eliminated: string[] = [];
      const scores = new Map<string, number>();
      
      for (const candidate of candidates) {
        if (candidate.eliminated) continue;
        
        // Type checking (simplified)
        const typeValid = candidate.value !== null && candidate.value !== undefined;
        scores.set(candidate.id, typeValid ? 1.0 : 0.0);
        
        if (!typeValid) {
          eliminated.push(candidate.id);
        }
      }
      
      return {
        discriminatorId: "disc_type_consistency",
        eliminated,
        scores,
        remainingCount: candidates.length - eliminated.length,
        decisive: eliminated.length > 0,
        reason: "Type consistency check",
        cost: 12,
        time: Date.now() - startTime
      };
    }
  };
}

/**
 * Create replay determinism discriminator
 */
function createReplayDeterminismDiscriminator(): Discriminator {
  return {
    id: "disc_replay_determinism",
    name: "ReplayDeterminism",
    kind: DiscriminatorKind.Decisive,
    category: DiscriminatorCategory.ReplayDeterminism,
    cost: 35,
    eliminationPower: 0.95,
    description: "Verify replay produces identical results",
    apply: (candidates, context) => {
      const startTime = Date.now();
      const eliminated: string[] = [];
      const scores = new Map<string, number>();
      
      for (const candidate of candidates) {
        if (candidate.eliminated) continue;
        
        // Check replay evidence
        const hasReplayEvidence = candidate.evidence.some(e => 
          e.source.includes("replay") && e.type === "positive"
        );
        
        scores.set(candidate.id, hasReplayEvidence ? 1.0 : 0.3);
        
        // Don't eliminate without replay evidence (just lower score)
      }
      
      return {
        discriminatorId: "disc_replay_determinism",
        eliminated,
        scores,
        remainingCount: candidates.length - eliminated.length,
        decisive: false,
        reason: "Replay determinism check",
        cost: 35,
        time: Date.now() - startTime
      };
    }
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: DISCRIMINATOR LIBRARY
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Discriminator library
 */
export class DiscriminatorLibrary {
  private discriminators: Map<string, Discriminator> = new Map();
  private categoryIndex: Map<DiscriminatorCategory, string[]> = new Map();
  
  constructor() {
    this.initializeBuiltInDiscriminators();
  }
  
  private initializeBuiltInDiscriminators(): void {
    this.register(createRefinementStabilityDiscriminator());
    this.register(createConditioningGateDiscriminator());
    this.register(createRoundtripDefectDiscriminator());
    this.register(createHornFillerDiscriminator());
    this.register(createInformationGainDiscriminator());
    this.register(createTypeConsistencyDiscriminator());
    this.register(createReplayDeterminismDiscriminator());
  }
  
  /**
   * Register discriminator
   */
  register(discriminator: Discriminator): void {
    this.discriminators.set(discriminator.id, discriminator);
    
    // Update category index
    if (!this.categoryIndex.has(discriminator.category)) {
      this.categoryIndex.set(discriminator.category, []);
    }
    this.categoryIndex.get(discriminator.category)!.push(discriminator.id);
  }
  
  /**
   * Get discriminator by ID
   */
  get(id: string): Discriminator | undefined {
    return this.discriminators.get(id);
  }
  
  /**
   * Get discriminators by category
   */
  getByCategory(category: DiscriminatorCategory): Discriminator[] {
    const ids = this.categoryIndex.get(category) ?? [];
    return ids.map(id => this.discriminators.get(id)!).filter(Boolean);
  }
  
  /**
   * Get discriminators by kind
   */
  getByKind(kind: DiscriminatorKind): Discriminator[] {
    return Array.from(this.discriminators.values())
      .filter(d => d.kind === kind);
  }
  
  /**
   * Get all discriminators
   */
  getAll(): Discriminator[] {
    return Array.from(this.discriminators.values());
  }
  
  /**
   * Get discriminators sorted by cost-effectiveness
   */
  getByCostEffectiveness(): Discriminator[] {
    return Array.from(this.discriminators.values())
      .sort((a, b) => (b.eliminationPower / b.cost) - (a.eliminationPower / a.cost));
  }
  
  /**
   * Get decisive discriminators
   */
  getDecisive(): Discriminator[] {
    return this.getByKind(DiscriminatorKind.Decisive);
  }
  
  /**
   * Get probabilistic discriminators
   */
  getProbabilistic(): Discriminator[] {
    return this.getByKind(DiscriminatorKind.Probabilistic);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: ELIMINATION ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Candidate set manager
 */
export interface CandidateSet<T = unknown> {
  id: string;
  target: string;
  candidates: Map<string, Candidate<T>>;
  eliminated: Set<string>;
  winner?: string;
  history: DiscriminationHistory;
}

/**
 * Elimination engine
 */
export class EliminationEngine {
  private library: DiscriminatorLibrary;
  
  constructor(library?: DiscriminatorLibrary) {
    this.library = library ?? new DiscriminatorLibrary();
  }
  
  /**
   * Create candidate set
   */
  createCandidateSet<T>(id: string, target: string, values: T[]): CandidateSet<T> {
    const candidates = new Map<string, Candidate<T>>();
    
    for (let i = 0; i < values.length; i++) {
      const candidateId = `cand_${id}_${i}`;
      candidates.set(candidateId, {
        id: candidateId,
        value: values[i],
        score: 1.0 / values.length,
        evidence: [],
        eliminated: false,
        metadata: {
          created: Date.now(),
          lastScored: Date.now(),
          scoringRounds: 0,
          discriminatorsApplied: []
        }
      });
    }
    
    return {
      id,
      target,
      candidates,
      eliminated: new Set(),
      history: {
        rounds: [],
        totalCost: 0,
        totalTime: 0
      }
    };
  }
  
  /**
   * Add evidence to candidate
   */
  addEvidence<T>(set: CandidateSet<T>, candidateId: string, evidence: EvidenceItem): void {
    const candidate = set.candidates.get(candidateId);
    if (candidate) {
      candidate.evidence.push(evidence);
    }
  }
  
  /**
   * Apply single discriminator
   */
  applyDiscriminator<T>(
    set: CandidateSet<T>,
    discriminatorId: string,
    context: DiscriminatorContext
  ): DiscriminatorResult {
    const discriminator = this.library.get(discriminatorId);
    if (!discriminator) {
      throw new Error(`Discriminator not found: ${discriminatorId}`);
    }
    
    const activeCandidates = Array.from(set.candidates.values())
      .filter(c => !c.eliminated);
    
    const result = discriminator.apply(activeCandidates, context);
    
    // Apply eliminations
    for (const id of result.eliminated) {
      const candidate = set.candidates.get(id);
      if (candidate) {
        candidate.eliminated = true;
        candidate.eliminationReason = discriminator.name;
        set.eliminated.add(id);
      }
    }
    
    // Update scores
    for (const [id, score] of result.scores) {
      const candidate = set.candidates.get(id);
      if (candidate) {
        candidate.score = (candidate.score + score) / 2;
        candidate.metadata.lastScored = Date.now();
        candidate.metadata.scoringRounds++;
        candidate.metadata.discriminatorsApplied.push(discriminatorId);
      }
    }
    
    // Update history
    set.history.rounds.push({
      discriminatorId,
      eliminated: result.eliminated,
      costSpent: result.cost,
      timeSpent: result.time
    });
    set.history.totalCost += result.cost;
    set.history.totalTime += result.time;
    
    return result;
  }
  
  /**
   * Run elimination loop with budget
   */
  runEliminationLoop<T>(
    set: CandidateSet<T>,
    budgets: DiscriminatorBudgets,
    config?: Partial<DiscriminatorConfig>
  ): EliminationLoopResult {
    const fullConfig: DiscriminatorConfig = {
      requireWitness: config?.requireWitness ?? false,
      stopOnFirst: config?.stopOnFirst ?? false,
      tieBreakStrategy: config?.tieBreakStrategy ?? "maxEvidence"
    };
    
    const context: DiscriminatorContext = {
      budgets,
      history: set.history,
      configuration: fullConfig
    };
    
    // Get discriminators sorted by cost-effectiveness
    const discriminators = this.library.getByCostEffectiveness();
    const results: DiscriminatorResult[] = [];
    let remainingBudget = budgets.maxCost;
    
    for (const disc of discriminators) {
      // Check budget
      if (disc.cost > remainingBudget) continue;
      
      // Check if already resolved
      const remaining = this.getRemainingCount(set);
      if (remaining <= 1) break;
      
      // Apply discriminator
      const result = this.applyDiscriminator(set, disc.id, context);
      results.push(result);
      remainingBudget -= result.cost;
      
      // Check stopOnFirst
      if (fullConfig.stopOnFirst && result.eliminated.length > 0) {
        break;
      }
    }
    
    // Determine winner if exactly one remaining
    const remainingCandidates = Array.from(set.candidates.values())
      .filter(c => !c.eliminated);
    
    if (remainingCandidates.length === 1) {
      set.winner = remainingCandidates[0].id;
    } else if (remainingCandidates.length > 1) {
      // Apply tie-break
      const winner = this.applyTieBreak(remainingCandidates, fullConfig.tieBreakStrategy);
      if (winner) {
        set.winner = winner.id;
      }
    }
    
    return {
      candidateSet: set,
      results,
      resolved: set.winner !== undefined,
      remainingCount: remainingCandidates.length,
      budgetSpent: budgets.maxCost - remainingBudget
    };
  }
  
  /**
   * Apply tie-break strategy
   */
  private applyTieBreak<T>(
    candidates: Candidate<T>[],
    strategy: TieBreakStrategy
  ): Candidate<T> | null {
    if (candidates.length === 0) return null;
    
    switch (strategy) {
      case "first":
        return candidates[0];
      
      case "random":
        return candidates[Math.floor(Math.random() * candidates.length)];
      
      case "maxEvidence":
        return candidates.reduce((best, c) => 
          c.evidence.length > best.evidence.length ? c : best
        );
      
      case "minCost":
        return candidates.reduce((best, c) => 
          c.metadata.scoringRounds < best.metadata.scoringRounds ? c : best
        );
      
      default:
        return candidates[0];
    }
  }
  
  /**
   * Get remaining candidate count
   */
  getRemainingCount<T>(set: CandidateSet<T>): number {
    return Array.from(set.candidates.values())
      .filter(c => !c.eliminated).length;
  }
}

export interface EliminationLoopResult {
  candidateSet: CandidateSet;
  results: DiscriminatorResult[];
  resolved: boolean;
  remainingCount: number;
  budgetSpent: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: INFORMATION GAIN CALCULATOR
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Information gain calculator
 */
export class InformationGainCalculator {
  /**
   * Compute entropy of candidate set
   */
  computeEntropy<T>(set: CandidateSet<T>): number {
    const remaining = Array.from(set.candidates.values())
      .filter(c => !c.eliminated);
    
    if (remaining.length <= 1) return 0;
    
    // Normalize scores
    const totalScore = remaining.reduce((sum, c) => sum + c.score, 0);
    const probabilities = remaining.map(c => c.score / Math.max(totalScore, 0.001));
    
    // Compute entropy: H = -Σ p log p
    let entropy = 0;
    for (const p of probabilities) {
      if (p > 0) {
        entropy -= p * Math.log2(p);
      }
    }
    
    return entropy;
  }
  
  /**
   * Estimate information gain from discriminator
   */
  estimateInformationGain<T>(
    set: CandidateSet<T>,
    discriminator: Discriminator
  ): number {
    const currentEntropy = this.computeEntropy(set);
    
    // Estimate expected elimination
    const expectedElimination = discriminator.eliminationPower * this.getRemainingCount(set);
    const expectedRemaining = Math.max(1, this.getRemainingCount(set) - expectedElimination);
    
    // Estimate new entropy (assuming uniform after elimination)
    const estimatedEntropy = Math.log2(expectedRemaining);
    
    // Information gain = reduction in entropy
    return Math.max(0, currentEntropy - estimatedEntropy);
  }
  
  /**
   * Rank discriminators by expected information gain
   */
  rankByInformationGain<T>(
    set: CandidateSet<T>,
    discriminators: Discriminator[]
  ): Array<{ discriminator: Discriminator; expectedGain: number; costEfficiency: number }> {
    return discriminators
      .map(d => ({
        discriminator: d,
        expectedGain: this.estimateInformationGain(set, d),
        costEfficiency: this.estimateInformationGain(set, d) / d.cost
      }))
      .sort((a, b) => b.costEfficiency - a.costEfficiency);
  }
  
  private getRemainingCount<T>(set: CandidateSet<T>): number {
    return Array.from(set.candidates.values())
      .filter(c => !c.eliminated).length;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: COMPLETE ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete Discriminator Library Engine
 */
export class DiscriminatorLibraryEngine {
  private library: DiscriminatorLibrary;
  private eliminationEngine: EliminationEngine;
  private infoGainCalculator: InformationGainCalculator;
  
  constructor() {
    this.library = new DiscriminatorLibrary();
    this.eliminationEngine = new EliminationEngine(this.library);
    this.infoGainCalculator = new InformationGainCalculator();
  }
  
  /**
   * Register custom discriminator
   */
  registerDiscriminator(discriminator: Discriminator): void {
    this.library.register(discriminator);
  }
  
  /**
   * Get discriminator
   */
  getDiscriminator(id: string): Discriminator | undefined {
    return this.library.get(id);
  }
  
  /**
   * Get all discriminators
   */
  getAllDiscriminators(): Discriminator[] {
    return this.library.getAll();
  }
  
  /**
   * Get discriminators by category
   */
  getDiscriminatorsByCategory(category: DiscriminatorCategory): Discriminator[] {
    return this.library.getByCategory(category);
  }
  
  /**
   * Create candidate set
   */
  createCandidateSet<T>(id: string, target: string, values: T[]): CandidateSet<T> {
    return this.eliminationEngine.createCandidateSet(id, target, values);
  }
  
  /**
   * Add evidence
   */
  addEvidence<T>(set: CandidateSet<T>, candidateId: string, evidence: EvidenceItem): void {
    this.eliminationEngine.addEvidence(set, candidateId, evidence);
  }
  
  /**
   * Run elimination
   */
  runElimination<T>(
    set: CandidateSet<T>,
    budgets: DiscriminatorBudgets,
    config?: Partial<DiscriminatorConfig>
  ): EliminationLoopResult {
    return this.eliminationEngine.runEliminationLoop(set, budgets, config);
  }
  
  /**
   * Compute entropy
   */
  computeEntropy<T>(set: CandidateSet<T>): number {
    return this.infoGainCalculator.computeEntropy(set);
  }
  
  /**
   * Rank discriminators by information gain
   */
  rankDiscriminators<T>(set: CandidateSet<T>): Array<{
    discriminator: Discriminator;
    expectedGain: number;
    costEfficiency: number;
  }> {
    return this.infoGainCalculator.rankByInformationGain(
      set,
      this.library.getAll()
    );
  }
  
  /**
   * Get best next discriminator
   */
  getBestNextDiscriminator<T>(
    set: CandidateSet<T>,
    remainingBudget: number
  ): Discriminator | null {
    const ranked = this.rankDiscriminators(set)
      .filter(r => r.discriminator.cost <= remainingBudget);
    
    return ranked.length > 0 ? ranked[0].discriminator : null;
  }
  
  /**
   * Get statistics
   */
  getStats(): DiscriminatorLibraryStats {
    const all = this.library.getAll();
    
    return {
      totalDiscriminators: all.length,
      decisiveCount: this.library.getDecisive().length,
      probabilisticCount: this.library.getProbabilistic().length,
      categories: Object.values(DiscriminatorCategory).length,
      avgCost: all.reduce((sum, d) => sum + d.cost, 0) / Math.max(all.length, 1),
      avgEliminationPower: all.reduce((sum, d) => sum + d.eliminationPower, 0) / Math.max(all.length, 1)
    };
  }
}

export interface DiscriminatorLibraryStats {
  totalDiscriminators: number;
  decisiveCount: number;
  probabilisticCount: number;
  categories: number;
  avgCost: number;
  avgEliminationPower: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Enums
  DiscriminatorKind,
  DiscriminatorCategory,
  
  // Classes
  DiscriminatorLibrary,
  EliminationEngine,
  InformationGainCalculator,
  DiscriminatorLibraryEngine
};
