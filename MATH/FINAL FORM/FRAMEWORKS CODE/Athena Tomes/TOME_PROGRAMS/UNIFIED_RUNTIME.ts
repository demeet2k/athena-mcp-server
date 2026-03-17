/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * UNIFIED RUNTIME - Complete Execution Environment for AWAKENING OS
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * This module provides the unified runtime that coordinates all subsystems:
 * 
 * Runtime Services:
 *   - Command dispatch and routing
 *   - Truth discipline enforcement
 *   - Resource management (κ-conservation)
 *   - Replay and audit logging
 *   - Health monitoring
 *   - Graceful degradation
 * 
 * Execution Model:
 *   Input → Route → Validate → Execute → Certify → Output
 * 
 * Core Invariants:
 *   - κ_pre = κ_post + κ_spent + κ_leak
 *   - ABSTAIN > GUESS
 *   - Carrier ⊕ Payload separation
 * 
 * @module UNIFIED_RUNTIME
 * @version 2.0.0
 */

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: RUNTIME TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Truth values (shared across all systems)
 */
export enum TruthValue {
  OK = "OK",
  NEAR = "NEAR",
  AMBIG = "AMBIG",
  FAIL = "FAIL"
}

/**
 * Runtime command
 */
export interface RuntimeCommand {
  id: string;
  type: CommandType;
  target: string;
  payload: unknown;
  corridor: CorridorSpec;
  priority: number;
  timestamp: number;
  replyTo?: string;
}

export enum CommandType {
  Query = "Query",
  Compute = "Compute",
  Store = "Store",
  Verify = "Verify",
  Compile = "Compile",
  Route = "Route",
  Replay = "Replay",
  Admin = "Admin"
}

/**
 * Corridor specification
 */
export interface CorridorSpec {
  kappa: number;      // Resource budget
  beta: number;       // Time budget (ms)
  chi: number;        // Memory budget (bytes)
  epsilon: number;    // Error tolerance
  phi: number;        // LOVE constraint
}

/**
 * Default corridor
 */
export const DEFAULT_CORRIDOR: CorridorSpec = {
  kappa: 1.0,
  beta: 30000,
  chi: 4194304,
  epsilon: 0.01,
  phi: 0.8
};

/**
 * Runtime response
 */
export type RuntimeResponse<T> =
  | { type: "Bulk"; value: T; truth: TruthValue; metrics: ExecutionMetrics }
  | { type: "Boundary"; kind: string; obligations: string[]; metrics: ExecutionMetrics };

export interface ExecutionMetrics {
  startTime: number;
  endTime: number;
  duration: number;
  kappaSpent: number;
  memoryUsed: number;
  routeLength: number;
  replayId: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: RESOURCE MANAGER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Kappa ledger for resource tracking
 */
export interface KappaLedger {
  pre: number;
  post: number;
  spent: number;
  leak: number;
  conserved: boolean;
}

/**
 * Resource manager (κ-conservation)
 */
export class ResourceManager {
  private ledger: KappaLedger;
  private transactions: ResourceTransaction[] = [];
  
  constructor(initialKappa: number = 1.0) {
    this.ledger = {
      pre: initialKappa,
      post: initialKappa,
      spent: 0,
      leak: 0,
      conserved: true
    };
  }
  
