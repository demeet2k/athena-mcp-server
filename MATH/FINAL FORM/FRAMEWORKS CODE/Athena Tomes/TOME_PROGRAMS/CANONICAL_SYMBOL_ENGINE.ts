/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * CANONICAL SYMBOL ENGINE - Symbol Table & Type Dictionary
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * From SELF_SUFFICIENCY_TOME Appendix A:
 * 
 * Core Laws:
 *   - Law A.1 (Canonicalization): Symbol names must be canonicalized
 *   - Law A.2 (Namespace isolation): Different namespaces may share names
 *     but never FQName
 *   - Law A.3 (No collisions): Within namespace-version, name→symbol is injective
 *   - Law A.5 (Reference resolution): Every reference must resolve with matching hash
 * 
 * Four alphabet layers: Lexical (ASCII), Mathematical (Unicode), Address, Namespace
 * Base-4 words for crystal addressing and holographic expansions
 * 
 * @module CANONICAL_SYMBOL_ENGINE
 * @version 2.0.0
 */

import { TruthValue, WitnessPtr } from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: ALPHABET AND SYMBOL TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Alphabet layers (Definition A.1)
 */
export enum AlphabetLayer {
  Lexical = "Lexical",       // ASCII-safe canonical
  Mathematical = "Math",      // Unicode/LaTeX presentation
  Address = "Address",        // Crystal addressing
  Namespace = "Namespace"     // Domain prefixes
}

/**
 * Symbol class (Definition A.2)
 */
export enum SymbolClass {
  TypeCtor = "TypeCtor",
  TermCtor = "TermCtor",
  Op = "Op",
  Pred = "Pred",
  Const = "Const",
  Hub = "Hub",
  Bridge = "Bridge",
  Detector = "Detector",
  CertSchema = "CertSchema",
  Codec = "Codec",
  Policy = "Policy"
}

/**
 * Symbol (Definition A.2)
 */
export interface Symbol {
  name: string;              // Lexical canonical name
  class: SymbolClass;
  arity: number;
  type: string;              // Kernel type signature
  namespace: string;
  version: string;
  alias?: string;            // Mathematical presentation
  hash: string;
}

/**
 * Base-4 word (Definition A.3)
 */
export type Base4Digit = 0 | 1 | 2 | 3;
export type Base4Word = Base4Digit[];

/**
 * Crystal tag (Definition A.4)
 */
export interface CrystalTag {
  chapter: number;           // 01-21
  lens: "S" | "F" | "C" | "R";
  facet: 1 | 2 | 3 | 4;
  atom: "a" | "b" | "c" | "d";
}

/**
 * Namespace (Definition A.5)
 */
export interface Namespace {
  id: string;
  owner: string;             // Principal
  scope: string;             // Domain separation
  versionPolicy: VersionPolicy;
  hash: string;
}

export interface VersionPolicy {
  monotone: boolean;
  compatibilityRules: string[];
}

/**
 * Fully qualified name (Definition A.6)
 */
export interface FQName {
  namespace: string;
  name: string;
  version: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: SYMBOL COMPILER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Canonicalization result
 */
export interface CanonicalizationResult {
  canonical: string;
  normalized: boolean;
  warnings: string[];
}

/**
 * Symbol compilation result
 */
export interface SymbolCompilationResult {
  success: boolean;
  symbol?: Symbol;
  fqName?: FQName;
  errors: CompilationError[];
  trace: string;
}

export interface CompilationError {
  code: string;
  message: string;
  location: string;
}

/**
 * Symbol compiler (Construction A.1)
 */
export class SymbolCompiler {
  private reservedPrefixes = ["Ch", "App", "core", "pack", "sys"];
  private forbiddenChars = /[^a-zA-Z0-9_]/g;
  
  /**
   * Compile symbol from source declaration
   */
  compile(
    name: string,
    symbolClass: SymbolClass,
    type: string,
    namespace: string,
    version: string,
    alias?: string
  ): SymbolCompilationResult {
    const errors: CompilationError[] = [];
    
    // Step 1: Canonicalize name (Law A.1)
    const canonResult = this.canonicalize(name);
    if (canonResult.warnings.length > 0) {
      errors.push(...canonResult.warnings.map(w => ({
        code: "CANON_WARN",
        message: w,
        location: name
      })));
    }
    
    // Step 2: Check reserved prefixes
    if (this.hasReservedPrefix(canonResult.canonical) && namespace !== "core") {
      errors.push({
        code: "RESERVED_PREFIX",
        message: `Symbol uses reserved prefix`,
        location: canonResult.canonical
      });
    }
    
    // Step 3: Compute FQName
    const fqName: FQName = {
      namespace,
      name: canonResult.canonical,
      version
    };
    
    // Step 4: Compute arity from type signature
    const arity = this.computeArity(type);
    
    // Step 5: Compute hash
    const hash = this.computeSymbolHash({
      name: canonResult.canonical,
      class: symbolClass,
      arity,
      type,
      namespace,
      version
    });
    
    const symbol: Symbol = {
      name: canonResult.canonical,
      class: symbolClass,
      arity,
      type,
      namespace,
      version,
      alias,
      hash
    };
    
    return {
      success: errors.length === 0,
      symbol: errors.length === 0 ? symbol : undefined,
      fqName,
      errors,
      trace: hashString(`compile_${name}_${Date.now()}`)
    };
  }
  
