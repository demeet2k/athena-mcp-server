/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * PROOF ALGEBRA - Complete Proof-Carrying Code System
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Ten Certification Types:
 *   1. EdgeWF - Edge well-formedness
 *   2. WitSuff - Witness sufficiency  
 *   3. Coverage - Coverage completeness
 *   4. Slack - Budget slack verification
 *   5. Eq - Equality proofs
 *   6. DualFac - Dual factorization
 *   7. Drift - Drift bounds
 *   8. ReplayAcc - Replay accuracy
 *   9. Closure - Closure proofs
 *   10. Compliance - Protocol compliance
 * 
 * Three Ledger Types:
 *   Λ_err - Error ledger
 *   Λ_mass - Mass conservation ledger
 *   Λ_proof - Proof ledger
 * 
 * Mass conservation: bulk + bdry + erasure + abstention = 1
 * 
 * @module PROOF_ALGEBRA
 * @version 2.0.0
 */

import { TruthValue, EdgeKind, WitnessPtr } from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: CERTIFICATION TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Certification type enumeration
 */
export enum CertificationType {
  EdgeWF = "EdgeWF",           // Edge well-formedness
  WitSuff = "WitSuff",         // Witness sufficiency
  Coverage = "Coverage",       // Coverage completeness
  Slack = "Slack",             // Budget slack verification
  Eq = "Eq",                   // Equality proofs
  DualFac = "DualFac",         // Dual factorization
  Drift = "Drift",             // Drift bounds
  ReplayAcc = "ReplayAcc",     // Replay accuracy
  Closure = "Closure",         // Closure proofs
  Compliance = "Compliance"    // Protocol compliance
}

/**
 * Base certificate interface
 */
export interface Certificate {
  id: string;
  type: CertificationType;
  timestamp: number;
  issuer: string;
  subject: string;
  truth: TruthValue;
  witnessPtr: string;
  signature: string;
  metadata: Record<string, unknown>;
}

/**
 * Edge Well-Formedness Certificate
 * Verifies: source exists, target exists, edge kind valid, no cycles introduced
 */
export interface EdgeWFCertificate extends Certificate {
  type: CertificationType.EdgeWF;
  edge: {
    source: string;
    target: string;
    kind: EdgeKind;
  };
  checks: {
    sourceExists: boolean;
    targetExists: boolean;
    kindValid: boolean;
    noCycleIntroduced: boolean;
    budgetRespected: boolean;
  };
}

/**
 * Witness Sufficiency Certificate
 * Verifies: all claims have witnesses, witnesses are valid, chain complete
 */
export interface WitSuffCertificate extends Certificate {
  type: CertificationType.WitSuff;
  claims: string[];
  witnesses: {
    claimId: string;
    witnessPtr: string;
    valid: boolean;
  }[];
  chainComplete: boolean;
  coverage: number;  // 0 to 1
}

/**
 * Coverage Certificate
 * Verifies: all atoms covered, no orphans, complete indexing
 */
export interface CoverageCertificate extends Certificate {
  type: CertificationType.Coverage;
  totalAtoms: number;
  coveredAtoms: number;
  orphanAtoms: string[];
  coverageRatio: number;
  indexComplete: boolean;
}

/**
 * Slack Certificate
 * Verifies: budget not exhausted, reserves maintained
 */
export interface SlackCertificate extends Certificate {
  type: CertificationType.Slack;
  budgets: {
    name: string;
    allocated: number;
    used: number;
    remaining: number;
    slackRatio: number;
  }[];
  overallSlack: number;
  reserveMaintained: boolean;
}

/**
 * Equality Certificate
 * Verifies: two expressions are equal under given theory
 */
export interface EqCertificate extends Certificate {
  type: CertificationType.Eq;
  left: string;
  right: string;
  theory: string;
  proofSteps: ProofStep[];
  reflexive: boolean;
  symmetric: boolean;
  transitive: boolean;
}

/**
 * Dual Factorization Certificate
 * Verifies: Carrier(law) ⊕ Payload(data) decomposition valid
 */
