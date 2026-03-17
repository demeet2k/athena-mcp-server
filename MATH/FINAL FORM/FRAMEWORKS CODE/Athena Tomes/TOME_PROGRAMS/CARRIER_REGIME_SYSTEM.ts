/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * CARRIER REGIME SYSTEM - Complete Semantic Foundation
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Core Semantic Objects (from SELF_SUFFICIENCY_TOME Ch01):
 * 
 * CARRIER K = (|K|, Ty_K, Val_K, Eq_K, Enc_K)
 *   - |K| = underlying representation set
 *   - Ty_K = type universe
 *   - Val_K(τ) = well-formed values of type τ
 *   - Eq_K(τ) = equivalence relation (semantic equality)
 *   - Enc_K = canonical prefix-free encoding
 * 
 * REGIME R = (K, C, B, Ω)
 *   - K = carrier
 *   - C = corridor predicates (guards)
 *   - B = typed boundary space
 *   - Ω = verifier contract
 * 
 * BOUNDARY β = ⟨kind, code, where, witness, requirements⟩
 *   - kind ∈ {Undefined, Singular, Ambiguous, OutOfCorridor, UnderResolved, NonTerminating}
 *   - code = stable identifier
 *   - where = source span/address
 *   - witness = minimal supporting data
 *   - requirements = obligations for refinement
 * 
 * Out(τ) = Bulk(τ) ⊕ Bdry(τ)
 * 
 * @module CARRIER_REGIME_SYSTEM
 * @version 2.0.0
 */

import { TruthValue, WitnessPtr } from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: PRIMITIVE SORTS AND ALPHABET
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Primitive sorts in the system
 */
export enum PrimitiveSort {
  Regime = "Regime",
  Carrier = "Carrier",
  Term = "Term",
  Type = "Type",
  Value = "Value",
  Boundary = "Boundary",
  Cert = "Cert",
  Seed = "Seed",
  Context = "Context",
  Judgment = "Judgment"
}

/**
 * Base alphabet symbol
 */
export interface Symbol {
  name: string;
  sort: PrimitiveSort;
  arity: number;
  encoding: number[];  // Prefix-free tag
}

/**
 * Type universe entry
 */
export interface TypeEntry {
  id: string;
  name: string;
  kind: "base" | "function" | "product" | "sum" | "out" | "cert";
  parameters: string[];  // Type parameters
  constructors: ConstructorEntry[];
}

export interface ConstructorEntry {
  name: string;
  argTypes: string[];
  returnType: string;
  tag: number;  // For encoding
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: CARRIER DEFINITION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Carrier: The semantic foundation
 * K = (|K|, Ty_K, Val_K, Eq_K, Enc_K)
 */
export interface Carrier<T = unknown> {
  id: string;
  name: string;
  
  /** |K| - underlying representation */
  representations: Set<string>;
  
  /** Ty_K - type universe */
  typeUniverse: TypeUniverse;
  
  /** Val_K(τ) - value space per type */
  valueSpace: ValueSpace<T>;
  
  /** Eq_K(τ) - semantic equality */
  equality: EqualityRelation<T>;
  
  /** Enc_K - canonical encoding */
  encoding: EncodingFunction<T>;
}

/**
 * Type universe for a carrier
 */
export interface TypeUniverse {
  types: Map<string, TypeEntry>;
  
  /** Check if type is well-formed */
  isWellFormed(typeId: string): boolean;
  
  /** Get all subtypes */
  getSubtypes(typeId: string): string[];
  
  /** Check subtype relation */
  isSubtype(sub: string, sup: string): boolean;
  
  /** Compute least upper bound */
  lub(t1: string, t2: string): string | null;
}

/**
 * Value space implementation
 */
export interface ValueSpace<T> {
  /** Get values of a type */
  getValues(typeId: string): Set<T>;
  
  /** Check if value is well-formed for type */
  isWellFormed(value: T, typeId: string): boolean;
  
  /** Validate value against type */
  validate(value: T, typeId: string): ValidationResult;
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
  witnesses: WitnessPtr[];
}

/**
 * Semantic equality relation
 */
export interface EqualityRelation<T> {
  /** Check equality of two values */
  equals(a: T, b: T, typeId: string): boolean;
  
