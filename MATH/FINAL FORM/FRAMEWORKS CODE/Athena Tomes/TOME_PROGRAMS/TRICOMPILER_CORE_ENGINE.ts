/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * TRICOMPILER CORE ENGINE - VoynichVM ISA & Execution Semantics
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * From VOYNICHVM_TRICOMPILER Ch02:
 * 
 * Core Components:
 *   - Token anatomy and parsing (Ch02.S1.a)
 *   - ISA_K4 opcode classes: D, O, S, QO (Ch02.S1.b)
 *   - FlagSet: Active/Fixed/Dissolved/Channeled/Sealed (Ch02.S1.c)
 *   - RegisterFileSpec: CHE/KE/OL/SAL/TAL/DAR/OR/CHOR (Ch02.S1.d)
 *   - OpcodeDynamics: state-transform generators (Ch02.F1.a)
 *   - MainCycleSchema: D→O→S→QO (Ch02.F1.b)
 * 
 * @module TRICOMPILER_CORE_ENGINE
 * @version 2.0.0
 */

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: ISA TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Opcode classes (K4 encoding)
 */
export enum OpcodeClass {
  D = "D",    // 00 - Drive toward FIXED
  O = "O",    // 01 - Drive toward ACTIVE
  S = "S",    // 10 - Enable transfer/phase change
  QO = "QO"   // 11 - Iterative circulation kernel
}

/**
 * K4 encoding map
 */
export const K4_ENCODE: Record<OpcodeClass, number> = {
  [OpcodeClass.D]: 0b00,
  [OpcodeClass.O]: 0b01,
  [OpcodeClass.S]: 0b10,
  [OpcodeClass.QO]: 0b11
};

export const K4_DECODE: Record<number, OpcodeClass> = {
  0b00: OpcodeClass.D,
  0b01: OpcodeClass.O,
  0b10: OpcodeClass.S,
  0b11: OpcodeClass.QO
};

/**
 * State flags
 */
export enum StateFlag {
  ACTIVE = "ACTIVE",
  FIXED = "FIXED",
  DISSOLVED = "DISSOLVED",
  CHANNELED = "CHANNELED",
  ITERATION = "ITERATION",
  SEALED = "SEALED",
  HALT = "HALT"
}

/**
 * Suffix to flag mapping
 */
export const SUFFIX_LIFT: Record<string, StateFlag[]> = {
  "y": [StateFlag.ACTIVE],
  "dy": [StateFlag.FIXED],
  "ol": [StateFlag.DISSOLVED],
  "or": [StateFlag.CHANNELED],
  "aiin": [StateFlag.ITERATION],
  "am": [StateFlag.SEALED]
};

/**
 * Registers
 */
export enum Register {
  CHE = "CHE",
  KE = "KE",
  OL = "OL",
  SAL = "SAL",
  TAL = "TAL",
  KAL = "KAL",
  DAR = "DAR",
  TAR = "TAR",
  OR = "OR",
  CHOR = "CHOR"
}

/**
 * Root to register mapping
 */
export const ROOT_REGISTER_MAP: Record<string, Register> = {
  "che": Register.CHE,
  "ke": Register.KE,
  "ol": Register.OL,
  "sal": Register.SAL,
  "tal": Register.TAL,
  "kal": Register.KAL,
  "dar": Register.DAR,
  "tar": Register.TAR,
  "or": Register.OR,
  "chor": Register.CHOR
};

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: TOKEN PARSING
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Token anatomy
 */
export interface TokenAnatomy {
  raw: string;
  prefix?: string;
  root: string;
  modifiers: string[];
  suffixes: string[];
}

/**
 * Instruction AST
 */
export interface InstrAST {
  opclass: OpcodeClass;
  root: string;
  mods: string[];
  state: Set<StateFlag>;
  raw: string;
  digest: string;
}

/**
 * Parse result
 */
export type ParseResult =
  | { type: "OK"; ast: InstrAST }
  | { type: "AMBIG"; candidates: InstrAST[]; evidencePlan: string[] }
  | { type: "FAIL"; reason: string; token: string };

/**
 * Token parser
 */
export class TokenParser {
  private opcodePatterns: Map<string, OpcodeClass> = new Map();
  
  constructor() {
    this.initializeOpcodePatterns();
  }
  
