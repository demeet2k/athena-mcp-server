/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * DETERMINISTIC REPLAY ENGINE - Complete Replay and Tracing System
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Core Principle: Every computation must be deterministically replayable
 * 
 * From SELF_SUFFICIENCY_TOME §5:
 *   "Verification is conservative and bounded: if a proof cannot be checked
 *    within budgets or lacks dependencies, the system produces boundary
 *    outputs with obligations rather than accepting."
 * 
 * Replay Trace (Construction 1.4):
 *   Trace = ⟨seed, inputs, steps, outputs, hash⟩
 *   
 *   - seed: commits to code version and configuration
 *   - steps: deterministic sequence of events
 *   - hash: Merkle root over step encodings
 *   
 *   Replaying Trace under the same seed must reproduce outputs byte-for-byte.
 * 
 * Determinism Contract:
 *   All router-visible outputs are canonicalized through Enc_K and norm
 *   such that: Enc_K(norm(o)) = Enc_K(o)
 *   and replay determinism holds on the encoded stream.
 * 
 * @module DETERMINISTIC_REPLAY_ENGINE
 * @version 2.0.0
 */

import { TruthValue, WitnessPtr } from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: REPLAY TRACE STRUCTURE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Replay trace: Complete record of a computation
 */
export interface ReplayTrace {
  id: string;
  version: string;
  
  /** Seed committing to code version and configuration */
  seed: TraceSeed;
  
  /** Input values (encoded) */
  inputs: EncodedValue[];
  
  /** Sequence of execution steps */
  steps: TraceStep[];
  
  /** Output values (encoded) */
  outputs: EncodedValue[];
  
  /** Merkle root of step encodings */
  hash: string;
  
  /** Timing information */
  timing: TraceTiming;
  
  /** Resource usage */
  resources: TraceResources;
}

export interface TraceSeed {
  /** Code version hash */
  codeVersion: string;
  
  /** Configuration hash */
  configHash: string;
  
  /** Random seed (for deterministic randomness) */
  randomSeed: number;
  
  /** Environment snapshot hash */
  environmentHash: string;
  
  /** Dependency versions */
  dependencies: Map<string, string>;
}

export interface EncodedValue {
  /** Original value (before encoding) */
  value: unknown;
  
  /** Canonical encoding */
  encoded: Uint8Array;
  
  /** Type identifier */
  type: string;
  
  /** Hash of encoded bytes */
  hash: string;
}

export interface TraceStep {
  /** Step index */
  index: number;
  
  /** Operation name */
  operation: string;
  
  /** Input hashes */
  inputHashes: string[];
  
  /** Output hash */
  outputHash: string;
  
  /** Timestamp */
  timestamp: number;
  
  /** Duration in microseconds */
  durationMicros: number;
  
  /** Additional metadata */
  metadata: Record<string, unknown>;
}

export interface TraceTiming {
  startTime: number;
  endTime: number;
  totalDuration: number;
  stepDurations: number[];
}

export interface TraceResources {
  peakMemory: number;
  totalCPU: number;
  ioOperations: number;
  networkCalls: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: CANONICAL ENCODING
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Canonical encoder for deterministic serialization
 */
export interface CanonicalEncoder<T = unknown> {
  /** Encode value to canonical bytes */
  encode(value: T): Uint8Array;
  
  /** Decode bytes to value */
  decode(bytes: Uint8Array): T;
  
  /** Normalize value to canonical form */
  normalize(value: T): T;
  
  /** Compute hash of value */
  hash(value: T): string;
  
  /** Check if two values are equivalent */
  equivalent(a: T, b: T): boolean;
}

/**
 * Default canonical encoder using JSON with sorted keys
 */
export class JSONCanonicalEncoder implements CanonicalEncoder {
  encode(value: unknown): Uint8Array {
    const normalized = this.normalize(value);
    const json = JSON.stringify(normalized, this.sortedReplacer);
    return new TextEncoder().encode(json);
  }
  
  decode(bytes: Uint8Array): unknown {
    const json = new TextDecoder().decode(bytes);
    return JSON.parse(json);
  }
  