  /** Get equivalence class representative */
  representative(value: T, typeId: string): T;
  
  /** Check if equality is decidable for type */
  isDecidable(typeId: string): boolean;
}

/**
 * Canonical encoding function
 */
export interface EncodingFunction<T> {
  /** Encode value to bytes */
  encode(value: T): Uint8Array;
  
  /** Decode bytes to value */
  decode(bytes: Uint8Array): T;
  
  /** Check prefix-free property */
  isPrefixFree(): boolean;
  
  /** Get encoding size */
  size(value: T): number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: BOUNDARY TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Boundary kind enumeration
 */
export enum BoundaryKind {
  Undefined = "Undefined",
  Singular = "Singular",
  Ambiguous = "Ambiguous",
  OutOfCorridor = "OutOfCorridor",
  UnderResolved = "UnderResolved",
  NonTerminating = "NonTerminating"
}

/**
 * Boundary object: β = ⟨kind, code, where, witness, requirements⟩
 */
export interface Boundary {
  /** Classification of failure */
  kind: BoundaryKind;
  
  /** Stable identifier code */
  code: string;
  
  /** Source location/address */
  where: SourceSpan;
  
  /** Minimal witness supporting classification */
  witness: BoundaryWitness;
  
  /** Obligations for refinement/discharge */
  requirements: Obligation[];
  
  /** Expected type tag */
  expectedType: string;
  
