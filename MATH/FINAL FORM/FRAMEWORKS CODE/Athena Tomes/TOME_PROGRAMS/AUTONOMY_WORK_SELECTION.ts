/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * AUTONOMY WORK SELECTION - Frontier Pressure and Dependency Centrality
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Autonomy Target (from SELF_SUFFICIENCY_TOME §0):
 * 
 * Autonomy is achieved when the system can:
 *   1. Choose the next work item DETERMINISTICALLY from frontier pressure
 *      and dependency centrality
 *   2. Generate certificates that a bounded verifier accepts under
 *      explicit corridor guards
 *   3. Improve its own tooling WITHOUT bypassing safety, using
 *      regulated critics and Negatify shadow probes
 * 
 * The objective is operational: REMOVE HUMANS FROM THE CRITICAL LOOP by
 * ensuring that every claim is emitted as a CERTIFIED ARTIFACT that is
 * addressable, replayable, and reconstructible.
 * 
 * Core Discipline: 4⁴ crystal with 21 chapters × 4 lenses × 4 facets
 * 
 * @module AUTONOMY_WORK_SELECTION
 * @version 2.0.0
 */

import { TruthValue, WitnessPtr } from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: WORK ITEM TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Work item status
 */
export enum WorkStatus {
  Pending = "Pending",
  InProgress = "InProgress",
  Blocked = "Blocked",
  Completed = "Completed",
  Failed = "Failed",
  Deferred = "Deferred"
}

/**
 * Work item priority
 */
export enum WorkPriority {
  Critical = 1,
  High = 2,
  Normal = 3,
  Low = 4,
  Background = 5
}

/**
 * Work item type
 */
export enum WorkItemType {
  Definition = "Definition",
  Theorem = "Theorem",
  Algorithm = "Algorithm",
  Route = "Route",
  Detector = "Detector",
  Codec = "Codec",
  Policy = "Policy",
  Refinement = "Refinement",
  Certification = "Certification"
}

/**
 * Work item: A unit of autonomous work
 */
export interface WorkItem {
  id: string;
  type: WorkItemType;
  status: WorkStatus;
  priority: WorkPriority;
  
  /** Description of work */
  description: string;
  
  /** Dependencies (other work item IDs) */
  dependencies: string[];
  
  /** Blockers (conditions that must be met) */
  blockers: WorkBlocker[];
  
  /** Corridor constraints */
  corridor: WorkCorridor;
  
  /** Resource requirements */
  resources: ResourceRequirements;
  
  /** Frontier pressure score */
  frontierPressure: number;
  
  /** Dependency centrality score */
  dependencyCentrality: number;
  
  /** Combined priority score */
  priorityScore: number;
  
  /** Creation time */
  created: number;
  
  /** Last updated */
  updated: number;
  
  /** Deadline (if any) */
  deadline?: number;
  
  /** Output artifact address */
  outputAddress?: string;
  
  /** Certification status */
  certified: boolean;
}

export interface WorkBlocker {
  id: string;
  condition: string;
  resolved: boolean;
  resolvedAt?: number;
}

export interface WorkCorridor {
  guards: string[];
  budgets: ResourceBudget;
  maxDepth: number;
  timeout: number;
}

export interface ResourceRequirements {
  minComputation: number;
  minMemory: number;
  minTime: number;
  preferredLevel: number;  // Holographic level (4, 16, 64, 256)
}

export interface ResourceBudget {
  computation: number;
  memory: number;
  time: number;
  depth: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: FRONTIER PRESSURE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Frontier: The boundary of completed work
 */
export interface Frontier {
  /** Completed work items */
  completed: Set<string>;
  
  /** Pending work items at the frontier */
  pending: Set<string>;
  
  /** Blocked work items */
  blocked: Set<string>;
  
  /** Pressure map: work item -> pressure score */
  pressureMap: Map<string, number>;
  