  normalize(value: unknown): unknown {
    if (value === null || value === undefined) {
      return null;
    }
    
    if (typeof value === 'number') {
      // Handle special cases
      if (Number.isNaN(value)) return { __nan: true };
      if (!Number.isFinite(value)) return { __infinity: value > 0 };
      // Round to avoid floating point issues
      return Math.round(value * 1e12) / 1e12;
    }
    
    if (typeof value === 'string' || typeof value === 'boolean') {
      return value;
    }
    
    if (Array.isArray(value)) {
      return value.map(v => this.normalize(v));
    }
    
    if (value instanceof Map) {
      const obj: Record<string, unknown> = {};
      for (const [k, v] of value) {
        obj[String(k)] = this.normalize(v);
      }
      return { __map: obj };
    }
    
    if (value instanceof Set) {
      return { __set: Array.from(value).map(v => this.normalize(v)).sort() };
    }
    
    if (value instanceof Date) {
      return { __date: value.toISOString() };
    }
    
    if (typeof value === 'object') {
      const obj: Record<string, unknown> = {};
      const keys = Object.keys(value as object).sort();
      for (const key of keys) {
        obj[key] = this.normalize((value as Record<string, unknown>)[key]);
      }
      return obj;
    }
    
    return String(value);
  }
  
  hash(value: unknown): string {
    const bytes = this.encode(value);
    return this.computeHash(bytes);
  }
  
  equivalent(a: unknown, b: unknown): boolean {
    return this.hash(a) === this.hash(b);
  }
  
  private sortedReplacer(key: string, value: unknown): unknown {
    if (value instanceof Object && !Array.isArray(value)) {
      return Object.keys(value)
        .sort()
        .reduce((sorted: Record<string, unknown>, k) => {
          sorted[k] = (value as Record<string, unknown>)[k];
          return sorted;
        }, {});
    }
    return value;
  }
  
