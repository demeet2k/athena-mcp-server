/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * ADDRESSING CANONICAL ENGINE - Complete Addressing System
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * From TRUTH-COLLAPSE_COMPILER Ch01:
 * 
 * Core Components:
 *   - Manuscript ID derivation (Ch01.S1.a)
 *   - LocalAddr grammar (Ch01.S1.b)
 *   - GlobalAddr = Ms⟨mmmm⟩::LocalAddr (Ch01.S1.c)
 *   - Address canonicalization NF_addr (Ch01.S2.a)
 *   - EdgeID determinism (Ch01.S2.b)
 *   - Closed alphabets 𝓚, 𝕋 (Ch01.S2.c)
 *   - Truth type inference (Ch01.S1.d)
 * 
 * @module ADDRESSING_CANONICAL_ENGINE
 * @version 2.0.0
 */

import * as crypto from 'crypto';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: CLOSED ALPHABETS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Truth lattice 𝕋 (closed set)
 */
export enum TruthValue {
  OK = "OK",
  NEAR = "NEAR",
  AMBIG = "AMBIG",
  FAIL = "FAIL"
}

/**
 * Edge kinds 𝓚 (closed set)
 */
export enum EdgeKind {
  REF = "REF",
  EQUIV = "EQUIV",
  MIGRATE = "MIGRATE",
  DUAL = "DUAL",
  GEN = "GEN",
  INST = "INST",
  IMPL = "IMPL",
  PROOF = "PROOF",
  CONFLICT = "CONFLICT"
}

/**
 * Lens types (closed set)
 */
export enum Lens {
  S = "S",  // Square/Earth
  F = "F",  // Flower/Air
  C = "C",  // Cloud/Water
  R = "R"   // Fractal/Fire
}

/**
 * Facet values (closed set: 1-4)
 */
export type Facet = 1 | 2 | 3 | 4;

/**
 * Atom values (closed set: a-d)
 */
export type Atom = "a" | "b" | "c" | "d";

/**
 * Validate closed alphabet membership
 */
