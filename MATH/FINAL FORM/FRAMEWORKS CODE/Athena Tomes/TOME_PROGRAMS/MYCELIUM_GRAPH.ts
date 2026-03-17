/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * MYCELIUM GRAPH - Complete Navigation Implementation
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Full implementation of the MyceliumGraph 𝒢 = (V, E, H, Q, Π, Ω, 𝕋, Ctx)
 * 
 * Features:
 * - Graph construction and modification
 * - Pathfinding with corridor constraints
 * - Truth value propagation
 * - Subgraph extraction
 * - Cycle detection
 * - Topological sorting
 * - Strongly connected components
 * 
 * @module MYCELIUM_GRAPH
 * @version 1.0.0
 */

import { 
  TruthValue, 
  TruthLattice, 
  EdgeKind, 
  EdgeAlgebra,
  Addressing,
  Corridors,
  WitnessPtr,
  LinkEdge,
  LinkEdges,
  ValidationResult
} from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: VERTEX TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface Vertex {
  id: string;
  address: string;              // Global address
  type: VertexType;
  truth: TruthValue;
  data: Record<string, unknown>;
  metadata: VertexMetadata;
}

export type VertexType = 
  | "atom"       // Individual atom in a station
  | "station"    // Chapter or appendix station
  | "hub"        // Appendix hub
  | "arc"        // Arc grouping
  | "external";  // External reference

export interface VertexMetadata {
  createdAt: number;
  modifiedAt: number;
  version: number;
  corridor?: string;
  witnessCount: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: EDGE TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface GraphEdge {
  id: string;
  source: string;      // Vertex ID
  target: string;      // Vertex ID
  kind: EdgeKind;
  weight: number;      // For pathfinding
  truth: TruthValue;
  witness?: WitnessPtr;
  metadata: EdgeMetadata;
}

export interface EdgeMetadata {
  createdAt: number;
  corridor: string;
  scope: "local" | "tome" | "global";
  bidirectional: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: MYCELIUM GRAPH CLASS
// ═══════════════════════════════════════════════════════════════════════════════

export class MyceliumGraph {
  private vertices: Map<string, Vertex> = new Map();
  private edges: Map<string, GraphEdge> = new Map();
  private adjacencyList: Map<string, Set<string>> = new Map();  // vertex -> edge IDs
  private reverseAdjacency: Map<string, Set<string>> = new Map();  // vertex -> incoming edge IDs
  
  public readonly id: string;
  public readonly manuscript: string;
  public corridor: Corridors.Corridor;
  
  constructor(id: string, manuscript: string, corridor: Corridors.Corridor) {
    this.id = id;
    this.manuscript = manuscript;
    this.corridor = corridor;
  }
  
  // ═══════════════════════════════════════════════════════════════════════════
  // VERTEX OPERATIONS
  // ═══════════════════════════════════════════════════════════════════════════
  
  addVertex(vertex: Vertex): void {
    if (this.vertices.has(vertex.id)) {
      throw new Error(`Vertex ${vertex.id} already exists`);
    }
    this.vertices.set(vertex.id, vertex);
    this.adjacencyList.set(vertex.id, new Set());
    this.reverseAdjacency.set(vertex.id, new Set());
  }
  
  getVertex(id: string): Vertex | undefined {
    return this.vertices.get(id);
  }
  
  hasVertex(id: string): boolean {
    return this.vertices.has(id);
  }
  
  removeVertex(id: string): boolean {
    if (!this.vertices.has(id)) return false;
    
    // Remove all incident edges
    const outEdges = this.adjacencyList.get(id) ?? new Set();
    const inEdges = this.reverseAdjacency.get(id) ?? new Set();
    
    for (const edgeId of outEdges) {
      this.removeEdge(edgeId);
    }
    for (const edgeId of inEdges) {
      this.removeEdge(edgeId);
    }
    
    this.vertices.delete(id);
    this.adjacencyList.delete(id);
    this.reverseAdjacency.delete(id);
    
    return true;
  }
  
  updateVertex(id: string, updates: Partial<Vertex>): boolean {
    const vertex = this.vertices.get(id);
    if (!vertex) return false;
    
    const updated = {
      ...vertex,
      ...updates,
      metadata: {
        ...vertex.metadata,
        modifiedAt: Date.now(),
        version: vertex.metadata.version + 1
      }
    };
    
    this.vertices.set(id, updated);
    return true;
  }
  