  /** Last computation time */
  computedAt: number;
}

/**
 * Compute frontier pressure for a work item
 * 
 * Frontier pressure measures how much "demand" there is for completing
 * a work item based on:
 *   - Number of dependent items waiting
 *   - Priority of dependent items
 *   - Time since creation
 *   - Deadline proximity
 */
export function computeFrontierPressure(
  item: WorkItem,
  dependents: WorkItem[],
  now: number
): number {
  let pressure = 0;
  
  // Base pressure from priority
  pressure += (6 - item.priority) * 10;  // Higher priority = more pressure
  
  // Pressure from waiting dependents
  for (const dep of dependents) {
    if (dep.status === WorkStatus.Blocked) {
      // Blocked items add more pressure
      pressure += (6 - dep.priority) * 5;
    } else if (dep.status === WorkStatus.Pending) {
      pressure += (6 - dep.priority) * 2;
    }
  }
  
  // Time pressure (age in hours)
  const ageHours = (now - item.created) / (1000 * 60 * 60);
  pressure += Math.min(ageHours, 100);  // Cap at 100
  
  // Deadline pressure
  if (item.deadline) {
    const hoursToDeadline = (item.deadline - now) / (1000 * 60 * 60);
    if (hoursToDeadline < 0) {
      pressure += 200;  // Overdue
    } else if (hoursToDeadline < 24) {
      pressure += 100 - (hoursToDeadline * 4);  // Approaching deadline
    }
  }
  
  return pressure;
}

/**
 * Frontier pressure calculator
 */
export class FrontierPressureCalculator {
  private frontier: Frontier;
  private items: Map<string, WorkItem>;
  private dependencyGraph: Map<string, Set<string>>;  // item -> items that depend on it
  
  constructor() {
    this.frontier = {
      completed: new Set(),
      pending: new Set(),
      blocked: new Set(),
      pressureMap: new Map(),
      computedAt: 0
    };
    this.items = new Map();
    this.dependencyGraph = new Map();
  }
  
  /**
   * Add work item
   */
  addItem(item: WorkItem): void {
    this.items.set(item.id, item);
    
    // Update dependency graph
    for (const dep of item.dependencies) {
      if (!this.dependencyGraph.has(dep)) {
        this.dependencyGraph.set(dep, new Set());
      }
      this.dependencyGraph.get(dep)!.add(item.id);
    }
    
    // Update frontier sets
    this.updateFrontierSets();
  }
  
  /**
   * Update item status
   */
  updateStatus(itemId: string, status: WorkStatus): void {
    const item = this.items.get(itemId);
    if (item) {
      item.status = status;
      item.updated = Date.now();
      this.updateFrontierSets();
    }
  }
  
  /**
   * Compute all frontier pressures
   */
  computeAllPressures(): void {
    const now = Date.now();
    
    for (const [id, item] of this.items) {
      if (item.status === WorkStatus.Pending || item.status === WorkStatus.Blocked) {
        const dependentIds = this.dependencyGraph.get(id) ?? new Set();
        const dependents = Array.from(dependentIds)
          .map(depId => this.items.get(depId))
          .filter((i): i is WorkItem => i !== undefined);
        
        const pressure = computeFrontierPressure(item, dependents, now);
        this.frontier.pressureMap.set(id, pressure);
        item.frontierPressure = pressure;
      }
    }
    
    this.frontier.computedAt = now;
  }
  
  /**
   * Get items sorted by frontier pressure
   */
  getByPressure(): WorkItem[] {
    return Array.from(this.items.values())
      .filter(i => i.status === WorkStatus.Pending)
      .sort((a, b) => b.frontierPressure - a.frontierPressure);
  }
  
  /**
   * Get frontier statistics
   */
  getStats(): FrontierStats {
    return {
      completedCount: this.frontier.completed.size,
      pendingCount: this.frontier.pending.size,
      blockedCount: this.frontier.blocked.size,
      avgPressure: this.computeAveragePressure(),
      maxPressure: this.computeMaxPressure(),
      computedAt: this.frontier.computedAt
    };
  }
  
  private updateFrontierSets(): void {
    this.frontier.completed.clear();
    this.frontier.pending.clear();
    this.frontier.blocked.clear();
    
    for (const [id, item] of this.items) {
      switch (item.status) {
        case WorkStatus.Completed:
          this.frontier.completed.add(id);
          break;
        case WorkStatus.Pending:
          this.frontier.pending.add(id);
          break;
        case WorkStatus.Blocked:
          this.frontier.blocked.add(id);
          break;
      }
    }
  }
  
