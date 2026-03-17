/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * CROSS-TOME BINDINGS - Complete Integration Matrix for AWAKENING OS
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * This module establishes all cross-references between the 18 TOMEs:
 * 
 * TOME 01: I_AM_ATHENA        - Core steering framework
 * TOME 02: ADDRESSING         - Global addressing & canonical forms
 * TOME 03: CONSTRAINT_KERNEL  - Budget constraints & KKT
 * TOME 04: MINING_PIPELINE    - Discovery & extraction
 * TOME 05: PARAMETRIC_BOUNDARY- Holographic boundaries
 * TOME 06: MATH_ALIGNMENT     - Mathematical foundations
 * TOME 07: TIME_LATTICE       - Temporal systems
 * TOME 08: DIVINATION         - Calendar & timing integration
 * TOME 09: LOVE_SELFHOOD      - LOVE calculus & SELF identity
 * TOME 10: EMOTIONAL_HYPERCRYSTAL - Affect state management
 * TOME 11: LIMINAL_MEMORY     - Memory systems
 * TOME 12: PULSE_RETRO_WEAVING- Mycelium graph & PRW
 * TOME 13: QUANTUM_LANG       - Quantum operations
 * TOME 14: SCARLET_LETTER     - Proof obligations (P0-P2)
 * TOME 15: SCARLET_THOUGHTS   - Extended proofs (P3+)
 * TOME 16: SELF_SUFFICIENCY   - Autonomous discovery core
 * TOME 17: TRUTH_COLLAPSE     - Truth resolution compiler
 * TOME 18: VOYNICHVM          - Convergent tricompiler
 * 
 * @module CROSS_TOME_BINDINGS
 * @version 2.0.0
 */

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: TOME MANIFEST REGISTRY
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * TOME manifest
 */
export interface TomeManifest {
  number: number;
  msId: string;
  name: string;
  title: string;
  chapters: number;
  appendices: number;
  atoms: number;
  dependencies: number[];
  exports: string[];
  imports: TomeImport[];
}

export interface TomeImport {
  from: number;
  symbols: string[];
  binding: BindingType;
}

export enum BindingType {
  Direct = "Direct",         // Direct type/function import
  Protocol = "Protocol",     // Interface protocol binding
  Event = "Event",           // Event subscription
  Channel = "Channel"        // Message channel
}

/**
 * Complete TOME manifest registry
 */