  /**
   * Canonicalize name (Law A.1)
   */
  canonicalize(name: string): CanonicalizationResult {
    const warnings: string[] = [];
    
    // Normalize separators
    let canonical = name.replace(/[-\s]+/g, "_");
    
    // Lowercase
    const lower = canonical.toLowerCase();
    if (lower !== canonical) {
      warnings.push("Converted to lowercase");
      canonical = lower;
    }
    
    // Remove forbidden characters
    const cleaned = canonical.replace(this.forbiddenChars, "");
    if (cleaned !== canonical) {
      warnings.push("Removed forbidden characters");
      canonical = cleaned;
    }
    
    return {
      canonical,
      normalized: warnings.length > 0,
      warnings
    };
  }
  
  private hasReservedPrefix(name: string): boolean {
    return this.reservedPrefixes.some(prefix => 
      name.toLowerCase().startsWith(prefix.toLowerCase())
    );
  }
  
  private computeArity(type: string): number {
    // Count arrows in type signature
    const arrows = (type.match(/->/g) || []).length;
    return arrows;
  }
  
  private computeSymbolHash(symbol: Partial<Symbol>): string {
    return hashString(JSON.stringify({
      name: symbol.name,
      class: symbol.class,
      type: symbol.type,
      namespace: symbol.namespace,
      version: symbol.version
    }));
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
// SECTION 3: SYMBOL TABLE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Symbol table entry
 */
export interface SymbolTableEntry {
  symbol: Symbol;
  fqName: FQName;
  dependencies: string[];
  registered: number;
  hash: string;
}

/**
 * Collision check result
 */
export interface CollisionCheckResult {
  hasCollision: boolean;
  existingSymbol?: Symbol;
  existingFQName?: FQName;
}

/**
 * Symbol table
 */
export class SymbolTable {
  private entries: Map<string, SymbolTableEntry> = new Map();  // FQName string -> entry
  private byName: Map<string, Set<string>> = new Map();        // name -> FQName strings
  private byNamespace: Map<string, Set<string>> = new Map();   // namespace -> FQName strings
  
  /**
   * Register symbol
   */
  register(
    symbol: Symbol,
    fqName: FQName,
    dependencies: string[]
  ): RegistrationResult {
    const fqNameStr = this.fqNameToString(fqName);
    
    // Check for collision (Law A.3)
    const collision = this.checkCollision(fqName);
    if (collision.hasCollision) {
      return {
        success: false,
        error: "Collision detected",
        existingSymbol: collision.existingSymbol
      };
    }
    
    const entry: SymbolTableEntry = {
      symbol,
      fqName,
      dependencies,
      registered: Date.now(),
      hash: hashString(JSON.stringify({ symbol, fqName }))
    };
    
    this.entries.set(fqNameStr, entry);
    
    // Update indices
    if (!this.byName.has(symbol.name)) {
      this.byName.set(symbol.name, new Set());
    }
    this.byName.get(symbol.name)!.add(fqNameStr);
    
    if (!this.byNamespace.has(fqName.namespace)) {
      this.byNamespace.set(fqName.namespace, new Set());
    }
    this.byNamespace.get(fqName.namespace)!.add(fqNameStr);
    
    return { success: true, entry };
  }
  
  /**
   * Resolve symbol (Law A.5)
   */
  resolve(fqName: FQName): ResolveResult {
    const fqNameStr = this.fqNameToString(fqName);
    const entry = this.entries.get(fqNameStr);
    
    if (!entry) {
      return {
        type: "Boundary",
        kind: "MissingDependency",
        obligations: [`Register symbol ${fqNameStr}`]
      };
    }
    
    return { type: "Bulk", entry };
  }
  
  /**
   * Resolve by hash
   */
  resolveByHash(hash: string): ResolveResult {
    for (const entry of this.entries.values()) {
      if (entry.symbol.hash === hash) {
        return { type: "Bulk", entry };
      }
    }
    
    return {
      type: "Boundary",
      kind: "MissingDependency",
      obligations: [`Symbol with hash ${hash} not found`]
    };
  }
  
  /**
   * Check collision (Law A.3)
   */
  checkCollision(fqName: FQName): CollisionCheckResult {
    const fqNameStr = this.fqNameToString(fqName);
    const existing = this.entries.get(fqNameStr);
    
    if (existing) {
      return {
        hasCollision: true,
        existingSymbol: existing.symbol,
        existingFQName: existing.fqName
      };
    }
    
    return { hasCollision: false };
  }
  
  /**
   * Get symbols by name
   */
  getByName(name: string): SymbolTableEntry[] {
    const fqNames = this.byName.get(name);
    if (!fqNames) return [];
    
    return Array.from(fqNames)
      .map(fqn => this.entries.get(fqn))
      .filter((e): e is SymbolTableEntry => e !== undefined);
  }
  
  /**
   * Get symbols by namespace
   */
  getByNamespace(namespace: string): SymbolTableEntry[] {
    const fqNames = this.byNamespace.get(namespace);
    if (!fqNames) return [];
    
    return Array.from(fqNames)
      .map(fqn => this.entries.get(fqn))
      .filter((e): e is SymbolTableEntry => e !== undefined);
  }
  
  /**
   * Get all entries
   */
  getAll(): SymbolTableEntry[] {
    return Array.from(this.entries.values());
  }
  
  /**
   * Compute table hash
   */
  computeTableHash(): string {
    const entries = Array.from(this.entries.entries())
      .sort((a, b) => a[0].localeCompare(b[0]));
    return hashString(JSON.stringify(entries.map(e => e[1].hash)));
  }
  
  private fqNameToString(fqName: FQName): string {
    return `${fqName.namespace}::${fqName.name}@${fqName.version}`;
  }
}

export interface RegistrationResult {
  success: boolean;
  error?: string;
  entry?: SymbolTableEntry;
  existingSymbol?: Symbol;
}

export type ResolveResult =
  | { type: "Bulk"; entry: SymbolTableEntry }
  | { type: "Boundary"; kind: string; obligations: string[] };

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: ARCHETYPE MAPPING
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Elemental basis (Definition A.7)
 */
export const ELEMENTAL_BASIS: Base4Digit[] = [0, 1, 2, 3];

/**
 * Archetype at depth n
 */
export interface Archetype {
  depth: number;
  word: Base4Word;
  hash: string;
}

/**
 * 16-archetype palette (Definition A.8)
 */
export interface ArchetypePalette {
  depth: number;
  archetypes: Map<string, Archetype>;
  aliasTable: Map<string, string>;  // base4 -> presentation
}

/**
 * Rotation (Definition A.9)
 */
export interface ArchetypeRotation {
  type: "permutation" | "adjacent_step" | "tunnel";
  from: Base4Word;
  to: Base4Word;
  certificate?: string;
}

/**
 * Archetype manager
 */
export class ArchetypeManager {
  private palettes: Map<number, ArchetypePalette> = new Map();
  private admittedLevels = [4, 16, 64, 256, 1024];
  
  constructor() {
    this.initializePalettes();
  }
  
  /**
   * Initialize standard palettes
   */
  private initializePalettes(): void {
    // Depth 1: 4 archetypes
    this.createPalette(1);
    
    // Depth 2: 16 archetypes
    this.createPalette(2);
    
    // Depth 3: 64 archetypes
    this.createPalette(3);
  }
  
  /**
   * Create palette at depth
   */
  createPalette(depth: number): ArchetypePalette {
    const archetypes = new Map<string, Archetype>();
    const count = Math.pow(4, depth);
    
    for (let i = 0; i < count; i++) {
      const word = this.numberToBase4(i, depth);
      const key = word.join("");
      
      archetypes.set(key, {
        depth,
        word,
        hash: hashString(`archetype_${depth}_${key}`)
      });
    }
    
    const palette: ArchetypePalette = {
      depth,
      archetypes,
      aliasTable: this.createDefaultAliases(depth)
    };
    
    this.palettes.set(depth, palette);
    return palette;
  }
  
  /**
   * Get archetype by word
   */
  getArchetype(word: Base4Word): Archetype | undefined {
    const depth = word.length;
    const palette = this.palettes.get(depth);
    if (!palette) return undefined;
    
    return palette.archetypes.get(word.join(""));
  }
  
  /**
   * Expand archetype (Construction A.6)
   */
  expand(archetype: Archetype): Archetype[] {
    const expanded: Archetype[] = [];
    
    for (const digit of ELEMENTAL_BASIS) {
      const newWord: Base4Word = [...archetype.word, digit];
      expanded.push({
        depth: archetype.depth + 1,
        word: newWord,
        hash: hashString(`archetype_${archetype.depth + 1}_${newWord.join("")}`)
      });
    }
    
    return expanded;
  }
  
  /**
   * Contract archetype (Construction A.6)
   */
  contract(archetype: Archetype): Archetype | null {
    if (archetype.depth <= 1) return null;
    
    const newWord = archetype.word.slice(0, -1) as Base4Word;
    return {
      depth: archetype.depth - 1,
      word: newWord,
      hash: hashString(`archetype_${archetype.depth - 1}_${newWord.join("")}`)
    };
  }
  
  /**
   * Rotate archetype (Definition A.9)
   */
  rotate(archetype: Archetype, rotation: ArchetypeRotation): RotationResult {
    // Check rotation legality (Law A.9)
    if (!this.isRotationLegal(rotation)) {
      return {
        type: "Boundary",
        kind: "IllegalRotation",
        obligations: ["Use legal rotation (adjacent steps or tunnel via Z*)"]
      };
    }
    
    return {
      type: "Bulk",
      result: {
        depth: archetype.depth,
        word: rotation.to,
        hash: hashString(`archetype_${archetype.depth}_${rotation.to.join("")}`)
      }
    };
  }
  
  /**
   * Mix archetypes (Construction A.5)
   */
  mix(
    arch1: Archetype,
    arch2: Archetype,
    theta: number
  ): MixResult {
    if (arch1.depth !== arch2.depth) {
      return {
        type: "Boundary",
        kind: "DepthMismatch",
        obligations: ["Mix only same-depth archetypes"]
      };
    }
    
    // Convex combination (simplified)
    const mixedWord: Base4Word = arch1.word.map((d1, i) => {
      const d2 = arch2.word[i];
      return (theta < 0.5 ? d1 : d2) as Base4Digit;
    });
    
    return {
      type: "Bulk",
      result: {
        depth: arch1.depth,
        word: mixedWord,
        hash: hashString(`mixed_${mixedWord.join("")}_${theta}`)
      }
    };
  }
  
  /**
   * Check rotation legality
   */
  private isRotationLegal(rotation: ArchetypeRotation): boolean {
    if (rotation.type === "tunnel") {
      return rotation.certificate !== undefined;
    }
    
    if (rotation.type === "adjacent_step") {
      // Check only one digit differs by 1
      let diffs = 0;
      for (let i = 0; i < rotation.from.length; i++) {
        const diff = Math.abs(rotation.from[i] - rotation.to[i]);
        if (diff === 1) diffs++;
        else if (diff > 1) return false;
      }
      return diffs <= 1;
    }
    
    return true;
  }
  
  private numberToBase4(n: number, digits: number): Base4Word {
    const word: Base4Word = [];
    for (let i = 0; i < digits; i++) {
      word.unshift((n % 4) as Base4Digit);
      n = Math.floor(n / 4);
    }
    return word;
  }
  
  private createDefaultAliases(depth: number): Map<string, string> {
    const aliases = new Map<string, string>();
    
    if (depth === 1) {
      aliases.set("0", "Earth/Square");
      aliases.set("1", "Air/Flower");
      aliases.set("2", "Water/Cloud");
      aliases.set("3", "Fire/Fractal");
    }
    
    return aliases;
  }
  
  /**
   * Get palette
   */
  getPalette(depth: number): ArchetypePalette | undefined {
    return this.palettes.get(depth);
  }
}

export type RotationResult =
  | { type: "Bulk"; result: Archetype }
  | { type: "Boundary"; kind: string; obligations: string[] };

export type MixResult =
  | { type: "Bulk"; result: Archetype }
  | { type: "Boundary"; kind: string; obligations: string[] };

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: NUMERIC RANGES AND BOUNDS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Range representation (Definition A.11)
 */
export type RangeType = "interval" | "affine" | "distributional";

/**
 * Interval range
 */
export interface IntervalRange {
  type: "interval";
  lower: number;
  upper: number;
}

/**
 * Affine range
 */
export interface AffineRange {
  type: "affine";
  center: number;
  noiseSymbols: Map<string, number>;  // symbol -> coefficient
}

/**
 * Error type (A.C1.b)
 */
export enum ErrorKind {
  Roundoff = "Roundoff",
  Truncation = "Truncation",
  Sampling = "Sampling",
  ModelMismatch = "ModelMismatch",
  Drift = "Drift",
  Quantization = "Quantization"
}

/**
 * Error object
 */
export interface ErrorObject {
  kind: ErrorKind;
  magnitude: number;
  envelope: IntervalRange;
  assumptions: string[];
  propagationRule: "additive" | "multiplicative" | "max";
}

/**
 * Uncertainty field (A.C1.c)
 */
export interface UncertaintyField {
  representation: RangeType;
  envelope: IntervalRange | AffineRange;
  coverageMeaning: "worst-case" | "probabilistic";
  riskBudget: number;
}

/**
 * Bound calculator (Construction A.7-A.9)
 */
export class BoundCalculator {
  private noiseSymbolCounter = 0;
  
  /**
   * Create interval
   */
  createInterval(lower: number, upper: number): IntervalRange {
    return { type: "interval", lower, upper };
  }
  
  /**
   * Create affine form
   */
  createAffine(center: number): AffineRange {
    return {
      type: "affine",
      center,
      noiseSymbols: new Map()
    };
  }
  
  /**
   * Add noise symbol to affine form
   */
  addNoiseSymbol(affine: AffineRange, coefficient: number): AffineRange {
    const newSymbol = `eps_${this.noiseSymbolCounter++}`;
    const newSymbols = new Map(affine.noiseSymbols);
    newSymbols.set(newSymbol, coefficient);
    
    return {
      type: "affine",
      center: affine.center,
      noiseSymbols: newSymbols
    };
  }
  
  /**
   * Interval addition
   */
  addIntervals(a: IntervalRange, b: IntervalRange): IntervalRange {
    return {
      type: "interval",
      lower: a.lower + b.lower,
      upper: a.upper + b.upper
    };
  }
  
  /**
   * Interval multiplication
   */
  multiplyIntervals(a: IntervalRange, b: IntervalRange): IntervalRange {
    const products = [
      a.lower * b.lower,
      a.lower * b.upper,
      a.upper * b.lower,
      a.upper * b.upper
    ];
    
    return {
      type: "interval",
      lower: Math.min(...products),
      upper: Math.max(...products)
    };
  }
  
  /**
   * Interval division with straddle detection
   */
  divideIntervals(a: IntervalRange, b: IntervalRange): DivisionResult {
    // Check for division by zero (straddle)
    if (b.lower <= 0 && b.upper >= 0) {
      return {
        type: "Boundary",
        kind: "DivisionByZeroStraddle",
        obligations: ["Split interval or refine to exclude zero"]
      };
    }
    
    const quotients = [
      a.lower / b.lower,
      a.lower / b.upper,
      a.upper / b.lower,
      a.upper / b.upper
    ];
    
    return {
      type: "Bulk",
      result: {
        type: "interval",
        lower: Math.min(...quotients),
        upper: Math.max(...quotients)
      }
    };
  }
  
  /**
   * Convert affine to interval
   */
  affineToInterval(affine: AffineRange): IntervalRange {
    let radius = 0;
    for (const coeff of affine.noiseSymbols.values()) {
      radius += Math.abs(coeff);
    }
    
    return {
      type: "interval",
      lower: affine.center - radius,
      upper: affine.center + radius
    };
  }
  
  /**
   * Check if interval straddles threshold (Law A.14)
   */
  straddlesThreshold(interval: IntervalRange, threshold: number): boolean {
    return interval.lower <= threshold && interval.upper >= threshold;
  }
  
  /**
   * Propagate error (Law A.11)
   */
  propagateError(
    base: IntervalRange,
    error: ErrorObject
  ): IntervalRange {
    switch (error.propagationRule) {
      case "additive":
        return {
          type: "interval",
          lower: base.lower - error.magnitude,
          upper: base.upper + error.magnitude
        };
      case "multiplicative":
        return {
          type: "interval",
          lower: base.lower * (1 - error.magnitude),
          upper: base.upper * (1 + error.magnitude)
        };
      case "max":
        return {
          type: "interval",
          lower: Math.min(base.lower, base.lower - error.magnitude),
          upper: Math.max(base.upper, base.upper + error.magnitude)
        };
    }
  }
  
  /**
   * Check conservativeness (Law A.11)
   */
  isConservative(envelope: IntervalRange, trueValue: number): boolean {
    return envelope.lower <= trueValue && trueValue <= envelope.upper;
  }
}

export type DivisionResult =
  | { type: "Bulk"; result: IntervalRange }
  | { type: "Boundary"; kind: string; obligations: string[] };

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: SEED AND HOLOGRAPHIC LEVELS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Canonical seed (Definition A.12)
 */
export interface CanonicalSeed {
  id: string;
  rebuildId: string;
  corridor: string;
  depsRoot: string;
  payloadHash: string;
  rebuild: RebuildRecipe;
}

export interface RebuildRecipe {
  steps: RebuildStep[];
  deterministic: boolean;
  hash: string;
}

export interface RebuildStep {
  operation: string;
  params: Record<string, unknown>;
}

/**
 * Level policy
 */
export interface LevelPolicy {
  admittedLevels: number[];  // 4^n only
  transitions: LevelTransition[];
  checkpointRequirements: string[];
}

export interface LevelTransition {
  from: number;
  to: number;
  allowed: boolean;
  requirements: string[];
}

/**
 * Seed manager (Construction A.10-A.11)
 */
export class SeedManager {
  private seeds: Map<string, CanonicalSeed> = new Map();
  private levelPolicy: LevelPolicy;
  
  constructor() {
    this.levelPolicy = {
      admittedLevels: [4, 16, 64, 256, 1024, 4096],
      transitions: this.createDefaultTransitions(),
      checkpointRequirements: ["dependency_closure", "hash_verification"]
    };
  }
  
  /**
   * Create seed
   */
  createSeed(
    corridor: string,
    depsRoot: string,
    payloadHash: string,
    rebuildSteps: RebuildStep[]
  ): CanonicalSeed {
    const seed: CanonicalSeed = {
      id: `seed_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      rebuildId: hashString(`rebuild_${payloadHash}`),
      corridor,
      depsRoot,
      payloadHash,
      rebuild: {
        steps: rebuildSteps,
        deterministic: true,
        hash: hashString(JSON.stringify(rebuildSteps))
      }
    };
    
    this.seeds.set(seed.id, seed);
    return seed;
  }
  
  /**
   * Expand seed to level (Law A.15)
   */
  expand(seedId: string, level: number): ExpandResult {
    const seed = this.seeds.get(seedId);
    if (!seed) {
      return {
        type: "Boundary",
        kind: "SeedNotFound",
        obligations: [`Create seed ${seedId}`]
      };
    }
    
    // Check admitted level (Law A.7)
    if (!this.levelPolicy.admittedLevels.includes(level)) {
      return {
        type: "Boundary",
        kind: "NonAdmittedLevel",
        obligations: [`Use admitted level (4^n)`]
      };
    }
    
    // Execute rebuild recipe
    const result = this.executeRebuild(seed, level);
    
    return {
      type: "Bulk",
      object: result,
      level,
      seedId: seed.id
    };
  }
  
  /**
   * Collapse to seed (Law A.15)
   */
  collapse(object: unknown, level: number): CollapseResult {
    // Verify fixed-point property
    const payloadHash = hashString(JSON.stringify(object));
    
    const seed = this.createSeed(
      "default",
      hashString(`deps_${Date.now()}`),
      payloadHash,
      [{ operation: "materialize", params: { level } }]
    );
    
    return {
      type: "Bulk",
      seed,
      originalLevel: level
    };
  }
  
  /**
   * Verify fixed-point (Law A.15)
   * Collapse(Expand(Z*)) = Z*
   */
  verifyFixedPoint(seedId: string, level: number): FixedPointResult {
    const expandResult = this.expand(seedId, level);
    if (expandResult.type === "Boundary") {
      return { verified: false, reason: expandResult.kind };
    }
    
    const collapseResult = this.collapse(expandResult.object, level);
    if (collapseResult.type === "Boundary") {
      return { verified: false, reason: "Collapse failed" };
    }
    
    const originalSeed = this.seeds.get(seedId);
    const newSeed = collapseResult.seed;
    
    // Check if payload hashes match
    const verified = originalSeed?.payloadHash === newSeed.payloadHash;
    
    return {
      verified,
      reason: verified ? undefined : "Hash mismatch",
      certificate: verified ? hashString(`fixed_point_${seedId}_${level}`) : undefined
    };
  }
  
  private executeRebuild(seed: CanonicalSeed, level: number): unknown {
    // Simplified rebuild - would execute actual steps
    return {
      seedId: seed.id,
      level,
      payloadHash: seed.payloadHash,
      rebuilt: true
    };
  }
  
  private createDefaultTransitions(): LevelTransition[] {
    const levels = this.levelPolicy?.admittedLevels ?? [4, 16, 64, 256];
    const transitions: LevelTransition[] = [];
    
    for (let i = 0; i < levels.length - 1; i++) {
      transitions.push({
        from: levels[i],
        to: levels[i + 1],
        allowed: true,
        requirements: []
      });
      transitions.push({
        from: levels[i + 1],
        to: levels[i],
        allowed: true,
        requirements: ["checkpoint_required"]
      });
    }
    
    return transitions;
  }
}

export type ExpandResult =
  | { type: "Bulk"; object: unknown; level: number; seedId: string }
  | { type: "Boundary"; kind: string; obligations: string[] };

export type CollapseResult =
  | { type: "Bulk"; seed: CanonicalSeed; originalLevel: number }
  | { type: "Boundary"; kind: string; obligations: string[] };

export interface FixedPointResult {
  verified: boolean;
  reason?: string;
  certificate?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: LINT SYSTEM
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Lint rule
 */
export interface LintRule {
  id: string;
  name: string;
  severity: "error" | "warning" | "info";
  check: (symbol: Symbol, table: SymbolTable) => LintViolation[];
}

/**
 * Lint violation
 */
export interface LintViolation {
  ruleId: string;
  severity: "error" | "warning" | "info";
  message: string;
  location: string;
  suggestion?: string;
}

/**
 * Lint suite (Construction A.2)
 */
export class LintSuite {
  private rules: LintRule[] = [];
  
  constructor() {
    this.initializeDefaultRules();
  }
  
  private initializeDefaultRules(): void {
    // Rule: Illegal characters
    this.rules.push({
      id: "ILLEGAL_CHAR",
      name: "Illegal Characters",
      severity: "error",
      check: (symbol) => {
        const violations: LintViolation[] = [];
        if (/[^a-zA-Z0-9_]/.test(symbol.name)) {
          violations.push({
            ruleId: "ILLEGAL_CHAR",
            severity: "error",
            message: `Symbol name contains illegal characters`,
            location: symbol.name,
            suggestion: "Remove special characters"
          });
        }
        return violations;
      }
    });
    
    // Rule: Reserved prefix
    this.rules.push({
      id: "RESERVED_PREFIX",
      name: "Reserved Prefix Misuse",
      severity: "error",
      check: (symbol) => {
        const violations: LintViolation[] = [];
        const reserved = ["Ch", "App", "core"];
        
        for (const prefix of reserved) {
          if (symbol.name.toLowerCase().startsWith(prefix.toLowerCase()) &&
              symbol.namespace !== "core") {
            violations.push({
              ruleId: "RESERVED_PREFIX",
              severity: "error",
              message: `Symbol uses reserved prefix "${prefix}"`,
              location: symbol.name,
              suggestion: "Rename or use core namespace"
            });
          }
        }
        return violations;
      }
    });
    
    // Rule: Dangling reference
    this.rules.push({
      id: "DANGLING_REF",
      name: "Undeclared Reference",
      severity: "error",
      check: (symbol, table) => {
        // Would check type signature for undefined references
        return [];
      }
    });
    
    // Rule: Non-canonical name
    this.rules.push({
      id: "NON_CANONICAL",
      name: "Non-canonical Name",
      severity: "warning",
      check: (symbol) => {
        const violations: LintViolation[] = [];
        if (symbol.name !== symbol.name.toLowerCase()) {
          violations.push({
            ruleId: "NON_CANONICAL",
            severity: "warning",
            message: `Symbol name should be lowercase`,
            location: symbol.name,
            suggestion: `Rename to ${symbol.name.toLowerCase()}`
          });
        }
        return violations;
      }
    });
  }
  
  /**
   * Run lint suite
   */
  run(symbol: Symbol, table: SymbolTable): LintResult {
    const violations: LintViolation[] = [];
    
    for (const rule of this.rules) {
      violations.push(...rule.check(symbol, table));
    }
    
    const errors = violations.filter(v => v.severity === "error");
    const warnings = violations.filter(v => v.severity === "warning");
    
    return {
      passed: errors.length === 0,
      violations,
      errorCount: errors.length,
      warningCount: warnings.length,
      trace: hashString(JSON.stringify(violations))
    };
  }
  
  /**
   * Add custom rule
   */
  addRule(rule: LintRule): void {
    this.rules.push(rule);
  }
}

export interface LintResult {
  passed: boolean;
  violations: LintViolation[];
  errorCount: number;
  warningCount: number;
  trace: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 8: COMPLETE ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete Canonical Symbol Engine
 */
export class CanonicalSymbolEngine {
  private compiler: SymbolCompiler;
  private table: SymbolTable;
  private archetypeManager: ArchetypeManager;
  private boundCalculator: BoundCalculator;
  private seedManager: SeedManager;
  private lintSuite: LintSuite;
  
  constructor() {
    this.compiler = new SymbolCompiler();
    this.table = new SymbolTable();
    this.archetypeManager = new ArchetypeManager();
    this.boundCalculator = new BoundCalculator();
    this.seedManager = new SeedManager();
    this.lintSuite = new LintSuite();
    
    this.initializeCoreSymbols();
  }
  
  /**
   * Initialize core symbol set
   */
  private initializeCoreSymbols(): void {
    // Core types
    const coreSymbols = [
      { name: "Addr", class: SymbolClass.TypeCtor, type: "Type" },
      { name: "Tag", class: SymbolClass.TypeCtor, type: "Type" },
      { name: "MerkleRef", class: SymbolClass.TypeCtor, type: "Type" },
      { name: "Out", class: SymbolClass.TypeCtor, type: "Type -> Type" },
      { name: "Bulk", class: SymbolClass.TermCtor, type: "a -> Out a" },
      { name: "Bdry", class: SymbolClass.TermCtor, type: "Boundary -> Out a" },
      { name: "Expand", class: SymbolClass.Op, type: "Seed -> Level -> Out Object" },
      { name: "Collapse", class: SymbolClass.Op, type: "Object -> Level -> Out Seed" }
    ];
    
    for (const sym of coreSymbols) {
      const result = this.compiler.compile(
        sym.name,
        sym.class,
        sym.type,
        "core",
        "1.0.0"
      );
      
      if (result.success && result.symbol && result.fqName) {
        this.table.register(result.symbol, result.fqName, []);
      }
    }
  }
  
  /**
   * Compile and register symbol
   */
  compileAndRegister(
    name: string,
    symbolClass: SymbolClass,
    type: string,
    namespace: string,
    version: string,
    dependencies: string[] = []
  ): CompileAndRegisterResult {
    // Compile
    const compileResult = this.compiler.compile(
      name, symbolClass, type, namespace, version
    );
    
    if (!compileResult.success || !compileResult.symbol || !compileResult.fqName) {
      return {
        success: false,
        errors: compileResult.errors
      };
    }
    
    // Lint
    const lintResult = this.lintSuite.run(compileResult.symbol, this.table);
    if (!lintResult.passed) {
      return {
        success: false,
        errors: lintResult.violations.map(v => ({
          code: v.ruleId,
          message: v.message,
          location: v.location
        }))
      };
    }
    
    // Register
    const regResult = this.table.register(
      compileResult.symbol,
      compileResult.fqName,
      dependencies
    );
    
    if (!regResult.success) {
      return {
        success: false,
        errors: [{ code: "REG_FAIL", message: regResult.error ?? "Unknown", location: name }]
      };
    }
    
    return {
      success: true,
      symbol: compileResult.symbol,
      entry: regResult.entry,
      lintResult
    };
  }
  
  /**
   * Resolve symbol
   */
  resolve(fqName: FQName): ResolveResult {
    return this.table.resolve(fqName);
  }
  
  /**
   * Get archetype
   */
  getArchetype(word: Base4Word): Archetype | undefined {
    return this.archetypeManager.getArchetype(word);
  }
  
  /**
   * Create interval
   */
  createInterval(lower: number, upper: number): IntervalRange {
    return this.boundCalculator.createInterval(lower, upper);
  }
  
  /**
   * Create seed
   */
  createSeed(
    corridor: string,
    depsRoot: string,
    payloadHash: string,
    rebuildSteps: RebuildStep[]
  ): CanonicalSeed {
    return this.seedManager.createSeed(corridor, depsRoot, payloadHash, rebuildSteps);
  }
  
  /**
   * Expand seed
   */
  expandSeed(seedId: string, level: number): ExpandResult {
    return this.seedManager.expand(seedId, level);
  }
  
  /**
   * Collapse to seed
   */
  collapseSeed(object: unknown, level: number): CollapseResult {
    return this.seedManager.collapse(object, level);
  }
  
  /**
   * Verify fixed-point
   */
  verifyFixedPoint(seedId: string, level: number): FixedPointResult {
    return this.seedManager.verifyFixedPoint(seedId, level);
  }
  
  /**
   * Get symbol table hash
   */
  getTableHash(): string {
    return this.table.computeTableHash();
  }
  
  /**
   * Get statistics
   */
  getStats(): CanonicalSymbolStats {
    return {
      symbolCount: this.table.getAll().length,
      namespaces: new Set(this.table.getAll().map(e => e.fqName.namespace)).size,
      archetypePalettes: 3,  // Depth 1, 2, 3
      admittedLevels: [4, 16, 64, 256, 1024]
    };
  }
}

export interface CompileAndRegisterResult {
  success: boolean;
  symbol?: Symbol;
  entry?: SymbolTableEntry;
  lintResult?: LintResult;
  errors?: CompilationError[];
}

export interface CanonicalSymbolStats {
  symbolCount: number;
  namespaces: number;
  archetypePalettes: number;
  admittedLevels: number[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Enums
  AlphabetLayer,
  SymbolClass,
  ErrorKind,
  
  // Classes
  SymbolCompiler,
  SymbolTable,
  ArchetypeManager,
  BoundCalculator,
  SeedManager,
  LintSuite,
  CanonicalSymbolEngine
};
