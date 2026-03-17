/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * AWAKENING OS - CORE INFRASTRUCTURE
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Complete implementation of shared infrastructure used by all 18 TOMEs.
 * This is the foundational layer providing:
 * 
 * - Truth Lattice with full semantics
 * - Edge algebra with composition rules
 * - Addressing system with validation
 * - Corridor budgets with tracking
 * - Replay capsules with cryptographic sealing
 * - Witness system with evidence chains
 * 
 * @module CORE_INFRASTRUCTURE
 * @version 3.0.0
 */

import * as crypto from 'crypto';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: TRUTH LATTICE - Complete Implementation
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Truth values form a bounded lattice with FAIL at bottom, OK at top.
 * Operations: meet (∧), join (∨), and comparison.
 */
export enum TruthValue {
  FAIL = 0,
  AMBIG = 1,
  NEAR = 2,
  OK = 3
}

export namespace TruthLattice {
  
  // Lattice ordering
  export function compare(a: TruthValue, b: TruthValue): -1 | 0 | 1 {
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
  }
  
  // Meet (greatest lower bound)
  export function meet(a: TruthValue, b: TruthValue): TruthValue {
    return Math.min(a, b) as TruthValue;
  }
  
  // Join (least upper bound)
  export function join(a: TruthValue, b: TruthValue): TruthValue {
    return Math.max(a, b) as TruthValue;
  }
  
  // Can promote from a to b?
  export function canPromote(from: TruthValue, to: TruthValue): boolean {
    return to >= from;
  }
  
  // Truth obligations for each level
  export interface TruthObligation {
    witnessRequired: boolean;
    replayRequired: boolean;
    residualAllowed: boolean;
    quarantineRequired: boolean;
    evidencePlanRequired: boolean;
  }
  
  export const Obligations: Record<TruthValue, TruthObligation> = {
    [TruthValue.OK]: {
      witnessRequired: true,
      replayRequired: true,
      residualAllowed: false,
      quarantineRequired: false,
      evidencePlanRequired: false
    },
    [TruthValue.NEAR]: {
      witnessRequired: true,
      replayRequired: true,
      residualAllowed: true,
      quarantineRequired: false,
      evidencePlanRequired: true
    },
    [TruthValue.AMBIG]: {
      witnessRequired: false,
      replayRequired: false,
      residualAllowed: true,
      quarantineRequired: false,
      evidencePlanRequired: true
    },
    [TruthValue.FAIL]: {
      witnessRequired: false,
      replayRequired: false,
      residualAllowed: true,
      quarantineRequired: true,
      evidencePlanRequired: false
    }
  };
  
  // Verdict with full metadata
  export interface Verdict {
    value: TruthValue;
    witness?: WitnessPtr;
    replay?: ReplayCapsule;
    residual?: ResidualLedger;
    evidencePlan?: EvidencePlan;
    quarantine?: QuarantineRecord;
  }
  
