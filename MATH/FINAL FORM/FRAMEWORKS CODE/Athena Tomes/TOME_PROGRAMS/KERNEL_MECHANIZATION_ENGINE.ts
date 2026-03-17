/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * KERNEL MECHANIZATION ENGINE - APIs, Verifier Contracts & Build System
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * From SELF_SUFFICIENCY_TOME Ch17:
 * 
 * Core Laws:
 *   - Law 17.1 (Determinism): Identical inputs/seeds/deps yield identical outputs
 *   - Law 17.2 (Purity typing): Pure/TraceOnly/ScopedIO/Forbidden effect types
 *   - Law 17.3 (Total routing): All functions return Out(τ), never crash
 *   - Law 17.4 (ABI canonicalization): Equal objects encode identically
 *   - Law 17.9 (Reproducible build): Same inputs → same outputs
 *   - Law 17.10 (Dependency closure): Complete deps or boundary
 * 
 * The kernel is the minimal trusted computing base that:
 *   1. Defines canonical data types and encodings
 *   2. Executes total routing (bulk⊕boundary) deterministically
 *   3. Verifies certificates under explicit complexity budgets
 *   4. Records replayable event logs with Merkle linking
 * 
 * @module KERNEL_MECHANIZATION_ENGINE
 * @version 2.0.0
 */

import { TruthValue, WitnessPtr } from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: KERNEL TYPES AND ABI
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Effect types for kernel functions (Law 17.2)
 */
export enum EffectType {
  Pure = "Pure",           // No external I/O, deterministic
  TraceOnly = "TraceOnly", // Appends to event log deterministically
  ScopedIO = "ScopedIO",   // I/O through capability-authorized channels
  Forbidden = "Forbidden"  // Disallowed inside kernel
}

/**
 * Core kernel type registry
 */
export enum KernelType {
  Addr = "Addr",
  Seed = "Seed",
  Regime = "Regime",
  State = "State",
  Corridor = "Corridor",
  Out = "Out",
  Boundary = "Boundary",
  Evidence = "Evidence",
  Detector = "Detector",
  Cert = "Cert",
  Trace = "Trace",
  MerkleRef = "MerkleRef",
  Artifact = "Artifact"
}

/**
 * Schema with hash for canonical encoding
 */
export interface TypeSchema {
  type: KernelType;
  version: string;
  fields: SchemaField[];
  hash: string;
}

export interface SchemaField {
  name: string;
  type: string;
  required: boolean;
  encoding: "fixed" | "varint" | "string" | "bytes" | "nested";
}

/**
 * Canonical encoder/decoder for kernel types
 */
export interface Codec<T> {
  type: KernelType;
  schemaHash: string;
  
  encode(value: T): Uint8Array;
  decode(bytes: Uint8Array): T | { error: string };
  normalize(value: T): T;
  hash(value: T): string;
}

/**
 * Kernel ABI definition
 */
export interface KernelABI {
  version: string;
  schemas: Map<KernelType, TypeSchema>;
  functionSignatures: Map<string, ABIFunction>;
  versionNegotiation: VersionNegotiation;
  hash: string;
}

export interface ABIFunction {
  name: string;
  inputs: ABIParameter[];
  outputs: ABIParameter[];
  effectType: EffectType;
  corridorRequirements: string[];
  deterministicSeeds: boolean;
  certificateHooks: string[];
}

export interface ABIParameter {
  name: string;
  type: KernelType;
  schemaHash: string;
}

export interface VersionNegotiation {
  minVersion: string;
  maxVersion: string;
  adaptableVersions: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: CODEC IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Generic codec implementation
 */
export class GenericCodec<T> implements Codec<T> {
  type: KernelType;
  schemaHash: string;
  private schema: TypeSchema;
  
  constructor(schema: TypeSchema) {
    this.type = schema.type;
    this.schema = schema;
    this.schemaHash = schema.hash;
  }
  
  /**
   * Encode value to canonical bytes
   */
  encode(value: T): Uint8Array {
    // Normalize first for canonical encoding
    const normalized = this.normalize(value);
    const json = JSON.stringify(normalized, this.canonicalReplacer);
    return new TextEncoder().encode(json);
  }
  
  /**
   * Decode bytes to value
   */
  decode(bytes: Uint8Array): T | { error: string } {
    try {
      const json = new TextDecoder().decode(bytes);
      return JSON.parse(json) as T;
    } catch (e) {
      return { error: `Decode error: ${e}` };
    }
  }
  
  /**
   * Normalize value to canonical form
   */
  normalize(value: T): T {
    // Deep sort object keys for canonical ordering
    return this.deepSortKeys(value) as T;
  }
  
  /**
   * Compute hash of value
   */
  hash(value: T): string {
    const encoded = this.encode(value);
    return this.computeHash(encoded);
  }
  
  private canonicalReplacer(key: string, value: unknown): unknown {
    if (value instanceof Map) {
      const entries = Array.from(value.entries()).sort((a, b) => 
        String(a[0]).localeCompare(String(b[0]))
      );
      return { __type: "Map", entries };
    }
    if (value instanceof Set) {
      return { __type: "Set", values: Array.from(value).sort() };
    }
    return value;
  }
  
