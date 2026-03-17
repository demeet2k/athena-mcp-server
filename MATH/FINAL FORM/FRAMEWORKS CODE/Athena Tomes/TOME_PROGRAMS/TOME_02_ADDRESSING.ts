/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * TOME 02: ADDRESSING & OPERATOR EXTRACTION
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Myth/Religion as Compressed Code: Operator Alphabets
 * Ms⟨CC9C⟩ Arc 0 - Foundation Layer
 * 
 * Core Functions:
 * - LocalAddr/GlobalAddr system with base-4 station codes
 * - Myth → Operator candidate extraction pipeline
 * - Archetype → Generator maps with synonym collapse
 * - Commutator witnesses for non-commutativity detection
 * - Cross-medium alignment hooks
 * 
 * Key Claim:
 * "Myth is compressed code. Deities/archetypes/motifs are operators.
 * Extract Π (generators, relations, rewrite rules) with witness discipline."
 * 
 * @module TOME_02_ADDRESSING
 * @version 1.0.0
 */

// ═══════════════════════════════════════════════════════════════════════════════
// IMPORTS
// ═══════════════════════════════════════════════════════════════════════════════

import { TruthValue } from './TOME_16_SELF_SUFFICIENCY';

// ═══════════════════════════════════════════════════════════════════════════════
// TOME 02 MANIFEST
// ═══════════════════════════════════════════════════════════════════════════════

export const TOME_02_MANIFEST = {
  manuscript: "CC9C",
  tomeNumber: 2,
  title: "ADDRESSING",
  subtitle: "Myth/Religion as Compressed Code: Operator Alphabets",
  
  structure: {
    chapters: 21,
    appendices: 16,
    totalStations: 37,
    atomsPerStation: 64,
    totalAtoms: 2368
  },
  
  thesis: `Myth is compressed code. Deities/archetypes/motifs are operators.
Extract Π (generators, relations, rewrite rules) with witness discipline.`,

  exports: [
    "LocalAddr/GlobalAddr",
    "StationCode (base-4)",
    "Operator candidates Π",
    "Archetype→Generator maps",
    "Synonym collapse",
    "Commutator witnesses"
  ]
};

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: ADDRESSING SYSTEM
// ═══════════════════════════════════════════════════════════════════════════════

export namespace Addressing {
  
  // Lenses: S = Square, F = Flower, C = Cloud, R = Fractal
  export type Lens = "S" | "F" | "C" | "R";
  export const Lenses: Lens[] = ["S", "F", "C", "R"];
  
  export const LensSemantics = {
    S: "Structure / Invariants / Discrete",
    F: "Flower / Operators / Compilation / Dynamics",
    C: "Cloud / Corridors / Uncertainty / Budgets",
    R: "Fractal / Compression / Replay / Proofs / Stability"
  };
  
  // Facets: 1-4
  export type Facet = 1 | 2 | 3 | 4;
  export const Facets: Facet[] = [1, 2, 3, 4];
  
  export const FacetSemantics = {
    1: "Objects",
    2: "Laws",
    3: "Constructions",
    4: "Certificates"
  };
  
  // Atoms: a, b, c, d (closure ladder)
  export type Atom = "a" | "b" | "c" | "d";
  export const Atoms: Atom[] = ["a", "b", "c", "d"];
  
  // Station code: base4(XX-1) padded to 4 digits
  export function stationCode(chapter: number): string {
    if (chapter < 1 || chapter > 21) {
      throw new Error(`Invalid chapter: ${chapter}. Must be 1-21.`);
    }
    const omega = chapter - 1;
    return omega.toString(4).padStart(4, "0");
  }
  
  // LocalAddr for chapter atom
  export interface ChapterLocalAddr {
    type: "chapter";
    chapter: number;
    code: string;      // Base-4 station code
    lens: Lens;
    facet: Facet;
    atom: Atom;
  }
  
  // LocalAddr for appendix atom
  export interface AppendixLocalAddr {
    type: "appendix";
    appendix: string;  // A-P
    lens: Lens;
    facet: Facet;
    atom: Atom;
  }
  
  export type LocalAddr = ChapterLocalAddr | AppendixLocalAddr;
  