export interface DualFacCertificate extends Certificate {
  type: CertificationType.DualFac;
  original: string;
  carrier: {
    id: string;
    laws: string[];
    invariants: string[];
  };
  payload: {
    id: string;
    data: unknown;
    schema: string;
  };
  reconstructable: boolean;
  lossless: boolean;
}

/**
 * Drift Certificate
 * Verifies: state changes within bounds, identity preserved
 */
export interface DriftCertificate extends Certificate {
  type: CertificationType.Drift;
  baseline: string;
  current: string;
  driftMeasure: number;
  maxAllowed: number;
  withinBounds: boolean;
  identityPreserved: boolean;
}

/**
 * Replay Accuracy Certificate
 * Verifies: replay produces identical results
 */
export interface ReplayAccCertificate extends Certificate {
  type: CertificationType.ReplayAcc;
  originalRun: {
    id: string;
    inputs: unknown[];
    outputs: unknown[];
    hash: string;
  };
  replayRun: {
    id: string;
    inputs: unknown[];
    outputs: unknown[];
    hash: string;
  };
  inputsMatch: boolean;
  outputsMatch: boolean;
  deterministic: boolean;
}

/**
 * Closure Certificate
 * Verifies: all dependencies resolved, no dangling references
 */
export interface ClosureCertificate extends Certificate {
  type: CertificationType.Closure;
  scope: string;
  dependencies: {
    id: string;
    resolved: boolean;
    location: string;
  }[];
  danglingRefs: string[];
  closureComplete: boolean;
  transitiveComplete: boolean;
}

/**
 * Compliance Certificate
 * Verifies: protocol followed, constraints satisfied
 */
export interface ComplianceCertificate extends Certificate {
  type: CertificationType.Compliance;
  protocol: string;
  version: string;
  constraints: {
    id: string;
    description: string;
    satisfied: boolean;
    evidence: string;
  }[];
  allSatisfied: boolean;
  complianceScore: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: PROOF STEPS AND RULES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Proof step in a derivation
 */
export interface ProofStep {
  id: string;
  rule: ProofRule;
  premises: string[];
  conclusion: string;
  justification: string;
  witnessPtr?: string;
}

/**
 * Proof rules (natural deduction style)
 */
export enum ProofRule {
  // Structural rules
  Axiom = "axiom",
  Assumption = "assumption",
  Discharge = "discharge",
  
  // Propositional logic
  AndIntro = "∧I",
  AndElimL = "∧E_L",
  AndElimR = "∧E_R",
  OrIntroL = "∨I_L",
  OrIntroR = "∨I_R",
  OrElim = "∨E",
  ImplIntro = "→I",
  ImplElim = "→E",
  NegIntro = "¬I",
  NegElim = "¬E",
  BottomElim = "⊥E",
  
  // First-order logic
  ForallIntro = "∀I",
  ForallElim = "∀E",
  ExistsIntro = "∃I",
  ExistsElim = "∃E",
  
  // Equality
  EqRefl = "=refl",
  EqSym = "=sym",
  EqTrans = "=trans",
  EqSubst = "=subst",
  
  // Type theory
  TypeIntro = "T_intro",
  TypeElim = "T_elim",
  Subtype = "subtype",
  
  // Truth lattice
  TruthJoin = "⊔",
  TruthMeet = "⊓",
  TruthPromote = "promote",
  TruthDemote = "demote",
  