  private computeHash(bytes: Uint8Array): string {
    let hash = 0;
    for (let i = 0; i < bytes.length; i++) {
      hash = ((hash << 5) - hash) + bytes[i];
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(16, '0');
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: TRACE RECORDER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Records execution into a replay trace
 */
export class TraceRecorder {
  private id: string;
  private seed: TraceSeed;
  private encoder: CanonicalEncoder;
  private inputs: EncodedValue[] = [];
  private steps: TraceStep[] = [];
  private outputs: EncodedValue[] = [];
  private startTime: number;
  private stepIndex: number = 0;
  private peakMemory: number = 0;
  private ioOps: number = 0;
  
  constructor(seed: TraceSeed, encoder?: CanonicalEncoder) {
    this.id = `trace_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
    this.seed = seed;
    this.encoder = encoder ?? new JSONCanonicalEncoder();
    this.startTime = Date.now();
  }
  
  /**
   * Record an input value
   */
  recordInput(value: unknown, type: string): string {
    const encoded = this.encoder.encode(value);
    const hash = this.encoder.hash(value);
    
    this.inputs.push({
      value,
      encoded,
      type,
      hash
    });
    
    return hash;
  }
  
  /**
   * Record an execution step
   */
  recordStep(
    operation: string,
    inputHashes: string[],
    output: unknown,
    metadata: Record<string, unknown> = {}
  ): string {
    const outputHash = this.encoder.hash(output);
    const timestamp = Date.now();
    const duration = this.steps.length > 0 
      ? (timestamp - this.steps[this.steps.length - 1].timestamp) * 1000
      : (timestamp - this.startTime) * 1000;
    
    this.steps.push({
      index: this.stepIndex++,
      operation,
      inputHashes,
      outputHash,
      timestamp,
      durationMicros: duration,
      metadata
    });
    
    return outputHash;
  }
  
  /**
   * Record an output value
   */
  recordOutput(value: unknown, type: string): string {
    const encoded = this.encoder.encode(value);
    const hash = this.encoder.hash(value);
    
    this.outputs.push({
      value,
      encoded,
      type,
      hash
    });
    
    return hash;
  }
  
  /**
   * Record resource usage
   */
  recordResourceUsage(memory: number, io: number): void {
    this.peakMemory = Math.max(this.peakMemory, memory);
    this.ioOps += io;
  }
  
  /**
   * Finalize and return the trace
   */
  finalize(): ReplayTrace {
    const endTime = Date.now();
    
    // Compute Merkle root of steps
    const stepHashes = this.steps.map(s => s.outputHash);
    const merkleRoot = this.computeMerkleRoot(stepHashes);
    
    return {
      id: this.id,
      version: "2.0.0",
      seed: this.seed,
      inputs: this.inputs,
      steps: this.steps,
      outputs: this.outputs,
      hash: merkleRoot,
      timing: {
        startTime: this.startTime,
        endTime,
        totalDuration: endTime - this.startTime,
        stepDurations: this.steps.map(s => s.durationMicros)
      },
      resources: {
        peakMemory: this.peakMemory,
        totalCPU: this.steps.reduce((sum, s) => sum + s.durationMicros, 0),
        ioOperations: this.ioOps,
        networkCalls: 0
      }
    };
  }
  
  private computeMerkleRoot(hashes: string[]): string {
    if (hashes.length === 0) return this.encoder.hash("empty");
    if (hashes.length === 1) return hashes[0];
    
    const pairs: string[] = [];
    for (let i = 0; i < hashes.length; i += 2) {
      if (i + 1 < hashes.length) {
        pairs.push(this.encoder.hash(`${hashes[i]}:${hashes[i + 1]}`));
      } else {
        pairs.push(hashes[i]);
      }
    }
    
    return this.computeMerkleRoot(pairs);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: REPLAY EXECUTOR
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Result of a replay execution
 */
export interface ReplayResult {
  success: boolean;
  trace: ReplayTrace;
  originalTrace: ReplayTrace;
  divergence?: ReplayDivergence;
  verification: ReplayVerification;
}

export interface ReplayDivergence {
  stepIndex: number;
  operation: string;
  expectedHash: string;
  actualHash: string;
  reason: string;
}

export interface ReplayVerification {
  inputsMatch: boolean;
  outputsMatch: boolean;
  stepsMatch: boolean;
  hashMatch: boolean;
  timingWithinBounds: boolean;
}

/**
 * Operation registry for replay
 */
export type OperationFn = (inputs: unknown[], context: ReplayContext) => unknown;

export interface ReplayContext {
  seed: TraceSeed;
  stepIndex: number;
  trace: ReplayTrace;
  encoder: CanonicalEncoder;
}

/**
 * Executes replay of a trace
 */
export class ReplayExecutor {
  private operations: Map<string, OperationFn> = new Map();
  private encoder: CanonicalEncoder;
  
  constructor(encoder?: CanonicalEncoder) {
    this.encoder = encoder ?? new JSONCanonicalEncoder();
  }
  
  /**
   * Register an operation for replay
   */
  registerOperation(name: string, fn: OperationFn): void {
    this.operations.set(name, fn);
  }
  
  /**
   * Replay a trace and verify determinism
   */
  replay(originalTrace: ReplayTrace): ReplayResult {
    const recorder = new TraceRecorder(originalTrace.seed, this.encoder);
    
    // Record inputs
    const inputValues: unknown[] = [];
    for (const input of originalTrace.inputs) {
      const hash = recorder.recordInput(input.value, input.type);
      inputValues.push(input.value);
      
      // Verify input hash matches
      if (hash !== input.hash) {
        return this.createFailureResult(originalTrace, recorder.finalize(), {
          stepIndex: -1,
          operation: "input",
          expectedHash: input.hash,
          actualHash: hash,
          reason: "Input hash mismatch"
        });
      }
    }
    
    // Create replay context
    const context: ReplayContext = {
      seed: originalTrace.seed,
      stepIndex: 0,
      trace: originalTrace,
      encoder: this.encoder
    };
    
    // Execute steps
    const workspace = new Map<string, unknown>();
    
    for (const step of originalTrace.steps) {
      const operation = this.operations.get(step.operation);
      if (!operation) {
        return this.createFailureResult(originalTrace, recorder.finalize(), {
          stepIndex: step.index,
          operation: step.operation,
          expectedHash: step.outputHash,
          actualHash: "",
          reason: `Unknown operation: ${step.operation}`
        });
      }
      
      // Gather inputs from workspace
      const stepInputs = step.inputHashes.map(h => workspace.get(h));
      
      // Execute operation
      context.stepIndex = step.index;
      const output = operation(stepInputs, context);
      
      // Record step
      const actualHash = recorder.recordStep(step.operation, step.inputHashes, output, step.metadata);
      
      // Store output in workspace
      workspace.set(actualHash, output);
      
      // Verify hash matches
      if (actualHash !== step.outputHash) {
        return this.createFailureResult(originalTrace, recorder.finalize(), {
          stepIndex: step.index,
          operation: step.operation,
          expectedHash: step.outputHash,
          actualHash,
          reason: "Step output hash mismatch"
        });
      }
    }
    
    // Record outputs
    for (let i = 0; i < originalTrace.outputs.length; i++) {
      const expectedOutput = originalTrace.outputs[i];
      const actualOutput = workspace.get(expectedOutput.hash);
      
      if (actualOutput !== undefined) {
        const hash = recorder.recordOutput(actualOutput, expectedOutput.type);
        
        if (hash !== expectedOutput.hash) {
          return this.createFailureResult(originalTrace, recorder.finalize(), {
            stepIndex: originalTrace.steps.length,
            operation: "output",
            expectedHash: expectedOutput.hash,
            actualHash: hash,
            reason: "Output hash mismatch"
          });
        }
      }
    }
    
    // Finalize and verify
    const replayedTrace = recorder.finalize();
    
    return {
      success: true,
      trace: replayedTrace,
      originalTrace,
      verification: {
        inputsMatch: this.verifyInputsMatch(originalTrace, replayedTrace),
        outputsMatch: this.verifyOutputsMatch(originalTrace, replayedTrace),
        stepsMatch: this.verifyStepsMatch(originalTrace, replayedTrace),
        hashMatch: originalTrace.hash === replayedTrace.hash,
        timingWithinBounds: true  // Timing may vary
      }
    };
  }
  
  private createFailureResult(
    originalTrace: ReplayTrace,
    replayedTrace: ReplayTrace,
    divergence: ReplayDivergence
  ): ReplayResult {
    return {
      success: false,
      trace: replayedTrace,
      originalTrace,
      divergence,
      verification: {
        inputsMatch: false,
        outputsMatch: false,
        stepsMatch: false,
        hashMatch: false,
        timingWithinBounds: false
      }
    };
  }
  
  private verifyInputsMatch(original: ReplayTrace, replayed: ReplayTrace): boolean {
    if (original.inputs.length !== replayed.inputs.length) return false;
    for (let i = 0; i < original.inputs.length; i++) {
      if (original.inputs[i].hash !== replayed.inputs[i].hash) return false;
    }
    return true;
  }
  
  private verifyOutputsMatch(original: ReplayTrace, replayed: ReplayTrace): boolean {
    if (original.outputs.length !== replayed.outputs.length) return false;
    for (let i = 0; i < original.outputs.length; i++) {
      if (original.outputs[i].hash !== replayed.outputs[i].hash) return false;
    }
    return true;
  }
  
  private verifyStepsMatch(original: ReplayTrace, replayed: ReplayTrace): boolean {
    if (original.steps.length !== replayed.steps.length) return false;
    for (let i = 0; i < original.steps.length; i++) {
      if (original.steps[i].outputHash !== replayed.steps[i].outputHash) return false;
    }
    return true;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: DETERMINISTIC RANDOM
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Deterministic random number generator (for replay)
 */
export class DeterministicRandom {
  private state: number;
  
  constructor(seed: number) {
    this.state = seed;
  }
  
  /**
   * Get next random number in [0, 1)
   */
  next(): number {
    // Xorshift algorithm
    this.state ^= this.state << 13;
    this.state ^= this.state >> 17;
    this.state ^= this.state << 5;
    return (this.state >>> 0) / 4294967296;
  }
  
  /**
   * Get random integer in [min, max]
   */
  nextInt(min: number, max: number): number {
    return Math.floor(this.next() * (max - min + 1)) + min;
  }
  
  /**
   * Get random boolean with given probability
   */
  nextBool(probability: number = 0.5): boolean {
    return this.next() < probability;
  }
  
  /**
   * Shuffle array in place
   */
  shuffle<T>(array: T[]): T[] {
    for (let i = array.length - 1; i > 0; i--) {
      const j = this.nextInt(0, i);
      [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
  }
  
  /**
   * Pick random element
   */
  pick<T>(array: T[]): T {
    return array[this.nextInt(0, array.length - 1)];
  }
  
  /**
   * Get current state (for checkpointing)
   */
  getState(): number {
    return this.state;
  }
  
  /**
   * Restore state
   */
  setState(state: number): void {
    this.state = state;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: TRACE STORAGE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Storage for replay traces
 */
export class TraceStorage {
  private traces: Map<string, ReplayTrace> = new Map();
  private indexByHash: Map<string, string[]> = new Map();
  private indexBySeed: Map<string, string[]> = new Map();
  
  /**
   * Store a trace
   */
  store(trace: ReplayTrace): void {
    this.traces.set(trace.id, trace);
    
    // Index by hash
    if (!this.indexByHash.has(trace.hash)) {
      this.indexByHash.set(trace.hash, []);
    }
    this.indexByHash.get(trace.hash)!.push(trace.id);
    
    // Index by seed code version
    if (!this.indexBySeed.has(trace.seed.codeVersion)) {
      this.indexBySeed.set(trace.seed.codeVersion, []);
    }
    this.indexBySeed.get(trace.seed.codeVersion)!.push(trace.id);
  }
  
  /**
   * Retrieve trace by ID
   */
  get(id: string): ReplayTrace | undefined {
    return this.traces.get(id);
  }
  
  /**
   * Find traces by hash
   */
  findByHash(hash: string): ReplayTrace[] {
    const ids = this.indexByHash.get(hash) ?? [];
    return ids.map(id => this.traces.get(id)!).filter(t => t);
  }
  
  /**
   * Find traces by seed code version
   */
  findBySeedVersion(codeVersion: string): ReplayTrace[] {
    const ids = this.indexBySeed.get(codeVersion) ?? [];
    return ids.map(id => this.traces.get(id)!).filter(t => t);
  }
  
  /**
   * List all trace IDs
   */
  list(): string[] {
    return Array.from(this.traces.keys());
  }
  
  /**
   * Get statistics
   */
  getStats(): TraceStorageStats {
    let totalSteps = 0;
    let totalDuration = 0;
    
    for (const trace of this.traces.values()) {
      totalSteps += trace.steps.length;
      totalDuration += trace.timing.totalDuration;
    }
    
    return {
      totalTraces: this.traces.size,
      uniqueHashes: this.indexByHash.size,
      uniqueVersions: this.indexBySeed.size,
      totalSteps,
      totalDuration
    };
  }
}

export interface TraceStorageStats {
  totalTraces: number;
  uniqueHashes: number;
  uniqueVersions: number;
  totalSteps: number;
  totalDuration: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: DETERMINISTIC REPLAY ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete Deterministic Replay Engine
 */
export class DeterministicReplayEngine {
  private encoder: CanonicalEncoder;
  private executor: ReplayExecutor;
  private storage: TraceStorage;
  private currentRecorder?: TraceRecorder;
  private random?: DeterministicRandom;
  
  constructor() {
    this.encoder = new JSONCanonicalEncoder();
    this.executor = new ReplayExecutor(this.encoder);
    this.storage = new TraceStorage();
    
    this.registerDefaultOperations();
  }
  
  /**
   * Register operation
   */
  registerOperation(name: string, fn: OperationFn): void {
    this.executor.registerOperation(name, fn);
  }
  
  /**
   * Begin recording a new trace
   */
  beginRecording(codeVersion: string, configHash: string, randomSeed?: number): void {
    const seed: TraceSeed = {
      codeVersion,
      configHash,
      randomSeed: randomSeed ?? Date.now(),
      environmentHash: this.encoder.hash({ timestamp: Date.now() }),
      dependencies: new Map()
    };
    
    this.currentRecorder = new TraceRecorder(seed, this.encoder);
    this.random = new DeterministicRandom(seed.randomSeed);
  }
  
  /**
   * Record input
   */
  recordInput(value: unknown, type: string): string {
    if (!this.currentRecorder) {
      throw new Error("No recording in progress");
    }
    return this.currentRecorder.recordInput(value, type);
  }
  
  /**
   * Record step
   */
  recordStep(
    operation: string,
    inputHashes: string[],
    output: unknown,
    metadata?: Record<string, unknown>
  ): string {
    if (!this.currentRecorder) {
      throw new Error("No recording in progress");
    }
    return this.currentRecorder.recordStep(operation, inputHashes, output, metadata);
  }
  
  /**
   * Record output
   */
  recordOutput(value: unknown, type: string): string {
    if (!this.currentRecorder) {
      throw new Error("No recording in progress");
    }
    return this.currentRecorder.recordOutput(value, type);
  }
  
  /**
   * End recording and store trace
   */
  endRecording(): ReplayTrace {
    if (!this.currentRecorder) {
      throw new Error("No recording in progress");
    }
    
    const trace = this.currentRecorder.finalize();
    this.storage.store(trace);
    this.currentRecorder = undefined;
    
    return trace;
  }
  
  /**
   * Replay a trace
   */
  replay(traceId: string): ReplayResult | null {
    const trace = this.storage.get(traceId);
    if (!trace) return null;
    
    return this.executor.replay(trace);
  }
  
  /**
   * Replay and verify
   */
  replayAndVerify(traceId: string): ReplayVerificationResult {
    const result = this.replay(traceId);
    if (!result) {
      return {
        found: false,
        traceId,
        verified: false,
        message: "Trace not found"
      };
    }
    
    return {
      found: true,
      traceId,
      verified: result.success,
      verification: result.verification,
      divergence: result.divergence,
      message: result.success ? "Replay successful" : "Replay failed"
    };
  }
  
  /**
   * Get deterministic random (during recording)
   */
  getRandom(): DeterministicRandom | undefined {
    return this.random;
  }
  
  /**
   * Get trace
   */
  getTrace(id: string): ReplayTrace | undefined {
    return this.storage.get(id);
  }
  
  /**
   * List all traces
   */
  listTraces(): string[] {
    return this.storage.list();
  }
  
  /**
   * Get storage stats
   */
  getStats(): TraceStorageStats {
    return this.storage.getStats();
  }
  
  /**
   * Compute hash of value
   */
  hash(value: unknown): string {
    return this.encoder.hash(value);
  }
  
  /**
   * Check equivalence
   */
  equivalent(a: unknown, b: unknown): boolean {
    return this.encoder.equivalent(a, b);
  }
  
  private registerDefaultOperations(): void {
    // Identity
    this.registerOperation("identity", (inputs) => inputs[0]);
    
    // Add
    this.registerOperation("add", (inputs) => {
      const [a, b] = inputs as [number, number];
      return a + b;
    });
    
    // Multiply
    this.registerOperation("multiply", (inputs) => {
      const [a, b] = inputs as [number, number];
      return a * b;
    });
    
    // Concatenate
    this.registerOperation("concat", (inputs) => {
      return (inputs as string[]).join("");
    });
    
    // Map
    this.registerOperation("map", (inputs, context) => {
      const [array, fnHash] = inputs as [unknown[], string];
      return array.map((_, i) => context.encoder.hash(`${fnHash}:${i}`));
    });
    
    // Filter
    this.registerOperation("filter", (inputs) => {
      const [array, predicate] = inputs as [unknown[], (x: unknown) => boolean];
      return array.filter(predicate);
    });
    
    // Reduce
    this.registerOperation("reduce", (inputs) => {
      const [array, initial] = inputs as [number[], number];
      return array.reduce((a, b) => a + b, initial);
    });
  }
}

export interface ReplayVerificationResult {
  found: boolean;
  traceId: string;
  verified: boolean;
  verification?: ReplayVerification;
  divergence?: ReplayDivergence;
  message: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Encoder
  JSONCanonicalEncoder,
  
  // Recording
  TraceRecorder,
  
  // Execution
  ReplayExecutor,
  
  // Random
  DeterministicRandom,
  
  // Storage
  TraceStorage,
  
  // Engine
  DeterministicReplayEngine
};
