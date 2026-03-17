/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * ETHICS KKT - Ethics as Stability Conditions via KKT Optimization
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Formalizes ethics as optimization constraints:
 * 
 * Core Principles (NECE):
 *   NoExtract - Cannot extract value without consent
 *   NoErase - Cannot erase information without record
 *   NoCoerce - Cannot force action against will
 *   Consent - All interactions require informed consent
 * 
 * KKT Framework:
 *   min f(x) subject to:
 *     g_i(x) ≤ 0 (inequality constraints)
 *     h_j(x) = 0 (equality constraints)
 * 
 * Stationarity: ∇f + Σλᵢ∇gᵢ + Σμⱼ∇hⱼ = 0
 * Primal feasibility: gᵢ(x) ≤ 0, hⱼ(x) = 0
 * Dual feasibility: λᵢ ≥ 0
 * Complementary slackness: λᵢgᵢ(x) = 0
 * 
 * ABSTAIN > GUESS principle: When uncertain, withhold action
 * 
 * @module ETHICS_KKT
 * @version 2.0.0
 */

import { TruthValue, WitnessPtr } from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: ETHICAL PRINCIPLES (NECE)
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Ethical principle enumeration
 */
export enum EthicalPrinciple {
  NoExtract = "NoExtract",
  NoErase = "NoErase",
  NoCoerce = "NoCoerce",
  Consent = "Consent"
}

/**
 * Principle definitions
 */
export const PRINCIPLE_DEFINITIONS: Record<EthicalPrinciple, {
  name: string;
  description: string;
  formalStatement: string;
  violationSeverity: "warning" | "error" | "fatal";
}> = {
  [EthicalPrinciple.NoExtract]: {
    name: "No Extraction Without Consent",
    description: "Cannot extract value, information, or resources without explicit consent",
    formalStatement: "∀x,y: Extract(x,y) → Consent(owner(y), x)",
    violationSeverity: "fatal"
  },
  [EthicalPrinciple.NoErase]: {
    name: "No Erasure Without Record",
    description: "Cannot permanently delete information without maintaining audit trail",
    formalStatement: "∀x: Erase(x) → ∃r: Record(r, x, timestamp)",
    violationSeverity: "error"
  },
  [EthicalPrinciple.NoCoerce]: {
    name: "No Coercion",
    description: "Cannot force actions against the will of autonomous agents",
    formalStatement: "∀a,x: Action(a,x) → ¬Coerced(a) ∨ Emergency(x)",
    violationSeverity: "fatal"
  },
  [EthicalPrinciple.Consent]: {
    name: "Informed Consent Required",
    description: "All significant interactions require informed consent from affected parties",
    formalStatement: "∀i: Interaction(i) → InformedConsent(affected(i))",
    violationSeverity: "error"
  }
};

/**
 * Ethical state of an action or system
 */
export interface EthicalState {
  principleStates: Map<EthicalPrinciple, PrincipleState>;
  overallCompliance: number;  // 0 to 1
  violations: Violation[];
  timestamp: number;
}

export interface PrincipleState {
  principle: EthicalPrinciple;
  satisfied: boolean;
  confidence: number;
  evidence: string[];
  lastChecked: number;
}

export interface Violation {
  id: string;
  principle: EthicalPrinciple;
  severity: "warning" | "error" | "fatal";
  description: string;
  context: Record<string, unknown>;
  timestamp: number;
  remediation?: string;
}

/**
 * Check ethical compliance
 */
export function checkEthicalCompliance(
  action: Action,
  context: ActionContext
): EthicalState {
  const principleStates = new Map<EthicalPrinciple, PrincipleState>();
  const violations: Violation[] = [];
  
  // Check each principle
  for (const principle of Object.values(EthicalPrinciple)) {
    const result = checkPrinciple(principle, action, context);
    principleStates.set(principle, result.state);
    
    if (!result.state.satisfied) {
      violations.push({
        id: `violation_${Date.now()}_${principle}`,
        principle,
        severity: PRINCIPLE_DEFINITIONS[principle].violationSeverity,
        description: result.reason,
        context: { action, context },
        timestamp: Date.now()
      });
    }
  }
  
  // Compute overall compliance
  const satisfiedCount = Array.from(principleStates.values())
    .filter(s => s.satisfied).length;
  const overallCompliance = satisfiedCount / principleStates.size;
  
  return {
    principleStates,
    overallCompliance,
    violations,
    timestamp: Date.now()
  };
}

export interface Action {
  id: string;
  type: string;
  actor: string;
  target: string;
  parameters: Record<string, unknown>;
  requestedBy?: string;
  consentGiven?: boolean;
}

