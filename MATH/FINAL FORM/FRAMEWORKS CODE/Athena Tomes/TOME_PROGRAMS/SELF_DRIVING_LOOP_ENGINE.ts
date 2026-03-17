/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * SELF-DRIVING LOOP ENGINE - DLK Scheduler & Self-Improvement
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * From SELF_SUFFICIENCY_TOME Ch20:
 * 
 * Core Laws:
 *   - Law 20.1 (Deterministic work selection): Identical frontier/deps/budgets/
 *     seeds yield same obligation selection byte-for-byte
 *   - Law 20.2 (Dependency centrality dominance): Priority monotone in centrality
 *     when risk is equal
 *   - Law 20.3 (Risk-constrained prioritization): No work item selected if it
 *     would violate κ/LOVE/Ω/φ constraints
 *   - Law 20.10 (Recursion stability): Self-upgrade loops must be stable under
 *     checkpointing
 * 
 * DLK = Deterministic Loop Kernel - the self-driving autonomy loop
 * 
 * @module SELF_DRIVING_LOOP_ENGINE
 * @version 2.0.0
 */

import { TruthValue, WitnessPtr } from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: NODE AND FRONTIER TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Node status
 */
export enum NodeStatus {
  Complete = "Complete",
  MissingCert = "MissingCert",
  Inconsistent = "Inconsistent",
  Unroutable = "Unroutable",
  UnderResolved = "UnderResolved",
  Ambiguous = "Ambiguous",
  DriftDetected = "DriftDetected"
}

/**
 * Node: Any addressable unit in the crystal
 */
export interface CrystalNode {
  address: string;
  type: NodeType;
  status: NodeStatus;
  metadata: NodeMetadata;
  contentHash: string;
}

export enum NodeType {
  Definition = "Definition",
  Law = "Law",
  Construction = "Construction",
  Certificate = "Certificate",
  Detector = "Detector",
  Bridge = "Bridge",
  PackModule = "PackModule",
  Artifact = "Artifact"
}

export interface NodeMetadata {
  dependencies: string[];    // Outgoing deps
  references: string[];      // Incoming refs
  impact: number;            // Downstream impact score
  risk: number;              // Risk score
  age: number;               // Time since creation
  corridor: string;          // Corridor context
  hash: string;
}

/**
 * Frontier set: Nodes requiring work
 */
export interface FrontierSet {
  nodes: Map<string, CrystalNode>;
  computed: number;
  hash: string;
}

/**
 * Obligation kind
 */
export enum ObligationKind {
  Refine = "Refine",
  Split = "Split",
  UpgradeLevel = "UpgradeLevel",
  ProvideProof = "ProvideProof",
  ProvideAdapter = "ProvideAdapter",
  Reroute = "Reroute",
  RepairCert = "RepairCert"
}

/**
 * Obligation
 */
export interface Obligation {
  id: string;
  kind: ObligationKind;
  target: string;            // Node address
  requirements: string[];
  budgets: ObligationBudget;
  schema: string;
  deadlinePolicy: DeadlinePolicy;
  priority: number;
  created: number;
}

export interface ObligationBudget {
  maxTime: number;
  maxMemory: number;
  maxSteps: number;
  riskBudget: number;
}

export interface DeadlinePolicy {
  softDeadline?: number;
  hardDeadline?: number;
  escalationPolicy: string;
}

/**
 * Obligation queue
 */
export interface ObligationQueue {
  obligations: Map<string, Obligation>;
  priorities: Map<string, number>;
  hash: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: PRIORITY COMPUTATION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Priority factors
 */
export interface PriorityFactors {
  safetyClass: number;           // 0-1, higher = more critical
  centralityGain: number;        // Dependency centrality
  ambiguityReduction: number;    // How much ambiguity resolved
  proofDebtReduction: number;    // How much proof debt discharged
  cost: number;                  // Resource cost
  age: number;                   // Time waiting
}

/**
 * Priority calculator (Construction 20.2)
 */
export class PriorityCalculator {
  private dependencyGraph: Map<string, Set<string>> = new Map();
  private reverseGraph: Map<string, Set<string>> = new Map();
  private centralityCache: Map<string, number> = new Map();
  
  /**
   * Add node to dependency graph
   */
  addNode(nodeId: string, dependencies: string[]): void {
    this.dependencyGraph.set(nodeId, new Set(dependencies));
    
    for (const dep of dependencies) {
      if (!this.reverseGraph.has(dep)) {
        this.reverseGraph.set(dep, new Set());
      }
      this.reverseGraph.get(dep)!.add(nodeId);
    }
    
    this.invalidateCentralityCache();
  }
  
  /**
   * Compute priority for obligation (Construction 20.2)
   * π(O) = Lex(SafetyClass, CentralityGain, AmbiguityReduction, 
   *            ProofDebtReduction, Cost, Age)
   */
  computePriority(obligation: Obligation, node: CrystalNode): number {
    const factors = this.computeFactors(obligation, node);
    
    // Lexicographic priority (higher values = higher priority)
    // Weight by position in lexicographic order
    return (
      factors.safetyClass * 1000000 +
      factors.centralityGain * 10000 +
      factors.ambiguityReduction * 100 +
      factors.proofDebtReduction * 10 +
      (1 - factors.cost) * 1 +
      factors.age * 0.001
    );
  }
  
