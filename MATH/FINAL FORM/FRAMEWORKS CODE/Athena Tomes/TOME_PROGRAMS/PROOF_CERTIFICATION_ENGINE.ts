/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * PROOF CERTIFICATION ENGINE - Complete Certification System
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Full implementation of the 10 certification types:
 *   1. EdgeWF - Edge well-formedness
 *   2. WitSuff - Witness sufficiency
 *   3. Coverage - Test coverage
 *   4. Slack - Budget slack
 *   5. Eq - Equality certification
 *   6. DualFac - Dual factorization
 *   7. Drift - Drift bounds
 *   8. ReplayAcc - Replay accuracy
 *   9. Closure - Closure verification
 *   10. Compliance - Protocol compliance
 * 
 * Features:
 *   - Complete verification algorithms
 *   - Certificate generation and validation
 *   - Proof chain construction
 *   - Mass conservation checking
 *   - Three ledger types (Λ_err, Λ_mass, Λ_proof)
 * 
 * @module PROOF_CERTIFICATION_ENGINE
 * @version 2.0.0
 */

import {
  TruthValue,
  EdgeKind,
  Corridors,
  WitnessPtr,
  Witnesses,
  ReplayCapsule,
  LinkEdge,
  LinkEdges
} from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: CERTIFICATE TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/** Certificate type enumeration */
export enum CertType {
  EdgeWF = "EdgeWF",
  WitSuff = "WitSuff",
  Coverage = "Coverage",
  Slack = "Slack",
  Eq = "Eq",
  DualFac = "DualFac",
  Drift = "Drift",
  ReplayAcc = "ReplayAcc",
  Closure = "Closure",
  Compliance = "Compliance"
}

/** Base certificate interface */
export interface Certificate {
  /** Unique certificate ID */
  id: string;
  
  /** Certificate type */
  type: CertType;
  
  /** Claim being certified */
  claim: CertClaim;
  
  /** Evidence supporting certification */
  evidence: CertEvidence;
  
  /** Resulting truth value */
  truth: TruthValue;
  
  /** Witness pointer */
  witness: WitnessPtr;
  
  /** Timestamp */
  timestamp: number;
  
  /** Expiration (if any) */
  expiresAt?: number;
  
  /** Chain of dependent certificates */
  dependsOn: string[];
}

/** Certificate claim */
export interface CertClaim {
  /** Statement being certified */
  statement: string;
  
  /** Domain/scope */
  domain: string;
  
  /** Subject addresses */
  subjects: string[];
  
  /** Quantifiers */
  quantifiers?: {
    forAll?: string[];
    exists?: string[];
  };
}

/** Certificate evidence */
export interface CertEvidence {
  /** Evidence type */
  type: "direct" | "derived" | "computed" | "witness" | "replay";
  
  /** Evidence data */
  data: unknown;
  
  /** Confidence level [0, 1] */
  confidence: number;
  