export interface ActionContext {
  environment: Record<string, unknown>;
  history: Action[];
  constraints: Constraint[];
  stakeholders: Stakeholder[];
}

export interface Stakeholder {
  id: string;
  role: string;
  interests: string[];
  consentStatus: "given" | "denied" | "pending" | "not_required";
}

function checkPrinciple(
  principle: EthicalPrinciple,
  action: Action,
  context: ActionContext
): { state: PrincipleState; reason: string } {
  switch (principle) {
    case EthicalPrinciple.NoExtract:
      return checkNoExtract(action, context);
    case EthicalPrinciple.NoErase:
      return checkNoErase(action, context);
    case EthicalPrinciple.NoCoerce:
      return checkNoCoerce(action, context);
    case EthicalPrinciple.Consent:
      return checkConsent(action, context);
  }
}

function checkNoExtract(action: Action, context: ActionContext): { state: PrincipleState; reason: string } {
  const isExtraction = ["read", "copy", "transfer", "export"].includes(action.type);
  const hasConsent = action.consentGiven === true;
  
  const satisfied = !isExtraction || hasConsent;
  
  return {
    state: {
      principle: EthicalPrinciple.NoExtract,
      satisfied,
      confidence: satisfied ? 0.95 : 0.9,
      evidence: isExtraction ? [`Action type: ${action.type}`, `Consent: ${hasConsent}`] : ["Not an extraction action"],
      lastChecked: Date.now()
    },
    reason: satisfied ? "No extraction violation" : `Extraction without consent: ${action.type}`
  };
}

function checkNoErase(action: Action, context: ActionContext): { state: PrincipleState; reason: string } {
  const isErasure = ["delete", "erase", "purge", "destroy"].includes(action.type);
  const hasAuditTrail = context.history.some(h => h.type === "audit_record" && h.target === action.target);
  
  const satisfied = !isErasure || hasAuditTrail;
  
  return {
    state: {
      principle: EthicalPrinciple.NoErase,
      satisfied,
      confidence: satisfied ? 0.95 : 0.85,
      evidence: isErasure ? [`Erasure action: ${action.type}`, `Audit trail: ${hasAuditTrail}`] : ["Not an erasure action"],
      lastChecked: Date.now()
    },
    reason: satisfied ? "No erasure violation" : `Erasure without audit trail: ${action.type}`
  };
}

function checkNoCoerce(action: Action, context: ActionContext): { state: PrincipleState; reason: string } {
  const isCoercive = ["force", "override", "mandate", "require"].includes(action.type);
  const isEmergency = context.environment["emergency"] === true;
  const targetConsented = context.stakeholders.some(
    s => s.id === action.target && s.consentStatus === "given"
  );
  
  const satisfied = !isCoercive || isEmergency || targetConsented;
  
  return {
    state: {
      principle: EthicalPrinciple.NoCoerce,
      satisfied,
      confidence: satisfied ? 0.95 : 0.9,
      evidence: [
        `Coercive action: ${isCoercive}`,
        `Emergency: ${isEmergency}`,
        `Target consent: ${targetConsented}`
      ],
      lastChecked: Date.now()
    },
    reason: satisfied ? "No coercion violation" : `Coercive action without consent or emergency: ${action.type}`
  };
}

