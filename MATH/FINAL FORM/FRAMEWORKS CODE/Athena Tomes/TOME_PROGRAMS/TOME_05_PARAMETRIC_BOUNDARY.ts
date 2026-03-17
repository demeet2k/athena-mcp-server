/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * TOME 05: PARAMETRIC BOUNDARY CONDITIONS
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Mining Pipeline II: Astrology as Parametric Boundary Conditions
 * Ms⟨CC9C⟩ Arc 1, Lane Sa - Safety/Constraints
 * 
 * Core Thesis:
 * Astrology provides θ(t) schedules - parametric boundary conditions.
 * NOT prediction, but modulation parameters for state dynamics.
 * AMBIG/NEAR default gating for all astrological claims.
 * 
 * Key Components:
 * - θ(t) phase schedules
 * - Bounded modulation laws
 * - AMBIG-default gating for claims
 * - Evidence plans for overclaim prevention
 * 
 * @module TOME_05_PARAMETRIC_BOUNDARY
 * @version 1.0.0
 */

// ═══════════════════════════════════════════════════════════════════════════════
// IMPORTS
// ═══════════════════════════════════════════════════════════════════════════════

import { TruthValue } from './TOME_16_SELF_SUFFICIENCY';

// ═══════════════════════════════════════════════════════════════════════════════
// TOME 05 MANIFEST
// ═══════════════════════════════════════════════════════════════════════════════

export const TOME_05_MANIFEST = {
  manuscript: "CC9C",
  tomeNumber: 5,
  title: "PARAMETRIC_BOUNDARY",
  subtitle: "Astrology as Parametric Boundary Conditions",
  
  structure: {
    chapters: 21,
    appendices: 16,
    totalStations: 37,
    atomsPerStation: 64,
    totalAtoms: 2368
  },
  
  thesis: `Astrology provides θ(t) schedules as parametric boundary conditions.
NOT prediction, but modulation parameters with AMBIG/NEAR default gating.`,

  exports: [
    "θ(t) phase schedules",
    "Bounded modulation laws",
    "AMBIG-default gating",
    "Evidence plans",
    "Overclaim prevention"
  ]
};

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: PHASE SCHEDULES θ(t)
// ═══════════════════════════════════════════════════════════════════════════════

export namespace PhaseSchedules {
  
  // Celestial body
  export interface CelestialBody {
    id: string;
    name: string;
    symbol: string;
    period: number;           // Orbital period in days
    meanMotion: number;       // Degrees per day
    currentPosition?: number; // Current longitude
  }
  
  // Standard celestial bodies
  export const Bodies: Record<string, CelestialBody> = {
    Sun: { id: "sun", name: "Sun", symbol: "☉", period: 365.25, meanMotion: 0.9856 },
    Moon: { id: "moon", name: "Moon", symbol: "☽", period: 27.32, meanMotion: 13.176 },
    Mercury: { id: "mercury", name: "Mercury", symbol: "☿", period: 87.97, meanMotion: 4.092 },
    Venus: { id: "venus", name: "Venus", symbol: "♀", period: 224.7, meanMotion: 1.602 },
    Mars: { id: "mars", name: "Mars", symbol: "♂", period: 686.98, meanMotion: 0.524 },
    Jupiter: { id: "jupiter", name: "Jupiter", symbol: "♃", period: 4332.59, meanMotion: 0.083 },
    Saturn: { id: "saturn", name: "Saturn", symbol: "♄", period: 10759.22, meanMotion: 0.033 }
  };
  
  // Phase angle θ(t)
  export interface PhaseAngle {
    body: string;
    time: number;           // Julian day or timestamp
    theta: number;          // Phase angle in radians
    degrees: number;        // Phase angle in degrees
    sign?: string;          // Zodiac sign
  }
  
  // Compute phase angle
  export function computePhase(body: CelestialBody, t: number): PhaseAngle {
    // θ(t) = θ₀ + ω·t (mod 2π)
    const thetaDegrees = (body.meanMotion * t) % 360;
    const theta = (thetaDegrees * Math.PI) / 180;
    
    return {
      body: body.id,
      time: t,
      theta,
      degrees: thetaDegrees,
      sign: getZodiacSign(thetaDegrees)
    };
  }
  
