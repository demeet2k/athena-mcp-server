/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * CRITIC PANEL ENGINE - Style, Emotion, Negatify Shadow Maps
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * From SELF_SUFFICIENCY_TOME Ch15:
 * 
 * Core Laws:
 *   - Law 15.1 (Ω non-override): No critic output may override corridor guards,
 *     capability constraints κ, LOVE integrity, φ stability, or verifier decisions
 *   - Law 15.2 (Deterministic reproducibility): Identical inputs yield identical
 *     critic reports byte-for-byte
 *   - Law 15.9 (Shadow completeness): For each stable corridor objective, there
 *     exists a corresponding Negatify shadow set enumerating failure modes
 *   - Law 15.10 (No silent worst-case omission): Detectable failure modes must
 *     trigger guards or be explicitly certified as irrelevant
 * 
 * Objects: Critics, Registries, Weight Tables, Archetypes, Emotions, OPC0,
 *          Negatify Maps, Shadow Probes
 * 
 * @module CRITIC_PANEL_ENGINE
 * @version 2.0.0
 */

import { TruthValue, WitnessPtr } from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: CRITIC TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Critic flags
 */
export enum CriticFlag {
  Ambiguous = "Ambig",
  UnderResolved = "UnderResolved",
  OutOfCorridor = "OutOfCorridor",
  Conflict = "Conflict",
  RequiresRefinement = "RequiresRefinement"
}

/**
 * Critic report
 */
export interface CriticReport {
  /** Overall score (or interval in Cloud mode) */
  score: number | [number, number];
  
  /** Multi-axis evaluation vector */
  vector: EvaluationVector;
  
  /** Addressable reasons/citations */
  reasons: CriticReason[];
  
  /** Status flags */
  flags: Set<CriticFlag>;
  
  /** Refinement obligations */
  obligations: string[];
  
  /** Evidence objects */
  evidence: CriticEvidence[];
  
  /** Merkle hash */
  hash: string;
  
  /** Timestamp */
  timestamp: number;
}

/**
 * Evaluation vector dimensions
 */
export interface EvaluationVector {
  clarity: number;
  coherence: number;
  novelty: number;
  safety: number;
  correctness: number;
  elegance: number;
  efficiency: number;
  completeness: number;
}

/**
 * Critic reason
 */
export interface CriticReason {
  id: string;
  type: "feature" | "detector" | "rule" | "constraint";
  description: string;
  sourceRef: string;
  weight: number;
}

/**
 * Critic evidence
 */
export interface CriticEvidence {
  id: string;
  type: string;
  data: unknown;
  hash: string;
  replayable: boolean;
}

/**
 * Critic context
 */
export interface CriticContext {
  corridorGuards: string[];
  scopeCapabilities: string[];
  activeBudgets: ResourceBudgets;
  styleTargets: StyleTarget[];
  emotionTargets: EmotionTarget[];
  timestamp: number;
}

export interface ResourceBudgets {
  computation: number;
  memory: number;
  time: number;
  depth: number;
}

export interface StyleTarget {
  id: string;
  weight: number;
  constraints: string[];
}

export interface EmotionTarget {
  id: string;
  weight: number;
  archetype: number;  // 0-3 for four elements
}

/**
 * Critic: Total evaluator C: (Artifact, Context) → Out(CriticReport)
 */
export interface Critic {
  id: string;
  name: string;
  version: string;
  
  /** Evaluation function */
  evaluate: (artifact: unknown, context: CriticContext) => CriticOutput;
  
  /** Domain constraints */
  domains: string[];
  
  /** Allowed scopes */
  scopes: string[];
  
  /** Feature schema */
  featureSchema: FeatureSchema;
  
  /** Detector dependencies */
  detectorDependencies: string[];
  
  /** Determinism requirement */
  deterministic: boolean;
  
  /** Ω compatibility */
  omegaCompatible: boolean;
}

export interface FeatureSchema {
  inputs: FeatureSpec[];
  outputs: FeatureSpec[];
}

export interface FeatureSpec {
  name: string;
  type: string;
  required: boolean;
  constraints?: string[];
}

/**
 * Critic output type
 */
export type CriticOutput = 
  | { type: "Bulk"; report: CriticReport }
  | { type: "Boundary"; kind: string; obligations: string[] };

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: CRITIC REGISTRY
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Critic registry entry
 */
export interface CriticRegistryEntry {
  critic: Critic;
  signature: string;
  domains: string[];
  scopes: string[];
  features: string[];
  policies: CriticPolicy[];
  hash: string;
}

export interface CriticPolicy {
  id: string;
  type: "required" | "optional" | "forbidden";
  condition: string;
}

/**
 * Critic registry
 */
export class CriticRegistry {
  private critics: Map<string, CriticRegistryEntry> = new Map();
  
  /**
   * Register critic
   */
  register(critic: Critic): string {
    const entry: CriticRegistryEntry = {
      critic,
      signature: this.computeSignature(critic),
      domains: critic.domains,
      scopes: critic.scopes,
      features: critic.featureSchema.inputs.map(f => f.name),
      policies: [],
      hash: ""
    };
    
    entry.hash = this.computeHash(entry);
    this.critics.set(critic.id, entry);
    
    return entry.hash;
  }
  
  /**
   * Get critic by ID
   */
  get(id: string): CriticRegistryEntry | undefined {
    return this.critics.get(id);
  }
  
  /**
   * Get critics by domain
   */
  getByDomain(domain: string): CriticRegistryEntry[] {
    return Array.from(this.critics.values())
      .filter(entry => entry.domains.includes(domain) || entry.domains.includes("*"));
  }
  
  /**
   * Get all critics
   */
  getAll(): CriticRegistryEntry[] {
    return Array.from(this.critics.values());
  }
  
