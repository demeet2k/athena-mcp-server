/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * TOME 07: TIME LATTICE
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Multi-Cycle Scheduling & Reconciliation
 * Ms⟨CC9C⟩ Arc 2, Lane Sa - Safety/Constraints
 * 
 * Core Functions:
 * - Phase vectors and time addresses
 * - LCM graph reconciliation
 * - Drift detection and compensation
 * - Reset windows and schedule management
 * 
 * Key Claim:
 * Time is addressed and schedulable via multi-cycle phase vectors.
 * LCM graphs reconcile different cycle periods.
 * 
 * @module TOME_07_TIME_LATTICE
 * @version 1.0.0
 */

// ═══════════════════════════════════════════════════════════════════════════════
// IMPORTS
// ═══════════════════════════════════════════════════════════════════════════════

import { TruthValue } from './TOME_16_SELF_SUFFICIENCY';

// ═══════════════════════════════════════════════════════════════════════════════
// TOME 07 MANIFEST
// ═══════════════════════════════════════════════════════════════════════════════

export const TOME_07_MANIFEST = {
  manuscript: "CC9C",
  tomeNumber: 7,
  title: "TIME_LATTICE",
  subtitle: "Multi-Cycle Scheduling & Reconciliation",
  
  structure: {
    chapters: 21,
    appendices: 16,
    totalStations: 37,
    atomsPerStation: 64,
    totalAtoms: 2368
  },
  
  thesis: `Time is addressed via multi-cycle phase vectors.
LCM graphs reconcile different cycle periods with drift detection.`,

  exports: [
    "Phase vectors",
    "Time addresses",
    "LCM graph reconciliation",
    "Drift detection",
    "Reset windows"
  ]
};

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: TIME CYCLES
// ═══════════════════════════════════════════════════════════════════════════════

export namespace TimeCycles {
  
  // A single time cycle
  export interface Cycle {
    id: string;
    name: string;
    period: number;         // Period in base units (e.g., days)
    unit: TimeUnit;
    offset: number;         // Epoch offset
    description: string;
  }
  
  export type TimeUnit = "day" | "month" | "year" | "custom";
  
  // Standard cycles
  export const StandardCycles: Record<string, Cycle> = {
    solarYear: {
      id: "solar_year",
      name: "Solar Year",
      period: 365.2422,
      unit: "day",
      offset: 0,
      description: "Earth's orbital period around the Sun"
    },
    lunarMonth: {
      id: "lunar_month",
      name: "Lunar Month",
      period: 29.53059,
      unit: "day",
      offset: 0,
      description: "Moon's synodic period"
    },
    week: {
      id: "week",
      name: "Week",
      period: 7,
      unit: "day",
      offset: 0,
      description: "7-day cycle"
    },
    tzolkin: {
      id: "tzolkin",
      name: "Tzolkin",
      period: 260,
      unit: "day",
      offset: 0,
      description: "Mayan sacred calendar"
    },
    haab: {
      id: "haab",
      name: "Haab",
      period: 365,
      unit: "day",
      offset: 0,
      description: "Mayan solar calendar"
    }
  };
  
  // Compute position within cycle
  export function cyclePosition(cycle: Cycle, t: number): number {
    return ((t - cycle.offset) % cycle.period + cycle.period) % cycle.period;
  }
  
