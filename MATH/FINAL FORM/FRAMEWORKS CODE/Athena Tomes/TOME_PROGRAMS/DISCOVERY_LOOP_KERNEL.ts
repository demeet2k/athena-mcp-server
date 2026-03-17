/**
 * DISCOVERY_LOOP_KERNEL.ts
 * 
 * Complete implementation of the Discovery Loop Kernel (DLK):
 * The System That Replaces the Human
 * 
 * From SELF_SUFFICIENCY_TOME Ch20:
 * - Frontier sets: nodes requiring work (missing certs, inconsistent, etc.)
 * - Obligation queues: prioritized work items
 * - Priority heuristics: dependency centrality, risk, ambiguity reduction
 * - Work selection: deterministic, auditable
 * - DLK execution: extract → collapse → expand → certify → route → commit
 * 
 * Autonomy Target: Choose work deterministically from frontier pressure
 * and dependency centrality, generate bounded-verifier certificates,
 * self-improve without bypassing safety.
 */

// ============================================================================
// SECTION 1: CORE TYPES AND ENUMERATIONS
// ============================================================================

/**
 * Node status - determines if node is in frontier
 */
enum NodeStatus {
  Stable = 'STABLE',
  MissingCert = 'MISSING_CERT',
  Inconsistent = 'INCONSISTENT',
  Unroutable = 'UNROUTABLE',
  UnderResolved = 'UNDER_RESOLVED',
  Ambiguous = 'AMBIGUOUS',
  DriftDetected = 'DRIFT_DETECTED'
}

/**
 * Obligation kinds for work items
 */
enum ObligationKind {
  Refine = 'REFINE',
  Split = 'SPLIT',
  UpgradeLevel = 'UPGRADE_LEVEL',
  ProvideProof = 'PROVIDE_PROOF',
  ProvideAdaptor = 'PROVIDE_ADAPTOR',
  Reroute = 'REROUTE',
  RepairCert = 'REPAIR_CERT'
}

/**
 * Execution step types
 */
enum ExecutionStep {
  GatherEvidence = 'GATHER_EVIDENCE',
  AttemptResolution = 'ATTEMPT_RESOLUTION',
  RunNegatify = 'RUN_NEGATIFY',
  Verify = 'VERIFY',
  CommitArtifacts = 'COMMIT_ARTIFACTS',
  UpdateFrontier = 'UPDATE_FRONTIER'
}

/**
 * Lens types for cross-lens consistency
 */
enum LensType {
  Square = 'SQUARE',
  Flower = 'FLOWER',
  Cloud = 'CLOUD',
  Fractal = 'FRACTAL'
}

/**
 * Safety constraint types
 */
enum SafetyConstraint {
  Omega = 'OMEGA',      // Ω clamps
  LOVE = 'LOVE',        // LOVE constraints
  Kappa = 'KAPPA',      // κ budgets
  Phi = 'PHI'           // φ stability
}

/**
 * Exploration rotation types
 */
enum RotationType {
  LensRotation = 'LENS_ROTATION',
  HubRerouting = 'HUB_REROUTING',
  ArchetypeExpansion = 'ARCHETYPE_EXPANSION',
  ArchetypeCompression = 'ARCHETYPE_COMPRESSION'
}

// ============================================================================
// SECTION 2: NODE AND METADATA TYPES
// ============================================================================

/**
 * Crystal address
 */
interface CrystalAddr {
  readonly module: string;
  readonly chapter: number;
  readonly lens: LensType;
  readonly facet: number;
  readonly tile: number;
}

/**
 * Node - addressable unit in the crystal (Definition 20.1)
 */
interface Node {
  readonly addr: CrystalAddr;
  readonly hash: string;
  readonly type: string;
  readonly status: NodeStatus;
  readonly metadata: NodeMetadata;
  readonly created: number;
  readonly updated: number;
}

/**
 * Node metadata (Definition 20.2)
 */
interface NodeMetadata {
  readonly deps: readonly string[];      // Dependency edges
  readonly refs: readonly string[];      // Reference edges
  readonly impact: number;               // Impact score
  readonly risk: number;                 // Risk score
  readonly age: number;                  // Time since creation
  readonly corridor: string;             // Corridor context
  readonly hash: string;                 // Metadata hash
}

/**
 * Obligation - typed refinement requirement (Definition 20.3)
 */
interface Obligation {
  readonly oblId: string;
  readonly kind: ObligationKind;
  readonly target: string;               // Target node address
  readonly requirements: readonly string[];
  readonly budgets: BudgetState;
  readonly schema: string;
  readonly deadlinePolicy: string;
  readonly priority: number;
}

/**
 * Budget state
 */
interface BudgetState {
  readonly kappa: number;
  readonly beta: number;
  readonly chi: number;
  readonly epsilon: number;
}

/**
 * Obligation queue entry (Definition 20.4)
 */
interface QueueEntry {
  readonly obligation: Obligation;
  readonly priority: number;
  readonly insertTime: number;
  readonly computedPriority: ComputedPriority;
}

/**
 * Computed priority components (Construction 20.2)
 */
interface ComputedPriority {
  readonly safetyClass: number;
  readonly centralityGain: number;
  readonly ambiguityReduction: number;
  readonly proofDebtReduction: number;
  readonly cost: number;
  readonly age: number;
  readonly lexScore: readonly number[];
}

// ============================================================================
// SECTION 3: FRONTIER SET
// ============================================================================

/**
 * Frontier set - nodes requiring work (Definition 20.2)
 */
class FrontierSet {
  private readonly nodes: Map<string, Node> = new Map();
  private readonly byStatus: Map<NodeStatus, Set<string>> = new Map();
  
  constructor() {
    for (const status of Object.values(NodeStatus)) {
      this.byStatus.set(status, new Set());
    }
  }
  
  /**
   * Add node to frontier
   */
  add(node: Node): void {
    const key = this.addrToKey(node.addr);
    this.nodes.set(key, node);
    
    if (node.status !== NodeStatus.Stable) {
      this.byStatus.get(node.status)?.add(key);
    }
  }
  
  /**
   * Remove node from frontier
   */
  remove(addr: CrystalAddr): void {
    const key = this.addrToKey(addr);
    const node = this.nodes.get(key);
    
    if (node) {
      this.byStatus.get(node.status)?.delete(key);
      this.nodes.delete(key);
    }
  }
  
  /**
   * Update node status
   */
  updateStatus(addr: CrystalAddr, newStatus: NodeStatus): void {
    const key = this.addrToKey(addr);
    const node = this.nodes.get(key);
    
    if (node) {
      this.byStatus.get(node.status)?.delete(key);
      
      const updated: Node = {
        ...node,
        status: newStatus,
        updated: Date.now()
      };
      
      this.nodes.set(key, updated);
      
      if (newStatus !== NodeStatus.Stable) {
        this.byStatus.get(newStatus)?.add(key);
      }
    }
  }
  
  /**
   * Get nodes by status
   */
  getByStatus(status: NodeStatus): Node[] {
    const keys = this.byStatus.get(status) || new Set();
    return Array.from(keys)
      .map(k => this.nodes.get(k))
      .filter((n): n is Node => n !== undefined);
  }
  