  // Check if verdict satisfies obligations
  export function validateVerdict(verdict: Verdict): ValidationResult {
    const obs = Obligations[verdict.value];
    const errors: string[] = [];
    
    if (obs.witnessRequired && !verdict.witness) {
      errors.push("Witness required for this truth level");
    }
    if (obs.replayRequired && !verdict.replay) {
      errors.push("Replay capsule required for this truth level");
    }
    if (!obs.residualAllowed && verdict.residual && verdict.residual.entries.length > 0) {
      errors.push("Residual not allowed for OK status");
    }
    if (obs.quarantineRequired && !verdict.quarantine) {
      errors.push("Quarantine required for FAIL status");
    }
    if (obs.evidencePlanRequired && !verdict.evidencePlan) {
      errors.push("Evidence plan required for NEAR/AMBIG status");
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: EDGE KINDS - Complete Algebra
// ═══════════════════════════════════════════════════════════════════════════════

export enum EdgeKind {
  REF = "REF",           // Reference: A points to B
  EQUIV = "EQUIV",       // Equivalence: A ≡ B (symmetric)
  MIGRATE = "MIGRATE",   // Migration: A → B (version change)
  DUAL = "DUAL",         // Duality: A ⟷ B (dual relationship)
  GEN = "GEN",           // Generalization: A ⊑ B
  INST = "INST",         // Instantiation: A : B (instance of)
  IMPL = "IMPL",         // Implementation: A implements B
  PROOF = "PROOF",       // Proof: A proves B
  CONFLICT = "CONFLICT"  // Conflict: A conflicts with B
}

export namespace EdgeAlgebra {
  
  // Edge properties
  export interface EdgeProperties {
    symmetric: boolean;
    transitive: boolean;
    reflexive: boolean;
    inverse?: EdgeKind;
  }
  
  export const Properties: Record<EdgeKind, EdgeProperties> = {
    [EdgeKind.REF]: { symmetric: false, transitive: true, reflexive: false },
    [EdgeKind.EQUIV]: { symmetric: true, transitive: true, reflexive: true },
    [EdgeKind.MIGRATE]: { symmetric: false, transitive: true, reflexive: false },
    [EdgeKind.DUAL]: { symmetric: true, transitive: false, reflexive: false },
    [EdgeKind.GEN]: { symmetric: false, transitive: true, reflexive: true, inverse: EdgeKind.INST },
    [EdgeKind.INST]: { symmetric: false, transitive: false, reflexive: false, inverse: EdgeKind.GEN },
    [EdgeKind.IMPL]: { symmetric: false, transitive: true, reflexive: false },
    [EdgeKind.PROOF]: { symmetric: false, transitive: false, reflexive: false },
    [EdgeKind.CONFLICT]: { symmetric: true, transitive: false, reflexive: false }
  };
  
  // Edge composition: if A -k1-> B and B -k2-> C, what is A -> C?
  export function compose(k1: EdgeKind, k2: EdgeKind): EdgeKind | null {
    // Composition rules
    const compositionTable: Partial<Record<EdgeKind, Partial<Record<EdgeKind, EdgeKind>>>> = {
      [EdgeKind.REF]: {
        [EdgeKind.REF]: EdgeKind.REF,
        [EdgeKind.EQUIV]: EdgeKind.REF,
        [EdgeKind.GEN]: EdgeKind.REF
      },
      [EdgeKind.GEN]: {
        [EdgeKind.GEN]: EdgeKind.GEN,
        [EdgeKind.EQUIV]: EdgeKind.GEN
      },
      [EdgeKind.INST]: {
        [EdgeKind.IMPL]: EdgeKind.IMPL
      },
      [EdgeKind.IMPL]: {
        [EdgeKind.IMPL]: EdgeKind.IMPL,
        [EdgeKind.REF]: EdgeKind.IMPL
      },
      [EdgeKind.MIGRATE]: {
        [EdgeKind.MIGRATE]: EdgeKind.MIGRATE,
        [EdgeKind.REF]: EdgeKind.MIGRATE
      },
      [EdgeKind.PROOF]: {
        [EdgeKind.PROOF]: EdgeKind.PROOF,
        [EdgeKind.REF]: EdgeKind.PROOF
      },
      [EdgeKind.EQUIV]: {
        [EdgeKind.EQUIV]: EdgeKind.EQUIV,
        [EdgeKind.REF]: EdgeKind.REF,
        [EdgeKind.GEN]: EdgeKind.GEN
      }
    };
    
    return compositionTable[k1]?.[k2] ?? null;
  }
  
  // Get inverse edge kind
  export function inverse(k: EdgeKind): EdgeKind | null {
    const props = Properties[k];
    if (props.symmetric) return k;
    return props.inverse ?? null;
  }
  
  // Check if edge can be added (no conflicts)
  export function canAdd(existing: EdgeKind[], newEdge: EdgeKind): boolean {
    // Cannot add CONFLICT alongside EQUIV
    if (newEdge === EdgeKind.CONFLICT && existing.includes(EdgeKind.EQUIV)) {
      return false;
    }
    if (newEdge === EdgeKind.EQUIV && existing.includes(EdgeKind.CONFLICT)) {
      return false;
    }
    return true;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: ADDRESSING SYSTEM - Complete Implementation
// ═══════════════════════════════════════════════════════════════════════════════

export type Lens = "S" | "F" | "C" | "R";
export type Facet = 1 | 2 | 3 | 4;
export type Atom = "a" | "b" | "c" | "d";
export type Rail = "Su" | "Me" | "Sa";

export namespace Addressing {
  
  export const LENSES: Lens[] = ["S", "F", "C", "R"];
  export const FACETS: Facet[] = [1, 2, 3, 4];
  export const ATOMS: Atom[] = ["a", "b", "c", "d"];
  export const RAILS: Rail[] = ["Su", "Me", "Sa"];
  
  export const LensSemantics: Record<Lens, string> = {
    S: "Square: Structure / Invariants / Discrete",
    F: "Flower: Operators / Compilation / Dynamics",
    C: "Cloud: Corridors / Uncertainty / Budgets",
    R: "Fractal: Compression / Replay / Proofs"
  };
  
  export const FacetSemantics: Record<Facet, string> = {
    1: "Objects",
    2: "Laws",
    3: "Constructions",
    4: "Certificates"
  };
  
  export const AtomSemantics: Record<Atom, string> = {
    a: "Definition / Declaration",
    b: "Algorithm / Implementation",
    c: "Verification / Validation",
    d: "Certificate / Proof"
  };
  
  // Convert chapter number to base-4 station code
  export function stationCode(chapter: number): string {
    if (chapter < 1 || chapter > 21) {
      throw new Error(`Invalid chapter number: ${chapter}. Must be 1-21.`);
    }
    const omega = chapter - 1;
    let result = "";
    let n = omega;
    for (let i = 0; i < 4; i++) {
      result = (n % 4).toString() + result;
      n = Math.floor(n / 4);
    }
    return result;
  }
  
  // Parse base-4 station code back to chapter number
  export function parseStationCode(code: string): number {
    if (!/^[0-3]{4}$/.test(code)) {
      throw new Error(`Invalid station code: ${code}`);
    }
    let omega = 0;
    for (let i = 0; i < 4; i++) {
      omega = omega * 4 + parseInt(code[i]);
    }
    return omega + 1;
  }
  
  // Chapter local address
  export interface ChapterAddr {
    kind: "chapter";
    chapter: number;
    code: string;
    lens: Lens;
    facet: Facet;
    atom: Atom;
  }
  
  // Appendix local address
  export interface AppendixAddr {
    kind: "appendix";
    appendix: string;  // A-P
    lens: Lens;
    facet: Facet;
    atom: Atom;
  }
  
  export type LocalAddr = ChapterAddr | AppendixAddr;
  
  // Global address with manuscript ID
  export interface GlobalAddr {
    manuscript: string;
    local: LocalAddr;
  }
  
  // Create chapter address
  export function chapterAddr(chapter: number, lens: Lens, facet: Facet, atom: Atom): ChapterAddr {
    return {
      kind: "chapter",
      chapter,
      code: stationCode(chapter),
      lens,
      facet,
      atom
    };
  }
  
  // Create appendix address
  export function appendixAddr(appendix: string, lens: Lens, facet: Facet, atom: Atom): AppendixAddr {
    if (!/^[A-P]$/.test(appendix)) {
      throw new Error(`Invalid appendix: ${appendix}. Must be A-P.`);
    }
    return {
      kind: "appendix",
      appendix,
      lens,
      facet,
      atom
    };
  }
  
  // Format local address as string
  export function formatLocal(addr: LocalAddr): string {
    if (addr.kind === "chapter") {
      return `Ch${addr.chapter.toString().padStart(2, "0")}⟨${addr.code}⟩.${addr.lens}${addr.facet}.${addr.atom}`;
    } else {
      return `App${addr.appendix}.${addr.lens}${addr.facet}.${addr.atom}`;
    }
  }
  
  // Format global address as string
  export function formatGlobal(addr: GlobalAddr): string {
    return `Ms⟨${addr.manuscript}⟩::${formatLocal(addr.local)}`;
  }
  
  // Parse local address from string
  export function parseLocal(str: string): LocalAddr | null {
    // Chapter pattern: Ch01⟨0000⟩.S1.a
    const chapterMatch = str.match(/^Ch(\d{2})⟨(\d{4})⟩\.([SFCR])([1-4])\.([abcd])$/);
    if (chapterMatch) {
      const chapter = parseInt(chapterMatch[1]);
      const code = chapterMatch[2];
      // Validate code matches chapter
      if (stationCode(chapter) !== code) {
        return null;
      }
      return {
        kind: "chapter",
        chapter,
        code,
        lens: chapterMatch[3] as Lens,
        facet: parseInt(chapterMatch[4]) as Facet,
        atom: chapterMatch[5] as Atom
      };
    }
    
    // Appendix pattern: AppA.S1.a
    const appendixMatch = str.match(/^App([A-P])\.([SFCR])([1-4])\.([abcd])$/);
    if (appendixMatch) {
      return {
        kind: "appendix",
        appendix: appendixMatch[1],
        lens: appendixMatch[2] as Lens,
        facet: parseInt(appendixMatch[3]) as Facet,
        atom: appendixMatch[4] as Atom
      };
    }
    
    return null;
  }
  
  // Parse global address from string
  export function parseGlobal(str: string): GlobalAddr | null {
    const match = str.match(/^Ms⟨([A-Z0-9]{4})⟩::(.+)$/);
    if (!match) return null;
    
    const local = parseLocal(match[2]);
    if (!local) return null;
    
    return {
      manuscript: match[1],
      local
    };
  }
  
  // Generate all 64 atoms for a station (4 lenses × 4 facets × 4 atoms)
  export function* stationAtoms(chapter: number): Generator<ChapterAddr> {
    for (const lens of LENSES) {
      for (const facet of FACETS) {
        for (const atom of ATOMS) {
          yield chapterAddr(chapter, lens, facet, atom);
        }
      }
    }
  }
  
  // Generate all 64 atoms for an appendix
  export function* appendixAtoms(appendix: string): Generator<AppendixAddr> {
    for (const lens of LENSES) {
      for (const facet of FACETS) {
        for (const atom of ATOMS) {
          yield appendixAddr(appendix, lens, facet, atom);
        }
      }
    }
  }
  
  // Compute arc from chapter (0-6)
  export function arc(chapter: number): number {
    return Math.floor((chapter - 1) / 3);
  }
  
  // Compute rotation within arc (0-2)
  export function rotation(chapter: number): number {
    return (chapter - 1) % 3;
  }
  
  // Get rail for chapter
  export function rail(chapter: number): Rail {
    const arcNum = arc(chapter);
    const rotNum = rotation(chapter);
    // Triad rotation pattern
    const triadOrder: Rail[][] = [
      ["Su", "Me", "Sa"],
      ["Me", "Sa", "Su"],
      ["Sa", "Su", "Me"]
    ];
    const rotOffset = arcNum % 3;
    return triadOrder[rotOffset][rotNum];
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: CORRIDOR BUDGETS - Complete Implementation
// ═══════════════════════════════════════════════════════════════════════════════

export namespace Corridors {
  
  export interface Budget {
    kappa_risk: number;       // Risk budget [0, 1]
    kappa_compute: number;    // Compute budget (units)
    kappa_evidence: number;   // Evidence budget (bits)
    kappa_authority: number;  // Authority level [0, 10]
  }
  
  export interface Corridor {
    id: string;
    budgets: Budget;
    constraints: Constraint[];
    active: boolean;
    parentId?: string;
  }
  
  export interface Constraint {
    id: string;
    expression: string;
    type: "equality" | "inequality" | "bound";
    enforced: boolean;
  }
  
  // Default budgets
  export const DEFAULT_BUDGET: Budget = {
    kappa_risk: 0.1,
    kappa_compute: 1000,
    kappa_evidence: 1024,
    kappa_authority: 5
  };
  
  // Check if operation is admissible within budget
  export function isAdmissible(
    required: Partial<Budget>,
    available: Budget
  ): { admissible: boolean; violations: string[] } {
    const violations: string[] = [];
    
    if (required.kappa_risk !== undefined && required.kappa_risk > available.kappa_risk) {
      violations.push(`Risk budget exceeded: need ${required.kappa_risk}, have ${available.kappa_risk}`);
    }
    if (required.kappa_compute !== undefined && required.kappa_compute > available.kappa_compute) {
      violations.push(`Compute budget exceeded: need ${required.kappa_compute}, have ${available.kappa_compute}`);
    }
    if (required.kappa_evidence !== undefined && required.kappa_evidence > available.kappa_evidence) {
      violations.push(`Evidence budget exceeded: need ${required.kappa_evidence}, have ${available.kappa_evidence}`);
    }
    if (required.kappa_authority !== undefined && required.kappa_authority > available.kappa_authority) {
      violations.push(`Authority level insufficient: need ${required.kappa_authority}, have ${available.kappa_authority}`);
    }
    
    return {
      admissible: violations.length === 0,
      violations
    };
  }
  
  // Consume budget and return remaining
  export function consume(available: Budget, spent: Partial<Budget>): Budget {
    return {
      kappa_risk: available.kappa_risk - (spent.kappa_risk ?? 0),
      kappa_compute: available.kappa_compute - (spent.kappa_compute ?? 0),
      kappa_evidence: available.kappa_evidence - (spent.kappa_evidence ?? 0),
      kappa_authority: available.kappa_authority  // Authority doesn't decrease
    };
  }
  
  // κ-conservation check
  export function checkConservation(
    pre: Budget,
    post: Budget,
    spent: Partial<Budget>,
    leak: Partial<Budget>
  ): boolean {
    const computedPost = {
      kappa_risk: pre.kappa_risk - (spent.kappa_risk ?? 0) - (leak.kappa_risk ?? 0),
      kappa_compute: pre.kappa_compute - (spent.kappa_compute ?? 0) - (leak.kappa_compute ?? 0),
      kappa_evidence: pre.kappa_evidence - (spent.kappa_evidence ?? 0) - (leak.kappa_evidence ?? 0),
      kappa_authority: pre.kappa_authority
    };
    
    const epsilon = 1e-10;
    return (
      Math.abs(computedPost.kappa_risk - post.kappa_risk) < epsilon &&
      Math.abs(computedPost.kappa_compute - post.kappa_compute) < epsilon &&
      Math.abs(computedPost.kappa_evidence - post.kappa_evidence) < epsilon
    );
  }
  
  // Create child corridor with reduced budget
  export function createChild(
    parent: Corridor,
    childId: string,
    budgetFraction: number = 0.5
  ): Corridor {
    return {
      id: childId,
      budgets: {
        kappa_risk: parent.budgets.kappa_risk * budgetFraction,
        kappa_compute: parent.budgets.kappa_compute * budgetFraction,
        kappa_evidence: parent.budgets.kappa_evidence * budgetFraction,
        kappa_authority: parent.budgets.kappa_authority
      },
      constraints: [...parent.constraints],
      active: true,
      parentId: parent.id
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: WITNESS SYSTEM - Complete Implementation
// ═══════════════════════════════════════════════════════════════════════════════

export interface WitnessPtr {
  id: string;
  type: "direct" | "derived" | "cross-medium" | "computational";
  sourceRefs: string[];
  timestamp: number;
  digest: string;
  confidence: number;
  chain?: WitnessPtr[];  // Evidence chain
}

export namespace Witnesses {
  
  // Create witness from direct observation
  export function createDirect(
    sourceRefs: string[],
    data: unknown
  ): WitnessPtr {
    const serialized = JSON.stringify(data);
    const digest = computeDigest(serialized);
    
    return {
      id: `wit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: "direct",
      sourceRefs,
      timestamp: Date.now(),
      digest,
      confidence: 1.0
    };
  }
  
  // Create derived witness from other witnesses
  export function createDerived(
    sources: WitnessPtr[],
    derivationRule: string
  ): WitnessPtr {
    const sourceRefs = sources.map(s => s.id);
    const combinedDigest = computeDigest(
      sources.map(s => s.digest).join(":") + ":" + derivationRule
    );
    
    // Confidence is product of source confidences (for independence)
    const confidence = sources.reduce((acc, s) => acc * s.confidence, 1.0);
    
    return {
      id: `wit_derived_${Date.now()}`,
      type: "derived",
      sourceRefs,
      timestamp: Date.now(),
      digest: combinedDigest,
      confidence,
      chain: sources
    };
  }
  
  // Verify witness chain integrity
  export function verifyChain(witness: WitnessPtr): boolean {
    if (!witness.chain || witness.chain.length === 0) {
      return true;  // Direct witness, no chain to verify
    }
    
    // Verify each link in the chain
    for (const link of witness.chain) {
      if (!verifyChain(link)) {
        return false;
      }
    }
    
    // Verify combined digest matches
    const expectedDigest = computeDigest(
      witness.chain.map(s => s.digest).join(":")
    );
    
    // Allow for derivation rule suffix
    return witness.digest.startsWith(expectedDigest.substring(0, 16));
  }
  
  // Compute confidence decay over time
  export function decayedConfidence(
    witness: WitnessPtr,
    halfLifeMs: number = 86400000  // 1 day default
  ): number {
    const age = Date.now() - witness.timestamp;
    const decayFactor = Math.pow(0.5, age / halfLifeMs);
    return witness.confidence * decayFactor;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: REPLAY CAPSULES - Complete Implementation
// ═══════════════════════════════════════════════════════════════════════════════

export interface ReplayCapsule {
  id: string;
  version: string;
  target: string;  // Address being certified
  inputs: Record<string, unknown>;
  outputs: Record<string, unknown>;
  steps: ReplayStep[];
  seal: CapsuleSeal;
}

export interface ReplayStep {
  index: number;
  operation: string;
  input: unknown;
  output: unknown;
  duration_us: number;
}

export interface CapsuleSeal {
  algorithm: "SHA256" | "SHA512";
  payloadDigest: string;
  timestamp: number;
  signer?: string;
}

export namespace ReplayCapsules {
  
  // Create replay capsule
  export function create(
    target: string,
    inputs: Record<string, unknown>,
    executor: (inputs: Record<string, unknown>) => { outputs: Record<string, unknown>; steps: ReplayStep[] }
  ): ReplayCapsule {
    const { outputs, steps } = executor(inputs);
    
    const capsule: Omit<ReplayCapsule, "seal"> = {
      id: `replay_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      version: "1.0.0",
      target,
      inputs,
      outputs,
      steps
    };
    
    const seal: CapsuleSeal = {
      algorithm: "SHA256",
      payloadDigest: computeDigest(JSON.stringify(capsule)),
      timestamp: Date.now()
    };
    
    return { ...capsule, seal };
  }
  
  // Verify replay capsule
  export function verify(capsule: ReplayCapsule): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    // Verify seal
    const capsuleWithoutSeal = { ...capsule };
    delete (capsuleWithoutSeal as any).seal;
    const computedDigest = computeDigest(JSON.stringify(capsuleWithoutSeal));
    
    if (computedDigest !== capsule.seal.payloadDigest) {
      errors.push("Seal digest mismatch");
    }
    
    // Verify steps are sequential
    for (let i = 0; i < capsule.steps.length; i++) {
      if (capsule.steps[i].index !== i) {
        errors.push(`Step index mismatch at position ${i}`);
      }
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }
  
  // Replay execution
  export function replay(
    capsule: ReplayCapsule,
    executor: (op: string, input: unknown) => unknown
  ): { success: boolean; divergence?: { step: number; expected: unknown; actual: unknown } } {
    for (const step of capsule.steps) {
      const actual = executor(step.operation, step.input);
      
      if (JSON.stringify(actual) !== JSON.stringify(step.output)) {
        return {
          success: false,
          divergence: {
            step: step.index,
            expected: step.output,
            actual
          }
        };
      }
    }
    
    return { success: true };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: RESIDUAL LEDGER & EVIDENCE PLANS
// ═══════════════════════════════════════════════════════════════════════════════

export interface ResidualLedger {
  id: string;
  entries: ResidualEntry[];
  totalMass: number;
}

export interface ResidualEntry {
  id: string;
  type: "obligation" | "debt" | "pending" | "unknown";
  description: string;
  mass: number;
  deadline?: number;
  upgradePath?: string;
}

export interface EvidencePlan {
  id: string;
  goal: string;
  steps: EvidenceStep[];
  estimatedCost: Partial<Corridors.Budget>;
  deadline?: number;
}

export interface EvidenceStep {
  index: number;
  action: string;
  expectedEvidence: string;
  required: boolean;
}

export interface QuarantineRecord {
  id: string;
  reason: string;
  containedAt: number;
  conflictWitnesses: WitnessPtr[];
  rollbackPointer?: string;
  minimalWitnessSet: string[];
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 8: CRYPTOGRAPHIC UTILITIES
// ═══════════════════════════════════════════════════════════════════════════════

export function computeDigest(data: string, algorithm: "SHA256" | "SHA512" = "SHA256"): string {
  // In browser/Node environment
  if (typeof crypto !== 'undefined' && crypto.createHash) {
    return crypto.createHash(algorithm.toLowerCase()).update(data).digest('hex');
  }
  
  // Fallback: simple hash for demonstration
  let hash = 0;
  for (let i = 0; i < data.length; i++) {
    const char = data.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(16).padStart(16, '0');
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 9: LINK EDGE SCHEMA - Complete Implementation
// ═══════════════════════════════════════════════════════════════════════════════

export interface LinkEdge {
  edgeId: string;
  kind: EdgeKind;
  source: string;  // GlobalAddr string
  destination: string;  // GlobalAddr string
  scope: EdgeScope;
  corridor: string;  // Corridor ID
  witnessPtr?: WitnessPtr;
  replayPtr?: ReplayCapsule;
  payload?: Record<string, unknown>;
  version: number;
  createdAt: number;
  truth: TruthValue;
}

export type EdgeScope = "local" | "tome" | "global";

export namespace LinkEdges {
  
  // Create a new edge
  export function create(
    kind: EdgeKind,
    source: string,
    destination: string,
    corridor: string,
    options: {
      scope?: EdgeScope;
      witness?: WitnessPtr;
      replay?: ReplayCapsule;
      payload?: Record<string, unknown>;
    } = {}
  ): LinkEdge {
    return {
      edgeId: `edge_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      kind,
      source,
      destination,
      scope: options.scope ?? "local",
      corridor,
      witnessPtr: options.witness,
      replayPtr: options.replay,
      payload: options.payload,
      version: 1,
      createdAt: Date.now(),
      truth: options.witness && options.replay ? TruthValue.OK : TruthValue.NEAR
    };
  }
  
  // Check edge well-formedness
  export function validate(edge: LinkEdge): ValidationResult {
    const errors: string[] = [];
    
    // Check source and destination are valid addresses
    if (!Addressing.parseGlobal(edge.source)) {
      errors.push(`Invalid source address: ${edge.source}`);
    }
    if (!Addressing.parseGlobal(edge.destination)) {
      errors.push(`Invalid destination address: ${edge.destination}`);
    }
    
    // Check witness if truth is OK
    if (edge.truth === TruthValue.OK && !edge.witnessPtr) {
      errors.push("OK truth requires witness");
    }
    if (edge.truth === TruthValue.OK && !edge.replayPtr) {
      errors.push("OK truth requires replay capsule");
    }
    
    // Check symmetric edges have matching inverse
    const props = EdgeAlgebra.Properties[edge.kind];
    if (props.symmetric && edge.source !== edge.destination) {
      // Symmetric edges should have both directions
      // (This would be checked at graph level)
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }
  
  // Compose edges if possible
  export function compose(e1: LinkEdge, e2: LinkEdge): LinkEdge | null {
    // e1.destination must equal e2.source
    if (e1.destination !== e2.source) {
      return null;
    }
    
    const composedKind = EdgeAlgebra.compose(e1.kind, e2.kind);
    if (!composedKind) {
      return null;
    }
    
    // Compose witnesses if both exist
    let composedWitness: WitnessPtr | undefined;
    if (e1.witnessPtr && e2.witnessPtr) {
      composedWitness = Witnesses.createDerived(
        [e1.witnessPtr, e2.witnessPtr],
        `compose(${e1.kind}, ${e2.kind})`
      );
    }
    
    return create(
      composedKind,
      e1.source,
      e2.destination,
      e1.corridor,
      {
        scope: e1.scope === "global" || e2.scope === "global" ? "global" : 
               e1.scope === "tome" || e2.scope === "tome" ? "tome" : "local",
        witness: composedWitness,
        payload: { composed: true, from: [e1.edgeId, e2.edgeId] }
      }
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 10: ROUTER - Hub Selection & Path Computation
// ═══════════════════════════════════════════════════════════════════════════════

export namespace Router {
  
  // Mandatory router signature (never dropped)
  export const SIGMA: string[] = ["AppA", "AppI", "AppM"];
  
  // Arc hubs
  export const ARC_HUBS: Record<number, string> = {
    0: "AppA",
    1: "AppC",
    2: "AppE",
    3: "AppF",
    4: "AppG",
    5: "AppN",
    6: "AppP"
  };
  
  // Lens bases
  export const LENS_BASES: Record<Lens, string> = {
    S: "AppC",
    F: "AppE",
    C: "AppI",
    R: "AppM"
  };
  
  // Facet bases
  export const FACET_BASES: Record<Facet, string> = {
    1: "AppA",
    2: "AppB",
    3: "AppH",
    4: "AppM"
  };
  
  // Truth overlay hubs
  export const TRUTH_OVERLAYS: Record<TruthValue, string | null> = {
    [TruthValue.OK]: "AppO",
    [TruthValue.NEAR]: "AppJ",
    [TruthValue.AMBIG]: "AppL",
    [TruthValue.FAIL]: "AppK"
  };
  
  // Compute route hubs for a target address
  export function computeRoute(
    target: Addressing.LocalAddr,
    truth: TruthValue,
    publishIntent: boolean = false
  ): string[] {
    const hubs: string[] = [];
    
    // P0: Mandatory signature (always included)
    hubs.push(...SIGMA);
    
    // P1: Arc hub
    if (target.kind === "chapter") {
      const arcNum = Addressing.arc(target.chapter);
      const arcHub = ARC_HUBS[arcNum];
      if (arcHub && !hubs.includes(arcHub)) {
        hubs.push(arcHub);
      }
    }
    
    // P2: Lens base
    const lensHub = LENS_BASES[target.lens];
    if (!hubs.includes(lensHub)) {
      hubs.push(lensHub);
    }
    
    // P3: Facet base (optional, may be pruned)
    const facetHub = FACET_BASES[target.facet];
    
    // P4: Truth overlay (if needed)
    const overlayHub = TRUTH_OVERLAYS[truth];
    if (overlayHub && publishIntent && truth === TruthValue.OK) {
      if (!hubs.includes(overlayHub)) {
        hubs.push(overlayHub);
      }
    } else if (overlayHub && truth !== TruthValue.OK) {
      if (!hubs.includes(overlayHub)) {
        hubs.push(overlayHub);
      }
    }
    
    // Prune to budget ≤ 6
    if (hubs.length <= 6) {
      // Can include facet hub
      if (!hubs.includes(facetHub) && hubs.length < 6) {
        hubs.push(facetHub);
      }
    }
    
    // Final prune if still over budget
    while (hubs.length > 6) {
      // Remove from end, but never remove SIGMA
      const toRemove = hubs.findIndex((h, i) => i >= 3);
      if (toRemove >= 0) {
        hubs.splice(toRemove, 1);
      } else {
        break;
      }
    }
    
    return hubs;
  }
  
  // Format route as string
  export function formatRoute(
    manuscript: string,
    hubs: string[],
    target: Addressing.LocalAddr
  ): string {
    const hubPath = hubs.join(" → ");
    const targetStr = Addressing.formatLocal(target);
    return `Ms⟨${manuscript}⟩::${hubPath} → ${targetStr}`;
  }
  
  // Validate route budget
  export function validateRoute(hubs: string[]): ValidationResult {
    const errors: string[] = [];
    
    if (hubs.length > 6) {
      errors.push(`Hub budget exceeded: ${hubs.length} > 6`);
    }
    
    // Check SIGMA is present
    for (const required of SIGMA) {
      if (!hubs.includes(required)) {
        errors.push(`Missing required hub: ${required}`);
      }
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 11: RUNTIME LOOP
// ═══════════════════════════════════════════════════════════════════════════════

export namespace Runtime {
  
  export type Phase = "rotate" | "nullify" | "jump" | "spin" | "collapse" | "ledger";
  
  export interface ExecutionContext {
    address: Addressing.GlobalAddr;
    corridor: Corridors.Corridor;
    inputs: Record<string, unknown>;
    state: Record<string, unknown>;
    phase: Phase;
    truth: TruthValue;
    witnesses: WitnessPtr[];
    ledgerEntries: string[];
  }
  
  export interface PhaseResult {
    success: boolean;
    output?: unknown;
    newState?: Record<string, unknown>;
    newTruth?: TruthValue;
    witness?: WitnessPtr;
    error?: string;
  }
  
  // Execute full runtime loop
  export function execute(
    address: Addressing.GlobalAddr,
    corridor: Corridors.Corridor,
    inputs: Record<string, unknown>,
    handlers: {
      rotate: (ctx: ExecutionContext) => PhaseResult;
      nullify: (ctx: ExecutionContext) => PhaseResult;
      jump: (ctx: ExecutionContext) => PhaseResult;
      spin: (ctx: ExecutionContext) => PhaseResult;
      collapse: (ctx: ExecutionContext) => PhaseResult;
      ledger: (ctx: ExecutionContext) => PhaseResult;
    }
  ): { verdict: TruthLattice.Verdict; capsule: ReplayCapsule } {
    const ctx: ExecutionContext = {
      address,
      corridor,
      inputs,
      state: {},
      phase: "rotate",
      truth: TruthValue.NEAR,
      witnesses: [],
      ledgerEntries: []
    };
    
    const steps: ReplayStep[] = [];
    const phases: Phase[] = ["rotate", "nullify", "jump", "spin", "collapse", "ledger"];
    
    for (let i = 0; i < phases.length; i++) {
      ctx.phase = phases[i];
      const startTime = performance.now();
      
      const result = handlers[ctx.phase](ctx);
      
      const endTime = performance.now();
      
      steps.push({
        index: i,
        operation: ctx.phase,
        input: { ...ctx.state },
        output: result.output,
        duration_us: (endTime - startTime) * 1000
      });
      
      if (!result.success) {
        ctx.truth = TruthValue.FAIL;
        break;
      }
      
      if (result.newState) {
        ctx.state = { ...ctx.state, ...result.newState };
      }
      if (result.newTruth !== undefined) {
        ctx.truth = result.newTruth;
      }
      if (result.witness) {
        ctx.witnesses.push(result.witness);
      }
    }
    
    // Create verdict
    const verdict: TruthLattice.Verdict = {
      value: ctx.truth,
      witness: ctx.witnesses.length > 0 ? 
        Witnesses.createDerived(ctx.witnesses, "execution") : undefined
    };
    
    // Create replay capsule
    const capsule = ReplayCapsules.create(
      Addressing.formatGlobal(address),
      inputs,
      () => ({ outputs: ctx.state, steps })
    );
    
    verdict.replay = capsule;
    
    return { verdict, capsule };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  TruthValue,
  TruthLattice,
  EdgeKind,
  EdgeAlgebra,
  Addressing,
  Corridors,
  Witnesses,
  ReplayCapsules,
  LinkEdges,
  Router,
  Runtime,
  computeDigest
};
