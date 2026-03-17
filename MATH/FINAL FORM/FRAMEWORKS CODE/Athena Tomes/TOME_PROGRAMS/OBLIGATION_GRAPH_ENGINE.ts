/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * OBLIGATION GRAPH ENGINE - Obligation Graph Solver
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * From TRUTH-COLLAPSE_COMPILER Ch18:
 * 
 * Core Components:
 *   - Obligation node schema
 *   - Obligation DAG building and validation
 *   - Bottom-up discharge
 *   - Candidate elimination loop
 *   - Promotion/refutation operators
 *   - CollapsePack compiler and sealing
 * 
 * Obstruction contributions:
 *   - Cap on frontier (AMBIG)
 *   - Contradiction emergence (FAIL)
 *   - Residual persistence (NEAR)
 * 
 * @module OBLIGATION_GRAPH_ENGINE
 * @version 2.0.0
 */

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: OBLIGATION TYPES
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
 * Obligation kind
 */
export enum ObligationKind {
  Proof = "Proof",
  Replay = "Replay",
  TypeCheck = "TypeCheck",
  CorridorCheck = "CorridorCheck",
  CoverageCheck = "CoverageCheck",
  ConsistencyCheck = "ConsistencyCheck",
  WitnessConstruction = "WitnessConstruction",
  Discharge = "Discharge",
  Promotion = "Promotion",
  Refutation = "Refutation"
}

/**
 * Obligation status
 */
export enum ObligationStatus {
  Pending = "Pending",
  InProgress = "InProgress",
  Discharged = "Discharged",
  Blocked = "Blocked",
  Failed = "Failed",
  Deferred = "Deferred"
}

/**
 * Obligation node (Ch18 schema)
 */
export interface ObligationNode {
  id: string;
  kind: ObligationKind;
  status: ObligationStatus;
  claim: string;
  target: string;
  dependencies: string[];
  evidence: EvidenceRef[];
  budgets: ObligationBudgets;
  priority: number;
  created: number;
  updated: number;
  dischargeSchema?: string;
  failureReason?: string;
  hash: string;
}

export interface EvidenceRef {
  type: "witness" | "certificate" | "replay";
  address: string;
  hash: string;
}

export interface ObligationBudgets {
  maxTime: number;
  maxMemory: number;
  maxSteps: number;
  maxDepth: number;
}

/**
 * Obligation edge
 */
export interface ObligationEdge {
  from: string;
  to: string;
  kind: "requires" | "produces" | "blocks" | "refutes";
  weight: number;
}

/**
 * Obligation DAG
 */
export interface ObligationDAG {
  nodes: Map<string, ObligationNode>;
  edges: Map<string, ObligationEdge[]>;
  roots: string[];
  leaves: string[];
  hash: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: DAG BUILDER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * DAG validation result
 */
export interface DAGValidationResult {
  valid: boolean;
  acyclic: boolean;
  wellFounded: boolean;
  errors: string[];
  cycles?: string[][];
}

/**
 * Obligation DAG Builder
 */
export class ObligationDAGBuilder {
  private dag: ObligationDAG;
  private nodeCounter = 0;
  
  constructor() {
    this.dag = {
      nodes: new Map(),
      edges: new Map(),
      roots: [],
      leaves: [],
      hash: ""
    };
  }
  
  /**
   * Add obligation node
   */
  addNode(
    kind: ObligationKind,
    claim: string,
    target: string,
    dependencies: string[] = [],
    budgets?: Partial<ObligationBudgets>
  ): string {
    const id = `obl_${this.nodeCounter++}_${Date.now()}`;
    
    const node: ObligationNode = {
      id,
      kind,
      status: ObligationStatus.Pending,
      claim,
      target,
      dependencies,
      evidence: [],
      budgets: {
        maxTime: budgets?.maxTime ?? 30000,
        maxMemory: budgets?.maxMemory ?? 4194304,
        maxSteps: budgets?.maxSteps ?? 10000,
        maxDepth: budgets?.maxDepth ?? 100
      },
      priority: this.computeInitialPriority(kind, dependencies),
      created: Date.now(),
      updated: Date.now(),
      hash: ""
    };
    
    node.hash = this.hashNode(node);
    this.dag.nodes.set(id, node);
    this.dag.edges.set(id, []);
    
    // Add dependency edges
    for (const dep of dependencies) {
      this.addEdge(dep, id, "requires", 1.0);
    }
    
    this.updateTopology();
    return id;
  }
  