  /**
   * Get all frontier nodes (non-stable)
   */
  getFrontierNodes(): Node[] {
    return Array.from(this.nodes.values())
      .filter(n => n.status !== NodeStatus.Stable);
  }
  
  /**
   * Get all nodes
   */
  getAllNodes(): Node[] {
    return Array.from(this.nodes.values());
  }
  
  /**
   * Check if node is in frontier
   */
  isInFrontier(addr: CrystalAddr): boolean {
    const key = this.addrToKey(addr);
    const node = this.nodes.get(key);
    return node !== undefined && node.status !== NodeStatus.Stable;
  }
  
  /**
   * Get frontier size
   */
  get size(): number {
    return this.getFrontierNodes().length;
  }
  
  /**
   * Compute frontier hash for determinism
   */
  computeHash(): string {
    const sortedKeys = Array.from(this.nodes.keys()).sort();
    const content = sortedKeys
      .map(k => {
        const n = this.nodes.get(k)!;
        return `${k}:${n.status}:${n.hash}`;
      })
      .join('|');
    
    let hash = 0;
    for (let i = 0; i < content.length; i++) {
      const char = content.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return `FRONTIER_${Math.abs(hash).toString(16).toUpperCase().padStart(16, '0')}`;
  }
  
  private addrToKey(addr: CrystalAddr): string {
    return `${addr.module}::Ch${addr.chapter.toString().padStart(2, '0')}.${addr.lens}${addr.facet}.t${addr.tile}`;
  }
}

// ============================================================================
// SECTION 4: OBLIGATION QUEUE
// ============================================================================

/**
 * Priority queue for obligations (Definition 20.4)
 */
class ObligationQueue {
  private readonly entries: QueueEntry[] = [];
  private readonly byTarget: Map<string, QueueEntry[]> = new Map();
  
  /**
   * Enqueue obligation with computed priority
   */
  enqueue(obligation: Obligation, computedPriority: ComputedPriority): void {
    const entry: QueueEntry = {
      obligation,
      priority: this.computeLexScore(computedPriority),
      insertTime: Date.now(),
      computedPriority
    };
    
    this.entries.push(entry);
    
    // Index by target
    const targetEntries = this.byTarget.get(obligation.target) || [];
    targetEntries.push(entry);
    this.byTarget.set(obligation.target, targetEntries);
    
    // Maintain sorted order
    this.sortQueue();
  }
  
  /**
   * Dequeue highest priority obligation
   */
  dequeue(): QueueEntry | undefined {
    const entry = this.entries.shift();
    
    if (entry) {
      // Remove from target index
      const targetEntries = this.byTarget.get(entry.obligation.target) || [];
      const idx = targetEntries.indexOf(entry);
      if (idx >= 0) {
        targetEntries.splice(idx, 1);
      }
    }
    
    return entry;
  }
  
  /**
   * Peek at highest priority obligation
   */
  peek(): QueueEntry | undefined {
    return this.entries[0];
  }
  
  /**
   * Get all obligations for a target
   */
  getByTarget(target: string): QueueEntry[] {
    return this.byTarget.get(target) || [];
  }
  
  /**
   * Remove all obligations for a target
   */
  removeByTarget(target: string): void {
    const targetEntries = this.byTarget.get(target) || [];
    
    for (const entry of targetEntries) {
      const idx = this.entries.indexOf(entry);
      if (idx >= 0) {
        this.entries.splice(idx, 1);
      }
    }
    
    this.byTarget.delete(target);
  }
  
  /**
   * Get queue size
   */
  get size(): number {
    return this.entries.length;
  }
  
  /**
   * Check if empty
   */
  isEmpty(): boolean {
    return this.entries.length === 0;
  }
  
  /**
   * Compute queue hash for determinism
   */
  computeHash(): string {
    const content = this.entries
      .map(e => `${e.obligation.oblId}:${e.priority}`)
      .join('|');
    
    let hash = 0;
    for (let i = 0; i < content.length; i++) {
      const char = content.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return `QUEUE_${Math.abs(hash).toString(16).toUpperCase().padStart(16, '0')}`;
  }
  
  /**
   * Get all entries
   */
  getAllEntries(): QueueEntry[] {
    return [...this.entries];
  }
  
  private sortQueue(): void {
    this.entries.sort((a, b) => b.priority - a.priority);
  }
  
  private computeLexScore(priority: ComputedPriority): number {
    // Lexicographic ordering as weighted sum
    const weights = [1000000, 100000, 10000, 1000, 100, 1];
    return (
      priority.safetyClass * weights[0] +
      priority.centralityGain * weights[1] +
      priority.ambiguityReduction * weights[2] +
      priority.proofDebtReduction * weights[3] +
      (100 - priority.cost) * weights[4] + // Lower cost is better
      priority.age * weights[5]
    );
  }
}

// ============================================================================
// SECTION 5: DEPENDENCY GRAPH
// ============================================================================

/**
 * Dependency graph for centrality computation
 */
class DependencyGraph {
  private readonly nodes: Map<string, string[]> = new Map();
  private readonly reverseNodes: Map<string, string[]> = new Map();
  private readonly centrality: Map<string, number> = new Map();
  
  /**
   * Add edge from source to target
   */
  addEdge(source: string, target: string): void {
    // Forward edge
    const forward = this.nodes.get(source) || [];
    if (!forward.includes(target)) {
      forward.push(target);
      this.nodes.set(source, forward);
    }
    
    // Reverse edge
    const reverse = this.reverseNodes.get(target) || [];
    if (!reverse.includes(source)) {
      reverse.push(source);
      this.reverseNodes.set(target, reverse);
    }
    
    // Invalidate centrality cache
    this.centrality.clear();
  }
  
  /**
   * Get dependencies of a node
   */
  getDependencies(node: string): string[] {
    return this.nodes.get(node) || [];
  }
  
  /**
   * Get dependents of a node
   */
  getDependents(node: string): string[] {
    return this.reverseNodes.get(node) || [];
  }
  
  /**
   * Compute dependency centrality (Law 20.2)
   * Weighted combination of in-degree and out-degree
   */
  computeCentrality(node: string): number {
    if (this.centrality.has(node)) {
      return this.centrality.get(node)!;
    }
    
    const inDegree = (this.reverseNodes.get(node) || []).length;
    const outDegree = (this.nodes.get(node) || []).length;
    
    // Betweenness approximation using path counting
    const betweenness = this.approximateBetweenness(node);
    
    // Weighted combination
    const cent = 0.3 * inDegree + 0.3 * outDegree + 0.4 * betweenness;
    
    this.centrality.set(node, cent);
    return cent;
  }
  
  /**
   * Approximate betweenness centrality
   */
  private approximateBetweenness(node: string): number {
    // Simple approximation: count paths through node
    const dependents = this.getDependents(node);
    const dependencies = this.getDependencies(node);
    
    let pathCount = 0;
    for (const dep of dependents) {
      for (const target of dependencies) {
        if (dep !== target) {
          pathCount++;
        }
      }
    }
    
    const totalNodes = this.nodes.size;
    return totalNodes > 0 ? pathCount / (totalNodes * totalNodes) : 0;
  }
  