  private deepSortKeys(obj: unknown): unknown {
    if (obj === null || typeof obj !== 'object') return obj;
    if (Array.isArray(obj)) return obj.map(v => this.deepSortKeys(v));
    
    const sorted: Record<string, unknown> = {};
    const keys = Object.keys(obj as Record<string, unknown>).sort();
    for (const key of keys) {
      sorted[key] = this.deepSortKeys((obj as Record<string, unknown>)[key]);
    }
    return sorted;
  }
  
  private computeHash(data: Uint8Array): string {
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
      hash = ((hash << 5) - hash) + data[i];
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(8, '0');
  }
}

/**
 * Codec registry
 */
export class CodecRegistry {
  private codecs: Map<KernelType, Codec<unknown>> = new Map();
  private schemas: Map<KernelType, TypeSchema> = new Map();
  
  /**
   * Register codec for type
   */
  register<T>(schema: TypeSchema): void {
    const codec = new GenericCodec<T>(schema);
    this.codecs.set(schema.type, codec as Codec<unknown>);
    this.schemas.set(schema.type, schema);
  }
  
  /**
   * Get codec for type
   */
  get<T>(type: KernelType): Codec<T> | undefined {
    return this.codecs.get(type) as Codec<T> | undefined;
  }
  
  /**
   * Get schema for type
   */
  getSchema(type: KernelType): TypeSchema | undefined {
    return this.schemas.get(type);
  }
  
  /**
   * Verify round-trip encoding
   */
  verifyRoundTrip<T>(type: KernelType, value: T): boolean {
    const codec = this.get<T>(type);
    if (!codec) return false;
    
    const encoded = codec.encode(value);
    const decoded = codec.decode(encoded);
    
    if ('error' in (decoded as object)) return false;
    
    const reEncoded = codec.encode(decoded as T);
    return this.arraysEqual(encoded, reEncoded);
  }
  