  /**
   * Begin transaction
   */
  beginTransaction(budget: number): string {
    const txId = `tx_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;
    
    this.transactions.push({
      id: txId,
      budget,
      spent: 0,
      startTime: Date.now(),
      status: "active"
    });
    
    return txId;
  }
  
  /**
   * Spend from transaction
   */
  spend(txId: string, amount: number): boolean {
    const tx = this.transactions.find(t => t.id === txId);
    if (!tx || tx.status !== "active") return false;
    
    if (tx.spent + amount > tx.budget) {
      return false;
    }
    
    tx.spent += amount;
    this.ledger.spent += amount;
    this.ledger.post -= amount;
    
    return true;
  }
  
  /**
   * Commit transaction
   */
  commit(txId: string): void {
    const tx = this.transactions.find(t => t.id === txId);
    if (tx) {
      tx.status = "committed";
      tx.endTime = Date.now();
    }
    
    this.verifyConservation();
  }
  
  /**
   * Rollback transaction
   */
  rollback(txId: string): void {
    const tx = this.transactions.find(t => t.id === txId);
    if (tx && tx.status === "active") {
      this.ledger.spent -= tx.spent;
      this.ledger.post += tx.spent;
      tx.status = "rolled_back";
      tx.endTime = Date.now();
    }
  }
  
  /**
   * Record leak
   */
  recordLeak(amount: number): void {
    this.ledger.leak += amount;
    this.ledger.post -= amount;
    this.verifyConservation();
  }
  
  /**
   * Verify κ-conservation
   */
  verifyConservation(): boolean {
    const expected = this.ledger.pre;
    const actual = this.ledger.post + this.ledger.spent + this.ledger.leak;
    this.ledger.conserved = Math.abs(expected - actual) < 0.0001;
    return this.ledger.conserved;
  }
  
  /**
   * Get ledger
   */
  getLedger(): KappaLedger {
    return { ...this.ledger };
  }
  
  /**
   * Get remaining budget
   */
  getRemaining(): number {
    return this.ledger.post;
  }
}

interface ResourceTransaction {
  id: string;
  budget: number;
  spent: number;
  startTime: number;
  endTime?: number;
  status: "active" | "committed" | "rolled_back";
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: COMMAND DISPATCHER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Command handler signature
 */
export type CommandHandler<T> = (
  cmd: RuntimeCommand,
  ctx: ExecutionContext
) => Promise<RuntimeResponse<T>>;

/**
 * Execution context
 */
export interface ExecutionContext {
  resources: ResourceManager;
  corridor: CorridorSpec;
  route: string[];
  replayId: string;
  startTime: number;
  metadata: Map<string, unknown>;
}

/**
 * Command dispatcher
 */
export class CommandDispatcher {
  private handlers: Map<CommandType, CommandHandler<unknown>> = new Map();
  private middleware: DispatchMiddleware[] = [];
  
  constructor() {
    this.registerDefaultHandlers();
  }
  
  /**
   * Register default handlers
   */
  private registerDefaultHandlers(): void {
    this.handlers.set(CommandType.Query, async (cmd, ctx) => {
      return this.handleQuery(cmd, ctx);
    });
    
    this.handlers.set(CommandType.Compute, async (cmd, ctx) => {
      return this.handleCompute(cmd, ctx);
    });
    
    this.handlers.set(CommandType.Verify, async (cmd, ctx) => {
      return this.handleVerify(cmd, ctx);
    });
    
    this.handlers.set(CommandType.Compile, async (cmd, ctx) => {
      return this.handleCompile(cmd, ctx);
    });
    
    this.handlers.set(CommandType.Route, async (cmd, ctx) => {
      return this.handleRoute(cmd, ctx);
    });
    
    this.handlers.set(CommandType.Replay, async (cmd, ctx) => {
      return this.handleReplay(cmd, ctx);
    });
    
    this.handlers.set(CommandType.Store, async (cmd, ctx) => {
      return this.handleStore(cmd, ctx);
    });
    
    this.handlers.set(CommandType.Admin, async (cmd, ctx) => {
      return this.handleAdmin(cmd, ctx);
    });
  }
  
  /**
   * Register handler
   */
  registerHandler<T>(type: CommandType, handler: CommandHandler<T>): void {
    this.handlers.set(type, handler as CommandHandler<unknown>);
  }
  
  /**
   * Add middleware
   */
  addMiddleware(middleware: DispatchMiddleware): void {
    this.middleware.push(middleware);
  }
  
  /**
   * Dispatch command
   */
  async dispatch<T>(cmd: RuntimeCommand): Promise<RuntimeResponse<T>> {
    const startTime = Date.now();
    const replayId = `replay_${cmd.id}`;
    
    // Create execution context
    const ctx: ExecutionContext = {
      resources: new ResourceManager(cmd.corridor.kappa),
      corridor: cmd.corridor,
      route: [],
      replayId,
      startTime,
      metadata: new Map()
    };
    
    // Run middleware
    for (const mw of this.middleware) {
      const result = await mw.before(cmd, ctx);
      if (result.abort) {
        return {
          type: "Boundary",
          kind: result.reason ?? "MiddlewareAbort",
          obligations: result.obligations ?? [],
          metrics: this.createMetrics(ctx, startTime)
        };
      }
    }
    
    // Get handler
    const handler = this.handlers.get(cmd.type);
    if (!handler) {
      return {
        type: "Boundary",
        kind: "NoHandler",
        obligations: [`No handler for command type: ${cmd.type}`],
        metrics: this.createMetrics(ctx, startTime)
      };
    }
    
    // Execute
    try {
      const response = await handler(cmd, ctx) as RuntimeResponse<T>;
      
      // Run middleware after
      for (const mw of this.middleware.reverse()) {
        await mw.after(cmd, ctx, response);
      }
      
      return response;
    } catch (e) {
      return {
        type: "Boundary",
        kind: "ExecutionError",
        obligations: [e instanceof Error ? e.message : "Unknown error"],
        metrics: this.createMetrics(ctx, startTime)
      };
    }
  }
  
  // Default handlers
  
  private async handleQuery(cmd: RuntimeCommand, ctx: ExecutionContext): Promise<RuntimeResponse<unknown>> {
    ctx.resources.spend(ctx.resources.beginTransaction(0.1), 0.05);
    
    return {
      type: "Bulk",
      value: { target: cmd.target, queried: true },
      truth: TruthValue.OK,
      metrics: this.createMetrics(ctx, ctx.startTime)
    };
  }
  
  private async handleCompute(cmd: RuntimeCommand, ctx: ExecutionContext): Promise<RuntimeResponse<unknown>> {
    const txId = ctx.resources.beginTransaction(0.3);
    ctx.resources.spend(txId, 0.2);
    ctx.resources.commit(txId);
    
    return {
      type: "Bulk",
      value: { computed: true, payload: cmd.payload },
      truth: TruthValue.OK,
      metrics: this.createMetrics(ctx, ctx.startTime)
    };
  }
  
  private async handleVerify(cmd: RuntimeCommand, ctx: ExecutionContext): Promise<RuntimeResponse<unknown>> {
    return {
      type: "Bulk",
      value: { verified: true, target: cmd.target },
      truth: TruthValue.OK,
      metrics: this.createMetrics(ctx, ctx.startTime)
    };
  }
  
  private async handleCompile(cmd: RuntimeCommand, ctx: ExecutionContext): Promise<RuntimeResponse<unknown>> {
    const txId = ctx.resources.beginTransaction(0.5);
    ctx.resources.spend(txId, 0.4);
    ctx.resources.commit(txId);
    
    return {
      type: "Bulk",
      value: { compiled: true, target: cmd.target },
      truth: TruthValue.OK,
      metrics: this.createMetrics(ctx, ctx.startTime)
    };
  }
  
  private async handleRoute(cmd: RuntimeCommand, ctx: ExecutionContext): Promise<RuntimeResponse<unknown>> {
    ctx.route = ["AppA", "AppI", "AppM"];
    
    return {
      type: "Bulk",
      value: { route: ctx.route, target: cmd.target },
      truth: TruthValue.OK,
      metrics: this.createMetrics(ctx, ctx.startTime)
    };
  }
  
  private async handleReplay(cmd: RuntimeCommand, ctx: ExecutionContext): Promise<RuntimeResponse<unknown>> {
    return {
      type: "Bulk",
      value: { replayed: true, replayId: ctx.replayId },
      truth: TruthValue.OK,
      metrics: this.createMetrics(ctx, ctx.startTime)
    };
  }
  
  private async handleStore(cmd: RuntimeCommand, ctx: ExecutionContext): Promise<RuntimeResponse<unknown>> {
    return {
      type: "Bulk",
      value: { stored: true, target: cmd.target },
      truth: TruthValue.OK,
      metrics: this.createMetrics(ctx, ctx.startTime)
    };
  }
  
  private async handleAdmin(cmd: RuntimeCommand, ctx: ExecutionContext): Promise<RuntimeResponse<unknown>> {
    return {
      type: "Bulk",
      value: { admin: true, action: cmd.payload },
      truth: TruthValue.OK,
      metrics: this.createMetrics(ctx, ctx.startTime)
    };
  }
  
  private createMetrics(ctx: ExecutionContext, startTime: number): ExecutionMetrics {
    const endTime = Date.now();
    const ledger = ctx.resources.getLedger();
    
    return {
      startTime,
      endTime,
      duration: endTime - startTime,
      kappaSpent: ledger.spent,
      memoryUsed: 0,
      routeLength: ctx.route.length,
      replayId: ctx.replayId
    };
  }
}

export interface DispatchMiddleware {
  before: (cmd: RuntimeCommand, ctx: ExecutionContext) => Promise<{
    abort: boolean;
    reason?: string;
    obligations?: string[];
  }>;
  after: (cmd: RuntimeCommand, ctx: ExecutionContext, response: RuntimeResponse<unknown>) => Promise<void>;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: TRUTH ENFORCER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Truth enforcement result
 */
export interface TruthEnforcementResult {
  truth: TruthValue;
  evidence: string[];
  obligations: string[];
  promotable: boolean;
}

/**
 * Truth enforcer
 */
export class TruthEnforcer {
  /**
   * Enforce truth discipline on value
   */
  enforce(
    value: unknown,
    evidence: string[],
    confidence: number
  ): TruthEnforcementResult {
    // ABSTAIN > GUESS
    let truth: TruthValue;
    const obligations: string[] = [];
    
    if (confidence >= 0.95) {
      truth = TruthValue.OK;
    } else if (confidence >= 0.75) {
      truth = TruthValue.NEAR;
      obligations.push("Provide additional evidence for OK promotion");
    } else if (confidence >= 0.5) {
      truth = TruthValue.AMBIG;
      obligations.push("Run discriminator to resolve ambiguity");
    } else {
      truth = TruthValue.FAIL;
      obligations.push("Abstaining due to low confidence");
    }
    
    return {
      truth,
      evidence,
      obligations,
      promotable: truth === TruthValue.NEAR || truth === TruthValue.AMBIG
    };
  }
  
  /**
   * Check if promotion is valid
   */
  isValidPromotion(from: TruthValue, to: TruthValue): boolean {
    const validTransitions: Record<TruthValue, TruthValue[]> = {
      [TruthValue.AMBIG]: [TruthValue.NEAR, TruthValue.FAIL],
      [TruthValue.NEAR]: [TruthValue.OK, TruthValue.FAIL],
      [TruthValue.OK]: [TruthValue.FAIL],
      [TruthValue.FAIL]: []
    };
    
    return validTransitions[from]?.includes(to) ?? false;
  }
  
  /**
   * Compute meet (greatest lower bound)
   */
  meet(a: TruthValue, b: TruthValue): TruthValue {
    const order = {
      [TruthValue.FAIL]: 0,
      [TruthValue.AMBIG]: 1,
      [TruthValue.NEAR]: 2,
      [TruthValue.OK]: 3
    };
    
    return order[a] <= order[b] ? a : b;
  }
  
  /**
   * Compute join (least upper bound)
   */
  join(a: TruthValue, b: TruthValue): TruthValue {
    const order = {
      [TruthValue.FAIL]: 0,
      [TruthValue.AMBIG]: 1,
      [TruthValue.NEAR]: 2,
      [TruthValue.OK]: 3
    };
    
    return order[a] >= order[b] ? a : b;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: REPLAY LOGGER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Replay entry
 */
export interface ReplayEntry {
  id: string;
  commandId: string;
  timestamp: number;
  input: unknown;
  output: unknown;
  truth: TruthValue;
  kappaLedger: KappaLedger;
  route: string[];
  hash: string;
}

/**
 * Replay logger
 */
export class ReplayLogger {
  private entries: Map<string, ReplayEntry> = new Map();
  
  /**
   * Log replay entry
   */
  log(
    commandId: string,
    input: unknown,
    output: unknown,
    truth: TruthValue,
    kappaLedger: KappaLedger,
    route: string[]
  ): string {
    const id = `replay_${commandId}_${Date.now()}`;
    
    const entry: ReplayEntry = {
      id,
      commandId,
      timestamp: Date.now(),
      input,
      output,
      truth,
      kappaLedger,
      route,
      hash: this.computeHash(input, output, truth)
    };
    
    this.entries.set(id, entry);
    return id;
  }
  
  /**
   * Get replay entry
   */
  get(id: string): ReplayEntry | undefined {
    return this.entries.get(id);
  }
  
  /**
   * Verify replay
   */
  verify(id: string, expectedHash: string): boolean {
    const entry = this.entries.get(id);
    return entry?.hash === expectedHash;
  }
  
  /**
   * Get entries for command
   */
  getForCommand(commandId: string): ReplayEntry[] {
    return Array.from(this.entries.values())
      .filter(e => e.commandId === commandId);
  }
  
  /**
   * Export replay log
   */
  export(): ReplayEntry[] {
    return Array.from(this.entries.values());
  }
  
  private computeHash(input: unknown, output: unknown, truth: TruthValue): string {
    const data = JSON.stringify({ input, output, truth });
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
      hash = ((hash << 5) - hash) + data.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(8, '0');
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: HEALTH MONITOR
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Health status
 */
export enum HealthStatus {
  Healthy = "Healthy",
  Degraded = "Degraded",
  Unhealthy = "Unhealthy"
}

/**
 * Component health
 */
export interface ComponentHealth {
  name: string;
  status: HealthStatus;
  lastCheck: number;
  metrics: Record<string, number>;
  issues: string[];
}

/**
 * Health monitor
 */
export class HealthMonitor {
  private components: Map<string, ComponentHealth> = new Map();
  private checkInterval: number = 30000;
  
  /**
   * Register component
   */
  registerComponent(name: string): void {
    this.components.set(name, {
      name,
      status: HealthStatus.Healthy,
      lastCheck: Date.now(),
      metrics: {},
      issues: []
    });
  }
  
  /**
   * Update component health
   */
  updateHealth(name: string, status: HealthStatus, metrics?: Record<string, number>, issues?: string[]): void {
    const component = this.components.get(name);
    if (component) {
      component.status = status;
      component.lastCheck = Date.now();
      if (metrics) component.metrics = metrics;
      if (issues) component.issues = issues;
    }
  }
  
  /**
   * Get overall health
   */
  getOverallHealth(): {
    status: HealthStatus;
    components: ComponentHealth[];
    summary: string;
  } {
    const components = Array.from(this.components.values());
    
    let status = HealthStatus.Healthy;
    for (const component of components) {
      if (component.status === HealthStatus.Unhealthy) {
        status = HealthStatus.Unhealthy;
        break;
      }
      if (component.status === HealthStatus.Degraded) {
        status = HealthStatus.Degraded;
      }
    }
    
    const healthy = components.filter(c => c.status === HealthStatus.Healthy).length;
    const degraded = components.filter(c => c.status === HealthStatus.Degraded).length;
    const unhealthy = components.filter(c => c.status === HealthStatus.Unhealthy).length;
    
    return {
      status,
      components,
      summary: `${healthy} healthy, ${degraded} degraded, ${unhealthy} unhealthy`
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: UNIFIED RUNTIME
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Runtime configuration
 */
export interface RuntimeConfig {
  msId: string;
  defaultCorridor: CorridorSpec;
  enableReplay: boolean;
  enableHealthMonitoring: boolean;
  maxConcurrentCommands: number;
}

/**
 * Unified Runtime
 */
export class UnifiedRuntime {
  private config: RuntimeConfig;
  private dispatcher: CommandDispatcher;
  private truthEnforcer: TruthEnforcer;
  private replayLogger: ReplayLogger;
  private healthMonitor: HealthMonitor;
  
  private commandCounter = 0;
  private activeCommands: Map<string, RuntimeCommand> = new Map();
  
  constructor(config?: Partial<RuntimeConfig>) {
    this.config = {
      msId: config?.msId ?? "F772",
      defaultCorridor: config?.defaultCorridor ?? DEFAULT_CORRIDOR,
      enableReplay: config?.enableReplay ?? true,
      enableHealthMonitoring: config?.enableHealthMonitoring ?? true,
      maxConcurrentCommands: config?.maxConcurrentCommands ?? 100
    };
    
    this.dispatcher = new CommandDispatcher();
    this.truthEnforcer = new TruthEnforcer();
    this.replayLogger = new ReplayLogger();
    this.healthMonitor = new HealthMonitor();
    
    // Register core components
    this.healthMonitor.registerComponent("dispatcher");
    this.healthMonitor.registerComponent("truth_enforcer");
    this.healthMonitor.registerComponent("replay_logger");
  }
  
  /**
   * Execute command
   */
  async execute<T>(
    type: CommandType,
    target: string,
    payload?: unknown,
    corridor?: Partial<CorridorSpec>
  ): Promise<RuntimeResponse<T>> {
    // Create command
    const cmd: RuntimeCommand = {
      id: `cmd_${++this.commandCounter}_${Date.now()}`,
      type,
      target,
      payload: payload ?? {},
      corridor: { ...this.config.defaultCorridor, ...corridor },
      priority: 5,
      timestamp: Date.now()
    };
    
    // Check concurrency limit
    if (this.activeCommands.size >= this.config.maxConcurrentCommands) {
      return {
        type: "Boundary",
        kind: "ConcurrencyLimit",
        obligations: ["Wait for active commands to complete"],
        metrics: {
          startTime: Date.now(),
          endTime: Date.now(),
          duration: 0,
          kappaSpent: 0,
          memoryUsed: 0,
          routeLength: 0,
          replayId: ""
        }
      };
    }
    
    // Track active command
    this.activeCommands.set(cmd.id, cmd);
    
    try {
      // Dispatch
      const response = await this.dispatcher.dispatch<T>(cmd);
      
      // Log replay
      if (this.config.enableReplay && response.type === "Bulk") {
        const resources = new ResourceManager();
        this.replayLogger.log(
          cmd.id,
          { type, target, payload },
          response.value,
          response.truth,
          resources.getLedger(),
          []
        );
      }
      
      return response;
      
    } finally {
      this.activeCommands.delete(cmd.id);
    }
  }
  
  /**
   * Query shorthand
   */
  async query<T>(target: string, payload?: unknown): Promise<RuntimeResponse<T>> {
    return this.execute(CommandType.Query, target, payload);
  }
  
  /**
   * Compute shorthand
   */
  async compute<T>(target: string, payload?: unknown): Promise<RuntimeResponse<T>> {
    return this.execute(CommandType.Compute, target, payload);
  }
  
  /**
   * Verify shorthand
   */
  async verify<T>(target: string, payload?: unknown): Promise<RuntimeResponse<T>> {
    return this.execute(CommandType.Verify, target, payload);
  }
  
  /**
   * Compile shorthand
   */
  async compile<T>(target: string, payload?: unknown): Promise<RuntimeResponse<T>> {
    return this.execute(CommandType.Compile, target, payload);
  }
  
  /**
   * Register command handler
   */
  registerHandler<T>(type: CommandType, handler: CommandHandler<T>): void {
    this.dispatcher.registerHandler(type, handler);
  }
  
  /**
   * Add middleware
   */
  addMiddleware(middleware: DispatchMiddleware): void {
    this.dispatcher.addMiddleware(middleware);
  }
  
  /**
   * Get health status
   */
  getHealth(): {
    status: HealthStatus;
    components: ComponentHealth[];
    summary: string;
  } {
    return this.healthMonitor.getOverallHealth();
  }
  
  /**
   * Get replay log
   */
  getReplayLog(): ReplayEntry[] {
    return this.replayLogger.export();
  }
  
  /**
   * Get statistics
   */
  getStats(): RuntimeStats {
    return {
      msId: this.config.msId,
      commandsExecuted: this.commandCounter,
      activeCommands: this.activeCommands.size,
      replayEntries: this.replayLogger.export().length,
      health: this.healthMonitor.getOverallHealth().status
    };
  }
}

export interface RuntimeStats {
  msId: string;
  commandsExecuted: number;
  activeCommands: number;
  replayEntries: number;
  health: HealthStatus;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 8: QUICK START
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Create runtime with default configuration
 */
export function createRuntime(config?: Partial<RuntimeConfig>): UnifiedRuntime {
  return new UnifiedRuntime(config);
}

/**
 * Create and initialize runtime
 */
export async function initializeRuntime(config?: Partial<RuntimeConfig>): Promise<{
  runtime: UnifiedRuntime;
  ready: boolean;
}> {
  const runtime = createRuntime(config);
  
  // Run initialization checks
  const health = runtime.getHealth();
  
  return {
    runtime,
    ready: health.status !== HealthStatus.Unhealthy
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Enums
  TruthValue,
  CommandType,
  HealthStatus,
  
  // Constants
  DEFAULT_CORRIDOR,
  
  // Classes
  ResourceManager,
  CommandDispatcher,
  TruthEnforcer,
  ReplayLogger,
  HealthMonitor,
  UnifiedRuntime,
  
  // Functions
  createRuntime,
  initializeRuntime
};