  private computeAveragePressure(): number {
    if (this.frontier.pressureMap.size === 0) return 0;
    
    let total = 0;
    for (const pressure of this.frontier.pressureMap.values()) {
      total += pressure;
    }
    return total / this.frontier.pressureMap.size;
  }
  
  private computeMaxPressure(): number {
    let max = 0;
    for (const pressure of this.frontier.pressureMap.values()) {
      max = Math.max(max, pressure);
    }
    return max;
  }
}

export interface FrontierStats {
  completedCount: number;
  pendingCount: number;
  blockedCount: number;
  avgPressure: number;
  maxPressure: number;
  computedAt: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: DEPENDENCY CENTRALITY
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Dependency graph for centrality computation
 */
export interface DependencyGraph {
  nodes: Set<string>;
  edges: Map<string, Set<string>>;  // from -> to (dependency direction)
  reverseEdges: Map<string, Set<string>>;  // to -> from
}

/**
 * Centrality scores
 */
export interface CentralityScores {
  /** Degree centrality: number of direct connections */
  degree: Map<string, number>;
  
  /** Betweenness centrality: how often node is on shortest paths */
  betweenness: Map<string, number>;
  
  /** PageRank-style centrality: importance based on incoming links */
  pageRank: Map<string, number>;
  
  /** Combined score */
  combined: Map<string, number>;
}

/**
 * Dependency centrality calculator
 */
export class DependencyCentralityCalculator {
  private graph: DependencyGraph;
  private scores: CentralityScores;
  
  constructor() {
    this.graph = {
      nodes: new Set(),
      edges: new Map(),
      reverseEdges: new Map()
    };
    
    this.scores = {
      degree: new Map(),
      betweenness: new Map(),
      pageRank: new Map(),
      combined: new Map()
    };
  }
  
  /**
   * Add node to graph
   */
  addNode(id: string): void {
    this.graph.nodes.add(id);
    if (!this.graph.edges.has(id)) {
      this.graph.edges.set(id, new Set());
    }
    if (!this.graph.reverseEdges.has(id)) {
      this.graph.reverseEdges.set(id, new Set());
    }
  }
  
  /**
   * Add edge (dependency)
   */
  addEdge(from: string, to: string): void {
    this.addNode(from);
    this.addNode(to);
    this.graph.edges.get(from)!.add(to);
    this.graph.reverseEdges.get(to)!.add(from);
  }
  
  /**
   * Compute all centrality measures
   */
  computeAll(): void {
    this.computeDegreeCentrality();
    this.computeBetweennessCentrality();
    this.computePageRank();
    this.computeCombinedScore();
  }
  
  /**
   * Get centrality score for a node
   */
  getCentrality(id: string): number {
    return this.scores.combined.get(id) ?? 0;
  }
  
  /**
   * Get nodes sorted by centrality
   */
  getByCentrality(): { id: string; score: number }[] {
    return Array.from(this.scores.combined.entries())
      .map(([id, score]) => ({ id, score }))
      .sort((a, b) => b.score - a.score);
  }
  
  private computeDegreeCentrality(): void {
    for (const id of this.graph.nodes) {
      const outDegree = this.graph.edges.get(id)?.size ?? 0;
      const inDegree = this.graph.reverseEdges.get(id)?.size ?? 0;
      this.scores.degree.set(id, outDegree + inDegree);
    }
  }
  