  private initializeOpcodePatterns(): void {
    // Prefix patterns for opcode detection
    this.opcodePatterns.set("d", OpcodeClass.D);
    this.opcodePatterns.set("o", OpcodeClass.O);
    this.opcodePatterns.set("s", OpcodeClass.S);
    this.opcodePatterns.set("q", OpcodeClass.QO);
  }
  
  /**
   * Parse token to anatomy
   */
  parseAnatomy(token: string): TokenAnatomy {
    const raw = token.toLowerCase().trim();
    
    // Extract prefix (first char if opcode indicator)
    let prefix: string | undefined;
    let rest = raw;
    
    if (this.opcodePatterns.has(raw[0])) {
      prefix = raw[0];
      rest = raw.slice(1);
    }
    
    // Extract suffixes
    const suffixes: string[] = [];
    for (const suffix of Object.keys(SUFFIX_LIFT)) {
      if (rest.endsWith(suffix)) {
        suffixes.push(suffix);
        rest = rest.slice(0, -suffix.length);
      }
    }
    
    // Extract modifiers (between root and suffix)
    const modifiers: string[] = [];
    const modPattern = /\.([\w]+)/g;
    let match;
    while ((match = modPattern.exec(rest)) !== null) {
      modifiers.push(match[1]);
    }
    rest = rest.replace(modPattern, "");
    
    return {
      raw: token,
      prefix,
      root: rest,
      modifiers,
      suffixes
    };
  }
  
  /**
   * Parse token to instruction AST
   */
  parseToken(token: string): ParseResult {
    const anatomy = this.parseAnatomy(token);
    
    // Determine opcode class
    let opclass: OpcodeClass | undefined;
    if (anatomy.prefix) {
      opclass = this.opcodePatterns.get(anatomy.prefix);
    }
    
    if (!opclass) {
      // Try to infer from root
      if (anatomy.root.startsWith("d")) opclass = OpcodeClass.D;
      else if (anatomy.root.startsWith("o")) opclass = OpcodeClass.O;
      else if (anatomy.root.startsWith("s")) opclass = OpcodeClass.S;
      else if (anatomy.root.startsWith("q")) opclass = OpcodeClass.QO;
    }
    
    if (!opclass) {
      // Ambiguous - return candidates
      return {
        type: "AMBIG",
        candidates: Object.values(OpcodeClass).map(oc => ({
          opclass: oc,
          root: anatomy.root,
          mods: anatomy.modifiers,
          state: this.liftFlags(anatomy.suffixes),
          raw: token,
          digest: this.digestAST(oc, anatomy.root, anatomy.modifiers)
        })),
        evidencePlan: ["Determine opcode from context", "Check corpus patterns"]
      };
    }
    
    // Extract state flags
    const state = this.liftFlags(anatomy.suffixes);
    
    // Check flag compatibility
    if (!this.checkFlagCompatibility(state)) {
      return {
        type: "FAIL",
        reason: "Incompatible flags",
        token
      };
    }
    
    const ast: InstrAST = {
      opclass,
      root: anatomy.root,
      mods: anatomy.modifiers,
      state,
      raw: token,
      digest: this.digestAST(opclass, anatomy.root, anatomy.modifiers)
    };
    
    return { type: "OK", ast };
  }
  
  /**
   * Lift suffixes to flags
   */
  liftFlags(suffixes: string[]): Set<StateFlag> {
    const flags = new Set<StateFlag>();
    
    for (const suffix of suffixes) {
      const lifted = SUFFIX_LIFT[suffix];
      if (lifted) {
        lifted.forEach(f => flags.add(f));
      }
    }
    
    return flags;
  }
  
  /**
   * Check flag compatibility (Ch02.S2.c)
   */
  private checkFlagCompatibility(flags: Set<StateFlag>): boolean {
    // HALT is exclusive
    if (flags.has(StateFlag.HALT) && flags.size > 1) {
      return false;
    }
    
    // ACTIVE and FIXED incompatible
    if (flags.has(StateFlag.ACTIVE) && flags.has(StateFlag.FIXED)) {
      return false;
    }
    
    return true;
  }
  
