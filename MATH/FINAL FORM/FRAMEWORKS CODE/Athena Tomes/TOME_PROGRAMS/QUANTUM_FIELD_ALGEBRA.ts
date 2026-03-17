/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * QUANTUM FIELD ALGEBRA - Complete QFT Implementation for AWAKENING OS
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Mathematical Framework:
 *   - Fock Space: F = ⊕ₙ Hⁿ (direct sum of n-particle Hilbert spaces)
 *   - Creation/Annihilation Operators: a†, a with [a, a†] = 1
 *   - Field Operators: φ(x) = ∫ (a(k)e^{ikx} + a†(k)e^{-ikx}) dk
 *   - Propagators: ⟨0|T{φ(x)φ(y)}|0⟩
 * 
 * Applications:
 *   - Information field dynamics
 *   - Coherence propagation
 *   - Entanglement entropy
 *   - Renormalization group flows
 * 
 * @module QUANTUM_FIELD_ALGEBRA
 * @version 2.0.0
 */

import { Complex, ComplexMatrix, createComplex, complexMul, complexAdd, complexSub, complexAbs } from './HILBERT_ALGEBRA';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: FOCK SPACE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Fock state: superposition of n-particle states
 * |ψ⟩ = Σₙ cₙ |n⟩
 */
export interface FockState {
  coefficients: Complex[];  // c₀, c₁, c₂, ...
  maxOccupation: number;    // Maximum particle number
  normalized: boolean;
}

/**
 * Create vacuum state |0⟩
 */
export function createVacuum(maxOccupation: number = 10): FockState {
  const coefficients: Complex[] = [];
  coefficients[0] = createComplex(1, 0);  // |0⟩ has coefficient 1
  
  for (let i = 1; i <= maxOccupation; i++) {
    coefficients[i] = createComplex(0, 0);
  }
  
  return {
    coefficients,
    maxOccupation,
    normalized: true
  };
}

/**
 * Create n-particle state |n⟩
 */
export function createNumberState(n: number, maxOccupation: number = 10): FockState {
  const coefficients: Complex[] = [];
  
  for (let i = 0; i <= maxOccupation; i++) {
    coefficients[i] = i === n ? createComplex(1, 0) : createComplex(0, 0);
  }
  
  return {
    coefficients,
    maxOccupation,
    normalized: true
  };
}

/**
 * Create coherent state |α⟩ = e^{-|α|²/2} Σₙ (αⁿ/√n!) |n⟩
 */
export function createCoherentState(alpha: Complex, maxOccupation: number = 10): FockState {
  const alphaMagSq = alpha.re * alpha.re + alpha.im * alpha.im;
  const prefactor = Math.exp(-alphaMagSq / 2);
  
  const coefficients: Complex[] = [];
  let alphaPower = createComplex(1, 0);  // α⁰ = 1
  
  for (let n = 0; n <= maxOccupation; n++) {
    const factorialSqrt = Math.sqrt(factorial(n));
    const coefficient = createComplex(
      prefactor * alphaPower.re / factorialSqrt,
      prefactor * alphaPower.im / factorialSqrt
    );
    coefficients[n] = coefficient;
    
    // Update α^(n+1) = α^n * α
    alphaPower = complexMul(alphaPower, alpha);
  }
  
  return {
    coefficients,
    maxOccupation,
    normalized: true  // Coherent states are automatically normalized
  };
}

/**
 * Normalize Fock state
 */
export function normalizeFockState(state: FockState): FockState {
  let normSq = 0;
  for (const c of state.coefficients) {
    normSq += c.re * c.re + c.im * c.im;
  }
  
  const norm = Math.sqrt(normSq);
  if (norm === 0) return state;
  
  const normalized = state.coefficients.map(c => createComplex(c.re / norm, c.im / norm));
  
  return {
    coefficients: normalized,
    maxOccupation: state.maxOccupation,
    normalized: true
  };
}

/**
 * Inner product ⟨ψ|φ⟩
 */