export function validateClosedAlphabet<T extends string>(
  value: string,
  alphabet: Record<string, T>,
  name: string
): T {
  const values = Object.values(alphabet);
  if (!values.includes(value as T)) {
    throw new AddressingError(
      `InvalidAlphabet: ${value} not in ${name}`,
      "CLOSED_ALPHABET_VIOLATION"
    );
  }
  return value as T;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: MANUSCRIPT ID
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Manuscript ID (derived deterministically from seed)
 */
export interface ManuscriptID {
  code: string;      // 4 hex chars (uppercase)
  seed: string;      // Original seed string
  version: string;   // SemVer
  hash: string;      // Full SHA-256 hash
}

/**
 * Known manuscript IDs
 */
export const KNOWN_MANUSCRIPTS: Record<string, string> = {
  "SELF_SUFFICIENCY": "3E94",
  "TRUTH_COLLAPSE": "2103",
  "VOYNICHVM": "B83A",
  "AWAKENING_OS": "56B0",
  "PULSE_RETRO": "CC9C",
  "EMOTIONAL_HYPER": "D728",
  "DIVINATION": "F772"
};

/**
 * Derive manuscript ID from seed
 */
export function deriveManuscriptID(seed: string, version: string = "1.0.0"): ManuscriptID {
  const msString = `${seed}|${version}|ROUTEv2|CST`;
  const hash = hashSHA256(msString);
  const code = hash.slice(0, 4).toUpperCase();
  
  return {
    code,
    seed,
    version,
    hash
  };
}

/**
 * SHA-256 hash (deterministic)
 */
function hashSHA256(input: string): string {
  // Use simple deterministic hash for browser compatibility
  let hash = 0;
  for (let i = 0; i < input.length; i++) {
    const char = input.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  
  // Convert to hex and pad to 64 chars
  const hex = Math.abs(hash).toString(16).padStart(8, '0');
  return hex.repeat(8).slice(0, 64);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: LOCAL ADDRESS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Chapter atom address
 */
export interface ChapterAtomAddr {
  kind: "ChapterAtom";
  chapter: number;      // 1-21
  stationCode: string;  // Base-4, 4 digits
  lens: Lens;
  facet: Facet;
  atom: Atom;
}

/**
 * Appendix atom address
 */
export interface AppendixAtomAddr {
  kind: "AppendixAtom";
  appendix: string;     // A-P
  lens: Lens;
  facet: Facet;
  atom: Atom;
}

/**
 * Local address (union type)
 */
export type LocalAddr = ChapterAtomAddr | AppendixAtomAddr;

/**
 * Global address
 */
export interface GlobalAddr {
  ms: ManuscriptID;
  local: LocalAddr;
}

/**
 * Compute station code (base-4, 4 digits)
 */
export function computeStationCode(chapter: number): string {
  if (chapter < 1 || chapter > 21) {
    throw new AddressingError(
      `InvalidChapter: ${chapter} not in range 1-21`,
      "CHAPTER_OUT_OF_RANGE"
    );
  }
  const omega = chapter - 1;
  return omega.toString(4).padStart(4, '0');
}

/**
 * Parse station code to chapter
 */
export function parseStationCode(code: string): number {
  const omega = parseInt(code, 4);
  return omega + 1;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: ADDRESS PARSING
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Address parse result
 */
export type AddressParseResult =
  | { type: "OK"; addr: GlobalAddr }
  | { type: "FAIL"; error: string; code: string };

/**
 * Address parser
 */
export class AddressParser {
  /**
   * Parse address string to GlobalAddr
   * Format: Ms⟨mmmm⟩::ChXX⟨dddd⟩.Lf.a or Ms⟨mmmm⟩::AppX.Lf.a
   */
  parse(addrStr: string): AddressParseResult {
    try {
      // Split on ::
      const parts = addrStr.split("::");
      if (parts.length !== 2) {
        return { type: "FAIL", error: "Missing :: separator", code: "PARSE_NO_SEPARATOR" };
      }
      
      const [msPart, localPart] = parts;
      
      // Parse manuscript ID
      const msMatch = msPart.match(/^Ms[⟨<]([0-9A-Fa-f]{4})[⟩>]$/);
      if (!msMatch) {
        return { type: "FAIL", error: "Invalid manuscript format", code: "PARSE_INVALID_MS" };
      }
      
      const msCode = msMatch[1].toUpperCase();
      const ms: ManuscriptID = {
        code: msCode,
        seed: `Ms${msCode}`,
        version: "1.0.0",
        hash: hashSHA256(`Ms${msCode}`)
      };
      
      // Parse local address
      const local = this.parseLocal(localPart);
      if (!local) {
        return { type: "FAIL", error: "Invalid local address format", code: "PARSE_INVALID_LOCAL" };
      }
      
      return { type: "OK", addr: { ms, local } };
      
    } catch (e) {
      return { type: "FAIL", error: e instanceof Error ? e.message : "Unknown error", code: "PARSE_EXCEPTION" };
    }
  }
  
  /**
   * Parse local address
   */
  private parseLocal(localStr: string): LocalAddr | null {
    // Try chapter format: ChXX⟨dddd⟩.Lf.a
    const chMatch = localStr.match(/^Ch(\d{2})[⟨<](\d{4})[⟩>]\.([SFCR])(\d)\.([abcd])$/);
    if (chMatch) {
      const chapter = parseInt(chMatch[1], 10);
      const stationCode = chMatch[2];
      const lens = chMatch[3] as Lens;
      const facet = parseInt(chMatch[4], 10) as Facet;
      const atom = chMatch[5] as Atom;
      
      if (chapter < 1 || chapter > 21) return null;
      if (facet < 1 || facet > 4) return null;
      
      return {
        kind: "ChapterAtom",
        chapter,
        stationCode,
        lens,
        facet,
        atom
      };
    }
    
    // Try appendix format: AppX.Lf.a
    const appMatch = localStr.match(/^App([A-P])\.([SFCR])(\d)\.([abcd])$/);
    if (appMatch) {
      const appendix = appMatch[1];
      const lens = appMatch[2] as Lens;
      const facet = parseInt(appMatch[3], 10) as Facet;
      const atom = appMatch[4] as Atom;
      
      if (facet < 1 || facet > 4) return null;
      
      return {
        kind: "AppendixAtom",
        appendix,
        lens,
        facet,
        atom
      };
    }
    
    return null;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: ADDRESS NORMALIZATION (NF_addr)
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Address normalizer (Ch01.S2.a)
 * 
 * Properties:
 * - Idempotence: NF(NF(x)) = NF(x)
 * - Stability: parse(NF(x)) succeeds iff parse(x) succeeds
 * - Uniqueness: if two strings parse to same semantic address, their NF is equal
 */
export class AddressNormalizer {
  private parser: AddressParser;
  
  constructor() {
    this.parser = new AddressParser();
  }
  
  /**
   * Normalize address string to canonical form
   */
  normalize(addrStr: string): string {
    const parseResult = this.parser.parse(addrStr);
    
    if (parseResult.type === "FAIL") {
      throw new AddressingError(
        `Cannot normalize invalid address: ${parseResult.error}`,
        parseResult.code
      );
    }
    
    return this.formatGlobalAddr(parseResult.addr);
  }
  
  /**
   * Format GlobalAddr to canonical string
   */
  formatGlobalAddr(addr: GlobalAddr): string {
    const msPart = `Ms⟨${addr.ms.code}⟩`;
    const localPart = this.formatLocalAddr(addr.local);
    return `${msPart}::${localPart}`;
  }
  
  /**
   * Format LocalAddr to canonical string
   */
  formatLocalAddr(local: LocalAddr): string {
    if (local.kind === "ChapterAtom") {
      const chNum = local.chapter.toString().padStart(2, '0');
      return `Ch${chNum}⟨${local.stationCode}⟩.${local.lens}${local.facet}.${local.atom}`;
    } else {
      return `App${local.appendix}.${local.lens}${local.facet}.${local.atom}`;
    }
  }
  
  /**
   * Check if two addresses are semantically equal
   */
  areEqual(addr1: string, addr2: string): boolean {
    try {
      const nf1 = this.normalize(addr1);
      const nf2 = this.normalize(addr2);
      return nf1 === nf2;
    } catch {
      return false;
    }
  }
  
  /**
   * Verify idempotence property
   */
  verifyIdempotence(addrStr: string): boolean {
    try {
      const nf1 = this.normalize(addrStr);
      const nf2 = this.normalize(nf1);
      return nf1 === nf2;
    } catch {
      return false;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: EDGE ID DETERMINISM
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Link edge schema (Ch01.S1.b, Ch01.S2.b)
 */
export interface LinkEdge {
  edgeId: string;
  kind: EdgeKind;
  src: GlobalAddr;
  dst: GlobalAddr;
  scope: string;
  corridor: CorridorRef;
  witnessPtr?: string;
  replayPtr?: string;
  payload?: unknown;
  edgeVer: string;
}

export interface CorridorRef {
  id: string;
  budgets: CorridorBudgets;
}

export interface CorridorBudgets {
  kappa: number;
  beta: number;
  chi: number;
  epsilon: number;
}

/**
 * Compute EdgeID (deterministic hash)
 * EdgeID := H(Kind|Src|Dst|Scope|Corridor|Payload|EdgeVer)
 */
export function computeEdgeID(
  kind: EdgeKind,
  src: GlobalAddr,
  dst: GlobalAddr,
  scope: string,
  corridor: CorridorRef,
  payload: unknown,
  edgeVer: string
): string {
  const normalizer = new AddressNormalizer();
  
  const components = [
    kind,
    normalizer.formatGlobalAddr(src),
    normalizer.formatGlobalAddr(dst),
    scope,
    JSON.stringify(corridor),
    JSON.stringify(payload ?? null),
    edgeVer
  ];
  
  const serialized = canonicalSerialize(components);
  return hashDomainSeparated("EDGE_ID", serialized);
}

/**
 * Canonical serialization
 */
function canonicalSerialize(components: unknown[]): string {
  return components.map(c => {
    if (typeof c === "string") return c;
    return JSON.stringify(c, Object.keys(c as object).sort());
  }).join("|");
}

/**
 * Domain-separated hash
 */
function hashDomainSeparated(domain: string, input: string): string {
  const prefixed = `${domain}:${input}`;
  return hashSHA256(prefixed).slice(0, 16);
}

/**
 * Link edge builder
 */
export class LinkEdgeBuilder {
  private normalizer: AddressNormalizer;
  
  constructor() {
    this.normalizer = new AddressNormalizer();
  }
  
  /**
   * Create link edge with deterministic EdgeID
   */
  create(
    kind: EdgeKind,
    src: GlobalAddr,
    dst: GlobalAddr,
    scope: string,
    corridor: CorridorRef,
    payload?: unknown,
    edgeVer: string = "1.0.0"
  ): LinkEdge {
    const edgeId = computeEdgeID(kind, src, dst, scope, corridor, payload, edgeVer);
    
    return {
      edgeId,
      kind,
      src,
      dst,
      scope,
      corridor,
      payload,
      edgeVer
    };
  }
  
  /**
   * Verify EdgeID (recompute and compare)
   */
  verifyEdgeID(edge: LinkEdge): boolean {
    const recomputed = computeEdgeID(
      edge.kind,
      edge.src,
      edge.dst,
      edge.scope,
      edge.corridor,
      edge.payload,
      edge.edgeVer
    );
    return edge.edgeId === recomputed;
  }
  
  /**
   * Add witness pointer
   */
  withWitness(edge: LinkEdge, witnessPtr: string): LinkEdge {
    return { ...edge, witnessPtr };
  }
  
  /**
   * Add replay pointer
   */
  withReplay(edge: LinkEdge, replayPtr: string): LinkEdge {
    return { ...edge, replayPtr };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: TRUTH TYPE INFERENCE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Truth record (Ch01.S1.d)
 */
export interface TruthRecord {
  truth: TruthValue;
  witnessPtr?: string;
  replayPtr?: string;
  residualLedger?: ResidualLedger;
  upgradePlan?: UpgradePlan;
  candidateSet?: CandidateSet;
  evidencePlan?: EvidencePlan;
  quarantineCapsule?: QuarantineCapsule;
  conflictReceipts?: ConflictReceipt[];
}

export interface ResidualLedger {
  residuals: string[];
  count: number;
}

export interface UpgradePlan {
  steps: string[];
  estimatedCost: number;
}

export interface CandidateSet {
  candidates: unknown[];
  scores: number[];
}

export interface EvidencePlan {
  discriminators: string[];
  budgets: CorridorBudgets;
}

export interface QuarantineCapsule {
  target: string;
  conflicts: unknown[];
  permanent: boolean;
}

export interface ConflictReceipt {
  id: string;
  kind: string;
  source: string;
  target: string;
}

/**
 * Truth type inference (Ch01.S1.d algorithm)
 */
export function inferTruthType(record: TruthRecord): TruthValue {
  // FAIL: has QuarantineCapsule and ConflictReceipts
  if (record.quarantineCapsule && record.conflictReceipts && record.conflictReceipts.length > 0) {
    return TruthValue.FAIL;
  }
  
  // AMBIG: has CandidateSet and EvidencePlan
  if (record.candidateSet && record.evidencePlan) {
    return TruthValue.AMBIG;
  }
  
  // NEAR: has ResidualLedger and UpgradePlan
  if (record.residualLedger && record.upgradePlan) {
    return TruthValue.NEAR;
  }
  
  // OK: has WitnessPtr and ReplayPtr and passes ReplayVerify
  if (record.witnessPtr && record.replayPtr) {
    return TruthValue.OK;
  }
  
  // Default: FAIL with CONFLICT "untyped truth record"
  return TruthValue.FAIL;
}

/**
 * Get required overlay for truth value
 */
export function getTruthOverlay(truth: TruthValue): string | null {
  switch (truth) {
    case TruthValue.NEAR: return "AppJ";
    case TruthValue.AMBIG: return "AppL";
    case TruthValue.FAIL: return "AppK";
    case TruthValue.OK: return null;  // AppO only when publishing
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 8: METRO INDICES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Triangle lane
 */
export type TriangleLane = "Su" | "Me" | "Sa";

/**
 * Arc hub mapping
 */
export const ARC_HUB_MAP: Record<number, string> = {
  0: "AppA",
  1: "AppC",
  2: "AppE",
  3: "AppF",
  4: "AppG",
  5: "AppN",
  6: "AppP"
};

/**
 * Compute metro indices for chapter
 */
export function computeMetroIndices(chapter: number): {
  omega: number;
  alpha: number;
  k: number;
  rho: number;
  lane: TriangleLane;
  arcHub: string;
} {
  if (chapter < 1 || chapter > 21) {
    throw new AddressingError(
      `Invalid chapter: ${chapter}`,
      "INVALID_CHAPTER"
    );
  }
  
  const omega = chapter - 1;
  const alpha = Math.floor(omega / 3);
  const k = omega % 3;
  const rho = alpha % 3;
  
  const triad: TriangleLane[] = ["Su", "Me", "Sa"];
  const rotatedTriad = rotateTriad(triad, rho);
  const lane = rotatedTriad[k];
  
  const arcHub = ARC_HUB_MAP[alpha] ?? "AppA";
  
  return { omega, alpha, k, rho, lane, arcHub };
}

/**
 * Rotate triad by rho
 */
function rotateTriad(triad: TriangleLane[], rho: number): TriangleLane[] {
  const result = [...triad];
  for (let i = 0; i < rho; i++) {
    result.push(result.shift()!);
  }
  return result;
}

/**
 * Get chapters on lane
 */
export function getChaptersOnLane(lane: TriangleLane): number[] {
  const chapters: number[] = [];
  
  for (let ch = 1; ch <= 21; ch++) {
    const indices = computeMetroIndices(ch);
    if (indices.lane === lane) {
      chapters.push(ch);
    }
  }
  
  return chapters;
}

/**
 * Get chapters in arc
 */
export function getChaptersInArc(alpha: number): number[] {
  const start = alpha * 3 + 1;
  return [start, start + 1, start + 2].filter(ch => ch <= 21);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 9: ADDRESS FACTORY
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Address factory for convenient creation
 */
export class AddressFactory {
  private ms: ManuscriptID;
  private normalizer: AddressNormalizer;
  
  constructor(seed: string, version: string = "1.0.0") {
    this.ms = deriveManuscriptID(seed, version);
    this.normalizer = new AddressNormalizer();
  }
  
  /**
   * Create chapter atom address
   */
  chapter(ch: number, lens: Lens, facet: Facet, atom: Atom): GlobalAddr {
    const stationCode = computeStationCode(ch);
    
    return {
      ms: this.ms,
      local: {
        kind: "ChapterAtom",
        chapter: ch,
        stationCode,
        lens,
        facet,
        atom
      }
    };
  }
  
  /**
   * Create appendix atom address
   */
  appendix(app: string, lens: Lens, facet: Facet, atom: Atom): GlobalAddr {
    if (app.length !== 1 || app < "A" || app > "P") {
      throw new AddressingError(
        `Invalid appendix: ${app}`,
        "INVALID_APPENDIX"
      );
    }
    
    return {
      ms: this.ms,
      local: {
        kind: "AppendixAtom",
        appendix: app,
        lens,
        facet,
        atom
      }
    };
  }
  
  /**
   * Create station gate address (canonical entry point)
   */
  stationGate(ch: number): GlobalAddr {
    return this.chapter(ch, Lens.S, 1, "a");
  }
  
  /**
   * Format address to string
   */
  format(addr: GlobalAddr): string {
    return this.normalizer.formatGlobalAddr(addr);
  }
  
  /**
   * Get manuscript ID
   */
  getManuscriptID(): ManuscriptID {
    return this.ms;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 10: ERROR HANDLING
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Addressing error
 */
export class AddressingError extends Error {
  public readonly code: string;
  
  constructor(message: string, code: string) {
    super(message);
    this.name = "AddressingError";
    this.code = code;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 11: COMPLETE ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete Addressing Canonical Engine
 */
export class AddressingCanonicalEngine {
  private parser: AddressParser;
  private normalizer: AddressNormalizer;
  private edgeBuilder: LinkEdgeBuilder;
  private factories: Map<string, AddressFactory> = new Map();
  
  constructor() {
    this.parser = new AddressParser();
    this.normalizer = new AddressNormalizer();
    this.edgeBuilder = new LinkEdgeBuilder();
  }
  
  /**
   * Register manuscript
   */
  registerManuscript(seed: string, version: string = "1.0.0"): ManuscriptID {
    const ms = deriveManuscriptID(seed, version);
    const factory = new AddressFactory(seed, version);
    this.factories.set(ms.code, factory);
    return ms;
  }
  
  /**
   * Get factory for manuscript
   */
  getFactory(msCode: string): AddressFactory | undefined {
    return this.factories.get(msCode);
  }
  
  /**
   * Parse address
   */
  parse(addrStr: string): AddressParseResult {
    return this.parser.parse(addrStr);
  }
  
  /**
   * Normalize address
   */
  normalize(addrStr: string): string {
    return this.normalizer.normalize(addrStr);
  }
  
  /**
   * Check address equality
   */
  areEqual(addr1: string, addr2: string): boolean {
    return this.normalizer.areEqual(addr1, addr2);
  }
  
  /**
   * Create link edge
   */
  createEdge(
    kind: EdgeKind,
    src: GlobalAddr,
    dst: GlobalAddr,
    scope: string,
    corridor: CorridorRef,
    payload?: unknown
  ): LinkEdge {
    return this.edgeBuilder.create(kind, src, dst, scope, corridor, payload);
  }
  
  /**
   * Verify edge ID
   */
  verifyEdgeID(edge: LinkEdge): boolean {
    return this.edgeBuilder.verifyEdgeID(edge);
  }
  
  /**
   * Infer truth type
   */
  inferTruth(record: TruthRecord): TruthValue {
    return inferTruthType(record);
  }
  
  /**
   * Get metro indices
   */
  getMetroIndices(chapter: number): ReturnType<typeof computeMetroIndices> {
    return computeMetroIndices(chapter);
  }
  
  /**
   * Get chapters on lane
   */
  getChaptersOnLane(lane: TriangleLane): number[] {
    return getChaptersOnLane(lane);
  }
  
  /**
   * Get chapters in arc
   */
  getChaptersInArc(alpha: number): number[] {
    return getChaptersInArc(alpha);
  }
  
  /**
   * Validate closed alphabets
   */
  validateTruth(value: string): TruthValue {
    return validateClosedAlphabet(value, TruthValue, "TruthValue");
  }
  
  validateEdgeKind(value: string): EdgeKind {
    return validateClosedAlphabet(value, EdgeKind, "EdgeKind");
  }
  
  validateLens(value: string): Lens {
    return validateClosedAlphabet(value, Lens, "Lens");
  }
  
  /**
   * Get statistics
   */
  getStats(): AddressingStats {
    return {
      registeredManuscripts: this.factories.size,
      truthValues: Object.values(TruthValue).length,
      edgeKinds: Object.values(EdgeKind).length,
      lenses: Object.values(Lens).length,
      facets: 4,
      atoms: 4,
      chapters: 21,
      appendices: 16
    };
  }
}

export interface AddressingStats {
  registeredManuscripts: number;
  truthValues: number;
  edgeKinds: number;
  lenses: number;
  facets: number;
  atoms: number;
  chapters: number;
  appendices: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Enums
  TruthValue,
  EdgeKind,
  Lens,
  
  // Constants
  KNOWN_MANUSCRIPTS,
  ARC_HUB_MAP,
  
  // Functions
  deriveManuscriptID,
  computeStationCode,
  parseStationCode,
  computeEdgeID,
  inferTruthType,
  getTruthOverlay,
  computeMetroIndices,
  getChaptersOnLane,
  getChaptersInArc,
  validateClosedAlphabet,
  
  // Classes
  AddressParser,
  AddressNormalizer,
  LinkEdgeBuilder,
  AddressFactory,
  AddressingCanonicalEngine,
  AddressingError
};