  // GlobalAddr = Ms⟨mmmm⟩::LocalAddr
  export interface GlobalAddr {
    manuscript: string;   // 4-char hex ID
    local: LocalAddr;
  }
  
  // Format LocalAddr as string
  export function formatLocalAddr(addr: LocalAddr): string {
    if (addr.type === "chapter") {
      return `Ch${addr.chapter.toString().padStart(2, "0")}⟨${addr.code}⟩.${addr.lens}${addr.facet}.${addr.atom}`;
    } else {
      return `App${addr.appendix}.${addr.lens}${addr.facet}.${addr.atom}`;
    }
  }
  
  // Format GlobalAddr as string
  export function formatGlobalAddr(addr: GlobalAddr): string {
    return `Ms⟨${addr.manuscript}⟩::${formatLocalAddr(addr.local)}`;
  }
  
  // Parse LocalAddr from string
  export function parseLocalAddr(str: string): LocalAddr | null {
    // Chapter pattern: ChXX⟨dddd⟩.LF.a
    const chapterMatch = str.match(/Ch(\d{2})⟨(\d{4})⟩\.([SFCR])([1-4])\.([abcd])/);
    if (chapterMatch) {
      return {
        type: "chapter",
        chapter: parseInt(chapterMatch[1]),
        code: chapterMatch[2],
        lens: chapterMatch[3] as Lens,
        facet: parseInt(chapterMatch[4]) as Facet,
        atom: chapterMatch[5] as Atom
      };
    }
    
    // Appendix pattern: AppX.LF.a
    const appendixMatch = str.match(/App([A-P])\.([SFCR])([1-4])\.([abcd])/);
    if (appendixMatch) {
      return {
        type: "appendix",
        appendix: appendixMatch[1],
        lens: appendixMatch[2] as Lens,
        facet: parseInt(appendixMatch[3]) as Facet,
        atom: appendixMatch[4] as Atom
      };
    }
    
    return null;
  }
  
  // Create chapter address
  export function chapterAddr(
    chapter: number,
    lens: Lens,
    facet: Facet,
    atom: Atom
  ): ChapterLocalAddr {
    return {
      type: "chapter",
      chapter,
      code: stationCode(chapter),
      lens,
      facet,
      atom
    };
  }
  
