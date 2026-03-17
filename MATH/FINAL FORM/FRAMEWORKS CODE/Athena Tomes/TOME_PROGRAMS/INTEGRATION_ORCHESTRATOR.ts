/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * INTEGRATION ORCHESTRATOR - Master System Integration
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * This orchestrator unifies all TOME engines into a coherent runtime:
 * 
 * From SELF_SUFFICIENCY_TOME:
 *   - Domain packs (Ch18)
 *   - Metro routing (Ch19)
 *   - Self-driving loop (Ch20)
 *   - Publication closure (Ch21)
 *   - Symbol tables (App A)
 *   - Certificate verification (App B)
 * 
 * From TRUTH-COLLAPSE_COMPILER:
 *   - Obligation graphs (Ch18)
 *   - Conflict algebra (Ch19)
 * 
 * From VOYNICHVM_TRICOMPILER:
 *   - Tricompiler core (Ch02)
 * 
 * Core Principles:
 *   - Truth Lattice: 𝕋 = {OK, NEAR, AMBIG, FAIL}
 *   - ABSTAIN > GUESS
 *   - κ-conservation: κ_pre = κ_post + κ_spent + κ_leak
 *   - Carrier ⊕ Payload separation
 * 
 * @module INTEGRATION_ORCHESTRATOR
 * @version 2.0.0
 */

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: CORE TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Truth lattice
 */
export enum TruthValue {
  OK = "OK",
  NEAR = "NEAR",
  AMBIG = "AMBIG",
  FAIL = "FAIL"
}

/**
 * Edge kinds (closed set)
 */
export enum EdgeKind {
  REF = "REF",
  EQUIV = "EQUIV",
  MIGRATE = "MIGRATE",
  DUAL = "DUAL",
  GEN = "GEN",
  INST = "INST",
  IMPL = "IMPL",
  PROOF = "PROOF",
  CONFLICT = "CONFLICT"
}

/**
 * Lens types
 */
export enum Lens {
  S = "S",  // Square/Earth
  F = "F",  // Flower/Air
  C = "C",  // Cloud/Water
  R = "R"   // Fractal/Fire
}

/**
 * Manuscript ID
 */
export interface ManuscriptID {
  code: string;
  base4: string;
  seed: string;
}

/**
 * Global address
 */
export interface GlobalAddr {
  ms: ManuscriptID;
  chapter: number;
  station: string;
  lens: Lens;
  facet: number;
  atom: string;
}

/**
 * Corridor budgets
 */
export interface CorridorBudgets {
  kappa: number;      // Resource budget
  beta: number;       // Time budget
  chi: number;        // Memory budget
  epsilon: number;    // Error budget
  phi: number;        // LOVE constraint
}

/**
 * System output
 */
export type SystemOutput<T> =
  | { type: "Bulk"; value: T; witness?: string }
  | { type: "Boundary"; kind: string; obligations: string[] };

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: SUBSYSTEM INTERFACES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Domain pack interface
 */
export interface DomainPackSubsystem {
  compilePack(manifest: unknown): SystemOutput<unknown>;
  registerPack(pack: unknown): void;
  getPack(domain: string): unknown | undefined;
  synthesizeAdapter(from: string, to: string): SystemOutput<unknown>;
}

/**
 * Metro routing interface
 */
export interface MetroRoutingSubsystem {
  computeRoute(source: string, target: string, corridor: CorridorBudgets): SystemOutput<string[]>;
  registerHub(hub: unknown): void;
  tunnel(seed: string, level: number): SystemOutput<unknown>;
}

/**
 * Self-driving loop interface
 */
export interface SelfDrivingSubsystem {
  extractFrontier(): unknown[];
  selectWork(obligations: unknown[]): unknown | null;
  executeWork(work: unknown): SystemOutput<unknown>;
  checkStuckness(): boolean;
  escape(): SystemOutput<unknown>;
}

/**
 * Publication interface
 */
export interface PublicationSubsystem {
  createPublication(artifacts: Map<string, unknown>): SystemOutput<unknown>;
  checkConsistency(): { consistent: boolean; conflicts: unknown[] };
  seal(pubId: string): SystemOutput<unknown>;
}

/**
 * Symbol table interface
 */