  /** Timestamp */
  timestamp: number;
}

export interface SourceSpan {
  file: string;
  startLine: number;
  startCol: number;
  endLine: number;
  endCol: number;
  context?: string;
}

export interface BoundaryWitness {
  data: unknown;
  description: string;
  provenance: string[];
}

export interface Obligation {
  id: string;
  description: string;
  kind: "proof" | "computation" | "input" | "resource";
  priority: number;
  deadline?: number;
  dependencies: string[];
}

/**
 * Bulk⊕Boundary output type
 * Out(τ) = Bulk(τ) ⊕ Bdry(τ)
 */
export type Out<T> = Bulk<T> | Bdry<T>;

export interface Bulk<T> {
  tag: "bulk";
  value: T;
  type: string;
  certificate?: string;
}

export interface Bdry<T> {
  tag: "bdry";
  boundary: Boundary;
  type: string;
  partialValue?: T;
}

/**
 * Type guards
 */
export function isBulk<T>(out: Out<T>): out is Bulk<T> {
  return out.tag === "bulk";
}

export function isBdry<T>(out: Out<T>): out is Bdry<T> {
  return out.tag === "bdry";
}

/**
 * Create Bulk value
 */
export function bulk<T>(value: T, type: string, certificate?: string): Bulk<T> {
  return { tag: "bulk", value, type, certificate };
}

/**
 * Create Boundary value
 */
export function bdry<T>(boundary: Boundary, type: string, partialValue?: T): Bdry<T> {
  return { tag: "bdry", boundary, type, partialValue };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: CORRIDOR PREDICATES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Corridor predicate (guard)
 */
export interface CorridorPredicate {
  id: string;
  name: string;
  
  /** The predicate function */
  evaluate: (state: CorridorState) => boolean;
  
  /** Human-readable description */
  description: string;
  
  /** Counter-witness generator when predicate fails */
  counterWitness: (state: CorridorState) => BoundaryWitness;
  
  /** Priority for evaluation order */
  priority: number;
}

export interface CorridorState {
  context: Context;
  inputs: unknown[];
  resources: ResourceBudget;
  environment: Map<string, unknown>;
  trace: string[];
}

export interface Context {
  bindings: Map<string, TypedBinding>;
  assumptions: Set<string>;
  goals: string[];
}

export interface TypedBinding {
  name: string;
  type: string;
  value?: unknown;
  mutable: boolean;
}

export interface ResourceBudget {
  computation: number;
  memory: number;
  time: number;
  depth: number;
}

/**
 * Corridor: Collection of predicates
 */
export interface Corridor {
  id: string;
  predicates: CorridorPredicate[];
  
  /** Check all predicates */
  check(state: CorridorState): CorridorCheckResult;
  
  /** Get active guards */
  activeGuards(): CorridorPredicate[];
}

export interface CorridorCheckResult {
  passed: boolean;
  failedPredicates: CorridorPredicate[];
  witnesses: BoundaryWitness[];
  resourceUsage: ResourceBudget;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: VERIFIER CONTRACT
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Verifier contract Ω
 */
export interface VerifierContract {
  id: string;
  
  /** Accepted certificate schemas */
  schemas: CertificateSchema[];
  
  /** Complexity budgets */
  budgets: ComplexityBudget;
  
  /** Verification function */
  verify: (cert: Certificate) => VerificationResult;
  
  /** Determinism guarantee */
  deterministic: boolean;
}

export interface CertificateSchema {
  name: string;
  fields: SchemaField[];
  validators: string[];
}

export interface SchemaField {
  name: string;
  type: string;
  required: boolean;
  validator?: (value: unknown) => boolean;
}

export interface ComplexityBudget {
  /** Maximum time in milliseconds */
  maxTimeMs: number;
  
  /** Maximum memory in bytes */
  maxMemoryBytes: number;
  
  /** Maximum proof depth */
  maxDepth: number;
  
  /** PTIME restriction (polynomial time) */
  ptimeRestricted: boolean;
}

export interface Certificate {
  id: string;
  claim: string;
  context: string[];
  assumptions: string[];
  witness: unknown;
  trace: string[];
  dependencies: string[];
  hash: string;
  timestamp: number;
}

export interface VerificationResult {
  accepted: boolean;
  reason?: string;
  failingComponent?: string;
  resourceUsage: {
    timeMs: number;
    memoryBytes: number;
    depth: number;
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: REGIME DEFINITION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Regime: R = (K, C, B, Ω)
 */
export interface Regime<T = unknown> {
  id: string;
  name: string;
  
  /** K - Carrier */
  carrier: Carrier<T>;
  
  /** C - Corridor predicates */
  corridor: Corridor;
  
  /** B - Boundary space */
  boundarySpace: BoundarySpace;
  
  /** Ω - Verifier contract */
  verifier: VerifierContract;
}

/**
 * Boundary space: typed classification
 */
export interface BoundarySpace {
  /** All boundary kinds */
  kinds: Set<BoundaryKind>;
  
  /** Stable code registry */
  codeRegistry: Map<string, BoundaryCodeEntry>;
  
  /** Classifier function */
  classify: (diagnostic: Diagnostic) => Boundary;
  
  /** Obligation generator */
  generateObligations: (boundary: Boundary) => Obligation[];
}

export interface BoundaryCodeEntry {
  code: string;
  kind: BoundaryKind;
  description: string;
  remediation: string[];
}

export interface Diagnostic {
  source: string;
  message: string;
  data: unknown;
  stackTrace: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: OPERATOR INTERFACE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Operator declaration
 */
export interface Operator<I extends unknown[], O> {
  name: string;
  signature: OperatorSignature;
  
  /** Total evaluator producing Out(τ) */
  eval: (...args: I) => Out<O>;
  
  /** Corridor guards */
  guards: CorridorPredicate[];
  
  /** Certificate emitter */
  emitCert: (inputs: I, output: Out<O>) => Certificate;
  
  /** Verifier hook */
  verify: (cert: Certificate) => boolean;
}

export interface OperatorSignature {
  inputTypes: string[];
  outputType: string;
  typeParameters?: string[];
  constraints?: string[];
}

/**
 * Operator registry
 */
export class OperatorRegistry {
  private operators: Map<string, Operator<unknown[], unknown>> = new Map();
  
  register<I extends unknown[], O>(op: Operator<I, O>): void {
    this.operators.set(op.name, op as Operator<unknown[], unknown>);
  }
  
  get<I extends unknown[], O>(name: string): Operator<I, O> | undefined {
    return this.operators.get(name) as Operator<I, O> | undefined;
  }
  
  has(name: string): boolean {
    return this.operators.has(name);
  }
  
  all(): Operator<unknown[], unknown>[] {
    return Array.from(this.operators.values());
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 8: BIND AND COMPOSITION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Monadic bind for Out type
 * bind: Out(τ) × (τ → Out(σ)) → Out(σ)
 */
export function bind<T, U>(
  out: Out<T>,
  k: (value: T) => Out<U>,
  callPath?: string
): Out<U> {
  if (isBulk(out)) {
    return k(out.value);
  } else {
    // Boundary propagation: preserve metadata, adjust type
    const extendedBoundary: Boundary = {
      ...out.boundary,
      where: callPath ? {
        ...out.boundary.where,
        context: `${out.boundary.where.context || ''} -> ${callPath}`
      } : out.boundary.where
    };
    
    return {
      tag: "bdry",
      boundary: extendedBoundary,
      type: "unknown", // Will be refined by caller
      partialValue: undefined
    };
  }
}

/**
 * Lift value to Bulk
 */
export function lift<T>(value: T, type: string): Out<T> {
  return bulk(value, type);
}

/**
 * Map function over Out
 */
export function mapOut<T, U>(out: Out<T>, f: (v: T) => U): Out<U> {
  return bind(out, v => lift(f(v), "mapped"));
}

/**
 * Sequence multiple Out values
 */
export function sequence<T>(outs: Out<T>[]): Out<T[]> {
  const results: T[] = [];
  
  for (const out of outs) {
    if (isBdry(out)) {
      return bdry(out.boundary, "array");
    }
    results.push(out.value);
  }
  
  return bulk(results, "array");
}

/**
 * Laws verification
 */
export const OutLaws = {
  /** bind(Bulk(w), k) = k(w) */
  leftIdentity: <T, U>(w: T, k: (v: T) => Out<U>, type: string): boolean => {
    const left = bind(bulk(w, type), k);
    const right = k(w);
    return JSON.stringify(left) === JSON.stringify(right);
  },
  
  /** bind(x, lift) = x */
  rightIdentity: <T>(x: Out<T>, type: string): boolean => {
    const left = bind(x, v => lift(v, type));
    return JSON.stringify(left) === JSON.stringify(x);
  },
  
  /** bind(bind(x, f), g) = bind(x, λu. bind(f(u), g)) */
  associativity: <T, U, V>(
    x: Out<T>,
    f: (v: T) => Out<U>,
    g: (v: U) => Out<V>
  ): boolean => {
    const left = bind(bind(x, f), g);
    const right = bind(x, u => bind(f(u), g));
    return JSON.stringify(left) === JSON.stringify(right);
  }
};

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 9: ROUTER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Router: Total dispatcher
 * route: EvalResult → Out(τ)
 */
export interface Router<T> {
  /** Route evaluation result to Out */
  route(result: EvalResult<T>, type: string): Out<T>;
  
  /** Boundary classifier */
  classifier: BoundaryClassifier;
}

export type EvalResult<T> = 
  | { success: true; value: T }
  | { success: false; diagnostic: Diagnostic };

export interface BoundaryClassifier {
  classify(diagnostic: Diagnostic): Boundary;
  isStable(diagnostic: Diagnostic): boolean;
}

/**
 * Create default router
 */
export function createRouter<T>(classifier: BoundaryClassifier): Router<T> {
  return {
    route(result: EvalResult<T>, type: string): Out<T> {
      if (result.success) {
        return bulk(result.value, type);
      } else {
        const boundary = classifier.classify(result.diagnostic);
        return bdry(boundary, type);
      }
    },
    classifier
  };
}

/**
 * Default boundary classifier
 */
export function createDefaultClassifier(): BoundaryClassifier {
  const kindPatterns: [RegExp, BoundaryKind][] = [
    [/undefined|not defined/i, BoundaryKind.Undefined],
    [/singular|divide by zero|infinity/i, BoundaryKind.Singular],
    [/ambiguous|multiple|conflict/i, BoundaryKind.Ambiguous],
    [/corridor|guard|permission/i, BoundaryKind.OutOfCorridor],
    [/unresolved|incomplete|partial/i, BoundaryKind.UnderResolved],
    [/timeout|non-terminating|infinite/i, BoundaryKind.NonTerminating]
  ];
  
  let codeCounter = 0;
  
  return {
    classify(diagnostic: Diagnostic): Boundary {
      let kind = BoundaryKind.Undefined;
      
      for (const [pattern, k] of kindPatterns) {
        if (pattern.test(diagnostic.message)) {
          kind = k;
          break;
        }
      }
      
      return {
        kind,
        code: `BDRY_${++codeCounter}_${kind}`,
        where: {
          file: diagnostic.source,
          startLine: 0,
          startCol: 0,
          endLine: 0,
          endCol: 0,
          context: diagnostic.stackTrace[0]
        },
        witness: {
          data: diagnostic.data,
          description: diagnostic.message,
          provenance: diagnostic.stackTrace
        },
        requirements: [],
        expectedType: "unknown",
        timestamp: Date.now()
      };
    },
    
    isStable(diagnostic: Diagnostic): boolean {
      return diagnostic.source !== "" && diagnostic.message !== "";
    }
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 10: CARRIER BUILDER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Build a carrier from components
 */
export class CarrierBuilder<T> {
  private id: string;
  private name: string;
  private representations: Set<string> = new Set();
  private types: Map<string, TypeEntry> = new Map();
  private values: Map<string, Set<T>> = new Map();
  private equalityFn: (a: T, b: T, type: string) => boolean = (a, b) => a === b;
  private encodeFn: (v: T) => Uint8Array = v => new TextEncoder().encode(JSON.stringify(v));
  private decodeFn: (b: Uint8Array) => T = b => JSON.parse(new TextDecoder().decode(b));
  
  constructor(id: string, name: string) {
    this.id = id;
    this.name = name;
  }
  
  addRepresentation(rep: string): this {
    this.representations.add(rep);
    return this;
  }
  
  addType(entry: TypeEntry): this {
    this.types.set(entry.id, entry);
    return this;
  }
  
  addValues(typeId: string, vals: T[]): this {
    if (!this.values.has(typeId)) {
      this.values.set(typeId, new Set());
    }
    for (const v of vals) {
      this.values.get(typeId)!.add(v);
    }
    return this;
  }
  
  setEquality(fn: (a: T, b: T, type: string) => boolean): this {
    this.equalityFn = fn;
    return this;
  }
  
  setEncoding(encode: (v: T) => Uint8Array, decode: (b: Uint8Array) => T): this {
    this.encodeFn = encode;
    this.decodeFn = decode;
    return this;
  }
  
  build(): Carrier<T> {
    const types = this.types;
    const values = this.values;
    const equalityFn = this.equalityFn;
    const encodeFn = this.encodeFn;
    const decodeFn = this.decodeFn;
    
    return {
      id: this.id,
      name: this.name,
      representations: this.representations,
      
      typeUniverse: {
        types,
        isWellFormed(typeId: string): boolean {
          return types.has(typeId);
        },
        getSubtypes(typeId: string): string[] {
          return Array.from(types.keys()).filter(t => {
            const entry = types.get(t);
            return entry?.parameters.includes(typeId);
          });
        },
        isSubtype(sub: string, sup: string): boolean {
          return sub === sup || this.getSubtypes(sup).includes(sub);
        },
        lub(t1: string, t2: string): string | null {
          if (t1 === t2) return t1;
          if (this.isSubtype(t1, t2)) return t2;
          if (this.isSubtype(t2, t1)) return t1;
          return null;
        }
      },
      
      valueSpace: {
        getValues(typeId: string): Set<T> {
          return values.get(typeId) ?? new Set();
        },
        isWellFormed(value: T, typeId: string): boolean {
          const vals = values.get(typeId);
          return vals?.has(value) ?? false;
        },
        validate(value: T, typeId: string): ValidationResult {
          const valid = this.isWellFormed(value, typeId);
          return {
            valid,
            errors: valid ? [] : [`Value not in type ${typeId}`],
            warnings: [],
            witnesses: []
          };
        }
      },
      
      equality: {
        equals(a: T, b: T, typeId: string): boolean {
          return equalityFn(a, b, typeId);
        },
        representative(value: T, typeId: string): T {
          return value;  // Default: identity
        },
        isDecidable(typeId: string): boolean {
          return true;
        }
      },
      
      encoding: {
        encode: encodeFn,
        decode: decodeFn,
        isPrefixFree(): boolean {
          return true;  // JSON encoding is prefix-free
        },
        size(value: T): number {
          return encodeFn(value).length;
        }
      }
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 11: REGIME BUILDER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Build a regime from components
 */
export class RegimeBuilder<T> {
  private id: string;
  private name: string;
  private carrier?: Carrier<T>;
  private predicates: CorridorPredicate[] = [];
  private boundaryKinds: Set<BoundaryKind> = new Set(Object.values(BoundaryKind));
  private boundaryCodes: Map<string, BoundaryCodeEntry> = new Map();
  private verifierSchemas: CertificateSchema[] = [];
  private complexityBudget: ComplexityBudget = {
    maxTimeMs: 10000,
    maxMemoryBytes: 100 * 1024 * 1024,
    maxDepth: 100,
    ptimeRestricted: false
  };
  
  constructor(id: string, name: string) {
    this.id = id;
    this.name = name;
  }
  
  setCarrier(carrier: Carrier<T>): this {
    this.carrier = carrier;
    return this;
  }
  
  addCorridorPredicate(pred: CorridorPredicate): this {
    this.predicates.push(pred);
    return this;
  }
  
  addBoundaryCode(entry: BoundaryCodeEntry): this {
    this.boundaryCodes.set(entry.code, entry);
    return this;
  }
  
  addVerifierSchema(schema: CertificateSchema): this {
    this.verifierSchemas.push(schema);
    return this;
  }
  
  setComplexityBudget(budget: Partial<ComplexityBudget>): this {
    this.complexityBudget = { ...this.complexityBudget, ...budget };
    return this;
  }
  
  build(): Regime<T> {
    if (!this.carrier) {
      throw new Error("Carrier must be set");
    }
    
    const predicates = this.predicates;
    const boundaryCodes = this.boundaryCodes;
    const verifierSchemas = this.verifierSchemas;
    const complexityBudget = this.complexityBudget;
    const classifier = createDefaultClassifier();
    
    return {
      id: this.id,
      name: this.name,
      carrier: this.carrier,
      
      corridor: {
        id: `corridor_${this.id}`,
        predicates,
        check(state: CorridorState): CorridorCheckResult {
          const failed: CorridorPredicate[] = [];
          const witnesses: BoundaryWitness[] = [];
          
          for (const pred of predicates) {
            if (!pred.evaluate(state)) {
              failed.push(pred);
              witnesses.push(pred.counterWitness(state));
            }
          }
          
          return {
            passed: failed.length === 0,
            failedPredicates: failed,
            witnesses,
            resourceUsage: state.resources
          };
        },
        activeGuards(): CorridorPredicate[] {
          return predicates.filter(p => p.priority > 0);
        }
      },
      
      boundarySpace: {
        kinds: this.boundaryKinds,
        codeRegistry: boundaryCodes,
        classify: classifier.classify,
        generateObligations(boundary: Boundary): Obligation[] {
          const entry = boundaryCodes.get(boundary.code);
          if (!entry) return [];
          
          return entry.remediation.map((rem, i) => ({
            id: `obl_${boundary.code}_${i}`,
            description: rem,
            kind: "proof" as const,
            priority: i,
            dependencies: []
          }));
        }
      },
      
      verifier: {
        id: `verifier_${this.id}`,
        schemas: verifierSchemas,
        budgets: complexityBudget,
        verify(cert: Certificate): VerificationResult {
          const startTime = Date.now();
          
          // Check schema compliance
          const schema = verifierSchemas.find(s => s.name === cert.claim);
          if (!schema) {
            return {
              accepted: false,
              reason: `No schema for claim: ${cert.claim}`,
              resourceUsage: { timeMs: Date.now() - startTime, memoryBytes: 0, depth: 0 }
            };
          }
          
          // Check budgets
          const elapsed = Date.now() - startTime;
          if (elapsed > complexityBudget.maxTimeMs) {
            return {
              accepted: false,
              reason: "Verification timeout",
              resourceUsage: { timeMs: elapsed, memoryBytes: 0, depth: 0 }
            };
          }
          
          return {
            accepted: true,
            resourceUsage: { timeMs: elapsed, memoryBytes: 0, depth: 0 }
          };
        },
        deterministic: true
      }
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 12: CARRIER REGIME ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete Carrier-Regime Engine
 */
export class CarrierRegimeEngine {
  private carriers: Map<string, Carrier<unknown>> = new Map();
  private regimes: Map<string, Regime<unknown>> = new Map();
  private operators: OperatorRegistry = new OperatorRegistry();
  private activeRegime?: string;
  
  /**
   * Register carrier
   */
  registerCarrier<T>(carrier: Carrier<T>): void {
    this.carriers.set(carrier.id, carrier as Carrier<unknown>);
  }
  
  /**
   * Register regime
   */
  registerRegime<T>(regime: Regime<T>): void {
    this.regimes.set(regime.id, regime as Regime<unknown>);
  }
  
  /**
   * Set active regime
   */
  setActiveRegime(id: string): boolean {
    if (this.regimes.has(id)) {
      this.activeRegime = id;
      return true;
    }
    return false;
  }
  
  /**
   * Get active regime
   */
  getActiveRegime(): Regime<unknown> | undefined {
    return this.activeRegime ? this.regimes.get(this.activeRegime) : undefined;
  }
  
  /**
   * Execute operation in current regime
   */
  execute<I extends unknown[], O>(
    operatorName: string,
    ...args: I
  ): Out<O> {
    const regime = this.getActiveRegime();
    if (!regime) {
      return bdry({
        kind: BoundaryKind.OutOfCorridor,
        code: "NO_REGIME",
        where: { file: "engine", startLine: 0, startCol: 0, endLine: 0, endCol: 0 },
        witness: { data: null, description: "No active regime", provenance: [] },
        requirements: [],
        expectedType: "unknown",
        timestamp: Date.now()
      }, "unknown");
    }
    
    const op = this.operators.get<I, O>(operatorName);
    if (!op) {
      return bdry({
        kind: BoundaryKind.Undefined,
        code: "NO_OPERATOR",
        where: { file: "engine", startLine: 0, startCol: 0, endLine: 0, endCol: 0 },
        witness: { data: operatorName, description: `Operator not found: ${operatorName}`, provenance: [] },
        requirements: [],
        expectedType: "unknown",
        timestamp: Date.now()
      }, "unknown");
    }
    
    // Check corridor
    const state: CorridorState = {
      context: {
        bindings: new Map(),
        assumptions: new Set(),
        goals: []
      },
      inputs: args,
      resources: { computation: 1000, memory: 1024 * 1024, time: 1000, depth: 10 },
      environment: new Map(),
      trace: []
    };
    
    const corridorCheck = regime.corridor.check(state);
    if (!corridorCheck.passed) {
      return bdry({
        kind: BoundaryKind.OutOfCorridor,
        code: "CORRIDOR_FAIL",
        where: { file: "engine", startLine: 0, startCol: 0, endLine: 0, endCol: 0 },
        witness: corridorCheck.witnesses[0],
        requirements: [],
        expectedType: op.signature.outputType,
        timestamp: Date.now()
      }, op.signature.outputType);
    }
    
    // Execute
    return op.eval(...args);
  }
  
  /**
   * Register operator
   */
  registerOperator<I extends unknown[], O>(op: Operator<I, O>): void {
    this.operators.register(op);
  }
  
  /**
   * Verify certificate
   */
  verifyCertificate(cert: Certificate): VerificationResult {
    const regime = this.getActiveRegime();
    if (!regime) {
      return {
        accepted: false,
        reason: "No active regime",
        resourceUsage: { timeMs: 0, memoryBytes: 0, depth: 0 }
      };
    }
    
    return regime.verifier.verify(cert);
  }
  
  /**
   * Get all carriers
   */
  getCarriers(): Carrier<unknown>[] {
    return Array.from(this.carriers.values());
  }
  
  /**
   * Get all regimes
   */
  getRegimes(): Regime<unknown>[] {
    return Array.from(this.regimes.values());
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Sorts
  PrimitiveSort,
  BoundaryKind,
  
  // Out type
  bulk,
  bdry,
  isBulk,
  isBdry,
  bind,
  lift,
  mapOut,
  sequence,
  OutLaws,
  
  // Builders
  CarrierBuilder,
  RegimeBuilder,
  
  // Registry
  OperatorRegistry,
  
  // Router
  createRouter,
  createDefaultClassifier,
  
  // Engine
  CarrierRegimeEngine
};
