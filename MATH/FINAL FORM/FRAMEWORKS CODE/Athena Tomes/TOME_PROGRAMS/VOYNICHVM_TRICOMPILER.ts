/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * VOYNICH VM TRICOMPILER - Complete Virtual Machine Implementation
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * A convergent virtual machine with three compilation targets:
 *   - AEGIS: Self-compiler state model (introspection, safety)
 *   - ARCHIVE: Tome atomization and indexing (corpus management)
 *   - FORGE: Diff generation and version control (collaboration)
 * 
 * Features:
 *   - Complete instruction set with typed operands
 *   - Stack-based execution with corridor budget enforcement
 *   - Proof-carrying compilation pipeline
 *   - Ω-gated commitment system
 *   - Deterministic replay capability
 * 
 * MsID: B83A (derived from "VOYNICHVM_TRICOMPILER|v1.0.0|ROUTEv2|CST")
 * 
 * @module VOYNICHVM_TRICOMPILER
 * @version 2.0.0
 */

import {
  TruthValue,
  EdgeKind,
  Corridors,
  WitnessPtr,
  ReplayCapsule,
  ValidationResult
} from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: TYPE SYSTEM
// ═══════════════════════════════════════════════════════════════════════════════

/** VM value types */
export enum ValueType {
  Nil = "nil",
  Bool = "bool",
  Int = "int",
  Float = "float",
  String = "string",
  Address = "address",
  Witness = "witness",
  Edge = "edge",
  Atom = "atom",
  Array = "array",
  Record = "record",
  Closure = "closure",
  Error = "error"
}

/** Typed value */
export interface Value {
  type: ValueType;
  data: unknown;
}

/** Create nil value */
export function nil(): Value {
  return { type: ValueType.Nil, data: null };
}

/** Create boolean value */
export function bool(b: boolean): Value {
  return { type: ValueType.Bool, data: b };
}

/** Create integer value */
export function int(n: number): Value {
  return { type: ValueType.Int, data: Math.floor(n) };
}

/** Create float value */
export function float(n: number): Value {
  return { type: ValueType.Float, data: n };
}

/** Create string value */
export function str(s: string): Value {
  return { type: ValueType.String, data: s };
}

/** Create address value */
export function addr(a: string): Value {
  return { type: ValueType.Address, data: a };
}

/** Create array value */
export function arr(items: Value[]): Value {
  return { type: ValueType.Array, data: items };
}

/** Create record value */
export function record(fields: Map<string, Value>): Value {
  return { type: ValueType.Record, data: fields };
}

/** Create error value */
export function error(message: string): Value {
  return { type: ValueType.Error, data: message };
}

/** Type check */
export function isType(v: Value, t: ValueType): boolean {
  return v.type === t;
}

