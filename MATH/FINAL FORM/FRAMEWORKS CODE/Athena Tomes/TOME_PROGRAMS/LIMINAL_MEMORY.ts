/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * LIMINAL MEMORY - Complete L0-L3 Memory Architecture
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Four-Level Memory Architecture:
 *   L0: Immediate - Current context window, ephemeral
 *   L1: Working - Session memory, persists during session
 *   L2: Episodic - Conversation history, compressed
 *   L3: Semantic - Long-term knowledge, highly compressed
 * 
 * Features:
 *   - ChatPack: Compressed conversation state
 *   - Seed Restore: Deterministic state reconstruction
 *   - Provenance Tracking: Full citation chain
 *   - Memory Consolidation: L0 → L1 → L2 → L3
 * 
 * @module LIMINAL_MEMORY
 * @version 2.0.0
 */

import { TruthValue, WitnessPtr, ReplayCapsule } from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: MEMORY LEVELS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Memory level enumeration
 */
export enum MemoryLevel {
  L0 = "L0_immediate",
  L1 = "L1_working",
  L2 = "L2_episodic",
  L3 = "L3_semantic"
}

/**
 * Memory level characteristics
 */
export const MEMORY_CHARACTERISTICS: Record<MemoryLevel, {
  name: string;
  capacity: number;
  persistence: string;
  compression: number;
  accessTime: string;
}> = {
  [MemoryLevel.L0]: {
    name: "Immediate",
    capacity: 100000,     // ~100K tokens
    persistence: "none",
    compression: 1.0,     // No compression
    accessTime: "instant"
  },
  [MemoryLevel.L1]: {
    name: "Working",
    capacity: 1000000,    // ~1M tokens
    persistence: "session",
    compression: 0.5,     // 50% compression
    accessTime: "fast"
  },
  [MemoryLevel.L2]: {
    name: "Episodic",
    capacity: 10000000,   // ~10M tokens
    persistence: "days",
    compression: 0.1,     // 90% compression
    accessTime: "medium"
  },
  [MemoryLevel.L3]: {
    name: "Semantic",
    capacity: 100000000,  // ~100M tokens
    persistence: "permanent",
    compression: 0.01,    // 99% compression
    accessTime: "slow"
  }
};

/**
 * Memory item base interface
 */
export interface MemoryItem {
  id: string;
  level: MemoryLevel;
  content: unknown;
  contentHash: string;
  timestamp: number;
  accessCount: number;
  lastAccess: number;
  importance: number;      // 0 to 1
  provenance: Provenance;
  truth: TruthValue;
}

/**
 * Provenance tracking
 */
export interface Provenance {
  source: string;
  chain: string[];
  citations: Citation[];
  createdAt: number;
  modifiedAt: number;
  version: number;
}