export interface SymbolTableSubsystem {
  registerSymbol(symbol: unknown): SystemOutput<string>;
  resolveSymbol(fqName: string): SystemOutput<unknown>;
  getArchetype(word: number[]): unknown | undefined;
}

/**
 * Certificate verification interface
 */
export interface CertificateSubsystem {
  verify(cert: unknown, budgets: CorridorBudgets): SystemOutput<boolean>;
  createMerkleProof(leaves: string[], index: number): unknown;
  verifyMerkleProof(proof: unknown): boolean;
}

/**
 * Obligation graph interface
 */
export interface ObligationSubsystem {
  createObligation(kind: string, claim: string, target: string): string;
  discharge(budgets: CorridorBudgets): SystemOutput<unknown>;
  compileCollapsePack(target: string): SystemOutput<unknown>;
}

/**
 * Conflict algebra interface
 */
export interface ConflictSubsystem {
  detectConflicts(context: unknown): { hasConflict: boolean; conflicts: unknown[] };
  createQuarantine(target: string, conflicts: unknown[]): unknown;
  isQuarantined(target: string): boolean;
}

/**
 * Tricompiler interface
 */
export interface TricompilerSubsystem {
  parseToken(token: string): SystemOutput<unknown>;
  compileAndRun(tokens: string[]): SystemOutput<unknown>;
  executeInstruction(state: unknown, instr: unknown): SystemOutput<unknown>;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: ROUTER V2
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Hub set (max 6)
 */
export interface HubSet {
  hubs: string[];
  signature: string[];
  overlays: string[];
}

/**
 * Arc hub mapping
 */
const ARC_HUB_MAP: Record<number, string> = {
  0: "AppA",
  1: "AppC",
  2: "AppE",
  3: "AppF",
  4: "AppG",
  5: "AppN",
  6: "AppP"
};

/**
 * Lens base mapping
 */
const LENS_BASE_MAP: Record<Lens, string> = {
  [Lens.S]: "AppC",
  [Lens.F]: "AppE",
  [Lens.C]: "AppI",
  [Lens.R]: "AppM"
};

/**
 * Facet base mapping
 */
const FACET_BASE_MAP: Record<number, string> = {
  1: "AppA",
  2: "AppB",
  3: "AppH",
  4: "AppM"
};

/**
 * Truth overlay mapping
 */
const TRUTH_OVERLAY_MAP: Record<TruthValue, string | null> = {
  [TruthValue.OK]: "AppO",    // Only when publishing
  [TruthValue.NEAR]: "AppJ",
  [TruthValue.AMBIG]: "AppL",
  [TruthValue.FAIL]: "AppK"
};

/**
 * Mandatory signature
 */
const MANDATORY_SIGNATURE = ["AppA", "AppI", "AppM"];

/**
 * Router V2
 */
export class RouterV2 {
  private maxHubSet = 6;
  
  /**
   * Compute hub set for address
   */
  computeHubSet(
    addr: GlobalAddr,
    truth: TruthValue,
    publishing: boolean = false
  ): HubSet {
    const hubs = new Set<string>(MANDATORY_SIGNATURE);
    const overlays: string[] = [];
    
    // Add lens base
    hubs.add(LENS_BASE_MAP[addr.lens]);
    
    // Add facet base
    hubs.add(FACET_BASE_MAP[addr.facet]);
    
    // Add arc hub (for chapters)
    if (addr.chapter > 0) {
      const omega = addr.chapter - 1;
      const alpha = Math.floor(omega / 3);
      hubs.add(ARC_HUB_MAP[alpha] ?? "AppA");
    }
    
    // Add truth overlay (non-droppable)
    const overlay = TRUTH_OVERLAY_MAP[truth];
    if (overlay && (truth !== TruthValue.OK || publishing)) {
      hubs.add(overlay);
      overlays.push(overlay);
    }
    
    // Enforce max hub set
    const hubArray = Array.from(hubs);
    if (hubArray.length > this.maxHubSet) {
      // Priority: Signature > Overlay > ArcHub > LensBase > FacetBase
      const prioritized = this.prioritize(hubArray, overlays);
      return {
        hubs: prioritized.slice(0, this.maxHubSet),
        signature: MANDATORY_SIGNATURE,
        overlays
      };
    }
    
    return {
      hubs: hubArray,
      signature: MANDATORY_SIGNATURE,
      overlays
    };
  }
  