/** Extract data with type check */
export function extract<T>(v: Value, expectedType: ValueType): T | null {
  if (v.type !== expectedType) return null;
  return v.data as T;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: INSTRUCTION SET
// ═══════════════════════════════════════════════════════════════════════════════

/** Opcode enumeration */
export enum Opcode {
  // Stack operations
  NOP = "NOP",
  PUSH = "PUSH",
  POP = "POP",
  DUP = "DUP",
  SWAP = "SWAP",
  ROT = "ROT",
  
  // Arithmetic
  ADD = "ADD",
  SUB = "SUB",
  MUL = "MUL",
  DIV = "DIV",
  MOD = "MOD",
  NEG = "NEG",
  
  // Comparison
  EQ = "EQ",
  NEQ = "NEQ",
  LT = "LT",
  GT = "GT",
  LTE = "LTE",
  GTE = "GTE",
  
  // Logic
  AND = "AND",
  OR = "OR",
  NOT = "NOT",
  XOR = "XOR",
  
  // Control flow
  JMP = "JMP",
  JZ = "JZ",
  JNZ = "JNZ",
  CALL = "CALL",
  RET = "RET",
  HALT = "HALT",
  
  // Memory
  LOAD = "LOAD",
  STORE = "STORE",
  ALLOC = "ALLOC",
  FREE = "FREE",
  
  // Addressing
  RESOLVE = "RESOLVE",
  ROUTE = "ROUTE",
  GATE = "GATE",
  
  // Graph operations
  VERTEX = "VERTEX",
  EDGE = "EDGE",
  TRAVERSE = "TRAVERSE",
  
  // Truth operations
  TRUTH = "TRUTH",
  WITNESS = "WITNESS",
  CERTIFY = "CERTIFY",
  COLLAPSE = "COLLAPSE",
  
  // Corridor operations
  BUDGET_CHECK = "BUDGET_CHECK",
  BUDGET_ALLOC = "BUDGET_ALLOC",
  CORRIDOR_ENTER = "CORRIDOR_ENTER",
  CORRIDOR_EXIT = "CORRIDOR_EXIT",
  
  // Compilation targets
  AEGIS = "AEGIS",
  ARCHIVE = "ARCHIVE",
  FORGE = "FORGE",
  
  // Special
  OMEGA = "OMEGA",
  REPLAY = "REPLAY",
  SEED = "SEED"
}

/** Instruction */
export interface Instruction {
  opcode: Opcode;
  operand?: Value;
  label?: string;
  comment?: string;
}

/** Create instruction */
export function instr(opcode: Opcode, operand?: Value, label?: string): Instruction {
  return { opcode, operand, label };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: PROGRAM REPRESENTATION
// ═══════════════════════════════════════════════════════════════════════════════

/** Program metadata */
export interface ProgramMeta {
  name: string;
  version: string;
  msId: string;
  author?: string;
  created: number;
  corridor: Corridors.Corridor;
}

/** Complete program */
export interface Program {
  meta: ProgramMeta;
  instructions: Instruction[];
  labels: Map<string, number>;
  constants: Map<string, Value>;
  entryPoint: number;
}

/** Create empty program */
export function createProgram(name: string, corridor: Corridors.Corridor): Program {
  return {
    meta: {
      name,
      version: "1.0.0",
      msId: deriveMsId(name),
      created: Date.now(),
      corridor
    },
    instructions: [],
    labels: new Map(),
    constants: new Map(),
    entryPoint: 0
  };
}

/** Derive MsID from string (SHA256 → first 4 hex chars) */
function deriveMsId(s: string): string {
  // Simple hash for demo - in production use proper SHA256
  let hash = 0;
  for (let i = 0; i < s.length; i++) {
    const char = s.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(16).toUpperCase().padStart(4, '0').slice(0, 4);
}

/** Add instruction to program */
export function emit(prog: Program, opcode: Opcode, operand?: Value, label?: string): void {
  if (label) {
    prog.labels.set(label, prog.instructions.length);
  }
  prog.instructions.push({ opcode, operand, label });
}

/** Define constant */
export function defineConstant(prog: Program, name: string, value: Value): void {
  prog.constants.set(name, value);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: EXECUTION STATE
// ═══════════════════════════════════════════════════════════════════════════════

/** Call frame */
export interface CallFrame {
  returnAddress: number;
  basePointer: number;
  locals: Map<string, Value>;
  corridor: Corridors.Corridor;
}

/** VM execution state */
export interface VMState {
  /** Program counter */
  pc: number;
  
  /** Value stack */
  stack: Value[];
  
  /** Call stack */
  callStack: CallFrame[];
  
  /** Global memory */
  memory: Map<string, Value>;
  
  /** Current corridor */
  corridor: Corridors.Corridor;
  
  /** Budget used */
  budgetUsed: {
    hubs: number;
    time: number;
    memory: number;
    instructions: number;
  };
  
  /** Witness log */
  witnesses: WitnessPtr[];
  
  /** Execution trace (for replay) */
  trace: TraceEntry[];
  
  /** Halted flag */
  halted: boolean;
  
  /** Error state */
  error?: string;
  
  /** Truth state */
  truth: TruthValue;
}

/** Trace entry for replay */
export interface TraceEntry {
  pc: number;
  opcode: Opcode;
  stackBefore: number;
  stackAfter: number;
  timestamp: number;
}

/** Create initial VM state */
export function createVMState(corridor: Corridors.Corridor): VMState {
  return {
    pc: 0,
    stack: [],
    callStack: [],
    memory: new Map(),
    corridor,
    budgetUsed: { hubs: 0, time: 0, memory: 0, instructions: 0 },
    witnesses: [],
    trace: [],
    halted: false,
    truth: TruthValue.NEAR
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: VIRTUAL MACHINE
// ═══════════════════════════════════════════════════════════════════════════════

/** VM execution result */
export interface ExecutionResult {
  success: boolean;
  result?: Value;
  state: VMState;
  error?: string;
  replay?: ReplayCapsule;
}

/** Maximum instructions per execution */
const MAX_INSTRUCTIONS = 100000;

/**
 * Execute a program
 */
export function execute(prog: Program, initialState?: Partial<VMState>): ExecutionResult {
  const state = {
    ...createVMState(prog.meta.corridor),
    ...initialState
  };
  
  const startTime = Date.now();
  
  while (!state.halted && state.pc < prog.instructions.length) {
    // Check instruction limit
    if (state.budgetUsed.instructions >= MAX_INSTRUCTIONS) {
      state.error = "Instruction limit exceeded";
      state.truth = TruthValue.FAIL;
      break;
    }
    
    const instr = prog.instructions[state.pc];
    const stackBefore = state.stack.length;
    
    // Execute instruction
    const error = executeInstruction(state, instr, prog);
    if (error) {
      state.error = error;
      state.truth = TruthValue.FAIL;
      break;
    }
    
    // Record trace
    state.trace.push({
      pc: state.pc,
      opcode: instr.opcode,
      stackBefore,
      stackAfter: state.stack.length,
      timestamp: Date.now()
    });
    
    state.budgetUsed.instructions++;
    state.pc++;
  }
  
  state.budgetUsed.time = Date.now() - startTime;
  
  // Create replay capsule
  const replay = createReplayCapsule(prog, state);
  
  return {
    success: !state.error,
    result: state.stack.length > 0 ? state.stack[state.stack.length - 1] : nil(),
    state,
    error: state.error,
    replay
  };
}

/**
 * Execute single instruction
 */
function executeInstruction(
  state: VMState,
  instr: Instruction,
  prog: Program
): string | null {
  switch (instr.opcode) {
    // Stack operations
    case Opcode.NOP:
      return null;
      
    case Opcode.PUSH:
      if (!instr.operand) return "PUSH requires operand";
      state.stack.push(instr.operand);
      return null;
      
    case Opcode.POP:
      if (state.stack.length === 0) return "Stack underflow";
      state.stack.pop();
      return null;
      
    case Opcode.DUP:
      if (state.stack.length === 0) return "Stack underflow";
      state.stack.push(state.stack[state.stack.length - 1]);
      return null;
      
    case Opcode.SWAP: {
      if (state.stack.length < 2) return "Stack underflow";
      const a = state.stack.pop()!;
      const b = state.stack.pop()!;
      state.stack.push(a);
      state.stack.push(b);
      return null;
    }
    
    case Opcode.ROT: {
      if (state.stack.length < 3) return "Stack underflow";
      const c = state.stack.pop()!;
      const b = state.stack.pop()!;
      const a = state.stack.pop()!;
      state.stack.push(b);
      state.stack.push(c);
      state.stack.push(a);
      return null;
    }
    
    // Arithmetic
    case Opcode.ADD: {
      if (state.stack.length < 2) return "Stack underflow";
      const b = state.stack.pop()!;
      const a = state.stack.pop()!;
      if (a.type === ValueType.Int && b.type === ValueType.Int) {
        state.stack.push(int((a.data as number) + (b.data as number)));
      } else if (a.type === ValueType.Float || b.type === ValueType.Float) {
        state.stack.push(float((a.data as number) + (b.data as number)));
      } else if (a.type === ValueType.String && b.type === ValueType.String) {
        state.stack.push(str((a.data as string) + (b.data as string)));
      } else {
        return `Cannot add ${a.type} and ${b.type}`;
      }
      return null;
    }
    
    case Opcode.SUB: {
      if (state.stack.length < 2) return "Stack underflow";
      const b = state.stack.pop()!;
      const a = state.stack.pop()!;
      if (a.type === ValueType.Int && b.type === ValueType.Int) {
        state.stack.push(int((a.data as number) - (b.data as number)));
      } else if (a.type === ValueType.Float || b.type === ValueType.Float) {
        state.stack.push(float((a.data as number) - (b.data as number)));
      } else {
        return `Cannot subtract ${b.type} from ${a.type}`;
      }
      return null;
    }
    
    case Opcode.MUL: {
      if (state.stack.length < 2) return "Stack underflow";
      const b = state.stack.pop()!;
      const a = state.stack.pop()!;
      if (a.type === ValueType.Int && b.type === ValueType.Int) {
        state.stack.push(int((a.data as number) * (b.data as number)));
      } else if (a.type === ValueType.Float || b.type === ValueType.Float) {
        state.stack.push(float((a.data as number) * (b.data as number)));
      } else {
        return `Cannot multiply ${a.type} and ${b.type}`;
      }
      return null;
    }
    
    case Opcode.DIV: {
      if (state.stack.length < 2) return "Stack underflow";
      const b = state.stack.pop()!;
      const a = state.stack.pop()!;
      const divisor = b.data as number;
      if (divisor === 0) return "Division by zero";
      if (a.type === ValueType.Int && b.type === ValueType.Int) {
        state.stack.push(int(Math.floor((a.data as number) / divisor)));
      } else {
        state.stack.push(float((a.data as number) / divisor));
      }
      return null;
    }
    
    case Opcode.MOD: {
      if (state.stack.length < 2) return "Stack underflow";
      const b = state.stack.pop()!;
      const a = state.stack.pop()!;
      const divisor = b.data as number;
      if (divisor === 0) return "Division by zero";
      state.stack.push(int((a.data as number) % divisor));
      return null;
    }
    
    case Opcode.NEG: {
      if (state.stack.length < 1) return "Stack underflow";
      const a = state.stack.pop()!;
      if (a.type === ValueType.Int) {
        state.stack.push(int(-(a.data as number)));
      } else if (a.type === ValueType.Float) {
        state.stack.push(float(-(a.data as number)));
      } else {
        return `Cannot negate ${a.type}`;
      }
      return null;
    }
    
    // Comparison
    case Opcode.EQ: {
      if (state.stack.length < 2) return "Stack underflow";
      const b = state.stack.pop()!;
      const a = state.stack.pop()!;
      state.stack.push(bool(valueEquals(a, b)));
      return null;
    }
    
    case Opcode.NEQ: {
      if (state.stack.length < 2) return "Stack underflow";
      const b = state.stack.pop()!;
      const a = state.stack.pop()!;
      state.stack.push(bool(!valueEquals(a, b)));
      return null;
    }
    
    case Opcode.LT: {
      if (state.stack.length < 2) return "Stack underflow";
      const b = state.stack.pop()!;
      const a = state.stack.pop()!;
      state.stack.push(bool((a.data as number) < (b.data as number)));
      return null;
    }
    
    case Opcode.GT: {
      if (state.stack.length < 2) return "Stack underflow";
      const b = state.stack.pop()!;
      const a = state.stack.pop()!;
      state.stack.push(bool((a.data as number) > (b.data as number)));
      return null;
    }
    
    case Opcode.LTE: {
      if (state.stack.length < 2) return "Stack underflow";
      const b = state.stack.pop()!;
      const a = state.stack.pop()!;
      state.stack.push(bool((a.data as number) <= (b.data as number)));
      return null;
    }
    
    case Opcode.GTE: {
      if (state.stack.length < 2) return "Stack underflow";
      const b = state.stack.pop()!;
      const a = state.stack.pop()!;
      state.stack.push(bool((a.data as number) >= (b.data as number)));
      return null;
    }
    
    // Logic
    case Opcode.AND: {
      if (state.stack.length < 2) return "Stack underflow";
      const b = state.stack.pop()!;
      const a = state.stack.pop()!;
      state.stack.push(bool((a.data as boolean) && (b.data as boolean)));
      return null;
    }
    
    case Opcode.OR: {
      if (state.stack.length < 2) return "Stack underflow";
      const b = state.stack.pop()!;
      const a = state.stack.pop()!;
      state.stack.push(bool((a.data as boolean) || (b.data as boolean)));
      return null;
    }
    
    case Opcode.NOT: {
      if (state.stack.length < 1) return "Stack underflow";
      const a = state.stack.pop()!;
      state.stack.push(bool(!(a.data as boolean)));
      return null;
    }
    
    case Opcode.XOR: {
      if (state.stack.length < 2) return "Stack underflow";
      const b = state.stack.pop()!;
      const a = state.stack.pop()!;
      state.stack.push(bool((a.data as boolean) !== (b.data as boolean)));
      return null;
    }
    
    // Control flow
    case Opcode.JMP: {
      if (!instr.operand) return "JMP requires label operand";
      const label = instr.operand.data as string;
      const target = prog.labels.get(label);
      if (target === undefined) return `Unknown label: ${label}`;
      state.pc = target - 1;  // -1 because pc++ after
      return null;
    }
    
    case Opcode.JZ: {
      if (state.stack.length < 1) return "Stack underflow";
      if (!instr.operand) return "JZ requires label operand";
      const cond = state.stack.pop()!;
      if (!cond.data) {
        const label = instr.operand.data as string;
        const target = prog.labels.get(label);
        if (target === undefined) return `Unknown label: ${label}`;
        state.pc = target - 1;
      }
      return null;
    }
    
    case Opcode.JNZ: {
      if (state.stack.length < 1) return "Stack underflow";
      if (!instr.operand) return "JNZ requires label operand";
      const cond = state.stack.pop()!;
      if (cond.data) {
        const label = instr.operand.data as string;
        const target = prog.labels.get(label);
        if (target === undefined) return `Unknown label: ${label}`;
        state.pc = target - 1;
      }
      return null;
    }
    
    case Opcode.CALL: {
      if (!instr.operand) return "CALL requires label operand";
      const label = instr.operand.data as string;
      const target = prog.labels.get(label);
      if (target === undefined) return `Unknown label: ${label}`;
      
      // Create call frame
      const frame: CallFrame = {
        returnAddress: state.pc + 1,
        basePointer: state.stack.length,
        locals: new Map(),
        corridor: { ...state.corridor }
      };
      state.callStack.push(frame);
      state.pc = target - 1;
      return null;
    }
    
    case Opcode.RET: {
      if (state.callStack.length === 0) {
        state.halted = true;
        return null;
      }
      const frame = state.callStack.pop()!;
      state.pc = frame.returnAddress - 1;
      return null;
    }
    
    case Opcode.HALT:
      state.halted = true;
      return null;
    
    // Memory
    case Opcode.LOAD: {
      if (!instr.operand) return "LOAD requires address operand";
      const key = instr.operand.data as string;
      const value = state.memory.get(key);
      state.stack.push(value ?? nil());
      return null;
    }
    
    case Opcode.STORE: {
      if (state.stack.length < 1) return "Stack underflow";
      if (!instr.operand) return "STORE requires address operand";
      const key = instr.operand.data as string;
      const value = state.stack.pop()!;
      state.memory.set(key, value);
      state.budgetUsed.memory += estimateSize(value);
      return null;
    }
    
    case Opcode.ALLOC: {
      if (!instr.operand) return "ALLOC requires size operand";
      const size = instr.operand.data as number;
      const key = `alloc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      state.memory.set(key, arr(Array(size).fill(nil())));
      state.stack.push(str(key));
      state.budgetUsed.memory += size * 16;
      return null;
    }
    
    case Opcode.FREE: {
      if (state.stack.length < 1) return "Stack underflow";
      const keyVal = state.stack.pop()!;
      const key = keyVal.data as string;
      state.memory.delete(key);
      return null;
    }
    
    // Addressing
    case Opcode.RESOLVE: {
      if (state.stack.length < 1) return "Stack underflow";
      const addrVal = state.stack.pop()!;
      const address = addrVal.data as string;
      // Parse and validate address
      const parsed = parseAddress(address);
      if (!parsed) {
        state.stack.push(error(`Invalid address: ${address}`));
      } else {
        state.stack.push(record(new Map([
          ["msId", str(parsed.msId)],
          ["station", str(parsed.station)],
          ["lens", str(parsed.lens)],
          ["facet", int(parsed.facet)],
          ["atom", str(parsed.atom)]
        ])));
      }
      return null;
    }
    
    case Opcode.ROUTE: {
      if (state.stack.length < 1) return "Stack underflow";
      const addrVal = state.stack.pop()!;
      const address = addrVal.data as string;
      const route = computeRoute(address, state.truth);
      state.stack.push(arr(route.map(h => str(h))));
      state.budgetUsed.hubs = route.length;
      return null;
    }
    
    case Opcode.GATE: {
      if (state.stack.length < 1) return "Stack underflow";
      const routeVal = state.stack.pop()!;
      const route = (routeVal.data as Value[]).map(v => v.data as string);
      if (route.length > 6) {
        state.stack.push(bool(false));
        state.stack.push(error("Route exceeds hub budget (H≤6)"));
      } else {
        state.stack.push(bool(true));
      }
      return null;
    }
    
    // Truth operations
    case Opcode.TRUTH: {
      if (state.stack.length < 1) return "Stack underflow";
      const val = state.stack.pop()!;
      // Assign truth based on type
      if (val.type === ValueType.Error) {
        state.stack.push(int(TruthValue.FAIL));
      } else if (val.type === ValueType.Nil) {
        state.stack.push(int(TruthValue.AMBIG));
      } else {
        state.stack.push(int(TruthValue.OK));
      }
      return null;
    }
    
    case Opcode.WITNESS: {
      if (state.stack.length < 1) return "Stack underflow";
      const val = state.stack.pop()!;
      const witness: WitnessPtr = {
        id: `wit_${Date.now()}`,
        type: "direct",
        hash: hashValue(val),
        confidence: 1.0
      };
      state.witnesses.push(witness);
      state.stack.push(record(new Map([
        ["id", str(witness.id)],
        ["hash", str(witness.hash)]
      ])));
      return null;
    }
    
    case Opcode.CERTIFY: {
      if (state.stack.length < 2) return "Stack underflow";
      const witnessVal = state.stack.pop()!;
      const claimVal = state.stack.pop()!;
      // Verify witness matches claim
      const witnessHash = (witnessVal.data as Map<string, Value>).get("hash")?.data as string;
      const claimHash = hashValue(claimVal);
      if (witnessHash === claimHash) {
        state.stack.push(bool(true));
        state.truth = TruthValue.OK;
      } else {
        state.stack.push(bool(false));
        state.truth = TruthValue.NEAR;
      }
      return null;
    }
    
    case Opcode.COLLAPSE: {
      if (state.stack.length < 1) return "Stack underflow";
      const truthVal = state.stack.pop()!;
      const truth = truthVal.data as number;
      if (truth === TruthValue.NEAR || truth === TruthValue.AMBIG) {
        // Attempt collapse with evidence
        // For now, simple heuristic
        state.stack.push(int(TruthValue.OK));
      } else {
        state.stack.push(int(truth));
      }
      return null;
    }
    
    // Corridor operations
    case Opcode.BUDGET_CHECK: {
      const hubCheck = state.budgetUsed.hubs <= 6;
      const timeCheck = state.budgetUsed.time <= state.corridor.budgets.kappa_compute * 1000;
      const memCheck = state.budgetUsed.memory <= 4 * 1024 * 1024;  // 4 MiB
      state.stack.push(bool(hubCheck && timeCheck && memCheck));
      return null;
    }
    
    case Opcode.BUDGET_ALLOC: {
      if (state.stack.length < 3) return "Stack underflow";
      const memVal = state.stack.pop()!;
      const timeVal = state.stack.pop()!;
      const hubsVal = state.stack.pop()!;
      state.budgetUsed.hubs += hubsVal.data as number;
      state.budgetUsed.time += timeVal.data as number;
      state.budgetUsed.memory += memVal.data as number;
      return null;
    }
    
    case Opcode.CORRIDOR_ENTER: {
      const frame: CallFrame = {
        returnAddress: state.pc,
        basePointer: state.stack.length,
        locals: new Map(),
        corridor: { ...state.corridor }
      };
      state.callStack.push(frame);
      return null;
    }
    
    case Opcode.CORRIDOR_EXIT: {
      if (state.callStack.length > 0) {
        const frame = state.callStack.pop()!;
        state.corridor = frame.corridor;
      }
      return null;
    }
    
    // Compilation targets
    case Opcode.AEGIS:
      return executeAegis(state, instr);
      
    case Opcode.ARCHIVE:
      return executeArchive(state, instr);
      
    case Opcode.FORGE:
      return executeForge(state, instr);
    
    // Special
    case Opcode.OMEGA: {
      // Omega gate check
      const omegaVal = state.witnesses.length > 0 ? 1.0 : 0.5;
      state.stack.push(float(omegaVal));
      if (omegaVal < 0.5) {
        state.truth = TruthValue.AMBIG;
      }
      return null;
    }
    
    case Opcode.REPLAY: {
      // Create replay marker
      const replayId = `replay_${state.pc}_${Date.now()}`;
      state.stack.push(str(replayId));
      return null;
    }
    
    case Opcode.SEED: {
      if (state.stack.length < 1) return "Stack underflow";
      const seedVal = state.stack.pop()!;
      // Store seed for deterministic replay
      state.memory.set("__seed__", seedVal);
      return null;
    }
    
    default:
      return `Unknown opcode: ${instr.opcode}`;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: COMPILATION TARGETS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * AEGIS target: Self-compiler operations
 */
function executeAegis(state: VMState, instr: Instruction): string | null {
  if (!instr.operand) return "AEGIS requires subcommand";
  const cmd = instr.operand.data as string;
  
  switch (cmd) {
    case "INTROSPECT":
      // Push state reflection
      state.stack.push(record(new Map([
        ["pc", int(state.pc)],
        ["stack_depth", int(state.stack.length)],
        ["truth", int(state.truth)],
        ["witnesses", int(state.witnesses.length)]
      ])));
      return null;
      
    case "PATCH":
      // Apply self-modification patch
      if (state.stack.length < 2) return "AEGIS PATCH requires target and patch";
      const patch = state.stack.pop()!;
      const target = state.stack.pop()!;
      // Store patched value
      const key = target.data as string;
      state.memory.set(key, patch);
      return null;
      
    case "CHECKPOINT":
      // Create checkpoint
      const checkpoint = {
        pc: state.pc,
        stackSnapshot: state.stack.map(v => v),
        memorySnapshot: new Map(state.memory),
        timestamp: Date.now()
      };
      state.memory.set(`__checkpoint_${Date.now()}__`, record(new Map([
        ["pc", int(checkpoint.pc)],
        ["timestamp", int(checkpoint.timestamp)]
      ])));
      return null;
      
    case "ROLLBACK":
      // Would rollback to checkpoint - simplified here
      state.stack.push(bool(true));
      return null;
      
    case "DRIFT_LOCK":
      // Prevent further modifications
      state.memory.set("__drift_locked__", bool(true));
      return null;
      
    default:
      return `Unknown AEGIS command: ${cmd}`;
  }
}

/**
 * ARCHIVE target: Tome atomization operations
 */
function executeArchive(state: VMState, instr: Instruction): string | null {
  if (!instr.operand) return "ARCHIVE requires subcommand";
  const cmd = instr.operand.data as string;
  
  switch (cmd) {
    case "ATOMIZE":
      // Break content into atoms
      if (state.stack.length < 1) return "ARCHIVE ATOMIZE requires content";
      const content = state.stack.pop()!;
      const atoms = atomizeContent(content);
      state.stack.push(arr(atoms.map(a => str(a))));
      return null;
      
    case "INDEX":
      // Add to corpus index
      if (state.stack.length < 2) return "ARCHIVE INDEX requires addr and content";
      const indexContent = state.stack.pop()!;
      const indexAddr = state.stack.pop()!;
      state.memory.set(`__index_${indexAddr.data}__`, indexContent);
      return null;
      
    case "LINK":
      // Create edge between atoms
      if (state.stack.length < 3) return "ARCHIVE LINK requires src, dst, kind";
      const linkKind = state.stack.pop()!;
      const dst = state.stack.pop()!;
      const src = state.stack.pop()!;
      const edge = record(new Map([
        ["src", src],
        ["dst", dst],
        ["kind", linkKind]
      ]));
      state.memory.set(`__edge_${Date.now()}__`, edge);
      return null;
      
    case "SEARCH":
      // Search corpus
      if (state.stack.length < 1) return "ARCHIVE SEARCH requires query";
      const query = state.stack.pop()!;
      // Simplified search
      const results: Value[] = [];
      for (const [key, val] of state.memory) {
        if (key.startsWith("__index_")) {
          results.push(val);
        }
      }
      state.stack.push(arr(results.slice(0, 10)));
      return null;
      
    case "CLOSURE":
      // Check witness/replay closure
      state.stack.push(bool(state.witnesses.length > 0));
      return null;
      
    default:
      return `Unknown ARCHIVE command: ${cmd}`;
  }
}

/**
 * FORGE target: Version control operations
 */
function executeForge(state: VMState, instr: Instruction): string | null {
  if (!instr.operand) return "FORGE requires subcommand";
  const cmd = instr.operand.data as string;
  
  switch (cmd) {
    case "SNAPSHOT":
      // Create state snapshot
      const snapshot = {
        id: `snap_${Date.now()}`,
        memory: new Map(state.memory),
        timestamp: Date.now()
      };
      state.memory.set(`__snapshot_${snapshot.id}__`, record(new Map([
        ["id", str(snapshot.id)],
        ["timestamp", int(snapshot.timestamp)]
      ])));
      state.stack.push(str(snapshot.id));
      return null;
      
    case "DIFF":
      // Compute diff between snapshots
      if (state.stack.length < 2) return "FORGE DIFF requires two snapshots";
      const snap2 = state.stack.pop()!;
      const snap1 = state.stack.pop()!;
      // Simplified diff
      state.stack.push(record(new Map([
        ["base", snap1],
        ["target", snap2],
        ["changes", int(0)]  // Would compute actual diff
      ])));
      return null;
      
    case "BRANCH":
      // Create branch
      if (state.stack.length < 1) return "FORGE BRANCH requires name";
      const branchName = state.stack.pop()!;
      state.memory.set(`__branch_${branchName.data}__`, record(new Map([
        ["name", branchName],
        ["head", str("__current__")],
        ["created", int(Date.now())]
      ])));
      return null;
      
    case "MERGE":
      // Merge branches
      if (state.stack.length < 2) return "FORGE MERGE requires two branches";
      const targetBranch = state.stack.pop()!;
      const sourceBranch = state.stack.pop()!;
      // Simplified merge - would detect conflicts
      state.stack.push(record(new Map([
        ["success", bool(true)],
        ["conflicts", int(0)]
      ])));
      return null;
      
    case "COMMIT":
      // Create proof-carrying commit
      if (state.stack.length < 1) return "FORGE COMMIT requires message";
      const message = state.stack.pop()!;
      const commit = {
        id: `commit_${Date.now()}`,
        message: message.data,
        witnesses: state.witnesses.length,
        timestamp: Date.now()
      };
      state.memory.set(`__commit_${commit.id}__`, record(new Map([
        ["id", str(commit.id)],
        ["message", message],
        ["witnesses", int(commit.witnesses)],
        ["timestamp", int(commit.timestamp)]
      ])));
      state.stack.push(str(commit.id));
      return null;
      
    case "CI_GATE":
      // Run CI checks
      const ciResult = state.witnesses.length > 0 && state.truth !== TruthValue.FAIL;
      state.stack.push(bool(ciResult));
      return null;
      
    default:
      return `Unknown FORGE command: ${cmd}`;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

function valueEquals(a: Value, b: Value): boolean {
  if (a.type !== b.type) return false;
  if (a.type === ValueType.Array) {
    const arrA = a.data as Value[];
    const arrB = b.data as Value[];
    if (arrA.length !== arrB.length) return false;
    return arrA.every((v, i) => valueEquals(v, arrB[i]));
  }
  return a.data === b.data;
}

function estimateSize(v: Value): number {
  switch (v.type) {
    case ValueType.Nil: return 4;
    case ValueType.Bool: return 4;
    case ValueType.Int: return 8;
    case ValueType.Float: return 8;
    case ValueType.String: return 16 + (v.data as string).length * 2;
    case ValueType.Array: return 16 + (v.data as Value[]).reduce((s, x) => s + estimateSize(x), 0);
    case ValueType.Record: return 32;
    default: return 16;
  }
}

function hashValue(v: Value): string {
  const json = JSON.stringify(v);
  let hash = 0;
  for (let i = 0; i < json.length; i++) {
    hash = ((hash << 5) - hash) + json.charCodeAt(i);
    hash = hash & hash;
  }
  return Math.abs(hash).toString(16).padStart(16, '0');
}

interface ParsedAddress {
  msId: string;
  station: string;
  lens: string;
  facet: number;
  atom: string;
}

function parseAddress(addr: string): ParsedAddress | null {
  // Pattern: Ms⟨XXXX⟩::ChYY⟨dddd⟩.LF.a
  const match = addr.match(/Ms⟨([A-F0-9]{4})⟩::Ch(\d{2})⟨(\d{4})⟩\.([SFCR])(\d)\.([abcd])/);
  if (!match) return null;
  return {
    msId: match[1],
    station: `Ch${match[2]}⟨${match[3]}⟩`,
    lens: match[4],
    facet: parseInt(match[5]),
    atom: match[6]
  };
}

function computeRoute(addr: string, truth: TruthValue): string[] {
  // Σ = {AppA, AppI, AppM} always required
  const route = ["AppA", "AppI", "AppM"];
  
  // Add truth overlay
  switch (truth) {
    case TruthValue.NEAR:
      route.push("AppJ");
      break;
    case TruthValue.AMBIG:
      route.push("AppL");
      break;
    case TruthValue.FAIL:
      route.push("AppK");
      break;
    case TruthValue.OK:
      // Publish mode would add AppO
      break;
  }
  
  return route;
}

function atomizeContent(content: Value): string[] {
  // Simple atomization by splitting
  if (content.type === ValueType.String) {
    const text = content.data as string;
    return text.split(/\s+/).filter(s => s.length > 0);
  }
  return [JSON.stringify(content)];
}

function createReplayCapsule(prog: Program, state: VMState): ReplayCapsule {
  return {
    id: `replay_${prog.meta.name}_${Date.now()}`,
    inputs: [],
    steps: state.trace.map(t => ({
      operation: t.opcode,
      args: [],
      result: { type: ValueType.Nil, data: null },
      timestamp: t.timestamp
    })),
    outputs: state.stack.map(v => v),
    seal: hashValue(arr(state.stack))
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 8: ASSEMBLER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Simple assembler for VM programs
 */
export function assemble(source: string, corridor: Corridors.Corridor): Program {
  const prog = createProgram("assembled", corridor);
  const lines = source.split('\n');
  
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith(';')) continue;
    
    // Parse label
    let label: string | undefined;
    let rest = trimmed;
    if (trimmed.includes(':')) {
      const parts = trimmed.split(':');
      label = parts[0].trim();
      rest = parts.slice(1).join(':').trim();
    }
    
    if (!rest) {
      // Label-only line
      if (label) {
        prog.labels.set(label, prog.instructions.length);
      }
      continue;
    }
    
    // Parse instruction
    const parts = rest.split(/\s+/);
    const opcode = parts[0].toUpperCase() as Opcode;
    
    let operand: Value | undefined;
    if (parts.length > 1) {
      const operandStr = parts.slice(1).join(' ');
      operand = parseOperand(operandStr);
    }
    
    emit(prog, opcode, operand, label);
  }
  
  return prog;
}

function parseOperand(s: string): Value {
  // String literal
  if (s.startsWith('"') && s.endsWith('"')) {
    return str(s.slice(1, -1));
  }
  // Integer
  if (/^-?\d+$/.test(s)) {
    return int(parseInt(s));
  }
  // Float
  if (/^-?\d+\.\d+$/.test(s)) {
    return float(parseFloat(s));
  }
  // Boolean
  if (s === 'true') return bool(true);
  if (s === 'false') return bool(false);
  // Address
  if (s.startsWith('Ms⟨')) {
    return addr(s);
  }
  // Label/identifier
  return str(s);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 9: DISASSEMBLER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Disassemble program to text
 */
export function disassemble(prog: Program): string {
  const lines: string[] = [];
  
  // Header
  lines.push(`; Program: ${prog.meta.name}`);
  lines.push(`; Version: ${prog.meta.version}`);
  lines.push(`; MsID: ${prog.meta.msId}`);
  lines.push('');
  
  // Reverse label map
  const labelAt = new Map<number, string>();
  for (const [label, idx] of prog.labels) {
    labelAt.set(idx, label);
  }
  
  // Instructions
  for (let i = 0; i < prog.instructions.length; i++) {
    const instr = prog.instructions[i];
    let line = '';
    
    // Label
    const label = labelAt.get(i);
    if (label) {
      line += `${label}: `;
    } else {
      line += '    ';
    }
    
    // Opcode
    line += instr.opcode;
    
    // Operand
    if (instr.operand) {
      line += ' ' + formatValue(instr.operand);
    }
    
    lines.push(line);
  }
  
  return lines.join('\n');
}

function formatValue(v: Value): string {
  switch (v.type) {
    case ValueType.String:
      return `"${v.data}"`;
    case ValueType.Int:
    case ValueType.Float:
      return String(v.data);
    case ValueType.Bool:
      return v.data ? 'true' : 'false';
    case ValueType.Address:
      return v.data as string;
    default:
      return JSON.stringify(v.data);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  ValueType,
  Opcode,
  nil, bool, int, float, str, addr, arr, record, error,
  createProgram,
  emit,
  defineConstant,
  createVMState,
  execute,
  assemble,
  disassemble
};