  get vertexCount(): number {
    return this.vertices.size;
  }
  
  *allVertices(): Generator<Vertex> {
    for (const vertex of this.vertices.values()) {
      yield vertex;
    }
  }
  
  // ═══════════════════════════════════════════════════════════════════════════
  // EDGE OPERATIONS
  // ═══════════════════════════════════════════════════════════════════════════
  
  addEdge(edge: GraphEdge): void {
    if (!this.vertices.has(edge.source)) {
      throw new Error(`Source vertex ${edge.source} does not exist`);
    }
    if (!this.vertices.has(edge.target)) {
      throw new Error(`Target vertex ${edge.target} does not exist`);
    }
    if (this.edges.has(edge.id)) {
      throw new Error(`Edge ${edge.id} already exists`);
    }
    
    this.edges.set(edge.id, edge);
    this.adjacencyList.get(edge.source)!.add(edge.id);
    this.reverseAdjacency.get(edge.target)!.add(edge.id);
    
    // If bidirectional, add reverse edge
    if (edge.metadata.bidirectional) {
      const reverseId = `${edge.id}_rev`;
      const reverseEdge: GraphEdge = {
        ...edge,
        id: reverseId,
        source: edge.target,
        target: edge.source
      };
      this.edges.set(reverseId, reverseEdge);
      this.adjacencyList.get(edge.target)!.add(reverseId);
      this.reverseAdjacency.get(edge.source)!.add(reverseId);
    }
  }
  
  getEdge(id: string): GraphEdge | undefined {
    return this.edges.get(id);
  }
  
  hasEdge(id: string): boolean {
    return this.edges.has(id);
  }
  
  removeEdge(id: string): boolean {
    const edge = this.edges.get(id);
    if (!edge) return false;
    
    this.edges.delete(id);
    this.adjacencyList.get(edge.source)?.delete(id);
    this.reverseAdjacency.get(edge.target)?.delete(id);
    
    return true;
  }
  
  get edgeCount(): number {
    return this.edges.size;
  }
  
  *allEdges(): Generator<GraphEdge> {
    for (const edge of this.edges.values()) {
      yield edge;
    }
  }
  
  // Get outgoing edges from vertex
  getOutEdges(vertexId: string): GraphEdge[] {
    const edgeIds = this.adjacencyList.get(vertexId);
    if (!edgeIds) return [];
    return Array.from(edgeIds).map(id => this.edges.get(id)!);
  }
  
  // Get incoming edges to vertex
  getInEdges(vertexId: string): GraphEdge[] {
    const edgeIds = this.reverseAdjacency.get(vertexId);
    if (!edgeIds) return [];
    return Array.from(edgeIds).map(id => this.edges.get(id)!);
  }
  
  // Get neighbors (targets of outgoing edges)
  getNeighbors(vertexId: string): Vertex[] {
    return this.getOutEdges(vertexId)
      .map(e => this.vertices.get(e.target)!)
      .filter(v => v !== undefined);
  }
  
  // Get predecessors (sources of incoming edges)
  getPredecessors(vertexId: string): Vertex[] {
    return this.getInEdges(vertexId)
      .map(e => this.vertices.get(e.source)!)
      .filter(v => v !== undefined);
  }
  
  // ═══════════════════════════════════════════════════════════════════════════
  // PATHFINDING
  // ═══════════════════════════════════════════════════════════════════════════
  
