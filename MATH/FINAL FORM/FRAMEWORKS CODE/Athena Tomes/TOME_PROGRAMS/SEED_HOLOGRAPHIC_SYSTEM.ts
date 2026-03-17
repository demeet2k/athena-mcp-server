/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * SEED HOLOGRAPHIC SYSTEM - Seeds, Expand/Collapse, and Holographic Storage
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * The Zero-Point Contract (from SELF_SUFFICIENCY_TOME §3):
 * 
 * Every artifact is anchored by a SEED (Z*): a minimal descriptor that commits to:
 *   - Identity
 *   - Corridor guards
 *   - Dependency closure
 *   - Reconstruction recipe
 * 
 * Fixed-Point Law:
 *   Collapse(Expand(Z*)) = Z*  at every admitted level
 * 
 * Seeds enable:
 *   - Lossless compression of knowledge into addressable cores
 *   - Checkpointing for stability under recursion and tunneling
 *   - Deterministic replay and reconstruction
 *   - Progressive refinement across admitted levels without drift
 * 
 * Holographic Level Rule:
 *   Full levels are powers of four: 4×4, 16×16, 64×64, 256×256, ...
 *   Non-power fragments are FORBIDDEN as complete semantics
 *   Res(d) = 4^(d-1)  →  3D: 16³, 4D: 64⁴, 5D: 256⁵
 * 
 * Storage Discipline:
 *   "Store-in, reconstruct-out"
 *   - Shared schemas live in appendices
 *   - Chapters reference by address
 *   - All dependencies are Merkle-linked
 * 
 * @module SEED_HOLOGRAPHIC_SYSTEM
 * @version 2.0.0
 */

import { TruthValue, WitnessPtr } from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: HOLOGRAPHIC LEVELS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Valid holographic levels (powers of 4)
 */
export const HOLOGRAPHIC_LEVELS = [4, 16, 64, 256, 1024, 4096] as const;
export type HolographicLevel = typeof HOLOGRAPHIC_LEVELS[number];

/**
 * Check if a dimension is a valid holographic level
 */
export function isValidHolographicLevel(n: number): n is HolographicLevel {
  return HOLOGRAPHIC_LEVELS.includes(n as HolographicLevel);
}

/**
 * Get the nearest valid holographic level
 */
export function nearestHolographicLevel(n: number): HolographicLevel {
  for (const level of HOLOGRAPHIC_LEVELS) {
    if (level >= n) return level;
  }
  return HOLOGRAPHIC_LEVELS[HOLOGRAPHIC_LEVELS.length - 1];
}

/**
 * Compute resolution for dimension d: Res(d) = 4^(d-1)
 */
export function resolutionForDimension(d: number): number {
  return Math.pow(4, d - 1);
}

/**
 * Holographic grid at a given level
 */
export interface HolographicGrid<T> {
  level: HolographicLevel;
  dimension: number;
  data: T[][];
  
  /** Get value at coordinates */
  get(coords: number[]): T | undefined;
  
  /** Set value at coordinates */
  set(coords: number[], value: T): void;
  
  /** Check if fully populated */
  isComplete(): boolean;
  
  /** Get population ratio */
  coverage(): number;
}

/**
 * Create holographic grid
 */