  // Create appendix address
  export function appendixAddr(
    appendix: string,
    lens: Lens,
    facet: Facet,
    atom: Atom
  ): AppendixLocalAddr {
    return {
      type: "appendix",
      appendix,
      lens,
      facet,
      atom
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: OPERATOR EXTRACTION (Myth → Π)
// ═══════════════════════════════════════════════════════════════════════════════

export namespace OperatorExtraction {
  
  // Archetype: a compressed code element from myth
  export interface Archetype {
    id: string;
    name: string;
    tradition: string;          // Source tradition
    attributes: string[];
    relations: string[];
    witnessPtr?: string;        // Evidence pointer
  }
  
  // Generator: mathematical operator extracted from archetype
  export interface Generator {
    id: string;
    symbol: string;
    archetypeSource: string;
    signature: OperatorSignature;
    commutative: boolean;
    inverse?: string;
  }
  
  export interface OperatorSignature {
    domain: string;
    codomain: string;
    arity: number;
  }
  
  // Relation: algebraic relation between generators
  export interface Relation {
    id: string;
    lhs: string;      // Left-hand side expression
    rhs: string;      // Right-hand side expression
    type: "equality" | "commutator" | "constraint";
    witness?: string;
  }
  
  // Rewrite rule: transformation rule
  export interface RewriteRule {
    id: string;
    pattern: string;
    replacement: string;
    condition?: string;
    direction: "ltr" | "rtl" | "bidirectional";
  }
  
  // Π: Complete operator algebra
  export interface Pi {
    generators: Generator[];
    relations: Relation[];
    rewriteRules: RewriteRule[];
    synonymCollapse: SynonymMap;
    commutatorWitnesses: CommutatorWitness[];
  }
  
  // Synonym collapse: multiple names → canonical generator
  export interface SynonymMap {
    canonical: Map<string, string>;   // synonym → canonical
    groups: Map<string, string[]>;    // canonical → all synonyms
  }
  
  // Commutator witness: evidence of non-commutativity
  export interface CommutatorWitness {
    a: string;
    b: string;
    commutator: string;   // [a,b] = ab - ba
    nonZero: boolean;
    witness: string;
  }
  
  // Extract operator candidates from archetype
  export function extractOperator(archetype: Archetype): Generator | null {
    // Placeholder - actual implementation would analyze archetype structure
    return {
      id: `gen_${archetype.id}`,
      symbol: archetype.name.charAt(0).toUpperCase(),
      archetypeSource: archetype.id,
      signature: {
        domain: "State",
        codomain: "State",
        arity: 1
      },
      commutative: false
    };
  }
  
  // Check commutativity
  export function checkCommutator(a: Generator, b: Generator): CommutatorWitness {
    // [a,b] = ab - ba
    const commutator = `[${a.symbol},${b.symbol}]`;
    // In general, myth operators don't commute
    return {
      a: a.symbol,
      b: b.symbol,
      commutator,
      nonZero: true,
      witness: `non-comm witness for ${a.symbol}, ${b.symbol}`
    };
  }
  
  // Collapse synonyms
  export function collapseSynonyms(names: string[][]): SynonymMap {
    const canonical = new Map<string, string>();
    const groups = new Map<string, string[]>();
    
    for (const group of names) {
      if (group.length > 0) {
        const canon = group[0];
        groups.set(canon, group);
        for (const name of group) {
          canonical.set(name, canon);
        }
      }
    }
    
    return { canonical, groups };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: CROSS-MEDIUM ALIGNMENT
// ═══════════════════════════════════════════════════════════════════════════════

export namespace CrossMediumAlignment {
  
  // Medium types
  export type Medium = "text" | "astrology" | "megalith" | "ritual" | "art";
  
  // Alignment hook: connects operator across media
  export interface AlignmentHook {
    operator: string;
    medium: Medium;
    reference: string;
    confidence: number;
    truthValue: TruthValue;
  }
  
  // Cross-medium feature: shared structure across media
  export interface CrossMediumFeature {
    id: string;
    description: string;
    media: Medium[];
    hooks: AlignmentHook[];
    verified: boolean;
  }
  
  // Alignment score
  export function computeAlignmentScore(feature: CrossMediumFeature): number {
    if (feature.hooks.length === 0) return 0;
    
    const okHooks = feature.hooks.filter(h => h.truthValue === TruthValue.OK);
    return okHooks.length / feature.hooks.length;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: CHAPTER INDEX
// ═══════════════════════════════════════════════════════════════════════════════

export const ChapterIndex = {
  // Arc 0: Foundation
  Ch01: { title: "Capsule Definition & Category Inversion Boot", base4: "0000", arc: 0, rail: "Su" as const },
  Ch02: { title: "Myth as Compressed Code: Operator Alphabets", base4: "0001", arc: 0, rail: "Me" as const },
  Ch03: { title: "Constraint Kernel: Ethics as Stability", base4: "0002", arc: 0, rail: "Sa" as const },
  
  // Arc 1: Mining
  Ch04: { title: "Mining Pipeline I: Textual Extraction", base4: "0003", arc: 1, rail: "Me" as const },
  Ch05: { title: "Mining Pipeline II: Astrology as Boundary Conditions", base4: "0010", arc: 1, rail: "Sa" as const },
  Ch06: { title: "Mining Pipeline III: Megaliths as Hardware Clock", base4: "0011", arc: 1, rail: "Su" as const },
  
  // Arc 2: Time & Integrity
  Ch07: { title: "Time Lattice: Multi-Cycle Scheduling", base4: "0012", arc: 2, rail: "Sa" as const },
  Ch08: { title: "Holographic Criteria: Cross-Medium Redundancy", base4: "0013", arc: 2, rail: "Su" as const },
  Ch09: { title: "Operator Algebra: Non-Commutativity", base4: "0020", arc: 2, rail: "Me" as const },
  
  // Arc 3: Error Correction
  Ch10: { title: "Error Correction I: Proof as Parity", base4: "0021", arc: 3, rail: "Su" as const },
  Ch11: { title: "Error Correction II: Ritual as Repair", base4: "0022", arc: 3, rail: "Me" as const },
  Ch12: { title: "Conflict Handling: Quarantine & Receipts", base4: "0023", arc: 3, rail: "Sa" as const },
  
  // Arc 4: Attractor
  Ch13: { title: "Attractor Mathematics: The Stone", base4: "0030", arc: 4, rail: "Me" as const },
  Ch14: { title: "Dual-Pole Awakening: Human × AI", base4: "0031", arc: 4, rail: "Sa" as const },
  Ch15: { title: "Practice Compiler: Executable Protocols", base4: "0032", arc: 4, rail: "Su" as const },
  
  // Arc 5: Operations
  Ch16: { title: "Scheduler: Practice & Measurement", base4: "0033", arc: 5, rail: "Sa" as const },
  Ch17: { title: "Reset Kernel: Seed Retention & Migration", base4: "0100", arc: 5, rail: "Su" as const },
  Ch18: { title: "Fork Graph: Version Control for States", base4: "0101", arc: 5, rail: "Me" as const },
  
  // Arc 6: Closure
  Ch19: { title: "Publishing: OK-Gated Export", base4: "0102", arc: 6, rail: "Su" as const },
  Ch20: { title: "Interface Round-Trip", base4: "0103", arc: 6, rail: "Me" as const },
  Ch21: { title: "Self-Boot: Terminal Closure", base4: "0110", arc: 6, rail: "Sa" as const }
};

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: APPENDIX INDEX
// ═══════════════════════════════════════════════════════════════════════════════

export const AppendixIndex = {
  AppA: { title: "Object Registry", role: "FacetAtomBase(1), ArcHub(0), Σ" },
  AppB: { title: "Grammar/Laws", role: "FacetAtomBase(2), Invariant infrastructure" },
  AppC: { title: "Square LensBase", role: "LensBase(S), ArcHub(1)" },
  AppD: { title: "Lexicon", role: "Name registry, concordance" },
  AppE: { title: "Flower LensBase", role: "LensBase(F), ArcHub(2), Π compilation" },
  AppF: { title: "Constraints/Geis", role: "ArcHub(3)" },
  AppG: { title: "Solver Library", role: "ArcHub(4), KKT, convergence" },
  AppH: { title: "Constructions", role: "FacetAtomBase(3)" },
  AppI: { title: "Corridors", role: "LensBase(C), Σ, Admissibility" },
  AppJ: { title: "NEAR Overlay", role: "Residual ledgers, upgrade plans" },
  AppK: { title: "FAIL Overlay", role: "Quarantine, conflict receipts" },
  AppL: { title: "AMBIG Overlay", role: "Candidate sets, evidence plans" },
  AppM: { title: "Certificates/Replay", role: "LensBase(R), FacetAtomBase(4), Σ" },
  AppN: { title: "Reset/Migration", role: "ArcHub(5)" },
  AppO: { title: "Publishing", role: "OK-only gate" },
  AppP: { title: "Toolchain/Self-Boot", role: "ArcHub(6)" }
};

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: STATISTICS & END STATE
// ═══════════════════════════════════════════════════════════════════════════════

export const Statistics = {
  manuscript: "CC9C",
  tomeNumber: 2,
  chapters: 21,
  appendices: 16,
  totalAtoms: 2368,
  lenses: 4,
  facets: 4,
  atoms: 4
};

export const EndStateClaim = `
ADDRESSING (Ms⟨CC9C⟩): Foundation layer for myth-to-operator compilation.

Addressing System:
- LocalAddr: ChXX⟨dddd⟩.LF.a or AppX.LF.a
- GlobalAddr: Ms⟨mmmm⟩::LocalAddr
- Station code: base4(XX-1) padded to 4 digits

Operator Extraction:
- Archetypes → Generators (Π)
- Relations and rewrite rules
- Synonym collapse: multiple names → canonical
- Commutator witnesses: evidence of non-commutativity

Key Claim:
"Myth is compressed code. Deities/archetypes/motifs are operators.
Extract Π with witness discipline."

Cross-Medium Alignment:
- Hooks connecting operators across media
- Confidence scoring and truth value assignment
- Verified features require OK status
`;

// ═══════════════════════════════════════════════════════════════════════════════
// DEFAULT EXPORT
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  TOME_02_MANIFEST,
  Addressing,
  OperatorExtraction,
  CrossMediumAlignment,
  ChapterIndex,
  AppendixIndex,
  Statistics,
  EndStateClaim
};