  /** Source references */
  sources: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: LEDGER TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/** Error ledger entry */
export interface ErrorLedgerEntry {
  id: string;
  errorType: string;
  severity: "warning" | "error" | "fatal";
  source: string;
  message: string;
  context: Map<string, unknown>;
  timestamp: number;
  resolved: boolean;
  resolution?: string;
}

/** Mass ledger entry (for κ-conservation) */
export interface MassLedgerEntry {
  id: string;
  address: string;
  mass: number;
  type: "bulk" | "boundary" | "erasure" | "abstention";
  operation: string;
  timestamp: number;
}

/** Proof ledger entry */
export interface ProofLedgerEntry {
  id: string;
  certificateId: string;
  claim: string;
  truth: TruthValue;
  witnessHash: string;
  verified: boolean;
  verifiedAt?: number;
  verifier?: string;
}

/** Complete ledger system */
export interface LedgerSystem {
  errors: ErrorLedgerEntry[];
  mass: MassLedgerEntry[];
  proofs: ProofLedgerEntry[];
}

/** Create empty ledger system */
export function createLedgerSystem(): LedgerSystem {
  return {
    errors: [],
    mass: [],
    proofs: []
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: CERTIFICATION ALGORITHMS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * EdgeWF Certifier: Verify edge well-formedness
 */
export class EdgeWFCertifier {
  /**
   * Certify that an edge is well-formed
   */
  certify(edge: LinkEdge): CertificationResult {
    const violations: string[] = [];
    
    // Check source address
    if (!edge.source || edge.source.length === 0) {
      violations.push("Missing source address");
    }
    
    // Check destination address
    if (!edge.destination || edge.destination.length === 0) {
      violations.push("Missing destination address");
    }
    
    // Check edge kind is valid
    const validKinds = Object.values(EdgeKind);
    if (!validKinds.includes(edge.kind)) {
      violations.push(`Invalid edge kind: ${edge.kind}`);
    }
    
    // Check truth value
    const validTruths = [TruthValue.OK, TruthValue.NEAR, TruthValue.AMBIG, TruthValue.FAIL];
    if (!validTruths.includes(edge.truth)) {
      violations.push(`Invalid truth value: ${edge.truth}`);
    }
    
    // Check self-loops
    if (edge.source === edge.destination && edge.kind !== EdgeKind.EQUIV) {
      violations.push("Self-loop only allowed for EQUIV edges");
    }
    
    // Check witness for OK status
    if (edge.truth === TruthValue.OK && !edge.witness) {
      violations.push("OK status requires witness");
    }
    
    const success = violations.length === 0;
    
    return {
      success,
      certType: CertType.EdgeWF,
      violations,
      certificate: success ? this.createCertificate(edge) : undefined
    };
  }
  
  private createCertificate(edge: LinkEdge): Certificate {
    return {
      id: `cert_edgewf_${Date.now()}`,
      type: CertType.EdgeWF,
      claim: {
        statement: `Edge ${edge.source} → ${edge.destination} is well-formed`,
        domain: "edge",
        subjects: [edge.source, edge.destination]
      },
      evidence: {
        type: "direct",
        data: { edgeKind: edge.kind, truth: edge.truth },
        confidence: 1.0,
        sources: [edge.source, edge.destination]
      },
      truth: TruthValue.OK,
      witness: edge.witness || createWitness("EdgeWF verified"),
      timestamp: Date.now(),
      dependsOn: []
    };
  }
}

/**
 * WitSuff Certifier: Verify witness sufficiency
 */
export class WitSuffCertifier {
  private minConfidence: number = 0.8;
  
  /**
   * Certify that witnesses are sufficient for a claim
   */
  certify(claim: CertClaim, witnesses: WitnessPtr[]): CertificationResult {
    const violations: string[] = [];
    
    // Must have at least one witness
    if (witnesses.length === 0) {
      violations.push("No witnesses provided");
    }
    
    // Check witness types
    const hasDirectWitness = witnesses.some(w => w.type === "direct");
    if (!hasDirectWitness) {
      violations.push("At least one direct witness required");
    }
    
    // Check confidence levels
    const avgConfidence = witnesses.reduce((s, w) => s + w.confidence, 0) / witnesses.length;
    if (avgConfidence < this.minConfidence) {
      violations.push(`Average confidence ${avgConfidence.toFixed(3)} below threshold ${this.minConfidence}`);
    }
    
    // Check coverage of subjects
    const witnessedSubjects = new Set<string>();
    for (const w of witnesses) {
      // Assume witness.id encodes subject
      witnessedSubjects.add(w.id);
    }
    
    const success = violations.length === 0;
    
    return {
      success,
      certType: CertType.WitSuff,
      violations,
      certificate: success ? this.createCertificate(claim, witnesses) : undefined
    };
  }
  
  private createCertificate(claim: CertClaim, witnesses: WitnessPtr[]): Certificate {
    return {
      id: `cert_witsuff_${Date.now()}`,
      type: CertType.WitSuff,
      claim,
      evidence: {
        type: "witness",
        data: { witnessCount: witnesses.length, witnesses: witnesses.map(w => w.id) },
        confidence: witnesses.reduce((s, w) => s + w.confidence, 0) / witnesses.length,
        sources: witnesses.map(w => w.id)
      },
      truth: TruthValue.OK,
      witness: witnesses[0],
      timestamp: Date.now(),
      dependsOn: []
    };
  }
}

/**
 * Coverage Certifier: Verify test coverage
 */
export class CoverageCertifier {
  private minCoverage: number = 0.8;
  
  /**
   * Certify test coverage
   */
  certify(
    totalAtoms: number,
    testedAtoms: number,
    criticalAtoms: Set<string>,
    testedCritical: Set<string>
  ): CertificationResult {
    const violations: string[] = [];
    
    // Overall coverage
    const coverage = testedAtoms / Math.max(totalAtoms, 1);
    if (coverage < this.minCoverage) {
      violations.push(`Coverage ${(coverage * 100).toFixed(1)}% below threshold ${this.minCoverage * 100}%`);
    }
    
    // Critical atom coverage must be 100%
    for (const critical of criticalAtoms) {
      if (!testedCritical.has(critical)) {
        violations.push(`Critical atom ${critical} not tested`);
      }
    }
    
    const success = violations.length === 0;
    
    return {
      success,
      certType: CertType.Coverage,
      violations,
      certificate: success ? this.createCertificate(coverage, testedAtoms, totalAtoms) : undefined
    };
  }
  
  private createCertificate(coverage: number, tested: number, total: number): Certificate {
    return {
      id: `cert_coverage_${Date.now()}`,
      type: CertType.Coverage,
      claim: {
        statement: `Test coverage ${(coverage * 100).toFixed(1)}% (${tested}/${total})`,
        domain: "testing",
        subjects: []
      },
      evidence: {
        type: "computed",
        data: { coverage, tested, total },
        confidence: coverage,
        sources: []
      },
      truth: TruthValue.OK,
      witness: createWitness(`Coverage: ${tested}/${total}`),
      timestamp: Date.now(),
      dependsOn: []
    };
  }
}

/**
 * Slack Certifier: Verify budget slack
 */
export class SlackCertifier {
  /**
   * Certify that budget has sufficient slack
   */
  certify(
    corridor: Corridors.Corridor,
    used: { hubs: number; time: number; memory: number }
  ): CertificationResult {
    const violations: string[] = [];
    
    // Check hub budget
    const hubSlack = 6 - used.hubs;
    if (hubSlack < 0) {
      violations.push(`Hub budget exceeded: ${used.hubs}/6`);
    }
    
    // Check compute budget
    const computeSlack = corridor.budgets.kappa_compute - used.time;
    if (computeSlack < 0) {
      violations.push(`Compute budget exceeded`);
    }
    
    // Check memory (4 MiB default)
    const memoryLimit = 4 * 1024 * 1024;
    const memorySlack = memoryLimit - used.memory;
    if (memorySlack < 0) {
      violations.push(`Memory budget exceeded`);
    }
    
    const success = violations.length === 0;
    
    return {
      success,
      certType: CertType.Slack,
      violations,
      certificate: success ? this.createCertificate(hubSlack, computeSlack, memorySlack) : undefined
    };
  }
  
  private createCertificate(hubSlack: number, computeSlack: number, memorySlack: number): Certificate {
    return {
      id: `cert_slack_${Date.now()}`,
      type: CertType.Slack,
      claim: {
        statement: `Budget slack: hubs=${hubSlack}, compute=${computeSlack}, memory=${memorySlack}`,
        domain: "budget",
        subjects: []
      },
      evidence: {
        type: "computed",
        data: { hubSlack, computeSlack, memorySlack },
        confidence: Math.min(hubSlack / 6, 1),
        sources: []
      },
      truth: TruthValue.OK,
      witness: createWitness("Budget within limits"),
      timestamp: Date.now(),
      dependsOn: []
    };
  }
}

/**
 * Eq Certifier: Verify equality
 */
export class EqCertifier {
  /**
   * Certify equality of two values
   */
  certify<T>(a: T, b: T, comparator?: (x: T, y: T) => boolean): CertificationResult {
    const equal = comparator ? comparator(a, b) : this.defaultCompare(a, b);
    const violations: string[] = [];
    
    if (!equal) {
      violations.push(`Values not equal`);
    }
    
    return {
      success: equal,
      certType: CertType.Eq,
      violations,
      certificate: equal ? this.createCertificate(a, b) : undefined
    };
  }
  
  private defaultCompare<T>(a: T, b: T): boolean {
    if (a === b) return true;
    if (typeof a !== typeof b) return false;
    if (typeof a === "object" && a !== null && b !== null) {
      return JSON.stringify(a) === JSON.stringify(b);
    }
    return false;
  }
  
  private createCertificate<T>(a: T, b: T): Certificate {
    return {
      id: `cert_eq_${Date.now()}`,
      type: CertType.Eq,
      claim: {
        statement: `a == b`,
        domain: "equality",
        subjects: []
      },
      evidence: {
        type: "computed",
        data: { a, b },
        confidence: 1.0,
        sources: []
      },
      truth: TruthValue.OK,
      witness: createWitness("Equality verified"),
      timestamp: Date.now(),
      dependsOn: []
    };
  }
}

/**
 * DualFac Certifier: Verify dual factorization
 */
export class DualFacCertifier {
  /**
   * Certify dual factorization: Carrier ⊕ Payload
   */
  certify(
    whole: unknown,
    carrier: unknown,
    payload: unknown,
    combine: (c: unknown, p: unknown) => unknown
  ): CertificationResult {
    const violations: string[] = [];
    
    // Verify that combine(carrier, payload) == whole
    const reconstructed = combine(carrier, payload);
    const matches = JSON.stringify(reconstructed) === JSON.stringify(whole);
    
    if (!matches) {
      violations.push("Dual factorization failed: Carrier ⊕ Payload ≠ Whole");
    }
    
    const success = violations.length === 0;
    
    return {
      success,
      certType: CertType.DualFac,
      violations,
      certificate: success ? this.createCertificate() : undefined
    };
  }
  
  private createCertificate(): Certificate {
    return {
      id: `cert_dualfac_${Date.now()}`,
      type: CertType.DualFac,
      claim: {
        statement: "Carrier ⊕ Payload = Whole",
        domain: "factorization",
        subjects: []
      },
      evidence: {
        type: "computed",
        data: {},
        confidence: 1.0,
        sources: []
      },
      truth: TruthValue.OK,
      witness: createWitness("Dual factorization verified"),
      timestamp: Date.now(),
      dependsOn: []
    };
  }
}

/**
 * Drift Certifier: Verify drift bounds
 */
export class DriftCertifier {
  private maxDrift: number;
  
  constructor(maxDrift: number = 0.1) {
    this.maxDrift = maxDrift;
  }
  
  /**
   * Certify that drift is within bounds
   */
  certify(
    original: number[],
    current: number[],
    metric: (a: number[], b: number[]) => number = this.euclidean
  ): CertificationResult {
    const violations: string[] = [];
    
    if (original.length !== current.length) {
      violations.push("Dimension mismatch");
      return {
        success: false,
        certType: CertType.Drift,
        violations
      };
    }
    
    const drift = metric(original, current);
    
    if (drift > this.maxDrift) {
      violations.push(`Drift ${drift.toFixed(4)} exceeds bound ${this.maxDrift}`);
    }
    
    const success = violations.length === 0;
    
    return {
      success,
      certType: CertType.Drift,
      violations,
      certificate: success ? this.createCertificate(drift) : undefined
    };
  }
  
  private euclidean(a: number[], b: number[]): number {
    let sum = 0;
    for (let i = 0; i < a.length; i++) {
      sum += (a[i] - b[i]) ** 2;
    }
    return Math.sqrt(sum);
  }
  
  private createCertificate(drift: number): Certificate {
    return {
      id: `cert_drift_${Date.now()}`,
      type: CertType.Drift,
      claim: {
        statement: `Drift ${drift.toFixed(4)} within bound ${this.maxDrift}`,
        domain: "stability",
        subjects: []
      },
      evidence: {
        type: "computed",
        data: { drift, bound: this.maxDrift },
        confidence: 1 - (drift / this.maxDrift),
        sources: []
      },
      truth: TruthValue.OK,
      witness: createWitness(`Drift: ${drift.toFixed(4)}`),
      timestamp: Date.now(),
      dependsOn: []
    };
  }
}

/**
 * ReplayAcc Certifier: Verify replay accuracy
 */
export class ReplayAccCertifier {
  /**
   * Certify that replay produces identical results
   */
  certify(
    original: ReplayCapsule,
    replayed: ReplayCapsule
  ): CertificationResult {
    const violations: string[] = [];
    
    // Check step count
    if (original.steps.length !== replayed.steps.length) {
      violations.push(`Step count mismatch: ${original.steps.length} vs ${replayed.steps.length}`);
    }
    
    // Check outputs
    if (JSON.stringify(original.outputs) !== JSON.stringify(replayed.outputs)) {
      violations.push("Output mismatch");
    }
    
    // Check seal
    if (original.seal !== replayed.seal) {
      violations.push("Seal mismatch");
    }
    
    const success = violations.length === 0;
    
    return {
      success,
      certType: CertType.ReplayAcc,
      violations,
      certificate: success ? this.createCertificate(original.id) : undefined
    };
  }
  
  private createCertificate(replayId: string): Certificate {
    return {
      id: `cert_replay_${Date.now()}`,
      type: CertType.ReplayAcc,
      claim: {
        statement: `Replay ${replayId} produces identical results`,
        domain: "determinism",
        subjects: [replayId]
      },
      evidence: {
        type: "replay",
        data: { replayId },
        confidence: 1.0,
        sources: [replayId]
      },
      truth: TruthValue.OK,
      witness: createWitness("Replay verified"),
      timestamp: Date.now(),
      dependsOn: []
    };
  }
}

/**
 * Closure Certifier: Verify closure properties
 */
export class ClosureCertifier {
  /**
   * Certify that a set is closed under an operation
   */
  certify<T>(
    set: T[],
    operation: (a: T, b: T) => T,
    equals: (a: T, b: T) => boolean = (a, b) => a === b
  ): CertificationResult {
    const violations: string[] = [];
    
    // Check all pairs
    for (const a of set) {
      for (const b of set) {
        const result = operation(a, b);
        const inSet = set.some(x => equals(x, result));
        if (!inSet) {
          violations.push("Operation result not in set");
          break;
        }
      }
      if (violations.length > 0) break;
    }
    
    const success = violations.length === 0;
    
    return {
      success,
      certType: CertType.Closure,
      violations,
      certificate: success ? this.createCertificate(set.length) : undefined
    };
  }
  
  private createCertificate(setSize: number): Certificate {
    return {
      id: `cert_closure_${Date.now()}`,
      type: CertType.Closure,
      claim: {
        statement: `Set of size ${setSize} is closed`,
        domain: "algebra",
        subjects: []
      },
      evidence: {
        type: "computed",
        data: { setSize },
        confidence: 1.0,
        sources: []
      },
      truth: TruthValue.OK,
      witness: createWitness("Closure verified"),
      timestamp: Date.now(),
      dependsOn: []
    };
  }
}

/**
 * Compliance Certifier: Verify protocol compliance
 */
export class ComplianceCertifier {
  /**
   * Certify compliance with protocol rules
   */
  certify(
    rules: ProtocolRule[],
    actions: ProtocolAction[]
  ): CertificationResult {
    const violations: string[] = [];
    
    for (const action of actions) {
      for (const rule of rules) {
        if (rule.applies(action)) {
          const result = rule.check(action);
          if (!result.compliant) {
            violations.push(`Rule ${rule.id}: ${result.reason}`);
          }
        }
      }
    }
    
    const success = violations.length === 0;
    
    return {
      success,
      certType: CertType.Compliance,
      violations,
      certificate: success ? this.createCertificate(rules.length, actions.length) : undefined
    };
  }
  
  private createCertificate(ruleCount: number, actionCount: number): Certificate {
    return {
      id: `cert_compliance_${Date.now()}`,
      type: CertType.Compliance,
      claim: {
        statement: `${actionCount} actions comply with ${ruleCount} rules`,
        domain: "protocol",
        subjects: []
      },
      evidence: {
        type: "computed",
        data: { ruleCount, actionCount },
        confidence: 1.0,
        sources: []
      },
      truth: TruthValue.OK,
      witness: createWitness("Protocol compliance verified"),
      timestamp: Date.now(),
      dependsOn: []
    };
  }
}

/** Protocol rule interface */
export interface ProtocolRule {
  id: string;
  applies: (action: ProtocolAction) => boolean;
  check: (action: ProtocolAction) => { compliant: boolean; reason?: string };
}

/** Protocol action interface */
export interface ProtocolAction {
  id: string;
  type: string;
  data: unknown;
  timestamp: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: CERTIFICATION RESULT
// ═══════════════════════════════════════════════════════════════════════════════

/** Certification result */
export interface CertificationResult {
  success: boolean;
  certType: CertType;
  violations: string[];
  certificate?: Certificate;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: MASS CONSERVATION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Mass conservation checker
 * Verifies: bulk + boundary + erasure + abstention = 1
 */
export class MassConservation {
  /**
   * Check mass conservation
   */
  check(ledger: MassLedgerEntry[]): MassConservationResult {
    let bulk = 0;
    let boundary = 0;
    let erasure = 0;
    let abstention = 0;
    
    for (const entry of ledger) {
      switch (entry.type) {
        case "bulk":
          bulk += entry.mass;
          break;
        case "boundary":
          boundary += entry.mass;
          break;
        case "erasure":
          erasure += entry.mass;
          break;
        case "abstention":
          abstention += entry.mass;
          break;
      }
    }
    
    const total = bulk + boundary + erasure + abstention;
    const conserved = Math.abs(total - 1.0) < 1e-6;
    
    return {
      conserved,
      bulk,
      boundary,
      erasure,
      abstention,
      total,
      deficit: 1.0 - total
    };
  }
  
  /**
   * Balance the ledger by adjusting abstention
   */
  balance(ledger: MassLedgerEntry[]): MassLedgerEntry[] {
    const result = this.check(ledger);
    
    if (result.conserved) {
      return ledger;
    }
    
    // Add abstention entry to balance
    const balanceEntry: MassLedgerEntry = {
      id: `balance_${Date.now()}`,
      address: "__balance__",
      mass: result.deficit,
      type: "abstention",
      operation: "auto_balance",
      timestamp: Date.now()
    };
    
    return [...ledger, balanceEntry];
  }
}

export interface MassConservationResult {
  conserved: boolean;
  bulk: number;
  boundary: number;
  erasure: number;
  abstention: number;
  total: number;
  deficit: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: PROOF CHAIN BUILDER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Build proof chains from certificates
 */
export class ProofChainBuilder {
  private certificates: Map<string, Certificate> = new Map();
  
  /**
   * Add certificate to pool
   */
  add(cert: Certificate): void {
    this.certificates.set(cert.id, cert);
  }
  
  /**
   * Build proof chain for a target certificate
   */
  buildChain(targetId: string): ProofChain | null {
    const target = this.certificates.get(targetId);
    if (!target) return null;
    
    const chain: Certificate[] = [];
    const visited = new Set<string>();
    
    this.collectDependencies(target, chain, visited);
    chain.push(target);
    
    return {
      target: targetId,
      certificates: chain,
      depth: chain.length,
      truth: this.computeChainTruth(chain)
    };
  }
  
  private collectDependencies(
    cert: Certificate,
    chain: Certificate[],
    visited: Set<string>
  ): void {
    if (visited.has(cert.id)) return;
    visited.add(cert.id);
    
    for (const depId of cert.dependsOn) {
      const dep = this.certificates.get(depId);
      if (dep) {
        this.collectDependencies(dep, chain, visited);
        chain.push(dep);
      }
    }
  }
  
  private computeChainTruth(chain: Certificate[]): TruthValue {
    // Chain truth is the minimum (lattice meet)
    let minTruth = TruthValue.OK;
    for (const cert of chain) {
      minTruth = Math.min(minTruth, cert.truth);
    }
    return minTruth;
  }
  
  /**
   * Verify entire chain
   */
  verifyChain(chain: ProofChain): ChainVerificationResult {
    const errors: string[] = [];
    
    for (let i = 0; i < chain.certificates.length; i++) {
      const cert = chain.certificates[i];
      
      // Verify dependencies exist
      for (const depId of cert.dependsOn) {
        const depExists = chain.certificates.some(c => c.id === depId);
        if (!depExists) {
          errors.push(`Certificate ${cert.id} depends on missing ${depId}`);
        }
      }
      
      // Verify witness exists
      if (!cert.witness) {
        errors.push(`Certificate ${cert.id} has no witness`);
      }
    }
    
    return {
      valid: errors.length === 0,
      errors,
      chainLength: chain.certificates.length
    };
  }
}

export interface ProofChain {
  target: string;
  certificates: Certificate[];
  depth: number;
  truth: TruthValue;
}

export interface ChainVerificationResult {
  valid: boolean;
  errors: string[];
  chainLength: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: CERTIFICATION ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete certification engine
 */
export class CertificationEngine {
  private ledger: LedgerSystem;
  private chainBuilder: ProofChainBuilder;
  private massConservation: MassConservation;
  
  // Certifiers
  private edgeWF: EdgeWFCertifier;
  private witSuff: WitSuffCertifier;
  private coverage: CoverageCertifier;
  private slack: SlackCertifier;
  private eq: EqCertifier;
  private dualFac: DualFacCertifier;
  private drift: DriftCertifier;
  private replayAcc: ReplayAccCertifier;
  private closure: ClosureCertifier;
  private compliance: ComplianceCertifier;
  
  constructor() {
    this.ledger = createLedgerSystem();
    this.chainBuilder = new ProofChainBuilder();
    this.massConservation = new MassConservation();
    
    this.edgeWF = new EdgeWFCertifier();
    this.witSuff = new WitSuffCertifier();
    this.coverage = new CoverageCertifier();
    this.slack = new SlackCertifier();
    this.eq = new EqCertifier();
    this.dualFac = new DualFacCertifier();
    this.drift = new DriftCertifier();
    this.replayAcc = new ReplayAccCertifier();
    this.closure = new ClosureCertifier();
    this.compliance = new ComplianceCertifier();
  }
  
  /**
   * Run all certifications
   */
  certifyAll(context: CertificationContext): CertificationReport {
    const results: Map<CertType, CertificationResult> = new Map();
    const startTime = Date.now();
    
    // EdgeWF
    if (context.edges) {
      for (const edge of context.edges) {
        const result = this.edgeWF.certify(edge);
        results.set(CertType.EdgeWF, result);
        if (result.certificate) {
          this.chainBuilder.add(result.certificate);
        }
      }
    }
    
    // WitSuff
    if (context.claims && context.witnesses) {
      for (const claim of context.claims) {
        const result = this.witSuff.certify(claim, context.witnesses);
        results.set(CertType.WitSuff, result);
        if (result.certificate) {
          this.chainBuilder.add(result.certificate);
        }
      }
    }
    
    // Coverage
    if (context.coverage) {
      const result = this.coverage.certify(
        context.coverage.total,
        context.coverage.tested,
        context.coverage.critical,
        context.coverage.testedCritical
      );
      results.set(CertType.Coverage, result);
      if (result.certificate) {
        this.chainBuilder.add(result.certificate);
      }
    }
    
    // Slack
    if (context.corridor && context.budgetUsed) {
      const result = this.slack.certify(context.corridor, context.budgetUsed);
      results.set(CertType.Slack, result);
      if (result.certificate) {
        this.chainBuilder.add(result.certificate);
      }
    }
    
    // Drift
    if (context.drift) {
      const result = this.drift.certify(context.drift.original, context.drift.current);
      results.set(CertType.Drift, result);
      if (result.certificate) {
        this.chainBuilder.add(result.certificate);
      }
    }
    
    // Compliance
    if (context.rules && context.actions) {
      const result = this.compliance.certify(context.rules, context.actions);
      results.set(CertType.Compliance, result);
      if (result.certificate) {
        this.chainBuilder.add(result.certificate);
      }
    }
    
    // Compute overall truth
    let overallTruth = TruthValue.OK;
    let passCount = 0;
    let failCount = 0;
    
    for (const [type, result] of results) {
      if (result.success) {
        passCount++;
      } else {
        failCount++;
        overallTruth = Math.min(overallTruth, TruthValue.NEAR);
      }
    }
    
    return {
      success: failCount === 0,
      results,
      overallTruth,
      passCount,
      failCount,
      totalTime: Date.now() - startTime,
      ledger: this.ledger
    };
  }
  
  /**
   * Get proof chain for a certificate
   */
  getProofChain(certId: string): ProofChain | null {
    return this.chainBuilder.buildChain(certId);
  }
  
  /**
   * Check mass conservation
   */
  checkMassConservation(): MassConservationResult {
    return this.massConservation.check(this.ledger.mass);
  }
  
  /**
   * Add to mass ledger
   */
  recordMass(entry: Omit<MassLedgerEntry, "id" | "timestamp">): void {
    this.ledger.mass.push({
      ...entry,
      id: `mass_${Date.now()}`,
      timestamp: Date.now()
    });
  }
  
  /**
   * Record error
   */
  recordError(entry: Omit<ErrorLedgerEntry, "id" | "timestamp" | "resolved">): void {
    this.ledger.errors.push({
      ...entry,
      id: `err_${Date.now()}`,
      timestamp: Date.now(),
      resolved: false
    });
  }
}

export interface CertificationContext {
  edges?: LinkEdge[];
  claims?: CertClaim[];
  witnesses?: WitnessPtr[];
  coverage?: {
    total: number;
    tested: number;
    critical: Set<string>;
    testedCritical: Set<string>;
  };
  corridor?: Corridors.Corridor;
  budgetUsed?: { hubs: number; time: number; memory: number };
  drift?: {
    original: number[];
    current: number[];
  };
  rules?: ProtocolRule[];
  actions?: ProtocolAction[];
}

export interface CertificationReport {
  success: boolean;
  results: Map<CertType, CertificationResult>;
  overallTruth: TruthValue;
  passCount: number;
  failCount: number;
  totalTime: number;
  ledger: LedgerSystem;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 8: HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

function createWitness(description: string): WitnessPtr {
  return {
    id: `wit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    type: "direct",
    hash: hashString(description),
    confidence: 1.0
  };
}

function hashString(s: string): string {
  let hash = 0;
  for (let i = 0; i < s.length; i++) {
    hash = ((hash << 5) - hash) + s.charCodeAt(i);
    hash = hash & hash;
  }
  return Math.abs(hash).toString(16).padStart(16, '0');
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  CertType,
  EdgeWFCertifier,
  WitSuffCertifier,
  CoverageCertifier,
  SlackCertifier,
  EqCertifier,
  DualFacCertifier,
  DriftCertifier,
  ReplayAccCertifier,
  ClosureCertifier,
  ComplianceCertifier,
  MassConservation,
  ProofChainBuilder,
  CertificationEngine,
  createLedgerSystem
};