  private digestAST(opclass: OpcodeClass, root: string, mods: string[]): string {
    return hashString(`${opclass}:${root}:${mods.join(",")}`);
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
// SECTION 3: REGISTER FILE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Register value
 */
export interface RegisterValue {
  data: Uint8Array;
  type: string;
  lastWrite: number;
  hash: string;
}

/**
 * Register file
 */
export class RegisterFile {
  private registers: Map<Register, RegisterValue> = new Map();
  
  constructor() {
    this.initializeRegisters();
  }
  
  private initializeRegisters(): void {
    for (const reg of Object.values(Register)) {
      this.registers.set(reg, {
        data: new Uint8Array(0),
        type: "empty",
        lastWrite: 0,
        hash: hashString("")
      });
    }
  }
  
  /**
   * Read register (deterministic empty for unset)
   */
  read(reg: Register): RegisterValue {
    return this.registers.get(reg) ?? {
      data: new Uint8Array(0),
      type: "empty",
      lastWrite: 0,
      hash: hashString("")
    };
  }
  
  /**
   * Write register (explicit effect)
   */
  write(reg: Register, data: Uint8Array, type: string): void {
    this.registers.set(reg, {
      data,
      type,
      lastWrite: Date.now(),
      hash: hashString(Array.from(data).join(","))
    });
  }
  
  /**
   * Get snapshot for replay
   */
  snapshot(): Map<Register, RegisterValue> {
    return new Map(this.registers);
  }
  
  /**
   * Restore from snapshot
   */
  restore(snapshot: Map<Register, RegisterValue>): void {
    this.registers = new Map(snapshot);
  }
  
  /**
   * Compute hash of entire register file
   */
  computeHash(): string {
    const hashes: string[] = [];
    for (const [reg, val] of this.registers) {
      hashes.push(`${reg}:${val.hash}`);
    }
    return hashString(hashes.sort().join(";"));
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: EXECUTION STATE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Execution state Ψ = (R, F, Θ, C, G)
 */
export interface ExecutionState {
  R: RegisterFile;                    // Register file
  F: Set<StateFlag>;                  // Global flags
  Theta: ExecutionContext;            // Context
  C: ExecutionCounters;               // Counters
  G?: TransportTopology;              // Optional transport topology
}

export interface ExecutionContext {
  kappa_drive: number;
  kappa_fix: number;
  kappa_circ: number;
  kappa_transfer: number;
  corridor: CorridorBudgets;
}

export interface CorridorBudgets {
  H_max: number;
  tau_std: number;
  mu_std: number;
}

export interface ExecutionCounters {
  instructions: number;
  cycles: number;
  time: number;
  memory: number;
}

export interface TransportTopology {
  nodes: string[];
  edges: [string, string][];
}

/**
 * Create initial state
 */
export function createInitialState(): ExecutionState {
  return {
    R: new RegisterFile(),
    F: new Set(),
    Theta: {
      kappa_drive: 1.0,
      kappa_fix: 1.0,
      kappa_circ: 1.0,
      kappa_transfer: 1.0,
      corridor: {
        H_max: 6,
        tau_std: 30000,
        mu_std: 4194304
      }
    },
    C: {
      instructions: 0,
      cycles: 0,
      time: 0,
      memory: 0
    }
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: OPCODE DYNAMICS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * IR instruction
 */
export interface IRInstr {
  op: OpcodeClass;
  dst: Register;
  mods: string[];
  flags: Set<StateFlag>;
  tokDigest: string;
  astDigest: string;
}

/**
 * Step result
 */
export type StepResult =
  | { type: "OK"; state: ExecutionState; trace: ExecutionTrace }
  | { type: "HALT"; state: ExecutionState; reason: string }
  | { type: "FAIL"; state: ExecutionState; error: string };

export interface ExecutionTrace {
  instr: IRInstr;
  preBefore: string;
  preAfter: string;
  flagsBefore: StateFlag[];
  flagsAfter: StateFlag[];
  duration: number;
}

/**
 * Opcode dynamics (state-transform generators)
 */
export class OpcodeDynamics {
  /**
   * T_D: drives flags toward FIXED
   */
  executeD(state: ExecutionState, instr: IRInstr): StepResult {
    const trace = this.createTrace(state, instr);
    const startTime = Date.now();
    
    // Remove ACTIVE, add tendency toward FIXED
    state.F.delete(StateFlag.ACTIVE);
    
    // Apply drive knob
    state.Theta.kappa_drive *= 0.9;
    state.Theta.kappa_fix *= 1.1;
    
    // Update counters
    state.C.instructions++;
    state.C.time += Date.now() - startTime;
    
    trace.flagsAfter = Array.from(state.F);
    trace.preAfter = state.R.computeHash();
    trace.duration = Date.now() - startTime;
    
    return { type: "OK", state, trace };
  }
  
  /**
   * T_O: drives toward ACTIVE
   */
  executeO(state: ExecutionState, instr: IRInstr): StepResult {
    const trace = this.createTrace(state, instr);
    const startTime = Date.now();
    
    // Add ACTIVE, remove FIXED
    state.F.add(StateFlag.ACTIVE);
    state.F.delete(StateFlag.FIXED);
    
    // Apply drive knob
    state.Theta.kappa_drive *= 1.1;
    state.Theta.kappa_fix *= 0.9;
    
    // Update counters
    state.C.instructions++;
    state.C.time += Date.now() - startTime;
    
    trace.flagsAfter = Array.from(state.F);
    trace.preAfter = state.R.computeHash();
    trace.duration = Date.now() - startTime;
    
    return { type: "OK", state, trace };
  }
  
  /**
   * T_S: enables transfer/phase change
   */
  executeS(state: ExecutionState, instr: IRInstr): StepResult {
    const trace = this.createTrace(state, instr);
    const startTime = Date.now();
    
    // Add transfer flags based on mods
    if (instr.flags.has(StateFlag.DISSOLVED)) {
      state.F.add(StateFlag.DISSOLVED);
    }
    if (instr.flags.has(StateFlag.CHANNELED)) {
      state.F.add(StateFlag.CHANNELED);
    }
    
    // Apply transfer knob
    state.Theta.kappa_transfer *= 1.2;
    
    // Update counters
    state.C.instructions++;
    state.C.time += Date.now() - startTime;
    
    trace.flagsAfter = Array.from(state.F);
    trace.preAfter = state.R.computeHash();
    trace.duration = Date.now() - startTime;
    
    return { type: "OK", state, trace };
  }
  
  /**
   * T_QO: iterative circulation kernel
   */
  executeQO(state: ExecutionState, instr: IRInstr): StepResult {
    const trace = this.createTrace(state, instr);
    const startTime = Date.now();
    
    // Add ITERATION flag
    state.F.add(StateFlag.ITERATION);
    
    // Apply circulation knob
    state.Theta.kappa_circ *= 1.1;
    
    // Circulation loop (bounded)
    let iterations = 0;
    const maxIterations = 10;
    
    while (iterations < maxIterations) {
      iterations++;
      state.C.cycles++;
      
      // Check stability predicate
      if (this.isStable(state)) {
        break;
      }
      
      // Check budget
      if (Date.now() - startTime > state.Theta.corridor.tau_std) {
        state.F.delete(StateFlag.ITERATION);
        trace.flagsAfter = Array.from(state.F);
        trace.preAfter = state.R.computeHash();
        trace.duration = Date.now() - startTime;
        
        return {
          type: "FAIL",
          state,
          error: "Budget exceeded in QO circulation"
        };
      }
    }
    
    // Remove ITERATION flag on completion
    state.F.delete(StateFlag.ITERATION);
    
    // Update counters
    state.C.instructions++;
    state.C.time += Date.now() - startTime;
    
    trace.flagsAfter = Array.from(state.F);
    trace.preAfter = state.R.computeHash();
    trace.duration = Date.now() - startTime;
    
    return { type: "OK", state, trace };
  }
  
  /**
   * Execute instruction
   */
  execute(state: ExecutionState, instr: IRInstr): StepResult {
    // Check for HALT
    if (instr.flags.has(StateFlag.HALT)) {
      return { type: "HALT", state, reason: "HALT instruction" };
    }
    
    switch (instr.op) {
      case OpcodeClass.D:
        return this.executeD(state, instr);
      case OpcodeClass.O:
        return this.executeO(state, instr);
      case OpcodeClass.S:
        return this.executeS(state, instr);
      case OpcodeClass.QO:
        return this.executeQO(state, instr);
      default:
        return { type: "FAIL", state, error: `Unknown opcode: ${instr.op}` };
    }
  }
  
  private createTrace(state: ExecutionState, instr: IRInstr): ExecutionTrace {
    return {
      instr,
      preBefore: state.R.computeHash(),
      preAfter: "",
      flagsBefore: Array.from(state.F),
      flagsAfter: [],
      duration: 0
    };
  }
  
  private isStable(state: ExecutionState): boolean {
    // Stability predicate: FIXED flag present and knobs balanced
    return state.F.has(StateFlag.FIXED) ||
           (state.Theta.kappa_drive < 0.5 && state.Theta.kappa_fix > 1.5);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: MAIN CYCLE SCHEMA
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Main cycle: D→O→S→QO
 */
export interface CycleSchema {
  sequence: OpcodeClass[];
  signature: number;
}

/**
 * Compute opcode signature (XOR of encodings)
 */
export function computeOpSig(ops: OpcodeClass[]): number {
  let sig = 0;
  for (const op of ops) {
    sig ^= K4_ENCODE[op];
  }
  return sig;
}

/**
 * Main cycle schema
 */
export const MAIN_CYCLE: CycleSchema = {
  sequence: [OpcodeClass.D, OpcodeClass.O, OpcodeClass.S, OpcodeClass.QO],
  signature: computeOpSig([OpcodeClass.D, OpcodeClass.O, OpcodeClass.S, OpcodeClass.QO])
};

// Verify: 00 ⊕ 01 ⊕ 10 ⊕ 11 = 00 (identity signature)

/**
 * Cycle executor
 */
export class CycleExecutor {
  private dynamics: OpcodeDynamics;
  
  constructor() {
    this.dynamics = new OpcodeDynamics();
  }
  
  /**
   * Execute main cycle
   */
  executeCycle(
    state: ExecutionState,
    instrs: IRInstr[]
  ): CycleExecutionResult {
    const traces: ExecutionTrace[] = [];
    let currentState = state;
    
    for (const instr of instrs) {
      const result = this.dynamics.execute(currentState, instr);
      
      if (result.type === "FAIL") {
        return {
          type: "FAIL",
          state: result.state,
          traces,
          error: result.error
        };
      }
      
      if (result.type === "HALT") {
        return {
          type: "HALT",
          state: result.state,
          traces,
          reason: result.reason
        };
      }
      
      traces.push(result.trace);
      currentState = result.state;
    }
    
    // Verify cycle signature
    const ops = instrs.map(i => i.op);
    const signature = computeOpSig(ops);
    
    return {
      type: "OK",
      state: currentState,
      traces,
      signature,
      cycleComplete: signature === MAIN_CYCLE.signature
    };
  }
  
  /**
   * Check oscillation policy (Ch02.F1.c)
   */
  checkOscillation(traces: ExecutionTrace[]): OscillationCheckResult {
    let activeCount = 0;
    let lastFixed = -1;
    
    for (let i = 0; i < traces.length; i++) {
      if (traces[i].flagsAfter.includes(StateFlag.ACTIVE)) {
        activeCount++;
      }
      if (traces[i].flagsAfter.includes(StateFlag.FIXED)) {
        activeCount = 0;
        lastFixed = i;
      }
    }
    
    // Warn if many ACTIVE without intervening FIXED
    if (activeCount > 3 && lastFixed < traces.length - 3) {
      return {
        healthy: false,
        warning: "Insufficient fixation: many ACTIVE states without FIXED checkpoint",
        residual: { type: "InsufficientFixation", count: activeCount }
      };
    }
    
    return { healthy: true };
  }
}

export type CycleExecutionResult =
  | { type: "OK"; state: ExecutionState; traces: ExecutionTrace[]; signature: number; cycleComplete: boolean }
  | { type: "HALT"; state: ExecutionState; traces: ExecutionTrace[]; reason: string }
  | { type: "FAIL"; state: ExecutionState; traces: ExecutionTrace[]; error: string };

export interface OscillationCheckResult {
  healthy: boolean;
  warning?: string;
  residual?: { type: string; count: number };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: STATIC CHECKER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Static check result
 */
export type StaticCheckResult =
  | { type: "OK" }
  | { type: "AMBIG"; issues: string[]; evidencePlan: string[] }
  | { type: "FAIL"; errors: StaticError[] };

export interface StaticError {
  code: string;
  message: string;
  location: string;
}

/**
 * Static checker (Ch02.S3.c)
 */
export class StaticChecker {
  /**
   * Check IR instruction
   */
  check(instr: IRInstr): StaticCheckResult {
    const errors: StaticError[] = [];
    const ambigIssues: string[] = [];
    
    // Check opcode closed set (S2.b)
    if (!Object.values(OpcodeClass).includes(instr.op)) {
      errors.push({
        code: "E_UNKNOWN_OPCODE",
        message: `Unknown opcode: ${instr.op}`,
        location: instr.tokDigest
      });
    }
    
    // Check flag compatibility (S2.c)
    if (instr.flags.has(StateFlag.HALT) && instr.flags.size > 1) {
      errors.push({
        code: "E_FLAG_CONFLICT",
        message: "HALT cannot co-occur with other flags",
        location: instr.tokDigest
      });
    }
    
    if (instr.flags.has(StateFlag.ACTIVE) && instr.flags.has(StateFlag.FIXED)) {
      errors.push({
        code: "E_FLAG_CONFLICT",
        message: "ACTIVE and FIXED incompatible",
        location: instr.tokDigest
      });
    }
    
    // Check register typing (S2.d)
    if (!Object.values(Register).includes(instr.dst)) {
      ambigIssues.push(`Unknown register: ${instr.dst}`);
    }
    
    // Check suffix legality (S1.c)
    // (Assuming flags came from valid suffix lift)
    
    if (errors.length > 0) {
      return { type: "FAIL", errors };
    }
    
    if (ambigIssues.length > 0) {
      return {
        type: "AMBIG",
        issues: ambigIssues,
        evidencePlan: ["Check register mapping", "Verify suffix patterns"]
      };
    }
    
    return { type: "OK" };
  }
  
  /**
   * Check program
   */
  checkProgram(instrs: IRInstr[]): StaticCheckResult {
    const allErrors: StaticError[] = [];
    const allAmbig: string[] = [];
    
    for (const instr of instrs) {
      const result = this.check(instr);
      
      if (result.type === "FAIL") {
        allErrors.push(...result.errors);
      } else if (result.type === "AMBIG") {
        allAmbig.push(...result.issues);
      }
    }
    
    if (allErrors.length > 0) {
      return { type: "FAIL", errors: allErrors };
    }
    
    if (allAmbig.length > 0) {
      return {
        type: "AMBIG",
        issues: allAmbig,
        evidencePlan: ["Resolve all ambiguous instructions"]
      };
    }
    
    return { type: "OK" };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 8: COMPLETE ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Disassembly result
 */
export interface DisassemblyResult {
  asts: (InstrAST | { type: "AMBIG"; candidates: InstrAST[] })[];
  errors: string[];
}

/**
 * Lowering result
 */
export interface LoweringResult {
  instrs: IRInstr[];
  ambiguous: number;
  errors: string[];
}

/**
 * Complete Tricompiler Core Engine
 */
export class TricompilerCoreEngine {
  private parser: TokenParser;
  private dynamics: OpcodeDynamics;
  private cycleExecutor: CycleExecutor;
  private staticChecker: StaticChecker;
  
  constructor() {
    this.parser = new TokenParser();
    this.dynamics = new OpcodeDynamics();
    this.cycleExecutor = new CycleExecutor();
    this.staticChecker = new StaticChecker();
  }
  
  /**
   * Parse token
   */
  parseToken(token: string): ParseResult {
    return this.parser.parseToken(token);
  }
  
  /**
   * Disassemble token stream
   */
  disassemble(tokens: string[]): DisassemblyResult {
    const asts: (InstrAST | { type: "AMBIG"; candidates: InstrAST[] })[] = [];
    const errors: string[] = [];
    
    for (const token of tokens) {
      const result = this.parser.parseToken(token);
      
      if (result.type === "OK") {
        asts.push(result.ast);
      } else if (result.type === "AMBIG") {
        asts.push({ type: "AMBIG", candidates: result.candidates });
      } else {
        errors.push(`${token}: ${result.reason}`);
      }
    }
    
    return { asts, errors };
  }
  
  /**
   * Lower AST to IR
   */
  lowerAST(ast: InstrAST): IRInstr {
    // Determine target register from root
    let dst = Register.CHE;  // Default
    for (const [root, reg] of Object.entries(ROOT_REGISTER_MAP)) {
      if (ast.root.includes(root)) {
        dst = reg;
        break;
      }
    }
    
    return {
      op: ast.opclass,
      dst,
      mods: ast.mods,
      flags: ast.state,
      tokDigest: hashString(ast.raw),
      astDigest: ast.digest
    };
  }
  
  /**
   * Lower program
   */
  lowerProgram(asts: InstrAST[]): LoweringResult {
    const instrs: IRInstr[] = [];
    let ambiguous = 0;
    const errors: string[] = [];
    
    for (const ast of asts) {
      try {
        instrs.push(this.lowerAST(ast));
      } catch (e) {
        errors.push(`Failed to lower: ${ast.raw}`);
        ambiguous++;
      }
    }
    
    return { instrs, ambiguous, errors };
  }
  
  /**
   * Static check
   */
  staticCheck(instrs: IRInstr[]): StaticCheckResult {
    return this.staticChecker.checkProgram(instrs);
  }
  
  /**
   * Execute instruction
   */
  executeInstruction(state: ExecutionState, instr: IRInstr): StepResult {
    return this.dynamics.execute(state, instr);
  }
  
  /**
   * Execute cycle
   */
  executeCycle(state: ExecutionState, instrs: IRInstr[]): CycleExecutionResult {
    return this.cycleExecutor.executeCycle(state, instrs);
  }
  
  /**
   * Full compile and run: parse → lower → check → execute
   */
  compileAndRun(tokens: string[]): CompileAndRunResult {
    // Disassemble
    const disasm = this.disassemble(tokens);
    if (disasm.errors.length > 0) {
      return {
        type: "FAIL",
        stage: "disassemble",
        errors: disasm.errors
      };
    }
    
    // Filter to resolved ASTs
    const resolvedAsts = disasm.asts.filter((a): a is InstrAST => !("type" in a));
    if (resolvedAsts.length !== disasm.asts.length) {
      return {
        type: "AMBIG",
        stage: "disassemble",
        ambiguousCount: disasm.asts.length - resolvedAsts.length,
        evidencePlan: ["Resolve ambiguous tokens"]
      };
    }
    
    // Lower
    const lowered = this.lowerProgram(resolvedAsts);
    if (lowered.errors.length > 0) {
      return {
        type: "FAIL",
        stage: "lower",
        errors: lowered.errors
      };
    }
    
    // Static check
    const checked = this.staticCheck(lowered.instrs);
    if (checked.type === "FAIL") {
      return {
        type: "FAIL",
        stage: "staticCheck",
        errors: checked.errors.map(e => e.message)
      };
    }
    if (checked.type === "AMBIG") {
      return {
        type: "AMBIG",
        stage: "staticCheck",
        ambiguousCount: checked.issues.length,
        evidencePlan: checked.evidencePlan
      };
    }
    
    // Execute
    const state = createInitialState();
    const result = this.executeCycle(state, lowered.instrs);
    
    if (result.type === "FAIL") {
      return {
        type: "FAIL",
        stage: "execute",
        errors: [result.error]
      };
    }
    
    // Check oscillation
    const oscCheck = this.cycleExecutor.checkOscillation(result.traces);
    
    return {
      type: "OK",
      state: result.state,
      traces: result.traces,
      cycleComplete: result.type === "OK" && result.cycleComplete,
      oscillationHealthy: oscCheck.healthy,
      warnings: oscCheck.warning ? [oscCheck.warning] : []
    };
  }
  
  /**
   * Get statistics
   */
  getStats(): TricompilerStats {
    return {
      opcodeClasses: Object.values(OpcodeClass).length,
      stateFlags: Object.values(StateFlag).length,
      registers: Object.values(Register).length,
      mainCycleSignature: MAIN_CYCLE.signature
    };
  }
}

export type CompileAndRunResult =
  | {
      type: "OK";
      state: ExecutionState;
      traces: ExecutionTrace[];
      cycleComplete: boolean;
      oscillationHealthy: boolean;
      warnings: string[];
    }
  | {
      type: "AMBIG";
      stage: string;
      ambiguousCount: number;
      evidencePlan: string[];
    }
  | {
      type: "FAIL";
      stage: string;
      errors: string[];
    };

export interface TricompilerStats {
  opcodeClasses: number;
  stateFlags: number;
  registers: number;
  mainCycleSignature: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Enums
  OpcodeClass,
  StateFlag,
  Register,
  
  // Constants
  K4_ENCODE,
  K4_DECODE,
  SUFFIX_LIFT,
  ROOT_REGISTER_MAP,
  MAIN_CYCLE,
  
  // Functions
  computeOpSig,
  createInitialState,
  
  // Classes
  TokenParser,
  RegisterFile,
  OpcodeDynamics,
  CycleExecutor,
  StaticChecker,
  TricompilerCoreEngine
};