  // Compute phase (0 to 2π)
  export function cyclePhase(cycle: Cycle, t: number): number {
    return (2 * Math.PI * cyclePosition(cycle, t)) / cycle.period;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: PHASE VECTORS
// ═══════════════════════════════════════════════════════════════════════════════

export namespace PhaseVectors {
  
  // Multi-cycle phase vector
  export interface PhaseVector {
    time: number;           // Absolute time
    phases: Map<string, number>;  // cycle_id → phase (0 to 2π)
    positions: Map<string, number>; // cycle_id → position within cycle
  }
  
  // Compute phase vector for given cycles
  export function computePhaseVector(
    t: number,
    cycles: TimeCycles.Cycle[]
  ): PhaseVector {
    const phases = new Map<string, number>();
    const positions = new Map<string, number>();
    
    for (const cycle of cycles) {
      phases.set(cycle.id, TimeCycles.cyclePhase(cycle, t));
      positions.set(cycle.id, TimeCycles.cyclePosition(cycle, t));
    }
    
    return { time: t, phases, positions };
  }
  
  // Phase vector distance (L2 on torus)
  export function phaseDistance(v1: PhaseVector, v2: PhaseVector): number {
    let sumSq = 0;
    
    for (const [cycleId, phase1] of v1.phases) {
      const phase2 = v2.phases.get(cycleId);
      if (phase2 !== undefined) {
        // Toroidal distance
        let diff = Math.abs(phase1 - phase2);
        diff = Math.min(diff, 2 * Math.PI - diff);
        sumSq += diff * diff;
      }
    }
    
    return Math.sqrt(sumSq);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: TIME ADDRESSES
// ═══════════════════════════════════════════════════════════════════════════════

export namespace TimeAddresses {
  
  // Time address: position specified by multiple cycles
  export interface TimeAddress {
    id: string;
    components: CycleComponent[];
    absoluteTime?: number;  // If resolvable
    ambiguous: boolean;     // If multiple solutions exist
    solutions?: number[];   // All possible absolute times
  }
  
  export interface CycleComponent {
    cycleId: string;
    position: number;       // Position within cycle
  }
  
  // Resolve time address to absolute time(s)
  export function resolveAddress(
    address: TimeAddress,
    cycles: Map<string, TimeCycles.Cycle>,
    searchRange: [number, number]
  ): TimeAddress {
    const solutions: number[] = [];
    const [tMin, tMax] = searchRange;
    
    // Find all times in range matching all cycle positions
    for (let t = tMin; t <= tMax; t++) {
      let matches = true;
      
      for (const comp of address.components) {
        const cycle = cycles.get(comp.cycleId);
        if (cycle) {
          const pos = TimeCycles.cyclePosition(cycle, t);
          if (Math.abs(pos - comp.position) > 0.5) {
            matches = false;
            break;
          }
        }
      }
      
      if (matches) {
        solutions.push(t);
      }
    }
    
    return {
      ...address,
      solutions,
      ambiguous: solutions.length !== 1,
      absoluteTime: solutions.length === 1 ? solutions[0] : undefined
    };
  }
  
  // Format time address
  export function formatAddress(address: TimeAddress): string {
    const parts = address.components.map(
      c => `${c.cycleId}:${c.position}`
    );
    return `T[${parts.join(",")}]`;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: LCM GRAPH RECONCILIATION
// ═══════════════════════════════════════════════════════════════════════════════

export namespace LCMGraph {
  
  // LCM node: represents a period that is LCM of component cycles
  export interface LCMNode {
    id: string;
    cycles: string[];       // Contributing cycle IDs
    period: number;         // LCM of cycle periods
    level: number;          // Depth in LCM tree
  }
  
  // LCM edge: connects cycles to their LCM
  export interface LCMEdge {
    source: string;
    target: string;
    ratio: number;          // How many source periods in target
  }
  
  // LCM graph
  export interface Graph {
    nodes: Map<string, LCMNode>;
    edges: LCMEdge[];
    root: string;           // Node with largest period
  }
  
  // Compute GCD
  export function gcd(a: number, b: number): number {
    a = Math.abs(Math.round(a));
    b = Math.abs(Math.round(b));
    while (b) {
      const t = b;
      b = a % b;
      a = t;
    }
    return a;
  }
  
  // Compute LCM
  export function lcm(a: number, b: number): number {
    return Math.abs(a * b) / gcd(a, b);
  }
  
  // Build LCM graph from cycles
  export function buildGraph(cycles: TimeCycles.Cycle[]): Graph {
    const nodes = new Map<string, LCMNode>();
    const edges: LCMEdge[] = [];
    
    // Add base cycles as level-0 nodes
    for (const cycle of cycles) {
      nodes.set(cycle.id, {
        id: cycle.id,
        cycles: [cycle.id],
        period: Math.round(cycle.period),
        level: 0
      });
    }
    
    // Build pairwise LCMs at level 1
    for (let i = 0; i < cycles.length; i++) {
      for (let j = i + 1; j < cycles.length; j++) {
        const c1 = cycles[i];
        const c2 = cycles[j];
        const period = lcm(Math.round(c1.period), Math.round(c2.period));
        const id = `lcm_${c1.id}_${c2.id}`;
        
        nodes.set(id, {
          id,
          cycles: [c1.id, c2.id],
          period,
          level: 1
        });
        
        edges.push({
          source: c1.id,
          target: id,
          ratio: period / Math.round(c1.period)
        });
        
        edges.push({
          source: c2.id,
          target: id,
          ratio: period / Math.round(c2.period)
        });
      }
    }
    
    // Find root (largest period)
    let root = cycles[0].id;
    let maxPeriod = 0;
    for (const [id, node] of nodes) {
      if (node.period > maxPeriod) {
        maxPeriod = node.period;
        root = id;
      }
    }
    
    return { nodes, edges, root };
  }
  
  // Find next alignment time
  export function nextAlignment(
    graph: Graph,
    currentTime: number,
    cycleIds: string[]
  ): number {
    // Find LCM node containing all requested cycles
    let targetPeriod = 1;
    for (const id of cycleIds) {
      const node = graph.nodes.get(id);
      if (node) {
        targetPeriod = lcm(targetPeriod, node.period);
      }
    }
    
    // Find next time that is multiple of target period
    const remainder = currentTime % targetPeriod;
    return currentTime + (targetPeriod - remainder);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: DRIFT DETECTION
// ═══════════════════════════════════════════════════════════════════════════════

export namespace DriftDetection {
  
  // Drift record
  export interface DriftRecord {
    cycleId: string;
    expectedPosition: number;
    observedPosition: number;
    drift: number;          // Difference
    driftRate: number;      // Drift per time unit
    timestamp: number;
  }
  
  // Drift threshold
  export interface DriftThreshold {
    cycleId: string;
    maxDrift: number;       // Maximum allowed drift
    alertLevel: "info" | "warning" | "error";
  }
  
  // Detect drift between expected and observed
  export function detectDrift(
    cycle: TimeCycles.Cycle,
    expectedTime: number,
    observedPosition: number
  ): DriftRecord {
    const expectedPosition = TimeCycles.cyclePosition(cycle, expectedTime);
    let drift = observedPosition - expectedPosition;
    
    // Normalize drift to [-period/2, period/2]
    if (drift > cycle.period / 2) {
      drift -= cycle.period;
    } else if (drift < -cycle.period / 2) {
      drift += cycle.period;
    }
    
    return {
      cycleId: cycle.id,
      expectedPosition,
      observedPosition,
      drift,
      driftRate: 0,  // Would need multiple observations
      timestamp: expectedTime
    };
  }
  
  // Check if drift exceeds threshold
  export function checkThreshold(
    drift: DriftRecord,
    threshold: DriftThreshold
  ): { exceeded: boolean; severity: string } {
    const exceeded = Math.abs(drift.drift) > threshold.maxDrift;
    return {
      exceeded,
      severity: exceeded ? threshold.alertLevel : "ok"
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: RESET WINDOWS
// ═══════════════════════════════════════════════════════════════════════════════

export namespace ResetWindows {
  
  // Reset window: time period where reset is allowed
  export interface ResetWindow {
    id: string;
    startTime: number;
    endTime: number;
    cycles: string[];       // Cycles that align in this window
    resetType: ResetType;
    priority: number;
  }
  
  export type ResetType = 
    | "soft"    // Recalibration only
    | "hard"    // Full state reset
    | "epoch";  // New epoch begins
  
  // Find reset windows in time range
  export function findResetWindows(
    lcmGraph: LCMGraph.Graph,
    cycles: TimeCycles.Cycle[],
    timeRange: [number, number]
  ): ResetWindow[] {
    const windows: ResetWindow[] = [];
    const [tMin, tMax] = timeRange;
    
    // Find times where multiple cycles align
    for (let t = tMin; t <= tMax; t++) {
      const alignedCycles: string[] = [];
      
      for (const cycle of cycles) {
        const pos = TimeCycles.cyclePosition(cycle, t);
        // Check if near cycle start (within 1% of period)
        if (pos < cycle.period * 0.01 || pos > cycle.period * 0.99) {
          alignedCycles.push(cycle.id);
        }
      }
      
      if (alignedCycles.length >= 2) {
        windows.push({
          id: `reset_${t}`,
          startTime: t,
          endTime: t + 1,
          cycles: alignedCycles,
          resetType: alignedCycles.length >= 3 ? "hard" : "soft",
          priority: alignedCycles.length
        });
      }
    }
    
    return windows;
  }
  
  // Check if time is in reset window
  export function inResetWindow(
    t: number,
    windows: ResetWindow[]
  ): ResetWindow | null {
    for (const window of windows) {
      if (t >= window.startTime && t <= window.endTime) {
        return window;
      }
    }
    return null;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: CHAPTER INDEX
// ═══════════════════════════════════════════════════════════════════════════════

export const ChapterIndex = {
  // Arc 0: Foundation
  Ch01: { title: "Time Cycle Definitions", base4: "0000", arc: 0, rail: "Su" as const },
  Ch02: { title: "Standard Cycles Catalog", base4: "0001", arc: 0, rail: "Me" as const },
  Ch03: { title: "Cycle Constraints", base4: "0002", arc: 0, rail: "Sa" as const },
  
  // Arc 1: Phase Vectors
  Ch04: { title: "Phase Vector Construction", base4: "0003", arc: 1, rail: "Me" as const },
  Ch05: { title: "Toroidal Distance", base4: "0010", arc: 1, rail: "Sa" as const },
  Ch06: { title: "Phase Interpolation", base4: "0011", arc: 1, rail: "Su" as const },
  
  // Arc 2: Time Addresses
  Ch07: { title: "Time Address Schema", base4: "0012", arc: 2, rail: "Sa" as const },
  Ch08: { title: "Address Resolution", base4: "0013", arc: 2, rail: "Su" as const },
  Ch09: { title: "Ambiguity Handling", base4: "0020", arc: 2, rail: "Me" as const },
  
  // Arc 3: LCM Graphs
  Ch10: { title: "LCM Computation", base4: "0021", arc: 3, rail: "Su" as const },
  Ch11: { title: "Graph Construction", base4: "0022", arc: 3, rail: "Me" as const },
  Ch12: { title: "Alignment Detection", base4: "0023", arc: 3, rail: "Sa" as const },
  
  // Arc 4: Drift
  Ch13: { title: "Drift Detection", base4: "0030", arc: 4, rail: "Me" as const },
  Ch14: { title: "Drift Thresholds", base4: "0031", arc: 4, rail: "Sa" as const },
  Ch15: { title: "Drift Compensation", base4: "0032", arc: 4, rail: "Su" as const },
  
  // Arc 5: Reset
  Ch16: { title: "Reset Window Definition", base4: "0033", arc: 5, rail: "Sa" as const },
  Ch17: { title: "Reset Scheduling", base4: "0100", arc: 5, rail: "Su" as const },
  Ch18: { title: "Epoch Management", base4: "0101", arc: 5, rail: "Me" as const },
  
  // Arc 6: Integration
  Ch19: { title: "Schedule Export", base4: "0102", arc: 6, rail: "Su" as const },
  Ch20: { title: "Cross-System Sync", base4: "0103", arc: 6, rail: "Me" as const },
  Ch21: { title: "Time Lattice Seal", base4: "0110", arc: 6, rail: "Sa" as const }
};

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 8: STATISTICS & END STATE
// ═══════════════════════════════════════════════════════════════════════════════

export const Statistics = {
  manuscript: "CC9C",
  tomeNumber: 7,
  chapters: 21,
  appendices: 16,
  totalAtoms: 2368,
  standardCycles: 5,
  resetTypes: 3
};

export const EndStateClaim = `
TIME LATTICE (Ms⟨CC9C⟩ Ch07): Multi-Cycle Scheduling & Reconciliation

Core Thesis:
Time is addressed via multi-cycle phase vectors.
LCM graphs reconcile different cycle periods with drift detection.

Time Cycles:
- Solar Year: 365.2422 days
- Lunar Month: 29.53059 days
- Week: 7 days
- Tzolkin: 260 days
- Haab: 365 days

Phase Vectors:
- Multi-cycle position at time t
- Toroidal distance for comparison
- Phase interpolation for queries

Time Addresses:
- Position specified by multiple cycles
- Resolution with ambiguity handling
- Search within time ranges

LCM Graph Reconciliation:
- Build LCM tree from cycle periods
- Find alignment times
- Track ratios between cycles

Drift Detection:
- Compare expected vs observed positions
- Threshold-based alerting
- Drift rate computation

Reset Windows:
- Soft: Recalibration only
- Hard: Full state reset
- Epoch: New epoch begins
`;

// ═══════════════════════════════════════════════════════════════════════════════
// DEFAULT EXPORT
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  TOME_07_MANIFEST,
  TimeCycles,
  PhaseVectors,
  TimeAddresses,
  LCMGraph,
  DriftDetection,
  ResetWindows,
  ChapterIndex,
  Statistics,
  EndStateClaim
};