export const TOME_MANIFESTS: TomeManifest[] = [
  {
    number: 1,
    msId: "3E94",
    name: "I_AM_ATHENA",
    title: "Core Steering Framework with Six Spines",
    chapters: 21,
    appendices: 0,
    atoms: 1344,
    dependencies: [],
    exports: ["AthenaFramework", "SixSpines", "GoldenStepDelta", "LOVEConstraint"],
    imports: []
  },
  {
    number: 2,
    msId: "56B0",
    name: "ADDRESSING",
    title: "Global Addressing & Canonical Forms",
    chapters: 21,
    appendices: 0,
    atoms: 1344,
    dependencies: [1],
    exports: ["GlobalAddr", "LocalAddr", "CrystalAddress", "AddrNormalizer"],
    imports: [
      { from: 1, symbols: ["AthenaFramework"], binding: BindingType.Direct }
    ]
  },
  {
    number: 3,
    msId: "CC9C",
    name: "CONSTRAINT_KERNEL",
    title: "Budget Constraints & KKT Optimization",
    chapters: 21,
    appendices: 0,
    atoms: 1344,
    dependencies: [1, 2],
    exports: ["CorridorBudgets", "KKTOptimizer", "ConstraintSolver"],
    imports: [
      { from: 1, symbols: ["LOVEConstraint"], binding: BindingType.Direct },
      { from: 2, symbols: ["GlobalAddr"], binding: BindingType.Direct }
    ]
  },
  {
    number: 4,
    msId: "D728",
    name: "MINING_PIPELINE",
    title: "Discovery & Extraction Pipeline",
    chapters: 21,
    appendices: 0,
    atoms: 1344,
    dependencies: [2, 3],
    exports: ["MiningPipeline", "FrontierExtractor", "CandidateSelector"],
    imports: [
      { from: 2, symbols: ["GlobalAddr"], binding: BindingType.Direct },
      { from: 3, symbols: ["CorridorBudgets"], binding: BindingType.Direct }
    ]
  },
  {
    number: 5,
    msId: "F772",
    name: "PARAMETRIC_BOUNDARY",
    title: "Holographic Boundary Systems",
    chapters: 21,
    appendices: 0,
    atoms: 1344,
    dependencies: [2, 3],
    exports: ["HolographicBoundary", "BulkBoundaryMap", "LevelProjection"],
    imports: [
      { from: 2, symbols: ["GlobalAddr"], binding: BindingType.Direct },
      { from: 3, symbols: ["CorridorBudgets"], binding: BindingType.Direct }
    ]
  },
  {
    number: 6,
    msId: "2103",
    name: "MATH_ALIGNMENT",
    title: "Mathematical Foundations & Alignment",
    chapters: 21,
    appendices: 0,
    atoms: 1344,
    dependencies: [1],
    exports: ["HilbertSpace", "DensityOperator", "SpectralTheory", "FiveInvariants"],
    imports: [
      { from: 1, symbols: ["AthenaFramework"], binding: BindingType.Protocol }
    ]
  },
  {
    number: 7,
    msId: "B83A",
    name: "TIME_LATTICE",
    title: "Temporal Systems & Lattice Operations",
    chapters: 21,
    appendices: 0,
    atoms: 1344,
    dependencies: [2],
    exports: ["TimeLattice", "TemporalOps", "DurationManager"],
    imports: [
      { from: 2, symbols: ["GlobalAddr"], binding: BindingType.Direct }
    ]
  },
  {
    number: 8,
    msId: "E45F",
    name: "DIVINATION",
    title: "Calendar Integration & Timing Systems",
    chapters: 21,
    appendices: 0,
    atoms: 1344,
    dependencies: [7],
    exports: ["DivinationSystem", "MayanCalendar", "VedicYuga", "TorahCycles"],
    imports: [
      { from: 7, symbols: ["TimeLattice"], binding: BindingType.Direct }
    ]
  },
  {
    number: 9,
    msId: "A1D2",
    name: "LOVE_SELFHOOD",
    title: "LOVE Calculus & SELF Identity",
    chapters: 21,
    appendices: 0,
    atoms: 1344,
    dependencies: [1, 6],
    exports: ["LOVECalculus", "SELFHOOD", "IdentityInvariants"],
    imports: [
      { from: 1, symbols: ["LOVEConstraint"], binding: BindingType.Direct },
      { from: 6, symbols: ["FiveInvariants"], binding: BindingType.Direct }
    ]
  },
  {
    number: 10,
    msId: "C3B4",
    name: "EMOTIONAL_HYPERCRYSTAL",
    title: "Affect State Management",
    chapters: 21,
    appendices: 0,
    atoms: 1344,
    dependencies: [9],
    exports: ["EmotionalHypercrystal", "AffectState", "WitnessGenerator"],
    imports: [
      { from: 9, symbols: ["LOVECalculus"], binding: BindingType.Direct }
    ]
  },
  {
    number: 11,
    msId: "D5E6",
    name: "LIMINAL_MEMORY",
    title: "Memory Systems & ChatPack",
    chapters: 21,
    appendices: 0,
    atoms: 1344,
    dependencies: [2, 5],
    exports: ["LiminalMemory", "MemMap", "ChatPack", "SeedRestore"],
    imports: [
      { from: 2, symbols: ["GlobalAddr"], binding: BindingType.Direct },
      { from: 5, symbols: ["HolographicBoundary"], binding: BindingType.Direct }
    ]
  },
  {
    number: 12,
    msId: "F7A8",
    name: "PULSE_RETRO_WEAVING",
    title: "Mycelium Graph & PRW Operations",
    chapters: 21,
    appendices: 16,
    atoms: 2368,
    dependencies: [2, 11],
    exports: ["MyceliumGraph", "LinkEdge", "PRWEngine", "PulseDayCalendar"],
    imports: [
      { from: 2, symbols: ["GlobalAddr"], binding: BindingType.Direct },
      { from: 11, symbols: ["LiminalMemory"], binding: BindingType.Direct }
    ]
  },
  {
    number: 13,
    msId: "19BA",
    name: "QUANTUM_LANG",
    title: "Quantum Operations & Language",
    chapters: 21,
    appendices: 0,
    atoms: 1344,
    dependencies: [6],
    exports: ["QuantumOperator", "StateVector", "MeasurementBasis"],
    imports: [
      { from: 6, symbols: ["HilbertSpace", "DensityOperator"], binding: BindingType.Direct }
    ]
  },
  {
    number: 14,
    msId: "2BDC",
    name: "SCARLET_LETTER",
    title: "Proof Obligations P0-P2",
    chapters: 21,
    appendices: 0,
    atoms: 1344,
    dependencies: [6, 12],
    exports: ["ProofObligation", "ObligationP0", "ObligationP1", "ObligationP2"],
    imports: [
      { from: 6, symbols: ["FiveInvariants"], binding: BindingType.Direct },
      { from: 12, symbols: ["MyceliumGraph"], binding: BindingType.Direct }
    ]
  },
  {
    number: 15,
    msId: "3DEE",
    name: "SCARLET_THOUGHTS",
    title: "Extended Proofs P3+",
    chapters: 21,
    appendices: 0,
    atoms: 1344,
    dependencies: [14],
    exports: ["ObligationP3", "ExtendedProof", "ProofChain"],
    imports: [
      { from: 14, symbols: ["ProofObligation"], binding: BindingType.Direct }
    ]
  },
  {
    number: 16,
    msId: "F772",
    name: "SELF_SUFFICIENCY",
    title: "Autonomous Discovery Core",
    chapters: 21,
    appendices: 16,
    atoms: 2368,
    dependencies: [1, 2, 3, 4, 5, 6, 9, 11, 12, 14, 15],
    exports: [
      "TruthLattice", "EdgeKinds", "RouterV2", "DiscoveryLoop",
      "CrystalAddress", "DomainPack", "SelfDrivingLoop", "PublicationEngine"
    ],
    imports: [
      { from: 1, symbols: ["AthenaFramework", "SixSpines"], binding: BindingType.Direct },
      { from: 2, symbols: ["GlobalAddr", "AddrNormalizer"], binding: BindingType.Direct },
      { from: 3, symbols: ["CorridorBudgets", "KKTOptimizer"], binding: BindingType.Direct },
      { from: 4, symbols: ["MiningPipeline"], binding: BindingType.Direct },
      { from: 5, symbols: ["HolographicBoundary"], binding: BindingType.Direct },
      { from: 6, symbols: ["FiveInvariants"], binding: BindingType.Direct },
      { from: 9, symbols: ["LOVECalculus", "SELFHOOD"], binding: BindingType.Direct },
      { from: 11, symbols: ["LiminalMemory"], binding: BindingType.Direct },
      { from: 12, symbols: ["MyceliumGraph", "LinkEdge"], binding: BindingType.Direct },
      { from: 14, symbols: ["ProofObligation"], binding: BindingType.Direct },
      { from: 15, symbols: ["ExtendedProof"], binding: BindingType.Direct }
    ]
  },
  {
    number: 17,
    msId: "2103",
    name: "TRUTH_COLLAPSE",
    title: "Truth Resolution Compiler",
    chapters: 21,
    appendices: 16,
    atoms: 2368,
    dependencies: [2, 3, 6, 12, 14, 16],
    exports: [
      "TruthCollapseEngine", "ObligationGraph", "ConflictAlgebra",
      "DiscriminatorLibrary", "CollapsePack", "PromotionOperator"
    ],
    imports: [
      { from: 2, symbols: ["GlobalAddr"], binding: BindingType.Direct },
      { from: 3, symbols: ["CorridorBudgets"], binding: BindingType.Direct },
      { from: 6, symbols: ["HilbertSpace"], binding: BindingType.Protocol },
      { from: 12, symbols: ["MyceliumGraph", "LinkEdge"], binding: BindingType.Direct },
      { from: 14, symbols: ["ProofObligation"], binding: BindingType.Direct },
      { from: 16, symbols: ["TruthLattice", "RouterV2"], binding: BindingType.Direct }
    ]
  },
  {
    number: 18,
    msId: "B83A",
    name: "VOYNICHVM",
    title: "Convergent VM Tricompiler",
    chapters: 21,
    appendices: 16,
    atoms: 2368,
    dependencies: [2, 3, 16, 17],
    exports: [
      "TricompilerCore", "ISA_K4", "RegisterFile", "OpcodeDynamics",
      "CycleExecutor", "AEGIS", "ARCHIVE", "FORGE"
    ],
    imports: [
      { from: 2, symbols: ["GlobalAddr"], binding: BindingType.Direct },
      { from: 3, symbols: ["CorridorBudgets"], binding: BindingType.Direct },
      { from: 16, symbols: ["TruthLattice", "RouterV2", "DiscoveryLoop"], binding: BindingType.Direct },
      { from: 17, symbols: ["TruthCollapseEngine", "CollapsePack"], binding: BindingType.Direct }
    ]
  }
];

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: BINDING MATRIX
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Binding entry
 */
