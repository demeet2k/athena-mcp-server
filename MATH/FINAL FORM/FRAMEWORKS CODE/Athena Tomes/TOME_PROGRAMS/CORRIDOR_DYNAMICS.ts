/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * CORRIDOR DYNAMICS - Complete Budget Management and Flow Control
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Corridor = (Dom, Obs, Env, Budgets κβχε)
 * 
 * Budget Types:
 *   κ (kappa) - Computation budget (CPU cycles, operations)
 *   β (beta)  - Memory budget (bytes, allocations)
 *   χ (chi)   - Time budget (milliseconds, deadlines)
 *   ε (epsilon) - Error budget (fault tolerance)
 * 
 * Conservation Laws:
 *   κ_pre = κ_post + κ_spent + κ_leak
 *   Mass conservation: bulk + bdry + erasure + abstention = 1
 * 
 * Flow Control:
 *   - Admission control
 *   - Rate limiting
 *   - Backpressure
 *   - Circuit breaking
 * 
 * @module CORRIDOR_DYNAMICS
 * @version 2.0.0
 */

import { TruthValue, WitnessPtr } from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: BUDGET TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Budget type enumeration
 */
export enum BudgetType {
  Kappa = "κ",    // Computation
  Beta = "β",     // Memory
  Chi = "χ",      // Time
  Epsilon = "ε"  // Error
}

/**
 * Individual budget
 */
export interface Budget {
  type: BudgetType;
  allocated: number;
  used: number;
  reserved: number;
  available: number;
  unit: string;
  limits: BudgetLimits;
}

export interface BudgetLimits {
  min: number;
  max: number;
  softLimit: number;  // Warning threshold
  hardLimit: number;  // Absolute maximum
  burstAllowed: number;  // Temporary overage
}

/**
 * Budget allocation request
 */
export interface AllocationRequest {
  type: BudgetType;
  amount: number;
  priority: "low" | "normal" | "high" | "critical";
  requesterId: string;
  purpose: string;
  duration?: number;  // For time-based allocations
}

/**
 * Budget allocation result
 */
export interface AllocationResult {
  success: boolean;
  allocated: number;
  requestId: string;
  expiresAt?: number;
  reason?: string;
}

/**
 * Create budget with defaults
 */
export function createBudget(
  type: BudgetType,
  allocated: number,
  limits?: Partial<BudgetLimits>
): Budget {
  const defaultLimits: BudgetLimits = {
    min: 0,
    max: allocated * 2,
    softLimit: allocated * 0.8,
    hardLimit: allocated,
    burstAllowed: allocated * 0.1
  };
  
  return {
    type,
    allocated,
    used: 0,
    reserved: 0,
    available: allocated,
    unit: getBudgetUnit(type),
    limits: { ...defaultLimits, ...limits }
  };
}