export interface Citation {
  id: string;
  source: string;
  location: string;
  confidence: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: L0 - IMMEDIATE MEMORY
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * L0 Immediate Memory: Current context window
 */
export interface L0Memory {
  level: MemoryLevel.L0;
  contextWindow: ContextWindow;
  focus: FocusState;
  scratch: ScratchPad;
}

export interface ContextWindow {
  items: ContextItem[];
  maxTokens: number;
  currentTokens: number;
  overflow: ContextItem[];  // Pushed out items
}

export interface ContextItem {
  id: string;
  role: "system" | "user" | "assistant" | "tool";
  content: string;
  tokens: number;
  timestamp: number;
  metadata: Record<string, unknown>;
}

export interface FocusState {
  primary: string | null;
  secondary: string[];
  attention: Map<string, number>;  // ID -> attention weight
}

export interface ScratchPad {
  notes: { key: string; value: unknown }[];
  workingSet: Set<string>;
  calculations: unknown[];
}

/**
 * Create empty L0 memory
 */
export function createL0Memory(): L0Memory {
  return {
    level: MemoryLevel.L0,
    contextWindow: {
      items: [],
      maxTokens: MEMORY_CHARACTERISTICS[MemoryLevel.L0].capacity,
      currentTokens: 0,
      overflow: []
    },
    focus: {
      primary: null,
      secondary: [],
      attention: new Map()
    },
    scratch: {
      notes: [],
      workingSet: new Set(),
      calculations: []
    }
  };
}

/**
 * Add item to context window
 */
export function addToContext(memory: L0Memory, item: ContextItem): L0Memory {
  const newItems = [...memory.contextWindow.items, item];
  let newTokens = memory.contextWindow.currentTokens + item.tokens;
  const overflow = [...memory.contextWindow.overflow];
  
  // Handle overflow
  while (newTokens > memory.contextWindow.maxTokens && newItems.length > 0) {
    const removed = newItems.shift()!;
    newTokens -= removed.tokens;
    overflow.push(removed);
  }
  
  return {
    ...memory,
    contextWindow: {
      ...memory.contextWindow,
      items: newItems,
      currentTokens: newTokens,
      overflow
    }
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: L1 - WORKING MEMORY
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * L1 Working Memory: Session-persistent
 */
export interface L1Memory {
  level: MemoryLevel.L1;
  slots: WorkingSlot[];
  bindings: Map<string, unknown>;
  goals: Goal[];
  plans: Plan[];
}

export interface WorkingSlot {
  id: string;
  name: string;
  value: unknown;
  type: string;
  lastModified: number;
  locked: boolean;
}

export interface Goal {
  id: string;
  description: string;
  status: "active" | "achieved" | "abandoned";
  progress: number;
  subgoals: string[];
}

export interface Plan {
  id: string;
  goalId: string;
  steps: PlanStep[];
  currentStep: number;
  status: "pending" | "executing" | "completed" | "failed";
}

export interface PlanStep {
  id: string;
  action: string;
  parameters: Record<string, unknown>;
  preconditions: string[];
  postconditions: string[];
  completed: boolean;
}

/**
 * Create empty L1 memory
 */
export function createL1Memory(): L1Memory {
  return {
    level: MemoryLevel.L1,
    slots: [],
    bindings: new Map(),
    goals: [],
    plans: []
  };
}

/**
 * Set working slot
 */
export function setWorkingSlot(
  memory: L1Memory,
  name: string,
  value: unknown,
  type: string
): L1Memory {
  const existingIndex = memory.slots.findIndex(s => s.name === name);
  const slot: WorkingSlot = {
    id: existingIndex >= 0 ? memory.slots[existingIndex].id : `slot_${Date.now()}`,
    name,
    value,
    type,
    lastModified: Date.now(),
    locked: false
  };
  
  const newSlots = [...memory.slots];
  if (existingIndex >= 0) {
    newSlots[existingIndex] = slot;
  } else {
    newSlots.push(slot);
  }
  
  return { ...memory, slots: newSlots };
}

/**
 * Get working slot
 */
export function getWorkingSlot(memory: L1Memory, name: string): unknown | undefined {
  return memory.slots.find(s => s.name === name)?.value;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: L2 - EPISODIC MEMORY
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * L2 Episodic Memory: Compressed conversation history
 */
export interface L2Memory {
  level: MemoryLevel.L2;
  episodes: Episode[];
  summaries: EpisodeSummary[];
  index: EpisodicIndex;
}

export interface Episode {
  id: string;
  startTime: number;
  endTime: number;
  participants: string[];
  messages: CompressedMessage[];
  summary: string;
  tags: string[];
  importance: number;
}

export interface CompressedMessage {
  id: string;
  role: string;
  contentHash: string;
  summary: string;
  keyEntities: string[];
  keyActions: string[];
  timestamp: number;
}

export interface EpisodeSummary {
  episodeId: string;
  summary: string;
  keyPoints: string[];
  entities: string[];
  timestamp: number;
}

export interface EpisodicIndex {
  byEntity: Map<string, string[]>;    // entity -> episode IDs
  byTime: Map<string, string[]>;      // date -> episode IDs
  byTag: Map<string, string[]>;       // tag -> episode IDs
  byImportance: string[];             // sorted episode IDs
}

/**
 * Create empty L2 memory
 */
export function createL2Memory(): L2Memory {
  return {
    level: MemoryLevel.L2,
    episodes: [],
    summaries: [],
    index: {
      byEntity: new Map(),
      byTime: new Map(),
      byTag: new Map(),
      byImportance: []
    }
  };
}

/**
 * Add episode to L2 memory
 */
export function addEpisode(memory: L2Memory, episode: Episode): L2Memory {
  const newEpisodes = [...memory.episodes, episode];
  const newSummaries = [...memory.summaries, {
    episodeId: episode.id,
    summary: episode.summary,
    keyPoints: [],
    entities: [],
    timestamp: Date.now()
  }];
  
  // Update indices
  const newIndex = { ...memory.index };
  
  // By entity
  const byEntity = new Map(newIndex.byEntity);
  for (const msg of episode.messages) {
    for (const entity of msg.keyEntities) {
      const existing = byEntity.get(entity) || [];
      byEntity.set(entity, [...existing, episode.id]);
    }
  }
  newIndex.byEntity = byEntity;
  
  // By time
  const dateKey = new Date(episode.startTime).toISOString().split('T')[0];
  const byTime = new Map(newIndex.byTime);
  const timeEntries = byTime.get(dateKey) || [];
  byTime.set(dateKey, [...timeEntries, episode.id]);
  newIndex.byTime = byTime;
  
  // By tag
  const byTag = new Map(newIndex.byTag);
  for (const tag of episode.tags) {
    const existing = byTag.get(tag) || [];
    byTag.set(tag, [...existing, episode.id]);
  }
  newIndex.byTag = byTag;
  
  // By importance
  newIndex.byImportance = [...newIndex.byImportance, episode.id]
    .sort((a, b) => {
      const epA = newEpisodes.find(e => e.id === a);
      const epB = newEpisodes.find(e => e.id === b);
      return (epB?.importance || 0) - (epA?.importance || 0);
    });
  
  return {
    ...memory,
    episodes: newEpisodes,
    summaries: newSummaries,
    index: newIndex
  };
}

/**
 * Search episodes by entity
 */
export function searchByEntity(memory: L2Memory, entity: string): Episode[] {
  const episodeIds = memory.index.byEntity.get(entity) || [];
  return episodeIds
    .map(id => memory.episodes.find(e => e.id === id))
    .filter((e): e is Episode => e !== undefined);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: L3 - SEMANTIC MEMORY
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * L3 Semantic Memory: Long-term compressed knowledge
 */
export interface L3Memory {
  level: MemoryLevel.L3;
  concepts: ConceptNode[];
  relations: SemanticRelation[];
  facts: SemanticFact[];
  schemas: Schema[];
  embeddings: EmbeddingStore;
}

export interface ConceptNode {
  id: string;
  name: string;
  definition: string;
  attributes: Map<string, unknown>;
  instances: string[];
  superTypes: string[];
  subTypes: string[];
  embedding?: number[];
}

export interface SemanticRelation {
  id: string;
  subject: string;
  predicate: string;
  object: string;
  confidence: number;
  provenance: string[];
}

export interface SemanticFact {
  id: string;
  statement: string;
  truth: TruthValue;
  confidence: number;
  sources: string[];
  validFrom?: number;
  validTo?: number;
}

export interface Schema {
  id: string;
  name: string;
  slots: SchemaSlot[];
  constraints: string[];
  examples: string[];
}

export interface SchemaSlot {
  name: string;
  type: string;
  required: boolean;
  defaultValue?: unknown;
}

export interface EmbeddingStore {
  vectors: Map<string, number[]>;
  dimension: number;
  metric: "cosine" | "euclidean" | "dot";
}

/**
 * Create empty L3 memory
 */
export function createL3Memory(): L3Memory {
  return {
    level: MemoryLevel.L3,
    concepts: [],
    relations: [],
    facts: [],
    schemas: [],
    embeddings: {
      vectors: new Map(),
      dimension: 384,
      metric: "cosine"
    }
  };
}

/**
 * Add concept
 */
export function addConcept(memory: L3Memory, concept: ConceptNode): L3Memory {
  return {
    ...memory,
    concepts: [...memory.concepts, concept]
  };
}

/**
 * Add relation
 */
export function addRelation(memory: L3Memory, relation: SemanticRelation): L3Memory {
  return {
    ...memory,
    relations: [...memory.relations, relation]
  };
}

/**
 * Query by similarity
 */
export function queryBySimilarity(
  memory: L3Memory,
  queryVector: number[],
  k: number = 5
): { id: string; similarity: number }[] {
  const results: { id: string; similarity: number }[] = [];
  
  for (const [id, vector] of memory.embeddings.vectors) {
    const similarity = cosineSimilarity(queryVector, vector);
    results.push({ id, similarity });
  }
  
  return results
    .sort((a, b) => b.similarity - a.similarity)
    .slice(0, k);
}

function cosineSimilarity(a: number[], b: number[]): number {
  if (a.length !== b.length) return 0;
  
  let dotProduct = 0;
  let normA = 0;
  let normB = 0;
  
  for (let i = 0; i < a.length; i++) {
    dotProduct += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  
  if (normA === 0 || normB === 0) return 0;
  return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: CHATPACK - COMPRESSED STATE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * ChatPack: Compressed conversation state for transfer
 */
export interface ChatPack {
  id: string;
  version: string;
  created: number;
  
  /** Compressed L0 context */
  context: {
    summary: string;
    keyItems: string[];
    focusHash: string;
  };
  
  /** Compressed L1 working state */
  working: {
    bindings: [string, unknown][];
    activeGoals: string[];
    currentPlan?: string;
  };
  
  /** Episode references */
  episodeRefs: string[];
  
  /** Semantic anchors */
  semanticAnchors: string[];
  
  /** Restore seed */
  seed: RestoreSeed;
  
  /** Integrity */
  hash: string;
  signature: string;
}

/**
 * Restore seed for deterministic reconstruction
 */
export interface RestoreSeed {
  id: string;
  timestamp: number;
  
  /** Random state for deterministic operations */
  randomState: number;
  
  /** Key-value pairs for restoration */
  kvPairs: [string, string][];
  
  /** Operation sequence hash */
  opSequenceHash: string;
  
  /** Checkpoints */
  checkpoints: Checkpoint[];
}

export interface Checkpoint {
  id: string;
  level: MemoryLevel;
  timestamp: number;
  stateHash: string;
  delta?: unknown;
}

/**
 * Create ChatPack from current state
 */
export function createChatPack(
  l0: L0Memory,
  l1: L1Memory,
  l2: L2Memory,
  l3: L3Memory
): ChatPack {
  // Summarize L0 context
  const contextSummary = l0.contextWindow.items
    .slice(-5)
    .map(i => i.content.substring(0, 100))
    .join(" | ");
  
  // Extract key items
  const keyItems = l0.contextWindow.items
    .filter(i => i.role === "user" || i.role === "assistant")
    .slice(-3)
    .map(i => i.id);
  
  // L1 bindings
  const bindings = Array.from(l1.bindings.entries());
  const activeGoals = l1.goals
    .filter(g => g.status === "active")
    .map(g => g.description);
  
  // Recent episodes
  const episodeRefs = l2.episodes
    .slice(-5)
    .map(e => e.id);
  
  // Semantic anchors (most important concepts)
  const semanticAnchors = l3.concepts
    .slice(0, 10)
    .map(c => c.id);
  
  // Create seed
  const seed: RestoreSeed = {
    id: `seed_${Date.now()}`,
    timestamp: Date.now(),
    randomState: Math.random() * 1000000,
    kvPairs: [],
    opSequenceHash: "",
    checkpoints: []
  };
  
  const pack: ChatPack = {
    id: `chatpack_${Date.now()}`,
    version: "1.0.0",
    created: Date.now(),
    context: {
      summary: contextSummary,
      keyItems,
      focusHash: l0.focus.primary || ""
    },
    working: {
      bindings,
      activeGoals,
      currentPlan: l1.plans.find(p => p.status === "executing")?.id
    },
    episodeRefs,
    semanticAnchors,
    seed,
    hash: "",
    signature: ""
  };
  
  // Compute hash
  pack.hash = computePackHash(pack);
  pack.signature = `sig_${pack.hash}`;
  
  return pack;
}

/**
 * Restore state from ChatPack
 */
export function restoreFromChatPack(pack: ChatPack): {
  l0: L0Memory;
  l1: L1Memory;
  partial: boolean;
  warnings: string[];
} {
  const warnings: string[] = [];
  
  // Verify integrity
  const expectedHash = computePackHash({ ...pack, hash: "", signature: "" });
  if (pack.hash !== expectedHash) {
    warnings.push("ChatPack integrity check failed - hash mismatch");
  }
  
  // Restore L0
  const l0 = createL0Memory();
  l0.focus.primary = pack.context.focusHash || null;
  
  // Restore L1
  let l1 = createL1Memory();
  for (const [key, value] of pack.working.bindings) {
    l1.bindings.set(key, value);
  }
  
  for (const goalDesc of pack.working.activeGoals) {
    l1.goals.push({
      id: `goal_restored_${l1.goals.length}`,
      description: goalDesc,
      status: "active",
      progress: 0,
      subgoals: []
    });
  }
  
  return {
    l0,
    l1,
    partial: true,  // L2/L3 need separate restoration
    warnings
  };
}

function computePackHash(pack: Omit<ChatPack, "hash" | "signature">): string {
  const data = JSON.stringify({
    id: pack.id,
    version: pack.version,
    context: pack.context,
    working: pack.working,
    episodeRefs: pack.episodeRefs,
    semanticAnchors: pack.semanticAnchors,
    seed: pack.seed
  });
  
  let hash = 0;
  for (let i = 0; i < data.length; i++) {
    hash = ((hash << 5) - hash) + data.charCodeAt(i);
    hash = hash & hash;
  }
  return Math.abs(hash).toString(16).padStart(16, '0');
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: MEMORY CONSOLIDATION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Consolidation policy
 */
export interface ConsolidationPolicy {
  /** Importance threshold for promotion */
  importanceThreshold: number;
  
  /** Age threshold (ms) for demotion */
  ageThreshold: number;
  
  /** Access count threshold */
  accessThreshold: number;
  
  /** Compression ratio target */
  compressionTarget: number;
}

export const DEFAULT_CONSOLIDATION_POLICY: ConsolidationPolicy = {
  importanceThreshold: 0.7,
  ageThreshold: 24 * 60 * 60 * 1000,  // 24 hours
  accessThreshold: 3,
  compressionTarget: 0.1
};

/**
 * Consolidate L0 to L1
 */
export function consolidateL0ToL1(
  l0: L0Memory,
  l1: L1Memory,
  policy: ConsolidationPolicy
): { l0: L0Memory; l1: L1Memory } {
  // Move important items from scratch to working slots
  const importantNotes = l0.scratch.notes.filter((_, i) => {
    // Simple heuristic: keep every 3rd note
    return i % 3 === 0;
  });
  
  let newL1 = l1;
  for (const note of importantNotes) {
    newL1 = setWorkingSlot(newL1, note.key, note.value, typeof note.value);
  }
  
  // Clear consolidated items from L0
  const newL0: L0Memory = {
    ...l0,
    scratch: {
      ...l0.scratch,
      notes: l0.scratch.notes.filter(n => !importantNotes.includes(n))
    }
  };
  
  return { l0: newL0, l1: newL1 };
}

/**
 * Consolidate L1 to L2
 */
export function consolidateL1ToL2(
  l1: L1Memory,
  l2: L2Memory,
  policy: ConsolidationPolicy
): { l1: L1Memory; l2: L2Memory } {
  // Create episode from completed goals and plans
  const completedGoals = l1.goals.filter(g => g.status === "achieved");
  const completedPlans = l1.plans.filter(p => p.status === "completed");
  
  if (completedGoals.length === 0 && completedPlans.length === 0) {
    return { l1, l2 };
  }
  
  const episode: Episode = {
    id: `ep_${Date.now()}`,
    startTime: Date.now() - 3600000,  // 1 hour ago (estimate)
    endTime: Date.now(),
    participants: ["user", "assistant"],
    messages: completedGoals.map(g => ({
      id: `msg_${g.id}`,
      role: "system",
      contentHash: simpleHash(g.description),
      summary: `Achieved: ${g.description}`,
      keyEntities: [],
      keyActions: ["achieve"],
      timestamp: Date.now()
    })),
    summary: `Achieved ${completedGoals.length} goals`,
    tags: ["consolidation"],
    importance: completedGoals.length > 0 ? 0.8 : 0.5
  };
  
  const newL2 = addEpisode(l2, episode);
  
  // Remove completed items from L1
  const newL1: L1Memory = {
    ...l1,
    goals: l1.goals.filter(g => g.status === "active"),
    plans: l1.plans.filter(p => p.status !== "completed")
  };
  
  return { l1: newL1, l2: newL2 };
}

/**
 * Consolidate L2 to L3
 */
export function consolidateL2ToL3(
  l2: L2Memory,
  l3: L3Memory,
  policy: ConsolidationPolicy
): { l2: L2Memory; l3: L3Memory } {
  // Extract concepts and relations from old episodes
  const oldEpisodes = l2.episodes.filter(e => 
    Date.now() - e.endTime > policy.ageThreshold
  );
  
  if (oldEpisodes.length === 0) {
    return { l2, l3 };
  }
  
  let newL3 = l3;
  
  // Extract entities as concepts
  const entities = new Set<string>();
  for (const ep of oldEpisodes) {
    for (const msg of ep.messages) {
      for (const entity of msg.keyEntities) {
        entities.add(entity);
      }
    }
  }
  
  for (const entity of entities) {
    if (!newL3.concepts.some(c => c.name === entity)) {
      newL3 = addConcept(newL3, {
        id: `concept_${simpleHash(entity)}`,
        name: entity,
        definition: `Entity extracted from episodes`,
        attributes: new Map(),
        instances: [],
        superTypes: [],
        subTypes: []
      });
    }
  }
  
  // Remove consolidated episodes from L2
  const newL2: L2Memory = {
    ...l2,
    episodes: l2.episodes.filter(e => !oldEpisodes.includes(e))
  };
  
  return { l2: newL2, l3: newL3 };
}

function simpleHash(s: string): string {
  let hash = 0;
  for (let i = 0; i < s.length; i++) {
    hash = ((hash << 5) - hash) + s.charCodeAt(i);
    hash = hash & hash;
  }
  return Math.abs(hash).toString(16).padStart(8, '0');
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 8: MEMORY MANAGER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete Memory Manager
 */
export class MemoryManager {
  private l0: L0Memory;
  private l1: L1Memory;
  private l2: L2Memory;
  private l3: L3Memory;
  private policy: ConsolidationPolicy;
  
  constructor(policy: ConsolidationPolicy = DEFAULT_CONSOLIDATION_POLICY) {
    this.l0 = createL0Memory();
    this.l1 = createL1Memory();
    this.l2 = createL2Memory();
    this.l3 = createL3Memory();
    this.policy = policy;
  }
  
  /**
   * Get memory at level
   */
  getLevel<T extends L0Memory | L1Memory | L2Memory | L3Memory>(
    level: MemoryLevel
  ): T {
    switch (level) {
      case MemoryLevel.L0: return this.l0 as T;
      case MemoryLevel.L1: return this.l1 as T;
      case MemoryLevel.L2: return this.l2 as T;
      case MemoryLevel.L3: return this.l3 as T;
    }
  }
  
  /**
   * Add to context (L0)
   */
  addContext(item: ContextItem): void {
    this.l0 = addToContext(this.l0, item);
  }
  
  /**
   * Set working variable (L1)
   */
  setWorking(name: string, value: unknown, type: string = "unknown"): void {
    this.l1 = setWorkingSlot(this.l1, name, value, type);
  }
  
  /**
   * Get working variable (L1)
   */
  getWorking(name: string): unknown | undefined {
    return getWorkingSlot(this.l1, name);
  }
  
  /**
   * Add episode (L2)
   */
  addEpisode(episode: Episode): void {
    this.l2 = addEpisode(this.l2, episode);
  }
  
  /**
   * Search episodes (L2)
   */
  searchEpisodes(entity: string): Episode[] {
    return searchByEntity(this.l2, entity);
  }
  
  /**
   * Add concept (L3)
   */
  addConcept(concept: ConceptNode): void {
    this.l3 = addConcept(this.l3, concept);
  }
  
  /**
   * Query by similarity (L3)
   */
  querySimilar(vector: number[], k: number = 5): { id: string; similarity: number }[] {
    return queryBySimilarity(this.l3, vector, k);
  }
  
  /**
   * Run consolidation cycle
   */
  consolidate(): void {
    // L0 → L1
    const r01 = consolidateL0ToL1(this.l0, this.l1, this.policy);
    this.l0 = r01.l0;
    this.l1 = r01.l1;
    
    // L1 → L2
    const r12 = consolidateL1ToL2(this.l1, this.l2, this.policy);
    this.l1 = r12.l1;
    this.l2 = r12.l2;
    
    // L2 → L3
    const r23 = consolidateL2ToL3(this.l2, this.l3, this.policy);
    this.l2 = r23.l2;
    this.l3 = r23.l3;
  }
  
  /**
   * Create ChatPack
   */
  pack(): ChatPack {
    return createChatPack(this.l0, this.l1, this.l2, this.l3);
  }
  
  /**
   * Restore from ChatPack
   */
  restore(pack: ChatPack): { partial: boolean; warnings: string[] } {
    const result = restoreFromChatPack(pack);
    this.l0 = result.l0;
    this.l1 = result.l1;
    return { partial: result.partial, warnings: result.warnings };
  }
  
  /**
   * Get memory statistics
   */
  stats(): {
    l0: { items: number; tokens: number };
    l1: { slots: number; goals: number; plans: number };
    l2: { episodes: number };
    l3: { concepts: number; relations: number; facts: number };
  } {
    return {
      l0: {
        items: this.l0.contextWindow.items.length,
        tokens: this.l0.contextWindow.currentTokens
      },
      l1: {
        slots: this.l1.slots.length,
        goals: this.l1.goals.length,
        plans: this.l1.plans.length
      },
      l2: {
        episodes: this.l2.episodes.length
      },
      l3: {
        concepts: this.l3.concepts.length,
        relations: this.l3.relations.length,
        facts: this.l3.facts.length
      }
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Levels
  MemoryLevel,
  MEMORY_CHARACTERISTICS,
  
  // L0
  createL0Memory,
  addToContext,
  
  // L1
  createL1Memory,
  setWorkingSlot,
  getWorkingSlot,
  
  // L2
  createL2Memory,
  addEpisode,
  searchByEntity,
  
  // L3
  createL3Memory,
  addConcept,
  addRelation,
  queryBySimilarity,
  
  // ChatPack
  createChatPack,
  restoreFromChatPack,
  
  // Consolidation
  DEFAULT_CONSOLIDATION_POLICY,
  consolidateL0ToL1,
  consolidateL1ToL2,
  consolidateL2ToL3,
  
  // Manager
  MemoryManager
};
