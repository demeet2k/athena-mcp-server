/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * CAPABILITY CORRIDOR ENGINE - Sandbox Planes & Least Privilege
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * From SELF_SUFFICIENCY_TOME Ch06:
 * 
 * Core Laws:
 *   - Law 6.1 (Default-deny): If no rule path yields Allow with satisfied guards
 *     and budgets, the decision is Deny
 *   - Law 6.2 (Least privilege): Any derived capability must satisfy scope
 *     attenuation with no privilege amplification
 *   - Law 6.3 (Guard non-bypassability): All actions must pass through a single
 *     decision point protected by verifier-checked guard predicates
 *   - Law 6.4 (Deny precedence): If both allow and deny rules match, deny wins
 *     unless explicit owner-signed exception
 * 
 * Objects: Principals, Owners, Scopes, Capabilities, Manifests, Rules,
 *          Trust Zones, Boundary Families
 * 
 * @module CAPABILITY_CORRIDOR_ENGINE
 * @version 2.0.0
 */

import { TruthValue, WitnessPtr } from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: PRINCIPAL AND OWNER TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Principal: Identity token bound to verifier-recognized public key
 */
export interface Principal {
  id: string;
  publicKey: string;
  policyNamespace: string;
  created: number;
  attestations: Attestation[];
}

/**
 * Attestation: Signed statement about a principal
 */
export interface Attestation {
  claim: string;
  issuer: string;
  signature: string;
  notBefore: number;
  expiry: number;
  hash: string;
}

/**
 * Owner: Principal designated as authority for a capability domain
 */
export interface Owner {
  principal: Principal;
  domain: string;
  ownershipStatement: string;
  signature: string;
  verifiable: boolean;
}

/**
 * Create ownership statement
 */
export function createOwnershipStatement(principal: Principal, domain: string): Owner {
  const statement = `Own(${principal.id}, ${domain})`;
  return {
    principal,
    domain,
    ownershipStatement: statement,
    signature: computeSignature(statement, principal.publicKey),
    verifiable: true
  };
}