  // Dijkstra's shortest path
  findShortestPath(
    startId: string, 
    endId: string,
    options: {
      maxCost?: number;
      allowedEdgeKinds?: EdgeKind[];
      minTruth?: TruthValue;
    } = {}
  ): { path: string[]; cost: number; edges: GraphEdge[] } | null {
    if (!this.vertices.has(startId) || !this.vertices.has(endId)) {
      return null;
    }
    
    const distances = new Map<string, number>();
    const previous = new Map<string, { vertex: string; edge: GraphEdge }>();
    const visited = new Set<string>();
    const queue: { id: string; distance: number }[] = [];
    
    distances.set(startId, 0);
    queue.push({ id: startId, distance: 0 });
    
    while (queue.length > 0) {
      // Sort by distance (priority queue would be better)
      queue.sort((a, b) => a.distance - b.distance);
      const current = queue.shift()!;
      
      if (visited.has(current.id)) continue;
      visited.add(current.id);
      
      if (current.id === endId) break;
      
      // Check max cost
      if (options.maxCost && current.distance > options.maxCost) continue;
      
      for (const edge of this.getOutEdges(current.id)) {
        // Filter by edge kind
        if (options.allowedEdgeKinds && !options.allowedEdgeKinds.includes(edge.kind)) {
          continue;
        }
        
        // Filter by truth value
        if (options.minTruth !== undefined && edge.truth < options.minTruth) {
          continue;
        }
        
        const newDist = current.distance + edge.weight;
        const oldDist = distances.get(edge.target) ?? Infinity;
        
        if (newDist < oldDist) {
          distances.set(edge.target, newDist);
          previous.set(edge.target, { vertex: current.id, edge });
          queue.push({ id: edge.target, distance: newDist });
        }
      }
    }
    
    if (!distances.has(endId)) return null;
    
    // Reconstruct path
    const path: string[] = [];
    const edges: GraphEdge[] = [];
    let current = endId;
    
    while (current !== startId) {
      path.unshift(current);
      const prev = previous.get(current);
      if (!prev) break;
      edges.unshift(prev.edge);
      current = prev.vertex;
    }
    path.unshift(startId);
    
    return {
      path,
      cost: distances.get(endId)!,
      edges
    };
  }
  
  // Find all paths (BFS with path limit)
  findAllPaths(
    startId: string,
    endId: string,
    maxPaths: number = 10,
    maxLength: number = 20
  ): { path: string[]; edges: GraphEdge[] }[] {
    const results: { path: string[]; edges: GraphEdge[] }[] = [];
    
    const stack: { 
      vertex: string; 
      path: string[]; 
      edges: GraphEdge[];
      visited: Set<string>;
    }[] = [{
      vertex: startId,
      path: [startId],
      edges: [],
      visited: new Set([startId])
    }];
    
    while (stack.length > 0 && results.length < maxPaths) {
      const current = stack.pop()!;
      
      if (current.vertex === endId) {
        results.push({ path: current.path, edges: current.edges });
        continue;
      }
      
      if (current.path.length >= maxLength) continue;
      
      for (const edge of this.getOutEdges(current.vertex)) {
        if (!current.visited.has(edge.target)) {
          const newVisited = new Set(current.visited);
          newVisited.add(edge.target);
          
          stack.push({
            vertex: edge.target,
            path: [...current.path, edge.target],
            edges: [...current.edges, edge],
            visited: newVisited
          });
        }
      }
    }
    
    return results;
  }
  
  // ═══════════════════════════════════════════════════════════════════════════
  // GRAPH ANALYSIS
  // ═══════════════════════════════════════════════════════════════════════════
  
  // Detect cycles using DFS
  hasCycles(): boolean {
    const white = new Set(this.vertices.keys());  // Not visited
    const gray = new Set<string>();                // In progress
    const black = new Set<string>();               // Completed
    
    const dfs = (vertexId: string): boolean => {
      white.delete(vertexId);
      gray.add(vertexId);
      
      for (const edge of this.getOutEdges(vertexId)) {
        if (gray.has(edge.target)) {
          return true;  // Back edge = cycle
        }
        if (white.has(edge.target) && dfs(edge.target)) {
          return true;
        }
      }
      
      gray.delete(vertexId);
      black.add(vertexId);
      return false;
    };
    
    for (const vertexId of this.vertices.keys()) {
      if (white.has(vertexId) && dfs(vertexId)) {
        return true;
      }
    }
    
    return false;
  }
  
  // Topological sort (Kahn's algorithm)
  topologicalSort(): string[] | null {
    const inDegree = new Map<string, number>();
    
    // Initialize in-degrees
    for (const v of this.vertices.keys()) {
      inDegree.set(v, 0);
    }
    
    for (const edge of this.edges.values()) {
      inDegree.set(edge.target, (inDegree.get(edge.target) ?? 0) + 1);
    }
    
    // Find vertices with no incoming edges
    const queue: string[] = [];
    for (const [v, deg] of inDegree) {
      if (deg === 0) queue.push(v);
    }
    
    const result: string[] = [];
    
    while (queue.length > 0) {
      const vertex = queue.shift()!;
      result.push(vertex);
      
      for (const edge of this.getOutEdges(vertex)) {
        const newDeg = (inDegree.get(edge.target) ?? 0) - 1;
        inDegree.set(edge.target, newDeg);
        if (newDeg === 0) queue.push(edge.target);
      }
    }
    
    // If not all vertices included, there's a cycle
    if (result.length !== this.vertices.size) {
      return null;
    }
    
    return result;
  }
  