  /**
   * Compute route
   */
  computeRoute(
    source: GlobalAddr,
    target: GlobalAddr,
    truth: TruthValue
  ): string[] {
    const targetHubs = this.computeHubSet(target, truth);
    
    // Route: source → ArcHub → LensBase → FacetBase → AppI → AppM → (overlay)
    const route: string[] = [];
    
    // Start with mandatory signature
    route.push(...MANDATORY_SIGNATURE.filter(h => !route.includes(h)));
    
    // Add target-specific hubs
    for (const hub of targetHubs.hubs) {
      if (!route.includes(hub)) {
        route.push(hub);
      }
    }
    
    return route;
  }
  
  private prioritize(hubs: string[], overlays: string[]): string[] {
    const priority: Record<string, number> = {
      "AppA": 100, "AppI": 99, "AppM": 98,  // Signature
      "AppJ": 90, "AppK": 90, "AppL": 90, "AppO": 90,  // Overlays
    };
    
    // Add overlay priority
    for (const o of overlays) {
      priority[o] = 95;  // Overlays are non-droppable
    }
    
    return hubs.sort((a, b) => (priority[b] ?? 50) - (priority[a] ?? 50));
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: MYCELIUM GRAPH
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Link edge
 */
export interface LinkEdge {
  edgeId: string;
  kind: EdgeKind;
  src: GlobalAddr;
  dst: GlobalAddr;
  scope: string;
  corridor: CorridorBudgets;
  witnessPtr?: string;
  replayPtr?: string;
  payload?: unknown;
  edgeVer: string;
}

/**
 * Mycelium graph
 */
export class MyceliumGraph {
  private vertices: Map<string, GlobalAddr> = new Map();
  private edges: Map<string, LinkEdge[]> = new Map();
  
  /**
   * Add vertex
   */
  addVertex(addr: GlobalAddr): void {
    const key = this.addrToKey(addr);
    this.vertices.set(key, addr);
    if (!this.edges.has(key)) {
      this.edges.set(key, []);
    }
  }
  
  /**
   * Add edge
   */
  addEdge(edge: LinkEdge): void {
    const srcKey = this.addrToKey(edge.src);
    
    if (!this.edges.has(srcKey)) {
      this.edges.set(srcKey, []);
    }
    
    this.edges.get(srcKey)!.push(edge);
  }
  
  /**
   * Get edges from vertex
   */
  getEdges(addr: GlobalAddr): LinkEdge[] {
    return this.edges.get(this.addrToKey(addr)) ?? [];
  }
  
  /**
   * Find path
   */
  findPath(src: GlobalAddr, dst: GlobalAddr): LinkEdge[] | null {
    const srcKey = this.addrToKey(src);
    const dstKey = this.addrToKey(dst);
    
    const visited = new Set<string>();
    const queue: { node: string; path: LinkEdge[] }[] = [{ node: srcKey, path: [] }];
    
    while (queue.length > 0) {
      const { node, path } = queue.shift()!;
      
      if (node === dstKey) return path;
      if (visited.has(node)) continue;
      visited.add(node);
      
      const edges = this.edges.get(node) ?? [];
      for (const edge of edges) {
        const nextKey = this.addrToKey(edge.dst);
        if (!visited.has(nextKey)) {
          queue.push({ node: nextKey, path: [...path, edge] });
        }
      }
    }
    
    return null;
  }
  
  /**
   * Get statistics
   */
  getStats(): { vertices: number; edges: number } {
    let edgeCount = 0;
    for (const edges of this.edges.values()) {
      edgeCount += edges.length;
    }
    return { vertices: this.vertices.size, edges: edgeCount };
  }
  
  private addrToKey(addr: GlobalAddr): string {
    return `${addr.ms.code}::Ch${addr.chapter.toString().padStart(2, '0')}⟨${addr.station}⟩.${addr.lens}${addr.facet}.${addr.atom}`;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: TRUTH DISCIPLINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Truth record
 */
export interface TruthRecord {
  truth: TruthValue;
  witnessPtr?: string;
  replayPtr?: string;
  residualLedger?: unknown;
  candidateSet?: unknown;
  quarantineCapsule?: unknown;
}

/**
 * Truth discipline engine
 */
export class TruthDiscipline {
  /**
   * Infer truth type from record
   */
  inferTruthType(record: TruthRecord): TruthValue {
    if (record.quarantineCapsule) {
      return TruthValue.FAIL;
    }
    
    if (record.candidateSet) {
      return TruthValue.AMBIG;
    }
    
    if (record.residualLedger) {
      return TruthValue.NEAR;
    }
    
    if (record.witnessPtr && record.replayPtr) {
      return TruthValue.OK;
    }
    
    return TruthValue.FAIL;
  }
  
  /**
   * Check valid transition
   */
  isValidTransition(from: TruthValue, to: TruthValue): boolean {
    // Valid: AMBIG→NEAR, NEAR→OK, *→FAIL
    // Invalid: OK→NEAR, OK→AMBIG, NEAR→AMBIG
    const validTransitions: Record<TruthValue, TruthValue[]> = {
      [TruthValue.AMBIG]: [TruthValue.NEAR, TruthValue.FAIL],
      [TruthValue.NEAR]: [TruthValue.OK, TruthValue.FAIL],
      [TruthValue.OK]: [TruthValue.FAIL],
      [TruthValue.FAIL]: []
    };
    
    return validTransitions[from]?.includes(to) ?? false;
  }
  
  /**
   * Promote truth
   */
  promote(record: TruthRecord, evidence: unknown): TruthRecord {
    const current = this.inferTruthType(record);
    
    if (current === TruthValue.AMBIG) {
      return {
        ...record,
        truth: TruthValue.NEAR,
        candidateSet: undefined,
        residualLedger: evidence
      };
    }
    
    if (current === TruthValue.NEAR) {
      return {
        ...record,
        truth: TruthValue.OK,
        residualLedger: undefined,
        witnessPtr: hashString(JSON.stringify(evidence)),
        replayPtr: hashString(`replay_${Date.now()}`)
      };
    }
    
    return record;
  }
  
  /**
   * Refute to FAIL
   */
  refute(record: TruthRecord, counterwitness: unknown): TruthRecord {
    return {
      ...record,
      truth: TruthValue.FAIL,
      quarantineCapsule: counterwitness
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
// SECTION 6: KAPPA CONSERVATION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Kappa ledger
 */
export interface KappaLedger {
  pre: number;
  post: number;
  spent: number;
  leak: number;
}

/**
 * Kappa manager (κ_pre = κ_post + κ_spent + κ_leak)
 */
export class KappaManager {
  private ledger: KappaLedger = { pre: 1.0, post: 1.0, spent: 0, leak: 0 };
  
  /**
   * Begin operation with budget
   */
  beginOperation(budget: number): void {
    this.ledger.pre = budget;
    this.ledger.post = budget;
    this.ledger.spent = 0;
    this.ledger.leak = 0;
  }
  
  /**
   * Spend kappa
   */
  spend(amount: number): boolean {
    if (this.ledger.post < amount) {
      return false;
    }
    
    this.ledger.post -= amount;
    this.ledger.spent += amount;
    return true;
  }
  
  /**
   * Record leak
   */
  recordLeak(amount: number): void {
    this.ledger.post -= amount;
    this.ledger.leak += amount;
  }
  
  /**
   * Verify conservation
   */
  verifyConservation(): boolean {
    const expected = this.ledger.pre;
    const actual = this.ledger.post + this.ledger.spent + this.ledger.leak;
    return Math.abs(expected - actual) < 0.0001;
  }
  
  /**
   * Get remaining budget
   */
  getRemainingBudget(): number {
    return this.ledger.post;
  }
  
  /**
   * Get ledger
   */
  getLedger(): KappaLedger {
    return { ...this.ledger };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: COMPLETE ORCHESTRATOR
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * System configuration
 */
export interface SystemConfig {
  msId: ManuscriptID;
  defaultCorridor: CorridorBudgets;
  maxHubSet: number;
}

/**
 * System state
 */
export interface SystemState {
  graph: MyceliumGraph;
  router: RouterV2;
  truthDiscipline: TruthDiscipline;
  kappaManager: KappaManager;
  truthRecords: Map<string, TruthRecord>;
}

/**
 * Integration result
 */
export type IntegrationResult<T> =
  | { type: "OK"; value: T; truth: TruthValue; kappa: KappaLedger }
  | { type: "NEAR"; value: T; residual: string[]; kappa: KappaLedger }
  | { type: "AMBIG"; candidates: T[]; evidencePlan: string[]; kappa: KappaLedger }
  | { type: "FAIL"; error: string; quarantine?: unknown; kappa: KappaLedger };

/**
 * Complete Integration Orchestrator
 */
export class IntegrationOrchestrator {
  private config: SystemConfig;
  private state: SystemState;
  
  // Subsystem registrations (would be actual implementations)
  private domainPacks?: DomainPackSubsystem;
  private metroRouting?: MetroRoutingSubsystem;
  private selfDriving?: SelfDrivingSubsystem;
  private publication?: PublicationSubsystem;
  private symbolTable?: SymbolTableSubsystem;
  private certificates?: CertificateSubsystem;
  private obligations?: ObligationSubsystem;
  private conflicts?: ConflictSubsystem;
  private tricompiler?: TricompilerSubsystem;
  
  constructor(config?: Partial<SystemConfig>) {
    this.config = {
      msId: config?.msId ?? { code: "2103", base4: "2103", seed: "AWAKENING_OS" },
      defaultCorridor: config?.defaultCorridor ?? {
        kappa: 1.0,
        beta: 30000,
        chi: 4194304,
        epsilon: 0.01,
        phi: 0.8
      },
      maxHubSet: config?.maxHubSet ?? 6
    };
    
    this.state = {
      graph: new MyceliumGraph(),
      router: new RouterV2(),
      truthDiscipline: new TruthDiscipline(),
      kappaManager: new KappaManager(),
      truthRecords: new Map()
    };
  }
  
  /**
   * Register subsystems
   */
  registerSubsystems(subsystems: {
    domainPacks?: DomainPackSubsystem;
    metroRouting?: MetroRoutingSubsystem;
    selfDriving?: SelfDrivingSubsystem;
    publication?: PublicationSubsystem;
    symbolTable?: SymbolTableSubsystem;
    certificates?: CertificateSubsystem;
    obligations?: ObligationSubsystem;
    conflicts?: ConflictSubsystem;
    tricompiler?: TricompilerSubsystem;
  }): void {
    if (subsystems.domainPacks) this.domainPacks = subsystems.domainPacks;
    if (subsystems.metroRouting) this.metroRouting = subsystems.metroRouting;
    if (subsystems.selfDriving) this.selfDriving = subsystems.selfDriving;
    if (subsystems.publication) this.publication = subsystems.publication;
    if (subsystems.symbolTable) this.symbolTable = subsystems.symbolTable;
    if (subsystems.certificates) this.certificates = subsystems.certificates;
    if (subsystems.obligations) this.obligations = subsystems.obligations;
    if (subsystems.conflicts) this.conflicts = subsystems.conflicts;
    if (subsystems.tricompiler) this.tricompiler = subsystems.tricompiler;
  }
  
  /**
   * Execute operation with full truth discipline
   */
  async execute<T>(
    operation: string,
    params: unknown,
    corridor?: CorridorBudgets
  ): Promise<IntegrationResult<T>> {
    const budgets = corridor ?? this.config.defaultCorridor;
    
    // Begin kappa tracking
    this.state.kappaManager.beginOperation(budgets.kappa);
    
    try {
      // Route operation
      const route = this.routeOperation(operation);
      
      // Spend kappa for routing
      if (!this.state.kappaManager.spend(0.01 * route.length)) {
        return {
          type: "FAIL",
          error: "Insufficient kappa for routing",
          kappa: this.state.kappaManager.getLedger()
        };
      }
      
      // Execute through route
      const result = await this.executeRoute<T>(operation, params, route, budgets);
      
      // Verify kappa conservation
      if (!this.state.kappaManager.verifyConservation()) {
        this.state.kappaManager.recordLeak(0.001);  // Account for rounding
      }
      
      return {
        ...result,
        kappa: this.state.kappaManager.getLedger()
      };
      
    } catch (e) {
      return {
        type: "FAIL",
        error: e instanceof Error ? e.message : "Unknown error",
        kappa: this.state.kappaManager.getLedger()
      };
    }
  }
  
  /**
   * Route operation to hub sequence
   */
  private routeOperation(operation: string): string[] {
    // Simplified routing based on operation type
    const route = [...MANDATORY_SIGNATURE];
    
    if (operation.includes("compile")) route.push("AppE");
    if (operation.includes("verify")) route.push("AppI");
    if (operation.includes("publish")) route.push("AppO");
    if (operation.includes("conflict")) route.push("AppK");
    
    return route;
  }
  
  /**
   * Execute through route
   */
  private async executeRoute<T>(
    operation: string,
    params: unknown,
    route: string[],
    budgets: CorridorBudgets
  ): Promise<Omit<IntegrationResult<T>, "kappa">> {
    // Simulate execution through hubs
    let currentTruth = TruthValue.AMBIG;
    let result: T | undefined;
    const residuals: string[] = [];
    
    for (const hub of route) {
      // Spend kappa per hub
      this.state.kappaManager.spend(0.02);
      
      // Hub-specific processing
      switch (hub) {
        case "AppI":
          // Truth discipline
          currentTruth = this.state.truthDiscipline.inferTruthType({
            truth: currentTruth,
            witnessPtr: hashString(JSON.stringify(params))
          });
          break;
        case "AppM":
          // Replay/serialization
          break;
        case "AppE":
          // Operator execution
          break;
      }
    }
    
    // Simulate result based on operation
    result = { operation, params, route, truth: currentTruth } as T;
    
    if (currentTruth === TruthValue.OK) {
      return { type: "OK", value: result, truth: TruthValue.OK };
    }
    
    if (currentTruth === TruthValue.NEAR) {
      return { type: "NEAR", value: result, residual: residuals };
    }
    
    if (currentTruth === TruthValue.AMBIG) {
      return {
        type: "AMBIG",
        candidates: [result],
        evidencePlan: ["Provide discriminator evidence"]
      };
    }
    
    return { type: "FAIL", error: "Operation failed" };
  }
  
  /**
   * Create global address
   */
  createAddress(chapter: number, lens: Lens, facet: number, atom: string): GlobalAddr {
    const omega = chapter - 1;
    const station = omega.toString(4).padStart(4, '0');
    
    return {
      ms: this.config.msId,
      chapter,
      station,
      lens,
      facet,
      atom
    };
  }
  
  /**
   * Add vertex to graph
   */
  addVertex(addr: GlobalAddr): void {
    this.state.graph.addVertex(addr);
  }
  
  /**
   * Add edge to graph
   */
  addEdge(edge: LinkEdge): void {
    this.state.graph.addEdge(edge);
  }
  
  /**
   * Compute hub set
   */
  computeHubSet(addr: GlobalAddr, truth: TruthValue): HubSet {
    return this.state.router.computeHubSet(addr, truth);
  }
  
  /**
   * Get system statistics
   */
  getStats(): SystemStats {
    const graphStats = this.state.graph.getStats();
    
    return {
      msId: this.config.msId.code,
      vertices: graphStats.vertices,
      edges: graphStats.edges,
      truthRecords: this.state.truthRecords.size,
      kappaBalance: this.state.kappaManager.getRemainingBudget(),
      subsystemsRegistered: {
        domainPacks: !!this.domainPacks,
        metroRouting: !!this.metroRouting,
        selfDriving: !!this.selfDriving,
        publication: !!this.publication,
        symbolTable: !!this.symbolTable,
        certificates: !!this.certificates,
        obligations: !!this.obligations,
        conflicts: !!this.conflicts,
        tricompiler: !!this.tricompiler
      }
    };
  }
  
  /**
   * Get configuration
   */
  getConfig(): SystemConfig {
    return { ...this.config };
  }
}

export interface SystemStats {
  msId: string;
  vertices: number;
  edges: number;
  truthRecords: number;
  kappaBalance: number;
  subsystemsRegistered: {
    domainPacks: boolean;
    metroRouting: boolean;
    selfDriving: boolean;
    publication: boolean;
    symbolTable: boolean;
    certificates: boolean;
    obligations: boolean;
    conflicts: boolean;
    tricompiler: boolean;
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Enums
  TruthValue,
  EdgeKind,
  Lens,
  
  // Constants
  ARC_HUB_MAP,
  LENS_BASE_MAP,
  FACET_BASE_MAP,
  TRUTH_OVERLAY_MAP,
  MANDATORY_SIGNATURE,
  
  // Classes
  RouterV2,
  MyceliumGraph,
  TruthDiscipline,
  KappaManager,
  IntegrationOrchestrator
};