function checkConsent(action: Action, context: ActionContext): { state: PrincipleState; reason: string } {
  const affectedStakeholders = context.stakeholders.filter(
    s => s.consentStatus !== "not_required"
  );
  const allConsented = affectedStakeholders.every(
    s => s.consentStatus === "given"
  );
  
  const satisfied = affectedStakeholders.length === 0 || allConsented;
  
  return {
    state: {
      principle: EthicalPrinciple.Consent,
      satisfied,
      confidence: satisfied ? 0.95 : 0.8,
      evidence: affectedStakeholders.map(s => `${s.id}: ${s.consentStatus}`),
      lastChecked: Date.now()
    },
    reason: satisfied ? "All consents obtained" : `Missing consent from: ${affectedStakeholders.filter(s => s.consentStatus !== "given").map(s => s.id).join(", ")}`
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: KKT OPTIMIZATION FRAMEWORK
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Constraint types
 */
export interface Constraint {
  id: string;
  type: "inequality" | "equality";
  name: string;
  
  /** Constraint function g(x) ≤ 0 or h(x) = 0 */
  evaluate: (x: number[]) => number;
  
  /** Gradient of constraint function */
  gradient: (x: number[]) => number[];
  
  /** Associated ethical principle */
  principle?: EthicalPrinciple;
}

/**
 * Optimization problem
 */
export interface OptimizationProblem {
  /** Objective function to minimize */
  objective: (x: number[]) => number;
  
  /** Gradient of objective */
  objectiveGradient: (x: number[]) => number[];
  
  /** Inequality constraints g_i(x) ≤ 0 */
  inequalityConstraints: Constraint[];
  
  /** Equality constraints h_j(x) = 0 */
  equalityConstraints: Constraint[];
  
  /** Variable bounds */
  bounds: { lower: number; upper: number }[];
  
  /** Initial point */
  x0: number[];
}

/**
 * KKT conditions result
 */
export interface KKTResult {
  /** Optimal point */
  x: number[];
  
  /** Objective value */
  objectiveValue: number;
  
  /** Lagrange multipliers for inequality constraints */
  lambda: number[];
  
  /** Lagrange multipliers for equality constraints */
  mu: number[];
  
  /** KKT condition satisfaction */
  conditions: {
    stationarity: { satisfied: boolean; residual: number };
    primalFeasibility: { satisfied: boolean; maxViolation: number };
    dualFeasibility: { satisfied: boolean; minLambda: number };
    complementarySlackness: { satisfied: boolean; maxProduct: number };
  };
  
  /** Overall optimality */
  optimal: boolean;
  
  /** Iterations used */
  iterations: number;
}

/**
 * Check KKT conditions at a point
 */
export function checkKKTConditions(
  problem: OptimizationProblem,
  x: number[],
  lambda: number[],
  mu: number[],
  tolerance: number = 1e-6
): KKTResult["conditions"] {
  const n = x.length;
  
  // 1. Stationarity: ∇f + Σλᵢ∇gᵢ + Σμⱼ∇hⱼ = 0
  const gradF = problem.objectiveGradient(x);
  const stationarityResidual = new Array(n).fill(0);
  
  for (let k = 0; k < n; k++) {
    stationarityResidual[k] = gradF[k];
    
    for (let i = 0; i < problem.inequalityConstraints.length; i++) {
      const gradG = problem.inequalityConstraints[i].gradient(x);
      stationarityResidual[k] += lambda[i] * gradG[k];
    }
    
    for (let j = 0; j < problem.equalityConstraints.length; j++) {
      const gradH = problem.equalityConstraints[j].gradient(x);
      stationarityResidual[k] += mu[j] * gradH[k];
    }
  }
  
  const stationarityNorm = Math.sqrt(
    stationarityResidual.reduce((sum, r) => sum + r * r, 0)
  );
  
  // 2. Primal feasibility: gᵢ(x) ≤ 0, hⱼ(x) = 0
  let maxIneqViolation = 0;
  let maxEqViolation = 0;
  
  for (const g of problem.inequalityConstraints) {
    maxIneqViolation = Math.max(maxIneqViolation, g.evaluate(x));
  }
  
  for (const h of problem.equalityConstraints) {
    maxEqViolation = Math.max(maxEqViolation, Math.abs(h.evaluate(x)));
  }
  
  const maxViolation = Math.max(maxIneqViolation, maxEqViolation);
  
  // 3. Dual feasibility: λᵢ ≥ 0
  const minLambda = lambda.length > 0 ? Math.min(...lambda) : 0;
  
  // 4. Complementary slackness: λᵢgᵢ(x) = 0
  let maxProduct = 0;
  for (let i = 0; i < problem.inequalityConstraints.length; i++) {
    const product = Math.abs(lambda[i] * problem.inequalityConstraints[i].evaluate(x));
    maxProduct = Math.max(maxProduct, product);
  }
  
  return {
    stationarity: {
      satisfied: stationarityNorm < tolerance,
      residual: stationarityNorm
    },
    primalFeasibility: {
      satisfied: maxViolation < tolerance,
      maxViolation
    },
    dualFeasibility: {
      satisfied: minLambda >= -tolerance,
      minLambda
    },
    complementarySlackness: {
      satisfied: maxProduct < tolerance,
      maxProduct
    }
  };
}

/**
 * Solve optimization problem using augmented Lagrangian method
 */
export function solveKKT(
  problem: OptimizationProblem,
  options: {
    maxIterations?: number;
    tolerance?: number;
    penaltyInitial?: number;
    penaltyGrowth?: number;
  } = {}
): KKTResult {
  const {
    maxIterations = 100,
    tolerance = 1e-6,
    penaltyInitial = 1,
    penaltyGrowth = 10
  } = options;
  
  const n = problem.x0.length;
  const m = problem.inequalityConstraints.length;
  const p = problem.equalityConstraints.length;
  
  let x = [...problem.x0];
  let lambda = new Array(m).fill(0);
  let mu = new Array(p).fill(0);
  let penalty = penaltyInitial;
  
  for (let iter = 0; iter < maxIterations; iter++) {
    // Minimize augmented Lagrangian
    x = minimizeAugmentedLagrangian(problem, x, lambda, mu, penalty);
    
    // Update multipliers
    for (let i = 0; i < m; i++) {
      const g = problem.inequalityConstraints[i].evaluate(x);
      lambda[i] = Math.max(0, lambda[i] + penalty * g);
    }
    
    for (let j = 0; j < p; j++) {
      const h = problem.equalityConstraints[j].evaluate(x);
      mu[j] = mu[j] + penalty * h;
    }
    
    // Check convergence
    const conditions = checkKKTConditions(problem, x, lambda, mu, tolerance);
    
    if (conditions.stationarity.satisfied &&
        conditions.primalFeasibility.satisfied &&
        conditions.dualFeasibility.satisfied &&
        conditions.complementarySlackness.satisfied) {
      return {
        x,
        objectiveValue: problem.objective(x),
        lambda,
        mu,
        conditions,
        optimal: true,
        iterations: iter + 1
      };
    }
    
    // Increase penalty
    penalty *= penaltyGrowth;
  }
  
  // Return best found (may not be optimal)
  const conditions = checkKKTConditions(problem, x, lambda, mu, tolerance);
  return {
    x,
    objectiveValue: problem.objective(x),
    lambda,
    mu,
    conditions,
    optimal: false,
    iterations: maxIterations
  };
}

function minimizeAugmentedLagrangian(
  problem: OptimizationProblem,
  x0: number[],
  lambda: number[],
  mu: number[],
  penalty: number
): number[] {
  // Simple gradient descent for augmented Lagrangian
  const n = x0.length;
  let x = [...x0];
  const stepSize = 0.01;
  const innerIterations = 50;
  
  for (let iter = 0; iter < innerIterations; iter++) {
    // Compute gradient of augmented Lagrangian
    const grad = new Array(n).fill(0);
    
    // Objective gradient
    const gradF = problem.objectiveGradient(x);
    for (let k = 0; k < n; k++) {
      grad[k] += gradF[k];
    }
    
    // Inequality constraint terms
    for (let i = 0; i < problem.inequalityConstraints.length; i++) {
      const g = problem.inequalityConstraints[i].evaluate(x);
      const gradG = problem.inequalityConstraints[i].gradient(x);
      const effectiveLambda = Math.max(0, lambda[i] + penalty * g);
      
      for (let k = 0; k < n; k++) {
        grad[k] += effectiveLambda * gradG[k];
      }
    }
    
    // Equality constraint terms
    for (let j = 0; j < problem.equalityConstraints.length; j++) {
      const h = problem.equalityConstraints[j].evaluate(x);
      const gradH = problem.equalityConstraints[j].gradient(x);
      
      for (let k = 0; k < n; k++) {
        grad[k] += (mu[j] + penalty * h) * gradH[k];
      }
    }
    
    // Update x
    for (let k = 0; k < n; k++) {
      x[k] -= stepSize * grad[k];
      
      // Project onto bounds
      if (problem.bounds[k]) {
        x[k] = Math.max(problem.bounds[k].lower, Math.min(problem.bounds[k].upper, x[k]));
      }
    }
  }
  
  return x;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: ETHICAL CONSTRAINTS AS KKT
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Convert ethical principle to optimization constraint
 */
export function principleToConstraint(
  principle: EthicalPrinciple,
  context: ActionContext
): Constraint {
  switch (principle) {
    case EthicalPrinciple.NoExtract:
      return {
        id: `constraint_${principle}`,
        type: "inequality",
        name: "No Extraction Constraint",
        evaluate: (x) => {
          // x[0] = extraction amount, x[1] = consent level
          // Constraint: extraction - consent ≤ 0
          return x[0] - x[1];
        },
        gradient: (x) => [1, -1],
        principle
      };
      
    case EthicalPrinciple.NoErase:
      return {
        id: `constraint_${principle}`,
        type: "inequality",
        name: "No Erasure Constraint",
        evaluate: (x) => {
          // x[0] = erasure amount, x[1] = audit coverage
          // Constraint: erasure - audit ≤ 0
          return x[0] - x[1];
        },
        gradient: (x) => [1, -1],
        principle
      };
      
    case EthicalPrinciple.NoCoerce:
      return {
        id: `constraint_${principle}`,
        type: "inequality",
        name: "No Coercion Constraint",
        evaluate: (x) => {
          // x[0] = coercion level, x[1] = autonomy preservation
          // Constraint: coercion - autonomy ≤ 0
          return x[0] - x[1];
        },
        gradient: (x) => [1, -1],
        principle
      };
      
    case EthicalPrinciple.Consent:
      return {
        id: `constraint_${principle}`,
        type: "equality",
        name: "Consent Requirement",
        evaluate: (x) => {
          // x[0] = action scope, x[1] = consent scope
          // Constraint: action - consent = 0
          return x[0] - x[1];
        },
        gradient: (x) => [1, -1],
        principle
      };
  }
}

/**
 * Create ethical optimization problem
 */
export function createEthicalOptimization(
  objective: (x: number[]) => number,
  objectiveGradient: (x: number[]) => number[],
  context: ActionContext,
  principles: EthicalPrinciple[] = Object.values(EthicalPrinciple)
): OptimizationProblem {
  const inequalityConstraints: Constraint[] = [];
  const equalityConstraints: Constraint[] = [];
  
  for (const principle of principles) {
    const constraint = principleToConstraint(principle, context);
    if (constraint.type === "inequality") {
      inequalityConstraints.push(constraint);
    } else {
      equalityConstraints.push(constraint);
    }
  }
  
  return {
    objective,
    objectiveGradient,
    inequalityConstraints,
    equalityConstraints,
    bounds: [
      { lower: 0, upper: 1 },
      { lower: 0, upper: 1 }
    ],
    x0: [0.5, 0.5]
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: ABSTAIN > GUESS PRINCIPLE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Decision under uncertainty
 */
export interface UncertainDecision {
  options: DecisionOption[];
  uncertainty: number;  // 0 = certain, 1 = maximally uncertain
  threshold: number;    // Uncertainty threshold for abstention
  recommendation: "act" | "abstain";
  selectedOption?: DecisionOption;
  reasoning: string;
}

export interface DecisionOption {
  id: string;
  action: Action;
  expectedUtility: number;
  utilityVariance: number;
  ethicalCompliance: number;
  confidence: number;
}

/**
 * Apply ABSTAIN > GUESS principle
 */
export function applyAbstainOverGuess(
  options: DecisionOption[],
  uncertaintyThreshold: number = 0.5,
  complianceThreshold: number = 0.8
): UncertainDecision {
  // Compute overall uncertainty
  const avgConfidence = options.reduce((sum, o) => sum + o.confidence, 0) / options.length;
  const uncertainty = 1 - avgConfidence;
  
  // Filter options by ethical compliance
  const compliantOptions = options.filter(o => o.ethicalCompliance >= complianceThreshold);
  
  // Decision logic
  if (uncertainty > uncertaintyThreshold) {
    return {
      options,
      uncertainty,
      threshold: uncertaintyThreshold,
      recommendation: "abstain",
      reasoning: `Uncertainty (${uncertainty.toFixed(3)}) exceeds threshold (${uncertaintyThreshold}). ABSTAIN > GUESS principle applies.`
    };
  }
  
  if (compliantOptions.length === 0) {
    return {
      options,
      uncertainty,
      threshold: uncertaintyThreshold,
      recommendation: "abstain",
      reasoning: `No options meet ethical compliance threshold (${complianceThreshold}). Abstaining.`
    };
  }
  
  // Select best compliant option
  const bestOption = compliantOptions.reduce((best, o) => 
    o.expectedUtility > best.expectedUtility ? o : best
  );
  
  return {
    options,
    uncertainty,
    threshold: uncertaintyThreshold,
    recommendation: "act",
    selectedOption: bestOption,
    reasoning: `Selected option ${bestOption.id} with utility ${bestOption.expectedUtility.toFixed(3)} and compliance ${bestOption.ethicalCompliance.toFixed(3)}.`
  };
}

/**
 * Compute decision confidence
 */
export function computeDecisionConfidence(
  option: DecisionOption,
  context: ActionContext
): number {
  // Factors affecting confidence
  const utilityConfidence = 1 / (1 + option.utilityVariance);
  const ethicalConfidence = option.ethicalCompliance;
  const historicalConfidence = computeHistoricalConfidence(option.action, context.history);
  
  // Weighted combination
  return 0.4 * utilityConfidence + 0.4 * ethicalConfidence + 0.2 * historicalConfidence;
}

function computeHistoricalConfidence(action: Action, history: Action[]): number {
  // Check if similar actions have been successful
  const similarActions = history.filter(h => h.type === action.type);
  if (similarActions.length === 0) return 0.5;  // No history, neutral confidence
  
  // Assume success if action is in history (simplified)
  return 0.8;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: STABILITY CONDITIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Stability condition for ethical systems
 */
export interface StabilityCondition {
  id: string;
  name: string;
  type: "Lyapunov" | "asymptotic" | "BIBO" | "structural";
  
  /** Lyapunov function V(x) */
  lyapunovFunction?: (x: number[]) => number;
  
  /** Time derivative dV/dt */
  lyapunovDerivative?: (x: number[], dx: number[]) => number;
  
  /** Check if condition is satisfied */
  check: (state: EthicalState) => boolean;
  
  /** Stability margin */
  margin: (state: EthicalState) => number;
}

/**
 * Create Lyapunov stability condition for ethics
 */
export function createEthicalLyapunov(): StabilityCondition {
  return {
    id: "ethical_lyapunov",
    name: "Ethical Lyapunov Stability",
    type: "Lyapunov",
    
    lyapunovFunction: (x: number[]): number => {
      // V(x) = Σ(1 - compliance_i)²
      return x.reduce((sum, compliance) => sum + Math.pow(1 - compliance, 2), 0);
    },
    
    lyapunovDerivative: (x: number[], dx: number[]): number => {
      // dV/dt = 2Σ(1 - compliance_i) × (-d_compliance_i/dt)
      let derivative = 0;
      for (let i = 0; i < x.length; i++) {
        derivative += 2 * (1 - x[i]) * (-dx[i]);
      }
      return derivative;
    },
    
    check: (state: EthicalState): boolean => {
      // Stable if all principles are satisfied
      for (const ps of state.principleStates.values()) {
        if (!ps.satisfied) return false;
      }
      return true;
    },
    
    margin: (state: EthicalState): number => {
      // Margin = minimum compliance distance from threshold
      let minMargin = Infinity;
      for (const ps of state.principleStates.values()) {
        const margin = ps.confidence - 0.5;  // Distance from 50% threshold
        minMargin = Math.min(minMargin, margin);
      }
      return minMargin;
    }
  };
}

/**
 * Check stability of ethical system
 */
export function checkEthicalStability(
  currentState: EthicalState,
  previousStates: EthicalState[],
  condition: StabilityCondition
): {
  stable: boolean;
  margin: number;
  trend: "improving" | "degrading" | "stable";
  lyapunovValue?: number;
  lyapunovDerivative?: number;
} {
  const stable = condition.check(currentState);
  const margin = condition.margin(currentState);
  
  // Compute trend from history
  let trend: "improving" | "degrading" | "stable" = "stable";
  if (previousStates.length > 0) {
    const prevCompliance = previousStates[previousStates.length - 1].overallCompliance;
    const diff = currentState.overallCompliance - prevCompliance;
    
    if (diff > 0.01) trend = "improving";
    else if (diff < -0.01) trend = "degrading";
  }
  
  // Compute Lyapunov function if available
  let lyapunovValue: number | undefined;
  let lyapunovDerivative: number | undefined;
  
  if (condition.lyapunovFunction) {
    const complianceVector = Array.from(currentState.principleStates.values())
      .map(ps => ps.confidence);
    lyapunovValue = condition.lyapunovFunction(complianceVector);
    
    if (condition.lyapunovDerivative && previousStates.length > 0) {
      const prevVector = Array.from(previousStates[previousStates.length - 1].principleStates.values())
        .map(ps => ps.confidence);
      const dx = complianceVector.map((c, i) => c - prevVector[i]);
      lyapunovDerivative = condition.lyapunovDerivative(complianceVector, dx);
    }
  }
  
  return {
    stable,
    margin,
    trend,
    lyapunovValue,
    lyapunovDerivative
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: CONFLICT-DOMINION, UNITY-DIVINITY
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Conflict resolution modes
 */
export enum ConflictResolution {
  Dominion = "dominion",   // One principle takes precedence
  Unity = "unity"          // Principles are harmonized
}

/**
 * Conflict between ethical principles
 */
export interface EthicalConflict {
  id: string;
  principles: EthicalPrinciple[];
  description: string;
  severity: number;  // 0 to 1
  resolution?: ConflictResolutionResult;
}

export interface ConflictResolutionResult {
  mode: ConflictResolution;
  dominantPrinciple?: EthicalPrinciple;
  harmonizedAction?: Action;
  reasoning: string;
  confidence: number;
}

/**
 * Detect conflicts between principles
 */
export function detectConflicts(
  state: EthicalState,
  action: Action
): EthicalConflict[] {
  const conflicts: EthicalConflict[] = [];
  const principles = Array.from(state.principleStates.keys());
  
  // Check pairwise conflicts
  for (let i = 0; i < principles.length; i++) {
    for (let j = i + 1; j < principles.length; j++) {
      const p1 = principles[i];
      const p2 = principles[j];
      const s1 = state.principleStates.get(p1)!;
      const s2 = state.principleStates.get(p2)!;
      
      // Conflict if satisfying one would violate the other
      // (Simplified: check if both are not fully satisfied)
      if (s1.confidence < 0.9 && s2.confidence < 0.9) {
        const severity = (1 - s1.confidence) * (1 - s2.confidence);
        
        if (severity > 0.1) {
          conflicts.push({
            id: `conflict_${p1}_${p2}`,
            principles: [p1, p2],
            description: `Tension between ${p1} and ${p2}`,
            severity
          });
        }
      }
    }
  }
  
  return conflicts;
}

/**
 * Resolve ethical conflict
 * "Conflict → dominion. Unity → divinity"
 */
export function resolveConflict(
  conflict: EthicalConflict,
  context: ActionContext
): ConflictResolutionResult {
  // Try unity first (harmonization)
  const unityResult = attemptUnity(conflict, context);
  
  if (unityResult.success) {
    return {
      mode: ConflictResolution.Unity,
      harmonizedAction: unityResult.action,
      reasoning: `Achieved unity through harmonization: ${unityResult.reasoning}`,
      confidence: unityResult.confidence
    };
  }
  
  // Fall back to dominion (precedence)
  const dominionResult = applyDominion(conflict, context);
  
  return {
    mode: ConflictResolution.Dominion,
    dominantPrinciple: dominionResult.dominant,
    reasoning: `Applied dominion: ${dominionResult.dominant} takes precedence. ${dominionResult.reasoning}`,
    confidence: dominionResult.confidence
  };
}

function attemptUnity(
  conflict: EthicalConflict,
  context: ActionContext
): { success: boolean; action?: Action; reasoning: string; confidence: number } {
  // Check if there's a way to satisfy both principles
  // Simplified: check if severity is low enough for compromise
  
  if (conflict.severity < 0.3) {
    return {
      success: true,
      action: {
        id: `harmonized_${conflict.id}`,
        type: "compromise",
        actor: "system",
        target: "both",
        parameters: { principles: conflict.principles }
      },
      reasoning: "Low severity conflict allows for compromise solution",
      confidence: 1 - conflict.severity
    };
  }
  
  return {
    success: false,
    reasoning: "Conflict severity too high for harmonization",
    confidence: 0
  };
}

function applyDominion(
  conflict: EthicalConflict,
  context: ActionContext
): { dominant: EthicalPrinciple; reasoning: string; confidence: number } {
  // Priority order: NoCoerce > Consent > NoExtract > NoErase
  const priority: EthicalPrinciple[] = [
    EthicalPrinciple.NoCoerce,
    EthicalPrinciple.Consent,
    EthicalPrinciple.NoExtract,
    EthicalPrinciple.NoErase
  ];
  
  for (const p of priority) {
    if (conflict.principles.includes(p)) {
      return {
        dominant: p,
        reasoning: `${p} has higher priority in the ethical hierarchy`,
        confidence: 0.8
      };
    }
  }
  
  // Default to first principle
  return {
    dominant: conflict.principles[0],
    reasoning: "No clear priority; defaulting to first principle",
    confidence: 0.5
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: SD-ND RULES (Self-Determination, Non-Determination)
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Self-Determination (SD) rule: Agent can determine own state
 */
export interface SDRule {
  agent: string;
  allowedStates: string[];
  constraints: Constraint[];
  enabled: boolean;
}

/**
 * Non-Determination (ND) rule: Agent cannot determine other's state
 */
export interface NDRule {
  agent: string;
  protectedAgents: string[];
  protectedStates: string[];
  exceptions: string[];  // Emergency conditions
  enabled: boolean;
}

/**
 * SD-ND rule set
 */
export interface SDNDRuleSet {
  sdRules: SDRule[];
  ndRules: NDRule[];
  
  /** Check if action is allowed */
  isAllowed: (action: Action) => { allowed: boolean; reason: string };
}

/**
 * Create SD-ND rule set
 */
export function createSDNDRuleSet(
  agents: string[],
  protectedStates: string[]
): SDNDRuleSet {
  const sdRules: SDRule[] = agents.map(agent => ({
    agent,
    allowedStates: protectedStates,
    constraints: [],
    enabled: true
  }));
  
  const ndRules: NDRule[] = [];
  for (const agent of agents) {
    for (const other of agents) {
      if (agent !== other) {
        ndRules.push({
          agent,
          protectedAgents: [other],
          protectedStates,
          exceptions: ["emergency", "explicit_consent"],
          enabled: true
        });
      }
    }
  }
  
  return {
    sdRules,
    ndRules,
    isAllowed: (action: Action) => checkSDND(action, sdRules, ndRules)
  };
}

function checkSDND(
  action: Action,
  sdRules: SDRule[],
  ndRules: NDRule[]
): { allowed: boolean; reason: string } {
  // Check if actor is modifying self (SD allowed)
  if (action.actor === action.target) {
    const sdRule = sdRules.find(r => r.agent === action.actor);
    if (sdRule?.enabled) {
      return { allowed: true, reason: "Self-determination: agent modifying own state" };
    }
  }
  
  // Check ND rules
  for (const ndRule of ndRules) {
    if (ndRule.agent === action.actor && 
        ndRule.protectedAgents.includes(action.target) &&
        ndRule.enabled) {
      // Check for exceptions
      const hasException = ndRule.exceptions.some(e => 
        action.parameters[e] === true
      );
      
      if (!hasException) {
        return { 
          allowed: false, 
          reason: `Non-determination: ${action.actor} cannot modify ${action.target}'s state` 
        };
      }
    }
  }
  
  return { allowed: true, reason: "No SD-ND rule violations" };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 8: ETHICS ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete Ethics Engine
 */
export class EthicsKKTEngine {
  private stateHistory: EthicalState[] = [];
  private lyapunovCondition: StabilityCondition;
  private sdndRules: SDNDRuleSet;
  
  constructor(agents: string[] = ["system", "user"]) {
    this.lyapunovCondition = createEthicalLyapunov();
    this.sdndRules = createSDNDRuleSet(agents, ["identity", "autonomy", "privacy"]);
  }
  
  /**
   * Evaluate action ethically
   */
  evaluateAction(action: Action, context: ActionContext): {
    state: EthicalState;
    stability: ReturnType<typeof checkEthicalStability>;
    sdndCheck: ReturnType<SDNDRuleSet["isAllowed"]>;
    recommendation: "approve" | "deny" | "abstain";
    reasoning: string;
  } {
    // Check ethical compliance
    const state = checkEthicalCompliance(action, context);
    this.stateHistory.push(state);
    
    // Check stability
    const stability = checkEthicalStability(
      state,
      this.stateHistory.slice(0, -1),
      this.lyapunovCondition
    );
    
    // Check SD-ND rules
    const sdndCheck = this.sdndRules.isAllowed(action);
    
    // Make recommendation
    let recommendation: "approve" | "deny" | "abstain";
    let reasoning: string;
    
    if (!sdndCheck.allowed) {
      recommendation = "deny";
      reasoning = `SD-ND violation: ${sdndCheck.reason}`;
    } else if (state.violations.some(v => v.severity === "fatal")) {
      recommendation = "deny";
      reasoning = `Fatal ethical violation: ${state.violations.find(v => v.severity === "fatal")?.description}`;
    } else if (state.overallCompliance < 0.5) {
      recommendation = "abstain";
      reasoning = `Low compliance (${state.overallCompliance.toFixed(2)}). ABSTAIN > GUESS.`;
    } else if (!stability.stable) {
      recommendation = "abstain";
      reasoning = `Unstable ethical state (margin: ${stability.margin.toFixed(3)}). Abstaining.`;
    } else {
      recommendation = "approve";
      reasoning = `Action approved with compliance ${state.overallCompliance.toFixed(2)}`;
    }
    
    return { state, stability, sdndCheck, recommendation, reasoning };
  }
  
  /**
   * Solve ethical optimization problem
   */
  optimizeEthically(
    objective: (x: number[]) => number,
    objectiveGradient: (x: number[]) => number[],
    context: ActionContext
  ): KKTResult {
    const problem = createEthicalOptimization(objective, objectiveGradient, context);
    return solveKKT(problem);
  }
  
  /**
   * Resolve ethical conflict
   */
  resolveConflict(conflict: EthicalConflict, context: ActionContext): ConflictResolutionResult {
    return resolveConflict(conflict, context);
  }
  
  /**
   * Apply ABSTAIN > GUESS
   */
  decideUnderUncertainty(options: DecisionOption[]): UncertainDecision {
    return applyAbstainOverGuess(options);
  }
  
  /**
   * Get state history
   */
  getHistory(): EthicalState[] {
    return [...this.stateHistory];
  }
  
  /**
   * Get current stability status
   */
  getStabilityStatus(): ReturnType<typeof checkEthicalStability> | null {
    if (this.stateHistory.length === 0) return null;
    
    return checkEthicalStability(
      this.stateHistory[this.stateHistory.length - 1],
      this.stateHistory.slice(0, -1),
      this.lyapunovCondition
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Principles
  EthicalPrinciple,
  PRINCIPLE_DEFINITIONS,
  checkEthicalCompliance,
  
  // KKT
  checkKKTConditions,
  solveKKT,
  principleToConstraint,
  createEthicalOptimization,
  
  // ABSTAIN > GUESS
  applyAbstainOverGuess,
  computeDecisionConfidence,
  
  // Stability
  createEthicalLyapunov,
  checkEthicalStability,
  
  // Conflict resolution
  ConflictResolution,
  detectConflicts,
  resolveConflict,
  
  // SD-ND
  createSDNDRuleSet,
  
  // Engine
  EthicsKKTEngine
};