  // Find strongly connected components (Kosaraju's algorithm)
  findStronglyConnectedComponents(): string[][] {
    const visited = new Set<string>();
    const stack: string[] = [];
    
    // First DFS to fill stack
    const dfs1 = (v: string) => {
      visited.add(v);
      for (const edge of this.getOutEdges(v)) {
        if (!visited.has(edge.target)) {
          dfs1(edge.target);
        }
      }
      stack.push(v);
    };
    
    for (const v of this.vertices.keys()) {
      if (!visited.has(v)) dfs1(v);
    }
    
    // Build reverse graph
    const reverseAdj = new Map<string, string[]>();
    for (const v of this.vertices.keys()) {
      reverseAdj.set(v, []);
    }
    for (const edge of this.edges.values()) {
      reverseAdj.get(edge.target)!.push(edge.source);
    }
    
    // Second DFS on reverse graph
    visited.clear();
    const components: string[][] = [];
    
    const dfs2 = (v: string, component: string[]) => {
      visited.add(v);
      component.push(v);
      for (const u of reverseAdj.get(v) ?? []) {
        if (!visited.has(u)) {
          dfs2(u, component);
        }
      }
    };
    
    while (stack.length > 0) {
      const v = stack.pop()!;
      if (!visited.has(v)) {
        const component: string[] = [];
        dfs2(v, component);
        components.push(component);
      }
    }
    
    return components;
  }
  
  // ═══════════════════════════════════════════════════════════════════════════
  // TRUTH VALUE PROPAGATION
  // ═══════════════════════════════════════════════════════════════════════════
  
  // Propagate truth values through graph
  propagateTruth(): Map<string, TruthValue> {
    const truthMap = new Map<string, TruthValue>();
    
    // Initialize with vertex truth values
    for (const [id, vertex] of this.vertices) {
      truthMap.set(id, vertex.truth);
    }
    
    // Propagate: vertex truth is meet of incoming edge truths and source truths
    let changed = true;
    let iterations = 0;
    const maxIterations = this.vertices.size * 2;
    
    while (changed && iterations < maxIterations) {
      changed = false;
      iterations++;
      
      for (const [id, vertex] of this.vertices) {
        const inEdges = this.getInEdges(id);
        
        if (inEdges.length === 0) continue;
        
        // Compute minimum truth from all incoming paths
        let minTruth = TruthValue.OK;
        
        for (const edge of inEdges) {
          const sourceTruth = truthMap.get(edge.source) ?? TruthValue.FAIL;
          const pathTruth = TruthLattice.meet(sourceTruth, edge.truth);
          minTruth = TruthLattice.meet(minTruth, pathTruth);
        }
        
        // Take meet with current vertex truth
        const newTruth = TruthLattice.meet(vertex.truth, minTruth);
        
        if (newTruth !== truthMap.get(id)) {
          truthMap.set(id, newTruth);
          changed = true;
        }
      }
    }
    
    return truthMap;
  }
  
  // Find vertices with specific truth value
  findByTruth(truth: TruthValue): Vertex[] {
    const result: Vertex[] = [];
    for (const vertex of this.vertices.values()) {
      if (vertex.truth === truth) {
        result.push(vertex);
      }
    }
    return result;
  }
  
  // ═══════════════════════════════════════════════════════════════════════════
  // SUBGRAPH OPERATIONS
  // ═══════════════════════════════════════════════════════════════════════════
  
  // Extract subgraph containing only specified vertices
  extractSubgraph(vertexIds: Set<string>): MyceliumGraph {
    const subgraph = new MyceliumGraph(
      `${this.id}_sub`,
      this.manuscript,
      this.corridor
    );
    
    // Add vertices
    for (const id of vertexIds) {
      const vertex = this.vertices.get(id);
      if (vertex) {
        subgraph.addVertex({ ...vertex });
      }
    }
    
    // Add edges where both endpoints are in subgraph
    for (const edge of this.edges.values()) {
      if (vertexIds.has(edge.source) && vertexIds.has(edge.target)) {
        subgraph.addEdge({ ...edge });
      }
    }
    
    return subgraph;
  }
  
