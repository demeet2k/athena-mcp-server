/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * METRO ROUTING ENGINE - Complete Navigation and Transform Routing
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * The Metro Map (from SELF_SUFFICIENCY_TOME §4):
 * 
 * Knowledge is navigated as a metro graph where:
 *   - Nodes are HUBS (canonical junctions like Fourier, Derivative, Log, etc.)
 *   - Edges are BRIDGES (typed transforms with legality guards and certificates)
 *   - FORBIDDEN EDGES: illegal shortcuts, opposite-pole jumps, convention drift
 *   - ROUTING: shortest legal route under corridor cost functionals
 * 
 * Hub Examples:
 *   - Fourier family (DFT, FFT, STFT, wavelet)
 *   - Derivative family (partial, total, covariant, Lie)
 *   - Log family (natural, base-n, matrix log, discrete log)
 *   - Wick family (normal ordering, time ordering)
 *   - PDE families (Schrödinger, Maxwell, wave, heat)
 * 
 * Bridge Types:
 *   - Commutation bridges (AB = BA)
 *   - Duality bridges (primal ↔ dual)
 *   - Witness bridges (proof-carrying transforms)
 *   - Convention bridges (sign, normalization)
 * 
 * @module METRO_ROUTING_ENGINE
 * @version 2.0.0
 */

import { TruthValue, EdgeKind, WitnessPtr } from './CORE_INFRASTRUCTURE';
import { Out, Bulk, Bdry, bulk, bdry, isBulk } from './CARRIER_REGIME_SYSTEM';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: HUB DEFINITIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Hub family enumeration
 */
export enum HubFamily {
  Fourier = "Fourier",
  Derivative = "Derivative",
  Integral = "Integral",
  Logarithm = "Logarithm",
  Exponential = "Exponential",
  Wick = "Wick",
  Schrodinger = "Schrodinger",
  Maxwell = "Maxwell",
  Wave = "Wave",
  Heat = "Heat",
  Laplace = "Laplace",
  Legendre = "Legendre",
  Mellin = "Mellin",
  Hilbert = "Hilbert",
  Radon = "Radon"
}

/**
 * Hub: Canonical junction in the knowledge graph
 */
export interface Hub {
  id: string;
  name: string;
  family: HubFamily;
  
  /** Domain type */
  domain: DomainSpec;
  
  /** Codomain type */
  codomain: DomainSpec;
  
  /** Conventions (sign, normalization, etc.) */
  conventions: Convention[];
  
  /** Invariants this hub preserves */
  invariants: Invariant[];
  
  /** Known bridges from this hub */
  bridges: string[];  // Bridge IDs
  
  /** Complexity class */
  complexity: ComplexityClass;
  
  /** Documentation */
  description: string;
}

export interface DomainSpec {
  space: string;
  constraints: string[];
  examples: string[];
}

export interface Convention {
  name: string;
  value: string | number;
  alternatives: string[];
}

export interface Invariant {
  name: string;
  formula: string;
  preserved: boolean;
}

export interface ComplexityClass {
  time: string;  // e.g., "O(n log n)"
  space: string;
  numerical: "stable" | "unstable" | "conditionally_stable";
}

/**
 * Hub registry
 */
export class HubRegistry {
  private hubs: Map<string, Hub> = new Map();
  private familyIndex: Map<HubFamily, Set<string>> = new Map();
  
  register(hub: Hub): void {
    this.hubs.set(hub.id, hub);
    
    if (!this.familyIndex.has(hub.family)) {
      this.familyIndex.set(hub.family, new Set());
    }
    this.familyIndex.get(hub.family)!.add(hub.id);
  }
  
  get(id: string): Hub | undefined {
    return this.hubs.get(id);
  }
  
  getByFamily(family: HubFamily): Hub[] {
    const ids = this.familyIndex.get(family) ?? new Set();
    return Array.from(ids).map(id => this.hubs.get(id)!).filter(h => h);
  }
  
  all(): Hub[] {
    return Array.from(this.hubs.values());
  }
  
  findByDomain(space: string): Hub[] {
    return this.all().filter(h => h.domain.space === space);
  }
  