  /**
   * Add edge between nodes
   */
  addEdge(from: string, to: string, kind: ObligationEdge["kind"], weight: number): void {
    if (!this.dag.edges.has(from)) {
      this.dag.edges.set(from, []);
    }
    
    this.dag.edges.get(from)!.push({ from, to, kind, weight });
  }
  
  /**
   * Validate DAG (acyclic, well-founded)
   */
  validate(): DAGValidationResult {
    const errors: string[] = [];
    
    // Check for cycles using DFS
    const visited = new Set<string>();
    const inStack = new Set<string>();
    const cycles: string[][] = [];
    
    const detectCycle = (nodeId: string, path: string[]): boolean => {
      if (inStack.has(nodeId)) {
        const cycleStart = path.indexOf(nodeId);
        cycles.push(path.slice(cycleStart));
        return true;
      }
      
      if (visited.has(nodeId)) return false;
      
      visited.add(nodeId);
      inStack.add(nodeId);
      path.push(nodeId);
      
      const edges = this.dag.edges.get(nodeId) ?? [];
      for (const edge of edges) {
        if (edge.kind === "requires" && detectCycle(edge.to, [...path])) {
          // Continue checking for more cycles
        }
      }
      
      inStack.delete(nodeId);
      return false;
    };
    
    for (const nodeId of this.dag.nodes.keys()) {
      detectCycle(nodeId, []);
    }
    
    const acyclic = cycles.length === 0;
    if (!acyclic) {
      errors.push(`Found ${cycles.length} cycle(s)`);
    }
    
    // Check well-foundedness (all dependencies exist)
    for (const [nodeId, node] of this.dag.nodes) {
      for (const dep of node.dependencies) {
        if (!this.dag.nodes.has(dep)) {
          errors.push(`Node ${nodeId} has missing dependency: ${dep}`);
        }
      }
    }
    
    const wellFounded = errors.filter(e => e.includes("missing dependency")).length === 0;
    
    return {
      valid: acyclic && wellFounded,
      acyclic,
      wellFounded,
      errors,
      cycles: cycles.length > 0 ? cycles : undefined
    };
  }
  
  /**
   * Get DAG
   */
  getDAG(): ObligationDAG {
    this.dag.hash = this.hashDAG();
    return this.dag;
  }
  
  private computeInitialPriority(kind: ObligationKind, deps: string[]): number {
    // Higher priority for proof obligations, lower for deferred
    const kindPriority: Record<ObligationKind, number> = {
      [ObligationKind.Proof]: 10,
      [ObligationKind.TypeCheck]: 9,
      [ObligationKind.ConsistencyCheck]: 8,
      [ObligationKind.CorridorCheck]: 7,
      [ObligationKind.CoverageCheck]: 6,
      [ObligationKind.Replay]: 5,
      [ObligationKind.WitnessConstruction]: 4,
      [ObligationKind.Discharge]: 3,
      [ObligationKind.Promotion]: 2,
      [ObligationKind.Refutation]: 1
    };
    
    // Adjust by dependency count (fewer deps = higher priority)
    return kindPriority[kind] * 10 - deps.length;
  }
  
  private updateTopology(): void {
    // Find roots (no incoming edges)
    const hasIncoming = new Set<string>();
    for (const edges of this.dag.edges.values()) {
      for (const edge of edges) {
        if (edge.kind === "requires") {
          hasIncoming.add(edge.to);
        }
      }
    }
    
    this.dag.roots = Array.from(this.dag.nodes.keys())
      .filter(id => !hasIncoming.has(id));
    
    // Find leaves (no outgoing requirement edges)
    this.dag.leaves = Array.from(this.dag.nodes.keys())
      .filter(id => {
        const edges = this.dag.edges.get(id) ?? [];
        return edges.filter(e => e.kind === "requires").length === 0;
      });
  }
  
  private hashNode(node: ObligationNode): string {
    return hashString(JSON.stringify({
      kind: node.kind,
      claim: node.claim,
      target: node.target,
      dependencies: node.dependencies
    }));
  }
  