  private computeBetweennessCentrality(): void {
    // Initialize
    for (const id of this.graph.nodes) {
      this.scores.betweenness.set(id, 0);
    }
    
    // For each source node
    for (const source of this.graph.nodes) {
      // BFS to find shortest paths
      const distances = new Map<string, number>();
      const pathCounts = new Map<string, number>();
      const predecessors = new Map<string, string[]>();
      
      const queue: string[] = [source];
      distances.set(source, 0);
      pathCounts.set(source, 1);
      
      while (queue.length > 0) {
        const current = queue.shift()!;
        const currentDist = distances.get(current)!;
        
        const neighbors = this.graph.edges.get(current) ?? new Set();
        for (const neighbor of neighbors) {
          if (!distances.has(neighbor)) {
            distances.set(neighbor, currentDist + 1);
            pathCounts.set(neighbor, 0);
            predecessors.set(neighbor, []);
            queue.push(neighbor);
          }
          
          if (distances.get(neighbor) === currentDist + 1) {
            pathCounts.set(neighbor, (pathCounts.get(neighbor) ?? 0) + (pathCounts.get(current) ?? 0));
            predecessors.get(neighbor)!.push(current);
          }
        }
      }
      
      // Accumulate betweenness
      const delta = new Map<string, number>();
      for (const id of this.graph.nodes) {
        delta.set(id, 0);
      }
      
      const sorted = Array.from(distances.entries())
        .sort((a, b) => b[1] - a[1])
        .map(([id]) => id);
      
      for (const w of sorted) {
        const preds = predecessors.get(w) ?? [];
        for (const v of preds) {
          const contribution = ((pathCounts.get(v) ?? 0) / (pathCounts.get(w) ?? 1)) * (1 + (delta.get(w) ?? 0));
          delta.set(v, (delta.get(v) ?? 0) + contribution);
        }
        
        if (w !== source) {
          this.scores.betweenness.set(w, 
            (this.scores.betweenness.get(w) ?? 0) + (delta.get(w) ?? 0)
          );
        }
      }
    }
    
    // Normalize
    const n = this.graph.nodes.size;
    if (n > 2) {
      const factor = 1 / ((n - 1) * (n - 2));
      for (const [id, score] of this.scores.betweenness) {
        this.scores.betweenness.set(id, score * factor);
      }
    }
  }
  
  private computePageRank(damping: number = 0.85, iterations: number = 100): void {
    const n = this.graph.nodes.size;
    const initialRank = 1 / n;
    
    // Initialize ranks
    for (const id of this.graph.nodes) {
      this.scores.pageRank.set(id, initialRank);
    }
    
    // Iterate
    for (let iter = 0; iter < iterations; iter++) {
      const newRanks = new Map<string, number>();
      
      for (const id of this.graph.nodes) {
        let rank = (1 - damping) / n;
        
        const incomingNodes = this.graph.reverseEdges.get(id) ?? new Set();
        for (const source of incomingNodes) {
          const sourceRank = this.scores.pageRank.get(source) ?? 0;
          const sourceOutDegree = this.graph.edges.get(source)?.size ?? 1;
          rank += damping * (sourceRank / sourceOutDegree);
        }
        
        newRanks.set(id, rank);
      }
      
      // Update ranks
      for (const [id, rank] of newRanks) {
        this.scores.pageRank.set(id, rank);
      }
    }
  }
  