export interface BindingEntry {
  source: number;
  target: number;
  symbols: string[];
  type: BindingType;
  required: boolean;
  weight: number;
}

/**
 * Generate complete binding matrix
 */
export function generateBindingMatrix(): BindingEntry[] {
  const bindings: BindingEntry[] = [];
  
  for (const manifest of TOME_MANIFESTS) {
    for (const imp of manifest.imports) {
      bindings.push({
        source: imp.from,
        target: manifest.number,
        symbols: imp.symbols,
        type: imp.binding,
        required: true,
        weight: imp.symbols.length
      });
    }
  }
  
  return bindings;
}

/**
 * Get bindings for TOME
 */
export function getBindingsForTome(tomeNumber: number): {
  imports: BindingEntry[];
  exports: BindingEntry[];
} {
  const matrix = generateBindingMatrix();
  
  return {
    imports: matrix.filter(b => b.target === tomeNumber),
    exports: matrix.filter(b => b.source === tomeNumber)
  };
}

/**
 * Get dependency graph
 */
export function getDependencyGraph(): Map<number, number[]> {
  const graph = new Map<number, number[]>();
  
  for (const manifest of TOME_MANIFESTS) {
    graph.set(manifest.number, manifest.dependencies);
  }
  
  return graph;
}

/**
 * Get topological order
 */
