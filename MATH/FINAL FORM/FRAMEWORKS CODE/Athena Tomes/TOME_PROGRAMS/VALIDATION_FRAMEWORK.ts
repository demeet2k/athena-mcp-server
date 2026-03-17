/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * VALIDATION FRAMEWORK - Comprehensive Testing & Verification
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * This module provides complete validation infrastructure:
 * 
 * Test Categories:
 *   - Unit Tests: Individual function/class validation
 *   - Integration Tests: Cross-subsystem interaction
 *   - Property Tests: Invariant verification
 *   - Replay Tests: Determinism validation
 *   - Performance Tests: Budget compliance
 * 
 * Validation Domains:
 *   - Truth Discipline: Truth lattice operations
 *   - Addressing: Canonical form validation
 *   - Routing: Hub set constraints
 *   - Conservation: κ-conservation invariant
 *   - Replay: Deterministic execution
 * 
 * @module VALIDATION_FRAMEWORK
 * @version 2.0.0
 */

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: TEST TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Test status
 */
export enum TestStatus {
  Pending = "Pending",
  Running = "Running",
  Passed = "Passed",
  Failed = "Failed",
  Skipped = "Skipped"
}

/**
 * Test category
 */
export enum TestCategory {
  Unit = "Unit",
  Integration = "Integration",
  Property = "Property",
  Replay = "Replay",
  Performance = "Performance"
}

/**
 * Test case
 */
export interface TestCase {
  id: string;
  name: string;
  category: TestCategory;
  subsystem: string;
  description: string;
  run: () => Promise<TestResult>;
  timeout?: number;
  tags?: string[];
}

/**
 * Test result
 */
export interface TestResult {
  testId: string;
  status: TestStatus;
  duration: number;
  assertions: AssertionResult[];
  error?: string;
  output?: unknown;
}

export interface AssertionResult {
  assertion: string;
  passed: boolean;
  expected?: unknown;
  actual?: unknown;
  message?: string;
}

/**
 * Test suite
 */
export interface TestSuite {
  name: string;
  category: TestCategory;
  tests: TestCase[];
  setup?: () => Promise<void>;
  teardown?: () => Promise<void>;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: ASSERTION LIBRARY
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Assertion context
 */
export class AssertionContext {
  private results: AssertionResult[] = [];
  
  /**
   * Assert equality
   */
  assertEquals<T>(actual: T, expected: T, message?: string): void {
    const passed = JSON.stringify(actual) === JSON.stringify(expected);
    this.results.push({
      assertion: "assertEquals",
      passed,
      expected,
      actual,
      message: message ?? `Expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`
    });
  }
  
  /**
   * Assert truthy
   */
  assertTrue(value: unknown, message?: string): void {
    const passed = !!value;
    this.results.push({
      assertion: "assertTrue",
      passed,
      expected: true,
      actual: !!value,
      message: message ?? `Expected truthy value`
    });
  }
  
  /**
   * Assert falsy
   */
  assertFalse(value: unknown, message?: string): void {
    const passed = !value;
    this.results.push({
      assertion: "assertFalse",
      passed,
      expected: false,
      actual: !!value,
      message: message ?? `Expected falsy value`
    });
  }
  
  /**
   * Assert defined
   */
  assertDefined(value: unknown, message?: string): void {
    const passed = value !== undefined && value !== null;
    this.results.push({
      assertion: "assertDefined",
      passed,
      expected: "defined",
      actual: value === undefined ? "undefined" : value === null ? "null" : "defined",
      message: message ?? `Expected defined value`
    });
  }
  
  /**
   * Assert throws
   */
  async assertThrows(fn: () => unknown | Promise<unknown>, message?: string): Promise<void> {
    let threw = false;
    try {
      await fn();
    } catch {
      threw = true;
    }
    
    this.results.push({
      assertion: "assertThrows",
      passed: threw,
      expected: "exception",
      actual: threw ? "exception" : "no exception",
      message: message ?? `Expected function to throw`
    });
  }
  
  /**
   * Assert in range
   */
  assertInRange(value: number, min: number, max: number, message?: string): void {
    const passed = value >= min && value <= max;
    this.results.push({
      assertion: "assertInRange",
      passed,
      expected: `[${min}, ${max}]`,
      actual: value,
      message: message ?? `Expected ${value} to be in range [${min}, ${max}]`
    });
  }
  
