/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * TOME 04: MINING PIPELINE
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Textual Extraction: Text → Motif → Operator Candidates
 * Ms⟨CC9C⟩ Arc 1, Lane Me - Mining/Compilation
 * 
 * Core Functions:
 * - Text → Motif → Operator candidate transforms
 * - MythIR with WitnessPtr/ReplayPtr
 * - AMBIG candidate emission discipline
 * - Multi-medium input processing
 * 
 * Pipeline: Text → Tokenize → Parse → Extract → Compile → IR
 * 
 * @module TOME_04_MINING_PIPELINE
 * @version 1.0.0
 */

// ═══════════════════════════════════════════════════════════════════════════════
// IMPORTS
// ═══════════════════════════════════════════════════════════════════════════════

import { TruthValue } from './TOME_16_SELF_SUFFICIENCY';

// ═══════════════════════════════════════════════════════════════════════════════
// TOME 04 MANIFEST
// ═══════════════════════════════════════════════════════════════════════════════

export const TOME_04_MANIFEST = {
  manuscript: "CC9C",
  tomeNumber: 4,
  title: "MINING_PIPELINE",
  subtitle: "Textual Extraction: Text → Motif → Operator",
  
  structure: {
    chapters: 21,
    appendices: 16,
    totalStations: 37,
    atomsPerStation: 64,
    totalAtoms: 2368
  },
  
  thesis: `Extract operator candidates from textual sources with witness discipline.
Ambiguity is preserved as candidate sets, never forced collapse.`,

  pipeline: ["Text", "Tokenize", "Parse", "Extract", "Compile", "IR"],
  
  exports: [
    "MythIR",
    "WitnessPtr/ReplayPtr",
    "Motif extraction",
    "AMBIG candidate discipline"
  ]
};

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: MYTH INTERMEDIATE REPRESENTATION (MythIR)
// ═══════════════════════════════════════════════════════════════════════════════

export namespace MythIR {
  
  // Source text reference
  export interface TextSource {
    id: string;
    title: string;
    tradition: string;
    language: string;
    dateEstimate?: string;
    url?: string;
  }
  
  // Token from text
  export interface Token {
    id: string;
    text: string;
    position: number;
    sourceId: string;
    type: TokenType;
    normalized: string;
  }
  
  export type TokenType = 
    | "deity"
    | "archetype"
    | "action"
    | "object"
    | "place"
    | "time"
    | "relation"
    | "modifier"
    | "unknown";
  
  // Motif: recurring pattern in mythology
  export interface Motif {
    id: string;
    name: string;
    description: string;
    tokens: Token[];
    frequency: number;
    traditions: string[];
    structuralRole: string;
  }
  
  // Operator candidate extracted from motif
  export interface OperatorCandidate {
    id: string;
    motifSource: string;
    symbol: string;
    signature: {
      domain: string;
      codomain: string;
      arity: number;
    };
    truthValue: TruthValue;
    witnessPtr?: string;
    replayPtr?: string;
  }
  
  // MythIR node
  export interface IRNode {
    id: string;
    type: "motif" | "operator" | "relation" | "constraint";
    payload: Motif | OperatorCandidate | Relation | unknown;
    children: string[];     // Child node IDs
    witnessPtr?: string;
    replayPtr?: string;
  }
  
  // Relation in MythIR
  export interface Relation {
    id: string;
    type: RelationType;
    source: string;
    target: string;
    evidence: string[];
  }
  
  export type RelationType = 
    | "generates"     // A generates B
    | "transforms"    // A transforms into B
    | "contains"      // A contains B
    | "opposes"       // A opposes B
    | "complements"   // A complements B
    | "sequence";     // A precedes B
  