  // Get reachable subgraph from a vertex
  getReachableSubgraph(startId: string, maxDepth: number = Infinity): MyceliumGraph {
    const reachable = new Set<string>();
    const queue: { id: string; depth: number }[] = [{ id: startId, depth: 0 }];
    
    while (queue.length > 0) {
      const { id, depth } = queue.shift()!;
      
      if (reachable.has(id) || depth > maxDepth) continue;
      reachable.add(id);
      
      for (const edge of this.getOutEdges(id)) {
        queue.push({ id: edge.target, depth: depth + 1 });
      }
    }
    
    return this.extractSubgraph(reachable);
  }
  
  // ═══════════════════════════════════════════════════════════════════════════
  // SERIALIZATION
  // ═══════════════════════════════════════════════════════════════════════════
  
  toJSON(): object {
    return {
      id: this.id,
      manuscript: this.manuscript,
      corridor: this.corridor,
      vertices: Array.from(this.vertices.values()),
      edges: Array.from(this.edges.values())
    };
  }
  
  static fromJSON(json: {
    id: string;
    manuscript: string;
    corridor: Corridors.Corridor;
    vertices: Vertex[];
    edges: GraphEdge[];
  }): MyceliumGraph {
    const graph = new MyceliumGraph(json.id, json.manuscript, json.corridor);
    
    for (const vertex of json.vertices) {
      graph.addVertex(vertex);
    }
    
    for (const edge of json.edges) {
      graph.addEdge(edge);
    }
    
    return graph;
  }
  
  // ═══════════════════════════════════════════════════════════════════════════
  // STATISTICS
  // ═══════════════════════════════════════════════════════════════════════════
  