  /**
   * Assert array contains
   */
  assertContains<T>(array: T[], item: T, message?: string): void {
    const passed = array.some(a => JSON.stringify(a) === JSON.stringify(item));
    this.results.push({
      assertion: "assertContains",
      passed,
      expected: item,
      actual: array,
      message: message ?? `Expected array to contain item`
    });
  }
  
  /**
   * Assert array length
   */
  assertLength(array: unknown[], expected: number, message?: string): void {
    const passed = array.length === expected;
    this.results.push({
      assertion: "assertLength",
      passed,
      expected,
      actual: array.length,
      message: message ?? `Expected length ${expected}, got ${array.length}`
    });
  }
  
  /**
   * Custom assertion
   */
  assert(passed: boolean, assertion: string, expected: unknown, actual: unknown, message?: string): void {
    this.results.push({
      assertion,
      passed,
      expected,
      actual,
      message
    });
  }
  
  /**
   * Get results
   */
  getResults(): AssertionResult[] {
    return [...this.results];
  }
  
  /**
   * All passed
   */
  allPassed(): boolean {
    return this.results.every(r => r.passed);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: TEST RUNNER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Test runner configuration
 */
export interface TestRunnerConfig {
  parallel: boolean;
  maxParallel: number;
  defaultTimeout: number;
  stopOnFirstFailure: boolean;
  verbose: boolean;
}

/**
 * Test run result
 */
export interface TestRunResult {
  total: number;
  passed: number;
  failed: number;
  skipped: number;
  duration: number;
  results: TestResult[];
  summary: string;
}

/**
 * Test runner
 */
export class TestRunner {
  private config: TestRunnerConfig;
  private suites: TestSuite[] = [];
  
  constructor(config?: Partial<TestRunnerConfig>) {
    this.config = {
      parallel: config?.parallel ?? false,
      maxParallel: config?.maxParallel ?? 4,
      defaultTimeout: config?.defaultTimeout ?? 30000,
      stopOnFirstFailure: config?.stopOnFirstFailure ?? false,
      verbose: config?.verbose ?? true
    };
  }
  
  /**
   * Add test suite
   */
  addSuite(suite: TestSuite): void {
    this.suites.push(suite);
  }
  
  /**
   * Run all tests
   */
  async runAll(): Promise<TestRunResult> {
    const startTime = Date.now();
    const results: TestResult[] = [];
    
    for (const suite of this.suites) {
      // Run setup
      if (suite.setup) {
        await suite.setup();
      }
      
      // Run tests
      for (const test of suite.tests) {
        const result = await this.runTest(test);
        results.push(result);
        
        if (this.config.stopOnFirstFailure && result.status === TestStatus.Failed) {
          break;
        }
      }
      
      // Run teardown
      if (suite.teardown) {
        await suite.teardown();
      }
      
      if (this.config.stopOnFirstFailure && results.some(r => r.status === TestStatus.Failed)) {
        break;
      }
    }
    
    const duration = Date.now() - startTime;
    const passed = results.filter(r => r.status === TestStatus.Passed).length;
    const failed = results.filter(r => r.status === TestStatus.Failed).length;
    const skipped = results.filter(r => r.status === TestStatus.Skipped).length;
    
    return {
      total: results.length,
      passed,
      failed,
      skipped,
      duration,
      results,
      summary: this.generateSummary(results, duration)
    };
  }
  
  /**
   * Run single test
   */
  private async runTest(test: TestCase): Promise<TestResult> {
    const timeout = test.timeout ?? this.config.defaultTimeout;
    const startTime = Date.now();
    
    try {
      // Run with timeout
      const result = await Promise.race([
        test.run(),
        new Promise<TestResult>((_, reject) => 
          setTimeout(() => reject(new Error("Timeout")), timeout)
        )
      ]);
      
      result.duration = Date.now() - startTime;
      return result;
      
    } catch (e) {
      return {
        testId: test.id,
        status: TestStatus.Failed,
        duration: Date.now() - startTime,
        assertions: [],
        error: e instanceof Error ? e.message : "Unknown error"
      };
    }
  }
  
  /**
   * Generate summary
   */
  private generateSummary(results: TestResult[], duration: number): string {
    const passed = results.filter(r => r.status === TestStatus.Passed).length;
    const failed = results.filter(r => r.status === TestStatus.Failed).length;
    const skipped = results.filter(r => r.status === TestStatus.Skipped).length;
    
    const lines: string[] = [
      "═══════════════════════════════════════════════════════════════════════",
      "                         TEST RESULTS SUMMARY                          ",
      "═══════════════════════════════════════════════════════════════════════",
      "",
      `  Total:    ${results.length}`,
      `  Passed:   ${passed} (${((passed / results.length) * 100).toFixed(1)}%)`,
      `  Failed:   ${failed}`,
      `  Skipped:  ${skipped}`,
      `  Duration: ${duration}ms`,
      ""
    ];
    
    if (failed > 0) {
      lines.push("FAILED TESTS:");
      for (const result of results.filter(r => r.status === TestStatus.Failed)) {
        lines.push(`  ✗ ${result.testId}: ${result.error ?? "Assertion failed"}`);
      }
      lines.push("");
    }
    
    lines.push("═══════════════════════════════════════════════════════════════════════");
    
    return lines.join("\n");
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: CORE VALIDATION TESTS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Truth discipline tests
 */
export function createTruthDisciplineTests(): TestSuite {
  return {
    name: "TruthDiscipline",
    category: TestCategory.Unit,
    tests: [
      {
        id: "truth_lattice_meet",
        name: "Truth Lattice Meet Operation",
        category: TestCategory.Unit,
        subsystem: "truth_discipline",
        description: "Verify meet (greatest lower bound) operation",
        run: async () => {
          const ctx = new AssertionContext();
          
          // Define truth values
          const OK = "OK", NEAR = "NEAR", AMBIG = "AMBIG", FAIL = "FAIL";
          const order: Record<string, number> = { FAIL: 0, AMBIG: 1, NEAR: 2, OK: 3 };
          
          const meet = (a: string, b: string): string => {
            return order[a] <= order[b] ? a : b;
          };
          
          // Test cases
          ctx.assertEquals(meet(OK, OK), OK, "OK ∧ OK = OK");
          ctx.assertEquals(meet(OK, NEAR), NEAR, "OK ∧ NEAR = NEAR");
          ctx.assertEquals(meet(OK, AMBIG), AMBIG, "OK ∧ AMBIG = AMBIG");
          ctx.assertEquals(meet(OK, FAIL), FAIL, "OK ∧ FAIL = FAIL");
          ctx.assertEquals(meet(NEAR, AMBIG), AMBIG, "NEAR ∧ AMBIG = AMBIG");
          ctx.assertEquals(meet(FAIL, FAIL), FAIL, "FAIL ∧ FAIL = FAIL");
          
          return {
            testId: "truth_lattice_meet",
            status: ctx.allPassed() ? TestStatus.Passed : TestStatus.Failed,
            duration: 0,
            assertions: ctx.getResults()
          };
        }
      },
      {
        id: "truth_valid_transitions",
        name: "Truth Valid Transitions",
        category: TestCategory.Unit,
        subsystem: "truth_discipline",
        description: "Verify only valid truth transitions are allowed",
        run: async () => {
          const ctx = new AssertionContext();
          
          const validTransitions: Record<string, string[]> = {
            AMBIG: ["NEAR", "FAIL"],
            NEAR: ["OK", "FAIL"],
            OK: ["FAIL"],
            FAIL: []
          };
          
          const isValid = (from: string, to: string): boolean => {
            return validTransitions[from]?.includes(to) ?? false;
          };
          
          // Valid transitions
          ctx.assertTrue(isValid("AMBIG", "NEAR"), "AMBIG → NEAR is valid");
          ctx.assertTrue(isValid("AMBIG", "FAIL"), "AMBIG → FAIL is valid");
          ctx.assertTrue(isValid("NEAR", "OK"), "NEAR → OK is valid");
          ctx.assertTrue(isValid("NEAR", "FAIL"), "NEAR → FAIL is valid");
          ctx.assertTrue(isValid("OK", "FAIL"), "OK → FAIL is valid");
          
          // Invalid transitions
          ctx.assertFalse(isValid("OK", "NEAR"), "OK → NEAR is invalid");
          ctx.assertFalse(isValid("OK", "AMBIG"), "OK → AMBIG is invalid");
          ctx.assertFalse(isValid("NEAR", "AMBIG"), "NEAR → AMBIG is invalid");
          ctx.assertFalse(isValid("FAIL", "OK"), "FAIL → OK is invalid");
          
          return {
            testId: "truth_valid_transitions",
            status: ctx.allPassed() ? TestStatus.Passed : TestStatus.Failed,
            duration: 0,
            assertions: ctx.getResults()
          };
        }
      },
      {
        id: "abstain_over_guess",
        name: "ABSTAIN > GUESS Principle",
        category: TestCategory.Property,
        subsystem: "truth_discipline",
        description: "Verify ABSTAIN > GUESS is enforced",
        run: async () => {
          const ctx = new AssertionContext();
          
          const decideTruth = (confidence: number): string => {
            if (confidence >= 0.95) return "OK";
            if (confidence >= 0.75) return "NEAR";
            if (confidence >= 0.5) return "AMBIG";
            return "FAIL"; // Abstain
          };
          
          // High confidence → OK
          ctx.assertEquals(decideTruth(0.99), "OK", "99% confidence → OK");
          ctx.assertEquals(decideTruth(0.95), "OK", "95% confidence → OK");
          
          // Medium confidence → NEAR
          ctx.assertEquals(decideTruth(0.85), "NEAR", "85% confidence → NEAR");
          ctx.assertEquals(decideTruth(0.75), "NEAR", "75% confidence → NEAR");
          
          // Low confidence → AMBIG (don't guess)
          ctx.assertEquals(decideTruth(0.60), "AMBIG", "60% confidence → AMBIG");
          ctx.assertEquals(decideTruth(0.50), "AMBIG", "50% confidence → AMBIG");
          
          // Very low → FAIL (abstain)
          ctx.assertEquals(decideTruth(0.40), "FAIL", "40% confidence → FAIL (abstain)");
          ctx.assertEquals(decideTruth(0.10), "FAIL", "10% confidence → FAIL (abstain)");
          
          return {
            testId: "abstain_over_guess",
            status: ctx.allPassed() ? TestStatus.Passed : TestStatus.Failed,
            duration: 0,
            assertions: ctx.getResults()
          };
        }
      }
    ]
  };
}

/**
 * Routing tests
 */
export function createRoutingTests(): TestSuite {
  return {
    name: "Routing",
    category: TestCategory.Unit,
    tests: [
      {
        id: "hub_set_max_six",
        name: "Hub Set Maximum Six",
        category: TestCategory.Property,
        subsystem: "routing",
        description: "Verify HubSet ≤ 6 constraint",
        run: async () => {
          const ctx = new AssertionContext();
          
          const MANDATORY_SIGNATURE = ["AppA", "AppI", "AppM"];
          const MAX_HUB_SET = 6;
          
          const computeHubSet = (lensBase: string, facetBase: string, arcHub: string, overlay?: string): string[] => {
            const hubs = new Set<string>(MANDATORY_SIGNATURE);
            hubs.add(lensBase);
            hubs.add(facetBase);
            hubs.add(arcHub);
            if (overlay) hubs.add(overlay);
            
            const hubArray = Array.from(hubs);
            if (hubArray.length > MAX_HUB_SET) {
              // Prioritize and trim
              return hubArray.slice(0, MAX_HUB_SET);
            }
            return hubArray;
          };
          
          // Test various combinations
          const hub1 = computeHubSet("AppC", "AppB", "AppE");
          ctx.assertTrue(hub1.length <= MAX_HUB_SET, "Basic hub set ≤ 6");
          
          const hub2 = computeHubSet("AppC", "AppB", "AppE", "AppJ");
          ctx.assertTrue(hub2.length <= MAX_HUB_SET, "Hub set with overlay ≤ 6");
          
          const hub3 = computeHubSet("AppE", "AppH", "AppN", "AppL");
          ctx.assertTrue(hub3.length <= MAX_HUB_SET, "Complex hub set ≤ 6");
          
          // Verify mandatory signature always present
          ctx.assertTrue(hub1.includes("AppA"), "AppA always present");
          ctx.assertTrue(hub1.includes("AppI"), "AppI always present");
          ctx.assertTrue(hub1.includes("AppM"), "AppM always present");
          
          return {
            testId: "hub_set_max_six",
            status: ctx.allPassed() ? TestStatus.Passed : TestStatus.Failed,
            duration: 0,
            assertions: ctx.getResults()
          };
        }
      },
      {
        id: "arc_hub_mapping",
        name: "Arc Hub Mapping",
        category: TestCategory.Unit,
        subsystem: "routing",
        description: "Verify arc to hub mapping",
        run: async () => {
          const ctx = new AssertionContext();
          
          const ARC_HUB_MAP: Record<number, string> = {
            0: "AppA",
            1: "AppC",
            2: "AppE",
            3: "AppF",
            4: "AppG",
            5: "AppN",
            6: "AppP"
          };
          
          const getArcHub = (chapter: number): string => {
            const omega = chapter - 1;
            const alpha = Math.floor(omega / 3);
            return ARC_HUB_MAP[alpha] ?? "AppA";
          };
          
          // Test arc assignments
          ctx.assertEquals(getArcHub(1), "AppA", "Ch01 → Arc 0 → AppA");
          ctx.assertEquals(getArcHub(2), "AppA", "Ch02 → Arc 0 → AppA");
          ctx.assertEquals(getArcHub(3), "AppA", "Ch03 → Arc 0 → AppA");
          ctx.assertEquals(getArcHub(4), "AppC", "Ch04 → Arc 1 → AppC");
          ctx.assertEquals(getArcHub(7), "AppE", "Ch07 → Arc 2 → AppE");
          ctx.assertEquals(getArcHub(10), "AppF", "Ch10 → Arc 3 → AppF");
          ctx.assertEquals(getArcHub(13), "AppG", "Ch13 → Arc 4 → AppG");
          ctx.assertEquals(getArcHub(16), "AppN", "Ch16 → Arc 5 → AppN");
          ctx.assertEquals(getArcHub(19), "AppP", "Ch19 → Arc 6 → AppP");
          
          return {
            testId: "arc_hub_mapping",
            status: ctx.allPassed() ? TestStatus.Passed : TestStatus.Failed,
            duration: 0,
            assertions: ctx.getResults()
          };
        }
      }
    ]
  };
}

/**
 * Conservation tests
 */
export function createConservationTests(): TestSuite {
  return {
    name: "Conservation",
    category: TestCategory.Property,
    tests: [
      {
        id: "kappa_conservation",
        name: "κ-Conservation Invariant",
        category: TestCategory.Property,
        subsystem: "resource_management",
        description: "Verify κ_pre = κ_post + κ_spent + κ_leak",
        run: async () => {
          const ctx = new AssertionContext();
          
          // Simulate resource management
          let kappa_pre = 1.0;
          let kappa_post = 1.0;
          let kappa_spent = 0;
          let kappa_leak = 0;
          
          const spend = (amount: number): boolean => {
            if (kappa_post < amount) return false;
            kappa_post -= amount;
            kappa_spent += amount;
            return true;
          };
          
          const recordLeak = (amount: number): void => {
            kappa_post -= amount;
            kappa_leak += amount;
          };
          
          const verifyConservation = (): boolean => {
            const expected = kappa_pre;
            const actual = kappa_post + kappa_spent + kappa_leak;
            return Math.abs(expected - actual) < 0.0001;
          };
          
          // Initial state
          ctx.assertTrue(verifyConservation(), "Initial conservation");
          
          // After spending
          spend(0.3);
          ctx.assertTrue(verifyConservation(), "Conservation after spend");
          ctx.assertEquals(kappa_spent, 0.3, "Spent amount correct");
          
          // After more spending
          spend(0.2);
          ctx.assertTrue(verifyConservation(), "Conservation after more spend");
          ctx.assertEquals(kappa_spent, 0.5, "Total spent correct");
          
          // After leak
          recordLeak(0.01);
          ctx.assertTrue(verifyConservation(), "Conservation after leak");
          
          // Final state
          ctx.assertInRange(kappa_post, 0, 1, "Final kappa in valid range");
          ctx.assertTrue(kappa_post + kappa_spent + kappa_leak === kappa_pre, "Final conservation");
          
          return {
            testId: "kappa_conservation",
            status: ctx.allPassed() ? TestStatus.Passed : TestStatus.Failed,
            duration: 0,
            assertions: ctx.getResults()
          };
        }
      }
    ]
  };
}

/**
 * Addressing tests
 */
export function createAddressingTests(): TestSuite {
  return {
    name: "Addressing",
    category: TestCategory.Unit,
    tests: [
      {
        id: "address_normalization",
        name: "Address Normalization",
        category: TestCategory.Unit,
        subsystem: "addressing",
        description: "Verify address normalization is idempotent and unique",
        run: async () => {
          const ctx = new AssertionContext();
          
          const normalizeAddr = (addr: string): string => {
            // Parse components
            const match = addr.match(/Ch(\d+).*\.([SFCR])(\d)\.(a|b|c|d)/);
            if (!match) return addr;
            
            const chapter = parseInt(match[1]);
            const lens = match[2];
            const facet = match[3];
            const atom = match[4];
            
            const code = (chapter - 1).toString(4).padStart(4, '0');
            return `Ch${chapter.toString().padStart(2, '0')}⟨${code}⟩.${lens}${facet}.${atom}`;
          };
          
          // Test idempotence
          const addr1 = "Ch08⟨0013⟩.F2.c";
          const norm1 = normalizeAddr(addr1);
          const norm1again = normalizeAddr(norm1);
          ctx.assertEquals(norm1, norm1again, "Normalization is idempotent");
          
          // Test canonical format
          const addr2 = "Ch1.S1.a";
          const norm2 = normalizeAddr(addr2);
          ctx.assertEquals(norm2, "Ch01⟨0000⟩.S1.a", "Canonical format correct");
          
          // Test uniqueness
          const addr3a = "Ch08.F2.c";
          const addr3b = "Ch8⟨0013⟩.F2.c";
          const norm3a = normalizeAddr(addr3a);
          const norm3b = normalizeAddr(addr3b);
          ctx.assertEquals(norm3a, norm3b, "Same semantic address normalizes to same");
          
          return {
            testId: "address_normalization",
            status: ctx.allPassed() ? TestStatus.Passed : TestStatus.Failed,
            duration: 0,
            assertions: ctx.getResults()
          };
        }
      },
      {
        id: "base4_encoding",
        name: "Base-4 Station Encoding",
        category: TestCategory.Unit,
        subsystem: "addressing",
        description: "Verify base-4 station code encoding",
        run: async () => {
          const ctx = new AssertionContext();
          
          const encodeStation = (chapter: number): string => {
            return (chapter - 1).toString(4).padStart(4, '0');
          };
          
          const decodeStation = (code: string): number => {
            return parseInt(code, 4) + 1;
          };
          
          // Test encoding
          ctx.assertEquals(encodeStation(1), "0000", "Ch01 → 0000");
          ctx.assertEquals(encodeStation(2), "0001", "Ch02 → 0001");
          ctx.assertEquals(encodeStation(5), "0010", "Ch05 → 0010");
          ctx.assertEquals(encodeStation(9), "0020", "Ch09 → 0020");
          ctx.assertEquals(encodeStation(17), "0100", "Ch17 → 0100");
          ctx.assertEquals(encodeStation(21), "0110", "Ch21 → 0110");
          
          // Test round-trip
          for (let ch = 1; ch <= 21; ch++) {
            const encoded = encodeStation(ch);
            const decoded = decodeStation(encoded);
            ctx.assertEquals(decoded, ch, `Round-trip Ch${ch}`);
          }
          
          return {
            testId: "base4_encoding",
            status: ctx.allPassed() ? TestStatus.Passed : TestStatus.Failed,
            duration: 0,
            assertions: ctx.getResults()
          };
        }
      }
    ]
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: INTEGRATION TEST BUILDER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Build complete test suite
 */
export function buildCompleteSuite(): TestRunner {
  const runner = new TestRunner({ verbose: true });
  
  runner.addSuite(createTruthDisciplineTests());
  runner.addSuite(createRoutingTests());
  runner.addSuite(createConservationTests());
  runner.addSuite(createAddressingTests());
  
  return runner;
}

/**
 * Run all validation tests
 */
export async function runAllValidation(): Promise<TestRunResult> {
  const runner = buildCompleteSuite();
  return runner.runAll();
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: PROPERTY GENERATORS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Random generators for property testing
 */
export const Generators = {
  truthValue: (): string => {
    const values = ["OK", "NEAR", "AMBIG", "FAIL"];
    return values[Math.floor(Math.random() * values.length)];
  },
  
  chapter: (): number => {
    return Math.floor(Math.random() * 21) + 1;
  },
  
  lens: (): string => {
    const lenses = ["S", "F", "C", "R"];
    return lenses[Math.floor(Math.random() * lenses.length)];
  },
  
  facet: (): number => {
    return Math.floor(Math.random() * 4) + 1;
  },
  
  atom: (): string => {
    const atoms = ["a", "b", "c", "d"];
    return atoms[Math.floor(Math.random() * atoms.length)];
  },
  
  kappa: (): number => {
    return Math.random();
  },
  
  address: (): string => {
    const ch = Generators.chapter();
    const l = Generators.lens();
    const f = Generators.facet();
    const a = Generators.atom();
    const code = (ch - 1).toString(4).padStart(4, '0');
    return `Ch${ch.toString().padStart(2, '0')}⟨${code}⟩.${l}${f}.${a}`;
  }
};

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Enums
  TestStatus,
  TestCategory,
  
  // Classes
  AssertionContext,
  TestRunner,
  
  // Test Suites
  createTruthDisciplineTests,
  createRoutingTests,
  createConservationTests,
  createAddressingTests,
  
  // Functions
  buildCompleteSuite,
  runAllValidation,
  
  // Generators
  Generators
};