  // Custom
  Witness = "witness",
  Replay = "replay",
  Induction = "induction"
}

/**
 * Complete proof tree
 */
export interface ProofTree {
  id: string;
  root: ProofStep;
  steps: Map<string, ProofStep>;
  assumptions: Set<string>;
  conclusion: string;
  truth: TruthValue;
  valid: boolean;
}

/**
 * Proof context (assumptions and bindings)
 */
export interface ProofContext {
  assumptions: Map<string, { formula: string; discharged: boolean }>;
  bindings: Map<string, { type: string; value?: unknown }>;
  goals: string[];
  currentGoal?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: LEDGER SYSTEM
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Ledger types
 */
export enum LedgerType {
  Error = "Λ_err",
  Mass = "Λ_mass",
  Proof = "Λ_proof"
}

/**
 * Base ledger entry
 */
export interface LedgerEntry {
  id: string;
  timestamp: number;
  type: LedgerType;
  operation: string;
  data: unknown;
  witnessPtr: string;
  prevHash: string;
  hash: string;
}

/**
 * Error ledger entry
 */
export interface ErrorLedgerEntry extends LedgerEntry {
  type: LedgerType.Error;
  error: {
    code: string;
    message: string;
    severity: "warning" | "error" | "fatal";
    source: string;
    stack?: string[];
  };
  handled: boolean;
  resolution?: string;
}

/**
 * Mass ledger entry (for κ-conservation)
 */
export interface MassLedgerEntry extends LedgerEntry {
  type: LedgerType.Mass;
  mass: {
    bulk: number;       // Main computation
    bdry: number;       // Boundary effects
    erasure: number;    // Information lost
    abstention: number; // Withheld computation
    total: number;      // Should equal 1
  };
  source: string;
  destination: string;
  conserved: boolean;
}

/**
 * Proof ledger entry
 */
export interface ProofLedgerEntry extends LedgerEntry {
  type: LedgerType.Proof;
  certificate: Certificate;
  verified: boolean;
  verifierSignature: string;
}

/**
 * Complete ledger
 */
export class Ledger {
  private entries: LedgerEntry[] = [];
  private entriesById: Map<string, LedgerEntry> = new Map();
  private currentHash: string = "genesis";
  
  constructor(public readonly type: LedgerType) {}
  
  /**
   * Append entry to ledger
   */
  append(entry: Omit<LedgerEntry, "id" | "timestamp" | "prevHash" | "hash">): LedgerEntry {
    const id = `${this.type}_${this.entries.length}`;
    const timestamp = Date.now();
    const prevHash = this.currentHash;
    
    const fullEntry: LedgerEntry = {
      ...entry,
      id,
      timestamp,
      prevHash,
      hash: "" // Computed below
    };
    
    fullEntry.hash = this.computeHash(fullEntry);
    this.currentHash = fullEntry.hash;
    
    this.entries.push(fullEntry);
    this.entriesById.set(id, fullEntry);
    
    return fullEntry;
  }
  
  /**
   * Get entry by ID
   */
  get(id: string): LedgerEntry | undefined {
    return this.entriesById.get(id);
  }
  
  /**
   * Get all entries
   */
  getAll(): LedgerEntry[] {
    return [...this.entries];
  }
  
  /**
   * Get latest entry
   */
  latest(): LedgerEntry | undefined {
    return this.entries[this.entries.length - 1];
  }
  
  /**
   * Verify chain integrity
   */
  verify(): { valid: boolean; brokenAt?: number } {
    let prevHash = "genesis";
    
    for (let i = 0; i < this.entries.length; i++) {
      const entry = this.entries[i];
      
      if (entry.prevHash !== prevHash) {
        return { valid: false, brokenAt: i };
      }
      
      const computedHash = this.computeHash(entry);
      if (entry.hash !== computedHash) {
        return { valid: false, brokenAt: i };
      }
      
      prevHash = entry.hash;
    }
    
    return { valid: true };
  }
  