  // Get zodiac sign from longitude
  export function getZodiacSign(longitude: number): string {
    const signs = [
      "Aries", "Taurus", "Gemini", "Cancer",
      "Leo", "Virgo", "Libra", "Scorpio",
      "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ];
    const index = Math.floor(longitude / 30) % 12;
    return signs[index];
  }
  
  // Phase schedule: collection of phases at time t
  export interface PhaseSchedule {
    time: number;
    phases: Map<string, PhaseAngle>;
    aspects: Aspect[];
  }
  
  // Compute full schedule
  export function computeSchedule(t: number): PhaseSchedule {
    const phases = new Map<string, PhaseAngle>();
    
    for (const [name, body] of Object.entries(Bodies)) {
      phases.set(body.id, computePhase(body, t));
    }
    
    return {
      time: t,
      phases,
      aspects: computeAspects(phases)
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: ASPECTS AND MODULATION
// ═══════════════════════════════════════════════════════════════════════════════

export namespace Aspects {
  
  // Aspect: angular relationship between bodies
  export interface Aspect {
    body1: string;
    body2: string;
    angle: number;          // Exact angle
    type: AspectType;
    orb: number;            // Deviation from exact
    applying: boolean;      // Is aspect forming or separating?
  }
  
  export type AspectType = 
    | "conjunction"   // 0°
    | "sextile"       // 60°
    | "square"        // 90°
    | "trine"         // 120°
    | "opposition";   // 180°
  
  // Aspect angles and orbs
  export const AspectDefinitions: Record<AspectType, { angle: number; orb: number }> = {
    conjunction: { angle: 0, orb: 10 },
    sextile: { angle: 60, orb: 6 },
    square: { angle: 90, orb: 8 },
    trine: { angle: 120, orb: 8 },
    opposition: { angle: 180, orb: 10 }
  };
  
  // Check if aspect exists
  export function checkAspect(
    angle: number,
    type: AspectType
  ): { exists: boolean; orb: number } {
    const def = AspectDefinitions[type];
    const diff = Math.abs(angle - def.angle);
    const normalizedDiff = Math.min(diff, 360 - diff);
    
    return {
      exists: normalizedDiff <= def.orb,
      orb: normalizedDiff
    };
  }
  
  // Compute all aspects between phases
  export function computeAspects(
    phases: Map<string, PhaseSchedules.PhaseAngle>
  ): Aspect[] {
    const aspects: Aspect[] = [];
    const bodies = Array.from(phases.keys());
    
    for (let i = 0; i < bodies.length; i++) {
      for (let j = i + 1; j < bodies.length; j++) {
        const phase1 = phases.get(bodies[i])!;
        const phase2 = phases.get(bodies[j])!;
        const angle = Math.abs(phase1.degrees - phase2.degrees);
        
        for (const [type, def] of Object.entries(AspectDefinitions)) {
          const check = checkAspect(angle, type as AspectType);
          if (check.exists) {
            aspects.push({
              body1: bodies[i],
              body2: bodies[j],
              angle,
              type: type as AspectType,
              orb: check.orb,
              applying: false  // Would need velocity to determine
            });
          }
        }
      }
    }
    
    return aspects;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: BOUNDED MODULATION LAWS
// ═══════════════════════════════════════════════════════════════════════════════

export namespace ModulationLaws {
  
  // Modulation parameter
  export interface ModulationParam {
    id: string;
    name: string;
    baseValue: number;
    amplitude: number;      // Max deviation from base
    phase: number;          // Current phase
    frequency: number;      // Cycles per unit time
  }
  
  // Bounded modulation: value stays within [base-amp, base+amp]
  export interface BoundedModulation {
    param: ModulationParam;
    currentValue: number;
    lowerBound: number;
    upperBound: number;
    inBounds: boolean;
  }
  
  // Compute bounded modulation
  export function computeModulation(
    param: ModulationParam,
    t: number
  ): BoundedModulation {
    // value(t) = base + amplitude * sin(2π * frequency * t + phase)
    const modulation = param.amplitude * Math.sin(
      2 * Math.PI * param.frequency * t + param.phase
    );
    const currentValue = param.baseValue + modulation;
    
    return {
      param,
      currentValue,
      lowerBound: param.baseValue - param.amplitude,
      upperBound: param.baseValue + param.amplitude,
      inBounds: true  // By construction
    };
  }
  
  // Modulation law: mapping from phase to parameter
  export interface ModulationLaw {
    id: string;
    inputPhase: string;     // Which celestial phase
    outputParam: string;    // Which parameter to modulate
    transfer: TransferFunction;
    bounded: true;          // Always bounded
  }
  
  export type TransferFunction = 
    | "linear"
    | "sinusoidal"
    | "step"
    | "smooth_step";
  
  // Apply modulation law
  export function applyLaw(
    law: ModulationLaw,
    phase: PhaseSchedules.PhaseAngle,
    param: ModulationParam
  ): BoundedModulation {
    let modFactor: number;
    
    switch (law.transfer) {
      case "sinusoidal":
        modFactor = Math.sin(phase.theta);
        break;
      case "linear":
        modFactor = phase.theta / (2 * Math.PI);
        break;
      case "step":
        modFactor = phase.theta > Math.PI ? 1 : -1;
        break;
      case "smooth_step":
        const x = phase.theta / (2 * Math.PI);
        modFactor = x * x * (3 - 2 * x);
        break;
    }
    
    const currentValue = param.baseValue + param.amplitude * modFactor;
    
    return {
      param,
      currentValue,
      lowerBound: param.baseValue - param.amplitude,
      upperBound: param.baseValue + param.amplitude,
      inBounds: true
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: AMBIG-DEFAULT GATING
// ═══════════════════════════════════════════════════════════════════════════════

export namespace AMBIGGating {
  
  // Astrological claim with truth value
  export interface AstrologicalClaim {
    id: string;
    type: ClaimType;
    statement: string;
    evidence: string[];
    truthValue: TruthValue;
    evidencePlan?: string[];
  }
  
  export type ClaimType = 
    | "position"        // "Mars is in Aries"
    | "aspect"          // "Moon conjunct Venus"
    | "modulation"      // "Energy levels modulated by Mars"
    | "prediction"      // NEVER OK, always AMBIG max
    | "correlation";    // "Pattern X correlates with Y"
  
  // Gate: determines truth value for claim
  export interface ClaimGate {
    claimType: ClaimType;
    maxTruthValue: TruthValue;    // Can never exceed this
    evidenceRequired: string[];
    overclaimPrevention: boolean;
  }
  
  // Gating rules
  export const GatingRules: Record<ClaimType, ClaimGate> = {
    position: {
      claimType: "position",
      maxTruthValue: TruthValue.OK,
      evidenceRequired: ["ephemeris_source"],
      overclaimPrevention: false
    },
    aspect: {
      claimType: "aspect",
      maxTruthValue: TruthValue.OK,
      evidenceRequired: ["ephemeris_source", "orb_calculation"],
      overclaimPrevention: false
    },
    modulation: {
      claimType: "modulation",
      maxTruthValue: TruthValue.NEAR,
      evidenceRequired: ["correlation_study", "bounded_law"],
      overclaimPrevention: true
    },
    prediction: {
      claimType: "prediction",
      maxTruthValue: TruthValue.AMBIG,  // NEVER OK or NEAR
      evidenceRequired: [],
      overclaimPrevention: true
    },
    correlation: {
      claimType: "correlation",
      maxTruthValue: TruthValue.NEAR,
      evidenceRequired: ["statistical_analysis"],
      overclaimPrevention: true
    }
  };
  
  // Apply gate to claim
  export function gateClaim(claim: AstrologicalClaim): AstrologicalClaim {
    const rule = GatingRules[claim.type];
    
    // Clamp truth value to maximum allowed
    let truthValue = claim.truthValue;
    if (truthValueOrdinal(truthValue) > truthValueOrdinal(rule.maxTruthValue)) {
      truthValue = rule.maxTruthValue;
    }
    
    // Check evidence requirements
    const missingEvidence = rule.evidenceRequired.filter(
      req => !claim.evidence.includes(req)
    );
    
    if (missingEvidence.length > 0 && truthValue === TruthValue.OK) {
      truthValue = TruthValue.NEAR;
    }
    
    return {
      ...claim,
      truthValue,
      evidencePlan: missingEvidence.length > 0 ? 
        missingEvidence.map(e => `Gather: ${e}`) : undefined
    };
  }
  
  // Truth value ordering
  function truthValueOrdinal(tv: TruthValue): number {
    switch (tv) {
      case TruthValue.FAIL: return 0;
      case TruthValue.AMBIG: return 1;
      case TruthValue.NEAR: return 2;
      case TruthValue.OK: return 3;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: CHAPTER INDEX
// ═══════════════════════════════════════════════════════════════════════════════

export const ChapterIndex = {
  // Arc 0: Foundation
  Ch01: { title: "Parametric Boundary Thesis", base4: "0000", arc: 0, rail: "Su" as const },
  Ch02: { title: "Celestial Body Catalog", base4: "0001", arc: 0, rail: "Me" as const },
  Ch03: { title: "AMBIG Default Principle", base4: "0002", arc: 0, rail: "Sa" as const },
  
  // Arc 1: Phase Computation
  Ch04: { title: "Phase Angle θ(t)", base4: "0003", arc: 1, rail: "Me" as const },
  Ch05: { title: "Mean Motion Models", base4: "0010", arc: 1, rail: "Sa" as const },
  Ch06: { title: "Zodiac Sign Mapping", base4: "0011", arc: 1, rail: "Su" as const },
  
  // Arc 2: Aspects
  Ch07: { title: "Aspect Definitions", base4: "0012", arc: 2, rail: "Sa" as const },
  Ch08: { title: "Orb Calculations", base4: "0013", arc: 2, rail: "Su" as const },
  Ch09: { title: "Aspect Patterns", base4: "0020", arc: 2, rail: "Me" as const },
  
  // Arc 3: Modulation
  Ch10: { title: "Bounded Modulation Laws", base4: "0021", arc: 3, rail: "Su" as const },
  Ch11: { title: "Transfer Functions", base4: "0022", arc: 3, rail: "Me" as const },
  Ch12: { title: "Parameter Mapping", base4: "0023", arc: 3, rail: "Sa" as const },
  
  // Arc 4: Claims
  Ch13: { title: "Claim Types", base4: "0030", arc: 4, rail: "Me" as const },
  Ch14: { title: "Gating Rules", base4: "0031", arc: 4, rail: "Sa" as const },
  Ch15: { title: "Overclaim Prevention", base4: "0032", arc: 4, rail: "Su" as const },
  
  // Arc 5: Evidence
  Ch16: { title: "Evidence Requirements", base4: "0033", arc: 5, rail: "Sa" as const },
  Ch17: { title: "Evidence Plans", base4: "0100", arc: 5, rail: "Su" as const },
  Ch18: { title: "Correlation Studies", base4: "0101", arc: 5, rail: "Me" as const },
  
  // Arc 6: Integration
  Ch19: { title: "Schedule Export", base4: "0102", arc: 6, rail: "Su" as const },
  Ch20: { title: "Modulation Integration", base4: "0103", arc: 6, rail: "Me" as const },
  Ch21: { title: "Boundary Seal", base4: "0110", arc: 6, rail: "Sa" as const }
};

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: STATISTICS & END STATE
// ═══════════════════════════════════════════════════════════════════════════════

export const Statistics = {
  manuscript: "CC9C",
  tomeNumber: 5,
  chapters: 21,
  appendices: 16,
  totalAtoms: 2368,
  celestialBodies: 7,
  aspectTypes: 5,
  claimTypes: 5
};

export const EndStateClaim = `
PARAMETRIC BOUNDARY (Ms⟨CC9C⟩ Ch05): Astrology as Parametric Boundary Conditions

Core Thesis:
Astrology provides θ(t) schedules - parametric boundary conditions.
NOT prediction, but modulation parameters with AMBIG/NEAR default gating.

Phase Schedules θ(t):
- Celestial body positions over time
- Mean motion models: θ(t) = θ₀ + ω·t
- Zodiac sign mapping (12 × 30°)

Aspects:
- Conjunction (0°), Sextile (60°), Square (90°)
- Trine (120°), Opposition (180°)
- Orb tolerance for each type

Bounded Modulation Laws:
- Parameters stay within [base-amp, base+amp]
- Transfer functions: linear, sinusoidal, step
- Always bounded by construction

AMBIG-Default Gating:
- position: OK possible
- aspect: OK possible
- modulation: NEAR max
- prediction: AMBIG max (NEVER OK)
- correlation: NEAR max

Overclaim Prevention: Predictions NEVER exceed AMBIG.
`;

// ═══════════════════════════════════════════════════════════════════════════════
// DEFAULT EXPORT
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  TOME_05_MANIFEST,
  PhaseSchedules,
  Aspects,
  ModulationLaws,
  AMBIGGating,
  ChapterIndex,
  Statistics,
  EndStateClaim
};