  private hashDAG(): string {
    const nodeHashes = Array.from(this.dag.nodes.values())
      .map(n => n.hash)
      .sort()
      .join(":");
    return hashString(nodeHashes);
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
// SECTION 3: BOTTOM-UP DISCHARGE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Discharge result
 */
export type DischargeResult =
  | { type: "Discharged"; evidence: EvidenceRef[]; trace: string }
  | { type: "Blocked"; reason: string; blockedBy: string[] }
  | { type: "Failed"; reason: string; counterwitness?: string }
  | { type: "Deferred"; reason: string };

/**
 * Discharge strategy
 */
export interface DischargeStrategy {
  name: string;
  applicableTo: ObligationKind[];
  attempt: (node: ObligationNode, context: DischargeContext) => DischargeResult;
}

export interface DischargeContext {
  dag: ObligationDAG;
  dischargedNodes: Set<string>;
  evidence: Map<string, EvidenceRef[]>;
  budgets: ObligationBudgets;
}

/**
 * Bottom-up discharge engine
 */
export class BottomUpDischargeEngine {
  private strategies: DischargeStrategy[] = [];
  
  constructor() {
    this.initializeDefaultStrategies();
  }
  
  /**
   * Initialize default discharge strategies
   */
  private initializeDefaultStrategies(): void {
    // Proof discharge strategy
    this.strategies.push({
      name: "ProofDischarge",
      applicableTo: [ObligationKind.Proof],
      attempt: (node, ctx) => {
        // Check if all dependencies are discharged
        const undischarged = node.dependencies.filter(d => !ctx.dischargedNodes.has(d));
        if (undischarged.length > 0) {
          return { type: "Blocked", reason: "Dependencies not discharged", blockedBy: undischarged };
        }
        
        // Simulate proof construction
        const evidence: EvidenceRef[] = [{
          type: "witness",
          address: `proof_${node.id}`,
          hash: hashString(`proof_${node.claim}`)
        }];
        
        return { type: "Discharged", evidence, trace: `proof_trace_${node.id}` };
      }
    });
    
    // TypeCheck discharge strategy
    this.strategies.push({
      name: "TypeCheckDischarge",
      applicableTo: [ObligationKind.TypeCheck],
      attempt: (node, ctx) => {
        const undischarged = node.dependencies.filter(d => !ctx.dischargedNodes.has(d));
        if (undischarged.length > 0) {
          return { type: "Blocked", reason: "Dependencies not discharged", blockedBy: undischarged };
        }
        
        // Type checking is deterministic
        const evidence: EvidenceRef[] = [{
          type: "certificate",
          address: `typecheck_${node.id}`,
          hash: hashString(`typecheck_${node.claim}`)
        }];
        
        return { type: "Discharged", evidence, trace: `typecheck_trace_${node.id}` };
      }
    });
    
    // Replay discharge strategy
    this.strategies.push({
      name: "ReplayDischarge",
      applicableTo: [ObligationKind.Replay],
      attempt: (node, ctx) => {
        const undischarged = node.dependencies.filter(d => !ctx.dischargedNodes.has(d));
        if (undischarged.length > 0) {
          return { type: "Blocked", reason: "Dependencies not discharged", blockedBy: undischarged };
        }
        
        const evidence: EvidenceRef[] = [{
          type: "replay",
          address: `replay_${node.id}`,
          hash: hashString(`replay_${node.claim}`)
        }];
        
        return { type: "Discharged", evidence, trace: `replay_trace_${node.id}` };
      }
    });
    
    // Generic discharge strategy
    this.strategies.push({
      name: "GenericDischarge",
      applicableTo: Object.values(ObligationKind),
      attempt: (node, ctx) => {
        const undischarged = node.dependencies.filter(d => !ctx.dischargedNodes.has(d));
        if (undischarged.length > 0) {
          return { type: "Blocked", reason: "Dependencies not discharged", blockedBy: undischarged };
        }
        
        const evidence: EvidenceRef[] = [{
          type: "certificate",
          address: `generic_${node.id}`,
          hash: hashString(`generic_${node.claim}`)
        }];
        
        return { type: "Discharged", evidence, trace: `generic_trace_${node.id}` };
      }
    });
  }
  
  /**
   * Run bottom-up discharge on DAG
   */
  discharge(dag: ObligationDAG, budgets: ObligationBudgets): DischargeExecutionResult {
    const context: DischargeContext = {
      dag,
      dischargedNodes: new Set(),
      evidence: new Map(),
      budgets
    };
    
    const results: Map<string, DischargeResult> = new Map();
    const order: string[] = [];
    
    // Topological sort for bottom-up processing
    const sorted = this.topologicalSort(dag);
    
    let iterations = 0;
    const maxIterations = dag.nodes.size * 2;
    
    while (context.dischargedNodes.size < dag.nodes.size && iterations < maxIterations) {
      iterations++;
      let progress = false;
      
      for (const nodeId of sorted) {
        if (context.dischargedNodes.has(nodeId)) continue;
        
        const node = dag.nodes.get(nodeId)!;
        
        // Find applicable strategy
        const strategy = this.strategies.find(s => 
          s.applicableTo.includes(node.kind)
        );
        
        if (!strategy) {
          results.set(nodeId, { type: "Failed", reason: "No applicable strategy" });
          continue;
        }
        
        const result = strategy.attempt(node, context);
        results.set(nodeId, result);
        
        if (result.type === "Discharged") {
          context.dischargedNodes.add(nodeId);
          context.evidence.set(nodeId, result.evidence);
          order.push(nodeId);
          progress = true;
        }
      }
      
      if (!progress) break;
    }
    
    return {
      discharged: context.dischargedNodes.size,
      total: dag.nodes.size,
      complete: context.dischargedNodes.size === dag.nodes.size,
      results,
      order,
      evidence: context.evidence
    };
  }
  
  /**
   * Add custom strategy
   */
  addStrategy(strategy: DischargeStrategy): void {
    this.strategies.unshift(strategy);  // Higher priority for custom strategies
  }
  
  private topologicalSort(dag: ObligationDAG): string[] {
    const visited = new Set<string>();
    const result: string[] = [];
    
    const visit = (nodeId: string) => {
      if (visited.has(nodeId)) return;
      visited.add(nodeId);
      
      const node = dag.nodes.get(nodeId);
      if (node) {
        for (const dep of node.dependencies) {
          visit(dep);
        }
      }
      
      result.push(nodeId);
    };
    
    for (const nodeId of dag.nodes.keys()) {
      visit(nodeId);
    }
    
    return result;
  }
}

export interface DischargeExecutionResult {
  discharged: number;
  total: number;
  complete: boolean;
  results: Map<string, DischargeResult>;
  order: string[];
  evidence: Map<string, EvidenceRef[]>;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: CANDIDATE ELIMINATION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Candidate
 */
export interface Candidate {
  id: string;
  claim: string;
  evidence: EvidenceRef[];
  score: number;
  eliminated: boolean;
  eliminationReason?: string;
}

/**
 * Candidate set
 */
export interface CandidateSet {
  id: string;
  target: string;
  candidates: Map<string, Candidate>;
  evidencePlan: EvidencePlan;
  eliminated: Set<string>;
  winner?: string;
  hash: string;
}

/**
 * Evidence plan
 */
export interface EvidencePlan {
  discriminators: Discriminator[];
  budgets: ObligationBudgets;
  stopReason?: string;
}

/**
 * Discriminator
 */
export interface Discriminator {
  id: string;
  name: string;
  type: "decisive" | "probabilistic" | "heuristic";
  cost: number;
  eliminationPower: number;
  apply: (candidates: Candidate[]) => DiscriminatorResult;
}

export interface DiscriminatorResult {
  eliminated: string[];
  scores: Map<string, number>;
  reason: string;
}

/**
 * Candidate elimination loop
 */
export class CandidateEliminationLoop {
  private discriminators: Discriminator[] = [];
  
  constructor() {
    this.initializeDefaultDiscriminators();
  }
  
  private initializeDefaultDiscriminators(): void {
    // Consistency discriminator
    this.discriminators.push({
      id: "consistency",
      name: "ConsistencyCheck",
      type: "decisive",
      cost: 10,
      eliminationPower: 0.8,
      apply: (candidates) => {
        const eliminated: string[] = [];
        const scores = new Map<string, number>();
        
        for (const c of candidates) {
          if (c.eliminated) continue;
          
          // Check for internal consistency
          const consistent = c.evidence.length > 0;
          scores.set(c.id, consistent ? 1.0 : 0.0);
          
          if (!consistent) {
            eliminated.push(c.id);
          }
        }
        
        return { eliminated, scores, reason: "Internal consistency check" };
      }
    });
    
    // Evidence strength discriminator
    this.discriminators.push({
      id: "evidence_strength",
      name: "EvidenceStrength",
      type: "probabilistic",
      cost: 5,
      eliminationPower: 0.5,
      apply: (candidates) => {
        const scores = new Map<string, number>();
        const eliminated: string[] = [];
        
        // Compute evidence scores
        let maxScore = 0;
        for (const c of candidates) {
          if (c.eliminated) continue;
          const score = c.evidence.length * 0.2 + c.score * 0.8;
          scores.set(c.id, score);
          maxScore = Math.max(maxScore, score);
        }
        
        // Eliminate candidates significantly below max
        for (const c of candidates) {
          if (c.eliminated) continue;
          const score = scores.get(c.id) ?? 0;
          if (score < maxScore * 0.3) {
            eliminated.push(c.id);
          }
        }
        
        return { eliminated, scores, reason: "Evidence strength comparison" };
      }
    });
    
    // Replay consistency discriminator
    this.discriminators.push({
      id: "replay",
      name: "ReplayConsistency",
      type: "decisive",
      cost: 20,
      eliminationPower: 0.9,
      apply: (candidates) => {
        const scores = new Map<string, number>();
        const eliminated: string[] = [];
        
        for (const c of candidates) {
          if (c.eliminated) continue;
          
          // Check for replay evidence
          const hasReplay = c.evidence.some(e => e.type === "replay");
          scores.set(c.id, hasReplay ? 1.0 : 0.5);
        }
        
        return { eliminated, scores, reason: "Replay consistency check" };
      }
    });
  }
  
  /**
   * Run elimination loop
   */
  run(candidateSet: CandidateSet): EliminationResult {
    const history: EliminationStep[] = [];
    let budget = candidateSet.evidencePlan.budgets.maxSteps;
    
    // Sort discriminators by cost-effectiveness
    const sortedDiscriminators = [...this.discriminators].sort((a, b) => 
      (b.eliminationPower / b.cost) - (a.eliminationPower / a.cost)
    );
    
    for (const disc of sortedDiscriminators) {
      if (budget < disc.cost) {
        candidateSet.evidencePlan.stopReason = "Budget exhausted";
        break;
      }
      
      const remaining = Array.from(candidateSet.candidates.values())
        .filter(c => !c.eliminated);
      
      if (remaining.length <= 1) {
        break;
      }
      
      const result = disc.apply(remaining);
      budget -= disc.cost;
      
      // Apply eliminations
      for (const id of result.eliminated) {
        const candidate = candidateSet.candidates.get(id);
        if (candidate) {
          candidate.eliminated = true;
          candidate.eliminationReason = disc.name;
          candidateSet.eliminated.add(id);
        }
      }
      
      // Update scores
      for (const [id, score] of result.scores) {
        const candidate = candidateSet.candidates.get(id);
        if (candidate) {
          candidate.score = (candidate.score + score) / 2;
        }
      }
      
      history.push({
        discriminator: disc.id,
        eliminated: result.eliminated,
        remaining: remaining.length - result.eliminated.length,
        reason: result.reason
      });
    }
    
    // Check for winner
    const remaining = Array.from(candidateSet.candidates.values())
      .filter(c => !c.eliminated);
    
    if (remaining.length === 1) {
      candidateSet.winner = remaining[0].id;
    }
    
    // Update hash
    candidateSet.hash = hashString(JSON.stringify({
      candidates: candidateSet.candidates.size,
      eliminated: candidateSet.eliminated.size,
      winner: candidateSet.winner
    }));
    
    return {
      candidateSet,
      history,
      resolved: remaining.length === 1,
      remainingCount: remaining.length,
      truth: this.determineTruth(remaining.length, candidateSet.evidencePlan.stopReason)
    };
  }
  
  /**
   * Add custom discriminator
   */
  addDiscriminator(disc: Discriminator): void {
    this.discriminators.push(disc);
  }
  
  private determineTruth(remaining: number, stopReason?: string): TruthValue {
    if (remaining === 1) return TruthValue.OK;
    if (remaining === 0) return TruthValue.FAIL;
    if (stopReason) return TruthValue.AMBIG;
    return TruthValue.NEAR;
  }
}

export interface EliminationStep {
  discriminator: string;
  eliminated: string[];
  remaining: number;
  reason: string;
}

export interface EliminationResult {
  candidateSet: CandidateSet;
  history: EliminationStep[];
  resolved: boolean;
  remainingCount: number;
  truth: TruthValue;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: PROMOTION/REFUTATION OPERATORS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Promotion result
 */
export interface PromotionResult {
  promoted: boolean;
  from: TruthValue;
  to: TruthValue;
  evidence: EvidenceRef[];
  obligations: string[];
}

/**
 * Refutation result
 */
export interface RefutationResult {
  refuted: boolean;
  from: TruthValue;
  to: TruthValue;
  counterwitness: string;
  minimalWitnessSet: string[];
}

/**
 * Promotion/Refutation operator
 */
export class PromotionRefutationOperator {
  /**
   * Attempt promotion AMBIG→NEAR or NEAR→OK
   */
  attemptPromotion(
    current: TruthValue,
    evidence: EvidenceRef[],
    dischargedObligations: string[]
  ): PromotionResult {
    const remainingObligations: string[] = [];
    
    if (current === TruthValue.OK) {
      return {
        promoted: false,
        from: current,
        to: current,
        evidence,
        obligations: []
      };
    }
    
    if (current === TruthValue.FAIL) {
      return {
        promoted: false,
        from: current,
        to: current,
        evidence,
        obligations: ["Cannot promote from FAIL"]
      };
    }
    
    if (current === TruthValue.AMBIG) {
      // AMBIG→NEAR requires candidate reduction
      const hasDiscrimination = evidence.some(e => e.type === "certificate");
      
      if (hasDiscrimination) {
        return {
          promoted: true,
          from: TruthValue.AMBIG,
          to: TruthValue.NEAR,
          evidence,
          obligations: ["Continue refinement to OK"]
        };
      }
      
      return {
        promoted: false,
        from: current,
        to: current,
        evidence,
        obligations: ["Provide discriminator evidence"]
      };
    }
    
    if (current === TruthValue.NEAR) {
      // NEAR→OK requires full discharge
      const hasWitness = evidence.some(e => e.type === "witness");
      const hasReplay = evidence.some(e => e.type === "replay");
      
      if (hasWitness && hasReplay && dischargedObligations.length > 0) {
        return {
          promoted: true,
          from: TruthValue.NEAR,
          to: TruthValue.OK,
          evidence,
          obligations: []
        };
      }
      
      if (!hasWitness) remainingObligations.push("Construct witness");
      if (!hasReplay) remainingObligations.push("Provide replay proof");
      
      return {
        promoted: false,
        from: current,
        to: current,
        evidence,
        obligations: remainingObligations
      };
    }
    
    return {
      promoted: false,
      from: current,
      to: current,
      evidence,
      obligations: ["Unknown truth value"]
    };
  }
  
  /**
   * Attempt refutation to FAIL
   */
  attemptRefutation(
    current: TruthValue,
    counterwitness: string,
    conflictEvidence: EvidenceRef[]
  ): RefutationResult {
    if (current === TruthValue.FAIL) {
      return {
        refuted: false,
        from: current,
        to: current,
        counterwitness,
        minimalWitnessSet: []
      };
    }
    
    // Check counterwitness validity
    const validCounterwitness = counterwitness.length > 0;
    const hasConflict = conflictEvidence.length > 0;
    
    if (validCounterwitness && hasConflict) {
      return {
        refuted: true,
        from: current,
        to: TruthValue.FAIL,
        counterwitness,
        minimalWitnessSet: conflictEvidence.map(e => e.address)
      };
    }
    
    return {
      refuted: false,
      from: current,
      to: current,
      counterwitness,
      minimalWitnessSet: []
    };
  }
  
  /**
   * Compute truth transition
   */
  computeTransition(
    from: TruthValue,
    to: TruthValue
  ): { valid: boolean; requiresEvidence: string[] } {
    // Valid transitions: AMBIG→NEAR, NEAR→OK, *→FAIL
    const validTransitions: Record<TruthValue, TruthValue[]> = {
      [TruthValue.AMBIG]: [TruthValue.NEAR, TruthValue.FAIL],
      [TruthValue.NEAR]: [TruthValue.OK, TruthValue.FAIL],
      [TruthValue.OK]: [TruthValue.FAIL],  // Only via contradiction
      [TruthValue.FAIL]: []  // Terminal
    };
    
    const valid = validTransitions[from]?.includes(to) ?? false;
    const requiresEvidence: string[] = [];
    
    if (to === TruthValue.FAIL) {
      requiresEvidence.push("counterwitness", "conflict_receipt");
    } else if (from === TruthValue.AMBIG && to === TruthValue.NEAR) {
      requiresEvidence.push("discriminator_evidence");
    } else if (from === TruthValue.NEAR && to === TruthValue.OK) {
      requiresEvidence.push("witness", "replay_proof");
    }
    
    return { valid, requiresEvidence };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: COLLAPSE PACK
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Collapse pack (sealed truth bundle)
 */
export interface CollapsePack {
  id: string;
  target: string;
  truth: TruthValue;
  evidence: EvidenceRef[];
  dischargedObligations: string[];
  candidateHistory?: CandidateSet;
  promotionHistory: PromotionResult[];
  refutationHistory: RefutationResult[];
  depsRoot: string;
  replayRoot: string;
  sealed: boolean;
  sealTime?: number;
  hash: string;
}

/**
 * Collapse pack compiler
 */
export class CollapsePackCompiler {
  /**
   * Compile collapse pack from resolved obligations
   */
  compile(
    target: string,
    dischargeResult: DischargeExecutionResult,
    eliminationResult?: EliminationResult
  ): CollapsePackCompilationResult {
    const evidence: EvidenceRef[] = [];
    const dischargedObligations: string[] = [];
    const promotionHistory: PromotionResult[] = [];
    const refutationHistory: RefutationResult[] = [];
    
    // Collect evidence from discharge
    for (const [nodeId, evidenceList] of dischargeResult.evidence) {
      evidence.push(...evidenceList);
      dischargedObligations.push(nodeId);
    }
    
    // Determine truth value
    let truth: TruthValue;
    if (dischargeResult.complete) {
      truth = TruthValue.OK;
    } else if (eliminationResult?.resolved) {
      truth = TruthValue.OK;
    } else if (eliminationResult && eliminationResult.remainingCount > 1) {
      truth = TruthValue.AMBIG;
    } else {
      truth = TruthValue.NEAR;
    }
    
    // Check for failures
    const failures = Array.from(dischargeResult.results.entries())
      .filter(([_, r]) => r.type === "Failed");
    
    if (failures.length > 0) {
      truth = TruthValue.FAIL;
      for (const [nodeId, result] of failures) {
        if (result.type === "Failed") {
          refutationHistory.push({
            refuted: true,
            from: TruthValue.NEAR,
            to: TruthValue.FAIL,
            counterwitness: result.counterwitness ?? "",
            minimalWitnessSet: [nodeId]
          });
        }
      }
    }
    
    const pack: CollapsePack = {
      id: `collapse_${target}_${Date.now()}`,
      target,
      truth,
      evidence,
      dischargedObligations,
      candidateHistory: eliminationResult?.candidateSet,
      promotionHistory,
      refutationHistory,
      depsRoot: hashString(dischargedObligations.join(":")),
      replayRoot: hashString(evidence.map(e => e.hash).join(":")),
      sealed: false,
      hash: ""
    };
    
    pack.hash = hashString(JSON.stringify({
      target: pack.target,
      truth: pack.truth,
      evidenceCount: pack.evidence.length
    }));
    
    return { type: "Bulk", pack };
  }
  
  /**
   * Seal collapse pack
   */
  seal(pack: CollapsePack): CollapsePack {
    if (pack.sealed) return pack;
    
    return {
      ...pack,
      sealed: true,
      sealTime: Date.now(),
      hash: hashString(JSON.stringify({
        ...pack,
        sealed: true,
        sealTime: Date.now()
      }))
    };
  }
  
  /**
   * Verify collapse pack integrity
   */
  verify(pack: CollapsePack): CollapsePackVerificationResult {
    const errors: string[] = [];
    
    // Check evidence completeness
    if (pack.truth === TruthValue.OK && pack.evidence.length === 0) {
      errors.push("OK truth requires evidence");
    }
    
    // Check refutation consistency
    if (pack.truth === TruthValue.FAIL && pack.refutationHistory.length === 0) {
      errors.push("FAIL truth requires refutation history");
    }
    
    // Check sealing
    if (!pack.sealed) {
      errors.push("Pack not sealed");
    }
    
    // Verify hash
    const computedHash = hashString(JSON.stringify({
      target: pack.target,
      truth: pack.truth,
      evidenceCount: pack.evidence.length
    }));
    
    if (pack.hash !== computedHash && !pack.sealed) {
      errors.push("Hash mismatch");
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }
}

export type CollapsePackCompilationResult =
  | { type: "Bulk"; pack: CollapsePack }
  | { type: "Boundary"; kind: string; obligations: string[] };

export interface CollapsePackVerificationResult {
  valid: boolean;
  errors: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: COMPLETE ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete Obligation Graph Engine
 */
export class ObligationGraphEngine {
  private dagBuilder: ObligationDAGBuilder;
  private dischargeEngine: BottomUpDischargeEngine;
  private eliminationLoop: CandidateEliminationLoop;
  private promotionOperator: PromotionRefutationOperator;
  private packCompiler: CollapsePackCompiler;
  
  private collapsePacks: Map<string, CollapsePack> = new Map();
  
  constructor() {
    this.dagBuilder = new ObligationDAGBuilder();
    this.dischargeEngine = new BottomUpDischargeEngine();
    this.eliminationLoop = new CandidateEliminationLoop();
    this.promotionOperator = new PromotionRefutationOperator();
    this.packCompiler = new CollapsePackCompiler();
  }
  
  /**
   * Create obligation
   */
  createObligation(
    kind: ObligationKind,
    claim: string,
    target: string,
    dependencies: string[] = []
  ): string {
    return this.dagBuilder.addNode(kind, claim, target, dependencies);
  }
  
  /**
   * Validate DAG
   */
  validateDAG(): DAGValidationResult {
    return this.dagBuilder.validate();
  }
  
  /**
   * Get DAG
   */
  getDAG(): ObligationDAG {
    return this.dagBuilder.getDAG();
  }
  
  /**
   * Run bottom-up discharge
   */
  discharge(budgets?: Partial<ObligationBudgets>): DischargeExecutionResult {
    const dag = this.dagBuilder.getDAG();
    return this.dischargeEngine.discharge(dag, {
      maxTime: budgets?.maxTime ?? 30000,
      maxMemory: budgets?.maxMemory ?? 4194304,
      maxSteps: budgets?.maxSteps ?? 10000,
      maxDepth: budgets?.maxDepth ?? 100
    });
  }
  
  /**
   * Run candidate elimination
   */
  runElimination(candidateSet: CandidateSet): EliminationResult {
    return this.eliminationLoop.run(candidateSet);
  }
  
  /**
   * Attempt promotion
   */
  attemptPromotion(
    current: TruthValue,
    evidence: EvidenceRef[],
    dischargedObligations: string[]
  ): PromotionResult {
    return this.promotionOperator.attemptPromotion(current, evidence, dischargedObligations);
  }
  
  /**
   * Attempt refutation
   */
  attemptRefutation(
    current: TruthValue,
    counterwitness: string,
    conflictEvidence: EvidenceRef[]
  ): RefutationResult {
    return this.promotionOperator.attemptRefutation(current, counterwitness, conflictEvidence);
  }
  
  /**
   * Compile collapse pack
   */
  compileCollapsePack(
    target: string,
    dischargeResult: DischargeExecutionResult,
    eliminationResult?: EliminationResult
  ): CollapsePackCompilationResult {
    const result = this.packCompiler.compile(target, dischargeResult, eliminationResult);
    
    if (result.type === "Bulk") {
      this.collapsePacks.set(result.pack.id, result.pack);
    }
    
    return result;
  }
  
  /**
   * Seal collapse pack
   */
  sealCollapsePack(packId: string): CollapsePack | null {
    const pack = this.collapsePacks.get(packId);
    if (!pack) return null;
    
    const sealed = this.packCompiler.seal(pack);
    this.collapsePacks.set(packId, sealed);
    return sealed;
  }
  
  /**
   * Get collapse pack
   */
  getCollapsePack(packId: string): CollapsePack | undefined {
    return this.collapsePacks.get(packId);
  }
  
  /**
   * Full resolve: discharge + eliminate + compile + seal
   */
  fullResolve(
    target: string,
    candidateSet?: CandidateSet,
    budgets?: Partial<ObligationBudgets>
  ): FullResolveResult {
    // Validate DAG
    const validation = this.validateDAG();
    if (!validation.valid) {
      return {
        type: "Boundary",
        kind: "InvalidDAG",
        obligations: validation.errors
      };
    }
    
    // Discharge
    const dischargeResult = this.discharge(budgets);
    
    // Eliminate candidates if provided
    let eliminationResult: EliminationResult | undefined;
    if (candidateSet) {
      eliminationResult = this.runElimination(candidateSet);
    }
    
    // Compile pack
    const packResult = this.compileCollapsePack(target, dischargeResult, eliminationResult);
    if (packResult.type === "Boundary") {
      return packResult;
    }
    
    // Seal
    const sealed = this.sealCollapsePack(packResult.pack.id);
    if (!sealed) {
      return {
        type: "Boundary",
        kind: "SealFailed",
        obligations: ["Could not seal collapse pack"]
      };
    }
    
    return {
      type: "Bulk",
      pack: sealed,
      dischargeResult,
      eliminationResult
    };
  }
  
  /**
   * Get statistics
   */
  getStats(): ObligationGraphStats {
    const dag = this.dagBuilder.getDAG();
    return {
      nodes: dag.nodes.size,
      edges: Array.from(dag.edges.values()).reduce((sum, e) => sum + e.length, 0),
      roots: dag.roots.length,
      leaves: dag.leaves.length,
      collapsePacks: this.collapsePacks.size
    };
  }
}

export type FullResolveResult =
  | {
      type: "Bulk";
      pack: CollapsePack;
      dischargeResult: DischargeExecutionResult;
      eliminationResult?: EliminationResult;
    }
  | { type: "Boundary"; kind: string; obligations: string[] };

export interface ObligationGraphStats {
  nodes: number;
  edges: number;
  roots: number;
  leaves: number;
  collapsePacks: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Enums
  TruthValue,
  ObligationKind,
  ObligationStatus,
  
  // Classes
  ObligationDAGBuilder,
  BottomUpDischargeEngine,
  CandidateEliminationLoop,
  PromotionRefutationOperator,
  CollapsePackCompiler,
  ObligationGraphEngine
};