  /**
   * Compute priority factors
   */
  computeFactors(obligation: Obligation, node: CrystalNode): PriorityFactors {
    return {
      safetyClass: this.computeSafetyClass(obligation, node),
      centralityGain: this.computeCentralityGain(node.address),
      ambiguityReduction: this.computeAmbiguityReduction(node),
      proofDebtReduction: this.computeProofDebtReduction(obligation),
      cost: this.estimateCost(obligation),
      age: this.normalizeAge(obligation.created)
    };
  }
  
  /**
   * Compute dependency centrality (Law 20.2)
   */
  computeCentrality(nodeId: string): number {
    if (this.centralityCache.has(nodeId)) {
      return this.centralityCache.get(nodeId)!;
    }
    
    // Compute betweenness-style centrality
    const inDegree = this.reverseGraph.get(nodeId)?.size ?? 0;
    const outDegree = this.dependencyGraph.get(nodeId)?.size ?? 0;
    
    // PageRank-inspired centrality (simplified)
    let centrality = (inDegree + outDegree) / 2;
    
    // Add contribution from dependents
    const dependents = this.reverseGraph.get(nodeId) ?? new Set();
    for (const dep of dependents) {
      centrality += 0.15 * (this.centralityCache.get(dep) ?? 1);
    }
    
    this.centralityCache.set(nodeId, centrality);
    return centrality;
  }
  
  private computeSafetyClass(obligation: Obligation, node: CrystalNode): number {
    // Higher value for safety-critical nodes
    if (node.type === NodeType.Certificate) return 0.9;
    if (obligation.kind === ObligationKind.RepairCert) return 0.85;
    if (node.metadata.risk > 0.5) return 0.8;
    return 0.5;
  }
  
  private computeCentralityGain(nodeId: string): number {
    const centrality = this.computeCentrality(nodeId);
    return Math.min(1, centrality / 10);  // Normalize to 0-1
  }
  
  private computeAmbiguityReduction(node: CrystalNode): number {
    if (node.status === NodeStatus.Ambiguous) return 0.8;
    if (node.status === NodeStatus.UnderResolved) return 0.6;
    return 0.3;
  }
  
  private computeProofDebtReduction(obligation: Obligation): number {
    if (obligation.kind === ObligationKind.ProvideProof) return 0.9;
    if (obligation.kind === ObligationKind.RepairCert) return 0.7;
    return 0.3;
  }
  
  private estimateCost(obligation: Obligation): number {
    const budget = obligation.budgets;
    return Math.min(1, (budget.maxTime + budget.maxSteps) / 100000);
  }
  
  private normalizeAge(created: number): number {
    const age = Date.now() - created;
    return Math.min(1, age / (24 * 60 * 60 * 1000));  // Normalize to days
  }
  