function getBudgetUnit(type: BudgetType): string {
  switch (type) {
    case BudgetType.Kappa: return "ops";
    case BudgetType.Beta: return "bytes";
    case BudgetType.Chi: return "ms";
    case BudgetType.Epsilon: return "errors";
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: CORRIDOR STRUCTURE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Corridor: Execution context with budgets
 */
export interface Corridor {
  id: string;
  
  /** Domain: What operations are allowed */
  domain: Domain;
  
  /** Observable: What can be observed/measured */
  observable: Observable;
  
  /** Environment: External context */
  environment: Environment;
  
  /** Budgets */
  budgets: {
    kappa: Budget;
    beta: Budget;
    chi: Budget;
    epsilon: Budget;
  };
  
  /** State */
  state: CorridorState;
  
  /** Metrics */
  metrics: CorridorMetrics;
}

export interface Domain {
  allowedOperations: Set<string>;
  deniedOperations: Set<string>;
  maxDepth: number;
  maxBranching: number;
  constraints: DomainConstraint[];
}

export interface DomainConstraint {
  name: string;
  predicate: (op: string, context: unknown) => boolean;
  message: string;
}

export interface Observable {
  metrics: string[];
  events: string[];
  traces: boolean;
  sampling: number;  // 0 to 1
}

export interface Environment {
  variables: Map<string, unknown>;
  secrets: Set<string>;  // Keys that are secret
  readonly: Set<string>;  // Keys that cannot be modified
  timestamp: number;
}

export interface CorridorState {
  status: "active" | "suspended" | "exhausted" | "closed";
  activeSince: number;
  lastActivity: number;
  suspendCount: number;
  resumeCount: number;
}

export interface CorridorMetrics {
  totalAllocations: number;
  totalReleases: number;
  peakUsage: Map<BudgetType, number>;
  violations: BudgetViolation[];
}

export interface BudgetViolation {
  type: BudgetType;
  timestamp: number;
  attempted: number;
  available: number;
  severity: "warning" | "error" | "critical";
}

/**
 * Create corridor with default budgets
 */
export function createCorridor(
  id: string,
  budgetConfig: {
    kappa?: number;
    beta?: number;
    chi?: number;
    epsilon?: number;
  } = {}
): Corridor {
  return {
    id,
    domain: {
      allowedOperations: new Set(["read", "write", "compute"]),
      deniedOperations: new Set(),
      maxDepth: 100,
      maxBranching: 10,
      constraints: []
    },
    observable: {
      metrics: ["cpu", "memory", "time", "errors"],
      events: ["start", "end", "error", "suspend", "resume"],
      traces: true,
      sampling: 1.0
    },
    environment: {
      variables: new Map(),
      secrets: new Set(),
      readonly: new Set(),
      timestamp: Date.now()
    },
    budgets: {
      kappa: createBudget(BudgetType.Kappa, budgetConfig.kappa ?? 1000000),
      beta: createBudget(BudgetType.Beta, budgetConfig.beta ?? 100 * 1024 * 1024),
      chi: createBudget(BudgetType.Chi, budgetConfig.chi ?? 30000),
      epsilon: createBudget(BudgetType.Epsilon, budgetConfig.epsilon ?? 10)
    },
    state: {
      status: "active",
      activeSince: Date.now(),
      lastActivity: Date.now(),
      suspendCount: 0,
      resumeCount: 0
    },
    metrics: {
      totalAllocations: 0,
      totalReleases: 0,
      peakUsage: new Map(),
      violations: []
    }
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: BUDGET MANAGER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Budget manager for a corridor
 */
export class BudgetManager {
  private corridor: Corridor;
  private allocations: Map<string, { type: BudgetType; amount: number; expiresAt?: number }> = new Map();
  private allocationCounter: number = 0;
  
  constructor(corridor: Corridor) {
    this.corridor = corridor;
  }
  
  /**
   * Request budget allocation
   */
  allocate(request: AllocationRequest): AllocationResult {
    const budget = this.getBudget(request.type);
    const requestId = `alloc_${++this.allocationCounter}`;
    
    // Check if corridor is active
    if (this.corridor.state.status !== "active") {
      return {
        success: false,
        allocated: 0,
        requestId,
        reason: `Corridor is ${this.corridor.state.status}`
      };
    }
    
    // Check available budget
    const effectiveAvailable = budget.available + 
      (request.priority === "critical" ? budget.limits.burstAllowed : 0);
    
    if (request.amount > effectiveAvailable) {
      this.recordViolation(request.type, request.amount, budget.available);
      return {
        success: false,
        allocated: 0,
        requestId,
        reason: `Insufficient budget: requested ${request.amount}, available ${effectiveAvailable}`
      };
    }
    
    // Allocate
    budget.used += request.amount;
    budget.available -= request.amount;
    
    // Track allocation
    const expiresAt = request.duration ? Date.now() + request.duration : undefined;
    this.allocations.set(requestId, {
      type: request.type,
      amount: request.amount,
      expiresAt
    });
    
    // Update metrics
    this.corridor.metrics.totalAllocations++;
    this.updatePeakUsage(request.type, budget.used);
    this.corridor.state.lastActivity = Date.now();
    
    return {
      success: true,
      allocated: request.amount,
      requestId,
      expiresAt
    };
  }
  
  /**
   * Release allocated budget
   */
  release(requestId: string): boolean {
    const allocation = this.allocations.get(requestId);
    if (!allocation) return false;
    
    const budget = this.getBudget(allocation.type);
    budget.used -= allocation.amount;
    budget.available += allocation.amount;
    
    this.allocations.delete(requestId);
    this.corridor.metrics.totalReleases++;
    this.corridor.state.lastActivity = Date.now();
    
    return true;
  }
  
  /**
   * Reserve budget (without using)
   */
  reserve(type: BudgetType, amount: number): boolean {
    const budget = this.getBudget(type);
    
    if (amount > budget.available) return false;
    
    budget.reserved += amount;
    budget.available -= amount;
    
    return true;
  }
  
  /**
   * Commit reserved budget
   */
  commitReservation(type: BudgetType, amount: number): boolean {
    const budget = this.getBudget(type);
    
    if (amount > budget.reserved) return false;
    
    budget.reserved -= amount;
    budget.used += amount;
    
    return true;
  }
  
  /**
   * Release reserved budget
   */
  releaseReservation(type: BudgetType, amount: number): boolean {
    const budget = this.getBudget(type);
    
    if (amount > budget.reserved) return false;
    
    budget.reserved -= amount;
    budget.available += amount;
    
    return true;
  }
  
  /**
   * Check κ conservation: κ_pre = κ_post + κ_spent + κ_leak
   */
  checkKappaConservation(pre: number, post: number, spent: number, leak: number): {
    conserved: boolean;
    deficit: number;
  } {
    const expected = post + spent + leak;
    const deficit = pre - expected;
    
    return {
      conserved: Math.abs(deficit) < 1e-10,
      deficit
    };
  }
  
  /**
   * Get budget status
   */
  getStatus(): {
    kappa: BudgetStatus;
    beta: BudgetStatus;
    chi: BudgetStatus;
    epsilon: BudgetStatus;
  } {
    return {
      kappa: this.getBudgetStatus(BudgetType.Kappa),
      beta: this.getBudgetStatus(BudgetType.Beta),
      chi: this.getBudgetStatus(BudgetType.Chi),
      epsilon: this.getBudgetStatus(BudgetType.Epsilon)
    };
  }
  
  /**
   * Expire old allocations
   */
  expireAllocations(): number {
    const now = Date.now();
    let expired = 0;
    
    for (const [requestId, allocation] of this.allocations) {
      if (allocation.expiresAt && allocation.expiresAt < now) {
        this.release(requestId);
        expired++;
      }
    }
    
    return expired;
  }
  
  private getBudget(type: BudgetType): Budget {
    switch (type) {
      case BudgetType.Kappa: return this.corridor.budgets.kappa;
      case BudgetType.Beta: return this.corridor.budgets.beta;
      case BudgetType.Chi: return this.corridor.budgets.chi;
      case BudgetType.Epsilon: return this.corridor.budgets.epsilon;
    }
  }
  
  private getBudgetStatus(type: BudgetType): BudgetStatus {
    const budget = this.getBudget(type);
    const utilizationRatio = budget.used / budget.allocated;
    
    let health: "healthy" | "warning" | "critical" | "exhausted";
    if (budget.available <= 0) {
      health = "exhausted";
    } else if (budget.used >= budget.limits.softLimit) {
      health = "critical";
    } else if (budget.used >= budget.limits.softLimit * 0.7) {
      health = "warning";
    } else {
      health = "healthy";
    }
    
    return {
      type,
      allocated: budget.allocated,
      used: budget.used,
      reserved: budget.reserved,
      available: budget.available,
      utilizationRatio,
      health
    };
  }
  
  private recordViolation(type: BudgetType, attempted: number, available: number): void {
    const violation: BudgetViolation = {
      type,
      timestamp: Date.now(),
      attempted,
      available,
      severity: attempted > available * 2 ? "critical" : "error"
    };
    
    this.corridor.metrics.violations.push(violation);
  }
  
  private updatePeakUsage(type: BudgetType, current: number): void {
    const peak = this.corridor.metrics.peakUsage.get(type) ?? 0;
    if (current > peak) {
      this.corridor.metrics.peakUsage.set(type, current);
    }
  }
}

export interface BudgetStatus {
  type: BudgetType;
  allocated: number;
  used: number;
  reserved: number;
  available: number;
  utilizationRatio: number;
  health: "healthy" | "warning" | "critical" | "exhausted";
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: FLOW CONTROL
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Rate limiter using token bucket algorithm
 */
export class RateLimiter {
  private tokens: number;
  private maxTokens: number;
  private refillRate: number;  // tokens per second
  private lastRefill: number;
  
  constructor(maxTokens: number, refillRate: number) {
    this.tokens = maxTokens;
    this.maxTokens = maxTokens;
    this.refillRate = refillRate;
    this.lastRefill = Date.now();
  }
  
  /**
   * Try to acquire tokens
   */
  tryAcquire(count: number = 1): boolean {
    this.refill();
    
    if (this.tokens >= count) {
      this.tokens -= count;
      return true;
    }
    
    return false;
  }
  
  /**
   * Get current token count
   */
  getTokens(): number {
    this.refill();
    return this.tokens;
  }
  
  /**
   * Get time until tokens available
   */
  getWaitTime(count: number): number {
    this.refill();
    
    if (this.tokens >= count) return 0;
    
    const needed = count - this.tokens;
    return (needed / this.refillRate) * 1000;
  }
  
  private refill(): void {
    const now = Date.now();
    const elapsed = (now - this.lastRefill) / 1000;
    const newTokens = elapsed * this.refillRate;
    
    this.tokens = Math.min(this.maxTokens, this.tokens + newTokens);
    this.lastRefill = now;
  }
}

/**
 * Circuit breaker for fault tolerance
 */
export class CircuitBreaker {
  private state: "closed" | "open" | "half-open" = "closed";
  private failures: number = 0;
  private successes: number = 0;
  private lastFailure: number = 0;
  
  private failureThreshold: number;
  private successThreshold: number;
  private timeout: number;  // ms before trying again
  
  constructor(
    failureThreshold: number = 5,
    successThreshold: number = 2,
    timeout: number = 30000
  ) {
    this.failureThreshold = failureThreshold;
    this.successThreshold = successThreshold;
    this.timeout = timeout;
  }
  
  /**
   * Check if request is allowed
   */
  isAllowed(): boolean {
    switch (this.state) {
      case "closed":
        return true;
        
      case "open":
        // Check if timeout has passed
        if (Date.now() - this.lastFailure > this.timeout) {
          this.state = "half-open";
          return true;
        }
        return false;
        
      case "half-open":
        return true;
    }
  }
  
  /**
   * Record success
   */
  recordSuccess(): void {
    if (this.state === "half-open") {
      this.successes++;
      if (this.successes >= this.successThreshold) {
        this.state = "closed";
        this.failures = 0;
        this.successes = 0;
      }
    } else {
      this.failures = 0;
    }
  }
  
  /**
   * Record failure
   */
  recordFailure(): void {
    this.failures++;
    this.lastFailure = Date.now();
    
    if (this.state === "half-open") {
      this.state = "open";
      this.successes = 0;
    } else if (this.failures >= this.failureThreshold) {
      this.state = "open";
    }
  }
  
  /**
   * Get current state
   */
  getState(): { state: string; failures: number; successes: number } {
    return {
      state: this.state,
      failures: this.failures,
      successes: this.successes
    };
  }
}

/**
 * Backpressure controller
 */
export class BackpressureController {
  private queueSize: number = 0;
  private maxQueueSize: number;
  private highWaterMark: number;
  private lowWaterMark: number;
  private paused: boolean = false;
  
  constructor(
    maxQueueSize: number = 1000,
    highWaterMark: number = 0.8,
    lowWaterMark: number = 0.3
  ) {
    this.maxQueueSize = maxQueueSize;
    this.highWaterMark = highWaterMark * maxQueueSize;
    this.lowWaterMark = lowWaterMark * maxQueueSize;
  }
  
  /**
   * Signal item added to queue
   */
  onEnqueue(): void {
    this.queueSize++;
    
    if (this.queueSize >= this.highWaterMark && !this.paused) {
      this.paused = true;
    }
  }
  
  /**
   * Signal item removed from queue
   */
  onDequeue(): void {
    this.queueSize = Math.max(0, this.queueSize - 1);
    
    if (this.queueSize <= this.lowWaterMark && this.paused) {
      this.paused = false;
    }
  }
  
  /**
   * Check if should accept new items
   */
  shouldAccept(): boolean {
    return this.queueSize < this.maxQueueSize && !this.paused;
  }
  
  /**
   * Get pressure level (0 to 1)
   */
  getPressure(): number {
    return this.queueSize / this.maxQueueSize;
  }
  
  /**
   * Get status
   */
  getStatus(): { queueSize: number; pressure: number; paused: boolean } {
    return {
      queueSize: this.queueSize,
      pressure: this.getPressure(),
      paused: this.paused
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: ADMISSION CONTROL
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Admission controller for requests
 */
export interface AdmissionPolicy {
  name: string;
  evaluate: (request: AdmissionRequest) => AdmissionDecision;
  priority: number;
}

export interface AdmissionRequest {
  id: string;
  type: string;
  priority: "low" | "normal" | "high" | "critical";
  resourceRequirements: {
    kappa?: number;
    beta?: number;
    chi?: number;
  };
  metadata: Record<string, unknown>;
}

export interface AdmissionDecision {
  admitted: boolean;
  reason: string;
  queuePosition?: number;
  estimatedWait?: number;
}

export class AdmissionController {
  private policies: AdmissionPolicy[] = [];
  private budgetManager: BudgetManager;
  private rateLimiter: RateLimiter;
  private circuitBreaker: CircuitBreaker;
  private backpressure: BackpressureController;
  
  constructor(budgetManager: BudgetManager) {
    this.budgetManager = budgetManager;
    this.rateLimiter = new RateLimiter(100, 10);
    this.circuitBreaker = new CircuitBreaker();
    this.backpressure = new BackpressureController();
    
    this.initializeDefaultPolicies();
  }
  
  /**
   * Evaluate admission request
   */
  evaluate(request: AdmissionRequest): AdmissionDecision {
    // Check circuit breaker
    if (!this.circuitBreaker.isAllowed()) {
      return {
        admitted: false,
        reason: "Circuit breaker is open"
      };
    }
    
    // Check rate limit
    if (!this.rateLimiter.tryAcquire()) {
      return {
        admitted: false,
        reason: "Rate limit exceeded",
        estimatedWait: this.rateLimiter.getWaitTime(1)
      };
    }
    
    // Check backpressure
    if (!this.backpressure.shouldAccept()) {
      return {
        admitted: false,
        reason: "Backpressure threshold exceeded"
      };
    }
    
    // Evaluate policies in priority order
    const sortedPolicies = [...this.policies].sort((a, b) => b.priority - a.priority);
    
    for (const policy of sortedPolicies) {
      const decision = policy.evaluate(request);
      if (!decision.admitted) {
        return decision;
      }
    }
    
    // Check resource availability
    const budgetStatus = this.budgetManager.getStatus();
    
    if (request.resourceRequirements.kappa && 
        budgetStatus.kappa.available < request.resourceRequirements.kappa) {
      return {
        admitted: false,
        reason: `Insufficient κ budget: need ${request.resourceRequirements.kappa}, have ${budgetStatus.kappa.available}`
      };
    }
    
    if (request.resourceRequirements.beta && 
        budgetStatus.beta.available < request.resourceRequirements.beta) {
      return {
        admitted: false,
        reason: `Insufficient β budget: need ${request.resourceRequirements.beta}, have ${budgetStatus.beta.available}`
      };
    }
    
    if (request.resourceRequirements.chi && 
        budgetStatus.chi.available < request.resourceRequirements.chi) {
      return {
        admitted: false,
        reason: `Insufficient χ budget: need ${request.resourceRequirements.chi}, have ${budgetStatus.chi.available}`
      };
    }
    
    // Admitted
    this.backpressure.onEnqueue();
    
    return {
      admitted: true,
      reason: "Request admitted"
    };
  }
  
  /**
   * Record completion (success or failure)
   */
  recordCompletion(success: boolean): void {
    if (success) {
      this.circuitBreaker.recordSuccess();
    } else {
      this.circuitBreaker.recordFailure();
    }
    
    this.backpressure.onDequeue();
  }
  
  /**
   * Add custom policy
   */
  addPolicy(policy: AdmissionPolicy): void {
    this.policies.push(policy);
  }
  
  /**
   * Get status
   */
  getStatus(): {
    rateLimiter: { tokens: number };
    circuitBreaker: ReturnType<CircuitBreaker["getState"]>;
    backpressure: ReturnType<BackpressureController["getStatus"]>;
    policyCount: number;
  } {
    return {
      rateLimiter: { tokens: this.rateLimiter.getTokens() },
      circuitBreaker: this.circuitBreaker.getState(),
      backpressure: this.backpressure.getStatus(),
      policyCount: this.policies.length
    };
  }
  
  private initializeDefaultPolicies(): void {
    // Priority policy
    this.policies.push({
      name: "priority",
      priority: 100,
      evaluate: (request) => ({
        admitted: true,
        reason: "Priority check passed"
      })
    });
    
    // Resource policy
    this.policies.push({
      name: "resource",
      priority: 90,
      evaluate: (request) => ({
        admitted: true,
        reason: "Resource check passed"
      })
    });
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: CORRIDOR DYNAMICS ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete Corridor Dynamics Engine
 */
export class CorridorDynamicsEngine {
  private corridors: Map<string, Corridor> = new Map();
  private budgetManagers: Map<string, BudgetManager> = new Map();
  private admissionControllers: Map<string, AdmissionController> = new Map();
  private corridorCounter: number = 0;
  
  /**
   * Create new corridor
   */
  createCorridor(config?: Parameters<typeof createCorridor>[1]): Corridor {
    const id = `corridor_${++this.corridorCounter}`;
    const corridor = createCorridor(id, config);
    
    this.corridors.set(id, corridor);
    
    const budgetManager = new BudgetManager(corridor);
    this.budgetManagers.set(id, budgetManager);
    
    const admissionController = new AdmissionController(budgetManager);
    this.admissionControllers.set(id, admissionController);
    
    return corridor;
  }
  
  /**
   * Get corridor by ID
   */
  getCorridor(id: string): Corridor | undefined {
    return this.corridors.get(id);
  }
  
  /**
   * Get budget manager for corridor
   */
  getBudgetManager(corridorId: string): BudgetManager | undefined {
    return this.budgetManagers.get(corridorId);
  }
  
  /**
   * Get admission controller for corridor
   */
  getAdmissionController(corridorId: string): AdmissionController | undefined {
    return this.admissionControllers.get(corridorId);
  }
  
  /**
   * Allocate budget in corridor
   */
  allocate(corridorId: string, request: AllocationRequest): AllocationResult {
    const manager = this.budgetManagers.get(corridorId);
    if (!manager) {
      return {
        success: false,
        allocated: 0,
        requestId: "",
        reason: `Corridor not found: ${corridorId}`
      };
    }
    
    return manager.allocate(request);
  }
  
  /**
   * Release budget in corridor
   */
  release(corridorId: string, requestId: string): boolean {
    const manager = this.budgetManagers.get(corridorId);
    return manager?.release(requestId) ?? false;
  }
  
  /**
   * Evaluate admission request
   */
  evaluateAdmission(corridorId: string, request: AdmissionRequest): AdmissionDecision {
    const controller = this.admissionControllers.get(corridorId);
    if (!controller) {
      return {
        admitted: false,
        reason: `Corridor not found: ${corridorId}`
      };
    }
    
    return controller.evaluate(request);
  }
  
  /**
   * Suspend corridor
   */
  suspend(corridorId: string): boolean {
    const corridor = this.corridors.get(corridorId);
    if (!corridor || corridor.state.status !== "active") return false;
    
    corridor.state.status = "suspended";
    corridor.state.suspendCount++;
    
    return true;
  }
  
  /**
   * Resume corridor
   */
  resume(corridorId: string): boolean {
    const corridor = this.corridors.get(corridorId);
    if (!corridor || corridor.state.status !== "suspended") return false;
    
    corridor.state.status = "active";
    corridor.state.resumeCount++;
    
    return true;
  }
  
  /**
   * Close corridor
   */
  close(corridorId: string): boolean {
    const corridor = this.corridors.get(corridorId);
    if (!corridor) return false;
    
    corridor.state.status = "closed";
    
    // Clean up
    this.budgetManagers.delete(corridorId);
    this.admissionControllers.delete(corridorId);
    
    return true;
  }
  
  /**
   * Get all corridor statuses
   */
  getAllStatuses(): Map<string, {
    corridor: CorridorState;
    budgets: ReturnType<BudgetManager["getStatus"]>;
    admission: ReturnType<AdmissionController["getStatus"]>;
  }> {
    const statuses = new Map();
    
    for (const [id, corridor] of this.corridors) {
      const budgetManager = this.budgetManagers.get(id);
      const admissionController = this.admissionControllers.get(id);
      
      statuses.set(id, {
        corridor: corridor.state,
        budgets: budgetManager?.getStatus() ?? null,
        admission: admissionController?.getStatus() ?? null
      });
    }
    
    return statuses;
  }
  
  /**
   * Check κ conservation across all corridors
   */
  checkGlobalConservation(): {
    conserved: boolean;
    totalAllocated: number;
    totalUsed: number;
    totalAvailable: number;
    deficit: number;
  } {
    let totalAllocated = 0;
    let totalUsed = 0;
    let totalAvailable = 0;
    
    for (const corridor of this.corridors.values()) {
      totalAllocated += corridor.budgets.kappa.allocated;
      totalUsed += corridor.budgets.kappa.used;
      totalAvailable += corridor.budgets.kappa.available;
    }
    
    const deficit = totalAllocated - (totalUsed + totalAvailable);
    
    return {
      conserved: Math.abs(deficit) < 1e-10,
      totalAllocated,
      totalUsed,
      totalAvailable,
      deficit
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Types
  BudgetType,
  
  // Budget
  createBudget,
  
  // Corridor
  createCorridor,
  
  // Manager
  BudgetManager,
  
  // Flow control
  RateLimiter,
  CircuitBreaker,
  BackpressureController,
  
  // Admission
  AdmissionController,
  
  // Engine
  CorridorDynamicsEngine
};