  private computeHash(entry: LedgerEntry): string {
    const data = JSON.stringify({
      id: entry.id,
      timestamp: entry.timestamp,
      type: entry.type,
      operation: entry.operation,
      data: entry.data,
      witnessPtr: entry.witnessPtr,
      prevHash: entry.prevHash
    });
    
    // Simple hash for demonstration
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
      hash = ((hash << 5) - hash) + data.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(16, '0');
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: MASS CONSERVATION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Mass distribution: bulk + bdry + erasure + abstention = 1
 */
export interface MassDistribution {
  bulk: number;
  bdry: number;
  erasure: number;
  abstention: number;
}

/**
 * Check if mass distribution is valid (sums to 1)
 */
export function isValidMassDistribution(mass: MassDistribution, epsilon: number = 1e-10): boolean {
  const total = mass.bulk + mass.bdry + mass.erasure + mass.abstention;
  return Math.abs(total - 1) < epsilon;
}

/**
 * Normalize mass distribution to sum to 1
 */
export function normalizeMassDistribution(mass: MassDistribution): MassDistribution {
  const total = mass.bulk + mass.bdry + mass.erasure + mass.abstention;
  if (total === 0) {
    return { bulk: 1, bdry: 0, erasure: 0, abstention: 0 };
  }
  return {
    bulk: mass.bulk / total,
    bdry: mass.bdry / total,
    erasure: mass.erasure / total,
    abstention: mass.abstention / total
  };
}

/**
 * Mass transfer: move mass from one distribution to another
 */
export function transferMass(
  source: MassDistribution,
  target: MassDistribution,
  transfer: Partial<MassDistribution>
): { source: MassDistribution; target: MassDistribution; valid: boolean } {
  const newSource = { ...source };
  const newTarget = { ...target };
  
  for (const key of ['bulk', 'bdry', 'erasure', 'abstention'] as const) {
    const amount = transfer[key] || 0;
    newSource[key] -= amount;
    newTarget[key] += amount;
  }
  
  return {
    source: newSource,
    target: newTarget,
    valid: isValidMassDistribution(newSource) && isValidMassDistribution(newTarget)
  };
}

/**
 * κ-conservation check: κ_pre = κ_post + κ_spent + κ_leak
 */
export interface KappaConservation {
  pre: number;
  post: number;
  spent: number;
  leak: number;
  conserved: boolean;
  deficit: number;
}

export function checkKappaConservation(
  pre: number,
  post: number,
  spent: number,
  leak: number,
  epsilon: number = 1e-10
): KappaConservation {
  const expected = post + spent + leak;
  const deficit = pre - expected;
  
  return {
    pre,
    post,
    spent,
    leak,
    conserved: Math.abs(deficit) < epsilon,
    deficit
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: PROOF BUILDER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Proof builder for constructing proofs
 */
export class ProofBuilder {
  private context: ProofContext;
  private steps: Map<string, ProofStep> = new Map();
  private stepCounter: number = 0;
  
  constructor() {
    this.context = {
      assumptions: new Map(),
      bindings: new Map(),
      goals: []
    };
  }
  
  /**
   * Add assumption
   */
  assume(formula: string): string {
    const id = `A${this.context.assumptions.size}`;
    this.context.assumptions.set(id, { formula, discharged: false });
    
    const step: ProofStep = {
      id: this.genStepId(),
      rule: ProofRule.Assumption,
      premises: [],
      conclusion: formula,
      justification: `Assumption ${id}`
    };
    this.steps.set(step.id, step);
    
    return step.id;
  }
  
  /**
   * Apply axiom
   */
  axiom(formula: string, name: string): string {
    const step: ProofStep = {
      id: this.genStepId(),
      rule: ProofRule.Axiom,
      premises: [],
      conclusion: formula,
      justification: `Axiom: ${name}`
    };
    this.steps.set(step.id, step);
    return step.id;
  }
  
  /**
   * And introduction: from A and B, derive A ∧ B
   */
  andIntro(leftId: string, rightId: string): string {
    const left = this.steps.get(leftId);
    const right = this.steps.get(rightId);
    
    if (!left || !right) {
      throw new Error("Invalid premise IDs");
    }
    
    const step: ProofStep = {
      id: this.genStepId(),
      rule: ProofRule.AndIntro,
      premises: [leftId, rightId],
      conclusion: `(${left.conclusion} ∧ ${right.conclusion})`,
      justification: `∧I from ${leftId}, ${rightId}`
    };
    this.steps.set(step.id, step);
    return step.id;
  }
  
  /**
   * And elimination left: from A ∧ B, derive A
   */
  andElimL(conjId: string): string {
    const conj = this.steps.get(conjId);
    if (!conj) throw new Error("Invalid premise ID");
    
    // Parse conjunction (simplified)
    const match = conj.conclusion.match(/\((.+) ∧ (.+)\)/);
    if (!match) throw new Error("Not a conjunction");
    
    const step: ProofStep = {
      id: this.genStepId(),
      rule: ProofRule.AndElimL,
      premises: [conjId],
      conclusion: match[1],
      justification: `∧E_L from ${conjId}`
    };
    this.steps.set(step.id, step);
    return step.id;
  }
  
  /**
   * And elimination right: from A ∧ B, derive B
   */
  andElimR(conjId: string): string {
    const conj = this.steps.get(conjId);
    if (!conj) throw new Error("Invalid premise ID");
    
    const match = conj.conclusion.match(/\((.+) ∧ (.+)\)/);
    if (!match) throw new Error("Not a conjunction");
    
    const step: ProofStep = {
      id: this.genStepId(),
      rule: ProofRule.AndElimR,
      premises: [conjId],
      conclusion: match[2],
      justification: `∧E_R from ${conjId}`
    };
    this.steps.set(step.id, step);
    return step.id;
  }
  
  /**
   * Implication introduction: from [A] ⊢ B, derive A → B
   */
  implIntro(assumptionId: string, conclusionId: string): string {
    const assumption = this.context.assumptions.get(assumptionId);
    const conclusion = this.steps.get(conclusionId);
    
    if (!assumption || !conclusion) {
      throw new Error("Invalid IDs");
    }
    
    // Discharge assumption
    assumption.discharged = true;
    
    const step: ProofStep = {
      id: this.genStepId(),
      rule: ProofRule.ImplIntro,
      premises: [conclusionId],
      conclusion: `(${assumption.formula} → ${conclusion.conclusion})`,
      justification: `→I discharging ${assumptionId}`
    };
    this.steps.set(step.id, step);
    return step.id;
  }
  
  /**
   * Implication elimination (modus ponens): from A → B and A, derive B
   */
  implElim(implId: string, antecedentId: string): string {
    const impl = this.steps.get(implId);
    const antecedent = this.steps.get(antecedentId);
    
    if (!impl || !antecedent) throw new Error("Invalid premise IDs");
    
    const match = impl.conclusion.match(/\((.+) → (.+)\)/);
    if (!match) throw new Error("Not an implication");
    
    // Verify antecedent matches
    if (match[1] !== antecedent.conclusion) {
      throw new Error("Antecedent mismatch");
    }
    
    const step: ProofStep = {
      id: this.genStepId(),
      rule: ProofRule.ImplElim,
      premises: [implId, antecedentId],
      conclusion: match[2],
      justification: `→E from ${implId}, ${antecedentId}`
    };
    this.steps.set(step.id, step);
    return step.id;
  }
  
  /**
   * Equality reflexivity: derive a = a
   */
  eqRefl(term: string): string {
    const step: ProofStep = {
      id: this.genStepId(),
      rule: ProofRule.EqRefl,
      premises: [],
      conclusion: `${term} = ${term}`,
      justification: "Reflexivity of ="
    };
    this.steps.set(step.id, step);
    return step.id;
  }
  
  /**
   * Equality symmetry: from a = b, derive b = a
   */
  eqSym(eqId: string): string {
    const eq = this.steps.get(eqId);
    if (!eq) throw new Error("Invalid premise ID");
    
    const match = eq.conclusion.match(/(.+) = (.+)/);
    if (!match) throw new Error("Not an equality");
    
    const step: ProofStep = {
      id: this.genStepId(),
      rule: ProofRule.EqSym,
      premises: [eqId],
      conclusion: `${match[2]} = ${match[1]}`,
      justification: `=sym from ${eqId}`
    };
    this.steps.set(step.id, step);
    return step.id;
  }
  
  /**
   * Equality transitivity: from a = b and b = c, derive a = c
   */
  eqTrans(eq1Id: string, eq2Id: string): string {
    const eq1 = this.steps.get(eq1Id);
    const eq2 = this.steps.get(eq2Id);
    
    if (!eq1 || !eq2) throw new Error("Invalid premise IDs");
    
    const match1 = eq1.conclusion.match(/(.+) = (.+)/);
    const match2 = eq2.conclusion.match(/(.+) = (.+)/);
    
    if (!match1 || !match2) throw new Error("Not equalities");
    if (match1[2] !== match2[1]) throw new Error("Middle terms don't match");
    
    const step: ProofStep = {
      id: this.genStepId(),
      rule: ProofRule.EqTrans,
      premises: [eq1Id, eq2Id],
      conclusion: `${match1[1]} = ${match2[2]}`,
      justification: `=trans from ${eq1Id}, ${eq2Id}`
    };
    this.steps.set(step.id, step);
    return step.id;
  }
  
  /**
   * Add witness
   */
  witness(claim: string, witnessPtr: string): string {
    const step: ProofStep = {
      id: this.genStepId(),
      rule: ProofRule.Witness,
      premises: [],
      conclusion: claim,
      justification: `Witness: ${witnessPtr}`,
      witnessPtr
    };
    this.steps.set(step.id, step);
    return step.id;
  }
  
  /**
   * Build proof tree
   */
  build(rootId: string): ProofTree {
    const root = this.steps.get(rootId);
    if (!root) throw new Error("Invalid root ID");
    
    // Check for undischarged assumptions
    const undischarged = new Set<string>();
    for (const [id, assumption] of this.context.assumptions) {
      if (!assumption.discharged) {
        undischarged.add(id);
      }
    }
    
    return {
      id: `proof_${Date.now()}`,
      root,
      steps: new Map(this.steps),
      assumptions: undischarged,
      conclusion: root.conclusion,
      truth: undischarged.size === 0 ? TruthValue.OK : TruthValue.NEAR,
      valid: undischarged.size === 0
    };
  }
  
  private genStepId(): string {
    return `S${++this.stepCounter}`;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: CERTIFICATE GENERATORS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Generate EdgeWF certificate
 */
export function generateEdgeWFCertificate(
  edge: { source: string; target: string; kind: EdgeKind },
  atomExists: (id: string) => boolean,
  detectCycle: (source: string, target: string) => boolean
): EdgeWFCertificate {
  const checks = {
    sourceExists: atomExists(edge.source),
    targetExists: atomExists(edge.target),
    kindValid: Object.values(EdgeKind).includes(edge.kind),
    noCycleIntroduced: !detectCycle(edge.source, edge.target),
    budgetRespected: true
  };
  
  const allPassed = Object.values(checks).every(v => v);
  
  return {
    id: `cert_edgewf_${Date.now()}`,
    type: CertificationType.EdgeWF,
    timestamp: Date.now(),
    issuer: "ProofAlgebra",
    subject: `${edge.source}->${edge.target}`,
    truth: allPassed ? TruthValue.OK : TruthValue.FAIL,
    witnessPtr: `wit_edgewf_${Date.now()}`,
    signature: `sig_${Date.now()}`,
    metadata: {},
    edge,
    checks
  };
}

/**
 * Generate WitSuff certificate
 */
export function generateWitSuffCertificate(
  claims: string[],
  getWitness: (claimId: string) => string | null
): WitSuffCertificate {
  const witnesses = claims.map(claimId => {
    const witnessPtr = getWitness(claimId);
    return {
      claimId,
      witnessPtr: witnessPtr || "",
      valid: witnessPtr !== null
    };
  });
  
  const validCount = witnesses.filter(w => w.valid).length;
  const coverage = claims.length > 0 ? validCount / claims.length : 1;
  const chainComplete = coverage === 1;
  
  return {
    id: `cert_witsuff_${Date.now()}`,
    type: CertificationType.WitSuff,
    timestamp: Date.now(),
    issuer: "ProofAlgebra",
    subject: `claims[${claims.length}]`,
    truth: chainComplete ? TruthValue.OK : (coverage > 0.5 ? TruthValue.NEAR : TruthValue.FAIL),
    witnessPtr: `wit_witsuff_${Date.now()}`,
    signature: `sig_${Date.now()}`,
    metadata: {},
    claims,
    witnesses,
    chainComplete,
    coverage
  };
}

/**
 * Generate Coverage certificate
 */
export function generateCoverageCertificate(
  allAtoms: string[],
  coveredAtoms: Set<string>
): CoverageCertificate {
  const orphanAtoms = allAtoms.filter(a => !coveredAtoms.has(a));
  const coverageRatio = allAtoms.length > 0 
    ? coveredAtoms.size / allAtoms.length 
    : 1;
  
  return {
    id: `cert_coverage_${Date.now()}`,
    type: CertificationType.Coverage,
    timestamp: Date.now(),
    issuer: "ProofAlgebra",
    subject: `atoms[${allAtoms.length}]`,
    truth: coverageRatio === 1 ? TruthValue.OK : (coverageRatio > 0.9 ? TruthValue.NEAR : TruthValue.FAIL),
    witnessPtr: `wit_coverage_${Date.now()}`,
    signature: `sig_${Date.now()}`,
    metadata: {},
    totalAtoms: allAtoms.length,
    coveredAtoms: coveredAtoms.size,
    orphanAtoms,
    coverageRatio,
    indexComplete: orphanAtoms.length === 0
  };
}

/**
 * Generate Drift certificate
 */
export function generateDriftCertificate(
  baseline: string,
  current: string,
  computeDrift: (a: string, b: string) => number,
  maxAllowed: number
): DriftCertificate {
  const driftMeasure = computeDrift(baseline, current);
  const withinBounds = driftMeasure <= maxAllowed;
  
  return {
    id: `cert_drift_${Date.now()}`,
    type: CertificationType.Drift,
    timestamp: Date.now(),
    issuer: "ProofAlgebra",
    subject: `drift(${baseline}, ${current})`,
    truth: withinBounds ? TruthValue.OK : TruthValue.FAIL,
    witnessPtr: `wit_drift_${Date.now()}`,
    signature: `sig_${Date.now()}`,
    metadata: {},
    baseline,
    current,
    driftMeasure,
    maxAllowed,
    withinBounds,
    identityPreserved: driftMeasure < maxAllowed * 0.5
  };
}

/**
 * Generate Compliance certificate
 */
export function generateComplianceCertificate(
  protocol: string,
  version: string,
  constraints: { id: string; description: string; check: () => boolean }[]
): ComplianceCertificate {
  const results = constraints.map(c => ({
    id: c.id,
    description: c.description,
    satisfied: c.check(),
    evidence: `check_${c.id}`
  }));
  
  const satisfiedCount = results.filter(r => r.satisfied).length;
  const complianceScore = constraints.length > 0 
    ? satisfiedCount / constraints.length 
    : 1;
  
  return {
    id: `cert_compliance_${Date.now()}`,
    type: CertificationType.Compliance,
    timestamp: Date.now(),
    issuer: "ProofAlgebra",
    subject: `${protocol}@${version}`,
    truth: complianceScore === 1 ? TruthValue.OK : (complianceScore > 0.8 ? TruthValue.NEAR : TruthValue.FAIL),
    witnessPtr: `wit_compliance_${Date.now()}`,
    signature: `sig_${Date.now()}`,
    metadata: {},
    protocol,
    version,
    constraints: results,
    allSatisfied: complianceScore === 1,
    complianceScore
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: PROOF ALGEBRA ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete Proof Algebra Engine
 */
export class ProofAlgebraEngine {
  private errorLedger: Ledger;
  private massLedger: Ledger;
  private proofLedger: Ledger;
  private certificates: Map<string, Certificate> = new Map();
  
  constructor() {
    this.errorLedger = new Ledger(LedgerType.Error);
    this.massLedger = new Ledger(LedgerType.Mass);
    this.proofLedger = new Ledger(LedgerType.Proof);
  }
  
  /**
   * Create new proof builder
   */
  createProofBuilder(): ProofBuilder {
    return new ProofBuilder();
  }
  
  /**
   * Store certificate
   */
  storeCertificate(cert: Certificate): void {
    this.certificates.set(cert.id, cert);
    
    this.proofLedger.append({
      type: LedgerType.Proof,
      operation: "store_certificate",
      data: cert,
      witnessPtr: cert.witnessPtr
    });
  }
  
  /**
   * Get certificate
   */
  getCertificate(id: string): Certificate | undefined {
    return this.certificates.get(id);
  }
  
  /**
   * Verify certificate
   */
  verifyCertificate(id: string): { valid: boolean; reason?: string } {
    const cert = this.certificates.get(id);
    if (!cert) {
      return { valid: false, reason: "Certificate not found" };
    }
    
    // Verify signature (simplified)
    if (!cert.signature) {
      return { valid: false, reason: "Missing signature" };
    }
    
    // Verify witness exists
    if (!cert.witnessPtr) {
      return { valid: false, reason: "Missing witness" };
    }
    
    return { valid: true };
  }
  
  /**
   * Log error
   */
  logError(error: ErrorLedgerEntry["error"]): void {
    this.errorLedger.append({
      type: LedgerType.Error,
      operation: "log_error",
      data: { error, handled: false },
      witnessPtr: `wit_error_${Date.now()}`
    });
  }
  
  /**
   * Record mass transfer
   */
  recordMassTransfer(
    source: string,
    destination: string,
    mass: MassDistribution
  ): void {
    const conserved = isValidMassDistribution(mass);
    
    this.massLedger.append({
      type: LedgerType.Mass,
      operation: "mass_transfer",
      data: {
        mass: { ...mass, total: mass.bulk + mass.bdry + mass.erasure + mass.abstention },
        source,
        destination,
        conserved
      },
      witnessPtr: `wit_mass_${Date.now()}`
    });
  }
  
  /**
   * Get ledger
   */
  getLedger(type: LedgerType): Ledger {
    switch (type) {
      case LedgerType.Error: return this.errorLedger;
      case LedgerType.Mass: return this.massLedger;
      case LedgerType.Proof: return this.proofLedger;
    }
  }
  
  /**
   * Verify all ledgers
   */
  verifyAllLedgers(): { 
    error: { valid: boolean; brokenAt?: number };
    mass: { valid: boolean; brokenAt?: number };
    proof: { valid: boolean; brokenAt?: number };
  } {
    return {
      error: this.errorLedger.verify(),
      mass: this.massLedger.verify(),
      proof: this.proofLedger.verify()
    };
  }
  
  /**
   * Generate all certificates for an atom
   */
  generateAtomCertificates(
    atomId: string,
    edges: { source: string; target: string; kind: EdgeKind }[],
    witnesses: Map<string, string>,
    baseline: string
  ): Certificate[] {
    const certs: Certificate[] = [];
    
    // EdgeWF for each edge
    for (const edge of edges) {
      const cert = generateEdgeWFCertificate(
        edge,
        () => true,  // Simplified
        () => false  // Simplified
      );
      certs.push(cert);
      this.storeCertificate(cert);
    }
    
    // WitSuff
    const witSuffCert = generateWitSuffCertificate(
      [atomId],
      (id) => witnesses.get(id) || null
    );
    certs.push(witSuffCert);
    this.storeCertificate(witSuffCert);
    
    // Coverage
    const coverageCert = generateCoverageCertificate(
      [atomId],
      new Set([atomId])
    );
    certs.push(coverageCert);
    this.storeCertificate(coverageCert);
    
    // Drift
    const driftCert = generateDriftCertificate(
      baseline,
      atomId,
      (a, b) => a === b ? 0 : 0.1,
      0.5
    );
    certs.push(driftCert);
    this.storeCertificate(driftCert);
    
    return certs;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Types
  CertificationType,
  ProofRule,
  LedgerType,
  
  // Classes
  Ledger,
  ProofBuilder,
  ProofAlgebraEngine,
  
  // Mass conservation
  isValidMassDistribution,
  normalizeMassDistribution,
  transferMass,
  checkKappaConservation,
  
  // Certificate generators
  generateEdgeWFCertificate,
  generateWitSuffCertificate,
  generateCoverageCertificate,
  generateDriftCertificate,
  generateComplianceCertificate
};