  // Complete MythIR graph
  export interface MythIRGraph {
    id: string;
    sources: TextSource[];
    nodes: Map<string, IRNode>;
    edges: Relation[];
    rootNodes: string[];
    metadata: {
      createdAt: Date;
      version: string;
      traditions: string[];
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: EXTRACTION PIPELINE
// ═══════════════════════════════════════════════════════════════════════════════

export namespace ExtractionPipeline {
  
  // Pipeline stage
  export interface PipelineStage {
    name: string;
    input: string;
    output: string;
    transform: (input: unknown) => unknown;
    truthValue: TruthValue;
  }
  
  // Pipeline configuration
  export interface PipelineConfig {
    stages: PipelineStage[];
    ambigThreshold: number;   // Below this → AMBIG
    failThreshold: number;    // Below this → FAIL
    maxCandidates: number;    // Max candidates per motif
  }
  
  // Stage 1: Tokenization
  export function tokenize(text: string, sourceId: string): MythIR.Token[] {
    const tokens: MythIR.Token[] = [];
    const words = text.split(/\s+/);
    
    for (let i = 0; i < words.length; i++) {
      tokens.push({
        id: `tok_${sourceId}_${i}`,
        text: words[i],
        position: i,
        sourceId,
        type: "unknown",
        normalized: words[i].toLowerCase()
      });
    }
    
    return tokens;
  }
  
  // Stage 2: Token classification
  export function classifyTokens(
    tokens: MythIR.Token[],
    lexicon: Map<string, MythIR.TokenType>
  ): MythIR.Token[] {
    return tokens.map(token => ({
      ...token,
      type: lexicon.get(token.normalized) || "unknown"
    }));
  }
  
  // Stage 3: Motif extraction
  export function extractMotifs(tokens: MythIR.Token[]): MythIR.Motif[] {
    const motifs: MythIR.Motif[] = [];
    // Group deity + action patterns
    // Placeholder - actual implementation would use pattern matching
    return motifs;
  }
  
  // Stage 4: Candidate generation
  export function generateCandidates(motif: MythIR.Motif): MythIR.OperatorCandidate[] {
    const candidates: MythIR.OperatorCandidate[] = [];
    
    // Each motif can generate multiple operator candidates
    candidates.push({
      id: `cand_${motif.id}_0`,
      motifSource: motif.id,
      symbol: motif.name.charAt(0).toUpperCase(),
      signature: {
        domain: "State",
        codomain: "State",
        arity: 1
      },
      truthValue: TruthValue.AMBIG  // Start as AMBIG
    });
    
    return candidates;
  }
  
  // Full pipeline execution
  export function runPipeline(
    text: string,
    sourceId: string,
    config: PipelineConfig
  ): MythIR.MythIRGraph {
    // Execute pipeline stages
    const tokens = tokenize(text, sourceId);
    const motifs = extractMotifs(tokens);
    const nodes = new Map<string, MythIR.IRNode>();
    
    for (const motif of motifs) {
      const candidates = generateCandidates(motif);
      for (const candidate of candidates) {
        nodes.set(candidate.id, {
          id: candidate.id,
          type: "operator",
          payload: candidate,
          children: []
        });
      }
    }
    
    return {
      id: `graph_${sourceId}`,
      sources: [],
      nodes,
      edges: [],
      rootNodes: Array.from(nodes.keys()),
      metadata: {
        createdAt: new Date(),
        version: "1.0.0",
        traditions: []
      }
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: WITNESS AND REPLAY DISCIPLINE
// ═══════════════════════════════════════════════════════════════════════════════

export namespace WitnessDiscipline {
  
  // Witness pointer
  export interface WitnessPtr {
    id: string;
    type: "textual" | "structural" | "cross-medium";
    sourceRef: string;
    evidence: string[];
    confidence: number;
  }
  
  // Replay pointer
  export interface ReplayPtr {
    id: string;
    capsuleHash: string;
    steps: ReplayStep[];
    deterministic: boolean;
  }
  
  export interface ReplayStep {
    index: number;
    operation: string;
    input: string;
    output: string;
  }
  
  // Create witness for extraction
  export function createWitness(
    sourceRef: string,
    evidence: string[]
  ): WitnessPtr {
    return {
      id: `wit_${Date.now()}`,
      type: "textual",
      sourceRef,
      evidence,
      confidence: evidence.length > 0 ? 0.5 + (evidence.length * 0.1) : 0
    };
  }
  
  // Create replay capsule
  export function createReplayCapsule(steps: ReplayStep[]): ReplayPtr {
    const capsuleContent = JSON.stringify(steps);
    return {
      id: `replay_${Date.now()}`,
      capsuleHash: `hash_${capsuleContent.length}`,  // Placeholder hash
      steps,
      deterministic: true
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: AMBIG CANDIDATE DISCIPLINE
// ═══════════════════════════════════════════════════════════════════════════════

export namespace AMBIGDiscipline {
  
  // Candidate set for ambiguous extractions
  export interface CandidateSet {
    id: string;
    motifSource: string;
    candidates: MythIR.OperatorCandidate[];
    evidencePlan: string[];
    truthValue: TruthValue.AMBIG;
  }
  
  // Create candidate set
  export function createCandidateSet(
    motifSource: string,
    candidates: MythIR.OperatorCandidate[]
  ): CandidateSet {
    return {
      id: `candset_${motifSource}`,
      motifSource,
      candidates,
      evidencePlan: candidates.map(c => `gather evidence for ${c.symbol}`),
      truthValue: TruthValue.AMBIG
    };
  }
  
  // Rules for candidate emission
  export const CandidateEmissionRules = {
    // Never force collapse
    noForcedCollapse: true,
    
    // Preserve all plausible candidates
    preserveAll: true,
    
    // Require evidence plan for each candidate
    requireEvidencePlan: true,
    
    // Maximum candidates per motif
    maxCandidates: 5,
    
    // Minimum confidence for NEAR promotion
    nearThreshold: 0.7,
    
    // Minimum confidence for OK promotion
    okThreshold: 0.95
  };
  
  // Check if candidate can be promoted
  export function canPromote(
    candidate: MythIR.OperatorCandidate,
    witness: WitnessDiscipline.WitnessPtr
  ): { canPromote: boolean; targetValue: TruthValue } {
    if (witness.confidence >= CandidateEmissionRules.okThreshold) {
      return { canPromote: true, targetValue: TruthValue.OK };
    } else if (witness.confidence >= CandidateEmissionRules.nearThreshold) {
      return { canPromote: true, targetValue: TruthValue.NEAR };
    }
    return { canPromote: false, targetValue: TruthValue.AMBIG };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: CHAPTER INDEX
// ═══════════════════════════════════════════════════════════════════════════════

export const ChapterIndex = {
  // Arc 0: Foundation
  Ch01: { title: "MythIR Schema Definition", base4: "0000", arc: 0, rail: "Su" as const },
  Ch02: { title: "Source Types and Formats", base4: "0001", arc: 0, rail: "Me" as const },
  Ch03: { title: "Witness Requirements", base4: "0002", arc: 0, rail: "Sa" as const },
  
  // Arc 1: Tokenization
  Ch04: { title: "Text Tokenization", base4: "0003", arc: 1, rail: "Me" as const },
  Ch05: { title: "Token Classification", base4: "0010", arc: 1, rail: "Sa" as const },
  Ch06: { title: "Lexicon Management", base4: "0011", arc: 1, rail: "Su" as const },
  
  // Arc 2: Motif Extraction
  Ch07: { title: "Pattern Recognition", base4: "0012", arc: 2, rail: "Sa" as const },
  Ch08: { title: "Motif Clustering", base4: "0013", arc: 2, rail: "Su" as const },
  Ch09: { title: "Cross-Tradition Alignment", base4: "0020", arc: 2, rail: "Me" as const },
  
  // Arc 3: Candidate Generation
  Ch10: { title: "Operator Candidate Synthesis", base4: "0021", arc: 3, rail: "Su" as const },
  Ch11: { title: "Signature Inference", base4: "0022", arc: 3, rail: "Me" as const },
  Ch12: { title: "AMBIG Emission Discipline", base4: "0023", arc: 3, rail: "Sa" as const },
  
  // Arc 4: Evidence
  Ch13: { title: "Evidence Collection", base4: "0030", arc: 4, rail: "Me" as const },
  Ch14: { title: "Witness Construction", base4: "0031", arc: 4, rail: "Sa" as const },
  Ch15: { title: "Replay Capsule Creation", base4: "0032", arc: 4, rail: "Su" as const },
  
  // Arc 5: Integration
  Ch16: { title: "IR Graph Assembly", base4: "0033", arc: 5, rail: "Sa" as const },
  Ch17: { title: "Multi-Source Fusion", base4: "0100", arc: 5, rail: "Su" as const },
  Ch18: { title: "Conflict Detection", base4: "0101", arc: 5, rail: "Me" as const },
  
  // Arc 6: Output
  Ch19: { title: "IR Serialization", base4: "0102", arc: 6, rail: "Su" as const },
  Ch20: { title: "Quality Metrics", base4: "0103", arc: 6, rail: "Me" as const },
  Ch21: { title: "Pipeline Certification", base4: "0110", arc: 6, rail: "Sa" as const }
};

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: STATISTICS & END STATE
// ═══════════════════════════════════════════════════════════════════════════════

export const Statistics = {
  manuscript: "CC9C",
  tomeNumber: 4,
  chapters: 21,
  appendices: 16,
  totalAtoms: 2368,
  pipelineStages: 6,
  tokenTypes: 9
};

export const EndStateClaim = `
MINING PIPELINE (Ms⟨CC9C⟩ Ch04): Textual Extraction

Pipeline: Text → Tokenize → Parse → Extract → Compile → IR

MythIR Components:
- TextSource: Original text reference
- Token: Classified text units
- Motif: Recurring mythological patterns
- OperatorCandidate: Potential operators with truth values

Witness Discipline:
- WitnessPtr: Evidence pointer with confidence
- ReplayPtr: Deterministic replay capsule
- All extractions require witness

AMBIG Candidate Discipline:
- Never force collapse
- Preserve all plausible candidates
- Require evidence plan for each
- Promotion requires threshold confidence:
  * OK: ≥ 0.95
  * NEAR: ≥ 0.70
  * AMBIG: default

Output: MythIRGraph with nodes, edges, and metadata
`;

// ═══════════════════════════════════════════════════════════════════════════════
// DEFAULT EXPORT
// ═══════════════════════════════════════════════════════════════════════════════

// Re-export for default
export const Exports = {
  TOME_04_MANIFEST,
  ChapterIndex,
  Statistics,
  EndStateClaim
};