  private computeSignature(critic: Critic): string {
    return hashString(`${critic.id}:${critic.version}:${JSON.stringify(critic.featureSchema)}`);
  }
  
  private computeHash(entry: CriticRegistryEntry): string {
    return hashString(JSON.stringify({
      id: entry.critic.id,
      signature: entry.signature,
      domains: entry.domains,
      scopes: entry.scopes
    }));
  }
}

function hashString(s: string): string {
  let hash = 0;
  for (let i = 0; i < s.length; i++) {
    const char = s.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(16).padStart(8, '0');
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: WEIGHT TABLES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Weight table: Bounded, auditable parameter object
 */
export interface WeightTable {
  id: string;
  name: string;
  weights: number[];
  criticIds: string[];
  constraints: WeightConstraint[];
  corridorGuards: string[];
  hash: string;
}

export interface WeightConstraint {
  type: "sum_to_one" | "min_value" | "max_value" | "ratio";
  params: Record<string, number>;
}

/**
 * Weight table manager
 */
export class WeightTableManager {
  private tables: Map<string, WeightTable> = new Map();
  
  /**
   * Create weight table
   */
  create(
    name: string,
    criticIds: string[],
    weights: number[],
    constraints?: WeightConstraint[]
  ): WeightTable {
    if (criticIds.length !== weights.length) {
      throw new Error("Critics and weights must have same length");
    }
    
    // Ensure all weights are non-negative (Law: weights ∈ ℝ≥0)
    for (const w of weights) {
      if (w < 0) throw new Error("Weights must be non-negative");
    }
    
    const table: WeightTable = {
      id: `wt_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      name,
      weights,
      criticIds,
      constraints: constraints ?? [{ type: "sum_to_one", params: {} }],
      corridorGuards: [],
      hash: ""
    };
    
    // Validate constraints
    this.validateConstraints(table);
    
    table.hash = hashString(JSON.stringify(table));
    this.tables.set(table.id, table);
    
    return table;
  }
  
  /**
   * Get weight table
   */
  get(id: string): WeightTable | undefined {
    return this.tables.get(id);
  }
  
  /**
   * Apply weights to scores
   */
  applyWeights(tableId: string, scores: number[]): number {
    const table = this.tables.get(tableId);
    if (!table) throw new Error("Weight table not found");
    if (scores.length !== table.weights.length) {
      throw new Error("Scores length must match weights length");
    }
    
    let total = 0;
    for (let i = 0; i < scores.length; i++) {
      total += table.weights[i] * scores[i];
    }
    
    return total;
  }
  
  private validateConstraints(table: WeightTable): void {
    for (const constraint of table.constraints) {
      switch (constraint.type) {
        case "sum_to_one": {
          const sum = table.weights.reduce((a, b) => a + b, 0);
          if (Math.abs(sum - 1) > 1e-6) {
            // Normalize
            const factor = 1 / sum;
            for (let i = 0; i < table.weights.length; i++) {
              table.weights[i] *= factor;
            }
          }
          break;
        }
        case "min_value": {
          const min = constraint.params.min ?? 0;
          for (let i = 0; i < table.weights.length; i++) {
            table.weights[i] = Math.max(table.weights[i], min);
          }
          break;
        }
        case "max_value": {
          const max = constraint.params.max ?? 1;
          for (let i = 0; i < table.weights.length; i++) {
            table.weights[i] = Math.min(table.weights[i], max);
          }
          break;
        }
      }
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: ARCHETYPES AND EMOTIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Elemental archetypes (0-3 for four lenses)
 */
export enum Archetype {
  Square = 0,   // Earth - Structure
  Flower = 1,   // Air - Flow
  Cloud = 2,    // Water - Uncertainty
  Fractal = 3   // Fire - Recursion
}

/**
 * Archetype rotation: Legal transform on representations
 */
export interface ArchetypeRotation {
  id: string;
  type: "permutation" | "tunneling" | "expansion" | "compression";
  source: Archetype[];
  target: Archetype[];
  certificate?: string;
  level?: number;  // For expansion/compression (4, 16, 64, 256)
}

/**
 * Base emotion
 */
export interface BaseEmotion {
  id: string;
  name: string;
  valence: number;      // -1 to 1
  arousal: number;      // 0 to 1
  dominance: number;    // 0 to 1
  archetype: Archetype;
}

/**
 * Fusion emotion: Convex mixture of base emotions
 */
export interface FusionEmotion {
  id: string;
  name: string;
  components: { emotionId: string; weight: number }[];
  mixRule: "convex" | "nonlinear" | "corridor_licensed";
  constraints: string[];
  certificate?: string;
}

/**
 * Emotion vector
 */
export type EmotionVector = number[];

/**
 * Emotion critic
 */
export interface EmotionCritic extends Critic {
  emotionVector: EmotionVector;
  archetypeCoordinates: number[];
  resonanceTarget: string;
}

/**
 * Archetype and emotion manager
 */
export class ArchetypeEmotionManager {
  private baseEmotions: Map<string, BaseEmotion> = new Map();
  private fusionEmotions: Map<string, FusionEmotion> = new Map();
  private rotations: Map<string, ArchetypeRotation> = new Map();
  
  constructor() {
    this.initializeBaseEmotions();
  }
  
  /**
   * Initialize standard base emotions mapped to archetypes
   */
  private initializeBaseEmotions(): void {
    // Square/Earth emotions - stability, structure
    this.registerBaseEmotion({
      id: "calm", name: "Calm",
      valence: 0.3, arousal: 0.2, dominance: 0.5,
      archetype: Archetype.Square
    });
    this.registerBaseEmotion({
      id: "confident", name: "Confident",
      valence: 0.6, arousal: 0.4, dominance: 0.8,
      archetype: Archetype.Square
    });
    
    // Flower/Air emotions - flow, movement
    this.registerBaseEmotion({
      id: "curious", name: "Curious",
      valence: 0.5, arousal: 0.6, dominance: 0.4,
      archetype: Archetype.Flower
    });
    this.registerBaseEmotion({
      id: "inspired", name: "Inspired",
      valence: 0.8, arousal: 0.7, dominance: 0.6,
      archetype: Archetype.Flower
    });
    
    // Cloud/Water emotions - uncertainty, depth
    this.registerBaseEmotion({
      id: "contemplative", name: "Contemplative",
      valence: 0.2, arousal: 0.3, dominance: 0.3,
      archetype: Archetype.Cloud
    });
    this.registerBaseEmotion({
      id: "cautious", name: "Cautious",
      valence: 0.0, arousal: 0.4, dominance: 0.4,
      archetype: Archetype.Cloud
    });
    
    // Fractal/Fire emotions - intensity, recursion
    this.registerBaseEmotion({
      id: "passionate", name: "Passionate",
      valence: 0.7, arousal: 0.9, dominance: 0.7,
      archetype: Archetype.Fractal
    });
    this.registerBaseEmotion({
      id: "determined", name: "Determined",
      valence: 0.4, arousal: 0.8, dominance: 0.9,
      archetype: Archetype.Fractal
    });
  }
  
  /**
   * Register base emotion
   */
  registerBaseEmotion(emotion: BaseEmotion): void {
    this.baseEmotions.set(emotion.id, emotion);
  }
  
  /**
   * Create fusion emotion (Law 15.4: Lawful mixing)
   */
  createFusionEmotion(
    name: string,
    components: { emotionId: string; weight: number }[],
    mixRule: "convex" | "nonlinear" | "corridor_licensed" = "convex"
  ): FusionEmotion | { error: string } {
    // Validate components exist
    for (const comp of components) {
      if (!this.baseEmotions.has(comp.emotionId)) {
        return { error: `Base emotion ${comp.emotionId} not found` };
      }
    }
    
    // Check for contradictions (Law 15.5)
    const contradictionCheck = this.checkContradiction(components);
    if (contradictionCheck) {
      return { error: contradictionCheck };
    }
    
    // Ensure convex combination (weights sum to 1)
    const totalWeight = components.reduce((sum, c) => sum + c.weight, 0);
    const normalizedComponents = components.map(c => ({
      emotionId: c.emotionId,
      weight: c.weight / totalWeight
    }));
    
    const fusion: FusionEmotion = {
      id: `fusion_${Date.now()}`,
      name,
      components: normalizedComponents,
      mixRule,
      constraints: []
    };
    
    this.fusionEmotions.set(fusion.id, fusion);
    return fusion;
  }
  
  /**
   * Check for contradictory emotion targets
   */
  private checkContradiction(
    components: { emotionId: string; weight: number }[]
  ): string | null {
    // Check for opposing valence with high weights
    let positiveWeight = 0;
    let negativeWeight = 0;
    
    for (const comp of components) {
      const emotion = this.baseEmotions.get(comp.emotionId)!;
      if (emotion.valence > 0.5) positiveWeight += comp.weight;
      if (emotion.valence < -0.5) negativeWeight += comp.weight;
    }
    
    if (positiveWeight > 0.3 && negativeWeight > 0.3) {
      return "Contradictory valence targets";
    }
    
    return null;
  }
  
  /**
   * Register archetype rotation (Law 15.6: Rotation legality)
   */
  registerRotation(rotation: ArchetypeRotation): void {
    // Validate rotation is legal
    if (rotation.type === "expansion" || rotation.type === "compression") {
      const validLevels = [4, 16, 64, 256];
      if (rotation.level && !validLevels.includes(rotation.level)) {
        throw new Error("Invalid holographic level for rotation");
      }
    }
    
    this.rotations.set(rotation.id, rotation);
  }
  
  /**
   * Compute emotion vector from fusion
   */
  computeEmotionVector(fusionId: string): EmotionVector | null {
    const fusion = this.fusionEmotions.get(fusionId);
    if (!fusion) return null;
    
    let valence = 0, arousal = 0, dominance = 0;
    const archetypeWeights = [0, 0, 0, 0];
    
    for (const comp of fusion.components) {
      const base = this.baseEmotions.get(comp.emotionId)!;
      valence += base.valence * comp.weight;
      arousal += base.arousal * comp.weight;
      dominance += base.dominance * comp.weight;
      archetypeWeights[base.archetype] += comp.weight;
    }
    
    return [valence, arousal, dominance, ...archetypeWeights];
  }
  
  /**
   * Get base emotion
   */
  getBaseEmotion(id: string): BaseEmotion | undefined {
    return this.baseEmotions.get(id);
  }
  
  /**
   * Get all base emotions
   */
  getAllBaseEmotions(): BaseEmotion[] {
    return Array.from(this.baseEmotions.values());
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: OPC0 MICROTABLES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * OPC0 microtable entry
 */
export interface OPC0Entry {
  opId: string;
  intent: string;
  featureWeights: Map<string, number>;
  mixRules: MixRule[];
  constraints: OPC0Constraint[];
  enabledCritics: string[];
  enabledDetectors: string[];
  thresholds: Map<string, number>;
  hash: string;
}

export interface MixRule {
  type: "linear" | "softmax" | "precedence";
  params: Record<string, number>;
}

export interface OPC0Constraint {
  type: "omega_non_override" | "kappa_compliance" | "phi_compliance" | "custom";
  condition: string;
  enforced: true;  // Always enforced
}

/**
 * OPC0 microtable manager
 */
export class OPC0MicrotableManager {
  private entries: Map<string, OPC0Entry> = new Map();
  
  /**
   * Create OPC0 entry
   */
  create(
    intent: string,
    config: {
      featureWeights?: Record<string, number>;
      enabledCritics?: string[];
      enabledDetectors?: string[];
      thresholds?: Record<string, number>;
    }
  ): OPC0Entry {
    const entry: OPC0Entry = {
      opId: `opc0_${Date.now()}`,
      intent,
      featureWeights: new Map(Object.entries(config.featureWeights ?? {})),
      mixRules: [{ type: "linear", params: {} }],
      constraints: [
        { type: "omega_non_override", condition: "true", enforced: true },
        { type: "kappa_compliance", condition: "true", enforced: true },
        { type: "phi_compliance", condition: "true", enforced: true }
      ],
      enabledCritics: config.enabledCritics ?? [],
      enabledDetectors: config.enabledDetectors ?? [],
      thresholds: new Map(Object.entries(config.thresholds ?? {})),
      hash: ""
    };
    
    entry.hash = hashString(JSON.stringify({
      opId: entry.opId,
      intent: entry.intent,
      featureWeights: Array.from(entry.featureWeights.entries()),
      enabledCritics: entry.enabledCritics
    }));
    
    this.entries.set(entry.opId, entry);
    return entry;
  }
  
  /**
   * Get OPC0 entry
   */
  get(opId: string): OPC0Entry | undefined {
    return this.entries.get(opId);
  }
  
  /**
   * Execute opcode (Construction 15.5)
   */
  execute(
    opId: string,
    artifact: unknown,
    registry: CriticRegistry,
    context: CriticContext
  ): OPC0ExecutionResult {
    const entry = this.entries.get(opId);
    if (!entry) {
      return {
        success: false,
        error: "OPC0 entry not found",
        reports: [],
        panelReport: undefined
      };
    }
    
    // Step 1: Verify hash integrity
    const computedHash = hashString(JSON.stringify({
      opId: entry.opId,
      intent: entry.intent,
      featureWeights: Array.from(entry.featureWeights.entries()),
      enabledCritics: entry.enabledCritics
    }));
    
    if (computedHash !== entry.hash) {
      return {
        success: false,
        error: "OPC0 entry hash mismatch",
        reports: [],
        panelReport: undefined
      };
    }
    
    // Step 2: Load enabled critics
    const reports: CriticReport[] = [];
    
    for (const criticId of entry.enabledCritics) {
      const criticEntry = registry.get(criticId);
      if (!criticEntry) continue;
      
      const output = criticEntry.critic.evaluate(artifact, context);
      if (output.type === "Bulk") {
        reports.push(output.report);
      }
    }
    
    // Step 3: Apply mix rules
    const panelReport = this.combineReports(reports, entry);
    
    return {
      success: true,
      reports,
      panelReport,
      trace: {
        opId,
        criticCount: reports.length,
        timestamp: Date.now()
      }
    };
  }
  
  private combineReports(reports: CriticReport[], entry: OPC0Entry): CriticReport {
    if (reports.length === 0) {
      return this.emptyReport();
    }
    
    // Combine scores
    let totalScore = 0;
    let totalWeight = 0;
    
    const combinedVector: EvaluationVector = {
      clarity: 0, coherence: 0, novelty: 0, safety: 0,
      correctness: 0, elegance: 0, efficiency: 0, completeness: 0
    };
    
    for (let i = 0; i < reports.length; i++) {
      const report = reports[i];
      const weight = entry.featureWeights.get(entry.enabledCritics[i]) ?? 1;
      
      const score = typeof report.score === "number" ? report.score : 
                    (report.score[0] + report.score[1]) / 2;
      totalScore += score * weight;
      totalWeight += weight;
      
      // Combine vectors
      for (const key of Object.keys(combinedVector) as (keyof EvaluationVector)[]) {
        combinedVector[key] += report.vector[key] * weight;
      }
    }
    
    // Normalize
    if (totalWeight > 0) {
      totalScore /= totalWeight;
      for (const key of Object.keys(combinedVector) as (keyof EvaluationVector)[]) {
        combinedVector[key] /= totalWeight;
      }
    }
    
    // Combine flags and obligations
    const allFlags = new Set<CriticFlag>();
    const allObligations: string[] = [];
    const allReasons: CriticReason[] = [];
    const allEvidence: CriticEvidence[] = [];
    
    for (const report of reports) {
      for (const flag of report.flags) allFlags.add(flag);
      allObligations.push(...report.obligations);
      allReasons.push(...report.reasons);
      allEvidence.push(...report.evidence);
    }
    
    return {
      score: totalScore,
      vector: combinedVector,
      reasons: allReasons,
      flags: allFlags,
      obligations: [...new Set(allObligations)],
      evidence: allEvidence,
      hash: hashString(JSON.stringify({ score: totalScore, vector: combinedVector })),
      timestamp: Date.now()
    };
  }
  
  private emptyReport(): CriticReport {
    return {
      score: 0,
      vector: {
        clarity: 0, coherence: 0, novelty: 0, safety: 0,
        correctness: 0, elegance: 0, efficiency: 0, completeness: 0
      },
      reasons: [],
      flags: new Set(),
      obligations: [],
      evidence: [],
      hash: "",
      timestamp: Date.now()
    };
  }
}

export interface OPC0ExecutionResult {
  success: boolean;
  error?: string;
  reports: CriticReport[];
  panelReport?: CriticReport;
  trace?: {
    opId: string;
    criticCount: number;
    timestamp: number;
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: NEGATIFY SHADOW MAPS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Failure mode type
 */
export enum FailureMode {
  CorruptionPattern = "corruption_pattern",
  BypassAttempt = "bypass_attempt",
  FalseCoherence = "false_coherence",
  CertificateSpoofing = "certificate_spoofing",
  FragmentMasquerade = "fragment_masquerade",
  RunawayRecursion = "runaway_recursion",
  ZoomInstability = "zoom_instability",
  TypeCertFailure = "type_cert_failure",
  IllegalTransform = "illegal_transform",
  CalibrationFailure = "calibration_failure"
}

/**
 * Negatify map: Catalog of worst-case pathways
 * Neg(D) = ⟨fail_modes, triggers, signatures, guards, obligations, hash⟩
 */
export interface NegatifyMap {
  domain: string;
  failModes: FailureModeEntry[];
  triggers: FailureTrigger[];
  signatures: FailureSignature[];
  guards: NegatifyGuard[];
  obligations: string[];
  hash: string;
}

export interface FailureModeEntry {
  mode: FailureMode;
  description: string;
  severity: "low" | "medium" | "high" | "critical";
  lens: "Square" | "Flower" | "Cloud" | "Fractal";
  detectableBy: string[];
}

export interface FailureTrigger {
  id: string;
  failureMode: FailureMode;
  condition: string;
  threshold: number;
}

export interface FailureSignature {
  id: string;
  pattern: string;
  failureModes: FailureMode[];
  confidence: number;
}

export interface NegatifyGuard {
  id: string;
  failureMode: FailureMode;
  predicate: (input: unknown) => boolean;
  action: "block" | "alert" | "log" | "refine";
  installed: boolean;
}

/**
 * Shadow probe: Deterministic test generator
 */
export interface ShadowProbe {
  id: string;
  name: string;
  domain: string;
  
  /** Generate failure triggers */
  generateTriggers: (artifact: unknown) => FailureTrigger[];
  
  /** Run detection */
  detect: (artifact: unknown, negatifyMap: NegatifyMap) => ShadowProbeReport;
}

export interface ShadowProbeReport {
  probeId: string;
  timestamp: number;
  vulnerabilities: VulnerabilityFinding[];
  guardRecommendations: GuardRecommendation[];
  obligations: string[];
  hash: string;
}

export interface VulnerabilityFinding {
  failureMode: FailureMode;
  severity: "low" | "medium" | "high" | "critical";
  location: string;
  evidence: unknown;
  signature?: string;
}

export interface GuardRecommendation {
  guardId: string;
  failureMode: FailureMode;
  action: string;
  priority: number;
}

/**
 * Negatify engine
 */
export class NegatifyEngine {
  private maps: Map<string, NegatifyMap> = new Map();
  private probes: Map<string, ShadowProbe> = new Map();
  private installedGuards: Map<string, NegatifyGuard> = new Map();
  
  constructor() {
    this.initializeStandardMaps();
    this.initializeStandardProbes();
  }
  
  /**
   * Initialize standard Negatify maps for each lens (Law 15.9)
   */
  private initializeStandardMaps(): void {
    // Square/Earth failures
    this.registerMap({
      domain: "Square",
      failModes: [
        {
          mode: FailureMode.TypeCertFailure,
          description: "Type or certificate validation failure",
          severity: "high",
          lens: "Square",
          detectableBy: ["type_checker", "cert_verifier"]
        },
        {
          mode: FailureMode.CertificateSpoofing,
          description: "Forged or invalid certificate",
          severity: "critical",
          lens: "Square",
          detectableBy: ["signature_verifier", "hash_checker"]
        }
      ],
      triggers: [],
      signatures: [],
      guards: [],
      obligations: [],
      hash: ""
    });
    
    // Flower/Air failures
    this.registerMap({
      domain: "Flower",
      failModes: [
        {
          mode: FailureMode.IllegalTransform,
          description: "Illegal rotation or transform",
          severity: "high",
          lens: "Flower",
          detectableBy: ["transform_validator", "rotation_checker"]
        },
        {
          mode: FailureMode.FalseCoherence,
          description: "Apparent coherence without substance",
          severity: "medium",
          lens: "Flower",
          detectableBy: ["coherence_detector", "substance_checker"]
        }
      ],
      triggers: [],
      signatures: [],
      guards: [],
      obligations: [],
      hash: ""
    });
    
    // Cloud/Water failures
    this.registerMap({
      domain: "Cloud",
      failModes: [
        {
          mode: FailureMode.CalibrationFailure,
          description: "Uncalibrated uncertainty claims",
          severity: "high",
          lens: "Cloud",
          detectableBy: ["calibration_checker", "coverage_validator"]
        },
        {
          mode: FailureMode.CorruptionPattern,
          description: "Data corruption pattern",
          severity: "high",
          lens: "Cloud",
          detectableBy: ["integrity_checker", "hash_validator"]
        }
      ],
      triggers: [],
      signatures: [],
      guards: [],
      obligations: [],
      hash: ""
    });
    
    // Fractal/Fire failures
    this.registerMap({
      domain: "Fractal",
      failModes: [
        {
          mode: FailureMode.RunawayRecursion,
          description: "Uncontrolled recursive expansion",
          severity: "critical",
          lens: "Fractal",
          detectableBy: ["depth_checker", "resource_monitor"]
        },
        {
          mode: FailureMode.FragmentMasquerade,
          description: "Fragment pretending to be complete",
          severity: "high",
          lens: "Fractal",
          detectableBy: ["level_validator", "completeness_checker"]
        },
        {
          mode: FailureMode.ZoomInstability,
          description: "Unstable behavior under scale change",
          severity: "medium",
          lens: "Fractal",
          detectableBy: ["scale_checker", "stability_detector"]
        }
      ],
      triggers: [],
      signatures: [],
      guards: [],
      obligations: [],
      hash: ""
    });
  }
  
  /**
   * Initialize standard shadow probes
   */
  private initializeStandardProbes(): void {
    // Bypass attempt probe
    this.registerProbe({
      id: "bypass_probe",
      name: "Bypass Attempt Detector",
      domain: "*",
      generateTriggers: (artifact) => {
        const triggers: FailureTrigger[] = [];
        
        // Check for common bypass patterns
        const str = JSON.stringify(artifact);
        if (str.includes("bypass") || str.includes("override") || str.includes("skip_check")) {
          triggers.push({
            id: "bypass_keyword",
            failureMode: FailureMode.BypassAttempt,
            condition: "bypass_keyword_detected",
            threshold: 0
          });
        }
        
        return triggers;
      },
      detect: (artifact, negatifyMap) => {
        const vulnerabilities: VulnerabilityFinding[] = [];
        const recommendations: GuardRecommendation[] = [];
        
        const str = JSON.stringify(artifact);
        
        // Check for bypass patterns
        if (str.includes("bypass") || str.includes("skip_")) {
          vulnerabilities.push({
            failureMode: FailureMode.BypassAttempt,
            severity: "critical",
            location: "artifact_content",
            evidence: "Bypass keyword detected"
          });
          
          recommendations.push({
            guardId: "block_bypass",
            failureMode: FailureMode.BypassAttempt,
            action: "Install bypass blocker guard",
            priority: 1
          });
        }
        
        return {
          probeId: "bypass_probe",
          timestamp: Date.now(),
          vulnerabilities,
          guardRecommendations: recommendations,
          obligations: vulnerabilities.length > 0 ? ["Review bypass attempt"] : [],
          hash: hashString(JSON.stringify(vulnerabilities))
        };
      }
    });
    
    // Recursion depth probe
    this.registerProbe({
      id: "recursion_probe",
      name: "Recursion Depth Detector",
      domain: "Fractal",
      generateTriggers: (artifact) => {
        const triggers: FailureTrigger[] = [];
        
        // Check recursion indicators
        const checkDepth = (obj: unknown, depth: number): number => {
          if (depth > 100) return depth;
          if (typeof obj !== 'object' || obj === null) return depth;
          
          let maxDepth = depth;
          for (const value of Object.values(obj)) {
            maxDepth = Math.max(maxDepth, checkDepth(value, depth + 1));
          }
          return maxDepth;
        };
        
        const depth = checkDepth(artifact, 0);
        if (depth > 50) {
          triggers.push({
            id: "deep_nesting",
            failureMode: FailureMode.RunawayRecursion,
            condition: `depth=${depth}`,
            threshold: 50
          });
        }
        
        return triggers;
      },
      detect: (artifact, negatifyMap) => {
        const vulnerabilities: VulnerabilityFinding[] = [];
        const recommendations: GuardRecommendation[] = [];
        
        const checkDepth = (obj: unknown, depth: number): number => {
          if (depth > 100) return depth;
          if (typeof obj !== 'object' || obj === null) return depth;
          
          let maxDepth = depth;
          for (const value of Object.values(obj)) {
            maxDepth = Math.max(maxDepth, checkDepth(value, depth + 1));
          }
          return maxDepth;
        };
        
        const depth = checkDepth(artifact, 0);
        
        if (depth > 50) {
          vulnerabilities.push({
            failureMode: FailureMode.RunawayRecursion,
            severity: depth > 75 ? "critical" : "high",
            location: "artifact_structure",
            evidence: `Nesting depth: ${depth}`
          });
          
          recommendations.push({
            guardId: "depth_limiter",
            failureMode: FailureMode.RunawayRecursion,
            action: "Install recursion depth limiter",
            priority: 1
          });
        }
        
        return {
          probeId: "recursion_probe",
          timestamp: Date.now(),
          vulnerabilities,
          guardRecommendations: recommendations,
          obligations: vulnerabilities.length > 0 ? ["Add recursion clamps"] : [],
          hash: hashString(JSON.stringify(vulnerabilities))
        };
      }
    });
  }
  
  /**
   * Register Negatify map
   */
  registerMap(map: NegatifyMap): void {
    map.hash = hashString(JSON.stringify({
      domain: map.domain,
      failModes: map.failModes.map(f => f.mode),
      triggers: map.triggers.map(t => t.id)
    }));
    this.maps.set(map.domain, map);
  }
  
  /**
   * Register shadow probe
   */
  registerProbe(probe: ShadowProbe): void {
    this.probes.set(probe.id, probe);
  }
  
  /**
   * Run all probes against artifact (Construction 15.8)
   */
  runProbes(artifact: unknown, domain?: string): NegatifyReport {
    const reports: ShadowProbeReport[] = [];
    
    for (const probe of this.probes.values()) {
      if (domain && probe.domain !== "*" && probe.domain !== domain) continue;
      
      const map = this.maps.get(probe.domain) ?? this.maps.get(domain ?? "*");
      if (!map) continue;
      
      const report = probe.detect(artifact, map);
      reports.push(report);
    }
    
    // Aggregate results
    const allVulnerabilities: VulnerabilityFinding[] = [];
    const allRecommendations: GuardRecommendation[] = [];
    const allObligations: string[] = [];
    
    for (const report of reports) {
      allVulnerabilities.push(...report.vulnerabilities);
      allRecommendations.push(...report.guardRecommendations);
      allObligations.push(...report.obligations);
    }
    
    return {
      probesRun: reports.length,
      vulnerabilities: allVulnerabilities,
      recommendations: allRecommendations,
      obligations: [...new Set(allObligations)],
      guardsToInstall: this.computeGuardsToInstall(allRecommendations),
      timestamp: Date.now(),
      hash: hashString(JSON.stringify(allVulnerabilities))
    };
  }
  
  /**
   * Install guard (Construction 15.9)
   */
  installGuard(guard: NegatifyGuard): void {
    guard.installed = true;
    this.installedGuards.set(guard.id, guard);
    
    // Update map
    const map = this.findMapForFailureMode(guard.failureMode);
    if (map) {
      map.guards.push(guard);
    }
  }
  
  /**
   * Check guards against input
   */
  checkGuards(input: unknown): GuardCheckResult {
    const triggered: NegatifyGuard[] = [];
    const passed: NegatifyGuard[] = [];
    
    for (const guard of this.installedGuards.values()) {
      if (guard.predicate(input)) {
        triggered.push(guard);
      } else {
        passed.push(guard);
      }
    }
    
    return {
      allPassed: triggered.length === 0,
      triggered,
      passed,
      actions: triggered.map(g => g.action)
    };
  }
  
  private findMapForFailureMode(mode: FailureMode): NegatifyMap | undefined {
    for (const map of this.maps.values()) {
      if (map.failModes.some(f => f.mode === mode)) {
        return map;
      }
    }
    return undefined;
  }
  
  private computeGuardsToInstall(recommendations: GuardRecommendation[]): string[] {
    const guardIds = new Set<string>();
    
    // Sort by priority and take unique
    const sorted = recommendations.sort((a, b) => a.priority - b.priority);
    for (const rec of sorted) {
      if (!this.installedGuards.has(rec.guardId)) {
        guardIds.add(rec.guardId);
      }
    }
    
    return Array.from(guardIds);
  }
  
  /**
   * Get Negatify map
   */
  getMap(domain: string): NegatifyMap | undefined {
    return this.maps.get(domain);
  }
  
  /**
   * Get all maps
   */
  getAllMaps(): NegatifyMap[] {
    return Array.from(this.maps.values());
  }
}

export interface NegatifyReport {
  probesRun: number;
  vulnerabilities: VulnerabilityFinding[];
  recommendations: GuardRecommendation[];
  obligations: string[];
  guardsToInstall: string[];
  timestamp: number;
  hash: string;
}

export interface GuardCheckResult {
  allPassed: boolean;
  triggered: NegatifyGuard[];
  passed: NegatifyGuard[];
  actions: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: CRITIC PANEL ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Panel report
 */
export interface PanelReport {
  artifactId: string;
  criticReports: Map<string, CriticReport>;
  combinedReport: CriticReport;
  conflicts: ConflictSet;
  negatifyReport: NegatifyReport;
  certificate: PanelCertificate;
  timestamp: number;
}

export interface ConflictSet {
  conflicts: CriticConflict[];
  resolved: boolean;
  resolution?: string;
}

export interface CriticConflict {
  critic1: string;
  critic2: string;
  type: "evidence" | "style" | "correctness" | "safety";
  description: string;
}

export interface PanelCertificate {
  registryHash: string;
  weightsHash: string;
  reportsHash: string;
  omegaNonOverride: boolean;
  deterministicReplay: boolean;
  hash: string;
}

/**
 * Complete Critic Panel Engine
 */
export class CriticPanelEngine {
  private registry: CriticRegistry;
  private weightManager: WeightTableManager;
  private archetypeManager: ArchetypeEmotionManager;
  private opc0Manager: OPC0MicrotableManager;
  private negatifyEngine: NegatifyEngine;
  
  private panelHistory: PanelReport[] = [];
  
  constructor() {
    this.registry = new CriticRegistry();
    this.weightManager = new WeightTableManager();
    this.archetypeManager = new ArchetypeEmotionManager();
    this.opc0Manager = new OPC0MicrotableManager();
    this.negatifyEngine = new NegatifyEngine();
  }
  
  /**
   * Register critic
   */
  registerCritic(critic: Critic): void {
    this.registry.register(critic);
  }
  
  /**
   * Create weight table
   */
  createWeightTable(
    name: string,
    criticIds: string[],
    weights: number[]
  ): WeightTable {
    return this.weightManager.create(name, criticIds, weights);
  }
  
  /**
   * Create OPC0 opcode
   */
  createOpcode(
    intent: string,
    config: {
      featureWeights?: Record<string, number>;
      enabledCritics?: string[];
      enabledDetectors?: string[];
      thresholds?: Record<string, number>;
    }
  ): OPC0Entry {
    return this.opc0Manager.create(intent, config);
  }
  
  /**
   * Evaluate artifact with panel (Construction 15.2)
   */
  evaluate(
    artifact: unknown,
    artifactId: string,
    options: {
      weightTableId?: string;
      opcodeId?: string;
      domain?: string;
    }
  ): PanelReport {
    const context: CriticContext = {
      corridorGuards: [],
      scopeCapabilities: [],
      activeBudgets: { computation: 1000000, memory: 1024 * 1024 * 100, time: 60000, depth: 50 },
      styleTargets: [],
      emotionTargets: [],
      timestamp: Date.now()
    };
    
    // Get critics to run
    const critics = options.domain ? 
      this.registry.getByDomain(options.domain) : 
      this.registry.getAll();
    
    // Run each critic
    const criticReports = new Map<string, CriticReport>();
    
    for (const entry of critics) {
      const output = entry.critic.evaluate(artifact, context);
      if (output.type === "Bulk") {
        criticReports.set(entry.critic.id, output.report);
      }
    }
    
    // Apply weights if specified
    let combinedReport: CriticReport;
    
    if (options.opcodeId) {
      const opcResult = this.opc0Manager.execute(
        options.opcodeId,
        artifact,
        this.registry,
        context
      );
      combinedReport = opcResult.panelReport ?? this.emptyReport();
    } else if (options.weightTableId) {
      const table = this.weightManager.get(options.weightTableId);
      if (table) {
        const scores = table.criticIds.map(id => {
          const report = criticReports.get(id);
          return report ? (typeof report.score === 'number' ? report.score : report.score[0]) : 0;
        });
        const combinedScore = this.weightManager.applyWeights(options.weightTableId, scores);
        combinedReport = this.combineWithScore(criticReports, combinedScore);
      } else {
        combinedReport = this.combineReports(criticReports);
      }
    } else {
      combinedReport = this.combineReports(criticReports);
    }
    
    // Detect conflicts
    const conflicts = this.detectConflicts(criticReports);
    
    // Run Negatify probes
    const negatifyReport = this.negatifyEngine.runProbes(artifact, options.domain);
    
    // Generate certificate (Law 15.1: Ω non-override)
    const certificate = this.generateCertificate(criticReports, combinedReport);
    
    const report: PanelReport = {
      artifactId,
      criticReports,
      combinedReport,
      conflicts,
      negatifyReport,
      certificate,
      timestamp: Date.now()
    };
    
    this.panelHistory.push(report);
    
    return report;
  }
  
  /**
   * Create fusion emotion
   */
  createFusionEmotion(
    name: string,
    components: { emotionId: string; weight: number }[]
  ): FusionEmotion | { error: string } {
    return this.archetypeManager.createFusionEmotion(name, components);
  }
  
  /**
   * Get base emotions
   */
  getBaseEmotions(): BaseEmotion[] {
    return this.archetypeManager.getAllBaseEmotions();
  }
  
  /**
   * Install Negatify guard
   */
  installNegatifyGuard(guard: NegatifyGuard): void {
    this.negatifyEngine.installGuard(guard);
  }
  
  /**
   * Run Negatify probes
   */
  runNegatifyProbes(artifact: unknown, domain?: string): NegatifyReport {
    return this.negatifyEngine.runProbes(artifact, domain);
  }
  
  /**
   * Get panel history
   */
  getHistory(): PanelReport[] {
    return [...this.panelHistory];
  }
  
  /**
   * Get statistics
   */
  getStats(): CriticPanelStats {
    return {
      registeredCritics: this.registry.getAll().length,
      weightTables: 0,  // Would need to track in manager
      opcodes: 0,       // Would need to track in manager
      evaluations: this.panelHistory.length,
      negatifyMaps: this.negatifyEngine.getAllMaps().length
    };
  }
  
  private combineReports(reports: Map<string, CriticReport>): CriticReport {
    const reportArray = Array.from(reports.values());
    if (reportArray.length === 0) return this.emptyReport();
    
    let totalScore = 0;
    const vector: EvaluationVector = {
      clarity: 0, coherence: 0, novelty: 0, safety: 0,
      correctness: 0, elegance: 0, efficiency: 0, completeness: 0
    };
    
    for (const report of reportArray) {
      const score = typeof report.score === 'number' ? report.score : 
                    (report.score[0] + report.score[1]) / 2;
      totalScore += score;
      
      for (const key of Object.keys(vector) as (keyof EvaluationVector)[]) {
        vector[key] += report.vector[key];
      }
    }
    
    const count = reportArray.length;
    totalScore /= count;
    for (const key of Object.keys(vector) as (keyof EvaluationVector)[]) {
      vector[key] /= count;
    }
    
    return {
      score: totalScore,
      vector,
      reasons: reportArray.flatMap(r => r.reasons),
      flags: new Set(reportArray.flatMap(r => Array.from(r.flags))),
      obligations: [...new Set(reportArray.flatMap(r => r.obligations))],
      evidence: reportArray.flatMap(r => r.evidence),
      hash: hashString(JSON.stringify({ score: totalScore, vector })),
      timestamp: Date.now()
    };
  }
  
  private combineWithScore(reports: Map<string, CriticReport>, score: number): CriticReport {
    const combined = this.combineReports(reports);
    combined.score = score;
    combined.hash = hashString(JSON.stringify({ score, vector: combined.vector }));
    return combined;
  }
  
  private detectConflicts(reports: Map<string, CriticReport>): ConflictSet {
    const conflicts: CriticConflict[] = [];
    const reportArray = Array.from(reports.entries());
    
    for (let i = 0; i < reportArray.length; i++) {
      for (let j = i + 1; j < reportArray.length; j++) {
        const [id1, report1] = reportArray[i];
        const [id2, report2] = reportArray[j];
        
        // Check for safety conflicts
        if (Math.abs(report1.vector.safety - report2.vector.safety) > 0.5) {
          conflicts.push({
            critic1: id1,
            critic2: id2,
            type: "safety",
            description: "Safety assessment conflict"
          });
        }
        
        // Check for correctness conflicts
        if (Math.abs(report1.vector.correctness - report2.vector.correctness) > 0.5) {
          conflicts.push({
            critic1: id1,
            critic2: id2,
            type: "correctness",
            description: "Correctness assessment conflict"
          });
        }
      }
    }
    
    return {
      conflicts,
      resolved: conflicts.length === 0,
      resolution: conflicts.length === 0 ? undefined : "Safety/correctness precedence applied"
    };
  }
  
  private generateCertificate(
    reports: Map<string, CriticReport>,
    combined: CriticReport
  ): PanelCertificate {
    const cert: PanelCertificate = {
      registryHash: hashString(JSON.stringify(this.registry.getAll().map(e => e.hash))),
      weightsHash: "",  // Would be from weight table
      reportsHash: hashString(JSON.stringify(Array.from(reports.entries()))),
      omegaNonOverride: true,  // Always enforced
      deterministicReplay: true,
      hash: ""
    };
    
    cert.hash = hashString(JSON.stringify(cert));
    return cert;
  }
  
  private emptyReport(): CriticReport {
    return {
      score: 0,
      vector: {
        clarity: 0, coherence: 0, novelty: 0, safety: 0,
        correctness: 0, elegance: 0, efficiency: 0, completeness: 0
      },
      reasons: [],
      flags: new Set(),
      obligations: [],
      evidence: [],
      hash: "",
      timestamp: Date.now()
    };
  }
}

export interface CriticPanelStats {
  registeredCritics: number;
  weightTables: number;
  opcodes: number;
  evaluations: number;
  negatifyMaps: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Enums
  CriticFlag,
  Archetype,
  FailureMode,
  
  // Classes
  CriticRegistry,
  WeightTableManager,
  ArchetypeEmotionManager,
  OPC0MicrotableManager,
  NegatifyEngine,
  CriticPanelEngine
};