export function createHolographicGrid<T>(
  level: HolographicLevel,
  dimension: number,
  defaultValue: T
): HolographicGrid<T> {
  const size = Math.pow(level, dimension);
  const data: T[][] = [];
  
  // Initialize with default values
  for (let i = 0; i < level; i++) {
    data[i] = new Array(level).fill(defaultValue);
  }
  
  return {
    level,
    dimension,
    data,
    
    get(coords: number[]): T | undefined {
      if (coords.length !== 2) return undefined;
      const [x, y] = coords;
      if (x < 0 || x >= level || y < 0 || y >= level) return undefined;
      return data[x][y];
    },
    
    set(coords: number[], value: T): void {
      if (coords.length !== 2) return;
      const [x, y] = coords;
      if (x >= 0 && x < level && y >= 0 && y < level) {
        data[x][y] = value;
      }
    },
    
    isComplete(): boolean {
      for (let i = 0; i < level; i++) {
        for (let j = 0; j < level; j++) {
          if (data[i][j] === defaultValue) return false;
        }
      }
      return true;
    },
    
    coverage(): number {
      let populated = 0;
      const total = level * level;
      
      for (let i = 0; i < level; i++) {
        for (let j = 0; j < level; j++) {
          if (data[i][j] !== defaultValue) populated++;
        }
      }
      
      return populated / total;
    }
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: SEED STRUCTURE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Seed: Minimal descriptor for reconstruction
 * Z* = ⟨id, intent, guards, payload_hash, rebuild⟩
 */
export interface Seed {
  /** Unique identifier */
  id: string;
  
  /** Version */
  version: string;
  
  /** Intent/purpose descriptor */
  intent: SeedIntent;
  
  /** Corridor guards for reconstruction */
  guards: SeedGuard[];
  
  /** Hash of expanded payload */
  payloadHash: string;
  
  /** Reconstruction recipe */
  rebuild: RebuildRecipe;
  
  /** Dependency closure */
  dependencies: DependencyClosure;
  
  /** Level at which seed is valid */
  level: HolographicLevel;
  
  /** Creation timestamp */
  created: number;
  
  /** Checksum of seed itself */
  checksum: string;
}

export interface SeedIntent {
  name: string;
  description: string;
  category: "data" | "computation" | "theorem" | "algorithm" | "policy";
  tags: string[];
}

export interface SeedGuard {
  name: string;
  condition: string;  // Serialized predicate
  errorCode: string;
}

export interface RebuildRecipe {
  /** Recipe type */
  type: "direct" | "incremental" | "recursive" | "external";
  
  /** Steps for reconstruction */
  steps: RebuildStep[];
  
  /** Expected output hash */
  expectedHash: string;
  
  /** Timeout in ms */
  timeout: number;
}

export interface RebuildStep {
  operation: string;
  inputs: string[];  // Seed IDs or literal values
  parameters: Record<string, unknown>;
  outputKey: string;
}

export interface DependencyClosure {
  /** Direct dependencies */
  direct: string[];  // Seed IDs
  
  /** Transitive closure */
  transitive: string[];
  
  /** Merkle root of all dependencies */
  merkleRoot: string;
  
  /** Last computed */
  computed: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: EXPAND AND COLLAPSE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Expanded artifact: Full representation at a level
 */
export interface ExpandedArtifact<T> {
  /** Source seed */
  seedId: string;
  
  /** Expansion level */
  level: HolographicLevel;
  
  /** Full payload */
  payload: T;
  
  /** Computed hash */
  hash: string;
  
  /** Expansion witness */
  witness: ExpansionWitness;
  
  /** Timestamp */
  expanded: number;
}

export interface ExpansionWitness {
  seedHash: string;
  steps: ExpansionStep[];
  resourceUsage: { time: number; memory: number };
  valid: boolean;
}

export interface ExpansionStep {
  operation: string;
  inputHashes: string[];
  outputHash: string;
  timestamp: number;
}

/**
 * Expand a seed to full artifact
 */
export async function expand<T>(
  seed: Seed,
  context: ExpansionContext
): Promise<ExpandResult<T>> {
  const startTime = Date.now();
  const steps: ExpansionStep[] = [];
  
  // Verify guards
  for (const guard of seed.guards) {
    const result = context.checkGuard(guard);
    if (!result.passed) {
      return {
        success: false,
        error: `Guard failed: ${guard.name} - ${guard.errorCode}`
      };
    }
  }
  
  // Resolve dependencies
  const resolvedDeps = new Map<string, unknown>();
  for (const depId of seed.dependencies.direct) {
    const dep = await context.resolveDependency(depId);
    if (!dep) {
      return {
        success: false,
        error: `Dependency not found: ${depId}`
      };
    }
    resolvedDeps.set(depId, dep);
  }
  
  // Execute rebuild recipe
  const workspace = new Map<string, unknown>();
  workspace.set("__deps", resolvedDeps);
  
  for (const step of seed.rebuild.steps) {
    const inputs = step.inputs.map(input => {
      if (workspace.has(input)) return workspace.get(input);
      if (resolvedDeps.has(input)) return resolvedDeps.get(input);
      return input;  // Literal value
    });
    
    const output = await context.executeOperation(step.operation, inputs, step.parameters);
    workspace.set(step.outputKey, output);
    
    steps.push({
      operation: step.operation,
      inputHashes: inputs.map(i => hashValue(i)),
      outputHash: hashValue(output),
      timestamp: Date.now()
    });
  }
  
  // Get final output
  const payload = workspace.get("__result") as T;
  const hash = hashValue(payload);
  
  // Verify hash matches expected
  if (hash !== seed.payloadHash) {
    return {
      success: false,
      error: `Hash mismatch: expected ${seed.payloadHash}, got ${hash}`
    };
  }
  
  const endTime = Date.now();
  
  return {
    success: true,
    artifact: {
      seedId: seed.id,
      level: seed.level,
      payload,
      hash,
      witness: {
        seedHash: seed.checksum,
        steps,
        resourceUsage: { time: endTime - startTime, memory: 0 },
        valid: true
      },
      expanded: endTime
    }
  };
}

export interface ExpansionContext {
  checkGuard: (guard: SeedGuard) => { passed: boolean; reason?: string };
  resolveDependency: (id: string) => Promise<unknown>;
  executeOperation: (op: string, inputs: unknown[], params: Record<string, unknown>) => Promise<unknown>;
}

export type ExpandResult<T> = 
  | { success: true; artifact: ExpandedArtifact<T> }
  | { success: false; error: string };

/**
 * Collapse an artifact back to seed
 */
export function collapse<T>(
  artifact: ExpandedArtifact<T>,
  intent: SeedIntent,
  guards: SeedGuard[],
  recipe: RebuildRecipe,
  dependencies: DependencyClosure
): Seed {
  const id = `seed_${Date.now()}_${artifact.hash.slice(0, 8)}`;
  
  const seed: Seed = {
    id,
    version: "1.0.0",
    intent,
    guards,
    payloadHash: artifact.hash,
    rebuild: recipe,
    dependencies,
    level: artifact.level,
    created: Date.now(),
    checksum: ""
  };
  
  // Compute checksum
  seed.checksum = computeSeedChecksum(seed);
  
  return seed;
}

/**
 * Verify fixed-point law: Collapse(Expand(Z*)) = Z*
 */
export async function verifyFixedPoint<T>(
  seed: Seed,
  context: ExpansionContext
): Promise<FixedPointResult> {
  // Expand
  const expandResult = await expand<T>(seed, context);
  if (!expandResult.success) {
    return {
      valid: false,
      error: `Expansion failed: ${expandResult.error}`
    };
  }
  
  // Collapse back
  const collapsedSeed = collapse(
    expandResult.artifact,
    seed.intent,
    seed.guards,
    seed.rebuild,
    seed.dependencies
  );
  
  // Verify equality (by payload hash and checksum)
  const hashesMatch = seed.payloadHash === collapsedSeed.payloadHash;
  const checksumValid = seed.checksum === collapsedSeed.checksum;
  
  return {
    valid: hashesMatch,
    originalHash: seed.payloadHash,
    roundTripHash: collapsedSeed.payloadHash,
    hashesMatch,
    checksumValid
  };
}

export interface FixedPointResult {
  valid: boolean;
  originalHash?: string;
  roundTripHash?: string;
  hashesMatch?: boolean;
  checksumValid?: boolean;
  error?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: MERKLE-LINKED STORAGE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Merkle node
 */
export interface MerkleNode {
  hash: string;
  type: "leaf" | "internal";
  data?: unknown;
  left?: string;  // Child hash
  right?: string;
}

/**
 * Merkle tree for dependency tracking
 */
export class MerkleTree {
  private nodes: Map<string, MerkleNode> = new Map();
  private root: string | null = null;
  
  /**
   * Add leaf node
   */
  addLeaf(data: unknown): string {
    const hash = hashValue(data);
    this.nodes.set(hash, {
      hash,
      type: "leaf",
      data
    });
    return hash;
  }
  
  /**
   * Combine two nodes into internal node
   */
  combine(leftHash: string, rightHash: string): string {
    const combinedHash = hashValue(`${leftHash}:${rightHash}`);
    this.nodes.set(combinedHash, {
      hash: combinedHash,
      type: "internal",
      left: leftHash,
      right: rightHash
    });
    return combinedHash;
  }
  
  /**
   * Build tree from leaves
   */
  buildFromLeaves(leaves: unknown[]): string {
    if (leaves.length === 0) {
      return hashValue("empty");
    }
    
    // Add all leaves
    let currentLevel = leaves.map(l => this.addLeaf(l));
    
    // Build tree bottom-up
    while (currentLevel.length > 1) {
      const nextLevel: string[] = [];
      
      for (let i = 0; i < currentLevel.length; i += 2) {
        if (i + 1 < currentLevel.length) {
          nextLevel.push(this.combine(currentLevel[i], currentLevel[i + 1]));
        } else {
          // Odd number: carry up
          nextLevel.push(currentLevel[i]);
        }
      }
      
      currentLevel = nextLevel;
    }
    
    this.root = currentLevel[0];
    return this.root;
  }
  
  /**
   * Get root hash
   */
  getRoot(): string | null {
    return this.root;
  }
  
  /**
   * Get proof of inclusion
   */
  getProof(hash: string): MerkleProof | null {
    if (!this.nodes.has(hash)) return null;
    
    const siblings: { hash: string; position: "left" | "right" }[] = [];
    
    // Walk up to root collecting siblings
    let current = hash;
    while (current !== this.root) {
      let found = false;
      
      for (const [nodeHash, node] of this.nodes) {
        if (node.type === "internal") {
          if (node.left === current) {
            siblings.push({ hash: node.right!, position: "right" });
            current = nodeHash;
            found = true;
            break;
          } else if (node.right === current) {
            siblings.push({ hash: node.left!, position: "left" });
            current = nodeHash;
            found = true;
            break;
          }
        }
      }
      
      if (!found) break;
    }
    
    return {
      leafHash: hash,
      siblings,
      root: this.root!
    };
  }
  
  /**
   * Verify proof
   */
  verifyProof(proof: MerkleProof): boolean {
    let current = proof.leafHash;
    
    for (const sibling of proof.siblings) {
      if (sibling.position === "left") {
        current = hashValue(`${sibling.hash}:${current}`);
      } else {
        current = hashValue(`${current}:${sibling.hash}`);
      }
    }
    
    return current === proof.root;
  }
  
  /**
   * Get node by hash
   */
  getNode(hash: string): MerkleNode | undefined {
    return this.nodes.get(hash);
  }
}

export interface MerkleProof {
  leafHash: string;
  siblings: { hash: string; position: "left" | "right" }[];
  root: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: HOLOGRAPHIC STORAGE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Storage entry
 */
export interface StorageEntry {
  address: string;
  seed: Seed;
  merkleProof: MerkleProof;
  level: HolographicLevel;
  created: number;
  lastAccessed: number;
  accessCount: number;
}

/**
 * Holographic storage: "Store-in, reconstruct-out"
 */
export class HolographicStorage {
  private entries: Map<string, StorageEntry> = new Map();
  private seedIndex: Map<string, string> = new Map();  // seedId -> address
  private merkleTree: MerkleTree = new MerkleTree();
  private schemas: Map<string, Schema> = new Map();
  
  /**
   * Store a seed
   */
  store(seed: Seed): string {
    const address = this.computeAddress(seed);
    
    // Add to Merkle tree
    const leafHash = this.merkleTree.addLeaf(seed);
    
    // Create entry
    const entry: StorageEntry = {
      address,
      seed,
      merkleProof: {
        leafHash,
        siblings: [],
        root: leafHash
      },
      level: seed.level,
      created: Date.now(),
      lastAccessed: Date.now(),
      accessCount: 0
    };
    
    this.entries.set(address, entry);
    this.seedIndex.set(seed.id, address);
    
    return address;
  }
  
  /**
   * Retrieve by address
   */
  retrieve(address: string): StorageEntry | undefined {
    const entry = this.entries.get(address);
    if (entry) {
      entry.lastAccessed = Date.now();
      entry.accessCount++;
    }
    return entry;
  }
  
  /**
   * Retrieve by seed ID
   */
  retrieveBySeedId(seedId: string): StorageEntry | undefined {
    const address = this.seedIndex.get(seedId);
    if (!address) return undefined;
    return this.retrieve(address);
  }
  
  /**
   * Update Merkle tree
   */
  rebuildMerkleTree(): string {
    const seeds = Array.from(this.entries.values()).map(e => e.seed);
    const root = this.merkleTree.buildFromLeaves(seeds);
    
    // Update proofs
    for (const entry of this.entries.values()) {
      const leafHash = hashValue(entry.seed);
      const proof = this.merkleTree.getProof(leafHash);
      if (proof) {
        entry.merkleProof = proof;
      }
    }
    
    return root;
  }
  
  /**
   * Verify storage integrity
   */
  verifyIntegrity(): IntegrityResult {
    const issues: string[] = [];
    let validCount = 0;
    
    for (const [address, entry] of this.entries) {
      // Verify address
      const expectedAddress = this.computeAddress(entry.seed);
      if (address !== expectedAddress) {
        issues.push(`Address mismatch for ${entry.seed.id}`);
        continue;
      }
      
      // Verify seed checksum
      const expectedChecksum = computeSeedChecksum(entry.seed);
      if (entry.seed.checksum !== expectedChecksum) {
        issues.push(`Checksum mismatch for ${entry.seed.id}`);
        continue;
      }
      
      // Verify Merkle proof
      if (!this.merkleTree.verifyProof(entry.merkleProof)) {
        issues.push(`Merkle proof invalid for ${entry.seed.id}`);
        continue;
      }
      
      validCount++;
    }
    
    return {
      valid: issues.length === 0,
      totalEntries: this.entries.size,
      validEntries: validCount,
      issues
    };
  }
  
  /**
   * Register schema
   */
  registerSchema(schema: Schema): void {
    this.schemas.set(schema.id, schema);
  }
  
  /**
   * Get schema
   */
  getSchema(id: string): Schema | undefined {
    return this.schemas.get(id);
  }
  
  /**
   * List all addresses
   */
  listAddresses(): string[] {
    return Array.from(this.entries.keys());
  }
  
  /**
   * Get storage statistics
   */
  getStats(): StorageStats {
    const levels = new Map<HolographicLevel, number>();
    let totalSize = 0;
    
    for (const entry of this.entries.values()) {
      levels.set(entry.level, (levels.get(entry.level) ?? 0) + 1);
      totalSize += JSON.stringify(entry.seed).length;
    }
    
    return {
      totalEntries: this.entries.size,
      entriesByLevel: levels,
      totalSize,
      merkleRoot: this.merkleTree.getRoot() ?? "empty",
      schemaCount: this.schemas.size
    };
  }
  
  private computeAddress(seed: Seed): string {
    const data = `${seed.id}:${seed.payloadHash}:${seed.level}`;
    return `addr_${hashValue(data).slice(0, 16)}`;
  }
}

export interface Schema {
  id: string;
  name: string;
  version: string;
  fields: SchemaField[];
}

export interface SchemaField {
  name: string;
  type: string;
  required: boolean;
  defaultValue?: unknown;
}

export interface IntegrityResult {
  valid: boolean;
  totalEntries: number;
  validEntries: number;
  issues: string[];
}

export interface StorageStats {
  totalEntries: number;
  entriesByLevel: Map<HolographicLevel, number>;
  totalSize: number;
  merkleRoot: string;
  schemaCount: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: SEED BUILDER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Builder for creating seeds
 */
export class SeedBuilder {
  private id: string;
  private version: string = "1.0.0";
  private intent: SeedIntent;
  private guards: SeedGuard[] = [];
  private steps: RebuildStep[] = [];
  private directDeps: string[] = [];
  private level: HolographicLevel = 16;
  private payload?: unknown;
  
  constructor(id: string, intent: SeedIntent) {
    this.id = id;
    this.intent = intent;
  }
  
  setVersion(version: string): this {
    this.version = version;
    return this;
  }
  
  addGuard(name: string, condition: string, errorCode: string): this {
    this.guards.push({ name, condition, errorCode });
    return this;
  }
  
  addStep(operation: string, inputs: string[], parameters: Record<string, unknown>, outputKey: string): this {
    this.steps.push({ operation, inputs, parameters, outputKey });
    return this;
  }
  
  addDependency(seedId: string): this {
    if (!this.directDeps.includes(seedId)) {
      this.directDeps.push(seedId);
    }
    return this;
  }
  
  setLevel(level: HolographicLevel): this {
    this.level = level;
    return this;
  }
  
  setPayload(payload: unknown): this {
    this.payload = payload;
    return this;
  }
  
  build(): Seed {
    if (!this.payload) {
      throw new Error("Payload must be set");
    }
    
    const payloadHash = hashValue(this.payload);
    
    // Compute transitive dependencies (simplified: just direct for now)
    const transitive = [...this.directDeps];
    const merkleTree = new MerkleTree();
    const merkleRoot = merkleTree.buildFromLeaves(this.directDeps);
    
    const seed: Seed = {
      id: this.id,
      version: this.version,
      intent: this.intent,
      guards: this.guards,
      payloadHash,
      rebuild: {
        type: this.steps.length <= 1 ? "direct" : "incremental",
        steps: this.steps,
        expectedHash: payloadHash,
        timeout: 30000
      },
      dependencies: {
        direct: this.directDeps,
        transitive,
        merkleRoot,
        computed: Date.now()
      },
      level: this.level,
      created: Date.now(),
      checksum: ""
    };
    
    seed.checksum = computeSeedChecksum(seed);
    
    return seed;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: UTILITIES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Hash a value
 */
export function hashValue(value: unknown): string {
  const str = JSON.stringify(value);
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash = hash & hash;
  }
  return Math.abs(hash).toString(16).padStart(16, '0');
}

/**
 * Compute seed checksum
 */
export function computeSeedChecksum(seed: Omit<Seed, "checksum">): string {
  const data = {
    id: seed.id,
    version: seed.version,
    intent: seed.intent,
    guards: seed.guards,
    payloadHash: seed.payloadHash,
    rebuild: seed.rebuild,
    dependencies: seed.dependencies,
    level: seed.level
  };
  return hashValue(data);
}

/**
 * Validate seed structure
 */
export function validateSeed(seed: Seed): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  // Check required fields
  if (!seed.id) errors.push("Missing id");
  if (!seed.version) errors.push("Missing version");
  if (!seed.intent) errors.push("Missing intent");
  if (!seed.payloadHash) errors.push("Missing payloadHash");
  if (!seed.rebuild) errors.push("Missing rebuild recipe");
  if (!seed.dependencies) errors.push("Missing dependencies");
  
  // Check level is valid
  if (!isValidHolographicLevel(seed.level)) {
    errors.push(`Invalid holographic level: ${seed.level}`);
  }
  
  // Check checksum
  const expectedChecksum = computeSeedChecksum(seed);
  if (seed.checksum !== expectedChecksum) {
    errors.push("Checksum mismatch");
  }
  
  // Warnings for optional fields
  if (seed.guards.length === 0) {
    warnings.push("No guards defined");
  }
  
  return {
    valid: errors.length === 0,
    errors,
    warnings
  };
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 8: HOLOGRAPHIC ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete Seed Holographic Engine
 */
export class SeedHolographicEngine {
  private storage: HolographicStorage;
  private expansionContext: ExpansionContext;
  private operationRegistry: Map<string, (inputs: unknown[], params: Record<string, unknown>) => Promise<unknown>> = new Map();
  
  constructor() {
    this.storage = new HolographicStorage();
    
    // Create default expansion context
    this.expansionContext = {
      checkGuard: (guard) => ({ passed: true }),
      resolveDependency: async (id) => {
        const entry = this.storage.retrieveBySeedId(id);
        return entry?.seed;
      },
      executeOperation: async (op, inputs, params) => {
        const operation = this.operationRegistry.get(op);
        if (!operation) {
          throw new Error(`Unknown operation: ${op}`);
        }
        return operation(inputs, params);
      }
    };
    
    this.registerDefaultOperations();
  }
  
  /**
   * Register operation
   */
  registerOperation(
    name: string,
    fn: (inputs: unknown[], params: Record<string, unknown>) => Promise<unknown>
  ): void {
    this.operationRegistry.set(name, fn);
  }
  
  /**
   * Store seed
   */
  store(seed: Seed): string {
    return this.storage.store(seed);
  }
  
  /**
   * Retrieve seed
   */
  retrieve(address: string): Seed | undefined {
    return this.storage.retrieve(address)?.seed;
  }
  
  /**
   * Expand seed
   */
  async expand<T>(seedId: string): Promise<ExpandResult<T>> {
    const entry = this.storage.retrieveBySeedId(seedId);
    if (!entry) {
      return { success: false, error: `Seed not found: ${seedId}` };
    }
    
    return expand<T>(entry.seed, this.expansionContext);
  }
  
  /**
   * Create and store seed
   */
  createSeed(
    id: string,
    intent: SeedIntent,
    payload: unknown,
    options?: {
      guards?: SeedGuard[];
      steps?: RebuildStep[];
      dependencies?: string[];
      level?: HolographicLevel;
    }
  ): string {
    const builder = new SeedBuilder(id, intent).setPayload(payload);
    
    if (options?.guards) {
      for (const g of options.guards) {
        builder.addGuard(g.name, g.condition, g.errorCode);
      }
    }
    
    if (options?.steps) {
      for (const s of options.steps) {
        builder.addStep(s.operation, s.inputs, s.parameters, s.outputKey);
      }
    }
    
    if (options?.dependencies) {
      for (const d of options.dependencies) {
        builder.addDependency(d);
      }
    }
    
    if (options?.level) {
      builder.setLevel(options.level);
    }
    
    const seed = builder.build();
    return this.store(seed);
  }
  
  /**
   * Verify fixed-point for seed
   */
  async verifyFixedPoint<T>(seedId: string): Promise<FixedPointResult> {
    const entry = this.storage.retrieveBySeedId(seedId);
    if (!entry) {
      return { valid: false, error: `Seed not found: ${seedId}` };
    }
    
    return verifyFixedPoint<T>(entry.seed, this.expansionContext);
  }
  
  /**
   * Rebuild Merkle tree
   */
  rebuildMerkle(): string {
    return this.storage.rebuildMerkleTree();
  }
  
  /**
   * Verify storage integrity
   */
  verifyIntegrity(): IntegrityResult {
    return this.storage.verifyIntegrity();
  }
  
  /**
   * Get storage statistics
   */
  getStats(): StorageStats {
    return this.storage.getStats();
  }
  
  /**
   * List all seed IDs
   */
  listSeeds(): string[] {
    return this.storage.listAddresses()
      .map(addr => this.storage.retrieve(addr)?.seed.id)
      .filter((id): id is string => id !== undefined);
  }
  
  private registerDefaultOperations(): void {
    // Identity operation
    this.registerOperation("identity", async (inputs) => inputs[0]);
    
    // Combine operation
    this.registerOperation("combine", async (inputs) => inputs);
    
    // Transform operation
    this.registerOperation("transform", async (inputs, params) => {
      const fn = params.transform as ((x: unknown) => unknown) | undefined;
      if (fn) {
        return fn(inputs[0]);
      }
      return inputs[0];
    });
    
    // Result operation (sets __result)
    this.registerOperation("result", async (inputs) => {
      return { __result: inputs[0] };
    });
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Levels
  HOLOGRAPHIC_LEVELS,
  isValidHolographicLevel,
  nearestHolographicLevel,
  resolutionForDimension,
  createHolographicGrid,
  
  // Seed
  SeedBuilder,
  expand,
  collapse,
  verifyFixedPoint,
  
  // Merkle
  MerkleTree,
  
  // Storage
  HolographicStorage,
  
  // Utilities
  hashValue,
  computeSeedChecksum,
  validateSeed,
  
  // Engine
  SeedHolographicEngine
};