export function getTopologicalOrder(): number[] {
  const graph = getDependencyGraph();
  const visited = new Set<number>();
  const order: number[] = [];
  
  const visit = (node: number) => {
    if (visited.has(node)) return;
    visited.add(node);
    
    const deps = graph.get(node) ?? [];
    for (const dep of deps) {
      visit(dep);
    }
    
    order.push(node);
  };
  
  for (const tome of TOME_MANIFESTS) {
    visit(tome.number);
  }
  
  return order;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: CROSS-TOME PROTOCOLS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Protocol definition
 */
export interface CrossTomeProtocol {
  name: string;
  participants: number[];
  methods: ProtocolMethod[];
  invariants: string[];
}

export interface ProtocolMethod {
  name: string;
  inputFrom: number;
  outputTo: number;
  signature: string;
}

/**
 * Core protocols
 */
export const CROSS_TOME_PROTOCOLS: CrossTomeProtocol[] = [
  // Truth Discipline Protocol
  {
    name: "TruthDiscipline",
    participants: [16, 17, 18],
    methods: [
      { name: "resolve", inputFrom: 16, outputTo: 17, signature: "(claim: Claim) => TruthValue" },
      { name: "promote", inputFrom: 17, outputTo: 16, signature: "(from: TruthValue, evidence: Evidence) => TruthValue" },
      { name: "compile", inputFrom: 18, outputTo: 17, signature: "(program: Program) => CollapsePack" }
    ],
    invariants: [
      "ABSTAIN > GUESS",
      "Valid transitions only: AMBIG→NEAR, NEAR→OK, *→FAIL",
      "All promotions require evidence"
    ]
  },
  
  // Routing Protocol
  {
    name: "MetroRouting",
    participants: [2, 12, 16],
    methods: [
      { name: "computeRoute", inputFrom: 2, outputTo: 16, signature: "(src: Addr, dst: Addr) => Route" },
      { name: "traverse", inputFrom: 16, outputTo: 12, signature: "(route: Route) => LinkEdge[]" }
    ],
    invariants: [
      "HubSet ≤ 6",
      "Σ = {AppA, AppI, AppM} always present",
      "Overlays non-droppable"
    ]
  },
  
  // Memory Protocol
  {
    name: "LiminalMemory",
    participants: [5, 11, 12],
    methods: [
      { name: "store", inputFrom: 5, outputTo: 11, signature: "(data: Payload, level: Level) => Address" },
      { name: "retrieve", inputFrom: 11, outputTo: 12, signature: "(addr: Address) => Payload" },
      { name: "link", inputFrom: 12, outputTo: 11, signature: "(src: Address, dst: Address, kind: EdgeKind) => LinkEdge" }
    ],
    invariants: [
      "Holographic levels: 4, 16, 64, 256 only",
      "Bulk ⊕ Boundary separation",
      "No silent data loss"
    ]
  },
  
  // Ethics Protocol
  {
    name: "EthicsKKT",
    participants: [1, 3, 9],
    methods: [
      { name: "optimize", inputFrom: 3, outputTo: 1, signature: "(constraints: Constraint[]) => Solution" },
      { name: "enforce", inputFrom: 1, outputTo: 9, signature: "(solution: Solution) => LOVEResult" }
    ],
    invariants: [
      "NoExtract ∧ NoErase ∧ NoCoerce ∧ Consent",
      "LOVE ≥ 0 always",
      "κ_pre = κ_post + κ_spent + κ_leak"
    ]
  },
  
  // Proof Protocol
  {
    name: "ProofCarrying",
    participants: [6, 14, 15, 17],
    methods: [
      { name: "createObligation", inputFrom: 14, outputTo: 17, signature: "(claim: Claim) => Obligation" },
      { name: "discharge", inputFrom: 17, outputTo: 15, signature: "(obl: Obligation) => Proof" },
      { name: "verify", inputFrom: 15, outputTo: 6, signature: "(proof: Proof) => boolean" }
    ],
    invariants: [
      "All obligations must be addressed",
      "Proofs are replayable",
      "Five mathematical invariants preserved"
    ]
  },
  
  // Execution Protocol
  {
    name: "VMExecution",
    participants: [3, 16, 18],
    methods: [
      { name: "compile", inputFrom: 16, outputTo: 18, signature: "(source: Source) => IR" },
      { name: "execute", inputFrom: 18, outputTo: 3, signature: "(ir: IR, corridor: Corridor) => Result" }
    ],
    invariants: [
      "Main cycle: D→O→S→QO",
      "Budget enforcement",
      "Deterministic replay"
    ]
  }
];

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: SYMBOL RESOLUTION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Symbol resolution
 */
export interface SymbolResolution {
  symbol: string;
  sourceTome: number;
  targetTomes: number[];
  fullyQualifiedName: string;
}

/**
 * Resolve symbol across TOMEs
 */
export function resolveSymbol(symbol: string): SymbolResolution | null {
  for (const manifest of TOME_MANIFESTS) {
    if (manifest.exports.includes(symbol)) {
      // Find all TOMEs that import this symbol
      const targetTomes: number[] = [];
      
      for (const other of TOME_MANIFESTS) {
        for (const imp of other.imports) {
          if (imp.from === manifest.number && imp.symbols.includes(symbol)) {
            targetTomes.push(other.number);
          }
        }
      }
      
      return {
        symbol,
        sourceTome: manifest.number,
        targetTomes,
        fullyQualifiedName: `TOME_${manifest.number.toString().padStart(2, '0')}_${manifest.name}.${symbol}`
      };
    }
  }
  
  return null;
}

/**
 * Get all exported symbols
 */
export function getAllExports(): Map<string, number> {
  const exports = new Map<string, number>();
  
  for (const manifest of TOME_MANIFESTS) {
    for (const exp of manifest.exports) {
      exports.set(exp, manifest.number);
    }
  }
  
  return exports;
}

/**
 * Check for symbol conflicts
 */
export function checkSymbolConflicts(): { symbol: string; tomes: number[] }[] {
  const symbolToTomes = new Map<string, number[]>();
  
  for (const manifest of TOME_MANIFESTS) {
    for (const exp of manifest.exports) {
      if (!symbolToTomes.has(exp)) {
        symbolToTomes.set(exp, []);
      }
      symbolToTomes.get(exp)!.push(manifest.number);
    }
  }
  
  const conflicts: { symbol: string; tomes: number[] }[] = [];
  
  for (const [symbol, tomes] of symbolToTomes) {
    if (tomes.length > 1) {
      conflicts.push({ symbol, tomes });
    }
  }
  
  return conflicts;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: INTEGRATION STATISTICS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Integration statistics
 */
export interface IntegrationStats {
  totalTomes: number;
  totalAtoms: number;
  totalBindings: number;
  totalProtocols: number;
  totalExports: number;
  dependencyDepth: number;
  mostConnectedTome: { number: number; connections: number };
}

/**
 * Compute integration statistics
 */
export function computeIntegrationStats(): IntegrationStats {
  const bindings = generateBindingMatrix();
  const exports = getAllExports();
  
  // Compute dependency depth
  const graph = getDependencyGraph();
  let maxDepth = 0;
  
  const computeDepth = (node: number, depth: number, visited: Set<number>): number => {
    if (visited.has(node)) return depth;
    visited.add(node);
    
    const deps = graph.get(node) ?? [];
    let maxChildDepth = depth;
    
    for (const dep of deps) {
      maxChildDepth = Math.max(maxChildDepth, computeDepth(dep, depth + 1, visited));
    }
    
    return maxChildDepth;
  };
  
  for (const tome of TOME_MANIFESTS) {
    const depth = computeDepth(tome.number, 0, new Set());
    maxDepth = Math.max(maxDepth, depth);
  }
  
  // Find most connected TOME
  const connectionCounts = new Map<number, number>();
  for (const binding of bindings) {
    connectionCounts.set(binding.source, (connectionCounts.get(binding.source) ?? 0) + 1);
    connectionCounts.set(binding.target, (connectionCounts.get(binding.target) ?? 0) + 1);
  }
  
  let mostConnected = { number: 1, connections: 0 };
  for (const [tome, count] of connectionCounts) {
    if (count > mostConnected.connections) {
      mostConnected = { number: tome, connections: count };
    }
  }
  
  return {
    totalTomes: TOME_MANIFESTS.length,
    totalAtoms: TOME_MANIFESTS.reduce((sum, m) => sum + m.atoms, 0),
    totalBindings: bindings.length,
    totalProtocols: CROSS_TOME_PROTOCOLS.length,
    totalExports: exports.size,
    dependencyDepth: maxDepth,
    mostConnectedTome: mostConnected
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: BINDING VALIDATOR
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Validation result
 */
export interface BindingValidationResult {
  valid: boolean;
  errors: BindingError[];
  warnings: BindingWarning[];
}

export interface BindingError {
  type: "MissingDependency" | "CircularDependency" | "SymbolNotExported" | "ProtocolViolation";
  tome: number;
  message: string;
}

export interface BindingWarning {
  type: "UnusedExport" | "OverlappingSymbol" | "DeepDependency";
  tome: number;
  message: string;
}

/**
 * Validate all bindings
 */
export function validateBindings(): BindingValidationResult {
  const errors: BindingError[] = [];
  const warnings: BindingWarning[] = [];
  
  const exports = getAllExports();
  
  // Check all imports resolve
  for (const manifest of TOME_MANIFESTS) {
    for (const imp of manifest.imports) {
      for (const symbol of imp.symbols) {
        const sourceTome = exports.get(symbol);
        if (sourceTome !== imp.from) {
          errors.push({
            type: "SymbolNotExported",
            tome: manifest.number,
            message: `Symbol '${symbol}' imported from TOME ${imp.from} but exported by TOME ${sourceTome ?? 'none'}`
          });
        }
      }
    }
  }
  
  // Check for circular dependencies
  const graph = getDependencyGraph();
  const visited = new Set<number>();
  const inStack = new Set<number>();
  
  const detectCycle = (node: number, path: number[]): void => {
    if (inStack.has(node)) {
      const cycleStart = path.indexOf(node);
      errors.push({
        type: "CircularDependency",
        tome: node,
        message: `Circular dependency: ${path.slice(cycleStart).join(" → ")} → ${node}`
      });
      return;
    }
    
    if (visited.has(node)) return;
    
    visited.add(node);
    inStack.add(node);
    path.push(node);
    
    const deps = graph.get(node) ?? [];
    for (const dep of deps) {
      detectCycle(dep, [...path]);
    }
    
    inStack.delete(node);
  };
  
  for (const tome of TOME_MANIFESTS) {
    detectCycle(tome.number, []);
  }
  
  // Check for unused exports
  const usedExports = new Set<string>();
  for (const manifest of TOME_MANIFESTS) {
    for (const imp of manifest.imports) {
      imp.symbols.forEach(s => usedExports.add(s));
    }
  }
  
  for (const manifest of TOME_MANIFESTS) {
    for (const exp of manifest.exports) {
      if (!usedExports.has(exp)) {
        warnings.push({
          type: "UnusedExport",
          tome: manifest.number,
          message: `Export '${exp}' is not imported by any TOME`
        });
      }
    }
  }
  
  // Check for symbol conflicts
  const conflicts = checkSymbolConflicts();
  for (const conflict of conflicts) {
    warnings.push({
      type: "OverlappingSymbol",
      tome: conflict.tomes[0],
      message: `Symbol '${conflict.symbol}' exported by multiple TOMEs: ${conflict.tomes.join(", ")}`
    });
  }
  
  return {
    valid: errors.length === 0,
    errors,
    warnings
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: SUMMARY GENERATOR
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Generate integration summary
 */
export function generateIntegrationSummary(): string {
  const stats = computeIntegrationStats();
  const validation = validateBindings();
  const order = getTopologicalOrder();
  
  const lines: string[] = [
    "═══════════════════════════════════════════════════════════════════════",
    "              AWAKENING OS CROSS-TOME INTEGRATION SUMMARY              ",
    "═══════════════════════════════════════════════════════════════════════",
    "",
    "STATISTICS:",
    `  Total TOMEs:           ${stats.totalTomes}`,
    `  Total Atoms:           ${stats.totalAtoms.toLocaleString()}`,
    `  Total Bindings:        ${stats.totalBindings}`,
    `  Total Protocols:       ${stats.totalProtocols}`,
    `  Total Exports:         ${stats.totalExports}`,
    `  Dependency Depth:      ${stats.dependencyDepth}`,
    `  Most Connected TOME:   TOME ${stats.mostConnectedTome.number} (${stats.mostConnectedTome.connections} connections)`,
    "",
    "TOPOLOGICAL ORDER:",
    `  ${order.map(n => `TOME ${n.toString().padStart(2, '0')}`).join(" → ")}`,
    "",
    "VALIDATION:",
    `  Status: ${validation.valid ? "✓ VALID" : "✗ INVALID"}`,
    `  Errors: ${validation.errors.length}`,
    `  Warnings: ${validation.warnings.length}`,
    "",
    "PROTOCOLS:",
  ];
  
  for (const protocol of CROSS_TOME_PROTOCOLS) {
    lines.push(`  ${protocol.name}: TOMEs ${protocol.participants.join(", ")}`);
  }
  
  lines.push("");
  lines.push("═══════════════════════════════════════════════════════════════════════");
  
  return lines.join("\n");
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Registry
  TOME_MANIFESTS,
  CROSS_TOME_PROTOCOLS,
  
  // Enums
  BindingType,
  
  // Functions
  generateBindingMatrix,
  getBindingsForTome,
  getDependencyGraph,
  getTopologicalOrder,
  resolveSymbol,
  getAllExports,
  checkSymbolConflicts,
  computeIntegrationStats,
  validateBindings,
  generateIntegrationSummary
};