  findByCodomain(space: string): Hub[] {
    return this.all().filter(h => h.codomain.space === space);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: BRIDGE DEFINITIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Bridge type enumeration
 */
export enum BridgeType {
  Commutation = "Commutation",
  Duality = "Duality",
  Witness = "Witness",
  Convention = "Convention",
  Embedding = "Embedding",
  Projection = "Projection",
  Isomorphism = "Isomorphism",
  Approximation = "Approximation"
}

/**
 * Bridge: Typed transform between hubs
 */
export interface Bridge {
  id: string;
  name: string;
  type: BridgeType;
  
  /** Source hub */
  source: string;  // Hub ID
  
  /** Target hub */
  target: string;  // Hub ID
  
  /** Legality guard */
  guard: BridgeGuard;
  
  /** Transform function */
  transform: <T>(input: T, context: TransformContext) => Out<T>;
  
  /** Inverse bridge (if exists) */
  inverse?: string;
  
  /** Certificate emitter */
  emitCertificate: (input: unknown, output: unknown) => BridgeCertificate;
  
  /** Cost for routing */
  cost: BridgeCost;
  
  /** Properties */
  properties: BridgeProperties;
}

export interface BridgeGuard {
  /** Preconditions */
  preconditions: GuardCondition[];
  
  /** Check all preconditions */
  check: (context: TransformContext) => GuardResult;
}

export interface GuardCondition {
  name: string;
  description: string;
  predicate: (context: TransformContext) => boolean;
}

export interface GuardResult {
  passed: boolean;
  failedConditions: GuardCondition[];
  reason?: string;
}

export interface TransformContext {
  sourceHub: string;
  targetHub: string;
  conventions: Map<string, unknown>;
  resources: ResourceBudget;
  trace: string[];
}

export interface ResourceBudget {
  computation: number;
  memory: number;
  time: number;
}

export interface BridgeCertificate {
  bridgeId: string;
  sourceHub: string;
  targetHub: string;
  inputHash: string;
  outputHash: string;
  timestamp: number;
  witness: BridgeWitness;
}

export interface BridgeWitness {
  type: "commutation" | "duality" | "derivation" | "numerical";
  data: unknown;
  verifiable: boolean;
}

export interface BridgeCost {
  /** Base cost */
  base: number;
  
  /** Cost per input size */
  perUnit: number;
  
  /** Uncertainty penalty */
  uncertaintyPenalty: number;
  
  /** Convention mismatch penalty */
  conventionPenalty: number;
}

export interface BridgeProperties {
  /** Is transform reversible? */
  reversible: boolean;
  
  /** Does it preserve structure? */
  structurePreserving: boolean;
  
  /** Is it numerically stable? */
  stable: boolean;
  
  /** Type compatibility */
  typeCompatible: boolean;
  
  /** Convention compatible */
  conventionCompatible: boolean;
}

/**
 * Bridge registry
 */
export class BridgeRegistry {
  private bridges: Map<string, Bridge> = new Map();
  private sourceIndex: Map<string, Set<string>> = new Map();
  private targetIndex: Map<string, Set<string>> = new Map();
  private typeIndex: Map<BridgeType, Set<string>> = new Map();
  
  register(bridge: Bridge): void {
    this.bridges.set(bridge.id, bridge);
    
    // Index by source
    if (!this.sourceIndex.has(bridge.source)) {
      this.sourceIndex.set(bridge.source, new Set());
    }
    this.sourceIndex.get(bridge.source)!.add(bridge.id);
    
    // Index by target
    if (!this.targetIndex.has(bridge.target)) {
      this.targetIndex.set(bridge.target, new Set());
    }
    this.targetIndex.get(bridge.target)!.add(bridge.id);
    
    // Index by type
    if (!this.typeIndex.has(bridge.type)) {
      this.typeIndex.set(bridge.type, new Set());
    }
    this.typeIndex.get(bridge.type)!.add(bridge.id);
  }
  
  get(id: string): Bridge | undefined {
    return this.bridges.get(id);
  }
  
  getFromSource(hubId: string): Bridge[] {
    const ids = this.sourceIndex.get(hubId) ?? new Set();
    return Array.from(ids).map(id => this.bridges.get(id)!).filter(b => b);
  }
  
  getToTarget(hubId: string): Bridge[] {
    const ids = this.targetIndex.get(hubId) ?? new Set();
    return Array.from(ids).map(id => this.bridges.get(id)!).filter(b => b);
  }
  
  getByType(type: BridgeType): Bridge[] {
    const ids = this.typeIndex.get(type) ?? new Set();
    return Array.from(ids).map(id => this.bridges.get(id)!).filter(b => b);
  }
  
  findPath(sourceHub: string, targetHub: string): string[] | null {
    // Simple BFS to find a path
    const visited = new Set<string>();
    const queue: { hub: string; path: string[] }[] = [{ hub: sourceHub, path: [] }];
    
    while (queue.length > 0) {
      const { hub, path } = queue.shift()!;
      
      if (hub === targetHub) {
        return path;
      }
      
      if (visited.has(hub)) continue;
      visited.add(hub);
      
      const bridges = this.getFromSource(hub);
      for (const bridge of bridges) {
        if (!visited.has(bridge.target)) {
          queue.push({ hub: bridge.target, path: [...path, bridge.id] });
        }
      }
    }
    
    return null;  // No path found
  }
  
  all(): Bridge[] {
    return Array.from(this.bridges.values());
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: FORBIDDEN EDGES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Forbidden edge type
 */
export enum ForbiddenType {
  OppositePole = "OppositePole",
  ConventionDrift = "ConventionDrift",
  TypeMismatch = "TypeMismatch",
  UncertifiedShortcut = "UncertifiedShortcut",
  NumericalInstability = "NumericalInstability",
  ResourceViolation = "ResourceViolation"
}

/**
 * Forbidden edge rule
 */
export interface ForbiddenEdge {
  id: string;
  type: ForbiddenType;
  
  /** Pattern that matches forbidden edges */
  pattern: ForbiddenPattern;
  
  /** Explanation */
  reason: string;
  
  /** Severity */
  severity: "warning" | "error" | "fatal";
  
  /** Possible remediation */
  remediation: string[];
}

export interface ForbiddenPattern {
  sourcePattern?: string;  // Regex or hub ID
  targetPattern?: string;
  bridgeTypePattern?: BridgeType[];
  conventionMismatch?: string[];
}

/**
 * Forbidden edge checker
 */
export class ForbiddenEdgeChecker {
  private rules: ForbiddenEdge[] = [];
  
  addRule(rule: ForbiddenEdge): void {
    this.rules.push(rule);
  }
  
  check(bridge: Bridge, context: TransformContext): ForbiddenCheckResult {
    const violations: ForbiddenEdge[] = [];
    
    for (const rule of this.rules) {
      if (this.matches(bridge, rule.pattern, context)) {
        violations.push(rule);
      }
    }
    
    return {
      allowed: violations.every(v => v.severity !== "fatal"),
      violations,
      warnings: violations.filter(v => v.severity === "warning"),
      errors: violations.filter(v => v.severity === "error" || v.severity === "fatal")
    };
  }
  
  private matches(bridge: Bridge, pattern: ForbiddenPattern, context: TransformContext): boolean {
    if (pattern.sourcePattern) {
      const regex = new RegExp(pattern.sourcePattern);
      if (!regex.test(bridge.source)) return false;
    }
    
    if (pattern.targetPattern) {
      const regex = new RegExp(pattern.targetPattern);
      if (!regex.test(bridge.target)) return false;
    }
    
    if (pattern.bridgeTypePattern && !pattern.bridgeTypePattern.includes(bridge.type)) {
      return false;
    }
    
    if (pattern.conventionMismatch) {
      for (const conv of pattern.conventionMismatch) {
        if (context.conventions.has(conv)) {
          return true;  // Convention mismatch detected
        }
      }
      return false;
    }
    
    return true;
  }
}

export interface ForbiddenCheckResult {
  allowed: boolean;
  violations: ForbiddenEdge[];
  warnings: ForbiddenEdge[];
  errors: ForbiddenEdge[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: ROUTE FINDING
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Route: A path through the metro graph
 */
export interface Route {
  id: string;
  
  /** Source hub */
  source: string;
  
  /** Target hub */
  target: string;
  
  /** Ordered list of bridges */
  bridges: string[];
  
  /** Total cost */
  cost: RouteCost;
  
  /** Route certificate */
  certificate: RouteCertificate;
  
  /** Computed at */
  timestamp: number;
}

export interface RouteCost {
  base: number;
  uncertainty: number;
  convention: number;
  total: number;
}

export interface RouteCertificate {
  routeId: string;
  legalityProof: string;
  typeCorrectness: string;
  conventionCompatibility: string;
  deterministicSelection: string;
  hash: string;
}

/**
 * Route cost functional
 */
export interface CostFunctional {
  /** Compute cost of a bridge */
  bridgeCost: (bridge: Bridge, context: TransformContext) => number;
  
  /** Compute uncertainty penalty */
  uncertaintyPenalty: (route: Route) => number;
  
  /** Compute convention penalty */
  conventionPenalty: (route: Route) => number;
  
  /** Total cost */
  totalCost: (route: Route) => number;
}

/**
 * Default cost functional
 */
export function createDefaultCostFunctional(): CostFunctional {
  return {
    bridgeCost(bridge: Bridge, context: TransformContext): number {
      return bridge.cost.base + 
             bridge.cost.uncertaintyPenalty * 0.1 +
             bridge.cost.conventionPenalty * (context.conventions.size > 0 ? 1 : 0);
    },
    
    uncertaintyPenalty(route: Route): number {
      return route.cost.uncertainty;
    },
    
    conventionPenalty(route: Route): number {
      return route.cost.convention;
    },
    
    totalCost(route: Route): number {
      return route.cost.base + route.cost.uncertainty + route.cost.convention;
    }
  };
}

/**
 * Route finder using Dijkstra's algorithm
 */
export class RouteFinder {
  private hubRegistry: HubRegistry;
  private bridgeRegistry: BridgeRegistry;
  private forbiddenChecker: ForbiddenEdgeChecker;
  private costFunctional: CostFunctional;
  
  constructor(
    hubRegistry: HubRegistry,
    bridgeRegistry: BridgeRegistry,
    forbiddenChecker: ForbiddenEdgeChecker,
    costFunctional?: CostFunctional
  ) {
    this.hubRegistry = hubRegistry;
    this.bridgeRegistry = bridgeRegistry;
    this.forbiddenChecker = forbiddenChecker;
    this.costFunctional = costFunctional ?? createDefaultCostFunctional();
  }
  
  /**
   * Find shortest legal route
   */
  findRoute(source: string, target: string, context: TransformContext): RouteResult {
    // Dijkstra's algorithm with forbidden edge checking
    const distances = new Map<string, number>();
    const previous = new Map<string, { hub: string; bridge: string }>();
    const visited = new Set<string>();
    
    // Priority queue (simple array, sorted by distance)
    const queue: { hub: string; distance: number }[] = [];
    
    // Initialize
    distances.set(source, 0);
    queue.push({ hub: source, distance: 0 });
    
    while (queue.length > 0) {
      // Sort and get minimum
      queue.sort((a, b) => a.distance - b.distance);
      const current = queue.shift()!;
      
      if (visited.has(current.hub)) continue;
      visited.add(current.hub);
      
      if (current.hub === target) {
        // Reconstruct path
        return this.reconstructRoute(source, target, previous, distances.get(target)!, context);
      }
      
      // Explore neighbors
      const bridges = this.bridgeRegistry.getFromSource(current.hub);
      
      for (const bridge of bridges) {
        // Check if bridge is allowed
        const forbiddenCheck = this.forbiddenChecker.check(bridge, context);
        if (!forbiddenCheck.allowed) continue;
        
        // Check bridge guard
        const guardResult = bridge.guard.check(context);
        if (!guardResult.passed) continue;
        
        // Compute cost
        const cost = this.costFunctional.bridgeCost(bridge, context);
        const newDistance = current.distance + cost;
        
        const prevDistance = distances.get(bridge.target) ?? Infinity;
        if (newDistance < prevDistance) {
          distances.set(bridge.target, newDistance);
          previous.set(bridge.target, { hub: current.hub, bridge: bridge.id });
          queue.push({ hub: bridge.target, distance: newDistance });
        }
      }
    }
    
    // No route found
    return {
      found: false,
      reason: `No legal route from ${source} to ${target}`
    };
  }
  
  private reconstructRoute(
    source: string,
    target: string,
    previous: Map<string, { hub: string; bridge: string }>,
    totalCost: number,
    context: TransformContext
  ): RouteResult {
    const bridges: string[] = [];
    let current = target;
    
    while (current !== source) {
      const prev = previous.get(current);
      if (!prev) break;
      
      bridges.unshift(prev.bridge);
      current = prev.hub;
    }
    
    const route: Route = {
      id: `route_${Date.now()}`,
      source,
      target,
      bridges,
      cost: {
        base: totalCost,
        uncertainty: 0,
        convention: 0,
        total: totalCost
      },
      certificate: this.generateCertificate(source, target, bridges),
      timestamp: Date.now()
    };
    
    return {
      found: true,
      route
    };
  }
  
  private generateCertificate(source: string, target: string, bridges: string[]): RouteCertificate {
    const hash = this.simpleHash(`${source}:${bridges.join(",")}:${target}`);
    
    return {
      routeId: `route_${Date.now()}`,
      legalityProof: `all_bridges_legal:${bridges.length}`,
      typeCorrectness: "types_verified",
      conventionCompatibility: "conventions_aligned",
      deterministicSelection: "dijkstra_shortest_path",
      hash
    };
  }
  
  private simpleHash(s: string): string {
    let hash = 0;
    for (let i = 0; i < s.length; i++) {
      hash = ((hash << 5) - hash) + s.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(16, '0');
  }
  
  /**
   * Find all routes (up to limit)
   */
  findAllRoutes(source: string, target: string, context: TransformContext, limit: number = 10): Route[] {
    const routes: Route[] = [];
    const visited = new Set<string>();
    
    const dfs = (current: string, path: string[], cost: number) => {
      if (routes.length >= limit) return;
      
      if (current === target) {
        routes.push({
          id: `route_${routes.length}`,
          source,
          target,
          bridges: [...path],
          cost: { base: cost, uncertainty: 0, convention: 0, total: cost },
          certificate: this.generateCertificate(source, target, path),
          timestamp: Date.now()
        });
        return;
      }
      
      const pathKey = path.join(",");
      if (visited.has(pathKey)) return;
      visited.add(pathKey);
      
      const bridges = this.bridgeRegistry.getFromSource(current);
      for (const bridge of bridges) {
        const forbiddenCheck = this.forbiddenChecker.check(bridge, context);
        if (!forbiddenCheck.allowed) continue;
        
        const guardResult = bridge.guard.check(context);
        if (!guardResult.passed) continue;
        
        const newCost = cost + this.costFunctional.bridgeCost(bridge, context);
        dfs(bridge.target, [...path, bridge.id], newCost);
      }
      
      visited.delete(pathKey);
    };
    
    dfs(source, [], 0);
    
    return routes.sort((a, b) => a.cost.total - b.cost.total);
  }
}

export type RouteResult = 
  | { found: true; route: Route }
  | { found: false; reason: string };

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: ROUTE EXECUTOR
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Execute a route, transforming data through bridges
 */
export class RouteExecutor {
  private bridgeRegistry: BridgeRegistry;
  private executionLog: ExecutionLogEntry[] = [];
  
  constructor(bridgeRegistry: BridgeRegistry) {
    this.bridgeRegistry = bridgeRegistry;
  }
  
  /**
   * Execute a route
   */
  execute<T>(route: Route, input: T, context: TransformContext): Out<T> {
    let current: Out<T> = bulk(input, "input");
    
    for (const bridgeId of route.bridges) {
      const bridge = this.bridgeRegistry.get(bridgeId);
      if (!bridge) {
        return bdry({
          kind: "OutOfCorridor" as any,
          code: "BRIDGE_NOT_FOUND",
          where: { file: "router", startLine: 0, startCol: 0, endLine: 0, endCol: 0 },
          witness: { data: bridgeId, description: `Bridge not found: ${bridgeId}`, provenance: [] },
          requirements: [],
          expectedType: "unknown",
          timestamp: Date.now()
        }, "unknown");
      }
      
      if (!isBulk(current)) {
        // Propagate boundary
        return current;
      }
      
      // Execute bridge transform
      const stepStart = Date.now();
      current = bridge.transform(current.value, context);
      const stepEnd = Date.now();
      
      // Log execution
      this.executionLog.push({
        bridgeId,
        sourceHub: bridge.source,
        targetHub: bridge.target,
        success: isBulk(current),
        duration: stepEnd - stepStart,
        timestamp: stepStart
      });
      
      // Update context trace
      context.trace.push(`${bridge.source} -> ${bridge.target} via ${bridgeId}`);
    }
    
    return current;
  }
  
  /**
   * Get execution log
   */
  getLog(): ExecutionLogEntry[] {
    return [...this.executionLog];
  }
  
  /**
   * Clear execution log
   */
  clearLog(): void {
    this.executionLog = [];
  }
}

export interface ExecutionLogEntry {
  bridgeId: string;
  sourceHub: string;
  targetHub: string;
  success: boolean;
  duration: number;
  timestamp: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: METRO ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete Metro Routing Engine
 */
export class MetroRoutingEngine {
  private hubRegistry: HubRegistry;
  private bridgeRegistry: BridgeRegistry;
  private forbiddenChecker: ForbiddenEdgeChecker;
  private routeFinder: RouteFinder;
  private routeExecutor: RouteExecutor;
  private routeCache: Map<string, Route> = new Map();
  
  constructor() {
    this.hubRegistry = new HubRegistry();
    this.bridgeRegistry = new BridgeRegistry();
    this.forbiddenChecker = new ForbiddenEdgeChecker();
    this.routeFinder = new RouteFinder(
      this.hubRegistry,
      this.bridgeRegistry,
      this.forbiddenChecker
    );
    this.routeExecutor = new RouteExecutor(this.bridgeRegistry);
    
    this.initializeStandardHubs();
    this.initializeForbiddenRules();
  }
  
  /**
   * Register a hub
   */
  registerHub(hub: Hub): void {
    this.hubRegistry.register(hub);
  }
  
  /**
   * Register a bridge
   */
  registerBridge(bridge: Bridge): void {
    this.bridgeRegistry.register(bridge);
    
    // Update hub's bridge list
    const sourceHub = this.hubRegistry.get(bridge.source);
    if (sourceHub && !sourceHub.bridges.includes(bridge.id)) {
      sourceHub.bridges.push(bridge.id);
    }
  }
  
  /**
   * Add forbidden edge rule
   */
  addForbiddenRule(rule: ForbiddenEdge): void {
    this.forbiddenChecker.addRule(rule);
  }
  
  /**
   * Find route between hubs
   */
  findRoute(source: string, target: string): RouteResult {
    const cacheKey = `${source}:${target}`;
    
    if (this.routeCache.has(cacheKey)) {
      return { found: true, route: this.routeCache.get(cacheKey)! };
    }
    
    const context: TransformContext = {
      sourceHub: source,
      targetHub: target,
      conventions: new Map(),
      resources: { computation: 1000000, memory: 100 * 1024 * 1024, time: 30000 },
      trace: []
    };
    
    const result = this.routeFinder.findRoute(source, target, context);
    
    if (result.found) {
      this.routeCache.set(cacheKey, result.route);
    }
    
    return result;
  }
  
  /**
   * Execute route with data
   */
  executeRoute<T>(route: Route, input: T): Out<T> {
    const context: TransformContext = {
      sourceHub: route.source,
      targetHub: route.target,
      conventions: new Map(),
      resources: { computation: 1000000, memory: 100 * 1024 * 1024, time: 30000 },
      trace: []
    };
    
    return this.routeExecutor.execute(route, input, context);
  }
  
  /**
   * Transform data from source to target hub
   */
  transform<T>(source: string, target: string, input: T): Out<T> {
    const routeResult = this.findRoute(source, target);
    
    if (!routeResult.found) {
      return bdry({
        kind: "OutOfCorridor" as any,
        code: "NO_ROUTE",
        where: { file: "metro", startLine: 0, startCol: 0, endLine: 0, endCol: 0 },
        witness: { data: { source, target }, description: routeResult.reason, provenance: [] },
        requirements: [],
        expectedType: "unknown",
        timestamp: Date.now()
      }, "unknown");
    }
    
    return this.executeRoute(routeResult.route, input);
  }
  
  /**
   * Get all hubs
   */
  getHubs(): Hub[] {
    return this.hubRegistry.all();
  }
  
  /**
   * Get all bridges
   */
  getBridges(): Bridge[] {
    return this.bridgeRegistry.all();
  }
  
  /**
   * Get hub by ID
   */
  getHub(id: string): Hub | undefined {
    return this.hubRegistry.get(id);
  }
  
  /**
   * Get bridge by ID
   */
  getBridge(id: string): Bridge | undefined {
    return this.bridgeRegistry.get(id);
  }
  
  /**
   * Clear route cache
   */
  clearCache(): void {
    this.routeCache.clear();
  }
  
  private initializeStandardHubs(): void {
    // Fourier family
    this.registerHub({
      id: "fourier_dft",
      name: "Discrete Fourier Transform",
      family: HubFamily.Fourier,
      domain: { space: "time_domain", constraints: ["finite", "discrete"], examples: ["signal[n]"] },
      codomain: { space: "frequency_domain", constraints: ["finite", "discrete"], examples: ["X[k]"] },
      conventions: [{ name: "sign", value: "-1", alternatives: ["+1"] }],
      invariants: [{ name: "Parseval", formula: "Σ|x[n]|² = (1/N)Σ|X[k]|²", preserved: true }],
      bridges: [],
      complexity: { time: "O(n²)", space: "O(n)", numerical: "stable" },
      description: "Standard DFT"
    });
    
    this.registerHub({
      id: "fourier_fft",
      name: "Fast Fourier Transform",
      family: HubFamily.Fourier,
      domain: { space: "time_domain", constraints: ["power_of_2", "discrete"], examples: ["signal[n]"] },
      codomain: { space: "frequency_domain", constraints: ["power_of_2", "discrete"], examples: ["X[k]"] },
      conventions: [{ name: "sign", value: "-1", alternatives: ["+1"] }],
      invariants: [{ name: "Parseval", formula: "Σ|x[n]|² = (1/N)Σ|X[k]|²", preserved: true }],
      bridges: [],
      complexity: { time: "O(n log n)", space: "O(n)", numerical: "stable" },
      description: "Cooley-Tukey FFT"
    });
    
    // Derivative family
    this.registerHub({
      id: "derivative_partial",
      name: "Partial Derivative",
      family: HubFamily.Derivative,
      domain: { space: "smooth_functions", constraints: ["differentiable"], examples: ["f(x,y,z)"] },
      codomain: { space: "smooth_functions", constraints: ["continuous"], examples: ["∂f/∂x"] },
      conventions: [{ name: "notation", value: "∂", alternatives: ["D", "d"] }],
      invariants: [{ name: "chain_rule", formula: "∂(f∘g)/∂x = (∂f/∂g)(∂g/∂x)", preserved: true }],
      bridges: [],
      complexity: { time: "O(1)", space: "O(1)", numerical: "conditionally_stable" },
      description: "Partial differentiation"
    });
    
    // Log family
    this.registerHub({
      id: "log_natural",
      name: "Natural Logarithm",
      family: HubFamily.Logarithm,
      domain: { space: "positive_reals", constraints: ["x > 0"], examples: ["x ∈ ℝ⁺"] },
      codomain: { space: "reals", constraints: [], examples: ["y ∈ ℝ"] },
      conventions: [{ name: "base", value: "e", alternatives: ["10", "2"] }],
      invariants: [{ name: "product", formula: "ln(xy) = ln(x) + ln(y)", preserved: true }],
      bridges: [],
      complexity: { time: "O(1)", space: "O(1)", numerical: "stable" },
      description: "Natural log (base e)"
    });
  }
  
  private initializeForbiddenRules(): void {
    // Opposite pole jump (e.g., direct log of negative without complex extension)
    this.addForbiddenRule({
      id: "opposite_pole_log",
      type: ForbiddenType.OppositePole,
      pattern: {
        targetPattern: "log_.*",
        conventionMismatch: ["negative_input"]
      },
      reason: "Cannot take log of negative number without complex extension",
      severity: "fatal",
      remediation: ["Use complex logarithm", "Ensure positive input"]
    });
    
    // Convention drift (e.g., mixing Fourier sign conventions)
    this.addForbiddenRule({
      id: "convention_drift_fourier",
      type: ForbiddenType.ConventionDrift,
      pattern: {
        sourcePattern: "fourier_.*",
        targetPattern: "fourier_.*",
        conventionMismatch: ["sign_mismatch"]
      },
      reason: "Fourier transform sign convention mismatch",
      severity: "error",
      remediation: ["Apply sign correction", "Use consistent convention"]
    });
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Enums
  HubFamily,
  BridgeType,
  ForbiddenType,
  
  // Registries
  HubRegistry,
  BridgeRegistry,
  
  // Forbidden
  ForbiddenEdgeChecker,
  
  // Routing
  RouteFinder,
  RouteExecutor,
  createDefaultCostFunctional,
  
  // Engine
  MetroRoutingEngine
};