  private computeCombinedScore(): void {
    // Normalize each score type to [0, 1]
    const maxDegree = Math.max(...this.scores.degree.values(), 1);
    const maxBetweenness = Math.max(...this.scores.betweenness.values(), 1);
    const maxPageRank = Math.max(...this.scores.pageRank.values(), 1);
    
    for (const id of this.graph.nodes) {
      const degree = (this.scores.degree.get(id) ?? 0) / maxDegree;
      const betweenness = (this.scores.betweenness.get(id) ?? 0) / maxBetweenness;
      const pageRank = (this.scores.pageRank.get(id) ?? 0) / maxPageRank;
      
      // Weighted combination
      const combined = 0.3 * degree + 0.4 * betweenness + 0.3 * pageRank;
      this.scores.combined.set(id, combined);
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: WORK ITEM SELECTOR
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Selection criteria weights
 */
export interface SelectionWeights {
  frontierPressure: number;
  dependencyCentrality: number;
  priority: number;
  resourceAvailability: number;
  deadline: number;
}

/**
 * Selection result
 */
export interface SelectionResult {
  selected: WorkItem | null;
  score: number;
  rationale: string[];
  alternatives: { item: WorkItem; score: number }[];
  timestamp: number;
}

/**
 * Deterministic work item selector
 */
export class WorkItemSelector {
  private pressureCalculator: FrontierPressureCalculator;
  private centralityCalculator: DependencyCentralityCalculator;
  private weights: SelectionWeights;
  private availableResources: ResourceBudget;
  
  constructor(weights?: Partial<SelectionWeights>) {
    this.pressureCalculator = new FrontierPressureCalculator();
    this.centralityCalculator = new DependencyCentralityCalculator();
    
    this.weights = {
      frontierPressure: 0.35,
      dependencyCentrality: 0.25,
      priority: 0.20,
      resourceAvailability: 0.10,
      deadline: 0.10,
      ...weights
    };
    
    this.availableResources = {
      computation: 1000000,
      memory: 1024 * 1024 * 1024,
      time: 3600000,
      depth: 100
    };
  }
  
  /**
   * Add work item
   */
  addWorkItem(item: WorkItem): void {
    this.pressureCalculator.addItem(item);
    this.centralityCalculator.addNode(item.id);
    
    for (const dep of item.dependencies) {
      this.centralityCalculator.addEdge(dep, item.id);
    }
  }
  
  /**
   * Update work item status
   */
  updateStatus(itemId: string, status: WorkStatus): void {
    this.pressureCalculator.updateStatus(itemId, status);
  }
  
  /**
   * Set available resources
   */
  setAvailableResources(resources: ResourceBudget): void {
    this.availableResources = resources;
  }
  
  /**
   * Select next work item DETERMINISTICALLY
   */
  selectNext(): SelectionResult {
    // Compute all metrics
    this.pressureCalculator.computeAllPressures();
    this.centralityCalculator.computeAll();
    
    // Get pending items
    const candidates = this.pressureCalculator.getByPressure();
    
    if (candidates.length === 0) {
      return {
        selected: null,
        score: 0,
        rationale: ["No pending work items"],
        alternatives: [],
        timestamp: Date.now()
      };
    }
    
    // Score each candidate
    const scored: { item: WorkItem; score: number; reasons: string[] }[] = [];
    
    for (const item of candidates) {
      const { score, reasons } = this.computeScore(item);
      scored.push({ item, score, reasons });
    }
    
    // Sort by score (deterministic - use item ID as tiebreaker)
    scored.sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score;
      return a.item.id.localeCompare(b.item.id);
    });
    
    const best = scored[0];
    
    return {
      selected: best.item,
      score: best.score,
      rationale: best.reasons,
      alternatives: scored.slice(1, 5).map(s => ({ item: s.item, score: s.score })),
      timestamp: Date.now()
    };
  }
  
  private computeScore(item: WorkItem): { score: number; reasons: string[] } {
    const reasons: string[] = [];
    let score = 0;
    
    // Frontier pressure component
    const pressureScore = item.frontierPressure / 200;  // Normalize to ~[0,1]
    score += this.weights.frontierPressure * pressureScore;
    reasons.push(`Frontier pressure: ${pressureScore.toFixed(3)}`);
    
    // Centrality component
    const centrality = this.centralityCalculator.getCentrality(item.id);
    score += this.weights.dependencyCentrality * centrality;
    reasons.push(`Centrality: ${centrality.toFixed(3)}`);
    
    // Priority component
    const priorityScore = (6 - item.priority) / 5;  // Normalize to [0,1]
    score += this.weights.priority * priorityScore;
    reasons.push(`Priority: ${priorityScore.toFixed(3)}`);
    
    // Resource availability component
    const resourceScore = this.checkResourceFit(item);
    score += this.weights.resourceAvailability * resourceScore;
    reasons.push(`Resource fit: ${resourceScore.toFixed(3)}`);
    
    // Deadline component
    if (item.deadline) {
      const now = Date.now();
      const hoursToDeadline = (item.deadline - now) / (1000 * 60 * 60);
      const deadlineScore = hoursToDeadline < 0 ? 1 : 
                            hoursToDeadline < 24 ? 0.5 + (24 - hoursToDeadline) / 48 :
                            0.5 * Math.exp(-hoursToDeadline / 168);  // Decay over a week
      score += this.weights.deadline * deadlineScore;
      reasons.push(`Deadline urgency: ${deadlineScore.toFixed(3)}`);
    }
    
    return { score, reasons };
  }
  
  private checkResourceFit(item: WorkItem): number {
    const req = item.resources;
    
    // Check if resources are available
    const computeRatio = Math.min(1, this.availableResources.computation / req.minComputation);
    const memoryRatio = Math.min(1, this.availableResources.memory / req.minMemory);
    const timeRatio = Math.min(1, this.availableResources.time / req.minTime);
    
    // Items that fit well score higher
    const fitScore = (computeRatio + memoryRatio + timeRatio) / 3;
    
    // Penalize items that can't fit at all
    if (computeRatio < 0.5 || memoryRatio < 0.5 || timeRatio < 0.5) {
      return fitScore * 0.5;
    }
    
    return fitScore;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: NEGATIFY SHADOW PROBES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Negatify probe: Tests for failure cases and safety bypasses
 */
export interface NegatifyProbe {
  id: string;
  name: string;
  
  /** Target system/module */
  target: string;
  
  /** Probe type */
  type: "failure" | "boundary" | "bypass" | "corruption";
  
  /** Test function */
  test: (context: ProbeContext) => ProbeResult;
  
  /** Severity if probe triggers */
  severity: "info" | "warning" | "error" | "critical";
  
  /** Guard to install on failure */
  guard?: string;
}

export interface ProbeContext {
  workItem?: WorkItem;
  inputs: unknown[];
  corridor: WorkCorridor;
  trace: string[];
}

export interface ProbeResult {
  triggered: boolean;
  findings: ProbeFinding[];
  guardInstalled: boolean;
  timestamp: number;
}

export interface ProbeFinding {
  type: string;
  description: string;
  evidence: unknown;
  location: string;
}

/**
 * Negatify shadow system
 */
export class NegatifyShadow {
  private probes: Map<string, NegatifyProbe> = new Map();
  private findings: ProbeFinding[] = [];
  private guardsInstalled: Set<string> = new Set();
  
  /**
   * Register probe
   */
  registerProbe(probe: NegatifyProbe): void {
    this.probes.set(probe.id, probe);
  }
  
  /**
   * Run all probes against a context
   */
  runProbes(context: ProbeContext): NegatifyReport {
    const results: Map<string, ProbeResult> = new Map();
    
    for (const [id, probe] of this.probes) {
      const result = probe.test(context);
      results.set(id, result);
      
      if (result.triggered) {
        this.findings.push(...result.findings);
        
        // Install guard if specified
        if (probe.guard && !this.guardsInstalled.has(probe.guard)) {
          this.guardsInstalled.add(probe.guard);
          result.guardInstalled = true;
        }
      }
    }
    
    return {
      probesRun: this.probes.size,
      triggered: Array.from(results.values()).filter(r => r.triggered).length,
      findings: this.findings.slice(-100),  // Last 100 findings
      guardsInstalled: Array.from(this.guardsInstalled),
      timestamp: Date.now()
    };
  }
  
  /**
   * Create standard probes
   */
  createStandardProbes(): void {
    // Bypass detection probe
    this.registerProbe({
      id: "bypass_detector",
      name: "Safety Bypass Detector",
      target: "corridor",
      type: "bypass",
      test: (ctx) => {
        const findings: ProbeFinding[] = [];
        
        // Check for missing guards
        if (ctx.corridor.guards.length === 0) {
          findings.push({
            type: "missing_guards",
            description: "No corridor guards defined",
            evidence: ctx.corridor,
            location: "corridor"
          });
        }
        
        // Check for excessive budgets
        if (ctx.corridor.budgets.computation > 1e12) {
          findings.push({
            type: "excessive_budget",
            description: "Computation budget exceeds safe limits",
            evidence: ctx.corridor.budgets.computation,
            location: "corridor.budgets.computation"
          });
        }
        
        return {
          triggered: findings.length > 0,
          findings,
          guardInstalled: false,
          timestamp: Date.now()
        };
      },
      severity: "critical",
      guard: "enforce_corridor_guards"
    });
    
    // Boundary probe
    this.registerProbe({
      id: "boundary_probe",
      name: "Boundary Condition Probe",
      target: "inputs",
      type: "boundary",
      test: (ctx) => {
        const findings: ProbeFinding[] = [];
        
        for (let i = 0; i < ctx.inputs.length; i++) {
          const input = ctx.inputs[i];
          
          // Check for null/undefined
          if (input === null || input === undefined) {
            findings.push({
              type: "null_input",
              description: `Input ${i} is null or undefined`,
              evidence: input,
              location: `inputs[${i}]`
            });
          }
          
          // Check for empty arrays
          if (Array.isArray(input) && input.length === 0) {
            findings.push({
              type: "empty_array",
              description: `Input ${i} is empty array`,
              evidence: input,
              location: `inputs[${i}]`
            });
          }
        }
        
        return {
          triggered: findings.length > 0,
          findings,
          guardInstalled: false,
          timestamp: Date.now()
        };
      },
      severity: "warning"
    });
    
    // Failure mode probe
    this.registerProbe({
      id: "failure_mode",
      name: "Failure Mode Probe",
      target: "workItem",
      type: "failure",
      test: (ctx) => {
        const findings: ProbeFinding[] = [];
        
        if (ctx.workItem) {
          // Check for circular dependencies
          const visited = new Set<string>();
          const checkCycle = (id: string, path: string[]): boolean => {
            if (path.includes(id)) return true;
            if (visited.has(id)) return false;
            visited.add(id);
            return false;
          };
          
          if (checkCycle(ctx.workItem.id, ctx.workItem.dependencies)) {
            findings.push({
              type: "circular_dependency",
              description: "Circular dependency detected",
              evidence: ctx.workItem.dependencies,
              location: "workItem.dependencies"
            });
          }
          
          // Check for unresolved blockers
          const unresolvedBlockers = ctx.workItem.blockers.filter(b => !b.resolved);
          if (unresolvedBlockers.length > 0 && ctx.workItem.status !== WorkStatus.Blocked) {
            findings.push({
              type: "unresolved_blockers",
              description: "Work item has unresolved blockers but is not blocked",
              evidence: unresolvedBlockers,
              location: "workItem.blockers"
            });
          }
        }
        
        return {
          triggered: findings.length > 0,
          findings,
          guardInstalled: false,
          timestamp: Date.now()
        };
      },
      severity: "error"
    });
  }
  
  /**
   * Get all findings
   */
  getFindings(): ProbeFinding[] {
    return [...this.findings];
  }
  
  /**
   * Clear findings
   */
  clearFindings(): void {
    this.findings = [];
  }
}

export interface NegatifyReport {
  probesRun: number;
  triggered: number;
  findings: ProbeFinding[];
  guardsInstalled: string[];
  timestamp: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: AUTONOMY ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete Autonomy Work Selection Engine
 */
export class AutonomyWorkSelectionEngine {
  private selector: WorkItemSelector;
  private negatify: NegatifyShadow;
  private workItems: Map<string, WorkItem> = new Map();
  private executionLog: ExecutionLogEntry[] = [];
  
  constructor() {
    this.selector = new WorkItemSelector();
    this.negatify = new NegatifyShadow();
    this.negatify.createStandardProbes();
  }
  
  /**
   * Add work item
   */
  addWorkItem(item: WorkItem): void {
    this.workItems.set(item.id, item);
    this.selector.addWorkItem(item);
  }
  
  /**
   * Create work item
   */
  createWorkItem(
    type: WorkItemType,
    description: string,
    options?: Partial<WorkItem>
  ): WorkItem {
    const id = `work_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    const now = Date.now();
    
    const item: WorkItem = {
      id,
      type,
      description,
      status: WorkStatus.Pending,
      priority: WorkPriority.Normal,
      dependencies: [],
      blockers: [],
      corridor: {
        guards: ["default_guard"],
        budgets: { computation: 100000, memory: 1024 * 1024 * 100, time: 60000, depth: 50 },
        maxDepth: 50,
        timeout: 60000
      },
      resources: {
        minComputation: 1000,
        minMemory: 1024 * 1024,
        minTime: 1000,
        preferredLevel: 16
      },
      frontierPressure: 0,
      dependencyCentrality: 0,
      priorityScore: 0,
      created: now,
      updated: now,
      certified: false,
      ...options
    };
    
    this.addWorkItem(item);
    return item;
  }
  
  /**
   * Select and execute next work item
   */
  selectNext(): SelectionResult {
    // Run Negatify probes first
    const probeContext: ProbeContext = {
      inputs: [],
      corridor: {
        guards: ["autonomy_guard"],
        budgets: { computation: 1000000, memory: 1024 * 1024 * 1024, time: 3600000, depth: 100 },
        maxDepth: 100,
        timeout: 3600000
      },
      trace: []
    };
    
    const negatifyReport = this.negatify.runProbes(probeContext);
    
    // Check for critical findings
    const criticalFindings = negatifyReport.findings.filter(f => 
      f.type === "missing_guards" || f.type === "excessive_budget"
    );
    
    if (criticalFindings.length > 0) {
      return {
        selected: null,
        score: 0,
        rationale: ["Critical safety findings detected", ...criticalFindings.map(f => f.description)],
        alternatives: [],
        timestamp: Date.now()
      };
    }
    
    // Select next work item
    const result = this.selector.selectNext();
    
    // Log selection
    if (result.selected) {
      this.executionLog.push({
        workItemId: result.selected.id,
        action: "selected",
        score: result.score,
        rationale: result.rationale,
        timestamp: Date.now()
      });
    }
    
    return result;
  }
  
  /**
   * Mark work item as completed
   */
  completeWorkItem(itemId: string, outputAddress: string): void {
    const item = this.workItems.get(itemId);
    if (item) {
      item.status = WorkStatus.Completed;
      item.outputAddress = outputAddress;
      item.updated = Date.now();
      this.selector.updateStatus(itemId, WorkStatus.Completed);
      
      this.executionLog.push({
        workItemId: itemId,
        action: "completed",
        score: 0,
        rationale: [`Output: ${outputAddress}`],
        timestamp: Date.now()
      });
    }
  }
  
  /**
   * Mark work item as failed
   */
  failWorkItem(itemId: string, reason: string): void {
    const item = this.workItems.get(itemId);
    if (item) {
      item.status = WorkStatus.Failed;
      item.updated = Date.now();
      this.selector.updateStatus(itemId, WorkStatus.Failed);
      
      this.executionLog.push({
        workItemId: itemId,
        action: "failed",
        score: 0,
        rationale: [reason],
        timestamp: Date.now()
      });
    }
  }
  
  /**
   * Get execution log
   */
  getExecutionLog(): ExecutionLogEntry[] {
    return [...this.executionLog];
  }
  
  /**
   * Get work item
   */
  getWorkItem(id: string): WorkItem | undefined {
    return this.workItems.get(id);
  }
  
  /**
   * Get all work items
   */
  getAllWorkItems(): WorkItem[] {
    return Array.from(this.workItems.values());
  }
  
  /**
   * Get statistics
   */
  getStats(): AutonomyStats {
    const items = Array.from(this.workItems.values());
    
    return {
      totalItems: items.length,
      pending: items.filter(i => i.status === WorkStatus.Pending).length,
      inProgress: items.filter(i => i.status === WorkStatus.InProgress).length,
      completed: items.filter(i => i.status === WorkStatus.Completed).length,
      failed: items.filter(i => i.status === WorkStatus.Failed).length,
      blocked: items.filter(i => i.status === WorkStatus.Blocked).length,
      certified: items.filter(i => i.certified).length,
      avgFrontierPressure: items.reduce((sum, i) => sum + i.frontierPressure, 0) / items.length || 0,
      avgCentrality: items.reduce((sum, i) => sum + i.dependencyCentrality, 0) / items.length || 0,
      executionLogSize: this.executionLog.length
    };
  }
}

export interface ExecutionLogEntry {
  workItemId: string;
  action: string;
  score: number;
  rationale: string[];
  timestamp: number;
}

export interface AutonomyStats {
  totalItems: number;
  pending: number;
  inProgress: number;
  completed: number;
  failed: number;
  blocked: number;
  certified: number;
  avgFrontierPressure: number;
  avgCentrality: number;
  executionLogSize: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Enums
  WorkStatus,
  WorkPriority,
  WorkItemType,
  
  // Frontier
  computeFrontierPressure,
  FrontierPressureCalculator,
  
  // Centrality
  DependencyCentralityCalculator,
  
  // Selection
  WorkItemSelector,
  
  // Negatify
  NegatifyShadow,
  
  // Engine
  AutonomyWorkSelectionEngine
};