function computeSignature(data: string, key: string): string {
  // Simulated signature - in production would use crypto
  return hashString(`sig:${data}:${key}`);
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
// SECTION 2: SCOPE AND CAPABILITY TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Permission types
 */
export enum Permission {
  Read = "read",
  Write = "write",
  Execute = "exec",
  Connect = "connect",
  Bind = "bind",
  Derive = "derive",
  Delegate = "delegate",
  Attest = "attest"
}

/**
 * Domain types
 */
export enum DomainType {
  Filesystem = "filesystem",
  Network = "network",
  Device = "device",
  Kernel = "kernel",
  Registry = "registry",
  Memory = "memory",
  Compute = "compute"
}

/**
 * Resource limit
 */
export interface ResourceLimit {
  rate: number;        // calls per second
  time: number;        // max time in ms
  bytes: number;       // max bytes
  calls: number;       // max calls
  memory: number;      // max memory bytes
  cpu: number;         // max CPU units
  depth: number;       // max recursion depth
}

/**
 * Scope: Triple ⟨D, perm, limit⟩
 */
export interface Scope {
  domain: DomainSpec;
  permissions: Set<Permission>;
  limits: ResourceLimit;
}

/**
 * Domain specification
 */
export interface DomainSpec {
  type: DomainType;
  path: string;        // e.g., "/data/user/*" for filesystem
  constraints: string[];
}

/**
 * Check if scope s1 is attenuation of s2
 * s1 ⪯ s2 iff D1 ⊆ D2, perm1 ⊆ perm2, limit1 ⪯ limit2
 */
export function isAttenuation(s1: Scope, s2: Scope): boolean {
  // Domain containment
  if (!isDomainContained(s1.domain, s2.domain)) return false;
  
  // Permission subset
  for (const perm of s1.permissions) {
    if (!s2.permissions.has(perm)) return false;
  }
  
  // Limit comparison (componentwise ≤)
  if (s1.limits.rate > s2.limits.rate) return false;
  if (s1.limits.time > s2.limits.time) return false;
  if (s1.limits.bytes > s2.limits.bytes) return false;
  if (s1.limits.calls > s2.limits.calls) return false;
  if (s1.limits.memory > s2.limits.memory) return false;
  if (s1.limits.cpu > s2.limits.cpu) return false;
  if (s1.limits.depth > s2.limits.depth) return false;
  
  return true;
}

function isDomainContained(d1: DomainSpec, d2: DomainSpec): boolean {
  if (d1.type !== d2.type) return false;
  
  // Path containment (simple glob matching)
  if (d2.path === "*") return true;
  if (d1.path === d2.path) return true;
  if (d2.path.endsWith("*")) {
    const prefix = d2.path.slice(0, -1);
    return d1.path.startsWith(prefix);
  }
  
  return false;
}

/**
 * Delegation mode
 */
export enum DelegationMode {
  None = "none",
  Attenuate = "attenuate",
  Full = "full"
}

/**
 * Capability: Signed, non-forgeable token
 * κ = ⟨id, p, s, nbf, exp, nonce, delegation, σ⟩
 */
export interface Capability {
  id: string;
  principal: string;       // Principal ID
  scope: Scope;
  notBefore: number;       // nbf
  expiry: number;          // exp
  nonce: string;
  delegation: DelegationSpec;
  signature: string;       // σ
  parentId?: string;       // For derived capabilities
}

export interface DelegationSpec {
  mode: DelegationMode;
  maxDepth: number;
  restrictions: string[];
}

/**
 * Create a new capability
 */
export function createCapability(
  principal: Principal,
  scope: Scope,
  owner: Owner,
  options?: {
    validityPeriod?: number;
    delegation?: DelegationSpec;
  }
): Capability {
  const now = Date.now();
  const validityPeriod = options?.validityPeriod ?? 3600000; // 1 hour default
  
  const cap: Capability = {
    id: `cap_${now}_${Math.random().toString(36).slice(2, 8)}`,
    principal: principal.id,
    scope,
    notBefore: now,
    expiry: now + validityPeriod,
    nonce: Math.random().toString(36).slice(2, 10),
    delegation: options?.delegation ?? { mode: DelegationMode.None, maxDepth: 0, restrictions: [] },
    signature: ""
  };
  
  // Sign with owner's key
  const dataToSign = JSON.stringify({
    id: cap.id,
    principal: cap.principal,
    scope: serializeScope(cap.scope),
    notBefore: cap.notBefore,
    expiry: cap.expiry,
    nonce: cap.nonce,
    delegation: cap.delegation
  });
  
  cap.signature = computeSignature(dataToSign, owner.principal.publicKey);
  
  return cap;
}

function serializeScope(scope: Scope): string {
  return JSON.stringify({
    domain: scope.domain,
    permissions: Array.from(scope.permissions),
    limits: scope.limits
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: RULES AND MANIFEST
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Action record
 */
export interface ActionRecord {
  actor: string;
  resource: string;
  operation: string;
  params: Record<string, unknown>;
  time: number;
}

/**
 * Rule outcome
 */
export enum RuleOutcome {
  Allow = "Allow",
  Deny = "Deny"
}

/**
 * Rule: Predicate over action record
 */
export interface Rule {
  id: string;
  name: string;
  predicate: (action: ActionRecord, context: RuleContext) => boolean;
  outcome: RuleOutcome;
  priority: number;
  conditions: string[];
  justification: string;
}

export interface RuleContext {
  corridorState: Record<string, unknown>;
  budgets: ResourceLimit;
  time: number;
}

/**
 * Capability Manifest
 * M = ⟨version, principal, scopes, denies, allows, guards, budgets, hash⟩
 */
export interface CapabilityManifest {
  version: string;
  principal: string;
  scopes: Scope[];
  denies: Rule[];
  allows: Rule[];
  guards: Guard[];
  budgets: ResourceLimit;
  hash: string;
  created: number;
  signature: string;
}

/**
 * Guard: Non-bypassable predicate
 */
export interface Guard {
  id: string;
  name: string;
  predicate: (action: ActionRecord, context: RuleContext) => GuardResult;
  required: boolean;
  bypassable: false;  // Always false - guards cannot be bypassed
}

export interface GuardResult {
  satisfied: boolean;
  reason: string;
  evidence?: unknown;
}

/**
 * Decision output type
 */
export type DecisionOutput = 
  | { type: "Bulk"; outcome: RuleOutcome }
  | { type: "Boundary"; kind: BoundaryKind; obligations: string[] };

export enum BoundaryKind {
  UnderresolvedIdentity = "UnderresolvedIdentity",
  AmbiguousRuleConflict = "AmbiguousRuleConflict",
  ExpiredSignature = "ExpiredSignature",
  InsufficientAttestation = "InsufficientAttestation",
  OutOfCorridor = "OutOfCorridor"
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: MANIFEST COMPILER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Decision DAG node
 */
export interface DecisionNode {
  id: string;
  type: "predicate" | "guard" | "leaf";
  predicate?: (action: ActionRecord, ctx: RuleContext) => boolean;
  guard?: Guard;
  outcome?: RuleOutcome;
  trueChild?: string;
  falseChild?: string;
  justification?: string;
}

/**
 * Compiled manifest
 */
export interface CompiledManifest {
  source: CapabilityManifest;
  decisionDAG: Map<string, DecisionNode>;
  rootNode: string;
  conflictTable: ConflictEntry[];
  guardChecklist: string[];
  merkleRoot: string;
}

export interface ConflictEntry {
  rule1: string;
  rule2: string;
  conflictType: "overlap" | "contradiction";
  resolution: "deny_precedence" | "explicit_exception" | "unresolved";
}

/**
 * Manifest compiler
 */
export class ManifestCompiler {
  /**
   * Compile manifest to decision DAG
   */
  compile(manifest: CapabilityManifest): CompiledManifest {
    const dag = new Map<string, DecisionNode>();
    const guardChecklist: string[] = [];
    const conflicts: ConflictEntry[] = [];
    
    // Step 1: Add guard nodes
    let currentId = "guard_0";
    let previousId: string | undefined;
    
    for (let i = 0; i < manifest.guards.length; i++) {
      const guard = manifest.guards[i];
      const nodeId = `guard_${i}`;
      guardChecklist.push(nodeId);
      
      dag.set(nodeId, {
        id: nodeId,
        type: "guard",
        guard,
        trueChild: `guard_${i + 1}`,
        falseChild: "deny_guard_fail"
      });
      
      previousId = nodeId;
    }
    
    // Guard failure leaf
    dag.set("deny_guard_fail", {
      id: "deny_guard_fail",
      type: "leaf",
      outcome: RuleOutcome.Deny,
      justification: "Guard check failed"
    });
    
    // Step 2: Add rule nodes
    const ruleStart = `rule_start`;
    if (previousId) {
      const lastGuard = dag.get(previousId);
      if (lastGuard) {
        lastGuard.trueChild = ruleStart;
      }
    }
    
    // Sort rules by priority (higher priority first)
    const sortedDenies = [...manifest.denies].sort((a, b) => b.priority - a.priority);
    const sortedAllows = [...manifest.allows].sort((a, b) => b.priority - a.priority);
    
    // Deny rules first (deny precedence)
    let ruleIndex = 0;
    for (const rule of sortedDenies) {
      const nodeId = `deny_rule_${ruleIndex}`;
      dag.set(nodeId, {
        id: nodeId,
        type: "predicate",
        predicate: rule.predicate,
        trueChild: `deny_${rule.id}`,
        falseChild: `deny_rule_${ruleIndex + 1}`,
        justification: rule.justification
      });
      
      dag.set(`deny_${rule.id}`, {
        id: `deny_${rule.id}`,
        type: "leaf",
        outcome: RuleOutcome.Deny,
        justification: rule.justification
      });
      
      ruleIndex++;
    }
    
    // Connect to allow rules
    if (ruleIndex > 0) {
      const lastDeny = dag.get(`deny_rule_${ruleIndex - 1}`);
      if (lastDeny) {
        lastDeny.falseChild = "allow_rule_0";
      }
    }
    
    // Allow rules
    let allowIndex = 0;
    for (const rule of sortedAllows) {
      const nodeId = `allow_rule_${allowIndex}`;
      dag.set(nodeId, {
        id: nodeId,
        type: "predicate",
        predicate: rule.predicate,
        trueChild: `allow_${rule.id}`,
        falseChild: `allow_rule_${allowIndex + 1}`,
        justification: rule.justification
      });
      
      dag.set(`allow_${rule.id}`, {
        id: `allow_${rule.id}`,
        type: "leaf",
        outcome: RuleOutcome.Allow,
        justification: rule.justification
      });
      
      allowIndex++;
    }
    
    // Default deny (Law 6.1)
    const lastAllow = dag.get(`allow_rule_${allowIndex - 1}`);
    if (lastAllow) {
      lastAllow.falseChild = "default_deny";
    }
    
    dag.set("default_deny", {
      id: "default_deny",
      type: "leaf",
      outcome: RuleOutcome.Deny,
      justification: "Default deny - no matching allow rule"
    });
    
    // Set root
    const rootNode = manifest.guards.length > 0 ? "guard_0" : 
                     sortedDenies.length > 0 ? "deny_rule_0" : 
                     sortedAllows.length > 0 ? "allow_rule_0" : "default_deny";
    
    // Detect conflicts
    for (const deny of manifest.denies) {
      for (const allow of manifest.allows) {
        // Simple conflict detection - in practice would be more sophisticated
        if (deny.conditions.some(c => allow.conditions.includes(c))) {
          conflicts.push({
            rule1: deny.id,
            rule2: allow.id,
            conflictType: "overlap",
            resolution: "deny_precedence"
          });
        }
      }
    }
    
    // Compute Merkle root
    const merkleRoot = this.computeMerkleRoot(manifest);
    
    return {
      source: manifest,
      decisionDAG: dag,
      rootNode,
      conflictTable: conflicts,
      guardChecklist,
      merkleRoot
    };
  }
  
  private computeMerkleRoot(manifest: CapabilityManifest): string {
    const leaves = [
      hashString(manifest.version),
      hashString(manifest.principal),
      hashString(JSON.stringify(manifest.scopes.map(serializeScope))),
      hashString(JSON.stringify(manifest.denies.map(r => r.id))),
      hashString(JSON.stringify(manifest.allows.map(r => r.id))),
      hashString(JSON.stringify(manifest.guards.map(g => g.id))),
      hashString(JSON.stringify(manifest.budgets))
    ];
    
    // Simple Merkle computation
    while (leaves.length > 1) {
      const newLeaves: string[] = [];
      for (let i = 0; i < leaves.length; i += 2) {
        if (i + 1 < leaves.length) {
          newLeaves.push(hashString(leaves[i] + leaves[i + 1]));
        } else {
          newLeaves.push(leaves[i]);
        }
      }
      leaves.length = 0;
      leaves.push(...newLeaves);
    }
    
    return leaves[0];
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: CAPABILITY CHECKER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Check result
 */
export interface CheckResult {
  outcome: DecisionOutput;
  matchedRules: string[];
  guardResults: Map<string, GuardResult>;
  budgetStatus: BudgetStatus;
  trace: CheckTrace;
}

export interface BudgetStatus {
  withinLimits: boolean;
  usage: ResourceLimit;
  remaining: ResourceLimit;
}

export interface CheckTrace {
  steps: CheckStep[];
  pathTaken: string[];
  timestamp: number;
  hash: string;
}

export interface CheckStep {
  nodeId: string;
  nodeType: string;
  result: boolean;
  reason: string;
}

/**
 * Budget ledger
 */
export class BudgetLedger {
  private usage: Map<string, ResourceLimit> = new Map();
  
  /**
   * Record usage
   */
  record(capabilityId: string, usage: Partial<ResourceLimit>): void {
    const current = this.usage.get(capabilityId) ?? this.emptyLimit();
    
    this.usage.set(capabilityId, {
      rate: current.rate + (usage.rate ?? 0),
      time: current.time + (usage.time ?? 0),
      bytes: current.bytes + (usage.bytes ?? 0),
      calls: current.calls + (usage.calls ?? 1),
      memory: current.memory + (usage.memory ?? 0),
      cpu: current.cpu + (usage.cpu ?? 0),
      depth: Math.max(current.depth, usage.depth ?? 0)
    });
  }
  
  /**
   * Check if within limits
   */
  checkLimits(capabilityId: string, limits: ResourceLimit): BudgetStatus {
    const current = this.usage.get(capabilityId) ?? this.emptyLimit();
    
    const remaining: ResourceLimit = {
      rate: limits.rate - current.rate,
      time: limits.time - current.time,
      bytes: limits.bytes - current.bytes,
      calls: limits.calls - current.calls,
      memory: limits.memory - current.memory,
      cpu: limits.cpu - current.cpu,
      depth: limits.depth - current.depth
    };
    
    const withinLimits = 
      remaining.rate >= 0 &&
      remaining.time >= 0 &&
      remaining.bytes >= 0 &&
      remaining.calls >= 0 &&
      remaining.memory >= 0 &&
      remaining.cpu >= 0 &&
      remaining.depth >= 0;
    
    return { withinLimits, usage: current, remaining };
  }
  
  private emptyLimit(): ResourceLimit {
    return { rate: 0, time: 0, bytes: 0, calls: 0, memory: 0, cpu: 0, depth: 0 };
  }
}

/**
 * Capability checker
 */
export class CapabilityChecker {
  private ledger: BudgetLedger;
  private principals: Map<string, Principal> = new Map();
  private owners: Map<string, Owner> = new Map();
  
  constructor() {
    this.ledger = new BudgetLedger();
  }
  
  /**
   * Register principal
   */
  registerPrincipal(principal: Principal): void {
    this.principals.set(principal.id, principal);
  }
  
  /**
   * Register owner
   */
  registerOwner(owner: Owner): void {
    this.owners.set(owner.domain, owner);
  }
  
  /**
   * Check capability against action
   */
  check(
    capability: Capability,
    action: ActionRecord,
    manifest: CompiledManifest
  ): CheckResult {
    const trace: CheckTrace = {
      steps: [],
      pathTaken: [],
      timestamp: Date.now(),
      hash: ""
    };
    const guardResults = new Map<string, GuardResult>();
    const matchedRules: string[] = [];
    
    // Step 1: Verify signature and validity window
    const now = Date.now();
    if (now < capability.notBefore || now > capability.expiry) {
      return {
        outcome: { type: "Boundary", kind: BoundaryKind.ExpiredSignature, obligations: ["Renew capability"] },
        matchedRules: [],
        guardResults,
        budgetStatus: this.ledger.checkLimits(capability.id, capability.scope.limits),
        trace
      };
    }
    
    // Step 2: Verify principal binding
    const principal = this.principals.get(capability.principal);
    if (!principal) {
      return {
        outcome: { type: "Boundary", kind: BoundaryKind.UnderresolvedIdentity, obligations: ["Register principal"] },
        matchedRules: [],
        guardResults,
        budgetStatus: this.ledger.checkLimits(capability.id, capability.scope.limits),
        trace
      };
    }
    
    // Step 3: Verify scope match
    if (!this.actionInScope(action, capability.scope)) {
      return {
        outcome: { type: "Bulk", outcome: RuleOutcome.Deny },
        matchedRules: ["scope_mismatch"],
        guardResults,
        budgetStatus: this.ledger.checkLimits(capability.id, capability.scope.limits),
        trace
      };
    }
    
    // Step 4: Verify budgets
    const budgetStatus = this.ledger.checkLimits(capability.id, capability.scope.limits);
    if (!budgetStatus.withinLimits) {
      return {
        outcome: { type: "Bulk", outcome: RuleOutcome.Deny },
        matchedRules: ["budget_exceeded"],
        guardResults,
        budgetStatus,
        trace
      };
    }
    
    // Step 5: Run through decision DAG
    const context: RuleContext = {
      corridorState: {},
      budgets: capability.scope.limits,
      time: now
    };
    
    let currentNode = manifest.decisionDAG.get(manifest.rootNode);
    
    while (currentNode) {
      trace.pathTaken.push(currentNode.id);
      
      if (currentNode.type === "leaf") {
        // Record usage
        this.ledger.record(capability.id, { calls: 1 });
        
        return {
          outcome: { type: "Bulk", outcome: currentNode.outcome! },
          matchedRules,
          guardResults,
          budgetStatus: this.ledger.checkLimits(capability.id, capability.scope.limits),
          trace: this.finalizeTrace(trace)
        };
      }
      
      let result: boolean;
      
      if (currentNode.type === "guard" && currentNode.guard) {
        const guardResult = currentNode.guard.predicate(action, context);
        guardResults.set(currentNode.guard.id, guardResult);
        result = guardResult.satisfied;
        
        trace.steps.push({
          nodeId: currentNode.id,
          nodeType: "guard",
          result,
          reason: guardResult.reason
        });
      } else if (currentNode.predicate) {
        result = currentNode.predicate(action, context);
        if (result) {
          matchedRules.push(currentNode.id);
        }
        
        trace.steps.push({
          nodeId: currentNode.id,
          nodeType: "predicate",
          result,
          reason: currentNode.justification ?? ""
        });
      } else {
        result = false;
      }
      
      const nextNodeId = result ? currentNode.trueChild : currentNode.falseChild;
      currentNode = nextNodeId ? manifest.decisionDAG.get(nextNodeId) : undefined;
    }
    
    // Default deny if we fall through
    return {
      outcome: { type: "Bulk", outcome: RuleOutcome.Deny },
      matchedRules: ["default_deny"],
      guardResults,
      budgetStatus: this.ledger.checkLimits(capability.id, capability.scope.limits),
      trace: this.finalizeTrace(trace)
    };
  }
  
  private actionInScope(action: ActionRecord, scope: Scope): boolean {
    // Check resource matches domain
    if (!action.resource.startsWith(scope.domain.path.replace("*", ""))) {
      return false;
    }
    
    // Check operation is permitted
    const opPermission = this.operationToPermission(action.operation);
    if (opPermission && !scope.permissions.has(opPermission)) {
      return false;
    }
    
    return true;
  }
  
  private operationToPermission(operation: string): Permission | undefined {
    const mapping: Record<string, Permission> = {
      "read": Permission.Read,
      "write": Permission.Write,
      "execute": Permission.Execute,
      "connect": Permission.Connect,
      "bind": Permission.Bind
    };
    return mapping[operation.toLowerCase()];
  }
  
  private finalizeTrace(trace: CheckTrace): CheckTrace {
    trace.hash = hashString(JSON.stringify(trace));
    return trace;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: TRUST ZONES AND ZONE GEOMETRY
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Trust zone: Region in policy space
 */
export interface TrustZone {
  id: string;
  name: string;
  scope: Scope;
  boundary: ZoneBoundary;
  adjacentZones: string[];
  bridges: ZoneBridge[];
}

/**
 * Zone boundary
 */
export interface ZoneBoundary {
  type: "hard" | "soft";
  guards: Guard[];
  thickness: number;  // Corridor margin
}

/**
 * Zone bridge: Transform for movement between zones
 */
export interface ZoneBridge {
  id: string;
  sourceZone: string;
  targetZone: string;
  requiredApproval: boolean;
  attenuationRequired: boolean;
  certificate?: string;
}

/**
 * Boundary family: Parameterized collection of boundaries
 */
export interface BoundaryFamily {
  id: string;
  parameter: string;
  boundaries: Map<number, ZoneBoundary>;
  refinementDirection: "tighter" | "looser";
}

/**
 * Zone geometry manager
 */
export class ZoneGeometry {
  private zones: Map<string, TrustZone> = new Map();
  private boundaryFamilies: Map<string, BoundaryFamily> = new Map();
  private adjacencyGraph: Map<string, Set<string>> = new Map();
  
  /**
   * Add trust zone
   */
  addZone(zone: TrustZone): void {
    this.zones.set(zone.id, zone);
    
    // Update adjacency graph
    if (!this.adjacencyGraph.has(zone.id)) {
      this.adjacencyGraph.set(zone.id, new Set());
    }
    
    for (const adjId of zone.adjacentZones) {
      this.adjacencyGraph.get(zone.id)!.add(adjId);
      
      if (!this.adjacencyGraph.has(adjId)) {
        this.adjacencyGraph.set(adjId, new Set());
      }
      this.adjacencyGraph.get(adjId)!.add(zone.id);
    }
  }
  
  /**
   * Check zone containment (Law 6.5)
   */
  checkContainment(zone1Id: string, zone2Id: string): ContainmentResult {
    const zone1 = this.zones.get(zone1Id);
    const zone2 = this.zones.get(zone2Id);
    
    if (!zone1 || !zone2) {
      return {
        contained: false,
        reason: "Zone not found",
        proof: undefined
      };
    }
    
    // Check scope attenuation
    if (!isAttenuation(zone1.scope, zone2.scope)) {
      return {
        contained: false,
        reason: "Scope not attenuated",
        proof: undefined
      };
    }
    
    // Check guard inclusion
    const guardsIncluded = zone1.boundary.guards.every(g1 =>
      zone2.boundary.guards.some(g2 => g2.id === g1.id)
    );
    
    if (!guardsIncluded) {
      return {
        contained: false,
        reason: "Guards not included",
        proof: undefined
      };
    }
    
    return {
      contained: true,
      reason: "Zone contained",
      proof: {
        attenuationProof: serializeScope(zone1.scope),
        guardInclusionProof: zone1.boundary.guards.map(g => g.id)
      }
    };
  }
  
  /**
   * Find escalation path between zones (Law 6.6)
   */
  findEscalationPath(
    sourceId: string,
    targetId: string
  ): EscalationPath | undefined {
    const source = this.zones.get(sourceId);
    const target = this.zones.get(targetId);
    
    if (!source || !target) return undefined;
    
    // BFS to find path
    const visited = new Set<string>();
    const queue: { zoneId: string; path: ZoneBridge[] }[] = [
      { zoneId: sourceId, path: [] }
    ];
    
    while (queue.length > 0) {
      const { zoneId, path } = queue.shift()!;
      
      if (zoneId === targetId) {
        return {
          source: sourceId,
          target: targetId,
          bridges: path,
          approvalsRequired: path.filter(b => b.requiredApproval).length,
          monotonic: this.isMonotonicEscalation(path)
        };
      }
      
      if (visited.has(zoneId)) continue;
      visited.add(zoneId);
      
      const zone = this.zones.get(zoneId);
      if (!zone) continue;
      
      for (const bridge of zone.bridges) {
        if (!visited.has(bridge.targetZone)) {
          queue.push({
            zoneId: bridge.targetZone,
            path: [...path, bridge]
          });
        }
      }
    }
    
    return undefined;
  }
  
  /**
   * Check if escalation path is monotonic (privilege only increases with approval)
   */
  private isMonotonicEscalation(bridges: ZoneBridge[]): boolean {
    for (const bridge of bridges) {
      const source = this.zones.get(bridge.sourceZone);
      const target = this.zones.get(bridge.targetZone);
      
      if (!source || !target) return false;
      
      // If target has more privilege, approval must be required
      if (!isAttenuation(target.scope, source.scope) && !bridge.requiredApproval) {
        return false;
      }
    }
    return true;
  }
  
  /**
   * Get all zones
   */
  getAllZones(): TrustZone[] {
    return Array.from(this.zones.values());
  }
  
  /**
   * Get adjacency graph
   */
  getAdjacencyGraph(): Map<string, Set<string>> {
    return new Map(this.adjacencyGraph);
  }
}

export interface ContainmentResult {
  contained: boolean;
  reason: string;
  proof?: {
    attenuationProof: string;
    guardInclusionProof: string[];
  };
}

export interface EscalationPath {
  source: string;
  target: string;
  bridges: ZoneBridge[];
  approvalsRequired: number;
  monotonic: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: DELEGATION ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Delegation chain entry
 */
export interface DelegationChainEntry {
  capability: Capability;
  attenuationProof: string;
  depth: number;
}

/**
 * Delegation engine
 */
export class DelegationEngine {
  private chains: Map<string, DelegationChainEntry[]> = new Map();
  
  /**
   * Derive attenuated capability (Law 6.2)
   */
  deriveCapability(
    parent: Capability,
    newScope: Scope,
    newPrincipal: Principal,
    owner: Owner
  ): Capability | { error: string } {
    // Check delegation is allowed
    if (parent.delegation.mode === DelegationMode.None) {
      return { error: "Parent capability does not allow delegation" };
    }
    
    // Check attenuation
    if (!isAttenuation(newScope, parent.scope)) {
      return { error: "New scope is not an attenuation of parent scope" };
    }
    
    // Check depth
    const currentChain = this.chains.get(parent.id) ?? [];
    if (currentChain.length >= parent.delegation.maxDepth) {
      return { error: "Maximum delegation depth exceeded" };
    }
    
    // Create derived capability
    const derived = createCapability(newPrincipal, newScope, owner, {
      delegation: {
        mode: parent.delegation.mode === DelegationMode.Full ? 
              DelegationMode.Attenuate : DelegationMode.None,
        maxDepth: Math.max(0, parent.delegation.maxDepth - 1),
        restrictions: [...parent.delegation.restrictions]
      }
    });
    
    derived.parentId = parent.id;
    
    // Record chain
    const newChain = [
      ...currentChain,
      {
        capability: derived,
        attenuationProof: this.createAttenuationProof(parent.scope, newScope),
        depth: currentChain.length + 1
      }
    ];
    this.chains.set(derived.id, newChain);
    
    return derived;
  }
  
  /**
   * Verify delegation chain
   */
  verifyChain(capabilityId: string): ChainVerificationResult {
    const chain = this.chains.get(capabilityId);
    
    if (!chain || chain.length === 0) {
      return {
        valid: true,
        depth: 0,
        issues: []
      };
    }
    
    const issues: string[] = [];
    
    for (let i = 1; i < chain.length; i++) {
      const parent = chain[i - 1].capability;
      const child = chain[i].capability;
      
      // Verify attenuation
      if (!isAttenuation(child.scope, parent.scope)) {
        issues.push(`Level ${i}: Scope not properly attenuated`);
      }
      
      // Verify parent allows delegation
      if (parent.delegation.mode === DelegationMode.None) {
        issues.push(`Level ${i}: Parent does not allow delegation`);
      }
    }
    
    return {
      valid: issues.length === 0,
      depth: chain.length,
      issues
    };
  }
  
  private createAttenuationProof(parentScope: Scope, childScope: Scope): string {
    return hashString(JSON.stringify({
      parent: serializeScope(parentScope),
      child: serializeScope(childScope),
      attenuated: isAttenuation(childScope, parentScope)
    }));
  }
}

export interface ChainVerificationResult {
  valid: boolean;
  depth: number;
  issues: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 8: CORRIDOR CERTIFICATE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Corridor proof certificate
 */
export interface CorridorProofCertificate {
  manifest: string;  // Hash
  action: ActionRecord;
  decision: RuleOutcome;
  matchedRules: string[];
  guardOutcomes: Map<string, boolean>;
  budgetStatus: BudgetStatus;
  trace: CheckTrace;
  hash: string;
  timestamp: number;
}

/**
 * Escalation log entry
 */
export interface EscalationLogEntry {
  requester: string;
  targetScope: Scope;
  justification: string;
  approvals: ApprovalEntry[];
  attenuationProof: string;
  time: number;
  hash: string;
}

export interface ApprovalEntry {
  approver: string;
  signature: string;
  validFrom: number;
  validUntil: number;
  revoked: boolean;
}

/**
 * Certificate generator
 */
export class CertificateGenerator {
  /**
   * Generate corridor proof certificate
   */
  generateCorridorProof(
    manifest: CompiledManifest,
    action: ActionRecord,
    checkResult: CheckResult
  ): CorridorProofCertificate {
    const cert: CorridorProofCertificate = {
      manifest: manifest.merkleRoot,
      action,
      decision: checkResult.outcome.type === "Bulk" ? 
                checkResult.outcome.outcome : RuleOutcome.Deny,
      matchedRules: checkResult.matchedRules,
      guardOutcomes: new Map(),
      budgetStatus: checkResult.budgetStatus,
      trace: checkResult.trace,
      hash: "",
      timestamp: Date.now()
    };
    
    // Convert guard results to boolean outcomes
    for (const [guardId, result] of checkResult.guardResults) {
      cert.guardOutcomes.set(guardId, result.satisfied);
    }
    
    // Compute certificate hash
    cert.hash = hashString(JSON.stringify({
      manifest: cert.manifest,
      action: cert.action,
      decision: cert.decision,
      matchedRules: cert.matchedRules,
      timestamp: cert.timestamp
    }));
    
    return cert;
  }
  
  /**
   * Generate escalation log
   */
  generateEscalationLog(
    requester: Principal,
    targetScope: Scope,
    justification: string,
    approvals: ApprovalEntry[]
  ): EscalationLogEntry {
    const entry: EscalationLogEntry = {
      requester: requester.id,
      targetScope,
      justification,
      approvals,
      attenuationProof: "",
      time: Date.now(),
      hash: ""
    };
    
    entry.hash = hashString(JSON.stringify({
      requester: entry.requester,
      targetScope: serializeScope(entry.targetScope),
      justification: entry.justification,
      approvals: entry.approvals.map(a => a.signature),
      time: entry.time
    }));
    
    return entry;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 9: CAPABILITY CORRIDOR ENGINE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete Capability Corridor Engine
 */
export class CapabilityCorridorEngine {
  private compiler: ManifestCompiler;
  private checker: CapabilityChecker;
  private zoneGeometry: ZoneGeometry;
  private delegationEngine: DelegationEngine;
  private certGenerator: CertificateGenerator;
  
  private manifests: Map<string, CompiledManifest> = new Map();
  private capabilities: Map<string, Capability> = new Map();
  private auditLog: CorridorProofCertificate[] = [];
  
  constructor() {
    this.compiler = new ManifestCompiler();
    this.checker = new CapabilityChecker();
    this.zoneGeometry = new ZoneGeometry();
    this.delegationEngine = new DelegationEngine();
    this.certGenerator = new CertificateGenerator();
  }
  
  /**
   * Register principal
   */
  registerPrincipal(principal: Principal): void {
    this.checker.registerPrincipal(principal);
  }
  
  /**
   * Register owner
   */
  registerOwner(owner: Owner): void {
    this.checker.registerOwner(owner);
  }
  
  /**
   * Compile and register manifest
   */
  registerManifest(manifest: CapabilityManifest): CompiledManifest {
    const compiled = this.compiler.compile(manifest);
    this.manifests.set(compiled.merkleRoot, compiled);
    return compiled;
  }
  
  /**
   * Issue capability
   */
  issueCapability(
    principal: Principal,
    scope: Scope,
    owner: Owner,
    options?: { validityPeriod?: number; delegation?: DelegationSpec }
  ): Capability {
    const cap = createCapability(principal, scope, owner, options);
    this.capabilities.set(cap.id, cap);
    return cap;
  }
  
  /**
   * Check action against capability and manifest
   */
  checkAction(
    capabilityId: string,
    action: ActionRecord,
    manifestHash: string
  ): CheckResult & { certificate: CorridorProofCertificate } {
    const capability = this.capabilities.get(capabilityId);
    const manifest = this.manifests.get(manifestHash);
    
    if (!capability || !manifest) {
      throw new Error("Capability or manifest not found");
    }
    
    const result = this.checker.check(capability, action, manifest);
    const certificate = this.certGenerator.generateCorridorProof(manifest, action, result);
    
    this.auditLog.push(certificate);
    
    return { ...result, certificate };
  }
  
  /**
   * Add trust zone
   */
  addTrustZone(zone: TrustZone): void {
    this.zoneGeometry.addZone(zone);
  }
  
  /**
   * Check zone containment
   */
  checkZoneContainment(zone1Id: string, zone2Id: string): ContainmentResult {
    return this.zoneGeometry.checkContainment(zone1Id, zone2Id);
  }
  
  /**
   * Find escalation path
   */
  findEscalationPath(sourceId: string, targetId: string): EscalationPath | undefined {
    return this.zoneGeometry.findEscalationPath(sourceId, targetId);
  }
  
  /**
   * Derive capability with attenuation
   */
  deriveCapability(
    parentId: string,
    newScope: Scope,
    newPrincipal: Principal,
    owner: Owner
  ): Capability | { error: string } {
    const parent = this.capabilities.get(parentId);
    if (!parent) {
      return { error: "Parent capability not found" };
    }
    
    const result = this.delegationEngine.deriveCapability(parent, newScope, newPrincipal, owner);
    
    if ('id' in result) {
      this.capabilities.set(result.id, result);
    }
    
    return result;
  }
  
  /**
   * Get audit log
   */
  getAuditLog(): CorridorProofCertificate[] {
    return [...this.auditLog];
  }
  
  /**
   * Get statistics
   */
  getStats(): CorridorStats {
    const decisions = this.auditLog.map(c => c.decision);
    
    return {
      manifests: this.manifests.size,
      capabilities: this.capabilities.size,
      zones: this.zoneGeometry.getAllZones().length,
      decisions: this.auditLog.length,
      allows: decisions.filter(d => d === RuleOutcome.Allow).length,
      denies: decisions.filter(d => d === RuleOutcome.Deny).length
    };
  }
}

export interface CorridorStats {
  manifests: number;
  capabilities: number;
  zones: number;
  decisions: number;
  allows: number;
  denies: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Types
  Permission,
  DomainType,
  DelegationMode,
  RuleOutcome,
  BoundaryKind,
  
  // Functions
  createOwnershipStatement,
  createCapability,
  isAttenuation,
  
  // Classes
  ManifestCompiler,
  BudgetLedger,
  CapabilityChecker,
  ZoneGeometry,
  DelegationEngine,
  CertificateGenerator,
  CapabilityCorridorEngine
};