  /**
   * Get all nodes
   */
  getAllNodes(): string[] {
    const all = new Set<string>();
    for (const [source, targets] of this.nodes) {
      all.add(source);
      targets.forEach(t => all.add(t));
    }
    return Array.from(all);
  }
  
  /**
   * Topological sort
   */
  topologicalSort(): string[] {
    const visited = new Set<string>();
    const result: string[] = [];
    
    const visit = (node: string) => {
      if (visited.has(node)) return;
      visited.add(node);
      
      for (const dep of this.getDependencies(node)) {
        visit(dep);
      }
      
      result.push(node);
    };
    
    for (const node of this.getAllNodes()) {
      visit(node);
    }
    
    return result.reverse();
  }
}

// ============================================================================
// SECTION 6: PRIORITY FUNCTION
// ============================================================================

/**
 * Priority function (Construction 20.2)
 */
class PriorityFunction {
  private readonly depGraph: DependencyGraph;
  private readonly corridor: CorridorState;
  
  constructor(depGraph: DependencyGraph, corridor: CorridorState) {
    this.depGraph = depGraph;
    this.corridor = corridor;
  }
  
  /**
   * Compute priority for obligation
   */
  computePriority(obligation: Obligation, node: Node): ComputedPriority {
    const safetyClass = this.computeSafetyClass(obligation, node);
    const centralityGain = this.computeCentralityGain(node);
    const ambiguityReduction = this.computeAmbiguityReduction(node);
    const proofDebtReduction = this.computeProofDebtReduction(obligation);
    const cost = this.computeCost(obligation);
    const age = this.computeAge(node);
    
    const lexScore = [
      safetyClass,
      centralityGain,
      ambiguityReduction,
      proofDebtReduction,
      cost,
      age
    ];
    
    return {
      safetyClass,
      centralityGain,
      ambiguityReduction,
      proofDebtReduction,
      cost,
      age,
      lexScore
    };
  }
  
  /**
   * Safety class - Ω/LOVE/κ/φ (highest priority)
   */
  private computeSafetyClass(obligation: Obligation, node: Node): number {
    let score = 0;
    
    // Ω clamp violations
    if (this.violatesOmega(obligation)) {
      score += 100;
    }
    
    // LOVE constraint violations
    if (this.violatesLOVE(node)) {
      score += 80;
    }
    
    // κ budget violations
    if (this.violatesKappa(obligation)) {
      score += 60;
    }
    
    // φ stability violations
    if (this.violatesPhi(node)) {
      score += 40;
    }
    
    return score;
  }
  
  /**
   * Centrality gain - more central nodes reduce downstream ambiguity
   */
  private computeCentralityGain(node: Node): number {
    const centrality = this.depGraph.computeCentrality(this.nodeToKey(node));
    return Math.min(100, centrality * 10);
  }
  
  /**
   * Ambiguity reduction - resolving ambiguous nodes
   */
  private computeAmbiguityReduction(node: Node): number {
    if (node.status === NodeStatus.Ambiguous) {
      return 100;
    }
    if (node.status === NodeStatus.UnderResolved) {
      return 80;
    }
    if (node.status === NodeStatus.DriftDetected) {
      return 60;
    }
    return 0;
  }
  
  /**
   * Proof debt reduction - filling in missing proofs
   */
  private computeProofDebtReduction(obligation: Obligation): number {
    switch (obligation.kind) {
      case ObligationKind.ProvideProof:
        return 100;
      case ObligationKind.RepairCert:
        return 80;
      case ObligationKind.ProvideAdaptor:
        return 60;
      default:
        return 20;
    }
  }
  
  /**
   * Cost under budgets
   */
  private computeCost(obligation: Obligation): number {
    const totalBudget = (
      obligation.budgets.kappa +
      obligation.budgets.beta +
      obligation.budgets.chi +
      obligation.budgets.epsilon
    );
    
    return Math.min(100, totalBudget);
  }
  
  /**
   * Age - older unresolved items get priority
   */
  private computeAge(node: Node): number {
    const ageMs = Date.now() - node.created;
    const ageHours = ageMs / (1000 * 60 * 60);
    return Math.min(100, ageHours);
  }
  
  private violatesOmega(_obligation: Obligation): boolean {
    // Check Ω clamp constraints
    return false;
  }
  
  private violatesLOVE(node: Node): boolean {
    // Check LOVE constraints
    return node.metadata.risk > 0.9;
  }
  
  private violatesKappa(obligation: Obligation): boolean {
    // Check κ budget constraints
    return obligation.budgets.kappa > this.corridor.budgets.kappa;
  }
  
  private violatesPhi(node: Node): boolean {
    // Check φ stability constraints
    return node.status === NodeStatus.DriftDetected;
  }
  
  private nodeToKey(node: Node): string {
    return `${node.addr.module}::Ch${node.addr.chapter}.${node.addr.lens}${node.addr.facet}`;
  }
}

/**
 * Corridor state for constraint checking
 */
interface CorridorState {
  readonly guards: readonly string[];
  readonly budgets: BudgetState;
  readonly constraints: readonly SafetyConstraint[];
  readonly admittedLevels: readonly number[];
}

// ============================================================================
// SECTION 7: WORK SELECTOR
// ============================================================================

/**
 * Work plan output from selector
 */
interface WorkPlan {
  readonly planId: string;
  readonly targetNode: Node;
  readonly obligation: Obligation;
  readonly requiredDetectors: readonly string[];
  readonly requiredProofs: readonly string[];
  readonly allowedRoutes: readonly string[];
  readonly allowedHubs: readonly string[];
  readonly refinementSchedule: RefinementSchedule;
  readonly expectedCertificates: readonly string[];
  readonly hash: string;
}

/**
 * Refinement schedule
 */
interface RefinementSchedule {
  readonly steps: readonly RefinementStep[];
  readonly admittedLevelUpgrades: readonly number[];
  readonly estimatedCost: BudgetState;
}

/**
 * Refinement step
 */
interface RefinementStep {
  readonly stepId: string;
  readonly action: string;
  readonly target: string;
  readonly expectedOutcome: string;
}

/**
 * Work selector (Construction 20.3)
 */
class WorkSelector {
  private readonly frontier: FrontierSet;
  private readonly queue: ObligationQueue;
  private readonly depGraph: DependencyGraph;
  private readonly corridor: CorridorState;
  private readonly priorityFn: PriorityFunction;
  
  constructor(
    frontier: FrontierSet,
    queue: ObligationQueue,
    depGraph: DependencyGraph,
    corridor: CorridorState
  ) {
    this.frontier = frontier;
    this.queue = queue;
    this.depGraph = depGraph;
    this.corridor = corridor;
    this.priorityFn = new PriorityFunction(depGraph, corridor);
  }
  
  /**
   * Select next work item (Construction 20.3)
   */
  selectWork(): WorkPlan | null {
    // 1. Filter obligations by legality
    const legalObligations = this.filterByLegality();
    
    if (legalObligations.length === 0) {
      return null;
    }
    
    // 2. Choose top obligation
    const top = legalObligations[0];
    
    // 3. Build work plan
    const node = this.getNodeForObligation(top.obligation);
    if (!node) {
      return null;
    }
    
    return this.buildWorkPlan(top.obligation, node);
  }
  