  private arraysEqual(a: Uint8Array, b: Uint8Array): boolean {
    if (a.length !== b.length) return false;
    for (let i = 0; i < a.length; i++) {
      if (a[i] !== b[i]) return false;
    }
    return true;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: ROUTER MODULE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Boundary kind
 */
export enum BoundaryKind {
  Undefined = "Undefined",
  Singular = "Singular",
  Ambiguous = "Ambiguous",
  OutOfCorridor = "OutOfCorridor",
  UnderResolved = "UnderResolved",
  NonTerminating = "NonTerminating",
  UnsupportedVersion = "UnsupportedVersion",
  MissingDependency = "MissingDependency"
}

/**
 * Boundary record
 */
export interface BoundaryRecord {
  kind: BoundaryKind;
  code: string;
  location: string;
  obligations: string[];
  witness?: unknown;
  timestamp: number;
  hash: string;
}

/**
 * Output type: Bulk ⊕ Boundary (Law 17.3)
 */
export type Out<T> = 
  | { type: "Bulk"; value: T }
  | { type: "Boundary"; boundary: BoundaryRecord };

/**
 * Create bulk output
 */
export function bulk<T>(value: T): Out<T> {
  return { type: "Bulk", value };
}

/**
 * Create boundary output
 */
export function boundary<T>(kind: BoundaryKind, obligations: string[]): Out<T> {
  return {
    type: "Boundary",
    boundary: {
      kind,
      code: kind,
      location: "",
      obligations,
      timestamp: Date.now(),
      hash: ""
    }
  };
}

/**
 * Router module
 */
export class RouterModule {
  private boundaryRegistry: Map<string, BoundaryRecord> = new Map();
  
  /**
   * Route result to Bulk or Boundary
   */
  route<T>(
    result: T | null | undefined,
    errorCondition: () => BoundaryKind | null,
    obligations: () => string[]
  ): Out<T> {
    const boundaryKind = errorCondition();
    
    if (boundaryKind !== null) {
      return this.createBoundary(boundaryKind, obligations());
    }
    
    if (result === null || result === undefined) {
      return this.createBoundary(BoundaryKind.Undefined, ["Provide valid result"]);
    }
    
    return bulk(result);
  }
  
  /**
   * Create boundary with registration
   */
  createBoundary<T>(kind: BoundaryKind, obligations: string[]): Out<T> {
    const record: BoundaryRecord = {
      kind,
      code: kind,
      location: new Error().stack?.split('\n')[2] ?? "",
      obligations,
      timestamp: Date.now(),
      hash: ""
    };
    
    record.hash = this.hashBoundary(record);
    this.boundaryRegistry.set(record.hash, record);
    
    return { type: "Boundary", boundary: record };
  }
  
  /**
   * Get boundary by hash
   */
  getBoundary(hash: string): BoundaryRecord | undefined {
    return this.boundaryRegistry.get(hash);
  }
  
  private hashBoundary(record: BoundaryRecord): string {
    const data = `${record.kind}:${record.code}:${record.timestamp}`;
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
      hash = ((hash << 5) - hash) + data.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(8, '0');
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: COMPLEXITY BUDGETS AND VERIFIER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complexity budget (Definition 17.7)
 */
export interface ComplexityBudget {
  maxTime: number;      // t_max in ms
  maxMemory: number;    // m_max in bytes
  maxStack: number;     // s_max depth
  maxSteps: number;     // steps_max
  maxIO: number;        // io_max operations
}

/**
 * Verification result
 */
export interface VerificationResult {
  accepted: boolean;
  reason: string;
  counterWitness?: unknown;
  cost: ResourceUsage;
  trace: VerificationTrace;
  hash: string;
}

export interface ResourceUsage {
  time: number;
  memory: number;
  steps: number;
  io: number;
}

export interface VerificationTrace {
  steps: VerificationStep[];
  merkleRefs: string[];
  timestamp: number;
}

export interface VerificationStep {
  operation: string;
  input: string;
  output: string;
  cost: number;
}

/**
 * Certificate structure
 */
export interface Certificate {
  id: string;
  claim: CertificateClaim;
  assumptions: string[];
  witness: unknown;
  dependencies: string[];  // Merkle refs
  complexity: number;      // Expected verification cost
  encoding: Uint8Array;
  hash: string;
}

export interface CertificateClaim {
  type: string;
  proposition: string;
  context: Record<string, unknown>;
}

/**
 * Verifier kernel (Construction 17.5)
 */
export class VerifierKernel {
  private budget: ComplexityBudget;
  private usage: ResourceUsage = { time: 0, memory: 0, steps: 0, io: 0 };
  private trace: VerificationTrace;
  
  constructor(budget: ComplexityBudget) {
    this.budget = budget;
    this.trace = { steps: [], merkleRefs: [], timestamp: Date.now() };
  }
  
  /**
   * Verify certificate (Law 17.7: Bounded verification)
   */
  verify(cert: Certificate): Out<VerificationResult> {
    const startTime = Date.now();
    this.usage = { time: 0, memory: 0, steps: 0, io: 0 };
    
    // Step 1: Parse and validate encoding
    const parseResult = this.parseAndValidate(cert);
    if (!parseResult.valid) {
      return boundary(BoundaryKind.Ambiguous, [parseResult.reason]);
    }
    
    // Step 2: Resolve dependencies
    const depsResult = this.resolveDependencies(cert.dependencies);
    if (!depsResult.resolved) {
      return boundary(BoundaryKind.MissingDependency, depsResult.missing);
    }
    
    // Step 3: Check budget
    if (this.exceedsBudget()) {
      return boundary(BoundaryKind.OutOfCorridor, ["Budget exceeded"]);
    }
    
    // Step 4: Run bounded verification
    const verifyResult = this.runBoundedVerification(cert);
    
    this.usage.time = Date.now() - startTime;
    
    const result: VerificationResult = {
      accepted: verifyResult.accepted,
      reason: verifyResult.reason,
      counterWitness: verifyResult.counterWitness,
      cost: { ...this.usage },
      trace: { ...this.trace },
      hash: this.hashResult(verifyResult)
    };
    
    return bulk(result);
  }
  
  private parseAndValidate(cert: Certificate): { valid: boolean; reason: string } {
    this.recordStep("parse", cert.id, "validating");
    
    // Check claim structure
    if (!cert.claim || !cert.claim.type || !cert.claim.proposition) {
      return { valid: false, reason: "Invalid claim structure" };
    }
    
    // Check witness presence
    if (cert.witness === undefined) {
      return { valid: false, reason: "Missing witness" };
    }
    
    // Check hash integrity
    const computedHash = this.computeCertHash(cert);
    if (computedHash !== cert.hash) {
      return { valid: false, reason: "Hash mismatch" };
    }
    
    return { valid: true, reason: "OK" };
  }
  
  private resolveDependencies(deps: string[]): { resolved: boolean; missing: string[] } {
    this.recordStep("resolve_deps", deps.join(","), "checking");
    
    // In production, would fetch from Merkle store
    // For now, assume all dependencies are resolvable
    const missing: string[] = [];
    
    for (const dep of deps) {
      this.trace.merkleRefs.push(dep);
      this.usage.io++;
      
      // Simulate dependency check
      if (dep.startsWith("INVALID_")) {
        missing.push(dep);
      }
    }
    
    return { resolved: missing.length === 0, missing };
  }
  
  private exceedsBudget(): boolean {
    return (
      this.usage.time > this.budget.maxTime ||
      this.usage.memory > this.budget.maxMemory ||
      this.usage.steps > this.budget.maxSteps ||
      this.usage.io > this.budget.maxIO
    );
  }
  
  private runBoundedVerification(cert: Certificate): { 
    accepted: boolean; 
    reason: string; 
    counterWitness?: unknown 
  } {
    this.recordStep("verify", cert.claim.proposition, "running");
    
    // Simulate verification based on claim type
    switch (cert.claim.type) {
      case "equality":
        return this.verifyEquality(cert);
      case "membership":
        return this.verifyMembership(cert);
      case "bound":
        return this.verifyBound(cert);
      case "replay":
        return this.verifyReplay(cert);
      default:
        return { accepted: false, reason: `Unknown claim type: ${cert.claim.type}` };
    }
  }
  
  private verifyEquality(cert: Certificate): { accepted: boolean; reason: string } {
    this.usage.steps++;
    const witness = cert.witness as { left: unknown; right: unknown };
    
    if (JSON.stringify(witness.left) === JSON.stringify(witness.right)) {
      return { accepted: true, reason: "Equality verified" };
    }
    return { accepted: false, reason: "Values not equal" };
  }
  
  private verifyMembership(cert: Certificate): { accepted: boolean; reason: string } {
    this.usage.steps++;
    const witness = cert.witness as { element: unknown; set: unknown[] };
    
    const found = witness.set.some(e => JSON.stringify(e) === JSON.stringify(witness.element));
    if (found) {
      return { accepted: true, reason: "Membership verified" };
    }
    return { accepted: false, reason: "Element not in set" };
  }
  
  private verifyBound(cert: Certificate): { accepted: boolean; reason: string } {
    this.usage.steps++;
    const witness = cert.witness as { value: number; lower: number; upper: number };
    
    if (witness.value >= witness.lower && witness.value <= witness.upper) {
      return { accepted: true, reason: "Bound verified" };
    }
    return { accepted: false, reason: "Value out of bounds" };
  }
  
  private verifyReplay(cert: Certificate): { accepted: boolean; reason: string } {
    this.usage.steps++;
    const witness = cert.witness as { originalHash: string; replayHash: string };
    
    if (witness.originalHash === witness.replayHash) {
      return { accepted: true, reason: "Replay verified" };
    }
    return { accepted: false, reason: "Replay hash mismatch" };
  }
  
  private recordStep(operation: string, input: string, output: string): void {
    this.trace.steps.push({
      operation,
      input,
      output,
      cost: this.usage.steps
    });
    this.usage.steps++;
  }
  
  private computeCertHash(cert: Certificate): string {
    const data = JSON.stringify({
      claim: cert.claim,
      assumptions: cert.assumptions,
      dependencies: cert.dependencies
    });
    
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
      hash = ((hash << 5) - hash) + data.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(8, '0');
  }
  
  private hashResult(result: { accepted: boolean; reason: string }): string {
    const data = `${result.accepted}:${result.reason}:${this.usage.time}`;
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
      hash = ((hash << 5) - hash) + data.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(8, '0');
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: DSL COMPILER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * DSL AST node types
 */
export enum ASTNodeType {
  Program = "Program",
  Definition = "Definition",
  Guard = "Guard",
  Route = "Route",
  Detector = "Detector",
  Certificate = "Certificate",
  Expression = "Expression",
  Literal = "Literal",
  Identifier = "Identifier"
}

/**
 * AST node
 */
export interface ASTNode {
  type: ASTNodeType;
  children: ASTNode[];
  value?: unknown;
  location: SourceLocation;
  hash: string;
}

export interface SourceLocation {
  line: number;
  column: number;
  file: string;
}

/**
 * DSL grammar specification
 */
export interface Grammar {
  name: string;
  version: string;
  productions: Production[];
  terminals: string[];
  startSymbol: string;
}

export interface Production {
  name: string;
  pattern: string;
  action: string;
}

/**
 * Compilation result
 */
export interface CompilationResult {
  success: boolean;
  ast?: ASTNode;
  ir?: KernelIR;
  artifact?: KernelArtifact;
  errors: CompilationError[];
  warnings: CompilationWarning[];
  trace: CompilationTrace;
}

export interface CompilationError {
  code: string;
  message: string;
  location: SourceLocation;
}

export interface CompilationWarning {
  code: string;
  message: string;
  location: SourceLocation;
}

export interface CompilationTrace {
  phases: PhaseTrace[];
  duration: number;
  hash: string;
}

export interface PhaseTrace {
  name: string;
  input: string;
  output: string;
  duration: number;
}

/**
 * Kernel IR (Intermediate Representation)
 */
export interface KernelIR {
  nodes: IRNode[];
  edges: IREdge[];
  types: IRType[];
  hash: string;
}

export interface IRNode {
  id: string;
  type: string;
  operation: string;
  inputs: string[];
  outputs: string[];
}

export interface IREdge {
  from: string;
  to: string;
  type: "data" | "control" | "dependency";
}

export interface IRType {
  name: string;
  schemaHash: string;
}

/**
 * DSL Compiler (Construction 17.4)
 */
export class DSLCompiler {
  private grammar: Grammar;
  private typeRules: Map<string, (node: ASTNode) => string> = new Map();
  
  constructor(grammar: Grammar) {
    this.grammar = grammar;
    this.initializeTypeRules();
  }
  
  /**
   * Compile DSL program to kernel artifact
   */
  compile(source: string, filename: string): Out<CompilationResult> {
    const trace: CompilationTrace = { phases: [], duration: 0, hash: "" };
    const startTime = Date.now();
    const errors: CompilationError[] = [];
    const warnings: CompilationWarning[] = [];
    
    // Phase 1: Parse
    const parseStart = Date.now();
    const parseResult = this.parse(source, filename);
    trace.phases.push({
      name: "parse",
      input: `${source.length} chars`,
      output: parseResult.ast ? "AST" : "error",
      duration: Date.now() - parseStart
    });
    
    if (!parseResult.ast) {
      errors.push(...parseResult.errors);
      return bulk({
        success: false,
        errors,
        warnings,
        trace
      });
    }
    
    // Phase 2: Typecheck
    const typecheckStart = Date.now();
    const typecheckResult = this.typecheck(parseResult.ast);
    trace.phases.push({
      name: "typecheck",
      input: "AST",
      output: typecheckResult.valid ? "typed AST" : "error",
      duration: Date.now() - typecheckStart
    });
    
    if (!typecheckResult.valid) {
      errors.push(...typecheckResult.errors);
      return bulk({
        success: false,
        ast: parseResult.ast,
        errors,
        warnings,
        trace
      });
    }
    
    // Phase 3: Normalize (Law 17.6)
    const normalizeStart = Date.now();
    const normalizedAST = this.normalize(parseResult.ast);
    trace.phases.push({
      name: "normalize",
      input: "typed AST",
      output: "normalized AST",
      duration: Date.now() - normalizeStart
    });
    
    // Phase 4: Lower to IR
    const lowerStart = Date.now();
    const ir = this.lowerToIR(normalizedAST);
    trace.phases.push({
      name: "lower",
      input: "normalized AST",
      output: `IR with ${ir.nodes.length} nodes`,
      duration: Date.now() - lowerStart
    });
    
    // Phase 5: Generate artifact
    const genStart = Date.now();
    const artifact = this.generateArtifact(ir);
    trace.phases.push({
      name: "generate",
      input: "IR",
      output: `artifact ${artifact.id}`,
      duration: Date.now() - genStart
    });
    
    trace.duration = Date.now() - startTime;
    trace.hash = this.hashTrace(trace);
    
    return bulk({
      success: true,
      ast: parseResult.ast,
      ir,
      artifact,
      errors,
      warnings,
      trace
    });
  }
  
  private parse(source: string, filename: string): { ast?: ASTNode; errors: CompilationError[] } {
    // Simplified parser - in production would use full grammar
    const lines = source.split('\n');
    const errors: CompilationError[] = [];
    
    const program: ASTNode = {
      type: ASTNodeType.Program,
      children: [],
      location: { line: 1, column: 1, file: filename },
      hash: ""
    };
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (line.length === 0 || line.startsWith('//')) continue;
      
      const node = this.parseLine(line, i + 1, filename);
      if (node) {
        program.children.push(node);
      } else {
        errors.push({
          code: "PARSE_ERROR",
          message: `Unable to parse line: ${line}`,
          location: { line: i + 1, column: 1, file: filename }
        });
      }
    }
    
    program.hash = this.hashAST(program);
    
    return { ast: errors.length === 0 ? program : undefined, errors };
  }
  
  private parseLine(line: string, lineNum: number, file: string): ASTNode | null {
    const location = { line: lineNum, column: 1, file };
    
    // Parse different constructs
    if (line.startsWith("guard ")) {
      return {
        type: ASTNodeType.Guard,
        children: [],
        value: line.slice(6),
        location,
        hash: this.hashString(line)
      };
    }
    
    if (line.startsWith("route ")) {
      return {
        type: ASTNodeType.Route,
        children: [],
        value: line.slice(6),
        location,
        hash: this.hashString(line)
      };
    }
    
    if (line.startsWith("detector ")) {
      return {
        type: ASTNodeType.Detector,
        children: [],
        value: line.slice(9),
        location,
        hash: this.hashString(line)
      };
    }
    
    if (line.startsWith("def ")) {
      return {
        type: ASTNodeType.Definition,
        children: [],
        value: line.slice(4),
        location,
        hash: this.hashString(line)
      };
    }
    
    return null;
  }
  
  private typecheck(ast: ASTNode): { valid: boolean; errors: CompilationError[] } {
    const errors: CompilationError[] = [];
    
    // Check each child node
    for (const child of ast.children) {
      const type = this.inferType(child);
      if (type === "error") {
        errors.push({
          code: "TYPE_ERROR",
          message: `Type error in ${child.type}`,
          location: child.location
        });
      }
    }
    
    return { valid: errors.length === 0, errors };
  }
  
  private inferType(node: ASTNode): string {
    const rule = this.typeRules.get(node.type);
    if (rule) return rule(node);
    return "unknown";
  }
  
  private initializeTypeRules(): void {
    this.typeRules.set(ASTNodeType.Guard, () => "Guard");
    this.typeRules.set(ASTNodeType.Route, () => "Route");
    this.typeRules.set(ASTNodeType.Detector, () => "Detector");
    this.typeRules.set(ASTNodeType.Definition, () => "Definition");
    this.typeRules.set(ASTNodeType.Program, () => "Program");
  }
  
  private normalize(ast: ASTNode): ASTNode {
    // Sort children for canonical ordering
    const normalized: ASTNode = {
      ...ast,
      children: [...ast.children].sort((a, b) => {
        if (a.type !== b.type) return a.type.localeCompare(b.type);
        return JSON.stringify(a.value).localeCompare(JSON.stringify(b.value));
      })
    };
    
    normalized.hash = this.hashAST(normalized);
    return normalized;
  }
  
  private lowerToIR(ast: ASTNode): KernelIR {
    const nodes: IRNode[] = [];
    const edges: IREdge[] = [];
    const types: IRType[] = [];
    
    let nodeId = 0;
    
    for (const child of ast.children) {
      const id = `node_${nodeId++}`;
      nodes.push({
        id,
        type: child.type,
        operation: child.type.toLowerCase(),
        inputs: [],
        outputs: [id + "_out"]
      });
    }
    
    // Connect sequential nodes
    for (let i = 0; i < nodes.length - 1; i++) {
      edges.push({
        from: nodes[i].id,
        to: nodes[i + 1].id,
        type: "control"
      });
    }
    
    return {
      nodes,
      edges,
      types,
      hash: this.hashString(JSON.stringify(nodes))
    };
  }
  
  private generateArtifact(ir: KernelIR): KernelArtifact {
    return {
      id: `artifact_${Date.now()}`,
      type: "compiled_dsl",
      contentHash: ir.hash,
      schemaHash: this.grammar.version,
      buildRecipe: "dsl_compile",
      replayBundle: "",
      dependencies: [],
      certificates: [],
      created: Date.now()
    };
  }
  
  private hashAST(node: ASTNode): string {
    return this.hashString(JSON.stringify({
      type: node.type,
      value: node.value,
      children: node.children.map(c => c.hash)
    }));
  }
  
  private hashTrace(trace: CompilationTrace): string {
    return this.hashString(JSON.stringify(trace.phases));
  }
  
  private hashString(s: string): string {
    let hash = 0;
    for (let i = 0; i < s.length; i++) {
      hash = ((hash << 5) - hash) + s.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(8, '0');
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: BUILD SYSTEM AND ARTIFACTS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Kernel artifact
 */
export interface KernelArtifact {
  id: string;
  type: string;
  contentHash: string;
  schemaHash: string;
  buildRecipe: string;
  replayBundle: string;
  dependencies: string[];  // Merkle refs
  certificates: string[];
  created: number;
}

/**
 * Build graph node
 */
export interface BuildNode {
  id: string;
  artifact: KernelArtifact;
  dependencies: string[];
  dependents: string[];
  built: boolean;
  hash: string;
}

/**
 * Build graph
 */
export interface BuildGraph {
  nodes: Map<string, BuildNode>;
  edges: Map<string, string[]>;
  rootHash: string;
  created: number;
}

/**
 * Merkle DAG node
 */
export interface MerkleNode {
  hash: string;
  content: Uint8Array;
  children: string[];
  type: "leaf" | "internal";
}

/**
 * Artifact publisher (Construction 17.7)
 */
export class ArtifactPublisher {
  private buildGraph: BuildGraph;
  private merkleDAG: Map<string, MerkleNode> = new Map();
  
  constructor() {
    this.buildGraph = {
      nodes: new Map(),
      edges: new Map(),
      rootHash: "",
      created: Date.now()
    };
  }
  
  /**
   * Add artifact to build graph
   */
  addArtifact(artifact: KernelArtifact): string {
    const nodeHash = this.hashArtifact(artifact);
    
    const node: BuildNode = {
      id: artifact.id,
      artifact,
      dependencies: artifact.dependencies,
      dependents: [],
      built: false,
      hash: nodeHash
    };
    
    this.buildGraph.nodes.set(artifact.id, node);
    this.buildGraph.edges.set(artifact.id, artifact.dependencies);
    
    // Update dependents
    for (const dep of artifact.dependencies) {
      const depNode = this.buildGraph.nodes.get(dep);
      if (depNode) {
        depNode.dependents.push(artifact.id);
      }
    }
    
    // Update root hash
    this.updateRootHash();
    
    return nodeHash;
  }
  
  /**
   * Publish artifact with full dependency closure (Law 17.10)
   */
  publish(artifactId: string): Out<PublishRecord> {
    const node = this.buildGraph.nodes.get(artifactId);
    if (!node) {
      return boundary(BoundaryKind.Undefined, ["Artifact not found"]);
    }
    
    // Check dependency closure
    const missingDeps = this.checkDependencyClosure(artifactId);
    if (missingDeps.length > 0) {
      return boundary(BoundaryKind.MissingDependency, missingDeps);
    }
    
    // Build Merkle DAG
    const closureRoot = this.buildMerkleDAG(artifactId);
    
    // Create publish record
    const record: PublishRecord = {
      artifactId,
      rootHash: closureRoot,
      schemaHashes: this.collectSchemaHashes(artifactId),
      requiredScopes: [],
      timestamp: Date.now(),
      hash: ""
    };
    
    record.hash = this.hashPublishRecord(record);
    
    return bulk(record);
  }
  
  /**
   * Get build graph
   */
  getBuildGraph(): BuildGraph {
    return this.buildGraph;
  }
  
  /**
   * Get dependency closure
   */
  getDependencyClosure(artifactId: string): string[] {
    const closure: Set<string> = new Set();
    const queue = [artifactId];
    
    while (queue.length > 0) {
      const current = queue.shift()!;
      if (closure.has(current)) continue;
      closure.add(current);
      
      const deps = this.buildGraph.edges.get(current) ?? [];
      queue.push(...deps);
    }
    
    return Array.from(closure);
  }
  
  private checkDependencyClosure(artifactId: string): string[] {
    const missing: string[] = [];
    const closure = this.getDependencyClosure(artifactId);
    
    for (const dep of closure) {
      if (!this.buildGraph.nodes.has(dep) && dep !== artifactId) {
        missing.push(dep);
      }
    }
    
    return missing;
  }
  
  private buildMerkleDAG(artifactId: string): string {
    const closure = this.getDependencyClosure(artifactId);
    
    // Build leaves
    for (const id of closure) {
      const node = this.buildGraph.nodes.get(id);
      if (node) {
        const merkleNode: MerkleNode = {
          hash: node.hash,
          content: new TextEncoder().encode(JSON.stringify(node.artifact)),
          children: node.dependencies,
          type: node.dependencies.length === 0 ? "leaf" : "internal"
        };
        this.merkleDAG.set(node.hash, merkleNode);
      }
    }
    
    // Compute root
    const rootNode = this.buildGraph.nodes.get(artifactId);
    return rootNode?.hash ?? "";
  }
  
  private collectSchemaHashes(artifactId: string): string[] {
    const hashes: Set<string> = new Set();
    const closure = this.getDependencyClosure(artifactId);
    
    for (const id of closure) {
      const node = this.buildGraph.nodes.get(id);
      if (node) {
        hashes.add(node.artifact.schemaHash);
      }
    }
    
    return Array.from(hashes);
  }
  
  private updateRootHash(): void {
    const nodeHashes = Array.from(this.buildGraph.nodes.values())
      .map(n => n.hash)
      .sort();
    
    this.buildGraph.rootHash = this.hashString(nodeHashes.join(":"));
  }
  
  private hashArtifact(artifact: KernelArtifact): string {
    return this.hashString(JSON.stringify({
      id: artifact.id,
      contentHash: artifact.contentHash,
      dependencies: artifact.dependencies
    }));
  }
  
  private hashPublishRecord(record: PublishRecord): string {
    return this.hashString(JSON.stringify({
      artifactId: record.artifactId,
      rootHash: record.rootHash,
      timestamp: record.timestamp
    }));
  }
  
  private hashString(s: string): string {
    let hash = 0;
    for (let i = 0; i < s.length; i++) {
      hash = ((hash << 5) - hash) + s.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(8, '0');
  }
}

export interface PublishRecord {
  artifactId: string;
  rootHash: string;
  schemaHashes: string[];
  requiredScopes: string[];
  timestamp: number;
  hash: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: REPLAY HARNESS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Replay harness (Construction 17.8)
 */
export class ReplayHarness {
  private merkleStore: Map<string, Uint8Array> = new Map();
  private eventLog: ReplayEvent[] = [];
  
  /**
   * Store content by hash
   */
  store(hash: string, content: Uint8Array): void {
    this.merkleStore.set(hash, content);
  }
  
  /**
   * Replay artifact build
   */
  replay(
    artifactId: string,
    publisher: ArtifactPublisher,
    seed: string
  ): Out<ReplayResult> {
    const startTime = Date.now();
    this.eventLog = [];
    
    // Get dependency closure
    const closure = publisher.getDependencyClosure(artifactId);
    
    // Reconstruct from Merkle closure
    const reconstructed: Map<string, KernelArtifact> = new Map();
    
    for (const id of closure) {
      const node = publisher.getBuildGraph().nodes.get(id);
      if (!node) {
        return boundary(BoundaryKind.MissingDependency, [`Missing: ${id}`]);
      }
      
      reconstructed.set(id, node.artifact);
      this.logEvent("reconstruct", id, node.hash);
    }
    
    // Re-execute deterministic steps
    const outputs: Map<string, string> = new Map();
    
    for (const id of closure) {
      const artifact = reconstructed.get(id)!;
      const outputHash = this.executeStep(artifact, seed);
      outputs.set(id, outputHash);
      this.logEvent("execute", id, outputHash);
    }
    
    // Compare hashes
    const mismatches: string[] = [];
    
    for (const [id, outputHash] of outputs) {
      const node = publisher.getBuildGraph().nodes.get(id);
      if (node && node.hash !== outputHash) {
        mismatches.push(`${id}: expected ${node.hash}, got ${outputHash}`);
      }
    }
    
    const result: ReplayResult = {
      success: mismatches.length === 0,
      artifactId,
      originalHash: publisher.getBuildGraph().nodes.get(artifactId)?.hash ?? "",
      replayHash: outputs.get(artifactId) ?? "",
      divergences: mismatches,
      eventLog: [...this.eventLog],
      duration: Date.now() - startTime,
      certificate: undefined
    };
    
    if (result.success) {
      result.certificate = this.generateReplayCertificate(result);
    }
    
    return bulk(result);
  }
  
  private executeStep(artifact: KernelArtifact, seed: string): string {
    // Deterministic execution based on seed
    const input = JSON.stringify({
      artifact: artifact.contentHash,
      deps: artifact.dependencies,
      seed
    });
    
    return this.hashString(input);
  }
  
  private logEvent(type: string, target: string, result: string): void {
    this.eventLog.push({
      type,
      target,
      result,
      timestamp: Date.now()
    });
  }
  
  private generateReplayCertificate(result: ReplayResult): Certificate {
    return {
      id: `replay_cert_${Date.now()}`,
      claim: {
        type: "replay",
        proposition: `Replay of ${result.artifactId} succeeded`,
        context: { originalHash: result.originalHash, replayHash: result.replayHash }
      },
      assumptions: [],
      witness: { originalHash: result.originalHash, replayHash: result.replayHash },
      dependencies: [],
      complexity: result.eventLog.length,
      encoding: new Uint8Array(),
      hash: this.hashString(JSON.stringify(result))
    };
  }
  
  private hashString(s: string): string {
    let hash = 0;
    for (let i = 0; i < s.length; i++) {
      hash = ((hash << 5) - hash) + s.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(8, '0');
  }
}

export interface ReplayEvent {
  type: string;
  target: string;
  result: string;
  timestamp: number;
}

export interface ReplayResult {
  success: boolean;
  artifactId: string;
  originalHash: string;
  replayHash: string;
  divergences: string[];
  eventLog: ReplayEvent[];
  duration: number;
  certificate?: Certificate;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 8: KERNEL MECHANIZATION ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete Kernel Mechanization Engine
 */
export class KernelMechanizationEngine {
  private codecRegistry: CodecRegistry;
  private router: RouterModule;
  private verifier: VerifierKernel;
  private compiler: DSLCompiler;
  private publisher: ArtifactPublisher;
  private replayHarness: ReplayHarness;
  
  private abi: KernelABI;
  private eventLog: KernelEvent[] = [];
  
  constructor(options?: { budget?: ComplexityBudget }) {
    this.codecRegistry = new CodecRegistry();
    this.router = new RouterModule();
    this.verifier = new VerifierKernel(options?.budget ?? {
      maxTime: 10000,
      maxMemory: 100 * 1024 * 1024,
      maxStack: 1000,
      maxSteps: 100000,
      maxIO: 1000
    });
    
    const grammar: Grammar = {
      name: "KernelDSL",
      version: "1.0.0",
      productions: [],
      terminals: [],
      startSymbol: "Program"
    };
    
    this.compiler = new DSLCompiler(grammar);
    this.publisher = new ArtifactPublisher();
    this.replayHarness = new ReplayHarness();
    
    this.abi = this.initializeABI();
    this.initializeCodecs();
  }
  
  /**
   * Initialize ABI
   */
  private initializeABI(): KernelABI {
    return {
      version: "1.0.0",
      schemas: new Map(),
      functionSignatures: new Map(),
      versionNegotiation: {
        minVersion: "1.0.0",
        maxVersion: "1.0.0",
        adaptableVersions: []
      },
      hash: ""
    };
  }
  
  /**
   * Initialize codecs for core types
   */
  private initializeCodecs(): void {
    for (const type of Object.values(KernelType)) {
      const schema: TypeSchema = {
        type: type as KernelType,
        version: "1.0.0",
        fields: [],
        hash: this.hashString(`schema:${type}:1.0.0`)
      };
      
      this.codecRegistry.register(schema);
    }
  }
  
  /**
   * Compile DSL source
   */
  compileDSL(source: string, filename: string): Out<CompilationResult> {
    this.logEvent("compile", { source: filename });
    return this.compiler.compile(source, filename);
  }
  
  /**
   * Verify certificate
   */
  verifyCertificate(cert: Certificate): Out<VerificationResult> {
    this.logEvent("verify", { certId: cert.id });
    return this.verifier.verify(cert);
  }
  
  /**
   * Publish artifact
   */
  publishArtifact(artifact: KernelArtifact): Out<PublishRecord> {
    this.logEvent("publish", { artifactId: artifact.id });
    this.publisher.addArtifact(artifact);
    return this.publisher.publish(artifact.id);
  }
  
  /**
   * Replay artifact build
   */
  replayBuild(artifactId: string, seed: string): Out<ReplayResult> {
    this.logEvent("replay", { artifactId, seed });
    return this.replayHarness.replay(artifactId, this.publisher, seed);
  }
  
  /**
   * Route result
   */
  route<T>(
    result: T | null | undefined,
    errorCondition: () => BoundaryKind | null,
    obligations: () => string[]
  ): Out<T> {
    return this.router.route(result, errorCondition, obligations);
  }
  
  /**
   * Get codec
   */
  getCodec<T>(type: KernelType): Codec<T> | undefined {
    return this.codecRegistry.get(type);
  }
  
  /**
   * Get ABI
   */
  getABI(): KernelABI {
    return this.abi;
  }
  
  /**
   * Get event log
   */
  getEventLog(): KernelEvent[] {
    return [...this.eventLog];
  }
  
  /**
   * Get statistics
   */
  getStats(): KernelStats {
    return {
      codecCount: Object.keys(KernelType).length,
      artifactCount: this.publisher.getBuildGraph().nodes.size,
      eventCount: this.eventLog.length,
      abiVersion: this.abi.version
    };
  }
  
  private logEvent(type: string, data: Record<string, unknown>): void {
    this.eventLog.push({
      type,
      data,
      timestamp: Date.now(),
      hash: this.hashString(JSON.stringify({ type, data, time: Date.now() }))
    });
  }
  
  private hashString(s: string): string {
    let hash = 0;
    for (let i = 0; i < s.length; i++) {
      hash = ((hash << 5) - hash) + s.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(8, '0');
  }
}

export interface KernelEvent {
  type: string;
  data: Record<string, unknown>;
  timestamp: number;
  hash: string;
}

export interface KernelStats {
  codecCount: number;
  artifactCount: number;
  eventCount: number;
  abiVersion: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Enums
  EffectType,
  KernelType,
  BoundaryKind,
  ASTNodeType,
  
  // Functions
  bulk,
  boundary,
  
  // Classes
  GenericCodec,
  CodecRegistry,
  RouterModule,
  VerifierKernel,
  DSLCompiler,
  ArtifactPublisher,
  ReplayHarness,
  KernelMechanizationEngine
};
