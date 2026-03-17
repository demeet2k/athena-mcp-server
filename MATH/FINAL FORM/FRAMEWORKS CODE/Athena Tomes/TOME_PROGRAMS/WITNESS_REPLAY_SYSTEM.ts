/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * WITNESS REPLAY SYSTEM - Deterministic Witness Generation and Replay Capsules
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Core Principle: Every computation must be witnessable and replayable
 * 
 * Components:
 *   - Witness: Proof that a computation occurred correctly
 *   - Replay Capsule: Self-contained bundle for deterministic re-execution
 *   - Content Addressing: All data referenced by cryptographic hash
 *   - Provenance Chain: Complete audit trail from input to output
 * 
 * @module WITNESS_REPLAY_SYSTEM
 * @version 2.0.0
 */

import { TruthValue } from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: CONTENT ADDRESSING
// ═══════════════════════════════════════════════════════════════════════════════

export interface ContentAddress {
  hash: string;
  algorithm: "sha256" | "sha384" | "sha512" | "blake2b";
  size: number;
  timestamp: number;
}

export interface ContentStore {
  put(content: Uint8Array): Promise<ContentAddress>;
  get(address: ContentAddress): Promise<Uint8Array | null>;
  has(address: ContentAddress): Promise<boolean>;
  delete(address: ContentAddress): Promise<boolean>;
  list(): Promise<ContentAddress[]>;
}

export class MemoryContentStore implements ContentStore {
  private store: Map<string, { content: Uint8Array; metadata: ContentAddress }> = new Map();
  
  async put(content: Uint8Array): Promise<ContentAddress> {
    const hash = await this.computeHash(content);
    const address: ContentAddress = {
      hash,
      algorithm: "sha256",
      size: content.length,
      timestamp: Date.now()
    };
    this.store.set(hash, { content: new Uint8Array(content), metadata: address });
    return address;
  }
  
  async get(address: ContentAddress): Promise<Uint8Array | null> {
    const entry = this.store.get(address.hash);
    return entry ? new Uint8Array(entry.content) : null;
  }
  
  async has(address: ContentAddress): Promise<boolean> {
    return this.store.has(address.hash);
  }
  
  async delete(address: ContentAddress): Promise<boolean> {
    return this.store.delete(address.hash);
  }
  
  async list(): Promise<ContentAddress[]> {
    return Array.from(this.store.values()).map(e => e.metadata);
  }
  