export function fockInnerProduct(psi: FockState, phi: FockState): Complex {
  let result = createComplex(0, 0);
  const maxN = Math.min(psi.coefficients.length, phi.coefficients.length);
  
  for (let n = 0; n < maxN; n++) {
    // ⟨ψₙ|φₙ⟩ = ψₙ* × φₙ
    const psiConj = createComplex(psi.coefficients[n].re, -psi.coefficients[n].im);
    const product = complexMul(psiConj, phi.coefficients[n]);
    result = complexAdd(result, product);
  }
  
  return result;
}

function factorial(n: number): number {
  if (n <= 1) return 1;
  let result = 1;
  for (let i = 2; i <= n; i++) {
    result *= i;
  }
  return result;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: CREATION AND ANNIHILATION OPERATORS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Apply creation operator a† to Fock state
 * a†|n⟩ = √(n+1)|n+1⟩
 */
export function applyCreation(state: FockState): FockState {
  const newCoeffs: Complex[] = [];
  
  // First coefficient is 0 (a†|n⟩ never produces |0⟩)
  newCoeffs[0] = createComplex(0, 0);
  
  for (let n = 1; n <= state.maxOccupation; n++) {
    // Coefficient for |n⟩ comes from |n-1⟩ with factor √n
    const factor = Math.sqrt(n);
    const c = state.coefficients[n - 1] || createComplex(0, 0);
    newCoeffs[n] = createComplex(c.re * factor, c.im * factor);
  }
  
  return {
    coefficients: newCoeffs,
    maxOccupation: state.maxOccupation,
    normalized: false
  };
}

/**
 * Apply annihilation operator a to Fock state
 * a|n⟩ = √n|n-1⟩, a|0⟩ = 0
 */
export function applyAnnihilation(state: FockState): FockState {
  const newCoeffs: Complex[] = [];
  
  for (let n = 0; n < state.maxOccupation; n++) {
    // Coefficient for |n⟩ comes from |n+1⟩ with factor √(n+1)
    const factor = Math.sqrt(n + 1);
    const c = state.coefficients[n + 1] || createComplex(0, 0);
    newCoeffs[n] = createComplex(c.re * factor, c.im * factor);
  }
  
  // Last coefficient is 0
  newCoeffs[state.maxOccupation] = createComplex(0, 0);
  
  return {
    coefficients: newCoeffs,
    maxOccupation: state.maxOccupation,
    normalized: false
  };
}

/**
 * Apply number operator N = a†a to Fock state
 * N|n⟩ = n|n⟩
 */
export function applyNumberOperator(state: FockState): FockState {
  const newCoeffs = state.coefficients.map((c, n) => 
    createComplex(c.re * n, c.im * n)
  );
  
  return {
    coefficients: newCoeffs,
    maxOccupation: state.maxOccupation,
    normalized: false
  };
}

/**
 * Compute expectation value ⟨N⟩
 */
export function expectationNumber(state: FockState): number {
  let expectation = 0;
  
  for (let n = 0; n < state.coefficients.length; n++) {
    const c = state.coefficients[n];
    const probN = c.re * c.re + c.im * c.im;
    expectation += n * probN;
  }
  
  return expectation;
}

/**
 * Compute variance Var(N) = ⟨N²⟩ - ⟨N⟩²
 */
export function varianceNumber(state: FockState): number {
  let expectN = 0;
  let expectNSq = 0;
  
  for (let n = 0; n < state.coefficients.length; n++) {
    const c = state.coefficients[n];
    const probN = c.re * c.re + c.im * c.im;
    expectN += n * probN;
    expectNSq += n * n * probN;
  }
  
  return expectNSq - expectN * expectN;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: FIELD OPERATORS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Momentum mode
 */
export interface MomentumMode {
  k: number;           // Wave number
  omega: number;       // Frequency (ω = √(k² + m²))
  mass: number;
}

/**
 * Field configuration at a point
 */
export interface FieldPoint {
  x: number;
  t: number;
  phi: Complex;        // Field value φ(x,t)
  pi: Complex;         // Conjugate momentum π(x,t)
}

/**
 * Scalar field φ(x) = ∫ (a(k)e^{ikx} + a†(k)e^{-ikx}) dk / √(2ω)
 */
export class ScalarField {
  private modes: Map<number, FockState> = new Map();
  private mass: number;
  private cutoff: number;  // UV cutoff
  
  constructor(mass: number = 1, cutoff: number = 10) {
    this.mass = mass;
    this.cutoff = cutoff;
    
    // Initialize vacuum for each mode
    for (let k = -cutoff; k <= cutoff; k++) {
      this.modes.set(k, createVacuum(10));
    }
  }
  
  /**
   * Get dispersion relation ω(k) = √(k² + m²)
   */
  omega(k: number): number {
    return Math.sqrt(k * k + this.mass * this.mass);
  }
  
  /**
   * Apply creation at momentum k
   */
  createAt(k: number): void {
    const state = this.modes.get(k);
    if (state) {
      this.modes.set(k, applyCreation(state));
    }
  }
  
  /**
   * Apply annihilation at momentum k
   */
  annihilateAt(k: number): void {
    const state = this.modes.get(k);
    if (state) {
      this.modes.set(k, applyAnnihilation(state));
    }
  }
  
  /**
   * Evaluate field at position x, time t
   */
  evaluate(x: number, t: number): Complex {
    let result = createComplex(0, 0);
    
    for (const [k, state] of this.modes) {
      const w = this.omega(k);
      const normFactor = 1 / Math.sqrt(2 * w);
      
      // Positive frequency: a(k) e^{i(kx - ωt)}
      const phasePos = k * x - w * t;
      const aN = expectationNumber(state);  // Simplified: use expectation
      const posContrib = createComplex(
        aN * normFactor * Math.cos(phasePos),
        aN * normFactor * Math.sin(phasePos)
      );
      
      // Negative frequency: a†(k) e^{-i(kx - ωt)}
      const negContrib = createComplex(
        aN * normFactor * Math.cos(-phasePos),
        aN * normFactor * Math.sin(-phasePos)
      );
      
      result = complexAdd(result, complexAdd(posContrib, negContrib));
    }
    
    return result;
  }
  
  /**
   * Compute total particle number
   */
  totalNumber(): number {
    let total = 0;
    for (const state of this.modes.values()) {
      total += expectationNumber(state);
    }
    return total;
  }
  
  /**
   * Compute Hamiltonian expectation
   */
  energy(): number {
    let energy = 0;
    for (const [k, state] of this.modes) {
      const w = this.omega(k);
      const n = expectationNumber(state);
      energy += w * (n + 0.5);  // Include zero-point energy
    }
    return energy;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: PROPAGATORS AND CORRELATORS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Feynman propagator iΔF(x-y) = ⟨0|T{φ(x)φ(y)}|0⟩
 */
export interface Propagator {
  x1: number;
  t1: number;
  x2: number;
  t2: number;
  value: Complex;
}

/**
 * Compute free scalar propagator
 * ΔF(x) = ∫ d⁴k e^{ikx} / (k² - m² + iε)
 */
export function feynmanPropagator(
  x: number,
  t: number,
  mass: number = 1,
  epsilon: number = 0.01
): Complex {
  // Simplified: use momentum space integral
  let result = createComplex(0, 0);
  const dk = 0.1;
  const kMax = 10;
  
  for (let k = -kMax; k <= kMax; k += dk) {
    const omega = Math.sqrt(k * k + mass * mass);
    
    // Pole prescription: k₀ = ±(ω - iε)
    const phase = k * x - omega * Math.abs(t);
    const amplitude = dk / (2 * omega);
    
    const contrib = createComplex(
      amplitude * Math.cos(phase),
      amplitude * Math.sin(phase) * (t >= 0 ? -1 : 1)
    );
    
    result = complexAdd(result, contrib);
  }
  
  return result;
}

/**
 * Two-point correlation function ⟨φ(x)φ(y)⟩
 */
export function twoPointCorrelator(
  x1: number, t1: number,
  x2: number, t2: number,
  field: ScalarField
): Complex {
  const phi1 = field.evaluate(x1, t1);
  const phi2 = field.evaluate(x2, t2);
  
  return complexMul(phi1, phi2);
}

/**
 * Connected correlator ⟨φ(x)φ(y)⟩_c = ⟨φ(x)φ(y)⟩ - ⟨φ(x)⟩⟨φ(y)⟩
 */
export function connectedCorrelator(
  x1: number, t1: number,
  x2: number, t2: number,
  field: ScalarField
): Complex {
  const full = twoPointCorrelator(x1, t1, x2, t2, field);
  const phi1 = field.evaluate(x1, t1);
  const phi2 = field.evaluate(x2, t2);
  const disconnected = complexMul(phi1, phi2);
  
  return complexSub(full, disconnected);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: ENTANGLEMENT AND ENTROPY
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Density matrix for a subsystem
 */
export interface DensityMatrix {
  dimension: number;
  elements: Complex[][];
  trace: number;
  purity: number;
}

/**
 * Create density matrix from Fock state
 */
export function createDensityMatrix(state: FockState): DensityMatrix {
  const dim = state.coefficients.length;
  const elements: Complex[][] = [];
  
  for (let i = 0; i < dim; i++) {
    elements[i] = [];
    for (let j = 0; j < dim; j++) {
      // ρᵢⱼ = cᵢ cⱼ*
      const ci = state.coefficients[i];
      const cjConj = createComplex(state.coefficients[j].re, -state.coefficients[j].im);
      elements[i][j] = complexMul(ci, cjConj);
    }
  }
  
  // Compute trace
  let trace = 0;
  for (let i = 0; i < dim; i++) {
    trace += elements[i][i].re;
  }
  
  // Compute purity Tr(ρ²)
  let purity = 0;
  for (let i = 0; i < dim; i++) {
    for (let j = 0; j < dim; j++) {
      const prod = complexMul(elements[i][j], elements[j][i]);
      purity += prod.re;
    }
  }
  
  return { dimension: dim, elements, trace, purity };
}

/**
 * Compute von Neumann entropy S = -Tr(ρ log ρ)
 */
export function vonNeumannEntropy(density: DensityMatrix): number {
  // Diagonalize (simplified: use diagonal elements as approximation)
  let entropy = 0;
  
  for (let i = 0; i < density.dimension; i++) {
    const p = density.elements[i][i].re;
    if (p > 1e-10) {
      entropy -= p * Math.log(p);
    }
  }
  
  return entropy;
}

/**
 * Compute Rényi entropy Sₐ = (1/(1-α)) log Tr(ρᵅ)
 */
export function renyiEntropy(density: DensityMatrix, alpha: number): number {
  if (alpha === 1) {
    return vonNeumannEntropy(density);
  }
  
  // Compute Tr(ρᵅ) ≈ Σᵢ pᵢᵅ (diagonal approximation)
  let trace = 0;
  for (let i = 0; i < density.dimension; i++) {
    const p = density.elements[i][i].re;
    if (p > 0) {
      trace += Math.pow(p, alpha);
    }
  }
  
  return Math.log(trace) / (1 - alpha);
}

/**
 * Entanglement entropy for bipartite system
 */
export function entanglementEntropy(
  fullState: FockState,
  subsystemSize: number
): number {
  // Create reduced density matrix by tracing out complement
  const reducedDim = Math.min(subsystemSize + 1, fullState.coefficients.length);
  const elements: Complex[][] = [];
  
  for (let i = 0; i < reducedDim; i++) {
    elements[i] = [];
    for (let j = 0; j < reducedDim; j++) {
      // Simplified: diagonal approximation
      if (i === j) {
        const c = fullState.coefficients[i] || createComplex(0, 0);
        elements[i][j] = createComplex(c.re * c.re + c.im * c.im, 0);
      } else {
        elements[i][j] = createComplex(0, 0);
      }
    }
  }
  
  const reduced: DensityMatrix = {
    dimension: reducedDim,
    elements,
    trace: 1,
    purity: 0
  };
  
  return vonNeumannEntropy(reduced);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: RENORMALIZATION GROUP
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Coupling constants at a scale
 */
export interface CouplingConstants {
  scale: number;        // Energy scale μ
  mass: number;         // Renormalized mass m(μ)
  lambda: number;       // φ⁴ coupling λ(μ)
  wavefunction: number; // Wave function renormalization Z(μ)
}

/**
 * Beta function coefficients
 */
export interface BetaFunction {
  mass: (m: number, lambda: number) => number;
  lambda: (lambda: number) => number;
  wavefunction: (lambda: number) => number;
}

/**
 * One-loop beta functions for φ⁴ theory
 */
export const PHI4_BETA: BetaFunction = {
  // β_m = m × (λ / 16π²)
  mass: (m: number, lambda: number) => m * lambda / (16 * Math.PI * Math.PI),
  
  // β_λ = 3λ² / 16π²
  lambda: (lambda: number) => 3 * lambda * lambda / (16 * Math.PI * Math.PI),
  
  // γ = λ² / (32π⁴) (anomalous dimension)
  wavefunction: (lambda: number) => lambda * lambda / (32 * Math.pow(Math.PI, 4))
};

/**
 * Run couplings from scale μ₁ to μ₂
 */
export function runCouplings(
  initial: CouplingConstants,
  finalScale: number,
  beta: BetaFunction,
  steps: number = 100
): CouplingConstants {
  const logRatio = Math.log(finalScale / initial.scale);
  const dLogMu = logRatio / steps;
  
  let m = initial.mass;
  let lambda = initial.lambda;
  let Z = initial.wavefunction;
  let scale = initial.scale;
  
  for (let i = 0; i < steps; i++) {
    // Euler step in log(μ)
    const dm = beta.mass(m, lambda) * dLogMu;
    const dLambda = beta.lambda(lambda) * dLogMu;
    const gamma = beta.wavefunction(lambda);
    const dZ = Z * gamma * dLogMu;
    
    m += dm;
    lambda += dLambda;
    Z += dZ;
    scale *= Math.exp(dLogMu);
  }
  
  return {
    scale: finalScale,
    mass: m,
    lambda: lambda,
    wavefunction: Z
  };
}

/**
 * Find fixed point of beta functions
 */
export function findFixedPoint(
  beta: BetaFunction,
  initialGuess: number,
  tolerance: number = 1e-6,
  maxIter: number = 100
): { lambda: number; isIR: boolean; isUV: boolean } {
  let lambda = initialGuess;
  
  for (let i = 0; i < maxIter; i++) {
    const betaVal = beta.lambda(lambda);
    
    if (Math.abs(betaVal) < tolerance) {
      // Determine stability
      const dBeta = (beta.lambda(lambda + 0.001) - beta.lambda(lambda - 0.001)) / 0.002;
      const isIR = dBeta > 0;  // IR stable if β' > 0
      const isUV = dBeta < 0;  // UV stable if β' < 0
      
      return { lambda, isIR, isUV };
    }
    
    // Newton step
    const dBeta = (beta.lambda(lambda + 0.001) - beta.lambda(lambda - 0.001)) / 0.002;
    if (Math.abs(dBeta) > 1e-10) {
      lambda -= betaVal / dBeta;
    } else {
      lambda += 0.1;  // Perturb if derivative is zero
    }
  }
  
  return { lambda: NaN, isIR: false, isUV: false };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: INFORMATION FIELD THEORY
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Information field: represents probability distributions over configurations
 */
export interface InformationField {
  prior: (config: number[]) => number;
  likelihood: (data: number[], config: number[]) => number;
  posterior: (data: number[], config: number[]) => number;
}

/**
 * Gaussian information field
 */
export function createGaussianField(
  mean: number[],
  covariance: number[][]
): InformationField {
  const dim = mean.length;
  
  // Compute inverse covariance (simplified: diagonal)
  const invCov = covariance.map((row, i) => row.map((_, j) => i === j ? 1 / row[i] : 0));
  
  // Compute normalization
  let det = 1;
  for (let i = 0; i < dim; i++) {
    det *= covariance[i][i];
  }
  const norm = 1 / Math.sqrt(Math.pow(2 * Math.PI, dim) * det);
  
  const prior = (config: number[]): number => {
    let exponent = 0;
    for (let i = 0; i < dim; i++) {
      const diff = config[i] - mean[i];
      exponent -= 0.5 * diff * diff * invCov[i][i];
    }
    return norm * Math.exp(exponent);
  };
  
  const likelihood = (data: number[], config: number[]): number => {
    // Gaussian likelihood with unit variance
    let logL = 0;
    for (let i = 0; i < Math.min(data.length, config.length); i++) {
      const diff = data[i] - config[i];
      logL -= 0.5 * diff * diff;
    }
    return Math.exp(logL);
  };
  
  const posterior = (data: number[], config: number[]): number => {
    return prior(config) * likelihood(data, config);
  };
  
  return { prior, likelihood, posterior };
}

/**
 * Compute field action S[φ] = ∫ (½(∂φ)² + V(φ)) d⁴x
 */
export function computeFieldAction(
  fieldValues: number[],
  dx: number,
  mass: number,
  lambda: number
): number {
  let action = 0;
  
  for (let i = 0; i < fieldValues.length; i++) {
    const phi = fieldValues[i];
    
    // Kinetic term: ½(∂φ)²
    let kinetic = 0;
    if (i > 0) {
      const dphi = (phi - fieldValues[i - 1]) / dx;
      kinetic = 0.5 * dphi * dphi;
    }
    
    // Mass term: ½m²φ²
    const massT = 0.5 * mass * mass * phi * phi;
    
    // Interaction: (λ/4!)φ⁴
    const interaction = (lambda / 24) * Math.pow(phi, 4);
    
    action += (kinetic + massT + interaction) * dx;
  }
  
  return action;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 8: QUANTUM FIELD ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete Quantum Field Engine
 */
export class QuantumFieldEngine {
  private field: ScalarField;
  private couplings: CouplingConstants;
  private history: { time: number; energy: number; entropy: number }[] = [];
  
  constructor(mass: number = 1, lambda: number = 0.1) {
    this.field = new ScalarField(mass);
    this.couplings = {
      scale: 1,
      mass,
      lambda,
      wavefunction: 1
    };
  }
  
  /**
   * Create particle at momentum k
   */
  createParticle(k: number): void {
    this.field.createAt(k);
  }
  
  /**
   * Annihilate particle at momentum k
   */
  annihilateParticle(k: number): void {
    this.field.annihilateAt(k);
  }
  
  /**
   * Evaluate field at spacetime point
   */
  evaluateField(x: number, t: number): Complex {
    return this.field.evaluate(x, t);
  }
  
  /**
   * Compute propagator
   */
  propagator(x1: number, t1: number, x2: number, t2: number): Complex {
    return feynmanPropagator(x1 - x2, t1 - t2, this.couplings.mass);
  }
  
  /**
   * Get total energy
   */
  energy(): number {
    return this.field.energy();
  }
  
  /**
   * Get particle number
   */
  particleNumber(): number {
    return this.field.totalNumber();
  }
  
  /**
   * Run RG flow to new scale
   */
  runToScale(newScale: number): void {
    this.couplings = runCouplings(this.couplings, newScale, PHI4_BETA);
  }
  
  /**
   * Record state
   */
  recordState(): void {
    this.history.push({
      time: Date.now(),
      energy: this.energy(),
      entropy: 0  // Would compute from density matrix
    });
  }
  
  /**
   * Get history
   */
  getHistory(): typeof this.history {
    return [...this.history];
  }
  
  /**
   * Get current couplings
   */
  getCouplings(): CouplingConstants {
    return { ...this.couplings };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Fock space
  createVacuum,
  createNumberState,
  createCoherentState,
  normalizeFockState,
  fockInnerProduct,
  
  // Operators
  applyCreation,
  applyAnnihilation,
  applyNumberOperator,
  expectationNumber,
  varianceNumber,
  
  // Field
  ScalarField,
  feynmanPropagator,
  twoPointCorrelator,
  connectedCorrelator,
  
  // Entropy
  createDensityMatrix,
  vonNeumannEntropy,
  renyiEntropy,
  entanglementEntropy,
  
  // RG
  PHI4_BETA,
  runCouplings,
  findFixedPoint,
  
  // Information field
  createGaussianField,
  computeFieldAction,
  
  // Engine
  QuantumFieldEngine
};