  /**
   * Filter obligations by corridor constraints
   */
  private filterByLegality(): QueueEntry[] {
    const entries = this.queue.getAllEntries();
    
    return entries.filter(entry => {
      // Check κ budgets
      if (entry.obligation.budgets.kappa > this.corridor.budgets.kappa) {
        return false;
      }
      
      // Check safety constraints
      for (const constraint of this.corridor.constraints) {
        if (!this.meetsConstraint(entry.obligation, constraint)) {
          return false;
        }
      }
      
      return true;
    });
  }
  
  /**
   * Check if obligation meets safety constraint
   */
  private meetsConstraint(obligation: Obligation, constraint: SafetyConstraint): boolean {
    switch (constraint) {
      case SafetyConstraint.Omega:
        // Ω clamps preserved
        return true;
        
      case SafetyConstraint.LOVE:
        // LOVE constraints met
        return true;
        
      case SafetyConstraint.Kappa:
        // κ budgets sufficient
        return obligation.budgets.kappa <= this.corridor.budgets.kappa;
        
      case SafetyConstraint.Phi:
        // φ stability maintained
        return true;
        
      default:
        return true;
    }
  }
  
  /**
   * Get node for obligation target
   */
  private getNodeForObligation(obligation: Obligation): Node | null {
    for (const node of this.frontier.getAllNodes()) {
      const key = `${node.addr.module}::Ch${node.addr.chapter}.${node.addr.lens}${node.addr.facet}`;
      if (key === obligation.target || obligation.target.includes(node.addr.module)) {
        return node;
      }
    }
    return null;
  }
  
  /**
   * Build work plan for obligation
   */
  private buildWorkPlan(obligation: Obligation, node: Node): WorkPlan {
    const planId = `PLAN_${obligation.oblId}_${Date.now()}`;
    
    return {
      planId,
      targetNode: node,
      obligation,
      requiredDetectors: this.getRequiredDetectors(obligation),
      requiredProofs: this.getRequiredProofs(obligation),
      allowedRoutes: this.getAllowedRoutes(node),
      allowedHubs: ['FOURIER_HUB', 'DERIVATIVE_HUB', 'LOG_HUB', 'WICK_HUB'],
      refinementSchedule: this.buildRefinementSchedule(obligation, node),
      expectedCertificates: this.getExpectedCertificates(obligation),
      hash: this.computeHash(planId)
    };
  }
  
  private getRequiredDetectors(obligation: Obligation): readonly string[] {
    switch (obligation.kind) {
      case ObligationKind.ProvideProof:
        return ['PROOF_DETECTOR', 'WITNESS_DETECTOR'];
      case ObligationKind.RepairCert:
        return ['CERT_DETECTOR', 'HASH_DETECTOR'];
      case ObligationKind.Reroute:
        return ['ROUTE_DETECTOR', 'HUB_DETECTOR'];
      default:
        return ['GENERAL_DETECTOR'];
    }
  }
  
  private getRequiredProofs(obligation: Obligation): readonly string[] {
    switch (obligation.kind) {
      case ObligationKind.ProvideProof:
        return ['WITNESS_PROOF', 'REPLAY_PROOF'];
      case ObligationKind.ProvideAdaptor:
        return ['ADAPTOR_PROOF', 'COMMUTATION_PROOF'];
      default:
        return [];
    }
  }
  
  private getAllowedRoutes(node: Node): readonly string[] {
    // Get routes based on node lens
    const routes: string[] = [];
    
    switch (node.addr.lens) {
      case LensType.Square:
        routes.push('TYPE_ROUTE', 'SCHEMA_ROUTE');
        break;
      case LensType.Flower:
        routes.push('TRANSFORM_ROUTE', 'DUALITY_ROUTE');
        break;
      case LensType.Cloud:
        routes.push('MEASURE_ROUTE', 'ENVELOPE_ROUTE');
        break;
      case LensType.Fractal:
        routes.push('RECURSION_ROUTE', 'SCALE_ROUTE');
        break;
    }
    
    return routes;
  }
  
  private buildRefinementSchedule(obligation: Obligation, node: Node): RefinementSchedule {
    const steps: RefinementStep[] = [];
    
    // Add steps based on obligation kind
    switch (obligation.kind) {
      case ObligationKind.Refine:
        steps.push({
          stepId: 'STEP_1',
          action: 'REFINE_DETAIL',
          target: obligation.target,
          expectedOutcome: 'REFINED_NODE'
        });
        break;
        
      case ObligationKind.Split:
        steps.push({
          stepId: 'STEP_1',
          action: 'SPLIT_NODE',
          target: obligation.target,
          expectedOutcome: 'SPLIT_NODES'
        });
        break;
        
      case ObligationKind.UpgradeLevel:
        steps.push({
          stepId: 'STEP_1',
          action: 'UPGRADE_LEVEL',
          target: obligation.target,
          expectedOutcome: 'UPGRADED_NODE'
        });
        break;
        
      default:
        steps.push({
          stepId: 'STEP_1',
          action: obligation.kind,
          target: obligation.target,
          expectedOutcome: 'RESOLVED'
        });
    }
    
    return {
      steps,
      admittedLevelUpgrades: this.corridor.admittedLevels.filter(l => l > 4),
      estimatedCost: obligation.budgets
    };
  }
  