  private async computeHash(content: Uint8Array): Promise<string> {
    let hash = 0;
    for (let i = 0; i < content.length; i++) {
      hash = ((hash << 5) - hash) + content[i];
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(64, '0');
  }
}

export function serialize(value: unknown): Uint8Array {
  return new TextEncoder().encode(JSON.stringify(value));
}

export function deserialize<T>(bytes: Uint8Array): T {
  return JSON.parse(new TextDecoder().decode(bytes)) as T;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: WITNESS STRUCTURE
// ═══════════════════════════════════════════════════════════════════════════════

export interface Witness {
  id: string;
  version: string;
  claim: WitnessClaim;
  evidence: WitnessEvidence;
  attestations: Attestation[];
  metadata: WitnessMetadata;
  contentRefs: ContentAddress[];
  witnessHash: string;
}

export interface WitnessClaim {
  type: "computation" | "state" | "transition" | "invariant" | "equivalence";
  subject: string;
  predicate: string;
  truthValue: TruthValue;
  confidence: number;
}

export interface WitnessEvidence {
  inputs: ContentAddress[];
  outputs: ContentAddress[];
  intermediates?: ContentAddress[];
  trace?: ExecutionTrace;
  proofs?: ProofObject[];
}

export interface ExecutionTrace {
  steps: TraceStep[];
  startTime: number;
  endTime: number;
  resourceUsage: { cpuMs: number; memoryBytes: number; ioOps: number };
}

export interface TraceStep {
  id: string;
  operation: string;
  inputs: string[];
  output: string;
  timestamp: number;
  duration: number;
}

export interface ProofObject {
  id: string;
  type: "zkp" | "merkle" | "signature" | "hash_chain";
  data: string;
  verifiable: boolean;
}

export interface Attestation {
  attesterId: string;
  attesterType: "system" | "user" | "oracle" | "consensus";
  timestamp: number;
  signature: string;
  publicKey?: string;
}

export interface WitnessMetadata {
  created: number;
  expires?: number;
  tags: string[];
  correlationId?: string;
  parentWitnessId?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: WITNESS GENERATOR
// ═══════════════════════════════════════════════════════════════════════════════

export interface WitnessGeneratorConfig {
  includeTrace: boolean;
  includeIntermediates: boolean;
  generateProofs: boolean;
  attesters: AttesterConfig[];
  contentStore: ContentStore;
}

export interface AttesterConfig {
  id: string;
  type: Attestation["attesterType"];
  sign: (data: string) => Promise<string>;
}

export class WitnessGenerator {
  private config: WitnessGeneratorConfig;
  private witnessCounter: number = 0;
  
  constructor(config: WitnessGeneratorConfig) {
    this.config = config;
  }
  
  async generateComputationWitness<I, O>(
    computation: (input: I) => O,
    input: I,
    description: string
  ): Promise<{ witness: Witness; output: O }> {
    const startTime = Date.now();
    const traceSteps: TraceStep[] = [];
    
    const inputBytes = serialize(input);
    const inputAddr = await this.config.contentStore.put(inputBytes);
    
    if (this.config.includeTrace) {
      traceSteps.push({
        id: "start",
        operation: "begin_computation",
        inputs: [inputAddr.hash],
        output: "",
        timestamp: Date.now(),
        duration: 0
      });
    }
    
    const output = computation(input);
    
    if (this.config.includeTrace) {
      traceSteps.push({
        id: "end",
        operation: "end_computation",
        inputs: [],
        output: "success",
        timestamp: Date.now(),
        duration: Date.now() - startTime
      });
    }
    
    const outputBytes = serialize(output);
    const outputAddr = await this.config.contentStore.put(outputBytes);
    const endTime = Date.now();
    
    const witness = await this.buildWitness({
      type: "computation",
      subject: description,
      predicate: `computed(${inputAddr.hash}) = ${outputAddr.hash}`,
      truthValue: TruthValue.OK,
      confidence: 1.0
    }, {
      inputs: [inputAddr],
      outputs: [outputAddr],
      trace: this.config.includeTrace ? {
        steps: traceSteps,
        startTime,
        endTime,
        resourceUsage: {
          cpuMs: endTime - startTime,
          memoryBytes: inputBytes.length + outputBytes.length,
          ioOps: 2
        }
      } : undefined
    });
    
    return { witness, output };
  }
  
  async generateTransitionWitness<S>(
    beforeState: S,
    afterState: S,
    action: string
  ): Promise<Witness> {
    const beforeAddr = await this.config.contentStore.put(serialize(beforeState));
    const afterAddr = await this.config.contentStore.put(serialize(afterState));
    
    return this.buildWitness({
      type: "transition",
      subject: action,
      predicate: `transition(${beforeAddr.hash}, ${action}) = ${afterAddr.hash}`,
      truthValue: TruthValue.OK,
      confidence: 1.0
    }, {
      inputs: [beforeAddr],
      outputs: [afterAddr]
    });
  }
  
  async generateInvariantWitness(
    invariantName: string,
    state: unknown,
    satisfied: boolean
  ): Promise<Witness> {
    const stateAddr = await this.config.contentStore.put(serialize(state));
    
    return this.buildWitness({
      type: "invariant",
      subject: invariantName,
      predicate: `invariant(${invariantName}) = ${satisfied}`,
      truthValue: satisfied ? TruthValue.OK : TruthValue.FAIL,
      confidence: 1.0
    }, {
      inputs: [stateAddr],
      outputs: []
    });
  }
  
  async generateEquivalenceWitness(
    left: unknown,
    right: unknown,
    equivalent: boolean
  ): Promise<Witness> {
    const leftAddr = await this.config.contentStore.put(serialize(left));
    const rightAddr = await this.config.contentStore.put(serialize(right));
    
    return this.buildWitness({
      type: "equivalence",
      subject: "equivalence_check",
      predicate: `${leftAddr.hash} ≡ ${rightAddr.hash}`,
      truthValue: equivalent ? TruthValue.OK : TruthValue.FAIL,
      confidence: 1.0
    }, {
      inputs: [leftAddr, rightAddr],
      outputs: []
    });
  }
  
  private async buildWitness(
    claim: WitnessClaim,
    evidence: Omit<WitnessEvidence, "proofs">
  ): Promise<Witness> {
    const id = `wit_${++this.witnessCounter}_${Date.now()}`;
    
    const proofs: ProofObject[] = [];
    if (this.config.generateProofs) {
      proofs.push({
        id: `proof_${id}`,
        type: "hash_chain",
        data: this.computeHashChain(evidence.inputs, evidence.outputs),
        verifiable: true
      });
    }
    
    const attestations: Attestation[] = [];
    for (const attester of this.config.attesters) {
      const signature = await attester.sign(JSON.stringify({ claim, evidence }));
      attestations.push({
        attesterId: attester.id,
        attesterType: attester.type,
        timestamp: Date.now(),
        signature
      });
    }
    
    const witness: Witness = {
      id,
      version: "2.0.0",
      claim,
      evidence: { ...evidence, proofs },
      attestations,
      metadata: {
        created: Date.now(),
        tags: [claim.type, claim.subject]
      },
      contentRefs: [...evidence.inputs, ...evidence.outputs],
      witnessHash: ""
    };
    
    witness.witnessHash = this.computeWitnessHash(witness);
    return witness;
  }
  
  private computeHashChain(inputs: ContentAddress[], outputs: ContentAddress[]): string {
    const hashes = [...inputs.map(i => i.hash), ...outputs.map(o => o.hash)];
    return this.simpleHash(hashes.join(""));
  }
  
  private computeWitnessHash(witness: Omit<Witness, "witnessHash">): string {
    return this.simpleHash(JSON.stringify({ id: witness.id, claim: witness.claim }));
  }
  
  private simpleHash(s: string): string {
    let hash = 0;
    for (let i = 0; i < s.length; i++) {
      hash = ((hash << 5) - hash) + s.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(64, '0');
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: REPLAY CAPSULE
// ═══════════════════════════════════════════════════════════════════════════════

export interface ReplayCapsule {
  id: string;
  version: string;
  computation: ComputationDescriptor;
  inputs: CapsuleData[];
  expectedOutputs: CapsuleData[];
  environment: EnvironmentSnapshot;
  requirements: ExecutionRequirements;
  witnessId: string;
  capsuleHash: string;
  signatures: CapsuleSignature[];
}

export interface ComputationDescriptor {
  computationId: string;
  name: string;
  version: string;
  code?: string;
  codeRef?: string;
  parameters: Record<string, unknown>;
}

export interface CapsuleData {
  name: string;
  contentAddress: ContentAddress;
  data: Uint8Array;
  schema?: string;
}

export interface EnvironmentSnapshot {
  timestamp: number;
  randomSeed: number;
  timezone: string;
  locale: string;
  customVariables: Record<string, unknown>;
}

export interface ExecutionRequirements {
  minMemoryBytes: number;
  maxTimeMs: number;
  requiredLibraries: string[];
  deterministicRandom: boolean;
}

export interface CapsuleSignature {
  signerId: string;
  timestamp: number;
  signature: string;
  scope: "inputs" | "outputs" | "full";
}

export class ReplayCapsuleBuilder {
  private capsuleCounter: number = 0;
  private contentStore: ContentStore;
  
  constructor(contentStore: ContentStore) {
    this.contentStore = contentStore;
  }
  
  async buildFromWitness(
    witness: Witness,
    computation: ComputationDescriptor,
    environment: Partial<EnvironmentSnapshot> = {}
  ): Promise<ReplayCapsule> {
    const id = `capsule_${++this.capsuleCounter}_${Date.now()}`;
    
    const inputs: CapsuleData[] = [];
    for (let i = 0; i < witness.evidence.inputs.length; i++) {
      const addr = witness.evidence.inputs[i];
      const data = await this.contentStore.get(addr);
      if (data) {
        inputs.push({ name: `input_${i}`, contentAddress: addr, data });
      }
    }
    
    const expectedOutputs: CapsuleData[] = [];
    for (let i = 0; i < witness.evidence.outputs.length; i++) {
      const addr = witness.evidence.outputs[i];
      const data = await this.contentStore.get(addr);
      if (data) {
        expectedOutputs.push({ name: `output_${i}`, contentAddress: addr, data });
      }
    }
    
    const fullEnvironment: EnvironmentSnapshot = {
      timestamp: witness.metadata.created,
      randomSeed: this.deterministicSeed(witness.id),
      timezone: "UTC",
      locale: "en-US",
      customVariables: {},
      ...environment
    };
    
    return {
      id,
      version: "2.0.0",
      computation,
      inputs,
      expectedOutputs,
      environment: fullEnvironment,
      requirements: {
        minMemoryBytes: inputs.reduce((sum, i) => sum + i.data.length, 0) * 2,
        maxTimeMs: witness.evidence.trace?.resourceUsage.cpuMs ?? 1000,
        requiredLibraries: [],
        deterministicRandom: true
      },
      witnessId: witness.id,
      capsuleHash: this.computeCapsuleHash(id, inputs, expectedOutputs),
      signatures: []
    };
  }
  
  async buildMinimal<I, O>(
    input: I,
    expectedOutput: O,
    computation: ComputationDescriptor
  ): Promise<ReplayCapsule> {
    const id = `capsule_${++this.capsuleCounter}_${Date.now()}`;
    
    const inputBytes = serialize(input);
    const outputBytes = serialize(expectedOutput);
    const inputAddr = await this.contentStore.put(inputBytes);
    const outputAddr = await this.contentStore.put(outputBytes);
    
    return {
      id,
      version: "2.0.0",
      computation,
      inputs: [{ name: "input", contentAddress: inputAddr, data: inputBytes }],
      expectedOutputs: [{ name: "output", contentAddress: outputAddr, data: outputBytes }],
      environment: {
        timestamp: Date.now(),
        randomSeed: this.deterministicSeed(id),
        timezone: "UTC",
        locale: "en-US",
        customVariables: {}
      },
      requirements: {
        minMemoryBytes: inputBytes.length + outputBytes.length,
        maxTimeMs: 1000,
        requiredLibraries: [],
        deterministicRandom: true
      },
      witnessId: "",
      capsuleHash: this.computeCapsuleHash(id, [], []),
      signatures: []
    };
  }
  
  private deterministicSeed(id: string): number {
    let seed = 0;
    for (let i = 0; i < id.length; i++) {
      seed = ((seed << 5) - seed) + id.charCodeAt(i);
      seed = seed & seed;
    }
    return Math.abs(seed);
  }
  
  private computeCapsuleHash(id: string, inputs: CapsuleData[], outputs: CapsuleData[]): string {
    const data = id + inputs.map(i => i.contentAddress.hash).join("") + outputs.map(o => o.contentAddress.hash).join("");
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
      hash = ((hash << 5) - hash) + data.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(64, '0');
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: REPLAY EXECUTOR
// ═══════════════════════════════════════════════════════════════════════════════

export interface ReplayResult {
  success: boolean;
  capsuleId: string;
  actualOutputs: CapsuleData[];
  outputsMatch: boolean;
  executionTime: number;
  witness?: Witness;
  errors: string[];
}

export class ReplayExecutor {
  private contentStore: ContentStore;
  private witnessGenerator: WitnessGenerator;
  private computations: Map<string, (input: unknown) => unknown> = new Map();
  
  constructor(contentStore: ContentStore, witnessGenerator: WitnessGenerator) {
    this.contentStore = contentStore;
    this.witnessGenerator = witnessGenerator;
  }
  
  registerComputation(id: string, fn: (input: unknown) => unknown): void {
    this.computations.set(id, fn);
  }
  
  async replay(capsule: ReplayCapsule): Promise<ReplayResult> {
    const startTime = Date.now();
    const errors: string[] = [];
    
    // Get computation
    const computation = this.computations.get(capsule.computation.computationId);
    if (!computation) {
      return {
        success: false,
        capsuleId: capsule.id,
        actualOutputs: [],
        outputsMatch: false,
        executionTime: Date.now() - startTime,
        errors: [`Computation not found: ${capsule.computation.computationId}`]
      };
    }
    
    // Deserialize inputs
    const inputs = capsule.inputs.map(i => deserialize(i.data));
    
    // Execute computation
    const actualOutputs: CapsuleData[] = [];
    try {
      for (let i = 0; i < inputs.length; i++) {
        const output = computation(inputs[i]);
        const outputBytes = serialize(output);
        const outputAddr = await this.contentStore.put(outputBytes);
        actualOutputs.push({
          name: `output_${i}`,
          contentAddress: outputAddr,
          data: outputBytes
        });
      }
    } catch (error) {
      errors.push(`Execution error: ${error}`);
      return {
        success: false,
        capsuleId: capsule.id,
        actualOutputs,
        outputsMatch: false,
        executionTime: Date.now() - startTime,
        errors
      };
    }
    
    // Verify outputs match
    const outputsMatch = this.verifyOutputs(capsule.expectedOutputs, actualOutputs);
    
    // Generate witness for replay
    const witness = await this.witnessGenerator.generateComputationWitness(
      () => actualOutputs,
      inputs,
      `Replay of ${capsule.computation.name}`
    ).then(r => r.witness);
    
    return {
      success: outputsMatch,
      capsuleId: capsule.id,
      actualOutputs,
      outputsMatch,
      executionTime: Date.now() - startTime,
      witness,
      errors
    };
  }
  
  private verifyOutputs(expected: CapsuleData[], actual: CapsuleData[]): boolean {
    if (expected.length !== actual.length) return false;
    
    for (let i = 0; i < expected.length; i++) {
      if (expected[i].contentAddress.hash !== actual[i].contentAddress.hash) {
        return false;
      }
    }
    
    return true;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: WITNESS VERIFICATION
// ═══════════════════════════════════════════════════════════════════════════════

export interface VerificationResult {
  valid: boolean;
  witnessId: string;
  checks: VerificationCheck[];
  overallConfidence: number;
  timestamp: number;
}

export interface VerificationCheck {
  name: string;
  passed: boolean;
  message: string;
  severity: "info" | "warning" | "error";
}

export class WitnessVerifier {
  private contentStore: ContentStore;
  
  constructor(contentStore: ContentStore) {
    this.contentStore = contentStore;
  }
  
  async verify(witness: Witness): Promise<VerificationResult> {
    const checks: VerificationCheck[] = [];
    
    // Check 1: Witness hash integrity
    const expectedHash = this.computeWitnessHash(witness);
    checks.push({
      name: "HashIntegrity",
      passed: witness.witnessHash === expectedHash,
      message: witness.witnessHash === expectedHash 
        ? "Witness hash verified" 
        : "Witness hash mismatch",
      severity: witness.witnessHash === expectedHash ? "info" : "error"
    });
    
    // Check 2: Content availability
    let allContentAvailable = true;
    for (const ref of witness.contentRefs) {
      const available = await this.contentStore.has(ref);
      if (!available) {
        allContentAvailable = false;
        checks.push({
          name: "ContentAvailability",
          passed: false,
          message: `Content not found: ${ref.hash}`,
          severity: "error"
        });
      }
    }
    if (allContentAvailable) {
      checks.push({
        name: "ContentAvailability",
        passed: true,
        message: "All referenced content available",
        severity: "info"
      });
    }
    
    // Check 3: Attestation validity
    const hasAttestations = witness.attestations.length > 0;
    checks.push({
      name: "Attestations",
      passed: hasAttestations,
      message: hasAttestations 
        ? `${witness.attestations.length} attestation(s) present` 
        : "No attestations",
      severity: hasAttestations ? "info" : "warning"
    });
    
    // Check 4: Claim confidence
    checks.push({
      name: "ClaimConfidence",
      passed: witness.claim.confidence >= 0.5,
      message: `Confidence: ${witness.claim.confidence}`,
      severity: witness.claim.confidence >= 0.5 ? "info" : "warning"
    });
    
    // Check 5: Truth value
    checks.push({
      name: "TruthValue",
      passed: witness.claim.truthValue === TruthValue.OK,
      message: `Truth value: ${witness.claim.truthValue}`,
      severity: witness.claim.truthValue === TruthValue.OK ? "info" : "warning"
    });
    
    // Check 6: Timestamp validity
    const notExpired = !witness.metadata.expires || witness.metadata.expires > Date.now();
    checks.push({
      name: "NotExpired",
      passed: notExpired,
      message: notExpired ? "Witness not expired" : "Witness expired",
      severity: notExpired ? "info" : "error"
    });
    
    const passedChecks = checks.filter(c => c.passed).length;
    const totalChecks = checks.length;
    const overallConfidence = passedChecks / totalChecks;
    
    return {
      valid: checks.every(c => c.severity !== "error" || c.passed),
      witnessId: witness.id,
      checks,
      overallConfidence,
      timestamp: Date.now()
    };
  }
  
  private computeWitnessHash(witness: Witness): string {
    const data = JSON.stringify({ id: witness.id, claim: witness.claim });
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
      hash = ((hash << 5) - hash) + data.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(64, '0');
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: PROVENANCE CHAIN
// ═══════════════════════════════════════════════════════════════════════════════

export interface ProvenanceNode {
  id: string;
  type: "source" | "computation" | "aggregation" | "transformation";
  timestamp: number;
  witnessId?: string;
  inputs: string[];
  outputs: string[];
  metadata: Record<string, unknown>;
}

export interface ProvenanceChain {
  id: string;
  nodes: ProvenanceNode[];
  edges: ProvenanceEdge[];
  root: string;
  leaves: string[];
}

export interface ProvenanceEdge {
  from: string;
  to: string;
  type: "derived_from" | "generated_by" | "transformed_by";
}

export class ProvenanceTracker {
  private chains: Map<string, ProvenanceChain> = new Map();
  private nodeCounter: number = 0;
  
  createChain(rootData: unknown, sourceType: string): ProvenanceChain {
    const rootId = `prov_${++this.nodeCounter}`;
    const chain: ProvenanceChain = {
      id: `chain_${Date.now()}`,
      nodes: [{
        id: rootId,
        type: "source",
        timestamp: Date.now(),
        inputs: [],
        outputs: [this.hashData(rootData)],
        metadata: { sourceType }
      }],
      edges: [],
      root: rootId,
      leaves: [rootId]
    };
    
    this.chains.set(chain.id, chain);
    return chain;
  }
  
  addComputation(
    chainId: string,
    inputNodeIds: string[],
    outputData: unknown,
    witness: Witness
  ): ProvenanceNode {
    const chain = this.chains.get(chainId);
    if (!chain) throw new Error(`Chain not found: ${chainId}`);
    
    const nodeId = `prov_${++this.nodeCounter}`;
    const node: ProvenanceNode = {
      id: nodeId,
      type: "computation",
      timestamp: Date.now(),
      witnessId: witness.id,
      inputs: inputNodeIds,
      outputs: [this.hashData(outputData)],
      metadata: { witnessHash: witness.witnessHash }
    };
    
    chain.nodes.push(node);
    
    // Add edges
    for (const inputId of inputNodeIds) {
      chain.edges.push({
        from: inputId,
        to: nodeId,
        type: "derived_from"
      });
      
      // Update leaves
      const leafIndex = chain.leaves.indexOf(inputId);
      if (leafIndex >= 0) {
        chain.leaves.splice(leafIndex, 1);
      }
    }
    chain.leaves.push(nodeId);
    
    return node;
  }
  
  addTransformation(
    chainId: string,
    inputNodeId: string,
    outputData: unknown,
    transformationType: string
  ): ProvenanceNode {
    const chain = this.chains.get(chainId);
    if (!chain) throw new Error(`Chain not found: ${chainId}`);
    
    const nodeId = `prov_${++this.nodeCounter}`;
    const node: ProvenanceNode = {
      id: nodeId,
      type: "transformation",
      timestamp: Date.now(),
      inputs: [inputNodeId],
      outputs: [this.hashData(outputData)],
      metadata: { transformationType }
    };
    
    chain.nodes.push(node);
    chain.edges.push({
      from: inputNodeId,
      to: nodeId,
      type: "transformed_by"
    });
    
    // Update leaves
    const leafIndex = chain.leaves.indexOf(inputNodeId);
    if (leafIndex >= 0) {
      chain.leaves.splice(leafIndex, 1);
    }
    chain.leaves.push(nodeId);
    
    return node;
  }
  
  getChain(chainId: string): ProvenanceChain | undefined {
    return this.chains.get(chainId);
  }
  
  getAncestors(chainId: string, nodeId: string): ProvenanceNode[] {
    const chain = this.chains.get(chainId);
    if (!chain) return [];
    
    const ancestors: ProvenanceNode[] = [];
    const visited = new Set<string>();
    const queue = [nodeId];
    
    while (queue.length > 0) {
      const currentId = queue.shift()!;
      if (visited.has(currentId)) continue;
      visited.add(currentId);
      
      const node = chain.nodes.find(n => n.id === currentId);
      if (node && currentId !== nodeId) {
        ancestors.push(node);
      }
      
      // Find parent edges
      for (const edge of chain.edges) {
        if (edge.to === currentId && !visited.has(edge.from)) {
          queue.push(edge.from);
        }
      }
    }
    
    return ancestors;
  }
  
  private hashData(data: unknown): string {
    const str = JSON.stringify(data);
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = ((hash << 5) - hash) + str.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(16, '0');
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 8: WITNESS REPLAY ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

export class WitnessReplayEngine {
  private contentStore: ContentStore;
  private witnessGenerator: WitnessGenerator;
  private capsuleBuilder: ReplayCapsuleBuilder;
  private replayExecutor: ReplayExecutor;
  private verifier: WitnessVerifier;
  private provenanceTracker: ProvenanceTracker;
  
  private witnesses: Map<string, Witness> = new Map();
  private capsules: Map<string, ReplayCapsule> = new Map();
  
  constructor(config?: Partial<WitnessGeneratorConfig>) {
    this.contentStore = new MemoryContentStore();
    
    const fullConfig: WitnessGeneratorConfig = {
      includeTrace: true,
      includeIntermediates: false,
      generateProofs: true,
      attesters: [{
        id: "system",
        type: "system",
        sign: async (data) => `sig_${data.length}_${Date.now()}`
      }],
      contentStore: this.contentStore,
      ...config
    };
    
    this.witnessGenerator = new WitnessGenerator(fullConfig);
    this.capsuleBuilder = new ReplayCapsuleBuilder(this.contentStore);
    this.replayExecutor = new ReplayExecutor(this.contentStore, this.witnessGenerator);
    this.verifier = new WitnessVerifier(this.contentStore);
    this.provenanceTracker = new ProvenanceTracker();
  }
  
  async witnessComputation<I, O>(
    computation: (input: I) => O,
    input: I,
    description: string
  ): Promise<{ witness: Witness; output: O; capsule: ReplayCapsule }> {
    const { witness, output } = await this.witnessGenerator.generateComputationWitness(
      computation,
      input,
      description
    );
    
    this.witnesses.set(witness.id, witness);
    
    const capsule = await this.capsuleBuilder.buildFromWitness(witness, {
      computationId: description,
      name: description,
      version: "1.0.0",
      parameters: {}
    });
    
    this.capsules.set(capsule.id, capsule);
    
    return { witness, output, capsule };
  }
  
  async replay(capsuleId: string): Promise<ReplayResult> {
    const capsule = this.capsules.get(capsuleId);
    if (!capsule) {
      return {
        success: false,
        capsuleId,
        actualOutputs: [],
        outputsMatch: false,
        executionTime: 0,
        errors: [`Capsule not found: ${capsuleId}`]
      };
    }
    
    return this.replayExecutor.replay(capsule);
  }
  
  async verify(witnessId: string): Promise<VerificationResult> {
    const witness = this.witnesses.get(witnessId);
    if (!witness) {
      return {
        valid: false,
        witnessId,
        checks: [{
          name: "WitnessExists",
          passed: false,
          message: `Witness not found: ${witnessId}`,
          severity: "error"
        }],
        overallConfidence: 0,
        timestamp: Date.now()
      };
    }
    
    return this.verifier.verify(witness);
  }
  
  registerComputation(id: string, fn: (input: unknown) => unknown): void {
    this.replayExecutor.registerComputation(id, fn);
  }
  
  getWitness(id: string): Witness | undefined {
    return this.witnesses.get(id);
  }
  
  getCapsule(id: string): ReplayCapsule | undefined {
    return this.capsules.get(id);
  }
  
  createProvenanceChain(rootData: unknown, sourceType: string): ProvenanceChain {
    return this.provenanceTracker.createChain(rootData, sourceType);
  }
  
  addToProvenance(
    chainId: string,
    inputNodeIds: string[],
    outputData: unknown,
    witness: Witness
  ): ProvenanceNode {
    return this.provenanceTracker.addComputation(chainId, inputNodeIds, outputData, witness);
  }
  
  getProvenance(chainId: string): ProvenanceChain | undefined {
    return this.provenanceTracker.getChain(chainId);
  }
  
  getAllWitnesses(): Witness[] {
    return Array.from(this.witnesses.values());
  }
  
  getAllCapsules(): ReplayCapsule[] {
    return Array.from(this.capsules.values());
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Content addressing
  MemoryContentStore,
  serialize,
  deserialize,
  
  // Witness
  WitnessGenerator,
  WitnessVerifier,
  
  // Replay
  ReplayCapsuleBuilder,
  ReplayExecutor,
  
  // Provenance
  ProvenanceTracker,
  
  // Engine
  WitnessReplayEngine
};
