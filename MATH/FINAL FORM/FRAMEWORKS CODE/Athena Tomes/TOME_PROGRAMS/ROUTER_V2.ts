/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * ROUTER V2 - Complete Hub-Based Routing System
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Implementation of the deterministic router with bounded hubs (≤6):
 * 
 * Components:
 *   - Σ Anchors: {AppA, AppI, AppM} - mandatory entry
 *   - LensBase: {AppC, AppE, AppI, AppM} - lens routing
 *   - FacetBase: {AppA, AppB, AppH, AppM} - facet routing
 *   - ArcHub: {AppA, AppC, AppE, AppF, AppG, AppN, AppP} - chapter arcs
 *   - Overlays: {AppJ, AppL, AppK, AppO} - truth overlays
 * 
 * Rails (Su/Me/Sa): Deterministic lane assignment based on chapter index
 * 
 * @module ROUTER_V2
 * @version 2.0.0
 */

import { TruthValue, EdgeKind } from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: APPENDIX CRYSTAL STRUCTURE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Appendix identifiers (A-P)
 */
export enum Appendix {
  AppA = "AppA",
  AppB = "AppB",
  AppC = "AppC",
  AppD = "AppD",
  AppE = "AppE",
  AppF = "AppF",
  AppG = "AppG",
  AppH = "AppH",
  AppI = "AppI",
  AppJ = "AppJ",
  AppK = "AppK",
  AppL = "AppL",
  AppM = "AppM",
  AppN = "AppN",
  AppO = "AppO",
  AppP = "AppP"
}

/**
 * Appendix roles and responsibilities
 */
export const APPENDIX_ROLES: Record<Appendix, AppendixRole> = {
  [Appendix.AppA]: {
    name: "Object Gate",
    description: "Schemas, station gates, edge schema; required entry anchor",
    functions: ["schemas", "station_gates", "edge_schema"],
    isSigma: true,
    isLensBase: false,
    isFacetBase: true,
    facet: 1
  },
  [Appendix.AppB]: {
    name: "Laws & Invariants",
    description: "Laws, invariants, admissibility, budgets",
    functions: ["laws", "invariants", "admissibility", "budgets"],
    isSigma: false,
    isLensBase: false,
    isFacetBase: true,
    facet: 2
  },
  [Appendix.AppC]: {
    name: "Truth Discipline",
    description: "Truth discipline, overlays, lint, promotion gate",
    functions: ["truth_discipline", "overlays", "lint", "promotion"],
    isSigma: false,
    isLensBase: true,
    lens: "S",
    isFacetBase: false
  },
  [Appendix.AppD]: {
    name: "Reserved",
    description: "Reserved for future use",
    functions: [],
    isSigma: false,
    isLensBase: false,
    isFacetBase: false
  },
  [Appendix.AppE]: {
    name: "Dynamics",
    description: "Dynamics operators, oscillation, anneal, attractors",
    functions: ["dynamics", "oscillation", "anneal", "attractors"],
    isSigma: false,
    isLensBase: true,
    lens: "F",
    isFacetBase: false
  },
  [Appendix.AppF]: {
    name: "Router Rules",
    description: "Router v2 specification, hub maps",
    functions: ["router_spec", "hub_maps"],
    isSigma: false,
    isLensBase: false,
    isFacetBase: false
  },
  [Appendix.AppG]: {
    name: "Transitions",
    description: "State transitions, protocol handlers",
    functions: ["transitions", "protocols"],
    isSigma: false,
    isLensBase: false,
    isFacetBase: false
  },
  [Appendix.AppH]: {
    name: "Constructions",
    description: "Build pipelines, emulation, generation",
    functions: ["pipelines", "emulation", "generation"],
    isSigma: false,
    isLensBase: false,
    isFacetBase: true,
    facet: 3
  },
  [Appendix.AppI]: {
    name: "Candidates & Evidence",
    description: "Candidate/evidence hub, ambiguity discipline, evidence artifacts",
    functions: ["candidates", "evidence", "ambiguity"],
    isSigma: true,
    isLensBase: true,
    lens: "C",
    isFacetBase: false
  },
  [Appendix.AppJ]: {
    name: "NEAR Overlay",
    description: "NEAR residuals, upgrade plans",
    functions: ["near_residuals", "upgrade_plans"],
    isSigma: false,
    isLensBase: false,
    isFacetBase: false,
    overlay: TruthValue.NEAR
  },
  [Appendix.AppK]: {
    name: "FAIL Overlay",
    description: "FAIL quarantine, isolation, conflict receipts",
    functions: ["quarantine", "isolation", "conflicts"],
    isSigma: false,
    isLensBase: false,
    isFacetBase: false,
    overlay: TruthValue.FAIL
  },
  [Appendix.AppL]: {
    name: "AMBIG Overlay",
    description: "AMBIG candidates, evidence plans",
    functions: ["ambig_candidates", "evidence_plans"],
    isSigma: false,
    isLensBase: false,
    isFacetBase: false,
    overlay: TruthValue.AMBIG
  },
  [Appendix.AppM]: {
    name: "Codecs & Replay",
    description: "Codecs, digests, replay capsules, clean verifier, certificates",
    functions: ["codecs", "digests", "replay", "verifier", "certificates"],
    isSigma: true,
    isLensBase: true,
    lens: "R",
    isFacetBase: true,
    facet: 4
  },
  [Appendix.AppN]: {
    name: "Namespace",
    description: "Cross-tome namespace, weave plans",
    functions: ["namespace", "weave_plans"],
    isSigma: false,
    isLensBase: false,
    isFacetBase: false
  },
  [Appendix.AppO]: {
    name: "OK Publish",
    description: "OK-publish, import/export, reproducibility bundles",
    functions: ["publish", "import_export", "repro_bundles"],
    isSigma: false,
    isLensBase: false,
    isFacetBase: false,
    overlay: TruthValue.OK,
    publishOnly: true
  },
  [Appendix.AppP]: {
    name: "Terminal",
    description: "Terminal seal, orbit closure",
    functions: ["seal", "closure"],
    isSigma: false,
    isLensBase: false,
    isFacetBase: false
  }
};