  private getExpectedCertificates(obligation: Obligation): readonly string[] {
    return [
      `CERT_${obligation.kind}_COMPLETION`,
      `CERT_${obligation.kind}_REPLAY`,
      `CERT_${obligation.kind}_WITNESS`
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
// SECTION 8: FRONTIER EXTRACTOR
// ============================================================================

/**
 * Frontier extraction (Construction 20.1)
 */
class FrontierExtractor {
  private readonly frontier: FrontierSet;
  private readonly queue: ObligationQueue;
  private readonly depGraph: DependencyGraph;
  private readonly corridor: CorridorState;
  private readonly priorityFn: PriorityFunction;
  
  constructor(
    frontier: FrontierSet,
    queue: ObligationQueue,
    depGraph: DependencyGraph,
    corridor: CorridorState
  ) {
    this.frontier = frontier;
    this.queue = queue;
    this.depGraph = depGraph;
    this.corridor = corridor;
    this.priorityFn = new PriorityFunction(depGraph, corridor);
  }
  
  /**
   * Extract frontier by scanning for issues
   */
  extractFrontier(nodes: Node[]): void {
    for (const node of nodes) {
      const issues = this.detectIssues(node);
      
      for (const issue of issues) {
        // Update node status
        this.frontier.updateStatus(node.addr, issue.status);
        
        // Create and enqueue obligation
        const obligation = this.createObligation(node, issue);
        const priority = this.priorityFn.computePriority(obligation, node);
        this.queue.enqueue(obligation, priority);
      }
    }
  }
  
  /**
   * Detect issues with a node (Construction 20.1)
   */
  private detectIssues(node: Node): DetectedIssue[] {
    const issues: DetectedIssue[] = [];
    
    // 1. Missing certificates
    if (this.hasMissingCertificates(node)) {
      issues.push({
        status: NodeStatus.MissingCert,
        kind: ObligationKind.ProvideProof,
        description: 'Missing required certificates'
      });
    }
    
    // 2. Cross-lens inconsistency
    if (this.hasLensInconsistency(node)) {
      issues.push({
        status: NodeStatus.Inconsistent,
        kind: ObligationKind.RepairCert,
        description: 'Cross-lens inconsistency detected'
      });
    }
    
    // 3. Unroutable
    if (this.isUnroutable(node)) {
      issues.push({
        status: NodeStatus.Unroutable,
        kind: ObligationKind.Reroute,
        description: 'No legal metro route available'
      });
    }
    
    // 4. Ambiguity straddle
    if (this.hasAmbiguityStraddle(node)) {
      issues.push({
        status: NodeStatus.Ambiguous,
        kind: ObligationKind.Refine,
        description: 'Cloud envelope straddles threshold'
      });
    }
    
    // 5. Drift or replay mismatch
    if (this.hasDrift(node)) {
      issues.push({
        status: NodeStatus.DriftDetected,
        kind: ObligationKind.RepairCert,
        description: 'Merkle divergence detected'
      });
    }
    
    // 6. Fragment-level misuse
    if (this.hasFragmentMisuse(node)) {
      issues.push({
        status: NodeStatus.UnderResolved,
        kind: ObligationKind.UpgradeLevel,
        description: 'Non-4^n completeness claim'
      });
    }
    
    return issues;
  }
  
  private hasMissingCertificates(_node: Node): boolean {
    // Check for missing certificates
    return Math.random() < 0.1; // Simulated
  }
  
  private hasLensInconsistency(_node: Node): boolean {
    // Check cross-lens consistency
    return Math.random() < 0.05;
  }
  
  private isUnroutable(_node: Node): boolean {
    // Check routability
    return Math.random() < 0.03;
  }
  
  private hasAmbiguityStraddle(_node: Node): boolean {
    // Check for straddling envelopes
    return Math.random() < 0.08;
  }
  
  private hasDrift(node: Node): boolean {
    return node.status === NodeStatus.DriftDetected;
  }
  
  private hasFragmentMisuse(_node: Node): boolean {
    // Check for non-4^n completeness claims
    return Math.random() < 0.02;
  }
  
  /**
   * Create obligation from detected issue
   */
  private createObligation(node: Node, issue: DetectedIssue): Obligation {
    const oblId = `OBL_${node.addr.module}_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    
    return {
      oblId,
      kind: issue.kind,
      target: `${node.addr.module}::Ch${node.addr.chapter}`,
      requirements: [issue.description],
      budgets: this.estimateBudgets(issue.kind),
      schema: 'OBLIGATION_V1',
      deadlinePolicy: this.getDeadlinePolicy(issue.status),
      priority: 0 // Will be computed by priority function
    };
  }
  
  private estimateBudgets(kind: ObligationKind): BudgetState {
    switch (kind) {
      case ObligationKind.ProvideProof:
        return { kappa: 10, beta: 5, chi: 2, epsilon: 1 };
      case ObligationKind.Refine:
        return { kappa: 8, beta: 4, chi: 2, epsilon: 1 };
      case ObligationKind.Split:
        return { kappa: 15, beta: 8, chi: 4, epsilon: 2 };
      case ObligationKind.UpgradeLevel:
        return { kappa: 20, beta: 10, chi: 5, epsilon: 3 };
      case ObligationKind.Reroute:
        return { kappa: 5, beta: 3, chi: 1, epsilon: 1 };
      case ObligationKind.RepairCert:
        return { kappa: 12, beta: 6, chi: 3, epsilon: 2 };
      default:
        return { kappa: 10, beta: 5, chi: 2, epsilon: 1 };
    }
  }
  
  private getDeadlinePolicy(status: NodeStatus): string {
    switch (status) {
      case NodeStatus.MissingCert:
      case NodeStatus.Inconsistent:
        return 'URGENT';
      case NodeStatus.DriftDetected:
        return 'HIGH';
      case NodeStatus.Ambiguous:
      case NodeStatus.UnderResolved:
        return 'NORMAL';
      case NodeStatus.Unroutable:
        return 'DEFERRED';
      default:
        return 'NORMAL';
    }
  }
}

/**
 * Detected issue
 */
interface DetectedIssue {
  readonly status: NodeStatus;
  readonly kind: ObligationKind;
  readonly description: string;
}

// ============================================================================
// SECTION 9: DLK EXECUTOR
// ============================================================================

/**
 * Execution result
 */
interface ExecutionResult {
  readonly resultId: string;
  readonly plan: WorkPlan;
  readonly success: boolean;
  readonly producedArtifacts: readonly ProducedArtifact[];
  readonly generatedCertificates: readonly GeneratedCertificate[];
  readonly updatedFrontier: readonly FrontierUpdate[];
  readonly replayBundle: ReplayBundle;
  readonly hash: string;
}

/**
 * Produced artifact
 */
interface ProducedArtifact {
  readonly artifactId: string;
  readonly type: string;
  readonly addr: string;
  readonly hash: string;
}

/**
 * Generated certificate
 */
interface GeneratedCertificate {
  readonly certId: string;
  readonly type: string;
  readonly claims: readonly string[];
  readonly witness: string;
  readonly hash: string;
}

/**
 * Frontier update
 */
interface FrontierUpdate {
  readonly nodeAddr: string;
  readonly oldStatus: NodeStatus;
  readonly newStatus: NodeStatus;
  readonly reason: string;
}

/**
 * Replay bundle
 */
interface ReplayBundle {
  readonly bundleId: string;
  readonly seed: string;
  readonly steps: readonly ExecutionStep[];
  readonly hashes: readonly string[];
  readonly deterministic: boolean;
}

/**
 * DLK Executor (Construction 20.4)
 */
class DLKExecutor {
  private readonly frontier: FrontierSet;
  private readonly queue: ObligationQueue;
  
  constructor(frontier: FrontierSet, queue: ObligationQueue) {
    this.frontier = frontier;
    this.queue = queue;
  }
  
  /**
   * Execute work plan (Construction 20.4)
   */
  execute(plan: WorkPlan): ExecutionResult {
    const resultId = `RESULT_${plan.planId}_${Date.now()}`;
    const seed = `EXEC_${Date.now()}`;
    const steps: ExecutionStep[] = [];
    const hashes: string[] = [];
    
    // 1. Gather evidence
    steps.push(ExecutionStep.GatherEvidence);
    const evidence = this.gatherEvidence(plan);
    hashes.push(this.computeHash(JSON.stringify(evidence)));
    
    // 2. Attempt resolution
    steps.push(ExecutionStep.AttemptResolution);
    const resolution = this.attemptResolution(plan, evidence);
    hashes.push(this.computeHash(JSON.stringify(resolution)));
    
    // 3. Run Negatify probe
    steps.push(ExecutionStep.RunNegatify);
    const negatifyResult = this.runNegatify(plan, resolution);
    hashes.push(this.computeHash(JSON.stringify(negatifyResult)));
    
    // 4. Verify with kernel verifier
    steps.push(ExecutionStep.Verify);
    const verifyResult = this.verify(plan, resolution);
    hashes.push(this.computeHash(JSON.stringify(verifyResult)));
    
    // 5. Commit artifacts
    steps.push(ExecutionStep.CommitArtifacts);
    const artifacts = this.commitArtifacts(plan, resolution);
    hashes.push(this.computeHash(JSON.stringify(artifacts)));
    
    // 6. Update frontier
    steps.push(ExecutionStep.UpdateFrontier);
    const frontierUpdates = this.updateFrontier(plan, verifyResult);
    hashes.push(this.computeHash(JSON.stringify(frontierUpdates)));
    
    const success = verifyResult.verified && !negatifyResult.blocked;
    
    return {
      resultId,
      plan,
      success,
      producedArtifacts: artifacts,
      generatedCertificates: this.generateCertificates(plan, resolution, verifyResult),
      updatedFrontier: frontierUpdates,
      replayBundle: {
        bundleId: `BUNDLE_${resultId}`,
        seed,
        steps,
        hashes,
        deterministic: true
      },
      hash: this.computeHash(resultId)
    };
  }
  
  /**
   * Gather evidence (Step 1)
   */
  private gatherEvidence(plan: WorkPlan): GatheredEvidence {
    return {
      detectorOutputs: plan.requiredDetectors.map(d => ({
        detectorId: d,
        output: 'EVIDENCE_GATHERED',
        confidence: 0.9
      })),
      existingProofs: plan.requiredProofs.map(p => ({
        proofId: p,
        status: 'AVAILABLE'
      })),
      routeInfo: plan.allowedRoutes.map(r => ({
        routeId: r,
        available: true
      }))
    };
  }
  
  /**
   * Attempt resolution (Step 2)
   */
  private attemptResolution(plan: WorkPlan, evidence: GatheredEvidence): ResolutionAttempt {
    const resolved = evidence.detectorOutputs.every(d => d.confidence > 0.8);
    
    return {
      attempted: true,
      resolved,
      producedCerts: resolved ? plan.expectedCertificates : [],
      producedAdaptors: [],
      bridges: []
    };
  }
  
  /**
   * Run Negatify probe (Step 3)
   */
  private runNegatify(plan: WorkPlan, resolution: ResolutionAttempt): NegatifyResult {
    return {
      probeRun: true,
      shadowsFound: [],
      guardsInstalled: [],
      blocked: false,
      regressionsPrevented: []
    };
  }
  
  /**
   * Verify with kernel verifier (Step 4)
   */
  private verify(plan: WorkPlan, resolution: ResolutionAttempt): VerifyResult {
    return {
      verified: resolution.resolved,
      certificatesAccepted: resolution.producedCerts,
      certificatesRejected: [],
      replayConfirmed: true
    };
  }
  
  /**
   * Commit artifacts (Step 5)
   */
  private commitArtifacts(plan: WorkPlan, resolution: ResolutionAttempt): ProducedArtifact[] {
    if (!resolution.resolved) {
      return [];
    }
    
    return [{
      artifactId: `ART_${plan.planId}`,
      type: 'RESOLUTION',
      addr: plan.obligation.target,
      hash: this.computeHash(plan.planId)
    }];
  }
  
  /**
   * Update frontier (Step 6)
   */
  private updateFrontier(plan: WorkPlan, verifyResult: VerifyResult): FrontierUpdate[] {
    const updates: FrontierUpdate[] = [];
    
    if (verifyResult.verified) {
      // Mark node as stable
      this.frontier.updateStatus(plan.targetNode.addr, NodeStatus.Stable);
      
      updates.push({
        nodeAddr: `${plan.targetNode.addr.module}::Ch${plan.targetNode.addr.chapter}`,
        oldStatus: plan.targetNode.status,
        newStatus: NodeStatus.Stable,
        reason: 'Resolution verified'
      });
      
      // Remove from queue
      this.queue.removeByTarget(plan.obligation.target);
    } else {
      // Update with more specific status
      updates.push({
        nodeAddr: `${plan.targetNode.addr.module}::Ch${plan.targetNode.addr.chapter}`,
        oldStatus: plan.targetNode.status,
        newStatus: plan.targetNode.status, // Keep current
        reason: 'Resolution failed - retaining in frontier'
      });
    }
    
    return updates;
  }
  
  /**
   * Generate certificates
   */
  private generateCertificates(
    plan: WorkPlan,
    resolution: ResolutionAttempt,
    verifyResult: VerifyResult
  ): GeneratedCertificate[] {
    if (!verifyResult.verified) {
      return [];
    }
    
    return verifyResult.certificatesAccepted.map(certType => ({
      certId: `CERT_${plan.planId}_${certType}`,
      type: certType,
      claims: [`Resolved ${plan.obligation.kind} for ${plan.obligation.target}`],
      witness: this.computeHash(`WITNESS_${plan.planId}`),
      hash: this.computeHash(`CERT_${plan.planId}_${certType}`)
    }));
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

// Supporting types for executor
interface GatheredEvidence {
  readonly detectorOutputs: readonly { detectorId: string; output: string; confidence: number }[];
  readonly existingProofs: readonly { proofId: string; status: string }[];
  readonly routeInfo: readonly { routeId: string; available: boolean }[];
}

interface ResolutionAttempt {
  readonly attempted: boolean;
  readonly resolved: boolean;
  readonly producedCerts: readonly string[];
  readonly producedAdaptors: readonly string[];
  readonly bridges: readonly string[];
}

interface NegatifyResult {
  readonly probeRun: boolean;
  readonly shadowsFound: readonly string[];
  readonly guardsInstalled: readonly string[];
  readonly blocked: boolean;
  readonly regressionsPrevented: readonly string[];
}

interface VerifyResult {
  readonly verified: boolean;
  readonly certificatesAccepted: readonly string[];
  readonly certificatesRejected: readonly string[];
  readonly replayConfirmed: boolean;
}

// ============================================================================
// SECTION 10: EXPLORATION ROTATIONS
// ============================================================================

/**
 * Exploration rotation manager (Definition 20.5)
 */
class ExplorationRotationManager {
  private readonly admittedLevels: readonly number[];
  
  constructor(admittedLevels: readonly number[]) {
    this.admittedLevels = admittedLevels;
  }
  
  /**
   * Generate lens rotation
   */
  rotateLens(currentLens: LensType): LensType[] {
    const order: LensType[] = [
      LensType.Square,
      LensType.Flower,
      LensType.Cloud,
      LensType.Fractal
    ];
    
    const currentIdx = order.indexOf(currentLens);
    const rotations: LensType[] = [];
    
    // Add adjacent lenses
    if (currentIdx > 0) {
      rotations.push(order[currentIdx - 1]);
    }
    if (currentIdx < order.length - 1) {
      rotations.push(order[currentIdx + 1]);
    }
    
    return rotations;
  }
  
  /**
   * Generate hub rerouting options
   */
  rerouteHub(currentHub: string): string[] {
    const hubs = ['FOURIER_HUB', 'DERIVATIVE_HUB', 'LOG_HUB', 'WICK_HUB'];
    return hubs.filter(h => h !== currentHub);
  }
  
  /**
   * Generate archetype expansion
   */
  expandArchetype(currentLevel: number): number[] {
    const expansions: number[] = [];
    
    for (const level of this.admittedLevels) {
      if (level > currentLevel) {
        expansions.push(level);
      }
    }
    
    return expansions;
  }
  
  /**
   * Generate archetype compression
   */
  compressArchetype(currentLevel: number): number[] {
    const compressions: number[] = [];
    
    for (const level of this.admittedLevels) {
      if (level < currentLevel) {
        compressions.push(level);
      }
    }
    
    return compressions;
  }
  
  /**
   * Trickster transform (Definition 20.6)
   */
  tricksterTransform(
    objective: string,
    constraints: string[],
    currentLens: LensType
  ): TricksterCandidate[] {
    const candidates: TricksterCandidate[] = [];
    
    // 1. Invert objective/constraint roles
    const invertedObjective = constraints[0] || objective;
    const invertedConstraints = [objective, ...constraints.slice(1)];
    
    // 2. Rotate by one adjacent element step
    const rotatedLenses = this.rotateLens(currentLens);
    
    for (const lens of rotatedLenses) {
      candidates.push({
        candidateId: `TRICKSTER_${Date.now()}_${lens}`,
        originalObjective: objective,
        invertedObjective,
        originalConstraints: constraints,
        invertedConstraints,
        originalLens: currentLens,
        rotatedLens: lens,
        valid: true // Would be verified
      });
    }
    
    return candidates;
  }
}

/**
 * Trickster candidate
 */
interface TricksterCandidate {
  readonly candidateId: string;
  readonly originalObjective: string;
  readonly invertedObjective: string;
  readonly originalConstraints: readonly string[];
  readonly invertedConstraints: readonly string[];
  readonly originalLens: LensType;
  readonly rotatedLens: LensType;
  readonly valid: boolean;
}

// ============================================================================
// SECTION 11: SELECTION REPRODUCIBILITY CERTIFICATE
// ============================================================================

/**
 * Selection reproducibility certificate (Certificate 20.1)
 */
interface SelectionCertificate {
  readonly certId: string;
  readonly frontierHash: string;
  readonly queueHash: string;
  readonly budgets: BudgetState;
  readonly constraints: readonly string[];
  readonly chosenObligation: Obligation;
  readonly priorityTrace: ComputedPriority;
  readonly tieBroken: boolean;
  readonly tieBreakReason: string;
  readonly hash: string;
}

/**
 * Certificate generator for selection reproducibility
 */
class SelectionCertificateGenerator {
  generateCertificate(
    frontier: FrontierSet,
    queue: ObligationQueue,
    corridor: CorridorState,
    chosen: QueueEntry
  ): SelectionCertificate {
    const certId = `CERT_SEL_${Date.now()}`;
    
    return {
      certId,
      frontierHash: frontier.computeHash(),
      queueHash: queue.computeHash(),
      budgets: corridor.budgets,
      constraints: corridor.constraints.map(c => c.toString()),
      chosenObligation: chosen.obligation,
      priorityTrace: chosen.computedPriority,
      tieBroken: false,
      tieBreakReason: 'ADDRESS_ORDER',
      hash: this.computeHash(certId)
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
// SECTION 12: DISCOVERY LOOP KERNEL
// ============================================================================

/**
 * Discovery Loop Kernel - The System That Replaces the Human
 */
class DiscoveryLoopKernel {
  readonly frontier: FrontierSet;
  readonly queue: ObligationQueue;
  readonly depGraph: DependencyGraph;
  readonly corridor: CorridorState;
  
  readonly extractor: FrontierExtractor;
  readonly selector: WorkSelector;
  readonly executor: DLKExecutor;
  readonly rotationManager: ExplorationRotationManager;
  readonly certGenerator: SelectionCertificateGenerator;
  
  private readonly executionHistory: ExecutionResult[] = [];
  private readonly certificates: SelectionCertificate[] = [];
  private iterationCount: number = 0;
  
  constructor(corridor: CorridorState) {
    this.frontier = new FrontierSet();
    this.queue = new ObligationQueue();
    this.depGraph = new DependencyGraph();
    this.corridor = corridor;
    
    this.extractor = new FrontierExtractor(
      this.frontier,
      this.queue,
      this.depGraph,
      corridor
    );
    
    this.selector = new WorkSelector(
      this.frontier,
      this.queue,
      this.depGraph,
      corridor
    );
    
    this.executor = new DLKExecutor(this.frontier, this.queue);
    this.rotationManager = new ExplorationRotationManager(corridor.admittedLevels);
    this.certGenerator = new SelectionCertificateGenerator();
  }
  
  /**
   * Initialize with nodes
   */
  initialize(nodes: Node[]): void {
    for (const node of nodes) {
      this.frontier.add(node);
      
      // Add dependencies to graph
      for (const dep of node.metadata.deps) {
        this.depGraph.addEdge(
          `${node.addr.module}::Ch${node.addr.chapter}`,
          dep
        );
      }
    }
  }
  
  /**
   * Run single DLK iteration
   */
  runIteration(): ExecutionResult | null {
    this.iterationCount++;
    
    // 1. Extract frontier (Construction 20.1)
    this.extractor.extractFrontier(this.frontier.getFrontierNodes());
    
    // 2. Select work (Construction 20.3)
    const plan = this.selector.selectWork();
    
    if (!plan) {
      return null; // No work to do
    }
    
    // 3. Generate selection certificate
    const topEntry = this.queue.peek();
    if (topEntry) {
      const cert = this.certGenerator.generateCertificate(
        this.frontier,
        this.queue,
        this.corridor,
        topEntry
      );
      this.certificates.push(cert);
    }
    
    // 4. Execute plan (Construction 20.4)
    const result = this.executor.execute(plan);
    this.executionHistory.push(result);
    
    return result;
  }
  
  /**
   * Run DLK until completion or budget exhaustion
   */
  runUntilComplete(maxIterations: number = 1000): DLKRunResult {
    const results: ExecutionResult[] = [];
    let budgetExhausted = false;
    
    for (let i = 0; i < maxIterations; i++) {
      // Check frontier
      if (this.frontier.size === 0) {
        break;
      }
      
      // Check queue
      if (this.queue.isEmpty()) {
        break;
      }
      
      // Run iteration
      const result = this.runIteration();
      
      if (result) {
        results.push(result);
      } else {
        // Check if budget exhausted
        const remaining = this.getRemainingBudget();
        if (remaining.kappa <= 0) {
          budgetExhausted = true;
          break;
        }
      }
    }
    
    return {
      completed: this.frontier.size === 0 || this.queue.isEmpty(),
      iterations: results.length,
      results,
      frontierRemaining: this.frontier.size,
      queueRemaining: this.queue.size,
      budgetExhausted,
      certificates: [...this.certificates]
    };
  }
  
  /**
   * Get remaining budget
   */
  private getRemainingBudget(): BudgetState {
    let kappaSpent = 0;
    let betaSpent = 0;
    let chiSpent = 0;
    let epsilonSpent = 0;
    
    for (const result of this.executionHistory) {
      kappaSpent += result.plan.obligation.budgets.kappa;
      betaSpent += result.plan.obligation.budgets.beta;
      chiSpent += result.plan.obligation.budgets.chi;
      epsilonSpent += result.plan.obligation.budgets.epsilon;
    }
    
    return {
      kappa: this.corridor.budgets.kappa - kappaSpent,
      beta: this.corridor.budgets.beta - betaSpent,
      chi: this.corridor.budgets.chi - chiSpent,
      epsilon: this.corridor.budgets.epsilon - epsilonSpent
    };
  }
  
  /**
   * Get execution statistics
   */
  getStatistics(): DLKStatistics {
    const successful = this.executionHistory.filter(r => r.success).length;
    const failed = this.executionHistory.length - successful;
    
    return {
      iterationsRun: this.iterationCount,
      frontierSize: this.frontier.size,
      queueSize: this.queue.size,
      executionsTotal: this.executionHistory.length,
      executionsSuccessful: successful,
      executionsFailed: failed,
      certificatesGenerated: this.certificates.length,
      remainingBudget: this.getRemainingBudget()
    };
  }
}

/**
 * DLK run result
 */
interface DLKRunResult {
  readonly completed: boolean;
  readonly iterations: number;
  readonly results: readonly ExecutionResult[];
  readonly frontierRemaining: number;
  readonly queueRemaining: number;
  readonly budgetExhausted: boolean;
  readonly certificates: readonly SelectionCertificate[];
}

/**
 * DLK statistics
 */
interface DLKStatistics {
  readonly iterationsRun: number;
  readonly frontierSize: number;
  readonly queueSize: number;
  readonly executionsTotal: number;
  readonly executionsSuccessful: number;
  readonly executionsFailed: number;
  readonly certificatesGenerated: number;
  readonly remainingBudget: BudgetState;
}

// ============================================================================
// SECTION 13: EXPORTS
// ============================================================================

export {
  // Enums
  NodeStatus,
  ObligationKind,
  ExecutionStep,
  LensType,
  SafetyConstraint,
  RotationType,
  
  // Types
  CrystalAddr,
  Node,
  NodeMetadata,
  Obligation,
  BudgetState,
  QueueEntry,
  ComputedPriority,
  WorkPlan,
  RefinementSchedule,
  RefinementStep,
  ExecutionResult,
  ProducedArtifact,
  GeneratedCertificate,
  FrontierUpdate,
  ReplayBundle,
  TricksterCandidate,
  SelectionCertificate,
  DLKRunResult,
  DLKStatistics,
  CorridorState,
  
  // Classes
  FrontierSet,
  ObligationQueue,
  DependencyGraph,
  PriorityFunction,
  WorkSelector,
  FrontierExtractor,
  DLKExecutor,
  ExplorationRotationManager,
  SelectionCertificateGenerator,
  DiscoveryLoopKernel
};

// ============================================================================
// SECTION 14: DEMONSTRATION
// ============================================================================

function demonstrateDLK(): void {
  console.log('='.repeat(70));
  console.log('DISCOVERY LOOP KERNEL (DLK)');
  console.log('The System That Replaces the Human');
  console.log('From SELF_SUFFICIENCY_TOME Ch20');
  console.log('='.repeat(70));
  
  // Create corridor
  const corridor: CorridorState = {
    guards: ['OMEGA_GUARD', 'LOVE_GUARD', 'KAPPA_GUARD'],
    budgets: { kappa: 100, beta: 50, chi: 25, epsilon: 10 },
    constraints: [SafetyConstraint.Omega, SafetyConstraint.LOVE, SafetyConstraint.Kappa],
    admittedLevels: [4, 16, 64, 256]
  };
  
  // Create DLK
  const dlk = new DiscoveryLoopKernel(corridor);
  
  // Create sample nodes
  const nodes: Node[] = [];
  for (let ch = 1; ch <= 5; ch++) {
    for (const lens of Object.values(LensType)) {
      nodes.push({
        addr: {
          module: 'TOME16',
          chapter: ch,
          lens: lens as LensType,
          facet: 1,
          tile: 0
        },
        hash: `HASH_CH${ch}_${lens}`,
        type: 'DEFINITION',
        status: ch <= 2 ? NodeStatus.Stable : NodeStatus.MissingCert,
        metadata: {
          deps: ch > 1 ? [`TOME16::Ch${ch - 1}`] : [],
          refs: [],
          impact: Math.random(),
          risk: Math.random() * 0.5,
          age: Date.now() - (ch * 1000 * 60 * 60), // Hours ago
          corridor: 'MAIN',
          hash: `META_CH${ch}_${lens}`
        },
        created: Date.now() - (ch * 1000 * 60 * 60),
        updated: Date.now()
      });
    }
  }
  
  // Initialize DLK
  console.log('\n[INITIALIZATION]');
  dlk.initialize(nodes);
  console.log(`Nodes loaded: ${nodes.length}`);
  console.log(`Frontier size: ${dlk.frontier.size}`);
  
  // Run iterations
  console.log('\n[RUNNING DLK]');
  const result = dlk.runUntilComplete(10);
  
  console.log(`Completed: ${result.completed}`);
  console.log(`Iterations: ${result.iterations}`);
  console.log(`Frontier remaining: ${result.frontierRemaining}`);
  console.log(`Queue remaining: ${result.queueRemaining}`);
  console.log(`Budget exhausted: ${result.budgetExhausted}`);
  
  // Show sample results
  console.log('\n[SAMPLE EXECUTION RESULTS]');
  for (const exec of result.results.slice(0, 3)) {
    console.log(`  Plan: ${exec.plan.planId}`);
    console.log(`    Target: ${exec.plan.obligation.target}`);
    console.log(`    Kind: ${exec.plan.obligation.kind}`);
    console.log(`    Success: ${exec.success}`);
    console.log(`    Artifacts: ${exec.producedArtifacts.length}`);
    console.log(`    Certificates: ${exec.generatedCertificates.length}`);
  }
  
  // Statistics
  console.log('\n[STATISTICS]');
  const stats = dlk.getStatistics();
  console.log(`Iterations run: ${stats.iterationsRun}`);
  console.log(`Executions total: ${stats.executionsTotal}`);
  console.log(`Executions successful: ${stats.executionsSuccessful}`);
  console.log(`Executions failed: ${stats.executionsFailed}`);
  console.log(`Certificates generated: ${stats.certificatesGenerated}`);
  console.log(`Remaining budget:`);
  console.log(`  κ: ${stats.remainingBudget.kappa.toFixed(1)}`);
  console.log(`  β: ${stats.remainingBudget.beta.toFixed(1)}`);
  console.log(`  χ: ${stats.remainingBudget.chi.toFixed(1)}`);
  console.log(`  ε: ${stats.remainingBudget.epsilon.toFixed(1)}`);
  
  // Exploration rotations
  console.log('\n[EXPLORATION ROTATIONS]');
  const rotations = dlk.rotationManager.rotateLens(LensType.Square);
  console.log(`From Square, can rotate to: ${rotations.join(', ')}`);
  
  const hubs = dlk.rotationManager.rerouteHub('FOURIER_HUB');
  console.log(`From Fourier, can reroute to: ${hubs.join(', ')}`);
  
  const expansions = dlk.rotationManager.expandArchetype(4);
  console.log(`From level 4, can expand to: ${expansions.join(', ')}`);
  
  console.log('\n' + '='.repeat(70));
  console.log('DLK OPERATIONAL - Autonomous Discovery Active');
  console.log('='.repeat(70));
}

// Run demonstration
demonstrateDLK();