  private invalidateCentralityCache(): void {
    this.centralityCache.clear();
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: FRONTIER EXTRACTION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Frontier extractor (Construction 20.1)
 */
export class FrontierExtractor {
  private nodes: Map<string, CrystalNode> = new Map();
  
  /**
   * Register node
   */
  registerNode(node: CrystalNode): void {
    this.nodes.set(node.address, node);
  }
  
  /**
   * Extract frontier set
   */
  extractFrontier(): FrontierSet {
    const frontierNodes = new Map<string, CrystalNode>();
    
    for (const [address, node] of this.nodes) {
      if (this.nodeNeedsWork(node)) {
        frontierNodes.set(address, node);
      }
    }
    
    return {
      nodes: frontierNodes,
      computed: Date.now(),
      hash: this.computeFrontierHash(frontierNodes)
    };
  }
  
  /**
   * Check if node needs work
   */
  private nodeNeedsWork(node: CrystalNode): boolean {
    // Status check
    if (node.status !== NodeStatus.Complete) {
      return true;
    }
    
    return false;
  }
  
  /**
   * Scan for specific issues
   */
  scanForIssues(node: CrystalNode): IssueReport[] {
    const issues: IssueReport[] = [];
    
    // Check missing certificates
    if (this.hasMissingCerts(node)) {
      issues.push({
        type: "missing_cert",
        severity: "high",
        nodeAddress: node.address,
        description: "Missing required certificate"
      });
    }
    
    // Check cross-lens inconsistencies
    if (this.hasInconsistencies(node)) {
      issues.push({
        type: "inconsistency",
        severity: "high",
        nodeAddress: node.address,
        description: "Cross-lens inconsistency detected"
      });
    }
    
    // Check unroutable nodes
    if (this.isUnroutable(node)) {
      issues.push({
        type: "unroutable",
        severity: "medium",
        nodeAddress: node.address,
        description: "No legal route to required hubs"
      });
    }
    
    // Check ambiguity straddles
    if (this.hasAmbiguityStraddle(node)) {
      issues.push({
        type: "ambiguity",
        severity: "medium",
        nodeAddress: node.address,
        description: "Ambiguity straddle crossing threshold"
      });
    }
    
    // Check drift
    if (this.hasDrift(node)) {
      issues.push({
        type: "drift",
        severity: "high",
        nodeAddress: node.address,
        description: "Drift or replay mismatch detected"
      });
    }
    
    return issues;
  }
  
  /**
   * Generate obligations from issues
   */
  generateObligations(issues: IssueReport[]): Obligation[] {
    const obligations: Obligation[] = [];
    
    for (const issue of issues) {
      const obl = this.issueToObligation(issue);
      obligations.push(obl);
    }
    
    return obligations;
  }
  
  private hasMissingCerts(node: CrystalNode): boolean {
    return node.status === NodeStatus.MissingCert;
  }
  
  private hasInconsistencies(node: CrystalNode): boolean {
    return node.status === NodeStatus.Inconsistent;
  }
  
  private isUnroutable(node: CrystalNode): boolean {
    return node.status === NodeStatus.Unroutable;
  }
  
  private hasAmbiguityStraddle(node: CrystalNode): boolean {
    return node.status === NodeStatus.Ambiguous;
  }
  
  private hasDrift(node: CrystalNode): boolean {
    return node.status === NodeStatus.DriftDetected;
  }
  
  private issueToObligation(issue: IssueReport): Obligation {
    const kindMap: Record<string, ObligationKind> = {
      "missing_cert": ObligationKind.ProvideProof,
      "inconsistency": ObligationKind.Refine,
      "unroutable": ObligationKind.Reroute,
      "ambiguity": ObligationKind.Split,
      "drift": ObligationKind.RepairCert
    };
    
    return {
      id: `obl_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      kind: kindMap[issue.type] ?? ObligationKind.Refine,
      target: issue.nodeAddress,
      requirements: [issue.description],
      budgets: {
        maxTime: 10000,
        maxMemory: 100 * 1024 * 1024,
        maxSteps: 10000,
        riskBudget: 0.1
      },
      schema: "default",
      deadlinePolicy: {
        escalationPolicy: "warn"
      },
      priority: 0,
      created: Date.now()
    };
  }
  
  private computeFrontierHash(nodes: Map<string, CrystalNode>): string {
    const addresses = Array.from(nodes.keys()).sort();
    return hashString(addresses.join(":"));
  }
}

export interface IssueReport {
  type: string;
  severity: "low" | "medium" | "high" | "critical";
  nodeAddress: string;
  description: string;
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
// SECTION 4: WORK SELECTOR (DLK Scheduler)
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Work plan
 */
export interface WorkPlan {
  obligation: Obligation;
  targetNode: string;
  requiredDetectors: string[];
  requiredProofs: string[];
  allowedRoutes: string[];
  refinementSchedule: RefinementStep[];
  expectedCertificates: string[];
  hash: string;
}

export interface RefinementStep {
  step: number;
  action: string;
  admittedLevel?: number;
  prerequisites: string[];
}

/**
 * Selection certificate (Certificate 20.1)
 */
export interface SelectionCertificate {
  frontierHash: string;
  queueHash: string;
  budgets: ObligationBudget;
  constraints: string[];
  chosenObligation: string;
  priorityTrace: PriorityTraceEntry[];
  hash: string;
}

export interface PriorityTraceEntry {
  obligationId: string;
  priority: number;
  factors: PriorityFactors;
  legal: boolean;
}

/**
 * Constraint set
 */
export interface ConstraintSet {
  kappaScopes: string[];
  loveConstraints: string[];
  omegaClamps: string[];
  phiStability: string[];
}

/**
 * Work selector (Construction 20.3)
 */
export class WorkSelector {
  private priorityCalc: PriorityCalculator;
  private constraints: ConstraintSet;
  private executionLog: ExecutionLogEntry[] = [];
  
  constructor() {
    this.priorityCalc = new PriorityCalculator();
    this.constraints = {
      kappaScopes: [],
      loveConstraints: [],
      omegaClamps: [],
      phiStability: []
    };
  }
  
  /**
   * Set constraints
   */
  setConstraints(constraints: ConstraintSet): void {
    this.constraints = constraints;
  }
  
  /**
   * Add node to dependency graph
   */
  addNode(nodeId: string, dependencies: string[]): void {
    this.priorityCalc.addNode(nodeId, dependencies);
  }
  
  /**
   * Select next work item (Law 20.1: Deterministic)
   */
  selectNext(
    frontier: FrontierSet,
    queue: ObligationQueue
  ): SelectionResult {
    const trace: PriorityTraceEntry[] = [];
    let bestObligation: Obligation | null = null;
    let bestPriority = -Infinity;
    
    // Step 1: Filter by legality (Law 20.3)
    const legalObligations: Obligation[] = [];
    
    for (const [id, obligation] of queue.obligations) {
      const node = frontier.nodes.get(obligation.target);
      if (!node) continue;
      
      const legal = this.checkLegality(obligation, node);
      const priority = this.priorityCalc.computePriority(obligation, node);
      
      trace.push({
        obligationId: id,
        priority,
        factors: this.priorityCalc.computeFactors(obligation, node),
        legal
      });
      
      if (legal) {
        legalObligations.push(obligation);
        
        if (priority > bestPriority) {
          bestPriority = priority;
          bestObligation = obligation;
        } else if (priority === bestPriority && bestObligation) {
          // Deterministic tie-break: address order, then hash
          if (obligation.target < bestObligation.target ||
              (obligation.target === bestObligation.target && 
               obligation.id < bestObligation.id)) {
            bestObligation = obligation;
          }
        }
      }
    }
    
    if (!bestObligation) {
      return {
        type: "Boundary",
        kind: "NoLegalWork",
        constraints: this.getBlockingConstraints(trace),
        certificate: this.generateSelectionCertificate(frontier, queue, trace, null)
      };
    }
    
    // Generate work plan
    const node = frontier.nodes.get(bestObligation.target)!;
    const plan = this.generateWorkPlan(bestObligation, node);
    
    // Log selection
    this.executionLog.push({
      timestamp: Date.now(),
      obligationId: bestObligation.id,
      priority: bestPriority,
      action: "selected"
    });
    
    return {
      type: "Bulk",
      obligation: bestObligation,
      plan,
      certificate: this.generateSelectionCertificate(frontier, queue, trace, bestObligation.id)
    };
  }
  
  /**
   * Check legality against constraints (Law 20.3)
   */
  private checkLegality(obligation: Obligation, node: CrystalNode): boolean {
    // Check κ scope
    for (const scope of this.constraints.kappaScopes) {
      if (!this.checkKappaScope(obligation, scope)) {
        return false;
      }
    }
    
    // Check LOVE constraints
    for (const love of this.constraints.loveConstraints) {
      if (!this.checkLoveConstraint(obligation, love)) {
        return false;
      }
    }
    
    // Check Ω clamps
    for (const omega of this.constraints.omegaClamps) {
      if (!this.checkOmegaClamp(obligation, omega)) {
        return false;
      }
    }
    
    // Check φ stability
    for (const phi of this.constraints.phiStability) {
      if (!this.checkPhiStability(obligation, phi)) {
        return false;
      }
    }
    
    return true;
  }
  
  private checkKappaScope(obligation: Obligation, scope: string): boolean {
    // Simplified - would check actual capability scopes
    return true;
  }
  
  private checkLoveConstraint(obligation: Obligation, constraint: string): boolean {
    // Simplified - would check LOVE integrity
    return true;
  }
  
  private checkOmegaClamp(obligation: Obligation, clamp: string): boolean {
    // Simplified - would check verifier constraints
    return true;
  }
  
  private checkPhiStability(obligation: Obligation, stability: string): boolean {
    // Simplified - would check stability constraints
    return true;
  }
  
  /**
   * Generate work plan
   */
  private generateWorkPlan(obligation: Obligation, node: CrystalNode): WorkPlan {
    return {
      obligation,
      targetNode: obligation.target,
      requiredDetectors: this.determineDetectors(obligation),
      requiredProofs: this.determineProofs(obligation),
      allowedRoutes: this.determineRoutes(obligation),
      refinementSchedule: this.determineRefinementSchedule(obligation),
      expectedCertificates: this.determineExpectedCertificates(obligation),
      hash: hashString(JSON.stringify({ id: obligation.id, target: obligation.target }))
    };
  }
  
  private determineDetectors(obligation: Obligation): string[] {
    const detectorMap: Record<ObligationKind, string[]> = {
      [ObligationKind.Refine]: ["refinement_detector"],
      [ObligationKind.Split]: ["split_detector"],
      [ObligationKind.UpgradeLevel]: ["level_detector"],
      [ObligationKind.ProvideProof]: ["proof_checker"],
      [ObligationKind.ProvideAdapter]: ["adapter_detector"],
      [ObligationKind.Reroute]: ["route_detector"],
      [ObligationKind.RepairCert]: ["cert_validator"]
    };
    return detectorMap[obligation.kind] ?? [];
  }
  
  private determineProofs(obligation: Obligation): string[] {
    if (obligation.kind === ObligationKind.ProvideProof) {
      return ["required_proof"];
    }
    return [];
  }
  
  private determineRoutes(obligation: Obligation): string[] {
    if (obligation.kind === ObligationKind.Reroute) {
      return ["alternative_route_1", "alternative_route_2"];
    }
    return ["default_route"];
  }
  
  private determineRefinementSchedule(obligation: Obligation): RefinementStep[] {
    return [{
      step: 1,
      action: "gather_evidence",
      prerequisites: []
    }, {
      step: 2,
      action: "execute_obligation",
      prerequisites: ["evidence_gathered"]
    }, {
      step: 3,
      action: "verify_result",
      prerequisites: ["execution_complete"]
    }];
  }
  
  private determineExpectedCertificates(obligation: Obligation): string[] {
    return [`cert_${obligation.kind.toLowerCase()}`];
  }
  
  private getBlockingConstraints(trace: PriorityTraceEntry[]): string[] {
    return trace
      .filter(t => !t.legal)
      .map(t => `blocked_${t.obligationId}`);
  }
  
  private generateSelectionCertificate(
    frontier: FrontierSet,
    queue: ObligationQueue,
    trace: PriorityTraceEntry[],
    chosenId: string | null
  ): SelectionCertificate {
    return {
      frontierHash: frontier.hash,
      queueHash: queue.hash,
      budgets: { maxTime: 10000, maxMemory: 100 * 1024 * 1024, maxSteps: 10000, riskBudget: 0.1 },
      constraints: [
        ...this.constraints.kappaScopes,
        ...this.constraints.loveConstraints,
        ...this.constraints.omegaClamps,
        ...this.constraints.phiStability
      ],
      chosenObligation: chosenId ?? "none",
      priorityTrace: trace,
      hash: hashString(JSON.stringify({ frontier: frontier.hash, chosen: chosenId }))
    };
  }
  
  /**
   * Get execution log
   */
  getExecutionLog(): ExecutionLogEntry[] {
    return [...this.executionLog];
  }
}

export type SelectionResult =
  | { type: "Bulk"; obligation: Obligation; plan: WorkPlan; certificate: SelectionCertificate }
  | { type: "Boundary"; kind: string; constraints: string[]; certificate: SelectionCertificate };

export interface ExecutionLogEntry {
  timestamp: number;
  obligationId: string;
  priority: number;
  action: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: STUCKNESS ESCAPE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Stuckness token
 */
export interface StucknessToken {
  id: string;
  targetNode: string;
  reason: StucknessReason;
  iterations: number;
  repeatedBoundaryCode?: string;
  created: number;
}

export enum StucknessReason {
  NoProgress = "NoProgress",
  RepeatedFailure = "RepeatedFailure",
  EvidenceNotTightening = "EvidenceNotTightening",
  ReplayMismatchPersists = "ReplayMismatchPersists"
}

/**
 * Exploration rotation
 */
export interface ExplorationRotation {
  id: string;
  type: "lens" | "hub" | "archetype";
  from: string;
  to: string;
  legal: boolean;
  certificate?: string;
}

/**
 * Escape operator (Construction 20.6)
 */
export class EscapeOperator {
  private stucknessThreshold = 5;  // Iterations before stuckness
  private iterationHistory: Map<string, number[]> = new Map();
  
  /**
   * Detect stuckness (Construction 20.5)
   */
  detectStuckness(
    nodeId: string,
    currentSeverity: number,
    boundaryCode?: string
  ): StucknessToken | null {
    const history = this.iterationHistory.get(nodeId) ?? [];
    history.push(currentSeverity);
    this.iterationHistory.set(nodeId, history);
    
    // Check for no progress
    if (history.length >= this.stucknessThreshold) {
      const recent = history.slice(-this.stucknessThreshold);
      const improving = recent.every((v, i) => i === 0 || v < recent[i - 1]);
      
      if (!improving) {
        return {
          id: `stuck_${nodeId}_${Date.now()}`,
          targetNode: nodeId,
          reason: StucknessReason.NoProgress,
          iterations: history.length,
          repeatedBoundaryCode: boundaryCode,
          created: Date.now()
        };
      }
    }
    
    return null;
  }
  
  /**
   * Generate escape plan
   */
  generateEscapePlan(token: StucknessToken): EscapePlan {
    // Enumerate lawful rotations
    const rotations = this.enumerateRotations(token);
    
    // Generate alternative plans
    const plans = this.generateAlternativePlans(token, rotations);
    
    // Score plans
    const scoredPlans = plans.map(plan => ({
      plan,
      score: this.scorePlan(plan),
      legal: this.checkPlanLegality(plan)
    }));
    
    // Select best legal plan
    const legalPlans = scoredPlans.filter(p => p.legal);
    legalPlans.sort((a, b) => b.score - a.score);
    
    const bestPlan = legalPlans[0]?.plan;
    
    return {
      token,
      rotations,
      selectedPlan: bestPlan,
      alternativePlans: plans,
      certificate: this.generateEscapeCertificate(token, rotations, bestPlan)
    };
  }
  
  private enumerateRotations(token: StucknessToken): ExplorationRotation[] {
    const rotations: ExplorationRotation[] = [];
    
    // Lens rotations (Earth → Air → Water → Fire)
    const lenses = ["Earth", "Air", "Water", "Fire"];
    for (let i = 0; i < lenses.length; i++) {
      rotations.push({
        id: `lens_${lenses[i]}_${lenses[(i + 1) % 4]}`,
        type: "lens",
        from: lenses[i],
        to: lenses[(i + 1) % 4],
        legal: true  // Adjacent steps are legal
      });
    }
    
    // Hub rotations
    const hubs = ["Fourier", "Derivative", "Log", "Wick"];
    for (const hub of hubs) {
      rotations.push({
        id: `hub_to_${hub}`,
        type: "hub",
        from: "current",
        to: hub,
        legal: true
      });
    }
    
    // Archetype expansion/compression
    const levels = [4, 16, 64, 256];
    for (let i = 0; i < levels.length - 1; i++) {
      rotations.push({
        id: `archetype_${levels[i]}_${levels[i + 1]}`,
        type: "archetype",
        from: String(levels[i]),
        to: String(levels[i + 1]),
        legal: true
      });
    }
    
    return rotations;
  }
  
  private generateAlternativePlans(
    token: StucknessToken,
    rotations: ExplorationRotation[]
  ): AlternativePlan[] {
    return rotations.map(rotation => ({
      id: `plan_${rotation.id}`,
      rotation,
      strategy: this.rotationToStrategy(rotation),
      expectedReduction: 0.3  // Estimate
    }));
  }
  
  private rotationToStrategy(rotation: ExplorationRotation): string {
    switch (rotation.type) {
      case "lens":
        return `Switch to ${rotation.to} lens perspective`;
      case "hub":
        return `Route through ${rotation.to} hub`;
      case "archetype":
        return `Expand to level ${rotation.to}`;
      default:
        return "Default strategy";
    }
  }
  
  private scorePlan(plan: AlternativePlan): number {
    // Score based on expected obligation reduction
    return plan.expectedReduction * 100;
  }
  
  private checkPlanLegality(plan: AlternativePlan): boolean {
    return plan.rotation.legal;
  }
  
  private generateEscapeCertificate(
    token: StucknessToken,
    rotations: ExplorationRotation[],
    selectedPlan?: AlternativePlan
  ): EscapeCertificate {
    return {
      stuckToken: token.id,
      rotationSet: rotations.map(r => r.id),
      chosenRotation: selectedPlan?.rotation.id ?? "none",
      plan: selectedPlan?.strategy ?? "none",
      legalityProofs: rotations.filter(r => r.legal).map(r => r.id),
      timestamp: Date.now(),
      hash: hashString(JSON.stringify({ token: token.id, plan: selectedPlan?.id }))
    };
  }
  
  /**
   * Clear history for node
   */
  clearHistory(nodeId: string): void {
    this.iterationHistory.delete(nodeId);
  }
}

export interface EscapePlan {
  token: StucknessToken;
  rotations: ExplorationRotation[];
  selectedPlan?: AlternativePlan;
  alternativePlans: AlternativePlan[];
  certificate: EscapeCertificate;
}

export interface AlternativePlan {
  id: string;
  rotation: ExplorationRotation;
  strategy: string;
  expectedReduction: number;
}

export interface EscapeCertificate {
  stuckToken: string;
  rotationSet: string[];
  chosenRotation: string;
  plan: string;
  legalityProofs: string[];
  timestamp: number;
  hash: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: SELF-IMPROVEMENT SYSTEM
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Self-improving tool (Definition 20.10)
 */
export interface SelfImprovingTool {
  id: string;
  type: "detector" | "compiler" | "verifier" | "adapter";
  seed: string;
  upgradePolicy: UpgradePolicy;
  regressionGuards: string[];  // Negatify
  verifierContract: string;
  version: number;
  hash: string;
}

export interface UpgradePolicy {
  maxDeltaPerIteration: number;
  mandatoryTests: string[];
  mandatoryAudits: string[];
  rollbackOnFailure: boolean;
}

/**
 * Tool upgrade result
 */
export interface ToolUpgradeResult {
  success: boolean;
  tool: SelfImprovingTool;
  delta: ToolDelta;
  tests: TestResult[];
  audits: AuditResult[];
  certificate: UpgradeCertificate;
}

export interface ToolDelta {
  changes: string[];
  addedRules: string[];
  modifiedRules: string[];
  removedRules: string[];
}

export interface TestResult {
  name: string;
  passed: boolean;
  details?: string;
}

export interface AuditResult {
  name: string;
  passed: boolean;
  findings: string[];
}

export interface UpgradeCertificate {
  toolId: string;
  previousVersion: number;
  newVersion: number;
  delta: ToolDelta;
  testsPassed: number;
  totalTests: number;
  auditsPassed: number;
  totalAudits: number;
  timestamp: number;
  hash: string;
}

/**
 * Meta-compiler upgrader (Construction 20.9)
 */
export class MetaCompilerUpgrader {
  private tools: Map<string, SelfImprovingTool> = new Map();
  private stableRoots: Map<string, string> = new Map();  // Tool -> last stable Merkle root
  
  /**
   * Register tool
   */
  registerTool(tool: SelfImprovingTool): void {
    this.tools.set(tool.id, tool);
    this.stableRoots.set(tool.id, tool.hash);
  }
  
  /**
   * Propose upgrade (Construction 20.9)
   */
  proposeUpgrade(
    toolId: string,
    delta: ToolDelta
  ): ToolUpgradeResult | { error: string } {
    const tool = this.tools.get(toolId);
    if (!tool) {
      return { error: "Tool not found" };
    }
    
    // Check delta size (Law 20.11)
    if (this.deltaSize(delta) > tool.upgradePolicy.maxDeltaPerIteration) {
      return { error: "Delta too large for single iteration" };
    }
    
    // Run conformance tests
    const testResults = this.runConformanceTests(tool, delta);
    const allTestsPassed = testResults.every(t => t.passed);
    
    // Run safety audits
    const auditResults = this.runSafetyAudits(tool, delta);
    const allAuditsPassed = auditResults.every(a => a.passed);
    
    if (!allTestsPassed || !allAuditsPassed) {
      if (tool.upgradePolicy.rollbackOnFailure) {
        // Rollback to stable root
        return { error: "Tests/audits failed, rollback required" };
      }
    }
    
    // Create upgraded tool
    const upgradedTool: SelfImprovingTool = {
      ...tool,
      version: tool.version + 1,
      hash: hashString(JSON.stringify({ ...tool, delta }))
    };
    
    // Update registry
    this.tools.set(toolId, upgradedTool);
    if (allTestsPassed && allAuditsPassed) {
      this.stableRoots.set(toolId, upgradedTool.hash);
    }
    
    return {
      success: allTestsPassed && allAuditsPassed,
      tool: upgradedTool,
      delta,
      tests: testResults,
      audits: auditResults,
      certificate: this.generateUpgradeCertificate(tool, upgradedTool, delta, testResults, auditResults)
    };
  }
  
  /**
   * Rollback to stable version
   */
  rollback(toolId: string): SelfImprovingTool | null {
    const stableRoot = this.stableRoots.get(toolId);
    const tool = this.tools.get(toolId);
    
    if (!tool || !stableRoot) return null;
    
    // In practice would reconstruct from Merkle store
    return tool;
  }
  
  private deltaSize(delta: ToolDelta): number {
    return delta.addedRules.length + 
           delta.modifiedRules.length + 
           delta.removedRules.length;
  }
  
  private runConformanceTests(tool: SelfImprovingTool, delta: ToolDelta): TestResult[] {
    return tool.upgradePolicy.mandatoryTests.map(test => ({
      name: test,
      passed: true,  // Simplified
      details: "Test passed"
    }));
  }
  
  private runSafetyAudits(tool: SelfImprovingTool, delta: ToolDelta): AuditResult[] {
    return tool.upgradePolicy.mandatoryAudits.map(audit => ({
      name: audit,
      passed: true,  // Simplified
      findings: []
    }));
  }
  
  private generateUpgradeCertificate(
    oldTool: SelfImprovingTool,
    newTool: SelfImprovingTool,
    delta: ToolDelta,
    tests: TestResult[],
    audits: AuditResult[]
  ): UpgradeCertificate {
    return {
      toolId: oldTool.id,
      previousVersion: oldTool.version,
      newVersion: newTool.version,
      delta,
      testsPassed: tests.filter(t => t.passed).length,
      totalTests: tests.length,
      auditsPassed: audits.filter(a => a.passed).length,
      totalAudits: audits.length,
      timestamp: Date.now(),
      hash: hashString(JSON.stringify({ old: oldTool.hash, new: newTool.hash }))
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: DLK EXECUTION ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * DLK iteration result
 */
export interface DLKIterationResult {
  iteration: number;
  selectedWork?: WorkPlan;
  executionResult?: ExecutionResult;
  newObligations: Obligation[];
  frontierDelta: FrontierDelta;
  certificates: string[];
  duration: number;
}

export interface ExecutionResult {
  success: boolean;
  artifacts: string[];
  boundaryOutput?: { kind: string; obligations: string[] };
}

export interface FrontierDelta {
  added: string[];
  removed: string[];
  updated: string[];
}

/**
 * Complete DLK Execution Engine (Construction 20.4)
 */
export class DLKExecutionEngine {
  private frontierExtractor: FrontierExtractor;
  private workSelector: WorkSelector;
  private escapeOperator: EscapeOperator;
  private metaUpgrader: MetaCompilerUpgrader;
  
  private frontier: FrontierSet;
  private queue: ObligationQueue;
  private iteration: number = 0;
  private history: DLKIterationResult[] = [];
  
  constructor() {
    this.frontierExtractor = new FrontierExtractor();
    this.workSelector = new WorkSelector();
    this.escapeOperator = new EscapeOperator();
    this.metaUpgrader = new MetaCompilerUpgrader();
    
    this.frontier = { nodes: new Map(), computed: Date.now(), hash: "" };
    this.queue = { obligations: new Map(), priorities: new Map(), hash: "" };
  }
  
  /**
   * Register node
   */
  registerNode(node: CrystalNode): void {
    this.frontierExtractor.registerNode(node);
    this.workSelector.addNode(node.address, node.metadata.dependencies);
  }
  
  /**
   * Set constraints
   */
  setConstraints(constraints: ConstraintSet): void {
    this.workSelector.setConstraints(constraints);
  }
  
  /**
   * Run single DLK iteration (Construction 20.4)
   */
  runIteration(): DLKIterationResult {
    const startTime = Date.now();
    this.iteration++;
    
    // Step 1: Extract frontier
    this.frontier = this.frontierExtractor.extractFrontier();
    
    // Step 2: Generate obligations from issues
    for (const node of this.frontier.nodes.values()) {
      const issues = this.frontierExtractor.scanForIssues(node);
      const newObligations = this.frontierExtractor.generateObligations(issues);
      
      for (const obl of newObligations) {
        if (!this.queue.obligations.has(obl.id)) {
          this.queue.obligations.set(obl.id, obl);
        }
      }
    }
    
    this.queue.hash = hashString(Array.from(this.queue.obligations.keys()).join(":"));
    
    // Step 3: Select work
    const selection = this.workSelector.selectNext(this.frontier, this.queue);
    
    let executionResult: ExecutionResult | undefined;
    let newObligations: Obligation[] = [];
    const frontierDelta: FrontierDelta = { added: [], removed: [], updated: [] };
    const certificates: string[] = [selection.certificate.hash];
    
    if (selection.type === "Bulk") {
      // Step 4: Execute work plan
      executionResult = this.executePlan(selection.plan);
      
      // Step 5: Run Negatify probe
      // (Would integrate with Negatify engine)
      
      // Step 6: Update frontier
      if (executionResult.success) {
        // Mark obligation as discharged
        this.queue.obligations.delete(selection.obligation.id);
        frontierDelta.removed.push(selection.obligation.target);
        
        // Check for stuckness escape
        this.escapeOperator.clearHistory(selection.obligation.target);
      } else {
        // Check for stuckness
        const stuckToken = this.escapeOperator.detectStuckness(
          selection.obligation.target,
          1,  // Current severity
          executionResult.boundaryOutput?.kind
        );
        
        if (stuckToken) {
          const escapePlan = this.escapeOperator.generateEscapePlan(stuckToken);
          certificates.push(escapePlan.certificate.hash);
          
          // Generate escape obligations
          if (escapePlan.selectedPlan) {
            newObligations.push({
              id: `escape_${stuckToken.id}`,
              kind: ObligationKind.Refine,
              target: stuckToken.targetNode,
              requirements: [escapePlan.selectedPlan.strategy],
              budgets: { maxTime: 10000, maxMemory: 100 * 1024 * 1024, maxSteps: 10000, riskBudget: 0.1 },
              schema: "escape",
              deadlinePolicy: { escalationPolicy: "warn" },
              priority: 100,
              created: Date.now()
            });
          }
        }
      }
    }
    
    const result: DLKIterationResult = {
      iteration: this.iteration,
      selectedWork: selection.type === "Bulk" ? selection.plan : undefined,
      executionResult,
      newObligations,
      frontierDelta,
      certificates,
      duration: Date.now() - startTime
    };
    
    this.history.push(result);
    return result;
  }
  
  /**
   * Execute work plan
   */
  private executePlan(plan: WorkPlan): ExecutionResult {
    // Simplified execution - would integrate with actual systems
    const success = Math.random() > 0.3;  // 70% success rate for demo
    
    if (success) {
      return {
        success: true,
        artifacts: [`artifact_${plan.obligation.id}`]
      };
    } else {
      return {
        success: false,
        artifacts: [],
        boundaryOutput: {
          kind: "ExecutionFailed",
          obligations: ["Retry with different strategy"]
        }
      };
    }
  }
  
  /**
   * Run multiple iterations
   */
  runIterations(count: number): DLKIterationResult[] {
    const results: DLKIterationResult[] = [];
    
    for (let i = 0; i < count; i++) {
      const result = this.runIteration();
      results.push(result);
      
      // Stop if frontier is empty
      if (this.frontier.nodes.size === 0) break;
    }
    
    return results;
  }
  
  /**
   * Register self-improving tool
   */
  registerTool(tool: SelfImprovingTool): void {
    this.metaUpgrader.registerTool(tool);
  }
  
  /**
   * Propose tool upgrade
   */
  proposeToolUpgrade(
    toolId: string,
    delta: ToolDelta
  ): ToolUpgradeResult | { error: string } {
    return this.metaUpgrader.proposeUpgrade(toolId, delta);
  }
  
  /**
   * Get frontier
   */
  getFrontier(): FrontierSet {
    return this.frontier;
  }
  
  /**
   * Get queue
   */
  getQueue(): ObligationQueue {
    return this.queue;
  }
  
  /**
   * Get history
   */
  getHistory(): DLKIterationResult[] {
    return [...this.history];
  }
  
  /**
   * Get statistics
   */
  getStats(): DLKStats {
    return {
      iterations: this.iteration,
      frontierSize: this.frontier.nodes.size,
      queueSize: this.queue.obligations.size,
      successfulIterations: this.history.filter(h => h.executionResult?.success).length,
      totalDuration: this.history.reduce((sum, h) => sum + h.duration, 0)
    };
  }
}

export interface DLKStats {
  iterations: number;
  frontierSize: number;
  queueSize: number;
  successfulIterations: number;
  totalDuration: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Enums
  NodeStatus,
  NodeType,
  ObligationKind,
  StucknessReason,
  
  // Classes
  PriorityCalculator,
  FrontierExtractor,
  WorkSelector,
  EscapeOperator,
  MetaCompilerUpgrader,
  DLKExecutionEngine
};