  getStatistics(): GraphStatistics {
    const edgesByKind = new Map<EdgeKind, number>();
    const verticesByTruth = new Map<TruthValue, number>();
    
    for (const edge of this.edges.values()) {
      edgesByKind.set(edge.kind, (edgesByKind.get(edge.kind) ?? 0) + 1);
    }
    
    for (const vertex of this.vertices.values()) {
      verticesByTruth.set(vertex.truth, (verticesByTruth.get(vertex.truth) ?? 0) + 1);
    }
    
    // Compute average degree
    let totalDegree = 0;
    for (const edges of this.adjacencyList.values()) {
      totalDegree += edges.size;
    }
    
    return {
      vertexCount: this.vertices.size,
      edgeCount: this.edges.size,
      averageDegree: this.vertices.size > 0 ? totalDegree / this.vertices.size : 0,
      edgesByKind: Object.fromEntries(edgesByKind),
      verticesByTruth: Object.fromEntries(verticesByTruth),
      hasCycles: this.hasCycles(),
      componentCount: this.findStronglyConnectedComponents().length
    };
  }
}

export interface GraphStatistics {
  vertexCount: number;
  edgeCount: number;
  averageDegree: number;
  edgesByKind: Record<string, number>;
  verticesByTruth: Record<string, number>;
  hasCycles: boolean;
  componentCount: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: ROUTE FUNCTION
// ═══════════════════════════════════════════════════════════════════════════════

export interface RouteQuery {
  source: string;
  target: string;
  requiredEdgeKinds?: EdgeKind[];
  excludedEdgeKinds?: EdgeKind[];
  minTruth?: TruthValue;
  maxHops?: number;
  corridorId?: string;
}

export interface RouteResult {
  success: boolean;
  truth: TruthValue;
  path?: string[];
  edges?: GraphEdge[];
  cost?: number;
  witness?: WitnessPtr;
  error?: string;
}

export function Route(
  query: RouteQuery,
  graph: MyceliumGraph,
  corridor: Corridors.Corridor
): RouteResult {
  // Check corridor budget
  const budgetCheck = Corridors.isAdmissible(
    { kappa_compute: 10 },  // Base cost for route computation
    corridor.budgets
  );
  
  if (!budgetCheck.admissible) {
    return {
      success: false,
      truth: TruthValue.FAIL,
      error: `Corridor budget violation: ${budgetCheck.violations.join(', ')}`
    };
  }
  
  // Find path with constraints
  const pathResult = graph.findShortestPath(
    query.source,
    query.target,
    {
      maxCost: query.maxHops ? query.maxHops * 10 : undefined,
      allowedEdgeKinds: query.requiredEdgeKinds,
      minTruth: query.minTruth
    }
  );
  
  if (!pathResult) {
    return {
      success: false,
      truth: TruthValue.AMBIG,
      error: "No path found"
    };
  }
  
  // Compute path truth (meet of all edge truths)
  let pathTruth = TruthValue.OK;
  for (const edge of pathResult.edges) {
    pathTruth = TruthLattice.meet(pathTruth, edge.truth);
  }
  
  return {
    success: true,
    truth: pathTruth,
    path: pathResult.path,
    edges: pathResult.edges,
    cost: pathResult.cost
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: GRAPH BUILDERS
// ═══════════════════════════════════════════════════════════════════════════════

export namespace GraphBuilders {
  
  // Build a chapter station subgraph
  export function buildChapterStation(
    chapter: number,
    manuscript: string,
    corridor: Corridors.Corridor
  ): MyceliumGraph {
    const graph = new MyceliumGraph(
      `ch${chapter.toString().padStart(2, '0')}`,
      manuscript,
      corridor
    );
    
    // Add vertices for each atom (4 lenses × 4 facets × 4 atoms = 64)
    for (const addr of Addressing.stationAtoms(chapter)) {
      const globalAddr = Addressing.formatGlobal({ manuscript, local: addr });
      
      graph.addVertex({
        id: globalAddr,
        address: globalAddr,
        type: "atom",
        truth: TruthValue.NEAR,
        data: {
          lens: addr.lens,
          facet: addr.facet,
          atom: addr.atom
        },
        metadata: {
          createdAt: Date.now(),
          modifiedAt: Date.now(),
          version: 1,
          witnessCount: 0
        }
      });
    }
    
    // Add closure edges (a → b → c → d within each lens/facet)
    for (const lens of Addressing.LENSES) {
      for (const facet of Addressing.FACETS) {
        const atoms = Addressing.ATOMS;
        for (let i = 0; i < atoms.length - 1; i++) {
          const source = Addressing.formatGlobal({
            manuscript,
            local: Addressing.chapterAddr(chapter, lens, facet, atoms[i])
          });
          const target = Addressing.formatGlobal({
            manuscript,
            local: Addressing.chapterAddr(chapter, lens, facet, atoms[i + 1])
          });
          
          graph.addEdge({
            id: `closure_${source}_${target}`,
            source,
            target,
            kind: EdgeKind.IMPL,
            weight: 1,
            truth: TruthValue.OK,
            metadata: {
              createdAt: Date.now(),
              corridor: corridor.id,
              scope: "local",
              bidirectional: false
            }
          });
        }
      }
    }
    
    return graph;
  }
  
  // Build hub graph (16 appendices)
  export function buildHubGraph(
    manuscript: string,
    corridor: Corridors.Corridor
  ): MyceliumGraph {
    const graph = new MyceliumGraph(
      "hubs",
      manuscript,
      corridor
    );
    
    const appendices = "ABCDEFGHIJKLMNOP".split('');
    
    // Add hub vertices
    for (const app of appendices) {
      graph.addVertex({
        id: `App${app}`,
        address: `Ms⟨${manuscript}⟩::App${app}`,
        type: "hub",
        truth: TruthValue.OK,
        data: { appendix: app },
        metadata: {
          createdAt: Date.now(),
          modifiedAt: Date.now(),
          version: 1,
          witnessCount: 0
        }
      });
    }
    
    // Add router signature edges (A → I → M)
    graph.addEdge({
      id: "sigma_A_I",
      source: "AppA",
      target: "AppI",
      kind: EdgeKind.REF,
      weight: 1,
      truth: TruthValue.OK,
      metadata: {
        createdAt: Date.now(),
        corridor: corridor.id,
        scope: "global",
        bidirectional: false
      }
    });
    
    graph.addEdge({
      id: "sigma_I_M",
      source: "AppI",
      target: "AppM",
      kind: EdgeKind.REF,
      weight: 1,
      truth: TruthValue.OK,
      metadata: {
        createdAt: Date.now(),
        corridor: corridor.id,
        scope: "global",
        bidirectional: false
      }
    });
    
    return graph;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  MyceliumGraph,
  Route,
  GraphBuilders
};