export interface AppendixRole {
  name: string;
  description: string;
  functions: string[];
  isSigma: boolean;
  isLensBase: boolean;
  lens?: string;
  isFacetBase: boolean;
  facet?: number;
  overlay?: TruthValue;
  publishOnly?: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: SIGMA, LENS, FACET, ARC MAPPINGS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Σ (Sigma) anchors - mandatory starting sequence
 */
export const SIGMA: Appendix[] = [Appendix.AppA, Appendix.AppI, Appendix.AppM];

/**
 * Lens to base appendix mapping
 */
export const LENS_BASE: Record<string, Appendix> = {
  "S": Appendix.AppC,  // Square - Truth
  "F": Appendix.AppE,  // Flower - Dynamics
  "C": Appendix.AppI,  // Cloud - Uncertainty
  "R": Appendix.AppM   // Fractal - Replay
};

/**
 * Facet to base appendix mapping
 */
export const FACET_BASE: Record<number, Appendix> = {
  1: Appendix.AppA,  // Objects and constructors
  2: Appendix.AppB,  // Laws/invariants/admissibility
  3: Appendix.AppH,  // Constructions/pipelines
  4: Appendix.AppM   // Certificates/replay proofs
};

/**
 * Arc (α) to hub appendix mapping
 */
export const ARC_HUB: Record<number, Appendix> = {
  0: Appendix.AppA,
  1: Appendix.AppC,
  2: Appendix.AppE,
  3: Appendix.AppF,
  4: Appendix.AppG,
  5: Appendix.AppN,
  6: Appendix.AppP
};

/**
 * Truth overlay mapping
 */
export const TRUTH_OVERLAY: Record<TruthValue, Appendix | null> = {
  [TruthValue.OK]: null,      // No overlay for OK (use AppO only for publish)
  [TruthValue.NEAR]: Appendix.AppJ,
  [TruthValue.AMBIG]: Appendix.AppL,
  [TruthValue.FAIL]: Appendix.AppK
};

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: RAILS AND TRIADS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Rail types (Su/Me/Sa)
 */
export enum Rail {
  Su = "Su",  // Sun
  Me = "Me",  // Mercury
  Sa = "Sa"   // Saturn
}

/**
 * Triad rotation
 */
export const TRIAD: Rail[] = [Rail.Su, Rail.Me, Rail.Sa];

/**
 * Compute rail assignment for chapter
 * 
 * For chapter index XX ∈ {01..21}:
 *   ω = XX - 1
 *   α = floor(ω / 3)
 *   k = ω mod 3
 *   ρ = α mod 3
 *   ν = Triad[(k + ρ) mod 3]
 */
export function computeRail(chapter: number): Rail {
  if (chapter < 1 || chapter > 21) {
    throw new Error(`Invalid chapter: ${chapter}. Must be 1-21.`);
  }
  
  const omega = chapter - 1;
  const alpha = Math.floor(omega / 3);
  const k = omega % 3;
  const rho = alpha % 3;
  const index = (k + rho) % 3;
  
  return TRIAD[index];
}

/**
 * Compute arc for chapter
 */
export function computeArc(chapter: number): number {
  if (chapter < 1 || chapter > 21) {
    throw new Error(`Invalid chapter: ${chapter}. Must be 1-21.`);
  }
  return Math.floor((chapter - 1) / 3);
}

/**
 * Get chapters on a specific rail
 */
export function getChaptersOnRail(rail: Rail): number[] {
  const chapters: number[] = [];
  for (let ch = 1; ch <= 21; ch++) {
    if (computeRail(ch) === rail) {
      chapters.push(ch);
    }
  }
  return chapters;
}

/**
 * Rail assignments for all chapters
 */
export const RAIL_ASSIGNMENTS: Record<Rail, number[]> = {
  [Rail.Su]: getChaptersOnRail(Rail.Su),
  [Rail.Me]: getChaptersOnRail(Rail.Me),
  [Rail.Sa]: getChaptersOnRail(Rail.Sa)
};

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: ADDRESS SYSTEM
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Lens types
 */
export type Lens = "S" | "F" | "C" | "R";

/**
 * Facet types
 */
export type Facet = 1 | 2 | 3 | 4;

/**
 * Atom types within a tile
 */
export type Atom = "a" | "b" | "c" | "d";

/**
 * Local address for chapters
 */
export interface ChapterAddress {
  type: "chapter";
  chapter: number;        // 1-21
  stationCode: string;    // Base-4, 4 digits (e.g., "0000" for Ch01)
  lens: Lens;
  facet: Facet;
  atom: Atom;
}

/**
 * Local address for appendices
 */
export interface AppendixAddress {
  type: "appendix";
  appendix: Appendix;
  lens: Lens;
  facet: Facet;
  atom: Atom;
}

export type LocalAddress = ChapterAddress | AppendixAddress;

/**
 * Global address
 */
export interface GlobalAddress {
  msId: string;           // e.g., "B83A"
  local: LocalAddress;
}

/**
 * Convert chapter number to base-4 station code
 */
export function toStationCode(chapter: number): string {
  const n = chapter - 1;
  const digits: string[] = [];
  let remaining = n;
  
  for (let i = 0; i < 4; i++) {
    digits.unshift(String(remaining % 4));
    remaining = Math.floor(remaining / 4);
  }
  
  return digits.join("");
}

/**
 * Parse station code to chapter number
 */
export function fromStationCode(code: string): number {
  let n = 0;
  for (let i = 0; i < code.length; i++) {
    n = n * 4 + parseInt(code[i], 10);
  }
  return n + 1;
}

/**
 * Render local address to string
 */
export function renderLocalAddress(addr: LocalAddress): string {
  if (addr.type === "chapter") {
    return `Ch${addr.chapter.toString().padStart(2, "0")}⟨${addr.stationCode}⟩.${addr.lens}${addr.facet}.${addr.atom}`;
  } else {
    return `${addr.appendix}.${addr.lens}${addr.facet}.${addr.atom}`;
  }
}

/**
 * Render global address to string
 */
export function renderGlobalAddress(addr: GlobalAddress): string {
  return `Ms⟨${addr.msId}⟩::${renderLocalAddress(addr.local)}`;
}

/**
 * Parse local address string
 */
export function parseLocalAddress(str: string): LocalAddress | null {
  // Chapter pattern: ChXX⟨dddd⟩.LF.a
  const chapterPattern = /^Ch(\d{2})⟨([0-3]{4})⟩\.([SFCR])([1-4])\.([abcd])$/;
  const chMatch = str.match(chapterPattern);
  if (chMatch) {
    return {
      type: "chapter",
      chapter: parseInt(chMatch[1], 10),
      stationCode: chMatch[2],
      lens: chMatch[3] as Lens,
      facet: parseInt(chMatch[4], 10) as Facet,
      atom: chMatch[5] as Atom
    };
  }
  
  // Appendix pattern: AppX.LF.a
  const appendixPattern = /^(App[A-P])\.([SFCR])([1-4])\.([abcd])$/;
  const appMatch = str.match(appendixPattern);
  if (appMatch) {
    return {
      type: "appendix",
      appendix: appMatch[1] as Appendix,
      lens: appMatch[2] as Lens,
      facet: parseInt(appMatch[3], 10) as Facet,
      atom: appMatch[4] as Atom
    };
  }
  
  return null;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: ROUTING ALGORITHM
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Route request
 */
export interface RouteRequest {
  src: GlobalAddress;
  dst: GlobalAddress;
  truth: TruthValue;
  publishIntent: boolean;
}

/**
 * Route result
 */
export interface RouteResult {
  success: boolean;
  hubs: Appendix[];
  hubCount: number;
  budgetOk: boolean;
  deduped: boolean;
  compressed: boolean;
  details: RouteDetails;
}

export interface RouteDetails {
  sigma: Appendix[];
  arcHub?: Appendix;
  lensBase: Appendix;
  facetBase: Appendix;
  overlay?: Appendix;
  publishHub?: Appendix;
  rawHubs: Appendix[];
  dedupedHubs: Appendix[];
  finalHubs: Appendix[];
}

/**
 * Maximum hub count
 */
export const MAX_HUBS = 6;

/**
 * Compute route between source and destination
 */
export function computeRoute(request: RouteRequest): RouteResult {
  const { src, dst, truth, publishIntent } = request;
  
  // Step 1: Start with Σ
  const rawHubs: Appendix[] = [...SIGMA];
  
  // Step 2: Add ArcHub if destination is chapter
  let arcHub: Appendix | undefined;
  if (dst.local.type === "chapter") {
    const arc = computeArc(dst.local.chapter);
    arcHub = ARC_HUB[arc];
    rawHubs.push(arcHub);
  }
  
  // Step 3: Add LensBase
  const lensBase = LENS_BASE[dst.local.lens];
  rawHubs.push(lensBase);
  
  // Step 4: Add FacetBase
  const facetBase = FACET_BASE[dst.local.facet];
  rawHubs.push(facetBase);
  
  // Step 5: Add overlay hub if truth ∈ {NEAR, AMBIG, FAIL}
  let overlay: Appendix | undefined;
  if (truth !== TruthValue.OK) {
    overlay = TRUTH_OVERLAY[truth] ?? undefined;
    if (overlay) {
      rawHubs.push(overlay);
    }
  }
  
  // Step 6: Add AppO if publishing OK
  let publishHub: Appendix | undefined;
  if (truth === TruthValue.OK && publishIntent) {
    publishHub = Appendix.AppO;
    rawHubs.push(publishHub);
  }
  
  // Step 7: Dedup
  const dedupedHubs = dedup(rawHubs);
  
  // Step 8: Compress if needed
  let finalHubs = dedupedHubs;
  let compressed = false;
  
  if (dedupedHubs.length > MAX_HUBS) {
    finalHubs = compressHubs(dedupedHubs, arcHub, overlay, publishHub);
    compressed = true;
  }
  
  const budgetOk = finalHubs.length <= MAX_HUBS;
  
  return {
    success: budgetOk,
    hubs: finalHubs,
    hubCount: finalHubs.length,
    budgetOk,
    deduped: rawHubs.length !== dedupedHubs.length,
    compressed,
    details: {
      sigma: SIGMA,
      arcHub,
      lensBase,
      facetBase,
      overlay,
      publishHub,
      rawHubs,
      dedupedHubs,
      finalHubs
    }
  };
}

/**
 * Deduplicate hub sequence while preserving order
 */
function dedup(hubs: Appendix[]): Appendix[] {
  const seen = new Set<Appendix>();
  const result: Appendix[] = [];
  
  for (const hub of hubs) {
    if (!seen.has(hub)) {
      seen.add(hub);
      result.push(hub);
    }
  }
  
  return result;
}

/**
 * Compress hub sequence if over budget
 * 
 * Priority (keep in order):
 * 1. Σ hubs (all)
 * 2. Overlay hub (if any)
 * 3. AppO (if publishing)
 * 4. ArcHub (if present)
 * 5. LensBase
 * 
 * Drop (in order):
 * 1. FacetBase first
 * 2. Any hub duplicating Σ or ArcHub/LensBase
 */
function compressHubs(
  hubs: Appendix[],
  arcHub?: Appendix,
  overlay?: Appendix,
  publishHub?: Appendix
): Appendix[] {
  // Priority hubs that must stay
  const mustKeep = new Set<Appendix>(SIGMA);
  if (overlay) mustKeep.add(overlay);
  if (publishHub) mustKeep.add(publishHub);
  if (arcHub) mustKeep.add(arcHub);
  
  // Start with must-keep hubs in order
  const result: Appendix[] = [];
  const added = new Set<Appendix>();
  
  for (const hub of hubs) {
    if (mustKeep.has(hub) && !added.has(hub)) {
      result.push(hub);
      added.add(hub);
    }
  }
  
  // Add remaining hubs up to budget
  for (const hub of hubs) {
    if (result.length >= MAX_HUBS) break;
    if (!added.has(hub)) {
      result.push(hub);
      added.add(hub);
    }
  }
  
  return result;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: ROUTE VERIFICATION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Verify a route is valid
 */
export function verifyRoute(route: RouteResult): RouteVerification {
  const issues: string[] = [];
  
  // Check budget
  if (route.hubCount > MAX_HUBS) {
    issues.push(`Hub count ${route.hubCount} exceeds maximum ${MAX_HUBS}`);
  }
  
  // Check Σ present
  for (const sigma of SIGMA) {
    if (!route.hubs.includes(sigma)) {
      issues.push(`Missing required Σ hub: ${sigma}`);
    }
  }
  
  // Check Σ order
  const sigmaIndices = SIGMA.map(s => route.hubs.indexOf(s));
  for (let i = 1; i < sigmaIndices.length; i++) {
    if (sigmaIndices[i] < sigmaIndices[i - 1]) {
      issues.push(`Σ hubs out of order: ${SIGMA[i-1]} should precede ${SIGMA[i]}`);
    }
  }
  
  // Check no duplicates
  const seen = new Set<Appendix>();
  for (const hub of route.hubs) {
    if (seen.has(hub)) {
      issues.push(`Duplicate hub: ${hub}`);
    }
    seen.add(hub);
  }
  
  return {
    valid: issues.length === 0,
    issues,
    hubSequence: route.hubs.join(" → ")
  };
}

export interface RouteVerification {
  valid: boolean;
  issues: string[];
  hubSequence: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: ORBIT SYSTEM
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * 21-station orbit: Ch01 → Ch02 → ... → Ch21 → Ch01
 */
export interface OrbitStation {
  chapter: number;
  stationCode: string;
  arc: number;
  rail: Rail;
  arcHub: Appendix;
  next: number;
  prev: number;
}

/**
 * Build the complete orbit
 */
export function buildOrbit(): OrbitStation[] {
  const orbit: OrbitStation[] = [];
  
  for (let ch = 1; ch <= 21; ch++) {
    orbit.push({
      chapter: ch,
      stationCode: toStationCode(ch),
      arc: computeArc(ch),
      rail: computeRail(ch),
      arcHub: ARC_HUB[computeArc(ch)],
      next: ch === 21 ? 1 : ch + 1,
      prev: ch === 1 ? 21 : ch - 1
    });
  }
  
  return orbit;
}

/**
 * Get arc triad (3 chapters in arc)
 */
export function getArcTriad(arc: number): OrbitStation[] {
  const orbit = buildOrbit();
  return orbit.filter(s => s.arc === arc);
}

/**
 * Get all stations on orbit path from start to end
 */
export function getOrbitPath(start: number, end: number): number[] {
  const path: number[] = [start];
  let current = start;
  
  while (current !== end) {
    current = current === 21 ? 1 : current + 1;
    path.push(current);
    if (path.length > 21) break;  // Safety
  }
  
  return path;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 8: ROUTER CLASS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Router V2 implementation
 */
export class RouterV2 {
  private msId: string;
  private orbit: OrbitStation[];
  private cache: Map<string, RouteResult> = new Map();
  
  constructor(msId: string = "B83A") {
    this.msId = msId;
    this.orbit = buildOrbit();
  }
  
  /**
   * Compute route between addresses
   */
  route(
    src: LocalAddress,
    dst: LocalAddress,
    truth: TruthValue = TruthValue.OK,
    publishIntent: boolean = false
  ): RouteResult {
    const request: RouteRequest = {
      src: { msId: this.msId, local: src },
      dst: { msId: this.msId, local: dst },
      truth,
      publishIntent
    };
    
    const cacheKey = this.cacheKey(request);
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)!;
    }
    
    const result = computeRoute(request);
    this.cache.set(cacheKey, result);
    
    return result;
  }
  
  /**
   * Compute route and verify
   */
  routeAndVerify(
    src: LocalAddress,
    dst: LocalAddress,
    truth: TruthValue = TruthValue.OK,
    publishIntent: boolean = false
  ): { route: RouteResult; verification: RouteVerification } {
    const route = this.route(src, dst, truth, publishIntent);
    const verification = verifyRoute(route);
    return { route, verification };
  }
  
  /**
   * Get station info for chapter
   */
  getStation(chapter: number): OrbitStation {
    return this.orbit[chapter - 1];
  }
  
  /**
   * Get arc info
   */
  getArc(arc: number): { stations: OrbitStation[]; hub: Appendix } {
    return {
      stations: getArcTriad(arc),
      hub: ARC_HUB[arc]
    };
  }
  
  /**
   * Get all chapters on rail
   */
  getRail(rail: Rail): OrbitStation[] {
    return this.orbit.filter(s => s.rail === rail);
  }
  
  /**
   * Format route for display
   */
  formatRoute(route: RouteResult): string {
    if (!route.success) {
      return `ROUTE FAILED (${route.hubCount} hubs > ${MAX_HUBS})`;
    }
    
    return route.hubs.join(" → ");
  }
  
  /**
   * Get routing statistics
   */
  getStats(): RouterStats {
    const arcDistribution: Record<number, number> = {};
    const railDistribution: Record<Rail, number> = {
      [Rail.Su]: 0,
      [Rail.Me]: 0,
      [Rail.Sa]: 0
    };
    
    for (const station of this.orbit) {
      arcDistribution[station.arc] = (arcDistribution[station.arc] || 0) + 1;
      railDistribution[station.rail]++;
    }
    
    return {
      stationCount: 21,
      arcCount: 7,
      railCount: 3,
      maxHubs: MAX_HUBS,
      sigmaSize: SIGMA.length,
      arcDistribution,
      railDistribution,
      cacheSize: this.cache.size
    };
  }
  
  private cacheKey(request: RouteRequest): string {
    return `${renderGlobalAddress(request.src)}|${renderGlobalAddress(request.dst)}|${request.truth}|${request.publishIntent}`;
  }
}

export interface RouterStats {
  stationCount: number;
  arcCount: number;
  railCount: number;
  maxHubs: number;
  sigmaSize: number;
  arcDistribution: Record<number, number>;
  railDistribution: Record<Rail, number>;
  cacheSize: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 9: CONVENIENCE FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Create chapter address
 */
export function chapterAddr(
  chapter: number,
  lens: Lens,
  facet: Facet,
  atom: Atom
): ChapterAddress {
  return {
    type: "chapter",
    chapter,
    stationCode: toStationCode(chapter),
    lens,
    facet,
    atom
  };
}

/**
 * Create appendix address
 */
export function appendixAddr(
  appendix: Appendix,
  lens: Lens,
  facet: Facet,
  atom: Atom
): AppendixAddress {
  return {
    type: "appendix",
    appendix,
    lens,
    facet,
    atom
  };
}

/**
 * Create gate address for chapter (always S1.a)
 */
export function chapterGate(chapter: number): ChapterAddress {
  return chapterAddr(chapter, "S", 1, "a");
}

/**
 * Create gate address for appendix (always S1.a)
 */
export function appendixGate(appendix: Appendix): AppendixAddress {
  return appendixAddr(appendix, "S", 1, "a");
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Enums
  Appendix,
  Rail,
  
  // Constants
  APPENDIX_ROLES,
  SIGMA,
  LENS_BASE,
  FACET_BASE,
  ARC_HUB,
  TRUTH_OVERLAY,
  TRIAD,
  RAIL_ASSIGNMENTS,
  MAX_HUBS,
  
  // Rail functions
  computeRail,
  computeArc,
  getChaptersOnRail,
  
  // Address functions
  toStationCode,
  fromStationCode,
  renderLocalAddress,
  renderGlobalAddress,
  parseLocalAddress,
  chapterAddr,
  appendixAddr,
  chapterGate,
  appendixGate,
  
  // Routing
  computeRoute,
  verifyRoute,
  
  // Orbit
  buildOrbit,
  getArcTriad,
  getOrbitPath,
  
  // Router class
  RouterV2
};
